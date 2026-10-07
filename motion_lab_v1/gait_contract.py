"""One maintained six-phase vocabulary for requests, previews and reviews."""
import hashlib
import json

VERSION = 1
PHASES = (
    {'index': 0, 'name': 'left_contact', 'support': 'double', 'lead': 'left',
     'prompt': 'right leg trailing / left forward contact'},
    {'index': 1, 'name': 'right_swing', 'support': 'left', 'lead': None,
     'prompt': 'right leg swings behind / left supports'},
    {'index': 2, 'name': 'right_passing', 'support': 'left', 'lead': None,
     'prompt': 'right knee passes forward / left supports'},
    {'index': 3, 'name': 'right_contact', 'support': 'double', 'lead': 'right',
     'prompt': 'left leg trailing / right forward contact'},
    {'index': 4, 'name': 'left_swing', 'support': 'right', 'lead': None,
     'prompt': 'left leg swings behind / right supports'},
    {'index': 5, 'name': 'left_passing', 'support': 'right', 'lead': None,
     'prompt': 'left knee passes forward / right supports'},
)
# Accepted ASTER contact-dwell starting point; visual calibration remains required.
WALK_PHASE_STARTS = [0, .2, .33, .5, .7, .83]


def digest():
    return hashlib.sha256(json.dumps({'version': VERSION, 'phases': PHASES,
        'walkPhaseStarts': WALK_PHASE_STARTS}, sort_keys=True).encode()).hexdigest()


def starts(spec):
    values = spec.get('phaseStarts', [i / 6 for i in range(6)])
    if (len(values) != 6 or values[0] != 0 or
            any(type(v) not in (int, float) or not 0 <= v < 1 for v in values) or
            any(b <= a for a, b in zip(values, values[1:]))):
        raise ValueError('Invalid six-phase timing')
    return values


def frame_at(phase, phase_starts):
    p = phase % 1
    return max(i for i, start in enumerate(phase_starts) if p >= start)
