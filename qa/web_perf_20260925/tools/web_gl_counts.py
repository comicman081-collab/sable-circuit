"""WebGL calls per frame during op 1 combat, per build (diagnostic; FPS here is not a measurement).

usage: python web_gl_counts.py <out_dir> <rounds> <label>=<url> [...]
Wraps a few WebGL2 methods in the page to count calls, plays the same flow as
web_fps_ab.py and reports the per-frame average over the last 6 s of combat. The
wrappers slow the page, so only the counts are meaningful.
"""
from pathlib import Path
import json
import os
import subprocess
import sys

OUT_DIR, ROUNDS, BUILDS = sys.argv[1], int(sys.argv[2]), [tuple(a.split('=', 1)) for a in sys.argv[3:]]
sys.argv = [sys.argv[0], OUT_DIR, '1'] + [f'{k}={v}' for k, v in BUILDS]
sys.path.insert(0, str(Path(__file__).parent))
import web_fps_ab as ab  # noqa: E402  (reuses its private-port Edge launch, CDP client and flow)

COUNT = r"""
(function(){
  const P = WebGL2RenderingContext.prototype;
  const names = ['createVertexArray','deleteVertexArray','createBuffer','deleteBuffer','bufferData','bufferSubData',
                 'getParameter','isEnabled','drawElements','drawArrays','drawElementsInstanced','drawArraysInstanced',
                 'checkFramebufferStatus','framebufferTexture2D','texImage2D','texSubImage2D','texStorage2D'];
  const c = window.__glc = {};
  for (const k of names) { c[k] = 0; const f = P[k]; P[k] = function(){ c[k]++; return f.apply(this, arguments); }; }
  const snaps = window.__glcSnaps = [];
  const loop = t => { snaps.push([t, ...names.map(k => c[k])]); if (snaps.length > 20000) snaps.splice(0, 10000); requestAnimationFrame(loop); };
  requestAnimationFrame(loop);
  window.__glcWindow = seconds => {
    const now = performance.now(); const w = snaps.filter(x => x[0] >= now - seconds * 1000);
    if (w.length < 2) return null;
    const a = w[0], b = w[w.length - 1], frames = w.length - 1, out = {frames};
    names.forEach((k, i) => out[k] = +((b[i + 1] - a[i + 1]) / frames).toFixed(2));
    return out;
  };
})();
"""


def main():
    env = os.environ.copy()
    for name in ('TEMP', 'TMP'):
        folder = ab.PROFILE / 'tmp'
        folder.mkdir(parents=True, exist_ok=True)
        env[name] = str(folder)
    browser = subprocess.Popen([
        ab.EDGE, f'--user-data-dir={ab.PROFILE}', f'--remote-debugging-port={ab.PORT}',
        '--no-first-run', '--no-default-browser-check', '--disable-sync',
        '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding',
        '--disable-background-timer-throttling', '--force-device-scale-factor=1',
        f'--window-size={ab.W},{ab.H + 90}', '--window-position=0,0', '--new-window', 'about:blank'], env=env)
    report = {'builds': dict(BUILDS), 'rounds': ROUNDS, 'devtools_port': ab.PORT, 'runs': []}
    try:
        endpoint = ab.wait_for_devtools()
        assert ab.listener_pid(ab.PORT) == browser.pid
        cdp = ab.Cdp(endpoint)
        for domain in ('Page.enable', 'Runtime.enable', 'Network.enable'):
            cdp.call(domain)
        cdp.call('Network.setCacheDisabled', cacheDisabled=True)
        cdp.call('Emulation.setDeviceMetricsOverride', width=ab.W, height=ab.H, deviceScaleFactor=1, mobile=False)
        cdp.call('Page.addScriptToEvaluateOnNewDocument', source=ab.INSTRUMENT)
        cdp.call('Page.addScriptToEvaluateOnNewDocument', source=COUNT)
        for round_index in range(ROUNDS):
            order = BUILDS[round_index % len(BUILDS):] + BUILDS[:round_index % len(BUILDS)]
            for label, url in order:
                row = ab.run_once(cdp, label, url, f'gl{round_index + 1}')
                row['gl_per_frame_late'] = cdp.eval('window.__glcWindow(6)')
                report['runs'].append(row)
                print('GL', label, row['valid'], json.dumps(row['gl_per_frame_late']), flush=True)
        try:
            cdp.call('Browser.close')
        except Exception:
            pass
    finally:
        Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
        (Path(OUT_DIR) / 'web_gl_counts.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        if browser.poll() is None:
            browser.terminate()


if __name__ == '__main__':
    main()
