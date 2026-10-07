#!/usr/bin/env bash
# Claude review helper (N-1 re-check of 89d30934): run Codex's two repaired quick tests against broken copies of the planner and of the
# tests themselves, one Godot at a time at below-normal priority, inside the scratch snapshot only.
# usage: rc_matrix.sh <snapshot name, e.g. proj_navrc> <case group: fp | hz | all>
# A case is  tag|production variant|test variant|test (fp = combat_query_fastpath, hz = hazard_expansion)
# production variant: none | revert (pre-fix files from 753cf029) | a name from mutate_rc.py prod;  test variant: none | a name (or a+b) from mutate_rc.py
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item1_review"; P="$ROOT/.cache/claude_scratch"
L="$P/nav_recheck_logs"; PROJ="$P/$1"; GROUP="${2:-all}"
PRISTINE="$L/pristine_$1"; mkdir -p "$PRISTINE" "$L/cases" "$PROJ/.cache/out"
cd "$ROOT"
[ -f "$PRISTINE/cover_navigation.gd" ] || {
  cp "$PROJ/scripts/combat/cover_navigation.gd" "$PROJ/scripts/combat/site7_enemy_tactics.gd" "$PROJ/tests/smoke/combat_query_fastpath_smoke.gd" "$PROJ/tests/smoke/hazard_expansion_smoke.gd" "$PRISTINE/"; }

run_case() {
  local tag="$1" pv="$2" tv="$3" which="$4" base kind extra
  cp "$PRISTINE/cover_navigation.gd" "$PROJ/scripts/combat/cover_navigation.gd"
  cp "$PRISTINE/site7_enemy_tactics.gd" "$PROJ/scripts/combat/site7_enemy_tactics.gd"
  case "$pv" in
    none) ;;
    revert) git show 753cf029:scripts/combat/cover_navigation.gd > "$PROJ/scripts/combat/cover_navigation.gd"
            git show 753cf029:scripts/combat/site7_enemy_tactics.gd > "$PROJ/scripts/combat/site7_enemy_tactics.gd" ;;
    *) python -B "$S/mutate_rc.py" prod "$pv" "$PRISTINE/cover_navigation.gd" "$PROJ/scripts/combat/cover_navigation.gd" > "$L/cases/$tag.mutate.log" 2>&1 || { echo "$tag: production mutation failed"; return; } ;;
  esac
  case "$which" in
    fp) base=combat_query_fastpath_smoke.gd; kind=test_fp; extra="" ;;
    hz) base=hazard_expansion_smoke.gd; kind=test_hz; extra="--out=res://.cache/out/hz_$tag.json" ;;
  esac
  local tgt="$PROJ/.cache/rc_$tag.gd"
  if [ "$tv" = none ]; then cp "$PRISTINE/$base" "$tgt"; else
    cp "$PRISTINE/$base" "$tgt.step"
    IFS='+' read -ra steps <<< "$tv"
    for st in "${steps[@]}"; do
      python -B "$S/mutate_rc.py" "$kind" "$st" "$tgt.step" "$tgt.next" >> "$L/cases/$tag.mutate.log" 2>&1 || { echo "$tag: test mutation $st failed"; return; }
      mv "$tgt.next" "$tgt.step"
    done
    mv "$tgt.step" "$tgt"
  fi
  local t0=$(date +%s)
  bash "$S/run_godot_low.sh" "$PROJ" "res://.cache/rc_$tag.gd" $extra > "$L/cases/$tag.log" 2>&1
  local code=$? wall=$(( $(date +%s) - t0 ))
  local result; result=$(grep -E '_SMOKE: (PASS|FAIL)' "$L/cases/$tag.log" | tail -1 | tr -d '\r')
  local nfail; nfail=$(grep -c '^FAIL:' "$L/cases/$tag.log")
  local nneg; nneg=$(grep -c '^FAIL:.*negative control' "$L/cases/$tag.log")
  local nplan; nplan=$(grep -c '^FAIL:.*_plan agrees' "$L/cases/$tag.log")
  local nlong; nlong=$(grep -c '^FAIL:.*new routes are no longer' "$L/cases/$tag.log")
  local nscript; nscript=$(grep -c 'SCRIPT ERROR' "$L/cases/$tag.log")
  python -B - "$tag" "$pv" "$tv" "$which" "$code" "$wall" "$result" "$nfail" "$nneg" "$nplan" "$nlong" "$nscript" >> "$L/rc_matrix.jsonl" <<'PY'
import json, sys
k = ["tag", "prod", "test_variant", "test", "exit", "wall_s", "result", "fail_lines", "negative_control_fails", "plan_agrees_fails", "no_longer_fails", "script_errors"]
v = sys.argv[1:]
print(json.dumps(dict(zip(k, v)), ensure_ascii=False))
PY
  echo "[$tag] prod=$pv test=$tv ($which): exit=$code ${wall}s  $result  FAIL-lines=$nfail neg=$nneg plan=$nplan long=$nlong scripterr=$nscript"
}

fp_cases() {
  run_case fp_base1 none none fp; run_case fp_base2 none none fp; run_case fp_base3 none none fp
  for v in over nophys nonodes noswap nomargin nowaypoints; do run_case "fp_$v" "$v" none fp; done
  for v in over nophys nonodes noswap nomargin nowaypoints; do run_case "fpx_$v" "$v" noexact fp; done
  run_case fp_revert revert none fp
  run_case fpx_revert revert noexact fp
}
hz_cases() {
  run_case hz_base1 none none hz; run_case hz_base2 none none hz; run_case hz_base3 none none hz
  run_case hz_noblocker none noblocker hz
  for v in over nophys nonodes noswap nomargin nowaypoints; do run_case "hz_$v" "$v" none hz; done
  run_case hz_revert revert none hz
  run_case hz_smallbox none smallbox hz
  run_case hz_smallbox_noblocker none smallbox+noblocker hz
}
case "$GROUP" in fp) fp_cases;; hz) hz_cases;; all) fp_cases; hz_cases;; esac
# leave the snapshot pristine
cp "$PRISTINE/cover_navigation.gd" "$PROJ/scripts/combat/cover_navigation.gd"; cp "$PRISTINE/site7_enemy_tactics.gd" "$PROJ/scripts/combat/site7_enemy_tactics.gd"
echo "RC_MATRIX_DONE $GROUP" >> "$L/rc_matrix.done"
