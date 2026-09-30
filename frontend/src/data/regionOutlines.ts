// Real simplified boundary geometry following coastal contours and Western Ghats / Brahmaputra valley

export const KERALA_BOUNDARY_GEOJSON: GeoJSON.FeatureCollection = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: { name: "State of Kerala Coastal Boundary" },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [74.90, 12.50], // Kasaragod North Coast
          [75.36, 11.87], // Kannur Coast
          [75.77, 11.25], // Kozhikode Coast
          [75.92, 10.77], // Ponnani Coast
          [76.22, 10.15], // Kochi / Azhikode
          [76.32, 9.49],  // Alappuzha Coast
          [76.58, 8.89],  // Kollam Coast
          [77.07, 8.31],  // Thiruvananthapuram Coast
          [77.15, 8.35],  // Southernmost border
          [77.18, 8.76],  // Ponmudi / Agasthyamalai
          [77.10, 9.15],  // Pathanamthitta Ghats
          [77.05, 9.58],  // Cardamom Hills
          [77.06, 10.17], // Munnar / Anamudi
          [76.80, 10.82], // Palakkad Gap
          [76.52, 11.15], // Silent Valley
          [76.25, 11.72], // Wayanad Hills
          [75.40, 12.55], // Kasaragod East
          [74.90, 12.50]  // Kasaragod North Coast (Closing loop)
        ]]
      }
    },
    {
      type: "Feature",
      properties: { name: "Periyar River Mainstem Channel" },
      geometry: {
        type: "LineString",
        coordinates: [
          [77.25, 9.55],
          [77.05, 9.75],
          [76.88, 9.92],
          [76.65, 10.08],
          [76.5781, 10.1416], // Neeleswaram Station
          [76.3516, 10.1076], // Aluva Station
          [76.20, 10.16]      // Arabian Sea Exit
        ]
      }
    },
    {
      type: "Feature",
      properties: { name: "Pamba River Mainstem Channel" },
      geometry: {
        "type": "LineString",
        coordinates: [
          [77.15, 9.35],
          [76.85, 9.38],
          [76.6122, 9.3175], // Chengannur Station
          [76.42, 9.34],
          [76.35, 9.49]       // Vembanad Lake Exit
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
      properties: { name: "Assam Valley Boundary" },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [89.95, 26.00], // Dhubri West Border
          [90.60, 26.15], // Goalpara North Bank
          [91.75, 26.18], // Guwahati North Bank
          [92.80, 26.63], // Tezpur North Bank
          [94.10, 27.20], // Lakhimpur Foothills
          [95.70, 27.80], // Tinsukia / Sadiya East
          [94.90, 27.48], // Dibrugarh South Bank
          [94.20, 26.75], // Jorhat
          [92.68, 26.35], // Nagaon / Karbi Anglong
          [91.80, 26.14], // Dispur / Meghalaya Border
          [90.62, 25.95], // Goalpara South Bank
          [89.95, 26.00]  // Dhubri West Border (Closing loop)
        ]]
      }
    },
    {
      type: "Feature",
      properties: { name: "Brahmaputra River Main Channel" },
      geometry: {
        type: "LineString",
        coordinates: [
          [95.50, 27.60],
          [94.9120, 27.4728], // Dibrugarh Station
          [93.80, 26.90],
          [92.8000, 26.6333], // Tezpur Station
          [91.7500, 26.1833], // Guwahati Station
          [90.60, 26.15],
          [89.85, 26.00]       // Bangladesh Exit
        ]
      }
    }
  ]
};
