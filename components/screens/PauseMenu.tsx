'use client';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';

interface PauseMenuProps {
  onResume: () => void;
  onMenu: () => void;
  soundEnabled: boolean;
  onToggleSound: () => void;
}

export function PauseMenu({ onResume, onMenu, soundEnabled, onToggleSound }: PauseMenuProps) {
  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-[#0a0a1a] border border-[#00ffff]/40 rounded-2xl p-8 mx-4 max-w-xs w-full text-center shadow-[0_0_60px_rgba(0,255,255,0.2)]"
      >
        <h2 className="text-3xl font-black text-[#00ffff] mb-6" style={{ textShadow: '0 0 20px rgba(0,255,255,0.6)' }}>
          PAUSED
        </h2>
        <div className="flex flex-col gap-3">
          <Button onClick={onResume} className="w-full">Resume</Button>
          <Button variant="ghost" onClick={onToggleSound} className="w-full">
            {soundEnabled ? 'Sound On' : 'Sound Off'}
          </Button>
          <Button variant="danger" onClick={onMenu} className="w-full">
            Quit to Menu
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
