import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FloodMap } from '../components/map/FloodMap';
import { Station } from '../types';
import { api } from '../services/api';
import { Shield, ArrowRight, Play, Cpu, AlertTriangle, Layers } from 'lucide-react';
import { RiskBadge } from '../components/common/Badge';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [stations, setStations] = useState<Station[]>([]);

  useEffect(() => {
    api.getStations().then(setStations).catch(console.error);
  }, []);

  return (
    <div className="space-y-8 pb-12">
      
      {/* Hero Section */}
      <section className="border-b border-survey-border dark:border-night-border pb-8">
        <div className="max-w-4xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded border border-survey-teal/30 dark:border-night-teal/30 bg-survey-card dark:bg-night-card font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-widest">
            <Shield className="h-3.5 w-3.5" /> FOSSEE NATIONAL MAKE-A-THON 2026 BLUEPRINT
          </div>

          <h1 className="font-serif text-4xl sm:text-5xl font-bold tracking-tight text-survey-ink dark:text-night-text leading-tight">
            Precision flood early-warning powered by virtual sensor digital twins.
          </h1>

          <p className="font-sans text-base sm:text-lg text-survey-slate dark:text-night-slate leading-relaxed max-w-3xl">
            FloodSense combines physical river telemetry, Open-Meteo hydrological forecasts, and LightGBM machine learning to provide 24-to-72-hour early warning lead times across Kerala and Assam river basins.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <button
              onClick={() => navigate('/live')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded bg-survey-teal hover:bg-survey-teal/90 text-white font-sans text-sm font-semibold transition-all shadow-xs cursor-pointer"
            >
              Open Live Monitor <ArrowRight className="h-4 w-4" />
            </button>
            <button
              onClick={() => navigate('/replay')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card hover:bg-survey-border/30 text-survey-ink dark:text-night-text font-sans text-sm font-medium transition-all cursor-pointer"
            >
              <Play className="h-4 w-4 text-survey-teal dark:text-night-teal" /> Replay Kerala 2018 Floods
            </button>
          </div>
        </div>
      </section>

      {/* Main Map Centerpiece */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-serif text-2xl font-bold text-survey-ink dark:text-night-text">Active River Gauging Grid</h2>
            <p className="font-sans text-xs text-survey-slate dark:text-night-slate">Interactive desaturated atlas tiles with live station risk markers & low-lying zone contours.</p>
          </div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal">{stations.length} STATIONS ONLINE</span>
        </div>

        <FloodMap
          stations={stations}
          onSelectStation={(st) => navigate(`/live?station=${st.id}`)}
          height="540px"
        />
      </section>

      {/* Grid Highlights & Quick Stats */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
        
        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase">EARLY WARNING LEAD TIME</span>
            <Shield className="h-4 w-4 text-survey-teal dark:text-night-teal" />
          </div>
          <div className="font-mono text-3xl font-bold text-survey-ink dark:text-night-text">29 Hours</div>
          <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
            Backtested lead time on the historic August 2018 Kerala flood event prior to peak discharge.
          </p>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase">ML CLASSIFIER ACCURACY</span>
            <Cpu className="h-4 w-4 text-survey-teal dark:text-night-teal" />
          </div>
          <div className="font-mono text-3xl font-bold text-survey-ink dark:text-night-text">99.89%</div>
          <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
            LightGBM classifier trained on 35,064 hourly records using strict time-based splits.
          </p>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase">OPEN HARDWARE READY</span>
            <Layers className="h-4 w-4 text-survey-teal dark:text-night-teal" />
          </div>
          <div className="font-mono text-3xl font-bold text-survey-ink dark:text-night-text">₹3,990</div>
          <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
            Estimated cost per solar-autonomous ESP32 node with JSN-SR04T ultrasonic transducer.
          </p>
        </div>

      </section>

    </div>
  );
};
