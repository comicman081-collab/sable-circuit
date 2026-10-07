#!/usr/bin/env python3
"""Fetch only approved, immutable external assets for SABLE CIRCUIT.

Quaternius is intentionally opt-in because its Standard archives are large:
``python tools/fetch_external_assets.py --group quaternius``.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from prepare_quaternius_animation_glb import strip_mesh_from_glb

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "external" / "manifest.json"


def require_project_path(candidate: Path) -> Path:
    resolved = candidate.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as error:
        raise RuntimeError(f"asset cache must be inside {ROOT}: {resolved}") from error
    return resolved


DEFAULT_CACHE_ROOT = require_project_path(
    Path(os.environ.get("SABLE_CIRCUIT_ASSET_CACHE", ROOT / ".cache" / "external_assets"))
) / "quaternius"
USER_AGENT = "SABLE-CIRCUIT-asset-fetcher/1"
_ARCHIVE_MEMORY_CACHE: dict[str, bytes] = {}
PROHIBITED_MARKERS = (
    "universal base character",
    "base character",
    "mannequin",
    "character mesh",
    "character model",
    "premium",
    "patreon",
    "source .blend",
    "pro version",
    "paid",
)


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_metadata(asset: dict) -> None:
    required = ("id", "name", "origin", "license", "destination", "sha256", "redistribution_policy")
    missing = [key for key in required if not asset.get(key)]
    if missing:
        raise RuntimeError(f"FAIL-CLOSED {asset.get('id', '<unknown>')}: missing metadata: {', '.join(missing)}")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", str(asset["sha256"])):
        raise RuntimeError(f"FAIL-CLOSED {asset['id']}: invalid destination SHA-256")
    if asset.get("group") == "quaternius":
        for key in (
            "source_tier",
            "commercial_use",
            "official_upstream",
            "download_source",
            "immutable_download_source",
            "source_archive_name",
            "source_archive_size",
            "source_archive_sha256",
            "source_entry",
            "source_size",
            "source_sha256",
            "source_upload_id",
            "root_motion",
        ):
            if key not in asset or (asset[key] in (None, "", False) and key not in ("root_motion",)):
                raise RuntimeError(f"FAIL-CLOSED {asset['id']}: missing Quaternius metadata: {key}")
        if asset["source_tier"] != "Standard (Free)":
            raise RuntimeError(f"FAIL-CLOSED {asset['id']}: non-Standard tier")
        if asset["commercial_use"] is not True:
            raise RuntimeError(f"FAIL-CLOSED {asset['id']}: commercial use is not explicitly true")
        if asset["license"] != "CC0-1.0":
            raise RuntimeError(f"FAIL-CLOSED {asset['id']}: license is not CC0-1.0")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", str(asset["source_archive_sha256"])):
            raise RuntimeError(f"FAIL-CLOSED {asset['id']}: immutable archive hash missing/invalid")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", str(asset["source_sha256"])):
            raise RuntimeError(f"FAIL-CLOSED {asset['id']}: immutable source-file hash missing/invalid")
        if not re.fullmatch(r"[0-9a-fA-F]{40}", str(asset.get("git_blob_sha1", ""))):
            raise RuntimeError(f"FAIL-CLOSED {asset['id']}: immutable Git blob hash missing/invalid")
        combined = " ".join(str(asset.get(key, "")) for key in ("name", "source_tier", "source_archive_name", "source_entry", "destination")).lower()
        for marker in PROHIBITED_MARKERS:
            if marker in combined:
                raise RuntimeError(f"FAIL-CLOSED {asset['id']}: prohibited marker {marker!r}")
        if asset.get("character_asset") is True or asset.get("contains_character_mesh") is True:
            raise RuntimeError(f"FAIL-CLOSED {asset['id']}: character/base-model asset")


def fetch_direct(asset: dict, force: bool = False) -> None:
    destination = ROOT / asset["destination"]
    expected = asset["sha256"].lower()
    if destination.is_file() and sha256(destination) == expected and not force:
        print(f"EXTERNAL_ASSET: OK cached {asset['id']} -> {destination.relative_to(ROOT)}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=destination.parent) as tmp:
        temp_path = Path(tmp.name)
    try:
        request = urllib.request.Request(asset["origin"], headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=60) as response, temp_path.open("wb") as out:
            shutil.copyfileobj(response, out)
        actual = sha256(temp_path)
        if actual != expected:
            raise RuntimeError(f"SHA-256 mismatch for {asset['id']}: expected {expected}, got {actual}")
        temp_path.replace(destination)
        print(f"EXTERNAL_ASSET: PASS {asset['id']} sha256={actual} -> {destination.relative_to(ROOT)}")
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _read_response(opener: urllib.request.OpenerDirector, request: urllib.request.Request) -> bytes:
    with opener.open(request, timeout=120) as response:
        return response.read()


def _csrf_token(page: bytes) -> str:
    text = page.decode("utf-8", errors="replace")
    patterns = (
        r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)',
        r'value=["\']([^"\']+)["\'][^>]*name=["\']csrf_token["\']',
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return html.unescape(match.group(1))
    raise RuntimeError("FAIL-CLOSED: official itch.io CSRF token not found")


def _json_url(payload: bytes, context: str) -> str:
    data = json.loads(payload.decode("utf-8"))
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        for key in ("url", "download_url", "downloadUrl"):
            if data.get(key):
                return str(data[key])
    raise RuntimeError(f"FAIL-CLOSED: {context} did not return a download URL")


def _official_standard_upload(opener: urllib.request.OpenerDirector, asset: dict, signed_page: str) -> str:
    page = _read_response(opener, urllib.request.Request(signed_page, headers={"User-Agent": USER_AGENT, "Referer": asset["download_source"]}))
    text = page.decode("utf-8", errors="replace")
    expected_upload = str(asset["source_upload_id"])
    match = re.search(r"data-upload_id=[\"']" + re.escape(expected_upload) + r"[\"']", text, re.IGNORECASE)
    if not match:
        raise RuntimeError(f"FAIL-CLOSED: expected official Standard upload {expected_upload} was not found")
    context = html.unescape(re.sub(r"<[^>]+>", " ", text[max(0, match.start() - 500) : match.end() + 1000])).lower()
    if "standard" not in context or any(marker in context for marker in ("pro", "premium", "paid")):
        raise RuntimeError(f"FAIL-CLOSED: official upload {expected_upload} is not clearly Standard")
    return expected_upload


def download_quaternius_archive(asset: dict, cache_root: Path) -> bytes:
    cache_key = asset["source_archive_name"]
    if cache_key in _ARCHIVE_MEMORY_CACHE:
        return _ARCHIVE_MEMORY_CACHE[cache_key]
    download_source = asset["download_source"].rstrip("/")
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    opener.addheaders = [("User-Agent", USER_AGENT)]
    purchase_url = download_source + "/purchase"
    purchase_page = _read_response(opener, urllib.request.Request(purchase_url))
    csrf = _csrf_token(purchase_page)
    encoded = urllib.parse.urlencode({"csrf_token": csrf}).encode("ascii")
    signed_page = _json_url(
        _read_response(opener, urllib.request.Request(download_source + "/download_url", data=encoded, headers={"Referer": purchase_url, "Content-Type": "application/x-www-form-urlencoded"})),
        "download_url",
    )
    upload_id = _official_standard_upload(opener, asset, signed_page)
    file_url = download_source + f"/file/{upload_id}?source=view_game&as_props=1"
    file_payload = _read_response(
        opener,
        urllib.request.Request(file_url, data=encoded, headers={"Referer": signed_page, "Content-Type": "application/x-www-form-urlencoded"}),
    )
    archive_url = _json_url(file_payload, "official Standard file endpoint")
    archive = _read_response(opener, urllib.request.Request(archive_url, headers={"Referer": signed_page}))
    cache_root.mkdir(parents=True, exist_ok=True)
    # Keep the ZIP in memory only.  Standard packages can contain preview
    # mannequin/model files; no upstream archive is left in the asset cache.
    _ARCHIVE_MEMORY_CACHE[cache_key] = archive
    return archive


def fetch_quaternius(asset: dict, force: bool, cache_root: Path) -> None:
    destination = ROOT / asset["destination"]
    expected = asset["sha256"].lower()
    if destination.is_file() and sha256(destination) == expected and not force:
        print(f"EXTERNAL_ASSET: OK cached {asset['id']} -> {destination.relative_to(ROOT)}")
        return

    archive = download_quaternius_archive(asset, cache_root)
    archive_hash = sha256_bytes(archive)
    if len(archive) != int(asset["source_archive_size"]) or archive_hash.lower() != asset["source_archive_sha256"].lower():
        raise RuntimeError(f"FAIL-CLOSED {asset['id']}: official Standard archive size/SHA-256 mismatch")
    with zipfile.ZipFile(io.BytesIO(archive)) as package:
        names = set(package.namelist())
        source_entry = asset["source_entry"]
        if source_entry not in names:
            raise RuntimeError(f"FAIL-CLOSED {asset['id']}: approved source entry missing: {source_entry}")
        prohibited = [name for name in names if any(marker in name.lower() for marker in PROHIBITED_MARKERS) or name.lower().endswith((".blend", ".fbx"))]
        if prohibited:
            print(f"EXTERNAL_ASSET: INFO skipped {len(prohibited)} prohibited upstream package entries")
        source = package.read(source_entry)
    if len(source) != int(asset["source_size"]) or sha256_bytes(source).lower() != asset["source_sha256"].lower():
        raise RuntimeError(f"FAIL-CLOSED {asset['id']}: approved source GLB size/SHA-256 mismatch")

    source_path = cache_root / f"{asset['id']}.source.glb"
    derived_path = cache_root / f"{asset['id']}.derived.glb"
    destination_temp = None
    try:
        source_path.write_bytes(source)
        strip_mesh_from_glb(source_path, derived_path)
        if derived_path.stat().st_size != int(asset["expected_size"]) or sha256(derived_path).lower() != expected:
            raise RuntimeError(f"FAIL-CLOSED {asset['id']}: derived GLB size/SHA-256 mismatch")
        destination.parent.mkdir(parents=True, exist_ok=True)
        # An explicitly overridden cache and the repository can be on different
        # volumes, so use a same-filesystem temporary destination before the
        # final atomic replace.
        with tempfile.NamedTemporaryFile(delete=False, dir=destination.parent) as tmp:
            destination_temp = Path(tmp.name)
        shutil.copyfile(derived_path, destination_temp)
        destination_temp.replace(destination)
    finally:
        # The source GLB also contains the preview mannequin in the official
        # package.  It is a transient conversion input and is never retained.
        for temporary in (source_path, derived_path, destination_temp):
            if temporary is not None and temporary.exists():
                temporary.unlink()
    print(f"EXTERNAL_ASSET: PASS {asset['id']} sha256={expected} -> {destination.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch immutable external assets declared by SABLE CIRCUIT.")
    parser.add_argument("--id", action="append", dest="ids", help="Fetch only this stable asset id. Repeatable.")
    parser.add_argument("--group", action="append", dest="groups", help="Fetch only this asset group. Repeatable.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cache-root", type=Path, default=DEFAULT_CACHE_ROOT)
    args = parser.parse_args()

    manifest = load_manifest()
    assets = manifest.get("assets", [])
    wanted_ids = set(args.ids or [])
    wanted_groups = set(args.groups or [])
    known_ids = {a.get("id") for a in assets}
    known_groups = {a.get("group") for a in assets if a.get("group")}
    unknown_ids = wanted_ids.difference(known_ids)
    unknown_groups = wanted_groups.difference(known_groups)
    if unknown_ids or unknown_groups:
        if unknown_ids:
            print("Unknown external asset id(s): " + ", ".join(sorted(unknown_ids)), file=sys.stderr)
        if unknown_groups:
            print("Unknown external asset group(s): " + ", ".join(sorted(unknown_groups)), file=sys.stderr)
        return 2

    if not wanted_ids and not wanted_groups:
        # Large Quaternius archives are never part of the default CI/download path.
        selected = [a for a in assets if a.get("group") != "quaternius"]
    else:
        selected = [a for a in assets if a.get("id") in wanted_ids or a.get("group") in wanted_groups]

    try:
        for asset in selected:
            require_metadata(asset)
            if asset.get("group") == "quaternius":
                fetch_quaternius(asset, args.force, args.cache_root)
            else:
                fetch_direct(asset, args.force)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
