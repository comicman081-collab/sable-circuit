"""Make a source-cycle review kit; no active atlas writes or art generation."""
import json
import math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
import character_workflow as w
import cycle_review
import gait_contract as contract


def prepare(character, direction, action='walk'):
    cycle_review.require_pilot(character, direction, action)
    expected = cycle_review.inputs(character, direction, action)
    from preview_gait import preview
    result = preview(character, direction, action)
    c = w.recipe(character)
    clip = result['clip']
    clip['phaseStarts'] = contract.starts(c['clips'][action])
    out = w.local(result['contact']).parents[3]
    atlas_path = out / 'public' / clip['image']
    contact_path = w.local(result['contact'])
    with Image.open(atlas_path) as im:
        atlas = im.convert('RGBA')
    cw, ch = clip['cell']
    frames = [atlas.crop((i % clip['columns'] * cw, i // clip['columns'] * ch,
                         (i % clip['columns'] + 1) * cw, (i // clip['columns'] + 1) * ch)) for i in range(6)]
    speed = c['locomotion']['runSpeed' if action == 'run' else 'walkSpeed']
    stride = c['locomotion']['runStride' if action == 'run' else 'walkStride']
    if not all(cycle_review.finite(v) and v > 0 for v in (speed, stride)):
        raise ValueError('Finite positive speed/stride required')
    duration = max(3 * stride / speed, 2.1)
    # MPEG-4 Part 2 (mp4v) decodes in OpenCV but not the Chromium review page.
    # VP8/WebM is playable by the same browser used for actual runtime QA.
    movie = out / f'{direction}_{action}_cycle_1080p.webm'
    writer = cv2.VideoWriter(str(movie), cv2.VideoWriter_fourcc(*'VP80'), 30, (1920, 1080))
    if not writer.isOpened():
        raise ValueError('Native preview video encoder unavailable')
    theta = w.DIRECTIONS.index(direction) * math.pi / 4
    try:
        for tick in range(math.ceil(duration * 30)):
            t = tick / 30
            phase = (t * speed / stride) % 1
            index = contract.frame_at(phase, clip['phaseStarts'])
            page = Image.new('RGB', (1920, 1080), '#101e27')
            draw = ImageDraw.Draw(page)
            draw.text((28, 20), f'{character.upper()} {direction} {action} | t={t:.3f}s | phase={phase:.3f} | frame={index}', fill='#e4ece9')
            draw.text((28, 48), 'DIAGNOSTIC SOURCE CYCLE / not game-runtime approval / native compiled cell at left; 270px game-scale at right', fill='#b8d4ce')
            draw.text((28, 76), f'contract {contract.digest()[:12]} / source {cycle_review.signature(expected)[:12]} / speed {speed} / stride {stride}', fill='#b8d4ce')
            page.paste(frames[index], (30, 170), frames[index])
            draw.line((30, 170 + clip['root'][1], 30 + cw, 170 + clip['root'][1]), fill='#72897e', width=2)
            ratio = 270 / clip['height']
            small = frames[index].resize((round(cw * ratio), round(ch * ratio)), Image.Resampling.LANCZOS)
            x0, y0 = 1240, 550
            # Root-locked preview, with ground moving at recipe velocity.
            # Source-frame changes are unwarped; slides remain visible.
            dx = t * speed * 270 / c['heightMetres'] * math.cos(theta)
            dy = t * speed * 270 / c['heightMetres'] * .5 * math.sin(theta)
            for x in range(880, 1920, 80):
                xx = 880 + (x - 880 - dx) % 1040
                draw.line((xx, 190, xx, 1000), fill='#2b4349')
            for y in range(190, 1000, 60):
                yy = 190 + (y - 190 - dy) % 810
                draw.line((880, yy, 1910, yy), fill='#2b4349')
            page.paste(small, (x0, y0), small)
            draw.text((900, 1020), 'Observe actual support-foot exchange, sliding and the 5 -> 0 seam. Different pixels are not different steps.', fill='#e4ece9')
            writer.write(cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR))
    finally:
        writer.release()
    cap = cv2.VideoCapture(str(movie))
    native = [int(cap.get(3)), int(cap.get(4))]
    frame_count = 0
    while cap.read()[0]:
        frame_count += 1
    cap.release()
    if native != [1920, 1080] or frame_count != math.ceil(duration * 30):
        raise ValueError('Cycle preview failed native sequential decoding')
    preview = {'kind': 'sable-cycle-preview', 'cycleInputs': expected, 'clip': clip,
               'atlas': w.binding(atlas_path), 'contact': w.binding(contact_path),
               'video': w.binding(movie), 'nativeVideo': native, 'cycles': frame_count / 30 * speed / stride,
               'durationSeconds': frame_count / 30, 'framesDecoded': frame_count,
               'visualApproval': False, 'gameRuntimeApproval': False}
    preview_path = out / 'cycle-preview.json'
    w.write(preview_path, preview)
    packet = {'kind': 'sable-cycle-observation', 'character': character, 'direction': direction,
              'action': action, 'inputs': expected, 'preview': w.binding(preview_path),
              'decision': 'unreviewed', 'reviewer': '', 'legMarkers': {'left': '', 'right': ''},
              'frames': [dict(index=p['index'], phase=p['name'], support=None,
                              landmarks={side + part: None for side in ('left', 'right') for part in ('Hip', 'Knee', 'Sole')}) for p in contract.PHASES],
              'observations': {name: {'decision': 'unreviewed', 'seconds': [], 'notes': ''} for name in cycle_review.OBSERVATIONS}}
    packet_path = out / 'cycle-observations.json'
    w.write(packet_path, packet)
    # Canvas avoids browser-specific native video decoder crashes. It presents
    # the same actual atlas at recipe speed; the encoded evidence stays intact.
    (out/'cycle-live-review.js').write_bytes(Path(__file__).with_name('cycle_live_review.js').read_bytes())
    html = out / 'cycle-review.html'
    html.write_text('<!doctype html><meta charset="utf-8"><title>Cycle review '+character+' '+direction+'</title>'
                   '<style>body{margin:0;background:#101e27;color:#dce9e4;font:20px sans-serif}canvas{display:block;width:1920px;height:1080px}img{display:block}button{font:20px sans-serif;padding:10px}</style>'
                   '<h1>'+character.upper()+' '+direction+' '+action+' — UNREVIEWED</h1>'
                   '<button disabled>1배속으로 세 주기 관찰·기록</button> <span id="status">원화 로딩 중</span>'
                   '<canvas width="1920" height="1080"></canvas>'
                   '<p><a href="'+movie.name+'">Native encoded evidence video</a> · Playback trace is not art approval.</p>'
                   '<script type="module" src="./cycle-live-review.js"></script>'
                   '<img alt="Chronological six-phase source sheet" src="'+contact_path.relative_to(out).as_posix()+'">', encoding='utf-8')
    return {'status': 'UNREVIEWED_CYCLE_KIT', 'packet': str(packet_path), 'preview': str(preview_path),
            'html': str(html), 'video': str(movie), 'inputSHA256': cycle_review.signature(expected)}
