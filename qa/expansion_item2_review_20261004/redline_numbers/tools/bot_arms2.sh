#!/usr/bin/env bash
# Claude review helper (REDLINE number study, 2026-10-04): serial rotated bot runs of ONE operation under several cells of
# (REDLINE enemy stats, armory damage level), below-normal priority, scratch snapshot only.
# usage: bot_arms2.sh <snapshot> <mission number> <rounds> <cell> [<cell> ...]
#   cell = label|contract|damage    e.g.  M0|redline:1.35,1.25,1.10,0.85|1.0     (damage 1.48 = armory level 6)
# Results: item2_review/bots_arms2.jsonl (one row per run), logs in item2_review/logs/cases/rl_*.log, done marker bots_arms2.done
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; R="$ROOT/.cache/claude_scratch/item2_review"
PROJ="$ROOT/.cache/claude_scratch/$1"; N="$2"; ROUNDS="$3"; shift 3
M=$(printf "MIS_CH01_%02d" "$N")
cells=("$@"); NC=${#cells[@]}
export LOWRUN_TIMEOUT=900     # a bot playthrough is ~110-250 s; the helper's default 200 s limit would cut it
mkdir -p "$R/logs/cases"
mkdir -p "$PROJ/.cache/out"
cp "$R/bot_arms2.gd" "$PROJ/.cache/bot_arms2.gd" || { echo "cannot copy bot_arms2.gd"; exit 1; }
for ((r=0; r<ROUNDS; r++)); do
  for ((k=0; k<NC; k++)); do
    cell="${cells[$(( (k + r) % NC ))]}"
    IFS='|' read -r label spec dmg <<< "$cell"
    out="res://.cache/out/rl_${N}_${label}_${r}"
    t0=$(date +%s)
    bash "$S/run_godot_low.sh" "$PROJ" res://.cache/bot_arms2.gd --mission="$M" --out="$out" --contract="$spec" --damage="$dmg" > "$R/logs/cases/rl_${N}_${label}_${r}.log" 2>&1
    code=$?; wall=$(( $(date +%s) - t0 ))
    python -B - "$PROJ/.cache/out/rl_${N}_${label}_${r}/full_operation.json" "$N" "$label" "$r" "$spec" "$dmg" "$code" "$wall" >> "$R/bots_arms2.jsonl" <<'PY'
import json, sys
from collections import defaultdict
p, n, label, r, spec, dmg, code, wall = sys.argv[1:]
try:
    d = json.load(open(p, encoding="utf-8"))
    res = d.get("result", {})
    tr = d.get("trace", [])
    last = tr[-1] if tr else {}
    boss = [h for h in last.get("hostiles", []) if str(h.get("id", "")).startswith("BOSS_")]
    per_step = defaultdict(float)
    for key, v in d.get("damage_by_source", {}).items():
        per_step[key.split(":")[0]] += float(v)
    contract = res.get("run_contract", {})
    row = {"op": n, "cell": label, "round": r, "contract": spec, "armory": dmg, "exit": code, "wall_s": wall, "status": d.get("status"),
           "outcome": res.get("outcome"), "elapsed": round(float(res.get("elapsed_seconds", 0)), 1), "depth": res.get("extraction_depth"),
           "kills": res.get("hostiles_defeated"), "last_step": last.get("step"),
           "boss_hp_left": round(float(boss[0]["hp"])) if boss else None,
           "damage": round(sum(float(v) for v in d.get("damage_by_source", {}).values()), 1),
           "per_step": {k: round(v) for k, v in sorted(per_step.items(), key=lambda kv: int(kv[0]))},
           "applied": [contract.get(k) for k in ("enemy_health_multiplier", "enemy_damage_multiplier", "enemy_speed_multiplier", "enemy_attack_interval_multiplier")],
           "failures": d.get("failures", [])[:3]}
except Exception as e:
    row = {"op": n, "cell": label, "round": r, "contract": spec, "armory": dmg, "exit": code, "wall_s": wall, "error": str(e)}
print(json.dumps(row, ensure_ascii=False))
PY
    tail -1 "$R/bots_arms2.jsonl" | cut -c1-300
  done
done
echo "BOT_ARMS2_DONE $N" >> "$R/bots_arms2.done"
