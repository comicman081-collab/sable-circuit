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
