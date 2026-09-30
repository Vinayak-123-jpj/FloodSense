# FloodSense Hydrological & Weather Data Specifications

## Primary Focus Regions & Station Metadata

### 1. Primary Region: Kerala (Periyar & Pamba Basins)
- **Neeleswaram (KL-PER-01)**: Lat `10.1416`, Lng `76.5781`, Warning `4.5m`, Danger `6.0m`, Elevation `12m`. Upper Periyar reservoir discharge monitoring.
- **Aluva (KL-PER-02)**: Lat `10.1076`, Lng `76.3516`, Warning `3.8m`, Danger `5.2m`, Elevation `7m`. Lower Periyar urban basin.
- **Chengannur (KL-PAM-01)**: Lat `9.3175`, Lng `76.6122`, Warning `5.0m`, Danger `6.5m`, Elevation `9m`. Central Pamba catchment.
- **Muvattupuzha (KL-MUV-01)**: Lat `9.9813`, Lng `76.5772`, Warning `4.0m`, Danger `5.5m`, Elevation `14m`. Tri-river confluence.
- **Chalakudy (KL-CHA-01)**: Lat `10.3070`, Lng `76.3323`, Warning `4.2m`, Danger `5.8m`, Elevation `11m`. Sholayar overflow gauge.
- **Thumpamon (KL-ACH-01)**: Lat `9.2560`, Lng `76.7110`, Warning `4.8m`, Danger `6.2m`, Elevation `15m`. Achenkovil flood plains.

---

### 2. Secondary Region: Assam (Brahmaputra Basin)
- **Guwahati (AS-BRA-01)**: Lat `26.1833`, Lng `91.7500`, Warning `48.5m`, Danger `49.68m`, Elevation `52m`. Mainstem Brahmaputra DC Court Ghat.
- **Dibrugarh (AS-BRA-02)**: Lat `27.4728`, Lng `94.9120`, Warning `104.5m`, Danger `105.7m`, Elevation `108m`. Upper Assam Himalayan runoff.
- **Kampur (AS-KOP-01)**: Lat `26.1500`, Lng `92.5833`, Warning `59.0m`, Danger `60.5m`, Elevation `63m`. Kopili flash flood basin.
- **Numaligarh (AS-DHA-01)**: Lat `26.5667`, Lng `93.7333`, Warning `78.0m`, Danger `79.5m`, Elevation `82m`. Dhansiri tributary.
- **Tezpur (AS-JIA-01)**: Lat `26.6333`, Lng `92.8000`, Warning `76.5m`, Danger `77.5m`, Elevation `80m`. Jia Bharali glacial melt gauge.

---

### 3. Open-Meteo API Endpoints & Offline Caching Strategy

1. **Weather API**: `https://archive-api.open-meteo.com/v1/archive`
   - Parameter: `hourly=precipitation` (in mm/hr)
2. **Global Flood API**: `https://flood-api.open-meteo.com/v1/flood`
   - Parameter: `daily=river_discharge` (in m³/s)
3. **Offline Fallback Storage**:
   - Downloads saved to `/data/raw/kerala_weather_flood.csv` (8,760 rows) and `/data/raw/assam_weather_flood.csv` (26,304 rows).
   - Committed in Git so the system operates offline without requiring active internet connectivity during judge demonstrations.
