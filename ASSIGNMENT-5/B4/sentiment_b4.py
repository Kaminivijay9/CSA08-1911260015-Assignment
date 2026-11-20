"""Task B4 - Final Engineering Decision: the sentiment scorer (completed TODO) and tests.

B4.1 apply the scorer to 50 complaints and compare with hand labels.
B4.2 index on (station, day) and measure the effect on the slowest query.
B4.3 production decision is written in the report.
"""
import sqlite3, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared"))
from load_db import build  # noqa: E402

POSITIVE = ["good", "clean", "fast", "helpful", "improved"]
NEGATIVE = ["bad", "dirty", "slow", "rude", "smoke", "broken"]
NEGATORS = ["not", "never", "no"]

def score(text):
    """TODO 1 completed: +1 per positive word, -1 per negative word; a preceding negator flips it."""
    words = text.lower().replace(".", " ").replace(",", " ").replace("!", " ").split()
    total = 0
    for i, w in enumerate(words):
        v = 1 if w in POSITIVE else -1 if w in NEGATIVE else 0
        if i > 0 and words[i - 1] in NEGATORS:
            v = -v
        total += v
    return total

def label(text):
    s = score(text)
    return "positive" if s > 0 else "negative" if s < 0 else "neutral"

# B4.1: 50 complaints. Hand labels were written before the scorer was run.
COMPLAINTS = [
 ("The bus was fast and clean today.", "positive"), ("Staff were helpful at the ward.", "positive"),
 ("Roads are clean and the lights work well.", "positive"), ("Service improved a lot this month.", "positive"),
 ("The driver was polite and the bus was on time.", "positive"), ("Air is good near the park.", "positive"),
 ("Garbage collection is clean and fast now.", "positive"), ("Not bad, service improved.", "positive"),
 ("The clerk was helpful and quick.", "positive"), ("Water supply is good again.", "positive"),
 ("Thank you, the drain is clean now.", "positive"), ("Metro stations are clean and good.", "positive"),
 ("Complaint handled fast, very helpful team.", "positive"), ("The new road is smooth and fast.", "positive"),
 ("Park is clean, good for children.", "positive"), ("Traffic signals are working, good job.", "positive"),
 ("Bus stop is clean and the shelter is good.", "positive"), ("Officials were helpful on the phone.", "positive"),
 ("Street lights improved after my call.", "positive"), ("Lake is cleaner and the walkway is good.", "positive"),
 ("Smoke from the factory, air is bad.", "negative"), ("The staff were not helpful.", "negative"),
 ("Drains are dirty and smell bad.", "negative"), ("Bus driver was rude to passengers.", "negative"),
 ("The road is broken near the school.", "negative"), ("Traffic is slow every morning.", "negative"),
 ("Water is dirty and the tap is broken.", "negative"), ("Garbage has not been collected for weeks.", "negative"),
 ("The clerk was rude and never answered.", "negative"), ("Complaint is still not resolved, service is slow.", "negative"),
 ("The park toilets are dirty.", "negative"), ("Construction smoke all day, very bad.", "negative"),
 ("Street lights are broken since May.", "negative"), ("The ambulance was slow to arrive.", "negative"),
 ("Sewage overflow, the lane is dirty.", "negative"), ("Officials are not good at answering calls.", "negative"),
 ("Power cuts are bad and the transformer is broken.", "negative"), ("The bus was late and the seats are dirty.", "negative"),
 ("The lake smells bad, the water is dirty.", "negative"), ("Ration shop staff were rude.", "negative"),
 ("The pothole is still there, not fixed.", "negative"), ("Noise and smoke from the workshop, very bad.", "negative"),
 ("Our area has no water, the pipe is broken.", "negative"), ("The clinic was slow and the staff rude.", "negative"),
 ("Bus stop is dirty but the driver was helpful.", "neutral"), ("The road is fine, nothing to report.", "neutral"),
 ("Water came back after the repair.", "neutral"), ("Visited the office on Monday.", "neutral"),
 ("The bus was late but the bus was clean.", "neutral"), ("Paid the bill and got a receipt.", "neutral"),
]

def run_b41():
    agree = 0
    for text, truth in COMPLAINTS:
        pred = label(text)
        agree += pred == truth
        if pred != truth:
            print(f"  disagree: scorer={pred:8s} hand={truth:8s} | {text}")
    print(f"B4.1 agreement with hand labels: {agree}/{len(COMPLAINTS)} = {100*agree/len(COMPLAINTS):.0f}%")

def run_b42():
    con = build()
    slow = ("SELECT AVG(pm25) FROM readings WHERE station_id = 3 AND day = '2026-06-15'")
    def timed():
        t0 = time.perf_counter()
        for _ in range(200):
            con.execute(slow).fetchone()
        return (time.perf_counter() - t0) / 200 * 1000
    con.execute("DROP INDEX IF EXISTS idx_readings_station_day")
    before = timed()
    con.execute("CREATE INDEX idx_readings_station_day ON readings(station_id, day)")
    after = timed()
    print(f"B4.2 average query time without index {before:.3f} ms, with index {after:.3f} ms")
    print("query plan with index:", con.execute("EXPLAIN QUERY PLAN " + slow).fetchall())
    con.close()

if __name__ == "__main__":
    # Complete the Code check
    print(score("Roads are clean and the bus was fast."), label("Roads are clean and the bus was fast."))
    for c in ["Roads are clean and the bus was fast.", "Smoke from the factory, air is bad.",
              "The staff were not helpful.", "Not bad, service improved."]:
        print(f"positive | negative | neutral? -> {label(c):8s} | {c}")
    # Failure case: sarcasm is read literally
    print("sarcasm check:", label("Oh great, the air is so clean, real fast progress."), "(meant as negative)")
    print("adversarial check, double negative:", label("It is not never clean."))
    run_b41()
    run_b42()
