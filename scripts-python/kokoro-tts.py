#!/usr/bin/env python3
"""Generate narration audio for an episode.

Usage:
    python scripts-python/kokoro-tts.py <episode_dir>

- Reads <episode_dir>/script.md
- Extracts only narration lines (** Narration : ** and the rest of the script,
  ignoring **Visuel :** lines and headings)
- If the narration is <= 500 words, generates the full audio via Kokoro TTS.
- If it is longer, generates the first 500 words with ElevenLabs and the rest
  with Kokoro, then concatenates them with FFmpeg.
- Writes <episode_dir>/assets/audio/voix.mp3
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

WORD_THRESHOLD = 500


def extract_narration(script_md: str) -> str:
    """Pull only the narration text out of the markdown script."""
    lines = script_md.splitlines()
    out: list[str] = []
    capture = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            capture = False
            continue
        if stripped.startswith('#'):
            continue
        if re.match(r'\*\*\s*Visuel\s*:\s*\*\*', stripped, re.IGNORECASE):
            capture = False
            continue
        m = re.match(r'\*\*\s*Narration\s*:\s*\*\*\s*(.*)', stripped, re.IGNORECASE)
        if m:
            text = m.group(1).strip()
            text = re.sub(r'^[«"\']+|[»"\']+$', '', text).strip()
            if text:
                out.append(text)
            capture = True
            continue
        if capture:
            out.append(stripped)
    text = ' '.join(out)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def split_at_words(text: str, n: int) -> tuple[str, str]:
    words = text.split()
    if len(words) <= n:
        return text, ''
    return ' '.join(words[:n]), ' '.join(words[n:])


def generate_kokoro(text: str, out_path: Path) -> None:
    """Generate audio with Kokoro TTS (local model)."""
    try:
        from kokoro import KPipeline
        import soundfile as sf
        import numpy as np
    except ImportError as e:
        raise RuntimeError(
            "Kokoro TTS not installed. Run: pip install kokoro soundfile"
        ) from e

    voice = os.environ.get('KOKORO_VOICE', 'ff_siwis')
    lang_code = os.environ.get('KOKORO_LANG', 'f')
    pipeline = KPipeline(lang_code=lang_code)

    chunks = []
    for _, _, audio in pipeline(text, voice=voice, speed=1.0):
        chunks.append(audio)
    if not chunks:
        raise RuntimeError("Kokoro returned no audio")
    full = np.concatenate(chunks)

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_tmp:
        wav_path = Path(wav_tmp.name)
    try:
        sf.write(str(wav_path), full, 24000)
        subprocess.run(
            ['ffmpeg', '-y', '-i', str(wav_path), '-codec:a', 'libmp3lame',
             '-qscale:a', '2', str(out_path)],
            check=True, capture_output=True,
        )
    finally:
        wav_path.unlink(missing_ok=True)


def generate_elevenlabs(text: str, out_path: Path) -> None:
    """Generate audio via the ElevenLabs HTTP API."""
    api_key = os.environ.get('ELEVENLABS_API_KEY')
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set")

    import urllib.request

    voice_id = os.environ.get('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')
    model_id = os.environ.get('ELEVENLABS_MODEL', 'eleven_multilingual_v2')
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    body = (
        '{"text": ' + repr(text).replace("'", '"') +
        ', "model_id": "' + model_id + '"}'
    ).encode('utf-8')

    import json
    body = json.dumps({'text': text, 'model_id': model_id}).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            'xi-api-key': api_key,
            'Content-Type': 'application/json',
            'Accept': 'audio/mpeg',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        out_path.write_bytes(resp.read())


def concat_mp3(parts: list[Path], out_path: Path) -> None:
    """Concatenate MP3 files via ffmpeg."""
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as fl:
        for p in parts:
            fl.write(f"file '{p.resolve()}'\n")
        list_path = Path(fl.name)
    try:
        subprocess.run(
            ['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
             '-i', str(list_path), '-c', 'copy', str(out_path)],
            check=True, capture_output=True,
        )
    finally:
        list_path.unlink(missing_ok=True)


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: kokoro-tts.py <episode_dir>', file=sys.stderr)
        return 1

    episode_dir = Path(sys.argv[1]).resolve()
    script_path = episode_dir / 'script.md'
    if not script_path.is_file():
        print(f'script.md not found in {episode_dir}', file=sys.stderr)
        return 1

    audio_dir = episode_dir / 'assets' / 'audio'
    audio_dir.mkdir(parents=True, exist_ok=True)
    out_path = audio_dir / 'voix.mp3'

    script_md = script_path.read_text(encoding='utf-8')
    narration = extract_narration(script_md)
    if not narration:
        print('No narration text found in script.md', file=sys.stderr)
        return 1

    word_count = len(narration.split())
    print(f'Narration: {word_count} words')

    if word_count <= WORD_THRESHOLD:
        print('Generating full audio via Kokoro...')
        generate_kokoro(narration, out_path)
    else:
        first, rest = split_at_words(narration, WORD_THRESHOLD)
        print(f'Generating first {WORD_THRESHOLD} words with ElevenLabs, rest with Kokoro...')
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            part1 = td_path / 'part1.mp3'
            part2 = td_path / 'part2.mp3'
            generate_elevenlabs(first, part1)
            generate_kokoro(rest, part2)
            concat_mp3([part1, part2], out_path)

    print(f'Wrote {out_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
