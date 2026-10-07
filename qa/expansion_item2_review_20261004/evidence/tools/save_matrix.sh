#!/usr/bin/env bash
# Claude review helper (item 2): load every input save with the OLD (7b26a152) and the NEW (b4aa2ae0) code, resave and re-read.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; P="$ROOT/.cache/claude_scratch"
for x in player_v3 old_v4 codex_v3 codex_v4 new_v5; do
  for pair in "old:proj_head" "new:proj_ic"; do
    tag="${pair%%:*}"; snap="${pair##*:}"
    cp "$P/$snap/.cache/in/$x.json" "$P/$snap/.cache/in/run_${tag}__$x.json"
    bash "$S/run_godot_low.sh" "$P/$snap" res://.cache/save_probe.gd --save=res://.cache/in/run_${tag}__$x.json --out=res://.cache/out/probe_${tag}__$x.json --resave=1 2>&1 | grep -aE "SAVE_PROBE|ERROR|SCRIPT" | head -3
  done
done
