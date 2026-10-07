#!/usr/bin/env bash
# Claude review helper (N-1): checks that need a quiet machine and therefore run after the whole-suite gate.
#   1. combat_query_fastpath on the pre-fix and the fix snapshot, plus the classifying probe (B-3 diagnosis)
#   2. my hazard escape grids (they use CoverNavigation._clear_ground as the oracle) on both snapshots: did the oracle's
#      change move any escape number? (25 px all rooms; 10 px operations 6-9)
# One Godot at a time, below-normal priority. Never start it while a regression runner is alive.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; P="$ROOT/.cache/claude_scratch"; L="$P/nav_review_logs"
: > "$L/post_chain.done"
bash "$S/fastpath_chain.sh"
for snap in proj_navhead proj_navfix; do
  cp "$S/hazard_escape_grid.gd" "$P/$snap/.cache/hazard_escape_grid.gd"
  bash "$S/run_godot_low.sh" "$P/$snap" res://.cache/hazard_escape_grid.gd --grid=25 --out=res://.cache/out/hazard25.json > "$L/hazard25_${snap}.log" 2>&1
  bash "$S/run_godot_low.sh" "$P/$snap" res://.cache/hazard_escape_grid.gd --grid=10 --missions=6,7,8,9 --out=res://.cache/out/hazard10.json > "$L/hazard10_${snap}.log" 2>&1
done
echo POST_CHAIN_DONE >> "$L/post_chain.done"
