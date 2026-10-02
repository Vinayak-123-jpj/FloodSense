export type RiskLevel = 'Green' | 'Yellow' | 'Orange' | 'Red';

export interface Station {
  id: string;
  name: string;
  region: string;
  river: string;
  latitude: number;
  longitude: number;
  elevation_m: number;
  warning_level_m: number;
  danger_level_m: number;
  normal_level_m: number;
  description?: string;
  current_water_level_m?: number;
  current_discharge_m3s?: number;
  p90_m3s?: number;
  p97_m3s?: number;
  p99_5_m3s?: number;
  historical_max_m3s?: number;
  current_risk_level?: RiskLevel;
  battery_pct?: number;
  rssi?: number;
  sensor_status?: 'OK' | 'DEGRADED' | 'FAULT';
}

export interface Reading {
  id: number;
  station_id: string;
  timestamp: string;
  water_level_cm: number;
  water_level_m: number;
  rainfall_mm_hr: number;
  discharge_m3s?: number;
  battery_pct: number;
  rssi: number;
  risk_level: RiskLevel;
  sensor_status: string;
  top_drivers?: string;
}

export interface ForecastHour {
  timestamp: string;
  predicted_water_level_m: number;
  predicted_risk_level: RiskLevel;
  rainfall_mm_hr: number;
  lower_bound_m: number;
  upper_bound_m: number;
}

export interface StationForecast {
  station_id: string;
  station_name: string;
  generated_at: string;
  horizon_hours: number;
  top_risk_drivers: string[];
  forecast_points: ForecastHour[];
}

export interface AlertItem {
  id: number;
  station_id: string;
  station_name?: string;
  timestamp: string;
  risk_level: RiskLevel;
  previous_risk_level: RiskLevel;
  reason: string;
  action_recommended: string;
  evacuation_route_url?: string;
  language: 'en' | 'hi';
  sent_to_telegram: boolean;
  outbox_logged: boolean;
}

export interface SimulationStatus {
  is_running: boolean;
  speed: number;
  current_scenario: 'live' | 'kerala_2018' | 'assam_2020';
  simulated_time: string;
  rain_multiplier: number;
}
