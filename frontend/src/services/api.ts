import axios from 'axios';
import { Station, Reading, StationForecast, AlertItem, SimulationStatus } from '../types';

const API_BASE = '/api';

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

  postReading: async (payload: { node_id: string; water_level_cm: number; rainfall_mm_hr: number; battery_pct?: number; rssi?: number }): Promise<Reading> => {
    const res = await axios.post(`${API_BASE}/readings`, payload);
    return res.data;
  }
};
