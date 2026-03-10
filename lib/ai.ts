import { Vector2D, CourseHole, Difficulty } from '@/types/game';
import { MAX_POWER } from './physics';

export interface AIShot {
  angle: number;
  power: number; // 0–1
}

function distanceTo(a: Vector2D, b: Vector2D): number {
  return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2);
}

function clamp(val: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, val));
}

// Calculate the ideal shot toward the hole
export function calculateAIShot(
  ballPos: Vector2D,
  holePos: Vector2D,
  hole: CourseHole,
  difficulty: Difficulty
): AIShot {
  // Ideal angle directly to hole
  const idealAngle = Math.atan2(holePos.y - ballPos.y, holePos.x - ballPos.x);
  const dist = distanceTo(ballPos, holePos);

  // Ideal power: scale by distance (max distance ~700px = full power)
  const idealPower = clamp(dist / 500, 0.2, 1.0);

  // Apply deviation based on difficulty
  let angleDeviation: number;
  let powerDeviation: number;

  switch (difficulty) {
    case 'easy':
      angleDeviation = (Math.random() - 0.5) * 0.7; // ±0.35 radians (~20°)
      powerDeviation = (Math.random() - 0.5) * 0.5;
      break;
    case 'medium':
      angleDeviation = (Math.random() - 0.5) * 0.35; // ±0.175 radians (~10°)
      powerDeviation = (Math.random() - 0.5) * 0.25;
      break;
    case 'hard':
      angleDeviation = (Math.random() - 0.5) * 0.12; // ±0.06 radians (~3.5°)
      powerDeviation = (Math.random() - 0.5) * 0.1;
      break;
    default:
      angleDeviation = (Math.random() - 0.5) * 0.35;
      powerDeviation = (Math.random() - 0.5) * 0.25;
  }

  // hole is used for potential future wall-aware AI
  void hole;

  return {
    angle: idealAngle + angleDeviation,
    power: clamp(idealPower + powerDeviation, 0.15, 1.0),
  };
}

// Convert shot to velocity
export function shotToVelocity(shot: AIShot): Vector2D {
  const speed = shot.power * MAX_POWER;
  return {
    x: Math.cos(shot.angle) * speed,
    y: Math.sin(shot.angle) * speed,
  };
}
