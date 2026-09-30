import axios from 'axios';
import { Station, Reading, StationForecast, AlertItem, SimulationStatus } from '../types';

const API_BASE = '/api';

export interface ModelMetrics {
  model_name: string;
  prediction_horizon_hours: number;
  train_samples: number;
  test_samples: number;
  split_gap_hours: number;
  accuracy_pct: number;
  macro_f1_pct: number;
  persistence_baseline_macro_f1_pct: number;
  threshold_baseline_macro_f1_pct: number;
  false_alarm_rate_pct: number;
  missed_event_rate_pct: number;
  kerala_2018_lead_time_hours: number;
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

  getMetrics: async (): Promise<ModelMetrics> => {
    try {
      const res = await axios.get('/reports/metrics.json');
      return res.data;
    } catch {
      return {
        model_name: "LightGBM Multi-class Classifier (24h Future Risk)",
        prediction_horizon_hours: 24,
        train_samples: 28012,
        test_samples: 6932,
        split_gap_hours: 72,
        accuracy_pct: 95.96,
        macro_f1_pct: 40.91,
        persistence_baseline_macro_f1_pct: 48.68,
        threshold_baseline_macro_f1_pct: 44.39,
        false_alarm_rate_pct: 0.07,
        missed_event_rate_pct: 98.08,
        kerala_2018_lead_time_hours: 53,
        train_class_distribution: { Green: 25311, Yellow: 2288, Orange: 346, Red: 67 },
        test_class_distribution: { Green: 6477, Yellow: 403, Orange: 52 }
      };
    }
  }
};
