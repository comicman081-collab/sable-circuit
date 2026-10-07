#!/usr/bin/env bash
# Claude review helper (N-07): rotated planner timing, head vs fix, 3 rounds, nothing else running.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
S="$ROOT/.cache/claude_scratch/item1_review"; P="$ROOT/.cache/claude_scratch"
L="$P/nav_review_logs/timing_ab.log"; : > "$L"
for round in 1 2 3; do
  if [ $((round % 2)) = 1 ]; then order="proj_navhead proj_navfix"; else order="proj_navfix proj_navhead"; fi
  for snap in $order; do
    load=$(powershell -NoProfile -Command "(Get-CimInstance Win32_Processor | Select-Object -First 1).LoadPercentage")
    t0=$(date +%s.%N)
    bash "$S/run_godot_low.sh" "$P/$snap" res://.cache/nav_plan_timing.gd --cell=12 --out=res://.cache/out/timing_r$round.json > "$P/nav_review_logs/timing_${snap}_r$round.log" 2>&1
    rc=$?
    t1=$(date +%s.%N)
    echo "round=$round build=$snap exit=$rc wall=$(python -c "print(round($t1-$t0,1))") load_before=${load}% $(grep -a 'NAV_PLAN_TIMING' "$P/nav_review_logs/timing_${snap}_r$round.log" | cut -c1-200)" >> "$L"
  done
done
echo TIMING_AB_DONE >> "$L"
