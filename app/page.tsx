'use client';
import { useState, useCallback } from 'react';
import { useGame } from '@/hooks/useGame';
import { useLocalStorage } from '@/hooks/useLocalStorage';
import { StartScreen } from '@/components/screens/StartScreen';
import { HoleComplete } from '@/components/screens/HoleComplete';
import { EndScreen } from '@/components/screens/EndScreen';
import { PauseMenu } from '@/components/screens/PauseMenu';
import { GameUI } from '@/components/game/GameUI';
import { GameCanvas } from '@/components/game/GameCanvas';
import { HighScore } from '@/types/game';
import { COURSES } from '@/lib/courses';

export default function Home() {
  const { config, startGame, completeHole, nextHole, togglePause, toggleSound, returnToMenu, currentHole } = useGame();
  const [highScores, setHighScores] = useLocalStorage<HighScore[]>('neon-golf-scores', []);
  const [playerStrokes, setPlayerStrokes] = useState(0);
  const [aiStrokes, setAiStrokes] = useState<number | null>(null);

  const handleStrokesUpdate = useCallback((ps: number, as_: number | null) => {
    setPlayerStrokes(ps);
    setAiStrokes(as_);
  }, []);

  const handleHoleComplete = useCallback(
    (ps: number, as_: number | null) => {
      setPlayerStrokes(0);
      setAiStrokes(null);
      completeHole(ps, as_);
    },
    [completeHole]
  );

  const handleSaveHighScore = useCallback(
    (name: string, totalStrokes: number) => {
      const entry: HighScore = { name, totalStrokes, date: new Date().toLocaleDateString() };
      const updated = [...highScores, entry]
        .sort((a, b) => a.totalStrokes - b.totalStrokes)
        .slice(0, 10);
      setHighScores(updated);
    },
    [highScores, setHighScores]
  );

  return (
    <main className="w-screen h-screen relative overflow-hidden bg-[#0a0a1a]">
      {config.screen === 'start' && (
        <StartScreen
          onStart={startGame}
          highScores={highScores}
          soundEnabled={config.soundEnabled}
          onToggleSound={toggleSound}
        />
      )}

      {(config.screen === 'playing' || config.screen === 'paused') && currentHole && (
        <>
          <GameUI
            currentHoleIndex={config.currentHoleIndex}
            playerStrokes={playerStrokes}
            aiStrokes={config.mode === 'vs_ai' ? aiStrokes : null}
            scores={config.scores}
            onPause={togglePause}
            soundEnabled={config.soundEnabled}
            onToggleSound={toggleSound}
            isVsAI={config.mode === 'vs_ai'}
          />
          <div className="w-full h-full">
            {config.screen === 'playing' && (
              <GameCanvas
                key={`hole-${currentHole.id}`}
                hole={currentHole}
                mode={config.mode}
                difficulty={config.difficulty}
                soundEnabled={config.soundEnabled}
                onHoleComplete={handleHoleComplete}
                onStrokesUpdate={handleStrokesUpdate}
              />
            )}
          </div>
          {config.screen === 'paused' && (
            <PauseMenu
              onResume={togglePause}
              onMenu={returnToMenu}
              soundEnabled={config.soundEnabled}
              onToggleSound={toggleSound}
            />
          )}
        </>
      )}

      {config.screen === 'hole_complete' && config.scores.length > 0 && (
        <HoleComplete
          score={config.scores[config.scores.length - 1]}
          onNext={nextHole}
          holeNumber={config.scores.length}
          totalHoles={COURSES.length}
        />
      )}

      {config.screen === 'game_over' && (
        <EndScreen
          scores={config.scores}
          onRestart={returnToMenu}
          onHighScoreSave={handleSaveHighScore}
          highScores={highScores}
        />
      )}
    </main>
  );
}
