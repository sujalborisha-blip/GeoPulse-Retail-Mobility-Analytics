"""
GeoPulse - Week 4: High-Contrast Uber H3 Grid Aggregator (500k+ Records)
========================================================================
Domain: Retail Strategy & Geospatial Analytics
Purpose: Spatial indexing of 500k+ GPS points into Uber H3 Hexagons (Res-9),
         with non-linear square-root heat normalization for vibrant contrast,
         generating 24-hour diurnal animated layers and cumulative citywide density.
"""

import time
import json
import math
import h3
import pandas as pd
from config import DATA_DIR, SIMULATION_PARAMS

def get_density_color(intensity):
    """
    Vibrant high-contrast cyber heatmap ramp:
    Neon Blue -> Electric Cyan -> Emerald Green -> Amber Gold -> Radiant Crimson
    """
    if intensity < 0.15:
        return "#1e3a8a"  # Royal Navy Blue (Low baseline)
    elif intensity < 0.35:
        return "#0284c7"  # Sky Blue
    elif intensity < 0.55:
        return "#06b6d4"  # Electric Cyan
    elif intensity < 0.72:
        return "#10b981"  # Emerald Green
    elif intensity < 0.88:
        return "#f59e0b"  # Bright Amber / Gold
    else:
        return "#ef4444"  # Crimson Hotspot

def generate_h3_hexagonal_density_layers(resolution=SIMULATION_PARAMS["h3_resolution"]):
    print("=" * 80)
    print(f"  GEOPULSE UBER H3 AGGREGATOR (VIBRANT CONTRAST RES-{resolution} GRID)")
    print("=" * 80)
    start_time = time.time()

    parquet_path = DATA_DIR / "raw_gps_pings.parquet"
    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
    else:
        df = pd.read_csv(DATA_DIR / "raw_gps_pings.csv")

    total_records = len(df)
    print(f"[*] Indexing {total_records:,} coordinates into Uber H3 Hexagonal Grid...")

    lats = df["latitude"].values
    lngs = df["longitude"].values
    df["h3_cell"] = [h3.latlng_to_cell(lat, lng, resolution) for lat, lng in zip(lats, lngs)]

    unique_cells = df["h3_cell"].nunique()
    print(f"[+] Active H3 Hexagonal Blocks: {unique_cells:,} unique cells.")

    # 1. 24-Hour Hourly Aggregation
    grouped_hourly = df.groupby(["hour", "h3_cell"]).agg(
        pings_count=("device_id", "count"),
        unique_devices=("device_id", "nunique")
    ).reset_index()

    max_pings_hourly = grouped_hourly["pings_count"].max()
    hourly_h3_data = {}

    for h in range(24):
        df_h = grouped_hourly[grouped_hourly["hour"] == h]
        features = []
        h_max = max(df_h["pings_count"].max(), 1) if len(df_h) > 0 else 1

        for _, row in df_h.iterrows():
            cell = row["h3_cell"]
            pings = int(row["pings_count"])
            devs = int(row["unique_devices"])

            # Square-root normalization brings out contrast across all commercial districts
            norm_ratio = pings / h_max
            intensity = min(1.0, math.sqrt(norm_ratio))

            boundary = h3.cell_to_boundary(cell)
            ring = [[round(pt[1], 6), round(pt[0], 6)] for pt in boundary]
            ring.append(ring[0])

            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [ring]},
                "properties": {
                    "h3_index": cell,
                    "hour": h,
                    "pings_count": pings,
                    "unique_devices": devs,
                    "intensity": round(intensity, 3),
                    "fill_color": get_density_color(intensity)
                }
            })
        hourly_h3_data[str(h)] = {"type": "FeatureCollection", "features": features}

    with open(DATA_DIR / "h3_hexagons_24h.json", "w") as f:
        json.dump(hourly_h3_data, f)

    # 2. All-Day Cumulative Layer
    allday_grouped = df.groupby("h3_cell").agg(
        total_pings=("device_id", "count"),
        unique_devices=("device_id", "nunique")
    ).reset_index()

    max_pings_allday = allday_grouped["total_pings"].max()
    allday_features = []
    for _, row in allday_grouped.iterrows():
        cell = row["h3_cell"]
        pings = int(row["total_pings"])
        devs = int(row["unique_devices"])

        norm_ratio = pings / max_pings_allday
        intensity = min(1.0, math.sqrt(norm_ratio))

        boundary = h3.cell_to_boundary(cell)
        ring = [[round(pt[1], 6), round(pt[0], 6)] for pt in boundary]
        ring.append(ring[0])

        allday_features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {
                "h3_index": cell,
                "total_pings": pings,
                "unique_devices": devs,
                "intensity": round(intensity, 3),
                "fill_color": get_density_color(intensity)
            }
        })

    with open(DATA_DIR / "h3_hexagons_allday.json", "w") as f:
        json.dump({"type": "FeatureCollection", "features": allday_features}, f)

    elapsed = time.time() - start_time
    print(f"[+] High-contrast H3 grid generated in {elapsed:.2f} seconds!")
    print("=" * 80)
    return hourly_h3_data, allday_features

if __name__ == "__main__":
    generate_h3_hexagonal_density_layers()
