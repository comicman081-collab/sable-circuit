"""Claude review helper (item 2): compare what the OLD (7b26a152) and NEW (item 2) code make of the same save file."""
import json
import sys
from pathlib import Path

P = Path(sys.argv[1])
out = []
inputs = ["player_v3", "old_v4", "codex_v3", "codex_v4", "new_v5"]
out.append("| 입력 저장 | 옛 코드가 읽음 | 새 코드가 읽음 | 공통 키 전부 같음 | 새 코드의 `redline_cleared` | 새 코드: 쓰고 다시 읽어도 같음 | 옛 코드: 쓰고 다시 읽어도 같음 |")
out.append("|---|---|---|---|---|---|---|")
bad = 0
for x in inputs:
    o = json.loads((P / "proj_head/.cache/out" / f"probe_old__{x}.json").read_text(encoding="utf-8"))
    n = json.loads((P / "proj_ic/.cache/out" / f"probe_new__{x}.json").read_text(encoding="utf-8"))
    os_, ns = o["snapshot"], n["snapshot"]
    diff_keys = sorted(k for k in set(os_) | set(ns) if k not in ("schema_version", "redline_cleared") and os_.get(k) != ns.get(k))
    extra = sorted(set(ns) - set(os_))
    same_core = not diff_keys and o["run_serial"] == n["run_serial"] and o["committed_run_ids"] == n["committed_run_ids"]
    new_rt = n["reread_snapshot"] == n["snapshot"] and n["reread_run_serial"] == n["run_serial"] and n["reread_committed_run_ids"] == n["committed_run_ids"]
    old_rt = o["reread_snapshot"] == o["snapshot"] and o["reread_run_serial"] == o["run_serial"]
    if not same_core or not new_rt:
        bad += 1
    out.append("| `%s` | schema %s 상수 %s | schema 상수 %s | %s%s | %s | %s | %s |" % (
        x, os_.get("schema_version"), o["schema_const"], n["schema_const"],
        "예" if same_core else "**아니오**: " + ", ".join(diff_keys), (" (새 코드에만 있는 키: " + ", ".join(extra) + ")") if extra else "",
        n["redline_cleared"], "예" if new_rt else "**아니오**", "예" if old_rt else "아니오"))
print("\n".join(out))
(P.parent / "claude_scratch/item2_review/evidence").mkdir(parents=True, exist_ok=True)
Path(sys.argv[2]).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print("BAD:", bad)
