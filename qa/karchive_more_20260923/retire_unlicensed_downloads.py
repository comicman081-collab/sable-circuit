"""Retire only the unlicensed non-3D files captured in this audit manifest."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json


AUDIT = Path(__file__).resolve().parent
ASSETS = Path("C:/ai_asset/karchive/2026-09-23").resolve()
STAGE = (AUDIT / "tmp" / "downloads").resolve()
MANIFEST = AUDIT / "retirement_manifest.json"
RECEIPT = AUDIT / "retirement_result.json"


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            result.update(block)
    return result.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if Path(manifest["target_root"]).resolve() != ASSETS:
        raise RuntimeError("Asset root mismatch")
    if Path(manifest["staging_root"]).resolve() != STAGE:
        raise RuntimeError("Staging root mismatch")
    if ASSETS.name != "2026-09-23" or ASSETS.parent != Path("C:/ai_asset/karchive").resolve():
        raise RuntimeError("Unexpected asset directory")
    if not STAGE.is_relative_to(AUDIT):
        raise RuntimeError("Staging escaped audit directory")
    for root in (ASSETS, STAGE):
        if not root.is_dir() or root.is_symlink():
            raise RuntimeError(f"Missing or linked directory: {root}")

    expected = {Path(item["path"]): item for item in manifest["files"]}
    if len(expected) != manifest["file_count"]:
        raise RuntimeError("Duplicate manifest paths")
    actual = {path for root in (ASSETS, STAGE) for path in root.rglob("*") if path.is_file()}
    if actual != set(expected):
        raise RuntimeError("Directory inventory differs from retirement manifest")
    for path, item in expected.items():
        if path.is_symlink() or not any(path.resolve().is_relative_to(root) for root in (ASSETS, STAGE)):
            raise RuntimeError(f"Unsafe target: {path}")
        if path.stat().st_size != item["bytes"] or digest(path) != item["sha256"]:
            raise RuntimeError(f"Changed file: {path}")

    for path in sorted(expected):
        path.unlink()
    for root in (ASSETS, STAGE):
        for directory in sorted((path for path in root.rglob("*") if path.is_dir()), key=lambda p: len(p.parts), reverse=True):
            directory.rmdir()
        root.rmdir()
    result = {
        "retired_at_utc": datetime.now(timezone.utc).isoformat(),
        "deleted_file_count": len(expected),
        "deleted_bytes": sum(item["bytes"] for item in expected.values()),
        "asset_root_exists": ASSETS.exists(),
        "stage_root_exists": STAGE.exists(),
        "prior_3d_archive_touched": False,
    }
    RECEIPT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
