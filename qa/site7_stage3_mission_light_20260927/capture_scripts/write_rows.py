"""Writes the mission rows of data/visual/site7_mood.json, including each mission's
own rows for the stage 3 plates that missions 3-5 share. Keeps the shared
"plates" section text untouched."""
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[2] / 'data' / 'visual' / 'site7_mood.json'
S3 = 'assets/environments/site7_v2/stage03/%s/%s_GAME.png'
text = PATH.read_text(encoding='utf-8')
mood = json.loads(text)
shared = mood['plates']
missions = mood['missions']

# Where a light sits on each floor template (texture coordinates).
BACK = {'S3_R01': [0.52, 0.34], 'S3_R02': [0.52, 0.34], 'S3_R03': [0.6, 0.36], 'S3_R04': [0.42, 0.4],
        'S3_R05': [0.7, 0.4], 'S3_R06': [0.55, 0.4], 'S3_O01': [0.6, 0.36], 'S3_O02': [0.6, 0.36]}
FRONT = {'S3_R01': [0.5, 0.8], 'S3_R02': [0.5, 0.8], 'S3_R03': [0.5, 0.8], 'S3_R04': [0.5, 0.8],
         'S3_R05': [0.5, 0.8], 'S3_R06': [0.45, 0.76], 'S3_O01': [0.55, 0.76], 'S3_O02': [0.55, 0.76]}
MIDDLE = {'S3_R01': [0.5, 0.56], 'S3_R02': [0.5, 0.56], 'S3_R03': [0.5, 0.56], 'S3_R04': [0.5, 0.56],
          'S3_R05': [0.55, 0.52], 'S3_R06': [0.5, 0.55], 'S3_O01': [0.52, 0.55], 'S3_O02': [0.52, 0.55]}
ROOMS = list(BACK)


def asset(plate):
    return S3 % (plate, plate)


# Mission 3 CORE PRESSURE: dark steel under red emergency light. Every room has a
# dim red emergency fill and a red alarm light that pulses (the painted red lamps
# of S3_R01/R02 strobe themselves); cool painted lamps are dimmed so red leads.
missions['MIS_CH01_03'].update({'exposure': -0.3, 'tint': [1.02, 0.97, 1.0], 'saturation': 1.1, 'contrast': 1.2})
m3 = {}
alarm_hz = {'S3_R01': 1.0, 'S3_R02': 1.1, 'S3_R03': 0.9, 'S3_R04': 1.0, 'S3_R05': 0.7, 'S3_R06': 1.2, 'S3_O01': 0.95, 'S3_O02': 0.85}
cool = {'S3_R03', 'S3_R06', 'S3_O02'}
for plate in ROOMS:
    row = {'fill': {'strength': 0.12, 'color': [1.0, 0.22, 0.16], 'reach': 0.7}}
    lights = [dict(light) for light in shared[asset(plate)].get('lights', [])]
    if plate in ('S3_R01', 'S3_R02'):
        # Their painted lamps are red: the lamps themselves strobe.
        row['lamps'] = dict(shared[asset(plate)]['lamps'], pulse=[alarm_hz[plate], 0.55])
    else:
        lights.append({'at': MIDDLE[plate], 'radius': 640, 'color': [1.0, 0.12, 0.08], 'strength': 0.4, 'pulse': [alarm_hz[plate], 0.6]})
    if plate in cool:
        row['lamps'] = dict(shared[asset(plate)]['lamps'], strength=0.5)
        row['tint'] = [1.02, 0.97, 0.99]
    if plate in ('S3_R04', 'S3_O01'):
        row['tint'] = [1.02, 0.97, 0.98]
    if lights:
        row['lights'] = lights
    m3[asset(plate)] = row
missions['MIS_CH01_03']['plates'] = m3

# Mission 4 FORGE DESCENT: heat rising from the crust below grows with depth, a
# warm overhead fill, steady lamps (no strobes); cool painted lamps are dimmed so
# the heat owns the floor.
heat = {'S3_R06': 0.16, 'S3_R04': 0.24, 'S3_R01': 0.32, 'S3_O01': 0.28, 'S3_R02': 0.38, 'S3_O02': 0.34, 'S3_R05': 0.46, 'S3_R03': 0.5}
cool = {'S3_R03', 'S3_R05', 'S3_R06', 'S3_O02'}
m4 = {}
for plate in ROOMS:
    h = heat[plate]
    m4[asset(plate)] = {
        'exposure': round(-0.42 + h * 0.5, 2), 'tint': [1.1, 0.98, 0.86], 'saturation': 1.1,
        'lamps': {'strength': 0.55 if plate in cool else 0.85, 'radius': 210},
        'fill': {'strength': round(0.08 + h * 0.2, 3), 'color': [1.0, 0.62, 0.3]},
        'lights': [{'at': FRONT[plate], 'radius': 540, 'color': [1.0, 0.36, 0.08], 'strength': h, 'pulse': [0.17 + h * 0.1, 0.3]}],
        'haze': [1.0, 0.5, 0.2],
    }
missions['MIS_CH01_04']['plates'] = m4

# Mission 5 OFFSHORE NULL: grey storm light through the rig, cold overhead fill,
# dim warm lamps, a slow rig beacon passing over each room; only the carrier's red
# lamps (the boss room on S3_R02) keep their warning pulse.
warm = {'S3_R01', 'S3_R02', 'S3_R04', 'S3_O01'}
beacon_hz = {'S3_R01': 0.1, 'S3_R05': 0.12, 'S3_R03': 0.09, 'S3_R04': 0.11, 'S3_R02': 0.08, 'S3_R06': 0.1, 'S3_O01': 0.13, 'S3_O02': 0.12}
m5 = {}
for plate in ROOMS:
    row = {
        'exposure': -0.38, 'tint': [0.92, 1.0, 1.1], 'saturation': 0.85,
        'lamps': {'strength': 0.5 if plate in warm else 0.75, 'radius': 200},
        'fill': {'strength': 0.12, 'color': [0.7, 0.86, 1.0], 'reach': 0.6},
        'lights': [{'at': BACK[plate], 'radius': 560, 'color': [0.75, 0.9, 1.0], 'strength': 0.22, 'pulse': [beacon_hz[plate], 0.9]}],
        'haze': [0.6, 0.8, 1.0],
    }
    if plate == 'S3_R02':
        row['lamps'] = {'strength': 0.95, 'radius': 220, 'pulse': [0.3, 0.3]}
        row['exposure'] = -0.45
    m5[asset(plate)] = row
missions['MIS_CH01_05']['plates'] = m5


def inline(value):
    return json.dumps(value, separators=(', ', ': '))


lines = ['  "missions": {']
names = list(missions)
for n, name in enumerate(names):
    row = missions[name]
    lines.append('    %s: {' % json.dumps(name))
    body = []
    body.append(', '.join('%s: %s' % (json.dumps(k), inline(row[k])) for k in ('exposure', 'tint', 'saturation') if k in row))
    body.append(', '.join('%s: %s' % (json.dumps(k), inline(row[k])) for k in ('contrast', 'pivot', 'shadows') if k in row))
    body.append('"abyss": %s' % inline(row['abyss']))
    extra = [k for k in row if k not in ('exposure', 'tint', 'saturation', 'contrast', 'pivot', 'shadows', 'abyss', 'plates')]
    assert not extra, extra
    if row.get('plates'):
        plates = list(row['plates'].items())
        block = '"plates": {\n' + ',\n'.join('        %s: %s' % (json.dumps(a), inline(v)) for a, v in plates) + '\n      }'
        body.append(block)
    lines.append(',\n'.join('      ' + b for b in body if b))
    lines.append('    }' + (',' if n < len(names) - 1 else ''))
lines.append('  },')
start = text.index('  "missions": {')
end = text.index('\n  "plates": {') + 1
out = text[:start] + '\n'.join(lines) + '\n' + text[end:]
assert json.loads(out)['plates'] == shared
PATH.write_text(out, encoding='utf-8', newline='\n')
print('wrote', PATH)
