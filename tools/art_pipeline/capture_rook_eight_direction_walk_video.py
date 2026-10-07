#!/usr/bin/env python3
"""Render a native-1080p, eight-direction ROOK movement review MP4.

This is deterministic review evidence from the promoted runtime atlases; it
does not generate or interpolate art.  Each panel displays the actual 384px
runtime cell without upscaling so alternating support feet can be inspected.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
CELL = 384
FPS = 24
FRAMES = 24
WIDTH, HEIGHT = 1920, 1080


def inside_project(value: Path) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(f"project-local path required: {path}") from error
    return path


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/segoeuib.ttf") if bold else Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf") if bold else Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def load_atlases(
    runtime: Path,
    *,
    key_exact_green: bool = False,
    move_atlas_name: str = "move.png",
) -> dict[str, Image.Image]:
    atlases: dict[str, Image.Image] = {}
    for direction in DIRECTIONS:
        path = runtime / direction / move_atlas_name
        if not path.is_file():
            raise SystemExit(f"missing runtime movement atlas: {path}")
        atlas = Image.open(path).convert("RGBA")
        if atlas.size != (CELL, CELL * FRAMES):
            raise SystemExit(f"unexpected movement atlas size: {path} {atlas.size}")
        if key_exact_green:
            # Candidate evidence exists before the final runtime RGBA export.
            # Key the authoring contract in memory only; never rewrite the
            # candidate atlas or present the keyed image as source art.
            pixels = atlas.load()
            for y in range(atlas.height):
                for x in range(atlas.width):
                    red, green, blue, _alpha = pixels[x, y]
                    if (red, green, blue) == (0, 255, 0):
                        pixels[x, y] = (0, 255, 0, 0)
        atlases[direction] = atlas
    return atlases


def render_frame(atlases: dict[str, Image.Image], index: int, title: str) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#071019")
    draw = ImageDraw.Draw(image)
    title_font, label_font, small_font = font(30, True), font(20, True), font(16)
    draw.rectangle((0, 0, WIDTH, 76), fill="#0b1722")
    draw.text((50, 20), f"{title}  |  8-DIRECTION RUNTIME WALK", fill="#e7f7ff", font=title_font)
    draw.text((50, 90), "Actual 384px runtime cells • Frame sequence 00–23 • no interpolation / no upscale", fill="#9db9c9", font=small_font)
    progress = (index + 1) / FRAMES
    draw.rounded_rectangle((1450, 30, 1850, 48), radius=9, fill="#203141")
    draw.rounded_rectangle((1450, 30, 1450 + int(400 * progress), 48), radius=9, fill="#69dcff")
    draw.text((1450, 54), f"FRAME {index:02d} / 23", fill="#bcecff", font=small_font)

    positions = ((120, 145), (552, 145), (984, 145), (1416, 145), (120, 625), (552, 625), (984, 625), (1416, 625))
    for direction, (x, y) in zip(DIRECTIONS, positions, strict=True):
        draw.rounded_rectangle((x - 12, y - 12, x + CELL + 12, y + CELL + 46), radius=12, fill="#152432", outline="#33556b", width=2)
        cell = atlases[direction].crop((0, index * CELL, CELL, (index + 1) * CELL))
        image.paste(cell, (x, y), cell)
        draw.text((x, y + CELL + 10), f"{direction}  •  MOVE F{index:02d}", fill="#83ddff", font=label_font)

    draw.text((50, 1046), "Native 1920×1080 evidence. Each subject remains in its atlas cell to show the exact in-game leg cycle.", fill="#a6bac7", font=small_font)
    return image


def write_video(atlases: dict[str, Image.Image], output: Path, cycles: int, title: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing video: {output}")
    container = av.open(str(output), mode="w")
    stream = container.add_stream("libx264", rate=FPS)
    stream.width, stream.height, stream.pix_fmt = WIDTH, HEIGHT, "yuv420p"
    stream.options = {"crf": "18", "preset": "medium", "movflags": "+faststart"}
    try:
        for frame_number in range(FRAMES * cycles):
            canvas = render_frame(atlases, frame_number % FRAMES, title)
            video = av.VideoFrame.from_image(canvas)
            for packet in stream.encode(video):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    finally:
        container.close()


def inspect_video(path: Path, *, expected_frames: int = FRAMES * 4) -> dict[str, object]:
    container = av.open(str(path))
    stream = container.streams.video[0]
    decoded = sum(1 for _ in container.decode(stream))
    result = {
        "path": path.relative_to(ROOT).as_posix(),
        "codec": stream.codec_context.name,
        "resolution": [stream.codec_context.width, stream.codec_context.height],
        "fps": float(stream.average_rate),
        "decoded_frames": decoded,
    }
    container.close()
    if result["resolution"] != [WIDTH, HEIGHT] or decoded != expected_frames:
        raise SystemExit(f"encoded video validation failed: {result}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", default="assets/units/operators/rook/fast_runtime_v1/current", type=Path)
    parser.add_argument("--output", default="artifacts/rook_c02_v27_eight_direction_walk_video/ROOK_C02_V27_8_DIRECTION_WALK_1920X1080.mp4", type=Path)
    parser.add_argument("--title", default="ROOK C02")
    parser.add_argument("--cycles", type=int, default=4, help="complete 24fps gait cycles to encode")
    parser.add_argument("--key-exact-green", action="store_true", help="key project #00FF00 candidate atlases in memory for pre-promotion review")
    parser.add_argument("--move-atlas-name", default="move.png", help="per-direction movement atlas filename, e.g. move_green.png for a pre-promotion candidate")
    args = parser.parse_args()
    runtime, output = inside_project(args.runtime), inside_project(args.output)
    if args.cycles < 1:
        raise SystemExit("--cycles must be positive")
    if Path(args.move_atlas_name).name != args.move_atlas_name:
        raise SystemExit("--move-atlas-name must be a filename, not a path")
    atlases = load_atlases(
        runtime,
        key_exact_green=args.key_exact_green,
        move_atlas_name=args.move_atlas_name,
    )
    write_video(atlases, output, cycles=args.cycles, title=args.title)
    result = inspect_video(output, expected_frames=FRAMES * args.cycles)
    print(json.dumps({"gate": "PASS", **result, "key_exact_green_in_memory": args.key_exact_green}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
