"""Build an isolated, source-preserving Godot Web demo for Sites hosting."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import math
import re
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / '.cache/sites_godot'
SITE = ROOT / 'web_demo'
DIST = SITE / 'dist'
# Build records go to a new dated folder per build (--qa=<folder> to choose), never
# back into an earlier release's record folder. --scripts-only reads the prior full
# build's derivative manifests from --qa, so pass that build's folder with it.
QA = ROOT / next((a.split('=', 1)[1] for a in sys.argv if a.startswith('--qa=')),
                 'qa/web_build_' + __import__('datetime').date.today().strftime('%Y%m%d'))
GODOT = Path('D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64.exe')
REQUIRED_UNIT_ASSETS = {'assets/units/operators/aster/vfx/ASTER_COIL_PROJECTILE_V6_RGBA.webp'}
# Retain the silent predecessor in the project, but do not package it beside
# its validated original-audio replacement.
WEB_EXCLUDED_ASSETS = {'assets/cinematics/sable_intro.ogv'}
WEB_MOTION_ATLAS_ROOT = Path('motion_lab_v1/public/assets/atlas')
# The title-screen squad lineup draws these three idle frames at near-native
# size, so the web pack keeps their approved full-resolution atlases too.
TITLE_FULL_RES_ATLASES = {
    'motion_lab_v1/public/assets/atlas/aster/S_idle.webp',
    'motion_lab_v1/public/assets/atlas/rook/SE_idle.webp',
    'motion_lab_v1/public/assets/atlas/mica/SW_idle.webp',
}

def remove_staged(relative: str):
    target = STAGE / relative
    for path in (target, target.with_suffix(target.suffix + '.import'), target.with_suffix(target.suffix + '.uid')):
        if path.exists():
            path.unlink()

def preserve_live_unit_assets():
    """Exclude retired units by subtree, never their still-active projectile."""
    exclusions = []
    def visit(path):
        relative = path.relative_to(STAGE).as_posix()
        if relative in REQUIRED_UNIT_ASSETS:
            return
        if not any(allowed.startswith(relative + '/') for allowed in REQUIRED_UNIT_ASSETS):
            exclusions.append(relative + '/*' if path.is_dir() else relative)
            return
        for child in sorted(path.iterdir()):
            if child.suffix not in ('.import', '.uid'):
                visit(child)
    for relative in REQUIRED_UNIT_ASSETS:
        source, target = ROOT / relative, STAGE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        target.with_suffix(target.suffix+'.import').write_text('[remap]\n\nimporter="keep"\n', encoding='utf8')
        assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(target.read_bytes()).digest()
    visit(STAGE / 'assets/units')
    preset = STAGE / 'export_presets.cfg'
    content = preset.read_text(encoding='utf8')
    # Idempotent: after the first repair this broad exclusion no longer exists.
    content = content.replace('assets/units/*', ','.join(exclusions))
    preset.write_text(content, encoding='utf8')

def derive_web_motion_atlases():
    """Downsample delivery copies only; never touch approved Studio atlases."""
    rows = []
    for source in sorted((ROOT / WEB_MOTION_ATLAS_ROOT).rglob('*.webp')):
        if source.name.endswith('.web.webp'):
            continue
        relative = source.relative_to(ROOT)
        derivative = (STAGE / relative).with_name(source.stem + '.web.webp')
        derivative.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source) as original:
            rgba = original.convert('RGBA')
            if rgba.width % 2 or rgba.height % 2:
                raise RuntimeError('Motion atlas is not divisible by two: ' + str(relative))
            reduced = rgba.resize((rgba.width // 2, rgba.height // 2), Image.Resampling.LANCZOS)
            reduced.save(derivative, 'WEBP', quality=95, method=4, exact=True)
            with Image.open(derivative) as encoded:
                decoded = encoded.convert('RGBA')
            if ImageChops.difference(reduced.getchannel('A'), decoded.getchannel('A')).getbbox():
                raise RuntimeError('Web motion atlas alpha changed: ' + str(relative))
            backdrop = Image.new('RGBA', reduced.size, (12, 24, 32, 255))
            expected = Image.alpha_composite(backdrop, reduced).convert('RGB')
            actual = Image.alpha_composite(backdrop, decoded).convert('RGB')
            rms = ImageStat.Stat(ImageChops.difference(expected, actual)).rms
            mse = sum(value * value for value in rms) / 3
            psnr = 10 * math.log10(255 * 255 / max(mse, 1e-10))
            if psnr < 34:
                raise RuntimeError('Web motion atlas compression quality below floor: ' + str(relative))
        derivative.with_suffix('.webp.import').write_text('[remap]\n\nimporter="keep"\n', encoding='utf8')
        rows.append({'source':relative.as_posix(),
                     'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                     'derivative':derivative.relative_to(STAGE).as_posix(),
                     'derivative_sha256':hashlib.sha256(derivative.read_bytes()).hexdigest(),
                     'source_dimensions':list(rgba.size), 'dimensions':list(reduced.size),
                     'alpha_unchanged_after_resize':True, 'psnr_db':psnr})
    (QA / 'web_motion_atlas_derivatives.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf8')
    print('WEB_MOTION_ATLASES', len(rows), sum((STAGE / row['derivative']).stat().st_size for row in rows), flush=True)
    return rows

def derive_web_machine_views():
    """Pack separate half-size robot views, preserving hashed PNG masters."""
    profiles = json.loads((ROOT / 'data/art_profiles/enemy_profiles.json').read_text(encoding='utf8'))['profiles']
    source_paths = set()
    for profile in profiles:
        machine = profile.get('machine_asset', {})
        if not machine:
            continue
        spec = json.loads((ROOT / machine['spec'].removeprefix('res://')).read_text(encoding='utf8'))
        for view in (spec['views'].values() if 'views' in spec else [spec]):
            source_paths.add(view['texture'].removeprefix('res://'))
    rows = []
    for relative_name in sorted(source_paths):
        source = ROOT / relative_name
        derivative = (STAGE / relative_name).with_suffix('.web.webp')
        derivative.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source) as original:
            rgba = original.convert('RGBA')
            reduced = rgba.resize((rgba.width // 2, rgba.height // 2), Image.Resampling.LANCZOS)
            reduced.save(derivative, 'WEBP', quality=95, method=4, exact=True)
            with Image.open(derivative) as encoded:
                decoded = encoded.convert('RGBA')
            if ImageChops.difference(reduced.getchannel('A'), decoded.getchannel('A')).getbbox():
                raise RuntimeError('Web machine alpha changed: ' + relative_name)
            backdrop = Image.new('RGBA', reduced.size, (12, 24, 32, 255))
            expected = Image.alpha_composite(backdrop, reduced).convert('RGB')
            actual = Image.alpha_composite(backdrop, decoded).convert('RGB')
            rms = ImageStat.Stat(ImageChops.difference(expected, actual)).rms
            mse = sum(value * value for value in rms) / 3
            psnr = 10 * math.log10(255 * 255 / max(mse, 1e-10))
            if psnr < 34:
                raise RuntimeError('Web machine compression quality below floor: ' + relative_name)
        derivative.with_suffix('.webp.import').write_text('[remap]\n\nimporter="keep"\n', encoding='utf8')
        rows.append({'source':relative_name,
                     'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                     'derivative':derivative.relative_to(STAGE).as_posix(),
                     'derivative_sha256':hashlib.sha256(derivative.read_bytes()).hexdigest(),
                     'source_dimensions':list(rgba.size), 'dimensions':list(reduced.size),
                     'alpha_unchanged_after_resize':True, 'psnr_db':psnr})
    (QA / 'web_machine_view_derivatives.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf8')
    print('WEB_MACHINE_VIEWS', len(rows), sum((STAGE / row['derivative']).stat().st_size for row in rows), flush=True)
    return rows

def run(args, name):
    env = os.environ.copy()
    for key in ('TEMP', 'TMP', 'XDG_CACHE_HOME'):
        dest = ROOT / '.cache/sites_tmp' / key.lower()
        dest.mkdir(parents=True, exist_ok=True)
        env[key] = str(dest)
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    with (QA / (name + '.log')).open('w', encoding='utf8') as log:
        proc = subprocess.run([str(GODOT), '--headless', '--path', str(STAGE), *args],
                              cwd=STAGE, env=env, startupinfo=startup,
                              stdout=log, stderr=subprocess.STDOUT, timeout=600)
    print(name, proc.returncode, flush=True)
    if proc.returncode:
        raise RuntimeError((QA / (name + '.log')).read_text(encoding='utf8'))

def prepare():
    for folder in (STAGE, DIST, QA):
        folder.mkdir(parents=True, exist_ok=True)
    paths = []
    web_plates = []
    for folder in ('scripts', 'scenes', 'data', 'assets', 'sound/music/runtime', 'motion_lab_v1/public/assets/atlas'):
        for source in (ROOT / folder).rglob('*'):
            if not source.is_file() or source.suffix in ('.import', '.uid'):
                continue
            relative = source.relative_to(ROOT)
            if relative.as_posix().startswith('assets/external/') or relative.as_posix() in WEB_EXCLUDED_ASSETS:
                remove_staged(relative.as_posix())
                continue
            target = STAGE / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or source.stat().st_mtime_ns > target.stat().st_mtime_ns:
                shutil.copy2(source, target)
            # All game texture readers consume original bytes, not imported textures.
            # Keep them lossless and prevent duplicate GPU texture packs in the export.
            if source.suffix.lower() in ('.png', '.webp', '.jpg', '.jpeg'):
                target.with_suffix(target.suffix + '.import').write_text('[remap]\n\nimporter="keep"\n', encoding='utf8')
            paths.append({'path':relative.as_posix(), 'bytes':source.stat().st_size,
                          'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
            if (relative.as_posix().startswith('assets/environments/') and source.suffix == '.png'
                    and 'karchive_props_v1' not in relative.parts and 'props' not in relative.parts):
                with Image.open(source) as source_image:
                    rgb = source_image.convert('RGBA')
                    derived = target.with_suffix('.webp')
                    rgb.save(derived, 'WEBP', quality=95, method=4, exact=True)
                    derived.with_suffix('.webp.import').write_text('[remap]\n\nimporter="keep"\n', encoding='utf8')
                    with Image.open(derived) as decoded:
                        decoded_rgba = decoded.convert('RGBA')
                        if ImageChops.difference(rgb.getchannel('A'), decoded_rgba.getchannel('A')).getbbox():
                            raise RuntimeError('Web plate alpha was altered: '+str(relative))
                        backdrop = Image.new('RGBA', rgb.size, (12,24,32,255))
                        original_visible = Image.alpha_composite(backdrop, rgb).convert('RGB')
                        derived_visible = Image.alpha_composite(backdrop, decoded_rgba).convert('RGB')
                        rms = ImageStat.Stat(ImageChops.difference(original_visible, derived_visible)).rms
                        mse = sum(value * value for value in rms) / 3
                        psnr = 10 * math.log10(255*255 / max(mse, 1e-10))
                    if psnr < 34:
                        raise RuntimeError('Web plate compression quality below floor: '+str(relative))
                    web_plates.append({'source':relative.as_posix(), 'source_sha256':paths[-1]['sha256'],
                                       'derived':derived.relative_to(STAGE).as_posix(),
                                       'derived_sha256':hashlib.sha256(derived.read_bytes()).hexdigest(),
                                       'dimensions':list(rgb.size), 'alpha_unchanged':True,
                                       'bytes':derived.stat().st_size, 'psnr_db':psnr})
    web_motion_atlases = derive_web_motion_atlases()
    derive_web_machine_views()
    shutil.copy2(ROOT / 'project.godot', STAGE / 'project.godot')
    preset = '''[preset.0]
name="Web"
platform="Web"
runnable=true
export_filter="all_resources"
include_filter="*.json,*.png,*.webp,*.jpg,*.jpeg,*.ogg,*.wav,*.mp3,*.ogv,*.txt,*.b64.*"
exclude_filter="assets/units/*"
export_path=""
script_export_mode=0
[preset.0.options]
variant/extensions_support=false
variant/thread_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=false
html/export_icon=true
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
progressive_web_app/enabled=false
'''
    (STAGE / 'export_presets.cfg').write_text(preset, encoding='utf8')
    excluded = [row['source'] for row in web_plates + web_motion_atlases if row['source'] not in TITLE_FULL_RES_ATLASES]
    preset = preset.replace('exclude_filter="assets/units/*"', 'exclude_filter="assets/units/*,' + ','.join(excluded) + '"')
    (STAGE / 'export_presets.cfg').write_text(preset, encoding='utf8')
    (QA / 'source_manifest.json').write_text(json.dumps(paths, ensure_ascii=False, indent=2), encoding='utf8')
    (QA / 'web_plate_derivatives.json').write_text(json.dumps(web_plates, ensure_ascii=False, indent=2), encoding='utf8')
    print('WEB_PLATES', len(web_plates), sum(row['bytes'] for row in web_plates), flush=True)
    print('STAGED', len(paths), sum(row['bytes'] for row in paths), flush=True)

def package_chunks():
    manifests = {}
    for name in ('index.pck', 'index.wasm'):
        path = DIST / name
        digest = hashlib.sha256()
        chunks = []
        with path.open('rb') as stream:
            while data := stream.read(20 * 1024 * 1024):
                digest.update(data)
                chunk_name = f'{name}.{len(chunks):03d}.bin'
                (DIST / chunk_name).write_bytes(data)
                chunks.append({'url':chunk_name, 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()})
        manifests[name] = {'bytes':path.stat().st_size, 'sha256':digest.hexdigest(), 'chunks':chunks}
        # Generated delivery file only: the byte-identical sharded version is now verified.
        assert sum(x['bytes'] for x in chunks) == path.stat().st_size
        path.unlink()
    (DIST / 'chunks.json').write_text(json.dumps(manifests), encoding='utf8')
    # The page shell the rewritten index.html loads: chunk reassembly, loading-screen
    # styles and the read-only status tool. Tracked here so a clean checkout builds a
    # complete dist.
    for shell_file in sorted((ROOT / 'tools/environment/web_shell').iterdir()):
        shutil.copy2(shell_file, DIST / shell_file.name)
    # Retire only this builder's obsolete delivery shards after re-chunking.
    live_chunks = {c['url'] for item in manifests.values() for c in item['chunks']}
    for old_chunk in DIST.glob('index.*.*.bin'):
        if old_chunk.name not in live_chunks:
            old_chunk.unlink()
    html = (DIST / 'index.html').read_text(encoding='utf8')
    html = html.replace('<title>SABLE CIRCUIT</title>', '<title>SABLE CIRCUIT — Playable Demo</title>')
    html = html.replace('<script src="index.js"></script>', '<script src="chunk-loader.js"></script>\n<script src="index.js"></script>')
    html = html.replace('</head>', '<link rel="stylesheet" href="web-ui.css"><script defer src="web-ui.js"></script></head>')
    html = html.replace('<progress id="status-progress">', '<h1 class="loading-brand">SABLE CIRCUIT</h1><p class="loading-copy">Loading the five-operation demo. The first download may take a few minutes.</p><progress id="status-progress">')
    html = html.replace('<link id="-gd-engine-icon" rel="icon" type="image/png" href="index.icon.png" />', '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 32\'%3E%3Crect width=\'32\' height=\'32\' rx=\'6\' fill=\'%230c1b24\'/%3E%3Cpath d=\'M24 8H8v8h16v8H8\' fill=\'none\' stroke=\'%239affec\' stroke-width=\'3\'/%3E%3C/svg%3E">')
    (DIST / 'index.html').write_text(html, encoding='utf8')
    patch_frame_blit()
    trim_unused_export_icons()
    print('CHUNKS', {k: v['bytes'] for k,v in manifests.items()}, flush=True)

def patch_frame_blit():
    """Emscripten's per-frame copy of the offscreen framebuffer to the canvas reads the
    scissor state with getParameter(SCISSOR_TEST). In Chromium that is a synchronous
    GPU-process round trip every frame (19% of main-thread time in combat,
    qa/web_fps_20260925); isEnabled returns the same boolean without one."""
    path = DIST / 'index.js'
    js = path.read_bytes()
    old, new = b'var prevScissorTest=gl.getParameter(3089)', b'var prevScissorTest=gl.isEnabled(3089)'
    if js.count(old) != 1:
        raise RuntimeError('Emscripten blit scissor read not found once in index.js; review the patch')
    path.write_bytes(js.replace(old, new))

def trim_unused_export_icons():
    """The custom loader hides the engine splash and already embeds its icon."""
    html_path = DIST / 'index.html'
    html = html_path.read_text(encoding='utf8')
    icon = re.search(r'<link rel="icon" type="image/svg\+xml" href="([^"]+)"', html)
    if not icon:
        raise RuntimeError('Missing embedded Site icon; preserve exported icons')
    html = html.replace('href="index.apple-touch-icon.png"', 'href="'+icon.group(1)+'"')
    html = html.replace('src="index.png"', 'src="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\'/%3E"')
    html_path.write_text(html, encoding='utf8')
    # Only this builder's reproducible exports; never source art or masters.
    for name in ('index.png', 'index.icon.png', 'index.apple-touch-icon.png'):
        path = DIST / name
        assert path.resolve().parent == DIST.resolve()
        if path.exists():
            path.unlink()

if __name__ == '__main__':
    # Only runtime music is exported, never duplicate originals or source paths.
    runtime_sources = {source.name for source in (ROOT / 'sound/music/runtime').glob('*.mp3')}
    staged_runtime = STAGE / 'sound/music/runtime'
    if staged_runtime.exists():
        for staged in staged_runtime.glob('*.mp3'):
            if staged.name not in runtime_sources:
                remove_staged(staged.relative_to(STAGE).as_posix())
    for source in (ROOT / 'sound/music/runtime').glob('*.mp3'):
        target = STAGE / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        target.with_suffix('.mp3.import').write_text('[remap]\n\nimporter="keep"\n', encoding='utf8')
    if (ROOT / 'sound/music/catalog.json').exists():
        (STAGE / 'sound/music').mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / 'sound/music/catalog.json', STAGE / 'sound/music/catalog.json')
    if '--scripts-only' in sys.argv:
        # Reuse the prior asset build only after binding it to unchanged masters.
        for row in json.loads((QA / 'web_plate_derivatives.json').read_text(encoding='utf8')):
            assert hashlib.sha256((ROOT / row['source']).read_bytes()).hexdigest() == row['source_sha256']
        for manifest_name in ('web_motion_atlas_derivatives.json', 'web_machine_view_derivatives.json'):
            for row in json.loads((QA / manifest_name).read_text(encoding='utf8')):
                assert hashlib.sha256((ROOT / row['source']).read_bytes()).hexdigest() == row['source_sha256']
                assert hashlib.sha256((STAGE / row['derivative']).read_bytes()).hexdigest() == row['derivative_sha256']
        rows = json.loads((QA / 'source_manifest.json').read_text(encoding='utf8'))
        rows = [row for row in rows if not row['path'].startswith(('scripts/', 'sound/music/'))]
        for source in list((ROOT / 'scripts').rglob('*.gd')) + list((ROOT / 'sound/music/runtime').glob('*.mp3')) + [ROOT / 'sound/music/catalog.json']:
            relative = source.relative_to(ROOT)
            target = STAGE / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            rows.append({'path':relative.as_posix(), 'bytes':source.stat().st_size,
                         'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
        preset_path = STAGE / 'export_presets.cfg'
        preset = preset_path.read_text(encoding='utf8')
        if '*.mp3' not in preset: preset_path.write_text(preset.replace('*.ogg,', '*.ogg,*.mp3,'), encoding='utf8')
        preset = preset_path.read_text(encoding='utf8')
        for title_atlas in TITLE_FULL_RES_ATLASES:
            preset = preset.replace(',' + title_atlas + ',', ',').replace(',' + title_atlas + '"', '"')
        preset_path.write_text(preset, encoding='utf8')
        (QA / 'source_manifest.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf8')
    else:
        prepare()
        run(['--editor', '--import'], 'import')
    preserve_live_unit_assets()
    run(['--export-release', 'Web', str(DIST / 'index.html')], 'export')
    run(['--main-pack', str(DIST / 'index.pck'), '--script',
         str(ROOT / 'tests/smoke/demo_packed_assets_smoke.gd')], 'packed_assets')
    package_chunks()
