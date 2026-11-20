"""Task B3 - Loops vs Libraries vs SQL: correctness, data size, profile and trade-off.

Daily mean PM2.5 per station, three ways: csv-module loops, pandas groupby, SQL GROUP BY.
"""
import csv, cProfile, io, pstats, sqlite3, sys, time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared"))
from generate import generate            # noqa: E402
from cleaning_rules import parse_pm25    # noqa: E402
import pandas as pd

def plain_loops(path):
    """Running sum and count in a dict: one pass, O(n) time, O(stations x days) memory."""
    sums, counts = defaultdict(float), defaultdict(int)
    with open(path, newline="", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            v = parse_pm25(rec["pm25"])
            if v is None:
                continue
            key = (rec["station"], rec["timestamp"][:10])
            sums[key] += v
            counts[key] += 1
    return {k: sums[k] / counts[k] for k in sums}

def pandas_groupby(path):
    df = pd.read_csv(path, dtype={"pm25": str})
    df["pm25"] = df["pm25"].fillna("").map(parse_pm25)
    df["day"] = df["timestamp"].str[:10]
    return df.dropna(subset=["pm25"]).groupby(["station", "day"])["pm25"].mean().to_dict()

def sql_group_by(path):
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE r (station TEXT, day TEXT, pm25 REAL)")
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            rows.append((rec["station"], rec["timestamp"][:10], parse_pm25(rec["pm25"])))
    con.executemany("INSERT INTO r VALUES (?,?,?)", rows)
    out = {(s, d): m for s, d, m in con.execute(
        "SELECT station, day, AVG(pm25) FROM r WHERE pm25 IS NOT NULL GROUP BY station, day")}
    con.close()
    return out

def same(a, b):
    return a.keys() == b.keys() and all(abs(a[k] - b[k]) < 1e-6 for k in a)

if __name__ == "__main__":
    # B3.1 correctness on the small dataset (1 station, first 3 days)
    small = ROOT / "data" / "small.csv"
    rows = [l for l in open(ROOT / "data" / "stations.csv", encoding="utf-8")][:1 + 72]
    small.write_text("".join(rows), encoding="utf-8")
    r1, r2, r3 = plain_loops(small), pandas_groupby(small), sql_group_by(small)
    print("B3.1 correctness: loops==pandas", same(r1, r2), "| loops==SQL", same(r1, r3), "| groups:", len(r1))

    # B3.2 increase data size: 1, 12 and 120 stations for a year (about 8,760 readings each)
    print(f"{'stations':>8} {'rows':>10} {'loops s':>9} {'pandas s':>9} {'SQL s':>9}")
    for n in (1, 12, 120):
        path = ROOT / "data" / f"stations_{n}.csv"
        if not path.exists():
            generate(path, n_stations=n)
        times = {}
        for name, fn in (("loops", plain_loops), ("pandas", pandas_groupby), ("SQL", sql_group_by)):
            t0 = time.perf_counter(); fn(path); times[name] = time.perf_counter() - t0
        rows_n = sum(1 for _ in open(path, encoding="utf-8")) - 1
        print(f"{n:>8} {rows_n:>10} {times['loops']:>9.2f} {times['pandas']:>9.2f} {times['SQL']:>9.2f}")

    # B3.3 profile the plain-Python version on 12 stations
    prof = cProfile.Profile(); prof.enable()
    plain_loops(ROOT / "data" / "stations_12.csv")
    prof.disable()
    buf = io.StringIO(); pstats.Stats(prof, stream=buf).sort_stats("tottime").print_stats(6)
    print(buf.getvalue()[:1200])
