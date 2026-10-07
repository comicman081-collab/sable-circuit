#!/bin/bash
# Boss-room fairness of operation 10's real R05_CORE (committed tip), scratch copy of the smoke, grids from coarse to fine. Sequential, one Godot at a time.
cd "$(dirname "$0")/../../.."
GODOT=$(ls /d/AI\ */Godot/4.7.1-standard/Godot_v4.7.1-stable_win64_console.exe)
OUT=.cache/claude_scratch/s10_g/fair
rm -f $OUT/fair.done
for g in 100 75 60 50 40 30 25 20 15 10; do
  s=$(date +%s)
  "$GODOT" --headless --path . --log-file $OUT/final_g$g.godot.log -s res://.cache/claude_scratch/op10_fairness/boss_room_fairness_op10.gd -- --grid=$g --out=res://.cache/claude_scratch/s10_g/fair/final_g$g.json > $OUT/final_g$g.out 2>&1
  echo "grid $g exit $? $(( $(date +%s) - s )) s" >> $OUT/progress.txt
done
echo done > $OUT/fair.done
