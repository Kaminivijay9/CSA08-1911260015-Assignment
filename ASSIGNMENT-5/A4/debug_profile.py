"""Task A4 - Plan debugging and profiling, with working examples.

A4.1 debugging: print, assert, logging and pdb (commented below).
A4.2 profiling: time.perf_counter() around a block, timeit, and cProfile.
"""
import cProfile, io, logging, pstats, time, timeit

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
log = logging.getLogger("clean")

def clean_value(raw):
    log.debug("raw=%r", raw)                 # logging instead of print: switch off with level=WARNING
    assert raw is not None, "raw value must not be None"
    s = raw.strip()
    if s in ("", "NA"):
        return None
    v = float(s)
    if v < 0:
        return None
    return v
# pdb: insert "import pdb; pdb.set_trace()" above the return, or run: python3 -m pdb debug_profile.py

def slow_sum_loop(values):
    total = 0.0
    for v in values:
        if v is not None:
            total += v
    return total

def fast_sum(values):
    return sum(v for v in values if v is not None)

if __name__ == "__main__":
    print("clean_value('48') =", clean_value("48"))
    print("clean_value('NA') =", clean_value("NA"))
    data = [float(i % 100) if i % 17 else None for i in range(200_000)]
    t0 = time.perf_counter(); slow_sum_loop(data); print(f"loop: {time.perf_counter() - t0:.4f}s")
    t0 = time.perf_counter(); fast_sum(data); print(f"generator: {time.perf_counter() - t0:.4f}s")
    print("timeit fast_sum x20:", round(timeit.timeit(lambda: fast_sum(data), number=20), 4), "s")
    prof = cProfile.Profile(); prof.enable()
    slow_sum_loop(data); fast_sum(data)
    prof.disable()
    buf = io.StringIO(); pstats.Stats(prof, stream=buf).sort_stats("cumulative").print_stats(5)
    print(buf.getvalue()[:900])
