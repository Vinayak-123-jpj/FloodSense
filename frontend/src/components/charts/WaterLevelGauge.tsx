import React from 'react';
import { Station } from '../../types';
import { Battery, Wifi, AlertTriangle } from 'lucide-react';

interface GaugeProps {
  station: Station;
  currentWaterLevelM?: number;
  batteryPct?: number;
  rssi?: number;
  sensorStatus?: string;
}

export const WaterLevelGauge: React.FC<GaugeProps> = ({
  station,
  currentWaterLevelM = station.normal_level_m,
  batteryPct = 98.0,
  rssi = -65,
  sensorStatus = 'OK'
}) => {
  const maxScale = Math.max(station.danger_level_m * 1.25, 8.0);
  const fillPct = Math.min(100, Math.max(0, (currentWaterLevelM / maxScale) * 100));

  const warningPct = (station.warning_level_m / maxScale) * 100;
  const dangerPct = (station.danger_level_m / maxScale) * 100;
  const normalPct = (station.normal_level_m / maxScale) * 100;

  return (
    <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 shadow-xs">
      <div className="flex items-center justify-between mb-3 border-b border-survey-border/60 dark:border-night-border/60 pb-2">
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">HYDROLOGICAL GAUGE</span>
          <span className="font-serif text-base font-bold text-survey-ink dark:text-night-text">{station.name} ({station.river})</span>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono text-survey-slate dark:text-night-slate">
          <span className="flex items-center gap-1">
            <Battery className={`h-4 w-4 ${batteryPct < 20 ? 'text-red-500' : 'text-emerald-600'}`} />
            {batteryPct.toFixed(0)}%
          </span>
          <span className="flex items-center gap-1">
            <Wifi className="h-4 w-4 text-survey-teal dark:text-night-teal" />
            {rssi} dBm
          </span>
        </div>
      </div>

      {/* Main Metric Digital Readout */}
      <div className="flex items-baseline justify-between mb-4">
        <div>
          <span className="font-mono text-3xl font-bold tracking-tight text-survey-ink dark:text-night-text">
            {currentWaterLevelM.toFixed(2)}
          </span>
          <span className="font-mono text-sm text-survey-slate dark:text-night-slate ml-1">meters</span>
        </div>
        <div className="text-right font-mono text-xs">
          <span className="text-survey-slate dark:text-night-slate block">Danger Mark: {station.danger_level_m.toFixed(2)}m</span>
          <span className="text-survey-slate dark:text-night-slate block">Warning Mark: {station.warning_level_m.toFixed(2)}m</span>
        </div>
      </div>

      {/* Vertical Animated Gauge Bar */}
      <div className="relative h-12 w-full rounded bg-survey-paper dark:bg-night-bg border border-survey-border dark:border-night-border overflow-hidden">
        {/* Fill level */}
        <div
          className="absolute left-0 top-0 bottom-0 bg-survey-teal/70 dark:bg-night-teal/70 transition-all duration-500"
          style={{ width: `${fillPct}%` }}
        />

        {/* Normal Level Indicator */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-emerald-500 z-10"
          style={{ left: `${normalPct}%` }}
          title={`Normal Level: ${station.normal_level_m}m`}
        />

        {/* Warning Level Marker */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-amber-500 stroke-dasharray z-10"
          style={{ left: `${warningPct}%` }}
          title={`Warning Threshold: ${station.warning_level_m}m`}
        />

        {/* Danger Level Marker */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-red-600 z-10"
          style={{ left: `${dangerPct}%` }}
          title={`Danger Threshold: ${station.danger_level_m}m`}
        />

        <div className="absolute inset-0 flex items-center justify-between px-3 text-[10px] font-mono text-survey-ink/70 dark:text-night-text/70 pointer-events-none">
          <span>0.0m</span>
          <span className="font-semibold text-amber-700 dark:text-amber-400">WARN {station.warning_level_m}m</span>
          <span className="font-semibold text-red-700 dark:text-red-400">DANGER {station.danger_level_m}m</span>
          <span>{maxScale.toFixed(1)}m</span>
        </div>
      </div>
    </div>
  );
};
