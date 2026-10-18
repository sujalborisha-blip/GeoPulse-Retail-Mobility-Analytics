"""
GeoPulse - Configuration Module (Enterprise Multi-Store Scale)
==============================================================
Domain: Retail Strategy & Geospatial Analytics
Purpose: Enterprise-scale retail network (8 Strategic Stores across Manhattan),
         commercial zoning hubs, 500m catchment parameters, and 500,000+ GPS ping scale.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

for folder in [DATA_DIR, OUTPUT_DIR, TEMPLATES_DIR, STATIC_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Geographic Bounding Box: Manhattan Metro Commercial Corridors
GEO_BOUNDS = {
    "min_lat": 40.6980,
    "max_lat": 40.7650,
    "min_lng": -74.0200,
    "max_lng": -73.9650,
    "center_lat": 40.7280,
    "center_lng": -73.9950,
    "zoom_default": 13
}

# Enterprise Retail Chain: "UrbanBean Coffee & Artisan Roasters"
# 8 Strategic Locations: Existing Operating Flagships + Candidate Expansions
STORES = {
    "STORE_01": {
        "id": "STORE_01",
        "name": "Wall Street Flagship",
        "district": "Financial District",
        "status": "EXISTING",
        "lat": 40.7075,
        "lng": -74.0090,
        "catchment_radius_m": 500,
        "avg_daily_revenue_usd": 5400.00,
        "avg_ticket_size_usd": 6.85,
        "color": "#10b981", # Emerald
        "description": "High-volume flagship anchor capturing investment bank commuters."
    },
    "STORE_02": {
        "id": "STORE_02",
        "name": "Fulton Transit Concourse",
        "district": "Financial District / World Trade",
        "status": "CANDIDATE",
        "lat": 40.7112,
        "lng": -74.0080,
        "catchment_radius_m": 500,
        "avg_daily_revenue_usd": 0.0,
        "avg_ticket_size_usd": 6.85,
        "color": "#ef4444", # Red / Severe Cannibalization Alert
        "description": "Proposed near-site 420m upstream of Store 01; severe commuter theft."
    },
    "STORE_03": {
        "id": "STORE_03",
        "name": "SoHo Broadway Corridor",
        "district": "SoHo Fashion Retail",
        "status": "EXISTING",
        "lat": 40.7235,
        "lng": -73.9985,
        "catchment_radius_m": 500,
        "avg_daily_revenue_usd": 4900.00,
        "avg_ticket_size_usd": 7.40,
        "color": "#10b981", # Emerald
        "description": "Thriving lifestyle & high-street shopping retail venue."
    },
    "STORE_04": {
        "id": "STORE_04",
        "name": "Union Square Plaza",
        "district": "Greenwich / East Village",
        "status": "CANDIDATE",
        "lat": 40.7358,
        "lng": -73.9908,
        "catchment_radius_m": 500,
        "avg_daily_revenue_usd": 0.0,
        "avg_ticket_size_usd": 6.95,
        "color": "#f59e0b", # Amber / Moderate Overlap
        "description": "High footfall transit hub; moderate 28% overlap with Flatiron."
    },
    "STORE_05": {
        "id": "STORE_05",
        "name": "Flatiron Tech District",
        "district": "Madison Square / Flatiron",
        "status": "CANDIDATE",
        "lat": 40.7410,
        "lng": -73.9897,
        "catchment_radius_m": 500,
        "avg_daily_revenue_usd": 0.0,
        "avg_ticket_size_usd": 7.20,
        "color": "#3b82f6", # Blue / Top Approved Candidate
        "description": "Prime tech/creative office cluster; zero overlap with Lower Manhattan."
    },
    "STORE_06": {
        "id": "STORE_06",
        "name": "Chelsea Market Corridor",
        "district": "Meatpacking / Chelsea",
        "status": "EXISTING",
        "lat": 40.7424,
        "lng": -74.0062,
        "catchment_radius_m": 500,
        "avg_daily_revenue_usd": 4650.00,
        "avg_ticket_size_usd": 7.50,
        "color": "#10b981", # Emerald
        "description": "Tech campus anchor adjacent to High Line & Google offices."
    },
    "STORE_07": {
        "id": "STORE_07",
        "name": "Hudson Yards Complex",
        "district": "Midtown West",
        "status": "CANDIDATE",
        "lat": 40.7538,
        "lng": -74.0022,
        "catchment_radius_m": 500,
        "avg_daily_revenue_usd": 0.0,
        "avg_ticket_size_usd": 7.80,
        "color": "#8b5cf6", # Purple / Approved Luxury Hub
        "description": "Ultra-modern corporate & luxury retail center; high net-new capture."
    },
    "STORE_08": {
        "id": "STORE_08",
        "name": "Times Square Midtown Hub",
        "district": "Theatre / Midtown Central",
        "status": "EXISTING",
        "lat": 40.7580,
        "lng": -73.9855,
        "catchment_radius_m": 500,
        "avg_daily_revenue_usd": 6800.00,
        "avg_ticket_size_usd": 7.10,
        "color": "#10b981", # Emerald
        "description": "Highest footfall density node in North America."
    }
}

# Commercial Mobility Anchors & Zoning Polygons
ZONING_POLYGONS = [
    {"name": "Financial District", "lat": 40.7075, "lng": -74.0090, "weight": 0.22},
    {"name": "Fulton Transit Corridor", "lat": 40.7112, "lng": -74.0080, "weight": 0.18},
    {"name": "SoHo Fashion District", "lat": 40.7235, "lng": -73.9985, "weight": 0.12},
    {"name": "Union Square Concourse", "lat": 40.7358, "lng": -73.9908, "weight": 0.11},
    {"name": "Flatiron Tech Corridor", "lat": 40.7410, "lng": -73.9897, "weight": 0.12},
    {"name": "Chelsea Tech / High Line", "lat": 40.7424, "lng": -74.0062, "weight": 0.09},
    {"name": "Hudson Yards Commerce", "lat": 40.7538, "lng": -74.0022, "weight": 0.08},
    {"name": "Times Square Central", "lat": 40.7580, "lng": -73.9855, "weight": 0.08}
]

# Massive Scale Simulation Parameters (500,000+ Records)
SIMULATION_PARAMS = {
    "num_devices": 25000,          # 25,000 unique mobile devices
    "pings_per_device_range": (18, 25), # Realistic 18-25 pings throughout day
    "target_total_pings": 525000,  # 500,000+ Massive GPS Ping Scale!
    "hours": list(range(24)),
    "h3_resolution": 9,            # ~100m edge length
    "random_seed": 42
}
