#!/usr/bin/env python3
"""Create a tightly bounded ASTER arm/rifle assembly for one fire candidate.

Unlike v1's overlapping construction plates, this creates exactly two derived
source layers from the immutable approved master: a body underlay with the
carry assembly removed and a coherent upper-weapon assembly.  It is not a
semantic model, a new character, or a runtime asset.  The one manual mask is
kept as reviewable source evidence so a later local repair can be constrained
to seams rather than regenerating ASTER.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageChops


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "docs/ART_PRODUCTION/ASTER_STATIC_MASTER_USER_GATE.json"
OUT = ROOT / "art_src/pilot_v2/aster_v2/puppet_2p5d/source_plates_v2/fire_E_upper_assembly_v1"
GREEN = (0, 255, 0)

# Exact hand-authored source mask: the rifle is kept together with both hands
# and sleeves.  The contours intentionally avoid head, hair and torso mass.
# It is a single static-key assembly, not an attempt to infer a mesh rig.
ASSEMBLY_POLYGONS = (
    # Stock, receiver, rail and muzzle module.
    [(382, 650), (565, 648), (728, 722), (1280, 864), (1540, 1002), (1615, 1138), (1480, 1165), (1190, 1105), (812, 1015), (560, 930), (378, 836)],
    # Trigger-side arm from right shoulder toward receiver.
    [(642, 660), (862, 660), (969, 815), (948, 1008), (788, 1155), (610, 1018), (582, 830)],
    # Support-side arm and forward hand.
    [(996, 706), (1278, 754), (1305, 902), (1230, 1100), (1060, 1080), (958, 920), (922, 784)],
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save_green(rgb: Image.Image, mask: Image.Image, image_path: Path, mask_path: Path) -> None:
    binary = mask.point(lambda value: 255 if value >= 128 else 0)
    image = Image.new("RGB", rgb.size, GREEN)
    image.paste(rgb, mask=binary)
    image.save(image_path)
    binary.save(mask_path)


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    if not (gate.get("status") == "PASS" and gate.get("decision") == "PASS" and gate.get("approved_by") == "user" and gate.get("user_visual_approval") is True):
        raise SystemExit("user-approved Static Master required")
    master, subject_mask = ROOT / gate["approved_master_path"], ROOT / gate["paired_mask_path"]
    if not master.is_file() or not subject_mask.is_file() or sha256(master) != gate.get("approved_master_sha256"):
        raise SystemExit("Static Master SHA/mask gate mismatch")
    if OUT.exists() and any(OUT.iterdir()):
        raise SystemExit(f"refusing existing v2 assembly: {OUT}")
    rgb, subject = Image.open(master).convert("RGB"), Image.open(subject_mask).convert("L")
    if rgb.size != (2048, 2048) or subject.size != (2048, 2048):
        raise SystemExit("approved source must be 2048x2048")

    raw_assembly = Image.new("L", rgb.size, 0)
    drawer = ImageDraw.Draw(raw_assembly)
    for polygon in ASSEMBLY_POLYGONS:
        drawer.polygon(polygon, fill=255)
    assembly = ImageChops.multiply(subject, raw_assembly).point(lambda value: 255 if value >= 128 else 0)
    assembly_box = assembly.getbbox()
    if assembly_box is None:
        raise SystemExit("empty upper-weapon assembly")
    underlay = ImageChops.subtract(subject, assembly).point(lambda value: 255 if value >= 128 else 0)

    OUT.mkdir(parents=True)
    underlay_rgb, underlay_mask = OUT / "ASTER_FIRE_E_UNDERLAY_GREEN.png", OUT / "ASTER_FIRE_E_UNDERLAY_MASK.png"
    assembly_rgb, assembly_mask = OUT / "ASTER_FIRE_E_UPPER_ASSEMBLY_GREEN.png", OUT / "ASTER_FIRE_E_UPPER_ASSEMBLY_MASK.png"
    assembly_region = OUT / "ASTER_FIRE_E_UPPER_ASSEMBLY_REGION_MASK.png"
    save_green(rgb, underlay, underlay_rgb, underlay_mask)
    save_green(rgb.crop(assembly_box), assembly.crop(assembly_box), assembly_rgb, assembly_mask)
    raw_assembly.save(assembly_region)
    manifest = {
        "schema": 1,
        "role": "ASTER E fire upper-weapon assembly v2; source-authoring only",
        "static_master": master.relative_to(ROOT).as_posix(),
        "static_master_sha256": sha256(master),
        "source_background": "#00FF00",
        "underlay": {"green": underlay_rgb.relative_to(ROOT).as_posix(), "mask": underlay_mask.relative_to(ROOT).as_posix(), "box_xyxy": [0, 0, 2048, 2048], "sha256": sha256(underlay_rgb)},
        "upper_weapon_assembly": {"green": assembly_rgb.relative_to(ROOT).as_posix(), "mask": assembly_mask.relative_to(ROOT).as_posix(), "box_xyxy": list(assembly_box), "sha256": sha256(assembly_rgb)},
        "region_mask": assembly_region.relative_to(ROOT).as_posix(),
        "assembly_subject_pixels": int(sum(value >= 128 for value in assembly.getdata())),
        "runtime_asset": False,
        "prohibitions": ["no Static Master modification", "no UAL visual mesh", "no Qwen generation", "no runtime promotion"],
        "next": "headless Blender v2 candidate with one coherent assembly and retained visual review",
    }
    (OUT / "ASTER_FIRE_E_UPPER_ASSEMBLY_V2_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_2P5D_FIRE_ASSEMBLY_V2=" + json.dumps({"output": OUT.relative_to(ROOT).as_posix(), "box": list(assembly_box), "pixels": manifest["assembly_subject_pixels"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
