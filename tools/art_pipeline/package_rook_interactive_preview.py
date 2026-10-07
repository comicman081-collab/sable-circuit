#!/usr/bin/env python3
"""Package the promoted ROOK runtime atlases beside the portable HTML preview.

The preview may be opened as ``file://`` by the Codex in-app browser, whose
local-file policy can reject references that traverse from ``artifacts`` into
the project's sibling ``assets`` directory.  This tool copies only the active
runtime atlas set into the project-local preview bundle and records hashes so
the preview cannot silently use an older candidate.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/units/operators/rook/fast_runtime_v1/current"
PREVIEW = ROOT / "artifacts/rook_c02_interactive_preview"
DESTINATION = PREVIEW / "runtime"
MANIFEST = PREVIEW / "ROOK_C02_INTERACTIVE_RUNTIME_MANIFEST.json"
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = {"idle": (4, 4.0), "move": (24, 24.0), "fire": (6, 12.0)}
CELL = 384


def project_path(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(f"path outside project: {resolved}") from error
    return resolved


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    project_path(SOURCE)
    project_path(PREVIEW)
    entries: list[dict[str, object]] = []
    for direction in DIRECTIONS:
        for state, (frames, fps) in STATES.items():
            source = SOURCE / direction / f"{state}.png"
            target = DESTINATION / direction / f"{state}.png"
            if not source.is_file():
                raise SystemExit(f"missing promoted runtime atlas: {source}")
            with Image.open(source) as image:
                if image.size != (CELL, CELL * frames) or image.mode != "RGBA":
                    raise SystemExit(f"invalid runtime atlas: {source} ({image.mode} {image.size})")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if digest(source) != digest(target):
                raise SystemExit(f"copy hash mismatch: {target}")
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

    payload = {
        "schema": 1,
        "role": "portable ROOK interactive-preview runtime bundle",
        "html": "artifacts/rook_c02_interactive_preview/ROOK_C02_INTERACTIVE_STRIDE_FIRE.html",
        "runtime_root": "artifacts/rook_c02_interactive_preview/runtime",
        "source_runtime_root": "assets/units/operators/rook/fast_runtime_v1/current",
        "directions": list(DIRECTIONS),
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"gate": "PASS", "entries": len(entries), "manifest": MANIFEST.relative_to(ROOT).as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
