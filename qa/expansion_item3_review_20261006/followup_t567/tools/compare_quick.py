"""Claude scratch (T-5/T-6/T-7): line up two runner summaries test by test.

usage: python -B compare_quick.py <new summary.json> <old summary.json>
Prints status and check-count differences, tests missing on either side, the guard verdict and git state."""
import json
import sys

new = json.load(open(sys.argv[1], encoding="utf-8"))
old = json.load(open(sys.argv[2], encoding="utf-8"))
nrows = {r["test"]: r for r in new["results"]}
orows = {r["test"]: r for r in old["results"]}
print("new: %s  head %s  dirty %s  overall %s  seconds %s" % (new["suite"], new["git_head"][:8], new["git_dirty"], new["overall"], new["seconds"]))
print("old: %s  head %s  dirty %s  overall %s  seconds %s" % (old["suite"], old["git_head"][:8], old["git_dirty"], old["overall"], old["seconds"]))
print("guard new:", json.dumps(new.get("guard"), ensure_ascii=False))
print("guard old:", json.dumps(old.get("guard"), ensure_ascii=False))
passed = sum(1 for r in new["results"] if r["status"] == "PASS")
print("new: %d of %d PASS" % (passed, len(new["results"])))
same = 0
for name in sorted(set(nrows) | set(orows)):
    a, b = nrows.get(name), orows.get(name)
    if a is None or b is None:
        print("ONLY IN %s: %s" % ("old" if a is None else "new", name))
        continue
    if a["status"] != b["status"] or a.get("checks") != b.get("checks"):
        print("DIFF %-28s %s %s checks -> %s %s checks" % (name, b["status"], b.get("checks"), a["status"], a.get("checks")))
    else:
        same += 1
print("same status and check count: %d of %d" % (same, len(set(nrows) | set(orows))))
print("checks total new %d  old %d" % (sum(r.get("checks") or 0 for r in new["results"]), sum(r.get("checks") or 0 for r in old["results"])))
