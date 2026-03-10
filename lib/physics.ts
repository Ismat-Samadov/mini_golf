import { Vector2D, Rect, CircleObstacle, MovingObstacle, WaterHazard } from '@/types/game';

export const BALL_RADIUS = 9;
export const HOLE_RADIUS = 13;
export const FRICTION = 0.982;
export const MIN_VELOCITY = 0.08;
export const MAX_POWER = 18;

export function distance(a: Vector2D, b: Vector2D): number {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
}

export function isMoving(vel: Vector2D): boolean {
  return Math.abs(vel.x) > MIN_VELOCITY || Math.abs(vel.y) > MIN_VELOCITY;
}

export function applyFriction(vel: Vector2D): Vector2D {
  return { x: vel.x * FRICTION, y: vel.y * FRICTION };
}

export function isBallInHole(ballPos: Vector2D, holePos: Vector2D): boolean {
  return distance(ballPos, holePos) < HOLE_RADIUS - BALL_RADIUS + 2;
}

// Ball vs Rectangle collision (axis-aligned)
export function resolveRectCollision(
  pos: Vector2D,
  vel: Vector2D,
  rect: Rect,
  restitution = 0.65
): { pos: Vector2D; vel: Vector2D; collided: boolean } {
  const r = BALL_RADIUS;
  const left = rect.x;
  const right = rect.x + rect.w;
  const top = rect.y;
  const bottom = rect.y + rect.h;

  // Check overlap
  if (pos.x + r <= left || pos.x - r >= right || pos.y + r <= top || pos.y - r >= bottom) {
    return { pos, vel, collided: false };
  }

  // Find minimum penetration axis
  const overlapLeft = pos.x + r - left;
  const overlapRight = right - (pos.x - r);
  const overlapTop = pos.y + r - top;
  const overlapBottom = bottom - (pos.y - r);

  const minOverlap = Math.min(overlapLeft, overlapRight, overlapTop, overlapBottom);

  let newPos = { ...pos };
  let newVel = { ...vel };

  if (minOverlap === overlapLeft) {
    newPos.x = left - r;
    newVel.x = -Math.abs(newVel.x) * restitution;
  } else if (minOverlap === overlapRight) {
    newPos.x = right + r;
    newVel.x = Math.abs(newVel.x) * restitution;
  } else if (minOverlap === overlapTop) {
    newPos.y = top - r;
    newVel.y = -Math.abs(newVel.y) * restitution;
  } else {
    newPos.y = bottom + r;
    newVel.y = Math.abs(newVel.y) * restitution;
  }

  return { pos: newPos, vel: newVel, collided: true };
}

// Ball vs Circle collision
export function resolveCircleCollision(
  pos: Vector2D,
  vel: Vector2D,
  cx: number,
  cy: number,
  r: number,
  restitution = 0.75
): { pos: Vector2D; vel: Vector2D; collided: boolean } {
  const dx = pos.x - cx;
  const dy = pos.y - cy;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const minDist = r + BALL_RADIUS;

  if (dist >= minDist) return { pos, vel, collided: false };
  if (dist === 0) return { pos: { x: pos.x + minDist, y: pos.y }, vel, collided: true };

  const nx = dx / dist;
  const ny = dy / dist;

  const newPos = { x: cx + nx * minDist, y: cy + ny * minDist };
  const dot = vel.x * nx + vel.y * ny;
  const newVel = {
    x: (vel.x - 2 * dot * nx) * restitution,
    y: (vel.y - 2 * dot * ny) * restitution,
  };

  return { pos: newPos, vel: newVel, collided: true };
}

export function isOnSurface(pos: Vector2D, surfaces: Rect[]): boolean {
  return surfaces.some(
    (s) =>
      pos.x - BALL_RADIUS >= s.x - 2 &&
      pos.x + BALL_RADIUS <= s.x + s.w + 2 &&
      pos.y - BALL_RADIUS >= s.y - 2 &&
      pos.y + BALL_RADIUS <= s.y + s.h + 2
  );
}

export function isInWater(pos: Vector2D, hazards: WaterHazard[]): boolean {
  return hazards.some(
    (h) => pos.x > h.x && pos.x < h.x + h.w && pos.y > h.y && pos.y < h.y + h.h
  );
}

// Step the physics simulation by one frame
export function stepPhysics(
  pos: Vector2D,
  vel: Vector2D,
  walls: Rect[],
  circleObstacles: CircleObstacle[],
  movingObstacles: MovingObstacle[]
): { pos: Vector2D; vel: Vector2D } {
  let p = { x: pos.x + vel.x, y: pos.y + vel.y };
  let v = applyFriction(vel);

  // Wall collisions
  for (const wall of walls) {
    const result = resolveRectCollision(p, v, wall);
    if (result.collided) {
      p = result.pos;
      v = result.vel;
    }
  }

  // Circle obstacle collisions
  for (const obs of circleObstacles) {
    const restitution = obs.isBumper ? 1.1 : 0.7;
    const result = resolveCircleCollision(p, v, obs.cx, obs.cy, obs.r, restitution);
    if (result.collided) {
      p = result.pos;
      v = result.vel;
    }
  }

  // Moving obstacle collisions
  for (const obs of movingObstacles) {
    const result = resolveCircleCollision(p, v, obs.cx + (obs._offset ?? 0) * (obs.axis === 'x' ? 1 : 0), obs.cy + (obs._offset ?? 0) * (obs.axis === 'y' ? 1 : 0), obs.r, 0.8);
    if (result.collided) {
      p = result.pos;
      v = result.vel;
    }
  }

  return { pos: p, vel: v };
}

// Update moving obstacles positions
export function stepMovingObstacles(obstacles: MovingObstacle[]): MovingObstacle[] {
  return obstacles.map((obs) => {
    const offset = obs._offset ?? 0;
    const dir = obs._dir ?? 1;
    let newOffset = offset + obs.speed * dir;
    let newDir = dir;
    if (newOffset >= obs.range) {
      newOffset = obs.range;
      newDir = -1;
    } else if (newOffset <= -obs.range) {
      newOffset = -obs.range;
      newDir = 1;
    }
    return { ...obs, _offset: newOffset, _dir: newDir };
  });
}
