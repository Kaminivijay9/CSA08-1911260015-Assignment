"""Task A5 - AI application for citizen complaints.

A5.1 lexicon sentiment scorer with negation, plus an extractive summariser.
A5.2 rule-based chatbot that answers from the SQLite database.
"""
import re, sqlite3, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared"))

POSITIVE = {"good", "clean", "fast", "helpful", "improved"}
NEGATIVE = {"bad", "dirty", "slow", "rude", "smoke", "broken"}
NEGATORS = {"not", "never", "no"}
STOP = {"the", "a", "an", "is", "was", "were", "and", "of", "from", "in", "on", "it", "to", "are"}

def score(text):
    words = re.sub(r"[^a-z\s]", " ", text.lower()).split()
    total, prev = 0, ""
    for w in words:
        v = 1 if w in POSITIVE else -1 if w in NEGATIVE else 0
        if prev in NEGATORS:
            v = -v
        total += v
        prev = w
    return total

def label(text):
    s = score(text)
    return "positive" if s > 0 else "negative" if s < 0 else "neutral"

def summarise(text, k=2):
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    freq = Counter(w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP)
    rank = sorted(sentences, key=lambda s: -sum(freq[w] for w in re.findall(r"[a-z]+", s.lower())))
    return [s for s in sentences if s in rank[:k]]  # keep original order

def answer(question, con):
    """Rule-based chatbot: matches keywords and queries the database."""
    q = question.lower()
    m = re.search(r"pm2\.?5", q)
    stations = [n for (n,) in con.execute("SELECT name FROM stations")]
    station = next((s for s in stations if s.lower() in q), None)
    if station and m and "average" in q or station and m and "mean" in q:
        v = con.execute("""SELECT AVG(r.pm25) FROM readings r JOIN stations s USING(station_id)
                           WHERE s.name = ? AND r.pm25 IS NOT NULL""", (station,)).fetchone()[0]
        return f"The average PM2.5 in {station} is {v:.1f} ug/m3 (all valid readings)."
    if station and "worst" in q or "highest" in q and station:
        return "Limitations: this bot only answers average-PM2.5 questions by station name."
    return "Sorry, I can only answer average PM2.5 questions for a named station."

if __name__ == "__main__":
    tests = ["Roads are clean and the bus was fast.", "Smoke from the factory, air is bad.",
             "The staff were not helpful.", "Not bad, service improved."]
    for t in tests:
        print(f"{label(t):8s} score={score(t):2d} | {t}")
    print("summary:", summarise(" ".join(tests)))
    from load_db import build
    con = build()
    print("bot:", answer("What is the average PM2.5 in Adyar?", con))
    print("bot:", answer("Will it rain tomorrow?", con))
    con.close()
