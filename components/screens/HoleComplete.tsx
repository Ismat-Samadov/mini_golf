'use client';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { ScoreEntry } from '@/types/game';
import { formatScore, scoreColor } from '@/lib/utils';

interface HoleCompleteProps {
  score: ScoreEntry;
  onNext: () => void;
  holeNumber: number;
  totalHoles: number;
}

export function HoleComplete({ score, onNext, holeNumber, totalHoles }: HoleCompleteProps) {
  const label = formatScore(score.playerStrokes, score.par);
  const color = scoreColor(score.playerStrokes, score.par);

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
      <motion.div
        initial={{ scale: 0.7, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', damping: 15, stiffness: 200 }}
        className="bg-[#0a0a1a] border border-[#00ff88]/40 rounded-2xl p-8 mx-4 max-w-sm w-full text-center shadow-[0_0_60px_rgba(0,255,136,0.2)]"
      >
        <p className="text-white/50 text-xs uppercase tracking-widest mb-2">
          Hole {holeNumber} / {totalHoles} Complete
        </p>
        <h2 className="text-5xl font-black mb-1 text-[#00ff88]" style={{ textShadow: '0 0 20px rgba(0,255,136,0.6)' }}>
          {label}
        </h2>
        <p className="text-white/40 text-sm mb-6">
          {score.playerStrokes} stroke{score.playerStrokes !== 1 ? 's' : ''} / Par {score.par}
        </p>

        {score.aiStrokes !== null && (
          <div className="mb-6 flex justify-center gap-8 text-sm">
            <div>
              <p className="text-white/40">You</p>
              <p className={`text-xl font-bold ${color}`}>{score.playerStrokes}</p>
            </div>
            <div>
              <p className="text-white/40">AI</p>
              <p className={`text-xl font-bold ${scoreColor(score.aiStrokes, score.par)}`}>{score.aiStrokes}</p>
            </div>
          </div>
        )}

        <Button onClick={onNext} className="w-full">
          {holeNumber < totalHoles ? 'Next Hole' : 'See Final Score'}
        </Button>
      </motion.div>
    </div>
  );
}
