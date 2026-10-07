#!/usr/bin/env bash
# Claude review helper: remove a scratch snapshot safely. Junctions are unlinked first (cmd rmdir, no recursion),
# the delete is gated on a zero reparse-point count, and the main project's directory counts are checked afterwards.
# usage: drop_snapshot.sh <name>
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
name="$1"; d=".cache/claude_scratch/$name"
[ -d "$d" ] || { echo "no such snapshot: $d"; exit 0; }
case "$name" in proj_*) ;; *) echo "refusing: name must start with proj_"; exit 1;; esac
before=""; for n in art_src assets motion_lab_v1 sound third_party .godot/imported; do before="$before $n=$(ls -A "$n" | wc -l)"; done
for l in assets art_src motion_lab_v1 sound third_party .godot/imported; do
  if [ -e "$d/$l" ]; then cmd //c rmdir "$(cygpath -w "$ROOT/$d/$l")" > /dev/null || { echo "could not unlink $l"; exit 1; }; fi
done
left=$(powershell -NoProfile -Command "(Get-ChildItem -LiteralPath '$d' -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { \$_.Attributes -band [IO.FileAttributes]::ReparsePoint } | Measure-Object).Count" | tr -d '\r')
if [ "$left" != "0" ]; then echo "reparse points left in $d: $left -- NOT deleting"; exit 1; fi
rm -rf "$d"
after=""; for n in art_src assets motion_lab_v1 sound third_party .godot/imported; do after="$after $n=$(ls -A "$n" | wc -l)"; done
if [ "$before" = "$after" ]; then echo "dropped $name; main directories unchanged:$after"; else echo "WARNING counts differ"; echo "before:$before"; echo "after: $after"; exit 1; fi
