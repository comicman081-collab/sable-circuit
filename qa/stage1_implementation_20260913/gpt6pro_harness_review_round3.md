# Round 3: verify the seven concrete R2 counterexamples, not final art approval

Same SABLE CIRCUIT local work. R1 and R2 actual visible replies are preserved at
motion_lab_v1/qa/stage1_enemies_20260913/cycle_capture/gpt6pro_review_round{1,2}.json.
This is a current-byte snapshot, not an assertion that all R1 work is finished.

Changes for your exact R2 cases:
- R2-01: BEFORE each pointer event retain actorPosition and requestedTarget;
  after dispatch compare actual target to that independent request. Validator
  recomputes requested world point from actor basis+sector+4m radius, not aim=sector.
- R2-02: ninth before/after Actor component is actual reload. Match ammo, cooldown,
  reload to initial timing, keep weapon cadence unchanged. Concurrent positive
  reload/cooldown use max; empty-magazine initiation still includes cooldown+reload.
- R2-03: source-atlas validator binds phaseStarts to actual recipe and re-runs
  source registration into memory; compares alpha, visible RGB, clip and muzzle
  metadata. RGB under zero alpha is normalized (WebP may discard hidden RGB).
- R2-04: distinguish each expected/alternative phase on their difference region,
  never on foreground/background average alone. Keep every native differing pixel
  for small regions, cap broad regions to 4096 evenly distributed native samples.
  An ambiguous pair is insufficient evidence, not automatic art-repair/approval.
  Added your frozen 32x32 patch counterexample, lossless FFV1; it is rejected.
  Positive fixture now really advances six different synthetic cells at recipe
  speed. Actual rifle candidate's 107 decoded frames also passed before its
  subsequent background-only source normalization; no artistic approval claimed.
- R2-05: shared source_provenance.response_master validates full path boundaries;
  result.png.other.png counterexample rejected. It is still local consistency,
  never cryptographic provider attestation.
- R2-06: candidate fingerprint includes prepare + matte + provenance code SHA.
  Actual prepare() test changes matte dependency and verifies first report retained.
- R2-07: machine hit rectangle transforms all four native corners into world AABB.
  Native interior points tested under rotation/nonuniform parent scale.

Other R1 work completed in the meantime: shared retained-master and explicit
derivation checks across all three importers and source_status; approved source
receipts bound by hash; decoded source-pixel rejection; failure-scoped cycle
records with actual failedSlots or requiredChange; independent source recompile;
pair halves prevalidated before slot writes; import invalidates delivery while
preserving history; handoff includes new code/matte evidence dependencies.
Historical accepted ASTER/MICA/ROOK raster bytes, gait and weapon settings are
not regenerated or changed; old evidence is not relabeled as a fresh run.

Executed locally on this implementation:
- Entire Python discovery: 90 tests, 94.876s, OK.
- Entire Node test suite: 30 tests, OK (actual existing Actor/renderer tests).
- Godot machine source/transform/projectile test: 370 checks, PASS.
- Real Stage 1 technical playthrough after geometry fix: 6 rooms, both optional
  recoveries, 10 defeats, EXTRACTED, all operators alive at boss exit (4/106/88 HP).
- Native 1920x1080 actual Godot candidate screenshots captured and decoded.
  Those are candidate previews only, not registry promotion or motion approval.

Still OPEN, not claimed fixed: atomic renderer loading / scoped legacy fallback;
browser 1x/no-seek observation and category-specific timing coverage; actual
anatomical-label observations and overlays; four-limb contract; final human enemy
cycles and Stage 1 raster promotion; full live browser recapture with the newly
strengthened QA rows. Pair prevalidation does not claim crash-proof filesystem
transactions. Independent generation by Luna has NOT been run.

Please review only whether R2-01 through R2-07 remain reproducibly defective in
this snapshot. Give the smallest new counterexample if one remains. Do not label
untested art/runtime or the whole MVP approved. Broader R1 remaining work above
is still tracked separately. Korean response requested.

## FILE: motion_lab_v1/source_provenance.py
SHA256: 2f46683d3242a15509bb23a04dd913f168647a957b514bf7433a5a836a985e02
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
    # Match a complete returned token, not another path with the same prefix.
    def full_token(match):
        before=normalized[:match.start()];after=normalized[match.end():]
        left_ok=not before or before[-1].isspace() or before[-1] in '\"\'`('
        right_ok=not after or after[0].isspace() or after[0] in '\"\'`)' or after=='.' or after.startswith('. ') or after.startswith('.\n')
        return left_ok and right_ok
    if not any(full_token(match) for match in re.finditer(re.escape(candidate),normalized)):
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

## FILE: motion_lab_v1/character_workflow.py
SHA256: 6d104ca8342c7296c34f801b3603fbb66787479c14b695e854c29619d35fedfe
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
            if not vector2(sample.get('muzzle')) or not vector2(sample.get('target')) or type(angle) not in (int,float) or not math.isfinite(angle):raise ValueError('Missing sampled muzzle ray')
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

## FILE: motion_lab_v1/cycle_review.py
SHA256: 9c51ffc52a007531967477233796aa3cc755b66b2abe8bb47ed0f5941449a245
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
            # Keep every pixel of small differences (the frozen-foot counter-
            # example is 2048 pixels). Bound broad-body comparisons to evenly
            # distributed native pixel samples; never dilute into background.
            offsets=np.flatnonzero(mask)
            offsets=offsets[::max(1,math.ceil(len(offsets)/4096))]
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
                correct_error=float(np.abs(pixels[mask]-expected[index][mask]).mean())
                other_error=float(np.abs(pixels[mask]-expected[alternative][mask]).mean())
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

## FILE: motion_lab_v1/public/qa/combat-checks.js
SHA256: 1dce9814a85f6def668daa1185b4fba446a70baa0cf45bb37f1ffd15c259af82
```text
// Development-only browser regression. Never bundled into a delivered HTML.
// Start a real held left mouse button on the canvas through the browser tool
// first; the test refuses to claim held-mouse coverage without it.
export async function runCombatChecks(){
  const debug=window.motionDebug,effects=document.getElementById('effects');
  if(!debug||debug.mode!=='combat'||!debug.controls.mouseDown)throw Error('Start held mouse fire on the combat canvas first');
  if(!window.__MOTION_BUILD__)throw Error('Open the current packaged HTML, not an unbound development page');
  if(!document.getElementById('autoaim').checked)throw Error('Enable movement facing before testing');
  const dirs=['E','SE','S','SW','W','NW','N','NE'];
  const chords=[['KeyD'],['KeyS','KeyD'],['KeyS'],['KeyS','KeyA'],['KeyA'],['KeyW','KeyA'],['KeyW'],['KeyW','KeyD']];
  const results=[],held=new Set();
  const key=(code,down,repeat=false)=>{
    effects.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,key:code,bubbles:true,cancelable:true,repeat}));
    if(down)held.add(code);else held.delete(code);
  };
  const release=()=>{for(const code of [...held])key(code,false);};
  const pointer=(angle,distance=.4)=>{
    const a=debug.actor,p=debug.project(a.x+Math.cos(angle)*distance,a.y+Math.sin(angle)*distance,debug.profile.weapon.height),r=effects.getBoundingClientRect();
    effects.dispatchEvent(new PointerEvent('pointermove',{pointerId:1,pointerType:'mouse',clientX:p[0]+r.left,clientY:p[1]+r.top,buttons:1,bubbles:true}));
  };
  const observe=(name,expected,updatePointer=null)=>new Promise((resolve,reject)=>{
    const started=performance.now(),shotStart=debug.actor.shots,eventStart=debug.actor.time,position=[debug.actor.x,debug.actor.y];
    const frames=new Set(),seenShots=new Set();let maxError=0,renderMatches=true,maxCursorError=0,convergedShots=0;
    function sample(now){
      if(!debug.controls.mouseDown){reject(Error('Held mouse fire was interrupted'));return;}
      const c=debug.current;frames.add(c.frame);renderMatches&&=c.spriteDirection===c.direction;
      for(const e of debug.events){
        if(e.time<=eventStart||seenShots.has(e.time))continue;
        seenShots.add(e.time);
        const angle=e.aim-dirs.indexOf(e.direction)*Math.PI/4;
        maxError=Math.max(maxError,Math.abs(Math.atan2(Math.sin(angle),Math.cos(angle)))*180/Math.PI);
        if(e.target&&e.converges){convergedShots++;maxCursorError=Math.max(maxCursorError,Math.abs((e.target[0]-e.origin[0])*Math.sin(e.aim)-(e.target[1]-e.origin[1])*Math.cos(e.aim)));}
      }
      if(now-started>=180&&debug.actor.shots>shotStart){
        const row={name,expected,direction:c.direction,spriteDirection:c.spriteDirection,shotCount:debug.actor.shots-shotStart,observedShots:seenShots.size,travel:Math.hypot(debug.actor.x-position[0],debug.actor.y-position[1]),frames:[...frames],maxFacingErrorDegrees:maxError,maxCursorError,convergedShots,heldMouse:debug.controls.mouseDown};
        const farAim=['mouse_E','mouse_S','mouse_W','mouse_N','repeat_preserves_mouse'].includes(name);
        row.pass=c.direction===expected&&c.spriteDirection===expected&&renderMatches&&maxError<=24.51&&row.travel>.01&&row.observedShots===row.shotCount&&(!farAim||(convergedShots>0&&maxCursorError<1e-5));
        resolve(row);return;
      }
      if(now-started>2400){reject(Error(name+': no shot within reload budget'));return;}
      if(updatePointer)updatePointer();
      requestAnimationFrame(sample);
    }
    if(updatePointer)updatePointer();requestAnimationFrame(sample);
  });
  try{
    key('KeyD',true);
    for(let i=0;i<8;i++)results.push(await observe('mouse_'+dirs[i],dirs[i],()=>pointer(i*Math.PI/4,i%2?.4:3)));
    release();
    for(let i=0;i<8;i++){
      pointer((i+4)%8*Math.PI/4,3);
      for(const code of chords[i])key(code,true);
      results.push(await observe('keyboard_'+dirs[i],dirs[i]));
      release();
    }
    key('KeyW',true);pointer(0,3);key('KeyW',true,true);
    results.push(await observe('repeat_preserves_mouse','E',()=>pointer(0,3)));
  }finally{release();}
  const rapidAim=await checkRapidAim(debug,effects);
  const scriptBytes=await fetch('/qa/combat-checks.js',{cache:'no-store'}).then(response=>{
    if(!response.ok)throw Error('Cannot fetch the browser test script');
    return response.arrayBuffer();
  });
  const digest=await crypto.subtle.digest('SHA-256',scriptBytes);
  const testScriptSHA256=[...new Uint8Array(digest)].map(value=>value.toString(16).padStart(2,'0')).join('');
  const externalResources=[...performance.getEntriesByType('resource')]
    .map(entry=>entry.name)
    .filter(name=>/^https?:/i.test(name)&&new URL(name,location.href).origin!==location.origin)
    .filter((name,index,all)=>all.indexOf(name)===index)
    .sort();
  return {schema:2,kind:'motion-studio-combat-browser',recordedAt:new Date().toISOString(),character:debug.profile.id,build:window.__MOTION_BUILD__,testScriptSHA256,externalResources,viewport:[innerWidth,innerHeight],input:'Real held mouse button; synthetic DOM movement/pointer events; actual fixed-step and WebGL renderer',results,rapidAim,pass:results.length===17&&results.every(r=>r.pass)&&rapidAim.every(r=>r.pass)};
}

// Eventual convergence is insufficient: probe in the input event's own turn,
// the first displayed frame, then the FIRST eligible projectile. Do not speed
// up the gun, refill ammo or retarget bullets to manufacture responsiveness.
async function checkRapidAim(d,effects){
  if(!d.aimSnapshot)throw Error('Runtime lacks immediate aim path');
  const frame=()=>new Promise(requestAnimationFrame),rows=[];
  const order=[0,4,2,6,1,5,3,7],dirs=['E','SE','S','SW','W','NW','N','NE'];
  const error=(m,t,a)=>Math.abs(Math.atan2(Math.sin(Math.atan2(t[1]-m[1],t[0]-m[0])-a),Math.cos(Math.atan2(t[1]-m[1],t[0]-m[0])-a)))*180/Math.PI;
  const move=down=>effects.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code:'KeyD',key:'d',bubbles:true,cancelable:true}));
  const locomotion=()=>JSON.stringify([d.actor.time,d.actor.phase,d.actor.distance,d.actor.x,d.actor.y,d.actor.ammo,d.actor.cooldown,d.actor.lastShot,d.actor.reload]);
  try{
    // Same bounded, obstacle-free lane as locomotion QA, while retaining the
    // real held trigger, cooldown, ammo, physics and renderer.
    d.actor.x=-4;d.actor.y=2.5;d.world.camera.x=-4;d.world.camera.y=2.5;
    const settle=performance.now();while(performance.now()-settle<400)await frame();
    for(const moving of [false,true]){
      if(moving)move(true);
      for(const dir of order){
        const initial=locomotion(),old=d.world.bullets.map(b=>[b,b.vx,b.vy]);
        const start=performance.now(),time=d.actor.time,shots=d.actor.shots,position=[d.actor.x,d.actor.y];
        const cooldown=Math.max(0,d.actor.cooldown),reload=d.actor.reload;
        const budget=(reload>0?Math.max(reload,cooldown):d.actor.ammo<=0?cooldown+d.profile.weapon.reloadSeconds:cooldown)+1/120;
        const r=effects.getBoundingClientRect();let screen;const inputSamples=[];
        // Several coalesced-style samples in one event-loop turn: last wins.
        for(const sample of [(dir+4)%8,(dir+2)%8,dir]){
          const a=sample*Math.PI/4;
          const actorPosition=[d.actor.x,d.actor.y],requestedTarget=[d.actor.x+4*Math.cos(a),d.actor.y+4*Math.sin(a)];
          screen=d.project(...requestedTarget,d.profile.weapon.height);
          effects.dispatchEvent(new PointerEvent('pointermove',{pointerId:1,pointerType:'mouse',clientX:r.left+screen[0],clientY:r.top+screen[1],buttons:1,bubbles:true}));
          inputSamples.push({sector:sample,actorPosition,requestedTarget,offsetMs:performance.now()-start,actorTime:d.actor.time,
            muzzle:[...d.aimSnapshot.muzzle],target:[...d.aimSnapshot.target],aim:d.aimSnapshot.aim});
        }
        const immediate=d.aimSnapshot;
        const inputError=error(immediate.muzzle,immediate.target,immediate.aim),immediateMs=performance.now()-start;
        const unchanged=locomotion()===initial;
        const afterInput=JSON.parse(locomotion());
        await frame();
        const c=d.current,visibleMuzzle=d.unproject(...c.muzzle,d.profile.weapon.height),visibleTarget=d.unproject(...screen,d.profile.weapon.height);
        const renderError=error(visibleMuzzle,visibleTarget,c.aim),firstFrameMs=performance.now()-start;
        let shot=d.events.find(e=>e.time>time);
        while(!shot&&performance.now()-start<2600){await frame();shot=d.events.find(e=>e.time>time);}
        const shotError=shot?.target?error(shot.origin,shot.target,shot.aim):999;
        const row={name:(moving?'moving':'stationary')+'_'+dirs[dir],heldMouse:d.controls.mouseDown,
          immediateErrorDegrees:inputError,immediateMs,firstFrameErrorDegrees:renderError,firstFrameMs,
          shotErrorDegrees:shotError,shotWaitSeconds:shot?shot.time-time:999,eligibleBudgetSeconds:budget,
          initialCooldownSeconds:cooldown,initialReloadSeconds:reload,initialAmmo:JSON.parse(initial)[5],
          inputSamples,locomotionBefore:JSON.parse(initial),locomotionAfterInput:afterInput,
          oldProjectileSamples:old.map(([b,x,y],index)=>({index,before:[x,y],after:[b.vx,b.vy]})),
          shotCount:d.actor.shots-shots,locomotionUnchanged:unchanged,
          travel:Math.hypot(d.actor.x-position[0],d.actor.y-position[1]),
          oldProjectileVelocityUnchanged:old.every(([b,x,y])=>b.vx===x&&b.vy===y)};
        row.pass=inputSamples.every(s=>Math.hypot(s.target[0]-s.requestedTarget[0],s.target[1]-s.requestedTarget[1])<1e-6)&&row.heldMouse&&inputError<1e-5&&renderError<1e-5&&shotError<1e-5&&immediateMs<=1000/120&&firstFrameMs<=50&&
          row.shotWaitSeconds<=budget+1/120+1e-8&&row.shotCount>=1&&unchanged&&row.oldProjectileVelocityUnchanged&&
          (moving?row.travel>.01:row.travel<.01);
        rows.push(row);
      }
      if(moving)move(false);
    }
  }finally{move(false);}
  return rows;
}

```

## FILE: motion_lab_v1/public/simulation.js
SHA256: 0eab50fb0f34686bead88589a7d554e34fb704f980d2d5391cbaa8fb53a5b50b
```text
// A fixed-step, renderer-independent controller shared by preview and combat.
export const DIRECTIONS=['E','SE','S','SW','W','NW','N','NE'];
export const TAU=Math.PI*2;
export const STEP=1/120;
export const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export const wrap=a=>Math.atan2(Math.sin(a),Math.cos(a));
export const direction=a=>(Math.round(a/(Math.PI/4))+8)%8;

export class Actor {
  constructor(profile){
    this.profile=profile;
    this.x=this.y=this.vx=this.vy=this.phase=this.time=this.distance=0;
    this.direction=0;this.aim=0;this.moveAngle=0;this.amount=0;
    this.run=false;this.firing=false;this.cooldown=0;this.reload=0;this.lastShot=-10;this.shotBuffer=0;
    this.ammo=profile.weapon.magazine;this.shots=0;this.kills=0;this.hp=100;
  }
  get recoil(){const t=(this.time-this.lastShot)*27;return t<0?0:(1+t)*Math.exp(-t);}
  requestReload(){if(this.reload===0&&this.ammo<this.profile.weapon.magazine)this.reload=this.profile.weapon.reloadSeconds;}
  queueShot(){this.shotBuffer=.18;}
  update(dt,input,blocks=[]){
    if(!(dt>0&&dt<=.05))throw new RangeError('Use bounded fixed simulation steps.');
    this.time+=dt;this.run=!!input.run;
    const firing=!!input.fire||this.shotBuffer>0;this.firing=firing;this.shotBuffer=Math.max(0,this.shotBuffer-dt);
    let x=input.x||0,y=input.y||0;const length=Math.hypot(x,y);
    if(length>1){x/=length;y/=length;}
    const speed=this.run?this.profile.locomotion.runSpeed:this.profile.locomotion.walkSpeed;
    const gain=1-Math.exp(-18*dt);
    this.vx+=(x*speed-this.vx)*gain;this.vy+=(y*speed-this.vy)*gain;
    let nx=this.x+this.vx*dt,ny=this.y+this.vy*dt;const radius=this.profile.radius||.19;
    for(const b of blocks){
      if(nx>b.x-radius&&nx<b.x+b.w+radius&&this.y>b.y-radius&&this.y<b.y+b.h+radius){nx=this.x;this.vx=0;}
      if(ny>b.y-radius&&ny<b.y+b.h+radius&&nx>b.x-radius&&nx<b.x+b.w+radius){ny=this.y;this.vy=0;}
    }
    nx=clamp(nx,-7.7,7.7);ny=clamp(ny,-5.7,5.7);
    const travel=Math.hypot(nx-this.x,ny-this.y);this.distance+=travel;
    this.x=nx;this.y=ny;
    if(travel>.000001){
      this.moveAngle=Math.atan2(this.vy,this.vx);
      const stride=this.run?this.profile.locomotion.runStride:this.profile.locomotion.walkStride;
      this.phase=(this.phase+travel/stride)%1;
    }
    this.amount+=(clamp(travel/(dt*speed),0,1)-this.amount)*(1-Math.exp(-16*dt));
    // Facing follows the requested direction immediately; velocity alone
    // still eases through the turn and controls the foot-cycle distance.
    if(input.aim!=null)this.aim=input.aim;else if(length>.02)this.aim=Math.atan2(y,x);
    if(Math.abs(wrap(this.aim-this.direction*Math.PI/4))>Math.PI/8+.035)this.direction=direction(this.aim);
    if(input.reload)this.requestReload();
    if(this.reload>0){this.reload=Math.max(0,this.reload-dt);if(this.reload===0)this.ammo=this.profile.weapon.magazine;}
    this.cooldown-=dt;
    let fired=false;
    if(firing&&this.reload===0&&this.cooldown<=0){
      if(this.ammo>0){
        this.ammo--;this.shots++;this.lastShot=this.time;fired=true;this.shotBuffer=0;
        this.cooldown+=this.profile.weapon.fireInterval;
      }else this.requestReload();
    }
    if(!firing||this.reload>0)this.cooldown=Math.max(0,this.cooldown);
    return fired;
  }
  renderPose(facingDirection=this.direction){
    const backwards=Math.cos(this.moveAngle-facingDirection*Math.PI/4)<-.35;
    return {phase:backwards?(1-this.phase)%1:this.phase,amount:this.amount,run:this.run,
      // Keep the weapon raised through the held-fire/recoil window so the
      // authored body and the muzzle/projectile line read as one action.
      firing:this.firing||this.recoil>.045,recoil:this.recoil,aim:this.aim,facing:facingDirection*Math.PI/4,time:this.time,
      reload:this.reload?Math.sin(Math.PI*this.reload/this.profile.weapon.reloadSeconds):0};
  }
}

export function segmentCircle(a,b,c,r){
  const dx=b[0]-a[0],dy=b[1]-a[1];
  const t=clamp(((c[0]-a[0])*dx+(c[1]-a[1])*dy)/(dx*dx+dy*dy||1),0,1);
  return Math.hypot(a[0]+t*dx-c[0],a[1]+t*dy-c[1])<=r;
}
export function segmentBox(a,b,box){
  let lo=0,hi=1;
  for(const [i,min,max] of [[0,box.x,box.x+box.w],[1,box.y,box.y+box.h]]){
    const d=b[i]-a[i];
    if(Math.abs(d)<1e-9){if(a[i]<min||a[i]>max)return false;continue;}
    let t0=(min-a[i])/d,t1=(max-a[i])/d;if(t0>t1)[t0,t1]=[t1,t0];
    lo=Math.max(lo,t0);hi=Math.min(hi,t1);if(lo>hi)return false;
  }
  return true;
}

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

## FILE: scripts/animation/site7_machine_sprite.gd
SHA256: 2ce25a68d5269cca543c7e4416cfcd32fd95b1e8bfff6c67efb95f34033cf3e8
```text
extends Node2D
## Source-preserving preview/runtime for non-walking machines only.
## A drone banks as one rigid object; an anchor stays anchored. Neither is a
## humanoid gait and neither may use a six-frame foot-cycle approval as proof.

var actor: EnemyActor
var sprite: Sprite2D
var kind := ""
var emitter_px := Vector2.ZERO
var image_size := Vector2.ZERO
var age := 0.0
var flash := 0.0
var render_scale := 1.0
var body_origin := Vector2.ZERO
var configured := false

func configure(owner_actor: EnemyActor, spec: Dictionary) -> bool:
    actor = owner_actor
    kind = str(spec.get("kind", ""))
    if kind not in ["hover_machine", "anchored_machine"]:
        push_error("Machine sprite cannot substitute for a walking enemy")
        return false
    var path := str(spec.get("texture", ""))
    var image := Image.load_from_file(path)
    if image == null or image.is_empty(): return false
    var source_hash := FileAccess.get_sha256(path)
    if source_hash != str(spec.get("texture_sha256", "")):
        push_error("Machine preview texture bytes differ from reviewed candidate")
        return false
    image_size = Vector2(image.get_size())
    var root_xy: Array = spec.get("root_px", [])
    var emitter_xy: Array = spec.get("emitter_px", [])
    if root_xy.size() != 2 or emitter_xy.size() != 2: return false
    emitter_px = Vector2(float(emitter_xy[0]), float(emitter_xy[1]))
    if not Rect2(Vector2.ZERO, image_size).has_point(emitter_px): return false
    render_scale = float(spec.get("display_height", 110.0)) / image_size.y
    if render_scale <= 0.0 or render_scale > 1.0: return false
    sprite = Sprite2D.new()
    sprite.name = "AuthoredMachinePixels"
    sprite.set_meta("preserve_authored_material", true)
    sprite.texture = ImageTexture.create_from_image(image)
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    sprite.centered = false
    sprite.scale = Vector2.ONE * render_scale
    body_origin = -Vector2(float(root_xy[0]), float(root_xy[1])) * render_scale
    sprite.position = body_origin
    add_child(sprite)
    configured = true
    return true

func _process(delta: float) -> void:
    if not configured: return
    age += delta
    flash = move_toward(flash, 0.0, delta * 7.0)
    sync_pose()
    queue_redraw()

func sync_pose() -> void:
    if not configured: return
    # Use bounded rigid-body motion only. No image stretching or cut-up limbs.
    if kind == "hover_machine":
        rotation = clampf(actor.velocity.x / 118.0, -1.0, 1.0) * 0.045
        position.y = sin(age * 2.8) * 3.0
        if actor.health <= 0.0:
            rotation += (0.55 - actor._death_left) * 1.2
            position.y += (0.55 - actor._death_left) * 65.0
    else:
        rotation = 0.0
        position = Vector2.ZERO
    sprite.modulate = Color.WHITE.lerp(Color(1.3,1.15,1.25),actor._hit_flash * 0.4)

func muzzle_world() -> Vector2:
    sync_pose()
    return sprite.to_global(emitter_px)

func fired() -> void:
    flash = 1.0
    queue_redraw()

func hit_rect_world() -> Rect2:
    var shape := Rect2(image_size * Vector2(0.12,0.15), image_size * Vector2(0.76,0.70))
    var bounds := Rect2(sprite.to_global(shape.position),Vector2.ZERO)
    for corner in [shape.position + Vector2(shape.size.x,0), shape.end, shape.position + Vector2(0,shape.size.y)]:
        bounds = bounds.expand(sprite.to_global(corner))
    return bounds

func _draw() -> void:
    if not configured or actor.health <= 0.0: return
    var center := body_origin + emitter_px * render_scale
    var charge := 0.0
    if actor.tactics and actor.tactics.state == "WINDUP":
        charge = clampf(1.0 - actor.tactics.state_left / actor.tactics.state_duration, 0.0, 1.0)
    var radius := 8.0 if kind == "hover_machine" else 26.0
    var power := maxf(flash, charge * 0.5)
    if power > 0.0:
        draw_circle(center, radius * (1.0 + power), Color(0.94,0.25,0.75,power * 0.22))
        draw_arc(center, radius * 1.4, -age, TAU-age, 32, Color(0.8,0.45,1.0,power * 0.75),1.5)

func debug_contract() -> Dictionary:
    return {"kind":kind,"configured":configured,"art_warp":false,
        "gait_claim":false,"emitter_px":emitter_px,"emitter_world":muzzle_world(),
        "native_size":image_size,"display_height":image_size.y * render_scale}

```

## FILE: tests/smoke/site7_machine_source_smoke.gd
SHA256: a606b858eebc272716f9b7d5622939815301f9a1b1c8d31019239e7661d3585d
```text
extends SceneTree
## Source pixel/candidate binding and real projectile-origin tests, not visual PASS.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("run")

func check(value: bool, label: String) -> void:
    checks += 1
    if not value:
        failures.append(label)
        push_error(label)

func run() -> void:
    var specs: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://motion_lab_v1/qa/stage1_enemies_20260913/machine_preview_specs.json"))
    for id in ["ENM_SITE7_DRONE_01","BOSS_SITE7_ANCHOR_01"]:
        var actor := ENEMY.instantiate() as EnemyActor
        actor.configure(id,620.0)
        root.add_child(actor)
        actor.set_physics_process(false)
        check(actor.preview_machine_source(specs[id]),id+" exact candidate binds")
        await process_frame
        await process_frame
        var sprite: Node2D = actor.machine_sprite
        check(is_instance_valid(sprite),id+" raster selected")
        if not is_instance_valid(sprite):continue
        check(not actor._visual_root.visible,id+" previous body hidden")
        check(sprite.sprite.material == null,id+" ImageGen authored materials unchanged")
        actor.rotation=0.13
        actor.scale=Vector2(0.8,1.2)
        for hz in [30,60,120]:
            for i in range(8):
                var dir := Vector2.from_angle(i * PI / 4.0)
                actor.velocity = dir * 118.0
                sprite._process(1.0 / hz)
                var expected: Vector2 = sprite.sprite.to_global(sprite.emitter_px)
                var bounds: Rect2 = sprite.hit_rect_world()
                for point in [Vector2(0.13,0.16),Vector2(0.87,0.16),Vector2(0.87,0.84),Vector2(0.13,0.84)]:
                    check(bounds.has_point(sprite.sprite.to_global(sprite.image_size*point)),"Machine AABB covers transformed native region")
                check(sprite.muzzle_world().distance_to(expected)<0.001,id+" emitter follows visible source transform")
                if id.begins_with("BOSS"):
                    check(sprite.position == Vector2.ZERO and sprite.rotation == 0.0,"Anchor stays anchored")
                var previous := root.get_child_count()
                actor._spawn_projectile(dir)
                check(root.get_child_count() == previous + 1,"One emitter, one projectile")
                var projectile := root.get_child(root.get_child_count()-1) as PrototypeProjectile
                check(projectile.global_position.distance_to(expected)<0.001,"Projectile starts at actual authored iris/orb")
                projectile.free()
        actor.apply_damage(10000.0)
        check(get_nodes_in_group("enemy_death_sequences").is_empty(),"No old SVG death fragments")
        actor.free()
    print("SITE7_MACHINE_SOURCE_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)

```

## FILE: motion_lab_v1/tests/test_cycle_review.py
SHA256: 9e1a18f3362f8e2d3c98f5e6172648b5e54ead5d150fe9e42930dd0307552c3e
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
           'clips':{'walk':{'frames':6},'idle':{'frames':1}},'locomotion':{'walkSpeed':1.35,'walkStride':1.6}}
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
        with self.assertRaisesRegex(ValueError,'distinguish'):
            cycle.validate_video_pixels(str(movie),w.sha(movie),str(path),w.sha(path),json.dumps(self.clip,sort_keys=True),1.35,1.6)

    def test_missing_pilot_blocks_non_e_intake_before_any_source_copy(self):
        source=self.root/'qa/not-read.png';source.write_bytes(b'invalid image proves guard runs first')
        before=(self.root/'art/fixture/SE_walk_0_master.png').read_bytes()
        with self.assertRaisesRegex(ValueError,'E full-cycle review'):
            intake_frame.intake('fixture','SE','walk',0,source)
        self.assertEqual((self.root/'art/fixture/SE_walk_0_master.png').read_bytes(),before)


if __name__=='__main__':unittest.main()

```

## FILE: motion_lab_v1/tests/test_character_workflow.py
SHA256: 01129185113f5bbefb580f9817754ba6a4037ead5222cc53f615b6f2d96c1180
```text
"""Deterministic technical fixtures only; no generated game art or API calls."""
import copy,hashlib,json,math,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
LAB=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LAB))
import character_workflow as workflow
import package_standalone as packager
import new_character
import build_character
import cycle_review
from PIL import Image

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value),encoding='utf-8')

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='workflow_',dir=base))
        assert self.root.resolve().is_relative_to(base.resolve())
        # Preserve tiny test fixtures as evidence; never recursively clean user assets.
        self.patches=[patch.object(module,'ROOT',self.root) for module in [workflow,packager,new_character,build_character]]
        for p in self.patches:p.start();self.addCleanup(p.stop)
        self.art=self.root/'art/fixture';self.art.mkdir(parents=True)
        self.reference=self.art/'identity_reference.png';self.reference.write_bytes(b'technical-identity-fixture')
        self.config=json.loads((LAB/'characters/mica.json').read_text(encoding='utf-8-sig'))
        self.config.update(id='fixture',name='TECHNICAL FIXTURE',source='art/fixture',workflowVersion=1,identityReference='art/fixture/identity_reference.png',referenceSHA256=digest(self.reference),clips={'walk':{'frames':6},'idle':{'frames':1}},annotations={})
        save(self.root/'characters/fixture.json',self.config)
    def populate_sources(self):
        reviews=[]
        for index,(slot,path) in enumerate(workflow.slots(self.config)):
            Image.new('RGBA',(16,24),(30+index,80,150,255)).save(path)
            master=self.art/f'technical_master_{index}.png';master.write_bytes(path.read_bytes())
            returned=str((self.root/f'fake_returned_{index}.png').resolve())
            proof=self.art/f'proof_{index}.json';save(proof,{'tool':'image_gen.imagegen','returnedPath':returned,'result':{'output_hint':'Technical fixture, not a real tool invocation: '+returned},'projectCopy':str(master.relative_to(self.root)),'projectCopySHA256':digest(master)})
            receipt=path.with_suffix('.source.json')
            save(receipt,{'generator':'Codex built-in ImageGen','sha256':digest(path),'destination':str(path.relative_to(self.root)),'toolResponse':workflow.binding(proof),'sourceMaster':workflow.binding(master)})
            reviews.append({'slot':slot,'decision':'approved','sourceSHA256':digest(path),'sourceReceiptSHA256':digest(receipt),'referenceSHA256':self.config['referenceSHA256'],'evidence':workflow.binding(path)})
        save(self.root/'qa/fixture/source_reviews.json',reviews)
        return list(workflow.slots(self.config))
    def browser_report(self):
        test_script=self.root/'public/qa/combat-checks.js';test_script.parent.mkdir(parents=True,exist_ok=True);test_script.write_text('fixture')
        rows=[{'name':f'{mode}_{d}','direction':d,'spriteDirection':d,'pass':True,'heldMouse':True,'shotCount':2,'observedShots':2,'travel':.2,'maxFacingErrorDegrees':0,'convergedShots':2,'maxCursorError':0} for mode in ['mouse','keyboard'] for d in workflow.DIRECTIONS]
        rows.append(dict(rows[0],name='repeat_preserves_mouse'))
        rapid=[dict(name=f'{mode}_{d}',pass_=True,heldMouse=True,locomotionUnchanged=True,oldProjectileVelocityUnchanged=True,immediateErrorDegrees=0,firstFrameErrorDegrees=0,shotErrorDegrees=0,immediateMs=.1,firstFrameMs=16,shotWaitSeconds=.1,eligibleBudgetSeconds=.1,shotCount=1) for mode in ['stationary','moving'] for d in workflow.DIRECTIONS]
        for r in rapid:
            r['pass']=r.pop('pass_');r['travel']=.2 if r['name'].startswith('moving_') else 0
            r.update(initialCooldownSeconds=.1-1/120,initialReloadSeconds=0,initialAmmo=1)
            sector=workflow.DIRECTIONS.index(r['name'].split('_',1)[1])
            r['inputSamples']=[dict(sector=s,offsetMs=.01*i,actorTime=0,actorPosition=[0,0],requestedTarget=[4*math.cos(s*math.pi/4),4*math.sin(s*math.pi/4)],muzzle=[0,0],target=[4*math.cos(s*math.pi/4),4*math.sin(s*math.pi/4)],aim=s*math.pi/4) for i,s in enumerate([(sector+4)%8,(sector+2)%8,sector])]
            r['locomotionBefore']=[0,0,0,0,0,1,.1-1/120,-10,0]
            r['locomotionAfterInput']=r['locomotionBefore'].copy()
            r['oldProjectileSamples']=[dict(index=0,before=[10,0],after=[10,0])]
        return {'kind':'motion-studio-combat-browser','character':'fixture','build':{'inputSHA256':'current'},'testScriptSHA256':digest(test_script),'pass':True,'results':rows,'rapidAim':rapid,'externalResources':[],'viewport':[1920,1080]}
    def test_missing_source_returns_concrete_pilot(self):
        report=workflow.source_status('fixture')
        self.assertFalse(report['ready']);self.assertEqual(report['next']['slot'],'E/idle/0')
    def test_static_walk_cannot_replace_the_required_motion(self):
        self.config['clips']['walk']['frames']=1;save(self.root/'characters/fixture.json',self.config)
        with self.assertRaises(ValueError):workflow.source_status('fixture')
    def test_scaffold_requests_exact_character_slots_without_generation(self):
        save(self.root/'characters/mica.json',self.config)
        for name,run,count in [('newwalk',False,56),('newrun',True,104)]:
            new_character.scaffold(name,name.upper(),self.reference,run)
            recipe=json.loads((self.root/'characters'/f'{name}.json').read_text())
            requests=json.loads((self.root/'art'/name/'requests.json').read_text())
            self.assertEqual(recipe['id'],name);self.assertEqual(recipe['annotations'],{})
            self.assertEqual(recipe['referenceSHA256'],digest(self.reference));self.assertEqual(len(requests),count)
            self.assertTrue(all(r['state']=='NEEDS_IMAGEGEN' and r['destination'].startswith('art/'+name+'/') for r in requests))
            self.assertEqual(recipe['clips']['walk']['phaseStarts'],[0,.2,.33,.5,.7,.83])
    def test_exact_reviewed_inputs_are_ready(self):
        self.populate_sources();self.assertTrue(workflow.source_status('fixture')['ready'])
    def test_delayed_shot_cannot_enlarge_its_own_budget(self):
        report=self.browser_report()
        report['rapidAim'][0].update(shotWaitSeconds=99,eligibleBudgetSeconds=100)
        path=self.root/'qa/browser.json';save(path,report)
        with self.assertRaisesRegex(ValueError,'Self-declared eligibility'):
            workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_summary_booleans_cannot_replace_actual_aim_samples(self):
        for key,value in [('inputSamples',[]),('locomotionAfterInput',[0]*9),
                          ('oldProjectileSamples',[dict(index=0,before=[10,0],after=[0,10])])]:
            report=self.browser_report();report['rapidAim'][0][key]=value
            path=self.root/'qa/browser.json';save(path,report)
            with self.assertRaises(ValueError):
                workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_reversal_labels_cannot_replace_changed_targets(self):
        report=self.browser_report()
        for sample in report['rapidAim'][0]['inputSamples']:
            sample.update(target=[4,0],aim=0)
        path=self.root/'qa/browser.json';save(path,report)
        with self.assertRaisesRegex(ValueError,'requested target'):
            workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_reload_budget_must_match_sampled_actor(self):
        report=self.browser_report();reload=self.config['weapon']['reloadSeconds']
        report['rapidAim'][0].update(initialReloadSeconds=reload,eligibleBudgetSeconds=reload+1/120,shotWaitSeconds=reload)
        path=self.root/'qa/browser.json';save(path,report)
        with self.assertRaisesRegex(ValueError,'sampled actor'):
            workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_source_rejection_cannot_be_cleared_with_new_notes(self):
        self.populate_sources()
        path=dict(workflow.slots(self.config))['E/walk/0']
        evidence=path.relative_to(self.root).as_posix()
        workflow.review_source('fixture','E/walk/0','repair',evidence,'Observed incorrect support leg','technical fixture reviewer')
        with self.assertRaisesRegex(ValueError,'Rejected source bytes'):
            workflow.review_source('fixture','E/walk/0','approved',evidence,'Changed notes, not the art','technical fixture reviewer')
    def test_missing_provenance_cannot_receive_approval(self):
        self.populate_sources()
        path=dict(workflow.slots(self.config))['E/walk/0']
        # Corrupt the tiny owned fixture receipt, leaving its pixel bytes alone.
        save(path.with_suffix('.source.json'),{})
        with self.assertRaisesRegex(ValueError,'provenance/readiness'):
            workflow.review_source('fixture','E/walk/0','approved',path.relative_to(self.root).as_posix(),'Actual fixture test','technical fixture reviewer')
    def test_receipt_only_change_invalidates_source_approval(self):
        self.populate_sources()
        target=dict(workflow.slots(self.config))['E/walk/0']
        receipt=target.with_suffix('.source.json');row=workflow.read(receipt)
        row['provenanceNote']='Changed evidence context';save(receipt,row)
        state=next(r for r in workflow.source_status('fixture')['slots'] if r['slot']=='E/walk/0')
        self.assertEqual(state['state'],'needs_review')
    def test_missing_master_cannot_downgrade_to_original(self):
        self.populate_sources()
        target=dict(workflow.slots(self.config))['E/walk/0']
        receipt=target.with_suffix('.source.json');row=workflow.read(receipt)
        row.pop('sourceMaster');save(receipt,row)
        state=next(r for r in workflow.source_status('fixture')['slots'] if r['slot']=='E/walk/0')
        self.assertEqual(state['state'],'stale_provenance')
    def test_reencoded_rejected_pixels_remain_rejected(self):
        from PIL.PngImagePlugin import PngInfo
        self.populate_sources()
        target=dict(workflow.slots(self.config))['E/walk/0']
        workflow.review_source('fixture','E/walk/0','repair',str(target),'Observed a wrong support foot in synthetic fixture','unit-test')
        before=digest(target)
        image=Image.open(target).copy();info=PngInfo();info.add_text('different-metadata','same actual pixels')
        image.save(target,pnginfo=info)
        self.assertNotEqual(before,digest(target))
        with self.assertRaisesRegex(ValueError,'Rejected source bytes'):
            workflow.review_source('fixture','E/walk/0','approved',str(target),'No pixels changed; this approval must fail','unit-test')
    def test_complete_sources_do_not_bypass_whole_cycle_gate(self):
        self.populate_sources();state=workflow.workflow_status('fixture')
        self.assertTrue(state['sourcesReady']);self.assertFalse(state['ready'])
        self.assertEqual(state['next']['kind'],'cycle-review')
        self.assertEqual(state['next']['direction'],'E')
        with self.assertRaisesRegex(ValueError,'Whole-cycle'):
            build_character.compile_character(self.root/'characters/fixture.json')
    def test_alternate_recipe_cannot_bypass_active_build_gate(self):
        self.populate_sources()
        alternative=copy.deepcopy(self.config);alternative.pop('workflowVersion')
        path=self.root/'qa/alternate.json';save(path,alternative)
        with self.assertRaisesRegex(ValueError,'canonical reviewed'):
            build_character.compile_character(path)
    def test_replacing_source_invalidates_previous_review(self):
        slots=self.populate_sources();slots[0][1].write_bytes(b'changed source')
        report=workflow.source_status('fixture');self.assertFalse(report['ready']);self.assertEqual(report['slots'][0]['state'],'stale_provenance')
    def test_pilot_source_review_precedes_cycle_approval(self):
        self.populate_sources()
        path=self.root/'qa/fixture/source_reviews.json'
        save(path,[r for r in workflow.read(path) if r['slot']!='E/walk/5'])
        state=workflow.workflow_status('fixture')
        self.assertFalse(state['ready'])
        self.assertEqual(state['next']['slot'],'E/walk/5')
    def test_reference_change_invalidates_readiness(self):
        self.populate_sources();self.reference.write_bytes(b'changed identity')
        self.assertFalse(workflow.source_status('fixture')['ready'])
    def test_duplicate_source_cannot_pass_as_a_distinct_phase(self):
        slots=self.populate_sources();slots[1][1].write_bytes(slots[0][1].read_bytes())
        report=workflow.source_status('fixture');self.assertFalse(report['ready']);self.assertIn('same source',report['errors'][0])
    def test_rejected_source_is_retained_and_blocks_build(self):
        slots=self.populate_sources();slot,path=slots[0]
        workflow.review_source('fixture',slot,'repair',str(path),'Fixture rejection, not a real visual review','unit-test')
        self.assertFalse(workflow.source_status('fixture')['ready'])
        self.assertTrue((self.root/'qa/fixture/quarantine'/digest(path)/path.name).exists());self.assertTrue(path.exists())
    def test_changed_tool_response_invalidates_provenance(self):
        self.populate_sources();save(self.art/'proof_0.json',{'changed':True})
        self.assertFalse(workflow.source_status('fixture')['ready'])
    def test_path_escape_and_identity_mismatch_fail(self):
        for value in ['../other','foo/bar','C:\\outside']:
            with self.assertRaises(ValueError):workflow.ident(value)
        self.config['source']='../outside';save(self.root/'characters/fixture.json',self.config)
        with self.assertRaises(ValueError):workflow.recipe('fixture')
    def test_browser_receipt_checks_rows_not_only_pass_label(self):
        report=self.browser_report();path=self.root/'qa/browser.json';save(path,report)
        workflow.check_browser('fixture',str(path),{'inputSHA256':'current'})
        for mutate in [lambda r:r['results'].pop(),lambda r:r['results'][0].update(spriteDirection='W'),lambda r:r['results'][0].update(heldMouse=False),lambda r:r['results'][0].update(observedShots=0),lambda r:r['results'][0].update(convergedShots=0),lambda r:r['results'][0].update(maxCursorError=1),lambda r:r['results'][0].update(maxFacingErrorDegrees=150),lambda r:r['build'].update(inputSHA256='old'),lambda r:r.update(viewport=[1280,720]),lambda r:r.update(externalResources=['https://example.invalid/image.png'])]:
            broken=copy.deepcopy(report);mutate(broken);save(path,broken)
            with self.assertRaises(ValueError):workflow.check_browser('fixture',str(path),{'inputSHA256':'current'})
    def test_bundle_changes_cannot_reuse_a_previous_receipt(self):
        path=self.root/'dist/FIXTURE_Motion_Studio.html';path.parent.mkdir();path.write_text('<html>fixture</html>')
        inputs={'runtime':'abc'};report={'character':'fixture','path':path.relative_to(self.root).as_posix(),'inputs':inputs,'inputSHA256':hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest(),'sha256':digest(path),'bytes':path.stat().st_size}
        save(self.root/'dist/fixture.package.json',report)
        with patch.object(packager,'bundle_inputs',return_value=inputs):
            workflow.check_package('fixture');path.write_text('changed')
            with self.assertRaises(ValueError):workflow.check_package('fixture')
    def test_rapid_aim_gate_rejects_eventual_pass_stale_input_and_homing(self):
        report=self.browser_report();path=self.root/'qa/rapid.json'
        for mutate in [lambda r:r.pop('rapidAim'),lambda r:r['rapidAim'].pop(),lambda r:r['rapidAim'][0].update(immediateErrorDegrees=180),lambda r:r['rapidAim'][0].update(firstFrameErrorDegrees=12),lambda r:r['rapidAim'][0].update(shotWaitSeconds=.5),lambda r:r['rapidAim'][0].update(immediateMs=float('nan')),lambda r:r['rapidAim'][0].update(oldProjectileVelocityUnchanged=False),lambda r:r['rapidAim'][0].update(locomotionUnchanged=False)]:
            broken=copy.deepcopy(report);mutate(broken);save(path,broken)
            with self.assertRaises(ValueError):workflow.check_browser('fixture',str(path),{'inputSHA256':'current'})
    def test_new_recipe_never_overwrites_an_existing_art_folder(self):
        (self.root/'characters/fixture.json').unlink() # owned technical fixture only
        with self.assertRaises(FileExistsError):new_character.scaffold('fixture','Fixture',self.reference)
        self.assertTrue(self.reference.exists())
    def test_incomplete_direction_set_cannot_be_packaged(self):
        save(self.root/'public/assets/atlas/fixture/profile.json',{'id':'fixture','views':{'E':{}},'missingDirections':[]})
        with self.assertRaises(ValueError):packager.bundle_inputs('fixture')
    def fake_build(self,config,direction,action,paths,annotations,output_root=None):
        out=output_root/'public/assets/atlas/fixture';out.mkdir(parents=True,exist_ok=True)
        path=out/f'{direction}_{action}.webp';Image.new('RGBA',(80,120),(30,80,150,255)).save(path,lossless=True)
        return {'image':f'assets/atlas/fixture/{path.name}','cell':[80,120],'frames':1,'columns':1,'height':100,'root':[40,115],'muzzles':[[60,40]],'sources':[{'source':paths[0].relative_to(self.root).as_posix()}]}
    def test_single_frame_imports_produce_their_own_portrait(self):
        self.populate_sources()
        with patch.object(build_character,'build',side_effect=self.fake_build),patch.object(cycle_review,'require_build'):
            build_character.compile_character(self.root/'characters/fixture.json')
        portrait=self.root/'public/assets/atlas/fixture/portrait.png';self.assertTrue(portrait.exists())
        self.assertEqual(Image.open(portrait).getpixel((20,20)),(30,80,150,255))
    def test_failed_and_partial_builds_preserve_the_existing_character(self):
        self.populate_sources();marker=self.root/'public/assets/atlas/fixture/existing.txt';marker.parent.mkdir(parents=True);marker.write_text('keep')
        calls=0
        def fail_late(*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==4:raise ValueError('injected late source failure')
            return self.fake_build(*args,**kwargs)
        with patch.object(build_character,'build',side_effect=fail_late),patch.object(cycle_review,'require_build'):
            with self.assertRaises(ValueError):build_character.compile_character(self.root/'characters/fixture.json')
        self.assertEqual(marker.read_text(),'keep')
        with patch.object(build_character,'build',side_effect=self.fake_build):
            build_character.compile_character(self.root/'characters/fixture.json',partial=True)
        self.assertEqual(marker.read_text(),'keep')

if __name__=='__main__':unittest.main()

```

## FILE: motion_lab_v1/tests/test_enemy_asset_provenance.py
SHA256: b6253cb959b2094ee7bf09ffa911003be66245dea0e1b3d7120362e8379bf5e2
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

## FILE: .agents/skills/sable-character-studio/SKILL.md
SHA256: 5e4887812b7e9c62110e766c049790b55e15ee779ada157de335ccda598c1929
```text
---
name: sable-character-studio
description: Create, repair, or resume SABLE CIRCUIT characters and their eight-direction movement and shooting in the working motion_lab_v1 Motion Studio. Use for MICA, ROOK, ASTER and subsequent characters, including Luna handoffs; not for legacy gate audits or other games.
---

# SABLE character studio

Use the actual implemented Motion Studio, not the retired production harness.
Read `motion_lab_v1/AGENTS.md` and the relevant sections of
`motion_lab_v1/README_KO.md` from the repository root. Run commands from
`motion_lab_v1`. The user's latest instructions take precedence over this skill.

## Choose the work, not a new pipeline

- **Explicit No-Tripo research or pipeline-comparison pilot:** read
  [the evidence-backed comparison route](references/no-tripo-pilot.md). Keep
  candidates isolated; a technical pilot does not authorize production swaps.
- **Movement, aim, firing or input bug:** repair the shared runtime in `public/`.
  `keyboard-input.js` stores physical codes. `combat-aim.js` owns the single aim
  used by facing and projectiles. `simulation.js` drives the actor;
  `atlas-renderer.js` displays the selected authored frame. Do not regenerate art
  or change character speed to hide an input/aim error.
  For slow rapid-turn response, follow [the aim latency contract](references/aim-response.md).
- **New character or source/pose/costume repair:** read
  [the authoring procedure](references/authoring.md). Use recipe data and the
  current per-slot status, not a copy of MICA's pixels or a new bespoke runtime.
- **Browser validation, packaging or handoff:** read
  [the browser procedure](references/browser-check.md). Test actual held firing
  and both mouse/keyboard direction changes, not only the Actor unit test.
- **Skating, fixed legs or legs thrashing during fire:** read
  [the gait repair procedure](references/gait-repair.md). Inspect the selected
  renderer and its actual textures before changing speed or generating art.
- **Any new/changed authored gait or delivery:** use the
  [enforced cycle gate](references/cycle-review.md). `prepare-cycle` creates
  review evidence, never approval. An approved E whole cycle is required before
  expanding sources; all affected cycles and timed runtime observations are
  required before active build and delivery.

## Keep the working invariants

- This six-phase authoring contract is **bipedal**, not a universal monster
  contract. Drones and anchored machines need their actual hover/root/emitter
  evidence; quadrupeds need four named limb chains and their own contact cycle.
  Do not invent foot observations or drop workflowVersion to make them pass.

- Latest directional input wins by default, even during held fire. Key repeat
  must not steal active mouse aim. Body and projectiles share one world-space
  aim. Resolve facing and the illustrated muzzle-to-cursor ray together before
  firing; never recompute a different bullet angle afterwards. Targets inside
  the weapon's reach use forward aim, not a backwards shot through the body.
  Commit pointer aim synchronously and refresh it after camera/pose changes,
  before emission and rendering. Do not couple it to gait or weapon cooldown.
- Visible new/repair artwork comes from built-in ImageGen. Blender/UAL guides
  provide pose/contact only. Keep original sources; inspect identity, anatomical
  left/right feet, weapon continuity and real alpha before accepting a frame.
- Never invent a tool result or visual approval. The workflow checks exact
  hashes and missing/duplicate inputs; it cannot judge anatomy or artistic
  continuity. Record real observations and evidence, not a technical PASS label.
- A saved response plus a source hash is provenance consistency, not provider
  attestation. Bind the actual returned master immediately, retain it, and
  compare allowed derivatives to its pixels. A report's preservation boolean
  cannot replace that comparison. Unverified provenance blocks source approval.
- Modern compiled recipes use `animation.presentation: authored_frames` and
  the shared MICA renderer. Movement and moving fire use the SAME whole-body
  gait phase; stationary recoil never changes the feet. Do not reintroduce
  ASTER's retired `coherent/move` leg-warp bundle or a split upper/lower fallback.
- On failure, use the reported slot/check to repair the smallest affected part.
  Two same-category source failures require inspecting the source/guide/prompt
  and changing the failed approach before another attempt, not an indefinite
  generation loop. Keep failed inputs and their evidence.
- A complete staged build may replace its character's development atlas, with
  the prior atlas preserved. Standalone files/reports are character-specific.
  Do not use `--activate-preview` or touch another character's active preview
  unless that preview switch is part of the user's request. Never deploy as a
  side effect of generating or repairing a character.

## Luna handoff

For character creation/resumption or a Luna handoff, use the
[executable reuse and handoff procedure](references/reuse-improvements.md).
`character_workflow.py handoff --character ID` emits the current reference,
recipe, rejected/missing slots, runnable next commands and dependency hashes.
Verify the packet with `verify-handoff --packet PATH` before using it; rebuild
the packet after source/code/review changes. These commands never generate art
or activate another character. Do not ask Luna to reinvent the renderer.
Repair known rejected slots/cycles first. Establish E idle and the complete E
walk cycle; `review-cycle` must validate its observations before expanding the
requested slots. Runtime rejection takes priority in the handoff even if all
individual source slots have approvals.
Do not silently substitute a different model, start a new user-owned task, or
claim an unperformed Luna reproduction. Model selection or delegation requires
the current user's request to support that action.

The accepted MICA prototype has 48 walk and 8 idle frames. Running reuses walk
cadence unless separate run art is requested and supplied; strafing and reload
hand artwork are not automatically supplied by a controller test. Current
capability and validation results are recorded in
`motion_lab_v1/qa/WORKFLOW_READINESS_2026-09-10.md`.

## External review applied, not universal approval

The user-requested GPT 6 Pro review on 2026-09-13 found concrete provenance,
derivative, cycle-video, aim-report and NPC-warning gaps. Track its actual reply
and remaining work in `qa/stage1_implementation_20260913/`. It did not run the
project, view the art, or approve delivery. READY_TO_RESUME is permission to
resume the named pending step; technical PASS and reviewed delivery are separate.

```

## FILE: .agents/skills/sable-character-studio/references/cycle-review.md
SHA256: 3ee00ae0fc5f6e7988ac0d14cb7d25d763fc91b710661b1d753b63a19f86bd2a
```text
# Enforced whole-cycle review

This is the current repair for the 2026-09-12 ROOK false approval. Run commands
from `motion_lab_v1`. This gate applies to modern `workflowVersion: 1` recipes;
it does not invent historical MICA approvals. Read the actual output of `status`.

## Before expanding beyond E

Finish and review E idle and all six E walk sources. The authoritative phase
vocabulary is `gait_contract.py`: **0 left contact, 1 right swing behind,
2 right passing forward, 3 right contact, 4 left swing behind, 5 left passing
forward**. Anatomical left/right belongs to the character, never the screen.
The same definitions generate new requests and validate cycle observations.
New walk recipes retain the accepted contact-dwell starting schedule; adjust
it only against the observed new stride, not to hide missing poses.

Before another direction or authored run is imported or approved, E walk must
have an exact current whole-cycle approval. All three importers and the source
approval command enforce this. A few approved E poses are insufficient.
Existing non-E files remain preserved; do not regenerate them just to populate
new ledgers. View them and repair only what the actual cycle requires.

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py status --character rook
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py prepare-cycle --character rook --direction E
```

`prepare-cycle` writes a fresh, isolated kit: native 1920×1080 three-loop video,
chronological source sheet, native source pair panels, local video-review HTML,
and **unreviewed** `cycle-observations.json`. The left video panel displays the
compiled cell at 1:1 pixels. The right displays a 270px character over ground
moving at the recipe velocity. This is source-cycle evidence, not the real
game controller. Nothing activates an atlas or sets an approval automatically.

Open the printed actual HTML/video and inspect at normal speed plus sequential
native decoded frames. Follow each actual leg from hip to knee to sole using
its costume/occlusion continuity. Do not assign left/right from the prompt or
move a pouch label mentally to make repeated limbs look like an opposite step.
Inspect all transitions, including 5→0, and ground-relative foot movement.

Fill the printed observation file using actual observations:

- `reviewer` and `decision`; a template remains unreviewed until inspected.
- `legMarkers.left/right`: how each actual anatomical leg was identified.
- Six `frames` in chronological order, with observed `support` and native
  **compiled cell** pixel coordinates for left/right hip, knee and sole.
  Coordinates are local to one 768×768 cell, not the six-cell page or raw master.
- `observations`: opposite contacts, passing/swing, loop seam, sliding, body and
  weapon continuity. Each needs an observed decision, concrete notes and at
  least two increasing video times in seconds. Generic test counts are not observations.

The validator checks exact source/recipe/contract/preview bindings, nonempty
timed observations, visible-pixel landmarks, connected vertical leg order and
opposite leading feet in the direction's projected ground axis. **Landmark labels
and artistic naturalness still need honest visual observation**; passing these
checks does not let a model invent anatomy or promise universal success.

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py review-cycle --character rook --direction E --decision approved --packet 'ACTUAL_PRINTED_OBSERVATION_FILE'
```

On failure, use `--decision repair --evidence ACTUAL_LOCAL_EVIDENCE --reviewer
ACTUAL_REVIEWER --notes ACTUAL_FAILURE` and an explicit `--rejection-scope`.
For `source-art`, repeat `--failed-slot E/walk/4` for the actual failed slots.
Both file and decoded-pixel hashes are retained; changing a good slot or PNG
metadata cannot fix a different rejected slot. For `timing`, `preview`,
`annotation`, or `runtime`, repeat `--required-change ACTUAL_LOCAL_FILE` for
the actual configuration/code/evidence requiring repair. Each named input must
change and a fresh whole-cycle review is still required. Do not regenerate good
art to resolve a video codec, timing, or annotation error. Prior records stay
intact and delivery becomes HOLD; evidence existence is not a visual PASS.

The current gate also recompiles each source into its cell without writing an
active atlas, compares all alpha and visible RGB pixels plus muzzle/clip data,
then checks decoded video panels against the phase schedule with codec tolerance.
RGB stored under alpha=0 is canonicalized because lossless WebP need not retain
invisible color bytes. Neither comparison judges naturalness or anatomical labels.

Use the same procedure for the other directions and for separate run art when
present. `build_character.py` itself refuses an active modern build until all
source and cycle gates pass. Its `--partial` path is still an isolated diagnostic
candidate and does not bypass activation. Do not call the compiler directly to
get around a rejected cycle. Source completeness, active-build readiness and
runtime approval are distinct fields in `status`.

## Actual runtime review

After building, packaging and the existing live browser checks/capture:

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py prepare-runtime-review --character rook --motion-evidence 'ACTUAL_CAPTURE.webm'
```

Fill the returned runtime observation file after reviewing that exact video.
Each direction needs observed foot exchange, sliding and loop continuity for
walk and run, with two real times inside its captured segment. Turning,
speed changes, planted fire and resume also need time-specific observations.
The file identifies the video hash, build and actual reviewer. Pass it through
`review-runtime --observations ACTUAL_FILE` with the other existing arguments.
Final `deliver` revalidates this record and every cycle; a prose-only approval,
stale clip or unresolved visual rejection does not pass.

Handoffs prioritize `REPAIR_RUNTIME_VISUAL` when a runtime rejection exists.
Follow their `nextSource`/cycle command to resolve the source cause. Do not
approve the unchanged package to clear the label. The request to make this
workflow reliable is authorization to repair it, not evidence that the
character or an unperformed Luna run has succeeded.

```

## FILE: .agents/skills/sable-character-studio/references/aim-response.md
SHA256: 802e67cfcdf2eea624f44974d21f52e9dda383c8d16c1c0dbf0b41d56de02f47
```text
# Rapid aim response — observed ROOK repair, 2026-09-13

Preserve user-accepted gait and source bytes when repairing aiming. This is
the shared Motion Studio route, not permission to recreate art or a controller.

## Diagnose the three different clocks

1. Input-to-aim: compare immediately inside the pointer event's turn, before
   waiting for physics or another animation frame. The previous runtime stored
   coordinates only; the next fixed step consumed them about one frame later.
2. Aim-to-visible pose: inspect the FIRST rendered frame and its actual muzzle
   over the current camera, including frames with no fixed physics update.
3. Aim-to-next projectile: inspect the FIRST eligible shot, accounting separately
   for remaining cooldown/reload. ROOK's .42-second interval is not input lag.

Use `applyPointerAim` in `public/combat-aim.js` through `studio.js`'s
`syncPointerAim`. Call it on pointer move/down, after actor/camera updates before
emission, and immediately before combat rendering. Body and projectile share
that solution. Never add aim interpolation, a sample queue, or a gait-clock gate.
Existing bullets keep their original velocity: turning the gun does not home
already-fired projectiles. Do not lower cooldown, increase projectile speed,
drop old bullets, or reset recoil/phase to make this test look responsive.

## Required regression

Follow `browser-check.md`. `runCombatChecks` now produces the original 17 cases
PLUS a mandatory 16-row `rapidAim` matrix: eight directions each stationary and
moving, a multi-sample reversal burst, immediate ray error, first-frame ray
error, first-eligible-shot timing, actual travel and unchanged old velocities.
The real mouse stays held; synthetic DOM events exercise the actual handler.
No ammo refill or weapon-speed override is allowed. Use the bounded free lane.
The synchronous three-sample burst budget is 8.33 ms; the first render must be
observed within 50 ms. Record actual times, not these limits as measurements.
`character_workflow.py` rejects old 17-only reports, stale hashes, eventual-only
success, false movement coverage, delayed shots and non-finite measurements.

The report now retains all three reversal samples, before/after locomotion
state and old projectile velocities. Eligibility is recalculated from the
observed initial ammo/cooldown/reload and current weapon recipe; the reporter
must retain reload in the before/after Actor snapshot. Capture the requested
world target BEFORE dispatching each pointer event; compare that independent
request to the observed target and actor-relative sector. Three changed sector
labels with an unchanged coherent muzzle/target/angle snapshot are not reversals.
Do not force the muzzle angle to equal the sector angle: the muzzle has an offset.
The reporter cannot enlarge its own allowed delay. Old summary-only reports need an actual
rerun, not manually inserted sample arrays. Keep NPC telegraph-locked aim
separate: enemies must not home their announced lunge onto new player input.

Node tests independently cover 30/60/120 Hz reversals, unchanged accepted gait,
ammo/recoil/cadence, latest-sample emission and non-homing flight. Retain the 40
locomotion cases and exact-build native temporal review for delivery. Preserve
prior accepted art/cycle reviews; new runtime bytes need new runtime evidence.

This repair and its tests are reusable by Luna, not an actual Luna reproduction
or a guarantee that every future character will pass without inspection.

```
