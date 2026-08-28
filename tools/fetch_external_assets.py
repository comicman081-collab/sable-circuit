#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "external" / "manifest.json"


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha1(path: Path) -> str:
    size = path.stat().st_size
    h = hashlib.sha1()
    h.update(f"blob {size}\0".encode("ascii"))
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_asset_policy(asset: dict) -> None:
    asset_id = str(asset.get("id", "<missing-id>"))
    if not asset.get("origin") or not asset.get("destination"):
        raise RuntimeError(f"External asset {asset_id} is missing origin/destination")
    if not asset.get("sha256") and not asset.get("git_blob_sha1"):
        raise RuntimeError(f"External asset {asset_id} has no immutable content hash")

    if asset.get("group") == "quaternius":
        if asset.get("source_tier") != "Standard (Free)":
            raise RuntimeError(f"Quaternius asset {asset_id} is not approved Standard (Free)")
        if asset.get("license") != "CC0-1.0":
            raise RuntimeError(f"Quaternius asset {asset_id} is not CC0-1.0")
        if asset.get("commercial_use") is not True:
            raise RuntimeError(f"Quaternius asset {asset_id} does not explicitly allow commercial use")

        values = "\n".join(str(asset.get(k, "")) for k in ("name", "origin", "destination", "version"))
        banned_markers = ("[Pro]", "[Source]", "/Pro/", "/Source/", "\\Pro\\", "\\Source\\", ".blend")
        found = [marker for marker in banned_markers if marker.lower() in values.lower()]
        if found:
            raise RuntimeError(f"Quaternius asset {asset_id} contains forbidden paid/source marker(s): {found}")


def verify_file(path: Path, asset: dict) -> tuple[bool, list[str]]:
    problems: list[str] = []
    expected_size = asset.get("expected_size")
    if expected_size is not None and path.stat().st_size != int(expected_size):
        problems.append(f"size expected {expected_size}, got {path.stat().st_size}")

    expected_sha256 = str(asset.get("sha256", "")).lower()
    if expected_sha256:
        actual_sha256 = sha256(path)
        if actual_sha256 != expected_sha256:
            problems.append(f"sha256 expected {expected_sha256}, got {actual_sha256}")

    expected_blob = str(asset.get("git_blob_sha1", "")).lower()
    if expected_blob:
        actual_blob = git_blob_sha1(path)
        if actual_blob != expected_blob:
            problems.append(f"git-blob-sha1 expected {expected_blob}, got {actual_blob}")

    return not problems, problems


def fetch(asset: dict, force: bool = False) -> None:
    validate_asset_policy(asset)
    destination = ROOT / asset["destination"]

    if destination.is_file() and not force:
        ok, problems = verify_file(destination, asset)
        if ok:
            print(f"EXTERNAL_ASSET: OK cached {asset['id']} -> {destination.relative_to(ROOT)}")
            return
        print(f"EXTERNAL_ASSET: cached file invalid for {asset['id']}: {'; '.join(problems)}", file=sys.stderr)

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=destination.parent) as tmp:
        temp_path = Path(tmp.name)
    try:
        request = urllib.request.Request(asset["origin"], headers={"User-Agent": "SABLE-CIRCUIT-asset-fetcher/2"})
        with urllib.request.urlopen(request, timeout=180) as response, temp_path.open("wb") as out:
            shutil.copyfileobj(response, out)

        ok, problems = verify_file(temp_path, asset)
        if not ok:
            raise RuntimeError(f"Integrity mismatch for {asset['id']}: {'; '.join(problems)}")

        temp_path.replace(destination)
        digest = sha256(destination)
        print(
            f"EXTERNAL_ASSET: PASS {asset['id']} sha256={digest} "
            f"size={destination.stat().st_size} -> {destination.relative_to(ROOT)}"
        )
    finally:
        if temp_path.exists():
            temp_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch immutable external assets declared by SABLE CIRCUIT.")
    parser.add_argument("--id", action="append", dest="ids", help="Fetch only this stable asset id. Repeatable.")
    parser.add_argument("--group", action="append", dest="groups", help="Fetch a declared asset group, e.g. quaternius. Repeatable.")
    parser.add_argument("--all", action="store_true", help="Fetch every declared external asset.")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest()
    assets = manifest.get("assets", [])

    # Validate the entire manifest even when only the default small asset set is fetched.
    # This makes accidentally declaring a paid/non-commercial Quaternius asset a CI-visible failure.
    for asset in assets:
        validate_asset_policy(asset)

    wanted_ids = set(args.ids or [])
    wanted_groups = set(args.groups or [])
    known_ids = {str(a.get("id")) for a in assets}
    known_groups = {str(a.get("group")) for a in assets if a.get("group")}

    missing_ids = wanted_ids.difference(known_ids)
    if missing_ids:
        print("Unknown external asset id(s): " + ", ".join(sorted(missing_ids)), file=sys.stderr)
        return 2
    missing_groups = wanted_groups.difference(known_groups)
    if missing_groups:
        print("Unknown external asset group(s): " + ", ".join(sorted(missing_groups)), file=sys.stderr)
        return 2

    if args.all:
        selected = assets
    elif wanted_ids or wanted_groups:
        selected = [
            a for a in assets
            if str(a.get("id")) in wanted_ids or str(a.get("group")) in wanted_groups
        ]
    else:
        selected = [a for a in assets if a.get("fetch_by_default", True)]

    if not selected:
        print("No external assets selected.")
        return 0

    for asset in selected:
        fetch(asset, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
