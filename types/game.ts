export interface Vector2D {
  x: number;
  y: number;
}

export interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface CircleObstacle {
  cx: number;
  cy: number;
  r: number;
  isBumper: boolean; // bumpers have higher bounce coefficient
}

export interface MovingObstacle {
  cx: number;
  cy: number;
  r: number;
  axis: 'x' | 'y';
  range: number;    // pixels to move in each direction
  speed: number;    // pixels per frame
  // runtime state (initialized from cx/cy)
  _offset?: number;
  _dir?: number;
}

export interface WaterHazard {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface CourseHole {
  id: number;
  name: string;
  par: number;
  width: number;
  height: number;
  surfaces: Rect[];          // green playable areas (visual)
  walls: Rect[];             // solid boundary walls
  circleObstacles: CircleObstacle[];
  movingObstacles: MovingObstacle[];
  waterHazards: WaterHazard[];
  startPos: Vector2D;
  holePos: Vector2D;
}

export type BallState = 'idle' | 'aiming' | 'rolling' | 'in_hole' | 'penalty';

export interface BallData {
  pos: Vector2D;
  vel: Vector2D;
  state: BallState;
  strokes: number;
  lastSafePos: Vector2D;
}

export type GameMode = 'solo' | 'vs_ai';
export type Difficulty = 'easy' | 'medium' | 'hard';
export type GameScreen = 'start' | 'playing' | 'hole_complete' | 'paused' | 'game_over';

export interface ScoreEntry {
  hole: number;
  par: number;
  playerStrokes: number;
  aiStrokes: number | null;
}

export interface HighScore {
  name: string;
  totalStrokes: number;
  date: string;
}
