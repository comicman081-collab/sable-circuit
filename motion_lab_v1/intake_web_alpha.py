"""Intake a user-authorized GPT web alpha conversion after native checks.

The web conversion is a tightly scoped bridge for a retained failed green
candidate.  This module never keys, crops, redraws or edits pixels; it only
hash-binds the downloaded web PNG, the bridge manifest and the actual web
response before placing the returned source in the requested recipe slot.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil

from PIL import Image

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
WEB_GENERATOR = 'GPT web alpha conversion'
WEB_DERIVATION = 'user-authorized GPT web alpha conversion; no local keying'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def local(path, label):
    candidate = Path(path).expanduser().resolve()
    if not candidate.is_file() or not candidate.is_relative_to(ROOT):
        raise ValueError(f'PROJECT_INPUT_REQUIRED: {label} must be an existing file inside motion_lab_v1')
    return candidate


def project_path(value, label):
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = PROJECT / candidate
    candidate = candidate.resolve()
    if not candidate.is_file() or not candidate.is_relative_to(PROJECT):
        raise ValueError(f'PROJECT_INPUT_REQUIRED: {label} must be an existing file inside this SABLE project')
    return candidate


def binding(path):
    path = local(path, 'binding')
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def _validate_bridge(character, slot, path, config):
    manifest = read(path)
    if manifest.get('kind') != 'sable-web-alpha-bridge' or manifest.get('schema') != 1:
        raise ValueError('WEB_ALPHA_BRIDGE_REQUIRED: unsupported bridge manifest')
    if manifest.get('character') != character or manifest.get('slot') != slot:
        raise ValueError('WEB_ALPHA_BRIDGE_REQUIRED: bridge character/slot differs from intake')
    if manifest.get('status') != 'WEB_ALPHA_BRIDGE_ONLY' or manifest.get('directIntakeAllowed') is not False:
        raise ValueError('WEB_ALPHA_BRIDGE_REQUIRED: source is not quarantine-only')
    source = manifest.get('source')
    if not isinstance(source, dict) or not isinstance(source.get('path'), str):
        raise ValueError('WEB_ALPHA_BRIDGE_REQUIRED: source binding missing')
    source_path = project_path(source['path'], 'green bridge source')
    if 'quarantine' not in source_path.parts:
        raise ValueError('WEB_ALPHA_BRIDGE_REQUIRED: green source must remain in quarantine')
    if sha(source_path) != source.get('sha256'):
        raise ValueError('WEB_ALPHA_BRIDGE_REQUIRED: green source hash changed')
    from web_alpha_bridge import inspect_green_master
    inspect_green_master(source_path)
    expected_identity = (ROOT / config['identityReference']).resolve()
    order = manifest.get('referenceOrder') or []
    if not order or project_path(order[0], 'bridge identity reference') != expected_identity:
        raise ValueError('WEB_ALPHA_BRIDGE_REQUIRED: identity reference order differs from recipe')
    tool = manifest.get('actualToolResponse')
    if not isinstance(tool, dict) or not isinstance(tool.get('path'), str):
        raise ValueError('WEB_ALPHA_BRIDGE_REQUIRED: Luna response binding missing')
    tool_path = project_path(tool['path'], 'Luna bridge response')
    if sha(tool_path) != tool.get('sha256'):
        raise ValueError('WEB_ALPHA_BRIDGE_REQUIRED: Luna response hash changed')
    return manifest, source_path, tool_path


def _validate_web_response(path, bridge_path, returned):
    proof = read(path)
    if proof.get('tool') != 'chatgpt.web.alpha_conversion' or not isinstance(proof.get('result'), dict) or not proof['result']:
        raise ValueError('GPT_WEB_RESPONSE_REQUIRED: actual alpha-conversion response metadata is missing')
    bound_bridge = proof.get('bridgeManifest')
    if not isinstance(bound_bridge, dict) or not bound_bridge.get('path'):
        raise ValueError('GPT_WEB_RESPONSE_REQUIRED: bridge manifest binding is missing')
    bridge_file = local(bridge_path, 'bridge manifest')
    bound_path = (ROOT / bound_bridge['path']).resolve()
    if bound_path != bridge_file or sha(bridge_file) != bound_bridge.get('sha256'):
        raise ValueError('GPT_WEB_RESPONSE_REQUIRED: bridge manifest hash differs')
    expected = local(returned, 'returned web PNG')
    if proof.get('projectCopy') != expected.relative_to(ROOT).as_posix() or proof.get('projectCopySHA256') != sha(expected):
        raise ValueError('GPT_WEB_RESPONSE_REQUIRED: project copy/hash differs from returned PNG')
    returned_path = proof.get('returnedPath')
    if not isinstance(returned_path, str) or not Path(returned_path).is_absolute() or Path(returned_path).resolve() != expected:
        raise ValueError('GPT_WEB_RESPONSE_REQUIRED: returned path is not the project copy')
    if proof['result'].get('returnedPath') not in (returned_path, str(expected)):
        raise ValueError('GPT_WEB_RESPONSE_REQUIRED: result does not bind returned path')
    return proof


def intake(character, direction, action, frame, returned, bridge_manifest, web_response):
    if not character or any(not isinstance(value, str) for value in (character, direction, action)):
        raise ValueError('Invalid recipe identity')
    import character_workflow as workflow
    config = workflow.recipe(character)
    slot = f'{direction}/{action}/{frame}'
    selected = dict(workflow.slots(config)).get(slot)
    if selected is None:
        raise ValueError('Invalid recipe slot')
    from cycle_review import require_pilot
    require_pilot(character, direction, action)
    returned = local(returned, 'returned web PNG')
    from source_alpha_policy import inspect_master
    native = inspect_master(returned)
    bridge_path = local(bridge_manifest, 'bridge manifest')
    manifest, green_source, luna_response = _validate_bridge(character, slot, bridge_path, config)
    web_path = local(web_response, 'GPT web response')
    proof = _validate_web_response(web_path, bridge_path, returned)

    folder = (ROOT / config['source']).resolve()
    if folder != ROOT / 'art' / character:
        raise ValueError('Source folder must be art/CHARACTER')
    target = selected
    if target.exists():
        previous = folder / 'previous'
        previous.mkdir(exist_ok=True)
        old = sha(target)[:12]
        prior = previous / f'{target.stem}_{old}{target.suffix}'
        if not prior.exists():
            shutil.copy2(target, prior)
        old_receipt = target.with_suffix('.source.json')
        if old_receipt.exists():
            prior_receipt = previous / f'{target.stem}_{old}.source.json'
            if not prior_receipt.exists():
                shutil.copy2(old_receipt, prior_receipt)
    if returned.resolve() != target.resolve():
        shutil.copy2(returned, target)
    receipt = {
        'generator': WEB_GENERATOR,
        'importedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source': str(returned.resolve()),
        'native': native['native'],
        'sha256': sha(target),
        'destination': target.relative_to(ROOT).as_posix(),
        'sourceMaster': binding(returned),
        'toolResponse': binding(web_path),
        'derivation': {
            'kind': WEB_DERIVATION,
            'resampling': False,
            'anatomicalWarp': False,
            'bridgeManifest': binding(bridge_path),
            'greenSource': {
                'path': green_source.relative_to(ROOT).as_posix(),
                'sha256': sha(green_source),
            },
        },
    }
    receipt_path = target.with_suffix('.source.json')
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding='utf-8')
    workflow.invalidate_delivery(character, 'GPT web alpha conversion returned a new source: ' + slot)
    result = {
        'status': 'INTAKED_WEB_ALPHA_HOLD_VISUAL_REVIEW',
        'character': character,
        'slot': slot,
        'target': workflow.binding(target),
        'receipt': workflow.binding(receipt_path),
        'nativeAlpha': native,
        'bridgeManifest': workflow.binding(bridge_path),
        'webResponse': workflow.binding(web_path),
        'lunaBridgeResponse': workflow.binding(luna_response),
        'directGreenIntake': False,
        'visualApproval': False,
        'notes': 'No local keying/crop/redraw; returned web PNG passed only the native format gate and still needs visual review.',
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--character', required=True)
    parser.add_argument('--direction', required=True)
    parser.add_argument('--action', required=True)
    parser.add_argument('--frame', type=int, required=True)
    parser.add_argument('--returned', type=Path, required=True)
    parser.add_argument('--bridge-manifest', type=Path, required=True)
    parser.add_argument('--web-response', type=Path, required=True)
    args = parser.parse_args()
    intake(args.character, args.direction, args.action, args.frame,
           args.returned, args.bridge_manifest, args.web_response)
