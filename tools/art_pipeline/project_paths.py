"""Read-only source and project-local output paths for art-production tools."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def require_project_output_path(candidate: Path, label: str) -> Path:
    """Resolve an output path and reject any write outside this project."""

    candidate = Path(candidate)
    resolved = (candidate if candidate.is_absolute() else PROJECT_ROOT / candidate).resolve()
    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError as error:
        raise RuntimeError(f"{label} must be inside {PROJECT_ROOT}: {resolved}") from error
    return resolved


# Models are read-only dependencies. They can be outside the project; only
# generated images, masks, exports, caches, and logs must stay inside it.
MODEL_ROOT = Path(os.environ.get("SABLE_CIRCUIT_MODEL_ROOT", PROJECT_ROOT / "tools" / "models")).resolve()


def local_model_path(name: str) -> Path:
    """Return a model path beneath this project unless explicitly overridden."""

    return MODEL_ROOT / name
