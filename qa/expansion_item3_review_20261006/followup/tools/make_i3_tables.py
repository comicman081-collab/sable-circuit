"""Claude review helper (item 3): turn i3_matrix.jsonl into the Markdown mutation table of the record.
usage: make_i3_tables.py <i3_matrix.jsonl> <out .md>      (run from the project root)
A cell is  `-`  when the test passed,  `n/T`  when it failed with n failing checks of T (the unbroken run's total),  `SE`  for a script
error (not a catch by a check, but the runner shows it red),  `HANG`  when the 200 s / 700 s limit stopped a process that never reached
quit()  (the runner shows that red as TIMEOUT),  blank when that mutant does not run that test."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mutate_i3 import M  # noqa: E402

EXPECT_PASS = {"research_plus_52"}            # the boundary of the economy band: it must stay green
TESTS = ["intel_supply", "module_expansion", "weapon_expansion", "lab_geometry", "contract_save", "m10_persistence", "m13_migration",
         "upgrade_economy", "m10_base_ui", "m10_intel", "m13_loadout", "campaign", "lab_capture_geometry", "hit_hurt_vfx",
         "m13_campaign", "m13_runtime"]
SHORT = {"intel_supply": "intel", "module_expansion": "module", "weapon_expansion": "weapon", "lab_geometry": "lab", "contract_save": "csave",
         "m10_persistence": "m10p", "m13_migration": "m13mig", "upgrade_economy": "econ", "m10_base_ui": "m10ui", "m10_intel": "m10intel",
         "m13_loadout": "m13load", "campaign": "campaign", "lab_capture_geometry": "labcap", "hit_hurt_vfx": "hitvfx",
         "m13_campaign": "m13camp", "m13_runtime": "m13run"}

rows = [json.loads(l) for l in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.strip()]
base = {}
last = {}
for r in rows:
    if r["mutant"] == "base":
        base[r["test"]] = r                      # a later baseline of the same test wins
    last[(r["mutant"], r["test"])] = r           # a later run of the same mutant wins


def total_of(test):
    b = base.get(test)
    if not b:
        return "?"
    m = re.search(r"(\d+)\s+checks?", b["result"] or "")
    if m:
        return m.group(1)
    n = int(b["pass_lines"]) + int(b["error_lines"])
    return str(n) if n else "?"


BASE_ERR = {t: int(base[t]["error_lines"]) for t in base}


def cell(r):
    if r is None:
        return ""
    if r["exit"] == "124":
        return "HANG"
    if int(r["script_errors"]) > 0:
        return "SE"
    if "FAIL" in (r["result"] or "") or r["exit"] != "0":
        n = max(0, int(r["error_lines"]) - BASE_ERR.get(r["test"], 0))
        return "**%d/%s**" % (n, total_of(r["test"]))
    return "-"


used = [t for t in TESTS if any(k[1] == t for k in last)]
out = []
out.append("| 부순 곳 | 설명 | " + " | ".join(SHORT[t] for t in used) + " | 잡은 시험 수 |")
out.append("|---|---|" + "---|" * len(used) + "---|")
uncaught = []
boundary = []
for name, (desc, _tests, _p) in M.items():
    cells = [cell(last.get((name, t))) for t in used]
    caught = sum(1 for c in cells if c.startswith("**") or c in ("SE", "HANG"))
    if name in EXPECT_PASS:
        boundary.append((name, caught))
    elif caught == 0:
        uncaught.append(name)
    if all(c == "" for c in cells):
        continue                                   # a mutant that has not been run yet
    out.append("| `%s` | %s | %s | %d |" % (name, desc, " | ".join(cells), caught))
out.append("")
out.append("칸: `-` 통과(못 잡음), `n/T` 변형 없는 실행의 전체 T개 중 n개 검사가 실패(잡음), `SE` 스크립트 오류로 멈춤, `HANG` 스크립트 오류 뒤 종료하지 못하고 시간 제한에서 중단(러너는 TIMEOUT으로 빨갛게 표시), 빈칸은 그 변형이 해당 시험을 돌리지 않음. 마지막 열은 SE·HANG을 포함해 빨갛게 된 시험 수.")
out.append("")
out.append("기준(변형 없음) 줄의 `ERROR:` 개수: " + (", ".join("%s %d" % (SHORT[t], BASE_ERR[t]) for t in BASE_ERR if BASE_ERR[t]) or "모두 0"))
out.append("기준 줄의 전체 검사 수: " + ", ".join("%s %s" % (SHORT[t], total_of(t)) for t in used if t in base))
out.append("")
out.append("아무 시험도 못 잡은 변형 %d개: %s" % (len(uncaught), ", ".join("`%s`" % u for u in uncaught) if uncaught else "없음"))
for name, caught in boundary:
    out.append("경계 확인 `%s`: 잡힌 시험 %d개 (0이어야 정상)" % (name, caught))
text = "\n".join(out) + "\n"
Path(sys.argv[2]).write_text(text, encoding="utf-8", newline="\n")
sys.stdout.buffer.write(text.encode("utf-8"))
