import axios from 'axios';
import { Station, Reading, StationForecast, AlertItem, SimulationStatus } from '../types';

const API_BASE = '/api';

export interface DetailedHorizonMetrics {
  accuracy_pct: number;
  macro_f1_pct: number;
  false_alarm_rate_pct: number;
  missed_event_rate_pct: number;
  orange_red_recall_pct: number;
  orange_red_precision_pct: number;
  false_alarms_per_station_year: number;
  macro_f1_ci_95?: [number, number];
  orange_red_recall_ci_95?: [number, number];
}

export interface HorizonBaselineComparison {
  lightgbm: DetailedHorizonMetrics;
  linear_logistic_regression: DetailedHorizonMetrics;
  persistence_baseline: DetailedHorizonMetrics;
  threshold_baseline: DetailedHorizonMetrics;
}

export interface Station2018Detail {
  river_name?: string;
  green_days_2018?: number;
  yellow_days_2018?: number;
  orange_days_2018?: number;
  red_days_2018?: number;
  actual_orange_red_days_2018: number;
  predicted_orange_red_days_2018: number;
  false_alarm_days_2018: number;
  august_2018_lead_time_days: number;
  august_2018_lead_time_hours: number;
}

export interface FullMetricsSummary {
  dataset_resolution: string;
  date_range: string;
  total_daily_samples: number;
  station_count: number;
  max_prediction_horizon_days: number;
  statistical_ci_note?: string;
  station_independence_note?: string;
  lead_time_disclaimer: string;
  percentile_proxies_disclaimer: string;
  modeled_discharge_disclaimer: string;
  rainfall_disclaimer: string;
  multi_horizon_time_split: {
    '1d': HorizonBaselineComparison;
    '2d': HorizonBaselineComparison;
    '3d': HorizonBaselineComparison;
  };
  heldout_2018_multi_horizon: {
    '1d': HorizonBaselineComparison;
    '2d': HorizonBaselineComparison;
    '3d': HorizonBaselineComparison;
  };
  leave_one_river_out_loro?: Record<string, DetailedHorizonMetrics>;
  loso_sample_test?: Record<string, DetailedHorizonMetrics>;
  station_2018_details: Record<string, Station2018Detail>;
  kerala_2018_median_lead_time_days: number;
  kerala_2018_median_lead_time_hours: number;
  train_class_distribution: Record<string, number>;
  test_class_distribution: Record<string, number>;
  confusion_matrix_heldout_2018?: {
    labels: string[];
    matrix: number[][];
  };
  feature_importances?: Array<{
    feature: string;
    label: string;
    importance: number;
  }>;
}

export const api = {
  getStations: async (region?: string): Promise<Station[]> => {
    const res = await axios.get(`${API_BASE}/stations`, { params: { region } });
    return res.data;
  },

  getStationById: async (id: string): Promise<Station> => {
    const res = await axios.get(`${API_BASE}/stations/${id}`);
    return res.data;
  },

  getStationReadings: async (id: string, limit = 100): Promise<Reading[]> => {
    const res = await axios.get(`${API_BASE}/stations/${id}/readings`, { params: { limit } });
    return res.data;
  },

  getStationForecast: async (id: string): Promise<StationForecast> => {
    const res = await axios.get(`${API_BASE}/stations/${id}/forecast`);
    return res.data;
  },

  getAlerts: async (station_id?: string, limit = 50): Promise<AlertItem[]> => {
    const res = await axios.get(`${API_BASE}/alerts`, { params: { station_id, limit } });
    return res.data;
  },

  clearAlerts: async (): Promise<void> => {
    await axios.post(`${API_BASE}/alerts/clear`);
  },

  getSimulationStatus: async (): Promise<SimulationStatus> => {
    const res = await axios.get(`${API_BASE}/simulate/status`);
    return res.data;
  },

  controlSimulation: async (action: 'start' | 'stop' | 'set_speed', speed?: number, scenario?: string, rain_multiplier?: number): Promise<SimulationStatus> => {
    const res = await axios.post(`${API_BASE}/simulate/control`, {
      action,
      speed,
      scenario,
      rain_multiplier
    });
    return res.data;
  },

  getFullMetrics: async (): Promise<FullMetricsSummary> => {
    const res = await axios.get('/reports/metrics.json');
    return res.data;
  },

  getRealLiveStationData: async (id: string): Promise<any> => {
    const res = await axios.get(`${API_BASE}/stations/${id}/real_live`);
    return res.data;
  },

  postDemoAlert: async (station_id: string, risk_level: string, language: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/alerts/demo`, null, {
      params: { station_id, risk_level, language }
    });
    return res.data;
  }
};
