#!/usr/bin/env bash
# Claude review helper (N-06): head and fix bot of one operation side by side (same conditions), pairs one after another.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; L="$ROOT/.cache/claude_scratch/nav_review_logs"
for item in "$@"; do   # item = op:tag
  op="${item%%:*}"; tag="${item##*:}"
  python -B "$S/bots_nav.py" head:$op:$tag > "$L/bot_head_${op}_$tag.log" 2>&1 &
  python -B "$S/bots_nav.py" fix:$op:$tag > "$L/bot_fix_${op}_$tag.log" 2>&1 &
  wait
done
echo BOT_PAIRS_DONE >> "$L/bot_pairs.done"
