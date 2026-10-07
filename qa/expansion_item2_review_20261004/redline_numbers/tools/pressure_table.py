"""Claude review helper (REDLINE number study, 2026-10-04): the arithmetic behind order doc 9.11.
Reads the four standard hazard cards from data/progression/run_modifiers.json and compares them with REDLINE before and after.
P = HP x damage / attack gap is a rule-of-thumb for the hit intake needed to kill the same enemies when the player plays the same way
(longer kill time x bigger hit x more hits); speed is not in it.  k = (hazard reward - 1) / (P - 1) is the reward paid per unit of added pressure.
usage (project root): python pressure_table.py [out.md]"""
import json
import math
import sys
from pathlib import Path

data = json.loads(Path('data/progression/run_modifiers.json').read_text(encoding='utf-8'))
OPP = {o['id']: o for o in data['opportunities']}
cards = []
for h in data['hazards']:
    cards.append((h['id'], float(h['enemy_health_multiplier']), float(h['enemy_damage_multiplier']), float(h['enemy_speed_multiplier']),
                  float(h['enemy_attack_interval_multiplier']), float(h['reward_multiplier'])))
cards.append(('REDLINE before (e091e25f)', 1.50, 1.35, 1.15, 0.80, 1.60))
cards.append(('REDLINE after (this change)', 1.35, 1.25, 1.12, 0.85, 1.60))
HP = {'ASTER': 96, 'ROOK': 138, 'MICA': 112}
out = ['| card | HP | damage | speed | gap | P | boss warning hit | hits to down ASTER/ROOK/MICA | hazard reward | k |', '|---|---:|---:|---:|---:|---:|---:|---|---:|---:|']
for name, h, d, s, g, r in cards:
    p = h * d / g
    warn = 20 * d
    hits = '/'.join(str(math.ceil(HP[k] / warn - 1e-9)) for k in ('ASTER', 'ROOK', 'MICA'))
    out.append('| %s | %.2f | %.2f | %.2f | %.2f | %.3f | %.1f | %s | %.2f | %.2f |' % (name, h, d, s, g, p, warn, hits, r, (r - 1) / (p - 1)))

best = {}
for res in ('research', 'salvage', 'fragment'):
    best[res] = max(float(o['%s_reward_multiplier' % res]) for o in OPP.values()) * max(float(h['reward_multiplier']) for h in data['hazards'])
lab = 1.72
out += ['', 'best standard reward factor (strongest hazard reward x strongest opportunity of that resource): ' +
        ', '.join('%s x%.3f' % (k, v) for k, v in best.items()),
        'REDLINE reward factor (unchanged): 1.60 x 1.50 = x2.40 on all three resources = x%.2f of the best standard research, x%.2f of the best standard salvage/fragment;' % (2.4 / best['research'], 2.4 / best['salvage']),
        'research at the maximum lab (+72 %%): REDLINE x%.2f, best standard x%.2f.' % (2.4 * lab, best['research'] * lab)]
text = '\n'.join(out) + '\n'
if len(sys.argv) > 1:
    Path(sys.argv[1]).write_text(text, encoding='utf-8', newline='\n')
sys.stdout.buffer.write(text.encode('utf-8'))
