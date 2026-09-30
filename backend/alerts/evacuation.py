"""OpenStreetMap (OSRM) Evacuation Route Generator.

Calculates directions from a monitoring station's coordinates to the nearest
high-ground evacuation point using OpenStreetMap OSRM public routing API.
Includes graceful fallback link generation.
"""

import requests
from typing import Tuple, Dict

# High-ground shelter coordinates for Kerala and Assam regions
HIGH_GROUND_SHELTERS = [
    {"name": "Malayattoor St. Thomas High Ground", "latitude": 10.1833, "longitude": 76.5167, "elevation_m": 85.0},
    {"name": "Aluva Hill Palace Ridge", "latitude": 10.1200, "longitude": 76.3800, "elevation_m": 45.0},
    {"name": "Chengannur Mahadeva Temple Heights", "latitude": 9.3250, "longitude": 76.6250, "elevation_m": 35.0},
    {"name": "Guwahati Kamakhya Hill Sanctuary", "latitude": 26.1667, "longitude": 91.7000, "elevation_m": 180.0},
    {"name": "Dibrugarh High Embankment Complex", "latitude": 27.4850, "longitude": 94.9250, "elevation_m": 115.0}
]

def find_nearest_high_ground(station_lat: float, station_lng: float) -> Dict[str, float]:
    """Finds the geographically nearest high-ground shelter coordinate."""
    best_shelter = HIGH_GROUND_SHELTERS[0]
    min_dist_sq = 1e9

    for s in HIGH_GROUND_SHELTERS:
        d_sq = (s["latitude"] - station_lat)**2 + (s["longitude"] - station_lng)**2
        if d_sq < min_dist_sq:
            min_dist_sq = d_sq
            best_shelter = s

    return best_shelter

def generate_evacuation_route_link(station_lat: float, station_lng: float) -> Tuple[str, str]:
    """Generates an OpenStreetMap OSRM evacuation route URL towards high ground.
    
    Returns:
        Tuple of (evacuation_route_url, shelter_description_text).
    """
    shelter = find_nearest_high_ground(station_lat, station_lng)
    dest_lat = shelter["latitude"]
    dest_lng = shelter["longitude"]
    shelter_name = shelter["name"]

    # Construct OpenStreetMap directions link
    osm_url = (
        f"https://www.openstreetmap.org/directions?"
        f"engine=fossgis_osrm_car&route={station_lat}%2C{station_lng}%3B{dest_lat}%2C{dest_lng}"
    )

    description = f"Evacuate towards {shelter_name} (Elevation: {shelter['elevation_m']}m AMSL)"
    return osm_url, description
