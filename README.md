# 🎬 Studio Animation

Pipeline de production d'animations narratives entièrement automatisé via GitHub Actions et IA.

## Concept

Chaque épisode démarre par une **issue GitHub** étiquetée `episode`. Une chaîne d'étapes s'enchaîne ensuite automatiquement :

1. **Script + prompts visuels** générés par Claude (rédaction) puis critiqués par Gemini Flash, intégrés par Claude, et déclinés en prompts pour Leonardo AI / Adobe Firefly / Ideogram.
2. **Images** générées hors workflow puis poussées dans `assets/images/` — déclenche le rendu Remotion (1920×1080 ou 1080×1920) avec sous-titres animés.
3. **Voix off** générée localement par `scripts-python/kokoro-tts.py` (Kokoro TTS, hybride avec ElevenLabs au-delà de 500 mots).
4. **Assemblage final** via FFmpeg quand `musique.mp3` arrive : voix + musique (20 % de volume) + fades + commentaire automatique sur l'issue.
5. **Galerie** publiée automatiquement sur GitHub Pages.

## Secrets GitHub à configurer

| Secret | Usage |
| --- | --- |
| `ANTHROPIC_API_KEY` | Claude (script + Remotion code) |
| `GEMINI_API_KEY` | Gemini Flash (critique + review code) |
| `ELEVENLABS_API_KEY` | Voix off premium au-delà de 500 mots |
| `GITHUB_TOKEN` | Fourni automatiquement par GitHub Actions |

À ajouter dans **Settings → Secrets and variables → Actions**.

## Comment créer un épisode

1. Ouvre une **issue** dans ce repo.
2. Le **titre** devient le titre de l'épisode (ex. `Le voyage d'une goutte d'eau`).
3. Le **corps** suit la structure de [`templates/brief-template.md`](templates/brief-template.md).
4. Ajoute le label **`episode`**.
5. Le workflow `generate-script.yml` crée le dossier `episodes/epNNN-slug/` et publie `script.md` + `prompts.md`. Les prompts sont commentés sur l'issue.
6. Génère les images sur Leonardo / Firefly / Ideogram, renomme-les dans l'ordre des plans (`plan-01.jpg`, `plan-02.jpg`, ...).
7. Pousse les images dans `episodes/epNNN-slug/assets/images/` → `render-animation.yml` produit `assets/video-raw.mp4`.
8. Lance la voix off en local :
   ```bash
   pip install kokoro soundfile
   python scripts-python/kokoro-tts.py episodes/epNNN-slug
   ```
   Push `assets/audio/voix.mp3`.
9. Choisis une musique de fond, place-la dans `assets/audio/musique.mp3` → `assemble-video.yml` assemble `output/episode-final.mp4` et déclenche `deploy-gallery.yml`.
10. La galerie est mise à jour à l'URL :
    `https://<utilisateur>.github.io/<repo>/`

## Pipeline complet

```
Issue (label: episode)
        │
        ▼
generate-script.yml ──► episodes/epNNN-slug/{brief,script,prompts}.md
                                                                    │
                                                                    ▼
                                          (génération images IA hors workflow)
                                                                    │
                                                                    ▼
push images ──► render-animation.yml ──► assets/video-raw.mp4
                                                                    │
                                                                    ▼
                                      kokoro-tts.py (local) ──► assets/audio/voix.mp3
                                                                    │
                                                                    ▼
push musique.mp3 ──► assemble-video.yml ──► output/episode-final.mp4
                                                                    │
                                                                    ▼
                                                            deploy-gallery.yml
                                                                    │
                                                                    ▼
                                                            GitHub Pages
```

## Structure du repo

```
.
├── .github/workflows/        # 4 pipelines GitHub Actions
├── episodes/                 # un dossier par épisode
│   └── ep001-exemple/
│       ├── brief.md
│       ├── script.md
│       ├── prompts.md
│       ├── assets/{images,audio}/
│       └── output/
├── templates/
│   ├── brief-template.md
│   └── animation-base/       # composant Remotion réutilisable
├── scripts-python/
│   └── kokoro-tts.py
└── web/
    └── index.html            # galerie statique
```

## Activer GitHub Pages

Dans **Settings → Pages**, choisir **Source: GitHub Actions**. La galerie est déployée automatiquement par `deploy-gallery.yml`.

## Licence

Code sous licence MIT. Les médias produits dépendent des licences des modèles d'images utilisés.
