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

  useEffect(() => {
    api.getStations().then(setStations).catch(console.error);
    api.getFullMetrics().then(setMetrics).catch(console.error);
  }, []);

  const leadDays = metrics?.kerala_2018_median_lead_time_days ?? 2;
  const leadHours = metrics?.kerala_2018_median_lead_time_hours ?? 48;

  const h2018_1d = metrics?.heldout_2018_multi_horizon?.['1d'];
  const macroF1 = h2018_1d?.lightgbm?.macro_f1_pct ?? 84.71;
  const persF1 = h2018_1d?.persistence_baseline?.macro_f1_pct ?? 85.58;
  const recall = h2018_1d?.lightgbm?.orange_red_recall_pct ?? 91.40;

  return (
    <div className="space-y-8 pb-12">
      <GuidedDemoModal isOpen={isDemoOpen} onClose={() => setIsDemoOpen(false)} />
      
      {/* Hero Section */}
      <section className="border-b border-survey-border dark:border-night-border pb-6">
        <div className="max-w-4xl space-y-3">
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded border border-survey-teal/30 dark:border-night-teal/30 bg-survey-card dark:bg-night-card font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-widest">
            <Shield className="h-3.5 w-3.5" /> FOSSEE NATIONAL MAKE-A-THON 2026 BLUEPRINT
          </div>

          <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-survey-ink dark:text-night-text leading-tight">
            Precision flood early-warning powered by virtual sensor digital twins.
          </h1>

          <p className="font-sans text-sm sm:text-base text-survey-slate dark:text-night-slate leading-relaxed max-w-3xl">
            FloodSense combines physical river telemetry, Open-Meteo hydrological forecasts, and LightGBM machine learning to provide 24-to-72-hour early warning lead times across Kerala and Assam river basins.
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
