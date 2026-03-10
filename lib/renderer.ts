import { Rect, CircleObstacle, MovingObstacle, WaterHazard, Vector2D } from '@/types/game';
import { BALL_RADIUS, HOLE_RADIUS } from './physics';

export interface RenderState {
  ballPos: Vector2D;
  holePos: Vector2D;
  surfaces: Rect[];
  walls: Rect[];
  circleObstacles: CircleObstacle[];
  movingObstacles: MovingObstacle[];
  waterHazards: WaterHazard[];
  aimStart: Vector2D | null;
  aimEnd: Vector2D | null;
  isAiming: boolean;
  flagAngle: number;
  ballInHole: boolean;
  aiPos: Vector2D | null;
  aiInHole: boolean;
}

function drawGreenTexture(ctx: CanvasRenderingContext2D, rect: Rect) {
  ctx.fillStyle = '#0d3320';
  ctx.fillRect(rect.x, rect.y, rect.w, rect.h);

  // Subtle grid lines for felt texture
  ctx.strokeStyle = 'rgba(0,255,136,0.06)';
  ctx.lineWidth = 1;
  const gridSize = 20;
  for (let x = rect.x; x < rect.x + rect.w; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, rect.y);
    ctx.lineTo(x, rect.y + rect.h);
    ctx.stroke();
  }
  for (let y = rect.y; y < rect.y + rect.h; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(rect.x, y);
    ctx.lineTo(rect.x + rect.w, y);
    ctx.stroke();
  }
}

function drawWall(ctx: CanvasRenderingContext2D, wall: Rect) {
  // Neon cyan wall with glow
  ctx.shadowColor = '#00ffff';
  ctx.shadowBlur = 8;
  ctx.fillStyle = '#00cccc';
  ctx.fillRect(wall.x, wall.y, wall.w, wall.h);
  ctx.shadowBlur = 0;

  // Highlight edge
  ctx.fillStyle = 'rgba(255,255,255,0.3)';
  ctx.fillRect(wall.x, wall.y, wall.w, 2);
  ctx.fillRect(wall.x, wall.y, 2, wall.h);
}

function drawHole(ctx: CanvasRenderingContext2D, pos: Vector2D, flagAngle: number) {
  // Hole cup (dark circle)
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, HOLE_RADIUS, 0, Math.PI * 2);
  ctx.fillStyle = '#000';
  ctx.fill();

  // Hole rim glow
  ctx.strokeStyle = '#00ff88';
  ctx.shadowColor = '#00ff88';
  ctx.shadowBlur = 12;
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.shadowBlur = 0;

  // Flagpole
  ctx.beginPath();
  ctx.moveTo(pos.x, pos.y);
  ctx.lineTo(pos.x, pos.y - 36);
  ctx.strokeStyle = '#888';
  ctx.lineWidth = 1.5;
  ctx.stroke();

  // Flag
  const fx = pos.x + Math.cos(flagAngle) * 14;
  const fy = pos.y - 36 + Math.sin(flagAngle) * 6;
  ctx.beginPath();
  ctx.moveTo(pos.x, pos.y - 36);
  ctx.lineTo(fx, fy);
  ctx.lineTo(pos.x, pos.y - 26);
  ctx.fillStyle = '#ff0066';
  ctx.fill();
}

function drawBall(ctx: CanvasRenderingContext2D, pos: Vector2D, color = '#ffffff') {
  // Shadow
  ctx.beginPath();
  ctx.arc(pos.x + 3, pos.y + 3, BALL_RADIUS, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(0,0,0,0.4)';
  ctx.fill();

  // Ball glow
  ctx.shadowColor = color;
  ctx.shadowBlur = 16;

  // Ball body
  const gradient = ctx.createRadialGradient(
    pos.x - 2, pos.y - 2, 1,
    pos.x, pos.y, BALL_RADIUS
  );
  gradient.addColorStop(0, '#ffffff');
  gradient.addColorStop(0.5, color);
  gradient.addColorStop(1, color === '#ffffff' ? '#cccccc' : color);

  ctx.beginPath();
  ctx.arc(pos.x, pos.y, BALL_RADIUS, 0, Math.PI * 2);
  ctx.fillStyle = gradient;
  ctx.fill();
  ctx.shadowBlur = 0;
}

function drawAimLine(
  ctx: CanvasRenderingContext2D,
  from: Vector2D,
  to: Vector2D
) {
  const dx = from.x - to.x;
  const dy = from.y - to.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const maxDrag = 120;
  const clampedDist = Math.min(dist, maxDrag);
  const angle = Math.atan2(dy, dx);

  // Extend the aim line forward from the ball
  const lineLength = clampedDist * 2;
  const endX = from.x + Math.cos(angle) * lineLength;
  const endY = from.y + Math.sin(angle) * lineLength;

  // Dotted aim line
  ctx.setLineDash([6, 6]);
  ctx.strokeStyle = 'rgba(255,255,0,0.7)';
  ctx.shadowColor = '#ffff00';
  ctx.shadowBlur = 6;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(from.x, from.y);
  ctx.lineTo(endX, endY);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.shadowBlur = 0;

  // Power indicator bar
  const power = clampedDist / maxDrag;
  const barW = 80;
  const barH = 10;
  const barX = from.x - barW / 2;
  const barY = from.y - 40;

  ctx.fillStyle = 'rgba(0,0,0,0.5)';
  ctx.fillRect(barX - 2, barY - 2, barW + 4, barH + 4);

  const barColor = power < 0.4 ? '#00ff88' : power < 0.7 ? '#ffff00' : '#ff4444';
  ctx.fillStyle = barColor;
  ctx.shadowColor = barColor;
  ctx.shadowBlur = 8;
  ctx.fillRect(barX, barY, barW * power, barH);
  ctx.shadowBlur = 0;

  ctx.strokeStyle = 'rgba(255,255,255,0.3)';
  ctx.lineWidth = 1;
  ctx.strokeRect(barX - 2, barY - 2, barW + 4, barH + 4);
}

function drawBumper(ctx: CanvasRenderingContext2D, obs: CircleObstacle) {
  const color = obs.isBumper ? '#ff00ff' : '#ff6600';

  ctx.shadowColor = color;
  ctx.shadowBlur = 16;
  ctx.beginPath();
  ctx.arc(obs.cx, obs.cy, obs.r, 0, Math.PI * 2);
  ctx.fillStyle = obs.isBumper ? '#660066' : '#663300';
  ctx.fill();
  ctx.strokeStyle = color;
  ctx.lineWidth = 3;
  ctx.stroke();
  ctx.shadowBlur = 0;
}

function drawMovingObstacle(ctx: CanvasRenderingContext2D, obs: MovingObstacle) {
  const offset = obs._offset ?? 0;
  const cx = obs.cx + (obs.axis === 'x' ? offset : 0);
  const cy = obs.cy + (obs.axis === 'y' ? offset : 0);

  ctx.shadowColor = '#ff4444';
  ctx.shadowBlur = 16;
  ctx.beginPath();
  ctx.arc(cx, cy, obs.r, 0, Math.PI * 2);
  ctx.fillStyle = '#440000';
  ctx.fill();
  ctx.strokeStyle = '#ff4444';
  ctx.lineWidth = 3;
  ctx.stroke();
  ctx.shadowBlur = 0;

  // Motion trail
  const dir = obs._dir ?? 1;
  for (let i = 1; i <= 3; i++) {
    const trailCx = cx - (obs.axis === 'x' ? obs.speed * dir * i * 3 : 0);
    const trailCy = cy - (obs.axis === 'y' ? obs.speed * dir * i * 3 : 0);
    ctx.beginPath();
    ctx.arc(trailCx, trailCy, obs.r * (1 - i * 0.25), 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255, 68, 68, ${0.15 - i * 0.04})`;
    ctx.fill();
  }
}

function drawWaterHazard(ctx: CanvasRenderingContext2D, h: WaterHazard, time: number) {
  ctx.fillStyle = '#001a33';
  ctx.fillRect(h.x, h.y, h.w, h.h);

  // Animated ripple
  ctx.strokeStyle = `rgba(0, 100, 255, ${0.3 + Math.sin(time * 0.05) * 0.2})`;
  ctx.lineWidth = 1;
  const rippleCount = 3;
  for (let i = 0; i < rippleCount; i++) {
    const rx = h.x + h.w / 2 + Math.sin(time * 0.02 + i * 2) * (h.w * 0.2);
    const ry = h.y + h.h / 2;
    const rr = 15 + i * 10 + ((time * 0.5 + i * 20) % 30);
    ctx.beginPath();
    ctx.ellipse(rx, ry, rr, rr * 0.4, 0, 0, Math.PI * 2);
    ctx.stroke();
  }

  ctx.fillStyle = 'rgba(0, 100, 255, 0.15)';
  ctx.fillRect(h.x, h.y, h.w, h.h);
}

export function renderFrame(
  ctx: CanvasRenderingContext2D,
  state: RenderState,
  time: number,
  width: number,
  height: number
) {
  // Background (out of bounds / rough)
  ctx.fillStyle = '#0a0a1a';
  ctx.fillRect(0, 0, width, height);

  // Rough border texture
  ctx.strokeStyle = 'rgba(0,255,136,0.03)';
  const roughSize = 30;
  for (let x = 0; x < width; x += roughSize) {
    for (let y = 0; y < height; y += roughSize) {
      if ((x / roughSize + y / roughSize) % 2 === 0) {
        ctx.fillStyle = 'rgba(20, 40, 20, 0.3)';
        ctx.fillRect(x, y, roughSize, roughSize);
      }
    }
  }

  // Water hazards (behind surfaces)
  state.waterHazards.forEach((h) => drawWaterHazard(ctx, h, time));

  // Green surfaces
  state.surfaces.forEach((s) => drawGreenTexture(ctx, s));

  // Walls
  state.walls.forEach((w) => drawWall(ctx, w));

  // Circle obstacles / bumpers
  state.circleObstacles.forEach((obs) => drawBumper(ctx, obs));

  // Moving obstacles
  state.movingObstacles.forEach((obs) => drawMovingObstacle(ctx, obs));

  // Hole
  drawHole(ctx, state.holePos, state.flagAngle);

  // AI ball
  if (state.aiPos && !state.aiInHole) {
    drawBall(ctx, state.aiPos, '#ff6600');
  }

  // Player ball
  if (!state.ballInHole) {
    drawBall(ctx, state.ballPos, '#ffffff');
  }

  // Aim line
  if (state.isAiming && state.aimStart && state.aimEnd) {
    drawAimLine(ctx, state.aimStart, state.aimEnd);
  }
}
