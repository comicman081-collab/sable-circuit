"""Claude review helper (item 2): turn ic_matrix.jsonl into the Markdown mutation table of the record.
usage: make_ic_tables.py <ic_matrix.jsonl> <out .md>      (run from the project root)
A cell is  `-`  when the test passed,  `n/T`  when it failed with n failing checks of T,  `SE`  for a script error (not a catch)."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mutate_ic import M  # noqa: E402

rows = [json.loads(l) for l in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.strip()]
base = {}
last = {}
for r in rows:
    if r["mutant"] == "base":
        base[r["test"]] = r
    last[(r["mutant"], r["test"])] = r          # a later run of the same mutant wins
TESTS = ["contract_offers", "contract_ui", "redline", "contract_save", "run_contract", "play_log", "boss_duel", "campaign"]
SHORT = {"contract_offers": "offers", "contract_ui": "ui", "redline": "redline", "contract_save": "save", "run_contract": "m11", "play_log": "playlog", "boss_duel": "duel", "campaign": "campaign"}
BASE_ERR = {t: int(base[t]["error_lines"]) for t in base}


def cell(r):
    if r is None:
        return ""
    if float(r["wall_s"]) >= 190:
        return "HANG"                      # the process never reached quit(): a crash after a script error, stopped by a timeout
    if int(r["script_errors"]) > 0:
        return "SE"
    m = re.search(r"\((\d+) checks", r["result"] or "")
    total = m.group(1) if m else "?"
    if "FAIL" in (r["result"] or "") or r["exit"] != "0":
        n = max(0, int(r["error_lines"]) - BASE_ERR.get(r["test"], 0))
        return "**%d/%s**" % (n, total)
    return "-"


out = []
out.append("| 부순 곳 | 설명 | " + " | ".join(SHORT[t] for t in TESTS) + " | 잡은 시험 수 |")
out.append("|---|---|" + "---|" * len(TESTS) + "---|")
uncaught = []
for name, (desc, _tests, _p) in M.items():
    cells = [cell(last.get((name, t))) for t in TESTS]
    caught = sum(1 for c in cells if c.startswith("**") or c in ("SE", "HANG"))   # SE / HANG: the runner shows these red as well
    if caught == 0 and name != "mission_id_restored":
        uncaught.append(name)
    out.append("| `%s` | %s | %s | %d |" % (name, desc, " | ".join(cells), caught))
out.append("")
out.append("칸: `-` 통과(못 잡음), `n/T` 전체 T개 중 n개 검사가 실패(잡음), `SE` 스크립트 오류로 멈춤, `HANG` 스크립트 오류 뒤 종료하지 못하고 200 s 제한에서 중단(러너는 TIMEOUT으로 빨갛게 표시), 빈칸은 그 변형이 해당 시험을 돌리지 않음. 마지막 열은 SE·HANG을 포함해 빨갛게 된 시험 수.")
out.append("")
out.append("기준(변형 없음) 줄의 `ERROR:` 개수: " + ", ".join("%s %d" % (SHORT[t], BASE_ERR[t]) for t in BASE_ERR if BASE_ERR[t]) + " (play_log가 만들기 전의 폴더를 여는 무해한 한 줄).")
out.append("")
out.append("아무 시험도 못 잡은 변형 %d개: %s" % (len(uncaught), ", ".join("`%s`" % u for u in uncaught) if uncaught else "없음"))
text = "\n".join(out) + "\n"
Path(sys.argv[2]).write_text(text, encoding="utf-8", newline="\n")
sys.stdout.buffer.write(text.encode("utf-8"))
