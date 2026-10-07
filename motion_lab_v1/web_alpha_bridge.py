"""Quarantine-only bridge for an explicitly user-authorized web alpha edit.

This module never keys, crops, edits or imports a green image.  It only proves
that a retained green-screen result is a bounded input for the user's GPT web
conversion request.  The returned web file must pass ``source_alpha_policy``
before normal intake is even considered.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent


def _project_file(path, label):
    candidate = Path(path).expanduser().resolve()
    if not candidate.is_file() or not candidate.is_relative_to(PROJECT):
        raise ValueError(f'PROJECT_BRIDGE_REQUIRED: {label} must be a project file')
    return candidate


def inspect_green_master(path):
    """Return facts proving a bounded green bridge input, without editing it."""
    path = _project_file(path, 'green source')
    with Image.open(path) as image:
        image.load()
        if image.format != 'PNG' or image.mode not in ('RGB', 'RGBA'):
            raise ValueError('WEB_ALPHA_BRIDGE_REQUIRES_PNG: green source must be PNG RGB/RGBA')
        pixels = np.asarray(image.convert('RGB'))
        size = list(image.size)
        mode = image.mode
    corners = pixels[[0, 0, -1, -1], [0, -1, 0, -1]].tolist()
    # Image generators sometimes perturb a requested #00FF00 matte by a few
    # values.  Accept only a clearly green, corner-bounded screen here; this
    # is still bridge-only evidence and is never a local keying/intake pass.
    near_green = (pixels[:, :, 0] <= 40) & (pixels[:, :, 1] >= 210) & (pixels[:, :, 2] <= 40)
    exact_green = (pixels[:, :, 0] <= 8) & (pixels[:, :, 1] >= 247) & (pixels[:, :, 2] <= 8)
    if not all((r <= 40 and g >= 210 and b <= 40) for r, g, b in corners):
        raise ValueError('WEB_ALPHA_BRIDGE_REQUIRES_GREEN_CORNERS: source is not a green-screen master')
    fraction = float(near_green.mean())
    if fraction < 0.20:
        raise ValueError(f'WEB_ALPHA_BRIDGE_REQUIRES_GREEN_BACKGROUND: only {fraction:.3f} green pixels')
    return {
        'path': path.relative_to(PROJECT).as_posix(),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'native': size,
        'mode': mode,
        'greenPixelFraction': fraction,
        'exactGreenPixelFraction': float(exact_green.mean()),
        'cornerRGB': corners,
        'backgroundUniformity': 'EXACT_UNIFORM_GREEN' if float(exact_green.mean()) >= 0.80 else 'NEAR_GREEN_NON_UNIFORM',
        'status': 'GREEN_BRIDGE_INPUT_ONLY',
        'directIntakeAllowed': False,
        'localKeyingAllowed': False,
    }


def make_manifest(character, slot, source, tool_response, reference_order=None):
    source = _project_file(source, 'green source')
    tool_response = _project_file(tool_response, 'actual tool response')
    if 'quarantine' not in source.parts:
        raise ValueError('WEB_ALPHA_BRIDGE_REQUIRES_QUARANTINE: source must stay quarantine-only')
    facts = inspect_green_master(source)
    return {
        'kind': 'sable-web-alpha-bridge',
        'schema': 1,
        'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'character': character,
        'slot': slot,
        'source': facts,
        'actualToolResponse': {
            'path': tool_response.relative_to(PROJECT).as_posix(),
            'sha256': hashlib.sha256(tool_response.read_bytes()).hexdigest(),
        },
        'referenceOrder': list(reference_order or []),
        'destination': 'user-authorized GPT web chat alpha conversion',
        'status': 'WEB_ALPHA_BRIDGE_ONLY',
        'directIntakeAllowed': False,
        'nextGate': 'source_alpha_policy.py on the returned web PNG',
        'localKeyingAllowed': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--character', required=True)
    parser.add_argument('--slot', required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--tool-response', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reference', action='append', default=[])
    args = parser.parse_args()
    manifest = make_manifest(args.character, args.slot, args.source,
                             args.tool_response, args.reference)
    output = _project_file(args.output, 'bridge manifest') if args.output.exists() else args.output.resolve()
    if not output.is_relative_to(PROJECT):
        raise ValueError('PROJECT_BRIDGE_REQUIRED: manifest must stay in project')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == '__main__':
    main()
