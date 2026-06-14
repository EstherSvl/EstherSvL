# The Glass Artist's Grid 🔮

An interactive, **Final Fantasy X sphere-grid-inspired** skill tree for the journey
to becoming a great glass artist — built with React + Vite, themed like a leaded
stained-glass panel.

Skills radiate outward from a central **Foundations** hub into six discipline
"arms". Each node can be clicked to move it through your real progress
(`Not started → Learning → Practiced → Mastered`), and your progress is saved
automatically in your browser. Prerequisite "came" lines light up as you master
the skills they connect, so the grid fills in as you advance — just like the
sphere grid.

## The disciplines

| Discipline | Skills |
|---|---|
| **Foundations** (centre) | Studio Safety & Setup · Glass Cutting · Design & Cartooning · Colour & Glass Selection |
| **Stained Glass** | Copper Foil (Tiffany) · Leadworking (Came) · Soldering · Glass in Lead (Panels) · Bevels & Jewels · Installing Windows |
| **Painting & Surface** | Glass Painting · Hard-Edge Line Work · Silver/Yellow Stain · Kiln Firing (Paint) · Glass Enamels · Gilding |
| **Kiln Glass** | Fusing · Mould Making · Slumping · Kiln Casting / Pâte de Verre |
| **Hot Glass** | Lampworking (Flamework) · Glassblowing · Murrine & Cane · Annealing & Heat Control |
| **Engraving & Texture** | Cold Working · Metal Engraving · Glass Engraving & Etching · Sandblasting |

All of the skills you asked for are included. The grid also adds a handful of
connecting skills that the craft naturally depends on — **glass cutting,
soldering, design/cartooning, colour & glass selection, kiln firing, silver
stain, slumping, kiln casting, annealing, bevels and murrine** — so the
prerequisites form a coherent learning path rather than floating in isolation.

## Why these connections?

The tree is organised so each skill builds on what comes before it, for example:

- **Glass cutting** underpins everything flat — Tiffany foiling, leadwork, bevels.
- **Leadworking + soldering → Glass in Lead → Installing Windows** is the full
  traditional stained-glass path, from came to a finished window in a building.
- **Glass painting → Hard-edge line work / Silver stain → Enamels** follows how
  painted glass is actually learned.
- **Fusing → Mould making → Slumping / Kiln casting** is the kiln-glass progression.
- **Cold working** sits at the cross-roads: fused, blown, cast and engraved work
  all pass through grinding and polishing, so it links several arms together
  (the dashed lines are these cross-discipline connections).
- **Metal engraving** feeds **glass engraving & etching** — the graver control
  transfers directly.

These choices are a starting point — tell me how you'd reorder or reconnect them
to match how *you* want to learn, and I'll adjust the grid.

## Running it locally

```bash
npm install
npm run dev      # start the dev server (prints a local URL)
npm run build    # production build into dist/
npm run preview  # preview the production build
```

## Publishing it online

A GitHub Actions workflow (`.github/workflows/deploy.yml`) builds and deploys the
site to **GitHub Pages** on every push to `main`. To switch it on:

1. Merge this branch into `main`.
2. In the repo: **Settings → Pages → Build and deployment → Source → GitHub Actions**.

The site will then be live at `https://esthersvl.github.io/esthersvl/`.

## Project structure

```
src/
  data/skills.js          # the skill tree: disciplines, nodes, prerequisites, descriptions
  hooks/useProgress.js     # progress state, saved to localStorage
  components/
    SkillGrid.jsx          # the pan/zoom SVG sphere grid
    DetailPanel.jsx        # the side panel for a selected skill
    Legend.jsx             # discipline + progress legend
  App.jsx                  # layout, header, progress bar
  styles.css               # stained-glass theme
```

To add or change skills, edit `src/data/skills.js` — each node has an `id`,
`name`, `discipline`, `x`/`y` position, `prereqs`, and `summary`/`details` text.
