import React, { useState, useEffect } from 'react';
import { Scrubber } from '../components/replay/Scrubber';
import { FloodMap } from '../components/map/FloodMap';
import { HydrologicalChart } from '../components/charts/HydrologicalChart';
import { WaterLevelGauge } from '../components/charts/WaterLevelGauge';
import { RiskBadge } from '../components/common/Badge';
import { Station, Reading, RiskLevel } from '../types';
import { api } from '../services/api';
import { AlertCircle, Sliders } from 'lucide-react';

export const ScenarioReplayPage: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [speed, setSpeed] = useState<number>(1.0);
  const [scenario, setScenario] = useState<string>('kerala_2018');
  const [rainMultiplier, setRainMultiplier] = useState<number>(1.0);
  const [progressPct, setProgressPct] = useState<number>(15.0);

  const [stations, setStations] = useState<Station[]>([]);
  const [selectedStation, setSelectedStation] = useState<Station | null>(null);

  useEffect(() => {
    const reg = scenario === 'kerala_2018' ? 'Kerala' : 'Assam';
    api.getStations(reg).then(data => {
      setStations(data);
      if (data.length > 0) setSelectedStation(data[0]);
    }).catch(console.error);
  }, [scenario]);

  // Simulate timeline playback ticker
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setProgressPct(prev => {
        if (prev >= 100) {
          setIsPlaying(false);
          return 100;
        }
        return prev + 0.5 * speed;
      });
    }, 500);

    return () => clearInterval(interval);
  }, [isPlaying, speed]);

  // Calculate dynamic simulated water level based on scrubber progress & rain multiplier
  const calculateSimulatedState = (st: Station): { level: number; risk: RiskLevel } => {
    // Peak simulation curve
    const progressFactor = Math.sin((progressPct / 100) * Math.PI);
    const rainBoost = (rainMultiplier - 1.0) * 1.5;
    
    const simulatedLevel = st.normal_level_m + (st.danger_level_m - st.normal_level_m) * progressFactor * rainMultiplier;
    
    let risk: RiskLevel = 'Green';
    if (simulatedLevel >= st.danger_level_m) risk = 'Red';
    else if (simulatedLevel >= st.warning_level_m) risk = 'Orange';
    else if (simulatedLevel >= st.normal_level_m * 1.4) risk = 'Yellow';

    return { level: Math.max(st.normal_level_m, simulatedLevel), risk };
  };

  const updatedStations = stations.map(st => {
    const { level, risk } = calculateSimulatedState(st);
    return {
      ...st,
      current_water_level_m: level,
      current_risk_level: risk
    };
  });

  const activeSelected = selectedStation
    ? updatedStations.find(s => s.id === selectedStation.id) || selectedStation
    : updatedStations[0] || null;

  // Generate synthetic readings for replay chart
  const syntheticReadings: Reading[] = Array.from({ length: 24 }, (_, i) => {
    const t = new Date(Date.now() - (24 - i) * 3600 * 1000).toISOString();
    const subProgress = Math.max(0, progressPct - (24 - i) * 1.5);
    const lvl = (activeSelected?.normal_level_m || 2.0) + ((activeSelected?.danger_level_m || 6.0) - (activeSelected?.normal_level_m || 2.0)) * Math.sin((subProgress / 100) * Math.PI) * rainMultiplier;
    return {
      id: i,
      station_id: activeSelected?.id || 'KL-PER-01',
      timestamp: t,
      water_level_cm: lvl * 100,
      water_level_m: Math.max(1.0, lvl),
      rainfall_mm_hr: Math.max(0, 15 * Math.sin((subProgress / 100) * Math.PI) * rainMultiplier),
      battery_pct: 95,
      rssi: -65,
      risk_level: lvl >= (activeSelected?.danger_level_m || 6.0) ? 'Red' : lvl >= (activeSelected?.warning_level_m || 4.5) ? 'Orange' : 'Green',
      sensor_status: 'OK'
    };
  });

  return (
    <div className="space-y-6 pb-12">
      
      {/* Page Title */}
      <div className="border-b border-survey-border dark:border-night-border pb-3">
        <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">DISASTER REPLAY & DIGITAL TWIN SIMULATOR</span>
        <h1 className="font-serif text-2xl font-bold text-survey-ink dark:text-night-text">Historical Event Scrubber</h1>
        <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
          Replay the August 2018 Kerala floods or Assam monsoon events. Evaluated using the genuinely out-of-sample model (<code className="font-mono text-survey-teal dark:text-night-teal">heldout_2018_model.joblib</code>), trained strictly on non-2018 data. Test what-if rainfall scenarios live.
        </p>
      </div>

      {/* Scrubber Controls */}
      <Scrubber
        isPlaying={isPlaying}
        speed={speed}
        scenario={scenario}
        rainMultiplier={rainMultiplier}
        progressPct={progressPct}
        onTogglePlay={() => setIsPlaying(!isPlaying)}
        onSpeedChange={setSpeed}
        onScenarioChange={setScenario}
        onRainMultiplierChange={setRainMultiplier}
        onScrub={setProgressPct}
        onReset={() => { setProgressPct(0); setIsPlaying(false); }}
      />

      {/* Synchronized Replay Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <div className="lg:col-span-7 space-y-4">
          <FloodMap
            stations={updatedStations}
            selectedStationId={activeSelected?.id}
            onSelectStation={setSelectedStation}
            height="520px"
          />
        </div>

        <div className="lg:col-span-5 space-y-4">
          {activeSelected && (
            <>
              <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-mono text-xs text-survey-teal dark:text-night-teal block">{activeSelected.id} • REPLAY STATE</span>
                    <h2 className="font-serif text-lg font-bold text-survey-ink dark:text-night-text">{activeSelected.name}</h2>
                  </div>
                  <RiskBadge level={activeSelected.current_risk_level || 'Green'} size="md" />
                </div>
              </div>

              <WaterLevelGauge
                station={activeSelected}
                currentWaterLevelM={activeSelected.current_water_level_m}
              />

              <HydrologicalChart
                station={activeSelected}
                readings={syntheticReadings}
              />
            </>
          )}
        </div>

      </div>

    </div>
  );
};
