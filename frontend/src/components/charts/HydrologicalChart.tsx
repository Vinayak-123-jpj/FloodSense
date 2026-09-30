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

  // Combine historical readings and forecast points into single timeline
  const historicalData = readings.map(r => ({
    timestamp: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    fullDate: new Date(r.timestamp).toLocaleString(),
    water_level: r.water_level_m,
    rainfall: r.rainfall_mm_hr,
    isForecast: false
  }));

  const forecastData = forecastPoints.map(f => ({
    timestamp: new Date(f.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    fullDate: new Date(f.timestamp).toLocaleString(),
    forecast_level: f.predicted_water_level_m,
    rainfall: f.rainfall_mm_hr,
    uncertaintyRange: [f.lower_bound_m, f.upper_bound_m],
    isForecast: true
  }));

  const combinedData = [...historicalData, ...forecastData];

  const gridColor = theme === 'dark' ? '#1F2D3A' : '#E2DCD0';
  const textColor = theme === 'dark' ? '#94A3B8' : '#4A5568';

  return (
    <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 shadow-xs">
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">72-HOUR HYDROLOGICAL TREND & FORECAST BAND</span>
          <span className="font-serif text-sm font-semibold text-survey-ink dark:text-night-text">Water Level (m) & Rainfall (mm/hr)</span>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono text-survey-slate dark:text-night-slate">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-survey-teal dark:bg-night-teal"></span> Historical Level
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-amber-500"></span> Forecast Line
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-amber-200 dark:bg-amber-900/40"></span> Uncertainty Envelope
          </span>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={combinedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="timestamp" stroke={textColor} fontSize={10} tickLine={false} />
            <YAxis yAxisId="level" domain={[0, Math.ceil(station.danger_level_m * 1.25)]} stroke={textColor} fontSize={10} tickLine={false} />
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

            {/* Warning & Danger Threshold Lines */}
            <ReferenceLine yAxisId="level" y={station.warning_level_m} stroke="#D97706" strokeDasharray="4 4" label={{ value: `Warning (${station.warning_level_m}m)`, fill: '#D97706', fontSize: 10 }} />
            <ReferenceLine yAxisId="level" y={station.danger_level_m} stroke="#DC2626" strokeDasharray="2 2" label={{ value: `Danger (${station.danger_level_m}m)`, fill: '#DC2626', fontSize: 10 }} />

            {/* Forecast Uncertainty Envelope Shading */}
            <Area yAxisId="level" type="monotone" dataKey="uncertaintyRange" fill="#FDE68A" fillOpacity={theme === 'dark' ? 0.15 : 0.4} stroke="none" />

            {/* Precipitation Bar */}
            <Bar yAxisId="rain" dataKey="rainfall" fill="#1F6B75" opacity={0.3} barSize={6} />

            {/* Historical Water Level Line */}
            <Line yAxisId="level" type="monotone" dataKey="water_level" stroke="#1F6B75" strokeWidth={2} dot={false} />

            {/* Forecast Water Level Line */}
            <Line yAxisId="level" type="monotone" dataKey="forecast_level" stroke="#D97706" strokeWidth={2} strokeDasharray="4 4" dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
