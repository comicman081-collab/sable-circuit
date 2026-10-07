#!/usr/bin/env python3
"""Static contract gate for the ASTER move/aim split review HTML.

This validates the fail-closed 8-dir/V1 -> 16-dir/V2 promotion contract and
the native 1920x1080 review harness. It never claims gameplay or visual PASS.
Dynamic browser evidence is intentionally captured only after the 16-dir art
dependency has passed its human visual gate.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "art_src/pilot_v2/aster_v2/interactive_preview/ASTER_360_INTERACTIVE_AIM_REVIEW.html"
ASSET_ROOT = ROOT / "assets/units/operators/aster"
OUTPUT = ROOT / "artifacts/aster_html_move_aim_split/ASTER_HTML_MOVE_AIM_SPLIT_STATIC_QA.json"
DIRECTIONS_8 = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
DIRECTIONS_16 = (
    "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW",
    "W", "WNW", "NW", "NNW", "N", "NNE", "NE", "ENE",
)
FRAME_LABELS_16 = (
    "aim", "preload", "recoil_contact_clean", "recover_early_clean", "recover", "ready_return",
)
MANIFEST_PROJECT_PATH = "assets/units/operators/aster/fire_upper_16_no_shoulder_v2/ASTER_FIRE_UPPER_16_NO_SHOULDER_V2_MANIFEST.json"
ALIGNMENT_PROJECT_PATH = "assets/units/operators/aster/fire_upper_16_no_shoulder_v2/ASTER_MUZZLE_ALIGNMENT_16_NO_SHOULDER_V2.json"
COMPOSITE_PROJECT_PATH = "assets/units/operators/aster/composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdefABCDEF" for char in value)


def finite_offset(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(number, (int, float)) and math.isfinite(number) for number in value)
    )


def require_markers(text: str, markers: tuple[str, ...]) -> dict[str, bool]:
    return {marker: marker in text for marker in markers}


def main() -> int:
    text = HTML.read_text(encoding="utf-8")
    markers = require_markers(
        text,
        (
            "const SECTOR_HYSTERESIS_DEGREES = 4",
            "moveAimIndependent:true",
            "fullBodyCrossfade:false",
            "function applyMovementVector",
            "function refreshUpperDirection",
            "function advanceGaitPhase",
            "lowerDirection=nearestDirection",
            "upperDirection=selectDirectionWithHysteresis",
            "fire_upper_16_no_shoulder_v2",
            "composite_fire_v6/fire_upper_8_fallback",
            "ASTER_TORSO_SOCKET_16_NO_SHOULDER_V4.json",
            "function validateTorsoSocket16",
            "offsets_source_px_by_frame",
            "function drawProtectedUpper16",
            "velocity_lower|translated_aim_upper|velocity_torso_bridge",
            "socket16_dependency_gate=",
            "socket16_dependency_promotion_not_ready",
            "socket16_manifest_source_mismatch",
            "muzzle16_hash_mismatch",
            "atlas_hash_${direction}_mismatch",
            "manifest.qa?.technical_result!=='PASS'",
            "manifest.candidate_status!=='PASS'",
            "manifest.visual_gate!=='PASS'",
            "manifest.promotion_ready!==true",
            "manifest.runtime_eligible!==true",
            "activeTorsoSocketPairs()",
            "V4_lower_lock_preserve_weapon_corridor_bridge_last",
            "aim_e_move_8",
            "move_e_aim_360",
            "stop_reverse_180",
            "reviewOnlyNoGameplayAuthority='true'",
            "lastShotGaitPhaseResetDelta",
            '<canvas id="stage" width="1920" height="1080"',
            "Native review canvas: 1920×1080 minimum backing store",
            "const VIEW_WIDTH = 1920",
            "const VIEW_HEIGHT = 1080",
            "const PLAYER_START_X = VIEW_WIDTH / 2",
            "const PLAYER_START_Y = VIEW_HEIGHT / 2",
            "const QA_AIM_SWEEP_START_X = VIEW_WIDTH * 0.184",
            "Math.max(VIEW_WIDTH, Math.round(rect.width * dpr))",
            "Math.max(VIEW_HEIGHT, Math.round(rect.height * dpr))",
            "native1080pFloorMet",
        ),
    )

    lower_assets: list[Path] = []
    fallback_upper_assets: list[Path] = []
    torso_bridge_assets: list[Path] = []
    for direction in DIRECTIONS_8:
        lower_assets.extend(
            (
                ASSET_ROOT / f"composite_fire_v6/idle_lower/{direction}/ASTER_IDLE_{direction}_LOWER_V6_ATLAS.webp",
                ASSET_ROOT / f"composite_fire_v6/move_lower/{direction}/ASTER_MOVE_{direction}_LOWER_V6_ATLAS.webp",
            )
        )
        fallback_upper_assets.append(
            ASSET_ROOT / f"composite_fire_v6/fire_upper/{direction}/ASTER_FIRE_{direction}_UPPER_V6_ATLAS.webp"
        )
        torso_bridge_assets.append(
            ASSET_ROOT / f"torso_bridge_v1/{direction}/ASTER_TORSO_BRIDGE_{direction}_V1_ATLAS.webp"
        )
    lower_missing = [str(path) for path in lower_assets if not path.is_file()]
    fallback_upper_missing = [str(path) for path in fallback_upper_assets if not path.is_file()]
    torso_bridge_missing = [str(path) for path in torso_bridge_assets if not path.is_file()]

    muzzle_path = ASSET_ROOT / "ASTER_MUZZLE_ALIGNMENT_V7.json"
    torso_socket8_path = ASSET_ROOT / "ASTER_TORSO_SOCKET_V1.json"
    muzzle = load_json(muzzle_path)
    torso_socket8 = load_json(torso_socket8_path)
    muzzle8_ok = (
        muzzle.get("schema") == 1
        and muzzle.get("source_frame") == 2
        and tuple(muzzle.get("directions", ())) == DIRECTIONS_8
        and all(direction in muzzle.get("calibration", {}) for direction in DIRECTIONS_8)
    )
    torso_socket8_ok = (
        torso_socket8.get("schema") == 1
        and torso_socket8.get("qa", {}).get("gate") == "PASS"
        and torso_socket8.get("qa", {}).get("passed_pairs") == 64
        and torso_socket8.get("qa", {}).get("all_64_connected") is True
        and torso_socket8.get("qa", {}).get("torso_bridge_required") is True
        and all(
            finite_offset(torso_socket8.get("offsets_source_px", {}).get(lower, {}).get(upper))
            for lower in DIRECTIONS_8 for upper in DIRECTIONS_8
        )
    )

    upper16_paths = {
        direction: ASSET_ROOT / f"fire_upper_16_no_shoulder_v2/{direction}/ASTER_FIRE_{direction}_UPPER_16_NO_SHOULDER_V2_ATLAS.png"
        for direction in DIRECTIONS_16
    }
    manifest_path = ASSET_ROOT / "fire_upper_16_no_shoulder_v2/ASTER_FIRE_UPPER_16_NO_SHOULDER_V2_MANIFEST.json"
    alignment_path = ASSET_ROOT / "fire_upper_16_no_shoulder_v2/ASTER_MUZZLE_ALIGNMENT_16_NO_SHOULDER_V2.json"
    socket16_path = ASSET_ROOT / "ASTER_TORSO_SOCKET_16_NO_SHOULDER_V4.json"
    composite_path = ASSET_ROOT / "composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_MANIFEST.json"
    upper16_missing = [
        str(path) for path in (*upper16_paths.values(), manifest_path, alignment_path, socket16_path, composite_path)
        if not path.is_file()
    ]
    manifest16 = load_json(manifest_path) if manifest_path.is_file() else {}
    alignment16 = load_json(alignment_path) if alignment_path.is_file() else {}
    socket16 = load_json(socket16_path) if socket16_path.is_file() else {}
    composite = load_json(composite_path) if composite_path.is_file() else {}

    atlas_hashes = {direction: sha256(path) for direction, path in upper16_paths.items() if path.is_file()}
    manifest_structural_ok = (
        manifest16.get("schema") == 1
        and manifest16.get("candidate_id") == "fire_upper_16_no_shoulder_v2"
        and tuple(manifest16.get("directions", ())) == DIRECTIONS_16
        and manifest16.get("frame_count_per_direction") == 6
        and manifest16.get("atlas_cell") == 384
        and all(
            manifest16.get("directions_output", {}).get(direction, {}).get("output_atlas")
            == f"assets/units/operators/aster/fire_upper_16_no_shoulder_v2/{direction}/ASTER_FIRE_{direction}_UPPER_16_NO_SHOULDER_V2_ATLAS.png"
            and is_sha256(manifest16.get("directions_output", {}).get(direction, {}).get("output_sha256"))
            and len(manifest16.get("directions_output", {}).get(direction, {}).get("frames", ())) == 6
            for direction in DIRECTIONS_16
        )
    )
    atlas_hash_agreement = manifest_structural_ok and all(
        manifest16["directions_output"][direction]["output_sha256"] == atlas_hashes.get(direction)
        for direction in DIRECTIONS_16
    )
    manifest_promotion_pass = (
        manifest16.get("qa", {}).get("technical_result") == "PASS"
        and manifest16.get("candidate_status") == "PASS"
        and manifest16.get("visual_gate") == "PASS"
        and manifest16.get("promotion_ready") is True
        and manifest16.get("runtime_eligible") is True
    )

    alignment16_structural_ok = (
        alignment16.get("schema") == 1
        and alignment16.get("source_frame") == 2
        and alignment16.get("cell_size") == 384
        and tuple(alignment16.get("directions", ())) == DIRECTIONS_16
        and all(direction in alignment16.get("calibration", {}) for direction in DIRECTIONS_16)
    )
    alignment16_hash = sha256(alignment_path) if alignment_path.is_file() else None
    alignment16_authority_agreement = (
        manifest16.get("muzzle_alignment_16_v2") == ALIGNMENT_PROJECT_PATH
        and manifest16.get("muzzle_alignment_16_v2_sha256") == alignment16_hash
    )
    alignment16_promotion_pass = alignment16.get("candidate_status") == "PASS"

    socket16_offsets_valid = all(
        finite_offset(socket16.get("offsets_source_px_by_frame", {}).get(lower, {}).get(upper, {}).get(label))
        for lower in DIRECTIONS_8 for upper in DIRECTIONS_16 for label in FRAME_LABELS_16
    )
    socket16_structural_ok = (
        socket16.get("schema") == 2
        and socket16.get("cell_size") == 384
        and tuple(socket16.get("lower_directions", ())) == DIRECTIONS_8
        and tuple(socket16.get("upper_directions", ())) == DIRECTIONS_16
        and socket16.get("lower_frame_count") == 24
        and socket16.get("upper_frame_count") == 6
        and tuple(socket16.get("upper_frame_labels", ())) == FRAME_LABELS_16
        and tuple(socket16.get("composition_order", ())) == (
            "velocity_lower", "translated_aim_upper", "velocity_torso_bridge",
        )
        and socket16.get("upper_lower_protection_policy", {}).get("weapon_corridor_exempt") is True
        and socket16.get("upper_lower_protection_policy", {}).get("torso_bridge_last") is True
        and socket16.get("upper_lower_protection_policy", {}).get("presentation_only") is True
        and socket16.get("qa", {}).get("pair_count") == 128
        and socket16.get("qa", {}).get("passed_pairs") == 128
        and socket16.get("qa", {}).get("failed_pairs") == 0
        and socket16.get("qa", {}).get("all_128_pairs_connected") is True
        and socket16.get("qa", {}).get("all_24_lower_phases_scanned") is True
        and socket16.get("qa", {}).get("samples_scanned") == 18432
        and socket16.get("qa", {}).get("expected_samples") == 18432
        and socket16.get("qa", {}).get("disconnected_samples") == 0
        and socket16.get("qa", {}).get("unsafe_locked_lower_overwrite_samples") == 0
        and socket16.get("qa", {}).get("safe_seam_gate") == "PASS"
        and socket16.get("qa", {}).get("locked_lower_preservation_gate") == "PASS"
        and socket16.get("qa", {}).get("cardinal_same_direction_offsets_zero") is True
        and socket16.get("qa", {}).get("technical_gate") == "PASS"
        and socket16_offsets_valid
    )
    manifest_hash = sha256(manifest_path) if manifest_path.is_file() else None
    composite_hash = sha256(composite_path) if composite_path.is_file() else None
    socket16_source_agreement = (
        socket16.get("sources", {}).get("fire_upper_16_manifest") == MANIFEST_PROJECT_PATH
        and socket16.get("sources", {}).get("fire_upper_16_manifest_sha256") == manifest_hash
        and socket16.get("sources", {}).get("composite_manifest") == COMPOSITE_PROJECT_PATH
        and socket16.get("sources", {}).get("composite_manifest_sha256") == composite_hash
        and all(
            socket16.get("sources", {}).get("atlas_sha256", {}).get("upper", {}).get(direction)
            == atlas_hashes.get(direction)
            for direction in DIRECTIONS_16
        )
    )
    dependency = socket16.get("dependency", {})
    socket16_promotion_pass = (
        dependency.get("technical_result") == "PASS"
        and dependency.get("technical_pass") is True
        and dependency.get("candidate_status") == "PASS"
        and dependency.get("candidate_or_promotion_pass") is True
        and dependency.get("promotion_ready") is True
        and dependency.get("visual_gate") == "PASS"
        and dependency.get("visual_pass") is True
        and dependency.get("gate") == "PASS"
        and socket16.get("qa", {}).get("dependency_gate") == "PASS"
        and socket16.get("qa", {}).get("promotion_gate") == "PASS"
        and socket16.get("candidate_status") == "PASS"
        and socket16.get("visual_gate") == "PASS"
        and socket16.get("runtime_eligible") is True
    )
    composite_structural_ok = (
        composite.get("schema") == 1
        and composite.get("cell") == 384
        and tuple(composite.get("directions", ())) == DIRECTIONS_8
        and all(
            len(composite.get("directions_output", {}).get(direction, {}).get("layers", {}).get(layer, {}).get("partition_frames", ())) == count
            and all(
                isinstance(frame.get("lower_costume_lock_y"), (int, float))
                for frame in composite["directions_output"][direction]["layers"][layer]["partition_frames"]
            )
            for direction in DIRECTIONS_8 for layer, count in (("move_lower", 24), ("idle_lower", 4))
        )
    )
    upper16_complete = (
        not upper16_missing
        and manifest_structural_ok
        and atlas_hash_agreement
        and manifest_promotion_pass
        and alignment16_structural_ok
        and alignment16_authority_agreement
        and alignment16_promotion_pass
        and socket16_structural_ok
        and socket16_source_agreement
        and socket16_promotion_pass
        and composite_structural_ok
    )

    forbidden = {
        "direction_change_resets_loop_frame": "lowerDirection=nearestDirection" in text and "loopFrameIndex = 0" in text,
        "set_loop_resets_phase": "function setLoop(state) {\n      loopState = state;\n      gaitPhase = 0" in text,
        "gameplay_authority_claim": "reviewOnlyNoGameplayAuthority='false'" in text,
        "stale_player_origin_512_310": "const player = { x:512, y:310 }" in text,
        "stale_reset_origin_512_310": "player.x=512" in text or "player.y=310" in text,
        "stale_qa_start_188_310": "player.x=188" in text or "player.y=310" in text,
        "cardinal_mid_socket_mapping": "nearestDirection(directionAngle(upper,upperDirections16),directions)" in text,
        "weak_candidate_or_promotion_gate": "candidate_status==='PASS' || payload.promotion_ready===true" in text,
    }
    pass_gate = (
        all(markers.values())
        and not lower_missing
        and not fallback_upper_missing
        and not torso_bridge_missing
        and muzzle8_ok
        and torso_socket8_ok
        and socket16_structural_ok
        and composite_structural_ok
        and not any(forbidden.values())
    )

    report = {
        "schema": 2,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate": "PASS" if pass_gate else "FAIL",
        "scope": "interactive_review_html_only",
        "gameplay_authority": False,
        "visual_quality_claimed": False,
        "html": {"path": str(HTML), "sha256": sha256(HTML), "size": HTML.stat().st_size},
        "contracts": {
            "required_markers": markers,
            "sector_hysteresis_degrees": 4,
            "move_aim_independent": True,
            "gait_phase_preserved_on_direction_and_fire": True,
            "full_body_alpha_crossfade": False,
            "native_review_resolution": [1920, 1080],
            "minimum_backing_store_enforced": True,
            "player_reset_center": [960, 540],
            "qa_modes": ["aim_e_move_8", "move_e_aim_360", "stop_reverse_180"],
            "atomic_16_promotion_requires": [
                "technical PASS", "candidate PASS", "visual PASS", "promotion_ready true",
                "runtime_eligible true", "muzzle16 path/hash PASS", "socket16 dependency/promotion PASS",
                "source path/hash agreement", "128/128 offsets and protection contract PASS",
            ],
        },
        "assets": {
            "lower_v6_count": len(lower_assets),
            "lower_v6_missing": lower_missing,
            "upper_8_fallback_count": len(fallback_upper_assets),
            "upper_8_fallback_missing": fallback_upper_missing,
            "torso_bridge_v1_count": len(torso_bridge_assets),
            "torso_bridge_v1_missing": torso_bridge_missing,
            "torso_socket_64_pairs_valid": torso_socket8_ok,
            "torso_socket_128_pairs_structural_valid": socket16_structural_ok,
            "torso_socket_128_offsets_valid": socket16_offsets_valid,
            "torso_socket_16_source_agreement": socket16_source_agreement,
            "torso_socket_16_dependency_promotion_pass": socket16_promotion_pass,
            "upper_16_family": "fire_upper_16_no_shoulder_v2",
            "upper_16_files_complete": not upper16_missing,
            "upper_16_missing": upper16_missing,
            "upper_16_manifest_structural_valid": manifest_structural_ok,
            "upper_16_manifest_promotion_pass": manifest_promotion_pass,
            "upper_16_atlas_hash_agreement": atlas_hash_agreement,
            "upper_16_muzzle_alignment_structural_valid": alignment16_structural_ok,
            "upper_16_muzzle_authority_agreement": alignment16_authority_agreement,
            "upper_16_muzzle_promotion_pass": alignment16_promotion_pass,
            "upper_16_atomic_promotion_ready": upper16_complete,
            "upper_16_candidate_status": manifest16.get("candidate_status"),
            "upper_16_visual_gate": manifest16.get("visual_gate"),
            "upper_16_runtime_eligible": manifest16.get("runtime_eligible") is True,
            "runtime_expected_family": "fire_upper_16_no_shoulder_v2" if upper16_complete else "composite_fire_v6/fire_upper_8_fallback",
            "runtime_expected_torso_pairs": 128 if upper16_complete else 64,
            "muzzle_alignment_8_valid": muzzle8_ok,
        },
        "forbidden_contracts": forbidden,
        "limitations": [
            "This gate validates the review HTML, not Godot gameplay movement.",
            "The promoted no-shoulder V2 bundle must fall back atomically if any art, hash, or socket dependency fails.",
            "A static PASS proves fail-closed wiring and native review resolution only, never visual quality.",
            "Dynamic 1920x1080 browser capture remains a separate requirement from this static wiring gate.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ASTER_HTML_MOVE_AIM_SPLIT_STATIC_QA: {report['gate']}")
    print(f"runtime_expected_family={report['assets']['runtime_expected_family']}")
    print(OUTPUT)
    return 0 if pass_gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
