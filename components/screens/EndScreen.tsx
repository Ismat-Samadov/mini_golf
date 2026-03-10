'use client';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { ScoreEntry, HighScore } from '@/types/game';
import { formatScore, scoreColor, totalPar, totalStrokes } from '@/lib/utils';
import { COURSES } from '@/lib/courses';

interface EndScreenProps {
  scores: ScoreEntry[];
  onRestart: () => void;
  onHighScoreSave: (name: string, score: number) => void;
  highScores: HighScore[];
}

export function EndScreen({ scores, onRestart, onHighScoreSave, highScores }: EndScreenProps) {
  const [name, setName] = useState('');
  const [saved, setSaved] = useState(false);

  const playerTotal = totalStrokes(scores);
  const parTotal = totalPar(COURSES);
  const diff = playerTotal - parTotal;
  const aiTotal = scores[0]?.aiStrokes !== null
    ? scores.reduce((s, e) => s + (e.aiStrokes ?? 0), 0)
    : null;

  const handleSave = () => {
    if (name.trim()) {
      onHighScoreSave(name.trim(), playerTotal);
      setSaved(true);
    }
  };

  // highScores used for future display — suppress unused warning
  void highScores;

  return (
    <div className="min-h-screen bg-[#0a0a1a] text-white flex flex-col items-center justify-center px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg"
      >
        <h1 className="text-4xl font-black text-center text-[#00ff88] mb-1" style={{ textShadow: '0 0 20px rgba(0,255,136,0.6)' }}>
          Round Complete!
        </h1>
        <p className="text-center text-white/50 mb-6">
          Total: <span className="text-white font-bold">{playerTotal}</span> strokes
          {' '}({diff >= 0 ? '+' : ''}{diff} vs par)
          {aiTotal !== null && <> &nbsp;|&nbsp; AI: <span className="text-orange-400 font-bold">{aiTotal}</span></>}
        </p>

        {/* Score card */}
        <div className="border border-white/10 rounded-xl overflow-hidden mb-6">
          <div className="grid grid-cols-4 gap-0 text-xs uppercase tracking-widest text-white/40 bg-white/5 px-4 py-2">
            <span>Hole</span>
            <span className="text-center">Par</span>
            <span className="text-center">You</span>
            <span className="text-center">{scores[0]?.aiStrokes !== null ? 'AI' : 'Score'}</span>
          </div>
          {scores.map((s) => (
            <div key={s.hole} className="grid grid-cols-4 gap-0 px-4 py-2 border-t border-white/5 text-sm">
              <span className="text-white/60">{s.hole}. {COURSES[s.hole - 1]?.name}</span>
              <span className="text-center text-white/60">{s.par}</span>
              <span className={`text-center font-bold ${scoreColor(s.playerStrokes, s.par)}`}>{s.playerStrokes}</span>
              <span className={`text-center font-bold ${s.aiStrokes !== null ? scoreColor(s.aiStrokes, s.par) : ''}`}>
                {s.aiStrokes !== null ? s.aiStrokes : formatScore(s.playerStrokes, s.par)}
              </span>
            </div>
          ))}
          <div className="grid grid-cols-4 gap-0 px-4 py-3 border-t border-[#00ff88]/30 bg-[#00ff88]/5 text-sm font-bold">
            <span className="text-[#00ff88]">TOTAL</span>
            <span className="text-center text-white/60">{parTotal}</span>
            <span className={`text-center ${scoreColor(playerTotal, parTotal)}`}>{playerTotal}</span>
            <span className={`text-center ${aiTotal !== null ? scoreColor(aiTotal, parTotal) : 'text-white/60'}`}>
              {aiTotal !== null ? aiTotal : formatScore(playerTotal, parTotal)}
            </span>
          </div>
        </div>

        {/* Save high score */}
        {!saved ? (
          <div className="flex gap-2 mb-6">
            <input
              type="text"
              placeholder="Enter your name..."
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={16}
              className="flex-1 bg-white/5 border border-white/20 rounded-lg px-4 py-2 text-white placeholder-white/30 focus:outline-none focus:border-[#00ff88]"
              onKeyDown={(e) => e.key === 'Enter' && handleSave()}
            />
            <Button variant="secondary" onClick={handleSave}>Save</Button>
          </div>
        ) : (
          <p className="text-center text-[#00ff88] mb-6">Score saved!</p>
        )}

        <div className="flex gap-4">
          <Button onClick={onRestart} className="flex-1" size="lg">
            PLAY AGAIN
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
