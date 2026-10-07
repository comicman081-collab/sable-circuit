"""Hard, SHA-locked user gate shared by ASTER production pipeline tools."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "docs/ART_PRODUCTION/ASTER_STATIC_MASTER_USER_GATE.json"
NONPROMOTABLE_MASTERS = {
    # The user approved this as a visual basis, never as a 2048px production
    # Static Master. It remains available for identity reference only.
    "1e7a117a68e77bcac7cf7a3840cc425dc0976edde5b8ddfa4e0465325d104366": "NONPROMOTABLE_VISUAL_BASIS_ONLY: qwen_1024_static_candidate",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _within_project(path: Path) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"master path must stay inside project: {resolved}") from exc
    return resolved


def evaluate_static_master_gate() -> dict:
    """Return a hard decision; only an exact approved 2048px master can pass."""
    report = {
        "accepted": False,
        "state": "HOLD",
        "approval_file": GATE_PATH.relative_to(ROOT).as_posix(),
        "required": {
            "status": "PASS",
            "decision": "PASS",
            "approved_by": "user",
            "user_visual_approval": True,
            "approved_master_path": "project-relative 2048px canonical source",
            "approved_master_sha256": "current source hash",
        },
    }
    if not GATE_PATH.is_file():
        report["reason"] = "No explicit user Static Master gate exists."
        return report
    try:
        gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        report["state"] = "INVALID"
        report["reason"] = f"Invalid user Static Master gate: {error}"
        return report
    report["approval"] = gate
    required_flags = (
        gate.get("status") == "PASS"
        and gate.get("decision") == "PASS"
        and gate.get("approved_by") == "user"
        and gate.get("user_visual_approval") is True
    )
    if not required_flags:
        report["reason"] = "status/decision/user approval flags do not all grant PASS"
        return report
    path_value = gate.get("approved_master_path")
    expected_hash = str(gate.get("approved_master_sha256", "")).lower()
    if not isinstance(path_value, str) or len(expected_hash) != 64:
        report["state"] = "INVALID"
        report["reason"] = "approved master path and SHA-256 are both required"
        return report
    try:
        master = _within_project(Path(path_value))
    except ValueError as error:
        report["state"] = "INVALID"
        report["reason"] = str(error)
        return report
    if not master.is_file():
        report["state"] = "INVALID"
        report["reason"] = f"approved master is missing: {master}"
        return report
    current_hash = sha256(master)
    report["master"] = {
        "path": master.relative_to(ROOT).as_posix(),
        "current_sha256": current_hash,
        "approved_sha256": expected_hash,
    }
    if current_hash in NONPROMOTABLE_MASTERS:
        report["state"] = "NONPROMOTABLE_SOURCE"
        report["reason"] = NONPROMOTABLE_MASTERS[current_hash]
        return report
    if current_hash != expected_hash:
        report["state"] = "STALE_OR_CHANGED"
        report["reason"] = "current master SHA-256 differs from the user-approved SHA-256"
        return report
    try:
        with Image.open(master) as image:
            resolution = [image.width, image.height]
    except OSError as error:
        report["state"] = "INVALID"
        report["reason"] = f"approved master cannot be opened: {error}"
        return report
    report["master"]["resolution"] = resolution
    if resolution != [2048, 2048]:
        report["state"] = "INVALID"
        report["reason"] = "approved master must be a 2048x2048 canonical source"
        return report
    report["accepted"] = True
    report["state"] = "PASS"
    report["reason"] = "user PASS, source SHA lock, and 2048px canonical master all match"
    return report
