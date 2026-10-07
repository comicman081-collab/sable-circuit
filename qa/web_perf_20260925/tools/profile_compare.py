"""Compare combat CPU profiles (web_profile.py output) with the statically identified names.

usage: python profile_compare.py <out.json> <label>=<combat.cpuprofile> [...]
"""
import collections
import json
import sys
from pathlib import Path

NAMES = {
    'wasm-function[2238]': 'GDScriptFunction::call (GDScript VM)',
    'wasm-function[43559]': 'GDScript::callp',
    'wasm-function[18792]': 'Main::iteration',
    'wasm-function[65213]': 'SceneTree::physics_process',
    'wasm-function[65205]': 'SceneTree::process',
    'wasm-function[18718]': 'RendererViewport::draw_viewports',
    'wasm-function[67320]': 'RasterizerCanvasGLES3::canvas_render_items',
    'wasm-function[65926]': 'CanvasItem::_redraw_callback',
    'wasm-function[67307]': 'RasterizerCanvasGLES3::request_polygon',
    'wasm-function[67306]': 'RasterizerCanvasGLES3::free_polygon',
}
JS = ['getParameter', 'isEnabled', 'createVertexArray', 'deleteVertexArray', 'createBuffer', 'bufferData',
      'checkFramebufferStatus', '(idle)', '(program)', '(garbage collector)']


def summarise(path):
    profile = json.loads(Path(path).read_text(encoding='utf-8'))
    nodes = {n['id']: n for n in profile['nodes']}
    parent = {}
    for n in profile['nodes']:
        for c in n.get('children', []):
            parent[c] = n['id']
    self_us = collections.Counter()
    for sample, delta in zip(profile['samples'], profile['timeDeltas']):
        self_us[sample] += delta
    total = sum(self_us.values())
    label = lambda nid: nodes[nid]['callFrame']['functionName'] or '(anonymous)'
    by_self = collections.Counter()
    inclusive = collections.Counter()
    for nid, us in self_us.items():
        by_self[label(nid)] += us
        seen = set()
        x = nid
        while x is not None:
            name = label(x)
            if name not in seen:
                inclusive[name] += us
                seen.add(name)
            x = parent.get(x)
    rows = {}
    for key in list(NAMES) + JS:
        rows[NAMES.get(key, key)] = {'function': key, 'self_share': round(by_self[key] / total, 4),
                                     'inclusive_share': round(inclusive[key] / total, 4)}
    return {'profiled_ms': round(total / 1000, 1), 'functions': rows}


def main():
    out = Path(sys.argv[1])
    report = {label: summarise(path) for label, path in (a.split('=', 1) for a in sys.argv[2:])}
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    labels = list(report)
    print(f"{'function':48s}" + ''.join(f'{l:>22s}' for l in labels))
    for name in report[labels[0]]['functions']:
        cells = ''.join(f"{report[l]['functions'][name]['self_share']*100:9.1f}% /{report[l]['functions'][name]['inclusive_share']*100:6.1f}%  " for l in labels)
        print(f'{name:48s}{cells}')


if __name__ == '__main__':
    main()
