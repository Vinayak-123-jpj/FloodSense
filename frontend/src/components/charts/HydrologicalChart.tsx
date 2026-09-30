import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid
} from 'recharts';
import { Reading, ForecastHour, Station } from '../../types';
import { useTheme } from '../../theme/ThemeContext';

interface ChartProps {
  station: Station;
  readings: Reading[];
  forecastPoints?: ForecastHour[];
}

export const HydrologicalChart: React.FC<ChartProps> = ({ station, readings, forecastPoints = [] }) => {
  const { theme } = useTheme();

  const p90 = station.p90_m3s || (station.region === 'Assam' ? 4500 : 160);
  const p97 = station.p97_m3s || (station.region === 'Assam' ? 7200 : 310);
  const p99_5 = station.p99_5_m3s || (station.region === 'Assam' ? 11500 : 550);

  // Combine historical readings and forecast points into single timeline
  const historicalData = readings.map(r => {
    const q = r.discharge_m3s !== undefined && r.discharge_m3s > 0
      ? r.discharge_m3s
      : Math.round(12.0 * Math.pow(Math.max(0.1, r.water_level_m - 1.2), 2.1));
    return {
      timestamp: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      fullDate: new Date(r.timestamp).toLocaleString(),
      discharge_m3s: q,
      water_level_m: r.water_level_m,
      rainfall: r.rainfall_mm_hr,
      isForecast: false
    };
  });

  const forecastData = forecastPoints.map(f => {
    const qForecast = Math.round(12.0 * Math.pow(Math.max(0.1, f.predicted_water_level_m - 1.2), 2.1));
    const qLower = Math.round(12.0 * Math.pow(Math.max(0.1, f.lower_bound_m - 1.2), 2.1));
    const qUpper = Math.round(12.0 * Math.pow(Math.max(0.1, f.upper_bound_m - 1.2), 2.1));
    return {
      timestamp: new Date(f.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      fullDate: new Date(f.timestamp).toLocaleString(),
      forecast_discharge: qForecast,
      water_level_m: f.predicted_water_level_m,
      rainfall: f.rainfall_mm_hr,
      uncertaintyRange: [qLower, qUpper],
      isForecast: true
    };
  });

  const combinedData = [...historicalData, ...forecastData];
  const maxDischargeObserved = Math.max(...combinedData.map((d: any) => (d.discharge_m3s || d.forecast_discharge || 0)), 10);
  const yMax = Math.ceil(Math.max(p99_5 * 1.3, maxDischargeObserved * 1.15));

  const gridColor = theme === 'dark' ? '#1F2D3A' : '#E2DCD0';
  const textColor = theme === 'dark' ? '#94A3B8' : '#4A5568';

  return (
    <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 shadow-xs">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">
            72-HOUR HYDROLOGICAL TREND & FORECAST BAND
          </span>
          <span className="font-serif text-sm font-semibold text-survey-ink dark:text-night-text">
            Discharge (m³/s) vs Percentile Proxies & Rainfall (mm/hr)
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-survey-slate dark:text-night-slate">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-survey-teal dark:bg-night-teal"></span> Discharge (m³/s)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-amber-500"></span> Forecast
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-amber-200 dark:bg-amber-900/40"></span> Uncertainty
          </span>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={combinedData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="timestamp" stroke={textColor} fontSize={10} tickLine={false} />
            <YAxis yAxisId="discharge" domain={[0, yMax]} stroke={textColor} fontSize={10} tickLine={false} />
            <YAxis yAxisId="rain" orientation="right" domain={[0, 60]} stroke={textColor} fontSize={10} tickLine={false} />

            <Tooltip
              contentStyle={{
                backgroundColor: theme === 'dark' ? '#131E28' : '#FAF7F0',
                borderColor: theme === 'dark' ? '#1F2D3A' : '#D8D2C2',
                borderRadius: '4px',
                fontSize: '11px',
                fontFamily: 'monospace'
              }}
            />

            {/* Percentile Threshold Lines */}
            <ReferenceLine yAxisId="discharge" y={p90} stroke="#EAB308" strokeDasharray="4 4" label={{ value: `p90 (${p90} m³/s)`, fill: '#CA8A04', fontSize: 10 }} />
            <ReferenceLine yAxisId="discharge" y={p97} stroke="#EA580C" strokeDasharray="4 4" label={{ value: `p97 (${p97} m³/s)`, fill: '#EA580C', fontSize: 10 }} />
            <ReferenceLine yAxisId="discharge" y={p99_5} stroke="#DC2626" strokeDasharray="2 2" label={{ value: `p99.5 (${p99_5} m³/s)`, fill: '#DC2626', fontSize: 10 }} />

            {/* Forecast Uncertainty Envelope Shading */}
            <Area yAxisId="discharge" type="monotone" dataKey="uncertaintyRange" fill="#FDE68A" fillOpacity={theme === 'dark' ? 0.15 : 0.4} stroke="none" />

            {/* Precipitation Bar */}
            <Bar yAxisId="rain" dataKey="rainfall" fill="#1F6B75" opacity={0.3} barSize={6} />

            {/* Historical Discharge Line */}
            <Line yAxisId="discharge" type="monotone" dataKey="discharge_m3s" stroke="#1F6B75" strokeWidth={2} dot={false} />

            {/* Forecast Discharge Line */}
            <Line yAxisId="discharge" type="monotone" dataKey="forecast_discharge" stroke="#D97706" strokeWidth={2} strokeDasharray="4 4" dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-2 text-[10px] font-sans text-survey-slate dark:text-night-slate">
        Discharge threshold lines represent historical training period percentiles (p90=Yellow, p97=Orange, p99.5=Red), NOT official CWC gauge marks.
      </p>
    </div>
  );
};
