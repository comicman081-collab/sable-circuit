#!/usr/bin/env bash
# Claude review helper (N-1): break Codex's fix four ways on a scratch copy and see which tests notice.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; P="$ROOT/.cache/claude_scratch"
L="$P/nav_review_logs"; SRC="$L/cover_navigation_fix.gd"; DST="$P/proj_navm4/scripts/combat/cover_navigation.gd"
run() { local tag="$1" script="$2"; shift 2; local t0=$(date +%s)
  bash "$S/run_godot_low.sh" "$P/proj_navm4" "$script" "$@" > "$L/m4_$tag.log" 2>&1; echo "EXIT=$? WALL=$(( $(date +%s) - t0 ))s" >> "$L/m4_$tag.log"; }
for variant in "$@"; do
  python -B "$S/mutate_nav.py" "$variant" "$SRC" "$DST" > "$L/m4_${variant}.mutate.log" 2>&1 || { echo "mutation $variant failed"; continue; }
  run ${variant}_audit res://.cache/audit_nav_pockets.gd --cell=12 --out=res://.cache/out/m4_${variant}.json
  run ${variant}_smoke res://tests/smoke/cover_navigation_smoke.gd
  case "$variant" in over|nophys) run ${variant}_enemynav res://tests/render/enemy_cover_navigation_regression.gd --out=res://.cache/out/m4_${variant}_en;; esac
  case "$variant" in over) run ${variant}_coverai res://tests/render/site7_cover_ai_check.gd --out=res://.cache/out/m4_${variant}_ca;; esac
  case "$variant" in noswap) run ${variant}_lane res://tests/smoke/firing_lane_search_smoke.gd;; esac
done
cp "$SRC" "$DST"; echo M4_DONE >> "$L/m4.done"
