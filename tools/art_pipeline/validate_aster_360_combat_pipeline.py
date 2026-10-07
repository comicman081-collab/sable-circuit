#!/usr/bin/env python3
"""Preflight the gated ASTER 360-degree combat-sprite production pipeline.

This is deliberately a *pipeline* validator. It does not create body art,
animation frames, atlases, or a runtime replacement. Those outputs may only
exist after the user explicitly accepts an ASTER Static Master. Blender and
UAL remain temporal pose references; the locked SABLE 2048 canonical master
plus constrained local Qwen retouches is the visual source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aster_static_master_gate import evaluate_static_master_gate

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_LOCK = ROOT / "art_src/pilot_v2/aster_v2/static_master/ASTER_STATIC_MASTER_AUTHORITY/AUTHORITY_LOCK.json"
OUT_DEFAULT = ROOT / "art_src/pilot_v2/aster_v2/animation_360/ASTER_360_PIPELINE_PRECHECK.json"
IMAGEGEN_FIRE_MANIFEST = ROOT / "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/ASTER_IMAGEGEN_V1_FIRE_DIRECTION_MASTER_MANIFEST.json"
IMAGEGEN_AIM_MANIFEST = ROOT / "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/aim_master_v2/ASTER_IMAGEGEN_V2_AIM_DIRECTION_MASTER_MANIFEST.json"
FIRE_360_MVP_MANIFEST = ROOT / "art_src/pilot_v2/aster_v2/animation_360/imagegen_aim_fire_mvp_v3/ASTER_IMAGEGEN_AIM_FIRE_360_MOTION_MVP_GREEN_MASK_MANIFEST.json"
UALS = {
    "UAL1_FREE_STANDARD": ROOT / "assets/external/quaternius/ual1/UAL1_Standard.glb",
    "UAL2_FREE_STANDARD": ROOT / "assets/external/quaternius/ual2/UAL2_Standard.glb",
}

DIRECTIONS = [
    {"sector": 0, "id": "E", "aim": [1.0, 0.0]},
    {"sector": 1, "id": "SE", "aim": [0.7071, 0.7071]},
    {"sector": 2, "id": "S", "aim": [0.0, 1.0]},
    {"sector": 3, "id": "SW", "aim": [-0.7071, 0.7071]},
    {"sector": 4, "id": "W", "aim": [-1.0, 0.0]},
    {"sector": 5, "id": "NW", "aim": [-0.7071, -0.7071]},
    {"sector": 6, "id": "N", "aim": [0.0, -1.0]},
    {"sector": 7, "id": "NE", "aim": [0.7071, -0.7071]},
]

ANIMATION_SPEC = {
    "idle": {
        "fps": 8,
        "key_ids": ["ready", "inhale", "micro_weight_shift", "return"],
        "ual_reference": "UAL1 Idle_Loop timing only; ASTER rifle upper body is authored separately",
        "readability": "rifle, hands, ponytail, and silhouette must remain locked",
    },
    "move": {
        "fps": 12,
        "key_ids": ["contact_a", "down_a", "passing_a", "high_a", "contact_b", "down_b", "passing_b", "high_b"],
        "ual_reference": "UAL1 Jog_Fwd_Loop timing only",
        "readability": "eight-sector locomotion with stable rifle and no foot sliding",
    },
    "fire": {
        "fps": 12,
        "key_ids": ["aim_set", "preload", "muzzle_contact", "recoil_peak", "recover", "ready_return"],
        "ual_reference": "UAL1 Pistol_Shoot timing, manually cleaned for ASTER coil rifle",
        "readability": "two-handed grip, muzzle direction, recoil, and recovery must agree",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_within_project(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"Output must stay inside project: {resolved}") from exc
    return resolved


def build_report() -> dict:
    authority = read_json(AUTHORITY_LOCK) if AUTHORITY_LOCK.is_file() else {}
    missing = [name for name, path in UALS.items() if not path.is_file()]
    animation_frames = sum(len(spec["key_ids"]) for spec in ANIMATION_SPEC.values()) * len(DIRECTIONS)
    static_gate = evaluate_static_master_gate()
    directional_fire = {}
    if IMAGEGEN_AIM_MANIFEST.is_file():
        try:
            directional_fire = read_json(IMAGEGEN_AIM_MANIFEST)
        except (OSError, json.JSONDecodeError):
            directional_fire = {"invalid": True}
    expected_directions = [item["id"] for item in DIRECTIONS]
    directional_fire_ready = (
        directional_fire.get("directions") == expected_directions
        and directional_fire.get("direction_count") == len(expected_directions)
        and len(directional_fire.get("records", [])) == len(expected_directions)
        and directional_fire.get("source_background") == "#00FF00"
        and directional_fire.get("muzzle_vfx_embedded_in_source") is False
        and directional_fire.get("krea2_used") is False
    )
    fire_mvp = {}
    if FIRE_360_MVP_MANIFEST.is_file():
        try:
            fire_mvp = read_json(FIRE_360_MVP_MANIFEST)
        except (OSError, json.JSONDecodeError):
            fire_mvp = {"invalid": True}
    fire_mvp_records = fire_mvp.get("records", [])
    expected_fire_keys = ANIMATION_SPEC["fire"]["key_ids"]
    fire_mvp_ready = (
        fire_mvp.get("frame_count") == len(expected_directions) * len(expected_fire_keys)
        and fire_mvp.get("directions") == expected_directions
        and fire_mvp.get("keys") == expected_fire_keys
        and len(fire_mvp_records) == len(expected_directions) * len(expected_fire_keys)
        and all(row.get("exact_green_outside_ratio") == 1.0 for row in fire_mvp_records)
        and all(
            bool(row.get("muzzle_vfx_visible")) == (row.get("key") in ("muzzle_contact", "recoil_peak"))
            for row in fire_mvp_records
        )
    )
    production_state = (
        "FIRE_360_MVP_USER_REVIEW_REQUIRED" if static_gate["accepted"] and fire_mvp_ready
        else "DIRECTIONAL_AIM_MASTER_USER_REVIEW_REQUIRED" if static_gate["accepted"] and directional_fire_ready
        else "READY_FOR_DIRECTIONAL_KEY_POSE_AUTHORING" if static_gate["accepted"]
        else "BLOCKED_STATIC_REVIEW"
    )
    return {
        "schema": 1,
        "pipeline": "ASTER_2D_360_COMBAT_SPRITE_V1",
        "production_state": production_state,
        "static_master_gate": static_gate,
        "authority": {
            "authority_lock": AUTHORITY_LOCK.relative_to(ROOT).as_posix(),
            "authority_lock_sha256": sha256(AUTHORITY_LOCK) if AUTHORITY_LOCK.is_file() else None,
            "camera_preset_id": authority.get("camera_preset_id"),
            "source_background": authority.get("source_matte"),
            "identity_invariants": authority.get("rejection_invariants", []),
        },
        "source_policy": {
            "visual_authority": "SABLE identity authority + locked 2048px canonical body source + constrained local retouch composition",
            "motion_authority": "UAL1/UAL2 FREE Standard timing and pose guide only",
            "blender": "5.2.1 headless pose extraction, fixed combat camera, and timing guide only",
            "qwen_2511": "single non-overlapping local retouches only; full-body regeneration, uncontrolled pose changes, direct runtime export, and batch animation generation are forbidden",
            "source_background_required": "#00FF00 exact RGB",
            "runtime_export": "RGBA derived only from matching binary subject mask",
            "krea2_allowed": False,
            "cloud_authoring": "Only the user-explicit ImageGen authoring calls recorded in the v2 aim-master manifest; no cloud runtime inference.",
            "base_or_mannequin_allowed": False,
            "low_poly_final_allowed": False,
        },
        "directional_fire_master": {
            "available": directional_fire_ready,
            "manifest": IMAGEGEN_AIM_MANIFEST.relative_to(ROOT).as_posix() if IMAGEGEN_AIM_MANIFEST.is_file() else None,
            "generation_tool": directional_fire.get("generation_tool"),
            "visual_gate": directional_fire.get("visual_gate", "NOT_CREATED"),
            "runtime_asset": False,
            "promotion_block": "user visual review of the eight-direction contact sheet is still required",
        },
        "fire_360_mvp": {
            "available": fire_mvp_ready,
            "manifest": FIRE_360_MVP_MANIFEST.relative_to(ROOT).as_posix() if FIRE_360_MVP_MANIFEST.is_file() else None,
            "frame_count": fire_mvp.get("frame_count", 0),
            "muzzle_vfx_policy": fire_mvp.get("muzzle_vfx_visible_only_on", []),
            "runtime_asset": False,
            "promotion_block": "Fire MVP needs user visual/motion review and Idle/Move 360 source sets before OperatorActor can be replaced.",
        },
        "ual_sources": {
            name: {
                "path": path.relative_to(ROOT).as_posix(),
                "exists": path.is_file(),
                "sha256": sha256(path) if path.is_file() else None,
                "visual_mesh_promoted": False,
            }
            for name, path in UALS.items()
        },
        "ual_sources_complete": not missing,
        "directions": DIRECTIONS,
        "direction_count": len(DIRECTIONS),
        "animation_spec": ANIMATION_SPEC,
        "planned_keyframe_count": animation_frames,
        "planned_directional_static_lock_count": len(DIRECTIONS),
        "manual_frame_contract": {
            "canvas": [2048, 2048],
            "source_pattern": "art_src/pilot_v2/aster_v2/animation_360/source/{state}/ASTER_{state}_{direction}_{key}_GREEN.png",
            "mask_pattern": "art_src/pilot_v2/aster_v2/animation_360/masks/{state}/ASTER_{state}_{direction}_{key}_MASK.png",
            "export_pattern": "assets/units/operators/aster/v2_360/{state}/ASTER_{state}_{direction}_{key}_RGBA.png",
            "final_export_blocked_until": "static master user gate PASS, directional identity lock PASS, per-frame green/mask QA PASS",
        },
        "runtime_contract": {
            "integration_status": "NOT_STARTED",
            "required_before_deploy": [
                "all eight sectors have authored idle, move, and fire keyframes",
                "atlas manifest maps all 8 sectors without mirroring identity-critical asymmetry",
                "actual AnimationPlayer/AnimatedSprite2D state switching replaces procedural bob-only presentation",
                "runtime proof captures movement and fire in every sector",
            ],
            "prohibited_now": [
                "attaching the pre-gate static candidate to OperatorActor",
                "promoting the isolated QA scene",
                "calling current static directional atlas a 360-degree animation set",
                "ROOK, MICA, or enemy expansion",
            ],
        },
        "next_allowed_action": (
            "Review the available ASTER Fire-360 MVP contact sheet. Its aim masters are VFX-free and its separate muzzle VFX is restricted to contact/recoil; do not runtime-promote before user visual/motion review and Idle/Move completion."
            if static_gate["accepted"] and fire_mvp_ready
            else "Review the available ASTER v2 eight-direction clean aim master contact sheet; only a user visual PASS may make those source masters eligible for per-direction Idle/Move/Fire keyframe authoring."
            if static_gate["accepted"] and directional_fire_ready
            else "Author exactly one ASTER 8-direction rifle-ready key-pose sheet from the locked Static Master and Blender guides; review it before full state/keyframe expansion."
            if static_gate["accepted"]
            else "Obtain user decision on the final 2048px canonical ASTER Static Master; until then only controlled local-retouch, guide, and preflight work is allowed."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT_DEFAULT)
    parser.add_argument("--require-static-pass", action="store_true")
    args = parser.parse_args()
    output = require_within_project(args.output)
    report = build_report()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ASTER_360_COMBAT_PIPELINE_PRECHECK=" + json.dumps({
        "output": output.relative_to(ROOT).as_posix(),
        "direction_count": report["direction_count"],
        "planned_keyframe_count": report["planned_keyframe_count"],
        "static_gate": report["static_master_gate"]["state"],
        "production_state": report["production_state"],
    }, ensure_ascii=False))
    if args.require_static_pass and not report["static_master_gate"]["accepted"]:
        print("ASTER_360_COMBAT_PIPELINE: HOLD - explicit user Static Master PASS is absent")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
