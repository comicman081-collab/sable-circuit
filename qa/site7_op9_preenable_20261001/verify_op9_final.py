import sys, json, hashlib, os
from types import SimpleNamespace
sys.path.insert(0, 'tools/environment')
import numpy as np
from PIL import Image
import audit_site7_plate_lighting as A
floors = json.load(open('data/visual/site7_plate_floors.json', encoding='utf-8'))['plates']
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
want = {  # from Codex's manifest (RAW == MASTER for ImageGen native output), factor
    'S9_C06': ('6ec901123478b69217010297367e7bc136193ce3db09d497d102053568e64269', 'a23350dc5c3276888f0a45b665ec59530b11316e9585a2ecd0e6cdbe5b13cfac', 0.7574),
    'S9_C07': ('4106b19c7543c645268c92086698be5e6ba3a80772f32c058f3e179f3831f354', '0c7ee943b5a8fc09f2a4fbd6a76761c93eb324efb866d8499ded7cbf296b4197', 0.6822),
}
ids = sorted(os.path.basename(k)[:-len('_GAME.png')] for k in floors if '/stage09/' in k)
print(len(ids), 'S9 plate rows:', ids)
bad = 0
for pid in ids:
    raw = f'art_src/environments/site7_v2/stage09/{pid}/{pid}_RAW_NATIVE.png'
    mas = f'art_src/environments/site7_v2/stage09/{pid}/{pid}_MASTER.png'
    game = f'assets/environments/site7_v2/stage09/{pid}/{pid}_GAME.png'
    exists = all(os.path.exists(p) for p in (raw, mas, game)) and os.path.exists(game + '.import')
    if not exists:
        print(pid, 'MISSING FILES'); bad += 1; continue
    im = Image.open(game); mim = np.asarray(Image.open(mas).convert('RGB')); gim = np.asarray(im.convert('RGB'))
    rawhash, masterhash, gamehash = sha(raw), sha(mas), sha(game)
    same_rm = rawhash == masterhash
    # exposure factor: ratio estimate on bright pixels, then exact LUT check on the neighbouring 4-decimal values
    sel = mim > 80
    est = float(np.median(gim[sel].astype(float) / mim[sel].astype(float)))
    best = None
    for f in [round(est + k * 0.0001, 4) for k in range(-6, 7)]:
        lut = np.clip(np.round(np.arange(256) * f), 0, 255).astype(np.uint8)
        d = int(np.abs(lut[mim].astype(int) - gim.astype(int)).max())
        if best is None or d < best[0]: best = (d, f)
        if d == 0: break
    fl = floors[game]
    plate = SimpleNamespace(asset=game, floor=[tuple(p) for p in fl['floor']])
    pf = A.plate_floor(plate)
    extra = ''
    if pid in want:
        wr, wg, wf = want[pid]
        extra = f" | manifest raw={rawhash==wr} game={gamehash==wg} factor={best[1]} vs {wf}"
        if not (rawhash == wr and gamehash == wg): bad += 1
    ok = same_rm and im.mode == 'RGB' and best[0] == 0 and not pf['problems']
    bad += not ok
    print(f"{pid}: {'OK ' if ok else 'BAD'} size {im.size} mode {im.mode} raw==master {same_rm} lutdiff {best[0]}@{best[1]} corner {tuple(int(v) for v in mim[2,2])} | axis {pf['axis']:.2f} luma {pf['luma']:.3f} sat {pf['saturation']:.3f} {pf['problems']}{extra}")
print('problems:', bad)
