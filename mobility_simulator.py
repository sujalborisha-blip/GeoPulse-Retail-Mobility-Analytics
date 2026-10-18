"""
GeoPulse - Week 1: Massive-Scale Mobility Data Simulator (500k+ Records)
========================================================================
Domain: Retail Strategy & Geospatial Analytics
Purpose: High-performance vectorized generator simulating 500,000+ mobile GPS pings
         across 25,000 unique devices moving through Manhattan's 8 major retail
         and commuter corridors in a full 24-hour diurnal cycle.
"""

import time
import uuid
import json
import numpy as np
import pandas as pd
from datetime import datetime
from config import DATA_DIR, STORES, ZONING_POLYGONS, SIMULATION_PARAMS, GEO_BOUNDS

def generate_synthetic_mobility_dataset(
    num_devices=SIMULATION_PARAMS["num_devices"],
    seed=SIMULATION_PARAMS["random_seed"],
    base_date_str="2026-10-18"
):
    print("=" * 80)
    print("  GEOPULSE MASSIVE MOBILITY SIMULATOR (WEEK 1: 500,000+ PINGS SCALE)")
    print("=" * 80)
    print(f"[*] Initializing simulation for {num_devices:,} unique mobile devices...")
    start_time = time.time()
    np.random.seed(seed)

    base_date = datetime.strptime(base_date_str, "%Y-%m-%d")

    # Generate 25,000 Anonymized Unique Device IDs
    print("[*] Synthesizing 25,000 unique anonymized device identifiers...")
    # Fast hex generation
    raw_uuids = [f"DEV_{uuid.uuid4().hex[:8].upper()}" for _ in range(num_devices)]

    # Assign Personas corresponding to the 8 commercial hubs
    # 0: Financial District / Wall St Commuters (~25%)
    # 1: Fulton Commuter Transit Flow (~18%)
    # 2: SoHo Shopping & Residents (~12%)
    # 3: Union Sq / Village Transit (~10%)
    # 4: Flatiron Tech Hub (~12%)
    # 5: Chelsea / Meatpacking Corridor (~9%)
    # 6: Hudson Yards Corporate (~7%)
    # 7: Times Square / Midtown Central (~7%)
    anchor_weights = [z["weight"] for z in ZONING_POLYGONS]
    assigned_anchors = np.random.choice(len(ZONING_POLYGONS), size=num_devices, p=anchor_weights)

    # Pre-generate random ping counts per device (18 to 24 pings)
    pings_per_dev = np.random.randint(
        SIMULATION_PARAMS["pings_per_device_range"][0],
        SIMULATION_PARAMS["pings_per_device_range"][1] + 1,
        size=num_devices
    )
    total_expected_pings = int(pings_per_dev.sum())
    print(f"[+] Total targeted pings to synthesize: {total_expected_pings:,} records.")

    # 24-hour city rush-hour probability distribution
    hour_weights = np.array([
        0.01, 0.01, 0.01, 0.01, 0.01, 0.02,  # 00:00 - 05:00
        0.05, 0.10, 0.13, 0.08, 0.06, 0.07,  # 06:00 - 11:00 (Morning Rush)
        0.11, 0.09, 0.06, 0.05, 0.07, 0.10,  # 12:00 - 17:00 (Lunch & Afternoon)
        0.08, 0.06, 0.04, 0.03, 0.02, 0.01   # 18:00 - 23:00 (Evening)
    ])
    hour_weights = hour_weights / hour_weights.sum()

    all_records = []

    print("[*] Generating diurnal trajectories and spatial coordinates across 8 zones...")
    
    # Store coordinates list for fast lookup
    zone_lats = np.array([z["lat"] for z in ZONING_POLYGONS])
    zone_lngs = np.array([z["lng"] for z in ZONING_POLYGONS])

    # Batch synthesize per device
    for dev_idx in range(num_devices):
        dev_id = raw_uuids[dev_idx]
        anchor_idx = assigned_anchors[dev_idx]
        n_p = pings_per_dev[dev_idx]

        # Anchor coordinates with slight resident/office jitter
        base_lat = zone_lats[anchor_idx] + np.random.normal(0, 0.0025)
        base_lng = zone_lngs[anchor_idx] + np.random.normal(0, 0.0025)

        # Sample hours
        hrs = np.random.choice(24, size=n_p, p=hour_weights, replace=True)
        hrs.sort()

        for h in hrs:
            minute = np.random.randint(0, 60)
            second = np.random.randint(0, 60)
            t_str = f"{base_date_str} {h:02d}:{minute:02d}:{second:02d}"

            # Spatial movement logic based on hour
            if anchor_idx == 0:
                # Financial District: morning rush passes Fulton (Store 02) -> Wall St (Store 01)
                if 7 <= h <= 9:
                    interp = (h - 7) / 2.0
                    p_lat = (1 - interp) * STORES["STORE_02"]["lat"] + interp * STORES["STORE_01"]["lat"] + np.random.normal(0, 0.0010)
                    p_lng = (1 - interp) * STORES["STORE_02"]["lng"] + interp * STORES["STORE_01"]["lng"] + np.random.normal(0, 0.0010)
                    act = "COMMUTE_WALK"
                elif 11 <= h <= 14:
                    p_lat = STORES["STORE_01"]["lat"] + np.random.normal(0, 0.0015)
                    p_lng = STORES["STORE_01"]["lng"] + np.random.normal(0, 0.0015)
                    act = "RETAIL_DINING"
                else:
                    p_lat = base_lat + np.random.normal(0, 0.0012)
                    p_lng = base_lng + np.random.normal(0, 0.0012)
                    act = "COMMERCIAL_OFFICE"
            else:
                # Other zones (Midtown, SoHo, Flatiron, Hudson Yards, Times Sq)
                if 11 <= h <= 14:
                    # Lunch walk within zone
                    p_lat = base_lat + np.random.normal(0, 0.0018)
                    p_lng = base_lng + np.random.normal(0, 0.0018)
                    act = "RETAIL_DINING"
                else:
                    p_lat = base_lat + np.random.normal(0, 0.0014)
                    p_lng = base_lng + np.random.normal(0, 0.0014)
                    act = "STATIONARY" if (h < 6 or h > 20) else "TRANSIT"

            # Clamp coordinates
            p_lat = max(GEO_BOUNDS["min_lat"], min(GEO_BOUNDS["max_lat"], p_lat))
            p_lng = max(GEO_BOUNDS["min_lng"], min(GEO_BOUNDS["max_lng"], p_lng))

            all_records.append((
                dev_id, t_str, int(h),
                round(float(p_lat), 6), round(float(p_lng), 6),
                round(float(np.random.uniform(4.0, 10.0)), 1),
                round(float(np.random.uniform(1.0, 4.8)), 1) if act != "STATIONARY" else 0.0,
                act, anchor_idx
            ))

    print(f"[*] Building high-performance DataFrame ({len(all_records):,} records)...")
    df = pd.DataFrame(all_records, columns=[
        "device_id", "timestamp", "hour", "latitude", "longitude",
        "accuracy_meters", "speed_kmh", "activity_type", "zone_anchor"
    ])
    df.sort_values(by=["timestamp", "device_id"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    elapsed = time.time() - start_time
    print(f"[+] Synthesis complete in {elapsed:.2f} seconds!")
    print(f"[+] Massive Scale Reached: {len(df):,} GPS pings across {df['device_id'].nunique():,} devices!")

    # Export to Parquet and CSV
    parquet_path = DATA_DIR / "raw_gps_pings.parquet"
    csv_path = DATA_DIR / "raw_gps_pings.csv"

    print(f"[*] Exporting to Lakehouse Parquet ({parquet_path.name})...")
    df.to_parquet(parquet_path, index=False, engine="pyarrow", compression="snappy")

    print(f"[*] Exporting sample CSV ({csv_path.name})...")
    df.to_csv(csv_path, index=False)

    # Export All 8 Stores to GeoJSON
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
                    "district": store["district"],
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
    with open(DATA_DIR / "stores.geojson", "w") as f:
        json.dump(stores_geojson, f, indent=2)

    print("[+] Stores GeoJSON exported with all 8 retail locations.")
    print("=" * 80)
    return df

if __name__ == "__main__":
    generate_synthetic_mobility_dataset()
