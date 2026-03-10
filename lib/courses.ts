import { CourseHole } from '@/types/game';

// Virtual canvas: 800 x 540
// Walls are 14px thick by convention

const W = 14; // wall thickness

export const COURSES: CourseHole[] = [
  // ── HOLE 1 – "Straight Shot" (par 2) ──────────────────────────────────────
  {
    id: 1,
    name: 'Straight Shot',
    par: 2,
    width: 800,
    height: 540,
    surfaces: [{ x: 80, y: 200, w: 640, h: 140 }],
    walls: [
      { x: 80, y: 200, w: 640, h: W },          // top
      { x: 80, y: 326, w: 640, h: W },          // bottom
      { x: 80, y: 200, w: W, h: 140 },          // left
      { x: 706, y: 200, w: W, h: 140 },         // right
    ],
    circleObstacles: [],
    movingObstacles: [],
    waterHazards: [],
    startPos: { x: 140, y: 270 },
    holePos: { x: 660, y: 270 },
  },

  // ── HOLE 2 – "The Corner" (par 3) ──────────────────────────────────────────
  {
    id: 2,
    name: 'The Corner',
    par: 3,
    width: 800,
    height: 540,
    surfaces: [
      { x: 80, y: 60, w: 180, h: 320 },    // vertical section
      { x: 260, y: 240, w: 360, h: 160 },  // horizontal section
    ],
    walls: [
      // Vertical section
      { x: 80, y: 60, w: 180, h: W },       // top
      { x: 80, y: 60, w: W, h: 340 },       // left
      { x: 240, y: 60, w: W, h: 180 },      // right top (up to corner)
      { x: 80, y: 386, w: 180, h: W },      // bottom of vertical (only left part)
      // Horizontal section
      { x: 260, y: 240, w: 360, h: W },     // top of horizontal
      { x: 260, y: 386, w: 360, h: W },     // bottom
      { x: 606, y: 240, w: W, h: 160 },     // right
      // Inner corner wall
      { x: 240, y: 386, w: W, h: W },       // inner corner piece to close gap
    ],
    circleObstacles: [],
    movingObstacles: [],
    waterHazards: [],
    startPos: { x: 170, y: 110 },
    holePos: { x: 560, y: 320 },
  },

  // ── HOLE 3 – "The Gap" (par 3) ─────────────────────────────────────────────
  {
    id: 3,
    name: 'The Gap',
    par: 3,
    width: 800,
    height: 540,
    surfaces: [{ x: 80, y: 180, w: 640, h: 180 }],
    walls: [
      { x: 80, y: 180, w: 640, h: W },  // top
      { x: 80, y: 346, w: 640, h: W },  // bottom
      { x: 80, y: 180, w: W, h: 180 },  // left
      { x: 706, y: 180, w: W, h: 180 }, // right
      // Gap walls (two pairs creating a 60px gap each)
      { x: 280, y: 180, w: W, h: 70 },  // left barrier top
      { x: 280, y: 296, w: W, h: 64 },  // left barrier bottom
      { x: 480, y: 180, w: W, h: 70 },  // right barrier top
      { x: 480, y: 296, w: W, h: 64 },  // right barrier bottom
    ],
    circleObstacles: [],
    movingObstacles: [],
    waterHazards: [],
    startPos: { x: 140, y: 270 },
    holePos: { x: 660, y: 270 },
  },

  // ── HOLE 4 – "Zigzag" (par 4) ──────────────────────────────────────────────
  {
    id: 4,
    name: 'Zigzag',
    par: 4,
    width: 800,
    height: 540,
    surfaces: [
      { x: 80, y: 60, w: 220, h: 140 },   // top-left
      { x: 200, y: 200, w: 320, h: 140 }, // middle
      { x: 400, y: 340, w: 220, h: 140 }, // bottom-right
    ],
    walls: [
      // Top-left section
      { x: 80, y: 60, w: 220, h: W },
      { x: 80, y: 60, w: W, h: 140 },
      { x: 286, y: 60, w: W, h: 140 },
      { x: 80, y: 186, w: 120, h: W },    // bottom left part only (opening on right)
      // Middle section
      { x: 200, y: 200, w: 320, h: W },
      { x: 200, y: 326, w: 200, h: W },   // bottom left (opening on right)
      { x: 506, y: 200, w: W, h: 140 },
      // Bottom-right section
      { x: 400, y: 340, w: W, h: 140 },   // top left part
      { x: 400, y: 466, w: 220, h: W },
      { x: 606, y: 340, w: W, h: 140 },
      { x: 400, y: 340, w: 120, h: W },   // top (partial, opening connects to middle)
    ],
    circleObstacles: [],
    movingObstacles: [],
    waterHazards: [],
    startPos: { x: 140, y: 130 },
    holePos: { x: 560, y: 410 },
  },

  // ── HOLE 5 – "Bumper Alley" (par 3) ────────────────────────────────────────
  {
    id: 5,
    name: 'Bumper Alley',
    par: 3,
    width: 800,
    height: 540,
    surfaces: [{ x: 80, y: 180, w: 640, h: 180 }],
    walls: [
      { x: 80, y: 180, w: 640, h: W },
      { x: 80, y: 346, w: 640, h: W },
      { x: 80, y: 180, w: W, h: 180 },
      { x: 706, y: 180, w: W, h: 180 },
    ],
    circleObstacles: [
      { cx: 260, cy: 230, r: 20, isBumper: true },
      { cx: 400, cy: 310, r: 20, isBumper: true },
      { cx: 540, cy: 230, r: 20, isBumper: true },
      { cx: 330, cy: 270, r: 16, isBumper: false },
      { cx: 470, cy: 270, r: 16, isBumper: false },
    ],
    movingObstacles: [],
    waterHazards: [],
    startPos: { x: 140, y: 270 },
    holePos: { x: 660, y: 270 },
  },

  // ── HOLE 6 – "The Gauntlet" (par 4) ────────────────────────────────────────
  {
    id: 6,
    name: 'The Gauntlet',
    par: 4,
    width: 800,
    height: 540,
    surfaces: [{ x: 80, y: 100, w: 640, h: 340 }],
    walls: [
      { x: 80, y: 100, w: 640, h: W },
      { x: 80, y: 426, w: 640, h: W },
      { x: 80, y: 100, w: W, h: 340 },
      { x: 706, y: 100, w: W, h: 340 },
      // Slalom walls (alternating from top and bottom, leaving 80px gaps)
      { x: 220, y: 100, w: W, h: 240 },   // from top
      { x: 370, y: 200, w: W, h: 240 },   // from bottom
      { x: 520, y: 100, w: W, h: 240 },   // from top
    ],
    circleObstacles: [],
    movingObstacles: [],
    waterHazards: [],
    startPos: { x: 140, y: 270 },
    holePos: { x: 660, y: 270 },
  },

  // ── HOLE 7 – "Moving Target" (par 4) ───────────────────────────────────────
  {
    id: 7,
    name: 'Moving Target',
    par: 4,
    width: 800,
    height: 540,
    surfaces: [{ x: 80, y: 180, w: 640, h: 180 }],
    walls: [
      { x: 80, y: 180, w: 640, h: W },
      { x: 80, y: 346, w: 640, h: W },
      { x: 80, y: 180, w: W, h: 180 },
      { x: 706, y: 180, w: W, h: 180 },
    ],
    circleObstacles: [
      { cx: 400, cy: 270, r: 18, isBumper: false },
    ],
    movingObstacles: [
      { cx: 260, cy: 270, r: 22, axis: 'y', range: 60, speed: 1.8 },
      { cx: 540, cy: 270, r: 22, axis: 'y', range: 60, speed: 2.2 },
    ],
    waterHazards: [],
    startPos: { x: 140, y: 270 },
    holePos: { x: 660, y: 270 },
  },

  // ── HOLE 8 – "Island Green" (par 4) ────────────────────────────────────────
  {
    id: 8,
    name: 'Island Green',
    par: 4,
    width: 800,
    height: 540,
    surfaces: [
      { x: 80, y: 220, w: 200, h: 100 },   // tee platform
      { x: 360, y: 180, w: 200, h: 180 },  // island green
      { x: 640, y: 220, w: 80, h: 100 },   // cup platform
    ],
    walls: [
      // Tee platform
      { x: 80, y: 220, w: 200, h: W },
      { x: 80, y: 306, w: 200, h: W },
      { x: 80, y: 220, w: W, h: 100 },
      { x: 266, y: 220, w: W, h: 100 },
      // Island green
      { x: 360, y: 180, w: 200, h: W },
      { x: 360, y: 346, w: 200, h: W },
      { x: 360, y: 180, w: W, h: 180 },
      { x: 546, y: 180, w: W, h: 180 },
      // Cup platform
      { x: 640, y: 220, w: 80, h: W },
      { x: 640, y: 306, w: 80, h: W },
      { x: 706, y: 220, w: W, h: 100 },
    ],
    circleObstacles: [],
    movingObstacles: [
      { cx: 310, cy: 270, r: 16, axis: 'y', range: 30, speed: 2.5 },
      { cx: 595, cy: 270, r: 16, axis: 'y', range: 30, speed: 2.5 },
    ],
    waterHazards: [
      { x: 280, y: 180, w: 80, h: 180 },  // water between tee and island
      { x: 560, y: 180, w: 80, h: 180 },  // water between island and cup
    ],
    startPos: { x: 140, y: 270 },
    holePos: { x: 680, y: 270 },
  },

  // ── HOLE 9 – "Grand Finale" (par 5) ────────────────────────────────────────
  {
    id: 9,
    name: 'Grand Finale',
    par: 5,
    width: 800,
    height: 540,
    surfaces: [
      { x: 80, y: 60, w: 160, h: 160 },    // start room
      { x: 160, y: 180, w: 480, h: 100 },  // top corridor
      { x: 560, y: 60, w: 160, h: 220 },   // right room
      { x: 400, y: 260, w: 320, h: 120 },  // right-bottom corridor
      { x: 80, y: 260, w: 400, h: 120 },   // bottom-left corridor
      { x: 80, y: 360, w: 200, h: 120 },   // bottom-left room
    ],
    walls: [
      // Start room
      { x: 80, y: 60, w: 160, h: W },
      { x: 80, y: 60, w: W, h: 160 },
      { x: 226, y: 60, w: W, h: 120 },     // right side of start room (partial)
      // Top corridor
      { x: 160, y: 180, w: 480, h: W },
      { x: 160, y: 266, w: 400, h: W },    // bottom (partial)
      // Right room
      { x: 560, y: 60, w: 160, h: W },
      { x: 706, y: 60, w: W, h: 320 },
      { x: 560, y: 266, w: W, h: 114 },    // left side of right room bottom
      // Right-bottom corridor
      { x: 560, y: 366, w: 160, h: W },    // bottom of right room extension
      { x: 400, y: 366, w: 160, h: W },
      { x: 400, y: 260, w: W, h: 120 },
      // Bottom left corridor
      { x: 80, y: 260, w: W, h: 120 },     // left side
      { x: 80, y: 366, w: 320, h: W },     // bottom (partial, for left corridor)
      // Bottom-left room
      { x: 80, y: 466, w: 200, h: W },
      { x: 266, y: 360, w: W, h: 120 },
    ],
    circleObstacles: [
      { cx: 420, cy: 225, r: 16, isBumper: true },
      { cx: 500, cy: 225, r: 16, isBumper: true },
    ],
    movingObstacles: [
      { cx: 300, cy: 315, r: 20, axis: 'x', range: 80, speed: 2.0 },
      { cx: 580, cy: 315, r: 18, axis: 'y', range: 40, speed: 2.4 },
    ],
    waterHazards: [],
    startPos: { x: 140, y: 130 },
    holePos: { x: 160, y: 420 },
  },
];
