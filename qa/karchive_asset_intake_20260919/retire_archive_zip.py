"""Verify the extracted kArchive library before removing its redundant ZIP."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json


ARCHIVE_ROOT = Path("C:/ai_asset/karchive/2026-09-19").resolve()
ZIP = ARCHIVE_ROOT / "all-6400.zip"
INVENTORY = ARCHIVE_ROOT / "inventory.json"
DOWNLOAD_RECEIPT = ARCHIVE_ROOT / "download_verification.json"
PROJECT_QA = Path(__file__).resolve().parent
LICENSE_COPY = PROJECT_QA / "bundled_LICENSE.txt"
RESULT = PROJECT_QA / "zip_retirement_20260924.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if ARCHIVE_ROOT != Path("C:/ai_asset/karchive/2026-09-19").resolve():
        raise RuntimeError("Unexpected archive root")
    if ZIP.resolve() != ARCHIVE_ROOT / "all-6400.zip" or ZIP.is_symlink():
        raise RuntimeError("Unexpected ZIP target")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    receipt = json.loads(DOWNLOAD_RECEIPT.read_text(encoding="utf-8"))
    if len(inventory) != 6400 or receipt["glb_count"] != 6400:
        raise RuntimeError("Model count mismatch")
    expected = {Path(row["local_path"]): row for row in inventory}
    actual = set((ARCHIVE_ROOT / "models").rglob("*.glb"))
    if set(expected) != actual:
        raise RuntimeError("Extracted file inventory mismatch")
    if sha256(LICENSE_COPY) != receipt["license_sha256"]:
        raise RuntimeError("Bundled license copy is missing or changed")
    with ZipFile(ZIP) as archive:
        members = {info.filename: info for info in archive.infolist()}
        if set(members) != {row["archive_member"] for row in inventory} | {"LICENSE.txt"}:
            raise RuntimeError("ZIP member inventory mismatch")
        if archive.read("LICENSE.txt") != LICENSE_COPY.read_bytes():
            raise RuntimeError("License copy differs from ZIP")
        for path, row in expected.items():
            info = members[row["archive_member"]]
            if info.file_size != row["bytes"] or f"{info.CRC:08x}" != row["zip_crc32"]:
                raise RuntimeError(f"Member metadata mismatch: {info.filename}")
    for path, row in expected.items():
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"Missing or linked extracted asset: {path}")
        if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
            raise RuntimeError(f"Extracted asset changed: {path}")
    if ZIP.stat().st_size != receipt["archive_bytes"] or sha256(ZIP) != receipt["archive_sha256"]:
        raise RuntimeError("ZIP differs from verified download")

    result = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "archive_path": str(ZIP),
        "archive_bytes": receipt["archive_bytes"],
        "archive_sha256": receipt["archive_sha256"],
        "extracted_glb_count": len(expected),
        "extracted_bytes": sum(row["bytes"] for row in inventory),
        "license_copy": str(LICENSE_COPY),
        "status": "VERIFIED_BEFORE_DELETION",
    }
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    ZIP.unlink()
    result["status"] = "ARCHIVE_DELETED_EXTRACTED_ASSETS_RETAINED"
    result["deleted_at_utc"] = datetime.now(timezone.utc).isoformat()
    result["zip_exists_after"] = ZIP.exists()
    result["extracted_glb_count_after"] = sum(1 for _ in (ARCHIVE_ROOT / "models").rglob("*.glb"))
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
