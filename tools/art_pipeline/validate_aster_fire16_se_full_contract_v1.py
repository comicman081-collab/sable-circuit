#!/usr/bin/env python3
"""Fail-closed independent validator for the ASTER Fire16 SE source contract.

The validator never authors mask pixels and never promotes runtime assets.  It
locks the approved SE source/subject, the accepted three manual rigid-cluster
masks, and the Blender SSE occlusion guide lineage.  All 17 accepted masks must
exist at fixed names below ``manual_full_contract_v1/accepted_v1``; the copied
SUBJECT and rigid-cluster masks must be byte-identical to their locked
authorities.  Even a successful run can report only
``PASS_FULL_SE_SOURCE_MASK_CONTRACT_ONLY_HOLD``.  The accepted mask package is
read-only input.  Independent review evidence is written only to the fixed
project-local sibling ``manual_full_contract_v1/independent_validation_v2``.

Missing or malformed authored masks are reported as FAIL.  A non-empty
independent-validation output root is immutable and causes a fail-closed stop;
accepted package files are never replaced.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from project_paths import PROJECT_ROOT, require_project_output_path


EXPECTED_SIZE = (1254, 1254)
REVIEW_SIZE = (1920, 1440)
GREEN = np.asarray((0, 255, 0), dtype=np.uint8)
COSTUME_ID = "ASTER_COMBAT_SUIT_C01"
PASS_RESULT = "PASS_FULL_SE_SOURCE_MASK_CONTRACT_ONLY_HOLD"
FAIL_RESULT = "FAIL"

AUTHORITY_SOURCE = (
    PROJECT_ROOT
    / "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/aim_master_v2/source/ASTER_FIRE_SE_DIRECTION_AIM_MASTER_V2_GREEN.png"
)
AUTHORITY_SUBJECT = (
    PROJECT_ROOT
    / "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/aim_master_v2/masks/ASTER_FIRE_SE_DIRECTION_AIM_MASTER_V2_MASK.png"
)
REPAIR_CONTRACT = PROJECT_ROOT / "docs/ART_PRODUCTION/ASTER_FIRE_UPPER_16_REPAIR_CONTRACT.md"
GUIDE_ROOT = (
    PROJECT_ROOT
    / "art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_v1_pose_guides_v3"
)
SSE_GUIDE = GUIDE_ROOT / "ASTER_FIRE_SSE_BLENDER_POSE_OCCLUSION_GUIDE_GREEN.png"
GUIDE_MANIFEST = GUIDE_ROOT / "ASTER_FIRE16_MID_POSE_GUIDES_MANIFEST.json"
AUTHORING_ROOT = (
    PROJECT_ROOT
    / "art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_sse_semantic_masks_v1"
)
MANUAL_THREE_ROOT = AUTHORING_ROOT / "manual_fallback_v1"
MANUAL_THREE_MANIFEST = MANUAL_THREE_ROOT / "ASTER_FIRE_SE_MANUAL_FALLBACK_V1_MANIFEST.json"
FULL_PARENT = AUTHORING_ROOT / "manual_full_contract_v1"
FULL_ROOT = FULL_PARENT / "accepted_v1"
VALIDATION_ROOT = FULL_PARENT / "independent_validation_v2"
ACCEPTED_MANIFEST = FULL_ROOT / "ASTER_FIRE_SE_FULL_CONTRACT_V1_MANIFEST.json"
EVIDENCE_VALIDATOR = PROJECT_ROOT / "tools/art_pipeline/validate_visual_evidence_1080p.py"

LOCKED_SHA256 = {
    "authority_source": "1a674d5d1f68cebc20a61fae1187f725500189700897785550b5642d8a174838",
    "authority_subject": "4dedc673b1d8029b7455e1259994e354285838ff7d7618d77828cef89ac8e9b5",
    "SUBJECT": "4dedc673b1d8029b7455e1259994e354285838ff7d7618d77828cef89ac8e9b5",
    "repair_contract": "4f3ccade8d41fb9cb59c302aa49e7d8958386c8cc902e268f3d5fcf0d065dbcd",
    "sse_guide": "476a3c69966732fb4c662a541caac59f6c36b2c53e5987adca6e93bd37a24cbf",
    "guide_manifest": "ae84b541026dbf7e4033404f9dbb9fabfcb085db95d57deb0936305e33fd9b8d",
    "manual_three_manifest": "6e463e3bd7bca1fbbfaa4c069d6fb082c29fc8f85fec2e37cc9f48a62ad26c50",
    "accepted_manifest": "1d7cbeeaf51f1b83fb296031ce3afb2b3471c3c1aae23f02fd483d72ada4c842",
    "RIFLE": "51876f84ba9fe1f5c3d300bc4057950e500bb655d58162547f59d6e4c52b55c6",
    "TRIGGER_FOREARM_HAND": "5ececa81d3870a91d91a7f799e8e41f15cb7c54dc2f32999110b8bdaf6d078e9",
    "SUPPORT_FOREARM_HAND": "bc5feaf79f9264a84fa22e6f58493378687f5a20ba488637c25bf41abbea83b9",
    "manual_RIFLE": "51876f84ba9fe1f5c3d300bc4057950e500bb655d58162547f59d6e4c52b55c6",
    "manual_TRIGGER_FOREARM_HAND": "5ececa81d3870a91d91a7f799e8e41f15cb7c54dc2f32999110b8bdaf6d078e9",
    "manual_SUPPORT_FOREARM_HAND": "bc5feaf79f9264a84fa22e6f58493378687f5a20ba488637c25bf41abbea83b9",
}

ALL_ROLES = [
    "SUBJECT",
    "HAIR_BACK",
    "BODY_CORE",
    "HEAD_FACE",
    "HAIR_FRONT",
    "ARM_TRIGGER_UPPER",
    "ARM_SUPPORT_UPPER",
    "RIFLE",
    "TRIGGER_FOREARM_HAND",
    "SUPPORT_FOREARM_HAND",
    "SHOULDER_PLATE",
    "ANATOMICAL_LEFT_WHITE_LEG_MODULE",
    "OPPOSITE_STRAPS_POUCH_LEG",
    "BOOTS_ACCESSORIES",
    "SHOULDER_ELBOW_SEAM_BRIDGE",
    "TARGET_OCCLUDE",
    "TARGET_REVEAL",
]
HARD_PART_ROLES = [
    "HAIR_BACK",
    "BODY_CORE",
    "HEAD_FACE",
    "HAIR_FRONT",
    "ARM_TRIGGER_UPPER",
    "ARM_SUPPORT_UPPER",
    "RIFLE",
    "TRIGGER_FOREARM_HAND",
    "SUPPORT_FOREARM_HAND",
    "SHOULDER_PLATE",
    "ANATOMICAL_LEFT_WHITE_LEG_MODULE",
    "OPPOSITE_STRAPS_POUCH_LEG",
    "BOOTS_ACCESSORIES",
]
BAND_ROLES = ["SHOULDER_ELBOW_SEAM_BRIDGE", "TARGET_OCCLUDE", "TARGET_REVEAL"]
LOCKED_ROLE_AUTHORITIES = {
    "SUBJECT": AUTHORITY_SUBJECT,
    "RIFLE": MANUAL_THREE_ROOT / "ASTER_FIRE_SE_RIFLE_MANUAL_FALLBACK_V1_MASK.png",
    "TRIGGER_FOREARM_HAND": MANUAL_THREE_ROOT
    / "ASTER_FIRE_SE_TRIGGER_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png",
    "SUPPORT_FOREARM_HAND": MANUAL_THREE_ROOT
    / "ASTER_FIRE_SE_SUPPORT_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png",
}
ROLE_PATHS = {
    role: FULL_ROOT / f"ASTER_FIRE_SE_{role}_MANUAL_FULL_CONTRACT_V1_MASK.png"
    for role in ALL_ROLES
}
OUTPUT_PATHS = {
    "review": VALIDATION_ROOT
    / "ASTER_FIRE_SE_FULL_CONTRACT_V1_INDEPENDENT_V2_REVIEW_1920X1440.png",
    "qa": VALIDATION_ROOT / "ASTER_FIRE_SE_FULL_CONTRACT_V1_INDEPENDENT_V2_QA.json",
    "manifest": VALIDATION_ROOT
    / "ASTER_FIRE_SE_FULL_CONTRACT_V1_INDEPENDENT_V2_MANIFEST.json",
    "evidence": VALIDATION_ROOT
    / "ASTER_FIRE_SE_FULL_CONTRACT_V1_INDEPENDENT_V2_EVIDENCE_1080P_QA.json",
}

ROLE_COLORS: dict[str, tuple[int, int, int]] = {
    "HAIR_BACK": (190, 150, 255),
    "BODY_CORE": (30, 170, 255),
    "HEAD_FACE": (255, 185, 150),
    "HAIR_FRONT": (240, 225, 255),
    "ARM_TRIGGER_UPPER": (0, 220, 255),
    "ARM_SUPPORT_UPPER": (255, 220, 0),
    "RIFLE": (255, 55, 55),
    "TRIGGER_FOREARM_HAND": (0, 255, 180),
    "SUPPORT_FOREARM_HAND": (255, 160, 30),
    "SHOULDER_PLATE": (255, 255, 255),
    "ANATOMICAL_LEFT_WHITE_LEG_MODULE": (110, 255, 255),
    "OPPOSITE_STRAPS_POUCH_LEG": (205, 150, 70),
    "BOOTS_ACCESSORIES": (130, 130, 255),
    "SHOULDER_ELBOW_SEAM_BRIDGE": (255, 0, 255),
    "TARGET_OCCLUDE": (230, 50, 150),
    "TARGET_REVEAL": (50, 255, 80),
}

# Fixed role ownership samples on the locked 1254px SE authority.  They guard
# identity and costume asymmetry; they are not a claim of visual quality.
IDENTITY_LANDMARKS: dict[str, dict[str, Any]] = {
    "mature_face_and_teal_eye_zone": {
        "owner": "HEAD_FACE",
        "points": [(497, 326), (535, 314)],
        "radius": 10,
        "minimum_coverage": 0.22,
    },
    "silver_front_hair": {
        "owner": "HAIR_FRONT",
        "points": [(469, 185), (435, 254)],
        "radius": 12,
        "minimum_coverage": 0.25,
    },
    "split_comet_ponytail": {
        "owner": "HAIR_BACK",
        "points": [(300, 150), (226, 300)],
        "radius": 14,
        "minimum_coverage": 0.22,
    },
    "navy_torso": {
        "owner": "BODY_CORE",
        "points": [(486, 548), (502, 607)],
        "radius": 14,
        "minimum_coverage": 0.30,
    },
    "trigger_upper_sleeve": {
        "owner": "ARM_TRIGGER_UPPER",
        "points": [(393, 352)],
        "radius": 15,
        "minimum_coverage": 0.22,
    },
    "support_upper_sleeve": {
        "owner": "ARM_SUPPORT_UPPER",
        "points": [(651, 431)],
        "radius": 15,
        "minimum_coverage": 0.20,
    },
    "canonical_right_shoulder_plate": {
        "owner": "SHOULDER_PLATE",
        "points": [(635, 323), (669, 361)],
        "radius": 13,
        "minimum_coverage": 0.25,
    },
    "anatomical_left_white_leg_module": {
        "owner": "ANATOMICAL_LEFT_WHITE_LEG_MODULE",
        "points": [(637, 665), (688, 814)],
        "radius": 15,
        "minimum_coverage": 0.22,
    },
    "opposite_thigh_straps_and_pouch": {
        "owner": "OPPOSITE_STRAPS_POUCH_LEG",
        "points": [(350, 672), (320, 650)],
        "radius": 15,
        "minimum_coverage": 0.20,
    },
    "paired_boots_and_accessories": {
        "owner": "BOOTS_ACCESSORIES",
        "points": [(251, 965), (758, 1082)],
        "radius": 16,
        "minimum_coverage": 0.22,
    },
}

# Locked weapon receiver/magazine inspection region.  The report records every
# hard role's share; RIFLE must remain the dominant assigned owner.  This is
# deliberately distinct from the non-weapon flap/strap below the receiver.
RECEIVER_MAGAZINE_POLYGON = np.asarray(
    [(530, 330), (650, 355), (640, 425), (535, 405)], dtype=np.int32
)
UNDER_RECEIVER_BODY_ROI_XYXY = (430, 438, 518, 524)

REPAIR_CONTRACT_TOKENS = [
    "ASTER_COMBAT_SUIT_C01",
    "SHOULDER_ELBOW_SEAM_BRIDGE",
    "TARGET_OCCLUDE",
    "TARGET_REVEAL",
    "6–12px",
    "Technical PASS does not grant visual PASS",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()


def read_image(path: Path, label: str, expected_mode: str) -> tuple[Image.Image, str]:
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    with Image.open(BytesIO(payload)) as opened:
        opened.load()
        if opened.mode != expected_mode:
            raise RuntimeError(f"{label} must use mode {expected_mode}, got {opened.mode}")
        if opened.size != EXPECTED_SIZE:
            raise RuntimeError(
                f"{label} must be 1254x1254, got {opened.size[0]}x{opened.size[1]}"
            )
        image = opened.copy()
    return image, digest


def load_rgb(path: Path, label: str) -> tuple[np.ndarray, str]:
    image, digest = read_image(path, label, "RGB")
    return np.asarray(image, dtype=np.uint8), digest


def load_binary(path: Path, label: str) -> tuple[np.ndarray, str]:
    image, digest = read_image(path, label, "L")
    raw = np.asarray(image, dtype=np.uint8)
    values = np.unique(raw)
    if not set(values.tolist()).issubset({0, 255}):
        raise RuntimeError(f"{label} must contain only 0/255, got {values[:16].tolist()}")
    mask = raw == 255
    if not np.any(mask):
        raise RuntimeError(f"{label} is empty")
    return mask, digest


def fixed_project_file(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(PROJECT_ROOT.resolve())
    except ValueError as error:
        raise RuntimeError(f"{label} must be project-local: {resolved}") from error
    if not resolved.is_file():
        raise RuntimeError(f"{label} is unavailable: {resolved}")
    return resolved


def reject_lexical_symlink_ancestry(candidate: Path, label: str) -> None:
    raw = candidate if candidate.is_absolute() else PROJECT_ROOT / candidate
    lexical = Path(os.path.abspath(raw))
    project = Path(os.path.abspath(PROJECT_ROOT))
    try:
        lexical.relative_to(project)
    except ValueError as error:
        raise RuntimeError(f"{label} must be project-local: {lexical}") from error
    cursor = lexical
    while True:
        if os.path.lexists(cursor) and cursor.is_symlink():
            raise RuntimeError(f"{label} ancestry may not be a symlink: {cursor}")
        if os.path.normcase(str(cursor)) == os.path.normcase(str(project)):
            return
        parent = cursor.parent
        if parent == cursor:
            raise RuntimeError(f"{label} ancestry escaped the project: {lexical}")
        cursor = parent


def paths_overlap_by_ancestry(first: Path, second: Path) -> bool:
    first_text = os.path.normcase(str(first.resolve()))
    second_text = os.path.normcase(str(second.resolve()))
    separator = os.sep
    return (
        first_text == second_text
        or first_text.startswith(second_text + separator)
        or second_text.startswith(first_text + separator)
    )


def resolve_mask_root(candidate: Path) -> Path:
    reject_lexical_symlink_ancestry(candidate, "accepted mask input root")
    requested = require_project_output_path(candidate, "accepted mask input root")
    canonical = require_project_output_path(FULL_ROOT, "canonical accepted mask input root")
    if os.path.normcase(str(requested)) != os.path.normcase(str(canonical)):
        raise RuntimeError(f"accepted mask input root is locked to {canonical}, got {requested}")
    if not canonical.is_dir():
        raise RuntimeError(f"accepted mask input root is unavailable: {canonical}")
    return canonical


def resolve_validation_root(candidate: Path, mask_root: Path) -> Path:
    reject_lexical_symlink_ancestry(candidate, "independent-validation output root")
    requested = require_project_output_path(candidate, "independent-validation output root")
    canonical = require_project_output_path(
        VALIDATION_ROOT, "canonical independent-validation output root"
    )
    if os.path.normcase(str(requested)) != os.path.normcase(str(canonical)):
        raise RuntimeError(
            f"independent-validation output root is locked to {canonical}, got {requested}"
        )
    if paths_overlap_by_ancestry(canonical, mask_root):
        raise RuntimeError(
            "accepted mask input and independent-validation output roots must be disjoint"
        )
    if os.path.lexists(canonical):
        if canonical.is_symlink():
            raise RuntimeError(f"independent-validation root may not be a symlink: {canonical}")
        if not canonical.is_dir():
            raise RuntimeError(f"independent-validation root is not a directory: {canonical}")
        retained = sorted(path.name for path in canonical.iterdir())
        if retained:
            raise RuntimeError(
                "independent-validation v2 is immutable and already contains: "
                + ", ".join(retained)
            )
    else:
        if not canonical.parent.is_dir():
            raise RuntimeError(
                f"independent-validation parent is unavailable: {canonical.parent}"
            )
        canonical.mkdir(parents=False, exist_ok=False)
    return canonical


def output_path(root: Path, key: str, suffix: str) -> Path:
    expected = OUTPUT_PATHS[key]
    candidate = require_project_output_path(root / expected.name, f"{key} output")
    if candidate.parent != root or candidate.suffix.lower() != suffix:
        raise RuntimeError(f"invalid {key} output path: {candidate}")
    if os.path.lexists(candidate):
        raise RuntimeError(f"immutable {key} output already exists: {candidate}")
    return candidate


def no_clobber_commit(temporary: Path, output: Path) -> None:
    if os.path.lexists(output):
        raise RuntimeError(f"refusing to replace existing output: {output}")
    try:
        os.link(temporary, output)
    except FileExistsError as error:
        raise RuntimeError(f"refusing to replace raced output: {output}") from error


def atomic_write_json(payload: dict[str, Any], output: Path) -> None:
    temporary = output.with_name(f"{output.name}.tmp-{os.getpid()}")
    if os.path.lexists(temporary):
        raise RuntimeError(f"temporary output already exists: {temporary}")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        json.loads(temporary.read_text(encoding="utf-8"))
        no_clobber_commit(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_save_review(image: Image.Image, output: Path) -> None:
    temporary = output.with_name(f"{output.name}.tmp-{os.getpid()}.png")
    if os.path.lexists(temporary):
        raise RuntimeError(f"temporary review already exists: {temporary}")
    try:
        with temporary.open("xb") as handle:
            image.save(handle, format="PNG")
        with Image.open(temporary) as decoded:
            decoded.verify()
        with Image.open(temporary) as decoded:
            if decoded.mode != "RGB" or decoded.size != REVIEW_SIZE:
                raise RuntimeError(
                    f"review decode mismatch: mode={decoded.mode} size={decoded.size}"
                )
        no_clobber_commit(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)


def component_metrics(mask: np.ndarray) -> dict[str, Any]:
    count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8), 8
    )
    areas = sorted((int(value) for value in stats[1:, cv2.CC_STAT_AREA]), reverse=True)
    ys, xs = np.nonzero(mask)
    return {
        "pixels": int(np.count_nonzero(mask)),
        "components": max(0, count - 1),
        "significant_components_32px": sum(area >= 32 for area in areas),
        "largest_component_ratio": float(areas[0]) / float(max(1, sum(areas))),
        "bbox_xyxy_exclusive": [
            int(xs.min()),
            int(ys.min()),
            int(xs.max()) + 1,
            int(ys.max()) + 1,
        ],
    }


def circle_mask(point: tuple[int, int], radius: int) -> np.ndarray:
    yy, xx = np.ogrid[: EXPECTED_SIZE[1], : EXPECTED_SIZE[0]]
    return (xx - point[0]) ** 2 + (yy - point[1]) ** 2 <= radius**2


def circle_coverage(mask: np.ndarray, point: tuple[int, int], radius: int) -> float:
    region = circle_mask(point, radius)
    return float(np.count_nonzero(mask & region)) / float(max(1, np.count_nonzero(region)))


def reject_hardlink_collisions(inputs: list[Path], outputs: list[Path]) -> None:
    normalized = [os.path.normcase(str(path.resolve())) for path in inputs + outputs]
    if len(normalized) != len(set(normalized)):
        raise RuntimeError("input/output path collision")
    existing = [path for path in inputs + outputs if path.exists()]
    for index, first in enumerate(existing):
        for second in existing[index + 1 :]:
            if os.path.samefile(first, second):
                raise RuntimeError(f"hardlink/path alias collision: {first} == {second}")


def validate_locked_json_lineage(
    manual_manifest: dict[str, Any], guide_manifest: dict[str, Any], failures: list[str]
) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    manual_checks = {
        "costume_id": manual_manifest.get("costume_id") == COSTUME_ID,
        "promotion_ready_false": manual_manifest.get("promotion_ready") is False,
        "contract_complete_false": manual_manifest.get("contract_complete") is False,
        "technical_result": manual_manifest.get("technical_result")
        == "PASS_THREE_SE_SOURCE_MASK_CHECKS_ONLY_HOLD",
        "source_path": manual_manifest.get("source") == relative(AUTHORITY_SOURCE),
        "source_sha": manual_manifest.get("source_sha256")
        == LOCKED_SHA256["authority_source"],
        "subject_path": manual_manifest.get("subject_mask") == relative(AUTHORITY_SUBJECT),
        "subject_sha": manual_manifest.get("subject_mask_sha256")
        == LOCKED_SHA256["authority_subject"],
    }
    manual_parts = manual_manifest.get("parts", {})
    for role, key in (
        ("RIFLE", "rifle"),
        ("TRIGGER_FOREARM_HAND", "trigger_forearm_hand"),
        ("SUPPORT_FOREARM_HAND", "support_forearm_hand"),
    ):
        record = manual_parts.get(key, {})
        manual_checks[f"{role}_path"] = record.get("path") == relative(
            LOCKED_ROLE_AUTHORITIES[role]
        )
        manual_checks[f"{role}_sha"] = record.get("sha256") == LOCKED_SHA256[role]
    checks["manual_three_manifest"] = manual_checks
    for name, passed in manual_checks.items():
        if not passed:
            failures.append(f"locked manual-three manifest check failed: {name}")

    records = guide_manifest.get("records", [])
    sse_records = [record for record in records if record.get("direction") == "SSE"]
    guide_checks: dict[str, bool] = {"one_sse_record": len(sse_records) == 1}
    if len(sse_records) == 1:
        record = sse_records[0]
        guide_checks.update(
            {
                "angle_67_5": record.get("angle_degrees") == 67.5,
                "image_path": record.get("image") == relative(SSE_GUIDE),
                "image_sha": record.get("sha256") == LOCKED_SHA256["sse_guide"],
                "resolution_1254": record.get("resolution") == [1254, 1254],
                "one_corridor": record.get("rifle_hands_forearms_one_corridor") is True,
                "not_final_character": record.get("final_character_asset") is False,
                "no_white_shoulder_proxy": record.get("unauthorized_white_shoulder_proxy_present")
                is False,
            }
        )
    costume_safety = guide_manifest.get("costume_safety", {})
    guide_checks["manifest_no_white_shoulder_proxy"] = (
        costume_safety.get("unauthorized_white_shoulder_proxy_present") is False
    )
    checks["sse_guide_manifest"] = guide_checks
    for name, passed in guide_checks.items():
        if not passed:
            failures.append(f"locked SSE guide manifest check failed: {name}")
    return checks


def validate_accepted_manifest(
    accepted_manifest: dict[str, Any],
    role_paths: dict[str, Path],
    digests: dict[str, str],
    failures: list[str],
) -> dict[str, Any]:
    outputs = accepted_manifest.get("outputs", {})
    checks: dict[str, Any] = {
        "result": accepted_manifest.get("result") == PASS_RESULT,
        "candidate_status_hold": accepted_manifest.get("candidate_status") == "HOLD",
        "contract_complete_true": accepted_manifest.get("contract_complete") is True,
        "promotion_ready_false": accepted_manifest.get("promotion_ready") is False,
        "runtime_asset_false": accepted_manifest.get("runtime_asset") is False,
        "runtime_promotion_false": accepted_manifest.get("runtime_promotion") is False,
        "visual_pass_false": accepted_manifest.get("visual_pass") is False,
        "costume_id": accepted_manifest.get("costume_id") == COSTUME_ID,
        "exact_role_set": isinstance(outputs, dict) and set(outputs) == set(ALL_ROLES),
    }
    role_checks: dict[str, Any] = {}
    for role in ALL_ROLES:
        record = outputs.get(role, {}) if isinstance(outputs, dict) else {}
        role_record = {
            "path": record.get("path") == relative(role_paths[role]),
            "sha256": record.get("sha256") == digests.get(role),
            "mode": record.get("mode") == "L",
            "resolution": record.get("resolution") == list(EXPECTED_SIZE),
            "binary_values": record.get("binary_values") == [0, 255],
        }
        role_checks[role] = role_record
        for name, passed in role_record.items():
            if not passed:
                failures.append(f"accepted manifest {role} check failed: {name}")
    for name, passed in checks.items():
        if not passed:
            failures.append(f"accepted manifest check failed: {name}")
    checks["roles"] = role_checks
    return checks


def validate_masks(
    source: np.ndarray,
    masks: dict[str, np.ndarray],
    failures: list[str],
) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    subject = masks["SUBJECT"]
    subject_pixels = int(np.count_nonzero(subject))
    exact_green = np.all(source == GREEN, axis=2)
    green_metrics = {
        "outside_subject_non_exact_green_pixels": int(
            np.count_nonzero((~subject) & (~exact_green))
        ),
        "inside_subject_exact_green_pixels": int(np.count_nonzero(subject & exact_green)),
    }
    metrics["locked_authority_green"] = green_metrics
    if green_metrics["outside_subject_non_exact_green_pixels"]:
        failures.append(
            "locked source exterior contains "
            f"{green_metrics['outside_subject_non_exact_green_pixels']} non-#00FF00 pixels"
        )
    if green_metrics["inside_subject_exact_green_pixels"]:
        failures.append(
            "locked subject contains "
            f"{green_metrics['inside_subject_exact_green_pixels']} exact-green pixels"
        )

    for role in ALL_ROLES:
        mask = masks[role]
        item = component_metrics(mask)
        item["subject_fraction"] = float(item["pixels"]) / float(max(1, subject_pixels))
        item["outside_subject_pixels"] = int(np.count_nonzero(mask & ~subject))
        item["exact_green_pixels"] = int(np.count_nonzero(mask & exact_green))
        metrics.setdefault("roles", {})[role] = item
        if role != "SUBJECT" and item["outside_subject_pixels"]:
            failures.append(
                f"{role}: {item['outside_subject_pixels']} pixels outside locked SUBJECT"
            )
        if role != "SUBJECT" and item["exact_green_pixels"]:
            failures.append(f"{role}: {item['exact_green_pixels']} exact-green pixels included")

    hard_count = np.zeros(EXPECTED_SIZE[::-1], dtype=np.uint16)
    for role in HARD_PART_ROLES:
        hard_count += masks[role].astype(np.uint16)
    seam = masks["SHOULDER_ELBOW_SEAM_BRIDGE"]
    occlude = masks["TARGET_OCCLUDE"]
    reveal = masks["TARGET_REVEAL"]
    allowed_band = seam | occlude | reveal
    all_count = hard_count.copy()
    for role in BAND_ROLES:
        all_count += masks[role].astype(np.uint16)

    hard_overlap = subject & (hard_count > 1)
    undeclared_miss = subject & (hard_count == 0) & ~allowed_band
    undeclared_overlap = subject & (all_count > 1) & ~allowed_band
    hard_union_outside_subject = (hard_count > 0) & ~subject
    metrics["partition"] = {
        "hard_part_overlap_pixels": int(np.count_nonzero(hard_overlap)),
        "subject_miss_pixels_total": int(np.count_nonzero(subject & (hard_count == 0))),
        "subject_miss_pixels_outside_declared_bands": int(np.count_nonzero(undeclared_miss)),
        "all_role_overlap_pixels_total": int(np.count_nonzero(subject & (all_count > 1))),
        "overlap_pixels_outside_declared_bands": int(np.count_nonzero(undeclared_overlap)),
        "hard_union_outside_subject_pixels": int(np.count_nonzero(hard_union_outside_subject)),
        "declared_band_pixels": int(np.count_nonzero(allowed_band)),
    }
    if np.any(hard_overlap):
        failures.append(
            f"hard semantic parts overlap at {np.count_nonzero(hard_overlap)} subject pixels"
        )
    if np.any(undeclared_miss):
        failures.append(
            f"hard-part union misses {np.count_nonzero(undeclared_miss)} subject pixels outside declared bands"
        )
    if np.any(undeclared_overlap):
        failures.append(
            f"role union overlaps at {np.count_nonzero(undeclared_overlap)} pixels outside declared bands"
        )
    if np.any(hard_union_outside_subject):
        failures.append(
            f"hard-part union has {np.count_nonzero(hard_union_outside_subject)} pixels outside SUBJECT"
        )

    pair_overlaps: dict[str, int] = {}
    for index, first in enumerate(HARD_PART_ROLES):
        for second in HARD_PART_ROLES[index + 1 :]:
            overlap = int(np.count_nonzero(masks[first] & masks[second]))
            pair_overlaps[f"{first}__{second}"] = overlap
            if overlap:
                failures.append(f"hard-part overlap {first}/{second}: {overlap} pixels")
    metrics["hard_part_pair_overlaps"] = pair_overlaps

    target_overlap = int(np.count_nonzero(occlude & reveal))
    target_fraction = {
        role: float(np.count_nonzero(masks[role])) / float(max(1, subject_pixels))
        for role in ("TARGET_OCCLUDE", "TARGET_REVEAL")
    }
    metrics["target_occlusion_bands"] = {
        "occlude_reveal_overlap_pixels": target_overlap,
        "subject_fractions": target_fraction,
        "ordering_authority": "Blender SSE guide only; guide pixels are never final character art",
    }
    if target_overlap:
        failures.append(f"TARGET_OCCLUDE/TARGET_REVEAL overlap: {target_overlap} pixels")
    for role, fraction in target_fraction.items():
        if not 0.0001 <= fraction <= 0.25:
            failures.append(f"{role} subject fraction {fraction:.6f} outside 0.0001-0.25")

    distance = cv2.distanceTransform(seam.astype(np.uint8), cv2.DIST_L2, 5)
    seam_distances = distance[seam]
    width_p95 = 2.0 * float(np.percentile(seam_distances, 95))
    width_max = 2.0 * float(np.max(seam_distances))
    seam_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
    expected_seam = np.zeros_like(subject)
    seam_pairs: dict[str, Any] = {}
    for upper_role, forearm_role in (
        ("ARM_TRIGGER_UPPER", "TRIGGER_FOREARM_HAND"),
        ("ARM_SUPPORT_UPPER", "SUPPORT_FOREARM_HAND"),
    ):
        upper = masks[upper_role]
        forearm = masks[forearm_role]
        expected_pair = (
            (cv2.dilate(upper.astype(np.uint8), seam_kernel) > 0)
            & (cv2.dilate(forearm.astype(np.uint8), seam_kernel) > 0)
            & subject
        )
        distance_to_upper = cv2.distanceTransform(
            (~upper).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE
        )
        distance_to_forearm = cv2.distanceTransform(
            (~forearm).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE
        )
        pair_name = f"{upper_role}__{forearm_role}"
        pair_metrics = {
            "pixels": int(np.count_nonzero(expected_pair)),
            "accepted_seam_pixels_on_pair": int(np.count_nonzero(seam & expected_pair)),
            "max_distance_to_upper_pixels": (
                float(distance_to_upper[expected_pair].max())
                if np.any(expected_pair)
                else None
            ),
            "max_distance_to_forearm_pixels": (
                float(distance_to_forearm[expected_pair].max())
                if np.any(expected_pair)
                else None
            ),
            "maximum_allowed_distance_each_side_with_raster_tolerance": 6.5,
        }
        seam_pairs[pair_name] = pair_metrics
        expected_seam |= expected_pair
        if pair_metrics["pixels"] == 0:
            failures.append(f"seam pair is empty: {pair_name}")
        if (
            pair_metrics["max_distance_to_upper_pixels"] is not None
            and pair_metrics["max_distance_to_upper_pixels"] > 6.5
        ):
            failures.append(f"seam pair exceeds upper-side 6px dilation: {pair_name}")
        if (
            pair_metrics["max_distance_to_forearm_pixels"] is not None
            and pair_metrics["max_distance_to_forearm_pixels"] > 6.5
        ):
            failures.append(f"seam pair exceeds forearm-side 6px dilation: {pair_name}")

    seam_missing = int(np.count_nonzero(expected_seam & ~seam))
    seam_extra = int(np.count_nonzero(seam & ~expected_seam))
    seam_xor = seam_missing + seam_extra
    seam_on_interface = int(np.count_nonzero(seam & expected_seam))
    seam_pixels = int(np.count_nonzero(seam))
    seam_interface_ratio = float(seam_on_interface) / float(max(1, seam_pixels))
    seam_metrics = {
        "derivation": (
            "union((dilate(UPPER, ellipse radius=6) intersection "
            "dilate(FOREARM_HAND, ellipse radius=6)) intersection SUBJECT)"
        ),
        "native_dilation_radius_each_side_pixels": 6,
        "declared_full_boundary_band_max_pixels": 12,
        "exact_expected_union_pixels": int(np.count_nonzero(expected_seam)),
        "exact_xor_pixels": seam_xor,
        "missing_expected_pixels": seam_missing,
        "unexpected_extra_pixels": seam_extra,
        "pairs": seam_pairs,
        "distance_transform_width_p95_pixels": width_p95,
        "distance_transform_width_max_pixels": width_max,
        "distance_transform_width_is_diagnostic_only": (
            "curved junction caps can exceed the nominal 12px band in raster space"
        ),
        "pixels": seam_pixels,
        "interface_support_ratio": seam_interface_ratio,
        "trigger_interface_pixels": seam_pairs[
            "ARM_TRIGGER_UPPER__TRIGGER_FOREARM_HAND"
        ]["accepted_seam_pixels_on_pair"],
        "support_interface_pixels": seam_pairs[
            "ARM_SUPPORT_UPPER__SUPPORT_FOREARM_HAND"
        ]["accepted_seam_pixels_on_pair"],
    }
    metrics["shoulder_elbow_seam_bridge"] = seam_metrics
    if seam_xor:
        failures.append(
            f"seam bridge differs from locked 6px-per-side derivation by {seam_xor} pixels"
        )
    if seam_interface_ratio != 1.0:
        failures.append(f"seam interface support {seam_interface_ratio:.6f} != 1.0")
    if seam_metrics["trigger_interface_pixels"] == 0:
        failures.append("seam bridge does not cover the trigger shoulder/elbow interface")
    if seam_metrics["support_interface_pixels"] == 0:
        failures.append("seam bridge does not cover the support shoulder/elbow interface")

    landmark_report: dict[str, Any] = {}
    for name, rule in IDENTITY_LANDMARKS.items():
        owner = rule["owner"]
        coverages = [
            circle_coverage(masks[owner], point, int(rule["radius"]))
            for point in rule["points"]
        ]
        passed = all(value >= float(rule["minimum_coverage"]) for value in coverages)
        landmark_report[name] = {
            "owner": owner,
            "points_xy": [list(point) for point in rule["points"]],
            "radius": rule["radius"],
            "minimum_coverage": rule["minimum_coverage"],
            "coverage": coverages,
            "pass": passed,
        }
        if not passed:
            failures.append(f"identity/costume landmark ownership failed: {name} -> {owner}")
    metrics["identity_costume_landmarks"] = landmark_report

    receiver_weapon_roi = np.zeros(EXPECTED_SIZE[::-1], dtype=np.uint8)
    cv2.fillPoly(receiver_weapon_roi, [RECEIVER_MAGAZINE_POLYGON], 1)
    receiver_counts = {
        role: int(np.count_nonzero(masks[role] & (receiver_weapon_roi > 0)))
        for role in HARD_PART_ROLES
    }
    assigned = sum(receiver_counts.values())
    dominant = max(receiver_counts, key=receiver_counts.get)
    rifle_share = float(receiver_counts["RIFLE"]) / float(max(1, assigned))
    receiver_report = {
        "polygon_xy": RECEIVER_MAGAZINE_POLYGON.tolist(),
        "semantic_decision": "weapon receiver/magazine remains owned by RIFLE",
        "expected_owner": "RIFLE",
        "assigned_pixels_by_role": receiver_counts,
        "assigned_pixels": assigned,
        "dominant_owner": dominant,
        "rifle_share_of_assigned_pixels": rifle_share,
        "pass": dominant == "RIFLE" and rifle_share >= 0.85,
    }
    metrics["receiver_magazine_weapon_ownership"] = receiver_report
    if not receiver_report["pass"]:
        failures.append(
            f"receiver/magazine ownership is {dominant}, RIFLE share {rifle_share:.6f} < 0.85"
        )

    x1, y1, x2, y2 = UNDER_RECEIVER_BODY_ROI_XYXY
    under_receiver_subject = subject[y1:y2, x1:x2]
    under_receiver_body = masks["BODY_CORE"][y1:y2, x1:x2]
    under_receiver_subject_pixels = int(np.count_nonzero(under_receiver_subject))
    under_receiver_body_pixels = int(np.count_nonzero(under_receiver_body))
    under_receiver_body_fraction = float(under_receiver_body_pixels) / float(
        max(1, under_receiver_subject_pixels)
    )
    under_receiver_report = {
        "roi_xyxy_exclusive": list(UNDER_RECEIVER_BODY_ROI_XYXY),
        "semantic_decision": (
            "receiver-under non-weapon flap/strap remains owned by BODY_CORE"
        ),
        "expected_owner": "BODY_CORE",
        "subject_pixels": under_receiver_subject_pixels,
        "body_core_pixels": under_receiver_body_pixels,
        "body_core_fraction_of_subject": under_receiver_body_fraction,
        "minimum_required_body_core_pixels": 4000,
        "minimum_required_fraction": 0.75,
        "pass": (
            under_receiver_body_pixels >= 4000
            and under_receiver_body_fraction >= 0.75
        ),
    }
    metrics["receiver_under_nonweapon_flap_strap_body_core_ownership"] = (
        under_receiver_report
    )
    if under_receiver_body_pixels < 4000:
        failures.append(
            "receiver-under non-weapon flap/strap BODY_CORE pixel support is insufficient"
        )
    if under_receiver_body_fraction < 0.75:
        failures.append(
            "receiver-under non-weapon flap/strap BODY_CORE coverage fraction is insufficient"
        )

    rigid = (
        masks["RIFLE"]
        | masks["TRIGGER_FOREARM_HAND"]
        | masks["SUPPORT_FOREARM_HAND"]
    )
    rigid_closed = cv2.morphologyEx(
        rigid.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)
    ) > 0
    rigid_metrics = component_metrics(rigid_closed)
    metrics["rigid_rifle_hands_forearms_after_2px_close"] = rigid_metrics
    if rigid_metrics["significant_components_32px"] != 1:
        failures.append(
            "rigid RIFLE|TRIGGER_FOREARM_HAND|SUPPORT_FOREARM_HAND union is not one corridor"
        )

    metrics["composition_invariants"] = {
        "hair_back_layer": "behind BODY_CORE and HEAD_FACE",
        "hair_front_layer": "in front of HEAD_FACE and neck",
        "sse_rifle_cluster_layer": "in front of BODY_CORE",
        "anatomical_asymmetry_mirroring_allowed": False,
        "runtime_promotion": False,
        "visual_pass_claimed": False,
    }
    return metrics


def overlay(source: np.ndarray, mask: np.ndarray, color: tuple[int, int, int]) -> np.ndarray:
    result = source.astype(np.float32).copy()
    tint = np.asarray(color, dtype=np.float32)
    result[mask] = result[mask] * 0.48 + tint * 0.52
    return np.clip(result, 0, 255).astype(np.uint8)


def build_review(
    source: np.ndarray | None,
    masks: dict[str, np.ndarray],
    result: str,
    missing_roles: list[str],
    failures: list[str],
) -> Image.Image:
    if source is None:
        native = np.full((EXPECTED_SIZE[1], EXPECTED_SIZE[0], 3), (26, 28, 34), np.uint8)
    else:
        native = source.copy()
    diagnostic = native.copy()
    for role in HARD_PART_ROLES + BAND_ROLES:
        mask = masks.get(role)
        if mask is None:
            continue
        color = ROLE_COLORS[role]
        diagnostic = overlay(diagnostic, mask, color)
        contours, _ = cv2.findContours(
            mask.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(native, contours, -1, color, 2)
    subject = masks.get("SUBJECT")
    if subject is not None:
        contours, _ = cv2.findContours(
            subject.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(native, contours, -1, (255, 255, 255), 2)
    cv2.polylines(
        native,
        [RECEIVER_MAGAZINE_POLYGON],
        isClosed=True,
        color=(255, 70, 70),
        thickness=2,
    )
    x1, y1, x2, y2 = UNDER_RECEIVER_BODY_ROI_XYXY
    cv2.rectangle(native, (x1, y1), (x2 - 1, y2 - 1), (255, 0, 255), 2)

    canvas = Image.new("RGB", REVIEW_SIZE, (18, 20, 26))
    canvas.paste(Image.fromarray(native), (24, 88))
    runtime = Image.fromarray(diagnostic).resize((384, 384), Image.Resampling.LANCZOS)
    gameplay = Image.fromarray(diagnostic).resize((131, 131), Image.Resampling.LANCZOS)
    canvas.paste(runtime, (1302, 88))
    canvas.paste(gameplay, (1710, 88))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text(
        (24, 24),
        f"ASTER FIRE16 SE FULL SOURCE-MASK INDEPENDENT VALIDATION V2 — {result}",
        fill="white",
        font=font,
    )
    draw.text((1302, 486), "SOURCE CONTRACT ONLY — ALWAYS HOLD", fill=(255, 188, 70), font=font)
    draw.text((1302, 512), f"Loaded roles: {len(masks)}/17", fill=(205, 215, 225), font=font)
    draw.text((1302, 536), "Native: 1254x1254 at 1:1", fill=(205, 215, 225), font=font)
    draw.text((1302, 560), "Inspection panels: 384px / 131px at 1:1", fill=(205, 215, 225), font=font)
    draw.text((1302, 590), "No runtime promotion. No visual PASS.", fill=(255, 188, 70), font=font)
    draw.text((1302, 614), "RED: receiver/magazine RIFLE ROI", fill=(255, 105, 105), font=font)
    draw.text((1302, 638), "MAGENTA: under-receiver BODY_CORE ROI", fill=(255, 105, 255), font=font)
    y = 676
    if missing_roles:
        draw.text((1302, y), "MISSING ROLES", fill=(255, 105, 105), font=font)
        y += 22
        for role in missing_roles:
            draw.text((1302, y), role, fill=(255, 125, 125), font=font)
            y += 18
    if failures:
        y += 10
        draw.text((1302, y), f"FAILURES ({len(failures)})", fill=(255, 105, 105), font=font)
        y += 22
        for failure in failures[:20]:
            lines = [failure[index : index + 68] for index in range(0, len(failure), 68)]
            for line in lines:
                if y > 1405:
                    break
                draw.text((1302, y), line, fill=(255, 135, 135), font=font)
                y += 17
            if y > 1405:
                break
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the locked ASTER Fire16 SE native 17-mask source contract."
    )
    parser.add_argument(
        "--mask-root",
        type=Path,
        default=FULL_ROOT,
        help="Read-only accepted_v1 input root; other roots are rejected.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=VALIDATION_ROOT,
        help="Locked independent_validation_v2 output root; other roots are rejected.",
    )
    args = parser.parse_args()

    mask_root = resolve_mask_root(args.mask_root)
    validation_root = resolve_validation_root(args.output_root, mask_root)
    role_paths = {
        role: mask_root / ROLE_PATHS[role].name
        for role in ALL_ROLES
    }
    outputs = {
        "review": output_path(validation_root, "review", ".png"),
        "qa": output_path(validation_root, "qa", ".json"),
        "manifest": output_path(validation_root, "manifest", ".json"),
        "evidence": output_path(validation_root, "evidence", ".json"),
    }
    failures: list[str] = []
    missing_roles: list[str] = []
    input_paths = {
        "authority_source": AUTHORITY_SOURCE,
        "authority_subject": AUTHORITY_SUBJECT,
        "repair_contract": REPAIR_CONTRACT,
        "sse_guide": SSE_GUIDE,
        "guide_manifest": GUIDE_MANIFEST,
        "manual_three_manifest": MANUAL_THREE_MANIFEST,
        "accepted_manifest": ACCEPTED_MANIFEST,
        "manual_RIFLE": LOCKED_ROLE_AUTHORITIES["RIFLE"],
        "manual_TRIGGER_FOREARM_HAND": LOCKED_ROLE_AUTHORITIES["TRIGGER_FOREARM_HAND"],
        "manual_SUPPORT_FOREARM_HAND": LOCKED_ROLE_AUTHORITIES["SUPPORT_FOREARM_HAND"],
        **role_paths,
    }
    reject_hardlink_collisions(
        [path for path in input_paths.values() if path.exists()], list(outputs.values())
    )

    digests: dict[str, str] = {}
    dependency_paths: dict[str, str] = {}
    for key, path in input_paths.items():
        dependency_paths[key] = relative(path)
        if not path.is_file():
            if key in ALL_ROLES:
                missing_roles.append(key)
                failures.append(f"missing required mask {key}: {relative(path)}")
            else:
                failures.append(f"missing locked dependency {key}: {relative(path)}")
            continue
        digest = sha256(path)
        digests[key] = digest
        expected = LOCKED_SHA256.get(key)
        if expected is not None and digest != expected:
            failures.append(f"locked SHA mismatch for {key}: {digest} != {expected}")

    source: np.ndarray | None = None
    masks: dict[str, np.ndarray] = {}
    try:
        source_path = fixed_project_file(AUTHORITY_SOURCE, "locked SE authority source")
        source, source_digest = load_rgb(source_path, "locked SE authority source")
        digests["authority_source"] = source_digest
    except Exception as error:  # Fail report must survive corrupt authority input.
        failures.append(f"authority source load failed: {error}")

    for role in ALL_ROLES:
        path = role_paths[role]
        if not path.is_file():
            if role not in missing_roles:
                missing_roles.append(role)
            continue
        try:
            loaded, digest = load_binary(path, role)
            masks[role] = loaded
            digests[role] = digest
            expected = LOCKED_SHA256.get(role)
            if expected is not None and digest != expected:
                failures.append(f"locked SHA mismatch for {role}: {digest} != {expected}")
        except Exception as error:
            failures.append(f"{role} mask load failed: {error}")
            if role not in missing_roles:
                missing_roles.append(role)

    locked_lineage_checks: dict[str, Any] = {}
    try:
        contract_text = fixed_project_file(REPAIR_CONTRACT, "repair contract").read_text(
            encoding="utf-8"
        )
        token_checks = {token: token in contract_text for token in REPAIR_CONTRACT_TOKENS}
        locked_lineage_checks["repair_contract_tokens"] = token_checks
        for token, passed in token_checks.items():
            if not passed:
                failures.append(f"repair contract token missing: {token}")
    except Exception as error:
        failures.append(f"repair contract read failed: {error}")

    try:
        _guide, guide_digest = load_rgb(
            fixed_project_file(SSE_GUIDE, "locked SSE guide"), "locked SSE guide"
        )
        digests["sse_guide"] = guide_digest
    except Exception as error:
        failures.append(f"SSE guide load failed: {error}")

    try:
        manual_manifest = json.loads(
            fixed_project_file(MANUAL_THREE_MANIFEST, "manual-three manifest").read_text(
                encoding="utf-8"
            )
        )
        guide_manifest = json.loads(
            fixed_project_file(GUIDE_MANIFEST, "SSE guide manifest").read_text(
                encoding="utf-8"
            )
        )
        locked_lineage_checks.update(
            validate_locked_json_lineage(manual_manifest, guide_manifest, failures)
        )
    except Exception as error:
        failures.append(f"locked manifest validation failed: {error}")

    try:
        accepted_manifest = json.loads(
            fixed_project_file(ACCEPTED_MANIFEST, "accepted full-contract manifest").read_text(
                encoding="utf-8"
            )
        )
        locked_lineage_checks["accepted_full_contract_manifest"] = (
            validate_accepted_manifest(
                accepted_manifest,
                role_paths,
                digests,
                failures,
            )
        )
    except Exception as error:
        failures.append(f"accepted full-contract manifest validation failed: {error}")

    metrics: dict[str, Any] = {}
    inputs_complete = source is not None and set(masks) == set(ALL_ROLES)
    if inputs_complete:
        metrics = validate_masks(source, masks, failures)
    else:
        missing_set = sorted(set(ALL_ROLES) - set(masks))
        missing_roles = sorted(set(missing_roles) | set(missing_set))
        failures.append(
            "full 17-mask validation skipped because required inputs are missing or invalid: "
            + ", ".join(missing_roles)
        )

    contract_complete = inputs_complete and not failures
    result = PASS_RESULT if contract_complete else FAIL_RESULT
    run_id = datetime.now(timezone.utc).isoformat()
    review = build_review(source, masks, result, missing_roles, failures)
    atomic_save_review(review, outputs["review"])

    evidence_process = subprocess.run(
        [
            sys.executable,
            str(EVIDENCE_VALIDATOR),
            str(outputs["review"]),
            "--require-dynamic-capture",
            "--output",
            str(outputs["evidence"]),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if evidence_process.returncode != 0:
        raise RuntimeError(
            "1080p evidence validator failed: "
            + evidence_process.stdout
            + evidence_process.stderr
        )
    evidence = json.loads(outputs["evidence"].read_text(encoding="utf-8"))
    if evidence.get("gate") != "PASS":
        raise RuntimeError(f"1080p evidence gate did not pass: {evidence.get('gate')}")

    input_integrity_after_evidence: dict[str, bool] = {}
    for key, path in input_paths.items():
        if not path.is_file() or key not in digests:
            input_integrity_after_evidence[key] = False
            continue
        input_integrity_after_evidence[key] = sha256(path) == digests[key]
    changed_inputs = sorted(
        key for key, unchanged in input_integrity_after_evidence.items() if not unchanged
    )
    if changed_inputs:
        raise RuntimeError(
            "accepted/locked input changed during independent validation: "
            + ", ".join(changed_inputs)
        )

    qa = {
        "schema": 2,
        "validator_revision": 2,
        "run_id_utc": run_id,
        "role": "ASTER Fire16 locked-SE full 17-mask native source-contract QA",
        "result": result,
        "candidate_status": "HOLD",
        "inputs_complete": inputs_complete,
        "contract_complete": contract_complete,
        "promotion_ready": False,
        "runtime_asset": False,
        "runtime_promotion": False,
        "visual_pass_claimed": False,
        "visual_gate": "HOLD_USER_VISUAL_REVIEW_REQUIRED",
        "costume_id": COSTUME_ID,
        "accepted_input_root": relative(mask_root),
        "independent_output_root": relative(validation_root),
        "required_roles": ALL_ROLES,
        "loaded_roles": sorted(masks),
        "missing_or_invalid_roles": missing_roles,
        "source_resolution": list(EXPECTED_SIZE),
        "paths": dependency_paths,
        "sha256": digests,
        "locked_lineage_checks": locked_lineage_checks,
        "input_integrity_after_evidence": input_integrity_after_evidence,
        "metrics": metrics,
        "failures": failures,
        "review": relative(outputs["review"]),
        "review_sha256": sha256(outputs["review"]),
        "review_resolution": list(REVIEW_SIZE),
        "evidence_1080p": {
            "path": relative(outputs["evidence"]),
            "sha256": sha256(outputs["evidence"]),
            "gate": evidence.get("gate"),
            "quality_claim": False,
        },
        "native_panel": {"xy": [24, 88], "resolution": [1254, 1254], "scale": "1:1"},
        "runtime_inspection_panel": {
            "xy": [1302, 88],
            "resolution": [384, 384],
            "scale": "1:1 inspection only",
        },
        "gameplay_inspection_panel": {
            "xy": [1710, 88],
            "resolution": [131, 131],
            "scale": "1:1 inspection only",
        },
        "network_used": False,
        "server_used": False,
        "existing_outputs_preemptively_deleted": False,
    }
    atomic_write_json(qa, outputs["qa"])

    manifest = {
        "schema": 2,
        "validator_revision": 2,
        "run_id_utc": run_id,
        "role": "ASTER Fire16 SE full native source-mask independent validation record",
        "result": result,
        "status": "HOLD",
        "inputs_complete": inputs_complete,
        "contract_complete": contract_complete,
        "promotion_ready": False,
        "runtime_asset": False,
        "visual_pass_claimed": False,
        "costume_id": COSTUME_ID,
        "accepted_input_root": relative(mask_root),
        "independent_output_root": relative(validation_root),
        "source": {
            "path": relative(AUTHORITY_SOURCE),
            "sha256": digests.get("authority_source"),
            "resolution": list(EXPECTED_SIZE),
        },
        "mask_records": {
            role: {
                "path": dependency_paths[role],
                "sha256": digests.get(role),
                "loaded": role in masks,
                "mode": "L",
                "binary_values": [0, 255],
                "resolution": list(EXPECTED_SIZE),
            }
            for role in ALL_ROLES
        },
        "locked_lineage": {
            "authority_subject": {
                "path": relative(AUTHORITY_SUBJECT),
                "sha256": digests.get("authority_subject"),
            },
            "repair_contract": {
                "path": relative(REPAIR_CONTRACT),
                "sha256": digests.get("repair_contract"),
            },
            "manual_three_manifest": {
                "path": relative(MANUAL_THREE_MANIFEST),
                "sha256": digests.get("manual_three_manifest"),
            },
            "accepted_full_contract_manifest": {
                "path": relative(ACCEPTED_MANIFEST),
                "sha256": digests.get("accepted_manifest"),
            },
            "manual_three_authority_masks": {
                role: {
                    "path": relative(LOCKED_ROLE_AUTHORITIES[role]),
                    "sha256": digests.get(f"manual_{role}"),
                }
                for role in (
                    "RIFLE",
                    "TRIGGER_FOREARM_HAND",
                    "SUPPORT_FOREARM_HAND",
                )
            },
            "sse_guide": {
                "path": relative(SSE_GUIDE),
                "sha256": digests.get("sse_guide"),
            },
            "sse_guide_manifest": {
                "path": relative(GUIDE_MANIFEST),
                "sha256": digests.get("guide_manifest"),
            },
        },
        "declared_overlap_bands": BAND_ROLES,
        "hard_disjoint_roles": HARD_PART_ROLES,
        "receiver_magazine_weapon_expected_owner": "RIFLE",
        "receiver_under_nonweapon_flap_strap_expected_owner": "BODY_CORE",
        "qa": {"path": relative(outputs["qa"]), "sha256": sha256(outputs["qa"])},
        "review": {
            "path": relative(outputs["review"]),
            "sha256": sha256(outputs["review"]),
            "resolution": list(REVIEW_SIZE),
        },
        "evidence_1080p": {
            "path": relative(outputs["evidence"]),
            "sha256": sha256(outputs["evidence"]),
            "gate": evidence.get("gate"),
            "quality_claim": False,
        },
        "prohibitions": [
            "no source mutation",
            "no runtime promotion",
            "no visual PASS claim",
            "no independently transformed rigid-cluster parts",
            "no image or mask authoring by this validator",
        ],
        "failures": failures,
    }
    atomic_write_json(manifest, outputs["manifest"])

    print(
        json.dumps(
            {
                "result": result,
                "contract_complete": contract_complete,
                "loaded_roles": len(masks),
                "failures": len(failures),
                "qa": str(outputs["qa"]),
                "manifest": str(outputs["manifest"]),
            },
            ensure_ascii=False,
        )
    )
    return 0 if result == PASS_RESULT else 1


if __name__ == "__main__":
    raise SystemExit(main())
