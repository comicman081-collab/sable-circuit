#!/usr/bin/env bash
# Claude review helper (item 2 review): run the contract tests against broken copies of the code, one Godot at a time at
# below-normal priority, inside the scratch snapshot only.
# usage: ic_matrix.sh <snapshot name, e.g. proj_ic> <mutant names... | all | base>
# Every mutant runs o u r s m p; b (boss_duel) and c (campaign) only where mutate_ic.py lists them.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; R="$ROOT/.cache/claude_scratch/item2_review"
PROJ="$ROOT/.cache/claude_scratch/$1"; shift
L="$R/logs"; mkdir -p "$L/cases" "$PROJ/.cache/out"
cd "$ROOT"

declare -A SCRIPT=(
  [o]=run_contract_offers_smoke.gd [u]=run_contract_ui_smoke.gd [r]=redline_smoke.gd [s]=run_contract_save_smoke.gd
  [m]=m11_run_contract_smoke.gd [p]=play_session_log_smoke.gd [b]=site7_boss_duel_smoke.gd [c]=site7_campaign_progression_smoke.gd )
declare -A NAME=( [o]=contract_offers [u]=contract_ui [r]=redline [s]=contract_save [m]=run_contract [p]=play_log [b]=boss_duel [c]=campaign )

run_test() {  # tag testkey
  local tag="$1" k="$2" log="$L/cases/${1}__${2}.log" t0 code wall result nerr nscript
  t0=$(date +%s)
  bash "$S/run_godot_low.sh" "$PROJ" "res://tests/smoke/${SCRIPT[$k]}" "--out=res://.cache/out/${tag}_${k}" > "$log" 2>&1
  code=$?; wall=$(( $(date +%s) - t0 ))
  result=$(grep -aE '(SMOKE|SMOKE_?[A-Z]*|ECONOMY|FAIRNESS|REGRESSION)[: ]+ ?(PASS|FAIL)|: (PASS|FAIL) ' "$log" | tail -1 | tr -d '\r' | cut -c1-160)
  nerr=$(grep -acE '^(ERROR|FAIL):' "$log")
  nscript=$(grep -acE 'SCRIPT ERROR|Parse Error' "$log")
  python -B - "$tag" "${NAME[$k]}" "$code" "$wall" "$nerr" "$nscript" "$result" >> "$R/ic_matrix.jsonl" <<'PY'
import json, sys
k = ["mutant", "test", "exit", "wall_s", "error_lines", "script_errors", "result"]
print(json.dumps(dict(zip(k, sys.argv[1:])), ensure_ascii=False))
PY
  echo "[$tag/${NAME[$k]}] exit=$code ${wall}s errors=$nerr scripterr=$nscript  $result"
}

run_mutant() {
  local name="$1" tests
  if [ "$name" = base ]; then python -B "$R/mutate_ic.py" restore "$PROJ" > /dev/null; tests="ousrmp"
  else
    python -B "$R/mutate_ic.py" apply "$PROJ" "$name" || { echo "[$name] apply failed"; return; }
    tests="ousrmp"
    local want; want=$(python -B "$R/mutate_ic.py" list | awk -v n="$name" '$1==n {print $2}' | sed 's/tests=//')
    case "$want" in *b*) tests="${tests}b";; esac
    case "$want" in *c*) tests="${tests}c";; esac
  fi
  for ((i=0; i<${#tests}; i++)); do run_test "$name" "${tests:$i:1}"; done
}

if [ "$1" = all ]; then
  for n in $(python -B "$R/mutate_ic.py" list | awk 'NF>2 && $1!~/mutants/ {print $1}'); do run_mutant "$n"; done
else
  for n in "$@"; do run_mutant "$n"; done
fi
python -B "$R/mutate_ic.py" restore "$PROJ" > /dev/null
echo "IC_MATRIX_DONE $*" >> "$R/ic_matrix.done"
