import axios from 'axios';
import { Station, Reading, StationForecast, AlertItem, SimulationStatus } from '../types';

const API_BASE = '/api';

export interface HorizonMetrics {
  accuracy_pct: number;
  macro_f1_pct: number;
  false_alarm_rate_pct: number;
  missed_event_rate_pct: number;
  orange_red_recall_pct: number;
}

export interface HorizonComparison {
  lightgbm: HorizonMetrics;
  shallow_tree_baseline: HorizonMetrics;
  persistence_baseline: HorizonMetrics;
  threshold_baseline: HorizonMetrics;
}

export interface FullMetricsSummary {
  dataset_resolution: string;
  date_range: string;
  total_daily_samples: number;
  station_count: number;
  percentile_proxies_disclaimer: string;
  modeled_discharge_disclaimer: string;
  multi_horizon_time_split: {
    '1d': HorizonComparison;
    '2d': HorizonComparison;
    '3d': HorizonComparison;
  };
  heldout_2018_event_test: {
    lightgbm: HorizonMetrics;
    persistence_baseline: HorizonMetrics;
  };
  loso_sample_test: Record<string, HorizonMetrics>;
  kerala_2018_station_lead_times_days: Record<string, number>;
  kerala_2018_median_lead_time_days: number;
  kerala_2018_median_lead_time_hours: number;
  train_class_distribution: Record<string, number>;
  test_class_distribution: Record<string, number>;
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
  }
};
