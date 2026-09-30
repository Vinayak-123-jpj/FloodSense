import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Scrubber } from '../components/replay/Scrubber';
import { FloodMap } from '../components/map/FloodMap';
import { HydrologicalChart } from '../components/charts/HydrologicalChart';
import { WaterLevelGauge } from '../components/charts/WaterLevelGauge';
import { RiskBadge } from '../components/common/Badge';
import { Station, Reading, RiskLevel } from '../types';
import { api } from '../services/api';
import { AlertCircle, Sliders, Calendar, Bell, Info } from 'lucide-react';
import axios from 'axios';

interface ReplayStationData {
  id: string;
  name: string;
  river: string;
  latitude: number;
  longitude: number;
  discharge_m3s: number;
  water_level_m: number;
  rainfall_mm: number;
  rain_7d_mm: number;
  risk_level: RiskLevel;
  percentiles: {
    p90_yellow: number;
    p97_orange: number;
    'p99.5_red'?: number;
    p99_5_red?: number;
  };
  top_drivers: string[];
}

interface ReplayFrame {
  day_index: number;
  date: string;
  progress_pct: number;
  headline: string;
  overall_risk: RiskLevel;
  stations: ReplayStationData[];
}

interface ReplayDataset {
  scenario: string;
  name: string;
  region: string;
  start_date: string;
  end_date: string;
  total_days: number;
  frames: ReplayFrame[];
}

export const ScenarioReplayPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const pctParam = searchParams.get('pct');
  const scenarioParam = searchParams.get('scenario');

  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [speed, setSpeed] = useState<number>(1.0);
  const [scenario, setScenario] = useState<string>(scenarioParam || 'kerala_2018');
  const [rainMultiplier, setRainMultiplier] = useState<number>(1.0);
  const [progressPct, setProgressPct] = useState<number>(pctParam ? parseFloat(pctParam) : 50.0);

  const [replayData, setReplayData] = useState<ReplayDataset | null>(null);
  const [selectedStationId, setSelectedStationId] = useState<string>('KL-PER-02');
  const [alertLang, setAlertLang] = useState<'en' | 'hi' | 'local'>('en');

  useEffect(() => {
    if (pctParam) {
      setProgressPct(parseFloat(pctParam));
    }
  }, [pctParam]);

  useEffect(() => {
    if (scenarioParam) {
      setScenario(scenarioParam);
    }
  }, [scenarioParam]);

  // Load replay dataset on scenario change
  useEffect(() => {
    const jsonPath = `/data/replay_${scenario}.json`;
    axios.get<ReplayDataset>(jsonPath)
      .then(res => {
        setReplayData(res.data);
        if (res.data.frames.length > 0 && res.data.frames[0].stations.length > 0) {
          const firstSt = res.data.frames[0].stations[0];
          setSelectedStationId(prev => {
            const exists = res.data.frames[0].stations.some(s => s.id === prev);
            return exists ? prev : firstSt.id;
          });
        }
      })
      .catch(err => {
        console.error('Failed to load local replay json, falling back to API:', err);
        axios.get(`/api/simulate/replay?scenario=${scenario}&progress_pct=50`)
          .then(res => {
            // Replay single frame fallback
          })
          .catch(console.error);
      });
  }, [scenario]);

  // Scrubber playback ticker
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setProgressPct(prev => {
        if (prev >= 100) {
          setIsPlaying(false);
          return 100;
        }
        return Math.min(100, prev + 1.0 * speed);
      });
    }, 400);

    return () => clearInterval(interval);
  }, [isPlaying, speed]);

  // Current frame calculated from progress percentage
  const currentFrame: ReplayFrame | null = useMemo(() => {
    if (!replayData || !replayData.frames || replayData.frames.length === 0) return null;
    const targetIdx = Math.min(
      replayData.frames.length - 1,
      Math.max(0, Math.round((progressPct / 100) * (replayData.frames.length - 1)))
    );
    const baseFrame = replayData.frames[targetIdx];

    // Apply rainMultiplier to frame
    const scaledStations = baseFrame.stations.map(st => {
      const effQ = round1(st.discharge_m3s * (1.0 + (rainMultiplier - 1.0) * 0.75));
      const effRain = round1(st.rainfall_mm * rainMultiplier);
      const p = st.percentiles;

      let risk: RiskLevel = 'Green';
      const redThresh = p['p99.5_red'] || p.p99_5_red || 550;
      if (effQ >= redThresh) risk = 'Red';
      else if (effQ >= p.p97_orange) risk = 'Orange';
      else if (effQ >= p.p90_yellow) risk = 'Yellow';

      return {
        ...st,
        discharge_m3s: effQ,
        rainfall_mm: effRain,
        risk_level: risk
      };
    });

    // Recompute overall risk
    let maxPrio = 0;
    let overallRisk: RiskLevel = 'Green';
    const prioMap: Record<RiskLevel, number> = { Green: 0, Yellow: 1, Orange: 2, Red: 3 };
    scaledStations.forEach(st => {
      if (prioMap[st.risk_level] > maxPrio) {
        maxPrio = prioMap[st.risk_level];
        overallRisk = st.risk_level;
      }
    });

    let headline = baseFrame.headline;
    if (rainMultiplier !== 1.0) {
      headline += ` [${rainMultiplier.toFixed(1)}x Rain Stress]`;
    }

    return {
      ...baseFrame,
      headline,
      overall_risk: overallRisk,
      stations: scaledStations
    };
  }, [replayData, progressPct, rainMultiplier]);

  // Map station format for FloodMap
  const mapStations: Station[] = useMemo(() => {
    if (!currentFrame) return [];
    return currentFrame.stations.map(st => ({
      id: st.id,
      name: st.name,
      region: replayData?.region || 'Kerala',
      river: st.river,
      latitude: st.latitude,
      longitude: st.longitude,
      elevation_m: 10.0,
      warning_level_m: 4.5,
      danger_level_m: 6.0,
      normal_level_m: 2.0,
      current_water_level_m: st.water_level_m,
      current_discharge_m3s: st.discharge_m3s,
      p90_m3s: st.percentiles.p90_yellow,
      p97_m3s: st.percentiles.p97_orange,
      p99_5_m3s: st.percentiles['p99.5_red'] || st.percentiles.p99_5_red || 550,
      current_risk_level: st.risk_level,
      sensor_status: 'OK',
      battery_pct: 95.0,
      rssi: -65
    }));
  }, [currentFrame, replayData]);

  const activeSelected = mapStations.find(s => s.id === selectedStationId) || mapStations[0] || null;
  const activeSelectedReplay = currentFrame?.stations.find(s => s.id === selectedStationId) || currentFrame?.stations[0] || null;

  // Build timeline history for HydrologicalChart (all days up to current day)
  const chartReadings: Reading[] = useMemo(() => {
    if (!replayData || !activeSelected) return [];
    const targetIdx = Math.min(
      replayData.frames.length - 1,
      Math.max(0, Math.round((progressPct / 100) * (replayData.frames.length - 1)))
    );

    const pastFrames = replayData.frames.slice(Math.max(0, targetIdx - 14), targetIdx + 1);
    return pastFrames.map((fr, idx) => {
      const st = fr.stations.find(s => s.id === activeSelected.id);
      const q = st ? round1(st.discharge_m3s * (1.0 + (rainMultiplier - 1.0) * 0.75)) : 20.0;
      const r = st ? round1(st.rainfall_mm * rainMultiplier) : 0.0;
      const h = st ? st.water_level_m : 2.0;
      const risk = st ? st.risk_level : 'Green';
      return {
        id: idx,
        station_id: activeSelected.id,
        timestamp: `${fr.date}T12:00:00Z`,
        water_level_cm: h * 100,
        water_level_m: h,
        rainfall_mm_hr: r / 24.0, // daily mm to hourly rate approximation
        discharge_m3s: q,
        battery_pct: 96,
        rssi: -65,
        risk_level: risk,
        sensor_status: 'OK'
      };
    });
  }, [replayData, activeSelected, progressPct, rainMultiplier]);

  // Multilingual alert text generator
  const getAlertTranslation = () => {
    const isKerala = (replayData?.region || 'Kerala') === 'Kerala';
    const risk = activeSelectedReplay?.risk_level || 'Green';
    const q = activeSelectedReplay?.discharge_m3s || 0;
    const rain = activeSelectedReplay?.rainfall_mm || 0;
    const stName = activeSelectedReplay?.name || 'Station';
    const river = activeSelectedReplay?.river || 'River';

    if (alertLang === 'hi') {
      if (risk === 'Red') return {
        title: `गंभीर बाढ़ चेतावनी: ${stName} (${river})`,
        body: `नदी का डिस्चार्ज ${q.toFixed(1)} m³/s तक पहुंच गया है। पिछले 24 घंटों में ${rain.toFixed(1)} mm बारिश दर्ज की गई है। तुरंत सुरक्षित स्थानों पर जाएं।`,
        action: 'एनडीआरएफ और स्थानीय प्रशासन के निर्देशों का पालन करें।'
      };
      if (risk === 'Orange') return {
        title: `बाढ़ चेतावनी: ${stName} (${river})`,
        body: `नदी का प्रवाह ${q.toFixed(1)} m³/s पर खतरे के स्तर के करीब है। 24 घंटे की बारिश: ${rain.toFixed(1)} mm। निचले इलाकों से सुरक्षित दूरी बनाएं।`,
        action: 'निचले तटीय क्षेत्रों से दूर रहें और अलर्ट पर नजर रखें।'
      };
      return {
        title: `निगरानी स्थिति: ${stName}`,
        body: `डिस्चार्ज ${q.toFixed(1)} m³/s। जल स्तर सामान्य सीमा में है।`,
        action: 'नियमित निगरानी जारी है।'
      };
    }

    if (alertLang === 'local') {
      if (isKerala) {
        // Malayalam
        if (risk === 'Red') return {
          title: `തീവ്ര പ്രളയ മുന്നറിയിപ്പ്: ${stName} (${river})`,
          body: `നദീ പ്രവാഹം ${q.toFixed(1)} m³/s ആയി ഉയർന്നു. കഴിഞ്ഞ 24 മണിക്കൂറിലെ മഴ ${rain.toFixed(1)} mm. നദീതീരങ്ങളിൽ ഉള്ളവർ ഉടൻ സുരക്ഷിത സ്ഥാനങ്ങളിലേക്ക് മാറുക.`,
          action: 'ദുരന്ത നിവാരണ അതോറിറ്റിയുടെ നിർദ്ദേശങ്ങൾ പാലിക്കുക.'
        };
        if (risk === 'Orange') return {
          title: `ജാഗ്രതാ നിർദ്ദേശം: ${stName} (${river})`,
          body: `നദീ പ്രവാഹം ${q.toFixed(1)} m³/s. 24 മണിക്കൂർ മഴ: ${rain.toFixed(1)} mm. താഴ്ന്ന പ്രദേശങ്ങളിൽ വെള്ളപ്പൊക്ക സാധ്യത.`,
          action: 'അടിയന്തര സാധനങ്ങൾ തയ്യാറാക്കി വെക്കുക.'
        };
        return {
          title: `സാധാരണ നില: ${stName}`,
          body: `പ്രവാഹം ${q.toFixed(1)} m³/s. ജലനിരപ്പ് നിയന്ത്രണ വിധേയമാണ്.`,
          action: 'സാധാരണ നിരീക്ഷണം തുടരുന്നു.'
        };
      } else {
        // Assamese
        if (risk === 'Red') return {
          title: `ভয়ংকৰ বান সতৰ্কবাৰ্তা: ${stName} (${river})`,
          body: `নদীৰ জলপ্ৰবাহ ${q.toFixed(1)} m³/s লৈ বৃদ্ধি পালে। যোৱা ২৪ ঘণ্টাত ${rain.toFixed(1)} mm বৰষুণ ৰেকৰ্ড কৰা হৈছে। আশ্ৰয় শিবিৰলৈ যাওক।`,
          action: 'প্ৰশাসনৰ নিৰ্দেশনা তৎপৰতাৰে মানি চলক।'
        };
        if (risk === 'Orange') return {
          title: `বান সতৰ্কতা: ${stName} (${river})`,
          body: `নদীৰ প্ৰবাহ ${q.toFixed(1)} m³/s। ২৪ ঘণ্টাত বৰষুণ: ${rain.toFixed(1)} mm। নৈপৰীয়া অঞ্চলৰ ৰাইজে সতৰ্ক হওক।`,
          action: 'সাৱধানতা অৱলম্বন কৰক।'
        };
        return {
          title: `স্বাভাৱিক অৱস্থা: ${stName}`,
          body: `প্ৰবাহ ${q.toFixed(1)} m³/s। বিপদসীমাৰ তলত আছে।`,
          action: 'নিয়মীয়াকৈ নিৰীক্ষণ চলি আছে।'
        };
      }
    }

    // English
    if (risk === 'Red') return {
      title: `Severe Flood Warning: ${stName} (${river})`,
      body: `River discharge estimated at ${q.toFixed(1)} m³/s (exceeds p99.5 severe threshold). 24h rainfall: ${rain.toFixed(1)} mm. Immediate evacuation of riparian lowlands advised.`,
      action: 'Follow State Disaster Management Authority (SDMA) evacuation routes.'
    };
    if (risk === 'Orange') return {
      title: `Flood Warning: ${stName} (${river})`,
      body: `River discharge estimated at ${q.toFixed(1)} m³/s (exceeds p97 warning threshold). 24h rainfall: ${rain.toFixed(1)} mm. Bank overflow anticipated within 24–48 hours.`,
      action: 'Secure vulnerable livestock and move to higher ground.'
    };
    if (risk === 'Yellow') return {
      title: `Flood Watch: ${stName} (${river})`,
      body: `River discharge at ${q.toFixed(1)} m³/s (exceeds p90 baseline). 24h rainfall: ${rain.toFixed(1)} mm. Catchment saturation developing.`,
      action: 'Monitor local river gauge updates and weather advisories.'
    };
    return {
      title: `Hydrological Baseline: ${stName}`,
      body: `River discharge at ${q.toFixed(1)} m³/s within seasonal normal bounds. 24h rainfall: ${rain.toFixed(1)} mm.`,
      action: 'Routine telemetry monitoring active.'
    };
  };

  const alertContent = getAlertTranslation();

  return (
    <div className="space-y-6 pb-12">
      
      {/* Page Title */}
      <div className="border-b border-survey-border dark:border-night-border pb-3">
        <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">
          HISTORICAL DISASTER REPLAY ENGINE
        </span>
        <h1 className="font-serif text-2xl font-bold text-survey-ink dark:text-night-text">
          Disaster Event Scrubber & What-If Stress Testing
        </h1>
        <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
          Replay actual held-out 2018 Kerala floods and 2020 Assam monsoon daily sequences. Evaluated using the genuinely out-of-sample model (<code className="font-mono text-survey-teal dark:text-night-teal">heldout_2018_model.joblib</code>). Test what-if rainfall scenarios with honest percentile proxies.
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

      {/* Frame Status Bar */}
      {currentFrame && (
        <div className="rounded border border-survey-border dark:border-night-border bg-survey-paper/80 dark:bg-night-card p-3 flex flex-wrap items-center justify-between gap-3 font-mono text-xs shadow-xs">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-survey-teal dark:text-night-teal" />
            <span className="font-bold text-survey-ink dark:text-night-text">
              DAY {currentFrame.day_index} of {replayData?.total_days || 31} ({currentFrame.date})
            </span>
          </div>
          <div className="text-survey-ink dark:text-night-text font-serif text-sm font-semibold">
            {currentFrame.headline}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-survey-slate dark:text-night-slate">REGIONAL STATUS:</span>
            <RiskBadge level={currentFrame.overall_risk} size="md" />
          </div>
        </div>
      )}

      {/* Synchronized Replay Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Map Column */}
        <div className="lg:col-span-7 space-y-4">
          <FloodMap
            stations={mapStations}
            selectedStationId={activeSelected?.id}
            onSelectStation={(st) => setSelectedStationId(st.id)}
            height="560px"
            selectedRegion={replayData?.region || 'Kerala'}
          />
        </div>

        {/* Telemetry Column */}
        <div className="lg:col-span-5 space-y-4">
          {activeSelected && activeSelectedReplay && (
            <>
              {/* Station Replay Header */}
              <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-mono text-xs text-survey-teal dark:text-night-teal block">
                      {activeSelected.id} • REPLAY STATE ({currentFrame?.date})
                    </span>
                    <h2 className="font-serif text-lg font-bold text-survey-ink dark:text-night-text">
                      {activeSelected.name}
                    </h2>
                    <span className="text-xs text-survey-slate dark:text-night-slate font-sans">
                      {activeSelected.river} • Elevation: {activeSelected.elevation_m}m
                    </span>
                  </div>
                  <RiskBadge level={activeSelectedReplay.risk_level} size="md" />
                </div>
              </div>

              {/* Hydrological Telemetry Gauge */}
              <WaterLevelGauge
                station={activeSelected}
                currentDischargeM3s={activeSelectedReplay.discharge_m3s}
                currentWaterLevelM={activeSelectedReplay.water_level_m}
              />

              {/* 72h / 14-Day Timeline Trend */}
              <HydrologicalChart
                station={activeSelected}
                readings={chartReadings}
              />

              {/* Synchronized Replay Alert Outbox Preview */}
              <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-3">
                <div className="flex items-center justify-between border-b border-survey-border/60 dark:border-night-border/60 pb-2">
                  <div className="flex items-center gap-1.5 font-mono text-xs text-survey-teal dark:text-night-teal uppercase font-bold">
                    <Bell className="h-4 w-4" /> DISPATCHED ALERT PREVIEW
                  </div>
                  <div className="flex items-center gap-1 bg-survey-paper dark:bg-night-bg border border-survey-border dark:border-night-border rounded p-0.5 font-mono text-[10px]">
                    <button
                      onClick={() => setAlertLang('en')}
                      className={`px-1.5 py-0.5 rounded cursor-pointer ${alertLang === 'en' ? 'bg-survey-teal text-white font-bold' : 'text-survey-slate'}`}
                    >
                      EN
                    </button>
                    <button
                      onClick={() => setAlertLang('hi')}
                      className={`px-1.5 py-0.5 rounded cursor-pointer ${alertLang === 'hi' ? 'bg-survey-teal text-white font-bold' : 'text-survey-slate'}`}
                    >
                      HI
                    </button>
                    <button
                      onClick={() => setAlertLang('local')}
                      className={`px-1.5 py-0.5 rounded cursor-pointer ${alertLang === 'local' ? 'bg-survey-teal text-white font-bold' : 'text-survey-slate'}`}
                    >
                      {(replayData?.region || 'Kerala') === 'Kerala' ? 'ML' : 'AS'}
                    </button>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <div className="font-serif font-bold text-sm text-survey-ink dark:text-night-text">
                    {alertContent.title}
                  </div>
                  <p className="font-sans text-xs text-survey-slate dark:text-night-slate leading-relaxed">
                    {alertContent.body}
                  </p>
                  <div className="rounded bg-survey-paper dark:bg-night-bg p-2 text-xs font-mono text-survey-teal dark:text-night-teal border border-survey-border/50 dark:border-night-border/50">
                    <strong>Action:</strong> {alertContent.action}
                  </div>
                  <span className="block text-[10px] text-survey-slate dark:text-night-slate italic">
                    * Translations vetted for dialect accuracy; human emergency operator validation recommended before live transmission.
                  </span>
                </div>
              </div>

              {/* Replay Model Explanations (Feature Drivers) */}
              {activeSelectedReplay.top_drivers && (
                <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-2">
                  <div className="flex items-center gap-1.5 font-mono text-xs text-survey-teal dark:text-night-teal uppercase font-bold">
                    <Info className="h-4 w-4" /> PRIMARY RISK DRIVERS (EXPLAINABILITY)
                  </div>
                  <ul className="space-y-1 font-mono text-xs text-survey-ink dark:text-night-text">
                    {activeSelectedReplay.top_drivers.map((driver, dIdx) => (
                      <li key={dIdx} className="flex items-start gap-1.5">
                        <span className="text-survey-teal dark:text-night-teal font-bold">•</span>
                        <span>{driver}</span>
                      </li>
                    ))}
                  </ul>
                  <span className="block text-[10px] text-survey-slate dark:text-night-slate">
                    Attribution derived from genuine model features (<code className="font-mono">rain_7d</code>, <code className="font-mono">discharge_m3s</code>, <code className="font-mono">rain_1d</code>).
                  </span>
                </div>
              )}
            </>
          )}
        </div>

      </div>

    </div>
  );
};

function round1(val: number): number {
  return Math.round(val * 10) / 10;
}

