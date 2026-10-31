"""
GeoPulse - Hyper-Local Retail Mobility & Store Cannibalization Analytics
========================================================================
Interactive Streamlit Application & Cloud Deployment Wrapper
Lead Analyst: Sujal Borisa | Infotact Solutions Virtual Internship Project 2
"""

import os
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Streamlit Page Config
st.set_page_config(
    page_title="GeoPulse | Retail Mobility Intelligence",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"

# Custom Styling
st.markdown("""
<style>
    /* Clean Dark Theme Background */
    .stApp {
        background-color: #050811;
        color: #f1f5f9;
    }
    header[data-testid="stHeader"] {
        background-color: rgba(5, 8, 17, 0.9);
    }
    section[data-testid="stSidebar"] {
        background-color: #090e1a;
        border-right: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #0f172a;
        border-radius: 8px;
        color: #94a3b8;
        padding-top: 8px;
        padding-bottom: 8px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all_datasets():
    with open(DATA_DIR / "stores.geojson", "r", encoding="utf-8") as f:
        stores = json.load(f)
    with open(DATA_DIR / "catchment_polygons.geojson", "r", encoding="utf-8") as f:
        catch = json.load(f)
    with open(DATA_DIR / "cannibalization_results.json", "r", encoding="utf-8") as f:
        cann = json.load(f)
    with open(DATA_DIR / "h3_hexagons_allday.json", "r", encoding="utf-8") as f:
        h3_all = json.load(f)
    with open(DATA_DIR / "h3_hexagons_24h.json", "r", encoding="utf-8") as f:
        h3_24 = json.load(f)
    df_hourly = pd.read_csv(DATA_DIR / "hourly_footfall.csv")
    hourly_records = df_hourly.to_dict(orient="records")

    kpis = {
        "total_pings": 537450,
        "unique_devices": 25000,
        "total_stores": len(stores["features"]),
        "store_02_cannibalization": 99.8,
        "store_05_net_new": 4970,
        "store_07_net_new": 1912
    }

    # Build client-side embedded bundle
    embedded = {
        "/api/kpis": kpis,
        "/api/stores": stores,
        "/api/catchments": catch,
        "/api/cannibalization": cann,
        "/api/hourly_footfall": hourly_records,
        "/api/h3/allday": h3_all
    }
    for h in range(24):
        embedded[f"/api/h3/{h}"] = h3_24.get(str(h), {"type": "FeatureCollection", "features": []})

    return embedded, cann, df_hourly

embedded_data, cannibalization_data, df_hourly = load_all_datasets()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0;">
        <h2 style="margin: 0; color: #38bdf8; font-weight: 900; letter-spacing: 1px;">GeoPulse</h2>
        <p style="margin: 0; color: #94a3b8; font-size: 12px;">Hyper-Local Retail Mobility Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    selected_view = st.radio(
        "Navigation",
        [
            "🗺️ Live Cyber-GIS Dashboard",
            "📊 Cannibalization Matrix (8x8)",
            "📈 Diurnal Footfall Explorer",
            "📑 Infotact Project Submission"
        ]
    )

    st.divider()
    
    st.markdown("### ⚡ Lakehouse Telemetry")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total GPS Pings", "537k+")
        st.metric("Active Hubs", "8 Stores")
    with col2:
        st.metric("Unique Devices", "25,000")
        st.metric("Catchment Radius", "500m")

    st.divider()
    st.markdown("""
    **Lead Analyst:** Sujal  
    **Program:** Infotact Solutions Virtual Internship (Project 2)  
    **Stack:** Python, Uber H3, Apache Parquet, Leaflet, Streamlit
    """)

# MAIN VIEW SWITCHER
if selected_view == "🗺️ Live Cyber-GIS Dashboard":
    # Read index.html and inject EMBEDDED_DATA directly into the <head>
    with open(TEMPLATES_DIR / "index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    injection = f"""
    <script>
        window.EMBEDDED_DATA = {json.dumps(embedded_data)};
    </script>
    """
    html_content = html_content.replace("<head>", f"<head>{injection}")

    # Render dashboard
    components.html(html_content, height=890, scrolling=False)

elif selected_view == "📊 Cannibalization Matrix (8x8)":
    st.markdown("## 📊 8x8 Pairwise Store Cannibalization Matrix")
    st.markdown(r"Set-Theory Overlap ($A \cap B$) measured across 25,000 unique device trajectories in 500m catchments.")

    matrix_data = cannibalization_data.get("overlap_matrix", {})
    df_matrix = pd.DataFrame(matrix_data)
    
    st.dataframe(
        df_matrix.style.background_gradient(cmap="Blues", axis=None).format("{:.1f}%"),
        use_container_width=True
    )

    st.markdown("### 🎯 Expansion Candidate Decision Summary")
    evals = cannibalization_data.get("candidate_evaluations", {})
    eval_list = []
    for cid, ev in evals.items():
        eval_list.append({
            "Candidate Site": f"{ev['name']} ({cid})",
            "District": ev["district"],
            "Overlap Rate": f"{ev['overlap_pct']}%",
            "Morning Intercept": f"{ev['morning_intercept_pct']}%",
            "Net-New Devices Acquired": f"+{ev['net_new_patrons']:,}",
            "Daily Revenue Dilution": f"-${ev['revenue_dilution_usd']:,.2f}/day",
            "Verdict": ev["verdict_badge"]
        })
    df_eval = pd.DataFrame(eval_list)
    st.table(df_eval)

elif selected_view == "📈 Diurnal Footfall Explorer":
    st.markdown("## 📈 24-Hour Diurnal Footfall Across Manhattan Retail Network")
    st.markdown("Hourly unique device visits derived from the Apache Parquet lakehouse.")
    
    visitor_cols = [c for c in df_hourly.columns if "unique_visitors" in c]
    st.line_chart(df_hourly.set_index("time_label")[visitor_cols])

    st.markdown("### 📋 Hourly Dataset Preview")
    st.dataframe(df_hourly, use_container_width=True)

elif selected_view == "📑 Infotact Project Submission":
    st.markdown("## 📑 Infotact Solutions Project 2 Submission Report")
    report_path = BASE_DIR / "WEEK_WISE_SUBMISSION_REPORTS.md"
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.info("Submission report file available in repository.")
