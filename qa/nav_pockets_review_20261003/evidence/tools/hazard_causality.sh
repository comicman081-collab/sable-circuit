#!/usr/bin/env bash
# Claude review helper (N-1, B-4): is hazard_expansion red because of the fix? Same test, pre-fix and fix snapshot, one after the other.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; P="$ROOT/.cache/claude_scratch"; L="$P/nav_review_logs"
: > "$L/hazard_causality.done"
for snap in proj_navhead proj_navfix; do
  bash "$S/run_godot_low.sh" "$P/$snap" res://tests/smoke/hazard_expansion_smoke.gd > "$L/hazard_expansion_${snap}.log" 2>&1
done
echo HAZARD_CAUSALITY_DONE >> "$L/hazard_causality.done"
