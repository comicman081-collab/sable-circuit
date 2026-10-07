#!/bin/bash
# Direct bot playthroughs of the held-back operation 10 (site7_full_operation_smoke.gd), one at a time, n runs. Nothing written under qa/.
cd "$(dirname "$0")/../../.."
GODOT=$(ls /d/AI\ */Godot/4.7.1-standard/Godot_v4.7.1-stable_win64_console.exe)
OUT=.cache/claude_scratch/s10_g/bot
: > $OUT/bots_progress.txt
for n in 1 2 3 4 5; do
  start=$(date +%s)
  timeout 1500 "$GODOT" --headless --path . --log-file "$OUT/bot_run$n.godot.log" -s res://tests/smoke/site7_full_operation_smoke.gd -- --mission=MIS_CH01_10 --out=res://$OUT/bot_run$n > "$OUT/bot_run$n.out.txt" 2>&1
  code=$?
  echo "bot_run$n exit=$code secs=$(( $(date +%s) - start )) | $(grep -a -E 'SITE7_FULL_OPERATION_SMOKE' "$OUT/bot_run$n.out.txt" | tail -1 | cut -c1-220)" >> $OUT/bots_progress.txt
done
echo DONE >> $OUT/bots_progress.txt
