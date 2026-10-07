#!/usr/bin/env python3
"""Render a five-second 1080p eight-direction walk and muzzle-alignment video."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
UNITS = {
    "E": (1.0, 0.0), "SE": (math.sqrt(0.5), math.sqrt(0.5)),
    "S": (0.0, 1.0), "SW": (-math.sqrt(0.5), math.sqrt(0.5)),
    "W": (-1.0, 0.0), "NW": (-math.sqrt(0.5), -math.sqrt(0.5)),
    "N": (0.0, -1.0), "NE": (math.sqrt(0.5), -math.sqrt(0.5)),
}
CELL, FPS, FRAME_COUNT = 384, 24, 120
WIDTH, HEIGHT = 1920, 1080


def inside_project(value: Path) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"project-local path required: {path}") from exc
    return path


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
    return ImageFont.truetype(path, size) if path.is_file() else ImageFont.load_default()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--descriptor", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title", default="CHARACTER")
    args = parser.parse_args()
    runtime = inside_project(args.runtime)
    descriptor_path = inside_project(args.descriptor)
    output = inside_project(args.output)
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing video: {output}")
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    atlases: dict[str, Image.Image] = {}
    for direction in DIRECTIONS:
        path = runtime / direction / "move.png"
        atlas = Image.open(path).convert("RGBA")
        if atlas.size != (CELL, CELL * 24):
            raise SystemExit(f"invalid movement atlas: {path} {atlas.size}")
        sockets = descriptor["directions"][direction].get("move_muzzle_xy")
        if not isinstance(sockets, list) or len(sockets) != 24:
            raise SystemExit(f"missing frame-indexed move sockets: {direction}")
        atlases[direction] = atlas

    output.parent.mkdir(parents=True, exist_ok=True)
    container = av.open(str(output), mode="w")
    stream = container.add_stream("libx264", rate=FPS)
    stream.width, stream.height, stream.pix_fmt = WIDTH, HEIGHT, "yuv420p"
    stream.options = {"crf": "18", "preset": "medium", "movflags": "+faststart"}
    positions = ((120, 145), (552, 145), (984, 145), (1416, 145), (120, 625), (552, 625), (984, 625), (1416, 625))
    title_font, label_font, small_font = font(29, True), font(18, True), font(15)
    try:
        for number in range(FRAME_COUNT):
            atlas_frame = number % 24
            pulse = number % 24
            canvas = Image.new("RGB", (WIDTH, HEIGHT), "#071019")
            draw = ImageDraw.Draw(canvas)
            draw.rectangle((0, 0, WIDTH, 76), fill="#0b1722")
            draw.text((50, 20), f"{args.title} | 8-DIRECTION WALK + FRAME MUZZLE ALIGNMENT", fill="#e7f7ff", font=title_font)
            draw.text((50, 91), "Actual 384px runtime cells • red socket = projectile birth • mint pulse = projectile", fill="#9db9c9", font=small_font)
            for direction, origin in zip(DIRECTIONS, positions, strict=True):
                x, y = origin
                draw.rounded_rectangle((x - 12, y - 12, x + CELL + 12, y + CELL + 46), radius=12, fill="#152432", outline="#33556b", width=2)
                cell = atlases[direction].crop((0, atlas_frame * CELL, CELL, (atlas_frame + 1) * CELL))
                canvas.paste(cell, origin, cell)
                socket = descriptor["directions"][direction]["move_muzzle_xy"][atlas_frame]
                sx, sy = x + float(socket[0]), y + float(socket[1])
                dx, dy = UNITS[direction]
                distance = 10.0 + pulse / 23.0 * 88.0
                px, py = sx + dx * distance, sy + dy * distance
                draw.ellipse((sx - 6, sy - 6, sx + 6, sy + 6), outline="#ff5252", width=3)
                draw.line((sx, sy, px, py), fill="#55bfae", width=3)
                draw.ellipse((px - 7, py - 7, px + 7, py + 7), outline="#7cf4e7", width=4)
                draw.text((x, y + CELL + 10), f"{direction} • MOVE F{atlas_frame:02d} • SOCKET [{socket[0]:.1f},{socket[1]:.1f}]", fill="#83ddff", font=label_font)
            draw.text((50, 1046), "Native 1920x1080, 24 fps, 5 seconds. No sprite upscale or interpolation.", fill="#a6bac7", font=small_font)
            frame = av.VideoFrame.from_image(canvas)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    finally:
        container.close()
        for atlas in atlases.values():
            atlas.close()

    check = av.open(str(output))
    video_stream = check.streams.video[0]
    decoded = sum(1 for _ in check.decode(video_stream))
    payload = {
        "gate": "PASS" if decoded == FRAME_COUNT else "FAIL",
        "path": output.relative_to(ROOT).as_posix(),
        "codec": video_stream.codec_context.name,
        "resolution": [video_stream.codec_context.width, video_stream.codec_context.height],
        "fps": float(video_stream.average_rate),
        "decoded_frames": decoded,
        "duration_seconds": decoded / FPS,
        "frame_indexed_muzzle_sockets": True,
    }
    check.close()
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
