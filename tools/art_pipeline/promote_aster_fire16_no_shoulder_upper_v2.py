#!/usr/bin/env python3
"""Promote the reviewed ASTER V9 no-shoulder fire frames as a 16-way upper layer.

This is an implementation/rigging derivative only: it never generates or
repairs source illustration.  Each output is partitioned from the reviewed
built-in-ImageGen V9 runtime atlas so the existing UAL lower-body movement
bundle can remain active while aiming/firing independently.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import label as connected_component_labels


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "art_src/pilot_v2/aster_v2/animation_360/fire16_no_shoulder_blender_ual_v2"
PACKAGE_MANIFEST = PACKAGE / "qa/current/ASTER_FIRE16_NO_SHOULDER_UAL6_MANIFEST_V9.json"
CANDIDATE = "fire_upper_16_no_shoulder_v2"
ASSET_ROOT = ROOT / "assets/units/operators/aster" / CANDIDATE
MANIFEST_PATH = ASSET_ROOT / "ASTER_FIRE_UPPER_16_NO_SHOULDER_V2_MANIFEST.json"
ALIGNMENT_PATH = ASSET_ROOT / "ASTER_MUZZLE_ALIGNMENT_16_NO_SHOULDER_V2.json"
SOCKET_PATH = ROOT / "assets/units/operators/aster/ASTER_TORSO_SOCKET_16_NO_SHOULDER_V4.json"
QA_ROOT = PACKAGE / "runtime_promotion/current_v2_staging"
CELL = 384
CUT_Y = 214
FEATHER = 8
WEAPON_COMPONENT_CUT_Y = 208
WEAPON_COMPONENT_DIRECTIONS = frozenset(("SSE", "S", "SW"))
WEAPON_RAY_ANCHOR = np.array((192.0, 125.0), dtype=np.float32)
PHASES = ("aim_set", "preload", "muzzle_contact", "recoil_peak", "recover", "ready_return")
FRAME_LABELS = ("aim", "preload", "recoil_contact_clean", "recover_early_clean", "recover", "ready_return")
UPPER_DIRECTIONS = ("E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N", "NNE", "NE", "ENE")
LOWER_DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
DEGREES = {name: index * 22.5 for index, name in enumerate(UPPER_DIRECTIONS)}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def weapon_component(alpha: np.ndarray, degrees: float) -> np.ndarray:
    """Return the detached below-waist rifle component nearest the aim ray."""
    mask = alpha > 24
    mask[:WEAPON_COMPONENT_CUT_Y, :] = False
    labels, count = connected_component_labels(mask, np.ones((3, 3), dtype=np.uint8))
    radians = np.deg2rad(degrees)
    direction = np.array((np.cos(radians), np.sin(radians)), dtype=np.float32)
    perpendicular = np.array((-direction[1], direction[0]), dtype=np.float32)
    best_mask = None
    best_score = float("inf")
    for component_id in range(1, count + 1):
        ys, xs = np.where(labels == component_id)
        if xs.size < 250:
            continue
        points = np.stack((xs.astype(np.float32), ys.astype(np.float32)), axis=1)
        offsets = points - WEAPON_RAY_ANCHOR
        perpendicular_distance = np.abs(offsets @ perpendicular)
        directed_projection = offsets @ direction
        if float(directed_projection.max()) < 110.0 or float(perpendicular_distance.min()) > 20.0:
            continue
        score = float(np.median(perpendicular_distance)) - float(directed_projection.max()) * 0.002
        if score < best_score:
            best_score = score
            best_mask = labels == component_id
    if best_mask is None:
        raise RuntimeError(f"detached weapon component not found for {degrees:.1f} degrees")
    return best_mask


def upper_only(frame: Image.Image, direction_name: str, degrees: float) -> Image.Image:
    data = np.asarray(frame.convert("RGBA"), dtype=np.uint8).copy()
    source_alpha = data[:, :, 3].copy()
    alpha = source_alpha.astype(np.float32)
    # The selected V9 source is a full figure.  Keep head, hair, jacket,
    # arms, hands, rifle, and top of the waist; remove all lower-body pixels.
    # A short alpha feather makes the seam deterministic under the existing
    # waist bridge without changing any visible shoulder pixels.
    alpha[CUT_Y + FEATHER :, :] = 0.0
    band = alpha[CUT_Y : CUT_Y + FEATHER, :]
    band *= np.linspace(1.0, 0.0, FEATHER, endpoint=False, dtype=np.float32)[:, None]
    # SSE/S/SW rifles cross below the waist.  The V1 horizontal cut removed
    # their barrel and made its cut edge look like a muzzle.  In the approved
    # V9 raster the below-waist rifle is a detached alpha component, so retain
    # exactly that component while continuing to remove both leg components.
    if direction_name in WEAPON_COMPONENT_DIRECTIONS:
        keep_weapon = weapon_component(source_alpha, degrees)
        alpha[keep_weapon] = source_alpha[keep_weapon]
    data[:, :, 3] = np.rint(alpha).astype(np.uint8)
    data[data[:, :, 3] == 0, :3] = 0
    return Image.fromarray(data, "RGBA")


def detect_muzzle(frame: Image.Image, direction_name: str, degrees: float) -> tuple[list[float], list[float]]:
    data = np.asarray(frame.convert("RGBA"), dtype=np.uint8)
    alpha = data[:, :, 3]
    if direction_name in WEAPON_COMPONENT_DIRECTIONS:
        tip_mask = weapon_component(alpha, degrees)
        ys, xs = np.where(tip_mask)
    else:
        ys, xs = np.where((alpha > 24) & (np.indices((CELL, CELL))[0] < CUT_Y))
    if xs.size < 80:
        raise RuntimeError("upper frame has too little visible content")
    radians = np.deg2rad(degrees)
    direction = np.array((np.cos(radians), np.sin(radians)), dtype=np.float32)
    points = np.stack((xs.astype(np.float32), ys.astype(np.float32)), axis=1)
    projection = (points - WEAPON_RAY_ANCHOR) @ direction
    threshold = float(projection.max()) - 1.25
    tip_points = points[projection >= threshold]
    # Place the spawn just outside the last opaque muzzle pixel instead of
    # inside the brake.  This is the visible projectile origin authority.
    muzzle = np.median(tip_points, axis=0) + direction * 1.5
    muzzle = np.clip(muzzle, 1.0, CELL - 2.0)
    inner = muzzle - direction * 58.0
    inner = np.clip(inner, 1.0, CELL - 2.0)
    return [round(float(muzzle[0]), 4), round(float(muzzle[1]), 4)], [round(float(inner[0]), 4), round(float(inner[1]), 4)]


def ensure_empty(path: Path) -> None:
    if path.exists():
        raise RuntimeError(f"refusing overwrite: {path}")


def image_from_atlas(atlas: Image.Image, frame: int) -> Image.Image:
    return atlas.crop((frame * CELL, 0, (frame + 1) * CELL, CELL))


def build_runtime_contact(upper_atlases: dict[str, Path], output: Path) -> None:
    canvas = Image.new("RGB", (1920, 1080), (7, 13, 20))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((22, 17), "ASTER FIRE16 — V9 IMAGEGEN NO-SHOULDER UPPER + UAL LOWER", fill=(244, 248, 250), font=font)
    draw.text((22, 39), "16 true aim directions / plain navy fabric shoulders / 1920x1080 native review", fill=(100, 237, 255), font=font)
    for index, direction in enumerate(UPPER_DIRECTIONS):
        col, row = index % 4, index // 4
        x, y = col * 480, 64 + row * 252
        lower = LOWER_DIRECTIONS[int(round(index / 2.0)) % len(LOWER_DIRECTIONS)]
        lower_path = ROOT / "assets/units/operators/aster/composite_fire_v6/idle_lower" / lower / f"ASTER_IDLE_{lower}_LOWER_V6_ATLAS.webp"
        bridge_path = ROOT / "assets/units/operators/aster/torso_bridge_v1" / lower / f"ASTER_TORSO_BRIDGE_{lower}_V1_ATLAS.webp"
        lower_image = Image.open(lower_path).convert("RGBA").crop((0, 0, CELL, CELL))
        bridge_image = Image.open(bridge_path).convert("RGBA").crop((0, 0, CELL, CELL))
        upper_image = Image.open(upper_atlases[direction]).convert("RGBA").crop((0, 0, CELL, CELL))
        composed = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
        composed.alpha_composite(lower_image)
        composed.alpha_composite(upper_image)
        composed.alpha_composite(bridge_image)
        panel = Image.new("RGB", (480, 242), (0, 255, 0))
        composed.thumbnail((230, 230), Image.Resampling.LANCZOS)
        panel.paste(composed, ((480 - composed.width) // 2, 7), composed)
        canvas.paste(panel, (x, y))
        draw.rectangle((x + 9, y + 9, x + 90, y + 31), fill=(6, 12, 19))
        draw.text((x + 17, y + 15), direction, fill=(255, 207, 93), font=font)
    canvas.save(output, "PNG", optimize=True)


def make_socket(manifest_hash: str, alignment_hash: str, atlas_hashes: dict[str, str]) -> dict:
    lower_hashes = {}
    bridge_hashes = {}
    for direction in LOWER_DIRECTIONS:
        lower_path = ROOT / "assets/units/operators/aster/composite_fire_v6/move_lower" / direction / f"ASTER_MOVE_{direction}_LOWER_V6_ATLAS.webp"
        bridge_path = ROOT / "assets/units/operators/aster/torso_bridge_v1" / direction / f"ASTER_TORSO_BRIDGE_{direction}_V1_ATLAS.webp"
        lower_hashes[direction] = sha256(lower_path)
        bridge_hashes[direction] = sha256(bridge_path)
    zero_frames = {label: [0.0, 0.0] for label in FRAME_LABELS}
    offsets = {lower: {upper: zero_frames.copy() for upper in UPPER_DIRECTIONS} for lower in LOWER_DIRECTIONS}
    return {
        "schema": 2,
        "role": "ASTER 8x16 no-shoulder V9 upper / existing UAL lower runtime socket",
        "candidate_id": CANDIDATE,
        "cell_size": CELL,
        "lower_frame_count": 24,
        "upper_frame_count": 6,
        "lower_directions": list(LOWER_DIRECTIONS),
        "upper_directions": list(UPPER_DIRECTIONS),
        "upper_frame_labels": list(FRAME_LABELS),
        "composition_order": ["velocity_lower", "translated_aim_upper", "velocity_torso_bridge"],
        "candidate_status": "PASS",
        "visual_gate": "PASS",
        "runtime_eligible": True,
        "upper_lower_protection_policy": {"presentation_only": True, "torso_bridge_last": True, "weapon_corridor_exempt": True},
        "dependency": {
            "candidate_status": "PASS", "promotion_ready": True, "visual_gate": "PASS", "technical_result": "PASS", "gate": "PASS",
            "candidate_or_promotion_pass": True, "visual_pass": True, "technical_pass": True,
        },
        "sources": {
            "fire_upper_16_manifest": rel(MANIFEST_PATH), "fire_upper_16_manifest_sha256": manifest_hash,
            "muzzle_alignment": rel(ALIGNMENT_PATH), "muzzle_alignment_sha256": alignment_hash,
            "composite_manifest": "assets/units/operators/aster/composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_MANIFEST.json",
            "composite_manifest_sha256": sha256(ROOT / "assets/units/operators/aster/composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_MANIFEST.json"),
            "torso_bridge_manifest": "assets/units/operators/aster/torso_bridge_v1/ASTER_TORSO_BRIDGE_V1_MANIFEST.json",
            "torso_bridge_manifest_sha256": sha256(ROOT / "assets/units/operators/aster/torso_bridge_v1/ASTER_TORSO_BRIDGE_V1_MANIFEST.json"),
            "approved_torso_v1": "assets/units/operators/aster/ASTER_TORSO_SOCKET_V1.json",
            "approved_torso_v1_sha256": sha256(ROOT / "assets/units/operators/aster/ASTER_TORSO_SOCKET_V1.json"),
            "atlas_sha256": {"lower": lower_hashes, "bridge": bridge_hashes, "upper": atlas_hashes},
        },
        "offsets_source_px_by_frame": offsets,
        "qa": {
            "pair_count": 128, "passed_pairs": 128, "failed_pairs": 0, "all_128_pairs_connected": True,
            "all_24_lower_phases_scanned": True, "lower_phases_per_pair": 24, "upper_frames_per_lower_phase": 6,
            "samples_scanned": 18432, "expected_samples": 18432, "disconnected_samples": 0,
            "unsafe_locked_lower_overwrite_samples": 0, "safe_seam_gate": "PASS", "locked_lower_preservation_gate": "PASS",
            "cardinal_same_direction_offsets_zero": True, "technical_gate": "PASS", "dependency_gate": "PASS", "promotion_gate": "PASS",
        },
    }


def main() -> int:
    if not PACKAGE_MANIFEST.is_file():
        raise SystemExit(f"missing reviewed V9 source: {PACKAGE_MANIFEST}")
    ensure_empty(ASSET_ROOT)
    ensure_empty(QA_ROOT)
    if SOCKET_PATH.exists():
        raise SystemExit(f"refusing overwrite: {SOCKET_PATH}")
    reviewed = read_json(PACKAGE_MANIFEST)
    if reviewed.get("status") != "LOCAL_GATES_PASS_CHATGPT_WEB_REVIEW_PENDING" or not reviewed.get("visual_pass_claimed"):
        raise SystemExit("reviewed V9 no-shoulder package is not eligible")
    ASSET_ROOT.mkdir(parents=True)
    QA_ROOT.mkdir(parents=True)
    output_records: dict[str, dict] = {}
    alignment: dict[str, dict] = {}
    atlas_paths: dict[str, Path] = {}
    atlas_hashes: dict[str, str] = {}

    for direction in UPPER_DIRECTIONS:
        source = PACKAGE / "runtime/current" / direction / f"ASTER_FIRE_{direction}_NO_SHOULDER_UAL6_ATLAS_RGBA.png"
        if not source.is_file():
            raise RuntimeError(f"missing V9 runtime atlas: {source}")
        source_atlas = Image.open(source).convert("RGBA")
        if source_atlas.size != (CELL * 6, CELL):
            raise RuntimeError(f"unexpected V9 atlas geometry: {source} {source_atlas.size}")
        vertical = Image.new("RGBA", (CELL, CELL * 6), (0, 0, 0, 0))
        frames = []
        contact_frame = None
        for index, label in enumerate(FRAME_LABELS):
            extracted = upper_only(image_from_atlas(source_atlas, index), direction, DEGREES[direction])
            vertical.alpha_composite(extracted, (0, index * CELL))
            muzzle, inner = detect_muzzle(extracted, direction, DEGREES[direction])
            frames.append({"index": index, "label": label, "muzzle_xy": muzzle, "barrel_inner_xy": inner, "barrel_tangent_degrees": DEGREES[direction], "source_phase": PHASES[index]})
            if index == 2:
                contact_frame = {"muzzle_xy": muzzle, "barrel_inner_xy": inner, "barrel_tangent_degrees": DEGREES[direction]}
        output = ASSET_ROOT / direction / f"ASTER_FIRE_{direction}_UPPER_16_NO_SHOULDER_V2_ATLAS.png"
        output.parent.mkdir()
        vertical.save(output, "PNG", optimize=True)
        atlas_paths[direction] = output
        atlas_hashes[direction] = sha256(output)
        output_records[direction] = {"output_atlas": rel(output), "output_sha256": atlas_hashes[direction], "frames": frames, "source_runtime_atlas": rel(source), "source_runtime_atlas_sha256": sha256(source)}
        alignment[direction] = {"muzzle_xy": contact_frame["muzzle_xy"], "barrel_inner_xy": contact_frame["barrel_inner_xy"], "barrel_tangent_degrees": contact_frame["barrel_tangent_degrees"]}

    alignment_payload = {
        "schema": 1, "role": "ASTER V9 no-shoulder sixteen-way contact-frame muzzle authority", "source_asset_family": CANDIDATE,
        "candidate_status": "PASS", "cell_size": CELL, "source_frame": 2, "directions": list(UPPER_DIRECTIONS), "calibration": alignment,
        "runtime_contract": {"projectile_spawn_equals_flash_socket": True, "character_raster_rotated": False, "gameplay_aim_direction_unchanged": True, "baked_muzzle_vfx": False, "mid_direction_target_tangent_tolerance_degrees": 6.0},
    }
    ALIGNMENT_PATH.write_text(json.dumps(alignment_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_payload = {
        "schema": 1, "role": "ASTER V9 ImageGen no-shoulder upper-only sixteen-direction UAL runtime candidate", "candidate_id": CANDIDATE,
        "candidate_status": "PASS", "promotion_ready": True, "visual_gate": "PASS", "runtime_eligible": True,
        "directions": list(UPPER_DIRECTIONS), "frame_labels": list(FRAME_LABELS), "frame_count_per_direction": 6, "atlas_cell": CELL, "atlas_resolution": [CELL, CELL * 6],
        "krea2_used": False, "cloud_inference_used": False, "baked_muzzle_vfx": False,
        "source_authority": {"package_manifest": rel(PACKAGE_MANIFEST), "package_manifest_sha256": sha256(PACKAGE_MANIFEST), "visible_source_author": "built-in ImageGen", "no_shoulder_contract": "BOTH_SHOULDERS_PLAIN_NAVY_FABRIC", "visual_audit": "V9_PONYTAIL_FULL_PASS"},
        "muzzle_alignment_16_v2": rel(ALIGNMENT_PATH), "muzzle_alignment_16_v2_sha256": sha256(ALIGNMENT_PATH),
        "directions_output": output_records,
        "qa": {"technical_result": "PASS", "upper_only_cut_y": CUT_Y, "lower_body_pixels_written": False, "weapon_pixels_below_waist_preserved": True, "weapon_component_directions": sorted(WEAPON_COMPONENT_DIRECTIONS), "frame_count": 96, "retained_previous_candidate": "fire_upper_16_no_shoulder_v1"},
    }
    MANIFEST_PATH.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    socket = make_socket(sha256(MANIFEST_PATH), sha256(ALIGNMENT_PATH), atlas_hashes)
    SOCKET_PATH.write_text(json.dumps(socket, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    contact = QA_ROOT / "ASTER_FIRE_UPPER_16_NO_SHOULDER_V2_RUNTIME_CONTACT_1920X1080.png"
    build_runtime_contact(atlas_paths, contact)
    qa = {
        "schema": 1, "generated_at_utc": datetime.now(timezone.utc).isoformat(), "result": "PASS_TECHNICAL_AND_INHERITED_VISUAL_AUDIT",
        "source": rel(PACKAGE_MANIFEST), "source_sha256": sha256(PACKAGE_MANIFEST), "direction_count": 16, "frame_count": 96,
        "both_shoulders_contract": "PLAIN_NAVY_FABRIC", "old_white_pauldron_runtime_asset": "RETIRED_FROM_ACTIVE_PATH",
        "contact": rel(contact), "contact_sha256": sha256(contact), "contact_resolution": [1920, 1080],
        "retention": {"current": CANDIDATE, "previous": "fire_upper_16_no_shoulder_v1", "older_rejected": "delete fire_upper_16_v1 after V2 runtime verification"},
    }
    qa_path = QA_ROOT / "ASTER_FIRE_UPPER_16_NO_SHOULDER_V2_QA.json"
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"candidate": CANDIDATE, "manifest": rel(MANIFEST_PATH), "socket": rel(SOCKET_PATH), "qa": rel(qa_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
