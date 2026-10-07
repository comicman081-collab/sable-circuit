#!/usr/bin/env python3
"""Extract an evenly sampled native-1080p contact sheet from a local video."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
CANVAS = (1920, 1080)
SAMPLES = 12


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("C:/Users/AAA/Videos/화면 녹화/화면 녹화 중 2026-09-02 171107.mp4"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    source = args.input.resolve()
    output = (ROOT / args.output).resolve() if not args.output.is_absolute() else args.output.resolve()
    report = (ROOT / args.report).resolve() if not args.report.is_absolute() else args.report.resolve()
    output.relative_to(ROOT); report.relative_to(ROOT)
    container = av.open(str(source))
    stream = container.streams.video[0]
    fps = float(stream.average_rate) if stream.average_rate else 30.0
    duration = float(stream.duration * stream.time_base) if stream.duration is not None else float(container.duration / av.time_base)
    if duration <= 0:
        raise SystemExit("video duration is unavailable")
    estimated_frames = max(1, round(duration * fps))
    times = [index * max(0.0, duration - 0.05) / (SAMPLES - 1) for index in range(SAMPLES)]
    frames: list[Image.Image] = []
    indices: list[int] = []
    for timestamp in times:
        container.seek(int(timestamp * av.time_base), backward=True, any_frame=False)
        chosen = None
        for frame in container.decode(video=0):
            chosen = frame
            if frame.time is None or float(frame.time) >= timestamp:
                break
        if chosen is None:
            raise SystemExit(f"failed to decode sample at {timestamp:.3f}s")
        frames.append(chosen.to_image().convert("RGB"))
        indices.append(min(estimated_frames - 1, round(timestamp * fps)))
    container.close()
    canvas = Image.new("RGB", CANVAS, "#071019")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((30, 18), f"USER VIDEO FRAME REVIEW · {source.name}", fill="#E7F7FF", font=font)
    panel_w, panel_h = 480, 330
    for sample_index, (frame_index, sampled_frame) in enumerate(zip(indices, frames, strict=True)):
        frame = sampled_frame.copy()
        frame.thumbnail((panel_w, panel_h - 26), Image.Resampling.LANCZOS)
        col, row = sample_index % 4, sample_index // 4
        left, top = col * panel_w, 54 + row * panel_h
        x = left + (panel_w - frame.width) // 2
        y = top + (panel_h - 26 - frame.height) // 2
        canvas.paste(frame, (x, y))
        draw.text((left + 10, top + panel_h - 22), f"sample {sample_index:02d} · frame {frame_index:04d}", fill="#7CF4E7", font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)
    payload = {
        "schema": 1,
        "input": str(source),
        "input_sha256": digest(source),
        "source_resolution": [stream.codec_context.width, stream.codec_context.height],
        "fps": fps,
        "duration_seconds": duration,
        "estimated_frames": estimated_frames,
        "sample_indices": indices,
        "output": output.relative_to(ROOT).as_posix(),
        "output_resolution": list(CANVAS),
    }
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
