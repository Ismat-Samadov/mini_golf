'use client';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { GameMode, Difficulty, HighScore } from '@/types/game';

interface StartScreenProps {
  onStart: (mode: GameMode, difficulty: Difficulty) => void;
  highScores: HighScore[];
  soundEnabled: boolean;
  onToggleSound: () => void;
}

export function StartScreen({ onStart, highScores, soundEnabled, onToggleSound }: StartScreenProps) {
  const [mode, setMode] = useState<GameMode>('solo');
  const [difficulty, setDifficulty] = useState<Difficulty>('medium');

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#0a0a1a] text-white px-4">
      {/* Animated background grid */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage:
              'linear-gradient(rgba(0,255,136,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,136,0.05) 1px, transparent 1px)',
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 flex flex-col items-center gap-8 w-full max-w-md"
      >
        {/* Title */}
        <div className="text-center">
          <motion.h1
            className="text-6xl font-black tracking-widest mb-2"
            style={{
              color: '#00ff88',
              textShadow: '0 0 30px rgba(0,255,136,0.8), 0 0 60px rgba(0,255,136,0.4)',
            }}
            animate={{ textShadow: ['0 0 30px rgba(0,255,136,0.8), 0 0 60px rgba(0,255,136,0.4)', '0 0 20px rgba(0,255,136,0.4), 0 0 40px rgba(0,255,136,0.2)', '0 0 30px rgba(0,255,136,0.8), 0 0 60px rgba(0,255,136,0.4)'] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            NEON GOLF
          </motion.h1>
          <p className="text-[#00ffff]/60 text-sm tracking-[0.3em] uppercase">Cyberpunk Mini Golf</p>
        </div>

        {/* Mode selection */}
        <div className="w-full">
          <p className="text-center text-white/50 text-xs uppercase tracking-widest mb-3">Game Mode</p>
          <div className="flex gap-3">
            {(['solo', 'vs_ai'] as GameMode[]).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 py-3 rounded-lg border-2 font-bold transition-all ${
                  mode === m
                    ? 'border-[#00ff88] text-[#00ff88] bg-[#00ff88]/10 shadow-[0_0_16px_rgba(0,255,136,0.4)]'
                    : 'border-white/20 text-white/50 hover:border-white/40'
                }`}
              >
                {m === 'solo' ? 'Solo' : 'vs AI'}
              </button>
            ))}
          </div>
        </div>

        {/* Difficulty selection */}
        <div className="w-full">
          <p className="text-center text-white/50 text-xs uppercase tracking-widest mb-3">Difficulty</p>
          <div className="flex gap-2">
            {(['easy', 'medium', 'hard'] as Difficulty[]).map((d) => {
              const colors = {
                easy: { active: 'border-green-400 text-green-400 bg-green-400/10 shadow-[0_0_16px_rgba(74,222,128,0.4)]', inactive: 'border-white/20 text-white/50' },
                medium: { active: 'border-yellow-400 text-yellow-400 bg-yellow-400/10 shadow-[0_0_16px_rgba(250,204,21,0.4)]', inactive: 'border-white/20 text-white/50' },
                hard: { active: 'border-red-400 text-red-400 bg-red-400/10 shadow-[0_0_16px_rgba(248,113,113,0.4)]', inactive: 'border-white/20 text-white/50' },
              };
              return (
                <button
                  key={d}
                  onClick={() => setDifficulty(d)}
                  className={`flex-1 py-2.5 rounded-lg border-2 font-bold capitalize transition-all text-sm ${
                    difficulty === d ? colors[d].active : colors[d].inactive
                  }`}
                >
                  {d}
                </button>
              );
            })}
          </div>
        </div>

        {/* Start button */}
        <Button size="lg" onClick={() => onStart(mode, difficulty)} className="w-full">
          TEE OFF
        </Button>

        {/* Sound toggle */}
        <button
          onClick={onToggleSound}
          className="text-white/40 hover:text-white/80 transition-colors text-sm flex items-center gap-2"
        >
          Sound {soundEnabled ? 'On' : 'Off'}
        </button>

        {/* High scores */}
        {highScores.length > 0 && (
          <div className="w-full border border-white/10 rounded-lg p-4 bg-white/5">
            <p className="text-center text-[#00ffff]/60 text-xs uppercase tracking-widest mb-3">High Scores</p>
            <div className="space-y-1">
              {highScores.slice(0, 5).map((hs, i) => (
                <div key={i} className="flex justify-between text-sm">
                  <span className="text-white/60">{i + 1}. {hs.name}</span>
                  <span className="text-[#00ff88]">{hs.totalStrokes} strokes</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
