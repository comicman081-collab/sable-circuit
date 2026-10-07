#!/usr/bin/env python3
"""Finalize V16 with the shared V13 matte/QA implementation."""

from __future__ import annotations

import json
import os
from pathlib import Path

import finalize_aster_sse_v13_no_shoulder as base


PACKAGE = base.PACKAGE
INCOMING_DIR = PACKAGE / ".incoming_v16"
RAW = INCOMING_DIR / "ASTER_FIRE_SSE_DIRECTION_AIM_MASTER_IMAGEGEN_V16_NO_SHOULDER_GREEN_RAW.png"
MASTER = PACKAGE / "current/ASTER_FIRE_SSE_DIRECTION_AIM_MASTER_IMAGEGEN_V16_NO_SHOULDER_GREEN.png"
V13_CURRENT = PACKAGE / "current/ASTER_FIRE_SSE_DIRECTION_AIM_MASTER_IMAGEGEN_V13_NO_SHOULDER_GREEN.png"
V13_PREVIOUS = PACKAGE / "previous/ASTER_FIRE_SSE_DIRECTION_AIM_MASTER_IMAGEGEN_V13_NO_SHOULDER_GREEN.png"
V9_PREVIOUS = PACKAGE / "previous/ASTER_FIRE_SSE_DIRECTION_AIM_MASTER_IMAGEGEN_V9_GREEN_RAW.png"
OUT = PACKAGE / "qa_v16_no_shoulder"

V16_RAW_SHA = "cab232394797c05053106524f2cea6063a7b045c68c037d7410387a046e63b92"
V13_MASTER_SHA = "166f986ad77a36a1d78d828e46bfa7d0711bca89369673a977eaeb9d8a1e9185"
V9_PREVIOUS_SHA = "dd97036f7443c41e5e199f4ba4c261343d89d574963a798112580d0b3f930d4f"


def configure() -> None:
    base.RAW = RAW
    base.MASTER = MASTER
    base.PREVIOUS = V13_CURRENT
    base.OUT = OUT
    base.EXPECTED = {
        RAW: V16_RAW_SHA,
        V13_CURRENT: V13_MASTER_SHA,
        base.AUTHORITY: base.EXPECTED[base.AUTHORITY],
    }
    base.MASK_NAME = "ASTER_FIRE_SSE_V16_NO_SHOULDER_MASK.png"
    base.RGBA_NAME = "ASTER_FIRE_SSE_V16_NO_SHOULDER_RGBA.png"
    base.REVIEW_NAME = "ASTER_FIRE_SSE_V16_NO_SHOULDER_REVIEW_1920X1440.png"
    base.QA_NAME = "ASTER_FIRE_SSE_V16_NO_SHOULDER_QA.json"
    base.MANIFEST_NAME = "ASTER_FIRE_SSE_V16_NO_SHOULDER_MANIFEST.json"
    base.EVIDENCE_NAME = "ASTER_FIRE_SSE_V16_NO_SHOULDER_EVIDENCE_1080P_QA.json"
    base.CANDIDATE_LABEL = "V16"


def rotate_retention() -> None:
    for path, expected in (
        (MASTER, base.sha256(MASTER)),
        (V13_CURRENT, V13_MASTER_SHA),
        (V9_PREVIOUS, V9_PREVIOUS_SHA),
    ):
        if not path.is_file() or base.sha256(path) != expected:
            raise RuntimeError(f"retention input missing or hash mismatch: {path}")
    if V13_PREVIOUS.exists():
        raise RuntimeError(f"refusing previous overwrite: {V13_PREVIOUS}")

    V9_PREVIOUS.unlink()
    os.replace(V13_CURRENT, V13_PREVIOUS)

    manifest_path = OUT / base.MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["previous"] = {
        "path": base.rel(V13_PREVIOUS),
        "sha256": base.sha256(V13_PREVIOUS),
    }
    temporary = manifest_path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    json.loads(temporary.read_text(encoding="utf-8"))
    os.replace(temporary, manifest_path)
    if INCOMING_DIR.exists() and not any(INCOMING_DIR.iterdir()):
        INCOMING_DIR.rmdir()


def main() -> int:
    configure()
    result = base.main()
    if result != 0:
        return result
    rotate_retention()
    print(
        json.dumps(
            {
                "current": os.fspath(MASTER),
                "previous": os.fspath(V13_PREVIOUS),
                "retention": "PASS_CURRENT_PLUS_ONE_PREVIOUS",
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
