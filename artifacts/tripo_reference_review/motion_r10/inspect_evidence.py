"""Independent read-only source/alpha and decoded temporal evidence inspection."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageSequence
from scipy.ndimage import label, binary_propagation

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent

def ref(path):
    p = ROOT / path
    return {'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def checked(reference):
    assert ref(reference['path']) == reference
    return ROOT / reference['path']

base = ROOT / 'artifacts/quarantine/generation_diagnostics/mica_direction_alpha_r01'
manifest = read(base / 'MANIFEST.json')
for key in ('source_report', 'builder', 'alpha_implementation', 'contact', 'battle_scale'):
    checked(manifest[key])
boards = {kind: Image.new('RGB', (1920,1080), (50,55,60)) for kind in ('residual', 'removed_teal')}
alpha_rows = []
for index, row in enumerate(manifest['directions']):
    qa = read(checked(row['qa']))
    source_path = ROOT / qa['input']
    assert ref(source_path)['sha256'] == qa['input_sha256']
    checked(qa['previous_mask']); checked(qa['original_scale_evidence'])
    original = Image.open(source_path).convert('RGB')
    derived = Image.open(checked(row['rgba'])).convert('RGBA')
    rgb = np.asarray(original); rgba = np.asarray(derived); values = rgb.astype(np.int16)
    family = ((values[:,:,1]>=12)&(values[:,:,1]-values[:,:,0]>=16)&(values[:,:,1]-values[:,:,2]>=16)
              &(values[:,:,1]*4>=values[:,:,0]*5)&(values[:,:,1]*4>=values[:,:,2]*5))
    seed = ((values[:,:,1]>=64)&(values[:,:,1]-values[:,:,0]>=45)&(values[:,:,1]-values[:,:,2]>=45)
            &(values[:,:,1]*4>=values[:,:,0]*5)&(values[:,:,1]*4>=values[:,:,2]*5))
    expected = binary_propagation(seed, mask=family)
    transparent = rgba[:,:,3]==0
    residual = family & ~transparent
    # This numerical subset is a diagnostic locator, not a semantic declaration
    # that every selected pixel depicts cyan equipment rather than green spill.
    teal_probe = ((values[:,:,1]>=100)&(values[:,:,1]-values[:,:,0]>=30)
                  &(abs(values[:,:,1]-values[:,:,2])<=30)) & transparent
    record = {'direction': row['direction'], 'source': ref(source_path), 'rgba': row['rgba'],
              'qa': row['qa'], 'original_scale_evidence': qa['original_scale_evidence'],
              'alpha_matches_independent_scipy_four_connected_propagation': bool(np.array_equal(expected, transparent)),
              'retained_rgb_byte_exact': bool(np.array_equal(rgb[~transparent],rgba[~transparent,:3])),
              'transparent_rgb_zeroed': bool(np.all(rgba[transparent,:3]==0)),
              'residual_green_family_pixels': int(residual.sum()),
              'removed_teal_numeric_probe_pixels': int(teal_probe.sum()), 'crops': {}}
    for kind, target in (('residual', residual), ('removed_teal', teal_probe)):
        labels,n = label(target); sizes=np.bincount(labels.ravel()); sizes[0]=0
        if not n: continue
        largest=int(np.argmax(sizes)); y,x=np.where(labels==largest)
        cx,cy=int(round(x.mean())),int(round(y.mean())); box=(cx-110,cy-110,cx+110,cy+110)
        left=original.crop(box); cut=derived.crop(box)
        right=Image.new('RGBA',(220,220),(232,234,237,255));right.alpha_composite(cut)
        px=(index%4)*480;py=(index//4)*540
        board=boards[kind];draw=ImageDraw.Draw(board)
        draw.text((px+12,py+15),f'{row["direction"]} {kind}: original / derived (1:1)',fill='white')
        draw.text((px+12,py+33),f'source crop {box}',fill='white')
        board.paste(left,(px+10,py+65));board.paste(right.convert('RGB'),(px+245,py+65))
        dark=Image.new('RGBA',(220,220),(17,25,33,255));dark.alpha_composite(cut)
        board.paste(dark.convert('RGB'),(px+245,py+300))
        record['crops'][kind]={'source_xyxy':list(box),'largest_cluster_pixels':int(sizes[largest])}
    alpha_rows.append(record)
board_refs=[]
for kind, board in boards.items():
    path=OUT/f'ALPHA_{kind.upper()}_NATIVE_1920x1080.png';board.save(path);board_refs.append(ref(path))
alpha_report={'scope':'exact-alpha relationship and original-scale contextual locators only',
              'production_ready':False,'manifest':ref(base/'MANIFEST.json'),'directions':alpha_rows,
              'boards':board_refs,'analysis_script':ref(__file__)}
(OUT/'ALPHA_QA_R1.json').write_text(json.dumps(alpha_report,indent=2)+'\n',encoding='utf-8')

run=ROOT/'artifacts/quarantine/generation_diagnostics/mica_source_skin_run_r01'
rows=[]
for p in sorted(run.glob('BATTLE_SCALE_[0-9]*.png')):
    decoded=Image.open(p).convert('RGBA')
    rows.append({'image':ref(p),'decoded_pixel_sha256':hashlib.sha256(decoded.tobytes()).hexdigest()})
apng=run/'BATTLE_SCALE_FORWARD_CYCLE_1920x1080.png';frames=[]
for i,f in enumerate(ImageSequence.Iterator(Image.open(apng))):
    frames.append({'frame':i,'duration_ms':f.info.get('duration'),
                   'decoded_pixel_sha256':hashlib.sha256(f.convert('RGBA').tobytes()).hexdigest()})
temporal={'scope':'R1 failed temporal capture evidence only','status':'FAIL',
          'completion':ref(run/'COMPLETION.json'),'apng':ref(apng),'captures':rows,
          'unique_decoded_capture_count':len({r['decoded_pixel_sha256'] for r in rows}),
          'decoded_apng_frames':frames,'production_ready':False}
(OUT/'TEMPORAL_CAPTURE_R1_FAIL.json').write_text(json.dumps(temporal,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'alpha':[{'direction':r['direction'],'exact_alpha':r['alpha_matches_independent_scipy_four_connected_propagation'],
                           'exact_retained_rgb':r['retained_rgb_byte_exact']} for r in alpha_rows],
                  'unique_capture_pixels':temporal['unique_decoded_capture_count']}))
