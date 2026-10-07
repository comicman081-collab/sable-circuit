#!/usr/bin/env bash
# Claude review helper: scratch copy of the project at one commit (never the shared working tree).
# usage: make_snapshot.sh <name> <commit>      -> .cache/claude_scratch/<name>
# Six directory junctions point back into the main project (5 art dirs + .godot/imported); drop_snapshot.sh removes them first.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
name="$1"; commit="$2"
d=".cache/claude_scratch/$name"
[ ! -e "$d" ] || { echo "already exists: $d"; exit 1; }
mkdir -p "$d/.godot"
git archive "$commit" scripts scenes data tests schemas project.godot | tar -x -C "$d"
for n in assets art_src motion_lab_v1 sound third_party; do
  cmd //c mklink //J "$(cygpath -w "$ROOT/$d/$n")" "$(cygpath -w "$ROOT/$n")" > /dev/null
done
cmd //c mklink //J "$(cygpath -w "$ROOT/$d/.godot/imported")" "$(cygpath -w "$ROOT/.godot/imported")" > /dev/null
cp .godot/.gdignore .godot/global_script_class_cache.cfg .godot/uid_cache.bin "$d/.godot/"
date +%Y-%m-%dT%H:%M:%S > "$d/.godot/regression_import.stamp"
echo "$name <- $commit : $(find "$d" -type f -not -path "*/.godot/imported/*" 2>/dev/null | wc -l) own files, 6 junctions"
