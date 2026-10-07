"""Verify historical source derivatives; new green intake is retired.

The ImageGen result remains the appearance authority.  This importer is for a
project-local, byte-preserving matte normalization (for example, replacing a
near-green exterior with exact ``#00FF00``).  It binds the original generated
master, the untouched tool response, and the normalization report so a
derived frame cannot masquerade as a fresh generation result.
"""

from __future__ import annotations

import argparse
import json
import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image

from character_workflow import ROOT, binding, local, sha


GREEN = (0, 255, 0)


def _actual_background(rgb):
    path=Path(__file__).resolve().parents[1]/'tools/character_pipeline/normalize_imagegen_chroma.py'
    spec=importlib.util.spec_from_file_location('sable_chroma_verification',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.edge_connected_background(rgb)[0]


def _verify_derivative(derived: Path, source_master: Path, tool_response: Path, report: Path, mask: Path) -> dict[str, object]:
    if not source_master.is_relative_to(ROOT):
        raise ValueError("source master must be copied below motion_lab_v1")
    if not tool_response.is_relative_to(ROOT) or not report.is_relative_to(ROOT) or not mask.is_relative_to(ROOT):
        raise ValueError("provenance and QA files must be below motion_lab_v1")
    from source_provenance import response_master
    if response_master(ROOT,tool_response)!=source_master:
        raise ValueError('Normalization source differs from actual preserved master')
    response = json.loads(tool_response.read_text(encoding="utf-8-sig"))
    if response.get("tool") != "image_gen.imagegen" or not response.get("result"):
        raise ValueError("tool response is not the actual ImageGen response")
    project_copy = response.get("projectCopy")
    if project_copy is None or local(project_copy) != source_master:
        raise ValueError("tool response must bind the project copy of the generated master")
    if response.get("projectCopySHA256") != sha(source_master):
        raise ValueError("generated master copy hash does not match tool response")

    normalize = json.loads(report.read_text(encoding="utf-8-sig"))
    if normalize.get("operation") != "edge-connected green matte normalization only; no source-art redraw":
        raise ValueError("unexpected normalization operation")
    if normalize.get("input_sha256") != sha(source_master):
        raise ValueError("normalization input is not the bound generated master")
    if normalize.get("output_sha256") != sha(derived):
        raise ValueError("normalization output hash is stale")
    if normalize.get("mask_sha256") != sha(mask) or normalize.get("subject_pixels_byte_exact") is not True:
        raise ValueError("normalization mask/report is stale")
    if normalize.get("alpha_ready") is not True:
        raise ValueError("normalization did not produce an alpha-ready source")

    with Image.open(derived) as image:
        image.load()
        if image.mode != "RGB":
            raise ValueError("normalized green source must remain RGB")
        if min(image.size) < 1024:
            raise ValueError("a native high-resolution source is required")
        rgb = np.asarray(image)
    with Image.open(mask) as mask_image:
        mask_image.load()
        mask_array = np.asarray(mask_image.convert("L"))
    if mask_array.shape != rgb.shape[:2] or not set(np.unique(mask_array)).issubset({0, 255}):
        raise ValueError("normalization mask must be native binary")
    with Image.open(source_master) as original:
        original.load()
        if original.mode != 'RGB' or original.size != (rgb.shape[1],rgb.shape[0]):
            raise ValueError('normalization must preserve original RGB mode and dimensions')
        original_rgb=np.asarray(original)
    subject=mask_array==255
    if not subject.any() or not np.array_equal(rgb[subject],original_rgb[subject]):
        raise ValueError('normalization changed protected subject pixels')
    background = mask_array == 0
    if not np.array_equal(background,_actual_background(original_rgb)):
        raise ValueError('normalization mask differs from original edge-connected background')
    if not background.any() or not np.all(rgb[background] == np.asarray(GREEN, dtype=np.uint8)):
        raise ValueError("derived background is not exact uniform green")
    return {
        "toolResponse": binding(tool_response),
        "sourceMaster": binding(source_master),
        "normalization": binding(report),
        "mask": binding(mask),
        "native": [int(rgb.shape[1]), int(rgb.shape[0])],
        "backgroundPixels": int(background.sum()),
    }


def intake(character: str, direction: str, action: str, frame: int, derived: Path, source_master: Path,
           tool_response: Path, report: Path, mask: Path) -> dict[str, object]:
    # Keep _verify_derivative available for old byte-bound sources. New work
    # must enter through native RGBA intake; no legacy CLI escape hatch.
    from source_alpha_policy import reject_chroma_intake
    reject_chroma_intake()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--character", required=True)
    parser.add_argument("--direction", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--frame", type=int, required=True)
    parser.add_argument("--derived", required=True)
    parser.add_argument("--source-master", required=True)
    parser.add_argument("--tool-response", required=True)
    parser.add_argument("--normalization-report", required=True)
    parser.add_argument("--mask", required=True)
    args = parser.parse_args()
    print(json.dumps(intake(args.character, args.direction, args.action, args.frame,
                            Path(args.derived), Path(args.source_master), Path(args.tool_response),
                            Path(args.normalization_report), Path(args.mask)), ensure_ascii=False))
