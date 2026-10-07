"""Claude scratch (room rule 1D): break each rule of the room-rule mechanism on the real tree, one mutant at a time,
run room_rule_smoke.gd directly (below-normal priority, bounded), restore from byte backups in a finally block and
compare the bytes with the backups at the end. Usage: python mutate_room_rule.py [name ...]   (cwd = project root)."""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / ".cache/claude_scratch/room_rule_mut"
BK = WORK / "backup"
OUT = WORK / "out"
RUNNER = ROOT / ".cache/claude_scratch/item1_review/run_godot_low.sh"
RR = "scripts/combat/room_rule.gd"
ST = "scripts/missions/story_stage_01.gd"
HUD = "scripts/ui/story_stage_hud.gd"
DAT = "data/progression/room_rules.json"
M3 = "data/missions/MIS_CH01_03.json"


def json_rule(select, rule):
    """A transform that puts `rule` on the first room `select(room)` accepts (mission file text in, text out)."""
    def transform(text):
        data = json.loads(text)
        for key in ("main_route", "optional_rooms"):
            for room in data.get(key, []):
                if select(room):
                    room["rule"] = rule
                    return json.dumps(data, ensure_ascii=False, indent=2)
        raise AssertionError("no room selected")
    return transform


def has_wave(room):
    return room.get("type") in ("COMBAT", "ELITE") and bool(room.get("reinforcements"))


def boss(room):
    return room.get("type") == "BOSS"


MUTANTS = [
    # name, file, pairs of (old, new) or a text transform, expected: "caught" (test must fail) or "pass" (a legitimate change)
    ("timer_boundary_gt", RR, [("elapsed >= float(rule.get(\"seconds\", INF))", "elapsed > float(rule.get(\"seconds\", INF))")], "caught"),
    ("timer_ignores_wave_wait", RR, [("wave_pending and wave_wait <= 0.0 and elapsed", "wave_pending and elapsed")], "caught"),
    ("timer_ignores_pending", RR, [("== \"OVERRUN\" and wave_pending and wave_wait <= 0.0 and elapsed", "== \"OVERRUN\" and wave_wait <= 0.0 and elapsed")], "caught"),
    ("clock_not_reset_on_call", ST, [("    _wave_index += 1\n    _room_rule_clock = 0.0\n", "    _wave_index += 1\n")], "caught"),
    ("line_not_refreshed_on_call", ST, [("    _refresh_room_rule_line()\n    queue_redraw()\n", "    queue_redraw()\n")], "caught"),
    ("entry_wait_changed", ST, [("_wave_wait = 1.4 if enemies_alive > 0 else 2.2", "_wave_wait = 1.4")], "caught"),
    ("thinned_path_no_call", ST, [("        _call_reinforcements()\n        return\n    if enemies_alive == 0:", "        pass\n        return\n    if enemies_alive == 0:")], "caught"),
    ("tick_not_called", ST, [("    _tick_room_rule(_delta)\n", "")], "caught"),
    ("rule_never_begun", ST, [("    _begin_room_rule(node)\n", "")], "caught"),
    ("rule_in_simulator", ST, [("if battle_preview or not node.has(\"rule\"): return", "if not node.has(\"rule\"): return")], "caught"),
    ("rule_survives_clear", ST, [("        _room_rule = {}\n        _set_room_rule_line(\"\")\n        preload(", "        preload(")], "caught"),
    ("rule_inherited_by_next_room", ST, [("    _room_rule = {}\n    _room_rule_clock = 0.0\n    _set_room_rule_line(\"\")\n    if battle_preview", "    if battle_preview")], "caught"),
    ("tip_missing", ST, [("    if not _room_rule.is_empty(): tips.append(RoomRule.tip(str(_room_rule.type)))\n", "")], "caught"),
    ("boss_room_allowed", RR, [("if str(room.get(\"type\", \"\")) == \"BOSS\":", "if false:")], "caught"),
    ("no_wave_check_dropped", RR, [("if bool(spec.get(\"needs_reinforcements\", false)) and (room.get(\"reinforcements\", []) as Array).is_empty():", "if false:")], "caught"),
    ("seconds_floor_dropped", RR, [("float(value) < float(spec.get(\"min_seconds\", 0.0)) or ", "")], "caught"),
    ("seconds_ceiling_dropped", RR, [(" or float(value) > float(spec.get(\"max_seconds\", INF))", "")], "caught"),
    ("hud_countdown_floor", RR, [("int(ceil(float(rule.get(\"seconds\", 0.0)) - elapsed))", "int(floor(float(rule.get(\"seconds\", 0.0)) - elapsed))")], "caught"),
    ("hud_shown_while_wave_inbound", RR, [(" or not wave_pending or wave_wait > 0.0: return \"\"", " or not wave_pending: return \"\"")], "caught"),
    ("hud_label_overlaps_intel", HUD, [("Vector2(924, 100), 13, W.RED", "Vector2(858, 84), 13, W.RED")], "caught"),
    ("hud_label_off_screen", HUD, [("Vector2(924, 100), 13, W.RED", "Vector2(1100, 100), 13, W.RED")], "caught"),
    ("data_default_seconds_30", DAT, [("\"seconds\": 45.0,", "\"seconds\": 30.0,")], "caught"),
    ("data_min_seconds_5", DAT, [("\"min_seconds\": 20.0", "\"min_seconds\": 5.0")], "caught"),
    ("data_tip_too_long", DAT, [("\"tip\": \"OVERRUN: the next wave comes on a timer,", "\"tip\": \"OVERRUN: the next wave comes on a timer and, so that the transmission panel has to wrap onto many lines, then some more words follow here,")], "caught"),
    ("mission_row_bad_seconds", M3, json_rule(has_wave, {"type": "OVERRUN", "seconds": 5}), "caught"),
    ("mission_row_on_boss", M3, json_rule(boss, {"type": "OVERRUN"}), "caught"),
    ("mission_row_valid_placement", M3, json_rule(has_wave, {"type": "OVERRUN", "seconds": 40}), "pass"),
]


def busy():
    cmd = "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'Godot*' -or $_.CommandLine -like '*[r]un_regression_suite*' } | ForEach-Object { '{0} {1}' -f $_.ProcessId, $_.Name }"
    return subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd], capture_output=True).stdout.decode("utf-8", "replace").strip()


def run_test(tag):
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    p = subprocess.run(["bash", str(RUNNER), str(ROOT), "res://tests/smoke/room_rule_smoke.gd", "--out=res://.cache/claude_scratch/room_rule_mut/out/%s.json" % tag],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env={**os.environ, "LOWRUN_TIMEOUT": "150"})
    text = p.stdout + p.stderr
    fails = [l[6:].strip() for l in text.splitlines() if l.startswith("FAIL:")]
    m = re.findall(r"ROOM_RULE_SMOKE: (PASS|FAIL) \((\d+) checks", text)
    script_err = len([l for l in text.splitlines() if "SCRIPT ERROR" in l or "Parse Error" in l])
    return {"tag": tag, "exit": p.returncode, "secs": round(time.time() - t0), "result": m[-1][0] if m else "NONE", "checks": int(m[-1][1]) if m else 0,
            "failed_checks": len(fails), "script_errors": script_err, "first": [f[:150] for f in fails[:3]]}


def main():
    names = sys.argv[1:] or [m[0] for m in MUTANTS]
    files = sorted({m[1] for m in MUTANTS})
    BK.mkdir(parents=True, exist_ok=True)
    reason = busy()
    if reason:
        raise SystemExit("another Godot / runner is alive:\n" + reason)
    for rel in files:
        shutil.copy2(ROOT / rel, BK / rel.replace("/", "__"))
    rows = []
    try:
        rows.append(run_test("control"))
        print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
        for name, rel, change, expect in MUTANTS:
            if name not in names:
                continue
            path = ROOT / rel
            text = (BK / rel.replace("/", "__")).read_text(encoding="utf-8")
            if callable(change):
                new_text = change(text)
            else:
                new_text = text
                for old, new in change:
                    assert new_text.count(old) == 1, (name, new_text.count(old), old[:70])
                    new_text = new_text.replace(old, new)
            path.write_text(new_text, encoding="utf-8", newline="\n")
            try:
                row = run_test(name)
            finally:
                shutil.copy2(BK / rel.replace("/", "__"), path)
            row["expect"] = expect
            row["verdict"] = "CAUGHT" if (row["result"] != "PASS" or row["script_errors"] or row["exit"] != 0) else "SURVIVED"
            row["as_expected"] = (row["verdict"] == "CAUGHT") == (expect == "caught")
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
    finally:
        for rel in files:
            shutil.copy2(BK / rel.replace("/", "__"), ROOT / rel)
    same = all((ROOT / rel).read_bytes() == (BK / rel.replace("/", "__")).read_bytes() for rel in files)
    print("RESTORED_BYTES_EQUAL", same, flush=True)
    (WORK / "mutants.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def check():
    """Every mutant must apply to the current tree exactly once; nothing is written."""
    bad = 0
    for name, rel, change, expect in MUTANTS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        try:
            if callable(change):
                change(text)
            else:
                for old, new in change:
                    n = text.count(old)
                    assert n == 1, "%d matches for %r" % (n, old[:70])
            print("ok   ", name)
        except AssertionError as error:
            bad += 1
            print("BAD  ", name, error)
    print("mutants", len(MUTANTS), "bad", bad)
    return bad


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        sys.exit(1 if check() else 0)
    main()
