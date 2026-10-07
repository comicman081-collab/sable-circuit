"""Summarise operation 10 bot runs: python bot_stats10.py <dir with full_operation.json> ... (JSON per run). Room names by main-route step."""
import json
import sys
from collections import defaultdict

ROOMS = {1: 'R02_RELAY', 2: 'R03_LOG', 3: 'R04_GALLERY', 4: 'R05_CORE', 5: 'R06_EXIT'}


def stats(path):
    j = json.load(open(path, encoding='utf-8'))
    r = j['result']
    by_room, by_source = defaultdict(float), defaultdict(float)
    for k, v in j['damage_by_source'].items():
        step, _op, src = k.split(':', 2)
        by_room[ROOMS.get(int(step), step)] += v
        by_source[src] += v
    tr = j['trace']
    downs, state = [], {}
    for t in tr:
        for i, h in enumerate(t['health']):
            if h <= 0 and not state.get(i):
                downs.append({'operator': i, 'tick': t['tick'], 'room': ROOMS.get(t['step'], t['step'])})
                state[i] = True
            elif h > 0 and state.get(i):
                state[i] = False
                downs[-1:] = downs[-1:]  # keep
    revived = [i for i, down in state.items() if not down]
    return {
        'status': j['status'], 'outcome': r.get('outcome'), 'game_secs': round(r.get('elapsed_seconds', 0), 1),
        'kills': r.get('hostiles_defeated'), 'full_route_cleared': r.get('full_route_cleared'),
        'research': r.get('secured_research'), 'salvage': r.get('secured_salvage'), 'fragments': r.get('secured_fragments'),
        'intel': r.get('secured_intel'), 'extraction_depth': r.get('extraction_depth'), 'ledger_recovered': r.get('ledger_recovered'),
        'carrier_fragment_secured': r.get('carrier_fragment_secured'),
        'dmg_by_room': {k: round(v, 1) for k, v in sorted(by_room.items())}, 'dmg_total': round(sum(by_room.values()), 1),
        'dmg_by_source': {k: round(v, 1) for k, v in sorted(by_source.items(), key=lambda kv: -kv[1])},
        'final_hp': [round(h, 1) for h in tr[-1]['health']], 'down_events': downs,
        'ended_down': [i for i, h in enumerate(tr[-1]['health']) if h <= 0],
        'skill_casts': sum(j['skill_casts'].values()), 'failures': j['failures'],
    }


if __name__ == '__main__':
    for p in sys.argv[1:]:
        try:
            print(p, json.dumps(stats(p), ensure_ascii=False))
        except Exception as e:  # noqa
            print(p, 'ERR', e)
