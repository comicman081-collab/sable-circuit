"""Claude review helper (item 3): read only. Lines up the whole-suite runner summary (88 tests) against my quick run and my
four-test run, so a dropped or changed check count shows up, then prints the ten playthroughs and the failures.
usage (project root): python -B qa/expansion_item3_review_20261006/followup/tools/compare_full_vs_quick.py
Reads only files in followup/runs/ (the regression_runs folders are git-ignored); writes nothing."""
import json
import sys
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1] / "runs"


def load(name):
    return json.loads((RUNS / name).read_text(encoding="utf-8"))


def by_test(summary):
    return {r["test"]: r for r in summary["results"]}


def main():
    full, quick, only4 = load("full_ccfaa96e_summary.json"), load("quick_0a14d5b6_summary.json"), load("only4_0a14d5b6_summary.json")
    rerun = load("rerun_full_op_08_ccfaa96e_summary.json")
    f, q, o = by_test(full), by_test(quick), by_test(only4)
    passed = [t for t, r in f.items() if r["status"] == "PASS"]
    failed = [t for t, r in f.items() if r["status"] != "PASS"]
    print(f"full run: suite={full['suite']} tests={len(f)} PASS={len(passed)} not-PASS={failed} overall={full['overall']}")
    print(f"  git_head={full['git_head'][:8]} git_dirty={full['git_dirty']} seconds={full['seconds']} guard={full['guard']}")
    print(f"rerun   : suite={rerun['suite']} tests={[r['test'] + ' ' + r['status'] for r in rerun['results']]} "
          f"git_head={rerun['git_head'][:8]} guard={rerun['guard']} seconds={rerun['seconds']}")
    print()
    both = [t for t in q if t in f]
    diff = [(t, q[t]["checks"], f[t]["checks"]) for t in both if q[t]["checks"] != f[t]["checks"]]
    print(f"quick tests: {len(q)} in the quick run, {len(both)} of them also in the full run; check counts that differ: {len(diff)}")
    for t, a, b in diff:
        print(f"  DIFF {t}: quick {a} -> full {b}")
    missing = [t for t in q if t not in f]
    print(f"  quick tests missing from the full run: {missing}")
    qnot = [t for t in q if q[t]['status'] != 'PASS']
    print(f"  quick run not-PASS: {qnot}")
    print()
    same4 = [(t, o[t]["checks"], f[t]["checks"]) for t in o]
    print("four-test run vs full run (checks):", ", ".join(f"{t} {a}/{b}{'' if a == b else ' DIFF'}" for t, a, b in same4))
    print()
    full_only = [t for t in f if t not in q]
    print(f"full-only tests: {len(full_only)}; PASS {sum(1 for t in full_only if f[t]['status'] == 'PASS')}; seconds {round(sum(float(f[t]['seconds']) for t in full_only), 1)}")
    print("playthroughs (runner seconds, status):")
    for t in full_only:
        if t.startswith("full_op_"):
            print(f"  {t}: {f[t]['seconds']} s {f[t]['status']}")
    print("other full-only (checks, seconds):")
    for t in full_only:
        if not t.startswith("full_op_"):
            print(f"  {t}: checks {f[t]['checks']} {f[t]['seconds']} s {f[t]['status']}")
    return 0 if not diff and not missing and not qnot else 1


if __name__ == "__main__":
    sys.exit(main())
