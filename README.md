# ⛳ Neon Golf — Cyberpunk Mini Golf

A browser-based mini golf game with a neon/cyberpunk aesthetic, 9 unique holes, physics-based gameplay, and an AI opponent.

![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js) ![TypeScript](https://img.shields.io/badge/TypeScript-strict-blue?logo=typescript) ![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-06B6D4?logo=tailwindcss)

---

## Features

- **9 unique holes** with increasing difficulty — straight shots, doglegs, slalom walls, bumpers, moving obstacles, water hazards, and more
- **AI opponent** with Easy / Medium / Hard difficulty tiers
- **Physics engine** — friction, wall bouncing, bumper deflection, circle-circle collision
- **Water hazards** with 2-stroke penalty and animated ripples
- **Moving obstacles** that patrol the fairway
- **Aim & power mechanic** — drag to aim, release to shoot; power bar shows shot strength
- **Full scorecard** — par tracking with Eagle / Birdie / Par / Bogey / Double Bogey labels
- **High score leaderboard** persisted to `localStorage`
- **Procedural sound effects** via Web Audio API (no audio files required)
- **Pause / Resume** at any time
- **Fully responsive** — scales to any screen size; touch controls on mobile
- **Neon/cyberpunk theme** — glowing walls, animated flag, motion trails, water ripples

---

## Controls

### Desktop (keyboard & mouse)

| Action | How |
|--------|-----|
| Aim | Click near the ball and drag |
| Set power | Drag further from ball = more power |
| Shoot | Release the mouse button |
| Pause / Resume | Click the ⏸ button (top-right) |
| Toggle sound | Click 🔊 / 🔇 (top-right) |

### Mobile (touch)

| Action | How |
|--------|-----|
| Aim | Touch near the ball and drag |
| Set power | Drag further = more power |
| Shoot | Lift your finger |
| Pause / Resume | Tap the ⏸ button |

---

## Holes

| # | Name | Par | Features |
|---|------|-----|----------|
| 1 | Straight Shot | 2 | Simple straight fairway — perfect for learning the controls |
| 2 | The Corner | 3 | L-shaped dogleg — aim for the bend |
| 3 | The Gap | 3 | Two wall barriers with gaps to shoot through |
| 4 | Zigzag | 4 | S-shaped multi-section course |
| 5 | Bumper Alley | 3 | Circular bumpers with high rebound — ricochets welcome |
| 6 | The Gauntlet | 4 | Alternating slalom walls from top and bottom |
| 7 | Moving Target | 4 | Two moving obstacles blocking the path |
| 8 | Island Green | 4 | Water hazards on both sides; time your shots |
| 9 | Grand Finale | 5 | Complex maze combining bumpers, moving obstacles, and multi-room layout |

---

## Scoring

| Result | Label |
|--------|-------|
| 2 under par | Eagle |
| 1 under par | Birdie |
| Even | Par |
| 1 over par | Bogey |
| 2 over par | Double Bogey |
| 3+ over par | +N |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | [Next.js 15](https://nextjs.org) (App Router) |
| Language | TypeScript (strict mode) |
| Styling | [Tailwind CSS](https://tailwindcss.com) |
| Rendering | HTML5 Canvas + `requestAnimationFrame` |
| Animations | [Framer Motion](https://www.framer.com/motion/) (UI transitions) |
| Audio | Web Audio API (procedural, no files) |
| Storage | `localStorage` (high scores) |
| Deploy | [Vercel](https://vercel.com) (zero-config) |

---

## Project Structure

```
mini_golf/
├── app/
│   ├── layout.tsx          # Root layout & metadata
│   ├── page.tsx            # Main page — game screen router
│   └── globals.css         # Global styles
├── components/
│   ├── game/
│   │   ├── GameCanvas.tsx  # Canvas renderer + physics loop
│   │   └── GameUI.tsx      # In-game HUD (strokes, par, controls)
│   ├── screens/
│   │   ├── StartScreen.tsx # Main menu
│   │   ├── HoleComplete.tsx# Between-hole overlay
│   │   ├── EndScreen.tsx   # Final scorecard
│   │   └── PauseMenu.tsx   # Pause overlay
│   └── ui/
│       └── Button.tsx      # Reusable neon button
├── hooks/
│   ├── useGame.ts          # Game state machine
│   ├── useSound.ts         # Web Audio API sound effects
│   └── useLocalStorage.ts  # Persistent storage hook
├── lib/
│   ├── physics.ts          # Ball movement, collision detection
│   ├── courses.ts          # All 9 hole definitions
│   ├── renderer.ts         # Canvas drawing functions
│   ├── ai.ts               # AI opponent shot calculation
│   └── utils.ts            # Score formatting helpers
├── types/
│   └── game.ts             # TypeScript interfaces
└── public/
    └── favicon.svg         # Neon golf ball icon
```

---

## Running Locally

**Prerequisites:** Node.js 18+

```bash
# 1. Clone the repository
git clone <repo-url>
cd mini_golf

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Deploy to Vercel

### Option A — Vercel CLI

```bash
npm i -g vercel
vercel
```

### Option B — GitHub integration

1. Push this repo to GitHub
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import the repository — Vercel auto-detects Next.js
4. Click **Deploy**

No environment variables or extra configuration required.

---

## License

MIT
