#!/usr/bin/env python3
"""Build visual proof and validate ASTER's fire-contact muzzle alignment.

The JSON contract is consumed by Godot and the interactive HTML preview.  This
validator independently checks its barrel-axis math against the authoritative
Fire V4 contact cells, then emits an overlay contact sheet and machine-readable
evidence.  It never edits source art.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "assets/units/operators/aster/ASTER_MUZZLE_ALIGNMENT_V7.json"
FIRE_ROOT = ROOT / "assets/units/operators/aster/fire_360_clean_v4"
OUTPUT_ROOT = ROOT / "artifacts/aster_muzzle_alignment_v7"
HTML_EVIDENCE_PATH = OUTPUT_ROOT / "ASTER_HTML_MUZZLE_ALIGNMENT_V7_EVIDENCE.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def angular_error_degrees(lhs: float, rhs: float) -> float:
    return abs((lhs - rhs + 180.0) % 360.0 - 180.0)


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    directions = contract["directions"]
    cell = int(contract["cell_size"])
    frame = int(contract["source_frame"])
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    contact = Image.new("RGB", (cell * 4, cell * 2), (7, 16, 21))
    draw = ImageDraw.Draw(contact)
    evidence: dict[str, object] = {
        "schema": 1,
        "contract": str(CONTRACT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "contract_sha256": sha256(CONTRACT_PATH),
        "source_frame": frame,
        "directions": {},
        # The triangular muzzle cage is open at its distal centre, so a valid
        # socket may sit several pixels outside/inside transparent negative
        # space.  Eight pixels constrains it to the measured device tip while
        # runtime flash/projectile equality is tested separately at <=2 px.
        "thresholds": {"socket_to_nearest_tip_alpha_px": 8.0, "declared_axis_error_degrees": 0.01},
    }
    passed = True
    for index, direction in enumerate(directions):
        atlas_path = FIRE_ROOT / f"ASTER_FIRE_{direction}_CLEAN_RGBA.webp"
        atlas = Image.open(atlas_path).convert("RGBA")
        source = atlas.crop((0, frame * cell, cell, (frame + 1) * cell))
        calibration = contract["calibration"][direction]
        muzzle_x, muzzle_y = map(float, calibration["muzzle_xy"])
        inner_x, inner_y = map(float, calibration["barrel_inner_xy"])
        declared = float(calibration["barrel_tangent_degrees"])
        measured = math.degrees(math.atan2(muzzle_y - inner_y, muzzle_x - inner_x)) % 360.0
        axis_error = angular_error_degrees(declared, measured)

        alpha = source.getchannel("A")
        radius = 8
        nearest = float("inf")
        nearest_xy = (int(round(muzzle_x)), int(round(muzzle_y)))
        for y in range(max(0, int(muzzle_y) - radius), min(cell, int(muzzle_y) + radius + 1)):
            for x in range(max(0, int(muzzle_x) - radius), min(cell, int(muzzle_x) + radius + 1)):
                if alpha.getpixel((x, y)) >= 24:
                    distance = math.hypot(x - muzzle_x, y - muzzle_y)
                    if distance < nearest:
                        nearest = distance
                        nearest_xy = (x, y)
        direction_pass = nearest <= 8.0 and axis_error <= 0.01
        passed = passed and direction_pass

        panel_x = (index % 4) * cell
        panel_y = (index // 4) * cell
        background = Image.new("RGBA", (cell, cell), (7, 16, 21, 255))
        background.alpha_composite(source)
        contact.paste(background.convert("RGB"), (panel_x, panel_y))
        tangent = math.radians(declared)
        forward = (muzzle_x + math.cos(tangent) * 72.0, muzzle_y + math.sin(tangent) * 72.0)
        backward = (muzzle_x - math.cos(tangent) * 92.0, muzzle_y - math.sin(tangent) * 92.0)
        draw.line((panel_x + backward[0], panel_y + backward[1], panel_x + forward[0], panel_y + forward[1]), fill=(255, 206, 65), width=2)
        draw.ellipse((panel_x + muzzle_x - 5, panel_y + muzzle_y - 5, panel_x + muzzle_x + 5, panel_y + muzzle_y + 5), outline=(92, 247, 255), width=3)
        draw.line((panel_x + muzzle_x - 8, panel_y + muzzle_y, panel_x + muzzle_x + 8, panel_y + muzzle_y), fill=(92, 247, 255), width=1)
        draw.line((panel_x + muzzle_x, panel_y + muzzle_y - 8, panel_x + muzzle_x, panel_y + muzzle_y + 8), fill=(92, 247, 255), width=1)
        draw.rectangle((panel_x, panel_y, panel_x + 154, panel_y + 22), fill=(0, 0, 0))
        draw.text((panel_x + 5, panel_y + 5), f"{direction}  {declared:.1f} deg", fill=(255, 255, 255))

        evidence["directions"][direction] = {
            "source_atlas": str(atlas_path.relative_to(ROOT)).replace("\\", "/"),
            "source_sha256": sha256(atlas_path),
            "muzzle_xy": [muzzle_x, muzzle_y],
            "barrel_inner_xy": [inner_x, inner_y],
            "declared_tangent_degrees": declared,
            "measured_tangent_degrees": measured,
            "declared_axis_error_degrees": axis_error,
            "nearest_alpha_xy": list(nearest_xy),
            "socket_to_nearest_tip_alpha_px": nearest,
            "pass": direction_pass,
        }

    contact_path = OUTPUT_ROOT / "ASTER_MUZZLE_ALIGNMENT_V7_CONTACT.png"
    contact.save(contact_path)
    evidence["contact"] = str(contact_path.relative_to(ROOT)).replace("\\", "/")
    evidence["contact_sha256"] = sha256(contact_path)
    if HTML_EVIDENCE_PATH.exists():
        html = json.loads(HTML_EVIDENCE_PATH.read_text(encoding="utf-8"))
        html_checks: dict[str, object] = {"path": str(HTML_EVIDENCE_PATH.relative_to(ROOT)).replace("\\", "/"), "directions": {}}
        html_pass = html.get("alignment_status") == "ready" and html.get("muzzle_lifetime_ms") == 60 and html.get("gameplay_aim_source") == "actor_center_to_pointer"
        shots = html.get("shots", [])
        html_pass = html_pass and len(shots) == len(directions)
        for index, direction in enumerate(directions):
            if index >= len(shots):
                break
            shot = shots[index]
            dataset = shot.get("dataset", {})
            expected_source = contract["calibration"][direction]["muzzle_xy"]
            expected_start = (512.0 + float(expected_source[0]) - 192.0, 310.0 + float(expected_source[1]) - 192.0)
            start = tuple(map(float, str(dataset.get("lastShotStart", "nan,nan")).split(",")))
            target = tuple(map(float, str(dataset.get("lastShotTarget", "nan,nan")).split(",")))
            start_error = math.hypot(start[0] - expected_start[0], start[1] - expected_start[1])
            trajectory = math.degrees(math.atan2(target[1] - start[1], target[0] - start[0])) % 360.0
            aim = float(dataset.get("aimDegrees", "nan")) % 360.0
            trajectory_error = angular_error_degrees(trajectory, aim)
            shot_pass = dataset.get("sector") == direction and dataset.get("muzzleAlignmentStatus") == "ready" and dataset.get("muzzleLifetimeMs") == "60" and start_error <= 2.0 and trajectory_error <= 1.0
            html_pass = html_pass and shot_pass
            html_checks["directions"][direction] = {
                "expected_start": list(expected_start),
                "actual_start": list(start),
                "start_error_px": start_error,
                "aim_degrees": aim,
                "trajectory_degrees": trajectory,
                "trajectory_error_degrees": trajectory_error,
                "authored_barrel_residual_degrees": float(dataset.get("lastShotResidualDegrees", "nan")),
                "pass": shot_pass,
            }
        html_checks["pass"] = html_pass
        evidence["html_runtime"] = html_checks
        passed = passed and html_pass
    else:
        evidence["html_runtime"] = {"status": "not_run", "pass": None}
    evidence["pass"] = passed
    evidence_path = OUTPUT_ROOT / "ASTER_MUZZLE_ALIGNMENT_V7_EVIDENCE.json"
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(f"ASTER_MUZZLE_ALIGNMENT_V7: {'PASS' if passed else 'FAIL'}")
    print(f"contact={contact_path}")
    print(f"evidence={evidence_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
