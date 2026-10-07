#!/usr/bin/env python3
"""Composite isolated Blender+UAL plates without transparent-depth overlap.

Each plate is rendered by Blender on its own.  This finalizer only performs
straight-alpha ordering and deterministic chroma-edge cleanup; it does not
author, repaint, or deform any source-art pixels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]


def project_path(value: str, label: str) -> Path:
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain below the project root: {path}") from exc
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cleaned_rgba(path: Path) -> Image.Image:
    with Image.open(path) as opened:
        rgba = np.asarray(opened.convert("RGBA"), dtype=np.uint8).copy()
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]
    values = rgb.astype(np.int16)
    red, green, blue = values[:, :, 0], values[:, :, 1], values[:, :, 2]

    # Remove only unmistakable chroma-key residue.  Cyan costume lights are
    # preserved because their green and blue channels remain close together.
    strong_chroma = (
        (alpha > 0)
        & (green >= 150)
        & ((green - red) >= 75)
        & ((green - blue) >= 75)
    )
    alpha[strong_chroma] = 0

    # Neutralize the one-pixel green spill band that survives filtered alpha.
    spill = (
        (alpha > 0)
        & (green >= 32)
        & ((green - red) >= 8)
        & ((green - blue) >= 8)
    )
    alpha[spill] = 0
    alpha[alpha <= 8] = 0
    rgb[alpha == 0] = 0
    return Image.fromarray(rgba, "RGBA")


def frame_metrics(image: Image.Image) -> dict[str, object]:
    rgba = np.asarray(image, dtype=np.uint8)
    alpha = rgba[:, :, 3]
    rgb = rgba[:, :, :3]
    visible = alpha > 0
    opaque_black = visible & (alpha >= 250) & np.all(rgb <= 3, axis=2)
    values = rgb.astype(np.int16)
    strong_chroma = (
        visible
        & (values[:, :, 1] >= 150)
        & ((values[:, :, 1] - values[:, :, 0]) >= 75)
        & ((values[:, :, 1] - values[:, :, 2]) >= 75)
    )
    ys, xs = np.nonzero(visible)
    bbox = [] if len(xs) == 0 else [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    return {
        "visible_pixel_count": int(np.count_nonzero(visible)),
        "opaque_pure_black_pixel_count": int(np.count_nonzero(opaque_black)),
        "visible_strong_chroma_pixel_count": int(np.count_nonzero(strong_chroma)),
        "visible_bbox_xyxy": bbox,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-manifest", required=True)
    args = parser.parse_args()

    render_manifest_path = project_path(args.render_manifest, "render manifest")
    render_manifest = json.loads(render_manifest_path.read_text(encoding="utf-8"))
    direction = str(render_manifest.get("direction", "E")).upper()
    candidate_root = render_manifest_path.parent
    output_root = candidate_root / "blender_frames" / direction / "move"
    output_root.mkdir(parents=True, exist_ok=True)

    upper_entry = render_manifest["upper_component"]
    upper_path = project_path(upper_entry["path"], "upper component")
    if sha256(upper_path) != upper_entry["sha256"]:
        raise SystemExit("upper component hash mismatch")
    upper = cleaned_rgba(upper_path)

    finalized_frames: list[dict[str, object]] = []
    for entry in render_manifest["frames"]:
        layers: list[tuple[float, str, Image.Image]] = []
        if "phase_component" in entry:
            name = str(entry["phase_key"])
            component = entry["phase_component"]
            component_path = project_path(component["path"], f"{name} component")
            if sha256(component_path) != component["sha256"]:
                raise SystemExit(f"{name} component hash mismatch: {component_path}")
            layers.append((0.2, name, cleaned_rgba(component_path)))
        else:
            for name, component in entry["components"].items():
                component_path = project_path(component["path"], f"{name} component")
                if sha256(component_path) != component["sha256"]:
                    raise SystemExit(f"{name} component hash mismatch: {component_path}")
                depth = float(entry["legs"][name]["render_depth"])
                layers.append((depth, name, cleaned_rgba(component_path)))
        layers.sort(key=lambda item: (item[0], item[1]))

        composite = Image.new("RGBA", upper.size, (0, 0, 0, 0))
        layer_order: list[str] = []
        for _depth, name, layer in layers:
            composite = Image.alpha_composite(composite, layer)
            layer_order.append(name)
        composite = Image.alpha_composite(composite, upper)
        layer_order.append("upper_fixed")
        output_path = output_root / f"{int(entry['index']):02d}.png"
        composite.save(output_path, optimize=True)
        metrics = frame_metrics(composite)
        if metrics["visible_strong_chroma_pixel_count"] != 0:
            raise SystemExit(f"visible chroma remained in {output_path}")
        finalized_frames.append(
            {
                "index": int(entry["index"]),
                "path": output_path.relative_to(ROOT).as_posix(),
                "sha256": sha256(output_path),
                "layer_order_back_to_front": layer_order,
                "metrics": metrics,
            }
        )

    manifest = {
        "schema": 1,
        "role": f"MICA C03 {direction} isolated Blender+UAL straight-alpha finalization",
        "direction": direction,
        "candidate_status": "UNREVIEWED_DO_NOT_PROMOTE",
        "source_art_modified": False,
        "motion_source": (
            "Blender discrete immutable ImageGen phase plates with UAL cadence"
            if any("phase_component" in entry for entry in render_manifest["frames"])
            else "Blender isolated rigid leg plates with UAL cadence"
        ),
        "compositing": "separate plate renders; deterministic straight-alpha back-to-front",
        "edge_cleanup": "strong chroma removal plus guarded green spill clamp",
        "render_manifest": render_manifest_path.relative_to(ROOT).as_posix(),
        "render_manifest_sha256": sha256(render_manifest_path),
        "frames": finalized_frames,
    }
    manifest_path = candidate_root / f"MICA_C03_{direction}_ISOLATED_LOWER_UAL_FINALIZE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
