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


def fetch(asset: dict, force: bool = False) -> None:
    destination = ROOT / asset["destination"]
    expected = asset["sha256"].lower()
    if destination.is_file() and sha256(destination) == expected and not force:
        print(f"EXTERNAL_ASSET: OK cached {asset['id']} -> {destination.relative_to(ROOT)}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=destination.parent) as tmp:
        temp_path = Path(tmp.name)
    try:
        request = urllib.request.Request(asset["origin"], headers={"User-Agent": "SABLE-CIRCUIT-asset-fetcher/1"})
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch immutable external assets declared by SABLE CIRCUIT.")
    parser.add_argument("--id", action="append", dest="ids", help="Fetch only this stable asset id. Repeatable.")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest()
    assets = manifest.get("assets", [])
    wanted = set(args.ids or [])
    selected = [a for a in assets if not wanted or a.get("id") in wanted]
    missing = wanted.difference({a.get("id") for a in selected})
    if missing:
        print("Unknown external asset id(s): " + ", ".join(sorted(missing)), file=sys.stderr)
        return 2
    for asset in selected:
        fetch(asset, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
