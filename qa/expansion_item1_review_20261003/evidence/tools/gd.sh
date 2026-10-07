#!/usr/bin/env bash
# Claude review helper: run a Godot script headless on a scratch snapshot; temp files and Godot user data stay on D:
# usage: gd.sh <proj_dir> <res_script> [extra godot user args after --]
proj="$1"; script="$2"; shift 2
mkdir -p "$proj/.cache/tmp" "$proj/.cache/godot_appdata" "$proj/.cache/godot_localappdata"
export TMP="$(cygpath -w "$proj/.cache/tmp")" TEMP="$(cygpath -w "$proj/.cache/tmp")" TMPDIR="$(cygpath -w "$proj/.cache/tmp")"
export APPDATA="$(cygpath -w "$proj/.cache/godot_appdata")" LOCALAPPDATA="$(cygpath -w "$proj/.cache/godot_localappdata")"
"D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64_console.exe" --headless --path "$(cygpath -w "$proj")" -s "$script" -- "$@"
