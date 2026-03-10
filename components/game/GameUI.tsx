'use client';
import { COURSES } from '@/lib/courses';
import { ScoreEntry } from '@/types/game';

interface GameUIProps {
  currentHoleIndex: number;
  playerStrokes: number;
  aiStrokes: number | null;
  scores: ScoreEntry[];
  onPause: () => void;
  soundEnabled: boolean;
  onToggleSound: () => void;
  isVsAI: boolean;
}

export function GameUI({
  currentHoleIndex,
  playerStrokes,
  aiStrokes,
  scores,
  onPause,
  soundEnabled,
  onToggleSound,
  isVsAI,
}: GameUIProps) {
  const hole = COURSES[currentHoleIndex];
  const totalScore = scores.reduce((s, e) => s + e.playerStrokes, 0) + playerStrokes;
  const totalPar = COURSES.slice(0, currentHoleIndex).reduce((s, h) => s + h.par, 0) + hole.par;
  const diff = totalScore - totalPar;

  return (
    <div className="absolute inset-x-0 top-0 z-20 flex items-center justify-between px-4 py-2 bg-gradient-to-b from-black/70 to-transparent">
      {/* Left: hole info */}
      <div className="flex flex-col">
        <span className="text-[#00ffff] text-xs uppercase tracking-widest">
          Hole {hole.id} / {COURSES.length}
        </span>
        <span className="text-white font-bold text-sm">{hole.name}</span>
        <span className="text-white/50 text-xs">Par {hole.par}</span>
      </div>

      {/* Center: stroke counter */}
      <div className="text-center">
        <span className="block text-white/40 text-xs uppercase tracking-widest">Strokes</span>
        <span className="text-3xl font-black text-white">{playerStrokes}</span>
        {isVsAI && aiStrokes !== null && (
          <span className="block text-orange-400 text-xs">AI: {aiStrokes}</span>
        )}
      </div>

      {/* Right: total score + controls */}
      <div className="flex flex-col items-end gap-1">
        <div className="flex gap-2">
          <button onClick={onToggleSound} className="text-white/50 hover:text-white text-sm transition-colors">
            {soundEnabled ? 'SND' : 'MUT'}
          </button>
          <button
            onClick={onPause}
            className="text-white/50 hover:text-white text-sm transition-colors px-2 py-0.5 border border-white/20 rounded"
          >
            II
          </button>
        </div>
        <span className="text-white/40 text-xs">
          Total: {totalScore} ({diff >= 0 ? '+' : ''}{diff})
        </span>
      </div>
    </div>
  );
}
