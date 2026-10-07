#!/usr/bin/env bash
# Claude review helper (item 3): the same save files read by the OLD code (381ef0fb, schema 5) and the NEW code (0a14d5b6, schema 6).
# Both snapshots are scratch copies; nothing is written outside .cache, the player's save is never read.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item3_review"; C="$ROOT/.cache/claude_scratch"
NEW="$C/proj_i3"; OLD="$C/proj_i3old"; O="$S/probe_out"; mkdir -p "$O"; rm -f "$S/probe.done"
run() {  # snapshot script args...
  local proj="$1" script="$2"; shift 2
  LOWRUN_TIMEOUT=120 bash "$C/item1_review/run_godot_low.sh" "$proj" "$script" "$@" 2>&1 | grep -aE "SAVE_PROBE|MAKE_RICH_V6|^ERROR:|SCRIPT ERROR|Parse Error" | cut -c1-260
}
for v in v3 v4 v5; do
  run "$OLD" res://.cache/probes/save_probe.gd --in=res://.cache/probes/in/save_$v.json --out=res://.cache/out/probe --tag=old_$v
  run "$NEW" res://.cache/probes/save_probe.gd --in=res://.cache/probes/in/save_$v.json --out=res://.cache/out/probe --tag=new_$v
done
run "$NEW" res://.cache/probes/make_rich_v6.gd --out=res://.cache/out/rich6_made.json
cp "$NEW/.cache/out/rich6_made.json" "$NEW/.cache/probes/in/rich6.json"; cp "$NEW/.cache/out/rich6_made.json" "$OLD/.cache/probes/in/rich6.json"
run "$OLD" res://.cache/probes/save_probe.gd --in=res://.cache/probes/in/rich6.json --out=res://.cache/out/probe --tag=old_rich6
run "$NEW" res://.cache/probes/save_probe.gd --in=res://.cache/probes/in/rich6.json --out=res://.cache/out/probe --tag=new_rich6
cp "$OLD"/.cache/out/probe/old_*.json "$O/"; cp "$NEW"/.cache/out/probe/new_*.json "$O/"
cp "$NEW/.cache/out/rich6_made.json" "$O/rich6_made.json"
echo probe_done > "$S/probe.done"
