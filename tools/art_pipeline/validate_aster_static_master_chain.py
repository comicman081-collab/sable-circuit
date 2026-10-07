#!/usr/bin/env python3
"""Validate the locked ASTER 2048 static-master local-retouch chain.

The validator is deliberately technical only.  A successful result means that
the compositing constraints were held; it never turns the Static Visual Gate
into PASS without an explicit user decision and SHA lock.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1"
MANIFEST = CANONICAL / "ASTER_STATIC_MASTER_2048_V1_MANIFEST.json"
FINAL_PROVENANCE = CANONICAL / "retouch_candidates/torso_garment_v1_seed251142/ASTER_STATIC_REGION_RETOUCH_PROVENANCE.json"
OUT = CANONICAL / "reviews/ASTER_STATIC_MASTER_CHAIN_QA.json"
GREEN = np.array([0, 255, 0], dtype=np.uint8)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def under_root(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(f"Path leaves project: {relative}") from error
    return path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    canonical = load_json(MANIFEST)
    base = under_root(canonical["working_rgb"]["path"])
    mask_path = under_root(canonical["working_mask"]["path"])
    if sha256(base) != canonical["working_rgb"]["sha256"]:
        raise SystemExit("Canonical working RGB SHA no longer matches its lock")
    if sha256(mask_path) != canonical["working_mask"]["sha256"]:
        raise SystemExit("Canonical mask SHA no longer matches its lock")

    chain: list[tuple[Path, dict]] = []
    current_path = FINAL_PROVENANCE
    seen: set[Path] = set()
    while True:
        if current_path in seen:
            raise SystemExit("Retouch provenance chain cycle")
        seen.add(current_path)
        current = load_json(current_path)
        if current.get("canonical_manifest") != MANIFEST.relative_to(ROOT).as_posix():
            raise SystemExit(f"Wrong canonical manifest in {current_path}")
        chain.append((current_path, current))
        authoring_base = current.get("authoring_base", {})
        if not authoring_base:
            if current.get("canonical_working_sha256") != canonical["working_rgb"]["sha256"]:
                raise SystemExit("Legacy first retouch does not identify the canonical SHA")
            if current.get("prior_regions", []):
                raise SystemExit("Legacy first retouch unexpectedly has prior regions")
            break
        if authoring_base.get("mode") == "canonical_working_base":
            if authoring_base.get("sha256") != canonical["working_rgb"]["sha256"]:
                raise SystemExit("First retouch does not start at canonical SHA")
            break
        if authoring_base.get("mode") != "accepted_local_retouch_candidate":
            raise SystemExit("Unknown authoring base mode")
        previous_provenance = under_root(authoring_base["provenance"])
        if sha256(previous_provenance) != authoring_base.get("provenance_sha256"):
            raise SystemExit("Previous provenance SHA mismatch")
        previous_rgb = under_root(authoring_base["path"])
        if sha256(previous_rgb) != authoring_base.get("sha256"):
            raise SystemExit("Previous patch RGB SHA mismatch")
        current_path = previous_provenance

    chain.reverse()
    regions = [record["region"] for _, record in chain]
    if len(regions) != len(set(regions)):
        raise SystemExit("A static-chain region was edited more than once")
    union = np.zeros((2048, 2048), dtype=bool)
    overlap_pixels = 0
    for region in regions:
        region_path = under_root(canonical["regions"][region]["path"])
        mask = np.asarray(Image.open(region_path).convert("L")) == 255
        overlap_pixels += int(np.count_nonzero(union & mask))
        union |= mask
    if overlap_pixels:
        raise SystemExit(f"Static-chain region masks overlap: {overlap_pixels} pixels")

    final = under_root(chain[-1][1]["proposal"])
    expected_final_sha = chain[-1][1]["proposal_sha256"]
    if sha256(final) != expected_final_sha:
        raise SystemExit("Final chain candidate SHA mismatch")
    before = np.asarray(Image.open(base).convert("RGB"))
    after = np.asarray(Image.open(final).convert("RGB"))
    alpha = np.asarray(Image.open(mask_path).convert("L"))
    if before.shape != (2048, 2048, 3) or after.shape != before.shape or alpha.shape != (2048, 2048):
        raise SystemExit("Static-chain dimensions are invalid")
    changed = np.any(before != after, axis=2)
    exterior_green = bool(np.all(after[alpha == 0] == GREEN))
    report = {
        "role": "ASTER 2048 static-master chain technical QA only; user visual decision still required",
        "status": "TECHNICAL_PASS__USER_REVIEW_REQUIRED",
        "canonical": {"path": base.relative_to(ROOT).as_posix(), "sha256": sha256(base)},
        "final_candidate": {"path": final.relative_to(ROOT).as_posix(), "sha256": sha256(final)},
        "chain": [
            {
                "region": record["region"],
                "provenance": provenance.relative_to(ROOT).as_posix(),
                "proposal": record["proposal"],
                "proposal_sha256": record["proposal_sha256"],
                "changed_pixels_within_region": record["changed_pixels_within_region"],
                "changed_pixels_outside_region": record["changed_pixels_outside_region"],
            }
            for provenance, record in chain
        ],
        "regions": regions,
        "region_overlap_pixels": overlap_pixels,
        "changed_pixels_total": int(np.count_nonzero(changed)),
        "changed_pixels_outside_union": int(np.count_nonzero(changed & ~union)),
        "exact_green_exterior": exterior_green,
        "cloud_inference_calls": 0,
        "krea2_calls": 0,
        "runtime_asset": False,
        "static_visual_gate": "USER_REVIEW_REQUIRED",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["changed_pixels_outside_union"] == 0 and exterior_green else 2


if __name__ == "__main__":
    raise SystemExit(main())
