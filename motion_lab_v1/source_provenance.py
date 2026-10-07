"""Recheck saved ImageGen/master/derivative relationships; not provider attestation.

All reads are project-local. A saved JSON can establish consistency, never prove
that a dishonest caller actually invoked a provider. Keep the real tool event.
"""
import hashlib
import json
import re
from pathlib import Path
from PIL import Image
import numpy as np


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def local(root, value):
    path = (root / value).resolve()
    if path == root or not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Missing project-local provenance input')
    return path


def bound(root, value):
    if not isinstance(value, dict): raise ValueError('Missing provenance binding')
    path = local(root, value['path'])
    if digest(path) != value['sha256']: raise ValueError('Stale provenance binding')
    return path


def pixels(path):
    with Image.open(path) as im:
        rgba = im.convert('RGBA')
        header = f'RGBA:{rgba.width}x{rgba.height}:'.encode()
        return hashlib.sha256(header + rgba.tobytes()).hexdigest()


def response_master(root, response_path):
    response_path = local(root, response_path)
    proof = json.loads(response_path.read_text(encoding='utf-8-sig'))
    result = proof.get('result')
    if proof.get('tool') == 'chatgpt.web.alpha_conversion':
        # The web route is an explicitly user-authorized matte-removal bridge.
        # It is accepted only when the downloaded project copy, the returned
        # path, and the bridge manifest are all hash-bound.  This is still
        # provenance consistency, not an assertion that the web page was honest.
        if not isinstance(result, dict) or not result:
            raise ValueError('Actual GPT web conversion metadata required')
        if not isinstance(proof.get('bridgeManifest'), dict):
            raise ValueError('GPT web response must bind its bridge manifest')
        manifest = bound(root, proof['bridgeManifest'])
        bridge = json.loads(manifest.read_text(encoding='utf-8-sig'))
        if (bridge.get('status') != 'WEB_ALPHA_BRIDGE_ONLY' or
                bridge.get('directIntakeAllowed') is not False):
            raise ValueError('Invalid web alpha bridge manifest')
        if not isinstance(proof.get('projectCopy'), str):
            raise ValueError('Missing exact GPT web project copy')
        master = local(root, proof['projectCopy'])
        copied_sha = proof.get('projectCopySHA256')
        if digest(master) != copied_sha:
            raise ValueError('GPT web project copy bytes changed (hash mismatch)')
        returned = proof.get('returnedPath')
        if not isinstance(returned, str) or not Path(returned).is_absolute():
            raise ValueError('Actual GPT web returned path missing')
        if Path(returned).resolve() != master:
            raise ValueError('GPT web returned path differs from project copy')
        if result.get('returnedPath') not in (returned, str(master)):
            raise ValueError('GPT web result does not bind returned path')
        with Image.open(master) as image:
            image.verify()
        return master
    if proof.get('tool') != 'image_gen.imagegen' or not isinstance(result, dict) or not result:
        raise ValueError('Actual ImageGen metadata required')
    returned = proof.get('returnedPath')
    hint = result.get('output_hint')
    if not isinstance(returned,str) or not Path(returned).is_absolute() or not isinstance(hint,str):
        raise ValueError('Actual returned path missing')
    normalized = hint.replace('\\','/')
    candidate = returned.replace('\\','/')
    # Quoted paths are indivisible: whitespace inside quotes is a filename
    # character, not permission to accept a shorter prefix. Remove their spans
    # before considering the explicitly supported unquoted tool sentences.
    quoted=list(re.finditer(r'''(["'`])([^\r\n]*?)\1''',normalized))
    exact_quoted=any(m.group(2)==candidate for m in quoted)
    unquoted=re.sub(r'''(["'`])([^\r\n]*?)\1''',' ',normalized)
    # A truncated quoted filename remains quoted through the end of its line;
    # never reinterpret a space-separated suffix as an independent path.
    unquoted=re.sub(r'''["'`][^\r\n]*''',' ',unquoted)
    def exact_unquoted(line):
        for match in re.finditer(re.escape(candidate),line):
            before=line[:match.start()];after=line[match.end():].strip()
            if (not before or before[-1].isspace()) and after in ('','.', 'by default.'):
                return True
        return False
    if not exact_quoted and not any(exact_unquoted(line) for line in unquoted.splitlines()):
        raise ValueError('Returned path differs from actual output metadata')
    if not isinstance(proof.get('projectCopy'),str):
        raise ValueError('Missing exact project copy')
    master = local(root, proof['projectCopy'])
    if digest(master) != proof.get('projectCopySHA256'):
        raise ValueError('Returned master bytes changed (hash mismatch)')
    with Image.open(master) as image:
        image.verify()
    return master


def validate_slot(root, target, receipt):
    """No missing derivation fields may downgrade an edited image to an original."""
    generator = receipt.get('generator')
    if generator not in ('Codex built-in ImageGen', 'GPT web alpha conversion') or digest(target) != receipt.get('sha256'):
        raise ValueError('Slot content or generator mismatch')
    if local(root,receipt['destination']) != target:
        raise ValueError('Receipt names a different slot')
    proof_path = bound(root,receipt.get('toolResponse'))
    original = response_master(root,proof_path)
    master = bound(root,receipt.get('sourceMaster'))
    if digest(master) != digest(original):
        raise ValueError('Preserved source master differs from returned project copy')
    derivation = receipt.get('derivation')
    if generator == 'GPT web alpha conversion':
        if not isinstance(derivation, dict) or derivation.get('kind') != 'user-authorized GPT web alpha conversion; no local keying':
            raise ValueError('GPT web conversion requires explicit no-key derivation')
        bridge = bound(root, derivation.get('bridgeManifest'))
        manifest = json.loads(bridge.read_text(encoding='utf-8-sig'))
        if (manifest.get('status') != 'WEB_ALPHA_BRIDGE_ONLY' or
                manifest.get('directIntakeAllowed') is not False):
            raise ValueError('Invalid GPT web bridge binding')
        return True
    if derivation is None:
        if digest(target) != digest(master):
            raise ValueError('Changed source needs its explicit derivation')
        return True
    if not isinstance(derivation,dict) or derivation.get('resampling') is not False or derivation.get('anatomicalWarp') is not False:
        raise ValueError('Unsupported source-art derivation')
    kind = derivation.get('kind')
    if kind == 'edge-connected green matte normalization only; no source-art redraw':
        from intake_derived_frame import _verify_derivative
        _verify_derivative(target,master,proof_path,bound(root,derivation.get('normalization')),bound(root,derivation.get('mask')))
    elif kind == 'chroma-key and connected-subject crop only':
        from build_atlas import subjects
        with Image.open(target) as image:
            actual = np.asarray(image.convert('RGBA'))
        matching = [im for im,box in subjects(master,2) if list(box) == derivation.get('box')]
        if len(matching) != 1 or not np.array_equal(actual,np.asarray(matching[0].convert('RGBA'))):
            raise ValueError('Pair crop pixels do not derive from the preserved master')
    else:
        raise ValueError('Unknown source-art derivation')
    return True
