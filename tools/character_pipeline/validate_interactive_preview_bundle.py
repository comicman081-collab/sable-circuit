#!/usr/bin/env python3
"""Validate a portable eight-direction interactive preview bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = {"idle": 4, "move": 24, "fire": 6}
CELL = 384


def project_path(value: Path, label: str) -> Path:
    resolved = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {resolved}") from exc
    return resolved


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--descriptor", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    html_path = project_path(args.html, "html")
    descriptor_path = project_path(args.descriptor, "descriptor")
    report_path = project_path(args.report, "report")
    if report_path.exists():
        raise SystemExit(f"refusing to overwrite report: {report_path}")
    text = html_path.read_text(encoding="utf-8")
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    if not re.search(r'<canvas[^>]+width="1920"[^>]+height="1080"', text):
        failures.append("missing native 1920x1080 canvas")
    if "new URL('./runtime/', window.location.href)" not in text:
        failures.append("runtime root is not portable and relative")
    muzzle_block = re.search(r"const MUZZLE = (\{.*?\});", text, re.DOTALL)
    parsed_muzzles: dict[str, object] = {}
    if muzzle_block:
        try:
            loaded_muzzles = json.loads(muzzle_block.group(1))
            if isinstance(loaded_muzzles, dict):
                parsed_muzzles = loaded_muzzles
        except json.JSONDecodeError:
            # Schema-1 previews used unquoted JS keys and one point per direction.
            for direction, x, y in re.findall(r"([A-Z]+):\[(-?[0-9.]+),(-?[0-9.]+)\]", muzzle_block.group(1)):
                parsed_muzzles[direction] = [float(x), float(y)]
    if tuple(parsed_muzzles) != DIRECTIONS:
        failures.append("HTML muzzle direction order is incomplete")
    for direction in DIRECTIONS:
        descriptor_entry = descriptor["directions"][direction]
        actual = parsed_muzzles.get(direction)
        if descriptor.get("schema", 1) >= 2:
            expected = {
                state: descriptor_entry[state + "_muzzle_xy"]
                for state in STATES
            }
            if actual != expected:
                failures.append(f"frame muzzle mismatch: {direction}")
        else:
            expected = [float(value) for value in descriptor_entry["muzzle_xy"]]
            if not isinstance(actual, list) or any(abs(left - right) > 0.001 for left, right in zip(actual, expected, strict=True)):
                failures.append(f"muzzle mismatch: {direction} html={actual} descriptor={expected}")
    files: list[dict[str, object]] = []
    runtime = html_path.parent / "runtime"
    for direction in DIRECTIONS:
        for state, frames in STATES.items():
            path = runtime / direction / f"{state}.png"
            if not path.is_file():
                failures.append(f"missing portable atlas: {direction}/{state}")
                continue
            with Image.open(path) as image:
                source = project_path(Path(descriptor["directions"][direction][state + "_atlas"]), f"descriptor {direction}/{state}")
                record = {
                    "path": path.relative_to(ROOT).as_posix(),
                    "sha256": digest(path),
                    "source_runtime": source.relative_to(ROOT).as_posix(),
                    "source_runtime_sha256": digest(source) if source.is_file() else None,
                    "mode": image.mode,
                    "resolution": list(image.size),
                    "alpha_extrema": list(image.getchannel("A").getextrema()) if image.mode == "RGBA" else None,
                }
                record["source_match"] = record["sha256"] == record["source_runtime_sha256"]
            if record["mode"] != "RGBA" or record["resolution"] != [CELL, CELL * frames] or record["alpha_extrema"] != [0, 255]:
                failures.append(f"invalid portable atlas: {direction}/{state} {record}")
            if not record["source_match"]:
                failures.append(f"portable atlas differs from promoted runtime: {direction}/{state}")
            files.append(record)
    payload = {
        "schema": 1,
        "gate": "PASS_STATIC_RUNTIME_BUNDLE" if not failures else "FAIL",
        "html": html_path.relative_to(ROOT).as_posix(),
        "html_sha256": digest(html_path),
        "descriptor": descriptor_path.relative_to(ROOT).as_posix(),
        "descriptor_sha256": digest(descriptor_path),
        "canvas": [1920, 1080],
        "directions": list(DIRECTIONS),
        "muzzle_descriptor_match": not any("muzzle" in item for item in failures),
        "portable_runtime_atlas_count": len(files),
        "files": files,
        "failures": failures,
        "dynamic_browser_note": "Browser file:// automation is a separate gate; this report validates the self-contained local bundle only.",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"gate": payload["gate"], "files": len(files), "muzzle_descriptor_match": payload["muzzle_descriptor_match"], "report": report_path.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
