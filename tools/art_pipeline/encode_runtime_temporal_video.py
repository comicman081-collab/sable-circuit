#!/usr/bin/env python3
"""Encode native runtime PNG evidence into a review video.

The PNGs are captured directly from Godot's 1920x1080 viewport.  This helper
only encodes those original frames; it never resizes a low-resolution movie.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import av
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
MIN_WIDTH = 1920
MIN_HEIGHT = 1080


def project_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve()
    resolved.relative_to(ROOT)
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def natural_key(path: Path) -> tuple[object, ...]:
    return tuple(int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", required=True, help="project-relative PNG frame directory")
    parser.add_argument("--output", required=True, help="project-relative MP4 output")
    parser.add_argument("--manifest", required=True, help="project-relative encoding manifest")
    parser.add_argument("--evidence", required=True, help="project-relative Godot temporal evidence JSON")
    parser.add_argument("--fps", type=int, default=24)
    args = parser.parse_args()

    frame_dir = project_path(args.frames)
    output = project_path(args.output)
    manifest_path = project_path(args.manifest)
    evidence_path = project_path(args.evidence)
    frames = sorted(frame_dir.glob("*.png"), key=natural_key)
    failures: list[str] = []
    width = height = 0
    if not frames:
        failures.append("no PNG frames found")
    else:
        try:
            with Image.open(frames[0]) as image:
                width, height = image.size
            if (width, height) != (MIN_WIDTH, MIN_HEIGHT):
                failures.append(f"first frame is {width}x{height}, expected {MIN_WIDTH}x{MIN_HEIGHT}")
        except Exception as exc:  # fail closed while retaining diagnostics
            failures.append(f"first frame decode failed: {type(exc).__name__}: {exc}")

    output.parent.mkdir(parents=True, exist_ok=True)
    encoded_count = 0
    if not failures:
        try:
            container = av.open(str(output), mode="w")
            stream = container.add_stream("libx264", rate=args.fps)
            stream.width = width
            stream.height = height
            stream.pix_fmt = "yuv420p"
            stream.options = {"crf": "18", "preset": "medium"}
            for index, path in enumerate(frames):
                with Image.open(path) as image:
                    rgb = np.asarray(image.convert("RGB"))
                if tuple(rgb.shape[:2]) != (height, width):
                    failures.append(f"frame {index} has shape {tuple(rgb.shape[:2])}")
                    break
                video_frame = av.VideoFrame.from_ndarray(rgb, format="rgb24")
                video_frame.pts = index
                video_frame.time_base = Fraction(1, args.fps)
                for packet in stream.encode(video_frame):
                    container.mux(packet)
                encoded_count += 1
            for packet in stream.encode():
                container.mux(packet)
            container.close()
        except Exception as exc:  # fail closed and preserve a diagnostic manifest
            failures.append(f"video encode failed: {type(exc).__name__}: {exc}")
            try:
                container.close()
            except Exception:
                pass

    evidence: dict[str, object] = {}
    if evidence_path.is_file():
        try:
            parsed = json.loads(evidence_path.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                evidence = parsed
        except Exception as exc:
            failures.append(f"evidence JSON parse failed: {type(exc).__name__}: {exc}")

    result = "PASS" if not failures and encoded_count == len(frames) and frames else "FAIL"
    report = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "encoder": "PyAV/libx264 from native Godot viewport PNGs",
        "source_frame_directory": str(frame_dir),
        "source_frame_count": len(frames),
        "encoded_frame_count": encoded_count,
        "resolution": [width, height],
        "fps": args.fps,
        "duration_seconds": (float(len(frames)) / args.fps) if args.fps else 0.0,
        "source_frames_native_1080p": bool(width >= MIN_WIDTH and height >= MIN_HEIGHT),
        "source_frame_sha256": [sha256(path) for path in frames] if result == "PASS" else [],
        "output_video": str(output),
        "output_sha256": sha256(output) if output.is_file() and output.stat().st_size > 0 else "",
        "evidence_json": str(evidence_path),
        "segments": evidence.get("segments", []),
        "failure_details": failures,
        "promotion": evidence.get("promotion", "CAPTURE_ONLY_HOLD"),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
