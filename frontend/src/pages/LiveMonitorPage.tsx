import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { FloodMap } from '../components/map/FloodMap';
import { WaterLevelGauge } from '../components/charts/WaterLevelGauge';
import { HydrologicalChart } from '../components/charts/HydrologicalChart';
import { RiskBadge } from '../components/common/Badge';
import { Station, Reading, ForecastHour } from '../types';
import { api } from '../services/api';
import { Radio, AlertCircle, Cpu, Wifi } from 'lucide-react';

export const LiveMonitorPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const stationParam = searchParams.get('station');

  const [stations, setStations] = useState<Station[]>([]);
  const [selectedStation, setSelectedStation] = useState<Station | null>(null);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [forecastPoints, setForecastPoints] = useState<ForecastHour[]>([]);
  const [topDrivers, setTopDrivers] = useState<string[]>([]);
  const [liveLog, setLiveLog] = useState<string[]>([]);

  // 1. Fetch stations on load
  useEffect(() => {
    api.getStations().then(data => {
      setStations(data);
      if (data.length > 0) {
        const initial = data.find(s => s.id === stationParam) || data[0];
        setSelectedStation(initial);
      }
    }).catch(console.error);
  }, [stationParam]);

  // 2. Fetch station readings and forecast when selected station changes
  useEffect(() => {
    if (!selectedStation) return;

    api.getStationReadings(selectedStation.id, 48).then(setReadings).catch(console.error);
    api.getStationForecast(selectedStation.id).then(fData => {
      setForecastPoints(fData.forecast_points);
      setTopDrivers(fData.top_risk_drivers);
    }).catch(console.error);
  }, [selectedStation]);

  // 3. Connect WebSocket for live updates over /ws/live
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/live`;
    let socket: WebSocket;

    try {
      socket = new WebSocket(wsUrl);
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'new_reading') {
            setLiveLog(prev => [
              `[${new Date().toLocaleTimeString()}] ${data.station_name}: Level ${data.water_level_m.toFixed(2)}m (${data.risk_level})`,
              ...prev.slice(0, 15)
            ]);

            // Update station in list
            setStations(prev => prev.map(s => {
              if (s.id === data.station_id) {
                return {
                  ...s,
                  current_water_level_m: data.water_level_m,
                  current_risk_level: data.risk_level,
                  battery_pct: data.battery_pct
                };
              }
              return s;
            }));
          }
        } catch (e) {
          // ignore parsing error
        }
      };
    } catch (e) {
      console.warn('WebSocket connection fallback:', e);
    }

    return () => {
      if (socket) socket.close();
    };
  }, []);

  const latestReading = readings.length > 0 ? readings[readings.length - 1] : null;

  return (
    <div className="space-y-4 pb-8">
      
      {/* Page Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-survey-border dark:border-night-border pb-3">
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">REAL-TIME MONITORING CONTROL ROOM</span>
          <h1 className="font-serif text-2xl font-bold text-survey-ink dark:text-night-text">Live Hydrological Network</h1>
        </div>

        {/* Region Filter Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => api.getStations('Kerala').then(setStations)}
            className="px-3 py-1 font-mono text-xs rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card text-survey-ink dark:text-night-text hover:border-survey-teal cursor-pointer"
          >
            Kerala Region (6)
          </button>
          <button
            onClick={() => api.getStations('Assam').then(setStations)}
            className="px-3 py-1 font-mono text-xs rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card text-survey-ink dark:text-night-text hover:border-survey-teal cursor-pointer"
          >
            Assam Region (5)
          </button>
        </div>
      </div>

      {/* Main Asymmetrical Grid (Map + Station Sidebar) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Interactive Map & Live Event Log */}
        <div className="lg:col-span-7 space-y-4">
          <FloodMap
            stations={stations}
            selectedStationId={selectedStation?.id}
            onSelectStation={setSelectedStation}
            height="580px"
          />

          {/* Live Telemetry Ticker Strip */}
          <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-3 font-mono text-xs">
            <div className="flex items-center gap-2 mb-2 text-survey-teal dark:text-night-teal font-semibold">
              <Radio className="h-4 w-4 animate-pulse" /> LIVE TELEMETRY TICKER STREAM (/ws/live)
            </div>
            <div className="h-20 overflow-y-auto space-y-1 text-survey-slate dark:text-night-slate scrollbar-thin">
              {liveLog.length === 0 ? (
                <div className="italic">Listening for virtual ESP32 sensor broadcasts...</div>
              ) : (
                liveLog.map((log, idx) => (
                  <div key={idx} className="hover:text-survey-ink dark:hover:text-night-text">{log}</div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Station Detail View */}
        <div className="lg:col-span-5 space-y-4">
          {selectedStation ? (
            <>
              {/* Station Summary Card */}
              <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="font-mono text-xs text-survey-teal dark:text-night-teal block">{selectedStation.id} • {selectedStation.region}</span>
                    <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">{selectedStation.name}</h2>
                    <span className="font-sans text-xs text-survey-slate dark:text-night-slate">{selectedStation.river}</span>
                  </div>
                  <RiskBadge level={selectedStation.current_risk_level || 'Green'} size="md" />
                </div>

                <p className="font-sans text-xs text-survey-slate dark:text-night-slate border-t border-survey-border/40 dark:border-night-border/40 pt-2">
                  {selectedStation.description}
                </p>
              </div>

              {/* Water Level Gauge */}
              <WaterLevelGauge
                station={selectedStation}
                currentWaterLevelM={selectedStation.current_water_level_m}
                batteryPct={selectedStation.battery_pct}
                rssi={selectedStation.rssi}
                sensorStatus={selectedStation.sensor_status}
              />

              {/* Plain-Language Top 3 Drivers Card */}
              <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-2">
                <div className="flex items-center gap-1.5 font-mono text-xs text-survey-teal dark:text-night-teal font-semibold">
                  <AlertCircle className="h-4 w-4 text-amber-500" /> EXPLAINABLE ML RISK DRIVERS
                </div>
                <ul className="space-y-1.5 font-sans text-xs text-survey-ink dark:text-night-text list-disc list-inside">
                  {topDrivers.length > 0 ? (
                    topDrivers.map((driver, i) => <li key={i}>{driver}</li>)
                  ) : (
                    <>
                      <li>Water level within normal baseline thresholds</li>
                      <li>72-hour cumulative precipitation forecast is nominal</li>
                      <li>Upstream discharge flow velocity stable</li>
                    </>
                  )}
                </ul>
              </div>

              {/* Hydrological 72h Chart */}
              <HydrologicalChart
                station={selectedStation}
                readings={readings}
                forecastPoints={forecastPoints}
              />
            </>
          ) : (
            <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-8 text-center font-mono text-xs text-survey-slate">
              Select a station on the map to inspect details.
            </div>
          )}
        </div>

      </div>

    </div>
  );
};
