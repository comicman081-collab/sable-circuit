#!/usr/bin/env bash
# Claude review helper (N-07, second method): head and fix planner timing run AT THE SAME TIME, 3 rounds, so any load from other
# programs hits both alike; the ratio of each pair is what counts.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; P="$ROOT/.cache/claude_scratch"; L="$P/nav_review_logs"
: > "$L/timing_pairs.log"
for round in 1 2 3; do
  for snap in proj_navhead proj_navfix; do
    ( bash "$S/run_godot_low.sh" "$P/$snap" res://.cache/nav_plan_timing.gd --cell=12 --out=res://.cache/out/timingp_r$round.json > "$L/timingp_${snap}_r$round.log" 2>&1 ) &
  done
  wait
  for snap in proj_navhead proj_navfix; do
    echo "round=$round build=$snap $(grep -a 'NAV_PLAN_TIMING' "$L/timingp_${snap}_r$round.log" | cut -c1-200)" >> "$L/timing_pairs.log"
  done
done
echo TIMING_PAIRS_DONE >> "$L/timing_pairs.log"
