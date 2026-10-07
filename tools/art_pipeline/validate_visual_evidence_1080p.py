#!/usr/bin/env python3
"""Fail closed when current SABLE visual evidence is below native 1080p.

This gate validates review containers, not source-art quality.  It deliberately
does not treat a large container as proof that a small source was authored at a
large resolution; callers must record source/runtime resolution and scaling in
their own manifest as required by the global visual-evidence contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
MIN_WIDTH = 1920
MIN_HEIGHT = 1080
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_SUFFIXES = {".avi", ".mp4", ".mov", ".mkv", ".webm"}


def inside_project(value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"refusing evidence outside project: {resolved}") from exc
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_image(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        width, height = image.size
        mode = image.mode
    return {
        "kind": "image",
        "evidence_class": "dynamic_or_authored_review_frame",
        "resolution": [width, height],
        "mode": mode,
        "decodable": True,
        "native_1080p_container": width >= MIN_WIDTH and height >= MIN_HEIGHT,
    }


def inspect_video(path: Path) -> dict[str, object]:
    try:
        import cv2
    except ImportError:
        cv2 = None

    if cv2 is not None:
        capture = cv2.VideoCapture(str(path))
        if not capture.isOpened():
            raise RuntimeError("OpenCV could not open video")
        width = int(round(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
        height = int(round(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        # MediaRecorder WebM can report a 1000Hz timebase as FPS and an
        # invented frame count, and has no reliable seek index. Decode all
        # frames forward instead of using that metadata as decoding evidence.
        shapes, timestamps = [], []
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            shapes.append(bool(frame is not None and frame.shape[:2] == (height, width)))
            timestamps.append(float(capture.get(cv2.CAP_PROP_POS_MSEC)))
        frames = len(shapes)
        if len(timestamps)>1 and timestamps[-1]>timestamps[0]:
            fps = (frames-1)*1000/(timestamps[-1]-timestamps[0])
        sample_indices = sorted({0, max(0, frames // 4), max(0, frames // 2), max(0, (frames * 3) // 4), max(0, frames - 1)})
        samples = [{"frame_index":i,"decoded_at_reported_resolution":bool(frames>i and shapes[i])} for i in sample_indices]
        if shapes and not all(shapes):
            samples.append({"frame_index":shapes.index(False),"decoded_at_reported_resolution":False})
        capture.release()
        decoder = "opencv"
    else:
        # PyAV is bundled in this workspace even where OpenCV is absent.  It
        # validates the same container/decoder facts without downloading a
        # second video stack merely for an evidence check.
        try:
            import av
        except ImportError as exc:
            raise SystemExit("OpenCV or PyAV is required to validate video evidence") from exc
        container = av.open(str(path))
        try:
            stream = container.streams.video[0]
            width, height = stream.codec_context.width, stream.codec_context.height
            fps = float(stream.average_rate) if stream.average_rate else 0.0
            decoded_shapes = [(frame.width, frame.height) for frame in container.decode(stream)]
        finally:
            container.close()
        frames = len(decoded_shapes)
        sample_indices = sorted({0, max(0, frames // 4), max(0, frames // 2), max(0, (frames * 3) // 4), max(0, frames - 1)})
        samples = [
            {
                "frame_index": frame_index,
                "decoded_at_reported_resolution": bool(
                    frames > frame_index and decoded_shapes[frame_index] == (width, height)
                ),
            }
            for frame_index in sample_indices
        ]
        decoder = "pyav"
    decodable = bool(frames > 0 and samples and all(sample["decoded_at_reported_resolution"] for sample in samples))
    return {
        "kind": "video",
        "evidence_class": "dynamic_capture",
        "decoder": decoder,
        "resolution": [width, height],
        "fps": fps,
        "frames": frames,
        "decode_samples": samples,
        "decodable": decodable,
        "native_1080p_container": width >= MIN_WIDTH and height >= MIN_HEIGHT,
    }


def inspect_html(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    canvases = [
        [int(width), int(height)]
        for width, height in re.findall(
            r"<canvas\b[^>]*\bwidth=[\"'](\d+)[\"'][^>]*\bheight=[\"'](\d+)[\"']",
            text,
            flags=re.IGNORECASE,
        )
    ]
    videos = [
        [int(width), int(height)]
        for width, height in re.findall(
            r"<video\b[^>]*\bwidth=[\"'](\d+)[\"'][^>]*\bheight=[\"'](\d+)[\"']",
            text,
            flags=re.IGNORECASE,
        )
    ]
    surfaces = canvases + videos
    accepted = bool(surfaces) and all(
        width >= MIN_WIDTH and height >= MIN_HEIGHT for width, height in surfaces
    )
    return {
        "kind": "html",
        "evidence_class": "static_config_only",
        "canvas_resolutions": canvases,
        "video_element_resolutions": videos,
        "decodable": bool(surfaces),
        "native_1080p_container": accepted,
        "dynamic_runtime_evidence": False,
        "dynamic_capture_required_for_visual_gate": True,
    }


def inspect(path: Path) -> dict[str, object]:
    if not path.is_file() or path.stat().st_size <= 0:
        return {"kind": "missing", "decodable": False, "native_1080p_container": False}
    suffix = path.suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        result = inspect_image(path)
    elif suffix in VIDEO_SUFFIXES:
        result = inspect_video(path)
    elif suffix in {".html", ".htm"}:
        result = inspect_html(path)
    else:
        return {"kind": "unsupported", "decodable": False, "native_1080p_container": False}
    result.update({"size_bytes": path.stat().st_size, "sha256": sha256(path)})
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", nargs="+", help="project-relative image, video, or HTML paths")
    parser.add_argument("--output", help="optional project-relative JSON report path")
    parser.add_argument(
        "--require-dynamic-capture",
        action="store_true",
        help="fail unless at least one native 1080p image/video capture is supplied; HTML is config-only",
    )
    args = parser.parse_args()

    records: list[dict[str, object]] = []
    for value in args.evidence:
        path = inside_project(value)
        try:
            detail = inspect(path)
            error = None
        except Exception as exc:  # fail closed while retaining diagnostics
            detail = {"kind": "error", "decodable": False, "native_1080p_container": False}
            error = f"{type(exc).__name__}: {exc}"
        records.append({"path": str(path), "error": error, **detail})

    container_gate = all(
        record.get("decodable") is True
        and record.get("native_1080p_container") is True
        for record in records
    )
    dynamic_records = [
        record for record in records if record.get("kind") in {"image", "video"}
    ]
    dynamic_capture_gate = bool(dynamic_records) and all(
        record.get("decodable") is True
        and record.get("native_1080p_container") is True
        for record in dynamic_records
    )
    gate = container_gate and (
        dynamic_capture_gate if args.require_dynamic_capture else True
    )
    html_only = bool(records) and all(record.get("kind") == "html" for record in records)
    if gate and html_only:
        gate_label = "PASS_STATIC_CONFIG_ONLY"
    else:
        gate_label = "PASS" if gate else "FAIL"
    report = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate": gate_label,
        "container_gate": "PASS" if container_gate else "FAIL",
        "dynamic_capture_gate": (
            "PASS" if dynamic_capture_gate else "NOT_PROVIDED" if not dynamic_records else "FAIL"
        ),
        "dynamic_capture_required": args.require_dynamic_capture,
        "minimum_native_review_resolution": [MIN_WIDTH, MIN_HEIGHT],
        "scope": "review_container_resolution_and_decode_only",
        "quality_claim": False,
        "anti_upscale_note": (
            "A PASS proves only a native-size review container. Source/master/runtime "
            "resolution and any scaling remain mandatory in the producing manifest."
        ),
        "evidence": records,
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = inside_project(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = output.with_suffix(output.suffix + ".tmp")
        staging.write_text(payload, encoding="utf-8")
        staging.replace(output)
    print(payload, end="")
    return 0 if gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
