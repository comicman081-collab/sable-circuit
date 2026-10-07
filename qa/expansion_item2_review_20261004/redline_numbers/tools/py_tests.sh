#!/usr/bin/env bash
# Claude review helper: the runner's non-Godot quick tests, run directly (no Godot, no runner, no qa/ writes) at below-normal priority.
cd "$(dirname "$0")/../../.." || exit 1
PY='C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe'
export LOWRUN_TIMEOUT=600
L=.cache/claude_scratch/item2_review/py_tests.log
: > "$L"
run() {  # name, args...
  name="$1"; shift
  t0=$(date +%s)
  python -B .cache/claude_scratch/item1_review/lowrun.py "$PY" -B "$@" > ".cache/claude_scratch/item2_review/py_$name.out" 2>&1
  code=$?
  echo "$name exit=$code $(( $(date +%s) - t0 ))s :: $(tail -n 1 .cache/claude_scratch/item2_review/py_$name.out | cut -c1-160)" >> "$L"
}
run world_layout tools/environment/build_site7_world_layout.py --check
run mood_light tools/environment/build_site7_mood_light.py --check
run walk_registration tools/character_pipeline/build_walk_torso_registration.py --check
run plate_axis tests/test_site7_plate_lighting_axis.py
run variety_placement tests/test_expansion_item1_placement.py
run seam_waiver tests/test_site7_plate_lighting_seam_waiver.py
run mood_contact tests/test_site7_mood_contact_compare.py
run art_hashes qa/site7_op10_art_approval_20261002/tools/verify_hashes.py
echo PY_TESTS_DONE >> "$L"
