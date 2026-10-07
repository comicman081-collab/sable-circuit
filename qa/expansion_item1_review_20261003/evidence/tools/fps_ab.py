"""Claude review instrument (V-20): same-session rotated FPS A/B of operations 6-10 (rooms R02 and R04), baseline vs reviewed snapshot.
Uses Codex's diagnostic probe byte for byte (fixed actors, frozen enemy AI, real autofire, real hazard cycles) in both snapshots,
alternating the arm order every round (AB / BA / AB ...). Native 1080p window, vsync off, gl_compatibility."""
import hashlib, json, os, shutil, statistics, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SNAP = ROOT / '.cache' / 'claude_scratch'
PROBE_SRC = ROOT / '.cache' / 'claude_scratch' / 'item1_review' / 'item1_perf_probe_fixed.gd'
GODOT = r'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe'
BUILDS = {'base': SNAP / 'proj_base', 'after': SNAP / 'proj_after'}
OUT = SNAP / 'item1_review' / 'fps_ab'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(rounds: int):
    OUT.mkdir(parents=True, exist_ok=True)
    for b, proj in BUILDS.items():
        dst = proj / '.cache' / 'probe' / 'item1_perf_probe.gd'
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROBE_SRC, dst)
        (proj / '.cache' / 'ab').mkdir(parents=True, exist_ok=True)
        assert sha(dst) == sha(PROBE_SRC), 'probe copies must be byte-identical'
    print('probe sha256', sha(PROBE_SRC), flush=True)
    reports = []
    for rnd in range(1, rounds + 1):
        order = ('base', 'after') if rnd % 2 == 1 else ('after', 'base')
        for build in order:
            proj = BUILDS[build]
            env = dict(os.environ)
            for k, sub in (('TMP', 'tmp'), ('TEMP', 'tmp'), ('TMPDIR', 'tmp'), ('APPDATA', 'godot_appdata'), ('LOCALAPPDATA', 'godot_localappdata')):
                d = proj / '.cache' / sub; d.mkdir(parents=True, exist_ok=True); env[k] = str(d)
            stem = f'round{rnd:02d}_{build}'
            out_res = f'res://.cache/ab/{stem}.json'
            cmd = [GODOT, '--path', str(proj), '--rendering-method', 'gl_compatibility', '-s', 'res://.cache/probe/item1_perf_probe.gd', '--',
                   f'--out={out_res}', f'--tag={build}', f'--round={rnd}', '--sample-seconds=7', '--warmup-seconds=2', '--max-runtime=240']
            t0 = time.time()
            p = subprocess.run(cmd, cwd=proj, capture_output=True, timeout=300, env=env)
            text = (p.stdout + p.stderr).decode('utf-8', 'replace')
            print(f'{stem}: exit {p.returncode} in {time.time() - t0:.0f}s', flush=True)
            if p.returncode != 0 or 'SCRIPT ERROR' in text:
                print(text[-1500:]); raise SystemExit(1)
            jp = proj / '.cache' / 'ab' / f'{stem}.json'
            rep = json.loads(jp.read_text(encoding='utf-8'))
            shutil.copyfile(jp, OUT / f'{stem}.json')
            reports.append(rep)
    (OUT / 'all_reports.json').write_text(json.dumps(reports, ensure_ascii=False), encoding='utf-8')
    summarize(reports)

def summarize(reports):
    rows = {}
    for rep in reports:
        for r in rep['runs']:
            rows.setdefault((r['mission'], r['room'], r['version']), []).append(r)
    print('\nmission room            metric        base(mean±sd)      after(mean±sd)     delta%   draws base->after   hazards')
    keys = sorted({(m, rm) for (m, rm, v) in rows})
    for m, rm in keys:
        b, a = rows[(m, rm, 'base')], rows[(m, rm, 'after')]
        for metric in ('fps', 'frame_ms', 'gpu_ms', 'process_ms'):
            bv = [x[metric] for x in b]; av = [x[metric] for x in a]
            bm, am = statistics.mean(bv), statistics.mean(av)
            bs = statistics.pstdev(bv); as_ = statistics.pstdev(av)
            delta = (am - bm) / bm * 100.0 if bm else 0.0
            extra = ''
            if metric == 'fps':
                extra = f'   {statistics.mean(x["draw_calls"] for x in b):.0f}->{statistics.mean(x["draw_calls"] for x in a):.0f}   {a[0].get("hazard_types")}'
            print(f'{m[-2:]} {rm:<16} {metric:<10} {bm:9.2f}±{bs:5.2f}   {am:9.2f}±{as_:5.2f}   {delta:+6.1f}%{extra}')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'summarize':
        summarize(json.loads((OUT / 'all_reports.json').read_text(encoding='utf-8')))
    else:
        main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
