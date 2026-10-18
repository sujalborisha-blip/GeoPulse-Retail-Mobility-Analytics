"""
GeoPulse - Week 2: Massive Spatial Engine & 8-Store Catchment Modeling
======================================================================
Domain: Retail Strategy & Geospatial Analytics
Purpose: 500m geodesic catchment polygons for 8 commercial store nodes,
         vectorized spatial joins across 500,000+ GPS coordinates,
         and multi-store hourly footfall modeling.
"""

import time
import json
import math
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon, mapping
from config import DATA_DIR, OUTPUT_DIR, STORES

EARTH_RADIUS_M = 6371000.0

def create_geodesic_circle_polygon(center_lat, center_lng, radius_m=500, num_points=64):
    coords = []
    lat_r = math.radians(center_lat)
    lng_r = math.radians(center_lng)
    d_r = radius_m / EARTH_RADIUS_M

    for i in range(num_points):
        bearing = math.radians(i * (360.0 / num_points))
        point_lat_r = math.asin(
            math.sin(lat_r) * math.cos(d_r) +
            math.cos(lat_r) * math.sin(d_r) * math.cos(bearing)
        )
        point_lng_r = lng_r + math.atan2(
            math.sin(bearing) * math.sin(d_r) * math.cos(lat_r),
            math.cos(d_r) - math.sin(lat_r) * math.sin(point_lat_r)
        )
        coords.append((math.degrees(point_lng_r), math.degrees(point_lat_r)))
    coords.append(coords[0])
    return Polygon(coords)

def vectorized_haversine(lat1, lng1, lat2_arr, lng2_arr):
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2_arr)
    delta_phi = np.radians(lat2_arr - lat1)
    delta_lambda = np.radians(lng2_arr - lng1)
    a = np.sin(delta_phi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return EARTH_RADIUS_M * c

def run_spatial_joins_and_aggregations():
    print("=" * 80)
    print("  GEOPULSE SPATIAL ENGINE (WEEK 2: 8-STORE CATCHMENT JOINS ACROSS 500K+ RECORDS)")
    print("=" * 80)
    start_time = time.time()

    # Load from Lakehouse Parquet
    parquet_path = DATA_DIR / "raw_gps_pings.parquet"
    if parquet_path.exists():
        df_pings = pd.read_parquet(parquet_path)
    else:
        df_pings = pd.read_csv(DATA_DIR / "raw_gps_pings.csv")

    total_pings = len(df_pings)
    print(f"[+] Loaded {total_pings:,} raw GPS mobility records from Lakehouse Parquet.")

    # 1. Generate 500-meter Catchment Polygons for all 8 Stores
    print(f"[*] Building 500m geodesic catchment polygons for all {len(STORES)} store locations...")
    catchment_features = []
    for store_id, store in STORES.items():
        poly = create_geodesic_circle_polygon(store["lat"], store["lng"], radius_m=store["catchment_radius_m"])
        catchment_features.append({
            "type": "Feature",
            "geometry": mapping(poly),
            "properties": {
                "store_id": store_id,
                "name": store["name"],
                "district": store["district"],
                "status": store["status"],
                "radius_m": store["catchment_radius_m"],
                "color": store["color"]
            }
        })

    with open(DATA_DIR / "catchment_polygons.geojson", "w") as f:
        json.dump({"type": "FeatureCollection", "features": catchment_features}, f, indent=2)
    print("[+] All 8 Catchment Polygons exported to data/catchment_polygons.geojson")

    # 2. Vectorized Spatial Joins across 500k records
    print("[*] Executing high-speed vectorized spatial join across 500,000+ points...")
    pings_lat = df_pings["latitude"].values
    pings_lng = df_pings["longitude"].values

    store_hits = {}
    for store_id, store in STORES.items():
        dists = vectorized_haversine(store["lat"], store["lng"], pings_lat, pings_lng)
        in_catchment = dists <= store["catchment_radius_m"]
        df_pings[f"in_{store_id}"] = in_catchment
        store_hits[store_id] = int(in_catchment.sum())
        print(f"  -> {store['name']} ({store['district']}): {store_hits[store_id]:,} pings captured.")

    # 3. Hourly Footfall Aggregation (00:00 - 23:00)
    print("[*] Calculating hourly unique patrons per store...")
    hourly_records = []
    for h in range(24):
        df_h = df_pings[df_pings["hour"] == h]
        row = {"hour": h, "time_label": f"{h:02d}:00"}
        for store_id in STORES.keys():
            store_pings = df_h[df_h[f"in_{store_id}"]]
            row[f"{store_id}_pings"] = len(store_pings)
            row[f"{store_id}_unique_visitors"] = store_pings["device_id"].nunique()
        hourly_records.append(row)

    df_hourly = pd.DataFrame(hourly_records)
    df_hourly.to_csv(DATA_DIR / "hourly_footfall.csv", index=False)

    # 4. Store Footfall Summary & Peak Hour Detection
    summary = {}
    for store_id, store in STORES.items():
        store_pings = df_pings[df_pings[f"in_{store_id}"]]
        unique_total = store_pings["device_id"].nunique()
        peak_idx = df_hourly[f"{store_id}_unique_visitors"].idxmax()
        peak_hour = int(df_hourly.loc[peak_idx, "hour"])
        peak_visitors = int(df_hourly.loc[peak_idx, f"{store_id}_unique_visitors"])

        morning_rush = int(df_pings[(df_pings["hour"].between(7, 9)) & (df_pings[f"in_{store_id}"])]['device_id'].nunique())
        lunch_rush = int(df_pings[(df_pings["hour"].between(11, 14)) & (df_pings[f"in_{store_id}"])]['device_id'].nunique())
        evening_rush = int(df_pings[(df_pings["hour"].between(17, 19)) & (df_pings[f"in_{store_id}"])]['device_id'].nunique())

        summary[store_id] = {
            "name": store["name"],
            "district": store["district"],
            "status": store["status"],
            "total_catchment_pings": store_hits[store_id],
            "total_unique_visitors": unique_total,
            "peak_hour": f"{peak_hour:02d}:00",
            "peak_hour_visitors": peak_visitors,
            "morning_rush_visitors": morning_rush,
            "lunch_rush_visitors": lunch_rush,
            "evening_rush_visitors": evening_rush
        }

    with open(DATA_DIR / "store_footfall_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    elapsed = time.time() - start_time
    rate = int(total_pings / max(elapsed, 0.001))
    print(f"[+] Spatial joins across {total_pings:,} points complete in {elapsed:.2f} seconds ({rate:,} pts/sec)!")
    print("=" * 80)
    return df_pings, df_hourly, summary

if __name__ == "__main__":
    run_spatial_joins_and_aggregations()
