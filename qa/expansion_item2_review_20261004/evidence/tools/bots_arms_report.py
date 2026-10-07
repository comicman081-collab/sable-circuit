"""Claude review helper (item 2): turn bots_arms.jsonl into the Markdown table of the record.
usage: bots_arms_report.py <bots_arms.jsonl> <out .md>
Counts, not verdicts: a bot is one scripted player, this PC's load moves its outcomes, and no human play is recorded."""
import json
import sys
from collections import defaultdict
from pathlib import Path

rows = [json.loads(l) for l in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.strip()]
ARMS = ["neutral", "default", "redline"]
LABEL = {"neutral": "중립 계약(러너의 `full_op_01`과 같은 호출)", "default": "실제 run id의 기본 제안(`build`)", "redline": "REDLINE"}
by = defaultdict(list)
for r in rows:
    by[r["arm"]].append(r)
out = []
out.append("| 갈래 | 판 수 | 추출 | 전멸·기타 | 걸린 시간(s) | 받은 피해(HP) | 마지막 방 깊이 |")
out.append("|---|---:|---:|---:|---|---|---|")
for arm in ARMS:
    rs = sorted(by.get(arm, []), key=lambda r: int(r["round"]))
    if not rs:
        continue
    ok = [r for r in rs if r.get("outcome") == "EXTRACTED" and not r.get("failures")]
    out.append("| %s | %d | **%d** | %d | %s | %s | %s |" % (
        LABEL[arm], len(rs), len(ok), len(rs) - len(ok),
        " / ".join(str(r.get("elapsed", "?")) for r in rs),
        " / ".join(str(r.get("damage", "?")) for r in rs),
        " / ".join(str(r.get("depth", "?")) for r in rs)))
out.append("")
out.append("판별 상세:")
out.append("")
out.append("| 라운드 | 갈래 | 계약 | 결과 | 시간(s) | 피해 | 깊이 | 실패한 검사 |")
out.append("|---:|---|---|---|---:|---:|---:|---|")
for r in sorted(rows, key=lambda r: (int(r["round"]), ARMS.index(r["arm"]) if r["arm"] in ARMS else 9)):
    out.append("| %s | %s | `%s` | %s | %s | %s | %s | %s |" % (
        r["round"], r["arm"], r.get("contract", ""), r.get("outcome", r.get("error", "?")), r.get("elapsed", "?"), r.get("damage", "?"),
        r.get("depth", "?"), "; ".join(str(f)[:60] for f in r.get("failures", [])) or "-"))
Path(sys.argv[2]).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))
