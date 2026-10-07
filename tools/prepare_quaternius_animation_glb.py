#!/usr/bin/env python3
"""Create an animation-only GLB from a Quaternius Standard GLB.

The official Standard GLBs include a mannequin as a preview/authoring aid.  SABLE
stores only the animation tracks and the target node hierarchy, never that mesh or
its material/texture data.
"""
from __future__ import annotations

import argparse
import copy
import json
import struct
from pathlib import Path


COMPONENT_SIZE = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
TYPE_COMPONENTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}


def read_glb(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    if len(raw) < 20 or raw[:4] != b"glTF":
        raise ValueError(f"{path} is not a GLB (missing glTF magic)")
    version, declared_length = struct.unpack_from("<II", raw, 4)
    if version != 2:
        raise ValueError(f"{path} has unsupported GLB version {version}")
    if declared_length != len(raw):
        raise ValueError(f"{path} declares {declared_length} bytes but contains {len(raw)}")
    offset = 12
    document = None
    binary = b""
    while offset < len(raw):
        chunk_length, chunk_type = struct.unpack_from("<I4s", raw, offset)
        offset += 8
        chunk = raw[offset : offset + chunk_length]
        if len(chunk) != chunk_length:
            raise ValueError(f"{path} contains a truncated GLB chunk")
        if chunk_type == b"JSON":
            document = json.loads(chunk.rstrip(b" \t\r\n").decode("utf-8"))
        elif chunk_type == b"BIN\x00":
            binary = chunk
        offset += chunk_length
    if not isinstance(document, dict) or not binary:
        raise ValueError(f"{path} must contain JSON and BIN chunks")
    return document, binary


def accessor_payload(document: dict, binary: bytes, index: int) -> bytes:
    accessors = document.get("accessors", [])
    views = document.get("bufferViews", [])
    accessor = accessors[index]
    if "sparse" in accessor:
        raise ValueError(f"animation accessor {index} uses sparse storage")
    if "bufferView" not in accessor:
        raise ValueError(f"animation accessor {index} has no bufferView")
    view = views[accessor["bufferView"]]
    if "byteStride" in view:
        raise ValueError(f"animation accessor {index} uses an unsupported byteStride")
    component_size = COMPONENT_SIZE[accessor["componentType"]]
    component_count = TYPE_COMPONENTS[accessor["type"]]
    payload_length = accessor["count"] * component_size * component_count
    view_start = view.get("byteOffset", 0)
    start = view_start + accessor.get("byteOffset", 0)
    end = start + payload_length
    if start < view_start or end > view_start + view["byteLength"] or end > len(binary):
        raise ValueError(f"animation accessor {index} points outside its bufferView")
    return binary[start:end]


def make_animation_only(document: dict, binary: bytes) -> tuple[dict, bytes]:
    animations = document.get("animations", [])
    if not animations:
        raise ValueError("source GLB has no animations")

    referenced = []
    for animation in animations:
        for sampler in animation.get("samplers", []):
            for key in ("input", "output"):
                if key not in sampler:
                    raise ValueError("animation sampler is missing input/output")
                if sampler[key] not in referenced:
                    referenced.append(sampler[key])
    for skin in document.get("skins", []):
        inverse_bind_matrices = skin.get("inverseBindMatrices")
        if inverse_bind_matrices is not None and inverse_bind_matrices not in referenced:
            referenced.append(inverse_bind_matrices)

    new_binary = bytearray()
    new_views = []
    new_accessors = []
    accessor_map = {}
    old_accessors = document.get("accessors", [])
    old_views = document.get("bufferViews", [])
    for old_index in referenced:
        payload = accessor_payload(document, binary, old_index)
        while len(new_binary) % 4:
            new_binary.append(0)
        new_view_index = len(new_views)
        new_views.append({"buffer": 0, "byteOffset": len(new_binary), "byteLength": len(payload)})
        new_binary.extend(payload)
        accessor = copy.deepcopy(old_accessors[old_index])
        accessor.pop("bufferView", None)
        accessor.pop("byteOffset", None)
        accessor["bufferView"] = new_view_index
        new_accessors.append(accessor)
        accessor_map[old_index] = len(new_accessors) - 1

    new_animations = copy.deepcopy(animations)
    for animation in new_animations:
        for sampler in animation.get("samplers", []):
            sampler["input"] = accessor_map[sampler["input"]]
            sampler["output"] = accessor_map[sampler["output"]]

    new_skins = copy.deepcopy(document.get("skins", []))
    for skin in new_skins:
        if "inverseBindMatrices" in skin:
            skin["inverseBindMatrices"] = accessor_map[skin["inverseBindMatrices"]]

    # Keep every target node index stable.  Remove the preview mesh and rendering
    # bindings, but retain the technical skin/joint metadata so Godot can create a
    # Skeleton3D without storing any character geometry.
    new_nodes = []
    for node in copy.deepcopy(document.get("nodes", [])):
        for key in ("mesh", "camera", "weights", "extensions"):
            node.pop(key, None)
        new_nodes.append(node)

    new_document = {
        "asset": {"version": "2.0", "generator": "SABLE CIRCUIT Quaternius animation-only preparer"},
        "scene": document.get("scene", 0),
        "scenes": copy.deepcopy(document.get("scenes", [])),
        "nodes": new_nodes,
        "animations": new_animations,
        "accessors": new_accessors,
        "bufferViews": new_views,
        "buffers": [{"byteLength": len(new_binary)}],
    }
    if new_skins:
        new_document["skins"] = new_skins
    if not new_document["scenes"]:
        raise ValueError("source GLB has no scene")
    return new_document, bytes(new_binary)


def write_glb(path: Path, document: dict, binary: bytes) -> None:
    json_chunk = json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    json_chunk += b" " * ((4 - len(json_chunk) % 4) % 4)
    binary_chunk = binary + b"\x00" * ((4 - len(binary) % 4) % 4)
    total_length = 12 + 8 + len(json_chunk) + 8 + len(binary_chunk)
    with path.open("wb") as stream:
        stream.write(struct.pack("<4sII", b"glTF", 2, total_length))
        stream.write(struct.pack("<I4s", len(json_chunk), b"JSON"))
        stream.write(json_chunk)
        stream.write(struct.pack("<I4s", len(binary_chunk), b"BIN\x00"))
        stream.write(binary_chunk)


def strip_mesh_from_glb(source: Path, destination: Path) -> None:
    document, binary = read_glb(source)
    output_document, output_binary = make_animation_only(document, binary)
    destination.parent.mkdir(parents=True, exist_ok=True)
    write_glb(destination, output_document, output_binary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    strip_mesh_from_glb(args.source, args.destination)
    print(f"ANIMATION_ONLY_GLB: PASS {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
