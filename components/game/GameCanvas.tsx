'use client';
import { useRef, useEffect, useCallback } from 'react';
import { CourseHole, BallData, Vector2D, GameMode, Difficulty, MovingObstacle } from '@/types/game';
import {
  BALL_RADIUS,
  MAX_POWER,
  stepPhysics,
  stepMovingObstacles,
  isBallInHole,
  isMoving,
  isOnSurface,
  isInWater,
} from '@/lib/physics';
import { renderFrame, RenderState } from '@/lib/renderer';
import { calculateAIShot, shotToVelocity } from '@/lib/ai';
import { useSound } from '@/hooks/useSound';

const MAX_DRAG = 120;
const AI_SHOT_DELAY = 1200; // ms before AI shoots

interface GameCanvasProps {
  hole: CourseHole;
  mode: GameMode;
  difficulty: Difficulty;
  soundEnabled: boolean;
  onHoleComplete: (playerStrokes: number, aiStrokes: number | null) => void;
  onStrokesUpdate: (playerStrokes: number, aiStrokes: number | null) => void;
}

export function GameCanvas({
  hole,
  mode,
  difficulty,
  soundEnabled,
  onHoleComplete,
  onStrokesUpdate,
}: GameCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animFrameRef = useRef<number>(0);
  const playSound = useSound(soundEnabled);

  // Game state refs (mutable, used in animation loop)
  const ballRef = useRef<BallData>({
    pos: { ...hole.startPos },
    vel: { x: 0, y: 0 },
    state: 'idle',
    strokes: 0,
    lastSafePos: { ...hole.startPos },
  });

  const aiRef = useRef<{
    pos: Vector2D;
    vel: Vector2D;
    state: 'idle' | 'rolling' | 'in_hole';
    strokes: number;
    thinkTimer: number;
  } | null>(
    mode === 'vs_ai'
      ? {
          pos: { ...hole.startPos },
          vel: { x: 0, y: 0 },
          state: 'idle',
          strokes: 0,
          thinkTimer: 0,
        }
      : null
  );

  const movingObsRef = useRef<MovingObstacle[]>(
    hole.movingObstacles.map((obs) => ({ ...obs, _offset: 0, _dir: 1 as 1 | -1 }))
  );

  const aimRef = useRef<{ start: Vector2D | null; end: Vector2D | null; active: boolean }>({
    start: null,
    end: null,
    active: false,
  });

  const flagAngleRef = useRef(0);
  const completedRef = useRef(false);
  const scaleRef = useRef(1);
  const offsetRef = useRef<Vector2D>({ x: 0, y: 0 });

  // Convert screen coords to virtual canvas coords
  const toVirtual = useCallback((screenX: number, screenY: number): Vector2D => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: screenX, y: screenY };
    const rect = canvas.getBoundingClientRect();
    const x = (screenX - rect.left - offsetRef.current.x) / scaleRef.current;
    const y = (screenY - rect.top - offsetRef.current.y) / scaleRef.current;
    return { x, y };
  }, []);

  // Stroke callbacks with stable ref
  const onStrokesUpdateRef = useRef(onStrokesUpdate);
  onStrokesUpdateRef.current = onStrokesUpdate;
  const onHoleCompleteRef = useRef(onHoleComplete);
  onHoleCompleteRef.current = onHoleComplete;

  // ─── Aiming handlers ─────────────────────────────────────────────────────────
  const handlePointerDown = useCallback(
    (ex: number, ey: number) => {
      const ball = ballRef.current;
      if (ball.state !== 'idle') return;

      const vp = toVirtual(ex, ey);
      const dx = vp.x - ball.pos.x;
      const dy = vp.y - ball.pos.y;
      // Start aiming if clicking near the ball
      if (Math.sqrt(dx * dx + dy * dy) < BALL_RADIUS * 4) {
        aimRef.current = { start: { ...ball.pos }, end: vp, active: true };
        ball.state = 'aiming';
      }
    },
    [toVirtual]
  );

  const handlePointerMove = useCallback(
    (ex: number, ey: number) => {
      if (!aimRef.current.active) return;
      aimRef.current.end = toVirtual(ex, ey);
    },
    [toVirtual]
  );

  const handlePointerUp = useCallback(() => {
    const aim = aimRef.current;
    const ball = ballRef.current;
    if (!aim.active || !aim.start || !aim.end) return;

    const dx = aim.start.x - aim.end.x;
    const dy = aim.start.y - aim.end.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist > 5) {
      // Shoot ball opposite to drag direction
      const power = Math.min(dist / MAX_DRAG, 1.0);
      const speed = power * MAX_POWER;
      const angle = Math.atan2(dy, dx);
      ball.vel = { x: Math.cos(angle) * speed, y: Math.sin(angle) * speed };
      ball.state = 'rolling';
      ball.strokes += 1;
      playSound('shoot');
      onStrokesUpdateRef.current(ball.strokes, aiRef.current?.strokes ?? null);
    } else {
      ball.state = 'idle';
    }

    aim.active = false;
    aim.start = null;
    aim.end = null;
  }, [playSound]);

  // ─── Mouse events ────────────────────────────────────────────────────────────
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const onMouseDown = (e: MouseEvent) => handlePointerDown(e.clientX, e.clientY);
    const onMouseMove = (e: MouseEvent) => handlePointerMove(e.clientX, e.clientY);
    const onMouseUp = () => handlePointerUp();
    const onTouchStart = (e: TouchEvent) => {
      e.preventDefault();
      const t = e.touches[0];
      handlePointerDown(t.clientX, t.clientY);
    };
    const onTouchMove = (e: TouchEvent) => {
      e.preventDefault();
      const t = e.touches[0];
      handlePointerMove(t.clientX, t.clientY);
    };
    const onTouchEnd = (e: TouchEvent) => {
      e.preventDefault();
      handlePointerUp();
    };

    canvas.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('touchstart', onTouchStart, { passive: false });
    canvas.addEventListener('touchmove', onTouchMove, { passive: false });
    canvas.addEventListener('touchend', onTouchEnd, { passive: false });

    return () => {
      canvas.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      canvas.removeEventListener('touchstart', onTouchStart);
      canvas.removeEventListener('touchmove', onTouchMove);
      canvas.removeEventListener('touchend', onTouchEnd);
    };
  }, [handlePointerDown, handlePointerMove, handlePointerUp]);

  // ─── Game loop ────────────────────────────────────────────────────────────────
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Reset state when hole changes
    ballRef.current = {
      pos: { ...hole.startPos },
      vel: { x: 0, y: 0 },
      state: 'idle',
      strokes: 0,
      lastSafePos: { ...hole.startPos },
    };
    if (aiRef.current) {
      aiRef.current = {
        pos: { ...hole.startPos },
        vel: { x: 0, y: 0 },
        state: 'idle',
        strokes: 0,
        thinkTimer: 0,
      };
    }
    movingObsRef.current = hole.movingObstacles.map((obs) => ({
      ...obs,
      _offset: 0,
      _dir: 1 as 1 | -1,
    }));
    completedRef.current = false;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let aiShotScheduled = false;

    const loop = (timestamp: number) => {
      flagAngleRef.current = Math.sin(timestamp * 0.003) * 0.4;

      // Resize canvas to container
      const container = canvas.parentElement!;
      const cw = container.clientWidth;
      const ch = container.clientHeight;

      if (canvas.width !== cw || canvas.height !== ch) {
        canvas.width = cw;
        canvas.height = ch;
      }

      // Calculate scale and offset to fit virtual canvas inside real canvas
      const scaleX = cw / hole.width;
      const scaleY = ch / hole.height;
      const scale = Math.min(scaleX, scaleY);
      scaleRef.current = scale;
      const offsetX = (cw - hole.width * scale) / 2;
      const offsetY = (ch - hole.height * scale) / 2;
      offsetRef.current = { x: offsetX, y: offsetY };

      // ── Physics update ───────────────────────────────────────────────────────
      const ball = ballRef.current;
      const ai = aiRef.current;
      const movingObs = movingObsRef.current;

      // Update moving obstacles
      movingObsRef.current = stepMovingObstacles(movingObs);

      // Player ball physics
      if (ball.state === 'rolling') {
        const prevVel = { ...ball.vel };
        const result = stepPhysics(ball.pos, ball.vel, hole.walls, hole.circleObstacles, movingObsRef.current);
        ball.pos = result.pos;
        ball.vel = result.vel;

        // Wall bounce sound (detect significant velocity change)
        const velChangeSq = (result.vel.x - prevVel.x) ** 2 + (result.vel.y - prevVel.y) ** 2;
        if (velChangeSq > 1) playSound('bounce');

        // Water hazard check
        if (isInWater(ball.pos, hole.waterHazards)) {
          playSound('water');
          ball.pos = { ...ball.lastSafePos };
          ball.vel = { x: 0, y: 0 };
          ball.strokes += 2; // penalty
          ball.state = 'idle';
          onStrokesUpdateRef.current(ball.strokes, ai?.strokes ?? null);
        } else if (isOnSurface(ball.pos, hole.surfaces)) {
          ball.lastSafePos = { ...ball.pos };
        }

        // Check if ball in hole
        if (isBallInHole(ball.pos, hole.holePos)) {
          ball.state = 'in_hole';
          playSound('hole_in');
        } else if (!isMoving(ball.vel)) {
          ball.vel = { x: 0, y: 0 };
          ball.state = 'idle';
        }
      }

      // AI ball physics (only in vs_ai mode)
      if (ai) {
        if (ai.state === 'idle' && !aiShotScheduled && ball.state !== 'aiming') {
          // AI shoots after a delay
          aiShotScheduled = true;
          setTimeout(() => {
            if (ai.state === 'idle') {
              const shot = calculateAIShot(ai.pos, hole.holePos, hole, difficulty);
              ai.vel = shotToVelocity(shot);
              ai.state = 'rolling';
              ai.strokes += 1;
              onStrokesUpdateRef.current(ballRef.current.strokes, ai.strokes);
            }
            aiShotScheduled = false;
          }, AI_SHOT_DELAY + Math.random() * 500);
        }

        if (ai.state === 'rolling') {
          const result = stepPhysics(ai.pos, ai.vel, hole.walls, hole.circleObstacles, movingObsRef.current);
          ai.pos = result.pos;
          ai.vel = result.vel;

          if (isBallInHole(ai.pos, hole.holePos)) {
            ai.state = 'in_hole';
          } else if (!isMoving(ai.vel)) {
            ai.vel = { x: 0, y: 0 };
            ai.state = 'idle';
          }
        }

        // AI keeps trying until in hole (max 8 shots for AI sanity)
        if (ai.state === 'idle' && !isBallInHole(ai.pos, hole.holePos) && ai.strokes < 8 && !aiShotScheduled) {
          aiShotScheduled = true;
          setTimeout(() => {
            if (ai.state === 'idle') {
              const shot = calculateAIShot(ai.pos, hole.holePos, hole, difficulty);
              ai.vel = shotToVelocity(shot);
              ai.state = 'rolling';
              ai.strokes += 1;
              onStrokesUpdateRef.current(ballRef.current.strokes, ai.strokes);
            }
            aiShotScheduled = false;
          }, AI_SHOT_DELAY);
        }
      }

      // ── Hole completion check ────────────────────────────────────────────────
      const playerDone = ball.state === 'in_hole' || ball.strokes >= 10;
      const aiDone = !ai || ai.state === 'in_hole' || ai.strokes >= 8;

      if (playerDone && aiDone && !completedRef.current) {
        completedRef.current = true;
        const finalPlayerStrokes = ball.strokes >= 10 ? 10 : ball.strokes;
        const finalAiStrokes = ai ? (ai.strokes >= 8 ? 8 : ai.strokes) : null;
        setTimeout(() => {
          onHoleCompleteRef.current(finalPlayerStrokes, finalAiStrokes);
        }, 800);
      }

      // ── Render ───────────────────────────────────────────────────────────────
      const state: RenderState = {
        ballPos: ball.pos,
        holePos: hole.holePos,
        surfaces: hole.surfaces,
        walls: hole.walls,
        circleObstacles: hole.circleObstacles,
        movingObstacles: movingObsRef.current,
        waterHazards: hole.waterHazards,
        aimStart: aimRef.current.start,
        aimEnd: aimRef.current.end,
        isAiming: aimRef.current.active,
        flagAngle: flagAngleRef.current,
        ballInHole: ball.state === 'in_hole',
        aiPos: ai?.pos ?? null,
        aiInHole: ai ? ai.state === 'in_hole' : false,
      };

      ctx.save();
      ctx.translate(offsetX, offsetY);
      ctx.scale(scale, scale);
      renderFrame(ctx, state, timestamp, hole.width, hole.height);
      ctx.restore();

      animFrameRef.current = requestAnimationFrame(loop);
    };

    animFrameRef.current = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(animFrameRef.current);
    };
  }, [hole, difficulty, mode, playSound]);

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-full touch-none cursor-crosshair"
      style={{ display: 'block' }}
    />
  );
}
