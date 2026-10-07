#!/usr/bin/env python3
"""Package Blender pose-switch frames into exact-green runtime atlases."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = {"idle": 4, "move": 24, "fire": 6}
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)


def project_path(path: Path, label: str) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {resolved}") from exc
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def longest_repeat(values: list[str]) -> int:
    maximum = run = 0
    previous = None
    for value in values:
        run = run + 1 if value == previous else 1
        previous = value
        maximum = max(maximum, run)
    return maximum


def pack_frame(path: Path, cell: int) -> np.ndarray:
    rgba = np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)
    if rgba.shape != (cell, cell, 4):
        raise SystemExit(f"unexpected Blender frame dimensions: {path} {rgba.shape}")
    rgb = rgba[:, :, :3]
    values = rgb.astype(np.int16)
    green_spill = (values[:, :, 1] >= values[:, :, 0] + 40) & (values[:, :, 1] >= values[:, :, 2] + 40)
    visible = (rgba[:, :, 3] >= 128) & ~green_spill
    packed = np.broadcast_to(GREEN, (cell, cell, 3)).copy()
    packed[visible] = rgb[visible]
    return packed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args()
    candidate = project_path(args.candidate, "candidate")
    spec_path = project_path(args.spec, "spec")
    manifest_path = candidate / "MICA_C03_POSE_SWITCH_BLENDER_UAL_RENDER_MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit(f"missing renderer manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("motion_only") is not True:
        raise SystemExit("renderer manifest must declare motion_only")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    cell = int(spec["runtime"]["cell_size"])
    if cell != 384:
        raise SystemExit("pose-switch packager requires 384px cells")
    if (candidate / "SOURCE_PROVENANCE.json").exists():
        raise SystemExit("refusing to overwrite packaged candidate")

    outputs: dict[str, dict[str, object]] = {}
    for direction in DIRECTIONS:
        rows = manifest.get("directions", {}).get(direction)
        if not isinstance(rows, dict):
            raise SystemExit(f"renderer manifest missing direction: {direction}")
        direction_output: dict[str, object] = {}
        for state, count in STATES.items():
            state_rows = rows.get(state)
            if not isinstance(state_rows, list) or len(state_rows) != count:
                raise SystemExit(f"missing {direction} {state} frame records")
            frame_paths = [candidate / "blender_frames" / direction / state / f"{index:02d}.png" for index in range(count)]
            if not all(path.is_file() for path in frame_paths):
                raise SystemExit(f"missing {direction} {state} frame file")
            cells = [pack_frame(path, cell) for path in frame_paths]
            frame_hashes = [hashlib.sha256(cell_data.tobytes()).hexdigest() for cell_data in cells]
            unique = len(set(frame_hashes))
            max_repeat = longest_repeat(frame_hashes)
            if state == "move" and (unique < 3 or max_repeat > 6):
                raise SystemExit(f"pose-switch gait structure failed: {direction} unique={unique} max_repeat={max_repeat}")
            atlas = np.concatenate(cells, axis=0)
            coverage = float(np.mean(np.all(atlas == GREEN, axis=2)))
            if not 0.10 <= coverage < 0.995:
                raise SystemExit(f"exact-green coverage failed: {direction} {state} {coverage:.6f}")
            output = candidate / direction / f"{state}_green.png"
            output.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(atlas, mode="RGB").save(output)
            pose_counts: dict[str, int] = {}
            for row in state_rows:
                name = str(row.get("pose_source", "unknown"))
                pose_counts[name] = pose_counts.get(name, 0) + 1
            direction_output[state] = {
                "atlas": output.relative_to(ROOT).as_posix(),
                "sha256": sha256(output),
                "frame_count": count,
                "atlas_resolution": [cell, cell * count],
                "unique_composite_frames": unique,
                "max_repeat": max_repeat,
                "exact_green_coverage": round(coverage, 6),
                "pose_source_counts": pose_counts,
            }
        outputs[direction] = direction_output

    provenance = {
        "schema": 1,
        "actor_id": spec["actor_id"],
        "imagegen_author": "built-in ImageGen",
        "blender_ual_motion": True,
        "source_art_modified": False,
        "costume_id": spec["costume_id"],
        "neutral_master_root": manifest["neutral_master_root"],
        "pose_source_root": manifest["pose_source_root"],
        "renderer_manifest": manifest_path.relative_to(ROOT).as_posix(),
        "renderer_manifest_sha256": sha256(manifest_path),
        "blender": manifest["blender"],
        "ual": manifest["ual"],
        "gait_contract": manifest["gait_contract"],
        "technical_packaging": "Blender RGBA frame packing and exact-green replacement only; no source-art redraw.",
        "outputs": outputs,
        "candidate_state": "UNREVIEWED_DO_NOT_PROMOTE",
        "review_status": {"ponytail_full": "PENDING_R17_POSE_SWITCH_REVIEW", "chatgpt_web": "PENDING_R17_ATTACHMENT_REVIEW"},
        "quarantine_policy": "Retain this candidate and all prior FAIL/HOLD candidates until a fully gated replacement is complete.",
    }
    provenance_path = candidate / "SOURCE_PROVENANCE.json"
    provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("POSE_SWITCH_BLENDER_UAL_PACKAGE_PASS=" + json.dumps({"candidate": candidate.relative_to(ROOT).as_posix(), "provenance": provenance_path.relative_to(ROOT).as_posix(), "directions": len(outputs)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
