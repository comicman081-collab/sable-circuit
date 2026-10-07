"""Validate the deterministic UAL1 Pistol_Shoot upper-body curve contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = (
    ROOT
    / "art_src/pilot_v2/aster_v2/animation_360/ual_fire_upper_v1"
    / "ASTER_UAL1_PISTOL_SHOOT_UPPER_CURVES_V1.json"
)
UAL1 = ROOT / "assets/external/quaternius/ual1/UAL1_Standard.glb"
EXPECTED_SOURCE_SHA256 = "d68996d486d8d08cad5d603932d42fab6de9eddb19640e6a9ff9fdf92c8fca15"
EXPECTED_FRAMES = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]
EXPECTED_LABELS = [
    "aim_set",
    "preload",
    "muzzle_contact",
    "recoil_peak",
    "recover",
    "ready_return",
]
EXPECTED_JOINTS = {
    "pelvis",
    "spine_01",
    "spine_02",
    "spine_03",
    "neck_01",
    "Head",
    "clavicle_l",
    "upperarm_l",
    "lowerarm_l",
    "hand_l",
    "clavicle_r",
    "upperarm_r",
    "lowerarm_r",
    "hand_r",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite_tree(value: Any) -> bool:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return True
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    if isinstance(value, list):
        return all(finite_tree(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and finite_tree(item) for key, item in value.items())
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()
    path = (args.input if args.input.is_absolute() else ROOT / args.input).resolve()
    path.relative_to(ROOT)
    if not path.is_file() or not UAL1.is_file():
        raise SystemExit("ASTER_UAL1_FIRE_UPPER_V1: FAIL missing contract or UAL1 source")
    report = json.loads(path.read_text(encoding="utf-8"))
    samples = report.get("samples", [])
    checks = {
        "schema": report.get("schema") == 1,
        "source_path": report.get("source", {}).get("path")
        == "assets/external/quaternius/ual1/UAL1_Standard.glb",
        "source_hash_live": sha256(UAL1) == EXPECTED_SOURCE_SHA256,
        "source_hash_manifest": report.get("source", {}).get("sha256")
        == EXPECTED_SOURCE_SHA256,
        "license": report.get("source", {}).get("license") == "CC0-1.0",
        "commercial_use": report.get("source", {}).get("commercial_use") is True,
        "motion_only": report.get("source", {}).get("motion_only") is True,
        "action": report.get("action", {}).get("name") == "Pistol_Shoot",
        "frames": report.get("action", {}).get("sample_frames") == EXPECTED_FRAMES,
        "labels": report.get("action", {}).get("sample_labels") == EXPECTED_LABELS,
        "sample_count": len(samples) == 6
        and report.get("action", {}).get("sample_count") == 6,
        "sample_sequence": [sample.get("source_frame") for sample in samples]
        == EXPECTED_FRAMES
        and [sample.get("label") for sample in samples] == EXPECTED_LABELS,
        "joints": all(set(sample.get("joints", {})) == EXPECTED_JOINTS for sample in samples),
        "deltas": all(
            set(sample.get("deltas_from_aim_set", {})) == EXPECTED_JOINTS
            for sample in samples
        ),
        "corridor": all(
            float(sample.get("two_hand_corridor", {}).get("hand_separation_norm", 0.0)) > 0.0
            for sample in samples
        ),
        "finite": finite_tree(report),
        "background": report.get("generated_with", {}).get("background_mode") is True,
        "no_final_mesh": report.get("safety", {}).get("ual_preview_mesh_used_in_final")
        is False
        and report.get("safety", {}).get("mesh_exported") is False
        and report.get("safety", {}).get("render_written") is False,
        "no_external_base": report.get("safety", {}).get("external_base_character_used")
        is False,
        "no_runtime_promotion": report.get("integration_contract", {}).get(
            "runtime_promotion_allowed"
        )
        is False
        and report.get("safety", {}).get("runtime_visual_promoted") is False,
        "visual_hold": report.get("integration_contract", {}).get("visual_gate")
        == "HOLD_USER_REVIEW_REQUIRED",
        "custom_sse_not_ual": report.get("integration_contract", {}).get(
            "custom_sse_spatial_guide_is_ual_driven"
        )
        is False,
        "lower_ual_preserved": "Jog_Fwd_Loop"
        in report.get("integration_contract", {}).get("lower_motion_authority", ""),
    }
    failed = [name for name, passed in checks.items() if not passed]
    payload = {
        "result": "PASS" if not failed else "FAIL",
        "input": path.relative_to(ROOT).as_posix(),
        "input_sha256": sha256(path),
        "checks": checks,
        "failed": failed,
        "sample_count": len(samples),
        "runtime_promotion_allowed": False,
    }
    print("ASTER_UAL1_FIRE_UPPER_V1_VALIDATION=" + json.dumps(payload, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
