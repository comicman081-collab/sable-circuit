#!/usr/bin/env bash
# Claude review helper (N-06 / bot A/B): pre-fix and fix bot playthroughs ONE AT A TIME (parallel runs change the outcome: both builds
# wipe on operation 10 when two bots share the CPU), order swapped every round so a slow minute does not favour one build.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; L="$ROOT/.cache/claude_scratch/nav_review_logs"
: > "$L/ab_serial.done"
python -B "$S/bots_nav.py" \
  head:6:s1 fix:6:s1 head:10:s1 fix:10:s1 \
  fix:6:s2 head:6:s2 fix:10:s2 head:10:s2 \
  head:6:s3 fix:6:s3 head:10:s3 fix:10:s3 \
  fix:6:s4 head:6:s4 \
  head:6:s5 fix:6:s5 > "$L/ab_serial.log" 2>&1
echo AB_SERIAL_DONE >> "$L/ab_serial.done"
