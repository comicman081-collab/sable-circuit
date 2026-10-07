"""Verify reusable R3 evidence without promoting it or rerunning generation.

The pinned historical inventory proves only the selected evidence bytes. Shared
skill documentation may evolve; it is deliberately not treated as frozen game
code. Performance FAIL and source HOLD remain distinct from technical reuse.
"""
from pathlib import Path
import hashlib
import json
import math
import statistics
from compact_atlas import require, verify as verify_atlas

PILOT = Path('motion_lab_v1/pilots/rook_completion_v3')
SEAL_SHA256 = '591e2f8371047e6c3c77bb93d4699980b6a5612191f62ceb4178cbe46bbac7f0'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def check_bindings(root, values):
    require(isinstance(values, dict) and bool(values), 'Missing input bindings')
    for name, digest in values.items():
        path = (root / name).resolve()
        require(path != root.resolve() and path.is_relative_to(root.resolve()), 'Evidence input escapes project')
        require(path.is_file() and sha(path) == digest, 'Stale evidence input: ' + name)

def evaluate_performance(baseline, candidate):
    require(len(baseline) == len(candidate) == 3, 'Use all three declared paired repeats')
    for row in baseline + candidate:
        for key in ('p95_ms', 'p99_ms'):
            value = row[key]
            require(type(value) in (int, float) and math.isfinite(value) and value > 0, 'Invalid timing value')
        require(row['p99_ms'] >= row['p95_ms'], 'Invalid percentile ordering')
        require(row['squad_count'] == 3 and row['end_hostiles'] == 3, 'Scene population mismatch')
    ratio = statistics.median(r['p95_ms'] for r in candidate) / statistics.median(r['p95_ms'] for r in baseline)
    absolute = all(r['p95_ms'] <= 16.67 and r['p99_ms'] <= 33.33 for r in candidate)
    return {'status': 'PASS' if absolute and ratio <= 1.10 else 'FAIL',
            'p95_median_ratio': ratio, 'absolute_budget_met': absolute,
            'relative_budget_met': ratio <= 1.10,
            'scope': 'ROOK pilot predeclared 1080p 3+3 desktop comparison; not a global device budget',
            'thresholds': {'p95_ms': 16.67, 'p99_ms': 33.33, 'p95_median_ratio': 1.10}}

def verify_r3(root):
    root = root.resolve()
    folder = root / PILOT
    require(not (folder / 'active-run.lock').exists(), 'Owned pilot still running; do not overlap validation')
    seal_path = folder / 'deliverables.json'
    require(sha(seal_path) == SEAL_SHA256, 'R3 historical inventory changed; do not relabel old evidence')
    inventory = {row['path']: row['sha256'] for row in read(seal_path)['files']}
    inspected = {seal_path.relative_to(root).as_posix(): SEAL_SHA256}

    def bound(name):
        path = folder / name
        key = path.relative_to(root).as_posix()
        require(key in inventory, 'Not in R3 sealed evidence: ' + name)
        check_bindings(root, {key: inventory[key]})
        inspected[key] = inventory[key]
        return read(path) if path.suffix == '.json' else path

    def process(name):
        value = bound(name)
        require(value['exit_code'] == 0 and value['inputs_unchanged_during_run'] is True, 'Failed or mutable run')
        check_bindings(root, value['input_hashes'])
        inspected.update(value['input_hashes'])

    bound('pilot_runtime.gd')
    bound('pilot_test.gd')
    bound('run_pilot.py')
    bound('compact/manifest.json')
    compact = verify_atlas(root, folder / 'compact/manifest.json')
    manifest = read(folder / 'compact/manifest.json')
    inspected[manifest['source_descriptor']['path']] = manifest['source_descriptor']['sha256']
    for page in manifest['directions'].values():
        inspected[page['texture']] = page['sha256']
        inspected.update({s['path']: s['sha256'] for s in page['sources']})
    perf = {}
    for variant in ('baseline', 'candidate_v3'):
        perf[variant] = []
        for repeat in (10, 11, 12):
            process(f'perf_{variant}_{repeat}.process.json')
            perf[variant].append(bound(f'perf_{variant}_{repeat}.json'))
    performance = evaluate_performance(perf['baseline'], perf['candidate_v3'])
    matrix = []
    for hz, repeat in ((30, 6), (60, 5), (120, 7)):
        process(f'matrix_candidate_v3_{repeat}.process.json')
        report = bound(f'candidate_v3_matrix_{hz}hz.json')
        require(report['count'] == 72 and len(report['rows']) == 72, 'Incomplete runtime matrix')
        passed = sum(row['technical'] == 'PASS' for row in report['rows'])
        require(passed == 72 and report['reload_gameplay'] is True, 'R3 technical regression')
        require(report['live_input']['diagonal_keys'] is True and report['live_input']['stopped'] is True, 'Input regression')
        matrix.append({'hz': hz, 'passed': passed, 'count': 72, 'scope': 'TECHNICAL_NOT_ANATOMICAL'})
    process('temporal_candidate_v3_2.process.json')
    temporal = bound('candidate_v3_temporal_60hz.json')
    require(len(temporal['rows']) == 32 and all(r['technical'] == 'PASS' for r in temporal['rows']), 'Temporal regression')
    require(all(temporal[k] is True for k in ('hit_gameplay', 'downed_blocks_fire', 'revived_fire')), 'State transition regression')
    for name in ('improvement_harness.py', 'compact_atlas.py'):
        path = root / 'motion_lab_v1' / name
        inspected[path.relative_to(root).as_posix()] = sha(path)
    return {'status': 'VERIFIED_LIMITED_REUSE', 'scope': 'Frozen R3 technical evidence; no new game run',
            'productionPromotion': False, 'newCharacterComplete': False, 'lunaGenerationTested': False,
            'reusable': ['lossless_explicit_cell_packing', 'distance_phase_and_selected_cell_commit_before_fire',
                         'preserve_stationary_recoil_feet', 'candidate_selection_before_first_texture_load',
                         'owned_bounded_exclusive_runner_with_input_hashes'],
            'compact': compact, 'matrix': matrix, 'temporalPassed': 32, 'performance': performance,
            'sourceVisualStatus': 'HOLD',
            'limits': ['No approved new ROOK art cycle', 'No dedicated strafe/sprint/reload-hand/hit art',
                       'Godot fast-runtime adapter is isolated; do not graft it into the authored-frame browser renderer',
                       'A new implementation or changed input needs fresh execution/evidence'],
            'inputs': inspected}
