import React from 'react';
import { Play, Pause, RotateCcw, CloudRain, Sliders } from 'lucide-react';

interface ScrubberProps {
  isPlaying: boolean;
  speed: number;
  scenario: string;
  rainMultiplier: number;
  progressPct: number;
  currentDate?: string;
  startDate?: string;
  endDate?: string;
  onTogglePlay: () => void;
  onSpeedChange: (speed: number) => void;
  onScenarioChange: (scenario: string) => void;
  onRainMultiplierChange: (mult: number) => void;
  onScrub: (pct: number) => void;
  onReset: () => void;
}

function formatDateLabel(rawDate?: string): string {
  if (!rawDate) return '';
  const d = new Date(rawDate);
  if (isNaN(d.getTime())) return rawDate;
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

export const Scrubber: React.FC<ScrubberProps> = ({
  isPlaying,
  speed,
  scenario,
  rainMultiplier,
  progressPct,
  currentDate,
  startDate,
  endDate,
  onTogglePlay,
  onSpeedChange,
  onScenarioChange,
  onRainMultiplierChange,
  onScrub,
  onReset
}) => {
  const displayStart = formatDateLabel(startDate || (scenario === 'assam_2020' ? '2020-07-01' : '2018-08-01'));
  const displayEnd = formatDateLabel(endDate || (scenario === 'assam_2020' ? '2020-07-31' : '2018-08-31'));
  const displayCurrent = formatDateLabel(currentDate || (scenario === 'assam_2020' ? '2020-07-15' : '2018-08-16'));

  return (
    <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 shadow-xs">
      
      {/* Top Header & Scenario Selector */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4 border-b border-survey-border/60 dark:border-night-border/60 pb-3">
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">HISTORICAL EVENT REPLAY ENGINE</span>
          <span className="font-serif text-base font-bold text-survey-ink dark:text-night-text">Timeline Scrubber & What-If Simulation</span>
        </div>

        <div className="flex items-center gap-2">
          <label className="font-mono text-xs text-survey-slate dark:text-night-slate">Scenario:</label>
          <select
            value={scenario}
            onChange={(e) => onScenarioChange(e.target.value)}
            className="rounded border border-survey-border dark:border-night-border bg-survey-paper dark:bg-night-bg px-2.5 py-1 font-mono text-xs text-survey-ink dark:text-night-text focus:outline-none focus:ring-1 focus:ring-survey-teal cursor-pointer"
          >
            <option value="kerala_2018">Kerala August 2018 Floods (Historic Event)</option>
            <option value="assam_2020">Assam Brahmaputra Basin (2020 Monsoon)</option>
          </select>
        </div>
      </div>

      {/* Main Timeline Scrubber Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-xs font-mono text-survey-slate dark:text-night-slate mb-1">
          <span className="font-semibold text-survey-ink dark:text-night-text">{displayStart}</span>
          <span className="text-survey-teal dark:text-night-teal font-bold px-2 py-0.5 rounded bg-survey-paper dark:bg-night-bg border border-survey-border dark:border-night-border">
            DATE: {displayCurrent} ({progressPct.toFixed(0)}%)
          </span>
          <span className="font-semibold text-survey-ink dark:text-night-text">{displayEnd}</span>
        </div>
        <input
          type="range"
          min="0"
          max="100"
          value={progressPct}
          onChange={(e) => onScrub(parseFloat(e.target.value))}
          className="h-2 w-full cursor-pointer appearance-none rounded bg-survey-paper dark:bg-night-bg border border-survey-border dark:border-night-border accent-survey-teal"
        />
      </div>

      {/* Playback Controls & What-If Rain Slider */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
        
        {/* Left: Play / Pause / Reset / Speed */}
        <div className="flex items-center gap-3">
          <button
            onClick={onTogglePlay}
            className="flex h-10 w-10 items-center justify-center rounded border border-survey-teal bg-survey-teal text-white hover:bg-survey-teal/90 transition-all cursor-pointer shadow-xs"
            title={isPlaying ? 'Pause Replay' : 'Play Replay'}
          >
            {isPlaying ? <Pause className="h-5 w-5 fill-current" /> : <Play className="h-5 w-5 fill-current ml-0.5" />}
          </button>

          <button
            onClick={onReset}
            className="flex h-10 w-10 items-center justify-center rounded border border-survey-border dark:border-night-border bg-survey-paper dark:bg-night-bg text-survey-ink dark:text-night-text hover:bg-survey-border/40 transition-all cursor-pointer"
            title="Reset Timeline to Start"
          >
            <RotateCcw className="h-4 w-4" />
          </button>

          {/* Speed Selector */}
          <div className="flex items-center gap-1 border border-survey-border dark:border-night-border rounded p-1 bg-survey-paper dark:bg-night-bg">
            {[0.5, 1, 5, 10, 30].map(s => (
              <button
                key={s}
                onClick={() => onSpeedChange(s)}
                className={`px-2 py-0.5 font-mono text-xs rounded transition-all cursor-pointer ${
                  speed === s
                    ? 'bg-survey-teal text-white font-bold'
                    : 'text-survey-slate dark:text-night-slate hover:text-survey-ink dark:hover:text-night-text'
                }`}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>

        {/* Right: What-If Rain Multiplier Slider */}
        <div className="flex items-center gap-3 bg-survey-paper dark:bg-night-bg p-2.5 rounded border border-survey-border dark:border-night-border">
          <CloudRain className="h-5 w-5 text-survey-teal dark:text-night-teal shrink-0" />
          <div className="flex-1">
            <div className="flex justify-between items-center text-xs font-mono mb-1">
              <span className="text-survey-ink dark:text-night-text font-medium flex items-center gap-1">
                <Sliders className="h-3 w-3" /> Rainfall Stress Multiplier
              </span>
              <div className="flex items-center gap-1.5">
                {rainMultiplier !== 1.0 && (
                  <span className="bg-amber-100 dark:bg-amber-900/60 text-amber-800 dark:text-amber-200 px-1.5 py-0.5 rounded text-[10px] font-bold border border-amber-300 dark:border-amber-700">
                    scenario, not a forecast
                  </span>
                )}
                <span className="text-amber-600 dark:text-amber-400 font-bold">{rainMultiplier.toFixed(1)}x Rain</span>
              </div>
            </div>
            <input
              type="range"
              min="1.0"
              max="3.0"
              step="0.1"
              value={rainMultiplier}
              onChange={(e) => onRainMultiplierChange(parseFloat(e.target.value))}
              className="h-1.5 w-full cursor-pointer appearance-none rounded bg-survey-border dark:bg-night-border accent-amber-600"
            />
          </div>
        </div>

      </div>
    </div>
  );
};
