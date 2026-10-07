# Round 5: bounded closure of the two R4 residual cases

Actual changes, not altered old receipts:
- Removed phase-difference pixel subsampling completely. Absolute mean and bad
  pixel fraction, as well as relative comparisons, visit EVERY differing pixel.
  Thresholds12 /48 /10% unchanged. The64px boundary ghost rejects,65px interlaced
  ghost rejects, normal65px motion passes. Added all three actual FFV1 cases.
- After complete quoted spans are consumed, remaining unmatched opening quote
  sections are excluded through end-of-line. They cannot expose a candidate path
  suffix to unquoted lookup. Added all three delimiter negative cases, retained
  real space-containing path and actual output boilerplate positive cases.

Actual local results after these changes:
- All Python96 tests passed in184.265s.
- Actual rifle source-cycle VP8:107 frames passed complete difference-region
  checks in8.138s. Art has not changed to make the validator pass.
- Godot authored-machine emitter + locked telegraph388 checks and actual projectile
  owner/ordinal339 checks passed. These are not visual quality approvals.

Please only retest your R4 sampling-boundary and unclosed-quote counterexamples
and their stated positive controls. The eight attached files are current-byte
sources, not a whole-project runtime package. If those cases are blocked, state
that limited result; do not imply unseen art, whole MVP or Luna reproduction PASS.
We continue the separately tracked asset production and R1 work locally.

## FILE: motion_lab_v1/cycle_review.py
SHA256: 3982de4d57cb3d370efa94a537a2c921c661059043e1e4268e93f1367ec42d8d

```text
"""Whole-cycle review gate. Pixel/landmark checks do not replace actual observation.

Templates are deliberately incomplete. No automatic art approval or provider calls.
"""
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path
import character_workflow as w
import gait_contract as contract

OBSERVATIONS = ('oppositeContacts', 'passingAndSwing', 'loopSeam', 'footSliding',
                'bodyContinuity', 'weaponContinuity')


def inputs(character, direction, action='walk'):
    from source_provenance import pixels
    c = w.recipe(character)
    if direction not in w.DIRECTIONS or action not in c['clips'] or action == 'idle':
        raise ValueError('Use an authored walk/run cycle and a valid direction')
    selected = dict(w.slots(c))
    names = [f'{direction}/{action}/{i}' for i in range(6)]
    files = [selected[name] for name in names]
    return {'character': character, 'direction': direction, 'action': action,
            'recipe': w.binding(w.ROOT / 'characters' / f'{character}.json'),
            'identity': w.binding(w.local(c['identityReference'])),
            'contractSHA256': contract.digest(),
            'compilerSHA256': w.sha(Path(__file__).with_name('build_atlas.py')),
            'previewCodeSHA256': w.sha(Path(__file__).with_name('cycle_preview.py')),
            'liveReviewCodeSHA256': w.sha(Path(__file__).with_name('cycle_live_review.js')),
            'recipeValues': {'speed':c['locomotion'][action+'Speed'], 'stride':c['locomotion'][action+'Stride'], 'heightMetres':c['heightMetres']},
            'provenanceCodeSHA256': w.sha(Path(__file__).with_name('source_provenance.py')),
            'reviewCodeSHA256': w.sha(Path(__file__)),
            'sources': [dict(slot=name, pixelSHA256=pixels(path), **w.binding(path)) for name, path in zip(names, files)]}


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def source_content(value):
    return {row['slot']:row.get('pixelSHA256',row['sha256']) for row in value['sources']}


def rejection_unresolved(row, expected):
    scope=row.get('rejectionScope','source-art')
    if scope=='source-art':
        old={r['slot']:r for r in row['inputs']['sources']}
        new={r['slot']:r for r in expected['sources']}
        # Historical unspecified failures remain conservative; changing one
        # unrelated frame is never an explicit resolution of a rejected frame.
        for slot in row.get('failedSlots',list(old)):
            if slot not in old or slot not in new:return True
            if old[slot]['sha256']==new[slot]['sha256']:return True
            if old[slot].get('pixelSHA256') and old[slot]['pixelSHA256']==new[slot].get('pixelSHA256'):return True
        return False
    changes=row.get('requiredChange',[])
    return not changes or any(not w.local(item['path']).is_file() or w.binding_valid(item) for item in changes)


def ledger(character):
    path = w.ROOT / 'qa' / character / 'cycle_reviews.json'
    return w.read(path) if path.exists() else []


def current(character, direction, action='walk'):
    try:
        expected = inputs(character, direction, action)
    except (OSError, ValueError):
        return {'direction': direction, 'action': action, 'state': 'missing_sources'}
    rows = [r for r in ledger(character) if r['direction'] == direction and r['action'] == action]
    latest = rows[-1] if rows else None
    state = 'needs_cycle_review'
    if latest and latest['decision'] == 'repair':
        state = 'repair' if rejection_unresolved(latest,expected) else 'needs_cycle_review'
    elif latest and latest.get('inputs') == expected:
        try:
            if not w.binding_valid(latest.get('packet')):
                raise ValueError('Changed cycle review packet')
            validate_packet(w.read(w.local(latest['packet']['path'])), expected)
            state = 'approved'
        except (OSError, ValueError, KeyError, TypeError):
            state = 'stale_cycle_review'
    return {'direction': direction, 'action': action, 'state': state,
            'inputSHA256': signature(expected)}


def status(character):
    c = w.recipe(character)
    if c.get('workflowVersion') != 1:
        return {'required': False, 'ready': True, 'cycles': []}
    rows = [current(character, d, a) for a in c['clips'] if a != 'idle' for d in w.DIRECTIONS]
    return {'required': True, 'ready': all(r['state'] == 'approved' for r in rows), 'cycles': rows}


def require_pilot(character, direction, action='walk'):
    c = w.recipe(character)
    if c.get('workflowVersion') != 1 or (direction == 'E' and action != 'run'):
        return
    pilot_sources=[r for r in w.source_status(character)['slots'] if r['slot'].startswith('E/walk/') or r['slot']=='E/idle/0']
    if current(character, 'E')['state'] != 'approved' or len(pilot_sources)!=7 or any(r['state']!='approved' for r in pilot_sources):
        raise ValueError('E full-cycle review required before expanding source art; run prepare-cycle --character ' + character + ' --direction E')


def require_build(character):
    if not w.source_status(character)['ready']:
        raise ValueError('Source approvals are incomplete')
    result = status(character)
    if not result['ready']:
        pending = next(r for r in result['cycles'] if r['state'] != 'approved')
        raise ValueError('Whole-cycle review required before active build: ' + pending['direction'] + '/' + pending['action'])
    return result


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


@lru_cache(maxsize=16)
def decoded_video(path, digest):
    """Cache only already hash-checked bytes, not caller-declared dimensions."""
    import cv2
    cap = cv2.VideoCapture(path)
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame.shape[:2] != (1080, 1920):
                raise ValueError('Cycle video is not native 1920x1080')
            frames += 1
        if not finite(fps) or fps <= 0 or frames == 0:
            raise ValueError('Cycle video must actually decode, not only have metadata')
        return frames, fps
    finally:
        cap.release()


def validate_landmarks(packet, clip, atlas):
    """Check observed anatomy labels against source pixels and opposite contacts."""
    import numpy as np
    frames = packet.get('frames', [])
    if len(frames) != 6 or [f.get('index') for f in frames] != list(range(6)):
        raise ValueError('Record all six chronological phases')
    markers = packet.get('legMarkers', {})
    if any(not isinstance(markers.get(side), str) or len(markers[side].strip()) < 8 for side in ('left', 'right')) or markers['left'] == markers['right']:
        raise ValueError('Identify each anatomical leg by actual costume/hip continuity')
    cw, ch = clip['cell']
    height = clip['height']
    theta = w.DIRECTIONS.index(packet['direction']) * math.pi / 4
    axis = [math.cos(theta), .5 * math.sin(theta)]
    norm = math.hypot(*axis)
    axis = [v / norm for v in axis]
    leads = []
    for i, row in enumerate(frames):
        phase = contract.PHASES[i]
        if row.get('phase') != phase['name'] or row.get('support') != phase['support']:
            raise ValueError('Observed support/phase differs from contract at frame ' + str(i))
        points = row.get('landmarks', {})
        for side in ('left', 'right'):
            for part in ('Hip', 'Knee', 'Sole'):
                point = points.get(side + part)
                if not isinstance(point, list) or len(point) != 2 or not all(finite(v) for v in point):
                    raise ValueError('Missing observed native-cell landmarks')
                x, y = point
                if not (0 <= x < cw and 0 <= y < ch):
                    raise ValueError('Landmark outside compiled cell')
                ox, oy = i % clip['columns'] * cw, i // clip['columns'] * ch
                region = atlas[oy + max(0, int(y)-5):oy + min(ch, int(y)+6),
                               ox + max(0, int(x)-5):ox + min(cw, int(x)+6), 3]
                if not np.any(region > 128):
                    raise ValueError('Landmark is not on visible subject pixels')
            hip, knee, sole = (points[side + p] for p in ('Hip', 'Knee', 'Sole'))
            if hip[1] >= knee[1] or knee[1] >= sole[1] or sole[1] - hip[1] < height * .18:
                raise ValueError('Trace the same connected leg from hip through knee to sole')
        left, right = points['leftSole'], points['rightSole']
        if math.dist(left, right) < height * .025:
            raise ValueError('Both leg labels point to the same foot')
        leads.append(sum((a-b)*d for a,b,d in zip(left, right, axis)))
    if leads[0] < height * .04 or leads[3] > -height * .04:
        raise ValueError('Opposite contacts do not exchange left/right leading feet')
    # Contact-only checks missed repeated swing/passing poses. Compare both
    # anatomical chains relative to their own hips, so a translated copy of the
    # same stance is not an opposite step. This cannot authenticate limb labels.
    for first,opposite in ((1,4),(2,5)):
        changes=[]
        for side in ('left','right'):
            a=frames[first]['landmarks'];b=frames[opposite]['landmarks']
            for part in ('Knee','Sole'):
                av=[a[side+part][i]-a[side+'Hip'][i] for i in (0,1)]
                bv=[b[side+part][i]-b[side+'Hip'][i] for i in (0,1)]
                changes.append(math.dist(av,bv))
        if sum(changes)/len(changes)<height*.025:
            raise ValueError('Opposite swing/passing poses repeat the same anatomical chains')
    return True


@lru_cache(maxsize=16)
def validate_video_pixels(video_path,video_sha,atlas_path,atlas_sha,clip_json,speed,stride):
    """Check actual decoded left-panel pixels against the chronological atlas.

    VP8 is lossy, so compare the composited source region with a small codec
    tolerance. Headers and ground-grid text are not accepted as image evidence.
    The inputs include hashes so changed bytes cannot reuse an earlier result.
    """
    import cv2
    import numpy as np
    from PIL import Image
    clip=json.loads(clip_json)
    cw,ch=clip['cell'];columns=clip['columns']
    if (cw,ch)!=(768,768) or columns!=3 or clip['frames']!=6:
        raise ValueError('Unexpected source-cycle preview layout')
    with Image.open(atlas_path) as image:
        atlas=np.array(image.convert('RGBA'))
    # Lossless WebP may canonicalize RGB under alpha=0. Compare every alpha
    # byte and every visible RGB byte, not undefined invisible color storage.
    atlas[atlas[:,:,3]==0,:3]=0
    expected=[]
    for i in range(6):
        rgba=atlas[i//columns*ch:(i//columns+1)*ch,i%columns*cw:(i%columns+1)*cw]
        if rgba.shape!=(ch,cw,4):raise ValueError('Incomplete chronological atlas')
        a=rgba[:,:,3:4].astype(float)/255
        expected.append((rgba[:,:,:3]*a+np.array([16,30,39])*(1-a)).astype(np.float32))
    discriminating={}
    root_y=int(clip.get('root',[384,716])[1])
    for i in range(6):
        for j in range(i):
            mask=np.max(np.abs(expected[i]-expected[j]),axis=2)>16
            mask[max(0,root_y-1):min(ch,root_y+3)]=False
            if int(mask.sum())<16:
                raise ValueError('Cycle video has insufficient distinguishable phase pixels; review capture, not automatic art approval')
            # Every differing native pixel is evidence. Subsampling lets an
            # interlaced ghost place correct pixels only on the sampled columns.
            offsets=np.flatnonzero(mask)
            discriminating[(i,j)]=np.unravel_index(offsets,(ch,cw))
    cap=cv2.VideoCapture(video_path)
    count=0
    try:
        fps=cap.get(cv2.CAP_PROP_FPS)
        if not finite(fps) or abs(fps-30)>0.01:raise ValueError('Cycle preview requires recorded 30 Hz chronology')
        starts=contract.starts(clip)
        while True:
            ok,frame=cap.read()
            if not ok:break
            index=contract.frame_at(count/fps*speed/stride,starts)
            pixels=cv2.cvtColor(frame[170:170+ch,30:30+cw],cv2.COLOR_BGR2RGB).astype(np.float32)
            if pixels.shape!=expected[index].shape:raise ValueError('Missing native source panel in cycle video')
            difference=np.abs(pixels-expected[index])
            # The compiler draws a ground baseline across these two rows.
            root_y=int(clip.get('root',[384,716])[1])
            difference[max(0,root_y-1):min(ch,root_y+3)]=0
            if float(difference.mean())>4.0 or float(np.quantile(difference,.99))>32.0:
                raise ValueError('Cycle video pixels do not show the expected authored phase at frame '+str(count))
            for alternative in range(6):
                if alternative==index:continue
                mask=discriminating[(max(index,alternative),min(index,alternative))]
                roi_error=np.abs(pixels[mask]-expected[index][mask])
                correct_error=float(roi_error.mean())
                other_error=float(np.abs(pixels[mask]-expected[alternative][mask]).mean())
                # Relative similarity is insufficient: a faint superposition
                # of all phases can be slightly closer to the intended one.
                # Fixed codec tolerances, never adjustable in review receipts.
                if correct_error>12.0 or float((roi_error.max(axis=1)>48.0).mean())>0.10:
                    raise ValueError('Cycle video pixels have excessive phase-region error at frame '+str(count))
                if other_error-correct_error<=1.0:
                    raise ValueError('Cycle video pixels do not distinguish the expected phase from another cell at frame '+str(count))
            count+=1
    finally:cap.release()
    if count==0:raise ValueError('Cycle video must actually decode')
    return count


def validate_packet(packet, expected):
    if packet.get('kind') != 'sable-cycle-observation' or packet.get('inputs') != expected:
        raise ValueError('Cycle review belongs to different sources, recipe or contract')
    if packet.get('character') != expected['character'] or packet.get('direction') != expected['direction'] or packet.get('action') != expected['action']:
        raise ValueError('Cycle identity mismatch')
    preview_binding = packet.get('preview')
    if not w.binding_valid(preview_binding):
        raise ValueError('Missing/stale complete-cycle preview')
    preview = w.read(w.local(preview_binding['path']))
    if preview.get('cycleInputs') != expected:
        raise ValueError('Preview does not match current source cycle')
    for key in ('video', 'atlas', 'contact'):
        if not w.binding_valid(preview.get(key)):
            raise ValueError('Changed cycle preview ' + key)
    if preview.get('nativeVideo') != [1920, 1080] or preview.get('cycles', 0) < 3:
        raise ValueError('Review three native 1080p cycles at recipe speed')
    if not finite(preview.get('durationSeconds')) or preview['durationSeconds'] < 2:
        raise ValueError('Missing cycle duration')
    frames, fps = decoded_video(str(w.local(preview['video']['path'])), preview['video']['sha256'])
    if abs(frames / fps - preview['durationSeconds']) > 1 / fps:
        raise ValueError('Cycle duration differs from decoded video')
    c = w.read(w.local(expected['recipe']['path']))
    action = expected['action']
    speed = c['locomotion'][action + 'Speed']
    stride = c['locomotion'][action + 'Stride']
    if not all(finite(v) and v > 0 for v in (speed, stride)) or frames / fps * speed / stride < 3 - 1e-6:
        raise ValueError('Decoded video does not span three cycles at recipe speed')
    validate_video_pixels(str(w.local(preview['video']['path'])),preview['video']['sha256'],
                          str(w.local(preview['atlas']['path'])),preview['atlas']['sha256'],
                          json.dumps(preview['clip'],sort_keys=True),speed,stride)
    validate_source_atlas(json.dumps(expected,sort_keys=True),json.dumps(preview['clip'],sort_keys=True),
                          str(w.local(preview['atlas']['path'])),preview['atlas']['sha256'])
    if not isinstance(packet.get('reviewer'), str) or not packet['reviewer'].strip():
        raise ValueError('Record the actual reviewer')
    if packet.get('decision') != 'approved':
        raise ValueError('Unreviewed or rejected cycle')
    if not isinstance(packet.get('observations'), dict):
        raise ValueError('Missing timed visual observations')
    for name in OBSERVATIONS:
        row = packet['observations'].get(name, {})
        times = row.get('seconds', [])
        if (row.get('decision') != 'pass' or not isinstance(row.get('notes'), str) or len(row['notes'].strip()) < 12 or
                not isinstance(times, list) or len(times) < 2 or
                not all(finite(t) and 0 <= t <= preview['durationSeconds'] for t in times) or
                any(b <= a for a,b in zip(times, times[1:]))):
            raise ValueError('Record actual timed observations: ' + name)
    from PIL import Image
    import numpy as np
    with Image.open(w.local(preview['atlas']['path'])) as im:
        if im.mode != 'RGBA':
            raise ValueError('Cycle atlas needs real alpha')
        validate_landmarks(packet, preview['clip'], np.array(im))
    return True


@lru_cache(maxsize=16)
def validate_source_atlas(expected_json, clip_json, atlas_path, atlas_sha):
    """Independently re-run source registration; never write an active atlas."""
    import numpy as np
    from PIL import Image
    from build_atlas import register
    expected=json.loads(expected_json); clip=json.loads(clip_json)
    c=w.read(w.local(expected['recipe']['path']))
    direction=expected['direction']; action=expected['action']
    annotations=c.get('annotations',{}).get(direction,{}).get(action,{})
    cell=c.get('cell',[768,768]); root=c.get('root',[384,716]); height=c.get('spriteHeight',656)
    if any(clip.get(key)!=value for key,value in [('cell',cell),('columns',3),('frames',6),('root',root),('height',height)]):
        raise ValueError('Cycle clip differs from source compiler contract')
    if clip.get('phaseStarts')!=contract.starts(c['clips'][action]):
        raise ValueError('Cycle phase schedule differs from recipe')
    with Image.open(atlas_path) as image:
        atlas=np.array(image.convert('RGBA'))
    atlas[atlas[:,:,3]==0,:3]=0
    for i,row in enumerate(expected['sources']):
        source=w.local(row['path'])
        if w.sha(source)!=row['sha256']: raise ValueError('Source changed during cycle check')
        fresh,note=register(source,c,direction,annotations.get(str(i),{}))
        fresh[fresh[:,:,3]==0,:3]=0
        x=i%3*cell[0]; y=i//3*cell[1]
        if not np.array_equal(atlas[y:y+cell[1],x:x+cell[0]],fresh):
            raise ValueError('Cycle atlas pixels do not compile from current source: '+row['slot'])
        if clip.get('muzzles',[None]*6)[i]!=note['muzzle'] or clip.get('sources',[None]*6)[i]!=note:
            raise ValueError('Cycle metadata does not compile from current source: '+row['slot'])
    return True


def record(character, direction, action, decision, packet_path=None, evidence=None, notes=None, reviewer=None,
           rejection_scope=None,failed_slots=None,required_change=None):
    if decision not in ('approved','repair'):raise ValueError('Use approved or repair')
    expected = inputs(character, direction, action)
    digest = signature(expected)
    previous = ledger(character)
    row = dict(character=character, direction=direction, action=action, inputs=expected,
               inputSHA256=digest, recordedAt=w.stamp(), decision=decision)
    if decision == 'approved':
        require_pilot(character, direction, action)
        source_rows=[r for r in w.source_status(character)['slots'] if r['slot'].startswith(f'{direction}/{action}/')]
        if len(source_rows)!=6 or any(r['state']!='approved' for r in source_rows):
            raise ValueError('Review the six current source frames before approving their cycle')
        unresolved=[r for r in previous if r['direction']==direction and r['action']==action and
                    r['decision']=='repair' and rejection_unresolved(r,expected)]
        if unresolved:
            raise ValueError('Rejected cycle source bytes are unchanged or required non-art repair is unresolved')
        packet = w.read(w.local(packet_path))
        validate_packet(packet, expected)
        row.update(packet=w.binding(w.local(packet_path)), reviewer=packet['reviewer'])
    else:
        if not notes or not reviewer or not evidence or not w.local(evidence).is_file():
            raise ValueError('Record real rejection observations and evidence')
        if rejection_scope not in ('source-art','timing','preview','annotation','runtime'):
            raise ValueError('Record an explicit rejection scope')
        row['rejectionScope']=rejection_scope
        if rejection_scope=='source-art':
            valid={r['slot'] for r in expected['sources']}
            if not failed_slots or not set(failed_slots)<=valid:raise ValueError('Name actual failed source slots')
            row['failedSlots']=list(dict.fromkeys(failed_slots))
        else:
            if not required_change:raise ValueError('Bind actual inputs/code/evidence requiring non-art repair')
            row['requiredChange']=[w.binding(w.local(path)) for path in required_change]
        row.update(notes=notes, reviewer=reviewer, evidence=w.binding(w.local(evidence)))
    previous.append(row)
    w.write(w.ROOT / 'qa' / character / 'cycle_reviews.json', previous)
    if decision != 'approved':
        w.invalidate_delivery(character, f'Cycle rejected: {direction}/{action}; {notes}')
    return row

```

## FILE: motion_lab_v1/source_provenance.py
SHA256: d6da53bb5321ad08008e52a0e371e7b712e9eb72c762baa545083f008fe5256d

```text
"""Recheck saved ImageGen/master/derivative relationships; not provider attestation.

All reads are project-local. A saved JSON can establish consistency, never prove
that a dishonest caller actually invoked a provider. Keep the real tool event.
"""
import hashlib
import json
import re
from pathlib import Path
from PIL import Image
import numpy as np


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def local(root, value):
    path = (root / value).resolve()
    if path == root or not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Missing project-local provenance input')
    return path


def bound(root, value):
    if not isinstance(value, dict): raise ValueError('Missing provenance binding')
    path = local(root, value['path'])
    if digest(path) != value['sha256']: raise ValueError('Stale provenance binding')
    return path


def pixels(path):
    with Image.open(path) as im:
        rgba = im.convert('RGBA')
        header = f'RGBA:{rgba.width}x{rgba.height}:'.encode()
        return hashlib.sha256(header + rgba.tobytes()).hexdigest()


def response_master(root, response_path):
    response_path = local(root, response_path)
    proof = json.loads(response_path.read_text(encoding='utf-8-sig'))
    result = proof.get('result')
    if proof.get('tool') != 'image_gen.imagegen' or not isinstance(result, dict) or not result:
        raise ValueError('Actual ImageGen metadata required')
    returned = proof.get('returnedPath')
    hint = result.get('output_hint')
    if not isinstance(returned,str) or not Path(returned).is_absolute() or not isinstance(hint,str):
        raise ValueError('Actual returned path missing')
    normalized = hint.replace('\\','/')
    candidate = returned.replace('\\','/')
    # Quoted paths are indivisible: whitespace inside quotes is a filename
    # character, not permission to accept a shorter prefix. Remove their spans
    # before considering the explicitly supported unquoted tool sentences.
    quoted=list(re.finditer(r'''(["'`])([^\r\n]*?)\1''',normalized))
    exact_quoted=any(m.group(2)==candidate for m in quoted)
    unquoted=re.sub(r'''(["'`])([^\r\n]*?)\1''',' ',normalized)
    # A truncated quoted filename remains quoted through the end of its line;
    # never reinterpret a space-separated suffix as an independent path.
    unquoted=re.sub(r'''["'`][^\r\n]*''',' ',unquoted)
    def exact_unquoted(line):
        for match in re.finditer(re.escape(candidate),line):
            before=line[:match.start()];after=line[match.end():].strip()
            if (not before or before[-1].isspace()) and after in ('','.', 'by default.'):
                return True
        return False
    if not exact_quoted and not any(exact_unquoted(line) for line in unquoted.splitlines()):
        raise ValueError('Returned path differs from actual output metadata')
    if not isinstance(proof.get('projectCopy'),str):
        raise ValueError('Missing exact project copy')
    master = local(root, proof['projectCopy'])
    if digest(master) != proof.get('projectCopySHA256'):
        raise ValueError('Returned master bytes changed (hash mismatch)')
    with Image.open(master) as image:
        image.verify()
    return master


def validate_slot(root, target, receipt):
    """No missing derivation fields may downgrade an edited image to an original."""
    if receipt.get('generator') != 'Codex built-in ImageGen' or digest(target) != receipt.get('sha256'):
        raise ValueError('Slot content or generator mismatch')
    if local(root,receipt['destination']) != target:
        raise ValueError('Receipt names a different slot')
    proof_path = bound(root,receipt.get('toolResponse'))
    original = response_master(root,proof_path)
    master = bound(root,receipt.get('sourceMaster'))
    if digest(master) != digest(original):
        raise ValueError('Preserved source master differs from returned project copy')
    derivation = receipt.get('derivation')
    if derivation is None:
        if digest(target) != digest(master):
            raise ValueError('Changed source needs its explicit derivation')
        return True
    if not isinstance(derivation,dict) or derivation.get('resampling') is not False or derivation.get('anatomicalWarp') is not False:
        raise ValueError('Unsupported source-art derivation')
    kind = derivation.get('kind')
    if kind == 'edge-connected green matte normalization only; no source-art redraw':
        from intake_derived_frame import _verify_derivative
        _verify_derivative(target,master,proof_path,bound(root,derivation.get('normalization')),bound(root,derivation.get('mask')))
    elif kind == 'chroma-key and connected-subject crop only':
        from build_atlas import subjects
        with Image.open(target) as image:
            actual = np.asarray(image.convert('RGBA'))
        matching = [im for im,box in subjects(master,2) if list(box) == derivation.get('box')]
        if len(matching) != 1 or not np.array_equal(actual,np.asarray(matching[0].convert('RGBA'))):
            raise ValueError('Pair crop pixels do not derive from the preserved master')
    else:
        raise ValueError('Unknown source-art derivation')
    return True

```

## FILE: motion_lab_v1/tests/test_cycle_review.py
SHA256: 94c3f9bfd6410726560e65140ce486dad3c9bb3406f8f507581571b4108f244b

```text
"""Synthetic review fixtures only. They are never production art approvals."""
import copy
import json
import sys
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import character_workflow as w
import cycle_review as cycle
import gait_contract as contract
import intake_frame
import build_atlas
PALETTE=[(90,120,130),(170,90,110),(100,160,190),(170,140,70),(80,100,190),(180,80,180)]


class CycleGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import cv2
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        cls.video_fixture=Path(tempfile.mkdtemp(prefix='cycle_video_',dir=base))/'synthetic_1080p.mp4'
        encoded=[]
        for i,color in enumerate(PALETTE):
            source=cls.video_fixture.with_name(f'phase_{i}.png');Image.new('RGB',(64,96),color).save(source)
            frame,_=build_atlas.register(source,{},'E',{})
            panel=Image.new('RGB',(1920,1080),(16,30,39))
            panel.paste(Image.fromarray(frame),(30,170),Image.fromarray(frame[:,:,3]))
            encoded.append(cv2.cvtColor(np.array(panel),cv2.COLOR_RGB2BGR))
        writer=cv2.VideoWriter(str(cls.video_fixture),cv2.VideoWriter_fourcc(*'mp4v'),30,(1920,1080))
        if not writer.isOpened():raise RuntimeError('Local cycle video encoder unavailable')
        try:
            for i in range(108):
                writer.write(encoded[contract.frame_at(i/30*1.35/1.6,contract.starts({}))])
        finally:writer.release()

    def setUp(self):
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='cycle_',dir=base))
        for module in (w,intake_frame,build_atlas):
            p=patch.object(module,'ROOT',self.root);p.start();self.addCleanup(p.stop)
        reference=self.root/'art/fixture/identity.png';reference.parent.mkdir(parents=True);reference.write_bytes(b'identity fixture')
        c={'id':'fixture','name':'Fixture','source':'art/fixture','workflowVersion':1,
           'identityReference':'art/fixture/identity.png','referenceSHA256':w.sha(reference),
           'heightMetres':1.72,'clips':{'walk':{'frames':6},'idle':{'frames':1}},'locomotion':{'walkSpeed':1.35,'walkStride':1.6}}
        w.write(self.root/'characters/fixture.json',c)
        reviews=[]
        for i,(slot,path) in enumerate(w.slots(c)):
            info=PngInfo();info.add_text('technical_slot',slot)
            Image.new('RGB',(64,96),PALETTE[int(slot.split('/')[-1])]).save(path,pnginfo=info)
            master=path.with_name(f'original_fixture_{i}.png');master.write_bytes(path.read_bytes())
            returned=str(self.root/f'fake_returned_{i}.png')
            proof=self.root/f'qa/tool-fixture-{i}.json';w.write(proof,{'tool':'image_gen.imagegen','returnedPath':returned,'result':{'output_hint':'Synthetic test; not a real invocation: '+returned},'projectCopy':str(master.relative_to(self.root)),'projectCopySHA256':w.sha(master)})
            receipt=path.with_suffix('.source.json')
            w.write(receipt,{'generator':'Codex built-in ImageGen','sha256':w.sha(path),'destination':str(path.relative_to(self.root)),'toolResponse':w.binding(proof),'sourceMaster':w.binding(master)})
            reviews.append({'slot':slot,'decision':'approved','sourceSHA256':w.sha(path),'sourceReceiptSHA256':w.sha(receipt),'referenceSHA256':c['referenceSHA256'],'evidence':w.binding(path)})
        w.write(self.root/'qa/fixture/source_reviews.json',reviews)
        self.expected=cycle.inputs('fixture','E')
        self.out=self.root/'qa/cycle';self.out.mkdir(parents=True)
        self.clip={'cell':[768,768],'height':656,'columns':3,'frames':6,'root':[384,716],'phaseStarts':contract.starts(c['clips']['walk']),'muzzles':[],'sources':[]}
        atlas=Image.new('RGBA',(2304,1536))
        for i,row in enumerate(self.expected['sources']):
            pixels,note=build_atlas.register(w.local(row['path']),c,'E',{})
            atlas.paste(Image.fromarray(pixels),(i%3*768,i//3*768))
            self.clip['muzzles'].append(note['muzzle']);self.clip['sources'].append(note)
        atlas_path=self.out/'atlas.png';atlas.save(atlas_path)
        contact=self.out/'contact.png';Image.new('RGB',(2304,1536)).save(contact)
        movie=self.out/'video.mp4';shutil.copy2(self.video_fixture,movie)
        self.preview=self.out/'preview.json'
        w.write(self.preview,{'cycleInputs':self.expected,'clip':self.clip,'atlas':w.binding(atlas_path),
                'contact':w.binding(contact),'video':w.binding(movie),'nativeVideo':[1920,1080],
                'cycles':3,'durationSeconds':3.6})
        soles=[([500,716],[220,690]),([390,716],[290,640]),([290,716],[450,650]),
               ([220,690],[500,716]),([290,640],[390,716]),([450,650],[290,716])]
        frames=[]
        for p,(left,right) in zip(contract.PHASES,soles):
            pts={}
            for side,sole,hx in [('left',left,375),('right',right,405)]:
                pts[side+'Hip']=[hx,360];pts[side+'Knee']=[(hx+sole[0])/2,(360+sole[1])/2];pts[side+'Sole']=sole
            frames.append({'index':p['index'],'phase':p['name'],'support':p['support'],'landmarks':pts})
        self.packet={'kind':'sable-cycle-observation','character':'fixture','direction':'E','action':'walk',
                     'inputs':self.expected,'preview':w.binding(self.preview),'decision':'approved','reviewer':'UNIT FIXTURE NOT ART REVIEW',
                     'legMarkers':{'left':'left technical marker','right':'right technical marker'},'frames':frames,
                     'observations':{name:{'decision':'pass','seconds':[.1,1.1], 'notes':'Synthetic geometry unit test only'} for name in cycle.OBSERVATIONS}}
        self.packet_path=self.out/'observations.json';w.write(self.packet_path,self.packet)

    def test_explicit_complete_technical_packet_is_accepted(self):
        self.assertTrue(cycle.validate_packet(self.packet,self.expected))

    def test_same_leading_leg_at_opposite_contact_is_rejected(self):
        p=copy.deepcopy(self.packet);p['frames'][3]['landmarks']=copy.deepcopy(p['frames'][0]['landmarks'])
        with self.assertRaisesRegex(ValueError,'Opposite contacts'):cycle.validate_packet(p,self.expected)

    def test_repeated_swing_and_passing_chain_is_rejected(self):
        for a,b in ((1,4),(2,5)):
            p=copy.deepcopy(self.packet)
            p['frames'][b]['landmarks']=copy.deepcopy(p['frames'][a]['landmarks'])
            with self.assertRaisesRegex(ValueError,'swing/passing'):
                cycle.validate_packet(p,self.expected)

    def test_rebound_video_hash_does_not_prove_the_correct_atlas_pixels(self):
        path=self.out/'atlas.png'
        Image.new('RGBA',(2304,1536),(220,30,80,255)).save(path)
        preview=w.read(self.preview);preview['atlas']=w.binding(path);w.write(self.preview,preview)
        self.packet['preview']=w.binding(self.preview)
        with self.assertRaisesRegex(ValueError,'video.*pixels'):
            cycle.validate_packet(self.packet,self.expected)

    def test_declared_video_dimensions_cannot_hide_undecodable_bytes(self):
        movie=self.out/'video.mp4';movie.write_bytes(b'not an actual video')
        preview=w.read(self.preview);preview['video']=w.binding(movie);w.write(self.preview,preview)
        self.packet['preview']=w.binding(self.preview)
        with self.assertRaisesRegex(ValueError,'actually decode'):cycle.validate_packet(self.packet,self.expected)

    def test_blank_approvals_wrong_phase_and_missing_video_binding_fail(self):
        for mutate in [lambda p:p.update(decision='unreviewed'),lambda p:p['frames'][1].update(phase='right_passing'),
                       lambda p:p['frames'][3].update(support='left'),lambda p:p['frames'][0]['landmarks'].update(leftSole=None),
                       lambda p:p['observations']['footSliding'].update(seconds=[]),lambda p:p['observations']['loopSeam'].update(notes=''),
                       lambda p:p.update(preview={'path':'missing.json','sha256':'0'*64})]:
            p=copy.deepcopy(self.packet);mutate(p)
            with self.assertRaises(ValueError):cycle.validate_packet(p,self.expected)

    def test_background_landmarks_are_rejected(self):
        atlas=np.zeros((1536,2304,4),dtype=np.uint8)
        with self.assertRaisesRegex(ValueError,'visible subject'):cycle.validate_landmarks(self.packet,self.clip,atlas)

    def test_changed_source_recipe_and_review_packet_invalidate_gate(self):
        cycle.record('fixture','E','walk','approved',str(self.packet_path))
        self.assertEqual(cycle.current('fixture','E')['state'],'approved')
        p=copy.deepcopy(self.packet);p['observations']['footSliding']['notes']='edited after approval'
        w.write(self.packet_path,p)
        self.assertNotEqual(cycle.current('fixture','E')['state'],'approved')
        w.write(self.packet_path,self.packet)
        Image.new('RGB',(64,96),(30,50,90)).save(self.root/'art/fixture/E_walk_3_master.png')
        self.assertNotEqual(cycle.current('fixture','E')['state'],'approved')

    def test_rejected_pixels_cannot_be_reapproved_by_notes(self):
        cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Actual fixture rejection',reviewer='unit fixture',rejection_scope='source-art',failed_slots=['E/walk/3'])
        with self.assertRaisesRegex(ValueError,'source bytes are unchanged'):
            cycle.record('fixture','E','walk','approved',str(self.packet_path))
        self.assertEqual(w.read(self.root/'dist/fixture.delivery.json')['status'],'HOLD_VISUAL_REPAIR')

    def test_renaming_rejected_sources_does_not_clear_rejection(self):
        cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Synthetic rejection fixture',reviewer='unit fixture',rejection_scope='source-art',failed_slots=['E/walk/3'])
        for i in range(6):
            path=self.root/f'art/fixture/E_walk_{i}_master.png'
            shutil.copy2(path,path.with_name(f'E_walk_{i}_override.png'))
        self.assertEqual(cycle.current('fixture','E')['state'],'repair')

    def test_other_slot_or_metadata_cannot_resolve_failed_slot(self):
        row=cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Synthetic E4 failed',reviewer='unit fixture',rejection_scope='source-art',failed_slots=['E/walk/4'])
        Image.new('RGB',(64,96),(70,80,90)).save(self.root/'art/fixture/E_walk_0_master.png')
        self.assertTrue(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))
        path=self.root/'art/fixture/E_walk_4_master.png'
        info=PngInfo();info.add_text('new_note','same rejected pixels')
        Image.new('RGB',(64,96),PALETTE[4]).save(path,pnginfo=info)
        self.assertTrue(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))

    def test_preview_repair_does_not_force_source_replacement(self):
        path=self.out/'preview-settings.json';w.write(path,{'testFixture':'old'})
        row=cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Synthetic preview fault',reviewer='unit fixture',rejection_scope='preview',required_change=[str(path)])
        before=cycle.source_content(cycle.inputs('fixture','E'))
        self.assertTrue(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))
        w.write(path,{'testFixture':'fixed'})
        self.assertFalse(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))
        self.assertEqual(before,cycle.source_content(cycle.inputs('fixture','E')))

    def test_rebound_source_metadata_cannot_use_old_atlas(self):
        path=self.root/'art/fixture/E_walk_0_master.png'
        Image.new('RGB',(64,96),(200,80,90)).save(path)
        expected=cycle.inputs('fixture','E')
        with self.assertRaisesRegex(ValueError,'atlas pixels'):
            cycle.validate_source_atlas(json.dumps(expected,sort_keys=True),json.dumps(self.clip,sort_keys=True),str(self.out/'atlas.png'),w.sha(self.out/'atlas.png'))

    def test_preview_timing_cannot_override_recipe(self):
        config=w.recipe('fixture');config['clips']['walk']['phaseStarts']=[0,.2,.33,.5,.7,.83]
        w.write(self.root/'characters/fixture.json',config)
        with self.assertRaisesRegex(ValueError,'phase schedule'):
            cycle.validate_source_atlas(json.dumps(cycle.inputs('fixture','E'),sort_keys=True),json.dumps(self.clip,sort_keys=True),str(self.out/'atlas.png'),w.sha(self.out/'atlas.png'))

    def test_frozen_panel_with_small_distinct_cells_is_rejected(self):
        import cv2
        atlas=Image.new('RGBA',(2304,1536));frames=[]
        for i in range(6):
            cell=np.full((768,768,4),(70,90,100,255),dtype=np.uint8)
            cell[300:332,100+i*70:132+i*70,:3]=255
            frames.append(cell);atlas.paste(Image.fromarray(cell),(i%3*768,i//3*768))
        path=self.out/'small_changes.png';atlas.save(path)
        movie=self.out/'frozen.mkv'
        writer=cv2.VideoWriter(str(movie),cv2.VideoWriter_fourcc(*'FFV1'),30,(1920,1080))
        self.assertTrue(writer.isOpened())
        page=np.full((1080,1920,3),(16,30,39),np.uint8);page[170:938,30:798]=frames[0][:,:,:3]
        encoded=cv2.cvtColor(page,cv2.COLOR_RGB2BGR)
        try:
            for _ in range(108):writer.write(encoded)
        finally:writer.release()
        with self.assertRaisesRegex(ValueError,'distinguish|phase-region'):
            cycle.validate_video_pixels(str(movie),w.sha(movie),str(path),w.sha(path),json.dumps(self.clip,sort_keys=True),1.35,1.6)

    def test_superposed_phase_ghosts_cannot_pass_as_authored_frames(self):
        import cv2
        atlas=Image.new('RGBA',(2304,1536));frames=[]
        for i in range(6):
            cell=np.full((768,768,4),(70,90,100,255),dtype=np.uint8)
            cell[300:332,100+i*70:132+i*70,:3]=255
            frames.append(cell[:,:,:3]);atlas.paste(Image.fromarray(cell),(i%3*768,i//3*768))
        path=self.out/'phase_ghost_atlas.png';atlas.save(path)
        base=np.rint(np.mean(frames,axis=0)).astype(np.uint8)
        for ghost in (False,True):
            movie=self.out/('ghosts.mkv' if ghost else 'correct_small_motion.mkv')
            writer=cv2.VideoWriter(str(movie),cv2.VideoWriter_fourcc(*'FFV1'),30,(1920,1080))
            self.assertTrue(writer.isOpened())
            try:
                for tick in range(108):
                    index=contract.frame_at(tick/30*1.35/1.6,contract.starts(self.clip))
                    cell=base.copy() if ghost else frames[index]
                    if ghost:cell[300:332,100+index*70:132+index*70]+=4
                    page=np.full((1080,1920,3),(16,30,39),np.uint8);page[170:938,30:798]=cell
                    writer.write(cv2.cvtColor(page,cv2.COLOR_RGB2BGR))
            finally:writer.release()
            args=(str(movie),w.sha(movie),str(path),w.sha(path),json.dumps(self.clip,sort_keys=True),1.35,1.6)
            if ghost:
                with self.assertRaisesRegex(ValueError,'phase-region'):cycle.validate_video_pixels(*args)
            else:self.assertEqual(cycle.validate_video_pixels(*args),108)

    def test_missing_pilot_blocks_non_e_intake_before_any_source_copy(self):
        source=self.root/'qa/not-read.png';source.write_bytes(b'invalid image proves guard runs first')
        before=(self.root/'art/fixture/SE_walk_0_master.png').read_bytes()
        with self.assertRaisesRegex(ValueError,'E full-cycle review'):
            intake_frame.intake('fixture','SE','walk',0,source)
        self.assertEqual((self.root/'art/fixture/SE_walk_0_master.png').read_bytes(),before)

    def test_interlaced_ghost_is_rejected_on_both_sides_of_old_sampling_limit(self):
        import cv2
        for height in [64,65]:
            atlas=Image.new('RGBA',(2304,1536));frames=[]
            for i in range(6):
                cell=np.full((768,768,4),(70,90,100,255),dtype=np.uint8)
                cell[300:300+height,100+i*70:132+i*70,:3]=255
                frames.append(cell[:,:,:3]);atlas.paste(Image.fromarray(cell),(i%3*768,i//3*768))
            path=self.out/f'interlaced_{height}.png';atlas.save(path)
            base=np.rint(np.mean(frames,axis=0)).astype(np.uint8)
            for ghost in ([True] if height==64 else [False,True]):
                movie=self.out/f'interlaced_{height}_{ghost}.mkv'
                writer=cv2.VideoWriter(str(movie),cv2.VideoWriter_fourcc(*'FFV1'),30,(1920,1080))
                self.assertTrue(writer.isOpened())
                try:
                    for tick in range(108):
                        index=contract.frame_at(tick/30*1.35/1.6,contract.starts(self.clip))
                        cell=base.copy() if ghost else frames[index]
                        if ghost:
                            cell[300:300+height,100+index*70:132+index*70]+=4
                            cell[:,::2]=frames[index][:,::2]
                        page=np.full((1080,1920,3),(16,30,39),np.uint8);page[170:938,30:798]=cell
                        writer.write(cv2.cvtColor(page,cv2.COLOR_RGB2BGR))
                finally:writer.release()
                args=(str(movie),w.sha(movie),str(path),w.sha(path),json.dumps(self.clip,sort_keys=True),1.35,1.6)
                if ghost:
                    with self.assertRaisesRegex(ValueError,'phase-region'):cycle.validate_video_pixels(*args)
                else:self.assertEqual(cycle.validate_video_pixels(*args),108)


if __name__=='__main__':unittest.main()

```

## FILE: motion_lab_v1/tests/test_enemy_asset_provenance.py
SHA256: a3b5b1ffda17c43134af837f3c4b2a1e971d1d300f2661d7cce11e94a7aab021

```text
"""Tiny local diagnostic inputs, not generated art or visual approvals."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

LAB=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LAB))
import prepare_enemy_asset as prep

class EnemyProvenanceTests(unittest.TestCase):
    def setUp(self):
        folder=LAB/'qa/technical_tests';folder.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='enemy_proof_',dir=folder))
        p=patch.object(prep,'ROOT',self.root);p.start();self.addCleanup(p.stop)
        self.source=self.root/'master.png';Image.new('RGBA',(16,24),(60,80,100,255)).save(self.source)
        self.response=self.root/'response.json'
        self.returned=str(self.root/'managed-original.png')
        self.proof={'tool':'image_gen.imagegen','returnedPath':self.returned,
                    'result':{'output_hint':'Generated image saved to '+self.returned},
                    'projectCopy':'master.png','projectCopySHA256':prep.sha(self.source)}
    def check(self):
        self.response.write_text(json.dumps(self.proof),encoding='utf-8')
        return prep.verify_source(self.source,self.response)
    def test_exact_retained_copy_survives_absent_managed_staging(self):
        self.check()
    def test_metadata_name_alone_does_not_prove_art(self):
        del self.proof['projectCopy']
        with self.assertRaisesRegex(ValueError,'exact project copy'):self.check()
    def test_source_tamper_rejected(self):
        self.source.write_bytes(b'changed fixture')
        with self.assertRaisesRegex(ValueError,'hash'):self.check()
    def test_other_tool_file_cannot_substitute(self):
        self.proof['result']['output_hint']='Saved another file.png'
        with self.assertRaisesRegex(ValueError,'metadata'):self.check()
    def test_returned_path_requires_exact_output_path(self):
        self.proof['result']['output_hint']=self.returned+'.other.png'
        with self.assertRaisesRegex(ValueError,'metadata'):self.check()
    def test_identifier_cannot_escape_qa(self):
        with self.assertRaisesRegex(ValueError,'asset id'):
            prep.prepare('../../runtime',self.source,self.response)

    def test_quoted_longer_path_is_not_the_returned_file(self):
        for quote in ['\"',"'",'`']:
            for suffix in [' other.png','. other.png']:
                self.proof['result']['output_hint']=f'Saved to {quote}{self.returned}{suffix}{quote}'
                with self.assertRaisesRegex(ValueError,'metadata'):self.check()

    def test_exact_path_with_spaces_remains_supported(self):
        self.proof['returnedPath']=str(self.root/'actual image with spaces.png')
        for hint in [f'Saved to "{self.proof["returnedPath"]}"',
                     f'Generated images are saved to {self.root} as {self.proof["returnedPath"]} by default.\nNext instruction.']:
            self.proof['result']['output_hint']=hint;self.check()

    def test_unclosed_quote_cannot_expose_a_path_suffix(self):
        for quote in ['"',"'",'`']:
            self.proof['result']['output_hint']=f'Saved to {quote}/staging/other {self.returned}'
            with self.assertRaisesRegex(ValueError,'metadata'):self.check()

    def test_matte_code_change_preserves_previous_preparation(self):
        # Real prepare() and real deterministic key_image, synthetic art only.
        Image.new('RGBA',(1024,1024),(60,80,100,254)).save(self.source)
        self.proof['projectCopySHA256']=prep.sha(self.source);self.check()
        matte=self.root/'build_atlas.py';matte.write_text('technical dependency version 1')
        (self.root/'source_provenance.py').write_text('technical dependency fingerprint')
        prep.prepare('fixture',self.source,self.response)
        first=next((self.root/'qa/stage1_enemies_20260913/fixture').glob('*/preparation.json'))
        first_hash=prep.sha(first)
        matte.write_text('technical dependency version 2')
        prep.prepare('fixture',self.source,self.response)
        reports=list((self.root/'qa/stage1_enemies_20260913/fixture').glob('*/preparation.json'))
        self.assertEqual(len(reports),2);self.assertEqual(prep.sha(first),first_hash)

```

## FILE: motion_lab_v1/character_workflow.py
SHA256: c80e556d0e2119eb8d42ee6c5d0678229dfa5cc1fb96f3115455d475d9cb10af

```text
"""Small, local-only handoff workflow for the implemented Motion Studio route.

It inventories exact source slots, binds human/model visual observations to
their files, runs the real tests, and refuses stale or incomplete delivery.
It never calls an image API, fabricates reviews, or publishes a deployment.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parent
DIRECTIONS=['E','SE','S','SW','W','NW','N','NE']
PILOT=['E/idle/0','E/walk/0','E/walk/3','E/walk/1','E/walk/4','E/walk/2','E/walk/5']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def ident(value):
    if not re.fullmatch(r'[a-z0-9_-]+',value):raise ValueError('Use an ASCII character id, not a path')
    return value
def local(value):
    path=(ROOT/value).resolve()
    if path==ROOT or not path.is_relative_to(ROOT):raise ValueError('Path must stay below motion_lab_v1')
    return path
def recipe(character):
    c=read(ROOT/'characters'/f'{ident(character)}.json')
    if c['id']!=character or local(c['source'])!=ROOT/'art'/character:raise ValueError('Recipe identity/source mismatch')
    if not {'walk','idle'}<=set(c['clips']) or set(c['clips'])-{'walk','idle','run'}:raise ValueError('Use explicit walk/idle and optional authored run clips')
    for clip in c['clips'].values():
        if type(clip.get('frames')) is not int or not 1<=clip['frames']<=24:raise ValueError('Invalid authored frame count')
        starts=clip.get('phaseStarts')
        if starts is not None and (not isinstance(starts,list) or len(starts)!=clip['frames'] or starts[0]!=0 or any(not isinstance(value,(int,float)) or isinstance(value,bool) or not 0<=value<1 for value in starts) or any(current<=previous for previous,current in zip(starts,starts[1:]))):raise ValueError('phaseStarts must begin at 0 and contain one increasing phase start per frame')
    if any(c['clips'][action]['frames']!=(1 if action=='idle' else 6) for action in c['clips']):raise ValueError('This six-phase workflow requires 6 walk/run frames and 1 idle frame per direction')
    return c
def slots(c):
    for direction in DIRECTIONS:
        for action,spec in c['clips'].items():
            for frame in range(spec['frames']):
                base=local(c['source'])/f'{direction}_{action}_{frame}'
                override=base.with_name(base.name+'_override.png')
                yield f'{direction}/{action}/{frame}',override if override.exists() else base.with_name(base.name+'_master.png')
def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
def binding_valid(value):
    try:return sha(local(value['path']))==value['sha256']
    except (KeyError,ValueError,OSError,TypeError):return False

def invalidate_delivery(character,reason):
    """Keep prior evidence, but do not leave a rejected delivery as current."""
    path=ROOT/'dist'/f'{ident(character)}.delivery.json'
    if path.exists():
        previous=ROOT/'qa'/character/'delivery_history'/f'{sha(path)}.json'
        previous.parent.mkdir(parents=True,exist_ok=True)
        if not previous.exists():shutil.copy2(path,previous)
    package=ROOT/'dist'/f'{character}.package.json'
    write(path,{'recordedAt':stamp(),'character':character,'status':'HOLD_VISUAL_REPAIR','reason':reason,'package':binding(package) if package.exists() else None,'reviewedDelivery':False})

def source_status(character):
    c=recipe(character)
    if c.get('workflowVersion')!=1:
        return {'character':character,'ready':False,'mode':'existing-runtime','next':'Use verify-runtime for the accepted existing package. Start an explicit source migration before new art; do not invent historical source reviews.','slots':[],'errors':['Existing paired-source package has no new-workflow review ledger']}
    reference=local(c['identityReference']);errors=[]
    if not reference.exists() or sha(reference)!=c['referenceSHA256']:errors.append('Identity reference missing or changed')
    ledger=ROOT/'qa'/character/'source_reviews.json'
    reviews=read(ledger) if ledger.exists() else []
    rows=[];seen={}
    for name,path in slots(c):
        row={'slot':name,'path':path.relative_to(ROOT).as_posix(),'state':'missing'}
        if path.exists():
            digest=sha(path);row.update(sha256=digest,state='needs_review')
            receipt=path.with_suffix('.source.json')
            if not receipt.exists():row['state']='missing_provenance'
            else:
                r=read(receipt)
                try:
                    from source_provenance import validate_slot
                    validate_slot(ROOT,path,r)
                except (ValueError,KeyError,TypeError,OSError) as error:
                    row['state']='stale_provenance';row['provenanceError']=str(error)
            if digest in seen:row['state']='duplicate_source';errors.append(f'{name}: same source as {seen[digest]}')
            seen[digest]=name
            current=[r for r in reviews if r['slot']==name]
            if row['state']=='needs_review' and current:
                review=current[-1]
                if review.get('sourceSHA256')==digest and review.get('sourceReceiptSHA256')==sha(receipt) and review.get('referenceSHA256')==c['referenceSHA256'] and binding_valid(review.get('evidence')):
                    row['state']='approved' if review['decision']=='approved' else 'repair'
        rows.append(row)
    pending=[r for r in rows if r['state']!='approved']
    pilots=[r for slot in PILOT for r in pending if r['slot']==slot]
    repairs=[r for r in pending if r['state']=='repair']
    next_row=(repairs or pilots or pending or [None])[0]
    return {'character':character,'mode':'source-authoring','ready':not errors and not pending,'requiredFrames':len(rows),'approvedFrames':len(rows)-len(pending),'next':next_row or 'build','errors':errors,'slots':rows}

def review_source(character,slot,decision,evidence,notes,reviewer):
    if decision not in ('approved','repair'):raise ValueError('Use approved or repair')
    c=recipe(character);path=dict(slots(c)).get(slot)
    if path is None or not path.exists():raise ValueError('Cannot review a missing source slot')
    if decision=='approved':
        from cycle_review import require_pilot
        direction,action,_=slot.split('/')
        require_pilot(character,direction,action)
    if not notes.strip() or not reviewer.strip():raise ValueError('Record the actual observation and reviewer')
    proof=local(evidence)
    if not proof.is_file():raise ValueError('Review evidence is missing')
    ledger=ROOT/'qa'/character/'source_reviews.json';reviews=read(ledger) if ledger.exists() else []
    if decision=='approved':
        from source_provenance import pixels
        pixel_hash=pixels(path)
        if any(r.get('decision')=='repair' and (r.get('sourceSHA256')==sha(path) or r.get('sourcePixelSHA256')==pixel_hash) for r in reviews):
            raise ValueError('Rejected source bytes are unchanged; notes cannot repair source art')
        state=next(r['state'] for r in source_status(character)['slots'] if r['slot']==slot)
        if state not in ('needs_review','approved'):
            raise ValueError('Source provenance/readiness must pass before approval: '+state)
    from source_provenance import pixels
    row={'recordedAt':stamp(),'slot':slot,'decision':decision,'reviewer':reviewer,'notes':notes,'sourceSHA256':sha(path),'sourcePixelSHA256':pixels(path),'sourceReceiptSHA256':sha(path.with_suffix('.source.json')) if path.with_suffix('.source.json').exists() else None,'referenceSHA256':c['referenceSHA256'],'evidence':binding(proof)}
    reviews.append(row);write(ledger,reviews)
    if decision=='repair':
        quarantine=ROOT/'qa'/character/'quarantine'/sha(path);quarantine.mkdir(parents=True,exist_ok=True)
        for src in [path,path.with_suffix('.source.json'),proof]:
            if src.exists() and not (quarantine/src.name).exists():shutil.copy2(src,quarantine/src.name)
        write(quarantine/'review.json',row)
        invalidate_delivery(character,'Source rejected: '+slot+'; '+notes)
    return row

def workflow_status(character):
    """Source completeness is not cycle readiness or a runtime approval."""
    source=source_status(character)
    if source['mode']=='existing-runtime':return source
    from cycle_review import status as cycle_status
    cycles=cycle_status(character)
    runtime_path=ROOT/'qa'/character/'runtime_reviews.json'
    runtime=read(runtime_path)[-1] if runtime_path.exists() and read(runtime_path) else None
    rejected=runtime is not None and runtime.get('decision')=='repair'
    result=dict(source,sourcesReady=source['ready'],cycleStatus=cycles,runtimeRepairRequired=rejected,
                ready=source['ready'] and cycles['ready'] and not rejected,
                activeBuildReady=source['ready'] and cycles['ready'])
    pilot=next(r for r in cycles['cycles'] if r['direction']=='E' and r['action']=='walk')
    pilot_sources=[r for r in source['slots'] if r['slot'] in PILOT]
    pilot_sources_ready=len(pilot_sources)==len(PILOT) and all(r['state']=='approved' for r in pilot_sources)
    if pilot_sources_ready and pilot['state'] not in ('approved','missing_sources'):
        result['next']={'kind':'cycle-review',**pilot,'command':f'character_workflow.py prepare-cycle --character {character} --direction E'}
    elif source['ready'] and not cycles['ready']:
        pending=next(r for r in cycles['cycles'] if r['state']!='approved')
        result['next']={'kind':'cycle-review',**pending,'command':f'character_workflow.py prepare-cycle --character {character} --direction {pending["direction"]} --action {pending["action"]}'}
    elif source['ready'] and cycles['ready']:
        result['next']='repair-runtime-and-recapture' if rejected else 'build-reviewed-cycles'
    if rejected:result['runtimeRejection']=runtime
    return result

def check_package(character):
    from package_standalone import bundle_inputs
    report=read(ROOT/'dist'/f'{ident(character)}.package.json')
    current=bundle_inputs(character)
    if report['character']!=character or report['inputs']!=current:raise ValueError('Stale package: run package_standalone.py for this character')
    if report['inputSHA256']!=hashlib.sha256(json.dumps(current,sort_keys=True).encode()).hexdigest():raise ValueError('Package input digest mismatch')
    destination=local(report['path'])
    if sha(destination)!=report['sha256'] or destination.stat().st_size!=report['bytes']:raise ValueError('Packaged HTML was changed')
    return report

def check_browser(character,path,package):
    report=read(local(path))
    expected={f'{mode}_{d}' for mode in ['mouse','keyboard'] for d in DIRECTIONS}|{'repeat_preserves_mouse'}
    rows=report.get('results',[])
    if report.get('kind')!='motion-studio-combat-browser' or report.get('character')!=character:raise ValueError('Wrong browser report')
    if report.get('build',{}).get('inputSHA256')!=package['inputSHA256']:raise ValueError('Browser report belongs to different source/runtime bytes')
    if report.get('testScriptSHA256')!=sha(ROOT/'public/qa/combat-checks.js'):raise ValueError('Browser test script changed; rerun it')
    if len(rows)!=17 or {r['name'] for r in rows}!=expected or report.get('pass') is not True:raise ValueError('Incomplete browser input matrix')
    for r in rows:
        facing='E' if r['name']=='repeat_preserves_mouse' else r['name'].split('_',1)[1]
        if r.get('pass') is not True or r.get('heldMouse') is not True or r.get('spriteDirection')!=facing or r.get('direction')!=facing or r.get('shotCount',0)<1 or r.get('observedShots')!=r.get('shotCount') or not r.get('travel',0)>.01 or not 0<=r.get('maxFacingErrorDegrees',999)<=24.51:
            raise ValueError('Browser case failed: '+r['name'])
        if r['name'] in ['mouse_E','mouse_S','mouse_W','mouse_N','repeat_preserves_mouse'] and (r.get('convergedShots',0)<1 or not 0<=r.get('maxCursorError',999)<1e-5):raise ValueError('Cursor convergence failed: '+r['name'])
    if report.get('externalResources')!=[]:raise ValueError('Standalone page used external resources or did not record them')
    if len(report.get('viewport',[]))!=2 or report['viewport'][0]<1920 or report['viewport'][1]<1080:raise ValueError('Use a native 1920x1080 or larger QA viewport')
    rapid=report.get('rapidAim',[])
    if len(rapid)!=16 or {r.get('name') for r in rapid}!={f'{mode}_{d}' for mode in ['stationary','moving'] for d in DIRECTIONS}:
        raise ValueError('Missing rapid aim latency matrix; eventual convergence is insufficient')
    import math
    weapon=recipe(character)['weapon']
    for key in ('fireInterval','reloadSeconds'):
        if type(weapon.get(key)) not in (int,float) or not math.isfinite(weapon[key]) or weapon[key]<=0:raise ValueError('Invalid authoritative weapon timing')
    for row in rapid:
        def finite(key):
            value=row.get(key)
            return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0
        if any(row.get(k) is not True for k in ['pass','heldMouse','locomotionUnchanged','oldProjectileVelocityUnchanged']):raise ValueError('Rapid aim state failed: '+row['name'])
        if any(not finite(k) or row[k]>=1e-5 for k in ['immediateErrorDegrees','firstFrameErrorDegrees','shotErrorDegrees']):raise ValueError('Rapid aim used a stale input: '+row['name'])
        if any(not finite(k) for k in ['immediateMs','firstFrameMs','shotWaitSeconds','eligibleBudgetSeconds']):raise ValueError('Invalid aim timing')
        if row['immediateMs']>1000/120 or row['firstFrameMs']>50:raise ValueError('Aim response exceeds latency budget')
        if any(not finite(k) for k in ['initialCooldownSeconds','initialReloadSeconds']):raise ValueError('Missing initial weapon timing')
        cooldown,reload=row['initialCooldownSeconds'],row['initialReloadSeconds']
        ammo=row.get('initialAmmo')
        if (cooldown>weapon['fireInterval']+1e-8 or reload>weapon['reloadSeconds']+1e-8 or
                type(ammo) is not int or not 0<=ammo<=weapon['magazine']):raise ValueError('Initial weapon state exceeds current recipe')
        expected_budget=(max(reload,cooldown) if reload>0 else cooldown+weapon['reloadSeconds'] if ammo==0 else cooldown)+1/120
        if abs(row['eligibleBudgetSeconds']-expected_budget)>1e-8:raise ValueError('Self-declared eligibility budget differs from weapon state')
        samples=row.get('inputSamples',[]);sector=DIRECTIONS.index(row['name'].split('_',1)[1])
        if len(samples)!=3 or [s.get('sector') for s in samples]!=[(sector+4)%8,(sector+2)%8,sector]:raise ValueError('Missing actual reversal sample sequence')
        previous_ms=-1.0
        def vector2(value):return isinstance(value,list) and len(value)==2 and all(type(v) in (int,float) and math.isfinite(v) for v in value)
        for sample in samples:
            ms=sample.get('offsetMs');angle=sample.get('aim')
            if type(ms) not in (int,float) or not math.isfinite(ms) or not previous_ms<=ms<=row['immediateMs']:raise ValueError('Invalid reversal sample time')
            previous_ms=ms
            muzzle=sample.get('muzzle')
            if (not isinstance(muzzle,list) or len(muzzle)!=3 or not vector2(muzzle[:2]) or
                type(muzzle[2]) not in (int,float) or not math.isfinite(muzzle[2]) or
                abs(muzzle[2]-weapon['height'])>1e-8 or not vector2(sample.get('target')) or
                type(angle) not in (int,float) or not math.isfinite(angle)):
                raise ValueError('Missing sampled muzzle ray at actual weapon height')
            if not vector2(sample.get('requestedTarget')) or not vector2(sample.get('actorPosition')):raise ValueError('Missing independently requested target')
            origin,requested=sample['actorPosition'],sample['requestedTarget']
            requested_angle=sample['sector']*math.pi/4
            if (math.hypot(*(requested[i]-origin[i]-4*f(requested_angle) for i,f in enumerate((math.cos,math.sin))))>1e-6 or
                math.hypot(*(sample['target'][i]-requested[i] for i in (0,1)))>1e-6):raise ValueError('Reversal labels do not match actual requested target')
            if origin!=row.get('locomotionBefore',[])[3:5] or sample.get('actorTime')!=row.get('locomotionBefore',[None])[0]:raise ValueError('Reversal actor basis differs from observed state')
            x,y=(sample['target'][i]-sample['muzzle'][i] for i in (0,1))
            difference=math.atan2(y,x)-angle
            if math.hypot(x,y)<1e-8 or abs(math.atan2(math.sin(difference),math.cos(difference)))>math.radians(1e-5):raise ValueError('A reversal sample used stale aim')
        before,after=row.get('locomotionBefore'),row.get('locomotionAfterInput')
        if (not isinstance(before,list) or len(before)!=9 or before!=after or
                any(type(v) not in (int,float) or not math.isfinite(v) for v in before)):
            raise ValueError('Immediate input changed locomotion or weapon state')
        if before[5]!=ammo or max(0,before[6])!=cooldown or before[8]!=reload:raise ValueError('Initial weapon state differs from sampled actor')
        old=row.get('oldProjectileSamples')
        if not isinstance(old,list):raise ValueError('Missing old projectile velocity samples')
        for i,bullet in enumerate(old):
            if bullet.get('index')!=i or not vector2(bullet.get('before')) or not vector2(bullet.get('after')) or bullet['before']!=bullet['after']:raise ValueError('Old projectile changed velocity')
        if row['shotWaitSeconds']>row['eligibleBudgetSeconds']+1/120+1e-8 or row.get('shotCount',0)<1:raise ValueError('Projectile missed first eligible step')
        if not finite('travel') or (row['travel']<=.01 if row['name'].startswith('moving_') else row['travel']>=.01):raise ValueError('Rapid aim movement coverage missing')
    return binding(local(path))

def verify_runtime(character,browser_report=None,locomotion_report=None):
    package=check_package(character);out=ROOT/'qa'/character
    run=out/'checks'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');run.mkdir(parents=True)
    env=os.environ.copy();env.update(TEMP=str(run),TMP=str(run),PYTHONDONTWRITEBYTECODE='1')
    tests=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('*.test.js'))
    commands=[[sys.executable,'-B','validate_character.py','--character',character],['node','--test',*tests],[sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_*.py'],['node','verify_bundle.mjs',str(local(package['path']))]]
    checks=[]
    for index,command in enumerate(commands):
        result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
        log=run/f'{index}.log';log.write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        checks.append({'command':command,'exitCode':result.returncode,'log':binding(log)})
        if result.returncode:raise ValueError('Validation failed; inspect '+str(log.relative_to(ROOT)))
    browser=check_browser(character,browser_report,package) if browser_report else None
    from locomotion_review import check as check_locomotion
    locomotion=check_locomotion(ROOT,character,locomotion_report,package) if locomotion_report else None
    result={'recordedAt':stamp(),'character':character,'status':'PASS_RUNTIME_CHECKS' if browser and locomotion else 'PASS_INPUT_CHECKS_ONLY' if browser else 'PASS_TECHNICAL_ONLY','package':binding(ROOT/'dist'/f'{character}.package.json'),'inputSHA256':package['inputSHA256'],'checks':checks,'browser':browser,'locomotion':locomotion,'scope':'Input plus temporal selected-renderer checks when supplied; no automatic anatomy, foot-contact, visual approval or Luna generation claim'}
    write(run/'result.json',result);write(out/'latest_runtime_check.json',result)
    return result

def review_runtime(character,evidence,decision,notes,reviewer,locomotion_report=None,motion_evidence=None,observations=None):
    from PIL import Image
    package=check_package(character);path=local(evidence)
    with Image.open(path) as image:
        image.load();width,height=image.size
    if width<1920 or height<1080:raise ValueError('Runtime visual review needs native 1920x1080 evidence')
    if not notes.strip() or not reviewer.strip():raise ValueError('Record actual visual observations and reviewer')
    result={'recordedAt':stamp(),'character':character,'inputSHA256':package['inputSHA256'],'evidence':binding(path),'nativeDimensions':[width,height],'decision':decision,'notes':notes,'reviewer':reviewer}
    if decision=='approved':
        from cycle_review import require_build
        require_build(character)
        if not locomotion_report or not motion_evidence:raise ValueError('A still image cannot approve gait. Supply current --locomotion-report and native --motion-evidence video after watching it')
        from locomotion_review import check as check_locomotion
        result['locomotion']=check_locomotion(ROOT,character,locomotion_report,package)
        import cv2
        video=local(motion_evidence);cap=cv2.VideoCapture(str(video))
        w,h,frames,fps=[cap.get(k) for k in [cv2.CAP_PROP_FRAME_WIDTH,cv2.CAP_PROP_FRAME_HEIGHT,cv2.CAP_PROP_FRAME_COUNT,cv2.CAP_PROP_FPS]]
        ok,_=cap.read();cap.release()
        if not ok or w<1920 or h<1080 or fps<=0 or frames/fps<2:raise ValueError('Motion review requires a decodable native 1080p video spanning at least two seconds')
        result['motionEvidence']=binding(video)
        from motion_evidence import check as check_motion
        result['motionCapture']=check_motion(ROOT,video,package)
        if not observations:raise ValueError('Supply time-specific --observations; generic notes cannot approve gait')
        from runtime_observations import validate
        validate(read(local(observations)),character,package,read(video.with_suffix('.json')),reviewer)
        result['observations']=binding(local(observations))
    path=ROOT/'qa'/character/'runtime_reviews.json';history=read(path) if path.exists() else [];history.append(result);write(path,history)
    if decision!='approved':invalidate_delivery(character,'Runtime visual review requires repair: '+notes)
    return result

def deliver(character,browser_report,locomotion_report):
    from cycle_review import require_build
    cycle_checks=require_build(character)
    # Fail before expensive tests when a visible rejection is still current.
    reviews=read(ROOT/'qa'/character/'runtime_reviews.json')
    if not reviews or reviews[-1].get('decision')!='approved':raise ValueError('Current runtime visual rejection/missing review must be resolved before delivery')
    status=source_status(character)
    if not status['ready']:raise ValueError('Source review is incomplete: '+json.dumps(status['next'],ensure_ascii=False))
    result=verify_runtime(character,browser_report,locomotion_report)
    reviews=read(ROOT/'qa'/character/'runtime_reviews.json');review=reviews[-1]
    if review['decision']!='approved' or review['inputSHA256']!=result['inputSHA256'] or not binding_valid(review['evidence']) or not binding_valid(review.get('motionEvidence')) or not binding_valid(review.get('motionCapture')) or review.get('locomotion')!=result['locomotion']:raise ValueError('Current temporal/visual review is missing, failed, or stale')
    if not binding_valid(review.get('observations')):raise ValueError('Time-specific runtime visual observations are missing/stale')
    from runtime_observations import validate
    validate(read(local(review['observations']['path'])),character,check_package(character),read(local(review['motionCapture']['path'])),review['reviewer'])
    from motion_evidence import check as check_motion
    check_motion(ROOT,local(review['motionEvidence']['path']),check_package(character))
    result.update(status='REVIEWED_DELIVERY',sourceReviews=binding(ROOT/'qa'/character/'source_reviews.json'),runtimeReviews=binding(ROOT/'qa'/character/'runtime_reviews.json'),cycleReviews=binding(ROOT/'qa'/character/'cycle_reviews.json'),cycleChecks=cycle_checks)
    write(ROOT/'dist'/f'{character}.delivery.json',result);return result

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ['status','handoff','build','verify-runtime','deliver','review-source','review-runtime']:
        s=sub.add_parser(name);s.add_argument('--character',required=True,type=ident)
        if name in ['verify-runtime','deliver']:s.add_argument('--browser-report',required=name=='deliver')
        if name in ['verify-runtime','deliver','review-runtime']:s.add_argument('--locomotion-report',required=name=='deliver')
        if name=='review-runtime':s.add_argument('--motion-evidence');s.add_argument('--observations')
        if name in ['review-source','review-runtime']:
            s.add_argument('--decision',choices=['approved','repair'],required=True);s.add_argument('--evidence',required=True);s.add_argument('--notes',required=True);s.add_argument('--reviewer',required=True)
        if name=='review-source':s.add_argument('--slot',required=True)
        if name=='handoff':s.add_argument('--output',help='New packet path below motion_lab_v1/qa; never overwritten')
    s=sub.add_parser('verify-handoff');s.add_argument('--packet',required=True)
    s=sub.add_parser('verify-improvements');s.add_argument('--output',help='Optional fresh QA receipt path')
    s=sub.add_parser('prepare-runtime-review');s.add_argument('--character',required=True,type=ident);s.add_argument('--motion-evidence',required=True)
    for name in ['prepare-cycle','review-cycle']:
        s=sub.add_parser(name);s.add_argument('--character',required=True,type=ident);s.add_argument('--direction',required=True,choices=DIRECTIONS);s.add_argument('--action',default='walk',choices=['walk','run'])
        if name=='review-cycle':
            s.add_argument('--decision',required=True,choices=['approved','repair']);s.add_argument('--packet');s.add_argument('--evidence');s.add_argument('--notes');s.add_argument('--reviewer')
            s.add_argument('--rejection-scope',choices=['source-art','timing','preview','annotation','runtime'])
            s.add_argument('--failed-slot',action='append');s.add_argument('--required-change',action='append')
    a=p.parse_args()
    try:
        if a.command=='status':result=workflow_status(a.character)
        elif a.command=='prepare-cycle':
            from cycle_preview import prepare
            result=prepare(a.character,a.direction,a.action)
        elif a.command=='review-cycle':
            from cycle_review import record
            result=record(a.character,a.direction,a.action,a.decision,a.packet,a.evidence,a.notes,a.reviewer,a.rejection_scope,a.failed_slot,a.required_change)
        elif a.command=='prepare-runtime-review':
            from motion_evidence import check as check_motion
            from runtime_observations import template
            package=check_package(a.character);video=local(a.motion_evidence);check_motion(ROOT,video,package)
            path=ROOT/'qa'/a.character/'runtime_observations'/f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.json'
            write(path,template(a.character,package,read(video.with_suffix('.json'))))
            result={'status':'UNREVIEWED_RUNTIME_TEMPLATE','path':str(path)}
        elif a.command=='handoff':
            from character_handoff import make
            packet=make(a.character)
            path=local(a.output or f'qa/{a.character}/handoffs/{datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.json')
            if not path.is_relative_to(ROOT/'qa') or path.exists():raise ValueError('Use a fresh QA packet path; prior handoffs are preserved')
            write(path,packet)
            result={'status':packet['status'],'packet':str(path),'nextAction':packet['nextAction'],'nextSource':packet['nextSource'],'warnings':packet['warnings'],'reviewedDelivery':False,'lunaGenerationTested':False}
        elif a.command=='verify-handoff':
            from character_handoff import verify
            result=verify(a.packet)
        elif a.command=='verify-improvements':
            from improvement_harness import verify_r3
            result=verify_r3(ROOT.parent)
            if a.output:
                path=local(a.output)
                if not path.is_relative_to(ROOT/'qa') or path.exists():raise ValueError('Use a fresh QA receipt path')
                write(path,result)
            result={k:v for k,v in result.items() if k!='inputs'}
        elif a.command=='build':
            status=source_status(a.character)
            if not status['ready']:raise ValueError('Resolve source status first: '+json.dumps(status['next'],ensure_ascii=False))
            from build_character import compile_character
            result=compile_character(ROOT/'characters'/f'{a.character}.json')
        elif a.command=='verify-runtime':result=verify_runtime(a.character,a.browser_report,a.locomotion_report)
        elif a.command=='deliver':result=deliver(a.character,a.browser_report,a.locomotion_report)
        elif a.command=='review-source':result=review_source(a.character,a.slot,a.decision,a.evidence,a.notes,a.reviewer)
        else:result=review_runtime(a.character,a.evidence,a.decision,a.notes,a.reviewer,a.locomotion_report,a.motion_evidence,a.observations)
        print(json.dumps(result,ensure_ascii=False));return 0
    except (ValueError,OSError,KeyError,TypeError,subprocess.TimeoutExpired) as error:
        print(json.dumps({'status':'NEEDS_FIX','error':str(error)},ensure_ascii=False));return 1

if __name__=='__main__':raise SystemExit(main())

```

## FILE: motion_lab_v1/build_atlas.py
SHA256: 1395b21aa409e4605ce769479e9984968f0a88912adda648879b6869d2dd527f

```text
"""Deterministic, model-free RGBA/atlas compiler for authored ImageGen frames."""
from pathlib import Path
import json,hashlib
import numpy as np
import cv2
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
DIRECTIONS=['E','SE','S','SW','W','NW','N','NE']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def key_image(path):
    im=Image.open(path)
    if im.mode=='RGBA' and im.getextrema()[3][0]<255:
        rgba=np.array(im);rgba[rgba[:,:,3]==0,:3]=0
        return rgba
    rgb=np.array(im.convert('RGB'));f=rgb.astype(np.float32)
    excess=f[:,:,1]-np.maximum(f[:,:,0],f[:,:,2])
    alpha=np.clip(1-(excess-8)/38,0,1)
    alpha[(excess>65)&(f[:,:,1]>85)]=0
    f[:,:,1]=np.where(alpha<.98,np.minimum(f[:,:,1],np.maximum(f[:,:,0],f[:,:,2])+4),f[:,:,1])
    f[alpha==0]=0
    return np.dstack((f,alpha*255)).astype(np.uint8)

def subjects(path,count):
    """Separate complete figures even when a rifle crosses a sheet-cell border."""
    rgba=key_image(path)
    n,labels,stats,_=cv2.connectedComponentsWithStats((rgba[:,:,3]>30).astype(np.uint8))
    components=sorted(range(1,n),key=lambda i:int(stats[i,cv2.CC_STAT_AREA]),reverse=True)[:count]
    if len(components)!=count or min(stats[i,cv2.CC_STAT_AREA] for i in components)<10000:
        raise ValueError(f'{path}: expected {count} separate complete figures')
    components.sort(key=lambda i:int(stats[i,cv2.CC_STAT_LEFT]))
    result=[]
    for i in components:
        x,y,w,h,area=map(int,stats[i]);mask=(labels==i).astype(np.uint8)
        mask=cv2.dilate(mask,np.ones((3,3),np.uint8))
        separated=rgba.copy();separated[mask==0]=0
        box=[max(0,x-12),max(0,y-12),min(rgba.shape[1],x+w+12),min(rgba.shape[0],y+h+12)]
        result.append((Image.fromarray(separated[box[1]:box[3],box[0]:box[2]]),box))
    return result

def register(path,config,direction,annotation):
    raw=key_image(path);ys,xs=np.where(raw[:,:,3]>200)
    if not len(xs):raise ValueError(f'{path}: no opaque subject')
    x0,y0,x1,y1=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)
    cell=config.get('cell',[768,768]);root=config.get('root',[384,716]);height=config.get('spriteHeight',656)
    scale=height/(y1-y0)
    anchor=annotation.get('hipX')
    if anchor is None:
        region=raw[int(y0+(y1-y0)*.39):int(y0+(y1-y0)*.47),:,3]
        valid=np.where((region>200).sum(axis=0)>region.shape[0]*.7)[0]
        anchor=float(np.median(valid))
    matrix=np.float32([[scale,0,root[0]-anchor*scale],[0,scale,root[1]-y1*scale]])
    corners=np.array([[x0,y0,1],[x1,y1,1]])@matrix.T
    if np.any(corners[0]<4) or corners[1,0]>cell[0]-4 or corners[1,1]>cell[1]-4:
        raise ValueError(f'{path}: cell too small / hip anchor invalid; bounds={corners.tolist()}')
    out=cv2.warpAffine(raw,matrix,tuple(cell),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_CONSTANT)
    if 'muzzle' in annotation:
        muzzle=(matrix@np.array([*annotation['muzzle'],1])).tolist()
    else:
        band=raw[y0:int(y0+(y1-y0)*.45),:,3];yy,xx=np.where(band>210);yy+=y0
        if direction in ['W','SW','NW']:
            edge=xx.min();choose=xx<=edge+3
        elif direction=='N':
            edge=yy.min();choose=yy<=edge+3
        elif direction=='S':
            choose=np.zeros_like(xx,dtype=bool)
            choose[np.argmin(abs(xx-anchor)+abs(yy-(y0+(y1-y0)*.32)))]=True
        else:
            edge=xx.max();choose=xx>=edge-3
        muzzle=(matrix@np.array([float(np.median(xx[choose])),float(np.median(yy[choose])),1])).tolist()
    green=(out[:,:,1].astype(int)-np.maximum(out[:,:,0],out[:,:,2]).astype(int)>45)&(out[:,:,3]>128)
    with Image.open(path) as native_image:native_size=list(native_image.size)
    note={'source':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'native':native_size,
          'bounds':[x0,y0,x1,y1],'hipX':anchor,'scale':scale,'matrix':matrix.tolist(),'muzzle':muzzle,
          'opaqueGreenPixels':int(green.sum()),'alphaBounds':corners.tolist()}
    return out,note

def build(config,direction,action,paths,annotations,output_root=None):
    output_root=output_root or ROOT
    ident=config['id'];out=output_root/'public/assets/atlas'/ident;out.mkdir(parents=True,exist_ok=True)
    pairs=[register(path,config,direction,annotations.get(str(i),{})) for i,path in enumerate(paths)]
    frames=[p[0] for p in pairs];notes=[p[1] for p in pairs]
    cell=config.get('cell',[768,768]);root=config.get('root',[384,716]);height=config.get('spriteHeight',656)
    cols=min(3,len(frames));rows=(len(frames)+cols-1)//cols;atlas=Image.new('RGBA',(cell[0]*cols,cell[1]*rows))
    for i,im in enumerate(frames):atlas.paste(Image.fromarray(im),(i%cols*cell[0],i//cols*cell[1]))
    atlas.save(out/f'{direction}_{action}.webp',lossless=True,method=5)
    preview=output_root/'reference/atlas'/ident;preview.mkdir(parents=True,exist_ok=True)
    contact=Image.new('RGB',atlas.size,(18,28,36));contact.paste(atlas,(0,0),atlas);draw=ImageDraw.Draw(contact)
    for i in range(len(frames)):
        ox=i%cols*cell[0];oy=i//cols*cell[1]
        draw.text((ox+20,oy+20),f'{direction} / {action} / {i}',fill='#b0dacc')
        draw.line((ox+20,oy+root[1],ox+cell[0]-20,oy+root[1]),fill='#35534f')
        m=notes[i]['muzzle'];draw.ellipse((ox+m[0]-4,oy+m[1]-4,ox+m[0]+4,oy+m[1]+4),outline='#ffcc70',width=2)
    contact.save(preview/f'{direction}_{action}_keyframes.png')
    anim=[]
    for im in frames:
        bg=Image.new('RGB',tuple(cell),(18,28,36));bg.paste(Image.fromarray(im),(0,0),Image.fromarray(im[:,:,3]));anim.append(bg)
    anim[0].save(preview/f'{direction}_{action}.gif',save_all=True,append_images=anim[1:],duration=round(1200/len(frames)),loop=0)
    record={'image':f'assets/atlas/{ident}/{direction}_{action}.webp','cell':cell,'columns':cols,'frames':len(frames),
            'root':root,'height':height,'authoredFrames':len(frames),'muzzles':[n['muzzle'] for n in notes],'sources':notes}
    (out/f'{direction}_{action}.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps({'direction':direction,'action':action,'frames':len(frames)}),flush=True)
    return record

```

## FILE: motion_lab_v1/gait_contract.py
SHA256: e297710d2fc2ecbf39f8e5920d1b31cb8e3cfd15d82b18cb79461b98c3c98a9a

```text
"""One maintained six-phase vocabulary for requests, previews and reviews."""
import hashlib
import json

VERSION = 1
PHASES = (
    {'index': 0, 'name': 'left_contact', 'support': 'double', 'lead': 'left',
     'prompt': 'right leg trailing / left forward contact'},
    {'index': 1, 'name': 'right_swing', 'support': 'left', 'lead': None,
     'prompt': 'right leg swings behind / left supports'},
    {'index': 2, 'name': 'right_passing', 'support': 'left', 'lead': None,
     'prompt': 'right knee passes forward / left supports'},
    {'index': 3, 'name': 'right_contact', 'support': 'double', 'lead': 'right',
     'prompt': 'left leg trailing / right forward contact'},
    {'index': 4, 'name': 'left_swing', 'support': 'right', 'lead': None,
     'prompt': 'left leg swings behind / right supports'},
    {'index': 5, 'name': 'left_passing', 'support': 'right', 'lead': None,
     'prompt': 'left knee passes forward / right supports'},
)
# Accepted ASTER contact-dwell starting point; visual calibration remains required.
WALK_PHASE_STARTS = [0, .2, .33, .5, .7, .83]


def digest():
    return hashlib.sha256(json.dumps({'version': VERSION, 'phases': PHASES,
        'walkPhaseStarts': WALK_PHASE_STARTS}, sort_keys=True).encode()).hexdigest()


def starts(spec):
    values = spec.get('phaseStarts', [i / 6 for i in range(6)])
    if (len(values) != 6 or values[0] != 0 or
            any(type(v) not in (int, float) or not 0 <= v < 1 for v in values) or
            any(b <= a for a, b in zip(values, values[1:]))):
        raise ValueError('Invalid six-phase timing')
    return values


def frame_at(phase, phase_starts):
    p = phase % 1
    return max(i for i, start in enumerate(phase_starts) if p >= start)

```

## FILE: motion_lab_v1/prepare_enemy_asset.py
SHA256: d63a443ba1e9704e158a6bd4830f4471ca8b61ab1ddbf4f58d51e1ae2ee4237a

```text
"""Deterministic enemy matte/crop and native QA. Never activates an app asset.

Uses the established model-free compiler. Source artwork stays byte-immutable.
No leg segmentation, anatomical warp, local model or synthetic missing pixels.
"""
from pathlib import Path
import argparse, hashlib, json, re
from PIL import Image, ImageDraw
import numpy as np
from build_atlas import key_image

ROOT=Path(__file__).resolve().parent

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_source(source, response):
    """Bind the exact retained master, not just the name of its generator.

    This is local provenance consistency, not cryptographic provider attestation
    or an artistic approval. The original tool response must be recorded honestly.
    """
    from source_provenance import response_master
    if response_master(ROOT,response)!=source:
        raise ValueError('Tool response must bind this exact project copy')
    return json.loads(response.read_text(encoding='utf-8-sig'))

def prepare(ident, source, response):
    if not re.fullmatch(r'[a-z0-9_-]+',ident):
        raise ValueError('Use an asset id, not a path')
    source=source.resolve(); response=response.resolve()
    if not source.is_relative_to(ROOT) or not response.is_relative_to(ROOT):
        raise ValueError('Project-local source and actual tool response required')
    verify_source(source,response)
    with Image.open(source) as opened:raw=opened.copy()
    if max(raw.size)<1024:
        raise ValueError('Native high-resolution generated master required')
    rgba=key_image(source)
    yy,xx=np.where(rgba[:,:,3]>30)
    if not len(xx):
        raise ValueError('Empty separated subject; retain as failed source')
    # Keep previous QA bytes when the preparation implementation changes.
    dependencies={'preparation':sha(Path(__file__)),'matte':sha(ROOT/'build_atlas.py'),'provenance':sha(ROOT/'source_provenance.py')}
    implementation=hashlib.sha256(json.dumps(dependencies,sort_keys=True).encode()).hexdigest()[:8]
    out=ROOT/'qa/stage1_enemies_20260913'/ident/(sha(source)[:12]+'_'+implementation)
    out.mkdir(parents=True,exist_ok=True)
    box=[max(0,int(xx.min())-12),max(0,int(yy.min())-12),min(raw.width,int(xx.max())+13),min(raw.height,int(yy.max())+13)]
    cut=Image.fromarray(rgba).crop(box)
    target=out/'candidate_rgba.png'; cut.save(target)
    # A 1:1 native crop on each matte is deliberately separate from fit previews.
    for label,native in [('native',True),('full',False)]:
        board=Image.new('RGB',(1920,1080),'#15232b')
        for ox,color in [(0,'#eeeeee'),(960,'#15232b')]:
            panel=Image.new('RGBA',(960,1080),color)
            im=cut.copy()
            if native:
                left=max(0,(im.width-940)//2); top=max(0,(im.height-1040)//2)
                im=im.crop((left,top,min(im.width,left+940),min(im.height,top+1040)))
            else: im.thumbnail((930,1030),Image.Resampling.LANCZOS)
            panel.alpha_composite(im,((960-im.width)//2,(1080-im.height)//2))
            board.paste(panel.convert('RGB'),(ox,0))
        ImageDraw.Draw(board).text((16,16),ident+' / '+('1:1 ORIGINAL PIXEL CROP' if native else 'FULL SUBJECT FIT'),fill='#e5974d')
        board.save(out/f'{label}_1920x1080.png')
    report={'id':ident,'status':'CANDIDATE_NOT_REVIEWED','source':str(source.relative_to(ROOT)),
            'sourceSHA256':sha(source),'toolResponse':{'path':str(response.relative_to(ROOT)),'sha256':sha(response)},
            'sourceNative':[raw.width,raw.height],'box':box,'candidate':str(target.relative_to(ROOT)),
            'candidateSHA256':sha(target),'candidateNative':list(cut.size),'native_review':[1920,1080],
            'operation':'existing key_image chroma/alpha separation then native crop only',
            'preparationCodeSHA256':sha(Path(__file__)),
            'matteCodeSHA256':sha(ROOT/'build_atlas.py'),
            'implementationDependencies':dependencies,
            'resampling':False,'anatomicalWarp':False,'runtimePromotion':False}
    (out/'preparation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--tool-response',type=Path,required=True)
    a=p.parse_args();prepare(a.id,a.source,a.tool_response)

```
