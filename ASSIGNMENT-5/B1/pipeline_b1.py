"""Task B1 - Implement and Validate the Cleaning Pipeline (completed TODO code).

Run:  python3 pipeline_b1.py
"""
import csv
import io
import sqlite3

RAW = """station,date,pm25
Adyar,2026-10-01,48
Adyar,2026-10-02,NA
Adyar,2026-10-03,
Guindy,2026-10-01,95
Guindy,2026-10-02,-5
Guindy,2026-10-03,121
"""


def load_clean(text):
    """Returns (station, date, pm25) tuples for valid, non-negative readings only."""
    rows = []
    for rec in csv.DictReader(io.StringIO(text)):   # TODO 1 completed
        raw = rec["pm25"].strip()
        if raw in ("", "NA"):          # empty or NA -> skip
            continue
        pm25 = float(raw)
        if pm25 < 0 or pm25 > 999:     # negative or impossible (A2 rule) -> skip
            continue
        rows.append((rec["station"].strip(), rec["date"].strip(), pm25))
    return rows


def min_max(values):
    """Scale each value to the range 0-1 using (v - min) / (max - min), rounded to 3 decimals."""
    lo, hi = min(values), max(values)   # TODO 2 completed
    if hi == lo:
        return [0.0 for _ in values]
    return [round((v - lo) / (hi - lo), 3) for v in values]


def store_and_query(rows):
    """B1.3: load cleaned rows with executemany and answer three questions with SQL."""
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE readings (station TEXT, day TEXT, pm25 REAL)")
    con.executemany("INSERT INTO readings VALUES (?, ?, ?)", rows)
    con.commit()
    avg_adyar_oct = con.execute(
        "SELECT AVG(pm25) FROM readings WHERE station = ? AND day LIKE '2026-10%'", ("Adyar",)
    ).fetchone()[0]
    valid_per_station = con.execute(
        "SELECT station, COUNT(*) FROM readings GROUP BY station ORDER BY station").fetchall()
    worst = con.execute(
        "SELECT station, day, pm25 FROM readings ORDER BY pm25 DESC LIMIT 1").fetchone()
    con.close()
    return avg_adyar_oct, valid_per_station, worst


def self_test():
    """A2 test row: a value above 999 must be dropped."""
    extra = RAW + "Adyar,2026-10-04,1500\n"
    assert all(p <= 999 for _, _, p in load_clean(extra)), "impossible value kept"
    assert len(load_clean(extra)) == len(load_clean(RAW)), "test row not dropped"
    print("self-test passed: impossible value 1500 is dropped")


if __name__ == "__main__":
    clean = load_clean(RAW)                          # Complete the Code step
    print(clean)
    print(min_max([pm for _, _, pm in clean]))
    self_test()
    avg, per_station, worst = store_and_query(clean)
    print("Q1 average Adyar PM2.5, October:", avg)
    print("Q2 valid readings per station:", per_station)
    print("Q3 highest reading:", worst)
