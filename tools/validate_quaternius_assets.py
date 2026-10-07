#!/usr/bin/env python3
"""Fail-closed validation for the approved Quaternius animation-only GLBs."""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "external" / "manifest.json"
QUATERNIUS_ROOT = ROOT / "assets" / "external" / "quaternius"
REQUIRED_IDS = (
    "QUATERNIUS_UAL1_STANDARD",
    "QUATERNIUS_UAL1_STANDARD_RM",
    "QUATERNIUS_UAL2_STANDARD",
    "QUATERNIUS_UAL2_STANDARD_RM",
)
PROHIBITED_MARKERS = ("base character", "mannequin", "premium", "patreon", "pro", "source", "paid")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def parse_glb(path: Path) -> tuple[dict, bytes]:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise RuntimeError(f"{path}: GLB magic is not glTF")
    version, declared_length = struct.unpack_from("<II", data, 4)
    if version != 2:
        raise RuntimeError(f"{path}: expected GLB version 2, got {version}")
    if declared_length != len(data):
        raise RuntimeError(f"{path}: declared {declared_length} bytes, actual {len(data)}")
    offset = 12
    document = None
    binary = None
    while offset < len(data):
        if offset + 8 > len(data):
            raise RuntimeError(f"{path}: truncated chunk header")
        chunk_length, chunk_type = struct.unpack_from("<I4s", data, offset)
        offset += 8
        chunk = data[offset : offset + chunk_length]
        if len(chunk) != chunk_length:
            raise RuntimeError(f"{path}: truncated chunk")
        if chunk_type == b"JSON":
            document = json.loads(chunk.rstrip(b" \t\r\n").decode("utf-8"))
        elif chunk_type == b"BIN\x00":
            binary = chunk
        offset += chunk_length
    if not isinstance(document, dict) or binary is None:
        raise RuntimeError(f"{path}: JSON/BIN chunks are incomplete")
    return document, binary


def validate_asset(asset: dict) -> tuple[str, list[str]]:
    destination = ROOT / asset["destination"]
    if not destination.is_file():
        raise RuntimeError(f"{asset['id']}: missing {destination}")
    data = destination.read_bytes()
    if len(data) != asset["expected_size"]:
        raise RuntimeError(f"{asset['id']}: size {len(data)} != expected {asset['expected_size']}")
    digest = sha256(data)
    if digest.lower() != asset["sha256"].lower():
        raise RuntimeError(f"{asset['id']}: SHA-256 mismatch")
    blob = git_blob_sha1(data)
    if blob.lower() != asset["git_blob_sha1"].lower():
        raise RuntimeError(f"{asset['id']}: Git blob SHA-1 mismatch")
    if asset.get("source_tier") != "Standard (Free)" or asset.get("license") != "CC0-1.0":
        raise RuntimeError(f"{asset['id']}: not explicitly pinned to FREE Standard / CC0-1.0")
    if asset.get("commercial_use") is not True or asset.get("modification") is not True or asset.get("redistribution_allowed") is not True:
        raise RuntimeError(f"{asset['id']}: commercial/modification/redistribution permission is incomplete")
    if asset.get("attribution_required") is not False:
        raise RuntimeError(f"{asset['id']}: attribution policy is not recorded as not required")
    if not asset.get("immutable_download_source") or not asset.get("source_revision"):
        raise RuntimeError(f"{asset['id']}: immutable upstream pin is missing")
    if (asset.get("godot_version") != "4.7.2.stable" or asset.get("godot_animation_count") != 43 or asset.get("godot_skeleton_count") != 1):
        raise RuntimeError(f"{asset['id']}: Godot import metadata is incomplete")

    document, binary = parse_glb(destination)
    if len(binary) == 0:
        raise RuntimeError(f"{asset['id']}: empty GLB BIN chunk")
    if document.get("meshes") or document.get("materials") or document.get("textures") or document.get("images"):
        raise RuntimeError(f"{asset['id']}: character/rendering data remains in animation-only GLB")
    if any("mesh" in node for node in document.get("nodes", [])):
        raise RuntimeError(f"{asset['id']}: node retains a character mesh binding")
    if len(document.get("skins", [])) != asset.get("skin_count") or not any("skin" in node for node in document.get("nodes", [])):
        raise RuntimeError(f"{asset['id']}: technical skeleton skin metadata is missing")
    animations = document.get("animations", [])
    names = [animation.get("name", "") for animation in animations]
    if len(animations) != asset["animation_count"] or len(names) != len(set(names)) or any(not name for name in names):
        raise RuntimeError(f"{asset['id']}: animation count/name integrity failed")
    return digest, names


def main() -> int:
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        by_id = {asset.get("id"): asset for asset in manifest.get("assets", [])}
        if set(REQUIRED_IDS) - set(by_id):
            raise RuntimeError("manifest is missing one or more required Quaternius IDs")
        all_names = {}
        for asset_id in REQUIRED_IDS:
            asset = by_id[asset_id]
            digest, names = validate_asset(asset)
            all_names[asset_id] = names
            print(f"QUATERNIUS_GLTF: PASS {asset_id} size={asset['expected_size']} sha256={digest} animations={len(names)} root_motion={asset['root_motion']}")

        for left, right in (("QUATERNIUS_UAL1_STANDARD", "QUATERNIUS_UAL1_STANDARD_RM"), ("QUATERNIUS_UAL2_STANDARD", "QUATERNIUS_UAL2_STANDARD_RM")):
            if all_names[left] != all_names[right]:
                raise RuntimeError(f"{left}/{right}: root-motion pair has different animation names")

        for path in QUATERNIUS_ROOT.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(QUATERNIUS_ROOT).as_posix().lower()
            if path.suffix.lower() in (".blend", ".fbx") or any(marker in relative for marker in PROHIBITED_MARKERS):
                raise RuntimeError(f"prohibited Quaternius file present: {path.relative_to(ROOT)}")

        readme = QUATERNIUS_ROOT / "README.md"
        readme_text = readme.read_text(encoding="utf-8")
        for required_text in ("Creator: Quaternius", "CC0 1.0", "Commercial game use: allowed", "Universal Base Characters were not used"):
            if required_text not in readme_text:
                raise RuntimeError(f"README missing required record: {required_text}")
    except Exception as exc:
        print(f"QUATERNIUS_VALIDATION: FAIL\n - {exc}")
        return 1
    print("QUATERNIUS_VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
