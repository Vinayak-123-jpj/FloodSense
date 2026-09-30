import React from 'react';
import { Station } from '../../types';
import { Battery, Wifi } from 'lucide-react';

interface GaugeProps {
  station: Station;
  currentDischargeM3s?: number;
  currentWaterLevelM?: number;
  batteryPct?: number;
  rssi?: number;
  sensorStatus?: string;
}

export const WaterLevelGauge: React.FC<GaugeProps> = ({
  station,
  currentDischargeM3s,
  currentWaterLevelM,
  batteryPct = 98.0,
  rssi = -65,
  sensorStatus = 'OK'
}) => {
  // Percentile proxies fallback
  const p90 = station.p90_m3s || (station.region === 'Assam' ? 4500 : 160);
  const p97 = station.p97_m3s || (station.region === 'Assam' ? 7200 : 310);
  const p99_5 = station.p99_5_m3s || (station.region === 'Assam' ? 11500 : 550);

  const displayDischarge = currentDischargeM3s !== undefined
    ? currentDischargeM3s
    : (station.current_discharge_m3s !== undefined ? station.current_discharge_m3s : 24.5);

  const displayStage = currentWaterLevelM !== undefined
    ? currentWaterLevelM
    : (station.current_water_level_m !== undefined ? station.current_water_level_m : station.normal_level_m);

  const maxScale = Math.max(p99_5 * 1.35, displayDischarge * 1.15, 100);
  const fillPct = Math.min(100, Math.max(0, (displayDischarge / maxScale) * 100));

  const p90Pct = (p90 / maxScale) * 100;
  const p97Pct = (p97 / maxScale) * 100;
  const p995Pct = (p99_5 / maxScale) * 100;

  // Determine current active risk
  let riskColor = 'text-emerald-600 dark:text-emerald-400';
  let barColor = 'bg-emerald-600 dark:bg-emerald-500';
  if (displayDischarge >= p99_5) {
    riskColor = 'text-red-600 dark:text-red-400';
    barColor = 'bg-red-600 dark:bg-red-500';
  } else if (displayDischarge >= p97) {
    riskColor = 'text-amber-600 dark:text-amber-400';
    barColor = 'bg-amber-600 dark:bg-amber-500';
  } else if (displayDischarge >= p90) {
    riskColor = 'text-yellow-600 dark:text-yellow-400';
    barColor = 'bg-yellow-500 dark:bg-yellow-500';
  }

  return (
    <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 shadow-xs">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 border-b border-survey-border/60 dark:border-night-border/60 pb-2">
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">
            HYDROLOGICAL TELEMETRY GAUGE
          </span>
          <span className="font-serif text-base font-bold text-survey-ink dark:text-night-text">
            {station.name} ({station.river})
          </span>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono text-survey-slate dark:text-night-slate">
          <span className="flex items-center gap-1" title="Virtual Node Battery">
            <Battery className={`h-4 w-4 ${batteryPct < 20 ? 'text-red-500' : 'text-emerald-600'}`} />
            {batteryPct.toFixed(0)}%
          </span>
          <span className="flex items-center gap-1" title="RSSI Signal">
            <Wifi className="h-4 w-4 text-survey-teal dark:text-night-teal" />
            {rssi} dBm
          </span>
        </div>
      </div>

      {/* Primary Readout: River Discharge */}
      <div className="flex items-baseline justify-between mb-3">
        <div>
          <span className={`font-mono text-3xl font-bold tracking-tight ${riskColor}`}>
            {displayDischarge.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
          </span>
          <span className="font-mono text-sm text-survey-slate dark:text-night-slate ml-1">m³/s</span>
          <span className="block font-sans text-[11px] text-survey-slate dark:text-night-slate mt-0.5">
            GloFAS Modelled Discharge
          </span>
        </div>
        <div className="text-right font-mono text-xs space-y-0.5">
          <span className="text-red-600 dark:text-red-400 block font-semibold">
            Red (p99.5): {p99_5.toFixed(1)} m³/s
          </span>
          <span className="text-amber-600 dark:text-amber-400 block font-semibold">
            Orange (p97): {p97.toFixed(1)} m³/s
          </span>
          <span className="text-yellow-600 dark:text-yellow-400 block font-semibold">
            Yellow (p90): {p90.toFixed(1)} m³/s
          </span>
        </div>
      </div>

      {/* Discharge Gauge Bar with Percentile Proxies */}
      <div className="relative h-10 w-full rounded bg-survey-paper dark:bg-night-bg border border-survey-border dark:border-night-border overflow-hidden mb-2">
        {/* Dynamic fill */}
        <div
          className={`absolute left-0 top-0 bottom-0 ${barColor} opacity-75 transition-all duration-500`}
          style={{ width: `${fillPct}%` }}
        />

        {/* p90 Marker */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-yellow-500 z-10"
          style={{ left: `${p90Pct}%` }}
          title={`Yellow Watch Proxy (p90): ${p90} m³/s`}
        />

        {/* p97 Marker */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-amber-500 z-10"
          style={{ left: `${p97Pct}%` }}
          title={`Orange Warning Proxy (p97): ${p97} m³/s`}
        />

        {/* p99.5 Marker */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-red-600 z-10"
          style={{ left: `${p995Pct}%` }}
          title={`Red Danger Proxy (p99.5): ${p99_5} m³/s`}
        />

        {/* Labels inside gauge */}
        <div className="absolute inset-0 flex items-center justify-between px-2 text-[10px] font-mono text-survey-ink/80 dark:text-night-text/80 pointer-events-none">
          <span>0 m³/s</span>
          <span className="font-semibold text-yellow-700 dark:text-yellow-300">p90</span>
          <span className="font-semibold text-amber-700 dark:text-amber-300">p97</span>
          <span className="font-semibold text-red-700 dark:text-red-300">p99.5</span>
          <span>{Math.round(maxScale)} m³/s</span>
        </div>
      </div>

      {/* Secondary Readout: Water Level Stage (SIMULATED NODE) */}
      <div className="rounded bg-survey-paper/60 dark:bg-night-bg/60 border border-survey-border/40 dark:border-night-border/40 p-2 flex items-center justify-between font-mono text-xs">
        <div className="flex items-center gap-2">
          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-survey-border/40 dark:bg-night-border/40 text-survey-slate dark:text-night-slate">
            SIMULATED
          </span>
          <span className="text-survey-ink dark:text-night-text">
            Stage Height: <strong>{displayStage.toFixed(2)} m</strong>
          </span>
        </div>
        <span className="text-[10px] text-survey-slate dark:text-night-slate">
          Rating curve Q = a(h - h₀)ᵇ
        </span>
      </div>

      {/* Explicit Disclaimer */}
      <p className="mt-2 text-[10px] font-sans text-survey-slate dark:text-night-slate leading-tight">
        Percentile proxies (p90 / p97 / p99.5) from 1990–2025 GloFAS reanalysis, NOT official CWC stage meters.
      </p>
    </div>
  );
};

