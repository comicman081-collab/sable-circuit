import sys, glob, os
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(os.path.join(src, 'MIS_CH01_0*.png')))
rooms = [f for f in files if os.path.basename(f).split('_', 3)[3].startswith(('R', 'O')) and f.endswith('_a.png')]
conns = [f for f in files if os.path.basename(f).split('_', 3)[3].startswith('C')]
picked = (rooms + conns)[:16]
sheet = Image.new('RGB', (1920, 1080))
for i, path in enumerate(picked):
    im = Image.open(path).convert('RGB').resize((480, 270), Image.LANCZOS)
    ImageDraw.Draw(im).text((6, 4), os.path.basename(path)[11:-4], fill=(255, 255, 0))
    sheet.paste(im, ((i % 4) * 480, (i // 4) * 270))
sheet.save(out)
