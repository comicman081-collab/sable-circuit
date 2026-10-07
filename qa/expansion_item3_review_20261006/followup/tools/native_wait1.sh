#!/usr/bin/env bash
# Claude review helper: native 1080p capture of the item-3 screens in the scratch snapshot, unbroken (control) and with the
# T-8 mutant (the results wait is 1.0 s again). Windowed, below-normal priority, everything inside the snapshot.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; S="$ROOT/.cache/claude_scratch/item3_review"; P="$ROOT/.cache/claude_scratch/proj_i3"
rm -f "$S/native.done"
python -B "$S/mutate_i3.py" restore "$P" > /dev/null
LOWRUN_TIMEOUT=240 bash "$S/run_godot_window_snap.sh" "$P" res://tests/render/expansion_item3_capture.gd --out=res://.cache/out/native_control > "$S/native_control.log" 2>&1
echo "control_exit=$?" >> "$S/native.done"
python -B "$S/mutate_i3.py" apply "$P" capture_wait_1s >> "$S/native.done"
LOWRUN_TIMEOUT=240 bash "$S/run_godot_window_snap.sh" "$P" res://tests/render/expansion_item3_capture.gd --out=res://.cache/out/native_wait1 > "$S/native_wait1.log" 2>&1
echo "wait1_exit=$?" >> "$S/native.done"
python -B "$S/mutate_i3.py" restore "$P" > /dev/null
echo native_done >> "$S/native.done"
