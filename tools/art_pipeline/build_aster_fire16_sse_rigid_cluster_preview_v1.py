#!/usr/bin/env python3
"""Build an ASTER SSE rigid rifle/hands structural preview.

This helper transforms the approved SE rifle, trigger forearm/hand, and
support forearm/hand masks as one immutable similarity cluster.  It emits a
green-matte, cluster-only structural preview and 1080p+ review evidence.  It
never composites the cluster over a body, generates pixels, starts a server,
or promotes an asset to runtime.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/"
    "aim_master_v2/source/ASTER_FIRE_SE_DIRECTION_AIM_MASTER_V2_GREEN.png"
)
SUBJECT = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/"
    "aim_master_v2/masks/ASTER_FIRE_SE_DIRECTION_AIM_MASTER_V2_MASK.png"
)
MASK_ROOT = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_semantic_masks_v1/manual_fallback_v1"
)
MASKS = {
    "rifle": MASK_ROOT / "ASTER_FIRE_SE_RIFLE_MANUAL_FALLBACK_V1_MASK.png",
    "trigger_forearm_hand": MASK_ROOT
    / "ASTER_FIRE_SE_TRIGGER_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png",
    "support_forearm_hand": MASK_ROOT
    / "ASTER_FIRE_SE_SUPPORT_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png",
}
MASK_QA = MASK_ROOT / "ASTER_FIRE_SE_THREE_PART_SOURCE_MASK_QA_V1.json"
OUT = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_rigid_cluster_preview_v1"
)
VALIDATOR = ROOT / "tools/art_pipeline/validate_visual_evidence_1080p.py"

GREEN_NAME = "ASTER_FIRE_SSE_RIGID_CLUSTER_PREVIEW_V1_GREEN.png"
REVIEW_NAME = "ASTER_FIRE_SSE_RIGID_CLUSTER_PREVIEW_V1_REVIEW_1920X1440.png"
QA_NAME = "ASTER_FIRE_SSE_RIGID_CLUSTER_PREVIEW_V1_TECHNICAL_QA.json"
MANIFEST_NAME = "ASTER_FIRE_SSE_RIGID_CLUSTER_PREVIEW_V1_MANIFEST.json"
EVIDENCE_NAME = "ASTER_FIRE_SSE_RIGID_CLUSTER_PREVIEW_V1_EVIDENCE_1080P_QA.json"

EXPECTED = {
    SOURCE: "1a674d5d1f68cebc20a61fae1187f725500189700897785550b5642d8a174838",
    SUBJECT: "4dedc673b1d8029b7455e1259994e354285838ff7d7618d77828cef89ac8e9b5",
    MASKS["rifle"]: "51876f84ba9fe1f5c3d300bc4057950e500bb655d58162547f59d6e4c52b55c6",
    MASKS["trigger_forearm_hand"]: "5ececa81d3870a91d91a7f799e8e41f15cb7c54dc2f32999110b8bdaf6d078e9",
    MASKS["support_forearm_hand"]: "bc5feaf79f9264a84fa22e6f58493378687f5a20ba488637c25bf41abbea83b9",
}
EXPECTED_SIZE = (1254, 1254)
EXACT_GREEN = np.asarray((0, 255, 0), dtype=np.uint8)

SOURCE_INNER = np.asarray((878.4531, 525.7656), dtype=np.float64)
SOURCE_MUZZLE = np.asarray((1018.8750, 610.6719), dtype=np.float64)
TARGET_INNER = np.asarray((752.7266, 649.8594), dtype=np.float64)
TARGET_MUZZLE = np.asarray((816.6171, 804.1048), dtype=np.float64)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def decode(path: Path, flags: int) -> np.ndarray:
    decoded = cv2.imdecode(np.frombuffer(path.read_bytes(), dtype=np.uint8), flags)
    if decoded is None:
        raise RuntimeError(f"could not decode {path}")
    return decoded


def similarity() -> tuple[np.ndarray, dict[str, float | list[list[float]]]]:
    source_vector = SOURCE_MUZZLE - SOURCE_INNER
    target_vector = TARGET_MUZZLE - TARGET_INNER
    source_angle = math.atan2(float(source_vector[1]), float(source_vector[0]))
    target_angle = math.atan2(float(target_vector[1]), float(target_vector[0]))
    rotation = target_angle - source_angle
    scale = float(np.linalg.norm(target_vector) / np.linalg.norm(source_vector))
    linear = scale * np.asarray(
        (
            (math.cos(rotation), -math.sin(rotation)),
            (math.sin(rotation), math.cos(rotation)),
        ),
        dtype=np.float64,
    )
    translation = TARGET_INNER - linear @ SOURCE_INNER
    matrix = np.column_stack((linear, translation))
    singular = np.linalg.svd(linear, compute_uv=False)
    mapped_inner = linear @ SOURCE_INNER + translation
    mapped_muzzle = linear @ SOURCE_MUZZLE + translation
    endpoint_residuals = (
        float(np.linalg.norm(mapped_inner - TARGET_INNER)),
        float(np.linalg.norm(mapped_muzzle - TARGET_MUZZLE)),
    )
    mapped_vector = mapped_muzzle - mapped_inner
    mapped_angle = math.degrees(math.atan2(float(mapped_vector[1]), float(mapped_vector[0])))
    target_degrees = math.degrees(target_angle)
    tangent_residual = abs(((mapped_angle - target_degrees + 180.0) % 360.0) - 180.0)
    return matrix, {
        "scale": scale,
        "rotation_degrees": math.degrees(rotation),
        "source_tangent_degrees": math.degrees(source_angle),
        "target_tangent_degrees": target_degrees,
        "mapped_tangent_degrees": mapped_angle,
        "tangent_residual_degrees": tangent_residual,
        "singular_values": [float(value) for value in singular],
        "singular_value_ratio": float(max(singular) / min(singular)),
        "endpoint_residual_pixels": [float(value) for value in endpoint_residuals],
        "mapped_inner_xy": [float(value) for value in mapped_inner],
        "mapped_muzzle_xy": [float(value) for value in mapped_muzzle],
        "matrix_2x3": [[float(value) for value in row] for row in matrix],
    }


def transform_cluster(
    source_rgb: np.ndarray, union: np.ndarray, matrix: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Warp the cluster once, with premultiplied color and a shared alpha."""
    alpha = union.astype(np.float32)
    premultiplied = source_rgb.astype(np.float32) * alpha[:, :, None]
    size = (EXPECTED_SIZE[0], EXPECTED_SIZE[1])
    warped_alpha = cv2.warpAffine(
        alpha,
        matrix,
        size,
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0.0,
    )
    warped_premultiplied = cv2.warpAffine(
        premultiplied,
        matrix,
        size,
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0.0, 0.0, 0.0),
    )
    warped_alpha = np.clip(warped_alpha, 0.0, 1.0)
    safe = np.maximum(warped_alpha[:, :, None], 1e-6)
    straight = np.clip(warped_premultiplied / safe, 0.0, 255.0)
    matte = (
        straight * warped_alpha[:, :, None]
        + EXACT_GREEN.astype(np.float32)[None, None, :] * (1.0 - warped_alpha[:, :, None])
    )
    output = np.rint(np.clip(matte, 0.0, 255.0)).astype(np.uint8)
    support = warped_alpha > 1e-6
    output[~support] = EXACT_GREEN
    return output, warped_alpha, support


def component_record(mask: np.ndarray) -> dict[str, object]:
    count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    areas = sorted((int(value) for value in stats[1:, cv2.CC_STAT_AREA]), reverse=True)
    ys, xs = np.nonzero(mask)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)] if xs.size else [0, 0, 0, 0]
    return {
        "pixels": int(np.count_nonzero(mask)),
        "components": max(0, count - 1),
        "significant_components": len([value for value in areas if value >= 200]),
        "largest_component_ratio": float(areas[0] / max(1, sum(areas))) if areas else 0.0,
        "bbox_xyxy_exclusive": bbox,
    }


def draw_anchor(
    draw: ImageDraw.ImageDraw,
    offset: tuple[int, int],
    inner: np.ndarray,
    muzzle: np.ndarray,
) -> None:
    ox, oy = offset
    p0 = (ox + int(round(float(inner[0]))), oy + int(round(float(inner[1]))))
    p1 = (ox + int(round(float(muzzle[0]))), oy + int(round(float(muzzle[1]))))
    draw.line((p0, p1), fill=(255, 0, 255), width=3)
    for point in (p0, p1):
        draw.ellipse((point[0] - 8, point[1] - 8, point[0] + 8, point[1] + 8), outline=(255, 0, 255), width=3)


def build_review(preview: np.ndarray, output: Path, geometry: dict[str, object], qa_result: str) -> None:
    sheet = Image.new("RGB", (1920, 1440), (8, 15, 20))
    native = Image.fromarray(preview, "RGB")
    runtime = native.resize((384, 384), Image.Resampling.LANCZOS)
    gameplay = native.resize((131, 131), Image.Resampling.LANCZOS)
    native_xy, runtime_xy, gameplay_xy = (24, 88), (1302, 88), (1710, 88)
    sheet.paste(native, native_xy)
    sheet.paste(runtime, runtime_xy)
    sheet.paste(gameplay, gameplay_xy)

    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    cyan, amber, white, muted = (75, 230, 246), (255, 190, 65), (245, 247, 250), (175, 190, 200)
    draw.text((24, 20), "ASTER SSE RIGID CLUSTER PREVIEW V1 — STRUCTURAL PREVIEW / HOLD", fill=white, font=font)
    draw.text((24, 43), "CONTRACT INCOMPLETE — cluster only; no body composite; no runtime promotion", fill=amber, font=font)
    draw.text((24, 70), "NATIVE 1254x1254 1:1", fill=cyan, font=font)
    draw.text((1302, 70), "384x384 1:1 inspection", fill=cyan, font=font)
    draw.text((1710, 70), "131x131 1:1 inspection", fill=cyan, font=font)
    draw_anchor(draw, native_xy, TARGET_INNER, TARGET_MUZZLE)

    x, y = 1302, 500
    lines = (
        f"QA: {qa_result}",
        "Role: transformed cluster only (RIFLE | TRIGGER | SUPPORT)",
        "One shared similarity transform; no per-part deformation",
        f"SE source inner: ({SOURCE_INNER[0]:.4f}, {SOURCE_INNER[1]:.4f})",
        f"SE source muzzle: ({SOURCE_MUZZLE[0]:.4f}, {SOURCE_MUZZLE[1]:.4f})",
        f"SSE target inner: ({TARGET_INNER[0]:.4f}, {TARGET_INNER[1]:.4f})",
        f"SSE target muzzle: ({TARGET_MUZZLE[0]:.4f}, {TARGET_MUZZLE[1]:.4f})",
        f"scale: {float(geometry['scale']):.9f}",
        f"rotation: {float(geometry['rotation_degrees']):.9f} deg",
        f"singular ratio: {float(geometry['singular_value_ratio']):.12f} <= 1.02",
        f"tangent residual: {float(geometry['tangent_residual_degrees']):.12f} deg <= 0.1",
        f"endpoint residual px: {max(geometry['endpoint_residual_pixels']):.12f}",
        "MAGENTA: mapped target anchor axis",
        "Exact-green matte exterior; no upscale in any panel",
        "Visual PASS is not claimed. Full 17-mask contract is incomplete.",
    )
    for index, line in enumerate(lines):
        fill = amber if index in {0, 1, 14} else muted
        draw.text((x, y + index * 23), line, fill=fill, font=font)
    sheet.save(output, "PNG", optimize=True)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    for path, expected_sha in EXPECTED.items():
        if not path.is_file() or sha256(path) != expected_sha:
            raise SystemExit(f"locked input unavailable or SHA mismatch: {path}")
    mask_qa = json.loads(MASK_QA.read_text(encoding="utf-8"))
    if mask_qa.get("result") != "PASS_THREE_SE_SOURCE_MASK_CHECKS_ONLY_HOLD":
        raise SystemExit("manual three-part source-mask QA is not at the locked preliminary PASS/HOLD state")

    source_bgr = decode(SOURCE, cv2.IMREAD_COLOR)
    subject_raw = decode(SUBJECT, cv2.IMREAD_GRAYSCALE)
    if source_bgr.shape[:2][::-1] != EXPECTED_SIZE or subject_raw.shape[:2][::-1] != EXPECTED_SIZE:
        raise SystemExit("locked SE source inputs must be 1254x1254")
    source_rgb = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2RGB)
    subject = subject_raw == 255
    parts = {name: decode(path, cv2.IMREAD_GRAYSCALE) == 255 for name, path in MASKS.items()}
    union = np.logical_or.reduce(tuple(parts.values()))
    if any(np.count_nonzero(mask & ~subject) for mask in parts.values()):
        raise SystemExit("locked source semantic mask escaped approved SE subject")

    matrix, geometry = similarity()
    preview, warped_alpha, support = transform_cluster(source_rgb, union, matrix)
    exact_green = np.all(preview == EXACT_GREEN[None, None, :], axis=2)
    input_metrics = component_record(union)
    output_metrics = component_record(warped_alpha >= 0.5)
    alpha_area = float(np.sum(warped_alpha))
    expected_alpha_area = float(np.count_nonzero(union)) * float(geometry["scale"]) ** 2
    area_ratio = alpha_area / max(1e-9, expected_alpha_area)
    border_alpha_pixels = int(
        np.count_nonzero(warped_alpha[0, :] > 1e-6)
        + np.count_nonzero(warped_alpha[-1, :] > 1e-6)
        + np.count_nonzero(warped_alpha[:, 0] > 1e-6)
        + np.count_nonzero(warped_alpha[:, -1] > 1e-6)
    )
    exterior_non_green = int(np.count_nonzero((~support) & (~exact_green)))
    interior_exact_green = int(np.count_nonzero((warped_alpha >= 0.5) & exact_green))

    failures: list[str] = []
    if float(geometry["singular_value_ratio"]) > 1.02:
        failures.append("rigid similarity singular-value ratio exceeds 1.02")
    if float(geometry["tangent_residual_degrees"]) > 0.1:
        failures.append("mapped endpoint tangent residual exceeds 0.1 degree")
    if max(geometry["endpoint_residual_pixels"]) > 1e-6:
        failures.append("mapped endpoint pixel residual exceeds 1e-6")
    if exterior_non_green:
        failures.append(f"exact-green exterior violation: {exterior_non_green} pixels")
    if border_alpha_pixels:
        failures.append(f"transformed cluster clipped by canvas border: {border_alpha_pixels} alpha pixels")
    if not 0.995 <= area_ratio <= 1.005:
        failures.append(f"transformed alpha area ratio {area_ratio:.6f} outside 0.995-1.005")
    qa_result = "PASS_STRUCTURAL_GEOMETRY_ONLY_HOLD" if not failures else "FAIL"

    # The accepted v1 package is immutable.  A revised structural attempt must
    # use a new versioned directory so current/previous retention stays
    # auditable instead of silently replacing the current evidence.
    if OUT.exists():
        if not OUT.is_dir():
            raise SystemExit(f"refusing non-directory output collision: {OUT}")
        if any(OUT.iterdir()):
            raise SystemExit(
                f"immutable rigid-cluster preview v1 already exists; author a new version instead of overwriting {OUT}"
            )
        OUT.rmdir()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".fire_upper_16_sse_rigid_cluster_preview_v1_", dir=OUT.parent))
    try:
        green_path = stage / GREEN_NAME
        review_path = stage / REVIEW_NAME
        qa_path = stage / QA_NAME
        manifest_path = stage / MANIFEST_NAME
        evidence_path = stage / EVIDENCE_NAME
        Image.fromarray(preview, "RGB").save(green_path, "PNG", optimize=True)
        build_review(preview, review_path, geometry, qa_result)

        qa = {
            "schema": 1,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "role": "ASTER SSE rigid rifle/hands cluster structural preview technical QA",
            "result": qa_result,
            "status": "HOLD_CONTRACT_INCOMPLETE",
            "promotion_ready": False,
            "runtime_asset": False,
            "visual_pass_claimed": False,
            "costume_id": "ASTER_COMBAT_SUIT_C01",
            "source_mask_gate": mask_qa.get("result"),
            "geometry": geometry,
            "thresholds": {
                "singular_value_ratio_max": 1.02,
                "mapped_tangent_residual_degrees_max": 0.1,
                "mapped_endpoint_residual_pixels_max": 1e-6,
                "transformed_alpha_area_ratio_range": [0.995, 1.005],
                "canvas_border_alpha_pixels": 0,
                "exterior_non_exact_green_pixels": 0,
            },
            "metrics": {
                "input_union": input_metrics,
                "output_union_alpha_ge_0p5": output_metrics,
                "input_union_pixels": int(np.count_nonzero(union)),
                "warped_alpha_area": alpha_area,
                "expected_scaled_alpha_area": expected_alpha_area,
                "transformed_alpha_area_ratio": area_ratio,
                "canvas_border_alpha_pixels": border_alpha_pixels,
                "exterior_non_exact_green_pixels": exterior_non_green,
                "interior_exact_green_pixels": interior_exact_green,
            },
            "failures": failures,
            "manual_visual_rejection_triggers": [
                "cut trigger hand or forearm",
                "cut support hand or forearm",
                "cut rifle barrel or open muzzle cage",
                "obvious resampling halo",
            ],
        }
        write_json(qa_path, qa)

        validator_cmd = [
            sys.executable,
            str(VALIDATOR),
            str(review_path),
            "--require-dynamic-capture",
            "--output",
            str(evidence_path),
        ]
        validator = subprocess.run(validator_cmd, cwd=ROOT, capture_output=True, text=True, check=False)
        if validator.returncode != 0:
            raise RuntimeError(f"1080p evidence validator failed: {validator.stdout}{validator.stderr}")
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        if evidence.get("gate") != "PASS":
            raise RuntimeError(f"1080p evidence gate did not pass: {evidence.get('gate')}")
        # The validator ran against the atomic staging copy.  Record the
        # stable post-promotion location in its report before hashing it into
        # the manifest; the pixels inspected are byte-identical after rename.
        for record in evidence.get("evidence", []):
            if Path(str(record.get("path", ""))).name == REVIEW_NAME:
                record["path"] = str(OUT / REVIEW_NAME)
        write_json(evidence_path, evidence)

        manifest = {
            "schema": 1,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "role": "ASTER SSE rigid-cluster-only structural preview",
            "status": "HOLD_CONTRACT_INCOMPLETE",
            "candidate_status": "HOLD",
            "promotion_ready": False,
            "runtime_asset": False,
            "visual_pass_claimed": False,
            "costume_id": "ASTER_COMBAT_SUIT_C01",
            "construction": {
                "method": "single shared 2D similarity transform of RIFLE | TRIGGER_FOREARM_HAND | SUPPORT_FOREARM_HAND",
                "independent_part_transforms": False,
                "body_composite_created": False,
                "model_used": False,
                "network_used": False,
                "server_used": False,
                "upscale_used": False,
            },
            "source": {"path": relative(SOURCE), "sha256": sha256(SOURCE), "resolution": [1254, 1254]},
            "subject_mask": {"path": relative(SUBJECT), "sha256": sha256(SUBJECT)},
            "source_mask_qa": {"path": relative(MASK_QA), "sha256": sha256(MASK_QA), "result": mask_qa.get("result")},
            "semantic_masks": {
                name: {"path": relative(path), "sha256": sha256(path)} for name, path in MASKS.items()
            },
            "anchors": {
                "source_inner_xy": SOURCE_INNER.tolist(),
                "source_muzzle_xy": SOURCE_MUZZLE.tolist(),
                "target_inner_xy": TARGET_INNER.tolist(),
                "target_muzzle_xy": TARGET_MUZZLE.tolist(),
            },
            "similarity": geometry,
            "output": {
                "path": relative(OUT / GREEN_NAME),
                "sha256": sha256(green_path),
                "resolution": [1254, 1254],
                "mode": "RGB",
                "matte": "exact #00FF00 outside transformed cluster support",
            },
            "review": {
                "path": relative(OUT / REVIEW_NAME),
                "sha256": sha256(review_path),
                "resolution": [1920, 1440],
                "native_panel": {"xy": [24, 88], "resolution": [1254, 1254], "scale": "1:1"},
                "runtime_inspection_panel": {"xy": [1302, 88], "resolution": [384, 384], "scale": "1:1"},
                "gameplay_inspection_panel": {"xy": [1710, 88], "resolution": [131, 131], "scale": "1:1"},
                "quality_claim": False,
            },
            "qa": {"path": relative(OUT / QA_NAME), "sha256": sha256(qa_path), "result": qa_result},
            "evidence_1080p": {"path": relative(OUT / EVIDENCE_NAME), "sha256": sha256(evidence_path), "gate": evidence.get("gate")},
            "contract_missing": list(mask_qa.get("missing_contract_masks", [])),
            "prohibitions": [
                "no body composite",
                "no finished-candidate claim",
                "no runtime promotion",
                "no visual PASS claim",
                "no per-part deformation",
            ],
        }
        write_json(manifest_path, manifest)
        if failures:
            raise RuntimeError("structural QA failure: " + "; ".join(failures))

        if OUT.exists():
            raise RuntimeError(f"output collision during atomic promotion: {OUT}")
        stage.replace(OUT)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise

    print(json.dumps({"output": str(OUT), "result": qa_result, "failures": failures}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
