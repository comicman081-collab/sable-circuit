#!/usr/bin/env python3
"""Transcode the deterministic Godot acceptance AVI to a compact MP4.

The source and destination must both live under the SABLE project.  Output is
written atomically, decoded again, and accepted only when every input frame was
written at the original resolution.  The wrapper removes the large AVI only
after this verifier succeeds.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[2]
MIN_REVIEW_RESOLUTION = (1920, 1080)


def inside_project(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"refusing path outside project: {resolved}") from exc
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()

    source = inside_project(Path(args.source))
    destination = inside_project(Path(args.destination))
    if not source.is_file() or source.stat().st_size <= 0:
        raise SystemExit(f"missing or empty source AVI: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_name(destination.stem + ".staging.mp4")
    if staging.exists():
        staging.unlink()

    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise SystemExit(f"OpenCV could not open {source}")
    width = int(round(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
    height = int(round(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    declared_frames = int(round(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
    if width <= 0 or height <= 0 or fps <= 0.0:
        capture.release()
        raise SystemExit("invalid AVI metadata")
    if width < MIN_REVIEW_RESOLUTION[0] or height < MIN_REVIEW_RESOLUTION[1]:
        capture.release()
        raise SystemExit(
            f"global 1080p gate failed: {(width, height)} < {MIN_REVIEW_RESOLUTION}"
        )

    writer = cv2.VideoWriter(
        str(staging),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        capture.release()
        raise SystemExit("OpenCV mp4v writer unavailable")

    written = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if frame.shape[1] != width or frame.shape[0] != height:
            writer.release()
            capture.release()
            staging.unlink(missing_ok=True)
            raise SystemExit(f"resolution drift at frame {written}")
        writer.write(frame)
        written += 1
    writer.release()
    capture.release()

    if written <= 0 or (declared_frames > 0 and written != declared_frames):
        staging.unlink(missing_ok=True)
        raise SystemExit(f"frame count mismatch: declared={declared_frames} written={written}")

    verify = cv2.VideoCapture(str(staging))
    verify_frames = int(round(verify.get(cv2.CAP_PROP_FRAME_COUNT))) if verify.isOpened() else 0
    verify_width = int(round(verify.get(cv2.CAP_PROP_FRAME_WIDTH))) if verify.isOpened() else 0
    verify_height = int(round(verify.get(cv2.CAP_PROP_FRAME_HEIGHT))) if verify.isOpened() else 0
    ok, first = verify.read() if verify.isOpened() else (False, None)
    verify.release()
    if not ok or first is None or verify_frames != written or (verify_width, verify_height) != (width, height):
        staging.unlink(missing_ok=True)
        raise SystemExit("staged MP4 decode verification failed")

    os.replace(staging, destination)
    print(json.dumps({
        "result": "PASS",
        "source": str(source),
        "destination": str(destination),
        "resolution": [width, height],
        "native_1080p_gate": "PASS",
        "fps": fps,
        "frames": written,
        "duration_seconds": written / fps,
        "file_size": destination.stat().st_size,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
