"""Build and check a Windows test build of SABLE CIRCUIT. Nothing is uploaded, signed or published.

A closed test build for a few people, not a release: no installer, no icon resources, no code signing, no update path.
It is made from a STAGED COPY of the runtime folders (the same idea as tools/environment/build_sites_demo.py), so the
project folder, its import cache and its tracked .import files are never touched, and the 30 GB of retired payloads
beside the project never reach Godot's file scan. Official Godot 4.7.1 export templates are copied from where they are
installed (read only) into .cache/export_trial/templates and checked against their recorded SHA-256.

  python tools/environment/build_windows_test_build.py build [--skip-import] [--debug]
  python tools/environment/build_windows_test_build.py check [--only boot,flow,perf,audit,native] [--frames 900] [--tag NAME]

The release template ignores `-s`, so only the game's own user arguments (`--battle-stage=N`, `--stage1`) can drive the
exported exe; scripts such as the pack audit run through the editor binary with `--main-pack` instead.

build  stages the runtime folders, imports them with the editor (headless), exports a release build and records its
       size, hashes and pack contents (record/build_record.json).
check  runs the exported exe: the title, every operation's battle preview through the game's own `--battle-stage=N`
       path, the deploy path (`--stage1`), and a pack audit (tools/environment/export_pack_audit.gd, run by the editor
       binary on the .pck). Every run's engine messages are collected, not judged: read them.

Output goes to .cache/export_trial/ (git-ignored): stage/, templates/, build/, logs/, record/, env/ (TEMP and APPDATA of
every Godot child are redirected there, so neither the editor's settings nor the packaged game's saves reach C:).
It refuses to start while any other Godot or the regression runner is alive.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'maintenance'))
from per_operation_fps import busy_reason, kill_tree  # noqa: E402

WORK = ROOT / '.cache' / 'export_trial'
STAGE = WORK / 'stage'
BUILD = WORK / 'build'
LOGS = WORK / 'logs'
RECORD = WORK / 'record'
ENV_DIR = WORK / 'env'
TEMPLATES = WORK / 'templates'
GODOT = ROOT.parents[1] / 'Godot' / '4.7.1-standard' / 'Godot_v4.7.1-stable_win64_console.exe'
TEMPLATE_SOURCE = Path(os.environ.get('APPDATA', '')) / 'Godot' / 'export_templates' / '4.7.1.stable'
TEMPLATE_MANIFEST = TEMPLATE_SOURCE / 'LANTERNLINE_WINDOWS_TEMPLATE_MANIFEST.json'
EXE = BUILD / 'SableCircuit.exe'
PCK = BUILD / 'SableCircuit.pck'
AUDIT = ROOT / 'tools' / 'environment' / 'export_pack_audit.gd'

# What the game reads at run time. Everything else in the project (docs, tests, source art, QA, tools) stays out.
RUNTIME_FOLDERS = ('scripts', 'scenes', 'data', 'assets', 'sound/music/runtime', 'motion_lab_v1/public/assets/atlas')
RUNTIME_FILES = ('sound/music/catalog.json', 'project.godot')
# Not read by the game: the kArchive source models and the intro video that the original-audio one replaced.
EXCLUDED = ('assets/external/', 'assets/cinematics/sable_intro.ogv')
# Raw files the game opens with FileAccess / Image.load_from_file, next to the imported copies.
INCLUDE_FILTER = '*.json,*.png,*.webp,*.jpg,*.jpeg,*.ogg,*.wav,*.mp3,*.ogv,*.txt,*.b64.*'
RAW_SUFFIXES = {'.png', '.webp', '.jpg', '.jpeg', '.ogg', '.wav', '.mp3', '.ogv', '.json', '.txt'}
RESOURCE_SUFFIXES = {'.tscn', '.tres', '.res', '.gd', '.gdshader', '.otf', '.ttf', '.svg'}
IMAGE_SUFFIXES = {'.png', '.webp', '.jpg', '.jpeg'}
# Every reader of these in scripts/ opens the original bytes (FileAccess.get_file_as_bytes, Image.load_from_file,
# AudioStreamMP3.load_from_buffer), and Godot packs only the imported copy of an imported file, never its source
# (include_filter does not add it): the first trial build had no title.mp3 and no raw PNG. Keeping them un-imported
# packs the originals, as tools/environment/build_sites_demo.py does. SVG, fonts, scenes and .res stay normally imported.
KEEP_SUFFIXES = IMAGE_SUFFIXES | {'.mp3'}
KEEP_IMPORT = '[remap]\n\nimporter="keep"\n'
STAGE_MODE = 2  # bump when the staging rules change; a stage built under another mode loses its import cache
MESSAGE_PREFIXES = ('ERROR:', 'WARNING:', 'SCRIPT ERROR:', 'USER ERROR:', 'USER WARNING:', 'USER SCRIPT ERROR:', 'Parse Error')


def sha256(path, chunk=16 * 1024 * 1024):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while data := stream.read(chunk):
            digest.update(data)
    return digest.hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True).stdout.decode('utf-8', 'replace').strip()


def child_env():
    """TEMP and the user-data roots of every Godot child sit inside the project's .cache, never on C:."""
    env = dict(os.environ)
    for key, sub in (('TMP', 'tmp'), ('TEMP', 'tmp'), ('TMPDIR', 'tmp'), ('APPDATA', 'appdata'), ('LOCALAPPDATA', 'localappdata')):
        folder = ENV_DIR / sub
        folder.mkdir(parents=True, exist_ok=True)
        env[key] = str(folder)
    return env


def capture_window(pid, path, clip_monitor=False):
    """Save the screen pixels of the biggest visible window of `pid`. Needs the window to be uncovered; returns None if it cannot.
    `clip_monitor` cuts the grab to the monitor the window sits on: a borderless full-screen Godot window can be a pixel or two
    taller than its monitor, and the monitor's own pixels are the frame a player sees."""
    try:
        import ctypes
        from ctypes import wintypes
        from PIL import ImageGrab
        user32 = ctypes.windll.user32
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            pass
        found = []

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def callback(hwnd, _lparam):
            owner = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
            if owner.value == pid and user32.IsWindowVisible(hwnd):
                rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                found.append(((rect.right - rect.left) * (rect.bottom - rect.top), rect.left, rect.top, rect.right, rect.bottom))
            return True

        user32.EnumWindows(callback, 0)
        if not found:
            return None
        _area, left, top, right, bottom = max(found)
        window = [left, top, right, bottom]
        if clip_monitor:
            class MonitorInfo(ctypes.Structure):
                _fields_ = [('cbSize', wintypes.DWORD), ('rcMonitor', wintypes.RECT), ('rcWork', wintypes.RECT), ('dwFlags', wintypes.DWORD)]

            user32.MonitorFromPoint.argtypes = [wintypes.POINT, wintypes.DWORD]
            user32.MonitorFromPoint.restype = wintypes.HANDLE
            user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MonitorInfo)]
            monitor = user32.MonitorFromPoint(wintypes.POINT((left + right) // 2, (top + bottom) // 2), 2)  # nearest monitor
            info = MonitorInfo()
            info.cbSize = ctypes.sizeof(MonitorInfo)
            if monitor and user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
                left, top = max(left, info.rcMonitor.left), max(top, info.rcMonitor.top)
                right, bottom = min(right, info.rcMonitor.right), min(bottom, info.rcMonitor.bottom)
        image = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        return {'path': str(path), 'size': list(image.size), 'window': window, 'grab': [left, top, right, bottom]}
    except Exception as error:  # a missing frame must not fail the run it documents
        return {'path': None, 'error': repr(error)}


def run_logged(cmd, cwd, log, timeout, shots=(), captured=None, clip_monitor=False):
    """Run one child with its output in `log`. Returns (exit code, seconds). A hang kills only this child's tree.
    `shots` is a list of (seconds after start, png path): the child's window is grabbed from the screen at those times."""
    started = time.time()
    pending = sorted(shots)
    with Path(log).open('wb') as stream:
        proc = subprocess.Popen(cmd, cwd=cwd, env=child_env(), stdout=stream, stderr=subprocess.STDOUT)
        try:
            while True:
                try:
                    code = proc.wait(timeout=0.4)
                    break
                except subprocess.TimeoutExpired:
                    pass
                elapsed = time.time() - started
                while pending and elapsed >= pending[0][0]:
                    _at, path = pending.pop(0)
                    result = capture_window(proc.pid, path, clip_monitor)
                    if captured is not None:
                        captured.append(result)
                if elapsed > timeout:
                    kill_tree(proc)
                    code = 124
                    break
        except KeyboardInterrupt:
            kill_tree(proc)
            raise
    return code, round(time.time() - started, 1)


def require_quiet():
    busy = busy_reason()
    if busy:
        raise SystemExit('Another Godot or the regression runner is alive, so nothing is started:\n' + busy)


# ---------------------------------------------------------------- staging

def excluded(rel):
    return rel.startswith(EXCLUDED)


def keeps_original(rel):
    return Path(rel).suffix.lower() in KEEP_SUFFIXES


def planned_files():
    """Relative path -> source file. The project's own .import of a kept-original file is not copied (see KEEP_SUFFIXES)."""
    files = {}
    for folder in RUNTIME_FOLDERS:
        for path in (ROOT / folder).rglob('*'):
            if path.is_file():
                rel = path.relative_to(ROOT).as_posix()
                if excluded(rel) or (rel.endswith('.import') and keeps_original(rel.removesuffix('.import'))):
                    continue
                files[rel] = path
    for rel in RUNTIME_FILES:
        files[rel] = ROOT / rel
    return files


def stage_project():
    """Mirror the runtime folders into the stage. Only files under the stage's own runtime folders are ever deleted."""
    files = planned_files()
    marker = STAGE / '.stage_mode'
    cleaned = False
    if STAGE.exists() and (not marker.exists() or marker.read_text(encoding='utf-8').strip() != str(STAGE_MODE)) and (STAGE / '.godot').exists():
        shutil.rmtree(STAGE / '.godot')
        cleaned = True
    STAGE.mkdir(parents=True, exist_ok=True)
    marker.write_text(str(STAGE_MODE), encoding='utf-8')
    copied = skipped = removed = 0
    generated = set()
    for rel in files:
        if keeps_original(rel):
            generated.add(rel + '.import')
            target = STAGE / (rel + '.import')
            if not target.exists() or target.read_text(encoding='utf-8') != KEEP_IMPORT:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(KEEP_IMPORT, encoding='utf-8', newline='\n')
    for rel, source in files.items():
        target = STAGE / rel
        info = source.stat()
        if target.exists() and target.stat().st_size == info.st_size and target.stat().st_mtime_ns >= info.st_mtime_ns:
            skipped += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1
    wanted = set(files) | generated
    for folder in RUNTIME_FOLDERS:
        base = STAGE / folder
        if not base.exists():
            continue
        for path in list(base.rglob('*')):
            if path.is_file() and path.relative_to(STAGE).as_posix() not in wanted:
                assert STAGE in path.parents
                path.unlink()
                removed += 1
    sizes = defaultdict(int)
    for rel, source in files.items():
        sizes[rel.split('/')[0] if '/' in rel else rel] += source.stat().st_size
    return {'files': len(files), 'copied': copied, 'unchanged': skipped, 'removed_stale': removed, 'import_cache_reset': cleaned,
            'kept_original_files': len(generated), 'bytes': sum(sizes.values()), 'bytes_by_top_folder': dict(sorted(sizes.items(), key=lambda item: -item[1]))}


def copy_templates():
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(TEMPLATE_MANIFEST.read_text(encoding='utf-8'))
    wanted = {row['file']: row for row in manifest['records']}
    result = {}
    for name in ('windows_release_x86_64.exe', 'windows_debug_x86_64.exe'):
        source, target = TEMPLATE_SOURCE / name, TEMPLATES / name
        if not target.exists() or target.stat().st_size != source.stat().st_size:
            shutil.copy2(source, target)
        digest = sha256(target)
        if digest != wanted[name]['sha256']:
            raise SystemExit(f'Template {name} does not match its recorded SHA-256 ({digest} != {wanted[name]["sha256"]})')
        result[name] = {'bytes': target.stat().st_size, 'sha256': digest, 'source': str(source)}
    return result


def write_preset():
    release = (TEMPLATES / 'windows_release_x86_64.exe').as_posix()
    debug = (TEMPLATES / 'windows_debug_x86_64.exe').as_posix()
    text = f'''[preset.0]

name="Windows Desktop"
platform="Windows Desktop"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter="{INCLUDE_FILTER}"
exclude_filter=""
export_path=""
patches=PackedStringArray()
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false
script_export_mode=0

[preset.0.options]

custom_template/debug="{debug}"
custom_template/release="{release}"
debug/export_console_wrapper=0
binary_format/embed_pck=false
texture_format/s3tc_bptc=true
texture_format/etc2_astc=false
binary_format/architecture="x86_64"
codesign/enable=false
application/modify_resources=false
'''
    (STAGE / 'export_presets.cfg').write_text(text, encoding='utf-8', newline='\n')


# ---------------------------------------------------------------- pack listing

def read_pck_index(path):
    """Best-effort listing of a .pck written by Godot 4.7 (format 4: header, flags, file base, directory offset, directory
    at the end; paths carry no res:// prefix). Returns None when the layout is not recognised."""
    try:
        with Path(path).open('rb') as stream:
            if stream.read(4) != b'GDPC':
                return None
            version, major, minor, patch = struct.unpack('<4I', stream.read(16))
            dir_offset = None
            if version >= 2:
                stream.read(12)  # flags, file base
                if version >= 3:
                    dir_offset, = struct.unpack('<Q', stream.read(8))
                else:
                    stream.read(64)
            else:
                stream.read(64)
            if dir_offset is not None:
                stream.seek(dir_offset)
            count, = struct.unpack('<I', stream.read(4))
            if count > 5_000_000:
                return None
            rows = []
            for _ in range(count):
                length, = struct.unpack('<I', stream.read(4))
                name = stream.read(length).rstrip(b'\0').decode('utf-8')
                offset, size = struct.unpack('<QQ', stream.read(16))
                stream.read(16)
                if version >= 2:
                    stream.read(4)
                rows.append((name.removeprefix('res://'), offset, size))
    except (OSError, struct.error, UnicodeDecodeError):
        return None
    if not rows or any(not name or '\0' in name for name, _, _ in rows):
        return None
    return {'format': version, 'engine': f'{major}.{minor}.{patch}', 'files': rows}


def summarise_pck(index):
    by_ext, by_top = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
    for name, _, size in index['files']:
        relative = name
        ext = Path(relative).suffix.lower() or '(none)'
        top = '.godot/imported' if relative.startswith('.godot/imported/') else (relative.split('/')[0] if '/' in relative else relative)
        by_ext[ext][0] += 1
        by_ext[ext][1] += size
        by_top[top][0] += 1
        by_top[top][1] += size
    order = lambda table: {key: {'files': value[0], 'bytes': value[1]} for key, value in sorted(table.items(), key=lambda item: -item[1][1])}
    return {'format': index['format'], 'engine': index['engine'], 'files': len(index['files']),
            'bytes_of_files': sum(size for _, _, size in index['files']), 'by_extension': order(by_ext), 'by_folder': order(by_top)}


# ---------------------------------------------------------------- build

def command_build(args):
    require_quiet()
    for folder in (WORK, STAGE, BUILD, LOGS, RECORD):
        folder.mkdir(parents=True, exist_ok=True)
    if not GODOT.exists():
        raise SystemExit(f'Godot not found: {GODOT}')
    record = {'started': datetime.now().isoformat(timespec='seconds'), 'commit': git('rev-parse', '--short', 'HEAD'),
              'dirty_files': len([line for line in git('status', '--porcelain').splitlines() if line.strip()]),
              'godot_editor': GODOT.name, 'include_filter': INCLUDE_FILTER, 'excluded': list(EXCLUDED),
              'runtime_folders': list(RUNTIME_FOLDERS) + list(RUNTIME_FILES)}
    started = time.time()
    record['templates'] = copy_templates()
    record['stage'] = stage_project()
    write_preset()
    print(f"staged {record['stage']['files']} files ({record['stage']['bytes'] / 1048576:.0f} MB), "
          f"{record['stage']['copied']} copied, {record['stage']['removed_stale']} stale removed ({time.time() - started:.0f} s)", flush=True)
    if not args.skip_import:
        code, seconds = run_logged([str(GODOT), '--headless', '--path', str(STAGE), '--editor', '--import'], STAGE, LOGS / 'import.log', 3600)
        record['import'] = {'exit_code': code, 'seconds': seconds}
        print(f'import: exit {code} in {seconds:.0f} s', flush=True)
        if code != 0:
            raise SystemExit('import failed, see ' + str(LOGS / 'import.log'))
    modes = [('release', '--export-release', EXE)]
    if args.debug:
        modes.append(('debug', '--export-debug', BUILD / 'SableCircuit_debug.exe'))
    for name, flag, target in modes:
        for old in (target, target.with_suffix('.pck')):
            if old.exists():
                old.unlink()
        code, seconds = run_logged([str(GODOT), '--headless', '--path', str(STAGE), flag, 'Windows Desktop', str(target)], STAGE, LOGS / f'export_{name}.log', 3600)
        record[f'export_{name}'] = {'exit_code': code, 'seconds': seconds}
        print(f'export {name}: exit {code} in {seconds:.0f} s', flush=True)
        if code != 0 or not target.exists():
            raise SystemExit(f'export {name} failed, see ' + str(LOGS / f'export_{name}.log'))
        pck = target.with_suffix('.pck')
        record[f'{name}_files'] = {'exe': {'bytes': target.stat().st_size, 'sha256': sha256(target)},
                                    'pck': {'bytes': pck.stat().st_size, 'sha256': sha256(pck)} if pck.exists() else None}
    index = read_pck_index(PCK)
    record['pack'] = summarise_pck(index) if index else 'listing not recognised'
    record['build_bytes'] = sum(path.stat().st_size for path in BUILD.iterdir() if path.is_file())
    record['seconds_total'] = round(time.time() - started, 1)
    (RECORD / 'build_record.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: record[key] for key in ('build_bytes', 'seconds_total')}), flush=True)
    if isinstance(record['pack'], dict):
        print('pack:', record['pack']['files'], 'files,', round(record['pack']['bytes_of_files'] / 1048576), 'MB')
        for key, row in list(record['pack']['by_folder'].items())[:8]:
            print(f"  {key:<24} {row['files']:6d} files {row['bytes'] / 1048576:8.1f} MB")


# ---------------------------------------------------------------- check

def engine_messages(text):
    found = Counter()
    for line in text.splitlines():
        if line.startswith(MESSAGE_PREFIXES):
            found[line[:220]] += 1
    return [{'line': line, 'count': count} for line, count in found.most_common()]


def game_args(frames, screen, log, extra=(), native=False):
    """A small window for the smoke runs; `native` is a borderless full screen, so a 1920 x 1080 monitor gives native 1080p frames."""
    window = ['--fullscreen'] if native else ['--windowed', '--resolution', '1280x720']
    return [str(EXE), '--audio-driver', 'Dummy', '--rendering-method', 'gl_compatibility', *window,
            '--screen', str(screen), '--quit-after', str(frames), '--log-file', str(log), *extra]


def read_log(stdout_log, engine_log):
    text = Path(stdout_log).read_text(encoding='utf-8', errors='replace') if Path(stdout_log).exists() else ''
    if Path(engine_log).exists():
        text += '\n' + Path(engine_log).read_text(encoding='utf-8', errors='replace')
    return text


def stage_references():
    """Files the stage holds, split by how the game opens them: raw bytes, loadable resources, images to decode, music to decode."""
    raw, resources, images, music = [], [], [], []
    for path in sorted(STAGE.rglob('*')):
        if not path.is_file() or '.godot' in path.relative_to(STAGE).parts or path.name in ('export_presets.cfg', '.stage_mode'):
            continue
        res = 'res://' + path.relative_to(STAGE).as_posix()
        suffix = path.suffix.lower()
        if suffix in RAW_SUFFIXES or '.b64.' in path.name:
            raw.append(res)
        if suffix in RESOURCE_SUFFIXES:
            resources.append(res)
        if suffix in IMAGE_SUFFIXES:
            images.append(res)
        if suffix == '.mp3':
            music.append(res)
    step = max(1, len(images) // 80)
    loadable = [res for res in resources if Path(res).suffix.lower() in {'.otf', '.ttf', '.res', '.tres', '.svg'}]
    return {'raw': raw, 'resources': resources, 'decode_samples': images[::step], 'load_samples': loadable, 'music': music}


def fps_summary(samples, skip=2):
    """`--print-fps` prints one value per second; the first seconds are the stage loading, so they are listed apart."""
    steady = samples[skip:]
    if not steady:
        return None
    ordered = sorted(steady)
    return {'seconds': len(steady), 'min': ordered[0], 'mean': round(sum(steady) / len(steady), 1), 'median': ordered[len(ordered) // 2],
            'first_seconds': samples[:skip]}


def run_one(name, frames, screen, extra, timeout, results, shot_at=None, engine_args=(), native=False):
    stdout_log, engine_log = LOGS / f'check_{name}.log', LOGS / f'check_{name}.engine.log'
    if engine_log.exists():
        engine_log.unlink()
    captured = []
    shots = [(shot_at, RECORD / 'shots' / f'{name}.png')] if shot_at else []
    command = game_args(frames, screen, engine_log, list(engine_args), native)
    if extra:
        command += ['--'] + list(extra)
    code, seconds = run_logged(command, BUILD, stdout_log, timeout, shots, captured, clip_monitor=native)
    text = read_log(stdout_log, engine_log)
    fps_samples = [int(match) for match in re.findall(r'^Project FPS: (\d+) ', text, re.MULTILINE)]
    row = {'name': name, 'exit_code': code, 'seconds': seconds, 'frames': frames, 'messages': engine_messages(text),
           'script_errors': sum(1 for line in text.splitlines() if line.startswith(('SCRIPT ERROR', 'Parse Error', 'USER SCRIPT ERROR'))),
           'log_lines': len(text.splitlines()), 'frame': captured[0] if captured else None, 'printed_fps': fps_samples,
           'fps_after_load': fps_summary(fps_samples)}
    results.append(row)
    flag = 'ok ' if code == 0 and not row['messages'] else ('MSG' if code == 0 else 'FAIL')
    fps = row['fps_after_load']
    fps_text = f"  fps min {fps['min']} median {fps['median']} mean {fps['mean']} (first seconds {fps['first_seconds']})" if fps else ''
    print(f"  {flag} {name:<14} exit {code:>3} {seconds:6.1f} s  {len(row['messages'])} distinct engine messages, {row['script_errors']} script errors{fps_text}", flush=True)
    return row


def command_check(args):
    require_quiet()
    if not EXE.exists():
        raise SystemExit('No exported build yet: run the build command first.')
    wanted = set(args.only.split(',')) if args.only else {'boot', 'flow', 'audit'}
    LOGS.mkdir(parents=True, exist_ok=True)
    results = []
    user_dir = ENV_DIR / 'appdata' / 'Godot' / 'app_userdata'
    before = {p for p in user_dir.rglob('*') if p.is_file()} if user_dir.exists() else set()
    print(f'checking {EXE} ({EXE.stat().st_size / 1048576:.0f} MB exe + {PCK.stat().st_size / 1048576:.0f} MB pck)', flush=True)
    if 'boot' in wanted:
        run_one('title', 240, args.screen, [], 180, results, shot_at=3, engine_args=['--print-fps'])
        for operation in range(1, 11):
            run_one(f'battle_op{operation:02d}', args.frames, args.screen, [f'--battle-stage={operation}'], 240, results, shot_at=7, engine_args=['--print-fps'])
    if 'flow' in wanted:
        run_one('deploy_op01', args.frames, args.screen, ['--stage1'], 240, results, shot_at=7, engine_args=['--print-fps'])
    if 'native' in wanted:
        # Borderless full screen on the chosen monitor, so the frames are as large as that monitor (1920 x 1080 on this PC's
        # second one): the project's evidence floor for any frame that is shown as evidence.
        for name, extra in (('native_title', []), ('native_battle_op10', ['--battle-stage=10']), ('native_deploy_op01', ['--stage1'])):
            row = run_one(name, 240 if name == 'native_title' else args.frames, args.screen, extra, 240, results, shot_at=3 if name == 'native_title' else 7,
                          engine_args=['--print-fps'], native=True)
            frame = row['frame']
            if frame and frame.get('size'):
                frame['native_1080p'] = frame['size'] == [1920, 1080]
                print(f"       frame {frame['size'][0]} x {frame['size'][1]}" + ('' if frame['native_1080p'] else '  (NOT 1920 x 1080)'), flush=True)
    if 'perf' in wanted:
        # Real combat in each operation's first room with the vsync cap off: the frame rate the packaged game could reach.
        for operation in range(1, 11):
            run_one(f'perf_op{operation:02d}', args.perf_frames, args.screen, [f'--battle-stage={operation}'], 240, results, engine_args=['--print-fps', '--disable-vsync'])
    if 'audit' in wanted:
        references = stage_references()
        list_path, out_path = RECORD / 'audit_list.json', RECORD / 'audit_result.json'
        RECORD.mkdir(parents=True, exist_ok=True)
        list_path.write_text(json.dumps(references), encoding='utf-8')
        if out_path.exists():
            out_path.unlink()
        stdout_log, engine_log = LOGS / 'check_audit.log', LOGS / 'check_audit.engine.log'
        # The release template ignores -s (the first attempt simply booted the game), so the pack is read through the editor
        # binary with --main-pack, the way build_sites_demo.py checks its web pack. No --path: res:// is the pack and nothing else.
        code, seconds = run_logged([str(GODOT), '--headless', '--audio-driver', 'Dummy', '--main-pack', str(PCK), '--log-file', str(engine_log),
                                    '-s', str(AUDIT), '--', f'--list={list_path}', f'--out={out_path}'], BUILD, stdout_log, 600)
        text = read_log(stdout_log, engine_log)
        audit = json.loads(out_path.read_text(encoding='utf-8')) if out_path.exists() else None
        results.append({'name': 'audit', 'exit_code': code, 'seconds': seconds, 'messages': engine_messages(text), 'result': audit})
        if audit:
            print(f"  audit exit {code}: raw {audit['raw_missing_count']} missing of {audit['raw_checked']}, resources {audit['resources_missing_count']} missing of "
                  f"{audit['resources_checked']}, decoded {audit['decoded_ok']}/{audit['decoded_checked']}, loaded {audit['loaded_ok']}/{audit['loaded_checked']}, "
                  f"music {audit['music_ok']}/{audit['music_checked']}", flush=True)
        else:
            print(f'  audit exit {code}: no result written; see {stdout_log}', flush=True)
    after = {p for p in user_dir.rglob('*') if p.is_file()} if user_dir.exists() else set()
    written = sorted(p.relative_to(ENV_DIR).as_posix() for p in after - before)
    report = {'stamp': datetime.now().isoformat(timespec='seconds'), 'commit': git('rev-parse', '--short', 'HEAD'), 'exe': str(EXE),
              'exe_bytes': EXE.stat().st_size, 'pck_bytes': PCK.stat().st_size, 'frames_per_battle_run': args.frames,
              'user_data_files_written': written[:60], 'user_data_files_written_count': len(written), 'runs': results}
    (RECORD / (f'check_report_{args.tag}.json' if args.tag else 'check_report.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    failed = [row['name'] for row in results if row['exit_code'] != 0]
    print(f"{len(results)} runs, {len(failed)} with a non-zero exit {failed or ''}; {len(written)} user-data files written under env/ (not on C:)")
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    build = sub.add_parser('build')
    build.add_argument('--skip-import', action='store_true', help='reuse the stage import already done')
    build.add_argument('--debug', action='store_true', help='also export a debug build (SableCircuit_debug.exe) for diagnosing')
    check = sub.add_parser('check')
    check.add_argument('--only', default='', help='comma list of boot, flow, perf, audit, native (default: boot, flow, audit)')
    check.add_argument('--perf-frames', type=int, default=2400, help='frames each uncapped perf run lives')
    check.add_argument('--frames', type=int, default=900, help='frames each battle run lives (900 is 15 s at 60 Hz)')
    check.add_argument('--screen', default='1', help='monitor index the windows open on')
    check.add_argument('--tag', default='', help='write record/check_report_<tag>.json instead of check_report.json (a partial rerun keeps the full report)')
    args = parser.parse_args()
    return command_build(args) if args.command == 'build' else command_check(args)


if __name__ == '__main__':
    sys.exit(main())
