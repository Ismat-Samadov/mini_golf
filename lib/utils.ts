export function formatScore(strokes: number, par: number): string {
  const diff = strokes - par;
  if (diff <= -2) return 'Eagle!';
  if (diff === -1) return 'Birdie!';
  if (diff === 0) return 'Par';
  if (diff === 1) return 'Bogey';
  if (diff === 2) return 'Double Bogey';
  return `+${diff}`;
}

export function scoreColor(strokes: number, par: number): string {
  const diff = strokes - par;
  if (diff <= -1) return 'text-yellow-400';
  if (diff === 0) return 'text-green-400';
  if (diff === 1) return 'text-orange-400';
  return 'text-red-500';
}

export function totalPar(holes: { par: number }[]): number {
  return holes.reduce((sum, h) => sum + h.par, 0);
}

export function totalStrokes(scores: { playerStrokes: number }[]): number {
  return scores.reduce((sum, s) => sum + s.playerStrokes, 0);
}
