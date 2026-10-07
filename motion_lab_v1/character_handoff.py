"""Emit exact-byte resume instructions for the existing character workflow.

No provider calls, model switches, generations, reviews, promotion, or scene
changes. A packet is a handoff, never proof of a Luna production run.
"""
from pathlib import Path
import hashlib
import json
import character_workflow as workflow
from source_alpha_policy import (requirement as alpha_requirement,
                                 validate_request_references)

CORE = ('character_workflow.py', 'character_handoff.py', 'source_alpha_policy.py', 'enemy_body_plan.py', 'improvement_harness.py', 'compact_atlas.py', 'README_KO.md',
        'web_alpha_bridge.py',
        'gait_contract.py', 'cycle_review.py', 'cycle_preview.py', 'cycle_live_review.js', 'runtime_observations.py', 'source_provenance.py',
        'new_character.py', 'build_character.py', 'build_atlas.py', 'intake_frame.py', 'intake_pair.py', 'preview_gait.py',
        'package_standalone.py', 'validate_character.py', 'intake_derived_frame.py', 'locomotion_review.py', 'motion_evidence.py',
        'public/keyboard-input.js', 'public/combat-aim.js', 'public/simulation.js', 'public/atlas-renderer.js', 'public/studio.js',
        'public/qa/combat-checks.js', 'public/qa/locomotion-checks.js', 'public/qa/capture-motion.js')
REFERENCES = ('SKILL.md', 'references/authoring.md', 'references/gait-repair.md',
              'references/browser-check.md', 'references/reuse-improvements.md', 'references/cycle-review.md',
              'references/aim-response.md', 'references/enemy-facing.md',
              'references/local-motion-assistance.md')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fingerprint(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()

def make(character):
    lab = workflow.ROOT.resolve()
    project = lab.parent
    config = workflow.recipe(character)
    status = workflow.workflow_status(character)
    inputs = {}

    def include(path):
        path = path.resolve()
        if path == project or not path.is_relative_to(project):
            raise ValueError('Handoff input must stay in project')
        inputs[path.relative_to(project).as_posix()] = sha(path) if path.is_file() else None

    for name in CORE:
        include(lab / name)
    for name in REFERENCES:
        include(project / '.agents/skills/sable-character-studio' / name)
    if character.startswith('site7_'):
        include(project / 'data/art_profiles/site7_enemy_body_plan.json')
    include(lab / 'characters' / f'{character}.json')
    include(lab / 'AGENTS.md')
    for path in (lab / 'tests').glob('*'):
        if path.is_file() and (path.suffix == '.py' or path.name.endswith('.test.js')):
            include(path)
    if config.get('identityReference'):
        include(workflow.local(config['identityReference']))
    for row in status['slots']:
        path = workflow.local(row['path'])
        include(path)
        receipt = path.with_suffix('.source.json')
        include(receipt)
        if receipt.is_file():
            source = workflow.read(receipt)
            for key in ('toolResponse', 'sourceMaster'):
                if source.get(key):
                    include(workflow.local(source[key]['path']))
            for key in ('normalization','mask'):
                entry=source.get('derivation',{}).get(key)
                if isinstance(entry,dict) and entry.get('path'):include(workflow.local(entry['path']))
    include(lab / 'art' / character / 'requests.json')
    requests_path=lab / 'art' / character / 'requests.json'
    if requests_path.is_file():
        for request in workflow.read(requests_path):
            # Validate request inputs before binding their hashes. This keeps
            # another project's image or managed staging file from entering a
            # Luna packet through a hand-edited manifest.
            validate_request_references(request, lab,
                                        config.get('identityReference'))
            if request.get('poseGuide'):include(workflow.local(request['poseGuide']))
    for relative in (f'qa/{character}/source_reviews.json', f'qa/{character}/runtime_reviews.json', f'qa/{character}/cycle_reviews.json',
                     f'dist/{character}.package.json', f'dist/{character}.delivery.json',
                     f'public/assets/atlas/{character}/profile.json'):
        path = workflow.local(relative)
        include(path)
        if path.is_file() and path.name.endswith('_reviews.json'):
            for row in workflow.read(path):
                for key in ('evidence', 'motionEvidence', 'motionCapture', 'locomotion', 'packet','observations'):
                    if isinstance(row.get(key), dict) and row[key].get('path'):
                        bound=workflow.local(row[key]['path']);include(bound)
                        if key=='packet' and bound.is_file():
                            packet=workflow.read(bound)
                            if packet.get('preview'):
                                pp=workflow.local(packet['preview']['path']);include(pp)
                                if pp.is_file():
                                    for evidence_key in ('video','atlas','contact'):
                                        entry=workflow.read(pp).get(evidence_key)
                                        if entry:include(workflow.local(entry['path']))
    profile_path = lab / f'public/assets/atlas/{character}/profile.json'
    if profile_path.is_file():
        profile = workflow.read(profile_path)
        if profile.get('id') != character:
            raise ValueError('Runtime profile identity differs from handoff')
        for view in profile.get('views', {}).values():
            for clip in view.values():
                if isinstance(clip, dict) and clip.get('image'):
                    include(workflow.local('public/' + clip['image']))
                if isinstance(clip, dict):
                    for source in clip.get('sources', []):
                        if source.get('source'):
                            include(workflow.local(source['source']))
        for relative in (f'public/assets/atlas/{character}/portrait.png', 'public/style.css',
                         'public/index.html', 'public/assets/Rajdhani-Medium.ttf'):
            include(workflow.local(relative))
        if profile.get('animation', {}).get('presentation') != 'authored_frames':
            selected = None
            for name in ('coherent', 'fire'):
                possible = workflow.local(f'public/assets/atlas/{character}/{name}/manifest.json')
                include(possible)
                if selected is None and possible.is_file():
                    selected = possible
            if selected:
                for entry in workflow.read(selected).get('directions', {}).values():
                    for key in ('idle','walk','run','move','fire','upper','idleLower','moveLower'):
                        if entry.get(key):
                            include(workflow.local('public/' + entry[key]))
    errors = list(status['errors'])
    if status['mode'] != 'existing-runtime' and status['errors']:
        action = 'REPAIR_SOURCE_STATUS_ERRORS'
    elif status['mode'] == 'existing-runtime':
        action = 'VERIFY_EXISTING_RUNTIME'
    elif status.get('runtimeRepairRequired'):
        action = 'REPAIR_RUNTIME_VISUAL'
    elif any(r['state'] in ('repair', 'source_alpha_repair') for r in status['slots']):
        action = 'REPAIR_REPORTED_SOURCE'
    elif isinstance(status.get('next'),dict) and status['next'].get('kind')=='cycle-source-repair':
        action = 'REPAIR_REPORTED_CYCLE_SOURCE'
    elif isinstance(status.get('next'),dict) and status['next'].get('kind')=='cycle-review':
        action = 'REVIEW_WHOLE_CYCLE'
    elif status['ready']:
        action = 'BUILD_REVIEWED_SOURCES'
    else:
        action = 'COMPLETE_OR_REVIEW_NEXT_SOURCE'
    candidate = None
    if character == 'rook':
        from improvement_harness import verify_r3
        try:
            candidate = verify_r3(project)
            inputs.update(candidate.pop('inputs'))
        except (ValueError, OSError, KeyError, TypeError) as error:
            candidate = {'status': 'STALE_OR_MISSING_EVIDENCE', 'error': str(error), 'productionPromotion': False}
            errors.append('Frozen R3 reuse evidence is unavailable/stale; do not regenerate retired inputs or claim its old result: ' + str(error))
        weapon_path = project / 'data/progression/weapons.json'
        include(weapon_path)
        if weapon_path.is_file():
            expected = next((row for row in workflow.read(weapon_path)['weapons']
                             if row.get('default_for') == 'CHR_PROTO_02'), None)
            if expected:
                mismatches = {key: {'recipe': config.get('weapon', {}).get(key), 'game': expected[game_key]}
                              for key, game_key in (('magazine','magazine_size'), ('fireInterval','fire_interval'),
                                                    ('reloadSeconds','reload_duration'))
                              if config.get('weapon', {}).get(key) != expected[game_key]}
                if mismatches:
                    errors.append('ROOK art scaffold weapon values differ from the actual game: ' + json.dumps(mismatches))
        errors.append('Before new ROOK HTML gameplay integration, verify movement-unit mapping and scattergun pellet behavior; an art scaffold is not a gameplay parity receipt.')
    ready_core = (all(inputs.get((lab / name).relative_to(project).as_posix()) for name in CORE)
                  and all(inputs.get(('.agents/skills/sable-character-studio/' + name)) for name in REFERENCES))
    if not ready_core:
        errors.append('Required current workflow module missing; repair installation before executing the packet')
    next_source = status.get('next')
    affected_direction = (next_source.get('slot','E/').split('/')[0] if 'slot' in next_source else next_source.get('direction','E')) if isinstance(next_source, dict) else 'E'
    affected_action = (next_source['slot'].split('/')[1] if 'slot' in next_source else next_source.get('action','walk')) if isinstance(next_source,dict) else 'walk'
    if affected_action=='idle':affected_action='walk'
    return {'kind': 'sable-character-handoff', 'schema': 1, 'recordedAt': workflow.stamp(),
            'character': character, 'route': 'motion_lab_v1/authored_frames',
            'status': 'READY_TO_RESUME' if ready_core else 'NEEDS_WORKFLOW_FIX',
            'nextAction': action, 'nextSource': status.get('next'), 'sourceStatus': status,
            'candidateEvidence': candidate, 'warnings': errors,
            'sourceArtPolicy': alpha_requirement(),
            'reference': config.get('identityReference'), 'recipe': f'characters/{character}.json',
            'commands': {'status': f'character_workflow.py status --character {character}',
                         'previewAffectedCycle': f'preview_gait.py --character {character} --direction {affected_direction} --action {affected_action}',
                         'prepareCycleReview': f'character_workflow.py prepare-cycle --character {character} --direction {affected_direction} --action {affected_action}',
                         'buildOnlyWhenReady': f'character_workflow.py build --character {character}',
                         'packageAfterBuild': f'package_standalone.py --character {character}',
                         'regressionPython': '-B -m unittest discover -s tests -p test_*.py',
                         'regressionNode': 'node --test tests/*.test.js'},
            'requiredReading': [str(project / '.agents/skills/sable-character-studio' / n) for n in REFERENCES],
            'boundaries': ['This packet authorizes no generation, model switch, delegation or deployment',
                           'Use actual reference and recipe; no copied character pixels or split-leg fallback',
                           'Repair known failures before expanding views; inspect real E idle/opposite contacts and chronological cycle',
                           'Two same-category source failures require changing the failed approach, not blind retries',
                           'Technical fixtures and pinned R3 evidence are NOT Luna production success',
                           'Actual source and native temporal runtime reviews still required for delivery'],
            'lunaGenerationTested': False, 'reviewedDelivery': False,
            'inputs': inputs, 'inputSHA256': fingerprint(inputs)}

def verify(packet_path):
    packet = workflow.read(workflow.local(packet_path))
    if packet.get('kind') != 'sable-character-handoff' or packet.get('schema') != 1:
        raise ValueError('Not a current character handoff')
    if packet.get('inputSHA256') != fingerprint(packet['inputs']):
        raise ValueError('Handoff fingerprint differs')
    project = workflow.ROOT.resolve().parent
    for name, digest in packet['inputs'].items():
        path = (project / name).resolve()
        if path == project or not path.is_relative_to(project):
            raise ValueError('Handoff input escapes project')
        if (sha(path) if path.is_file() else None) != digest:
            raise ValueError('Stale handoff input: ' + name)
    fresh = make(packet['character'])
    if fresh['inputs'] != packet['inputs'] or fresh['sourceStatus'] != packet['sourceStatus']:
        raise ValueError('Source choice or current dependency set changed; recreate handoff')
    for key in ('route','status','nextAction','nextSource','candidateEvidence','warnings','commands',
                'reference','recipe','sourceArtPolicy','requiredReading','boundaries','lunaGenerationTested','reviewedDelivery'):
        if packet.get(key) != fresh[key]:
            raise ValueError('Handoff instructions or conclusions were changed: ' + key)
    return {'status': 'CURRENT_HANDOFF', 'character': packet['character'],
            'inputSHA256': packet['inputSHA256'], 'nextAction': fresh['nextAction'],
            'reviewedDelivery': False, 'lunaGenerationTested': False}
