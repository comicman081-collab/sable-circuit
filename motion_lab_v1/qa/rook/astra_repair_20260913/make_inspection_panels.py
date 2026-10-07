"""Native-pixel diagnostic layouts only; no art alteration or runtime writes."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
STAGE = ROOT / 'qa/build_candidates/rook/f06f3dfe300c42ceab0a7aae86e14f4a'
OUT = Path(__file__).resolve().parent
directions = ['E', 'SE', 'S', 'SW', 'W', 'NW', 'N', 'NE']
panel = Image.new('RGB', (3072, 1536), '#121c24')
for i, d in enumerate(directions):
    frame = Image.open(STAGE / f'reference/atlas/rook/{d}_idle_keyframes.png')
    assert frame.size == (768, 768)
    panel.paste(frame, (i % 4 * 768, i // 4 * 768))
panel.save(OUT / 'idle_native_compiled_3072x1536.png')
(OUT / 'idle_native_compiled_3072x1536.json').write_text(json.dumps({
    'nativeDimensions': list(panel.size), 'sourceCell': [768, 768],
    'pixelUpscaling': False, 'candidateOnly': True, 'stage': str(STAGE),
    'note': 'Compiled cell inspection, not source-resolution approval or runtime delivery.'
}, indent=2), encoding='utf-8')
print(OUT / 'idle_native_compiled_3072x1536.png')
