"""One CPU profile of the web build's main thread during op 1 combat (diagnostic only).

usage: python web_profile.py <out_dir> <url>
Writes profile_summary.json (self time by function, top 40) and the raw .cpuprofile.
"""
from pathlib import Path
import collections
import json
import sys
import time

OUT_DIR, URL = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0], OUT_DIR, '1', f'build={URL}']
sys.path.insert(0, str(Path(__file__).parent))
import web_fps_ab as ab  # noqa: E402  (reuses its private-port Edge launch and CDP client)


def main():
    import os
    import subprocess
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
    try:
        endpoint = ab.wait_for_devtools()
        assert ab.listener_pid(ab.PORT) == browser.pid
        cdp = ab.Cdp(endpoint)
        for domain in ('Page.enable', 'Runtime.enable', 'Profiler.enable'):
            cdp.call(domain)
        cdp.call('Emulation.setDeviceMetricsOverride', width=ab.W, height=ab.H, deviceScaleFactor=1, mobile=False)
        cdp.call('Page.addScriptToEvaluateOnNewDocument', source=ab.INSTRUMENT)
        cdp.call('Profiler.setSamplingInterval', interval=500)
        cdp.call('Page.navigate', url=URL)
        ab.wait_engine_running(cdp)
        time.sleep(2.0)
        cdp.click(336, 585)
        time.sleep(3.0)
        cdp.key('Enter', 'Enter', 13)
        time.sleep(3.5)
        cdp.click(1520, 652)
        time.sleep(2.0)
        for _ in range(7):
            cdp.click(1576, 820)
            time.sleep(1.3)
        cdp.click(1520, 972)
        time.sleep(8.0)
        cdp.call('Profiler.start')
        moves = [('d', 'KeyD', 68), ('w', 'KeyW', 87), ('d', 'KeyD', 68), ('s', 'KeyS', 83)]
        for step in range(7):
            key = moves[step % len(moves)]
            cdp.call('Input.dispatchKeyEvent', type='rawKeyDown', key=key[0], code=key[1], windowsVirtualKeyCode=key[2])
            for burst in range(4):
                cdp.click(1180 + 40 * (step % 3), 430 + 30 * (burst % 2))
                time.sleep(0.35)
            cdp.call('Input.dispatchKeyEvent', type='keyUp', key=key[0], code=key[1], windowsVirtualKeyCode=key[2])
            time.sleep(0.2)
        profile = cdp.call('Profiler.stop')['profile']
        fps = cdp.eval('window.__sableFps(10)')
        final_url = cdp.eval('location.href')
        Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
        (Path(OUT_DIR) / 'combat.cpuprofile').write_text(json.dumps(profile), encoding='utf-8')
        nodes = {n['id']: n for n in profile['nodes']}
        deltas = profile.get('timeDeltas', [])
        self_us = collections.Counter()
        for sample, delta in zip(profile.get('samples', []), deltas):
            frame = nodes[sample]['callFrame']
            label = frame['functionName'] or '(anonymous)'
            if frame.get('url'):
                label += ' @' + frame['url'].rsplit('/', 1)[-1]
            self_us[label] += delta
        total = sum(self_us.values())
        top = [{'function': name, 'self_ms': round(us / 1000, 1), 'share': round(us / total, 4)} for name, us in self_us.most_common(40)]
        summary = {'url': URL, 'final_url': final_url, 'fps_10s': fps, 'profiled_ms': round(total / 1000, 1), 'top_self': top}
        (Path(OUT_DIR) / 'profile_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
        print(json.dumps({'fps': fps['fps'], 'final_url': final_url, 'profiled_ms': summary['profiled_ms']}))
        for row in top[:25]:
            print(f"{row['share']*100:5.1f}%  {row['self_ms']:8.1f} ms  {row['function'][:90]}")
        try:
            cdp.call('Browser.close')
        except Exception:
            pass
    finally:
        time.sleep(2.0)
        if browser.poll() is None:
            browser.terminate()


main()
