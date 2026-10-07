#!/usr/bin/env bash
# Claude review helper (item 3 review): run the intel / module / weapon / lab tests against broken copies of the code, one Godot at
# a time at below-normal priority, inside the scratch snapshot only (nothing on C:, nothing under qa/).
# usage: i3_matrix.sh <snapshot name, e.g. proj_i3> <mutant names... | all | base | base:<tests>>
# Every mutant runs the tests its row in mutate_i3.py lists (letters, see that file); `base` runs the whole letter set once on the
# unbroken snapshot (the baseline error-line counts the table subtracts); `base:ilw` runs only those letters.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; R="$ROOT/.cache/claude_scratch/item3_review"
PROJ="$ROOT/.cache/claude_scratch/$1"; shift
L="$R/logs"; mkdir -p "$L/cases" "$PROJ/.cache/out"
cd "$ROOT"

# letter -> runner test name, script, --out style ('' none, 'dir' folder, otherwise a file name in the folder), time limit in seconds
declare -A NAME=( [i]=intel_supply [m]=module_expansion [w]=weapon_expansion [l]=lab_geometry [s]=contract_save [p]=m10_persistence
  [g]=m13_migration [e]=upgrade_economy [b]=m10_base_ui [n]=m10_intel [o]=m13_loadout [c]=campaign [t]=lab_capture_geometry
  [h]=hit_hurt_vfx [q]=m13_campaign [r]=m13_runtime )
declare -A SCRIPT=( [i]=tests/smoke/intel_supply_smoke.gd [m]=tests/smoke/module_expansion_smoke.gd [w]=tests/smoke/weapon_expansion_smoke.gd
  [l]=tests/smoke/lab_geometry_smoke.gd [s]=tests/smoke/run_contract_save_smoke.gd [p]=tests/smoke/m10_persistence_smoke.gd
  [g]=tests/smoke/m13_weapon_base_migration_smoke.gd [e]=tests/smoke/upgrade_economy_smoke.gd [b]=tests/smoke/m10_base_ui_action_smoke.gd
  [n]=tests/smoke/m10_intel_loadout_smoke.gd [o]=tests/smoke/m13_weapon_loadout_smoke.gd [c]=tests/smoke/site7_campaign_progression_smoke.gd
  [t]=tests/render/expansion_item3_capture.gd [h]=tests/smoke/combat_hit_hurt_vfx_smoke.gd [q]=tests/smoke/m13_weapon_campaign_smoke.gd
  [r]=tests/smoke/m13_weapon_runtime_smoke.gd )
declare -A OUTSTYLE=( [i]=intel_supply.json [m]=module_expansion.json [w]=weapon_expansion.json [l]=lab_geometry.json [s]=save.json [p]=save.json
  [g]=save.json [e]=save.json [b]= [n]= [o]=save.json [c]=dir [t]=dir [h]= [q]= [r]= )
declare -A LIMIT=( [c]=700 [t]=200 )
ALL=imwlspgebnoctqhr

run_test() {  # tag letter
  local tag="$1" k="$2" log="$L/cases/${1}__${NAME[$2]}.log" t0 code wall result nerr nscript npass out limit
  local dir="$PROJ/.cache/out/${tag}_${NAME[$k]}"; mkdir -p "$dir"
  out=""
  case "${OUTSTYLE[$k]}" in
    "") ;;
    dir) out="--out=res://.cache/out/${tag}_${NAME[$k]}" ;;
    *) out="--out=res://.cache/out/${tag}_${NAME[$k]}/${OUTSTYLE[$k]}" ;;
  esac
  limit="${LIMIT[$k]:-200}"
  t0=$(date +%s)
  LOWRUN_TIMEOUT="$limit" bash "$S/run_godot_low.sh" "$PROJ" "res://${SCRIPT[$k]}" $out > "$log" 2>&1
  code=$?; wall=$(( $(date +%s) - t0 ))
  result=$(grep -aE '(PASS|FAIL)' "$log" | grep -avE '^(PASS|FAIL): ' | grep -aE '[A-Z_]{6,}[: ]' | tail -1 | tr -d '\r' | cut -c1-160)
  nerr=$(grep -aE '^(ERROR|FAIL):' "$log" | grep -avc 'resources still in use at exit')   # that exit warning is not a failed check
  nscript=$(grep -acE 'SCRIPT ERROR|Parse Error' "$log")
  npass=$(grep -acE '^PASS: ' "$log")
  python -B - "$tag" "${NAME[$k]}" "$code" "$wall" "$nerr" "$nscript" "$npass" "$result" >> "$R/i3_matrix.jsonl" <<'PY'
import json, sys
k = ["mutant", "test", "exit", "wall_s", "error_lines", "script_errors", "pass_lines", "result"]
print(json.dumps(dict(zip(k, sys.argv[1:])), ensure_ascii=False))
PY
  echo "[$tag/${NAME[$k]}] exit=$code ${wall}s errors=$nerr scripterr=$nscript pass=$npass  $result"
}

run_mutant() {
  local name="$1" tests want
  case "$name" in
    base) python -B "$R/mutate_i3.py" restore "$PROJ" > /dev/null; tests="$ALL" ;;
    base:*) python -B "$R/mutate_i3.py" restore "$PROJ" > /dev/null; tests="${name#base:}"; name=base ;;
    *)
      python -B "$R/mutate_i3.py" apply "$PROJ" "$name" || { echo "[$name] apply failed"; return; }
      want=$(python -B "$R/mutate_i3.py" list | awk -v n="$name" '$1==n {print $2}' | sed 's/tests=//')
      tests="$want" ;;
  esac
  for ((i=0; i<${#tests}; i++)); do run_test "$name" "${tests:$i:1}"; done
}

if [ "$1" = all ]; then
  for n in $(python -B "$R/mutate_i3.py" list | awk 'NF>2 && $1!~/mutants/ {print $1}'); do run_mutant "$n"; done
else
  for n in "$@"; do run_mutant "$n"; done
fi
python -B "$R/mutate_i3.py" restore "$PROJ" > /dev/null
echo "I3_MATRIX_DONE $*" >> "$R/i3_matrix.done"
