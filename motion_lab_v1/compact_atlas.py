"""Pack existing vertical FastRuntime cells without changing pixels or timing.

Local project adapter, not image generation or a SpriteGen exporter. New
authored-frame characters keep the Motion Studio compiler; this tool is for
explicit legacy-descriptor imports only. All outputs are isolated under qa/.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
from PIL import Image

LAB = Path(__file__).resolve().parent
PROJECT = LAB.parent
DIRECTIONS = ('E', 'SE', 'S', 'SW', 'W', 'NW', 'N', 'NE')
STATES = ('idle', 'move', 'fire')

def require(condition, message):
    if not condition:
        raise ValueError(message)

def local(root, value):
    path = (root / value).resolve()
    require(path != root.resolve() and path.is_relative_to(root.resolve()), 'Path escapes declared project root')
    return path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def rgba(path):
    with Image.open(path) as source:
        require(source.mode == 'RGBA', f'Expected actual RGBA atlas, not automatic alpha conversion: {path.name}')
        return source.copy()

def descriptor(root, path):
    value = read(path)
    size = value['cell_size']
    require(type(size) is int and 1 <= size <= 2048, 'Invalid cell size')
    require(set(value['directions']) == set(DIRECTIONS), 'Exactly eight descriptor directions required')
    require(set(value['states']) == set(STATES), 'Supported import states: idle/move/fire')
    for state, spec in value['states'].items():
        fps, count = spec['fps'], spec['frames']
        require(type(count) is int and 0 < count <= 256, 'Invalid frame count')
        require(type(fps) in (float, int) and math.isfinite(fps) and fps > 0, 'Invalid positive FPS')
        for direction in DIRECTIONS:
            local(root, value['directions'][direction][state + '_atlas'])
    return value

def verify(root, manifest_path):
    root = root.resolve()
    manifest_path = local(root, manifest_path)
    manifest = read(manifest_path)
    require(manifest['kind'] == 'lossless_explicit_cells', 'Unsupported manifest kind')
    source = local(root, manifest['source_descriptor']['path'])
    require(sha(source) == manifest['source_descriptor']['sha256'], 'Source descriptor changed')
    desc = descriptor(root, source)
    size = desc['cell_size']
    for key in ('cell_size', 'display_scale', 'display_offset', 'states'):
        require(manifest[key] == desc[key], f'Contract changed: {key}')
    require(set(manifest['directions']) == set(DIRECTIONS), 'Missing/extra compact direction')
    cells = before = after = png_before = png_after = max_edge = 0
    for direction in DIRECTIONS:
        row = manifest['directions'][direction]
        page_path = local(root, row['texture'])
        require(sha(page_path) == row['sha256'], 'Packed image changed')
        page = rgba(page_path)
        require(list(page.size) == row['size'], 'Page dimensions differ')
        require(row['muzzle_xy'] == desc['directions'][direction]['muzzle_xy'], 'Muzzle/pivot contract changed')
        require(set(row['states']) == set(STATES), 'Missing/extra state')
        bound = {item['path']: item['sha256'] for item in row['sources']}
        require(len(bound) == len(STATES), 'Incomplete original texture bindings')
        for state in STATES:
            source_path = local(root, desc['directions'][direction][state + '_atlas'])
            require(bound.get(source_path.relative_to(root).as_posix()) == sha(source_path), 'Original texture changed')
            original = rgba(source_path)
            spec = desc['states'][state]
            require(original.size == (size, size * spec['frames']), 'Unsupported source cell layout')
            frames = row['states'][state]
            require(len(frames) == spec['frames'], 'Stored duplicates must retain all timing slots')
            for index, cell in enumerate(frames):
                require(cell['source_frame'] == index, 'Frame order changed')
                duration = cell['duration_seconds']
                require(type(duration) in (float, int) and math.isfinite(duration) and
                        math.isclose(duration, 1 / spec['fps'], rel_tol=0, abs_tol=1e-12), 'Frame duration changed')
                x, y, w, h = (cell[key] for key in ('x', 'y', 'w', 'h'))
                require(all(type(n) is int for n in (x, y, w, h)), 'Integer cell rectangle required')
                require(w == h == size and 0 <= x <= page.width - w and 0 <= y <= page.height - h, 'Cell outside page')
                expected = original.crop((0, index * size, size, (index + 1) * size)).tobytes()
                actual = page.crop((x, y, x + w, y + h)).tobytes()
                require(actual == expected, 'Decoded RGBA differs from original (including hidden RGB)')
                require(hashlib.sha256(actual).hexdigest() == cell['rgba_sha256'], 'Cell digest differs')
                cells += 1
            before += original.width * original.height * 4
            png_before += source_path.stat().st_size
        after += page.width * page.height * 4
        png_after += page_path.stat().st_size
        max_edge = max(max_edge, *page.size)
    return {'rgba_exact_timing_cells': cells, 'timing_unchanged': True, 'resampled': False,
            'source_rgba_base_bytes': before, 'candidate_rgba_base_bytes': after,
            'source_png_bytes': png_before, 'candidate_png_bytes': png_after,
            'max_texture_edge': max_edge, 'scope': 'PIXEL_AND_TIMING_ONLY', 'production_approved': False}

def pack(root, source_path, output, columns=4):
    root = root.resolve()
    source_path = local(root, source_path)
    output = local(root / 'motion_lab_v1/qa', output)
    require(type(columns) is int and 1 <= columns <= 8, 'Use one to eight page columns')
    require(not output.exists(), 'Existing candidate preserved; choose a fresh output directory')
    desc = descriptor(root, source_path)
    size = desc['cell_size']
    manifest = {key: desc[key] for key in ('cell_size', 'display_scale', 'display_offset', 'states')}
    manifest.update(schema=1, kind='lossless_explicit_cells', production_approved=False,
                    source_descriptor={'path': source_path.relative_to(root).as_posix(), 'sha256': sha(source_path)},
                    directions={})
    output.mkdir(parents=True)  # Keep failed candidates; never overwrite/delete them on failure.
    for direction in DIRECTIONS:
        unique, indices, rows, sources = [], {}, {}, []
        for state in STATES:
            path = local(root, desc['directions'][direction][state + '_atlas'])
            original = rgba(path)
            spec = desc['states'][state]
            require(original.size == (size, size * spec['frames']), 'Unsupported source layout')
            sources.append({'path': path.relative_to(root).as_posix(), 'sha256': sha(path)})
            frames = []
            for index in range(spec['frames']):
                cell = original.crop((0, index * size, size, (index + 1) * size))
                digest = hashlib.sha256(cell.tobytes()).hexdigest()
                if digest not in indices:
                    indices[digest] = len(unique)
                    unique.append(cell)
                target = indices[digest]
                frames.append({'x': target % columns * size, 'y': target // columns * size,
                               'w': size, 'h': size, 'duration_seconds': 1 / spec['fps'],
                               'source_frame': index, 'rgba_sha256': digest})
            rows[state] = frames
        page_size = (columns * size, math.ceil(len(unique) / columns) * size)
        require(max(page_size) <= 8192, 'Candidate page exceeds adapter limit; choose another layout')
        page = Image.new('RGBA', page_size)
        for index, cell in enumerate(unique):
            page.paste(cell, (index % columns * size, index // columns * size))
        path = output / f'{direction}.png'
        page.save(path, optimize=True)
        manifest['directions'][direction] = {
            'texture': path.relative_to(root).as_posix(), 'sha256': sha(path), 'size': list(page.size),
            'unique_cells': len(unique), 'states': rows, 'sources': sources,
            'muzzle_xy': desc['directions'][direction]['muzzle_xy']}
    manifest_path = output / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    checks = verify(root, manifest_path)
    manifest['checks'] = checks
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return {'manifest': str(manifest_path), 'checks': checks}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    command = sub.add_parser('pack')
    command.add_argument('--descriptor', required=True, type=Path)
    command.add_argument('--output', required=True, type=Path, help='Fresh directory below motion_lab_v1/qa')
    command.add_argument('--columns', type=int, default=4)
    command = sub.add_parser('verify')
    command.add_argument('--manifest', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = (pack(PROJECT, args.descriptor.resolve(), args.output.resolve(), args.columns)
                  if args.command == 'pack' else verify(PROJECT, args.manifest.resolve()))
        print(json.dumps(result))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'NEEDS_FIX', 'error': str(error)}))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
