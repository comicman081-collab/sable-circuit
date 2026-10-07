#!/usr/bin/env python3
"""Make exact-green source/mask pairs and contacts for ASTER Idle/Move 360."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
GREEN = np.array((0, 255, 0), dtype=np.uint8)


def project_path(path: Path) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(f"path must remain inside project: {resolved}") from error
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_and_mask(raw: Path, source: Path, mask: Path, qa: Path) -> dict[str, object]:
    rgb = np.asarray(Image.open(raw).convert("RGB"))
    signed = rgb.astype(np.int16)
    # The renderer's controlled world is exact green. The slightly tolerant
    # test preserves antialiased dark edge pixels rather than clipping them.
    green_backdrop = (
        (signed[:, :, 1] >= signed[:, :, 0] + 35)
        & (signed[:, :, 1] >= signed[:, :, 2] + 35)
        & (np.max(np.abs(signed - GREEN.astype(np.int16)), axis=2) <= 64)
    )
    subject = ~green_backdrop
    coverage = float(subject.mean())
    if not 0.06 <= coverage <= 0.70:
        raise RuntimeError(f"mask coverage outside contract for {raw.name}: {coverage:.4f}")
    clean = rgb.copy()
    clean[~subject] = GREEN
    source.parent.mkdir(parents=True, exist_ok=True)
    mask.parent.mkdir(parents=True, exist_ok=True)
    qa.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(clean, "RGB").save(source)
    Image.fromarray((subject.astype(np.uint8) * 255), "L").save(mask)
    exact = float(np.all(clean[~subject] == GREEN, axis=1).mean())
    record = {
        "pass": exact == 1.0,
        "raw": raw.relative_to(ROOT).as_posix(),
        "source": source.relative_to(ROOT).as_posix(),
        "mask": mask.relative_to(ROOT).as_posix(),
        "exact_green_outside_ratio": exact,
        "subject_coverage": coverage,
        "source_sha256": sha256(source),
        "mask_sha256": sha256(mask),
    }
    qa.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    record["qa"] = qa.relative_to(ROOT).as_posix()
    return record


def contact(candidate: Path, state: str, keys: list[str], directions: list[str], records: dict[tuple[str, str], dict[str, object]], tile_size: int) -> str:
    preview = candidate / "previews"
    preview.mkdir(exist_ok=True)
    canvas = Image.new("RGB", (len(directions) * tile_size, len(keys) * tile_size), tuple(GREEN.tolist()))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for row, key in enumerate(keys):
        for col, direction in enumerate(directions):
            item = records[(direction, key)]
            image = Image.open(ROOT / item["source"]).convert("RGB").resize((tile_size, tile_size), Image.Resampling.LANCZOS)
            x, y = col * tile_size, row * tile_size
            canvas.paste(image, (x, y))
            draw.rectangle((x + 4, y + 4, x + min(tile_size - 4, 130), y + 20), fill=(0, 20, 18))
            draw.text((x + 7, y + 7), f"{direction} {key}", fill=(220, 255, 240), font=font)
    path = preview / f"ASTER_{state.upper()}_360_IMAGEGEN_MVP_CONTACT_GREEN.png"
    canvas.save(path)
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--tile", type=int, default=192)
    args = parser.parse_args()
    candidate = project_path(args.candidate)
    raw_manifest_path = candidate / "ASTER_IMAGEGEN_IDLE_MOVE_360_MVP_MANIFEST.json"
    output_manifest = candidate / "ASTER_IMAGEGEN_IDLE_MOVE_360_MVP_GREEN_MASK_MANIFEST.json"
    if output_manifest.exists():
        raise SystemExit("refusing to overwrite finalized Idle/Move manifest")
    raw_manifest = json.loads(raw_manifest_path.read_text(encoding="utf-8"))
    records = []
    for row in raw_manifest["raw_renders"]:
        state, direction, key = row["state"], row["direction"], row["key"]
        raw = ROOT / row["file"]
        stem = f"ASTER_{state.upper()}_{direction}_{key.upper()}"
        processed = source_and_mask(raw, candidate / "source" / state / direction / f"{stem}_GREEN.png", candidate / "masks" / state / direction / f"{stem}_MASK.png", candidate / "qa" / state / direction / f"{stem}_QA.json")
        records.append({**row, **processed})
    directions = raw_manifest["directions"]
    by_state = {}
    for state, keys in raw_manifest["states"].items():
        rows = [row for row in records if row["state"] == state]
        by_key = {(row["direction"], row["key"]): row for row in rows}
        if len(by_key) != len(directions) * len(keys):
            raise RuntimeError(f"missing direction/key coverage in {state}")
        by_state[state] = {
            "keys": keys,
            "record_count": len(rows),
            "contact": contact(candidate, state, keys, directions, by_key, args.tile),
        }
    manifest = {
        "schema": 1,
        "role": "ASTER Idle/Move 360 exact-green/mask source-art motion MVP; non-final",
        "source_background": "#00FF00",
        "directions": directions,
        "states": by_state,
        "records": records,
        "ual_source": raw_manifest["ual_source"],
        "ual_actions": raw_manifest["ual_actions"],
        "ual_role": raw_manifest["ual_role"],
        "e_move_visual_status": "four authored lower-body poses mapped across eight cadence keys",
        "other_direction_move_visual_status": raw_manifest["other_direction_move_policy"],
        "runtime_status": raw_manifest["runtime_status"],
        "visual_gate": "USER_REVIEW_REQUIRED",
    }
    output_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_IMAGEGEN_IDLE_MOVE_360_FINALIZE_PASS=" + json.dumps({"records": len(records), "contacts": {state: value["contact"] for state, value in by_state.items()}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
