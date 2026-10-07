"""Claude scratch (T-5/T-6 fixes): break each new rule on the real tree one at a time, run lab_geometry, restore from backups.
Always restores in a finally block and compares the bytes with the backups at the end."""
import json, re, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BK = ROOT / ".cache/claude_scratch/t567/backup"
FILES = {"hud": "scripts/ui/story_stage_hud.gd", "lobby": "scripts/ui/base_lobby.gd"}
HUD_POS = 'Vector2(924, 82), 11, Color("5d827f")'
MUTANTS = [
  ("hud_box_old_position", "hud", [(HUD_POS, 'Vector2(616, 82), 11, Color("5d827f")'), ("_intel_label.size = Vector2(332, 16)", "_intel_label.size = Vector2(640, 16)")]),
  ("hud_box_too_narrow", "hud", [("_intel_label.size = Vector2(332, 16)", "_intel_label.size = Vector2(250, 16)")]),
  ("lobby_samples_abbreviations", "lobby", [("IntelSamples.named_counts(intel)", 'IntelSamples.counts(intel," ")')]),
  ("lobby_no_second_line", "lobby", [("var two_lines:=not choices.is_empty()", "var two_lines:=false")]),
  ("lobby_bracket_first_not_equipped", "lobby", [('"[%s]"%names[j] if j==selected else names[j]', '"[%s]"%names[j] if j==0 else names[j]')]),
  ("lobby_never_brackets", "lobby", [('"[%s]"%names[j] if j==selected else names[j]', "names[j]")]),
  ("lobby_listing_font_9", "lobby", [("_fit_lab_label(listing,10,list_box)", "_fit_lab_label(listing,9,list_box)")]),
  ("lobby_listing_overlaps_first_line", "lobby", [("listing.position=Vector2(0,y+19)", "listing.position=Vector2(0,y+16)")]),
  ("lobby_listing_runs_into_button", "lobby", [("var list_box:=Vector2(240,16)", "var list_box:=Vector2(300,16)")]),
]

def run_lab(tag):
    out = ROOT / ".cache/t567/out" / tag
    out.mkdir(parents=True, exist_ok=True)
    env_cmd = ["bash", str(ROOT / ".cache/claude_scratch/item1_review/run_godot_low.sh"), str(ROOT), "res://tests/smoke/lab_geometry_smoke.gd",
               "--out=res://.cache/t567/out/%s/lab_geometry.json" % tag]
    t0 = time.time()
    p = subprocess.run(env_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env={**__import__("os").environ, "LOWRUN_TIMEOUT": "150"})
    text = p.stdout + p.stderr
    errs = [l for l in text.splitlines() if l.startswith(("ERROR:", "FAIL:")) and "resources still in use" not in l]
    m = re.findall(r"LAB_GEOMETRY_SMOKE: (PASS|FAIL) \((\d+) checks\)", text)
    script_err = len([l for l in text.splitlines() if "SCRIPT ERROR" in l or "Parse Error" in l])
    return {"tag": tag, "exit": p.returncode, "secs": round(time.time() - t0), "result": m[-1][0] if m else "NONE", "checks": int(m[-1][1]) if m else 0,
            "failed": len(errs), "script_errors": script_err, "first": [e[:130] for e in errs[:3]]}

def main():
    names = sys.argv[1:] or [m[0] for m in MUTANTS]
    for key, rel in FILES.items():
        shutil.copy2(ROOT / rel, BK / (key + ".gd"))
    rows = []
    try:
        rows.append(run_lab("control"))
        print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
        for name, key, pairs in MUTANTS:
            if name not in names: continue
            path = ROOT / FILES[key]
            text = (BK / (key + ".gd")).read_text(encoding="utf-8")
            for old, new in pairs:
                assert text.count(old) == 1, (name, text.count(old), old[:60])
                text = text.replace(old, new)
            path.write_text(text, encoding="utf-8", newline="\n")
            try:
                rows.append(run_lab(name))
            finally:
                shutil.copy2(BK / (key + ".gd"), path)
            print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
    finally:
        for key, rel in FILES.items():
            shutil.copy2(BK / (key + ".gd"), ROOT / rel)
    same = all((ROOT / rel).read_bytes() == (BK / (key + ".gd")).read_bytes() for key, rel in FILES.items())
    print("RESTORED_BYTES_EQUAL", same)
    (ROOT / ".cache/t567/mutants.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

main()
