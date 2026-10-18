# GeoPulse: Week-Wise Infotact Portal Submissions & Viva Guide

Use this document to copy-paste directly into the Infotact submission portal for Week 1, Week 2, Week 3, Week 4 reviews, and to ace your Viva / Final Interview.

---

## 📝 WEEK 1: Data Synthesis & Geospatial Lakehouse Ingestion

### Portal Submission Text (Copy & Paste):
```markdown
During Week 1 of Project 2 (GeoPulse), I developed and executed the high-throughput synthetic mobility data pipeline:

1. Mobility Simulation Engine:
   - Built 'mobility_simulator.py' using vectorized NumPy algorithms to generate 119,680 realistic GPS pings across 6,000 unique anonymized mobile devices (DeviceID, Latitude, Longitude, Timestamp, Accuracy, Speed, Activity).
   - Modeled distinct urban movement personas: Wall Street financial commuters, Flatiron creative/tech workers, SoHo retail shoppers, and general urban transit.
   - Incorporated realistic diurnal commute dynamics with morning rush hour (08:00 - 09:30 AM), lunch and coffee peaks (12:00 - 02:00 PM), and evening transit dispersals (05:00 - 07:30 PM).

2. Lakehouse Storage & Geospatial Formats:
   - Exported the dataset into Apache Parquet format with Snappy compression for optimized columnar query performance.
   - Structured store entities and initial commercial zoning boundaries into GeoJSON format.
   - Validated coordinate precision within the defined bounding box ([40.7000, 40.7550] Lat, [-74.0180, -73.9720] Lng).
```

---

## 📝 WEEK 2: Catchment Area Modeling & Vectorized Spatial Joins

### Portal Submission Text (Copy & Paste):
```markdown
During Week 2, I implemented the core spatial transformation and catchment area modeling engine:

1. 500-Meter Catchment Area Polygons:
   - Implemented geodesic circular buffer calculations using spherical trigonometry in 'spatial_engine.py' to generate exact 500-meter catchment area polygons around Store A (Wall St Flagship), Candidate Store B (Fulton Transit), and Candidate Store C (Flatiron).
   - Exported catchment geometries into 'data/catchment_polygons.geojson'.

2. Vectorized Spatial Joins & Intersections:
   - Developed a vectorized Haversine distance matrix algorithm capable of calculating point-in-polygon / distance intersections across 100k+ records in 1.16 seconds (~103,000 points/sec).
   - Successfully captured 41,792 pings inside Store A's catchment, 41,731 pings in Store B's catchment, and 20,052 pings in Store C's catchment.

3. Hourly ELT Aggregation & Mid-Project Audit:
   - Aggregated total pings and unique devices per store per hour (00:00 to 23:00) into 'data/hourly_footfall.csv'.
   - Generated the Mid-Project Spatial Audit Report ('mid_project_spatial_audit.json') validating sub-second execution, optimal memory footprint (<200MB), and confirmed morning/lunch rush traffic spike integrity.
```

---

## 📝 WEEK 3: Retail Cannibalization Analytics & Commuter Interception

### Portal Submission Text (Copy & Paste):
```markdown
During Week 3, I developed the Retail Cannibalization Analytics Engine to evaluate store expansion viability:

1. Unique Customer Trajectory Tracking:
   - Built 'cannibalization_analyzer.py' to extract unique Device ID sets for each store catchment area across the 24-hour cycle.
   - Calculated mathematical set intersections: |Devices_A ∩ Devices_B| vs |Devices_A ∩ Devices_C|.

2. Commuter Interception & Cannibalization Rates:
   - Proved that Candidate Store B exhibits a 97.0% overall customer overlap and intercepts 98.2% of Store A's morning commuter traffic (07:00 - 09:00 AM).
   - Confirmed that Candidate Store C demonstrates 95.4% geographic isolation with only 4.6% overlap with Store A.

3. Financial Impact Modeling & Strategic Decisions:
   - Modeled revenue dilution: Candidate Store B cannibalizes an estimated $3,293.00/day from Store A's high-margin morning sales while acquiring only 89 net-new devices.
   - Recommended the Investment Committee REJECT Candidate Store B lease and APPROVE Candidate Store C, which delivers +1,964 purely net-new unique patrons.
```

---

## 📝 WEEK 4: Uber H3 Hexagonal Density, 24-Hour Timeline Slider & Automation

### Portal Submission Text (Copy & Paste):
```markdown
During Week 4, I completed the interactive mobility dashboard and automated pipeline orchestration:

1. Uber H3 Hexagonal Grid Aggregation:
   - Utilized Uber H3 spatial indexing (Resolution 9, ~100m edge length) in 'h3_grid_aggregator.py' to cluster GPS coordinates into 257 distinct hexagonal cells.
   - Generated 24 individual hourly GeoJSON layers and an all-day cumulative density layer with dynamic 5-tier heat color gradients.

2. Interactive 24-Hour Diurnal Web Dashboard:
   - Developed a full-stack Flask application ('app.py') rendering a dark-mode CartoDB DarkMatter map interface.
   - Integrated an interactive 24-hour timeline scrub slider with Play/Pause animation, allowing users to watch diurnal footfall waves flow through the city in real time.
   - Added interactive layer toggles (H3 Grid, Catchments, Stores), a real-time Cannibalization Diagnostic Simulator, and a multi-line hourly footfall Chart.js visualization.

3. End-to-End Pipeline Automation:
   - Orchestrated the entire workflow via 'pipeline_runner.py', automating data synthesis, spatial joins, cannibalization math, and H3 aggregation into a single automated command with execution telemetry.
```

---

## 🎓 VIVA & FINAL REVIEW QUESTIONS & ANSWERS

### Q1: What is the core business problem that GeoPulse solves?
* **Answer:** "Standard retail expansion relies on static census data, which ignores how people actually move throughout the day. This leads to store cannibalization—where a new store accidentally steals customers from an existing location. GeoPulse analyzes dynamic mobile GPS pings, 500-meter catchment areas, and Uber H3 hexagonal grids to quantify customer overlap and recommend whether a retail lease should be approved or rejected."

### Q2: Why did you use Uber H3 Hexagons instead of regular square grids?
* **Answer:** "Uber H3 is a discrete global hexagonal hierarchical spatial index. Hexagons are superior to square grids because every neighbor of a hexagon is equidistant (sharing equal contact length), eliminating corner-direction distortion. This makes distance-based spatial density and movement trajectory calculations significantly more accurate for footfall modeling."

### Q3: What is 'Store Cannibalization' and how did you measure it mathematically?
* **Answer:** "Cannibalization occurs when a new candidate store captures customers who were already visiting your existing store. I measured this using Set Theory on unique device IDs across 24 hours:
  $$\text{Cannibalization Rate} = \frac{|\text{Devices in Store A} \cap \text{Devices in Candidate Store}|}{|\text{Devices in Store A}|} \times 100$$
  Candidate B showed a 98.2% morning commuter interception rate because it was placed 400m upstream on the same commuter path, whereas Candidate C had only 4.6% overlap and captured 1,964 net-new customers."

### Q4: How did you ensure fast spatial processing across 120,000+ coordinates without crashing the system?
* **Answer:** "Instead of running nested Python loops or heavy geometric buffer overlaps that consume gigabytes of memory, I used vectorized Haversine distance computations via NumPy and indexed coordinates into Uber H3 cells. This allowed the engine to process 120,000 points in just 1.16 seconds (~103,000 points/second) with a memory footprint under 200MB."
