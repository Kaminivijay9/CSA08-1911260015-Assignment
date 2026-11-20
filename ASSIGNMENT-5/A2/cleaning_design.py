"""Task A2 - Cleaning rules, normalisation and the alternative-concept comparison.

A2.1 cleaning rules  A2.2 min-max and z-score normalisation  A2.3 standard formats.
"""
import sys, time, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared"))
from cleaning_rules import parse_pm25  # noqa: E402
from load_db import build              # noqa: E402

def fill_forward(values):
    out, last = [], None
    for v in values:
        last = v if v is not None else last
        out.append(last)
    return out

def fill_median(values):
    med = statistics.median(v for v in values if v is not None)
    return [med if v is None else v for v in values]

def min_max(values):
    lo, hi = min(values), max(values)
    return [(v - lo) / (hi - lo) for v in values]

def z_score(values):
    mu, sd = statistics.fmean(values), statistics.pstdev(values)
    return [(v - mu) / sd for v in values]

def daily_mean(values):
    return statistics.fmean(v for v in values if v is not None)

if __name__ == "__main__":
    con = build()
    raw = [r[0] for r in con.execute(
        "SELECT pm25 FROM readings WHERE station_id = 1 ORDER BY ts LIMIT 24")]
    # Use raw CSV text values for the illustration of missing data
    print("valid values in first 24 hours (station 1):", sum(v is not None for v in raw), "of", len(raw))
    print("min-max first 5:", [round(x, 3) for x in min_max([v for v in raw if v is not None])[:5]])
    print("z-score first 5:", [round(x, 3) for x in z_score([v for v in raw if v is not None])[:5]])
    print("mean after fill-forward:", round(statistics.fmean(fill_forward(raw)[i] for i in range(len(raw)) if fill_forward(raw)[i] is not None), 3))
    print("mean after fill-median:", round(statistics.fmean(fill_median(raw)), 3))

    # Alternative concept: dropping vs filling, time and space on the full table
    all_vals = [r[0] for r in con.execute("SELECT pm25 FROM readings ORDER BY station_id, ts")]
    t0 = time.perf_counter(); kept = [v for v in all_vals if v is not None]; t_drop = time.perf_counter() - t0
    t0 = time.perf_counter(); filled = fill_forward(all_vals); t_ffill = time.perf_counter() - t0
    t0 = time.perf_counter(); med = fill_median(all_vals); t_med = time.perf_counter() - t0
    print(f"drop: {len(kept)} values kept in {t_drop:.4f}s (O(n))")
    print(f"fill-forward: {len(filled)} values in {t_ffill:.4f}s (O(n), one pass)")
    print(f"fill-median: {len(med)} values in {t_med:.4f}s (O(n log n) because of the sort)")
    con.close()
