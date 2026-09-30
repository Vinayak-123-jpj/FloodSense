// Simplified GeoJSON boundaries & river path lines for offline map fallback

export const KERALA_BOUNDARY_GEOJSON: GeoJSON.FeatureCollection = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: { name: "Kerala Region Boundary" },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [74.9, 12.8],
          [75.5, 12.4],
          [76.0, 11.9],
          [76.8, 11.6],
          [77.2, 10.8],
          [77.5, 9.8],
          [77.3, 8.3],
          [76.9, 8.8],
          [76.4, 9.4],
          [76.1, 10.0],
          [75.7, 10.8],
          [75.2, 11.8],
          [74.9, 12.8]
        ]]
      }
    },
    {
      type: "Feature",
      properties: { name: "Periyar River Mainstem" },
      geometry: {
        type: "LineString",
        coordinates: [
          [77.1, 9.6],
          [76.8, 9.9],
          [76.5781, 10.1416], // Neeleswaram
          [76.3516, 10.1076], // Aluva
          [76.22, 10.18]
        ]
      }
    },
    {
      type: "Feature",
      properties: { name: "Pamba River Mainstem" },
      geometry: {
        type: "LineString",
        coordinates: [
          [77.2, 9.3],
          [76.8, 9.35],
          [76.6122, 9.3175], // Chengannur
          [76.4, 9.3]
        ]
      }
    }
  ]
};

export const ASSAM_BOUNDARY_GEOJSON: GeoJSON.FeatureCollection = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: { name: "Assam Brahmaputra Valley Boundary" },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [89.7, 26.2],
          [91.5, 26.8],
          [93.5, 27.2],
          [95.8, 27.8],
          [96.0, 27.0],
          [94.0, 26.2],
          [92.0, 25.8],
          [89.7, 26.2]
        ]]
      }
    },
    {
      type: "Feature",
      properties: { name: "Brahmaputra Mainstem" },
      geometry: {
        type: "LineString",
        coordinates: [
          [95.5, 27.6],
          [94.9120, 27.4728], // Dibrugarh
          [92.8000, 26.6333], // Tezpur
          [91.7500, 26.1833], // Guwahati
          [89.9, 26.1]
        ]
      }
    }
  ]
};
