"""Claude review helper (N-1): cell-by-cell comparison of two nav_direction_dump2.gd dumps (before = HEAD, after = the fix).

usage: nav_dump_diff2.py before.csv after.csv [--json out.json]

Rows: mission,room,step,x,y,dx,dy,blocked8,plen   (blocked8 and plen are optional in older dumps)
Exit 1 when the two dumps do not hold the same cells, or any cell that had a direction before has none after.
"""
import csv
import json
import math
import sys
from collections import defaultdict


def load(path):
    rows = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if len(row) < 7:
                continue
            key = (row[0], row[1], int(row[2]), row[3], row[4])
            rows[key] = {
                "d": (float(row[5]), float(row[6])),
                "blocked": int(row[7]) if len(row) > 7 else None,
                "plen": float(row[8]) if len(row) > 8 else None,
            }
    return rows


def turn(a, b):
    la, lb = math.hypot(*a), math.hypot(*b)
    if la < 1e-6 or lb < 1e-6:
        return None
    dot = max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / (la * lb)))
    return math.degrees(math.acos(dot))


def main():
    args = sys.argv[1:]
    out = None
    if "--json" in args:
        i = args.index("--json"); out = args[i + 1]; del args[i:i + 2]
    before, after = load(args[0]), load(args[1])
    report = {"cells_before": len(before), "cells_after": len(after)}
    bad = False
    if set(before) != set(after):
        report["cell_set_differs"] = {"only_before": len(set(before) - set(after)), "only_after": len(set(after) - set(before))}
        bad = True
    keys = sorted(set(before) & set(after))
    total = {"fixed_dead": 0, "broken": 0, "both_dead": 0, "turn_gt2": 0, "turn_gt15": 0, "turn_gt45": 0, "turn_gt90": 0, "identical": 0,
             "newly_blocked": 0, "newly_unblocked": 0, "blocked_before": 0, "blocked_after": 0,
             "plen_shorter": 0, "plen_longer": 0, "plen_same": 0, "plen_longer_cells": []}
    rooms = defaultdict(lambda: defaultdict(int))
    shorter_gain = 0.0
    for key in keys:
        b, a = before[key], after[key]
        room = (key[0], key[1])
        r = rooms[room]
        r["cells"] += 1
        dead_b = math.hypot(*b["d"]) < 1e-4
        dead_a = math.hypot(*a["d"]) < 1e-4
        if dead_b and not dead_a: total["fixed_dead"] += 1; r["fixed_dead"] += 1
        elif not dead_b and dead_a: total["broken"] += 1; r["broken"] += 1; bad = True
        elif dead_b and dead_a: total["both_dead"] += 1; r["both_dead"] += 1
        else:
            t = turn(b["d"], a["d"])
            if t <= 0.01: total["identical"] += 1; r["identical"] += 1
            if t > 2: total["turn_gt2"] += 1; r["turn_gt2"] += 1
            if t > 15: total["turn_gt15"] += 1; r["turn_gt15"] += 1
            if t > 45: total["turn_gt45"] += 1; r["turn_gt45"] += 1
            if t > 90: total["turn_gt90"] += 1; r["turn_gt90"] += 1
        if b["blocked"] is not None and a["blocked"] is not None:
            total["blocked_before"] += b["blocked"]; total["blocked_after"] += a["blocked"]
            if a["blocked"] and not b["blocked"]: total["newly_blocked"] += 1; r["newly_blocked"] += 1
            if b["blocked"] and not a["blocked"]: total["newly_unblocked"] += 1
        if b["plen"] is not None and a["plen"] is not None and not dead_b and not dead_a:
            delta = a["plen"] - b["plen"]
            if delta < -1.0: total["plen_shorter"] += 1; shorter_gain += -delta; r["plen_shorter"] += 1
            elif delta > 1.0:
                total["plen_longer"] += 1; r["plen_longer"] += 1
                if len(total["plen_longer_cells"]) < 25:
                    total["plen_longer_cells"].append({"cell": list(key), "before": b["plen"], "after": a["plen"]})
            else: total["plen_same"] += 1
    report["totals"] = total
    report["mean_plen_gain_px_on_shorter"] = round(shorter_gain / max(1, total["plen_shorter"]), 1)
    report["rooms_with_any_change"] = {"%s %s" % room: dict(v) for room, v in sorted(rooms.items()) if any(k not in ("cells", "identical") for k in v)}
    print(json.dumps({k: v for k, v in report.items() if k != "rooms_with_any_change"}, indent=1))
    print("rooms with any change: %d of %d" % (len(report["rooms_with_any_change"]), len(rooms)))
    for room, v in report["rooms_with_any_change"].items():
        print("  %-28s cells=%-5d fixed_dead=%-3d turn>2=%-4d turn>45=%-4d plen_shorter=%-4d plen_longer=%-3d newly_blocked=%d" % (
            room, v.get("cells", 0), v.get("fixed_dead", 0), v.get("turn_gt2", 0), v.get("turn_gt45", 0), v.get("plen_shorter", 0), v.get("plen_longer", 0), v.get("newly_blocked", 0)))
    if out:
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=1)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
