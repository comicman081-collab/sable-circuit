"""Per-operation native FPS survey: an instrument, not a test, and no approval of performance.

Runs tools/maintenance/per_operation_fps_probe.gd once per round. The operation order is rotated by three places
every round and every second round is reversed (the room order too), so each operation sits at different places in
the session and the drift of this shared PC spreads over all of them: the project's rule is same-session rotated
runs, never one pass. One Godot window per round, native 1080p, vsync off, gl_compatibility, borderless on the
second monitor when there is one, audio driver Dummy. It refuses to start while any other Godot or the regression
runner is alive (the person's other project runs Godot too, and the runner's `qa/` guard must stay quiet).

  python tools/maintenance/per_operation_fps.py [--rounds 4] [--ops 1-10] [--steps 1,3,4] [--out DIR] [--shots]
  python tools/maintenance/per_operation_fps.py --summarize DIR

It runs the project through the editor binary. An exported build cannot be driven this way (the release template
ignores -s); tools/environment/build_windows_test_build.py `check` measures that one with --print-fps instead.
Output goes to .cache/fps_survey/<stamp>/ (git-ignored): roundNN.json, all_reports.json, meta.json, summary.md.
The summary ranks operations against each other on this PC and flags; it never passes or fails anything.
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GODOT = ROOT.parents[1] / 'Godot' / '4.7.1-standard' / 'Godot_v4.7.1-stable_win64_console.exe'
PROBE = 'res://tools/maintenance/per_operation_fps_probe.gd'
HEAVY_RATIO = 1.25  # an operation's mean frame time this far above the median operation's gets a HEAVY flag
NOISY_CV = 0.15     # spread of its per-round means over their mean above this gets a NOISY flag


def run_ps(command, timeout=40):
    done = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', command], capture_output=True, timeout=timeout)
    return done.stdout.decode('utf-8', 'replace').strip()


def busy_reason():
    """Any Godot or the regression runner alive. The [r] keeps this very command line from matching itself."""
    return run_ps("Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'Godot*' -or $_.CommandLine -like '*[r]un_regression_suite*' }"
                  " | ForEach-Object { '{0} {1}' -f $_.ProcessId, $_.Name }")


def cpu_load():
    try:
        return float(run_ps('(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average'))
    except (ValueError, subprocess.TimeoutExpired):
        return None


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True).stdout.decode('utf-8', 'replace').strip()


def parse_ops(text):
    result = []
    for part in text.split(','):
        if '-' in part:
            first, last = part.split('-')
            result.extend(range(int(first), int(last) + 1))
        else:
            result.append(int(part))
    return result


def round_order(ops, rnd):
    shift = ((rnd - 1) * 3) % len(ops)
    order = ops[shift:] + ops[:shift]
    return order[::-1] if rnd % 2 == 0 else order


def kill_tree(proc):
    subprocess.run(['taskkill', '/T', '/F', '/PID', str(proc.pid)], capture_output=True)
    proc.wait()


def run_round(rnd, ops, steps, args, out_dir):
    order = round_order(ops, rnd)
    room_steps = steps[::-1] if rnd % 2 == 0 else steps
    stem = f'round{rnd:02d}'
    rel = out_dir.relative_to(ROOT).as_posix()
    per_operation = 12 + len(room_steps) * (args.warmup_seconds + args.sample_seconds + 4)
    max_runtime = int(len(order) * per_operation + 60)
    env = dict(os.environ)
    scratch = ROOT / '.cache' / 'fps_survey' / 'env'
    for key, sub in (('TMP', 'tmp'), ('TEMP', 'tmp'), ('TMPDIR', 'tmp'), ('APPDATA', 'appdata'), ('LOCALAPPDATA', 'localappdata')):
        folder = scratch / sub
        folder.mkdir(parents=True, exist_ok=True)
        env[key] = str(folder)
    probe_args = [f'--round={rnd}', f'--order={",".join(map(str, order))}',
                  f'--steps={",".join(map(str, room_steps))}', f'--sample-seconds={args.sample_seconds}',
                  f'--warmup-seconds={args.warmup_seconds}', f'--max-runtime={max_runtime}', f'--screen={args.screen}']
    if args.shots:
        probe_args.append(f'--shot-dir={out_dir / "shots" / stem}')
    cmd = [str(GODOT), '--path', str(ROOT), '--rendering-method', 'gl_compatibility', '--audio-driver', 'Dummy', '-s', PROBE, '--',
           f'--out=res://{rel}/{stem}.json', '--tag=project', *probe_args]
    print(f'round {rnd}: operations {order}, rooms {room_steps}', flush=True)
    started = time.time()
    proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = []

    def pump():
        for raw in proc.stdout:
            line = raw.decode('utf-8', 'replace').rstrip()
            lines.append(line)
            if line.startswith('FPS_SURVEY '):
                try:
                    row = json.loads(line[len('FPS_SURVEY '):])
                    print(f'    op{row["operation"]:02d} {row["room"]:<16} {row["fps"]:7.1f} fps  p99 {row["p99_ms"]:5.2f} ms  gpu {row["gpu_ms"]:5.2f} ms', flush=True)
                except (ValueError, KeyError):
                    print('    ' + line, flush=True)

    reader = threading.Thread(target=pump, daemon=True)
    reader.start()
    try:
        code = proc.wait(timeout=max_runtime + 90)
    except subprocess.TimeoutExpired:
        kill_tree(proc)
        code = 124
    except KeyboardInterrupt:
        kill_tree(proc)
        raise
    reader.join(timeout=10)
    text = '\n'.join(lines)
    if code != 0 or 'SCRIPT ERROR' in text or 'Parse Error' in text:
        print(text[-3000:])
        raise SystemExit(f'round {rnd} failed (exit {code})')
    (out_dir / f'{stem}.log').write_text(text, encoding='utf-8')
    report = json.loads((out_dir / f'{stem}.json').read_text(encoding='utf-8'))
    report['wall_seconds'] = round(time.time() - started, 1)
    report['engine_error_lines'] = sum(1 for line in lines if line.startswith('ERROR:') or line.startswith('WARNING:'))
    messages = {}
    for line in lines:
        if line.startswith('ERROR:') or line.startswith('WARNING:'):
            messages[line[:240]] = messages.get(line[:240], 0) + 1
    report['engine_messages'] = [{'line': line, 'count': count} for line, count in sorted(messages.items(), key=lambda item: -item[1])]
    return report


def mean(values):
    return statistics.mean(values) if values else 0.0


def spread(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def summarize(reports, meta):
    rows = [row for report in reports for row in report['runs']]
    ops = sorted({row['operation'] for row in rows})
    rounds = sorted({row['round'] for row in rows})
    overall = mean([row['frame_ms'] for row in rows])
    stats = {}
    for op in ops:
        mine = [row for row in rows if row['operation'] == op]
        per_round = [mean([row['frame_ms'] for row in mine if row['round'] == rd]) for rd in rounds if any(row['round'] == rd for row in mine)]
        stats[op] = {
            'n': len(mine), 'fps': mean([row['fps'] for row in mine]), 'frame_ms': mean([row['frame_ms'] for row in mine]),
            'round_sd': spread(per_round), 'p99_ms': mean([row['p99_ms'] for row in mine]), 'worst_p99_ms': max(row['p99_ms'] for row in mine),
            'max_ms': max(row['max_ms'] for row in mine), 'gpu_ms': mean([row['gpu_ms'] for row in mine]),
            'process_ms': mean([row['process_ms'] for row in mine]), 'draw_calls': mean([row['draw_calls'] for row in mine]),
            'primitives': mean([row['primitives'] for row in mine]), 'video_mem_mb': mean([row['video_mem_mb'] for row in mine]),
            'load_ms': mean([row['stage_load_ms'] for row in mine]),
        }
    median_frame = statistics.median([stats[op]['frame_ms'] for op in ops])
    out = ['# Per-operation FPS survey', '']
    out.append(f"commit `{meta.get('commit')}` ({meta.get('dirty_files')} changed files), {meta.get('godot')}, {meta.get('adapter')}, "
               f"{len(rounds)} rounds x {len(ops)} operations x {len(meta.get('steps', []))} rooms, "
               f"{meta.get('sample_seconds')} s samples after {meta.get('warmup_seconds')} s warm-up, 1080p, vsync off, screen {meta.get('screen')}.")
    out.append(f"CPU load before each round (%): {meta.get('cpu_load_before_percent')}. Median operation frame time {median_frame:.3f} ms; "
               f"HEAVY = above {HEAVY_RATIO:.2f}x that, NOISY = per-round spread above {NOISY_CV:.0%} of the mean. Flags ask for a closer look, not a verdict.")
    out += ['', '## Per operation (all rooms, all rounds)', '',
            '| op | n | fps | frame ms | round sd ms | vs median | p99 ms (worst) | max ms | gpu ms | process max/s ms | draws | primitives | video MB | cold load ms | flags |',
            '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for op in ops:
        s = stats[op]
        flags = []
        if s['frame_ms'] > HEAVY_RATIO * median_frame:
            flags.append('HEAVY')
        if s['frame_ms'] and s['round_sd'] / s['frame_ms'] > NOISY_CV:
            flags.append('NOISY')
        out.append(f"| {op:02d} | {s['n']} | {s['fps']:.1f} | {s['frame_ms']:.3f} | {s['round_sd']:.3f} | {(s['frame_ms'] / median_frame - 1) * 100:+.1f}% | "
                   f"{s['p99_ms']:.2f} ({s['worst_p99_ms']:.2f}) | {s['max_ms']:.2f} | {s['gpu_ms']:.3f} | {s['process_ms']:.3f} | {s['draw_calls']:.0f} | "
                   f"{s['primitives']:.0f} | {s['video_mem_mb']:.0f} | {s['load_ms']:.0f} | {' '.join(flags) or '-'} |")
    out += ['', '## Per operation and room', '',
            '| op | room | enemies | hazards | fps (mean +- sd over rounds) | frame ms | p99 ms | gpu ms | draws | primitives | live vfx | max live vfx |',
            '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for op in ops:
        for room in sorted({row['room'] for row in rows if row['operation'] == op}, key=lambda name: min(r['step'] for r in rows if r['operation'] == op and r['room'] == name)):
            mine = [row for row in rows if row['operation'] == op and row['room'] == room]
            fps = [row['fps'] for row in mine]
            hazards = ','.join(sorted(set(sum([row.get('hazard_types', []) for row in mine], [])))) or '-'
            out.append(f"| {op:02d} | {room} | {mine[0]['fixed_enemy_count']} | {hazards} | {mean(fps):.1f} +- {spread(fps):.1f} | {mean([r['frame_ms'] for r in mine]):.3f} | "
                       f"{mean([r['p99_ms'] for r in mine]):.2f} | {mean([r['gpu_ms'] for r in mine]):.3f} | {mean([r['draw_calls'] for r in mine]):.0f} | "
                       f"{mean([r['primitives'] for r in mine]):.0f} | {mean([r['live_vfx_mean'] for r in mine]):.1f} | {max(r['live_vfx_peak'] for r in mine)} |")
    out += ['', '## Drift: by round and by place in the session', '',
            'A round whose mean sits far from 100 % means the PC itself was busier or quieter that round; a place that sits far from 100 % means the order matters.', '',
            '| round | mean frame ms | vs all |', '|---|---|---|']
    for rd in rounds:
        value = mean([row['frame_ms'] for row in rows if row['round'] == rd])
        out.append(f'| {rd} | {value:.3f} | {value / overall * 100:.1f}% |')
    out += ['', '| place in round | mean frame ms | vs all |', '|---|---|---|']
    for place in sorted({row['order_position'] for row in rows}):
        value = mean([row['frame_ms'] for row in rows if row['order_position'] == place])
        out.append(f'| {place} | {value:.3f} | {value / overall * 100:.1f}% |')
    out += ['', 'The first room measured after a stage loads can run slower while its textures settle; every operation gets the same share of first rooms.', '',
            '| room measured n-th in its stage | mean frame ms | vs all |', '|---|---|---|']
    for place in sorted({row['room_position'] for row in rows}):
        value = mean([row['frame_ms'] for row in rows if row['room_position'] == place])
        out.append(f'| {place} | {value:.3f} | {value / overall * 100:.1f}% |')
    messages = {}
    for report in reports:
        for item in report.get('engine_messages', []):
            messages[item['line']] = max(messages.get(item['line'], 0), item['count'])
    if messages:
        out += ['', '## Engine messages (ERROR / WARNING lines Godot printed, per round)', '',
                'Distinct lines and the most any one round printed them. They come from the real stage scene, so the same lines can appear in play; judge each one, do not count them.', '',
                '| per round | message |', '|---|---|']
        for line, count in sorted(messages.items(), key=lambda item: -item[1]):
            out.append(f"| {count} | `{line.replace('|', '/')}` |")
    out += ['', 'Frame times come from a fixed-actor preview fixture (frozen enemy AI, real autofire and hazards, no reinforcement waves, no HUD refresh): '
            'they rank the operations against each other on this PC and are not an in-play frame rate or a statement about slower machines. '
            '"process max/s" is Godot\'s TIME_PROCESS monitor, which reads above the mean frame time here (it looks like the worst frame of the previous second, refreshed about once a second), so treat it as a spike indicator, not a mean.', '']
    return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--rounds', type=int, default=4)
    parser.add_argument('--ops', default='1-10')
    parser.add_argument('--steps', default='1,3,4', help='battle-preview steps: 1 = R02, 3 = R04, 4 = R05 (boss)')
    parser.add_argument('--sample-seconds', type=float, default=6.0)
    parser.add_argument('--warmup-seconds', type=float, default=3.0)
    parser.add_argument('--screen', default='auto', help='auto (second monitor if any), primary, or an index')
    parser.add_argument('--out', default='')
    parser.add_argument('--shots', action='store_true', help='also save one native frame per sampled room under <out>/shots/')
    parser.add_argument('--summarize', default='', help='re-summarize an existing output folder and exit')
    args = parser.parse_args()
    if args.summarize:
        folder = Path(args.summarize)
        reports = json.loads((folder / 'all_reports.json').read_text(encoding='utf-8'))
        meta = json.loads((folder / 'meta.json').read_text(encoding='utf-8'))
        text = summarize(reports, meta)
        (folder / 'summary.md').write_text(text, encoding='utf-8')
        print(text)
        return
    ops = parse_ops(args.ops)
    steps = [int(part) for part in args.steps.split(',')]
    if not GODOT.exists():
        raise SystemExit(f'Godot not found: {GODOT}')
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = Path(args.out) if args.out else ROOT / '.cache' / 'fps_survey' / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    loads = []
    for rnd in range(1, args.rounds + 1):
        busy = busy_reason()
        if busy:
            raise SystemExit('Another Godot or the regression runner is alive, so no window is opened:\n' + busy)
        loads.append(cpu_load())
        reports.append(run_round(rnd, ops, steps, args, out_dir))
        (out_dir / 'all_reports.json').write_text(json.dumps(reports, ensure_ascii=False), encoding='utf-8')
    first = reports[0]
    meta = {'commit': git('rev-parse', '--short', 'HEAD'), 'dirty_files': len([line for line in git('status', '--porcelain').splitlines() if line.strip()]),
            'godot': first['godot'], 'adapter': first['adapter'], 'renderer': first['renderer'], 'screen': first['screen'],
            'screen_count': first['screen_count'], 'sample_seconds': args.sample_seconds, 'warmup_seconds': args.warmup_seconds,
            'steps': steps, 'ops': ops, 'rounds': args.rounds, 'cpu_load_before_percent': loads,
            'order_per_round': {str(rnd): round_order(ops, rnd) for rnd in range(1, args.rounds + 1)},
            'wall_seconds_per_round': [report['wall_seconds'] for report in reports],
            'engine_error_lines_per_round': [report['engine_error_lines'] for report in reports], 'started': stamp}
    (out_dir / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    text = summarize(reports, meta)
    (out_dir / 'summary.md').write_text(text, encoding='utf-8')
    print(text)
    print(f'\nwritten to {out_dir}')


if __name__ == '__main__':
    sys.exit(main())
