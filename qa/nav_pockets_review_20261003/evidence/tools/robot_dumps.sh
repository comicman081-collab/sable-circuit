#!/usr/bin/env bash
# Claude review helper (N-1 side effects): the same cell-by-cell direction dump as dump2, but with the room's first lane robot
# (4 px wider collider than the operator) as the probe, on the HEAD copy and the fix copy at the same time.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; P="$ROOT/.cache/claude_scratch"; L="$P/nav_review_logs"
: > "$L/robot_dumps.done"
for snap in proj_navhead proj_navfix; do
  ( bash "$S/run_godot_low.sh" "$P/$snap" res://.cache/nav_direction_dump2.gd --cell=12 --actor=robot --out=res://.cache/out/dump2_robot.csv > "$L/dump2_robot_${snap}.log" 2>&1 ) &
done
wait
echo ROBOT_DUMPS_DONE >> "$L/robot_dumps.done"
