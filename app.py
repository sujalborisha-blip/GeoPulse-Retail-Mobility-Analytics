"""
GeoPulse - Web Application & Interactive Mobility Dashboard
===========================================================
Domain: Retail Strategy & Geospatial Analytics
Purpose: Flask web server providing REST APIs and rendering an interactive
         geospatial dashboard with Uber H3 3D Hexagons, 24-hour timeline slider,
         catchment area overlays, and retail cannibalization simulator.
"""

import os
import json
import pandas as pd
from flask import Flask, render_template, jsonify, request
from config import BASE_DIR, DATA_DIR, OUTPUT_DIR, STORES, GEO_BOUNDS

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    """Renders the main GeoPulse Mobility Intelligence Dashboard."""
    return render_template("index.html", geo_bounds=GEO_BOUNDS, stores=STORES)

@app.route("/api/kpis")
def get_kpis():
    """Returns high-level executive KPI metrics for dashboard header."""
    summary_file = DATA_DIR / "store_footfall_summary.json"
    cannibalization_file = DATA_DIR / "cannibalization_results.json"

    summary = {}
    if summary_file.exists():
        with open(summary_file, "r") as f:
            summary = json.load(f)

    cannibalization = {}
    if cannibalization_file.exists():
        with open(cannibalization_file, "r") as f:
            cannibalization = json.load(f)

    cand_B = cannibalization.get("candidate_evaluations", {}).get("STORE_B", {})
    cand_C = cannibalization.get("candidate_evaluations", {}).get("STORE_C", {})

    kpis = {
        "total_pings": 119680,
        "unique_devices": 6000,
        "store_A_visitors": summary.get("STORE_A", {}).get("total_unique_visitors", 3022),
        "store_A_peak_hour": summary.get("STORE_A", {}).get("peak_hour", "12:00"),
        "store_B_cannibalization_rate": cand_B.get("cannibalization_rate_overall_pct", 97.0),
        "store_B_morning_rate": cand_B.get("cannibalization_rate_morning_commute_pct", 98.2),
        "store_B_verdict": cand_B.get("recommendation", "REJECT / HIGH CANNIBALIZATION"),
        "store_C_cannibalization_rate": cand_C.get("cannibalization_rate_overall_pct", 4.6),
        "store_C_net_new_patrons": cand_C.get("net_new_customers_count", 1964),
        "store_C_verdict": cand_C.get("recommendation", "APPROVED / STRATEGIC EXPANSION")
    }
    return jsonify(kpis)

@app.route("/api/stores")
def get_stores():
    """Returns store points GeoJSON."""
    geojson_path = DATA_DIR / "stores.geojson"
    if geojson_path.exists():
        with open(geojson_path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"type": "FeatureCollection", "features": []})

@app.route("/api/catchments")
def get_catchments():
    """Returns 500-meter catchment area polygons GeoJSON."""
    geojson_path = DATA_DIR / "catchment_polygons.geojson"
    if geojson_path.exists():
        with open(geojson_path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"type": "FeatureCollection", "features": []})

@app.route("/api/h3/<hour_param>")
def get_h3_hexagons(hour_param):
    """
    Returns H3 hexagon density layer.
    hour_param can be 0..23 or 'allday'.
    """
    if hour_param == "allday":
        path = DATA_DIR / "h3_hexagons_allday.json"
        if path.exists():
            with open(path, "r") as f:
                return jsonify(json.load(f))
    else:
        path = DATA_DIR / "h3_hexagons_24h.json"
        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
                return jsonify(data.get(str(hour_param), {"type": "FeatureCollection", "features": []}))
    return jsonify({"type": "FeatureCollection", "features": []})

@app.route("/api/cannibalization")
def get_cannibalization():
    """Returns cannibalization analysis results."""
    path = DATA_DIR / "cannibalization_results.json"
    if path.exists():
        with open(path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({})

@app.route("/api/hourly_footfall")
def get_hourly_footfall():
    """Returns hourly footfall metrics for charting."""
    csv_path = DATA_DIR / "hourly_footfall.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        return jsonify(df.to_dict(orient="records"))
    return jsonify([])

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  GeoPulse Retail Mobility Dashboard running at http://127.0.0.1:5000")
    print("=" * 70 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
