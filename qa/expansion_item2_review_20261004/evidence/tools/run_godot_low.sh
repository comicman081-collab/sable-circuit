#!/usr/bin/env bash
# Claude review helper: run a Godot script headless on a scratch snapshot at BELOW_NORMAL priority, with every temp / user-data
# folder inside the snapshot (nothing on C:), so a review run never competes with Codex's own timing-sensitive runs.
# usage: run_godot_low.sh <snapshot_dir> <res_script> [godot user args after --]
proj="$1"; script="$2"; shift 2
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
mkdir -p "$proj/.cache/tmp" "$proj/.cache/godot_appdata" "$proj/.cache/godot_localappdata"
export TMP="$(cygpath -w "$proj/.cache/tmp")" TEMP="$(cygpath -w "$proj/.cache/tmp")" TMPDIR="$(cygpath -w "$proj/.cache/tmp")"
export APPDATA="$(cygpath -w "$proj/.cache/godot_appdata")" LOCALAPPDATA="$(cygpath -w "$proj/.cache/godot_localappdata")"
exec python -B "$ROOT/.cache/claude_scratch/item1_review/lowrun.py" "D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64_console.exe" --headless --path "$(cygpath -w "$proj")" -s "$script" -- "$@"
