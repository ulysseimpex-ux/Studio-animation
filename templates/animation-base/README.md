# Animation Base — Remotion Template

Composant Remotion réutilisable utilisé par tous les épisodes.

## Compositions

- `EpisodeHorizontal` — 1920×1080 (YouTube)
- `EpisodeVertical` — 1080×1920 (Reels / Shorts)

## Props

```ts
{
  title: string;
  shots: Array<{
    image: string;          // chemin relatif au dossier public
    narration: string;      // sous-titre affiché en bas
    durationSeconds: number; // 3 à 5 recommandé
  }>;
}
```

## Rendu local

```bash
npm install
npx remotion render src/index.ts EpisodeHorizontal out/video-raw.mp4 --props=./props.json
```

Le workflow `render-animation.yml` clone ce template dans le dossier de l'épisode, écrit `props.json` à partir du script et des images, puis lance le rendu.
