#!/usr/bin/env bash
# Claude review helper (N-1, B-3): is combat_query_fastpath red because of the fix, and is anything left unexplained?
#   1. original test on the pre-fix snapshot (expect PASS)       2. original test on the fix snapshot (expect FAIL)
#   3. scratch probe on the fix snapshot (classifies the differing plans; second reference with the new rules)
# Runs one Godot at a time at below-normal priority. Never start it while a regression runner is alive.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; P="$ROOT/.cache/claude_scratch"; L="$P/nav_review_logs"
: > "$L/fastpath_chain.done"
cp "$S/fastpath_probe.gd" "$P/proj_navfix/.cache/fastpath_probe.gd"
bash "$S/run_godot_low.sh" "$P/proj_navhead" res://tests/smoke/combat_query_fastpath_smoke.gd > "$L/fastpath_head.log" 2>&1
bash "$S/run_godot_low.sh" "$P/proj_navfix" res://tests/smoke/combat_query_fastpath_smoke.gd > "$L/fastpath_fix.log" 2>&1
bash "$S/run_godot_low.sh" "$P/proj_navfix" res://.cache/fastpath_probe.gd > "$L/fastpath_probe_fix.log" 2>&1
echo FASTPATH_CHAIN_DONE >> "$L/fastpath_chain.done"
