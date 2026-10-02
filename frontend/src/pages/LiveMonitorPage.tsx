import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { FloodMap } from '../components/map/FloodMap';
import { WaterLevelGauge } from '../components/charts/WaterLevelGauge';
import { HydrologicalChart } from '../components/charts/HydrologicalChart';
import { RiskBadge, SourceBadge } from '../components/common/Badge';
import { Station, Reading, ForecastHour } from '../types';
import { api } from '../services/api';
import { Radio, AlertCircle, Cpu, Wifi, Database, Server } from 'lucide-react';

export const LiveMonitorPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const stationParam = searchParams.get('station');

  const [stations, setStations] = useState<Station[]>([]);
  const [selectedStation, setSelectedStation] = useState<Station | null>(null);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [forecastPoints, setForecastPoints] = useState<ForecastHour[]>([]);
  const [topDrivers, setTopDrivers] = useState<string[]>([]);
  const [liveLog, setLiveLog] = useState<string[]>([]);

  // Telemetry source mode toggle
  const initialSource = searchParams.get('source')?.toUpperCase() === 'SIMULATED' ? 'SIMULATED' : 'REAL';
  const [sourceMode, setSourceMode] = useState<'REAL' | 'SIMULATED'>(initialSource);
  const [realLiveData, setRealLiveData] = useState<any>(null);
  const [isCachedSnapshot, setIsCachedSnapshot] = useState<boolean>(false);
  const [fetchedAt, setFetchedAt] = useState<string>('');

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

  // 2. Fetch station readings and forecast when selected station or source mode changes
  useEffect(() => {
    if (!selectedStation) return;

    if (sourceMode === 'REAL') {
      api.getRealLiveStationData(selectedStation.id)
        .then(res => {
          setRealLiveData(res);
          setIsCachedSnapshot(!!res.is_cached);
          setFetchedAt(res.fetched_at || '');
          if (res.top_risk_drivers) {
            setTopDrivers(res.top_risk_drivers);
          }
        })
        .catch(err => {
          console.warn('Real live data fetch failed, using fallback simulated telemetry:', err);
          setIsCachedSnapshot(true);
        });
    }

    api.getStationReadings(selectedStation.id, 48).then(setReadings).catch(console.error);
    api.getStationForecast(selectedStation.id).then(fData => {
      setForecastPoints(fData.forecast_points);
      if (sourceMode === 'SIMULATED') {
        setTopDrivers(fData.top_risk_drivers);
      }
    }).catch(console.error);
  }, [selectedStation, sourceMode]);

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

  return (
    <div className="space-y-4 pb-8">
      
      {/* Page Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-survey-border dark:border-night-border pb-3">
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">HYDROLOGICAL NETWORK MONITORING</span>
          <h1 className="font-serif text-2xl font-bold text-survey-ink dark:text-night-text">River Station Telemetry & Risk Monitor</h1>
          <span className="font-sans text-xs text-survey-slate dark:text-night-slate block">
            Primary Forecast: Open-Meteo GloFAS Discharge vs Station Thresholds (p90/p97/p99.5) • Secondary Layer: Experimental LightGBM Model
          </span>
        </div>

        {/* Telemetry Source Toggle & Region Filter */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Data Source Selector */}
          <div className="flex items-center rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-1">
            <button
              onClick={() => setSourceMode('REAL')}
              className={`flex items-center gap-1.5 px-3 py-1 font-mono text-xs rounded transition-colors cursor-pointer ${
                sourceMode === 'REAL'
                  ? 'bg-sky-500 text-white font-semibold shadow-xs'
                  : 'text-survey-slate dark:text-night-slate hover:text-survey-ink dark:hover:text-night-text'
              }`}
            >
              <Database className="h-3.5 w-3.5" />
              Real Data (Open-Meteo)
            </button>
            <button
              onClick={() => setSourceMode('SIMULATED')}
              className={`flex items-center gap-1.5 px-3 py-1 font-mono text-xs rounded transition-colors cursor-pointer ${
                sourceMode === 'SIMULATED'
                  ? 'bg-amber-500 text-white font-semibold shadow-xs'
                  : 'text-survey-slate dark:text-night-slate hover:text-survey-ink dark:hover:text-night-text'
              }`}
            >
              <Cpu className="h-3.5 w-3.5" />
              Simulated Sensors
            </button>
          </div>

          {/* Region Buttons */}
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

          {/* Live Telemetry / Data Freshness Panel */}
          {sourceMode === 'REAL' ? (
            <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 font-mono text-xs shadow-xs space-y-3">
              <div className="flex items-center justify-between border-b border-survey-border/60 dark:border-night-border/60 pb-2">
                <div className="flex items-center gap-2 text-survey-teal dark:text-night-teal font-semibold">
                  <Database className="h-4 w-4 text-sky-500" /> OPEN-METEO DATA FRESHNESS & CACHE CONTROL
                </div>
                <SourceBadge mode={sourceMode} isCached={isCachedSnapshot} fetchedAt={fetchedAt} />
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-sans text-xs">
                <div>
                  <span className="block font-mono text-[10px] uppercase text-survey-slate dark:text-night-slate">Primary Source</span>
                  <span className="font-semibold text-survey-ink dark:text-night-text">Open-Meteo GloFAS 0.05°</span>
                </div>
                <div>
                  <span className="block font-mono text-[10px] uppercase text-survey-slate dark:text-night-slate">Fetched At (IST)</span>
                  <span className="font-semibold text-survey-ink dark:text-night-text">
                    {fetchedAt ? new Date(fetchedAt).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) + ' IST' : 'Live'}
                  </span>
                </div>
                <div>
                  <span className="block font-mono text-[10px] uppercase text-survey-slate dark:text-night-slate">Next Auto-Refresh</span>
                  <span className="font-semibold text-survey-ink dark:text-night-text">In 30 Minutes</span>
                </div>
                <div>
                  <span className="block font-mono text-[10px] uppercase text-survey-slate dark:text-night-slate">Cache Status</span>
                  <span className={`font-semibold ${isCachedSnapshot ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'}`}>
                    {isCachedSnapshot ? 'Cached Snapshot (Offline)' : 'Live API (Fresh)'}
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-3 font-mono text-xs shadow-xs">
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2 text-survey-teal dark:text-night-teal font-semibold">
                  <Radio className="h-4 w-4 animate-pulse text-amber-500" /> VIRTUAL ESP32 TELEMETRY BROADCAST
                </div>
                <SourceBadge mode={sourceMode} isCached={isCachedSnapshot} fetchedAt={fetchedAt} />
              </div>
              <div className="h-20 overflow-y-auto space-y-1 text-survey-slate dark:text-night-slate scrollbar-thin">
                {liveLog.length === 0 ? (
                  <div className="italic">Listening for virtual ESP32 sensor broadcasts over WebSocket...</div>
                ) : (
                  liveLog.map((log, idx) => (
                    <div key={idx} className="hover:text-survey-ink dark:hover:text-night-text">{log}</div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Station Detail View */}
        <div className="lg:col-span-5 space-y-4">
          {selectedStation ? (
            <>
              {/* Station Summary Card */}
              <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono text-xs text-survey-teal dark:text-night-teal block">{selectedStation.id} • {selectedStation.region}</span>
                      <SourceBadge mode={sourceMode} isCached={isCachedSnapshot} fetchedAt={fetchedAt} />
                    </div>
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
                currentDischargeM3s={selectedStation.current_discharge_m3s}
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
                      <li>River discharge within normal baseline percentiles</li>
                      <li>7-day cumulative rainfall below warning thresholds</li>
                      <li>Antecedent catchment moisture levels nominal</li>
                    </>
                  )}
                </ul>
              </div>

              {/* Hydrological 72h Chart */}
              <HydrologicalChart
                station={selectedStation}
                readings={readings}
                forecastPoints={forecastPoints}
                realDailySeries={sourceMode === 'REAL' ? realLiveData?.recent_daily_series : undefined}
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
