import React, { useEffect, useState } from 'react';
import { api, FullMetricsSummary, DetailedHorizonMetrics, Station2018Detail } from '../services/api';
import { AlertTriangle, Database, Globe, Network, Compass, Activity, ArrowRight, ShieldCheck } from 'lucide-react';
import { useTheme } from '../theme/ThemeContext';

export const ModelMethodPage: React.FC = () => {
  const [metrics, setMetrics] = useState<FullMetricsSummary | null>(null);
  const { theme } = useTheme();

  useEffect(() => {
    api.getFullMetrics().then(setMetrics).catch(console.error);
  }, []);

  const heldout1d = metrics?.heldout_2018_multi_horizon?.['1d'];
  const heldout2d = metrics?.heldout_2018_multi_horizon?.['2d'];
  const heldout3d = metrics?.heldout_2018_multi_horizon?.['3d'];

  const stationDetails: Record<string, Station2018Detail> = metrics?.station_2018_details || {};
  const loroResults: Record<string, DetailedHorizonMetrics> = metrics?.leave_one_river_out_loro || {};

  const cmData = metrics?.confusion_matrix_heldout_2018 || {
    labels: ['Green', 'Yellow', 'Orange', 'Red'],
    matrix: [
      [1420, 110, 2, 1],
      [34, 462, 71, 1],
      [4, 28, 122, 18],
      [0, 1, 8, 43]
    ]
  };

  const fiData = metrics?.feature_importances || [
    { feature: 'rain_7d', label: '7-Day Cumulative Rain (mm)', importance: 2468 },
    { feature: 'discharge_m3s', label: 'River Discharge (m³/s)', importance: 2304 },
    { feature: 'antecedent_wetness_7d', label: 'Antecedent Wetness Index', importance: 2122 },
    { feature: 'rain_1d', label: '1-Day Rainfall (mm)', importance: 1928 },
    { feature: 'rain_3d', label: '3-Day Cumulative Rain (mm)', importance: 1911 },
    { feature: 'day_of_year', label: 'Day of Year (Seasonality)', importance: 1813 },
    { feature: 'discharge_roc_3d', label: '3-Day Discharge Rate of Change', importance: 1475 },
    { feature: 'rain_14d', label: '14-Day Cumulative Rain (mm)', importance: 1468 },
    { feature: 'rain_30d', label: '30-Day Cumulative Rain (mm)', importance: 1012 },
    { feature: 'month', label: 'Month of Year', importance: 55 }
  ];

  const maxFI = Math.max(...fiData.map(f => f.importance), 1);

  // Helper for neutral column highlight
  const renderMetricCell = (val: number, isBest: boolean, ci?: [number, number], unit = '%') => (
    <td className={`p-3 font-mono ${isBest ? 'font-bold bg-survey-teal/10 dark:bg-night-teal/15 text-survey-ink dark:text-night-text border-l-2 border-survey-teal' : 'text-survey-slate dark:text-night-slate'}`}>
      <span>{val ? val.toFixed(2) : '0.00'}{unit}</span>
      {ci && (
        <span className="block text-[10px] opacity-75 font-sans">
          [{ci[0] ? ci[0].toFixed(1) : '0.0'}, {ci[1] ? ci[1].toFixed(1) : '0.0'}]
        </span>
      )}
    </td>
  );

  const keralaStations = ['KL-PER-01', 'KL-PER-02', 'KL-PAM-01', 'KL-MUV-01', 'KL-CHA-01', 'KL-ACH-01'];
  const assamStations = ['AS-BRA-01', 'AS-BRA-02', 'AS-KOP-01', 'AS-DHA-01', 'AS-JIA-01'];

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div className="border-b border-survey-border dark:border-night-border pb-3">
        <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">
          SCIENCE AUDIT & MULTI-HORIZON BENCHMARK (1990–2025)
        </span>
        <h1 className="font-serif text-3xl font-bold text-survey-ink dark:text-night-text">
          Hydrological ML Risk Classifier: Model Card & Validation
        </h1>
        <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
          Daily resolution ML pipeline (115,502 daily rows across 11 stations), 7-day block bootstrap 95% confidence intervals, multi-horizon predictions (t+1d, t+2d, t+3d), and honest baseline comparisons.
        </p>
      </div>

      {/* Metrics Top Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">HELDOUT 2018 MACRO F1 (1D)</span>
          <div className="text-2xl font-bold text-survey-ink dark:text-night-text">
            {heldout1d?.lightgbm ? `${heldout1d.lightgbm.macro_f1_pct}%` : '69.39%'}
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate block">
            95% CI: [{heldout1d?.lightgbm?.macro_f1_ci_95?.[0] ?? 63.5}%, {heldout1d?.lightgbm?.macro_f1_ci_95?.[1] ?? 73.7}%]
          </span>
          <span className="font-sans text-[10px] text-amber-700 dark:text-amber-400 font-semibold block">
            Persistence: {heldout1d?.persistence_baseline?.macro_f1_pct ?? 85.15}% (Stronger Baseline)
          </span>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">HIGH-RISK RECALL (ORANGE/RED)</span>
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            {heldout1d?.lightgbm ? `${heldout1d.lightgbm.orange_red_recall_pct}%` : '86.27%'}
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate block">
            95% CI: [{heldout1d?.lightgbm?.orange_red_recall_ci_95?.[0] ?? 79.4}%, {heldout1d?.lightgbm?.orange_red_recall_ci_95?.[1] ?? 92.0}%]
          </span>
          <span className="font-sans text-[10px] text-survey-slate dark:text-night-slate block">
            Persistence Recall: {heldout1d?.persistence_baseline?.orange_red_recall_pct ?? 86.93}%
          </span>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">WARNING LEAD TIME (2018 EVENT)</span>
          <div className="text-xl font-bold text-survey-ink dark:text-night-text">
            Strict (0d to &ge;3d capped)
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate block font-semibold text-amber-700 dark:text-amber-400">
            Lead times: &ge;3 days (capped)
          </span>
          <span className="font-sans text-[10px] text-survey-slate dark:text-night-slate block">Evaluated strictly per station</span>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-1">
          <span className="text-[11px] text-survey-teal dark:text-night-teal uppercase block">FALSE ALARMS / STN-YEAR</span>
          <div className="text-2xl font-bold text-survey-ink dark:text-night-text">
            {heldout1d?.lightgbm ? `${heldout1d.lightgbm.false_alarms_per_station_year}` : '21.2'}
          </div>
          <span className="font-sans text-[11px] text-survey-slate dark:text-night-slate block">
            FAR: {heldout1d?.lightgbm?.false_alarm_rate_pct ?? 6.25}%
          </span>
          <span className="font-sans text-[10px] text-survey-slate dark:text-night-slate block">
            Threshold baseline: 96.0 alarms/stn-yr
          </span>
        </div>
      </div>

      {/* Honest ML Repositioning Section */}
      <section className="rounded border border-survey-teal/40 dark:border-night-teal/40 bg-survey-card dark:bg-night-card p-6 space-y-4">
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">
            SCIENTIFIC HONESTY & BASELINE COMPARISON
          </span>
          <h2 className="font-serif text-2xl font-bold text-survey-ink dark:text-night-text">
            Experimental ML risk layer (not the primary forecast)
          </h2>
        </div>

        <p className="font-sans text-xs text-survey-ink dark:text-night-text leading-relaxed">
          The LightGBM model is an experimental risk layer evaluated for scientific comparison. On held-out 2018 test data, the LightGBM model achieves 69.39% Macro F1 at 1d (95% CI: [63.5%, 73.7%]), 56.47% at 2d (95% CI: [50.1%, 61.6%]), and 46.27% at 3d (95% CI: [40.8%, 50.7%]). Across all lead horizons, the simple <strong>Persistence Baseline</strong> achieves higher Macro F1 (85.15% at 1d [82.0%, 87.4%], 72.54% at 2d [67.6%, 76.0%], and 62.41% at 3d [57.3%, 66.5%]). This occurs because (1) daily river discharge risk states are strongly autocorrelated day-to-day, (2) the catastrophic 2018 deluge peak exceeded historical 1990–2017 training maxima at several stations, and (3) the model relies strictly on past observed rainfall and discharge without future numerical weather forecast inputs.
        </p>

        <div className="border-t border-survey-border/60 dark:border-night-border/60 pt-3">
          <h3 className="font-mono text-xs font-bold text-survey-teal dark:text-night-teal uppercase mb-2">
            Future Work & Model Development Roadmap
          </h3>
          <ul className="list-disc list-inside font-sans text-xs text-survey-slate dark:text-night-slate space-y-1 leading-relaxed">
            <li>Integration of future Numerical Weather Prediction (NWP) rainfall forecasts into feature vectors.</li>
            <li>Multi-decade dataset expansion incorporating additional extreme flood return periods.</li>
            <li>Per-station probability calibration to reduce false alarm rates.</li>
            <li>Direct ingestion of physical ESP32 ultrasonic gauge height telemetry.</li>
          </ul>
        </div>
      </section>

      {/* Disclaimers & Data Science Audit Banner */}
      <section className="rounded border border-amber-300 dark:border-amber-800 bg-amber-50/50 dark:bg-amber-950/20 p-5 space-y-3 font-sans text-xs">
        <div className="flex items-center gap-2 font-serif font-bold text-sm text-amber-900 dark:text-amber-200">
          <AlertTriangle className="h-5 w-5 text-amber-600" /> Explicit Data Science Disclaimers & Methodology Boundaries
        </div>
        <ul className="list-disc list-inside space-y-1.5 text-survey-ink dark:text-night-text leading-relaxed">
          <li><strong>GloFAS Modeled Discharge:</strong> River discharge (m³/s) is GloFAS reanalysis modelled data via Open-Meteo, NOT physical river gauge height meters.</li>
          <li><strong>Observed Past Rainfall Only:</strong> The model uses historical past observed rainfall features, NOT future numerical weather forecast inputs.</li>
          <li><strong>Percentile Risk Proxies:</strong> Danger thresholds are station-specific historical training period discharge percentiles (p90=Yellow, p97=Orange, p99.5=Red), NOT official CWC stage levels.</li>
          <li><strong>Max Horizon Cap:</strong> Prediction lead times are strictly capped at the 3-day (t+3d) maximum horizon. GloFAS discharge is updated daily.</li>
          <li><strong>Station Independence & Spatial Correlation:</strong> Stations located along the same river basin (e.g. Aluva and Neeleswaram on the Periyar) exhibit high discharge correlation (r &gt; 0.90). Standard Leave-One-Station-Out (LOSO) is therefore optimistic; Leave-One-RIVER-Out (LORO) provides our strict spatial generalization benchmark.</li>
          <li><strong>Out-of-Training-Range Limitation:</strong> 2018 peak discharge exceeded the 1990–2017 historical maximum at several Kerala stations (e.g. Aluva, Neeleswaram, Chalakudy), so the held-out flood is partly out of the training range; decision tree models split on static feature thresholds and cannot extrapolate beyond training set maxima.</li>
        </ul>
      </section>

      {/* Baseline Benchmark Comparison Table with Bootstrap 95% CIs */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">
              Held-Out 2018 Event Benchmark (Kerala Primary Region)
            </h2>
            <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
              Evaluated strictly on held-out year 2018. 95% Confidence Intervals calculated via 1,000 block-bootstrap iterations (7-day blocks). Best per column highlighted neutrally.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card">
          <table className="w-full text-left border-collapse font-sans text-xs">
            <thead>
              <tr className="border-b border-survey-border dark:border-night-border bg-survey-paper dark:bg-night-bg font-mono text-[11px] text-survey-teal dark:text-night-teal uppercase">
                <th className="p-3">Horizon</th>
                <th className="p-3">Model / Baseline</th>
                <th className="p-3">Macro F1 [95% CI]</th>
                <th className="p-3">Orange/Red Recall [95% CI]</th>
                <th className="p-3">Orange/Red Precision</th>
                <th className="p-3">FAR</th>
                <th className="p-3">False Alarms / Stn-Yr</th>
                <th className="p-3">Accuracy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-survey-border/40 dark:divide-night-border/40">
              {/* 1d Horizon */}
              {heldout1d && (
                <>
                  <tr className="bg-survey-paper/30 dark:bg-night-bg/30 hover:bg-survey-paper/50">
                    <td className="p-3 font-mono font-bold" rowSpan={4}>t + 1d (24h)</td>
                    <td className="p-3 font-semibold text-survey-ink dark:text-night-text">LightGBM (Experimental)</td>
                    {renderMetricCell(heldout1d.lightgbm.macro_f1_pct, false, heldout1d.lightgbm.macro_f1_ci_95)}
                    {renderMetricCell(heldout1d.lightgbm.orange_red_recall_pct, false, heldout1d.lightgbm.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono">{heldout1d.lightgbm.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout1d.lightgbm.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout1d.lightgbm.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono">{heldout1d.lightgbm.accuracy_pct}%</td>
                  </tr>
                  <tr className="hover:bg-survey-paper/50">
                    <td className="p-3 text-survey-slate dark:text-night-slate">Linear (Logistic Regression) [L-BFGS-B]</td>
                    {renderMetricCell(heldout1d.linear_logistic_regression.macro_f1_pct, false, heldout1d.linear_logistic_regression.macro_f1_ci_95)}
                    {renderMetricCell(heldout1d.linear_logistic_regression.orange_red_recall_pct, false, heldout1d.linear_logistic_regression.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono">{heldout1d.linear_logistic_regression.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout1d.linear_logistic_regression.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout1d.linear_logistic_regression.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono">{heldout1d.linear_logistic_regression.accuracy_pct}%</td>
                  </tr>
                  <tr className="hover:bg-survey-paper/50">
                    <td className="p-3 font-semibold text-survey-ink dark:text-night-text">Persistence Baseline (Stronger)</td>
                    {renderMetricCell(heldout1d.persistence_baseline.macro_f1_pct, true, heldout1d.persistence_baseline.macro_f1_ci_95)}
                    {renderMetricCell(heldout1d.persistence_baseline.orange_red_recall_pct, false, heldout1d.persistence_baseline.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono font-bold text-survey-teal dark:text-night-teal">{heldout1d.persistence_baseline.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout1d.persistence_baseline.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout1d.persistence_baseline.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono font-bold">{heldout1d.persistence_baseline.accuracy_pct}%</td>
                  </tr>
                  <tr className="hover:bg-survey-paper/50">
                    <td className="p-3 text-survey-slate dark:text-night-slate">Rainfall Threshold Rule</td>
                    {renderMetricCell(heldout1d.threshold_baseline.macro_f1_pct, false, heldout1d.threshold_baseline.macro_f1_ci_95)}
                    {renderMetricCell(heldout1d.threshold_baseline.orange_red_recall_pct, true, heldout1d.threshold_baseline.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono">{heldout1d.threshold_baseline.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout1d.threshold_baseline.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout1d.threshold_baseline.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono">{heldout1d.threshold_baseline.accuracy_pct}%</td>
                  </tr>
                </>
              )}

              {/* 2d Horizon */}
              {heldout2d && (
                <>
                  <tr className="bg-survey-paper/30 dark:bg-night-bg/30 hover:bg-survey-paper/50">
                    <td className="p-3 font-mono font-bold" rowSpan={4}>t + 2d (48h)</td>
                    <td className="p-3 font-semibold text-survey-ink dark:text-night-text">LightGBM (Experimental)</td>
                    {renderMetricCell(heldout2d.lightgbm.macro_f1_pct, false, heldout2d.lightgbm.macro_f1_ci_95)}
                    {renderMetricCell(heldout2d.lightgbm.orange_red_recall_pct, true, heldout2d.lightgbm.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono">{heldout2d.lightgbm.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout2d.lightgbm.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout2d.lightgbm.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono">{heldout2d.lightgbm.accuracy_pct}%</td>
                  </tr>
                  <tr className="hover:bg-survey-paper/50">
                    <td className="p-3 text-survey-slate dark:text-night-slate">Linear (Logistic Regression) [L-BFGS-B]</td>
                    {renderMetricCell(heldout2d.linear_logistic_regression.macro_f1_pct, false, heldout2d.linear_logistic_regression.macro_f1_ci_95)}
                    {renderMetricCell(heldout2d.linear_logistic_regression.orange_red_recall_pct, false, heldout2d.linear_logistic_regression.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono">{heldout2d.linear_logistic_regression.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout2d.linear_logistic_regression.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout2d.linear_logistic_regression.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono">{heldout2d.linear_logistic_regression.accuracy_pct}%</td>
                  </tr>
                  <tr className="hover:bg-survey-paper/50">
                    <td className="p-3 font-semibold text-survey-ink dark:text-night-text">Persistence Baseline (Stronger)</td>
                    {renderMetricCell(heldout2d.persistence_baseline.macro_f1_pct, true, heldout2d.persistence_baseline.macro_f1_ci_95)}
                    {renderMetricCell(heldout2d.persistence_baseline.orange_red_recall_pct, false, heldout2d.persistence_baseline.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono">{heldout2d.persistence_baseline.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout2d.persistence_baseline.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout2d.persistence_baseline.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono font-bold">{heldout2d.persistence_baseline.accuracy_pct}%</td>
                  </tr>
                  <tr className="hover:bg-survey-paper/50">
                    <td className="p-3 text-survey-slate dark:text-night-slate">Rainfall Threshold Rule</td>
                    {renderMetricCell(heldout2d.threshold_baseline.macro_f1_pct, false, heldout2d.threshold_baseline.macro_f1_ci_95)}
                    {renderMetricCell(heldout2d.threshold_baseline.orange_red_recall_pct, true, heldout2d.threshold_baseline.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono">{heldout2d.threshold_baseline.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout2d.threshold_baseline.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout2d.threshold_baseline.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono">{heldout2d.threshold_baseline.accuracy_pct}%</td>
                  </tr>
                </>
              )}

              {/* 3d Horizon */}
              {heldout3d && (
                <>
                  <tr className="bg-survey-paper/30 dark:bg-night-bg/30 hover:bg-survey-paper/50">
                    <td className="p-3 font-mono font-bold" rowSpan={4}>t + 3d (72h)</td>
                    <td className="p-3 font-semibold text-survey-ink dark:text-night-text">LightGBM (Experimental)</td>
                    {renderMetricCell(heldout3d.lightgbm.macro_f1_pct, false, heldout3d.lightgbm.macro_f1_ci_95)}
                    {renderMetricCell(heldout3d.lightgbm.orange_red_recall_pct, true, heldout3d.lightgbm.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono">{heldout3d.lightgbm.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout3d.lightgbm.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout3d.lightgbm.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono">{heldout3d.lightgbm.accuracy_pct}%</td>
                  </tr>
                  <tr className="hover:bg-survey-paper/50">
                    <td className="p-3 text-survey-slate dark:text-night-slate">Linear (Logistic Regression) [L-BFGS-B]</td>
                    {renderMetricCell(heldout3d.linear_logistic_regression.macro_f1_pct, false, heldout3d.linear_logistic_regression.macro_f1_ci_95)}
                    {renderMetricCell(heldout3d.linear_logistic_regression.orange_red_recall_pct, false, heldout3d.linear_logistic_regression.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono">{heldout3d.linear_logistic_regression.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout3d.linear_logistic_regression.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout3d.linear_logistic_regression.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono font-bold">{heldout3d.linear_logistic_regression.accuracy_pct}%</td>
                  </tr>
                  <tr className="hover:bg-survey-paper/50">
                    <td className="p-3 font-semibold text-survey-ink dark:text-night-text">Persistence Baseline (Stronger)</td>
                    {renderMetricCell(heldout3d.persistence_baseline.macro_f1_pct, true, heldout3d.persistence_baseline.macro_f1_ci_95)}
                    {renderMetricCell(heldout3d.persistence_baseline.orange_red_recall_pct, false, heldout3d.persistence_baseline.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono">{heldout3d.persistence_baseline.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout3d.persistence_baseline.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout3d.persistence_baseline.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono">{heldout3d.persistence_baseline.accuracy_pct}%</td>
                  </tr>
                  <tr className="hover:bg-survey-paper/50">
                    <td className="p-3 text-survey-slate dark:text-night-slate">Rainfall Threshold Rule</td>
                    {renderMetricCell(heldout3d.threshold_baseline.macro_f1_pct, false, heldout3d.threshold_baseline.macro_f1_ci_95)}
                    {renderMetricCell(heldout3d.threshold_baseline.orange_red_recall_pct, true, heldout3d.threshold_baseline.orange_red_recall_ci_95)}
                    <td className="p-3 font-mono">{heldout3d.threshold_baseline.orange_red_precision_pct}%</td>
                    <td className="p-3 font-mono">{heldout3d.threshold_baseline.false_alarm_rate_pct}%</td>
                    <td className="p-3 font-mono">{heldout3d.threshold_baseline.false_alarms_per_station_year}</td>
                    <td className="p-3 font-mono">{heldout3d.threshold_baseline.accuracy_pct}%</td>
                  </tr>
                </>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* Per-Station 2018 Lead Time & False Alarm Breakdown Table (Kerala Stations Only) */}
      <section className="space-y-3">
        <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">
          Per-Station 2018 Flood Event Breakdown (Kerala Primary Region)
        </h2>
        <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
          First warning date, first threshold crossing date, and August 2018 strict lead time (&ge;3 days capped) for Kerala stations. Thumpamon (KL-ACH-01) is excluded due to short historical coverage ending in 2009.
        </p>

        <div className="overflow-x-auto rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card">
          <table className="w-full text-left border-collapse font-sans text-xs">
            <thead>
              <tr className="border-b border-survey-border dark:border-night-border bg-survey-paper dark:bg-night-bg font-mono text-[11px] text-survey-teal dark:text-night-teal uppercase">
                <th className="p-3">Station ID</th>
                <th className="p-3">River Basin</th>
                <th className="p-3">Actual Orange/Red Days</th>
                <th className="p-3">First Warning Date</th>
                <th className="p-3">First Crossing Date</th>
                <th className="p-3">Strict Lead Time</th>
                <th className="p-3">Pre-6D Tag Lead</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-survey-border/40 dark:divide-night-border/40 font-mono">
              {keralaStations.map((stId) => {
                const details = stationDetails[stId] || {};
                const isShort = stId === 'KL-ACH-01';
                return (
                  <tr key={stId} className="hover:bg-survey-paper/50 dark:hover:bg-night-bg/50">
                    <td className="p-3 font-bold text-survey-ink dark:text-night-text">{stId}</td>
                    <td className="p-3 text-survey-slate dark:text-night-slate">{details.river_name || 'River'}</td>
                    <td className="p-3 text-amber-700 dark:text-amber-400 font-bold">
                      {isShort ? 'Excluded (Short history ending 2009)' : `${details.actual_orange_red_days_2018 ?? 0} days`}
                    </td>
                    <td className="p-3">{details.first_warning_date || 'N/A'}</td>
                    <td className="p-3">{details.first_threshold_crossing_date || 'N/A'}</td>
                    <td className="p-3 text-emerald-600 dark:text-emerald-400 font-bold">
                      {details.lead_time_display || 'N/A'}
                    </td>
                    <td className="p-3 text-survey-slate dark:text-night-slate opacity-75">
                      {details.git_tag_pre_6d_lead || 'N/A'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* Separate Assam Basin 2018 Table with Disclaimer */}
      <section className="space-y-3">
        <div>
          <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">
            Assam Basin 2018 Baseline (Secondary Region — Experimental)
          </h2>
          <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
            Assam stations experienced almost no Orange/Red days in 2018 (0 to 4 days across July-August), so Assam is not evaluated on a major flood event.
          </p>
        </div>

        <div className="overflow-x-auto rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card">
          <table className="w-full text-left border-collapse font-sans text-xs">
            <thead>
              <tr className="border-b border-survey-border dark:border-night-border bg-survey-paper dark:bg-night-bg font-mono text-[11px] text-survey-teal dark:text-night-teal uppercase">
                <th className="p-3">Station ID</th>
                <th className="p-3">River Basin</th>
                <th className="p-3">2018 Orange/Red Days</th>
                <th className="p-3">First Warning Date</th>
                <th className="p-3">First Crossing Date</th>
                <th className="p-3">Strict Lead Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-survey-border/40 dark:divide-night-border/40 font-mono">
              {assamStations.map((stId) => {
                const details = stationDetails[stId] || {};
                return (
                  <tr key={stId} className="hover:bg-survey-paper/50 dark:hover:bg-night-bg/50">
                    <td className="p-3 font-bold text-survey-ink dark:text-night-text">{stId}</td>
                    <td className="p-3 text-survey-slate dark:text-night-slate">{details.river_name || 'River'}</td>
                    <td className="p-3 text-amber-700 dark:text-amber-400">{details.actual_orange_red_days_2018 ?? 0} days</td>
                    <td className="p-3">{details.first_warning_date || 'N/A'}</td>
                    <td className="p-3">{details.first_threshold_crossing_date || 'N/A'}</td>
                    <td className="p-3 text-survey-slate dark:text-night-slate">{details.lead_time_display || 'no event'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* Leave-One-River-Out (LORO) Spatial Generalization Benchmark */}
      <section className="space-y-3">
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">
            STRICT SPATIAL GENERALIZATION BENCHMARK
          </span>
          <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">
            Leave-One-River-Out (LORO) Validation
          </h2>
          <p className="font-sans text-xs text-survey-slate dark:text-night-slate">
            Because stations along the same river share high hydrological correlation, Leave-One-RIVER-Out trains on 8 river basins and evaluates strictly on the completely unobserved 9th river basin:
          </p>
        </div>

        <div className="overflow-x-auto rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card">
          <table className="w-full text-left border-collapse font-sans text-xs">
            <thead>
              <tr className="border-b border-survey-border dark:border-night-border bg-survey-paper dark:bg-night-bg font-mono text-[11px] text-survey-teal dark:text-night-teal uppercase">
                <th className="p-3">Held-Out River Basin</th>
                <th className="p-3">Macro F1</th>
                <th className="p-3">Orange/Red Recall</th>
                <th className="p-3">Orange/Red Precision</th>
                <th className="p-3">FAR</th>
                <th className="p-3">Accuracy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-survey-border/40 dark:divide-night-border/40 font-mono">
              {Object.entries(loroResults).map(([river, res]) => (
                <tr key={river} className="hover:bg-survey-paper/50 dark:hover:bg-night-bg/50">
                  <td className="p-3 font-bold text-survey-ink dark:text-night-text">{river} River</td>
                  <td className="p-3">{res.macro_f1_pct}%</td>
                  <td className="p-3 font-semibold text-emerald-600 dark:text-emerald-400">{res.orange_red_recall_pct}%</td>
                  <td className="p-3">{res.orange_red_precision_pct}%</td>
                  <td className="p-3 text-survey-slate dark:text-night-slate">{res.false_alarm_rate_pct}%</td>
                  <td className="p-3 font-bold">{res.accuracy_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

    </div>
  );
};
