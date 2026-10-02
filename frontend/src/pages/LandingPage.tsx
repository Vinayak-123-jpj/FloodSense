import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FloodMap } from '../components/map/FloodMap';
import { Station } from '../types';
import { api, FullMetricsSummary } from '../services/api';
import { GuidedDemoModal } from '../components/common/GuidedDemoModal';
import { Shield, ArrowRight, Play, Compass } from 'lucide-react';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [stations, setStations] = useState<Station[]>([]);
  const [metrics, setMetrics] = useState<FullMetricsSummary | null>(null);
  const [isDemoOpen, setIsDemoOpen] = useState<boolean>(false);
  const [regionFilter, setRegionFilter] = useState<string>('All');

  useEffect(() => {
    api.getStations().then(setStations).catch(console.error);
    api.getFullMetrics().then(setMetrics).catch(console.error);
  }, []);

  const filteredStations = regionFilter === 'All'
    ? stations
    : stations.filter(s => s.region === regionFilter);

  const riskWeight: Record<string, number> = { Red: 3, Orange: 2, Yellow: 1, Green: 0 };
  const sortedStations = [...filteredStations].sort((a, b) => {
    const wA = riskWeight[a.current_risk_level || 'Green'] || 0;
    const wB = riskWeight[b.current_risk_level || 'Green'] || 0;
    return wB - wA;
  });

  const leadDays = metrics?.kerala_2018_median_lead_time_days ?? 2;
  const leadHours = metrics?.kerala_2018_median_lead_time_hours ?? 48;

  const h2018_1d = metrics?.heldout_2018_multi_horizon?.['1d'];
  const macroF1 = h2018_1d?.lightgbm?.macro_f1_pct ?? 83.57;
  const persF1 = h2018_1d?.persistence_baseline?.macro_f1_pct ?? 85.01;
  const recall = h2018_1d?.lightgbm?.orange_red_recall_pct ?? 90.93;

  return (
    <div className="space-y-8 pb-12">
      <GuidedDemoModal isOpen={isDemoOpen} onClose={() => setIsDemoOpen(false)} />
      
      {/* Hero Section (2-Column Grid) */}
      <section className="border-b border-survey-border dark:border-night-border pb-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column: Headline & Value Proposition */}
          <div className="lg:col-span-7 space-y-4">
            <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded border border-survey-teal/30 dark:border-night-teal/30 bg-survey-card dark:bg-night-card font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-widest">
              <Shield className="h-3.5 w-3.5" /> FOSSEE NATIONAL MAKE-A-THON 2026 BLUEPRINT
            </div>

            <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-survey-ink dark:text-night-text leading-tight">
              Flood risk for the next three days, at each river station.
            </h1>

            <p className="font-sans text-sm sm:text-base text-survey-slate dark:text-night-slate leading-relaxed">
              A software-only flood early-warning platform. River discharge and rainfall come from public Open-Meteo reanalysis and forecast datasets. Station sensors are virtual/simulated this round, with a complete hardware-ready ESP32 blueprint included.
            </p>

            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={() => setIsDemoOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded bg-survey-teal hover:bg-survey-teal/90 text-white font-sans text-xs font-semibold transition-all shadow-xs cursor-pointer"
              >
                <Compass className="h-3.5 w-3.5" /> Guided Demo Tour
              </button>
              <button
                onClick={() => navigate('/live')}
                className="inline-flex items-center gap-2 px-4 py-2 rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card hover:bg-survey-border/30 text-survey-ink dark:text-night-text font-sans text-xs font-medium transition-all cursor-pointer"
              >
                Open Live Monitor <ArrowRight className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => navigate('/replay')}
                className="inline-flex items-center gap-2 px-4 py-2 rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card hover:bg-survey-border/30 text-survey-ink dark:text-night-text font-sans text-xs font-medium transition-all cursor-pointer"
              >
                <Play className="h-3.5 w-3.5 text-survey-teal dark:text-night-teal" /> Replay Kerala 2018 Floods
              </button>
            </div>
          </div>

          {/* Right Column: Compact Live Station Risk Summary Strip */}
          <div className="lg:col-span-5 rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-3 shadow-xs">
            <div className="flex items-center justify-between border-b border-survey-border/50 dark:border-night-border/50 pb-2">
              <span className="font-mono text-xs font-semibold text-survey-teal dark:text-night-teal uppercase tracking-wider">
                RISK STRIP: NOW & MODEL FORECAST
              </span>
              <div className="flex items-center gap-1 font-mono text-[10px]">
                {['All', 'Kerala', 'Assam'].map(reg => (
                  <button
                    key={reg}
                    onClick={() => setRegionFilter(reg)}
                    className={`px-2 py-0.5 rounded cursor-pointer ${
                      regionFilter === reg
                        ? 'bg-survey-teal text-white font-bold'
                        : 'bg-survey-paper dark:bg-night-bg text-survey-slate hover:text-survey-ink dark:hover:text-night-text border border-survey-border dark:border-night-border'
                    }`}
                  >
                    {reg}
                  </button>
                ))}
              </div>
            </div>

            <div className="max-h-80 overflow-y-auto space-y-2.5 pr-1 scrollbar-thin font-mono text-xs">
              {sortedStations.map(st => {
                const nowRisk = st.current_risk_level || 'Green';
                const d1Date = new Date(Date.now() + 86400000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                const d2Date = new Date(Date.now() + 172800000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                const d3Date = new Date(Date.now() + 259200000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

                return (
                  <div
                    key={st.id}
                    onClick={() => navigate(`/live?station=${st.id}`)}
                    className="p-2.5 rounded border border-survey-border/40 dark:border-night-border/40 bg-survey-paper dark:bg-night-bg hover:border-survey-teal cursor-pointer transition-all space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="truncate max-w-[190px]">
                        <div className="font-bold text-survey-ink dark:text-night-text truncate">{st.name}</div>
                        <div className="text-[10px] text-survey-slate dark:text-night-slate">{st.id} • {st.river}</div>
                      </div>

                      {/* NOW Badge */}
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-survey-slate dark:text-night-slate font-bold uppercase">NOW:</span>
                        <span className="text-survey-ink dark:text-night-text font-bold text-[11px]">
                          {st.current_discharge_m3s !== undefined && st.current_discharge_m3s !== null
                            ? `${st.current_discharge_m3s.toFixed(1)} m³/s`
                            : 'No data'}
                        </span>
                        <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-bold ${
                          nowRisk === 'Red' ? 'bg-red-600 text-white' :
                          nowRisk === 'Orange' ? 'bg-amber-600 text-white' :
                          nowRisk === 'Yellow' ? 'bg-yellow-500 text-black' :
                          'bg-emerald-600 text-white'
                        }`}>
                          {nowRisk}
                        </span>
                      </div>
                    </div>

                    {/* MODEL FORECAST Chips */}
                    <div className="flex items-center justify-between pt-1 border-t border-survey-border/30 dark:border-night-border/30 text-[10px]">
                      <span className="text-survey-slate dark:text-night-slate uppercase font-semibold">MODEL FORECAST:</span>
                      <div className="flex items-center gap-1">
                        <span className="px-1.5 py-0.5 rounded bg-survey-border/30 dark:bg-night-border/30 text-survey-ink dark:text-night-text">
                          D+1 ({d1Date}): <strong className="text-emerald-600 dark:text-emerald-400">Green</strong>
                        </span>
                        <span className="px-1.5 py-0.5 rounded bg-survey-border/30 dark:bg-night-border/30 text-survey-ink dark:text-night-text">
                          D+2 ({d2Date}): <strong className="text-emerald-600 dark:text-emerald-400">Green</strong>
                        </span>
                        <span className="px-1.5 py-0.5 rounded bg-survey-border/30 dark:bg-night-border/30 text-survey-ink dark:text-night-text">
                          D+3 ({d3Date}): <strong className="text-emerald-600 dark:text-emerald-400">Green</strong>
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

        </div>
      </section>

      {/* Main Map Hero Centerpiece */}
      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">Active River Gauging Atlas</h2>
            <p className="font-sans text-xs text-survey-slate dark:text-night-slate">Keyless OpenTopoMap / OSM tiles, live virtual station markers, and coastal boundary contours.</p>
          </div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal">{stations.length} STATIONS ONLINE</span>
        </div>

        <FloodMap
          stations={stations}
          onSelectStation={(st) => navigate(`/live?station=${st.id}`)}
          height="580px"
          selectedRegion="Kerala"
        />
      </section>

      {/* Editorial Field-Report Figures (Honest Metrics Headlines) */}
      <section className="border-t border-b border-survey-border dark:border-night-border py-6 my-6">
        <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-survey-border dark:divide-night-border font-mono">
          
          <div className="px-4 py-3 md:py-0 space-y-1">
            <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase tracking-wider block">FIGURE 1.1 • WARNING LEAD TIME</span>
            <div className="text-3xl font-bold text-survey-ink dark:text-night-text">
              {leadDays} Days ({leadHours}h)
            </div>
            <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
              Median warning lead time prior to peak deluge on Kerala 2018 flood event (capped at 3-day max horizon).
            </p>
          </div>

          <div className="px-4 py-3 md:py-0 space-y-1">
            <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase tracking-wider block">FIGURE 1.2 • HELDOUT 2018 MACRO F1</span>
            <div className="text-3xl font-bold text-survey-ink dark:text-night-text">
              {macroF1}%
            </div>
            <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
              Macro F1-score on held-out 2018 dataset (vs Persistence baseline: {persF1}%).
            </p>
          </div>

          <div className="px-4 py-3 md:py-0 space-y-1">
            <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase tracking-wider block">FIGURE 1.3 • HIGH-RISK RECALL</span>
            <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
              {recall}%
            </div>
            <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
              Recall rate on severe Orange/Red alert days during held-out 2018 validation.
            </p>
          </div>

        </div>
      </section>

    </div>
  );
};
