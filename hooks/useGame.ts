'use client';
import { useState, useCallback } from 'react';
import { GameScreen, GameMode, Difficulty, ScoreEntry } from '@/types/game';
import { COURSES } from '@/lib/courses';

export interface GameConfig {
  screen: GameScreen;
  mode: GameMode;
  difficulty: Difficulty;
  currentHoleIndex: number;
  scores: ScoreEntry[];
  soundEnabled: boolean;
}

const initialConfig: GameConfig = {
  screen: 'start',
  mode: 'solo',
  difficulty: 'medium',
  currentHoleIndex: 0,
  scores: [],
  soundEnabled: true,
};

export function useGame() {
  const [config, setConfig] = useState<GameConfig>(initialConfig);

  const startGame = useCallback((mode: GameMode, difficulty: Difficulty) => {
    setConfig({
      ...initialConfig,
      screen: 'playing',
      mode,
      difficulty,
    });
  }, []);

  const completeHole = useCallback(
    (playerStrokes: number, aiStrokes: number | null) => {
      const hole = COURSES[config.currentHoleIndex];
      const entry: ScoreEntry = {
        hole: hole.id,
        par: hole.par,
        playerStrokes,
        aiStrokes,
      };
      const newScores = [...config.scores, entry];
      const isLastHole = config.currentHoleIndex >= COURSES.length - 1;

      setConfig((prev) => ({
        ...prev,
        scores: newScores,
        screen: isLastHole ? 'game_over' : 'hole_complete',
      }));
    },
    [config.currentHoleIndex, config.scores]
  );

  const nextHole = useCallback(() => {
    setConfig((prev) => ({
      ...prev,
      currentHoleIndex: prev.currentHoleIndex + 1,
      screen: 'playing',
    }));
  }, []);

  const togglePause = useCallback(() => {
    setConfig((prev) => ({
      ...prev,
      screen: prev.screen === 'paused' ? 'playing' : 'paused',
    }));
  }, []);

  const toggleSound = useCallback(() => {
    setConfig((prev) => ({ ...prev, soundEnabled: !prev.soundEnabled }));
  }, []);

  const returnToMenu = useCallback(() => {
    setConfig(initialConfig);
  }, []);

  return {
    config,
    startGame,
    completeHole,
    nextHole,
    togglePause,
    toggleSound,
    returnToMenu,
    currentHole: COURSES[config.currentHoleIndex],
  };
}
