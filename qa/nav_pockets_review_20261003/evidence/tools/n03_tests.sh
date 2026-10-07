#!/usr/bin/env bash
# Claude review helper (N-03): the five navigation tests on one snapshot, same order and arguments as the runner
# (--headless -s res://<test> [-- --out=...]). usage: n03_tests.sh <snapshot name> [tag]
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
snap="$1"; tag="${2:-$1}"
P="$ROOT/.cache/claude_scratch/$snap"
L="$ROOT/.cache/claude_scratch/nav_review_logs"
mkdir -p "$P/.cache/out"
run() { # name script [args]
  local name="$1" script="$2"; shift 2
  local t0=$(date +%s)
  bash "$ROOT/.cache/claude_scratch/item1_review/run_godot_low.sh" "$P" "$script" "$@" > "$L/n03_${tag}_$name.log" 2>&1
  local rc=$?
  echo "EXIT=$rc WALL=$(( $(date +%s) - t0 ))s" >> "$L/n03_${tag}_$name.log"
}
run cover_navigation res://tests/smoke/cover_navigation_smoke.gd
run firing_lane res://tests/smoke/firing_lane_search_smoke.gd
run world_route res://tests/smoke/site7_world_route_navigation_smoke.gd
run cover_ai res://tests/render/site7_cover_ai_check.gd --out=res://.cache/out/cover_ai
run enemy_cover_nav res://tests/render/enemy_cover_navigation_regression.gd --out=res://.cache/out/enemy_cover_nav
echo "N03 DONE $snap"
