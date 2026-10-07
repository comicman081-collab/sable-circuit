"""Same-session web FPS A/B: several builds, rounds rotated, one visible Edge window.

usage: python web_fps_ab.py <out_dir> <rounds> <label>=<url> [<label>=<url> ...]

Each round plays every build once (title -> intro skip -> briefing -> deploy op 1 ->
14 s of walking and firing -> 6 s more), in a rotated order so drift in machine load
spreads over all builds. HTTP cache is disabled. Screenshots go to <out_dir>/shots.
Nothing is deployed; everything stays under the project .cache.
"""
from pathlib import Path
import base64
import json
import os
import statistics
import subprocess
import sys
import time
import urllib.request

import websocket

sys.path.insert(0, str(Path(__file__).parent))
import field_check  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1]).resolve()
ROUNDS = int(sys.argv[2])
BUILDS = [tuple(a.split('=', 1)) for a in sys.argv[3:]]
SHOTS = OUT / 'shots'
SHOTS.mkdir(parents=True, exist_ok=True)
PROFILE = ROOT / '.cache' / 'edge_fps_profile'
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
W, H = 1920, 1080


def free_port():
    # Another automation session on this machine used the fixed 9333 and drove this
    # browser to its own page; take an unused ephemeral port instead.
    import socket
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        return probe.getsockname()[1]


PORT = free_port()


def listener_pid(port):
    rows = subprocess.run(['netstat', '-ano', '-p', 'TCP'], capture_output=True, text=True).stdout.splitlines()
    for row in rows:
        parts = row.split()
        if len(parts) >= 5 and parts[1] == f'127.0.0.1:{port}' and parts[3] == 'LISTENING':
            return int(parts[4])
    return None

INSTRUMENT = r"""
window.__sable = {lost: [], restored: [], frames: []};
const loop = t => { const f = window.__sable.frames; f.push(t); if (f.length > 40000) f.splice(0, 20000); requestAnimationFrame(loop); };
requestAnimationFrame(loop);
(function hook(){
  const canvas = document.querySelector('canvas');
  if (!canvas) { setTimeout(hook, 50); return; }
  canvas.addEventListener('webglcontextlost', () => window.__sable.lost.push(performance.now()));
  canvas.addEventListener('webglcontextrestored', () => window.__sable.restored.push(performance.now()));
})();
window.__sableFps = (seconds) => {
  const f = window.__sable.frames; const now = performance.now();
  const win = f.filter(t => t >= now - seconds*1000);
  if (win.length < 2) return {seconds, fps: 0, frames: win.length, p50_ms: null, p95_ms: null, max_ms: null, over_33ms: null, lost: window.__sable.lost.length};
  const gaps = []; for (let i=1;i<win.length;i++) gaps.push(win[i]-win[i-1]); gaps.sort((a,b)=>a-b);
  const q = p => +gaps[Math.min(gaps.length-1, Math.floor(gaps.length*p))].toFixed(2);
  return {seconds, fps: +((win.length-1)/((win[win.length-1]-win[0])/1000)).toFixed(1), frames: win.length,
          p50_ms: q(0.5), p95_ms: q(0.95), max_ms: q(1), over_33ms: gaps.filter(g => g > 33.4).length, lost: window.__sable.lost.length};
};
"""


class Cdp:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=120, suppress_origin=True)
        self.next_id = 0

    def call(self, method, **params):
        self.next_id += 1
        my_id = self.next_id
        self.ws.send(json.dumps({'id': my_id, 'method': method, 'params': params}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get('id') == my_id:
                if 'error' in message:
                    raise RuntimeError(f'{method}: {message["error"]}')
                return message.get('result', {})

    def eval(self, expression):
        result = self.call('Runtime.evaluate', expression=expression, awaitPromise=True, returnByValue=True)
        if 'exceptionDetails' in result:
            raise RuntimeError(str(result['exceptionDetails'])[:400])
        return result.get('result', {}).get('value')

    def click(self, x, y):
        for kind in ('mouseMoved', 'mousePressed', 'mouseReleased'):
            self.call('Input.dispatchMouseEvent', type=kind, x=x, y=y, button='left', clickCount=1)
            time.sleep(0.05)

    def key(self, name, code, vk, hold=0.08):
        self.call('Input.dispatchKeyEvent', type='rawKeyDown', key=name, code=code, windowsVirtualKeyCode=vk)
        time.sleep(hold)
        self.call('Input.dispatchKeyEvent', type='keyUp', key=name, code=code, windowsVirtualKeyCode=vk)

    def shot(self, path):
        data = self.call('Page.captureScreenshot', format='png', captureBeyondViewport=False)['data']
        path.write_bytes(base64.b64decode(data))


def wait_for_devtools():
    for _ in range(100):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json') as response:
                pages = [p for p in json.load(response) if p.get('type') == 'page']
                if pages:
                    return pages[0]['webSocketDebuggerUrl']
        except OSError:
            pass
        time.sleep(0.3)
    raise RuntimeError('DevTools endpoint did not come up')


def wait_engine_running(cdp):
    # The page draws rAF frames from the start, but the main thread stalls while the pack
    # and wasm load; wait for 3 s of steady frames after at least 8 s on the page.
    started = time.time()
    time.sleep(8.0)
    while time.time() - started < 120:
        stats = cdp.eval('window.__sableFps(3)')
        if stats and stats['fps'] >= 30 and stats['max_ms'] is not None and stats['max_ms'] < 200:
            return round(time.time() - started, 1)
        time.sleep(1.0)
    return None


def run_once(cdp, label, url, tag):
    row = {'build': label, 'url': url, 'tag': tag}
    cdp.call('Page.navigate', url=url)
    row['ready_s'] = wait_engine_running(cdp)
    time.sleep(2.0)
    row['title_fps'] = cdp.eval('window.__sableFps(4)')
    cdp.click(336, 585)            # START CAMPAIGN
    time.sleep(3.0)
    cdp.key('Enter', 'Enter', 13)   # skip intro
    time.sleep(3.5)
    cdp.click(1520, 652)           # OPEN MISSION BRIEFING
    time.sleep(2.0)
    for _ in range(7):             # step through the comms until DEPLOY shows
        cdp.click(1576, 820)
        time.sleep(1.3)
    cdp.click(1520, 972)           # DEPLOY
    time.sleep(8.0)
    cdp.key('F9', 'F9', 120)
    moves = [('d', 'KeyD', 68), ('w', 'KeyW', 87), ('d', 'KeyD', 68), ('s', 'KeyS', 83)]
    for step in range(7):
        key = moves[step % len(moves)]
        cdp.call('Input.dispatchKeyEvent', type='rawKeyDown', key=key[0], code=key[1], windowsVirtualKeyCode=key[2])
        for burst in range(4):
            cdp.click(1180 + 40 * (step % 3), 430 + 30 * (burst % 2))
            time.sleep(0.35)
        cdp.call('Input.dispatchKeyEvent', type='keyUp', key=key[0], code=key[1], windowsVirtualKeyCode=key[2])
        time.sleep(0.2)
    row['field_fps_10s'] = cdp.eval('window.__sableFps(10)')
    cdp.shot(SHOTS / f'{tag}_{label}_field.png')
    time.sleep(6.0)
    row['field_fps_late_6s'] = cdp.eval('window.__sableFps(6)')
    row['context_lost'] = cdp.eval('window.__sable.lost.length')
    row['final_url'] = cdp.eval('location.href')
    # A run counts only if its field screenshot shows the field HUD (field_check.py;
    # an FPS threshold mistook fast field runs near the 100 Hz cap for menu runs) and
    # its tab stayed on the measured page.
    in_field, row['field_region_mad'] = field_check.in_field(SHOTS / f'{tag}_{label}_field.png')
    row['valid'] = in_field and row['ready_s'] is not None and row['final_url'].startswith(url)
    print('RUN', json.dumps({k: row[k] for k in ('build', 'tag', 'ready_s', 'valid')}),
          row['title_fps']['fps'], row['field_fps_10s']['fps'], row['field_fps_late_6s']['fps'], flush=True)
    return row


def main():
    env = os.environ.copy()
    for name in ('TEMP', 'TMP'):
        folder = PROFILE / 'tmp'
        folder.mkdir(parents=True, exist_ok=True)
        env[name] = str(folder)
    browser = subprocess.Popen([
        EDGE, f'--user-data-dir={PROFILE}', f'--remote-debugging-port={PORT}',
        '--no-first-run', '--no-default-browser-check', '--disable-sync',
        '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding',
        '--disable-background-timer-throttling', '--force-device-scale-factor=1',
        f'--window-size={W},{H + 90}', '--window-position=0,0', '--new-window', 'about:blank'], env=env)
    report = {'date': '2026-09-25', 'rounds': ROUNDS, 'builds': dict(BUILDS), 'devtools_port': PORT, 'runs': []}
    try:
        endpoint = wait_for_devtools()
        owner = listener_pid(PORT)
        assert owner == browser.pid, f'DevTools port {PORT} is owned by pid {owner}, not the launched Edge {browser.pid}'
        cdp = Cdp(endpoint)
        for domain in ('Page.enable', 'Runtime.enable', 'Network.enable'):
            cdp.call(domain)
        cdp.call('Network.clearBrowserCache')
        cdp.call('Network.setCacheDisabled', cacheDisabled=True)
        cdp.call('Emulation.setDeviceMetricsOverride', width=W, height=H, deviceScaleFactor=1, mobile=False)
        cdp.call('Page.addScriptToEvaluateOnNewDocument', source=INSTRUMENT)
        report['gpu_renderer'] = cdp.eval("(() => { const g = document.createElement('canvas').getContext('webgl2'); const d = g && g.getExtension('WEBGL_debug_renderer_info'); return d ? g.getParameter(d.UNMASKED_RENDERER_WEBGL) : null; })()")
        for round_index in range(ROUNDS):
            order = BUILDS[round_index % len(BUILDS):] + BUILDS[:round_index % len(BUILDS)]
            for label, url in order:
                try:
                    report['runs'].append(run_once(cdp, label, url, f'r{round_index + 1}'))
                except Exception as error:
                    report['runs'].append({'build': label, 'tag': f'r{round_index + 1}', 'error': str(error)[:300], 'valid': False})
                    print('RUN_ERROR', label, str(error)[:200], flush=True)
        summary = {}
        for label, _ in BUILDS:
            rows = [r for r in report['runs'] if r['build'] == label and r.get('valid')]
            summary[label] = {
                'valid_runs': len(rows),
                'title_median': statistics.median([r['title_fps']['fps'] for r in rows]) if rows else None,
                'field10_median': statistics.median([r['field_fps_10s']['fps'] for r in rows]) if rows else None,
                'late6_median': statistics.median([r['field_fps_late_6s']['fps'] for r in rows]) if rows else None,
                'field10_all': [r['field_fps_10s']['fps'] for r in rows],
                'late6_all': [r['field_fps_late_6s']['fps'] for r in rows],
            }
        report['summary'] = summary
        print('SUMMARY', json.dumps(summary), flush=True)
        try:
            cdp.call('Browser.close')
        except Exception:
            pass
    finally:
        (OUT / 'web_fps_ab.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        time.sleep(2.0)
        if browser.poll() is None:
            browser.terminate()


if __name__ == '__main__':
    main()
