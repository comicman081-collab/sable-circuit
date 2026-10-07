"""Claude review helper (N-1): pick the cells for the physical walk-out from two direction dumps.

usage: nav_cells_select.py before.csv after.csv outdir [--seed 20261003] [--changed-per-room 3] [--same-per-room 1]

before.csv / after.csv rows: mission,room,step,x,y,dx,dy[,blocked8]  (nav_direction_dump.gd / nav_direction_dump2.gd).
Writes into outdir (rows are mission,step,x,y):
  cells_dead.csv     every cell the BEFORE dump gave a zero vector (the audit's dead cells)
  cells_changed.csv  a seeded sample of live cells whose direction turned by more than 2 degrees
  cells_same.csv     a seeded sample of live cells whose direction did not change (control)
  selection.json     counts
"""
import csv
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path


def load(path):
    rows = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if len(row) < 7:
                continue
            key = (row[0], int(row[2]), row[3], row[4])
            rows[key] = (row[1], float(row[5]), float(row[6]), int(row[7]) if len(row) > 7 else 0)
    return rows


def angle(a, b):
    la = math.hypot(*a)
    lb = math.hypot(*b)
    if la < 1e-6 or lb < 1e-6:
        return 180.0 if (la < 1e-6) != (lb < 1e-6) else 0.0
    dot = max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / (la * lb)))
    return math.degrees(math.acos(dot))


def write(path, keys):
    with open(path, "w", encoding="utf-8", newline="") as handle:
        for mission, step, x, y in keys:
            handle.write("%s,%d,%s,%s\n" % (mission, step, x, y))


def main():
    args = sys.argv[1:]
    seed = 20261003
    changed_per_room = 3
    same_per_room = 1
    while "--seed" in args:
        i = args.index("--seed"); seed = int(args[i + 1]); del args[i:i + 2]
    while "--changed-per-room" in args:
        i = args.index("--changed-per-room"); changed_per_room = int(args[i + 1]); del args[i:i + 2]
    while "--same-per-room" in args:
        i = args.index("--same-per-room"); same_per_room = int(args[i + 1]); del args[i:i + 2]
    before = load(args[0])
    after = load(args[1])
    outdir = Path(args[2])
    outdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    dead = []
    newblocked = []
    changed = defaultdict(list)
    bigturn = defaultdict(list)
    same = defaultdict(list)
    for key, (room, dx, dy, _blk) in sorted(before.items()):
        if key not in after:
            continue
        mission, step, x, y = key
        if abs(dx) < 1e-4 and abs(dy) < 1e-4:
            dead.append((mission, step, x, y))
            continue
        turn = angle((dx, dy), (after[key][1], after[key][2]))
        (changed if turn > 2.0 else same)[(mission, step)].append((mission, step, x, y))
        if turn > 45.0: bigturn[(mission, step)].append((mission, step, x, y))
        if after[key][3] and not before[key][3]: newblocked.append((mission, step, x, y))
    pick_changed = []
    pick_same = []
    for room_key in sorted(changed):
        pick_changed += rng.sample(changed[room_key], min(changed_per_room, len(changed[room_key])))
    for room_key in sorted(same):
        pick_same += rng.sample(same[room_key], min(same_per_room, len(same[room_key])))
    pick_big = []
    for room_key in sorted(bigturn):
        pick_big += rng.sample(bigturn[room_key], min(3, len(bigturn[room_key])))
    write(outdir / "cells_newblocked.csv", newblocked)
    write(outdir / "cells_bigturn.csv", pick_big)
    write(outdir / "cells_dead.csv", dead)
    write(outdir / "cells_changed.csv", pick_changed)
    write(outdir / "cells_same.csv", pick_same)
    summary = {"seed": seed, "dead": len(dead), "newly_blocked": len(newblocked), "bigturn_pool": sum(len(v) for v in bigturn.values()), "bigturn_sample": len(pick_big), "changed_pool": sum(len(v) for v in changed.values()), "changed_sample": len(pick_changed),
               "same_pool": sum(len(v) for v in same.values()), "same_sample": len(pick_same), "rooms_with_changes": len(changed)}
    (outdir / "selection.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
