"""Read-only comparison of the item-3 runner summaries against every earlier PASS.

`qa/regression_runs/` is git-ignored, so the numbers are copied into the review record
(evidence/runner_compare_out.txt). Usage: python runner_compare.py <quick_stamp> <custom_stamp>
"""
import json
import pathlib
import sys

ROOT = pathlib.Path("qa/regression_runs")
quick_stamp, custom_stamp = sys.argv[1], sys.argv[2]


def load(path):
    try:
        return json.load(open(path / "summary.json", encoding="utf-8"))
    except Exception:
        return None


earlier = {}
for run in sorted(ROOT.glob("2026*")):
    if run.name.startswith("20261006"):
        continue
    summary = load(run)
    if not summary:
        continue
    for r in summary["results"]:
        if r["status"] == "PASS" and r.get("checks") is not None:
            earlier.setdefault(r["test"], []).append((run.name[:15], r["checks"], summary["git_head"][:8]))

for stamp in (quick_stamp, custom_stamp):
    s = load(ROOT / stamp)
    print("run %s: suite=%s head=%s %s %ds overall=%s guard=%s" % (
        stamp, s["suite"], s["git_head"][:8], "dirty" if s.get("git_dirty") else "clean", int(s["seconds"]),
        s["overall"], {k: len(v) for k, v in s["guard"].items()}))
    not_pass = [r["test"] for r in s["results"] if r["status"] != "PASS"]
    print("  tests: %d, not PASS: %s" % (len(s["results"]), not_pass or "none"))
    below = []
    for r in s["results"]:
        h = earlier.get(r["test"], [])
        if h and r.get("checks") is not None and r["checks"] < max(x[1] for x in h):
            below.append((r["test"], r["checks"], max(x[1] for x in h)))
    print("  below an earlier PASS maximum:", below or "none")
    print("  %-22s %7s   %-8s %s" % ("test", "checks", "earlier", "(max earlier PASS)"))
    for r in s["results"]:
        h = earlier.get(r["test"], [])
        mx = max((x[1] for x in h), default=None)
        mark = "" if mx is None or r["checks"] == mx else ("  +%d" % (r["checks"] - mx) if r["checks"] > mx else "  -%d" % (mx - r["checks"]))
        print("  %-22s %7s   %-8s%s" % (r["test"], r.get("checks"), mx, mark))
