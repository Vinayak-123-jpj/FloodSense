import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Tooltip as LeafletTooltip, GeoJSON, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { Station, RiskLevel } from '../../types';
import { useTheme } from '../../theme/ThemeContext';
import { RiskBadge } from '../common/Badge';
import { KERALA_BOUNDARY_GEOJSON, ASSAM_BOUNDARY_GEOJSON } from '../../data/regionOutlines';
import { Layers } from 'lucide-react';

interface FloodMapProps {
  stations: Station[];
  selectedStationId?: string;
  onSelectStation: (station: Station) => void;
  height?: string;
  selectedRegion?: string;
  onRegionChange?: (region: string) => void;
}

// Custom SVG marker icon with decluttered labels (label visible at zoom >= 9 or if selected)
const createCustomMarkerIcon = (station: Station, risk: RiskLevel = 'Green', isSelected = false, showLabel = false) => {
  const colorMap: Record<RiskLevel, string> = {
    Green: '#2E7D32',
    Yellow: '#D97706',
    Orange: '#EA580C',
    Red: '#DC2626'
  };

  const shapeMap: Record<RiskLevel, string> = {
    Green: '●',
    Yellow: '▲',
    Orange: '◆',
    Red: '⬢'
  };

  const color = colorMap[risk] || '#2E7D32';
  const shape = shapeMap[risk] || '●';
  const isHighRisk = risk === 'Orange' || risk === 'Red';
  const size = isSelected ? 34 : 26;

  const svg = `
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
      <svg width="${size}" height="${size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" style="margin: 0 auto;">
        ${isHighRisk ? `
          <circle cx="16" cy="16" r="14" fill="${color}" opacity="0.3">
            <animate attributeName="r" values="10;16;10" dur="1.8s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0.6;0.1;0.6" dur="1.8s" repeatCount="indefinite"/>
          </circle>
        ` : ''}
        <circle cx="16" cy="16" r="${isSelected ? 11 : 9}" fill="${color}" stroke="#FFFFFF" stroke-width="2.5" />
        <text x="16" y="20" font-size="10" font-weight="bold" fill="#FFFFFF" text-anchor="middle">${shape}</text>
      </svg>
      ${(showLabel || isSelected) ? `
        <div style="
          font-family: monospace;
          font-size: 9px;
          font-weight: 700;
          color: ${color};
          background-color: rgba(255, 255, 255, 0.95);
          padding: 1px 4px;
          border-radius: 3px;
          border: 1px solid ${color};
          box-shadow: 0 1px 3px rgba(0,0,0,0.25);
          white-space: nowrap;
          margin-top: 1px;
        ">
          ${station.name} (${risk.toUpperCase()})
        </div>
      ` : ''}
    </div>
  `;

  return L.divIcon({
    html: svg,
    className: 'custom-station-marker-container',
    iconSize: [80, 50],
    iconAnchor: [40, 25],
    popupAnchor: [0, -25]
  });
};

// Component to control fitBounds centering & track zoom level for decluttering
const MapViewController: React.FC<{
  stations: Station[];
  selectedRegion?: string;
  onZoomChange: (zoom: number) => void;
  onCursorMove: (coords: { lat: number; lng: number }) => void;
}> = ({ stations, selectedRegion, onZoomChange, onCursorMove }) => {
  const map = useMap();

  useMapEvents({
    zoomend: () => onZoomChange(map.getZoom()),
    mousemove: (e) => onCursorMove({ lat: e.latlng.lat, lng: e.latlng.lng })
  });

  useEffect(() => {
    onZoomChange(map.getZoom());
    const filtered = selectedRegion && selectedRegion !== 'All'
      ? stations.filter(s => s.region === selectedRegion)
      : stations;

    if (filtered.length > 0) {
      const bounds = L.latLngBounds(filtered.map(s => [s.latitude, s.longitude]));
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 });
    }
  }, [stations, selectedRegion, map]);

  return null;
};

export const FloodMap: React.FC<FloodMapProps> = ({
  stations,
  selectedStationId,
  onSelectStation,
  height = 'calc(100vh - 4rem)',
  selectedRegion = 'Kerala',
  onRegionChange
}) => {
  const { theme } = useTheme();
  const [cursorCoords, setCursorCoords] = useState<{ lat: number; lng: number }>({ lat: 10.1416, lng: 76.5781 });
  const [activeRegionFilter, setActiveRegionFilter] = useState<string>(selectedRegion);
  const [currentZoom, setCurrentZoom] = useState<number>(8);
  const [useOfflineFallback, setUseOfflineFallback] = useState<boolean>(!navigator.onLine);

  useEffect(() => {
    setActiveRegionFilter(selectedRegion);
  }, [selectedRegion]);

  // 4-second timeout to check tile loading and activate offline fallback if network is unreachable
  useEffect(() => {
    const handleOnline = () => setUseOfflineFallback(false);
    const handleOffline = () => setUseOfflineFallback(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    const timer = setTimeout(() => {
      if (!navigator.onLine) setUseOfflineFallback(true);
    }, 4000);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearTimeout(timer);
    };
  }, []);

  const handleRegionClick = (reg: string) => {
    setActiveRegionFilter(reg);
    if (onRegionChange) onRegionChange(reg);
  };

  // Standard OSM tiles with CSS theme filters (dark tile filter / light warm sepia tint filter)
  const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  const tileAttribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

  return (
    <div className="relative w-full overflow-hidden border border-survey-border dark:border-night-border rounded shadow-xs" style={{ height }}>
      
      {/* On-Map Region Switcher Control */}
      <div className="absolute top-3 right-3 z-[400] flex items-center gap-1 bg-survey-paper/95 dark:bg-night-bg/95 p-1 rounded border border-survey-border dark:border-night-border shadow-xs backdrop-blur-xs font-mono text-xs">
        <span className="text-survey-teal dark:text-night-teal px-1 font-semibold flex items-center gap-1">
          <Layers className="h-3.5 w-3.5" /> REGION:
        </span>
        {['Kerala', 'Assam', 'All'].map(reg => (
          <button
            key={reg}
            onClick={() => handleRegionClick(reg)}
            className={`px-2.5 py-1 rounded transition-all cursor-pointer ${
              activeRegionFilter === reg
                ? 'bg-survey-teal text-white font-bold'
                : 'text-survey-slate dark:text-night-slate hover:text-survey-ink dark:hover:text-night-text'
            }`}
          >
            {reg}
          </button>
        ))}
      </div>

      <MapContainer
        center={[10.1416, 76.5781]}
        zoom={8}
        style={{ height: '100%', width: '100%', backgroundColor: theme === 'dark' ? '#0C141B' : '#F2EEE4' }}
        zoomControl={true}
      >
        <MapViewController
          stations={stations}
          selectedRegion={activeRegionFilter}
          onZoomChange={setCurrentZoom}
          onCursorMove={setCursorCoords}
        />

        {/* Tile Layer with 4s / offline fallback */}
        {!useOfflineFallback && (
          <TileLayer
            url={tileUrl}
            subdomains="abc"
            attribution={tileAttribution}
            maxZoom={17}
            className={theme === 'dark' ? 'dark-tile-filter' : 'light-tile-filter'}
            eventHandlers={{
              tileerror: () => setUseOfflineFallback(true)
            }}
          />
        )}

        {/* Bundled GeoJSON Vector Fallback Layers (solid clean geometry) */}
        <GeoJSON
          data={KERALA_BOUNDARY_GEOJSON}
          style={{
            color: '#1F6B75',
            weight: 1.5,
            fillColor: '#1F6B75',
            fillOpacity: useOfflineFallback ? 0.12 : 0.04
          }}
        />

        <GeoJSON
          data={ASSAM_BOUNDARY_GEOJSON}
          style={{
            color: '#C88A2E',
            weight: 1.5,
            fillColor: '#C88A2E',
            fillOpacity: useOfflineFallback ? 0.12 : 0.04
          }}
        />

        {stations.map(st => {
          const risk = st.current_risk_level || 'Green';
          const isSelected = st.id === selectedStationId;
          const showTextLabel = currentZoom >= 10 || isSelected;
          const icon = createCustomMarkerIcon(st, risk, isSelected, showTextLabel);

          return (
            <Marker
              key={st.id}
              position={[st.latitude, st.longitude]}
              icon={icon}
              eventHandlers={{
                click: () => onSelectStation(st)
              }}
            >
                <LeafletTooltip direction="top" offset={[0, -25]} opacity={0.95}>
                  <div className="font-mono text-xs">
                    <strong className="block text-slate-900">{st.name} ({st.river})</strong>
                    <div>Risk Level: <span className="font-bold">{risk}</span></div>
                    <div>Discharge: {(st.current_discharge_m3s !== undefined && st.current_discharge_m3s !== null ? st.current_discharge_m3s : 0).toFixed(1)} m³/s</div>
                  </div>
                </LeafletTooltip>

                <Popup className="custom-leaflet-popup">
                  <div className="p-1 font-sans text-xs dark:text-slate-100 text-slate-900">
                    <div className="font-serif text-sm font-bold dark:text-white text-slate-900 mb-0.5">{st.name}</div>
                    <div className="dark:text-slate-400 text-slate-600 mb-2">{st.river} ({st.region})</div>
                    <div className="mb-2">
                      <RiskBadge level={risk} size="sm" />
                    </div>
                    <div className="font-mono text-[11px] space-y-1 dark:text-slate-200 text-slate-700">
                      <div>Current Discharge: <strong>{(st.current_discharge_m3s !== undefined && st.current_discharge_m3s !== null ? st.current_discharge_m3s : 0).toFixed(1)} m³/s</strong></div>
                      <div className="text-[10px] text-yellow-600 dark:text-yellow-400">p90 Threshold: {st.p90_m3s ? st.p90_m3s.toFixed(1) : 'N/A'} m³/s</div>
                      <div className="text-[10px] text-amber-600 dark:text-amber-400">p97 Threshold: {st.p97_m3s ? st.p97_m3s.toFixed(1) : 'N/A'} m³/s</div>
                      <div className="text-[10px] text-red-600 dark:text-red-400">p99.5 Threshold: {st.p99_5_m3s ? st.p99_5_m3s.toFixed(1) : 'N/A'} m³/s</div>
                    </div>
                  </div>
                </Popup>
              </Marker>
          );
        })}
      </MapContainer>

      {/* Cursor Readout Micro-detail */}
      <div className="absolute bottom-3 left-3 z-[400] rounded bg-survey-paper/90 dark:bg-night-bg/90 px-2.5 py-1 border border-survey-border dark:border-night-border font-mono text-[11px] text-survey-ink dark:text-night-text backdrop-blur-xs shadow-xs">
        <span className="text-survey-teal dark:text-night-teal font-medium">CURSOR:</span> {cursorCoords.lat.toFixed(4)}°N, {cursorCoords.lng.toFixed(4)}°E {useOfflineFallback && '(OFFLINE VECTOR MODE)'}
      </div>
    </div>
  );
};
