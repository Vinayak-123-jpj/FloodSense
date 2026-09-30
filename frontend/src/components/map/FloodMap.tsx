import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Tooltip as LeafletTooltip, Polygon, GeoJSON, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { Station, RiskLevel } from '../../types';
import { useTheme } from '../../theme/ThemeContext';
import { RiskBadge } from '../common/Badge';
import { KERALA_BOUNDARY_GEOJSON, ASSAM_BOUNDARY_GEOJSON } from '../../data/regionOutlines';
import { Layers, MapPin } from 'lucide-react';

interface FloodMapProps {
  stations: Station[];
  selectedStationId?: string;
  onSelectStation: (station: Station) => void;
  height?: string;
  selectedRegion?: string;
  onRegionChange?: (region: string) => void;
}

// Custom SVG icon generator for station markers with label & dual shape icon
const createCustomMarkerIcon = (station: Station, risk: RiskLevel = 'Green', isSelected = false) => {
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
  const size = isSelected ? 36 : 28;

  const svg = `
    <div style="display: flex; flex-direction: column; items-center; justify-content: center; text-align: center;">
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
      <div style="
        font-family: monospace;
        font-size: 9px;
        font-weight: 700;
        color: ${color};
        background-color: rgba(255, 255, 255, 0.92);
        padding: 1px 4px;
        border-radius: 3px;
        border: 1px solid ${color};
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        white-space: nowrap;
        margin-top: 1px;
      ">
        ${station.name} (${risk.toUpperCase()})
      </div>
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

// Component to handle map view bounds fitting on region changes
const MapBoundsController: React.FC<{ stations: Station[]; selectedRegion?: string }> = ({ stations, selectedRegion }) => {
  const map = useMap();

  useEffect(() => {
    const filtered = selectedRegion && selectedRegion !== 'All'
      ? stations.filter(s => s.region === selectedRegion)
      : stations;

    if (filtered.length > 0) {
      const bounds = L.latLngBounds(filtered.map(s => [s.latitude, s.longitude]));
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 11 });
    }
  }, [stations, selectedRegion, map]);

  return null;
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
  height = 'calc(100vh - 4rem)',
  selectedRegion = 'Kerala',
  onRegionChange
}) => {
  const { theme } = useTheme();
  const [cursorCoords, setCursorCoords] = useState<{ lat: number; lng: number }>({ lat: 10.1416, lng: 76.5781 });
  const [activeRegionFilter, setActiveRegionFilter] = useState<string>(selectedRegion);
  const [tileError, setTileError] = useState<boolean>(false);

  useEffect(() => {
    setActiveRegionFilter(selectedRegion);
  }, [selectedRegion]);

  const handleRegionClick = (reg: string) => {
    setActiveRegionFilter(reg);
    if (onRegionChange) onRegionChange(reg);
  };

  // Keyless Carto tile URLs
  const primaryTileUrl = theme === 'dark'
    ? 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png'
    : 'https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png';

  const osmFallbackTileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

  const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>';

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
        <MapBoundsController stations={stations} selectedRegion={activeRegionFilter} />
        
        {/* Tile Layer with Fallback */}
        <TileLayer
          url={tileError ? osmFallbackTileUrl : primaryTileUrl}
          subdomains="abcd"
          attribution={attribution}
          maxZoom={18}
          eventHandlers={{
            tileerror: () => setTileError(true)
          }}
          className={tileError ? (theme === 'dark' ? 'dark-tile-filter' : 'light-tile-filter') : ''}
        />

        <CursorTracker onMove={setCursorCoords} />

        {/* Offline Vector Overlay Layers */}
        <GeoJSON
          data={KERALA_BOUNDARY_GEOJSON}
          style={{
            color: '#1F6B75',
            weight: 1.5,
            dashArray: '3, 3',
            fillColor: '#1F6B75',
            fillOpacity: 0.05
          }}
        />

        <GeoJSON
          data={ASSAM_BOUNDARY_GEOJSON}
          style={{
            color: '#C88A2E',
            weight: 1.5,
            dashArray: '3, 3',
            fillColor: '#C88A2E',
            fillOpacity: 0.05
          }}
        />

        {stations.map(st => {
          const risk = st.current_risk_level || 'Green';
          const isSelected = st.id === selectedStationId;
          const icon = createCustomMarkerIcon(st, risk, isSelected);

          // Low-lying zone contour polygon
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

              <Marker
                position={[st.latitude, st.longitude]}
                icon={icon}
                eventHandlers={{
                  click: () => onSelectStation(st)
                }}
              >
                {/* Hover Tooltip */}
                <LeafletTooltip direction="top" offset={[0, -25]} opacity={0.95}>
                  <div className="font-mono text-xs">
                    <strong className="block text-slate-900">{st.name} ({st.river})</strong>
                    <div>Risk: <span className="font-bold">{risk}</span></div>
                    <div>Water Level: {(st.current_water_level_m || st.normal_level_m).toFixed(2)}m</div>
                    <div className="text-[10px] text-slate-500">Updated: Just now</div>
                  </div>
                </LeafletTooltip>

                {/* Click Popup */}
                <Popup className="custom-leaflet-popup">
                  <div className="p-1 font-sans text-xs">
                    <div className="font-serif text-sm font-bold text-slate-900 mb-1">{st.name}</div>
                    <div className="text-slate-600 mb-2">{st.river} ({st.region})</div>
                    <div className="mb-2">
                      <RiskBadge level={risk} size="sm" />
                    </div>
                    <div className="font-mono text-[11px] text-slate-700 space-y-0.5">
                      <div>Water Level: <strong>{(st.current_water_level_m || st.normal_level_m).toFixed(2)}m</strong></div>
                      <div>Warning Level: {st.warning_level_m}m</div>
                      <div>Danger Level: {st.danger_level_m}m</div>
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
