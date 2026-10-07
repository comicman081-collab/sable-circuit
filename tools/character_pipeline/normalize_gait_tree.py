#!/usr/bin/env python3
"""Normalize every extracted gait cell below one project-local source tree."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NORMALIZER = Path(__file__).with_name("normalize_imagegen_walk_green.py")


def project_path(value: Path) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"source root must remain inside project: {path}") from exc
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--art-prefix", required=True)
    args = parser.parse_args()
    source_root = project_path(args.source_root)
    inputs = sorted(source_root.rglob(f"{args.art_prefix}_*_GAIT_F??_IMAGEGEN_GREEN.png"))
    if not inputs:
        raise SystemExit(f"no extracted gait cells found beneath {source_root}")
    completed = 0
    for source in inputs:
        output_dir = source.parent / "normalized"
        stem = source.stem
        targets = {
            "output": output_dir / f"{stem}_EXACT_GREEN.png",
            "mask": output_dir / f"{stem}_MASK.png",
            "qa": output_dir / f"{stem}_NORMALIZATION_QA.json",
        }
        if all(path.is_file() for path in targets.values()):
            completed += 1
            continue
        if any(path.exists() for path in targets.values()):
            raise SystemExit(f"partial normalization output exists for {source}")
        subprocess.run(
            [
                sys.executable,
                str(NORMALIZER),
                "--input",
                str(source),
                "--output",
                str(targets["output"]),
                "--mask",
                str(targets["mask"]),
                "--qa",
                str(targets["qa"]),
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        completed += 1
    print(f"GAIT_TREE_NORMALIZE_PASS={{\"cells\":{completed}}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
