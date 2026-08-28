#!/usr/bin/env python3
"""Validate staged M7 authored-raster payloads without requiring image libraries.

Raster atlases are stored as ordered base64 text chunks so the repository can keep
binary generation separate from runtime code. A producer may upload incrementally;
a prefix that contains a valid RIFF/WebP header but is shorter than the RIFF-declared
file size is a legal *staged partial* and must remain quarantined by runtime code.
Malformed headers, invalid base64, non-contiguous chunk numbering, or payloads larger
than the declared RIFF size are repository-contract failures.
"""

from __future__ import annotations

import base64
import binascii
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RASTER_ROOT = ROOT / "assets" / "generated" / "raster"
IDENTITIES = ("aster", "rook", "mica")
CHUNK_RE = re.compile(r"^(?P<identity>[a-z0-9_]+)_direction_atlas\.webp\.b64\.(?P<index>\d+)$")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_identity(identity: str) -> None:
    directory = RASTER_ROOT / identity
    if not directory.is_dir():
        print(f"M7_RASTER_PAYLOAD {identity}: MISSING (vector fallback remains authoritative)")
        return

    entries: list[tuple[int, Path]] = []
    for path in directory.iterdir():
        if not path.is_file():
            continue
        match = CHUNK_RE.match(path.name)
        if match is None:
            fail(f"unexpected raster payload file for {identity}: {path.relative_to(ROOT)}")
        if match.group("identity") != identity:
            fail(f"raster chunk identity mismatch: {path.relative_to(ROOT)}")
        entries.append((int(match.group("index")), path))

    if not entries:
        print(f"M7_RASTER_PAYLOAD {identity}: MISSING (empty directory)")
        return

    entries.sort(key=lambda item: item[0])
    indexes = [index for index, _ in entries]
    expected_indexes = list(range(len(entries)))
    if indexes != expected_indexes:
        fail(f"{identity} raster chunks are not contiguous from 00: got {indexes}")

    encoded = "".join(path.read_text(encoding="utf-8").strip() for _, path in entries)
    if not encoded:
        fail(f"{identity} raster chunks are empty")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        fail(f"{identity} raster base64 is invalid: {exc}")

    if len(raw) < 12:
        fail(f"{identity} raster payload is too short for RIFF/WebP header: {len(raw)} bytes")
    if raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
        fail(f"{identity} raster payload does not have RIFF/WEBP signature")

    declared = int.from_bytes(raw[4:8], "little") + 8
    present = len(raw)
    if declared <= 12:
        fail(f"{identity} raster RIFF declares impossible size: {declared}")
    if present > declared:
        fail(f"{identity} raster exceeds RIFF-declared size: present={present} declared={declared}")

    if present < declared:
        missing = declared - present
        ratio = present / declared
        print(
            "M7_RASTER_PAYLOAD "
            f"{identity}: PARTIAL_QUARANTINED chunks={len(entries)} "
            f"encoded_chars={len(encoded)} present={present} declared={declared} "
            f"missing={missing} completion={ratio:.2%}"
        )
        return

    print(
        "M7_RASTER_PAYLOAD "
        f"{identity}: COMPLETE chunks={len(entries)} encoded_chars={len(encoded)} bytes={present}"
    )


def main() -> int:
    for identity in IDENTITIES:
        validate_identity(identity)
    print("M7_RASTER_PAYLOAD_VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
