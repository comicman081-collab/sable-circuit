"""Claude scratch (T-5/T-6/T-7): assemble qa/expansion_item3_review_20261006/followup_t567/ from the scratch outputs.

Run only when no runner is alive (it writes under qa/).
usage: python -B build_evidence.py <quick run folder name> <only4 run folder name>"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "qa/expansion_item3_review_20261006/followup_t567"
SCR = ROOT / ".cache/claude_scratch/t567"
OUT = ROOT / ".cache/t567"
RUNS = ROOT / "qa/regression_runs"
quick, only4 = sys.argv[1], sys.argv[2]

for sub in ("runs", "native", "break", "probes", "tools"):
    (DEST / sub).mkdir(parents=True, exist_ok=True)

# runs: summaries (the runner folders are git-ignored) and the line-up against the previous quick run
for stamp, tag in ((quick, "quick"), (only4, "only4")):
    shutil.copy2(RUNS / stamp / "summary.json", DEST / "runs" / ("%s_%s_summary.json" % (tag, stamp)))
    shutil.copy2(RUNS / stamp / "SUMMARY_KO.md", DEST / "runs" / ("%s_%s_SUMMARY_KO.md" % (tag, stamp)))
shutil.copy2(SCR / "tested_blobs.txt", DEST / "runs/tested_blobs.txt")

# native: reports and three of the seven PNGs (the PNGs are git-ignored; the report binds all seven by SHA-256)
for name in ("capture_report.json",):
    shutil.copy2(OUT / "native_after" / name, DEST / "native" / name)
shutil.copy2(OUT / "validator_report.json", DEST / "native/validator_report.json")
shutil.copy2(OUT / "native_after.log", DEST / "native/native_after.log")
for name in ("lab_page1.png", "lab_module_cycle.png", "field_intel8.png"):
    shutil.copy2(OUT / "native_after" / name, DEST / "native" / name)

# break: the raw rows and a table
rows = [json.loads(line) for line in (OUT / "mutants.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
shutil.copy2(OUT / "mutants.jsonl", DEST / "break/mutants.jsonl")
lines = ["| 변형 | 종료 코드 | 결과 | 실패 / 검사 | 스크립트 오류 | 첫 실패 검사 |", "|---|---|---|---|---|---|"]
for r in rows:
    first = (r["first"][0].replace("ERROR: ", "") if r["first"] else "—").replace("|", "/")
    lines.append("| `%s` | %s | %s | %d / %s | %d | %s |" % (r["tag"], r["exit"], r["result"], r["failed"], format(r["checks"], ","), r["script_errors"], first))
(DEST / "break/mutants_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

# probes: outputs written by the re-run, plus the before / after import logs
for name in ("module_rows_probe_out.txt", "ui_probe_out.txt"):
    src = OUT / "probes" / name
    if src.exists():
        shutil.copy2(src, DEST / "probes" / name)
imp = ["러너가 Godot를 다시 가져올 때(`_import.log`) 음악 원본 `fps_bgm_06_sniper_ridge.wav`에서 나는 오류 줄 수. `keep` 설정(T-7) 앞뒤.", ""]
for f in sorted(RUNS.glob("*/logs/_import.log")):
    text = f.read_text(encoding="utf-8", errors="replace")
    imp.append("%-34s ERROR %d   Not a WAV %d" % (f.parent.parent.name, len(re.findall(r"^ERROR", text, re.M)), text.count("Not a WAV")))
(DEST / "probes/import_logs_before_after.txt").write_text("\n".join(imp) + "\n", encoding="utf-8", newline="\n")

# tools
for src in (SCR / "mutate_t567.py", SCR / "compare_quick.py", SCR / "build_evidence.py", ROOT / ".cache/probes/ui_probe.gd", ROOT / ".cache/probes/module_rows_probe.gd"):
    shutil.copy2(src, DEST / "tools" / src.name)
print("built", DEST)
