# TIE — Project Page

Source for the project page of
**TIE: Time Interval Encoding for Video Generation over Events** (2026 preprint).

Live URL (intended): <https://matrixteam-ai.github.io/pages/TIE/>

## Structure

```
project-page/
├── index.html                # the page itself (single-file)
├── README.md                 # this file
└── static/
    ├── css/
    │   └── main.css          # all styles
    ├── js/                   # (currently empty — JS is inline in index.html)
        ├── videos/               # demo videos and posters
    └── images/
        ├── logos/            # affiliation logo files (see logos/README.md)
        ├── logos/            # affiliation logo files
        └── figs/             # project-page figures exported from the paper/source assets
```

## Local preview

The page is fully static — no build step. Just open `index.html` in a
browser, or serve the folder with any static server:

```bash
cd project-page
python3 -m http.server 8080
# open http://localhost:8080
```

## Deploying to GitHub Pages

If this folder is the entire `gh-pages` site, push to a branch named
`gh-pages` (or `main` with Pages set to "/ (root)") of the
`MatrixTeam-AI/pages` repository, under a `TIE/` subdirectory:

```
pages/
└── TIE/
    ├── index.html
    └── static/...
```

That mirrors the requested URL `matrixteam-ai.github.io/pages/TIE/`.

## Remaining launch items

These items should be completed before the public launch once the final
release links and social assets are ready.

| Placeholder                              | What to drop in                                                    |
| ---------------------------------------- | ------------------------------------------------------------------ |
| `static/images/og-card.png`              | 1200×630 social-share card                                         |
| `static/images/logos/*.svg`              | Affiliation logos — see `static/images/logos/README.md`            |
| arXiv link in CTA + badge                | Activate after the real arXiv ID exists                            |
| Code / dataset links                     | Replace coming-soon states with public release URLs                |

## Credits

Page hand-built for Matrix Team. Layout inspired by the academic project
pages of [Nerfies](https://nerfies.github.io/).
