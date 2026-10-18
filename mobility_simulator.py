"""
GeoPulse - Week 1: Mobility Data Simulator
===========================================
Domain: Retail Strategy & Geospatial Analytics
Purpose: High-performance generator of anonymized mobile GPS pings
         (DeviceID, Lat, Long, Timestamp, Accuracy, Speed) mimicking
         dynamic metropolitan pedestrian footfall and commuter patterns.
"""

import time
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from config import DATA_DIR, STORES, ZONING_POLYGONS, SIMULATION_PARAMS, GEO_BOUNDS

def generate_synthetic_mobility_dataset(
    num_devices=SIMULATION_PARAMS["num_devices"],
    seed=SIMULATION_PARAMS["random_seed"],
    base_date_str="2026-10-18"
):
    """
    Generates a massive, realistic GPS mobility ping dataset simulating urban flow.
    Models distinct urban personas:
      1. Financial District Commuters (heavy footfall near Wall St & Fulton Hub)
      2. Midtown / Flatiron Tech Workers (concentrated near Madison Square)
      3. Retail & Shopping Corridors (SoHo shoppers)
      4. Residential & General Urban Transit
    """
    print("=" * 70)
    print("  GEOPULSE MOBILITY SIMULATOR (WEEK 1: DATA SYNTHESIS)")
    print("=" * 70)
    print(f"[*] Initializing simulation for {num_devices:,} unique mobile devices...")
    start_time = time.time()
    np.random.seed(seed)

    base_date = datetime.strptime(base_date_str, "%Y-%m-%d")

    # Generate Unique Device IDs (Anonymized SHA-like format)
    device_ids = [f"DEV_{uuid.uuid4().hex[:8].upper()}" for _ in range(num_devices)]

    # Assign Device Personas
    # Persona 0: Wall St & Lower Manhattan Commuters (~45% - key for Store A / B interaction)
    # Persona 1: Flatiron / Midtown Workers (~30% - key for Store C non-overlap)
    # Persona 2: SoHo / Downtown Shoppers (~15%)
    # Persona 3: Random Citywide Commuters (~10%)
    persona_probs = [0.45, 0.30, 0.15, 0.10]
    personas = np.random.choice([0, 1, 2, 3], size=num_devices, p=persona_probs)

    all_pings = []

    # Persona Base Anchors (Home, Work, Transit)
    # Wall St Commuters anchor around Fulton/Wall St
    p0_home_lat = np.random.normal(40.7180, 0.015, size=num_devices)
    p0_home_lng = np.random.normal(-74.0020, 0.012, size=num_devices)

    p0_work_lat = np.random.normal(STORES["STORE_A"]["lat"], 0.003, size=num_devices)
    p0_work_lng = np.random.normal(STORES["STORE_A"]["lng"], 0.003, size=num_devices)

    # Flatiron Commuters anchor around Store C
    p1_work_lat = np.random.normal(STORES["STORE_C"]["lat"], 0.004, size=num_devices)
    p1_work_lng = np.random.normal(STORES["STORE_C"]["lng"], 0.004, size=num_devices)

    print("[*] Generating 24-hour diurnal movement trajectories...")

    for dev_idx in range(num_devices):
        dev_id = device_ids[dev_idx]
        persona = personas[dev_idx]

        # Each device generates 16-24 pings throughout the day
        n_pings = np.random.randint(SIMULATION_PARAMS["pings_per_device_range"][0],
                                    SIMULATION_PARAMS["pings_per_device_range"][1] + 1)
        
        # Pick realistic hours with probability distribution mimicking city rush hours
        # Hours: 0 to 23
        hour_weights = [
            0.01, 0.01, 0.01, 0.01, 0.01, 0.02,  # 00:00 - 05:00 (Night)
            0.04, 0.09, 0.12, 0.08, 0.06, 0.07,  # 06:00 - 11:00 (Morning Rush)
            0.11, 0.09, 0.06, 0.05, 0.07, 0.10,  # 12:00 - 17:00 (Lunch & Afternoon)
            0.09, 0.06, 0.04, 0.03, 0.02, 0.01   # 18:00 - 23:00 (Evening & Night)
        ]
        hour_weights = np.array(hour_weights) / sum(hour_weights)
        sample_hours = np.random.choice(range(24), size=n_pings, p=hour_weights, replace=True)
        sample_hours.sort()

        for h in sample_hours:
            minute = np.random.randint(0, 60)
            second = np.random.randint(0, 60)
            timestamp = base_date.replace(hour=int(h), minute=int(minute), second=int(second))

            # Position calculation based on Persona and Hour
            if persona == 0:
                # Wall Street Commuter:
                # 07-09: Passes Fulton transit hub (near Store B) walking toward Wall St (Store A)
                # 11-14: Lunch walking near Store A / Fulton
                # 17-19: Evening commute back through Fulton
                if 7 <= h <= 9:
                    # Morning commute: High density walking down Broadway / Fulton to Wall St
                    interp = (h - 7) / 2.0
                    lat = (1 - interp) * STORES["STORE_B"]["lat"] + interp * STORES["STORE_A"]["lat"] + np.random.normal(0, 0.0012)
                    lng = (1 - interp) * STORES["STORE_B"]["lng"] + interp * STORES["STORE_A"]["lng"] + np.random.normal(0, 0.0012)
                    activity = "COMMUTE_WALK"
                elif 11 <= h <= 14:
                    # Lunch peak: Dwell around Wall St / Fulton
                    if np.random.rand() > 0.45:
                        lat = STORES["STORE_A"]["lat"] + np.random.normal(0, 0.0015)
                        lng = STORES["STORE_A"]["lng"] + np.random.normal(0, 0.0015)
                    else:
                        lat = STORES["STORE_B"]["lat"] + np.random.normal(0, 0.0018)
                        lng = STORES["STORE_B"]["lng"] + np.random.normal(0, 0.0018)
                    activity = "RETAIL_DINING"
                elif 17 <= h <= 19:
                    # Evening rush: walking north toward Fulton transit
                    lat = STORES["STORE_B"]["lat"] + np.random.normal(0, 0.0020)
                    lng = STORES["STORE_B"]["lng"] + np.random.normal(0, 0.0020)
                    activity = "COMMUTE_TRANSIT"
                else:
                    # Work desk / Home
                    lat = p0_work_lat[dev_idx] + np.random.normal(0, 0.0010)
                    lng = p0_work_lng[dev_idx] + np.random.normal(0, 0.0010)
                    activity = "STATIONARY"

            elif persona == 1:
                # Flatiron Tech Worker (Store C corridor)
                if 11 <= h <= 14:
                    lat = STORES["STORE_C"]["lat"] + np.random.normal(0, 0.0020)
                    lng = STORES["STORE_C"]["lng"] + np.random.normal(0, 0.0020)
                    activity = "RETAIL_DINING"
                else:
                    lat = p1_work_lat[dev_idx] + np.random.normal(0, 0.0030)
                    lng = p1_work_lng[dev_idx] + np.random.normal(0, 0.0030)
                    activity = "COMMERCIAL_OFFICE"

            elif persona == 2:
                # SoHo Retail Shopper (Between Canal St and Houston St)
                lat = np.random.uniform(40.7200, 40.7280)
                lng = np.random.uniform(-74.0040, -73.9940)
                activity = "SHOPPING_LEISURE"

            else:
                # General City Mobility
                lat = np.random.uniform(GEO_BOUNDS["min_lat"], GEO_BOUNDS["max_lat"])
                lng = np.random.uniform(GEO_BOUNDS["min_lng"], GEO_BOUNDS["max_lng"])
                activity = "TRANSIT"

            # Clamp coordinates within bounding box
            lat = max(GEO_BOUNDS["min_lat"], min(GEO_BOUNDS["max_lat"], lat))
            lng = max(GEO_BOUNDS["min_lng"], min(GEO_BOUNDS["max_lng"], lng))

            accuracy_m = round(float(np.random.uniform(3.5, 12.0)), 1)
            speed_kmh = round(float(np.random.uniform(1.2, 5.5)), 2) if activity != "STATIONARY" else 0.0

            all_pings.append({
                "device_id": dev_id,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "hour": int(h),
                "latitude": round(float(lat), 6),
                "longitude": round(float(lng), 6),
                "accuracy_meters": accuracy_m,
                "speed_kmh": speed_kmh,
                "activity_type": activity,
                "persona": persona
            })

    # Build DataFrame
    df = pd.DataFrame(all_pings)
    df.sort_values(by=["timestamp", "device_id"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    elapsed = time.time() - start_time
    print(f"[+] Generation complete in {elapsed:.2f} seconds!")
    print(f"[+] Total GPS Pings generated: {len(df):,}")
    print(f"[+] Unique Devices: {df['device_id'].nunique():,}")
    print(f"[+] Date Simulated: {base_date_str} (Full 24-Hour Cycle)")

    # Export to CSV and Parquet
    csv_path = DATA_DIR / "raw_gps_pings.csv"
    parquet_path = DATA_DIR / "raw_gps_pings.parquet"

    print(f"[*] Exporting to {csv_path.name}...")
    df.to_csv(csv_path, index=False)
    
    print(f"[*] Exporting to {parquet_path.name} (Optimized Columnar Lakehouse format)...")
    df.to_parquet(parquet_path, index=False, engine="pyarrow", compression="snappy")

    # Export Stores GeoJSON for map consumption
    stores_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [store["lng"], store["lat"]]
                },
                "properties": {
                    "store_id": sid,
                    "name": store["name"],
                    "status": store["status"],
                    "catchment_radius_m": store["catchment_radius_m"],
                    "color": store["color"],
                    "avg_daily_revenue_usd": store["avg_daily_revenue_usd"],
                    "description": store["description"]
                }
            }
            for sid, store in STORES.items()
        ]
    }
    
    import json
    with open(DATA_DIR / "stores.geojson", "w") as f:
        json.dump(stores_geojson, f, indent=2)

    print("[+] Stores GeoJSON exported successfully.")
    print("=" * 70)
    return df

if __name__ == "__main__":
    df = generate_synthetic_mobility_dataset()
    print("Sample Records:")
    print(df.head(5))
