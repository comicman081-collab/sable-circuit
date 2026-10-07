#!/usr/bin/env python3
"""Bake ASTER's visibly articulated V6 move loop from measured UAL1 curves.

This generator deliberately has no procedural sine-wave fallback.  It requires
the Blender-exported 24-sample Jog_Fwd_Loop curve contract, then uses those
measured pelvis/spine and left/right leg trajectories to drive a smooth 2D
joint cage over each accepted ASTER direction authority.  The upper body,
hands, and rifle remain a near-rigid group; only the lower-body cage receives
independent thigh/calf/foot deformation.

V6 fixes the V5 failure mode where large numerical controls were blurred by
cross-leg Gaussian averaging until the legs looked fixed at gameplay scale.
Each lower-body pixel is now assigned to the nearest UAL leg chain before
within-leg joint blending, and gait amplitude is gated *after* atlas scaling
and the runtime 0.34 display scale.

Outputs are authored green-screen PNG frames/masks and lossless RGBA WebP
atlases.  The final runtime files contain 24 independently baked cells, not a
runtime alpha crossfade.  V5 is never overwritten and remains the immediate
previous candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
SCREEN_VECTOR = {
    "E": (1.0, 0.0),
    "SE": (math.sqrt(0.5), math.sqrt(0.5)),
    "S": (0.0, 1.0),
    "SW": (-math.sqrt(0.5), math.sqrt(0.5)),
    "W": (-1.0, 0.0),
    "NW": (-math.sqrt(0.5), -math.sqrt(0.5)),
    "N": (0.0, -1.0),
    "NE": (math.sqrt(0.5), -math.sqrt(0.5)),
}
FRAME_COUNT = 24
PLAYBACK_FPS = 24
DISPLAY_SCALE = 0.34
MIN_BOOT_TRAJECTORY_DISPLAY_PX = 12.0
MIN_KNEE_TRAJECTORY_DISPLAY_PX = 6.0
MIN_CONTACT_PASSING_DISPLAY_PX = 8.0
GREEN_U8 = np.array([0, 255, 0], dtype=np.uint8)
GREEN_F32 = GREEN_U8.astype(np.float32)
GREEN_SPILL_MARGIN = 45.0
REQUIRED_JOINTS = (
    "root",
    "pelvis",
    "spine_01",
    "spine_02",
    "spine_03",
    "neck_01",
    "Head",
    "thigh_l",
    "calf_l",
    "foot_l",
    "ball_l",
    "thigh_r",
    "calf_r",
    "foot_r",
    "ball_r",
)
UPPER_JOINTS = ("pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "Head")
LEG_JOINTS = ("thigh_l", "calf_l", "foot_l", "ball_l", "thigh_r", "calf_r", "foot_r", "ball_r")
CONTROL_RADII = {
    "thigh_l": 0.115,
    "calf_l": 0.100,
    "foot_l": 0.090,
    "ball_l": 0.075,
    "thigh_r": 0.115,
    "calf_r": 0.100,
    "foot_r": 0.090,
    "ball_r": 0.075,
}
CONTROL_GAINS = {
    "thigh_l": 0.92,
    "calf_l": 1.04,
    "foot_l": 1.12,
    "ball_l": 1.14,
    "thigh_r": 0.92,
    "calf_r": 1.04,
    "foot_r": 1.12,
    "ball_r": 1.14,
}
LEG_CHAINS = {
    "left": ("thigh_l", "calf_l", "foot_l", "ball_l"),
    "right": ("thigh_r", "calf_r", "foot_r", "ball_r"),
}
# Direction-specific 1254x1254 ASTER raster landmarks.  Left/right are
# anatomical: left owns the white/cyan leg, right owns the holster leg.
# These were audited against the accepted CONTACT_A authority at source size;
# they intentionally replace V5's generic pelvis projection.
ASTER_RASTER_LANDMARKS = {
    "E": {
        "left": ((563, 602), (660, 795), (688, 972), (768, 1102)),
        "right": ((456, 615), (378, 817), (238, 944), (183, 1062)),
    },
    "SE": {
        "left": ((553, 627), (675, 803), (733, 997), (777, 1135)),
        "right": ((459, 627), (330, 796), (249, 900), (210, 1004)),
    },
    "S": {
        "left": ((692, 660), (744, 805), (751, 914), (758, 1068)),
        "right": ((554, 659), (504, 796), (450, 920), (413, 1057)),
    },
    "SW": {
        "left": ((839, 640), (924, 803), (1038, 1005), (1043, 1164)),
        "right": ((718, 650), (579, 813), (515, 912), (449, 1017)),
    },
    "W": {
        "left": ((733, 610), (669, 822), (627, 1040), (530, 1152)),
        "right": ((823, 615), (919, 794), (1018, 935), (945, 1010)),
    },
    "NW": {
        "left": ((692, 615), (590, 790), (508, 990), (405, 1072)),
        "right": ((786, 615), (875, 790), (969, 989), (927, 1072)),
    },
    "N": {
        "left": ((557, 685), (490, 817), (447, 950), (405, 987)),
        "right": ((657, 688), (702, 846), (753, 1070), (790, 1140)),
    },
    "NE": {
        "left": ((519, 660), (407, 792), (345, 882), (324, 950)),
        "right": ((604, 655), (687, 805), (757, 1024), (837, 1081)),
    },
}
WEAPON_CALIBRATION_CELL = {
    "E": ((342.0, 126.0), (286.0, 120.0)),
    "SE": ((310.0, 184.0), (266.0, 158.0)),
    "S": ((192.0, 286.0), (192.0, 234.0)),
    "SW": ((61.0, 184.0), (112.0, 159.0)),
    "W": ((48.0, 97.0), (107.0, 97.0)),
    "NW": ((65.0, 29.0), (111.0, 49.0)),
    "N": ((192.0, 23.0), (192.0, 73.0)),
    "NE": ((311.0, 29.0), (263.0, 58.0)),
}


def project_path(path: Path, label: str) -> Path:
    value = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        value.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside the SABLE project: {value}") from exc
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite_triplet(value: Any, label: str) -> np.ndarray:
    if not isinstance(value, list) or len(value) != 3:
        raise SystemExit(f"{label} must be a three-number list")
    array = np.asarray(value, dtype=np.float64)
    if not np.all(np.isfinite(array)):
        raise SystemExit(f"{label} contains a non-finite value")
    return array


def load_ual_contract(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not path.is_file():
        raise SystemExit(
            "UAL locomotion curves are required; refusing sine/procedural fallback: " + str(path)
        )
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read UAL locomotion contract: {exc}") from exc
    locomotion = contract.get("locomotion")
    if not isinstance(locomotion, dict):
        raise SystemExit("UAL contract is missing object locomotion")
    samples = locomotion.get("samples")
    if not isinstance(samples, list) or len(samples) != FRAME_COUNT:
        raise SystemExit(f"UAL locomotion.samples must contain exactly {FRAME_COUNT} samples")
    phases: list[float] = []
    for expected_index, sample in enumerate(samples):
        if not isinstance(sample, dict) or sample.get("index") != expected_index:
            raise SystemExit(f"UAL sample index mismatch at {expected_index}")
        phase = sample.get("phase")
        if not isinstance(phase, (int, float)) or not math.isfinite(float(phase)):
            raise SystemExit(f"UAL sample {expected_index} has invalid phase")
        phases.append(float(phase))
        contacts = sample.get("contacts")
        if not isinstance(contacts, dict) or not isinstance(contacts.get("left"), bool) or not isinstance(contacts.get("right"), bool):
            raise SystemExit(f"UAL sample {expected_index} contacts.left/right must be booleans")
        if not isinstance(sample.get("events"), list):
            raise SystemExit(f"UAL sample {expected_index} events must be a list")
        if not isinstance(sample.get("root_motion"), dict):
            raise SystemExit(f"UAL sample {expected_index} root_motion must be an object")
        joints = sample.get("joints")
        if not isinstance(joints, dict):
            raise SystemExit(f"UAL sample {expected_index} joints must be an object")
        for joint_name in REQUIRED_JOINTS:
            joint = joints.get(joint_name)
            if not isinstance(joint, dict):
                raise SystemExit(f"UAL sample {expected_index} missing joint {joint_name}")
            finite_triplet(
                joint.get("position_root_space_norm_xyz"),
                f"sample {expected_index} {joint_name}.position_root_space_norm_xyz",
            )
            finite_triplet(
                joint.get("delta_from_reference_norm_xyz"),
                f"sample {expected_index} {joint_name}.delta_from_reference_norm_xyz",
            )
            screen_delta = joint.get("screen_delta_xy")
            if not isinstance(screen_delta, list) or len(screen_delta) != 2:
                raise SystemExit(f"sample {expected_index} {joint_name}.screen_delta_xy must have two numbers")
            if not np.all(np.isfinite(np.asarray(screen_delta, dtype=np.float64))):
                raise SystemExit(f"sample {expected_index} {joint_name}.screen_delta_xy contains non-finite values")
            for quaternion_key in ("local_rotation_quaternion_wxyz", "local_rotation_delta_quaternion_wxyz"):
                quaternion = joint.get(quaternion_key)
                if not isinstance(quaternion, list) or len(quaternion) != 4:
                    raise SystemExit(
                        f"sample {expected_index} {joint_name}.{quaternion_key} must have four numbers"
                    )
                if not np.all(np.isfinite(np.asarray(quaternion, dtype=np.float64))):
                    raise SystemExit(
                        f"sample {expected_index} {joint_name}.{quaternion_key} contains non-finite values"
                    )
    if any(b <= a for a, b in zip(phases, phases[1:])):
        raise SystemExit("UAL sample phases must be strictly increasing")
    if phases[0] < -1e-6 or phases[-1] >= 1.0 + 1e-6:
        raise SystemExit("UAL phases must describe one endpoint-exclusive normalized loop")
    return contract, samples


def read_authority(source: Path, mask: Path) -> tuple[np.ndarray, np.ndarray]:
    if not source.is_file():
        raise SystemExit(f"direction authority missing: {source}")
    if not mask.is_file():
        raise SystemExit(f"direction authority mask missing: {mask}")
    rgb = np.asarray(Image.open(source).convert("RGB"), dtype=np.uint8)
    alpha = np.asarray(Image.open(mask).convert("L"), dtype=np.uint8).astype(np.float32) / 255.0
    if rgb.shape[:2] != alpha.shape:
        raise SystemExit(f"authority/mask resolution mismatch: {source} / {mask}")
    visible = alpha > (16.0 / 255.0)
    if not np.any(visible):
        raise SystemExit(f"authority mask contains no visible ASTER pixels: {mask}")
    background = ~visible
    exact_green_ratio = float(np.mean(np.all(rgb[background] == GREEN_U8, axis=1))) if np.any(background) else 1.0
    if exact_green_ratio < 0.995:
        raise SystemExit(f"authority is not an exact green-screen source ({exact_green_ratio:.5f}): {source}")
    return rgb, np.clip(alpha, 0.0, 1.0)


def green_spill_mask(rgb: np.ndarray) -> np.ndarray:
    """Return pixels that belong to the keyed green matte, including its edge.

    The inclusive comparison is intentional.  A few NE authority edge pixels
    sit exactly 45 levels above both red and blue; treating those as costume
    pixels made the fixed-rifle identity QA compare a deliberately removed
    matte pixel against the source and falsely report a 255-alpha drift.
    """
    values = rgb.astype(np.float32)
    return (
        (values[:, :, 1] >= values[:, :, 0] + GREEN_SPILL_MARGIN)
        & (values[:, :, 1] >= values[:, :, 2] + GREEN_SPILL_MARGIN)
    )


def read_upper_preserve_alpha(path: Path, source_shape: tuple[int, int]) -> np.ndarray:
    if not path.is_file():
        raise SystemExit(f"upper/rifle preserve atlas missing: {path}")
    atlas = np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)
    if atlas.shape[1] != 384 or atlas.shape[0] % 384 != 0:
        raise SystemExit(f"upper/rifle preserve atlas has invalid dimensions: {path} {atlas.shape}")
    frames = atlas.reshape(atlas.shape[0] // 384, 384, 384, 4)
    union = np.max(frames[:, :, :, 3], axis=0)
    resized = np.asarray(
        Image.fromarray(union, "L").resize(
            (source_shape[1], source_shape[0]), Image.Resampling.BILINEAR
        ),
        dtype=np.float32,
    ) / 255.0
    return np.clip(resized, 0.0, 1.0)


def silhouette_geometry(alpha: np.ndarray) -> dict[str, float]:
    ys, xs = np.nonzero(alpha > (16.0 / 255.0))
    left, right = float(xs.min()), float(xs.max())
    top, bottom = float(ys.min()), float(ys.max())
    body_h = bottom - top + 1.0
    hip_y = top + body_h * 0.535
    band = (ys >= top + body_h * 0.47) & (ys <= top + body_h * 0.61)
    pelvis_x = float(np.median(xs[band])) if np.any(band) else float(np.median(xs))
    return {
        "left": left,
        "right": right,
        "top": top,
        "bottom": bottom,
        "height": body_h,
        "pelvis_x": pelvis_x,
        "pelvis_y": hip_y,
    }


def project_local(vector_xyz: np.ndarray, direction: str, body_h: float, *, anchor: bool) -> np.ndarray:
    facing = np.asarray(SCREEN_VECTOR[direction], dtype=np.float64)
    right = np.asarray((-facing[1], facing[0]), dtype=np.float64)
    lateral_scale = 0.76 if anchor else 0.70
    forward_scale = 0.34 if anchor else 0.42
    vertical_scale = 0.78 if anchor else 0.72
    return (
        right * float(vector_xyz[0]) * body_h * lateral_scale
        + facing * -float(vector_xyz[1]) * body_h * forward_scale
        + np.asarray((0.0, -float(vector_xyz[2]) * body_h * vertical_scale), dtype=np.float64)
    )


def projected_ual_anchors(
    reference_sample: dict[str, Any], direction: str, geometry: dict[str, float]
) -> dict[str, np.ndarray]:
    joints = reference_sample["joints"]
    pelvis_reference = finite_triplet(
        joints["pelvis"]["position_root_space_norm_xyz"], "reference pelvis position"
    )
    pelvis_pixel = np.asarray((geometry["pelvis_x"], geometry["pelvis_y"]), dtype=np.float64)
    margin = geometry["height"] * 0.025
    anchors: dict[str, np.ndarray] = {}
    for name in LEG_JOINTS:
        position = finite_triplet(
            joints[name]["position_root_space_norm_xyz"], f"reference {name} position"
        )
        projected = pelvis_pixel + project_local(position - pelvis_reference, direction, geometry["height"], anchor=True)
        projected[0] = np.clip(projected[0], geometry["left"] + margin, geometry["right"] - margin)
        projected[1] = np.clip(projected[1], geometry["pelvis_y"] - margin, geometry["bottom"] - margin)
        anchors[name] = projected
    return anchors


def two_means_1d(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if values.size < 64:
        raise SystemExit("not enough boot-authority pixels for two-leg landmark fitting")
    centers = np.percentile(values, (22.0, 78.0)).astype(np.float64)
    labels = np.zeros(values.shape, dtype=np.int32)
    for _ in range(40):
        labels = np.argmin(np.abs(values[:, None] - centers[None, :]), axis=1).astype(np.int32)
        updated = np.asarray(
            [float(np.mean(values[labels == index])) for index in range(2)],
            dtype=np.float64,
        )
        if not np.all(np.isfinite(updated)):
            raise SystemExit("boot landmark clustering produced an empty leg")
        if np.allclose(updated, centers, atol=1e-5):
            centers = updated
            break
        centers = updated
    order = np.argsort(centers)
    remap = np.empty(2, dtype=np.int32)
    remap[order] = np.arange(2, dtype=np.int32)
    return centers[order], remap[labels]


def control_anchors(
    rgb: np.ndarray,
    alpha: np.ndarray,
    reference_sample: dict[str, Any],
    direction: str,
    geometry: dict[str, float],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Fit UAL leg chains to ASTER's actual direction-specific raster legs.

    V5 projected generic UAL joints from the pelvis and could place a foot
    control 100+ source pixels away from the visible boot.  V6 uses audited
    anatomical-left/right hip, knee, ankle, and toe coordinates for each
    accepted ASTER direction authority.  Bright-boot clustering remains an
    independent sanity check rather than an animation driver.
    """
    projected = projected_ual_anchors(reference_sample, direction, geometry)
    grid_y = np.indices(alpha.shape)[0]
    brightness = np.mean(rgb.astype(np.float32), axis=2)
    visible = alpha > (16.0 / 255.0)
    boot_candidates = (
        visible
        & (grid_y > geometry["top"] + geometry["height"] * 0.77)
        & (brightness > 60.0)
    )
    candidate_y, candidate_x = np.nonzero(boot_candidates)
    centers, labels = two_means_1d(candidate_x.astype(np.float64))
    anchors: dict[str, np.ndarray] = {}
    fit_rows: dict[str, Any] = {}
    distance_to_visible = cv2.distanceTransform((~visible).astype(np.uint8), cv2.DIST_L2, 5)
    for side in ("left", "right"):
        suffix = side[0]
        hip, knee, ankle, toe = (
            np.asarray(point, dtype=np.float64)
            for point in ASTER_RASTER_LANDMARKS[direction][side]
        )
        anchors[f"thigh_{suffix}"] = hip
        anchors[f"calf_{suffix}"] = knee
        anchors[f"foot_{suffix}"] = ankle
        anchors[f"ball_{suffix}"] = toe
        projected_error = float(np.linalg.norm(projected[f"foot_{suffix}"] - ankle))
        cluster_index = int(np.argmin(np.abs(centers - ankle[0])))
        visibility_distances: dict[str, float] = {}
        for label, point in (("hip", hip), ("knee", knee), ("ankle", ankle), ("toe", toe)):
            px = int(np.clip(round(float(point[0])), 0, alpha.shape[1] - 1))
            py = int(np.clip(round(float(point[1])), 0, alpha.shape[0] - 1))
            distance = float(distance_to_visible[py, px])
            visibility_distances[label] = round(distance, 3)
            if distance > 24.0:
                raise SystemExit(
                    f"{direction} {side} {label} landmark is {distance:.3f}px from ASTER silhouette"
                )
        fit_rows[side] = {
            "raster_cluster_index": cluster_index,
            "raster_hip_xy": [round(float(value), 3) for value in hip],
            "raster_knee_xy": [round(float(value), 3) for value in knee],
            "raster_ankle_xy": [round(float(value), 3) for value in ankle],
            "raster_toe_xy": [round(float(value), 3) for value in toe],
            "v5_projected_ual_foot_xy": [round(float(value), 3) for value in projected[f"foot_{suffix}"]],
            "v5_projected_foot_to_raster_ankle_error_px": round(projected_error, 3),
            "candidate_pixel_count": int(np.count_nonzero(labels == cluster_index)),
            "landmark_to_visible_distance_px": visibility_distances,
        }

    ankle_separation = float(
        np.linalg.norm(anchors["foot_l"] - anchors["foot_r"])
    )
    if ankle_separation < geometry["height"] * 0.12:
        raise SystemExit(f"{direction} fitted ankles are not separable: {ankle_separation:.3f}px")
    fit = {
        "method": "audited direction-specific ASTER raster hip/knee/ankle/toe landmarks",
        "boot_cluster_centers_x": [round(float(value), 3) for value in centers],
        "ankle_separation_px": round(ankle_separation, 3),
        "sides": fit_rows,
    }
    return anchors, fit


def raw_sample_displacements(sample: dict[str, Any], direction: str, body_h: float) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    joints = sample["joints"]
    upper_candidates = []
    for name in UPPER_JOINTS:
        local_delta = finite_triplet(
            joints[name]["delta_from_reference_norm_xyz"], f"{name} delta"
        )
        upper_candidates.append(project_local(local_delta, direction, body_h, anchor=False))
    upper = np.median(np.asarray(upper_candidates), axis=0)

    controls: dict[str, np.ndarray] = {}
    for name in LEG_JOINTS:
        local_delta = finite_triplet(
            joints[name]["delta_from_reference_norm_xyz"], f"{name} delta"
        )
        controls[name] = project_local(local_delta, direction, body_h, anchor=False)
    return upper, controls


def motion_scales(samples: list[dict[str, Any]], direction: str, body_h: float) -> dict[str, float]:
    """Create one scale per trajectory, never a frame-by-frame hard clamp.

    UAL's normalized foot reach can approach a full body height.  A per-frame
    clamp creates velocity discontinuities at the cap boundary, so the whole
    measured trajectory is scaled once to the SABLE sprite amplitude budget.
    """
    raw = [raw_sample_displacements(sample, direction, body_h) for sample in samples]
    upper_peak = max(float(np.linalg.norm(item[0])) for item in raw)
    # Keep the rifle/hand/muzzle group pixel-stable.  The locomotion signal is
    # deliberately spent only below the pelvis; no full-body pumping is used
    # to fake movement.
    result = {"upper": 0.0}
    for name in LEG_JOINTS:
        peak = max(float(np.linalg.norm(item[1][name])) for item in raw)
        # V5's 5.5/7.5/9.5% budgets collapsed to only 6-9 displayed pixels
        # after 1254->384 atlas reduction and 0.34 runtime scale.  These V6
        # budgets retain the UAL curve/timing while making contact, passing,
        # and swing poses readable at the actual gameplay scale.
        limit = body_h * (
            0.105 if name.startswith("thigh")
            else 0.165 if name.startswith("calf")
            else 0.225 if name.startswith("foot")
            else 0.235
        )
        result[name] = min(1.0, limit / max(peak, 1e-9))
    return result


def sample_displacements(
    sample: dict[str, Any], direction: str, body_h: float, scales: dict[str, float]
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    upper, controls = raw_sample_displacements(sample, direction, body_h)
    upper = upper * scales["upper"]
    return upper, {name: value * scales[name] for name, value in controls.items()}


def wrap_angle_radians(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def quaternion_angle_degrees(value: Any, label: str) -> float:
    if not isinstance(value, list) or len(value) != 4:
        raise SystemExit(f"{label} must be a four-number quaternion")
    quaternion = np.asarray(value, dtype=np.float64)
    if not np.all(np.isfinite(quaternion)):
        raise SystemExit(f"{label} contains a non-finite value")
    norm = max(float(np.linalg.norm(quaternion)), 1e-9)
    w = float(np.clip(abs(quaternion[0] / norm), 0.0, 1.0))
    return math.degrees(2.0 * math.acos(w))


def retarget_chain_displacements(
    all_samples: list[dict[str, Any]],
    sample_index: int,
    sample: dict[str, Any],
    direction: str,
    body_h: float,
    anchors: dict[str, np.ndarray],
    upper_delta: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Retarget UAL contact/swing trajectories onto ASTER with two-bone IK.

    Each raster leg keeps its authored thigh/calf lengths.  UAL root-space
    forward position and foot height define the ankle target, UAL contact flags
    pin the stance foot vertically, and a two-bone IK solve produces the knee
    flex.  The UAL foot->ball angle drives boot pitch.  This makes contact and
    passing poses visible while preventing rubber limbs and body pumping.
    """
    sample_joints = sample["joints"]
    controls: dict[str, np.ndarray] = {}
    rotation_rows: dict[str, Any] = {}
    facing = np.asarray(SCREEN_VECTOR[direction], dtype=np.float64)
    screen_right = np.asarray((-facing[1], facing[0]), dtype=np.float64)
    for side, chain in LEG_CHAINS.items():
        suffix = side[0]
        contact_reference_index = 0 if side == "left" else 12
        contact_reference = all_samples[contact_reference_index]["joints"]
        foot_name = f"foot_{suffix}"
        ball_name = f"ball_{suffix}"
        forward_curve = np.asarray(
            [
                -float(entry["joints"][foot_name]["position_root_space_norm_xyz"][1])
                for entry in all_samples
            ],
            dtype=np.float64,
        )
        height_curve = np.asarray(
            [
                float(entry["joints"][foot_name]["position_root_space_norm_xyz"][2])
                for entry in all_samples
            ],
            dtype=np.float64,
        )
        forward_span = max(float(np.ptp(forward_curve)), 1e-6)
        contact_forward = float(forward_curve[contact_reference_index])
        contact_height = float(height_curve[contact_reference_index])
        lift_span = max(float(np.max(height_curve) - contact_height), 1e-6)
        forward_phase = float(forward_curve[sample_index] - contact_forward) / forward_span
        forward_offset = forward_phase * body_h * 0.185
        lift_normalized = float(np.clip(
            (height_curve[sample_index] - contact_height) / lift_span,
            0.0,
            1.0,
        ))
        if bool(sample["contacts"][side]):
            lift_normalized = 0.0
        lift_offset = lift_normalized * body_h * 0.078
        current_lateral = float(sample_joints[foot_name]["position_root_space_norm_xyz"][0])
        contact_lateral = float(contact_reference[foot_name]["position_root_space_norm_xyz"][0])
        lateral_offset = float(np.clip(
            (current_lateral - contact_lateral) * body_h * 0.42,
            -body_h * 0.025,
            body_h * 0.025,
        ))
        hip = anchors[chain[0]] + upper_delta * 0.25
        source_hip_to_ankle = anchors[foot_name] - anchors[chain[0]]
        perpendicular_to_leg = np.asarray(
            (-source_hip_to_ankle[1], source_hip_to_ankle[0]), dtype=np.float64
        )
        arc_sign = 1.0 if float(np.dot(perpendicular_to_leg, facing)) >= 0.0 else -1.0
        gait_arc = float(np.clip(
            forward_phase * math.radians(34.0) * arc_sign,
            -math.radians(34.0),
            math.radians(34.0),
        ))
        arc_cosine = math.cos(gait_arc)
        arc_sine = math.sin(gait_arc)
        lifted_length_scale = 1.0 - lift_normalized * 0.130
        arced_vector = np.asarray(
            (
                arc_cosine * float(source_hip_to_ankle[0]) - arc_sine * float(source_hip_to_ankle[1]),
                arc_sine * float(source_hip_to_ankle[0]) + arc_cosine * float(source_hip_to_ankle[1]),
            ),
            dtype=np.float64,
        ) * lifted_length_scale
        # UAL lateral motion remains as a small depth cue.  The main stride is
        # an arc around the fitted ASTER hip, so near-extended legs still move
        # visibly instead of being erased by reach clamping.
        desired_ankle = hip + arced_vector + screen_right * lateral_offset
        thigh_length = float(np.linalg.norm(anchors[chain[1]] - anchors[chain[0]]))
        calf_length = float(np.linalg.norm(anchors[chain[2]] - anchors[chain[1]]))
        target_vector = desired_ankle - hip
        target_distance = max(float(np.linalg.norm(target_vector)), 1e-6)
        min_reach = abs(thigh_length - calf_length) + body_h * 0.010
        max_reach = thigh_length + calf_length - body_h * 0.008
        solved_distance = float(np.clip(target_distance, min_reach, max_reach))
        direction_to_ankle = target_vector / target_distance
        ankle = hip + direction_to_ankle * solved_distance
        along = (
            thigh_length * thigh_length
            - calf_length * calf_length
            + solved_distance * solved_distance
        ) / (2.0 * solved_distance)
        bend_height = math.sqrt(max(thigh_length * thigh_length - along * along, 0.0))
        base = hip + direction_to_ankle * along
        perpendicular = np.asarray((-direction_to_ankle[1], direction_to_ankle[0]), dtype=np.float64)
        source_line = anchors[foot_name] - anchors[chain[0]]
        source_knee = anchors[chain[1]] - anchors[chain[0]]
        source_cross = float(source_line[0] * source_knee[1] - source_line[1] * source_knee[0])
        bend_sign = 1.0 if source_cross >= 0.0 else -1.0
        knee = base + perpendicular * bend_height * bend_sign

        source_boot_vector = anchors[ball_name] - anchors[foot_name]
        contact_foot = finite_triplet(
            contact_reference[foot_name]["position_root_space_norm_xyz"],
            f"contact {foot_name} position",
        )
        contact_ball = finite_triplet(
            contact_reference[ball_name]["position_root_space_norm_xyz"],
            f"contact {ball_name} position",
        )
        sample_foot = finite_triplet(
            sample_joints[foot_name]["position_root_space_norm_xyz"],
            f"sample {foot_name} position",
        )
        sample_ball = finite_triplet(
            sample_joints[ball_name]["position_root_space_norm_xyz"],
            f"sample {ball_name} position",
        )
        contact_boot_2d = project_local(contact_ball - contact_foot, direction, body_h, anchor=True)
        sample_boot_2d = project_local(sample_ball - sample_foot, direction, body_h, anchor=True)
        boot_angle = float(np.clip(
            wrap_angle_radians(
                math.atan2(float(sample_boot_2d[1]), float(sample_boot_2d[0]))
                - math.atan2(float(contact_boot_2d[1]), float(contact_boot_2d[0]))
            ),
            -math.radians(18.0),
            math.radians(18.0),
        ))
        cosine = math.cos(boot_angle)
        sine = math.sin(boot_angle)
        rotated_boot = np.asarray(
            (
                cosine * float(source_boot_vector[0]) - sine * float(source_boot_vector[1]),
                sine * float(source_boot_vector[0]) + cosine * float(source_boot_vector[1]),
            ),
            dtype=np.float64,
        )
        toe = ankle + rotated_boot
        targets = {chain[0]: hip, chain[1]: knee, chain[2]: ankle, chain[3]: toe}
        for name in chain:
            controls[name] = targets[name] - anchors[name]

        source_thigh_angle = math.atan2(
            float(anchors[chain[1]][1] - anchors[chain[0]][1]),
            float(anchors[chain[1]][0] - anchors[chain[0]][0]),
        )
        target_thigh_angle = math.atan2(float(knee[1] - hip[1]), float(knee[0] - hip[0]))
        source_calf_angle = math.atan2(
            float(anchors[chain[2]][1] - anchors[chain[1]][1]),
            float(anchors[chain[2]][0] - anchors[chain[1]][0]),
        )
        target_calf_angle = math.atan2(float(ankle[1] - knee[1]), float(ankle[0] - knee[0]))
        rotation_rows[side] = {
            "contact_reference_frame": contact_reference_index,
            "contact": bool(sample["contacts"][side]),
            "forward_offset_px": round(forward_offset, 4),
            "lift_offset_px": round(lift_offset, 4),
            "gait_arc_deg": round(math.degrees(gait_arc), 4),
            "desired_ankle_clamped_px": round(float(np.linalg.norm(desired_ankle - ankle)), 4),
            "thigh_rotation_deg": round(math.degrees(wrap_angle_radians(target_thigh_angle - source_thigh_angle)), 4),
            "calf_rotation_deg": round(math.degrees(wrap_angle_radians(target_calf_angle - source_calf_angle)), 4),
            "boot_rotation_deg": round(math.degrees(boot_angle), 4),
            "ual_local_rotation_delta_deg": {
                name: round(quaternion_angle_degrees(
                    sample_joints[name]["local_rotation_delta_quaternion_wxyz"],
                    f"sample {name} local rotation delta",
                ), 4)
                for name in chain[:3]
            },
        }
    return controls, rotation_rows


def smoothstep(edge0: float, edge1: float, values: np.ndarray) -> np.ndarray:
    scaled = np.clip((values - edge0) / max(edge1 - edge0, 1e-6), 0.0, 1.0)
    return scaled * scaled * (3.0 - 2.0 * scaled)


def segment_distance_sq(
    grid_x: np.ndarray, grid_y: np.ndarray, start: np.ndarray, end: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    vector = end - start
    length_sq = max(float(np.dot(vector, vector)), 1e-6)
    along = np.clip(
        ((grid_x - float(start[0])) * float(vector[0]) + (grid_y - float(start[1])) * float(vector[1]))
        / length_sq,
        0.0,
        1.0,
    ).astype(np.float32)
    closest_x = float(start[0]) + along * float(vector[0])
    closest_y = float(start[1]) + along * float(vector[1])
    return (grid_x - closest_x) ** 2 + (grid_y - closest_y) ** 2, along


def similarity_displacement(
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    source_start: np.ndarray,
    source_end: np.ndarray,
    target_start: np.ndarray,
    target_end: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return a length-preserving-enough 2D bone transform displacement.

    Positions extracted from UAL already contain the integrated joint
    rotations.  Mapping each source bone to its target segment therefore
    produces visible thigh/knee/ankle rotation without needing a 3D preview
    mesh in the final sprite.  Scale is bounded to prevent rubber limbs.
    """
    source_vector = source_end - source_start
    target_vector = target_end - target_start
    source_length = max(float(np.linalg.norm(source_vector)), 1e-6)
    target_length = max(float(np.linalg.norm(target_vector)), 1e-6)
    source_angle = math.atan2(float(source_vector[1]), float(source_vector[0]))
    target_angle = math.atan2(float(target_vector[1]), float(target_vector[0]))
    angle = target_angle - source_angle
    cosine = math.cos(angle)
    sine = math.sin(angle)
    scale = float(np.clip(target_length / source_length, 0.82, 1.18))
    local_x = grid_x - float(source_start[0])
    local_y = grid_y - float(source_start[1])
    transformed_x = float(target_start[0]) + scale * (cosine * local_x - sine * local_y)
    transformed_y = float(target_start[1]) + scale * (sine * local_x + cosine * local_y)
    return transformed_x - grid_x, transformed_y - grid_y


def weapon_preserve_weights(
    alpha: np.ndarray,
    upper_preserve_alpha: np.ndarray,
    direction: str,
) -> tuple[np.ndarray, np.ndarray]:
    height, width = alpha.shape
    grid_y, grid_x = np.mgrid[0:height, 0:width].astype(np.float32)
    source_scale = float(width) / 384.0
    muzzle_cell, inner_cell = WEAPON_CALIBRATION_CELL[direction]
    muzzle = np.asarray(muzzle_cell, dtype=np.float64) * source_scale
    inner = np.asarray(inner_cell, dtype=np.float64) * source_scale
    axis = muzzle - inner
    axis /= max(float(np.linalg.norm(axis)), 1e-6)
    start = muzzle - axis * 250.0 * source_scale
    end = muzzle + axis * 12.0 * source_scale
    distance_sq, _ = segment_distance_sq(grid_x, grid_y, start, end)
    distance = np.sqrt(distance_sq)
    visible = alpha > (16.0 / 255.0)
    corridor = 1.0 - smoothstep(20.0 * source_scale, 28.0 * source_scale, distance)
    # Reuse the existing reviewed Fire-upper split only as a mask authority.
    # It contains hands/rifle/muzzle but no legs, so the downward S rifle can
    # cross the animated lower body without freezing unrelated thigh pixels.
    preserve = np.clip(upper_preserve_alpha * corridor, 0.0, 1.0).astype(np.float32)
    core = visible & (upper_preserve_alpha >= (254.0 / 255.0)) & (corridor >= 0.72)
    if int(np.count_nonzero(core)) < 128:
        raise RuntimeError(f"{direction} weapon upper-mask preserve core is too small")
    preserve[core] = 1.0
    return preserve.astype(np.float32), core


def deformation_maps(
    alpha: np.ndarray,
    upper_preserve_alpha: np.ndarray,
    direction: str,
    geometry: dict[str, float],
    anchors: dict[str, np.ndarray],
    upper_delta: np.ndarray,
    control_deltas: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    height, width = alpha.shape
    grid_y, grid_x = np.mgrid[0:height, 0:width].astype(np.float32)
    body_h = geometry["height"]

    # Everything starts with one tiny rigid upper-body displacement.  Hands,
    # rifle, head, and hair never receive an independent warp.
    upper_x = np.full((height, width), float(upper_delta[0]), dtype=np.float32)
    upper_y = np.full((height, width), float(upper_delta[1]), dtype=np.float32)
    lower_activation = smoothstep(
        geometry["pelvis_y"] - body_h * 0.010,
        geometry["pelvis_y"] + body_h * 0.090,
        grid_y,
    ).astype(np.float32)

    leg_fields: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    leg_distance_sq: dict[str, np.ndarray] = {}
    for side, chain in LEG_CHAINS.items():
        weighted_x = np.zeros((height, width), dtype=np.float32)
        weighted_y = np.zeros((height, width), dtype=np.float32)
        weight_sum = np.zeros((height, width), dtype=np.float32)
        minimum_distance = np.full((height, width), np.inf, dtype=np.float32)
        for bone_index, (start_name, end_name) in enumerate(zip(chain, chain[1:])):
            source_start = anchors[start_name]
            source_end = anchors[end_name]
            target_start = source_start + control_deltas[start_name]
            target_end = source_end + control_deltas[end_name]
            distance_sq, along = segment_distance_sq(grid_x, grid_y, source_start, source_end)
            minimum_distance = np.minimum(minimum_distance, distance_sq)
            # Segment-local influence plus a smooth hand-off at knee/ankle.
            radius = body_h * (0.115 if bone_index == 0 else 0.100 if bone_index == 1 else 0.085)
            weight = np.exp(-distance_sq / max(2.0 * radius * radius, 1.0)).astype(np.float32)
            end_softness = 0.72 + 0.28 * np.sin(np.pi * along).astype(np.float32)
            weight *= end_softness
            delta_x, delta_y = similarity_displacement(
                grid_x,
                grid_y,
                source_start,
                source_end,
                target_start,
                target_end,
            )
            weighted_x += weight * delta_x
            weighted_y += weight * delta_y
            weight_sum += weight
        leg_fields[side] = (
            weighted_x / np.maximum(weight_sum, 1e-6),
            weighted_y / np.maximum(weight_sum, 1e-6),
            weight_sum,
        )
        leg_distance_sq[side] = minimum_distance

    # Assign pixels to a leg chain before blending bones.  This is the core V6
    # fix: V5 mixed left/right controls in one denominator, cancelling the
    # alternating gait exactly where both legs overlap in a 2.5D view.
    ownership_sigma = max(body_h * 0.085, 1.0)
    left_affinity = np.exp(-leg_distance_sq["left"] / (2.0 * ownership_sigma * ownership_sigma)).astype(np.float32)
    right_affinity = np.exp(-leg_distance_sq["right"] / (2.0 * ownership_sigma * ownership_sigma)).astype(np.float32)
    affinity_sum = np.maximum(left_affinity + right_affinity, 1e-6)
    left_ownership = left_affinity / affinity_sum
    right_ownership = right_affinity / affinity_sum
    leg_x = left_ownership * leg_fields["left"][0] + right_ownership * leg_fields["right"][0]
    leg_y = left_ownership * leg_fields["left"][1] + right_ownership * leg_fields["right"][1]

    nearest_distance = np.minimum(leg_distance_sq["left"], leg_distance_sq["right"])
    support_radius = max(body_h * 0.145, 1.0)
    leg_support = np.exp(-nearest_distance / (2.0 * support_radius * support_radius)).astype(np.float32)
    leg_support = np.clip(leg_support * lower_activation, 0.0, 1.0)
    weapon_preserve, weapon_core = weapon_preserve_weights(alpha, upper_preserve_alpha, direction)
    displacement_x = upper_x * (1.0 - leg_support) + leg_x * leg_support
    displacement_y = upper_y * (1.0 - leg_support) + leg_y * leg_support

    map_x = (grid_x - displacement_x).astype(np.float32)
    map_y = (grid_y - displacement_y).astype(np.float32)
    diagnostics = {
        "displacement_x": displacement_x,
        "displacement_y": displacement_y,
        "left_ownership": left_ownership,
        "right_ownership": right_ownership,
        "left_distance_sq": leg_distance_sq["left"],
        "right_distance_sq": leg_distance_sq["right"],
        "weapon_preserve": weapon_preserve,
        "weapon_core": weapon_core,
    }
    return map_x, map_y, diagnostics


def deform_frame(
    rgb: np.ndarray,
    alpha: np.ndarray,
    upper_preserve_alpha: np.ndarray,
    direction: str,
    geometry: dict[str, float],
    anchors: dict[str, np.ndarray],
    upper_delta: np.ndarray,
    control_deltas: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    map_x, map_y, diagnostics = deformation_maps(
        alpha,
        upper_preserve_alpha,
        direction,
        geometry,
        anchors,
        upper_delta,
        control_deltas,
    )
    source_pm = rgb.astype(np.float32) * alpha[:, :, None]
    # True complementary layer split: the reviewed upper mask owns head,
    # torso, hands, and rifle/muzzle at the original pixels.  Only its exact
    # complement is warped as lower body, then the fixed upper is composited on
    # top.  This prevents both rifle bending and a deformed duplicate peeking
    # around the S muzzle cage.
    upper_weight = np.clip(upper_preserve_alpha, 0.0, 1.0).astype(np.float32)
    upper_alpha = alpha * upper_weight
    upper_pm = source_pm * upper_weight[:, :, None]
    lower_alpha = alpha * (1.0 - upper_weight)
    lower_pm = source_pm * (1.0 - upper_weight[:, :, None])
    # Before deformation the split must be a lossless partition of the source.
    # This is checked on every direction/frame so a preserve-mask change cannot
    # silently punch a hole in the costume or duplicate the rifle layer.
    partition_pm_error = float(np.max(np.abs((upper_pm + lower_pm) - source_pm)))
    partition_alpha_error = float(np.max(np.abs((upper_alpha + lower_alpha) - alpha)))
    if partition_pm_error > 1e-4 or partition_alpha_error > 1e-6:
        raise RuntimeError(
            f"{direction} complementary RGBA split is not lossless: "
            f"pm={partition_pm_error:.8f} alpha={partition_alpha_error:.8f}"
        )
    warped_lower_pm = cv2.remap(
        lower_pm,
        map_x,
        map_y,
        cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    warped_lower_alpha = cv2.remap(
        lower_alpha,
        map_x,
        map_y,
        cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    warped_lower_alpha = np.clip(warped_lower_alpha, 0.0, 1.0)
    warped_pm = upper_pm + warped_lower_pm * (1.0 - upper_alpha[:, :, None])
    warped_alpha = upper_alpha + warped_lower_alpha * (1.0 - upper_alpha)
    warped_alpha = np.clip(warped_alpha, 0.0, 1.0)
    straight = np.zeros_like(warped_pm)
    np.divide(
        warped_pm,
        np.maximum(warped_alpha[:, :, None], 1.0 / 255.0),
        out=straight,
        where=warped_alpha[:, :, None] > 0,
    )
    straight = np.clip(straight, 0.0, 255.0)
    chroma_residual = green_spill_mask(straight)
    warped_alpha[chroma_residual] = 0.0
    straight[chroma_residual] = 0.0
    # Quantization can move a boundary pixel exactly onto the inclusive matte
    # threshold, so key once more in the same uint8 domain used by QA/export.
    foreground_u8 = np.rint(straight).astype(np.uint8)
    quantized_chroma_residual = green_spill_mask(foreground_u8)
    warped_alpha[quantized_chroma_residual] = 0.0
    foreground_u8[quantized_chroma_residual] = 0
    straight = foreground_u8.astype(np.float32)
    green = straight * warped_alpha[:, :, None] + GREEN_F32[None, None, :] * (1.0 - warped_alpha[:, :, None])
    green[warped_alpha < (1.0 / 255.0)] = GREEN_F32
    diagnostics["partition_pm_error"] = np.asarray(partition_pm_error, dtype=np.float32)
    diagnostics["partition_alpha_error"] = np.asarray(partition_alpha_error, dtype=np.float32)
    return (
        np.rint(green).astype(np.uint8),
        np.rint(warped_alpha * 255.0).astype(np.uint8),
        foreground_u8,
        map_x,
        map_y,
        diagnostics,
    )


def tile_rgba(rgb: np.ndarray, alpha_u8: np.ndarray, size: int) -> Image.Image:
    alpha = alpha_u8.astype(np.float32) / 255.0
    premultiplied = np.rint(rgb.astype(np.float32) * alpha[:, :, None]).astype(np.uint8)
    pm_small = np.asarray(
        Image.fromarray(premultiplied, "RGB").resize((size, size), Image.Resampling.LANCZOS),
        dtype=np.float32,
    )
    alpha_small = np.asarray(
        Image.fromarray(alpha_u8, "L").resize((size, size), Image.Resampling.LANCZOS),
        dtype=np.float32,
    ) / 255.0
    straight = np.zeros_like(pm_small, dtype=np.float32)
    np.divide(
        pm_small,
        np.maximum(alpha_small[:, :, None], 1.0 / 255.0),
        out=straight,
        where=alpha_small[:, :, None] > 0,
    )
    straight[alpha_small < (1.0 / 255.0)] = 0
    rgba = np.dstack((np.rint(np.clip(straight, 0.0, 255.0)).astype(np.uint8), np.rint(alpha_small * 255.0).astype(np.uint8)))
    return Image.fromarray(rgba, "RGBA")


def decoded_frame_metrics(frames: list[np.ndarray]) -> dict[str, Any]:
    hashes = [hashlib.sha256(frame.tobytes()).hexdigest() for frame in frames]
    adjacent = [
        float(np.mean(np.abs(frames[index].astype(np.int16) - frames[(index + 1) % len(frames)].astype(np.int16))))
        for index in range(len(frames))
    ]
    regular = adjacent[:-1]
    median_regular = float(np.median(regular))
    seam = adjacent[-1]
    return {
        "unique_decoded_frames": len(set(hashes)),
        "mean_adjacent_rgba_delta": round(float(np.mean(adjacent)), 6),
        "median_non_seam_rgba_delta": round(median_regular, 6),
        "loop_seam_rgba_delta": round(seam, 6),
        "loop_seam_to_median_ratio": round(seam / max(median_regular, 1e-6), 6),
    }


def maximum_pairwise_distance(points: np.ndarray) -> float:
    return max(
        float(np.linalg.norm(points[first] - points[second]))
        for first in range(len(points))
        for second in range(first + 1, len(points))
    )


def gait_display_metrics(
    frame_rows: list[dict[str, Any]],
    anchors: dict[str, np.ndarray],
    source_width: int,
    tile_size: int,
) -> dict[str, Any]:
    display_factor = float(tile_size) / float(source_width) * DISPLAY_SCALE
    result: dict[str, Any] = {
        "runtime_display_scale": DISPLAY_SCALE,
        "source_to_runtime_display_factor": round(display_factor, 8),
        "legs": {},
    }
    for side in ("left", "right"):
        suffix = side[0]
        boot_name = f"foot_{suffix}"
        knee_name = f"calf_{suffix}"
        boot = np.asarray(
            [anchors[boot_name] + np.asarray(row["lower_cage_delta_px"][boot_name], dtype=np.float64) for row in frame_rows]
        )
        knee = np.asarray(
            [anchors[knee_name] + np.asarray(row["lower_cage_delta_px"][knee_name], dtype=np.float64) for row in frame_rows]
        )
        adjacent = np.linalg.norm(np.diff(np.concatenate((boot, boot[:1]), axis=0), axis=0), axis=1) * display_factor
        contact_reference = 0 if side == "left" else 12
        passing_index = (contact_reference + 6) % FRAME_COUNT
        evidence = [row["ual_rotation_retarget"][side] for row in frame_rows]
        boot_pitch = [float(row["boot_rotation_deg"]) for row in evidence]
        calf_rotation = [float(row["calf_rotation_deg"]) for row in evidence]
        contact_lift = [
            float(entry["lift_offset_px"])
            for entry in evidence
            if bool(entry["contact"])
        ]
        leg_metrics = {
            "boot_trajectory_p2p_display_px": round(maximum_pairwise_distance(boot) * display_factor, 4),
            "knee_trajectory_p2p_display_px": round(maximum_pairwise_distance(knee) * display_factor, 4),
            "contact_to_passing_display_px": round(
                float(np.linalg.norm(boot[contact_reference] - boot[passing_index])) * display_factor,
                4,
            ),
            "median_adjacent_boot_motion_display_px": round(float(np.median(adjacent)), 4),
            "max_adjacent_boot_motion_display_px": round(float(np.max(adjacent)), 4),
            "loop_seam_boot_motion_display_px": round(float(adjacent[-1]), 4),
            "toe_clearance_display_px": round(
                max(float(entry["lift_offset_px"]) for entry in evidence) * display_factor,
                4,
            ),
            "max_contact_lift_display_px": round(max(contact_lift, default=0.0) * display_factor, 4),
            "boot_pitch_range_deg": round(max(boot_pitch) - min(boot_pitch), 4),
            "calf_rotation_range_deg": round(max(calf_rotation) - min(calf_rotation), 4),
        }
        if leg_metrics["boot_trajectory_p2p_display_px"] < MIN_BOOT_TRAJECTORY_DISPLAY_PX:
            raise RuntimeError(f"{side} boot trajectory is visually frozen: {leg_metrics}")
        if leg_metrics["knee_trajectory_p2p_display_px"] < MIN_KNEE_TRAJECTORY_DISPLAY_PX:
            raise RuntimeError(f"{side} knee trajectory is visually frozen: {leg_metrics}")
        if leg_metrics["contact_to_passing_display_px"] < MIN_CONTACT_PASSING_DISPLAY_PX:
            raise RuntimeError(f"{side} contact/passing poses are not separable: {leg_metrics}")
        if leg_metrics["median_adjacent_boot_motion_display_px"] < 0.8:
            raise RuntimeError(f"{side} boot motion is sub-pixel at runtime: {leg_metrics}")
        if leg_metrics["toe_clearance_display_px"] < 5.0:
            raise RuntimeError(f"{side} swing toe clearance is not visible: {leg_metrics}")
        if leg_metrics["max_contact_lift_display_px"] > 0.05:
            raise RuntimeError(f"{side} planted contact was lifted: {leg_metrics}")
        if leg_metrics["loop_seam_boot_motion_display_px"] > 4.0:
            raise RuntimeError(f"{side} boot loop seam pops: {leg_metrics}")
        result["legs"][side] = leg_metrics

    inter_foot = []
    upper = []
    for row in frame_rows:
        left = anchors["foot_l"] + np.asarray(row["lower_cage_delta_px"]["foot_l"], dtype=np.float64)
        right = anchors["foot_r"] + np.asarray(row["lower_cage_delta_px"]["foot_r"], dtype=np.float64)
        inter_foot.append(float(np.linalg.norm(left - right)) * display_factor)
        upper.append(np.asarray(row["upper_rigid_delta_px"], dtype=np.float64))
    upper_points = np.asarray(upper)
    result["max_inter_foot_separation_display_px"] = round(max(inter_foot), 4)
    result["min_inter_foot_separation_display_px"] = round(min(inter_foot), 4)
    result["upper_rigid_bob_p2p_display_px"] = round(
        maximum_pairwise_distance(upper_points) * display_factor,
        4,
    )
    if result["max_inter_foot_separation_display_px"] < 10.0:
        raise RuntimeError(f"inter-foot stride is not readable: {result}")
    if result["upper_rigid_bob_p2p_display_px"] > 2.6:
        raise RuntimeError(f"upper body pumping exceeds V6 budget: {result}")
    result["gate"] = "PASS"
    return result


def atomic_promote(staging: Path, destination: Path) -> None:
    if destination.exists():
        raise SystemExit(f"refusing to overwrite existing V5 output: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staging, destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--curves",
        type=Path,
        default=Path("art_src/pilot_v2/aster_v2/animation_360/ual_locomotion_v5/ASTER_UAL1_LOCOMOTION_CURVES_V5.json"),
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path("art_src/pilot_v2/aster_v2/animation_360/imagegen_idle_move_360_mvp_v1/source/move"),
    )
    parser.add_argument(
        "--mask-root",
        type=Path,
        default=Path("art_src/pilot_v2/aster_v2/animation_360/imagegen_idle_move_360_mvp_v1/masks/move"),
    )
    parser.add_argument(
        "--upper-preserve-root",
        type=Path,
        default=Path("assets/units/operators/aster/composite_fire_v5/fire_upper"),
    )
    parser.add_argument(
        "--authoring-output",
        type=Path,
        default=Path("art_src/pilot_v2/aster_v2/animation_360/move_360_ual_v6"),
    )
    parser.add_argument(
        "--runtime-output",
        type=Path,
        default=Path("assets/units/operators/aster/move_360_ual_v6"),
    )
    parser.add_argument("--tile", type=int, default=384)
    args = parser.parse_args()
    if args.tile < 128 or args.tile > 1024:
        raise SystemExit("tile must be between 128 and 1024")

    curves_path = project_path(args.curves, "UAL curves")
    source_root = project_path(args.source_root, "source root")
    mask_root = project_path(args.mask_root, "mask root")
    upper_preserve_root = project_path(args.upper_preserve_root, "upper preserve root")
    authoring = project_path(args.authoring_output, "authoring output")
    runtime = project_path(args.runtime_output, "runtime output")
    if authoring.exists() or runtime.exists():
        raise SystemExit("refusing to overwrite V6; V5 must remain the immediate previous candidate")
    contract, samples = load_ual_contract(curves_path)

    authoring.parent.mkdir(parents=True, exist_ok=True)
    runtime.parent.mkdir(parents=True, exist_ok=True)
    authoring_stage = Path(tempfile.mkdtemp(prefix="move_360_ual_v6_authoring_", dir=authoring.parent))
    runtime_stage = Path(tempfile.mkdtemp(prefix="move_360_ual_v6_runtime_", dir=runtime.parent))
    promoted_authoring = False
    promoted_runtime = False
    try:
        direction_records: list[dict[str, Any]] = []
        preview_tiles: list[tuple[str, int, Image.Image]] = []
        for direction in DIRECTIONS:
            authority = source_root / direction / f"ASTER_MOVE_{direction}_CONTACT_A_GREEN.png"
            authority_mask = mask_root / direction / f"ASTER_MOVE_{direction}_CONTACT_A_MASK.png"
            rgb, alpha = read_authority(authority, authority_mask)
            upper_preserve_path = (
                upper_preserve_root
                / direction
                / f"ASTER_FIRE_{direction}_UPPER_V5_ATLAS.webp"
            )
            upper_preserve_alpha = read_upper_preserve_alpha(upper_preserve_path, alpha.shape)
            geometry = silhouette_geometry(alpha)
            anchors, landmark_fit = control_anchors(rgb, alpha, samples[0], direction, geometry)
            scales = motion_scales(samples, direction, geometry["height"])
            source_dir = authoring_stage / direction / "source"
            masks_dir = authoring_stage / direction / "masks"
            runtime_dir = runtime_stage / direction
            source_dir.mkdir(parents=True)
            masks_dir.mkdir(parents=True)
            runtime_dir.mkdir(parents=True)
            atlas = Image.new("RGBA", (args.tile, args.tile * FRAME_COUNT), (0, 0, 0, 0))
            frame_rows: list[dict[str, Any]] = []
            source_hashes: list[str] = []
            mask_areas: list[int] = []
            atlas_frames: list[np.ndarray] = []
            weapon_core_rgb_deltas: list[int] = []
            weapon_core_alpha_deltas: list[int] = []
            visible_green_residual_counts: list[int] = []
            partition_pm_errors: list[float] = []
            partition_alpha_errors: list[float] = []

            for index, sample in enumerate(samples):
                raw_upper_delta, _ = raw_sample_displacements(sample, direction, geometry["height"])
                upper_delta = raw_upper_delta * scales["upper"]
                controls, rotation_evidence = retarget_chain_displacements(
                    samples,
                    index,
                    sample,
                    direction,
                    geometry["height"],
                    anchors,
                    upper_delta,
                )
                frame_rgb, frame_alpha, foreground_rgb, map_x, map_y, deformation_diagnostics = deform_frame(
                    rgb,
                    alpha,
                    upper_preserve_alpha,
                    direction,
                    geometry,
                    anchors,
                    upper_delta,
                    controls,
                )
                source_chroma = green_spill_mask(rgb)
                weapon_core = (
                    deformation_diagnostics["weapon_core"]
                    & (alpha > (16.0 / 255.0))
                    & ~source_chroma
                )
                if int(np.count_nonzero(weapon_core)) < 128:
                    raise RuntimeError(f"{direction} weapon preserve core did not cover enough visible pixels")
                rgb_delta = np.abs(foreground_rgb.astype(np.int16) - rgb.astype(np.int16))
                alpha_delta = np.abs(
                    frame_alpha.astype(np.int16)
                    - np.rint(alpha * 255.0).astype(np.int16)
                )
                weapon_core_rgb_deltas.append(int(np.max(rgb_delta[weapon_core])))
                weapon_core_alpha_deltas.append(int(np.max(alpha_delta[weapon_core])))
                partition_pm_errors.append(float(deformation_diagnostics["partition_pm_error"]))
                partition_alpha_errors.append(float(deformation_diagnostics["partition_alpha_error"]))
                output_visible = frame_alpha > 16
                output_green = green_spill_mask(foreground_rgb)
                visible_green_residual_counts.append(int(np.count_nonzero(output_visible & output_green)))
                if visible_green_residual_counts[-1] != 0:
                    raise RuntimeError(
                        f"{direction} frame {index} contains {visible_green_residual_counts[-1]} green spill pixels"
                    )
                frame_path = source_dir / f"ASTER_MOVE_{direction}_UAL_V6_F{index:02d}_GREEN.png"
                mask_path = masks_dir / f"ASTER_MOVE_{direction}_UAL_V6_F{index:02d}_MASK.png"
                Image.fromarray(frame_rgb, "RGB").save(frame_path, optimize=True)
                Image.fromarray(frame_alpha, "L").save(mask_path, optimize=True)
                tile = tile_rgba(foreground_rgb, frame_alpha, args.tile)
                atlas.alpha_composite(tile, (0, index * args.tile))
                decoded = np.asarray(tile, dtype=np.uint8)
                atlas_frames.append(decoded)
                source_hashes.append(sha256(frame_path))
                mask_areas.append(int(np.count_nonzero(frame_alpha > 16)))
                if index in (0, 4, 8, 12, 16, 20):
                    preview_tiles.append((direction, index, tile.resize((384, 384), Image.Resampling.LANCZOS)))
                frame_rows.append({
                    "index": index,
                    "phase": round(float(sample["phase"]), 8),
                    "contacts": sample["contacts"],
                    "events": sample["events"],
                    "source": (authoring / direction / "source" / frame_path.name).relative_to(ROOT).as_posix(),
                    "mask": (authoring / direction / "masks" / mask_path.name).relative_to(ROOT).as_posix(),
                    "source_sha256": source_hashes[-1],
                    "upper_rigid_delta_px": [round(float(value), 5) for value in upper_delta],
                    "lower_cage_delta_px": {
                        name: [round(float(value), 5) for value in controls[name]] for name in LEG_JOINTS
                    },
                    "ual_rotation_retarget": rotation_evidence,
                    "weapon_core_max_rgb_delta": weapon_core_rgb_deltas[-1],
                    "weapon_core_max_alpha_delta": weapon_core_alpha_deltas[-1],
                    "visible_green_residual_pixels": visible_green_residual_counts[-1],
                    "complementary_partition_pm_error": partition_pm_errors[-1],
                    "complementary_partition_alpha_error": partition_alpha_errors[-1],
                })

            if len(set(source_hashes)) != FRAME_COUNT:
                raise RuntimeError(f"{direction} did not produce {FRAME_COUNT} distinct authored frames")
            area_delta = (max(mask_areas) - min(mask_areas)) / max(float(np.mean(mask_areas)), 1.0)
            if area_delta > 0.14:
                raise RuntimeError(f"{direction} silhouette area drift exceeds 14%: {area_delta:.6f}")
            gait_metrics = gait_display_metrics(frame_rows, anchors, rgb.shape[1], args.tile)
            if max(weapon_core_rgb_deltas) > 1 or max(weapon_core_alpha_deltas) > 1:
                raise RuntimeError(
                    f"{direction} rifle/muzzle preserve core drifted: "
                    f"rgb={max(weapon_core_rgb_deltas)} alpha={max(weapon_core_alpha_deltas)}"
                )
            metrics = decoded_frame_metrics(atlas_frames)
            if metrics["unique_decoded_frames"] != FRAME_COUNT:
                raise RuntimeError(f"{direction} atlas has duplicate decoded cells")
            if metrics["loop_seam_to_median_ratio"] > 2.75:
                raise RuntimeError(
                    f"{direction} loop seam is discontinuous: {metrics['loop_seam_to_median_ratio']:.4f}x median"
                )

            atlas_path_stage = runtime_dir / f"ASTER_MOVE_{direction}_360_UAL_V6_ATLAS.webp"
            atlas.save(atlas_path_stage, "WEBP", lossless=True, method=6, exact=True)
            decoded_atlas = np.asarray(Image.open(atlas_path_stage).convert("RGBA"), dtype=np.uint8)
            expected_atlas = np.asarray(atlas, dtype=np.uint8)
            if decoded_atlas.shape != (args.tile * FRAME_COUNT, args.tile, 4):
                raise RuntimeError(f"{direction} atlas resolution mismatch: {decoded_atlas.shape}")
            if not np.array_equal(decoded_atlas, expected_atlas):
                raise RuntimeError(f"{direction} lossless WebP round-trip changed RGBA pixels")

            atlas_path = runtime / direction / atlas_path_stage.name
            manifest = {
                "schema": 1,
                "role": f"ASTER {direction} UAL1-measured 24-frame articulated locomotion atlas V6",
                "direction": direction,
                "direction_authority": authority.relative_to(ROOT).as_posix(),
                "direction_authority_sha256": sha256(authority),
                "direction_authority_mask": authority_mask.relative_to(ROOT).as_posix(),
                "direction_authority_mask_sha256": sha256(authority_mask),
                "upper_rifle_preserve_mask_authority": upper_preserve_path.relative_to(ROOT).as_posix(),
                "upper_rifle_preserve_mask_authority_sha256": sha256(upper_preserve_path),
                "ual_curve_contract": curves_path.relative_to(ROOT).as_posix(),
                "ual_curve_contract_sha256": sha256(curves_path),
                "ual_motion_authority": "UAL1 Standard / Jog_Fwd_Loop",
                "deformation": {
                    "method": "direction-specific ASTER raster landmarks plus UAL bone-chain similarity transforms",
                    "upper_body": "pixel-rigid; no locomotion bob; hands/rifle/muzzle corridor explicitly excluded from leg deformation",
                    "lower_body": "left/right thigh-knee-ankle-toe chains are isolated before segment rotation/translation blending",
                    "runtime_crossfade_baked": False,
                    "procedural_sine_fallback": False,
                    "trajectory_scale_factors": {name: round(float(value), 8) for name, value in scales.items()},
                    "raster_landmark_fit": landmark_fit,
                },
                "frame_size": [args.tile, args.tile],
                "frame_count": FRAME_COUNT,
                "playback_fps": PLAYBACK_FPS,
                "atlas_resolution": [args.tile, args.tile * FRAME_COUNT],
                "atlas_layout": "vertical",
                "frames": frame_rows,
                "qa": {
                    **metrics,
                    "gait_display_metrics": gait_metrics,
                    "weapon_core_max_rgb_delta": max(weapon_core_rgb_deltas),
                    "weapon_core_max_alpha_delta": max(weapon_core_alpha_deltas),
                    "weapon_corridor_pixel_stable": True,
                    "visible_green_residual_pixels": max(visible_green_residual_counts),
                    "complementary_partition_pm_error": max(partition_pm_errors),
                    "complementary_partition_alpha_error": max(partition_alpha_errors),
                    "complementary_partition_lossless": True,
                    "silhouette_area_delta_ratio": round(float(area_delta), 6),
                    "lossless_webp_roundtrip": True,
                    "exact_green_authoring_background": True,
                },
                "atlas": atlas_path.relative_to(ROOT).as_posix(),
                "atlas_sha256": sha256(atlas_path_stage),
                "cloud_calls": 0,
                "krea2_calls": 0,
                "base_character_visual_used": False,
                "visual_gate": "USER_REVIEW_REQUIRED",
            }
            manifest_stage = runtime_dir / f"ASTER_MOVE_{direction}_360_UAL_V6_MANIFEST.json"
            manifest_stage.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            direction_records.append({
                "direction": direction,
                "atlas": manifest["atlas"],
                "manifest": (runtime / direction / manifest_stage.name).relative_to(ROOT).as_posix(),
                "atlas_sha256": manifest["atlas_sha256"],
                "qa": manifest["qa"],
            })

        # Six representative frames per direction expose gait continuity and
        # identity stability without hiding errors behind animation playback.
        preview_cell = 384
        preview_row = 410
        preview = Image.new("RGBA", (preview_cell * 6, preview_row * len(DIRECTIONS)), (16, 22, 29, 255))
        draw = ImageDraw.Draw(preview)
        lookup = {(direction, index): tile for direction, index, tile in preview_tiles}
        for row, direction in enumerate(DIRECTIONS):
            for column, index in enumerate((0, 4, 8, 12, 16, 20)):
                x = column * preview_cell
                y = row * preview_row
                preview.alpha_composite(lookup[(direction, index)], (x, y))
                draw.rectangle((x, y, x + 108, y + 25), fill=(4, 9, 13, 230))
                draw.text((x + 7, y + 6), f"{direction} F{index:02d}", fill=(132, 238, 244, 255))
        preview_stage = authoring_stage / "ASTER_MOVE_360_UAL_V6_MOTION_CONTACT.png"
        preview.save(preview_stage, optimize=True)

        root_manifest = {
            "schema": 1,
            "role": "ASTER 8-direction, 24-frame UAL1-measured articulated locomotion atlas V6 authoring result",
            "directions": list(DIRECTIONS),
            "frame_count_per_direction": FRAME_COUNT,
            "playback_fps": PLAYBACK_FPS,
            "atlas_frame_size": [args.tile, args.tile],
            "atlas_resolution_per_direction": [args.tile, args.tile * FRAME_COUNT],
            "ual_curve_contract": curves_path.relative_to(ROOT).as_posix(),
            "ual_curve_contract_sha256": sha256(curves_path),
            "ual_contract_summary": {
                "motion": "UAL1 Standard / Jog_Fwd_Loop",
                "sample_count": len(samples),
                "contact_windows_present": isinstance(contract["locomotion"].get("contact_windows"), (list, dict)),
                "events_present": isinstance(contract["locomotion"].get("events"), list),
                "root_motion_metrics_present": isinstance(contract["locomotion"].get("root_motion_metrics"), dict),
            },
            "deformation_contract": {
                "measured_joint_curves": True,
                "sine_fallback": False,
                "upper_body_rifle_rigid": True,
                "weapon_corridor_preserve_mask": True,
                "audited_direction_specific_raster_landmarks": True,
                "independent_leg_chains": True,
                "two_bone_ik": True,
                "ual_contact_driven_foot_plant": True,
                "ual_boot_pitch": True,
                "runtime_alpha_crossfade_baked": False,
                "movement_relative_variant": "forward_only; runtime aim-x-move direction expansion remains separate integration work",
            },
            "direction_outputs": direction_records,
            "contact_sheet": (authoring / preview_stage.name).relative_to(ROOT).as_posix(),
            "contact_sheet_sha256": sha256(preview_stage),
            "preserved_immediate_previous": "assets/units/operators/aster/move_360_ual_v5",
            "runtime_status": "ASSET_READY_NOT_CONNECTED_BY_THIS_GENERATOR",
            "visual_gate": "USER_REVIEW_REQUIRED",
            "production_expansion": "HOLD",
        }
        root_manifest_stage = authoring_stage / "ASTER_MOVE_360_UAL_V6_MANIFEST.json"
        root_manifest_stage.write_text(json.dumps(root_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        atomic_promote(authoring_stage, authoring)
        promoted_authoring = True
        atomic_promote(runtime_stage, runtime)
        promoted_runtime = True
        print("ASTER_MOVE_360_UAL_V6=" + json.dumps({
            "directions": len(DIRECTIONS),
            "frames_per_direction": FRAME_COUNT,
            "fps": PLAYBACK_FPS,
            "atlas_resolution": [args.tile, args.tile * FRAME_COUNT],
            "preview": root_manifest["contact_sheet"],
            "visual_gate": root_manifest["visual_gate"],
        }, ensure_ascii=False))
        return 0
    finally:
        if not promoted_authoring and authoring_stage.exists():
            shutil.rmtree(authoring_stage)
        if not promoted_runtime and runtime_stage.exists():
            shutil.rmtree(runtime_stage)


if __name__ == "__main__":
    raise SystemExit(main())
