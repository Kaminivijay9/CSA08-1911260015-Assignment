"""Task A1.1 - Inspect the source: describe the CSV and count every data-quality problem."""
import csv, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared"))
from generate import generate  # noqa: E402

path = ROOT / "data" / "stations.csv"
if not path.exists():
    generate(path)

problems, examples, rows, stations = Counter(), {}, 0, set()
with open(path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print("columns:", reader.fieldnames)
    for rec in reader:
        rows += 1
        stations.add(rec["station"])
        raw = rec["pm25"].strip()
        if raw == "":
            kind = "blank pm25"
        elif raw.upper() in ("NA", "N/A"):
            kind = "NA text"
        else:
            v = float(raw)
            kind = "negative" if v < 0 else "above 999" if v > 999 else None
        if kind:
            problems[kind] += 1
            examples.setdefault(kind, (rec["station"], rec["timestamp"], raw))
print("rows:", rows, "| stations:", len(stations))
for kind, n in problems.most_common():
    print(f"{kind:12s} {n:6d}  e.g. {examples[kind]}")
print("problem rate: %.2f%%" % (100 * sum(problems.values()) / rows))
