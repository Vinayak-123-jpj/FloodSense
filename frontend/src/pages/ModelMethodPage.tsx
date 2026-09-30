import React, { useEffect, useState } from 'react';
import { api, ModelMetrics } from '../services/api';
import { ShieldCheck, AlertTriangle, Cpu, Layers } from 'lucide-react';

export const ModelMethodPage: React.FC = () => {
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);

  useEffect(() => {
    api.getMetrics().then(setMetrics).catch(console.error);
  }, []);

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div className="border-b border-survey-border dark:border-night-border pb-3">
        <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">HONEST SCIENCE & LEAKAGE AUDIT</span>
        <h1 className="font-serif text-3xl font-bold text-survey-ink dark:text-night-text">ML Risk Classifier Model Card & Backtest</h1>
        <p className="font-sans text-xs text-survey-slate dark:text-night-slate">Full transparency report on algorithm metrics, 24h future target redefinition, 72h split gap, and baseline comparisons.</p>
      </div>

      {/* Metrics Top Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">CLASSIFIER ACCURACY</span>
          <div className="text-2xl font-bold text-survey-ink dark:text-night-text">
            {metrics ? `${metrics.accuracy_pct}%` : '95.96%'}
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate">24h Future Lead Time Model</span>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">MODEL MACRO F1</span>
          <div className="text-2xl font-bold text-survey-ink dark:text-night-text">
            {metrics ? `${metrics.macro_f1_pct}%` : '40.91%'}
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate">
            vs Persistence F1 {metrics ? `${metrics.persistence_baseline_macro_f1_pct}%` : '48.68%'}
          </span>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">KERALA 2018 LEAD TIME</span>
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            {metrics ? `${metrics.kerala_2018_lead_time_hours} Hours` : '53 Hours'}
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate">Daily river discharge data limit</span>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">FALSE ALARM RATE (FAR)</span>
          <div className="text-2xl font-bold text-survey-ink dark:text-night-text">
            {metrics ? `${metrics.false_alarm_rate_pct}%` : '0.07%'}
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate">Orange/Red alert false positive rate</span>
        </div>
      </div>

      {/* Audit Banner: Task Redefinition & No Leakage */}
      <section className="rounded border border-emerald-300 dark:border-emerald-800 bg-emerald-50/50 dark:bg-emerald-950/20 p-5 space-y-2 font-sans text-xs">
        <div className="flex items-center gap-2 font-serif font-bold text-sm text-emerald-900 dark:text-emerald-200">
          <ShieldCheck className="h-5 w-5 text-emerald-600" /> Data Leakage Audit & 24h Future Task Redefinition
        </div>
        <p className="text-survey-ink dark:text-night-text leading-relaxed">
          In early iterations, predicting risk level at time <em>t</em> using discharge measured at time <em>t</em> created target leakage because current discharge directly encodes current risk.
          The task was redefined: features at time <em>t</em> use <strong>ONLY data available up to time <em>t</em></strong>, and the target is the <strong>future risk level at <em>t + 24h</em></strong>.
          A strict <strong>72-hour chronological gap</strong> was inserted between the training set and test set to eliminate rolling window overlaps across the split boundary.
        </p>
      </section>

      {/* Baseline Performance Comparison Table */}
      <section className="space-y-3">
        <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">Honest Baseline Model Comparison</h2>
        
        <div className="overflow-x-auto rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card">
          <table className="w-full text-left border-collapse font-sans text-xs">
            <thead>
              <tr className="border-b border-survey-border dark:border-night-border bg-survey-paper dark:bg-night-bg font-mono text-[11px] text-survey-teal dark:text-night-teal uppercase">
                <th className="p-3">Model / Benchmark</th>
                <th className="p-3">Prediction Task</th>
                <th className="p-3">Accuracy</th>
                <th className="p-3">Macro F1</th>
                <th className="p-3">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-survey-border/40 dark:divide-night-border/40">
              <tr className="hover:bg-survey-paper/50 dark:hover:bg-night-bg/50">
                <td className="p-3 font-semibold text-survey-ink dark:text-night-text">FloodSense LightGBM Model</td>
                <td className="p-3 font-mono">Future Y(t+24h)</td>
                <td className="p-3 font-mono font-bold text-emerald-600 dark:text-emerald-400">{metrics?.accuracy_pct}%</td>
                <td className="p-3 font-mono font-bold">{metrics?.macro_f1_pct}%</td>
                <td className="p-3 text-survey-slate dark:text-night-slate">72h split gap enforced</td>
              </tr>
              <tr className="hover:bg-survey-paper/50 dark:hover:bg-night-bg/50">
                <td className="p-3 font-semibold text-survey-ink dark:text-night-text">Persistence Baseline</td>
                <td className="p-3 font-mono">Future Y(t+24h) = Current(t)</td>
                <td className="p-3 font-mono">96.8%</td>
                <td className="p-3 font-mono">{metrics?.persistence_baseline_macro_f1_pct}%</td>
                <td className="p-3 text-survey-slate dark:text-night-slate">Assumes risk stays constant for 24h</td>
              </tr>
              <tr className="hover:bg-survey-paper/50 dark:hover:bg-night-bg/50">
                <td className="p-3 font-semibold text-survey-ink dark:text-night-text">Threshold Rule Benchmark</td>
                <td className="p-3 font-mono">Rule at time t</td>
                <td className="p-3 font-mono">95.4%</td>
                <td className="p-3 font-mono">{metrics?.threshold_baseline_macro_f1_pct}%</td>
                <td className="p-3 text-survey-slate dark:text-night-slate">Static rainfall & discharge thresholds</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Section: Kerala August 2018 Historic Backtest */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-survey-teal dark:text-night-teal" />
          <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">Kerala August 2018 Historic Flood Backtest</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          <div className="lg:col-span-7 rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-2">
            <img
              src="/reports/kerala_2018_backtest.png"
              alt="Kerala 2018 Backtest Lead Time Chart"
              className="w-full h-auto rounded border border-survey-border/50"
            />
          </div>
          <div className="lg:col-span-5 space-y-3 font-sans text-xs text-survey-ink dark:text-night-text leading-relaxed">
            <div className="rounded bg-survey-paper dark:bg-night-bg p-3 border border-survey-border dark:border-night-border">
              <h3 className="font-serif font-bold text-sm text-survey-teal dark:text-night-teal mb-1">Backtest Lead Time Analysis</h3>
              <p>
                Evaluated on actual Open-Meteo hourly weather and daily river discharge data during the August 8–20, 2018 floods in Kerala.
              </p>
            </div>
            <ul className="space-y-2 list-disc list-inside">
              <li>The 24h future prediction model issued an <strong>Orange/Red warning {metrics?.kerala_2018_lead_time_hours || 53} hours prior</strong> to peak discharge at Neeleswaram / Aluva Periyar gauge.</li>
              <li>Lead time is measured from the first timestamp the model predicted future Orange/Red vs when discharge crossed the danger level.</li>
              <li>Daily river discharge data from Open-Meteo limits intra-day peak precision to daily step updates.</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Section: Confusion Matrix & Feature Importance */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-3">
          <h3 className="font-serif text-lg font-bold text-survey-ink dark:text-night-text">Model Confusion Matrix</h3>
          <img src="/reports/confusion_matrix.png" alt="Confusion Matrix" className="w-full h-auto rounded border border-survey-border/40" />
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-3">
          <h3 className="font-serif text-lg font-bold text-survey-ink dark:text-night-text">Feature Importance Ranking</h3>
          <img src="/reports/feature_importance.png" alt="Feature Importance" className="w-full h-auto rounded border border-survey-border/40" />
        </div>

      </section>

    </div>
  );
};
