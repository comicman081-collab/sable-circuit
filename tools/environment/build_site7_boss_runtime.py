#!/usr/bin/env python3
"""Bind the ImageGen boss masters of operations 6-10 to their runtime folders.

For each boss it re-runs the native-alpha gate on the source master, copies the master
byte for byte into `assets/enemies/<folder>/authored_core_v1/`, writes the `spec.json`
the machine sprite reads (fixed root, single top emitter, the machine's own bounds) and
the `.import` sidecar the editor would write. Nothing is keyed, cropped, scaled or
re-encoded, and no art is approved by this tool. `--check` verifies the tree against the
table without writing (the regression runner does not call it; the boss registry smoke
guards the same bindings at run time).

Root: the lowest ground-contact point of the mount, as for the earlier bosses. Emitter:
the centre of the one glowing top node. Both are source pixels measured on the pictures
and checked on marked overlays (`qa/site7_ops_6_10_boss_integration_20260929/`).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "motion_lab_v1"))
import source_alpha_policy as policy  # noqa: E402

RAW = "motion_lab_v1/art/site7_enemies_raw"
# On-screen the field-scale presentation draws a boss at 0.84 of its display size.
FIELD_SCALE = 0.84
# The machine's visible height (alpha >= 128) before the field scale, in world pixels, the way
# the earlier bosses read: RELAY 217, REMNANT 219, CARRIER 195, ANCHOR 266.
BOSSES = [
    {"key": "aerator_tower", "enemy_id": "BOSS_SITE7_AERATOR_01", "folder": "stage6_aerator_tower",
     "png": "AERATOR_TOWER.png", "visible_height": 226.0, "root": (632, 990), "emitter": (632, 324),
     "contract": "stationary spore-bloom node crowning the cap; one omnidirectional top emitter; the five petal louvres and the two planter pods are not independent barrels"},
    {"key": "cryo_compressor", "enemy_id": "BOSS_SITE7_CRYO_01", "folder": "stage7_cryo_compressor",
     "png": "CRYO_COMPRESSOR.png", "visible_height": 236.0, "root": (412, 1216), "emitter": (575, 246),
     "contract": "stationary beacon node on the lattice mast above the compressor block; one omnidirectional top emitter; the radiator wall, manifolds and pipes are not independent barrels"},
    {"key": "signal_gantry", "enemy_id": "BOSS_SITE7_GANTRY_01", "folder": "stage8_signal_gantry",
     "png": "SIGNAL_GANTRY.png", "visible_height": 236.0, "root": (697, 1103), "emitter": (695, 123),
     "contract": "stationary signal-yellow lens cluster at the centre top of the cross-beam; one omnidirectional top emitter; the hanging signal lamps and counterweights are not independent barrels"},
    {"key": "index_spire", "enemy_id": "BOSS_SITE7_ARCHIVE_01", "folder": "stage9_index_spire",
     "png": "INDEX_SPIRE.png", "visible_height": 246.0, "root": (701, 1060), "emitter": (701, 86),
     "contract": "stationary turquoise node at the tip of the needle read-head; one omnidirectional top emitter; the stepped memory tiers are not independent barrels"},
    {"key": "origin_core", "enemy_id": "BOSS_SITE7_ORIGIN_01", "folder": "stage10_origin_core",
     "png": "ORIGIN_CORE.png", "visible_height": 262.0, "root": (616, 1281), "emitter": (614, 100),
     "contract": "stationary white node at the tip of the tallest prism; one omnidirectional top emitter; the two lower prisms and the ribs are not independent barrels"},
]
IMPORT_TEMPLATE = """[remap]

importer="texture"
type="CompressedTexture2D"
uid="uid://{uid}"
path="res://.godot/imported/{name}-{digest}.ctex"
metadata={{
"vram_texture": false
}}

[deps]

source_file="{res}"
dest_files=["res://.godot/imported/{name}-{digest}.ctex"]

[params]

compress/mode=0
compress/high_quality=false
compress/lossy_quality=0.7
compress/uastc_level=0
compress/rdo_quality_loss=0.0
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=false
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/channel_remap/red=0
process/channel_remap/green=1
process/channel_remap/blue=2
process/channel_remap/alpha=3
process/fix_alpha_border=true
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit=0
detect_3d/compress_to=1
"""
UID_ALPHABET = "abcdefghijklmnopqrstuvwxyz01234567"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_uid(res_path: str) -> str:
    """A repeatable uid in Godot's text form (the editor keeps whatever the sidecar holds)."""
    number = int(hashlib.sha256(res_path.encode()).hexdigest(), 16) & ((1 << 62) - 1)
    text = ""
    while number:
        number, digit = divmod(number, len(UID_ALPHABET))
        text = UID_ALPHABET[digit] + text
    return text or "a"


def visible_rect(path: Path) -> list[int]:
    alpha = np.asarray(Image.open(path).convert("RGBA"))[..., 3]
    ys, xs = np.where(alpha >= 128)
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def build_spec(row: dict, size: tuple[int, int], texture_sha: str, rect: list[int]) -> str:
    height = size[1] * row["visible_height"] / (rect[3] - rect[1])
    lines = [
        "{",
        '  "schema_version": 1,',
        f'  "enemy_id": "{row["enemy_id"]}",',
        '  "kind": "anchored_machine",',
        f'  "texture": "res://assets/enemies/{row["folder"]}/authored_core_v1/{row["png"]}",',
        f'  "texture_sha256": "{texture_sha}",',
        f'  "display_height": {round(height):.1f},',
        f'  "root_px": [{row["root"][0]}, {row["root"][1]}],',
        f'  "emitter_px": [{row["emitter"][0]}, {row["emitter"][1]}],',
        f'  "visible_rect_px": [{rect[0]}, {rect[1]}, {rect[2]}, {rect[3]}],',
        '  "emitter_visible": true,',
        f'  "emission_contract": "{row["contract"]}"',
        "}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="verify only; write nothing")
    parser.add_argument("--record", type=Path, help="write the binding table (JSON) here")
    args = parser.parse_args()
    table = []
    failures: list[str] = []
    for row in BOSSES:
        raw = ROOT / RAW / f"{row['key']}_master.png"
        folder = ROOT / "assets" / "enemies" / row["folder"] / "authored_core_v1"
        runtime = folder / row["png"]
        res_png = f"res://assets/enemies/{row['folder']}/authored_core_v1/{row['png']}"
        verdict = policy.inspect_master(raw)
        if not str(verdict.get("status", "")).startswith("PASS"):
            failures.append(f"{row['key']}: source master fails the alpha gate: {verdict}")
            continue
        size = Image.open(raw).size
        rect = visible_rect(raw)
        master_sha = sha256(raw)
        spec_text = build_spec(row, size, master_sha, rect)
        digest = hashlib.md5(res_png.encode()).hexdigest()
        import_text = IMPORT_TEMPLATE.format(uid=stable_uid(res_png), name=row["png"], digest=digest, res=res_png)
        for label, (x, y) in (("root", row["root"]), ("emitter", row["emitter"])):
            if not (0 <= x < size[0] and 0 <= y < size[1]):
                failures.append(f"{row['key']}: {label} {x},{y} is outside the {size} image")
        if args.check:
            if not runtime.is_file() or sha256(runtime) != master_sha:
                failures.append(f"{row['key']}: runtime PNG is missing or not byte-identical to its master")
            spec_path = folder / "spec.json"
            if not spec_path.is_file() or spec_path.read_text(encoding="utf-8") != spec_text:
                failures.append(f"{row['key']}: spec.json is missing or differs from the table")
            if not (folder / f"{row['png']}.import").is_file():
                failures.append(f"{row['key']}: import sidecar missing")
        else:
            folder.mkdir(parents=True, exist_ok=True)
            runtime.write_bytes(raw.read_bytes())
            (folder / "spec.json").write_text(spec_text, encoding="utf-8", newline="\n")
            sidecar = folder / f"{row['png']}.import"
            if not sidecar.exists():
                sidecar.write_text(import_text, encoding="utf-8", newline="\n")
        spec_sha = hashlib.sha256(spec_text.encode("utf-8")).hexdigest()
        spec = json.loads(spec_text)
        on_screen = row["visible_height"] * FIELD_SCALE
        table.append({
            "enemy_id": row["enemy_id"], "source_master": f"{RAW}/{row['key']}_master.png",
            "source_sha256": master_sha, "runtime_png": str(runtime.relative_to(ROOT)).replace("\\", "/"),
            "runtime_sha256": master_sha, "byte_identical_to_master": True,
            "spec": f"res://assets/enemies/{row['folder']}/authored_core_v1/spec.json", "spec_sha256": spec_sha,
            "native_size": list(size), "visible_rect_px": rect, "root_px": list(row["root"]),
            "emitter_px": list(row["emitter"]), "display_height": spec["display_height"],
            "visible_height_world_px": row["visible_height"], "visible_height_on_screen_px": round(on_screen, 1),
            "alpha_policy": verdict.get("status"), "alpha_policy_id": policy.POLICY_ID,
        })
    if args.record and not failures:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(json.dumps({"status": "PASS", "field_scale": FIELD_SCALE, "bosses": table}, indent=2) + "\n", encoding="utf-8")
    for item in table:
        print(f"{item['enemy_id']}: spec sha256 {item['spec_sha256']} display_height {item['display_height']} visible {item['visible_rect_px']}")
    for line in failures:
        print("FAIL:", line)
    print("SITE7_BOSS_RUNTIME:", "PASS" if not failures else "FAIL", "(check)" if args.check else "(written)")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
