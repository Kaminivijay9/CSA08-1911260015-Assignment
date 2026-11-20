"""Task A3 - Design the analysis and visualisation (SQL summary table and charts)."""
import sqlite3, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared"))
from load_db import build  # noqa: E402

OUT = Path(__file__).resolve().parent / "charts"
OUT.mkdir(exist_ok=True)

con = build()
# A3.2 summary table: daily min, max, mean and valid count per station (SQL GROUP BY)
summary = con.execute("""
    SELECT s.name, r.day, MIN(r.pm25), MAX(r.pm25), AVG(r.pm25), COUNT(r.pm25)
    FROM readings r JOIN stations s USING (station_id)
    GROUP BY s.name, r.day ORDER BY s.name, r.day""").fetchall()
print("daily summary rows:", len(summary))
print("first rows:", summary[:3])
con.execute("DROP TABLE IF EXISTS daily_summary")
con.execute("CREATE TABLE daily_summary (station TEXT, day TEXT, min_pm25 REAL, max_pm25 REAL, mean_pm25 REAL, valid_count INT)")
con.executemany("INSERT INTO daily_summary VALUES (?,?,?,?,?,?)", summary)
con.commit()

# A3.1 charts
monthly = con.execute("""SELECT substr(day,1,7), AVG(pm25) FROM readings
                         WHERE pm25 IS NOT NULL GROUP BY substr(day,1,7) ORDER BY 1""").fetchall()
plt.figure(figsize=(7, 4))
plt.plot([m for m, _ in monthly], [v for _, v in monthly], marker="o")
plt.title("Trend: mean PM2.5 per month (all stations)"); plt.ylabel("ug/m3"); plt.xticks(rotation=45)
plt.tight_layout(); plt.savefig(OUT / "trend_monthly.png", dpi=120); plt.close()

per_station = con.execute("""SELECT s.name, AVG(r.pm25) FROM readings r JOIN stations s USING (station_id)
                             WHERE r.pm25 IS NOT NULL GROUP BY s.name ORDER BY 2 DESC""").fetchall()
plt.figure(figsize=(8, 4))
plt.bar([n for n, _ in per_station], [v for _, v in per_station])
plt.title("Comparison of stations: mean PM2.5"); plt.ylabel("ug/m3"); plt.xticks(rotation=60, ha="right")
plt.tight_layout(); plt.savefig(OUT / "stations_bar.png", dpi=120); plt.close()

pairs = con.execute("SELECT temp_c, pm25 FROM readings WHERE pm25 IS NOT NULL AND temp_c IS NOT NULL "
                    "AND pm25 <= 999 ORDER BY RANDOM() LIMIT 3000").fetchall()
plt.figure(figsize=(6, 4))
plt.scatter([t for t, _ in pairs], [p for _, p in pairs], s=6, alpha=0.5)
plt.title("Temperature vs PM2.5 (3000 sampled readings)"); plt.xlabel("temp C"); plt.ylabel("ug/m3")
plt.tight_layout(); plt.savefig(OUT / "temp_vs_pm25.png", dpi=120); plt.close()

hourly = con.execute("""SELECT CAST(substr(ts,12,2) AS INT) h, AVG(pm25) FROM readings
                        WHERE pm25 IS NOT NULL GROUP BY h ORDER BY h""").fetchall()
worst = max(hourly, key=lambda x: x[1])
plt.figure(figsize=(7, 4))
plt.bar([h for h, _ in hourly], [v for _, v in hourly])
plt.title(f"Hours with the worst air (worst hour: {worst[0]:02d}:00)"); plt.xlabel("hour"); plt.ylabel("ug/m3")
plt.tight_layout(); plt.savefig(OUT / "hourly.png", dpi=120); plt.close()
print("worst hour:", worst)
print("charts saved to", OUT)
con.close()
