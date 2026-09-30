import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { Station, RiskLevel } from '../../types';
import { useTheme } from '../../theme/ThemeContext';
import { RiskBadge } from '../common/Badge';

interface FloodMapProps {
  stations: Station[];
  selectedStationId?: string;
  onSelectStation: (station: Station) => void;
  height?: string;
}

// Custom SVG icon generator for station markers with pulse
const createCustomMarkerIcon = (risk: RiskLevel = 'Green', isSelected = false) => {
  const colorMap: Record<RiskLevel, string> = {
    Green: '#2E7D32',
    Yellow: '#D97706',
    Orange: '#EA580C',
    Red: '#DC2626'
  };

  const color = colorMap[risk] || '#2E7D32';
  const isHighRisk = risk === 'Orange' || risk === 'Red';
  const size = isSelected ? 34 : 26;

  const svg = `
    <svg width="${size}" height="${size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
      ${isHighRisk ? `
        <circle cx="16" cy="16" r="14" fill="${color}" opacity="0.3">
          <animate attributeName="r" values="10;16;10" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.6;0.1;0.6" dur="2s" repeatCount="indefinite"/>
        </circle>
      ` : ''}
      <circle cx="16" cy="16" r="${isSelected ? 10 : 8}" fill="${color}" stroke="#FFFFFF" stroke-width="2.5" />
      <circle cx="16" cy="16" r="3" fill="#FFFFFF" />
    </svg>
  `;

  return L.divIcon({
    html: svg,
    className: 'custom-station-marker',
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2]
  });
};

// Component to track cursor coordinates
const CursorTracker: React.FC<{ onMove: (coords: { lat: number; lng: number }) => void }> = ({ onMove }) => {
  useMapEvents({
    mousemove: (e) => {
      onMove({ lat: e.latlng.lat, lng: e.latlng.lng });
    }
  });
  return null;
};

export const FloodMap: React.FC<FloodMapProps> = ({
  stations,
  selectedStationId,
  onSelectStation,
  height = 'calc(100vh - 4rem)'
}) => {
  const { theme } = useTheme();
  const [cursorCoords, setCursorCoords] = useState<{ lat: number; lng: number }>({ lat: 10.1416, lng: 76.5781 });

  // Map center defaults to Kerala
  const centerLat = 10.1416;
  const centerLng = 76.5781;

  // CartoDB desaturated tiles
  const tileUrl = theme === 'dark'
    ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
    : 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';

  const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>';

  return (
    <div className="relative w-full overflow-hidden border border-survey-border dark:border-night-border rounded shadow-xs" style={{ height }}>
      <MapContainer
        center={[centerLat, centerLng]}
        zoom={8}
        style={{ height: '100%', width: '100%', backgroundColor: theme === 'dark' ? '#0C141B' : '#F2EEE4' }}
        zoomControl={true}
      >
        <TileLayer url={tileUrl} attribution={attribution} maxZoom={18} />
        <CursorTracker onMove={setCursorCoords} />

        {stations.map(st => {
          const risk = st.current_risk_level || 'Green';
          const isSelected = st.id === selectedStationId;
          const icon = createCustomMarkerIcon(risk, isSelected);

          // Generate low-lying polygon contour around station
          const delta = 0.035;
          const polygonCoords: [number, number][] = [
            [st.latitude + delta, st.longitude - delta],
            [st.latitude + delta * 1.2, st.longitude + delta * 0.8],
            [st.latitude - delta * 0.9, st.longitude + delta * 1.1],
            [st.latitude - delta * 1.1, st.longitude - delta * 0.7]
          ];

          const polygonColor = risk === 'Red' ? '#DC2626' : risk === 'Orange' ? '#EA580C' : '#1F6B75';

          return (
            <React.Fragment key={st.id}>
              {/* Low-lying zone polygon */}
              <Polygon
                positions={polygonCoords}
                pathOptions={{
                  color: polygonColor,
                  fillColor: polygonColor,
                  fillOpacity: risk === 'Red' ? 0.35 : 0.15,
                  weight: 1.5,
                  dashArray: '4, 4'
                }}
              />

              {/* Station Marker */}
              <Marker
                position={[st.latitude, st.longitude]}
                icon={icon}
                eventHandlers={{
                  click: () => onSelectStation(st)
                }}
              >
                <Popup className="custom-leaflet-popup">
                  <div className="p-1 font-sans text-xs">
                    <div className="font-serif text-sm font-bold text-slate-900 mb-1">{st.name}</div>
                    <div className="text-slate-600 mb-2">{st.river} ({st.region})</div>
                    <div className="mb-2">
                      <RiskBadge level={risk} size="sm" />
                    </div>
                    <div className="font-mono text-[11px] text-slate-700">
                      <div>Water Level: <strong>{(st.current_water_level_m || st.normal_level_m).toFixed(2)}m</strong></div>
                      <div>Danger Mark: {st.danger_level_m}m</div>
                    </div>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Cursor Readout Micro-detail */}
      <div className="absolute bottom-3 left-3 z-[400] rounded bg-survey-paper/90 dark:bg-night-bg/90 px-2.5 py-1 border border-survey-border dark:border-night-border font-mono text-[11px] text-survey-ink dark:text-night-text backdrop-blur-xs shadow-xs">
        <span className="text-survey-teal dark:text-night-teal font-medium">CURSOR:</span> {cursorCoords.lat.toFixed(4)}°N, {cursorCoords.lng.toFixed(4)}°E
      </div>
    </div>
  );
};
