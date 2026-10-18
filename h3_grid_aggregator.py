"""
GeoPulse - Week 4: Uber H3 Hexagonal Grid Aggregator
====================================================
Domain: Retail Strategy & Geospatial Analytics
Purpose: Spatial indexing of GPS coordinates into Uber H3 Hexagons (Resolution 9),
         computing 24-hour diurnal footfall density, and generating 3D hexagonal
         polygons with dynamic heat color ramps for map rendering.
"""

import time
import json
import h3
import numpy as np
import pandas as pd
from config import DATA_DIR, OUTPUT_DIR, SIMULATION_PARAMS

def get_density_color(intensity):
    """
    Returns an ultra-modern cyber-dark heatmap hex color
    based on normalized intensity [0.0 to 1.0].
    Gradient: Cool Indigo -> Cyan -> Emerald -> Electric Gold -> Crimson
    """
    if intensity < 0.15:
        return "#312e81"  # Deep Indigo (low background)
    elif intensity < 0.35:
        return "#06b6d4"  # Cyan (moderate transit)
    elif intensity < 0.60:
        return "#10b981"  # Emerald (steady footfall)
    elif intensity < 0.85:
        return "#f59e0b"  # Amber / Gold (high density)
    else:
        return "#ef4444"  # Crimson Red (extreme peak hotspot)

def generate_h3_hexagonal_density_layers(resolution=SIMULATION_PARAMS["h3_resolution"]):
    """
    Indexes raw pings into Uber H3 hexagons across 24 hourly time buckets.
    Exports GeoJSON structures for 24-hour slider animation.
    """
    print("=" * 70)
    print("  GEOPULSE H3 GRID AGGREGATOR (WEEK 4: 3D HEXAGONAL DENSITY)")
    print("=" * 70)
    start_time = time.time()

    # Load enriched GPS pings
    parquet_path = DATA_DIR / "raw_gps_pings.parquet"
    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
    else:
        df = pd.read_csv(DATA_DIR / "raw_gps_pings.csv")

    total_records = len(df)
    print(f"[*] Indexing {total_records:,} coordinates into Uber H3 Cells (Resolution {resolution})...")

    # Fast vectorized H3 cell assignment
    lats = df["latitude"].values
    lngs = df["longitude"].values
    h3_cells = [h3.latlng_to_cell(lat, lng, resolution) for lat, lng in zip(lats, lngs)]
    df["h3_cell"] = h3_cells

    unique_cells = df["h3_cell"].nunique()
    print(f"[+] Spatial clustering active: {unique_cells:,} unique H3 hexagonal blocks identified.")

    # 1. Compute 24-Hour Hourly H3 Aggregations
    print("[*] Building 24-hour animated time slider layers (Hours 00:00 to 23:00)...")
    hourly_h3_data = {}

    # Find max hourly ping count to normalize color ramp
    grouped_hourly = df.groupby(["hour", "h3_cell"]).agg(
        pings_count=("device_id", "count"),
        unique_devices=("device_id", "nunique")
    ).reset_index()

    max_pings_single_hour = grouped_hourly["pings_count"].max()
    print(f"[+] Peak hourly hexagon density: {max_pings_single_hour:,} pings/hour/cell.")

    for h in range(24):
        df_h = grouped_hourly[grouped_hourly["hour"] == h]
        features = []

        for _, row in df_h.iterrows():
            cell = row["h3_cell"]
            pings = int(row["pings_count"])
            devs = int(row["unique_devices"])
            intensity = min(1.0, pings / max(max_pings_single_hour * 0.75, 1))

            # Get boundary coordinates from H3 v4 API
            boundary = h3.cell_to_boundary(cell)
            # GeoJSON requires [lng, lat] and closed ring
            ring = [[round(pt[1], 6), round(pt[0], 6)] for pt in boundary]
            ring.append(ring[0])

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [ring]
                },
                "properties": {
                    "h3_index": cell,
                    "hour": h,
                    "pings_count": pings,
                    "unique_devices": devs,
                    "intensity": round(intensity, 3),
                    "fill_color": get_density_color(intensity),
                    "elevation_height": int(intensity * 120)  # For 3D extrusion effect
                }
            })

        hourly_h3_data[str(h)] = {
            "type": "FeatureCollection",
            "features": features
        }

    # Save 24-hour time slider data
    with open(DATA_DIR / "h3_hexagons_24h.json", "w") as f:
        json.dump(hourly_h3_data, f)
    print("[+] 24-hour animated GeoJSON layers exported to data/h3_hexagons_24h.json")

    # 2. Compute All-Day Cumulative H3 Aggregation
    print("[*] Generating all-day cumulative footfall density layer...")
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
        intensity = min(1.0, pings / max_pings_allday)

        boundary = h3.cell_to_boundary(cell)
        ring = [[round(pt[1], 6), round(pt[0], 6)] for pt in boundary]
        ring.append(ring[0])

        allday_features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [ring]
            },
            "properties": {
                "h3_index": cell,
                "total_pings": pings,
                "unique_devices": devs,
                "intensity": round(intensity, 3),
                "fill_color": get_density_color(intensity),
                "elevation_height": int(intensity * 180)
            }
        })

    allday_geojson = {
        "type": "FeatureCollection",
        "features": allday_features
    }
    with open(DATA_DIR / "h3_hexagons_allday.json", "w") as f:
        json.dump(allday_geojson, f)
    print("[+] Cumulative H3 Layer exported to data/h3_hexagons_allday.json")

    elapsed = time.time() - start_time
    print(f"[+] Uber H3 Aggregator completed in {elapsed:.3f} seconds!")
    print("=" * 70)
    return hourly_h3_data, allday_geojson

if __name__ == "__main__":
    generate_h3_hexagonal_density_layers()
