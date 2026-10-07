#!/usr/bin/env bash
# Claude review helper (item 2): serial rotated bot runs of one operation under three contract arms
# (neutral {} = the runner's, default = RunContract.build of a real run id, redline), below-normal priority, scratch snapshot only.
# usage: bot_arms.sh <snapshot> <mission number> <rounds>
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; R="$ROOT/.cache/claude_scratch/item2_review"
PROJ="$ROOT/.cache/claude_scratch/$1"; N="$2"; ROUNDS="$3"; M=$(printf "MIS_CH01_%02d" "$N")
export LOWRUN_TIMEOUT=900     # a bot playthrough is ~140-250 s; the helper's default 200 s limit would cut it
cp "$R/bot_arms.gd" "$PROJ/.cache/bot_arms.gd"
arms=(neutral default redline)
for ((r=0; r<ROUNDS; r++)); do
  for ((k=0; k<3; k++)); do
    arm="${arms[$(( (k + r) % 3 ))]}"
    spec="$arm"; [ "$arm" = default ] && spec="default:CH01-RUN-$(printf %06d $((r*7+11)))"
    out="res://.cache/out/bot_${N}_${arm}_${r}"
    t0=$(date +%s)
    bash "$S/run_godot_low.sh" "$PROJ" res://.cache/bot_arms.gd --mission="$M" --out="$out" --contract="$spec" > "$R/logs/cases/bot_${N}_${arm}_${r}.log" 2>&1
    code=$?; wall=$(( $(date +%s) - t0 ))
    python -B - "$PROJ/.cache/out/bot_${N}_${arm}_${r}/full_operation.json" "$N" "$arm" "$r" "$spec" "$code" "$wall" >> "$R/bots_arms.jsonl" <<'PY'
import json, sys
p, n, arm, r, spec, code, wall = sys.argv[1:]
try:
    d = json.load(open(p, encoding="utf-8"))
    res = d.get("result", {})
    row = {"op": n, "arm": arm, "round": r, "contract": spec, "exit": code, "wall_s": wall, "status": d.get("status"),
           "outcome": res.get("outcome"), "elapsed": round(float(res.get("elapsed_seconds", 0)), 1), "depth": res.get("extraction_depth"),
           "damage": round(sum(float(v) for v in d.get("damage_by_source", {}).values()), 1), "failures": d.get("failures", [])[:3]}
except Exception as e:
    row = {"op": n, "arm": arm, "round": r, "contract": spec, "exit": code, "wall_s": wall, "error": str(e)}
print(json.dumps(row, ensure_ascii=False))
PY
    tail -1 "$R/bots_arms.jsonl" | cut -c1-260
  done
done
echo "BOT_ARMS_DONE $N" >> "$R/bots_arms.done"
