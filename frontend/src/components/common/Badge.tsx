import React from 'react';
import { RiskLevel } from '../../types';

interface BadgeProps {
  level: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<BadgeProps> = ({ level, size = 'md' }) => {
  const configs = {
    Green: {
      bg: 'bg-emerald-100 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800',
      shape: '●', // Circle
      label: 'NORMAL (GREEN)'
    },
    Yellow: {
      bg: 'bg-amber-100 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-800',
      shape: '▲', // Triangle
      label: 'ADVISORY (YELLOW)'
    },
    Orange: {
      bg: 'bg-orange-100 dark:bg-orange-950/40 text-orange-800 dark:text-orange-300 border-orange-300 dark:border-orange-800',
      shape: '◆', // Diamond
      label: 'WARNING (ORANGE)'
    },
    Red: {
      bg: 'bg-red-100 dark:bg-red-950/40 text-red-800 dark:text-red-300 border-red-300 dark:border-red-800',
      shape: '⬢', // Octagon
      label: 'DANGER (RED)'
    }
  };

  const cfg = configs[level] || configs.Green;
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-2.5 py-1 text-xs font-mono font-medium gap-1.5',
    lg: 'px-3.5 py-1.5 text-sm font-mono font-semibold gap-2'
  };

  return (
    <span className={`inline-flex items-center rounded border ${cfg.bg} ${sizeClasses[size]} tracking-wide uppercase shadow-xs`}>
      <span className="text-[10px] select-none">{cfg.shape}</span>
      <span>{cfg.label}</span>
    </span>
  );
};

export const SimulatedBadge: React.FC = () => (
  <span className="inline-flex items-center px-2 py-0.5 rounded border border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300 font-mono text-[10px] font-semibold tracking-wider uppercase">
    SIMULATED TELEMETRY
  </span>
);
