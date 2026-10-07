"""Verify and unpack the user-requested source library without overwriting files."""
from pathlib import Path, PurePosixPath
from collections import Counter
import hashlib
import json
import struct
import zipfile

ROOT = Path(__file__).resolve().parent
LIBRARY = Path("C:/ai_asset/karchive/2026-09-19")
ARCHIVE = LIBRARY / "all-6400.zip"
EXPECTED_BYTES = 4327982924


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inspect_glb(data):
    magic, version, declared = struct.unpack_from("<4sII", data)
    assert magic == b"glTF" and version == 2 and declared == len(data)
    pos, doc, binary_length = 12, None, 0
    while pos < len(data):
        size, kind = struct.unpack_from("<II", data, pos)
        pos += 8
        assert size % 4 == 0 and pos + size <= len(data)
        if kind == 0x4E4F534A:
            doc = json.loads(data[pos:pos + size])
        elif kind == 0x004E4942:
            binary_length += size
        pos += size
    assert doc and pos == len(data)
    accessors = doc.get("accessors", [])
    vertices, triangles, primitives, modes = 0, 0, 0, Counter()
    for mesh in doc.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            primitives += 1
            mode = primitive.get("mode", 4)
            modes[str(mode)] += 1
            vertex_count = accessors[primitive["attributes"]["POSITION"]]["count"]
            vertices += vertex_count
            count = accessors[primitive["indices"]]["count"] if "indices" in primitive else vertex_count
            triangles += count // 3 if mode == 4 else max(0, count - 2) if mode in (5, 6) else 0
    external = [item["uri"] for item in doc.get("buffers", []) + doc.get("images", []) if item.get("uri") and not item["uri"].startswith("data:")]
    return {"glb_version": version, "meshes": len(doc.get("meshes", [])), "primitives": primitives,
            "vertices_primitive_sum": vertices, "triangles_mesh_sum": triangles,
            "nodes": len(doc.get("nodes", [])), "materials": len(doc.get("materials", [])),
            "images": len(doc.get("images", [])), "textures": len(doc.get("textures", [])),
            "skins": len(doc.get("skins", [])), "animations": len(doc.get("animations", [])),
            "external_resources": external, "extensions_required": doc.get("extensionsRequired", []),
            "generator": doc.get("asset", {}).get("generator"), "primitive_modes": dict(modes)}


assert ARCHIVE.stat().st_size == EXPECTED_BYTES
destination = LIBRARY / "models"
if destination.exists():
    raise SystemExit("Refusing to overwrite an existing models directory")
destination.mkdir()
inventory, errors = [], []
with zipfile.ZipFile(ARCHIVE) as archive:
    infos = archive.infolist()
    assert len(infos) == 6401 and sum(x.file_size for x in infos) < 6_000_000_000
    license_data = archive.read("LICENSE.txt")
    (ROOT / "bundled_LICENSE.txt").write_bytes(license_data)
    for index, info in enumerate(infos):
        relative = PurePosixPath(info.filename)
        assert not relative.is_absolute() and ".." not in relative.parts and ":" not in str(relative) and "\\" not in str(relative)
        target = destination.joinpath(*relative.parts).resolve()
        assert target.is_relative_to(destination.resolve())
        assert relative.suffix.lower() in (".glb", ".txt")
        data = archive.read(info)  # Reading fully also checks each member's CRC.
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output:
            output.write(data)
        if relative.suffix.lower() == ".glb":
            entry = {"id": relative.stem, "collection": relative.parts[0], "archive_member": info.filename,
                     "local_path": str(target), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                     "zip_crc32": f"{info.CRC:08x}"}
            try:
                entry.update(inspect_glb(data))
                entry["structural_status"] = "PASS_GLB_HEADER_JSON_AND_ZIP_CRC_ONLY"
            except Exception as error:
                entry["structural_status"] = "FAIL"
                entry["error"] = repr(error)
                errors.append(entry["id"])
            inventory.append(entry)
        if index and index % 1000 == 0:
            print(f"Verified and unpacked {index} / {len(infos)}", flush=True)

summary = {"source_page": "https://karchive.vibeline.co.kr/models", "archive_path": str(ARCHIVE),
           "archive_bytes": ARCHIVE.stat().st_size, "archive_sha256": sha(ARCHIVE),
           "unpacked_bytes": sum(i.file_size for i in infos), "glb_count": len(inventory),
           "collections": dict(Counter(r["collection"] for r in inventory)),
           "structural_failures": errors, "zip_crc_all_members": "PASS",
           "models_with_skins": sum(bool(r.get("skins")) for r in inventory),
           "models_with_animations": sum(bool(r.get("animations")) for r in inventory),
           "models_with_external_resources": sum(bool(r.get("external_resources")) for r in inventory),
           "triangle_min": min(r.get("triangles_mesh_sum", 0) for r in inventory),
           "triangle_max": max(r.get("triangles_mesh_sum", 0) for r in inventory),
           "license_sha256": hashlib.sha256(license_data).hexdigest(),
           "verification_limit": "ZIP CRC and GLB structure only; not full glTF conformance, artistic quality, or runtime approval."}
for folder in (ROOT, LIBRARY):
    (folder / "inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    (folder / "download_verification.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
