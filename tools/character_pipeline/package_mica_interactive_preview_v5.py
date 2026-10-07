#!/usr/bin/env python3
"""Package a hash-verified, file:// portable MICA interactive preview.

The preview never reaches outside its own ``runtime`` folder.  This prevents a
browser's local-file policy from hiding a stale-atlas or missing-atlas error,
and keeps the exact runtime descriptor sockets coupled to the HTML projectile
origin table.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PREFIX = "MICA_C03"
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = {"idle": (4, 4.0), "move": (24, 24.0), "fire": (6, 12.0)}
CELL = 384
DEFAULT_RUNTIME = ROOT / "assets/units/operators/mica/fast_runtime_v1/current"
DEFAULT_DESCRIPTOR = ROOT / "data/character_pipeline/mica_runtime.json"
DEFAULT_TEMPLATE = ROOT / "artifacts/mica_c03_interactive_preview/MICA_C03_INTERACTIVE_STRIDE_FIRE.html"


def project_path(value: Path, label: str) -> Path:
    resolved = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {resolved}") from exc
    return resolved


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load_descriptor(descriptor_path: Path) -> tuple[dict[str, object], dict[str, dict[str, list[list[float]]]]]:
    payload = json.loads(descriptor_path.read_text(encoding="utf-8"))
    if payload.get("schema") != 2 or list(payload.get("directions", {})) != list(DIRECTIONS):
        raise SystemExit("MICA V5 preview requires schema-2 eight-direction runtime descriptor")
    muzzles: dict[str, dict[str, list[list[float]]]] = {}
    for direction in DIRECTIONS:
        entry = payload["directions"][direction]
        state_rows: dict[str, list[list[float]]] = {}
        for state, (frames, _fps) in STATES.items():
            row = entry.get(f"{state}_muzzle_xy")
            if not isinstance(row, list) or len(row) != frames:
                raise SystemExit(f"missing frame muzzle table: {direction}.{state}")
            if any(not isinstance(point, list) or len(point) != 2 for point in row):
                raise SystemExit(f"invalid frame muzzle table: {direction}.{state}")
            state_rows[state] = row
        muzzles[direction] = state_rows
    return payload, muzzles


def render_html(template: Path, muzzles: dict[str, dict[str, list[list[float]]]], revision: str) -> str:
    source = template.read_text(encoding="utf-8")
    source = re.sub(r"MICA C03 V[0-9]+(?: R[0-9]+)? — [^<]+", f"MICA C03 {revision} — Full-Body 8-Direction Stride & Frame-Tracked Fire", source, count=1)
    source = re.sub(r"MICA C03 V[0-9]+(?: R[0-9]+)? · [^<]+", f"MICA C03 {revision} · FULL-BODY 8-DIRECTION STRIDE &amp; FRAME-TRACKED FIRE", source, count=1)
    source = re.sub(r"(?:V[0-9]+[^<]*|E 방향[^<]*) · Blender\+UAL[^<]*네이티브 1920×1080", f"{revision} 직접 전신 보행 원화 · Blender+UAL 교대 보행 · 프레임별 실제 총구 소켓 · 네이티브 1920×1080", source, count=1)
    table = json.dumps(muzzles, ensure_ascii=False, separators=(",", ":"))
    pattern = r"const MUZZLE = \{.*?\};\n    const STATE ="
    updated, count = re.subn(pattern, f"const MUZZLE = {table};\\n    const STATE =", source, count=1, flags=re.DOTALL)
    if count != 1:
        raise SystemExit("legacy preview does not contain one replaceable MUZZLE table")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new empty project-local preview directory")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="existing project-local HTML template")
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME, help="reviewed project-local RGBA runtime atlas root")
    parser.add_argument("--descriptor", type=Path, default=DEFAULT_DESCRIPTOR, help="matching schema-2 project-local runtime descriptor")
    parser.add_argument("--revision", default="V7 R3", help="human-readable reviewed candidate revision")
    parser.add_argument("--diagnostic-only", action="store_true", help="legacy HTML is not Godot movement/fire parity; never deliver it as accepted gameplay")
    args = parser.parse_args()
    if not args.diagnostic_only:
        raise SystemExit("LEGACY_PREVIEW_BLOCKED: this template uses different movement/fire logic from Godot. Use a same-runtime web export and motion_harness browser matrix. --diagnostic-only permits an explicitly unapproved diagnostic bundle.")
    output = project_path(args.output, "output")
    template = project_path(args.template, "template")
    runtime = project_path(args.runtime, "runtime")
    descriptor_input = project_path(args.descriptor, "descriptor")
    if output.exists():
        raise SystemExit(f"refusing to overwrite preview output: {output}")
    if not runtime.is_dir() or not descriptor_input.is_file() or not template.is_file():
        raise SystemExit("MICA preview source runtime, descriptor, or template is missing")

    descriptor, muzzles = load_descriptor(descriptor_input)
    html = render_html(template, muzzles, args.revision)
    output.mkdir(parents=True)
    html_path = output / "MICA_C03_INTERACTIVE_STRIDE_FIRE.html"
    html_path.write_text(html, encoding="utf-8")
    descriptor_path = output / "MICA_C03_RUNTIME_DESCRIPTOR.json"
    descriptor_path.write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    entries: list[dict[str, object]] = []
    for direction in DIRECTIONS:
        for state, (frames, fps) in STATES.items():
            source = runtime / direction / f"{state}.png"
            target = output / "runtime" / direction / f"{state}.png"
            if not source.is_file():
                raise SystemExit(f"missing runtime atlas: {source}")
            with Image.open(source) as image:
                if image.mode != "RGBA" or image.size != (CELL, CELL * frames):
                    raise SystemExit(f"invalid runtime atlas: {source} {image.mode} {image.size}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if digest(source) != digest(target):
                raise SystemExit(f"preview runtime copy hash mismatch: {target}")
            entries.append({
                "direction": direction,
                "state": state,
                "frames": frames,
                "fps": fps,
                "source": source.relative_to(ROOT).as_posix(),
                "source_sha256": digest(source),
                "preview": target.relative_to(ROOT).as_posix(),
                "preview_sha256": digest(target),
            })
    manifest = {
        "schema": 2,
        "gate": "HOLD_DIAGNOSTIC_ONLY_NOT_GODOT_BEHAVIOR_PARITY",
        "role": f"portable MICA {args.revision} interactive-preview runtime bundle",
        "html": html_path.relative_to(ROOT).as_posix(),
        "html_sha256": digest(html_path),
        "descriptor": descriptor_path.relative_to(ROOT).as_posix(),
        "descriptor_sha256": digest(descriptor_path),
        "source_runtime_root": runtime.relative_to(ROOT).as_posix(),
        "runtime_root": (output / "runtime").relative_to(ROOT).as_posix(),
        "directions": list(DIRECTIONS),
        "entries": entries,
    }
    manifest_path = output / "MICA_C03_INTERACTIVE_RUNTIME_BUNDLE.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"gate": manifest["gate"], "preview": output.relative_to(ROOT).as_posix(), "entries": len(entries)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
