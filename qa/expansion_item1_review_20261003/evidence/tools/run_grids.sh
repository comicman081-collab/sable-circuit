#!/usr/bin/env bash
cd "D:/AI 종합 폴더/Games/Sable-circuit"
G=.cache/claude_scratch/item1_review/gd.sh
for p in proj_base proj_after; do
  echo "== $p grid 25 all missions" 
  $G .cache/claude_scratch/$p res://.cache/probe/hazard_escape_grid.gd --grid=25 --out=res://.cache/probe/escape_$p.json 2>&1 | grep -E "^ROOM|HAZARD_ESCAPE_GRID|SCRIPT ERROR|Parse Error" 
done
echo "DONE"
