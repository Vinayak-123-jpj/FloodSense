import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { useTheme } from '../../theme/ThemeContext';
import { Sun, Moon, Radio, Activity } from 'lucide-react';

export const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('en-US', { hour12: false }) + ' IST');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { path: '/', label: 'Overview' },
    { path: '/live', label: 'Live Monitor' },
    { path: '/replay', label: 'Scenario Replay' },
    { path: '/alerts', label: 'Alert Outbox' },
    { path: '/model-method', label: 'Model & Method' },
    { path: '/hardware', label: 'Open Hardware' }
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-survey-border dark:border-night-border bg-survey-paper/95 dark:bg-night-bg/95 backdrop-blur-md transition-colors duration-200">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        
        {/* Brand & Status */}
        <div className="flex items-center gap-3">
          <NavLink to="/" className="flex items-center gap-2 group">
            <div className="flex h-9 w-9 items-center justify-center rounded border border-survey-teal dark:border-night-teal bg-survey-card dark:bg-night-card text-survey-teal dark:text-night-teal shadow-xs group-hover:bg-survey-teal group-hover:text-white transition-all">
              <Activity className="h-5 w-5 stroke-[1.75]" />
            </div>
            <div>
              <span className="font-serif text-lg font-bold tracking-tight text-survey-ink dark:text-night-text block leading-none">
                FLOODSENSE
              </span>
              <span className="font-mono text-[10px] tracking-widest text-survey-teal dark:text-night-teal uppercase block mt-0.5">
                EARLY WARNING GRID
              </span>
            </div>
          </NavLink>

          <span className="hidden md:inline-block h-4 w-px bg-survey-border dark:bg-night-border mx-1"></span>

          <div className="hidden md:flex items-center gap-2 text-xs font-mono text-survey-slate dark:text-night-slate">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>VIRTUAL SENSORS LIVE</span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="hidden lg:flex items-center gap-1 font-sans text-sm font-medium">
          {navItems.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded transition-all ${
                  isActive
                    ? 'bg-survey-teal text-white shadow-xs font-semibold'
                    : 'text-survey-ink/80 dark:text-night-text/80 hover:text-survey-teal dark:hover:text-night-teal hover:bg-survey-border/40 dark:hover:bg-night-border/40'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Right Utility: Clock & Theme Toggle */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card font-mono text-xs text-survey-ink dark:text-night-text">
            <Radio className="h-3.5 w-3.5 text-survey-teal dark:text-night-teal animate-pulse" />
            <span>{timeStr}</span>
          </div>

          <button
            onClick={toggleTheme}
            className="flex h-9 w-9 items-center justify-center rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card text-survey-ink dark:text-night-text hover:bg-survey-border/50 dark:hover:bg-night-border/50 transition-all cursor-pointer"
            title={theme === 'light' ? 'Switch to Night Watch Theme' : 'Switch to Day Survey Theme'}
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <Moon className="h-4 w-4 text-survey-ink" />
            ) : (
              <Sun className="h-4 w-4 text-amber-400" />
            )}
          </button>
        </div>

      </div>

      {/* Mobile Sub-Navigation Bar */}
      <div className="lg:hidden flex overflow-x-auto border-t border-survey-border dark:border-night-border px-2 py-1.5 gap-1 font-sans text-xs scrollbar-none">
        {navItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `whitespace-nowrap px-3 py-1 rounded transition-all ${
                isActive
                  ? 'bg-survey-teal text-white font-medium'
                  : 'text-survey-ink dark:text-night-text hover:bg-survey-border/30 dark:hover:bg-night-border/30'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </div>
    </header>
  );
};
