"""Read-only audit: probe validators using in-memory copies, never QA receipts."""
import copy
import hashlib
import json
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(LAB))
from locomotion_review import validate_report


def main():
    report = json.loads((LAB / 'qa/rook_locomotion_browser.json').read_text(encoding='utf-8'))
    script_sha = hashlib.sha256((LAB / 'public/qa/locomotion-checks.js').read_bytes()).hexdigest()
    digest = report['build']['inputSHA256']
    result = {'kind': 'negative-validator-audit', 'productionReceiptsModified': False,
              'inputSHA256': digest, 'probes': []}

    def probe(name, candidate):
        try:
            accepted = validate_report(candidate, 'rook', digest, script_sha)
            result['probes'].append({'name': name, 'validatorAccepted': accepted})
        except ValueError as error:
            result['probes'].append({'name': name, 'validatorAccepted': False, 'error': str(error)})

    probe('unchanged actual report', report)
    scrambled = copy.deepcopy(report)
    permutation = [0, 3, 1, 4, 2, 5]
    for row in scrambled['results']:
        if row['stationary']:
            continue
        for sample in row['samples']:
            sample['frame'] = permutation[sample['frame']]
        row['frames'] = sorted({sample['frame'] for sample in row['samples']})
    probe('impossible chronological order while preserving six frame IDs', scrambled)

    frozen = copy.deepcopy(report)
    for row in frozen['results']:
        for sample in row['samples']:
            sample.update(time=0, phase=0, position=[0, 0])
    probe('all sampled times, phases and positions frozen; original travel summaries retained', frozen)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
