"""Read-only admission gate for new ImageGen masters (user rule 2026-09-13;
alpha-255 interiors allowed by the user on 2026-09-28).

Historical source/provenance verification remains separate. This gate never
keys a backdrop, clamps alpha, edits pixels, or grants visual approval.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

POLICY_ID = 'native_rgba_alpha_0_255_v2'
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROMPT = ('Deliver an actual RGBA PNG with transparent background alpha 0 '
          'and an opaque subject interior (alpha 254 or 255). '
          'No green/chroma background, painted checkerboard, matte, '
          'floor, shadow or glow. Preserve native alpha from generation; '
          'no keyed or alpha-clamped substitute. Failed transparency remains '
          'a rejected candidate; do not retry with green.')


def requirement():
    return {'id': POLICY_ID, 'mode': 'RGBA', 'alphaRange': [0, 255],
            'backgroundAlpha': 0, 'subjectInteriorAlpha': 255,
            'greenFallbackAllowed': False, 'nativeMasterRequired': True,
            'visualReviewRequired': True}


def require_project_reference(path, label='reference', project_root=None,
                              require_existing=True):
    """Resolve a generation reference and reject other-project/staging files.

    ImageGen may return its newly generated output in managed staging, but
    appearance and pose *inputs* must already be project-owned.  This keeps a
    stale image from another game or chat from silently becoming SABLE art.
    """
    project_root = Path(project_root).resolve() if project_root is not None else PROJECT_ROOT
    candidate = Path(path).expanduser().resolve()
    if require_existing and not candidate.is_file():
        raise FileNotFoundError(candidate)
    try:
        candidate.relative_to(project_root)
    except ValueError as error:
        raise ValueError(
            f'PROJECT_REFERENCE_REQUIRED: {label} must be a file inside {project_root}'
        ) from error
    blocked = {'generated_images', 'codex-clipboard', 'local_body_studio', 'localforge_direct_v2'}
    if any(part.lower() in blocked for part in candidate.parts):
        raise ValueError(
            f'PROJECT_REFERENCE_REQUIRED: {label} cannot use managed staging or another project'
        )
    return candidate


def validate_request_references(request, root=None, expected_reference=None):
    """Validate every appearance/pose input named by a request row.

    ``expected_reference`` binds a row to the identity reference in its
    character recipe, preventing a valid image from another SABLE character
    from being silently used as appearance authority.
    """
    root = Path(root).resolve() if root is not None else PROJECT_ROOT
    for key in ('reference', 'poseGuide'):
        value = request.get(key)
        if not value:
            continue
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = root / candidate
        require_project_reference(candidate, key, root,
                                  require_existing=(key == 'reference'))
        if key == 'reference' and expected_reference:
            expected = Path(expected_reference)
            if not expected.is_absolute():
                expected = root / expected
            expected = expected.resolve()
            if candidate != expected:
                raise ValueError(
                    'PROJECT_REFERENCE_REQUIRED: request reference differs from recipe identity reference'
                )
    return True


def inspect_master(path):
    """Measure decoded original pixels. Numeric success is format-only."""
    path = Path(path)
    with Image.open(path) as image:
        image.load()
        if image.format != 'PNG' or image.mode != 'RGBA':
            raise ValueError('NATIVE_ALPHA_REQUIRED: returned master must be an actual RGBA PNG; RGB, green and painted checkerboard are rejected')
        alpha = np.asarray(image.getchannel('A'))
        native = list(image.size)
    # Alpha 255 is an opaque interior, not a failure (user 2026-09-28); the
    # background checks below still reject a canvas with no alpha-0 margin.
    low, high = int(alpha.min()), int(alpha.max())
    visible = alpha > 0
    if not visible.any() or high < 250:
        raise ValueError('SUBJECT_OPACITY_REQUIRED: empty or uniformly translucent subject')
    transparent_fraction = float((alpha == 0).mean())
    if transparent_fraction < .10:
        raise ValueError('TRANSPARENT_BACKGROUND_REQUIRED: less than 10% alpha-zero margin/background')
    corners = [int(alpha[y, x]) for y, x in [(0, 0), (0, -1), (-1, 0), (-1, -1)]]
    if any(corners):
        raise ValueError('TRANSPARENT_CORNERS_REQUIRED: canvas corners must have alpha 0')
    near_opaque_fraction = float((alpha[visible] >= 250).mean())
    if near_opaque_fraction < .80:
        raise ValueError('SUBJECT_OPACITY_REQUIRED: subject interior must remain near opaque, not a translucent canvas')
    return {'policy': POLICY_ID, 'status': 'PASS_ALPHA_FORMAT_ONLY',
            'sourceSHA256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'native': native, 'mode': 'RGBA', 'alphaMin': low, 'alphaMax': high,
            'transparentPixels': int((alpha == 0).sum()),
            'visiblePixels': int(visible.sum()), 'cornerAlpha': corners,
            'nearOpaqueVisibleFraction': near_opaque_fraction,
            'visualApproved': False}


def inspect_slot_master(root, receipt):
    from source_provenance import bound, response_master
    master = response_master(root, bound(root, receipt.get('toolResponse')))
    return inspect_master(master)


def reject_chroma_intake():
    raise ValueError('NATIVE_ALPHA_REQUIRED: new green/chroma derivative intake is disabled by user instruction; retain existing masters for historical verification')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(inspect_master(args.source)))
