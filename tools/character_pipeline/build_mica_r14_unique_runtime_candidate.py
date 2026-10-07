#!/usr/bin/env python3
"""Assemble the reviewed MICA R14 Blender+UAL move frames into a QA runtime.

This is a deterministic packaging step.  It does not generate, repaint, or
alter source art.  Each selected 384x384 Blender+UAL frame is copied into a
24-cell RGBA atlas so the FastCharacterRuntime can play the authored cadence
without the old duplicated-pose 2x/0x root-motion pulse.  The current idle and
fire atlases are copied unchanged into a separate candidate directory; the
promoted ``current`` runtime is never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
MOVE_FRAMES = 24
CELL = 384
R8C_MANIFEST = ROOT / "docs/ART_PRODUCTION/MICA_C03_V8_R14_EIGHTDIR_R8C_RECAPTURE_MANIFEST.json"
CURRENT_RUNTIME = ROOT / "assets/units/operators/mica/fast_runtime_v1/current"
CURRENT_DESCRIPTOR = ROOT / "data/character_pipeline/mica_runtime.json"


SOURCE_CANDIDATES = {
    "N": "art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_v8_r13_n_segmented_ual",
    "NE": "art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_v8_r14_ne_shared_handoff_r7_ual",
    "E": "art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_v8_r14_e_shared_handoff_r3_ual",
    "SE": "art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_v8_r14_se_lateral_handoff_ual",
    "S": "art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_v8_r13_s_segmented_ual",
    "SW": "art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_v8_r14_sw_lateral_handoff_ual",
    "W": "art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_v8_r14_w_shared_handoff_r3_ual",
    "NW": "art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_v8_r14_nw_shared_handoff_r7_ual",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def project_path(value: Path, label: str) -> Path:
    resolved = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside the project: {resolved}") from exc
    return resolved


def load_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{label} must be a JSON object: {path}")
    return value


def build_move_atlas(source_root: Path, direction: str, output: Path) -> dict[str, object]:
    frame_paths = [source_root / "blender_frames" / direction / "move" / f"{index:02d}.png" for index in range(MOVE_FRAMES)]
    if not all(path.is_file() for path in frame_paths):
        missing = [str(path) for path in frame_paths if not path.is_file()]
        raise SystemExit(f"missing {direction} Blender+UAL move frames: {missing[:3]}")

    frames: list[np.ndarray] = []
    frame_records: list[dict[str, object]] = []
    for index, path in enumerate(frame_paths):
        with Image.open(path) as image:
            rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
        if tuple(rgba.shape) != (CELL, CELL, 4):
            raise SystemExit(f"unexpected {direction} F{index:02d} dimensions: {path} {rgba.shape}")
        if not np.any(rgba[:, :, 3] > 0):
            raise SystemExit(f"{direction} F{index:02d} is fully transparent: {path}")
        frames.append(rgba.copy())
        frame_records.append({
            "index": index,
            "source": path.relative_to(ROOT).as_posix(),
            "source_sha256": sha256(path),
            "native_resolution": [CELL, CELL],
            "visible_pixels": int(np.count_nonzero(rgba[:, :, 3] > 0)),
        })

    content_hashes = [hashlib.sha256(frame.tobytes()).hexdigest() for frame in frames]
    if len(set(content_hashes)) != MOVE_FRAMES:
        raise SystemExit(f"{direction} candidate move frames are not all unique")
    atlas = np.concatenate(frames, axis=0)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(atlas, mode="RGBA").save(output, format="PNG")
    with Image.open(output) as check:
        decoded = np.asarray(check.convert("RGBA"), dtype=np.uint8)
    if decoded.shape != atlas.shape or not np.array_equal(decoded, atlas):
        raise SystemExit(f"lossless atlas round-trip failed: {output}")
    return {
        "atlas": output.relative_to(ROOT).as_posix(),
        "sha256": sha256(output),
        "resolution": [CELL, CELL * MOVE_FRAMES],
        "frame_count": MOVE_FRAMES,
        "unique_frames": len(set(content_hashes)),
        "source_candidate": source_root.relative_to(ROOT).as_posix(),
        "frames": frame_records,
    }


def copy_state(source: Path, output: Path, direction: str, state: str, frame_count: int) -> dict[str, object]:
    if not source.is_file():
        raise SystemExit(f"missing current {direction}/{state} atlas: {source}")
    with Image.open(source) as image:
        if image.mode != "RGBA" or image.size != (CELL, CELL * frame_count):
            raise SystemExit(f"invalid current {direction}/{state} atlas: {source} {image.mode} {image.size}")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, output)
    if sha256(source) != sha256(output):
        raise SystemExit(f"state copy hash mismatch: {output}")
    return {
        "atlas": output.relative_to(ROOT).as_posix(),
        "sha256": sha256(output),
        "resolution": [CELL, CELL * frame_count],
        "frame_count": frame_count,
        "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(source),
        "unchanged_copy": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new project-local candidate runtime directory")
    parser.add_argument("--descriptor", type=Path, default=CURRENT_DESCRIPTOR, help="current schema-2 MICA descriptor")
    parser.add_argument("--r8c-manifest", type=Path, default=R8C_MANIFEST, help="R8C source mapping manifest")
    parser.add_argument(
        "--root-scale",
        type=float,
        default=None,
        help=(
            "Optional candidate-only movement multiplier. When supplied, the descriptor "
            "enables move_root_sync with one continuous factor for every authored cell."
        ),
    )
    parser.add_argument(
        "--candidate-name",
        default="r14_r8c_unique_move_qa",
        help="Candidate label written to the isolated descriptor/manifest.",
    )
    args = parser.parse_args()

    output = project_path(args.output, "output")
    descriptor_path = project_path(args.descriptor, "descriptor")
    r8c_manifest_path = project_path(args.r8c_manifest, "R8C manifest")
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing candidate: {output}")

    r8c_manifest = load_json(r8c_manifest_path, "R8C manifest")
    if r8c_manifest.get("candidate_status") != "UNREVIEWED_DO_NOT_PROMOTE":
        raise SystemExit("R8C source mapping must remain UNREVIEWED_DO_NOT_PROMOTE")
    directions = r8c_manifest.get("directions")
    if not isinstance(directions, dict) or set(directions) != set(DIRECTIONS):
        raise SystemExit("R8C manifest does not cover exactly eight directions")
    for direction in DIRECTIONS:
        recorded = str(directions[direction].get("source_candidate", "")) if isinstance(directions[direction], dict) else ""
        if recorded != SOURCE_CANDIDATES[direction]:
            raise SystemExit(f"R8C source mapping drift for {direction}: {recorded}")

    descriptor = load_json(descriptor_path, "MICA descriptor")
    if descriptor.get("schema") != 2 or descriptor.get("actor_id") != "CHR_PROTO_03":
        raise SystemExit("expected MICA schema-2 descriptor")
    if set(descriptor.get("directions", {})) != set(DIRECTIONS):
        raise SystemExit("MICA descriptor direction set is incomplete")

    output.mkdir(parents=True)
    outputs: dict[str, dict[str, object]] = {}
    descriptor_candidate = json.loads(json.dumps(descriptor))
    descriptor_candidate["candidate"] = str(args.candidate_name)
    if args.root_scale is None:
        descriptor_candidate["move_root_sync"] = {
            "enabled": False,
            "samples_per_pose": 1,
            "advance_scale": 1.0,
            "hold_scale": 1.0,
            "rationale": "R14 R8C carries 24 unique Blender+UAL move cells; gameplay root advances continuously at one factor per unique frame.",
        }
    else:
        root_scale = float(args.root_scale)
        if not 0.0 < root_scale <= 2.0:
            raise SystemExit("--root-scale must be greater than 0 and at most 2.0")
        descriptor_candidate["move_root_sync"] = {
            "enabled": True,
            "samples_per_pose": 1,
            "advance_scale": root_scale,
            "hold_scale": root_scale,
            "rationale": (
                "Candidate-only gait-speed calibration: R8C authored sole/root travel is "
                "approximately 1.64px per 24fps move cell; the descriptor factor is kept "
                "constant so a 60Hz runtime capture can measure planted support without "
                "the legacy duplicate-cell 2x/0x pulse."
            ),
        }
    for direction in DIRECTIONS:
        source_root = project_path(Path(SOURCE_CANDIDATES[direction]), f"{direction} source candidate")
        if not source_root.is_dir():
            raise SystemExit(f"missing source candidate: {source_root}")
        direction_out = output / direction
        move_record = build_move_atlas(source_root, direction, direction_out / "move.png")
        idle_record = copy_state(CURRENT_RUNTIME / direction / "idle.png", direction_out / "idle.png", direction, "idle", 4)
        fire_record = copy_state(CURRENT_RUNTIME / direction / "fire.png", direction_out / "fire.png", direction, "fire", 6)
        outputs[direction] = {"idle": idle_record, "move": move_record, "fire": fire_record}
        direction_spec = descriptor_candidate["directions"][direction]
        direction_spec["move_atlas"] = move_record["atlas"]
        # The current frame-indexed muzzle table remains valid for this QA
        # candidate because R14 changes only the lower-body move plates.  Its
        # hashes and source provenance stay pinned in the descriptor manifest.

    descriptor_out = output / "runtime_descriptor.json"
    descriptor_out.write_text(json.dumps(descriptor_candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    descriptor_out_hash = sha256(descriptor_out)

    manifest = {
        "schema": 1,
        "role": "MICA C03 R14 R8C unique-frame FastCharacterRuntime QA candidate",
        "actor_id": "CHR_PROTO_03",
        "costume_id": "MICA_RECON_C03",
        "candidate_status": "UNREVIEWED_DO_NOT_PROMOTE",
        "promotion": "HOLD_PENDING_GODOT_RUNTIME_AND_PONYTAIL_FULL_REVIEW",
        "source_art_modified": False,
        "motion_source": "Blender + UAL R14 R8C recapture mapping",
        "r8c_manifest": r8c_manifest_path.relative_to(ROOT).as_posix(),
        "r8c_manifest_sha256": sha256(r8c_manifest_path),
        "input_descriptor": descriptor_path.relative_to(ROOT).as_posix(),
        "input_descriptor_sha256": sha256(descriptor_path),
        "runtime_descriptor": descriptor_out.relative_to(ROOT).as_posix(),
        "runtime_descriptor_sha256": descriptor_out_hash,
        "frame_contract": {
            "cell_size": CELL,
            "move_frames": MOVE_FRAMES,
            "move_frame_uniqueness": "24/24 per direction",
            "move_root_sync": (
                "disabled; continuous root factor 1.0"
                if args.root_scale is None
                else f"enabled; continuous root factor {float(args.root_scale):.9f}"
            ),
            "idle_source": "copied unchanged from current for QA isolation",
            "fire_source": "copied unchanged from current for QA isolation",
        },
        "directions": outputs,
        "quarantine": {
            "prior_current_and_failed_candidates_preserved": True,
            "deletion_performed": False,
            "retirement_manifest_required_before_disposal": True,
        },
    }
    manifest_path = output / "MICA_C03_R14_R8C_UNIQUE_RUNTIME_CANDIDATE.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate": output.relative_to(ROOT).as_posix(),
        "runtime_descriptor": descriptor_out.relative_to(ROOT).as_posix(),
        "manifest": manifest_path.relative_to(ROOT).as_posix(),
        "directions": len(outputs),
        "unique_move_frames_per_direction": MOVE_FRAMES,
        "promotion": manifest["promotion"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
