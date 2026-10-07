#!/usr/bin/env python3
"""Validate ASTER lower-costume ownership across every Fire composite pair."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np


BUILDER_PATH = Path(__file__).with_name("build_aster_composite_fire_v5.py")
SPEC = importlib.util.spec_from_file_location("aster_composite_builder", BUILDER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generation", choices=("v5", "v6"), default="v5")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    generation = args.generation
    generation_upper = generation.upper()
    root = BUILDER.ROOT
    specs = BUILDER.resolved_source_specs(generation)
    family = f"composite_fire_{generation}"
    runtime = root / f"assets/units/operators/aster/{family}"
    authoring = root / f"art_src/pilot_v2/aster_v2/animation_360/{family}"
    manifest_path = runtime / f"ASTER_COMPOSITE_FIRE_{generation_upper}_MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit(f"composite manifest missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _alignment_path, muzzle_calibration, alignment_sha = BUILDER.load_muzzle_alignment()
    if manifest.get("muzzle_alignment_authority_sha256") != alignment_sha:
        raise SystemExit("composite muzzle alignment authority hash drifted")

    directions: dict[str, Any] = {}
    total_pairs = 0
    failures: list[str] = []
    for direction in BUILDER.DIRECTIONS:
        move_source = BUILDER.read_atlas(
            root / specs["move_lower"]["path"].format(direction=direction),
            24,
        )
        idle_source = BUILDER.read_atlas(
            root / specs["idle_lower"]["path"].format(direction=direction),
            4,
        )
        geometry = BUILDER.direction_geometry(move_source)
        clean_move_support = cv2.dilate(
            (np.max(move_source[:, :, :, 3], axis=0) > 8).astype(np.uint8),
            np.ones((9, 9), np.uint8),
            iterations=1,
        ) > 0
        cleaned_idle: list[np.ndarray] = []
        for frame in idle_source:
            cleaned, _cleanup = BUILDER.clean_idle_shadow_artifact(
                frame,
                clean_move_support,
                geometry["split_y"],
            )
            cleaned_idle.append(cleaned)
        lower_sources = {"move_lower": move_source, "idle_lower": cleaned_idle}
        split = {
            kind: BUILDER.read_atlas(
                runtime / Path(spec["output"].format(direction=direction)),
                int(spec["count"]),
            )
            for kind, spec in specs.items()
        }
        direction_summary: dict[str, Any] = {}
        for lower_kind in ("move_lower", "idle_lower"):
            count = 0
            minimum_costume = 1.0
            minimum_accent = 1.0
            maximum_mismatch = 0
            maximum_hole = 0
            disconnected = 0
            for lower_index, lower_frame in enumerate(split[lower_kind]):
                for upper_index, upper_frame in enumerate(split["fire_upper"]):
                    qa = BUILDER.composite_qa(
                        lower_frame,
                        upper_frame,
                        lower_sources[lower_kind][lower_index],
                        clean_move_support,
                        geometry,
                        direction,
                        muzzle_calibration,
                    )
                    count += 1
                    total_pairs += 1
                    minimum_costume = min(minimum_costume, qa["lower_costume_exact_retention_ratio"])
                    minimum_accent = min(minimum_accent, qa["white_cyan_exact_retention_ratio"])
                    maximum_mismatch = max(maximum_mismatch, qa["lower_costume_mismatch_pixels"])
                    maximum_hole = max(maximum_hole, qa["lower_costume_largest_missing_hole_px"])
                    if not qa["connected_lower_ownership"]:
                        disconnected += 1
                    if (
                        qa["lower_costume_mismatch_pixels"]
                        or qa["lower_costume_missing_hole_pixels"]
                        or qa["white_cyan_mismatch_pixels"]
                        or not qa["connected_lower_ownership"]
                    ):
                        failures.append(
                            f"{direction}:{lower_kind}:lower{lower_index}:fire{upper_index}"
                        )
            direction_summary[lower_kind] = {
                "pairs": count,
                "minimum_lower_costume_exact_retention_ratio": minimum_costume,
                "minimum_white_cyan_exact_retention_ratio": minimum_accent,
                "maximum_mismatch_pixels": maximum_mismatch,
                "maximum_missing_hole_component_px": maximum_hole,
                "disconnected_ownership_pairs": disconnected,
            }
        directions[direction] = direction_summary

    expected_pairs = len(BUILDER.DIRECTIONS) * (24 + 4) * 6
    contact_path = authoring / f"ASTER_COMPOSITE_FIRE_{generation_upper}_COSTUME_REGRESSION_CONTACT.png"
    passed = total_pairs == expected_pairs and not failures and contact_path.is_file()
    report = {
        "schema": 1,
        "generation": generation,
        "costumeId": "ASTER_COMBAT_SUIT_C01",
        "identity_changed": False,
        "manifest": manifest_path.relative_to(root).as_posix(),
        "manifest_sha256": BUILDER.sha256(manifest_path),
        "visual_contact": contact_path.relative_to(root).as_posix(),
        "visual_contact_sha256": BUILDER.sha256(contact_path) if contact_path.is_file() else None,
        "frame_pairs_scanned": total_pairs,
        "expected_frame_pairs": expected_pairs,
        "directions": directions,
        "failures": failures,
        "COSTUME_CONTINUITY_PASS": passed,
        "runtime_eligible_on_this_gate": passed,
    }
    output = args.output
    if output is None:
        output = root / "artifacts" / f"aster_costume_continuity_{generation}" / f"ASTER_COSTUME_CONTINUITY_{generation_upper}_QA.json"
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"ASTER_COSTUME_CONTINUITY_{generation_upper}="
        + json.dumps(
            {
                "result": "PASS" if passed else "FAIL",
                "pairs": total_pairs,
                "failures": len(failures),
                "report": output.relative_to(root).as_posix(),
            },
            ensure_ascii=False,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
