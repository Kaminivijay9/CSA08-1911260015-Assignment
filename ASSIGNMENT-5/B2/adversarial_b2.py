"""Task B2 - Engineer Adversarial Data (completed TODO code + adversarial inputs).

Run:  python3 adversarial_b2.py
"""
import csv
import io
import os
import sqlite3
import tempfile

readings = [("Adyar", "2026-10-01", 48.0), ("Guindy", "2026-10-01", 95.0),
            ("Guindy", "2026-10-03", 121.0), ("Adyar", "2026-10-04", 60.0)]

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE aq (station TEXT, day TEXT, pm25 REAL)")
con.executemany("INSERT INTO aq VALUES (?, ?, ?)", readings)   # TODO 1: one executemany call
con.commit()


def station_average(name):
    """TODO 2: parameterised SELECT - the ? placeholder keeps the input as data, not SQL."""
    row = con.execute("SELECT AVG(pm25) FROM aq WHERE station = ?", (name,)).fetchone()
    return row[0]


def station_average_concat(name):
    """Unsafe version built with +, used only to show the quote-character failure."""
    return con.execute("SELECT AVG(pm25) FROM aq WHERE station = '" + name + "'").fetchone()[0]


if __name__ == "__main__":
    print(station_average("Adyar"), station_average("Guindy"))          # expected: 54.0 108.0
    print(station_average("Adyar' OR '1'='1"))                          # expected: None
    try:
        con.execute("INSERT INTO aq VALUES (?, ?, ?)", ("T'Nagar", "2026-10-01", 70.0))
        print("T'Nagar (placeholder):", station_average("T'Nagar"))
        print("T'Nagar (concatenated):", station_average_concat("T'Nagar"))
    except sqlite3.OperationalError as e:
        print("concatenated query failed:", e)

    # Adversarial files: missing column, wrong delimiter, wrong encoding, empty file
    cases = {
        "missing_column.csv": ("utf-8", "station,date\nAdyar,2026-10-01\n"),
        "wrong_delimiter.csv": ("utf-8", "station;date;pm25\nAdyar;2026-10-01;48\n"),
        "utf16_encoding.csv": ("utf-16", "station,date,pm25\nAdyar,2026-10-01,48\n"),
        "empty.csv": ("utf-8", ""),
    }
    folder = tempfile.mkdtemp(prefix="b2_")
    for name, (enc, text) in cases.items():
        path = os.path.join(folder, name)
        with open(path, "w", encoding=enc) as f:
            f.write(text)
        try:
            with open(path, encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                total = sum(float(r["pm25"]) for r in rows)
            print(f"{name}: read {len(rows)} rows, total {total}")
        except (KeyError, UnicodeDecodeError, ValueError) as e:
            print(f"{name}: rejected with {type(e).__name__}: {e}")
        else:
            if not rows:
                print(f"{name}: accepted silently with 0 rows (needs an explicit check)")
    con.close()
