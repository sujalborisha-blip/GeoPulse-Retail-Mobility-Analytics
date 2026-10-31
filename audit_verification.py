import json
import sys
import pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

# 1. Hourly Footfall Verification
df_hourly = pd.read_csv('data/hourly_footfall.csv')
print("=== 1. HOURLY FOOTFALL AT HOUR 0 (12:00 AM) ===")
row0 = df_hourly[df_hourly['hour'] == 0].iloc[0]
print("Hour 0 Label:", row0['time_label'])
print("STORE_01 (Wall St Flagship) Visitors:", row0['STORE_01_unique_visitors'])
print("STORE_07 (Hudson Yards) Visitors:", row0['STORE_07_unique_visitors'])

# 2. Cannibalization Summary Verification
with open('data/cannibalization_results.json') as f:
    cann = json.load(f)
print("\n=== 2. CANNIBALIZATION FOR STORE_07 (HUDSON YARDS) ===")
s07 = cann['candidate_evaluations']['STORE_07']
print("Name:", s07['name'])
print("Overlap Pct:", s07['overlap_pct'], "%")
print("Net New Patrons:", s07['net_new_patrons'])
print("Verdict:", s07['verdict_badge'])

# 3. Check Hexagon Cell matching user's tooltip
with open('data/h3_hexagons_24h.json') as f:
    h3_data = json.load(f)
h0 = h3_data['0']['features']
print(f"\n=== 3. H3 HEXAGONS AT HOUR 0 ===")
print("Total Hexagons Active at 12:00 AM:", len(h0))
matches = [f['properties'] for f in h0 if f['properties']['pings_count'] == 106 and f['properties']['unique_devices'] == 104]
for m in matches:
    print("MATCH FOUND IN RAW H3 DATA:")
    print("  Hexagon Index:", m['h3_index'])
    print("  Footfall Pings:", m['pings_count'])
    print("  Unique Patrons:", m['unique_devices'])
    print("  Density Index:", f"{int(m['intensity']*100)}%")
    print("  Fill Color:", m['fill_color'])

# 4. Verify Raw Parquet File Source
df_raw = pd.read_parquet('data/raw_gps_pings.parquet')
print("\n=== 4. RAW PARQUET LAKEHOUSE VERIFICATION ===")
print("Total GPS Rows in Parquet:", len(df_raw))
print("Unique Devices in Parquet:", df_raw['device_id'].nunique())
hour_0_pings = len(df_raw[df_raw['hour'] == 0])
print("Total Pings at Hour 0 across Manhattan:", hour_0_pings)

print("\n=== 5. ALL 4 CANDIDATES SET THEORY AUDIT ===")
for cid, ev in cann['candidate_evaluations'].items():
    print(f"[{cid}] {ev['name']}:")
    print(f"   - Overlap Rate: {ev['overlap_pct']}%")
    print(f"   - Net New Patrons: +{ev['net_new_patrons']} devices")
    print(f"   - Morning Rush Intercept: {ev['morning_intercept_pct']}%")
    print(f"   - Revenue Dilution: ${ev['revenue_dilution_usd']}/day")
    print(f"   - System Verdict: {ev['verdict_badge']}")
