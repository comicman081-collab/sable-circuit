#!/usr/bin/env python3
"""Build an RGBA runtime atlas and schema-2 descriptor for a pose-switch candidate.

The pose-switch packager deliberately keeps review atlases RGB/#00FF00 so the
source contract is inspectable.  Godot and the portable HTML preview consume a
separate project-local RGBA derivative.  This tool only keys the exact green
matte; it never repaints or regenerates source art and it refuses to overwrite
an existing runtime directory or descriptor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = {"idle": (4, 4.0), "move": (24, 24.0), "fire": (6, 12.0)}
CELL = 384
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)

# Coordinates are measured on the native 384px fire-contact cells.  The
# candidate is intentionally kept behind the review gate; the source and web
# reviewers may replace these tables before promotion.  Keeping a per-frame
# table (rather than a fixed direction offset) makes a later correction local
# and keeps the HTML/descriptor validator honest.
BASE_MUZZLE = {
    "E": [270.0, 135.0],
    "SE": [256.0, 151.0],
    "S": [191.0, 182.0],
    # R17 SW's weapon is visibly lower-right in the source art.  This point is
    # the actual barrel end, not a fake lower-left projection; the direction is
    # explicitly HOLD until the R18 SW source replacement is reviewed.
    "SW": [224.0, 158.0],
    "W": [111.0, 105.0],
    "NW": [119.0, 98.0],
    "N": [208.0, 53.0],
    "NE": [251.0, 84.0],
}


def project_path(value: Path, label: str) -> Path:
    resolved = (value if value.is_absolute() else ROOT / value).resolve()
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


def exact_green_rgba(source: Path, target: Path) -> dict[str, object]:
    rgb = np.asarray(Image.open(source).convert("RGB"), dtype=np.uint8)
    if rgb.ndim != 3 or rgb.shape[1] != CELL or rgb.shape[0] % CELL:
        raise SystemExit(f"invalid RGB atlas dimensions: {source} {rgb.shape}")
    green = np.all(rgb == GREEN, axis=2)
    if not bool(green[0, 0]) or not bool(green[-1, -1]):
        raise SystemExit(f"runtime source is not exact-green framed: {source}")
    alpha = np.where(green, 0, 255).astype(np.uint8)
    rgba = np.dstack((rgb, alpha))
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, mode="RGBA").save(target)
    coverage = float(green.mean())
    return {
        "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(source),
        "runtime": target.relative_to(ROOT).as_posix(),
        "runtime_sha256": sha256(target),
        "resolution": [int(rgb.shape[1]), int(rgb.shape[0])],
        "frames": int(rgb.shape[0] // CELL),
        "exact_green_coverage": round(coverage, 6),
        "alpha_zero_pixels": int(green.sum()),
        "source_art_modified": False,
    }


def repeated(point: list[float], count: int) -> list[list[float]]:
    return [[float(point[0]), float(point[1])] for _ in range(count)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new empty project-local runtime directory")
    parser.add_argument("--descriptor", type=Path, required=True, help="new project-local schema-2 descriptor")
    args = parser.parse_args()
    candidate = project_path(args.candidate, "candidate")
    output = project_path(args.output, "output")
    descriptor_path = project_path(args.descriptor, "descriptor")
    if not candidate.is_dir():
        raise SystemExit(f"candidate directory is missing: {candidate}")
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty runtime directory: {output}")
    if descriptor_path.exists():
        raise SystemExit(f"refusing to overwrite descriptor: {descriptor_path}")

    directions: dict[str, dict[str, object]] = {}
    atlas_rows: list[dict[str, object]] = []
    for direction in DIRECTIONS:
        entry: dict[str, object] = {}
        for state, (frames, fps) in STATES.items():
            source = candidate / direction / f"{state}_green.png"
            if not source.is_file():
                raise SystemExit(f"missing pose-switch atlas: {source}")
            target = output / direction / f"{state}.png"
            record = exact_green_rgba(source, target)
            if int(record["frames"]) != frames:
                raise SystemExit(f"frame count mismatch for {direction}.{state}: {record}")
            entry[f"{state}_atlas"] = target.relative_to(ROOT).as_posix()
            entry[f"{state}_muzzle_xy"] = repeated(BASE_MUZZLE[direction], frames)
            atlas_rows.append({"direction": direction, "state": state, "fps": fps, **record})
        entry["muzzle_xy"] = list(BASE_MUZZLE[direction])
        entry["muzzle_source"] = "native R17 fire-contact frame inspection; SW directional weapon mismatch HOLD"
        entry["muzzle_review"] = candidate.relative_to(ROOT).joinpath("MICA_C03_MUZZLE_SOCKET_AUTO_R17_1920X1080.png").as_posix()
        directions[direction] = entry

    descriptor = {
        "schema": 2,
        "actor_id": "CHR_PROTO_03",
        "display_name": "MICA",
        "costume_id": "MICA_RECON_C03",
        "candidate": candidate.relative_to(ROOT).as_posix(),
        "candidate_state": "UNREVIEWED_DO_NOT_PROMOTE",
        "cell_size": CELL,
        "display_scale": 0.34,
        "display_offset": [0.0, -49.0],
        "move_root_sync": {
            "enabled": True,
            "samples_per_pose": 1,
            "advance_scale": 1.0,
            "hold_scale": 0.0,
            "rationale": "Atlas planes are root-held; Godot/HTML owns world translation while UAL supplies cadence metadata.",
        },
        "states": {name: {"frames": frames, "fps": fps} for name, (frames, fps) in STATES.items()},
        "directions": directions,
        "source_contract": {
            "imagegen_author": "built-in ImageGen",
            "motion_authoring": "Blender+UAL",
            "costume_continuity": "PENDING_R17_REVIEW",
            "runtime_alpha": "exact-green matte keyed into separate RGBA derivative",
            "source_candidate": candidate.relative_to(ROOT).as_posix(),
            "no_source_art_redraw": True,
        },
        "review_gates": {
            "ponytail_full": "PENDING_R17_RUNTIME_REVIEW",
            "chatgpt_web": "PENDING_R17_HTML_REVIEW",
            "native_dynamic_1920x1080": "PENDING",
            "muzzle_projectile_contact": "PENDING",
        },
    }
    descriptor_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor_path.write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema": 1,
        "role": "MICA C03 R17 pose-switch project-local RGBA runtime derivative",
        "candidate": candidate.relative_to(ROOT).as_posix(),
        "candidate_state": "UNREVIEWED_DO_NOT_PROMOTE",
        "runtime_root": output.relative_to(ROOT).as_posix(),
        "descriptor": descriptor_path.relative_to(ROOT).as_posix(),
        "descriptor_sha256": sha256(descriptor_path),
        "atlas_rows": atlas_rows,
        "muzzle_contract": {
            "source": "native fire-contact frame inspection",
            "directional_hold": ["SW"],
            "review_required_before_promotion": True,
        },
        "gates": {
            "rgba_runtime_derivative": "PASS_TECHNICAL",
            "visual": "HOLD",
            "ponytail_full": "PENDING",
            "chatgpt_web": "PENDING",
            "dynamic_capture": "PENDING",
        },
        "source_art_modified": False,
        "quarantine_policy": "Retain candidate and all prior FAIL/HOLD candidates until every required gate passes.",
    }
    manifest_path = output / "MICA_C03_R17_POSE_SWITCH_RUNTIME_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("POSE_SWITCH_RUNTIME_BUILD_PASS=" + json.dumps({"runtime": output.relative_to(ROOT).as_posix(), "descriptor": descriptor_path.relative_to(ROOT).as_posix(), "atlases": len(atlas_rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
