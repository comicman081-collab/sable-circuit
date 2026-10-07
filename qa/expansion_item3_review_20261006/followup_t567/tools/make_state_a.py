"""Claude scratch (T-5/T-6/T-7): build the working tree of the FIRST commit (T-5 alone) so lab_geometry can be run on it.

State A = HEAD lobby + HEAD intel_samples + HEAD test with only the HUD hunk + the new HUD box.
That is exactly the tree one gets by reverting the T-6 commit later, so the "veto T-6" path is tested too.
usage: python -B make_state_a.py        (backs up the full state first; restore with restore_full.py)"""
import hashlib
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BK = ROOT / ".cache/claude_scratch/t567/state_full"
FILES = [
    "scripts/core/intel_samples.gd",
    "scripts/ui/base_lobby.gd",
    "scripts/ui/story_stage_hud.gd",
    "sound/music/originals/fps_bgm_06_sniper_ridge.wav.import",
    "tests/smoke/lab_geometry_smoke.gd",
]
tested = {}
for line in (ROOT / ".cache/claude_scratch/t567/tested_blobs.txt").read_text(encoding="utf-8").splitlines():
    sha, path = line.split(None, 1)
    tested[path.strip()] = sha


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def head(path: str) -> bytes:
    return subprocess.run(["git", "show", "HEAD:" + path], cwd=ROOT, capture_output=True, check=True).stdout


BK.mkdir(parents=True, exist_ok=True)
for rel in FILES:
    src = ROOT / rel
    assert blob(src) == tested[rel], ("working file is not the tested one", rel)
    dst = BK / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

# lobby and intel_samples back to HEAD
for rel in ("scripts/core/intel_samples.gd", "scripts/ui/base_lobby.gd"):
    (ROOT / rel).write_bytes(head(rel))

# test: HEAD + only the HUD hunk
anchor = b'        text_fit(stage.hud._intel_label,"HUD intel")\n'
add = (b'        var intel_box:Rect2=stage.hud._intel_label.get_global_rect()\n'
       b'        check(not intel_box.intersects(stage.hud._transmission_panel.get_global_rect()),"HUD intel box stays clear of the transmission panel")\n'
       b'        check(Rect2(0,0,1280,720).encloses(intel_box),"HUD intel box stays on screen")\n')
text = head("tests/smoke/lab_geometry_smoke.gd")
assert text.count(anchor) == 1
(ROOT / "tests/smoke/lab_geometry_smoke.gd").write_bytes(text.replace(anchor, anchor + add))
print("state A built; full state backed up under", BK)
