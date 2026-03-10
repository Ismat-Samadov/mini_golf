'use client';
import { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  ...props
}: ButtonProps) {
  const base =
    'font-bold rounded-lg transition-all duration-150 select-none active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary:
      'bg-transparent border-2 border-[#00ff88] text-[#00ff88] hover:bg-[#00ff88] hover:text-black shadow-[0_0_16px_rgba(0,255,136,0.4)] hover:shadow-[0_0_24px_rgba(0,255,136,0.7)]',
    secondary:
      'bg-transparent border-2 border-[#00ffff] text-[#00ffff] hover:bg-[#00ffff] hover:text-black shadow-[0_0_16px_rgba(0,255,255,0.3)] hover:shadow-[0_0_24px_rgba(0,255,255,0.6)]',
    danger:
      'bg-transparent border-2 border-[#ff4444] text-[#ff4444] hover:bg-[#ff4444] hover:text-white shadow-[0_0_16px_rgba(255,68,68,0.3)]',
    ghost: 'bg-transparent border border-white/20 text-white/70 hover:text-white hover:border-white/50',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-6 py-2.5 text-base',
    lg: 'px-10 py-4 text-lg tracking-widest uppercase',
  };

  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {...props}>
      {children}
    </button>
  );
}
