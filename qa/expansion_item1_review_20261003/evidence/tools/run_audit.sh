#!/usr/bin/env bash
cd "D:/AI 종합 폴더/Games/Sable-circuit"
G=.cache/claude_scratch/item1_review/gd.sh
$G .cache/claude_scratch/proj_after res://.cache/probe/nav_pocket_audit.gd --cell=12 --out=res://.cache/probe/nav_audit_after.json 2>&1 | grep -E "^AUDIT|NAV_POCKET_AUDIT|SCRIPT ERROR|Parse Error"
echo "DONE"
