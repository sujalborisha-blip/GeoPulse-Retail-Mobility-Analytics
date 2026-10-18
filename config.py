"""
GeoPulse - Configuration Module
===============================
Domain: Retail Strategy & Geospatial Analytics
Purpose: Central configuration for store locations, geospatial bounding boxes,
         catchment radius, and simulation parameters.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Ensure runtime directories exist
for folder in [DATA_DIR, OUTPUT_DIR, TEMPLATES_DIR, STATIC_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Geographic Bounding Box: Manhattan Retail & Commuter Corridor
# Centered around Financial District, SoHo, and Midtown
GEO_BOUNDS = {
    "min_lat": 40.7000,
    "max_lat": 40.7550,
    "min_lng": -74.0180,
    "max_lng": -73.9720,
    "center_lat": 40.7180,
    "center_lng": -73.9980,
    "zoom_default": 13
}

# Retail Chain: "UrbanBean Coffee & Roastery"
# Store network evaluated for expansion & cannibalization
STORES = {
    "STORE_A": {
        "id": "STORE_A",
        "name": "Wall Street Flagship (Existing)",
        "status": "EXISTING",
        "lat": 40.7075,
        "lng": -74.0090,
        "catchment_radius_m": 500,  # 500-meter catchment area required by syllabus
        "avg_daily_revenue_usd": 4850.00,
        "avg_ticket_size_usd": 6.85,
        "color": "#10b981",  # Emerald Green
        "description": "Primary high-volume revenue generator in Financial District."
    },
    "STORE_B": {
        "id": "STORE_B",
        "name": "Fulton Transit Hub (Proposed Candidate 1)",
        "status": "CANDIDATE",
        "lat": 40.7112,
        "lng": -74.0080,
        "catchment_radius_m": 500,
        "avg_daily_revenue_usd": 0.0,
        "avg_ticket_size_usd": 6.85,
        "color": "#ef4444",  # Red / High Cannibalization Alert
        "description": "Located ~420m north of Store A; intercepting identical commuter flow."
    },
    "STORE_C": {
        "id": "STORE_C",
        "name": "Flatiron / Madison Sq (Proposed Candidate 2)",
        "status": "CANDIDATE",
        "lat": 40.7410,
        "lng": -73.9897,
        "catchment_radius_m": 500,
        "avg_daily_revenue_usd": 0.0,
        "avg_ticket_size_usd": 7.20,
        "color": "#3b82f6",  # Royal Blue / Clean Expansion
        "description": "Midtown commercial/tech corridor ~3.8km away; zero customer overlap."
    }
}

# Commercial Zones / POIs for Mobility Anchors
ZONING_POLYGONS = [
    {
        "zone_id": "ZONE_FIN_DISTRICT",
        "name": "Financial District Corporate Core",
        "type": "COMMERCIAL_OFFICE",
        "lat_range": (40.7040, 40.7100),
        "lng_range": (-74.0130, -74.0060),
        "morning_weight": 0.35,
        "lunch_weight": 0.40,
        "evening_weight": 0.25
    },
    {
        "zone_id": "ZONE_FULTON_TRANSIT",
        "name": "Fulton Transit Hub & Commuter Concourse",
        "type": "TRANSIT_HUB",
        "lat_range": (40.7095, 40.7135),
        "lng_range": (-74.0100, -74.0050),
        "morning_weight": 0.40,
        "lunch_weight": 0.25,
        "evening_weight": 0.35
    },
    {
        "zone_id": "ZONE_SOHO_RETAIL",
        "name": "SoHo High Street Retail Corridor",
        "type": "COMMERCIAL_RETAIL",
        "lat_range": (40.7210, 40.7270),
        "lng_range": (-74.0030, -73.9960),
        "morning_weight": 0.10,
        "lunch_weight": 0.35,
        "evening_weight": 0.55
    },
    {
        "zone_id": "ZONE_FLATIRON_TECH",
        "name": "Flatiron Tech & Creative Hub",
        "type": "COMMERCIAL_OFFICE",
        "lat_range": (40.7380, 40.7440),
        "lng_range": (-73.9930, -73.9860),
        "morning_weight": 0.30,
        "lunch_weight": 0.45,
        "evening_weight": 0.25
    }
]

# Mobility Simulation Parameters
SIMULATION_PARAMS = {
    "num_devices": 6000,           # 6,000 unique synthetic mobile devices
    "pings_per_device_range": (15, 25), # Realistic 15-25 pings throughout the day
    "target_total_pings": 120000,  # ~120,000 total GPS points
    "hours": list(range(24)),
    "h3_resolution": 9,             # ~100m hexagon edge length for hyper-local density
    "random_seed": 42
}
