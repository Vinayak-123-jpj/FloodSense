import React, { useEffect, useState } from 'react';
import { api, FullMetricsSummary } from '../services/api';
import { ShieldCheck, AlertTriangle, Cpu, Layers, BarChart3, Database } from 'lucide-react';

export const ModelMethodPage: React.FC = () => {
  const [metrics, setMetrics] = useState<FullMetricsSummary | null>(null);

  useEffect(() => {
    api.getFullMetrics().then(setMetrics).catch(console.error);
  }, []);

  const m1d = metrics?.multi_horizon_time_split['1d']?.lightgbm;
  const m2d = metrics?.multi_horizon_time_split['2d']?.lightgbm;
  const m3d = metrics?.multi_horizon_time_split['3d']?.lightgbm;
  const heldout = metrics?.heldout_2018_event_test?.lightgbm;

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div className="border-b border-survey-border dark:border-night-border pb-3">
        <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">SCIENCE AUDIT & MULTI-HORIZON BENCHMARK (1990–2025)</span>
        <h1 className="font-serif text-3xl font-bold text-survey-ink dark:text-night-text">ML Risk Classifier Model Card & Audit</h1>
        <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
          Daily resolution ML pipeline (131,490 samples), 3 validation protocols, multi-horizon predictions (t+1d, t+2d, t+3d), and honest baseline comparisons.
        </p>
      </div>

      {/* Metrics Top Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">HELDOUT 2018 ACCURACY</span>
          <div className="text-2xl font-bold text-survey-ink dark:text-night-text">
            {heldout ? `${heldout.accuracy_pct}%` : '90.63%'}
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate">Genuinely Out-of-Sample 2018 Set</span>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">HELDOUT 2018 MACRO F1</span>
          <div className="text-2xl font-bold text-survey-ink dark:text-night-text">
            {heldout ? `${heldout.macro_f1_pct}%` : '84.71%'}
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate">
            High-Risk Recall: {heldout ? `${heldout.orange_red_recall_pct}%` : '91.4%'}
          </span>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">AUGUST 2018 LEAD TIME</span>
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            {metrics ? `${metrics.kerala_2018_median_lead_time_days} Days (${metrics.kerala_2018_median_lead_time_hours}h)` : '2 Days (48h)'}
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate">Prior to peak flood deluge</span>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">FALSE ALARM RATE (FAR)</span>
          <div className="text-2xl font-bold text-survey-ink dark:text-night-text">
            {heldout ? `${heldout.false_alarm_rate_pct}%` : '4.11%'}
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate">Orange/Red alert false positive rate</span>
        </div>
      </div>

      {/* Disclaimers & Data Honesty Banner */}
      <section className="rounded border border-amber-300 dark:border-amber-800 bg-amber-50/50 dark:bg-amber-950/20 p-4 space-y-2 font-sans text-xs">
        <div className="flex items-center gap-2 font-serif font-bold text-sm text-amber-900 dark:text-amber-200">
          <AlertTriangle className="h-5 w-5 text-amber-600" /> Critical Data Science Disclaimers
        </div>
        <ul className="list-disc list-inside space-y-1 text-survey-ink dark:text-night-text leading-relaxed">
          <li><strong>GloFAS Modeled Discharge:</strong> River discharge values ($m^3/s$) are obtained from Open-Meteo GloFAS reanalysis modeling, NOT physical river gauge height meters.</li>
          <li><strong>Percentile Risk Labels:</strong> Station danger levels are defined using station-specific historical training period percentiles (p90=Yellow, p97=Orange, p99.5=Red), NOT official CWC absolute stage thresholds.</li>
          <li><strong>Daily Temporal Resolution:</strong> Training data consists of daily rows (131,490 samples from 1990 to 2025 across 10 stations), matching GloFAS update rates.</li>
        </ul>
      </section>

      {/* Multi-Horizon Performance Comparison Table */}
      <section className="space-y-3">
        <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">Multi-Horizon Performance & Baseline Comparison</h2>
        
        <div className="overflow-x-auto rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card">
          <table className="w-full text-left border-collapse font-sans text-xs">
            <thead>
              <tr className="border-b border-survey-border dark:border-night-border bg-survey-paper dark:bg-night-bg font-mono text-[11px] text-survey-teal dark:text-night-teal uppercase">
                <th className="p-3">Horizon</th>
                <th className="p-3">Model</th>
                <th className="p-3">Accuracy</th>
                <th className="p-3">Macro F1</th>
                <th className="p-3">False Alarm Rate (FAR)</th>
                <th className="p-3">Missed Event Rate (MER)</th>
                <th className="p-3">Orange/Red Recall</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-survey-border/40 dark:divide-night-border/40">
              {/* 1d Horizon */}
              <tr className="bg-survey-paper/30 dark:bg-night-bg/30 hover:bg-survey-paper/50">
                <td className="p-3 font-mono font-bold" rowSpan={4}>t + 1d (24h)</td>
                <td className="p-3 font-semibold text-survey-ink dark:text-night-text">LightGBM (Primary)</td>
                <td className="p-3 font-mono font-bold text-emerald-600 dark:text-emerald-400">{m1d?.accuracy_pct}%</td>
                <td className="p-3 font-mono font-bold">{m1d?.macro_f1_pct}%</td>
                <td className="p-3 font-mono">{m1d?.false_alarm_rate_pct}%</td>
                <td className="p-3 font-mono">{m1d?.missed_event_rate_pct}%</td>
                <td className="p-3 font-mono font-bold text-emerald-600 dark:text-emerald-400">{m1d?.orange_red_recall_pct}%</td>
              </tr>
              <tr className="hover:bg-survey-paper/50">
                <td className="p-3 text-survey-slate dark:text-night-slate">Shallow Tree Baseline (depth=2)</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.shallow_tree_baseline?.accuracy_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.shallow_tree_baseline?.macro_f1_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.shallow_tree_baseline?.false_alarm_rate_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.shallow_tree_baseline?.missed_event_rate_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.shallow_tree_baseline?.orange_red_recall_pct}%</td>
              </tr>
              <tr className="hover:bg-survey-paper/50">
                <td className="p-3 text-survey-slate dark:text-night-slate">Persistence Baseline</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.persistence_baseline?.accuracy_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.persistence_baseline?.macro_f1_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.persistence_baseline?.false_alarm_rate_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.persistence_baseline?.missed_event_rate_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.persistence_baseline?.orange_red_recall_pct}%</td>
              </tr>
              <tr className="hover:bg-survey-paper/50">
                <td className="p-3 text-survey-slate dark:text-night-slate">Threshold Rule Benchmark</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.threshold_baseline?.accuracy_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.threshold_baseline?.macro_f1_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.threshold_baseline?.false_alarm_rate_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.threshold_baseline?.missed_event_rate_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['1d']?.threshold_baseline?.orange_red_recall_pct}%</td>
              </tr>

              {/* 2d Horizon */}
              <tr className="bg-survey-paper/30 dark:bg-night-bg/30 hover:bg-survey-paper/50">
                <td className="p-3 font-mono font-bold" rowSpan={2}>t + 2d (48h)</td>
                <td className="p-3 font-semibold text-survey-ink dark:text-night-text">LightGBM (Primary)</td>
                <td className="p-3 font-mono font-bold text-emerald-600 dark:text-emerald-400">{m2d?.accuracy_pct}%</td>
                <td className="p-3 font-mono font-bold">{m2d?.macro_f1_pct}%</td>
                <td className="p-3 font-mono">{m2d?.false_alarm_rate_pct}%</td>
                <td className="p-3 font-mono">{m2d?.missed_event_rate_pct}%</td>
                <td className="p-3 font-mono font-bold text-emerald-600 dark:text-emerald-400">{m2d?.orange_red_recall_pct}%</td>
              </tr>
              <tr className="hover:bg-survey-paper/50">
                <td className="p-3 text-survey-slate dark:text-night-slate">Persistence Baseline</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['2d']?.persistence_baseline?.accuracy_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['2d']?.persistence_baseline?.macro_f1_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['2d']?.persistence_baseline?.false_alarm_rate_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['2d']?.persistence_baseline?.missed_event_rate_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['2d']?.persistence_baseline?.orange_red_recall_pct}%</td>
              </tr>

              {/* 3d Horizon */}
              <tr className="bg-survey-paper/30 dark:bg-night-bg/30 hover:bg-survey-paper/50">
                <td className="p-3 font-mono font-bold" rowSpan={2}>t + 3d (72h)</td>
                <td className="p-3 font-semibold text-survey-ink dark:text-night-text">LightGBM (Primary)</td>
                <td className="p-3 font-mono font-bold text-emerald-600 dark:text-emerald-400">{m3d?.accuracy_pct}%</td>
                <td className="p-3 font-mono font-bold">{m3d?.macro_f1_pct}%</td>
                <td className="p-3 font-mono">{m3d?.false_alarm_rate_pct}%</td>
                <td className="p-3 font-mono">{m3d?.missed_event_rate_pct}%</td>
                <td className="p-3 font-mono font-bold text-emerald-600 dark:text-emerald-400">{m3d?.orange_red_recall_pct}%</td>
              </tr>
              <tr className="hover:bg-survey-paper/50">
                <td className="p-3 text-survey-slate dark:text-night-slate">Persistence Baseline</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['3d']?.persistence_baseline?.accuracy_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['3d']?.persistence_baseline?.macro_f1_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['3d']?.persistence_baseline?.false_alarm_rate_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['3d']?.persistence_baseline?.missed_event_rate_pct}%</td>
                <td className="p-3 font-mono">{metrics?.multi_horizon_time_split['3d']?.persistence_baseline?.orange_red_recall_pct}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Section: Kerala August 2018 Historic Backtest */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-survey-teal dark:text-night-teal" />
          <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">Held-Out 2018 Flood Event Validation & Backtest</h2>
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
              <h3 className="font-serif font-bold text-sm text-survey-teal dark:text-night-teal mb-1">Genuinely Out-of-Sample Protocol</h3>
              <p>
                Year 2018 (including a 7-day safety buffer on each side: 2017-12-25 to 2019-01-07) was strictly removed from training data.
                Station discharge percentiles were recalculated strictly on non-2018 training data.
              </p>
            </div>
            <ul className="space-y-2 list-disc list-inside">
              <li><strong>Accuracy:</strong> {heldout?.accuracy_pct}% on held-out 2018 dataset.</li>
              <li><strong>Macro F1:</strong> {heldout?.macro_f1_pct}% (vs Persistence {metrics?.heldout_2018_event_test?.persistence_baseline?.macro_f1_pct}%).</li>
              <li><strong>High-Risk Recall:</strong> {heldout?.orange_red_recall_pct}% recall on severe Orange/Red alert days.</li>
              <li><strong>Lead Time:</strong> Median warning lead time of <strong>{metrics?.kerala_2018_median_lead_time_days} days ({metrics?.kerala_2018_median_lead_time_hours} hours)</strong> prior to peak discharge across Kerala stations.</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Section: Confusion Matrix & Feature Importance */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-3">
          <h3 className="font-serif text-lg font-bold text-survey-ink dark:text-night-text">Held-Out 2018 Confusion Matrix</h3>
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
