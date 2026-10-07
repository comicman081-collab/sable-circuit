# SABLE CIRCUIT Round 10 — only close R9-H01 / R9-H02

R8 boss capture fixes remain unchanged and closed. Please narrowly verify the two actual Python routing defects you reproduced in Round9, not a new architecture audit or art approval.

R9-H01: cycle_followup restricts itself to E/walk if that cycle is needs_cycle_review, stale_cycle_review or repair while all seven E source slots are approved. workflow_status still preserves explicit source repair and incomplete/unreviewed E sources first. Only after E whole-cycle approval do non-E cycle followups resume. Tests cover both pending/stale cases against competing SE repair, E source-art versus timing repair, plus existing approved-E/SE-repair positive controls.

R9-H02: common previewAffectedCycle AND prepareCycleReview commands now carry explicit --action from nextSource.action or its slot. Idle maps to walk. Tests execute the actual character_workflow.main argparse and dispatch with only cycle_preview.prepare artifact creation stubbed, so SE/run really reaches callback with run. Both cycle selection and walk/run/idle source-slot paths are checked. Command-string equality is additional, not the only proof.

Before the fix the new local reproducer showed expected SE/run callback but actual SE/walk; both E pending/stale combinations chose SE repair. The first draft fixture itself lacked a path field; that test-fixture error was corrected before obtaining the intended four failing assertions. No assertion was weakened to turn a wrong selection green. After the fix, the focused 26-test suite passed. Two scope-positive test methods were then added (E repair scope and slot action mapping), and the actual full 105-test run completed OK, attached below. The source-count and decoders are technical fixtures, not a Luna run or artistic result. Skill validation also returned Skill is valid.

Please state whether R9-H01/H02 original counterexamples are closed and whether these narrow changes regress their positive controls. Distinguish your actual execution from our supplied 105-test log. No sprites, recipes, movement speed, weapon numbers, gameplay registry or Godot boss code were changed for these two harness fixes. Separate SE source repair work continues and is NOT submitted for approval here.

## FILE: motion_lab_v1/character_workflow.py
SHA256: 589704da4ee520b8d7c3e2a4eaa35afdab69125aab71b840c5a417d88f0bb7ac
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

def cycle_followup(character, source, cycles):
    """Keep a rejected/complete non-E cycle ahead of unrelated missing views."""
    from cycle_review import ledger
    from source_provenance import pixels
    rows={r['slot']:r for r in source['slots']}
    pilot=next((r for r in cycles['cycles'] if r['direction']=='E' and r['action']=='walk'),None)
    if (pilot and pilot['state'] in ('needs_cycle_review','stale_cycle_review','repair') and
            all(name in rows and rows[name]['state']=='approved' for name in PILOT)):
        # Valid isolated sources cannot substitute for stale/pending E gait evidence.
        cycles={'cycles':[pilot]}
    for cycle in cycles['cycles']:
        if cycle['state']!='repair':continue
        rejection=next((r for r in reversed(ledger(character)) if r['direction']==cycle['direction'] and
                        r['action']==cycle['action'] and r['decision']=='repair'),None)
        if rejection and rejection.get('rejectionScope','source-art')=='source-art':
            old={r['slot']:r for r in rejection['inputs']['sources']}
            for slot in rejection.get('failedSlots',list(old)):
                current=rows.get(slot)
                if not current:continue
                unchanged=current.get('sha256')==old[slot]['sha256']
                if not unchanged and current['state']=='approved' and old[slot].get('pixelSHA256'):
                    unchanged=pixels(local(current['path']))==old[slot]['pixelSHA256']
                if unchanged or current['state']!='approved':
                    return {**current,'kind':'cycle-source-repair','direction':cycle['direction'],
                            'action':cycle['action'],'cycleState':'repair',
                            'reason':rejection.get('notes','Rejected cycle source must be repaired')}
        # Timing/preview/annotation/runtime rejection must not request new art.
        return {'kind':'cycle-review',**cycle,'rejectionScope':rejection.get('rejectionScope') if rejection else None,
                'command':f'character_workflow.py prepare-cycle --character {character} --direction {cycle["direction"]} --action {cycle["action"]}'}
    for cycle in cycles['cycles']:
        if cycle['state'] in ('approved','missing_sources'):continue
        names=[f'{cycle["direction"]}/{cycle["action"]}/{i}' for i in range(6)]
        if cycle['direction']=='E' and cycle['action']=='walk':names+=['E/idle/0']
        if all(name in rows and rows[name]['state']=='approved' for name in names):
            return {'kind':'cycle-review',**cycle,
                    'command':f'character_workflow.py prepare-cycle --character {character} --direction {cycle["direction"]} --action {cycle["action"]}'}
    return None

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
    followup=cycle_followup(character,source,cycles)
    if any(r['state']=='repair' for r in source['slots']):
        pass  # Preserve source_status's explicit failed-slot priority.
    elif isinstance(source['next'],dict) and source['next'].get('slot') in PILOT:
        pass  # An incomplete/unreviewed pilot cannot be skipped for another cycle.
    elif followup:
        result['next']=followup
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

## FILE: motion_lab_v1/character_handoff.py
SHA256: 81d73a7025f5b9b364751553a84c875bcc6b836d86291b334547fda39c2e9bc1
```text
"""Emit exact-byte resume instructions for the existing character workflow.

No provider calls, model switches, generations, reviews, promotion, or scene
changes. A packet is a handoff, never proof of a Luna production run.
"""
from pathlib import Path
import hashlib
import json
import character_workflow as workflow

CORE = ('character_workflow.py', 'character_handoff.py', 'improvement_harness.py', 'compact_atlas.py', 'README_KO.md',
        'gait_contract.py', 'cycle_review.py', 'cycle_preview.py', 'cycle_live_review.js', 'runtime_observations.py', 'source_provenance.py',
        'new_character.py', 'build_character.py', 'build_atlas.py', 'intake_frame.py', 'intake_pair.py', 'preview_gait.py',
        'package_standalone.py', 'validate_character.py', 'intake_derived_frame.py', 'locomotion_review.py', 'motion_evidence.py',
        'public/keyboard-input.js', 'public/combat-aim.js', 'public/simulation.js', 'public/atlas-renderer.js', 'public/studio.js',
        'public/qa/combat-checks.js', 'public/qa/locomotion-checks.js', 'public/qa/capture-motion.js')
REFERENCES = ('SKILL.md', 'references/authoring.md', 'references/gait-repair.md',
              'references/browser-check.md', 'references/reuse-improvements.md', 'references/cycle-review.md',
              'references/aim-response.md', 'references/enemy-facing.md')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fingerprint(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()

def make(character):
    lab = workflow.ROOT.resolve()
    project = lab.parent
    config = workflow.recipe(character)
    status = workflow.workflow_status(character)
    inputs = {}

    def include(path):
        path = path.resolve()
        if path == project or not path.is_relative_to(project):
            raise ValueError('Handoff input must stay in project')
        inputs[path.relative_to(project).as_posix()] = sha(path) if path.is_file() else None

    for name in CORE:
        include(lab / name)
    for name in REFERENCES:
        include(project / '.agents/skills/sable-character-studio' / name)
    include(lab / 'characters' / f'{character}.json')
    include(lab / 'AGENTS.md')
    for path in (lab / 'tests').glob('*'):
        if path.is_file() and (path.suffix == '.py' or path.name.endswith('.test.js')):
            include(path)
    if config.get('identityReference'):
        include(workflow.local(config['identityReference']))
    for row in status['slots']:
        path = workflow.local(row['path'])
        include(path)
        receipt = path.with_suffix('.source.json')
        include(receipt)
        if receipt.is_file():
            source = workflow.read(receipt)
            for key in ('toolResponse', 'sourceMaster'):
                if source.get(key):
                    include(workflow.local(source[key]['path']))
            for key in ('normalization','mask'):
                entry=source.get('derivation',{}).get(key)
                if isinstance(entry,dict) and entry.get('path'):include(workflow.local(entry['path']))
    include(lab / 'art' / character / 'requests.json')
    requests_path=lab / 'art' / character / 'requests.json'
    if requests_path.is_file():
        for request in workflow.read(requests_path):
            if request.get('poseGuide'):include(workflow.local(request['poseGuide']))
    for relative in (f'qa/{character}/source_reviews.json', f'qa/{character}/runtime_reviews.json', f'qa/{character}/cycle_reviews.json',
                     f'dist/{character}.package.json', f'dist/{character}.delivery.json',
                     f'public/assets/atlas/{character}/profile.json'):
        path = workflow.local(relative)
        include(path)
        if path.is_file() and path.name.endswith('_reviews.json'):
            for row in workflow.read(path):
                for key in ('evidence', 'motionEvidence', 'motionCapture', 'locomotion', 'packet','observations'):
                    if isinstance(row.get(key), dict) and row[key].get('path'):
                        bound=workflow.local(row[key]['path']);include(bound)
                        if key=='packet' and bound.is_file():
                            packet=workflow.read(bound)
                            if packet.get('preview'):
                                pp=workflow.local(packet['preview']['path']);include(pp)
                                if pp.is_file():
                                    for evidence_key in ('video','atlas','contact'):
                                        entry=workflow.read(pp).get(evidence_key)
                                        if entry:include(workflow.local(entry['path']))
    profile_path = lab / f'public/assets/atlas/{character}/profile.json'
    if profile_path.is_file():
        profile = workflow.read(profile_path)
        if profile.get('id') != character:
            raise ValueError('Runtime profile identity differs from handoff')
        for view in profile.get('views', {}).values():
            for clip in view.values():
                if isinstance(clip, dict) and clip.get('image'):
                    include(workflow.local('public/' + clip['image']))
                if isinstance(clip, dict):
                    for source in clip.get('sources', []):
                        if source.get('source'):
                            include(workflow.local(source['source']))
        for relative in (f'public/assets/atlas/{character}/portrait.png', 'public/style.css',
                         'public/index.html', 'public/assets/Rajdhani-Medium.ttf'):
            include(workflow.local(relative))
        if profile.get('animation', {}).get('presentation') != 'authored_frames':
            selected = None
            for name in ('coherent', 'fire'):
                possible = workflow.local(f'public/assets/atlas/{character}/{name}/manifest.json')
                include(possible)
                if selected is None and possible.is_file():
                    selected = possible
            if selected:
                for entry in workflow.read(selected).get('directions', {}).values():
                    for key in ('idle','walk','run','move','fire','upper','idleLower','moveLower'):
                        if entry.get(key):
                            include(workflow.local('public/' + entry[key]))
    errors = list(status['errors'])
    if status['mode'] != 'existing-runtime' and status['errors']:
        action = 'REPAIR_SOURCE_STATUS_ERRORS'
    elif status['mode'] == 'existing-runtime':
        action = 'VERIFY_EXISTING_RUNTIME'
    elif status.get('runtimeRepairRequired'):
        action = 'REPAIR_RUNTIME_VISUAL'
    elif any(r['state'] == 'repair' for r in status['slots']):
        action = 'REPAIR_REPORTED_SOURCE'
    elif isinstance(status.get('next'),dict) and status['next'].get('kind')=='cycle-source-repair':
        action = 'REPAIR_REPORTED_CYCLE_SOURCE'
    elif isinstance(status.get('next'),dict) and status['next'].get('kind')=='cycle-review':
        action = 'REVIEW_WHOLE_CYCLE'
    elif status['ready']:
        action = 'BUILD_REVIEWED_SOURCES'
    else:
        action = 'COMPLETE_OR_REVIEW_NEXT_SOURCE'
    candidate = None
    if character == 'rook':
        from improvement_harness import verify_r3
        try:
            candidate = verify_r3(project)
            inputs.update(candidate.pop('inputs'))
        except (ValueError, OSError, KeyError, TypeError) as error:
            candidate = {'status': 'STALE_OR_MISSING_EVIDENCE', 'error': str(error), 'productionPromotion': False}
            errors.append('Frozen R3 reuse evidence is unavailable/stale; do not regenerate retired inputs or claim its old result: ' + str(error))
        weapon_path = project / 'data/progression/weapons.json'
        include(weapon_path)
        if weapon_path.is_file():
            expected = next((row for row in workflow.read(weapon_path)['weapons']
                             if row.get('default_for') == 'CHR_PROTO_02'), None)
            if expected:
                mismatches = {key: {'recipe': config.get('weapon', {}).get(key), 'game': expected[game_key]}
                              for key, game_key in (('magazine','magazine_size'), ('fireInterval','fire_interval'),
                                                    ('reloadSeconds','reload_duration'))
                              if config.get('weapon', {}).get(key) != expected[game_key]}
                if mismatches:
                    errors.append('ROOK art scaffold weapon values differ from the actual game: ' + json.dumps(mismatches))
        errors.append('Before new ROOK HTML gameplay integration, verify movement-unit mapping and scattergun pellet behavior; an art scaffold is not a gameplay parity receipt.')
    ready_core = (all(inputs.get((lab / name).relative_to(project).as_posix()) for name in CORE)
                  and all(inputs.get(('.agents/skills/sable-character-studio/' + name)) for name in REFERENCES))
    if not ready_core:
        errors.append('Required current workflow module missing; repair installation before executing the packet')
    next_source = status.get('next')
    affected_direction = (next_source.get('slot','E/').split('/')[0] if 'slot' in next_source else next_source.get('direction','E')) if isinstance(next_source, dict) else 'E'
    affected_action = (next_source['slot'].split('/')[1] if 'slot' in next_source else next_source.get('action','walk')) if isinstance(next_source,dict) else 'walk'
    if affected_action=='idle':affected_action='walk'
    return {'kind': 'sable-character-handoff', 'schema': 1, 'recordedAt': workflow.stamp(),
            'character': character, 'route': 'motion_lab_v1/authored_frames',
            'status': 'READY_TO_RESUME' if ready_core else 'NEEDS_WORKFLOW_FIX',
            'nextAction': action, 'nextSource': status.get('next'), 'sourceStatus': status,
            'candidateEvidence': candidate, 'warnings': errors,
            'reference': config.get('identityReference'), 'recipe': f'characters/{character}.json',
            'commands': {'status': f'character_workflow.py status --character {character}',
                         'previewAffectedCycle': f'preview_gait.py --character {character} --direction {affected_direction} --action {affected_action}',
                         'prepareCycleReview': f'character_workflow.py prepare-cycle --character {character} --direction {affected_direction} --action {affected_action}',
                         'buildOnlyWhenReady': f'character_workflow.py build --character {character}',
                         'packageAfterBuild': f'package_standalone.py --character {character}',
                         'regressionPython': '-B -m unittest discover -s tests -p test_*.py',
                         'regressionNode': 'node --test tests/*.test.js'},
            'requiredReading': [str(project / '.agents/skills/sable-character-studio' / n) for n in REFERENCES],
            'boundaries': ['This packet authorizes no generation, model switch, delegation or deployment',
                           'Use actual reference and recipe; no copied character pixels or split-leg fallback',
                           'Repair known failures before expanding views; inspect real E idle/opposite contacts and chronological cycle',
                           'Two same-category source failures require changing the failed approach, not blind retries',
                           'Technical fixtures and pinned R3 evidence are NOT Luna production success',
                           'Actual source and native temporal runtime reviews still required for delivery'],
            'lunaGenerationTested': False, 'reviewedDelivery': False,
            'inputs': inputs, 'inputSHA256': fingerprint(inputs)}

def verify(packet_path):
    packet = workflow.read(workflow.local(packet_path))
    if packet.get('kind') != 'sable-character-handoff' or packet.get('schema') != 1:
        raise ValueError('Not a current character handoff')
    if packet.get('inputSHA256') != fingerprint(packet['inputs']):
        raise ValueError('Handoff fingerprint differs')
    project = workflow.ROOT.resolve().parent
    for name, digest in packet['inputs'].items():
        path = (project / name).resolve()
        if path == project or not path.is_relative_to(project):
            raise ValueError('Handoff input escapes project')
        if (sha(path) if path.is_file() else None) != digest:
            raise ValueError('Stale handoff input: ' + name)
    fresh = make(packet['character'])
    if fresh['inputs'] != packet['inputs'] or fresh['sourceStatus'] != packet['sourceStatus']:
        raise ValueError('Source choice or current dependency set changed; recreate handoff')
    for key in ('route','status','nextAction','nextSource','candidateEvidence','warnings','commands',
                'reference','recipe','requiredReading','boundaries','lunaGenerationTested','reviewedDelivery'):
        if packet.get(key) != fresh[key]:
            raise ValueError('Handoff instructions or conclusions were changed: ' + key)
    return {'status': 'CURRENT_HANDOFF', 'character': packet['character'],
            'inputSHA256': packet['inputSHA256'], 'nextAction': fresh['nextAction'],
            'reviewedDelivery': False, 'lunaGenerationTested': False}

```

## FILE: motion_lab_v1/tests/test_reuse_improvements.py
SHA256: 21d4f5112598d2f2149ead987be30c80fafbe21b44557021ae91ad15292cc4b4
```text
"""Local technical fixtures only. No game art, providers, or model runs."""
import copy
import contextlib
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import compact_atlas as atlas
import improvement_harness as harness
import character_handoff as handoff
import character_workflow as workflow

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')

def fixture_root(prefix):
    parent = LAB / 'qa/technical_tests'
    parent.mkdir(parents=True, exist_ok=True)
    # Keep owned fixtures and failed evidence; never recursively clean user data.
    return Path(tempfile.mkdtemp(prefix=prefix, dir=parent))

class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.root = fixture_root('lossless_')
        self.desc_path = self.root / 'descriptor.json'
        self.output = self.root / 'motion_lab_v1/qa/candidate'
        desc = {'cell_size': 4, 'display_scale': .5, 'display_offset': [0, -4],
                'states': {'idle': {'frames': 1, 'fps': 1}, 'move': {'frames': 4, 'fps': 24},
                           'fire': {'frames': 2, 'fps': 12}}, 'directions': {}}
        for direction in atlas.DIRECTIONS:
            row = {'muzzle_xy': [3, 1]}
            for state, spec in desc['states'].items():
                path = self.root / direction / (state + '.png')
                path.parent.mkdir(parents=True, exist_ok=True)
                image = Image.new('RGBA', (4, 4 * spec['frames']))
                for index in range(spec['frames']):
                    # Two visually transparent but byte-distinct cells catch
                    # accidental hidden-RGB normalization and false deduplication.
                    cell = Image.new('RGBA', (4, 4), (20 + 20 * (index % 2), 80, 120, 0))
                    image.paste(cell, (0, index * 4))
                image.save(path)
                row[state + '_atlas'] = path.relative_to(self.root).as_posix()
            desc['directions'][direction] = row
        save(self.desc_path, desc)

    def build(self):
        result = atlas.pack(self.root, self.desc_path, self.output)
        return Path(result['manifest'])

    def test_preserves_all_slots_and_hidden_rgba(self):
        path = self.build()
        result = atlas.verify(self.root, path)
        self.assertEqual(result['rgba_exact_timing_cells'], 56)
        self.assertTrue(result['timing_unchanged'])
        self.assertFalse(result['production_approved'])
        manifest = atlas.read(path)
        self.assertEqual(manifest['directions']['E']['unique_cells'], 2)
        frames = manifest['directions']['E']['states']['move']
        self.assertEqual(len(frames), 4)
        self.assertAlmostEqual(sum(f['duration_seconds'] for f in frames), 4 / 24)
        self.assertEqual(frames[0]['x'], frames[2]['x'])

    def test_changed_duration_or_order_or_offset_fails(self):
        path = self.build()
        original = atlas.read(path)
        for mutate in (
            lambda m: m['directions']['E']['states']['move'][0].update(duration_seconds=.5),
            lambda m: m['directions']['E']['states']['move'][0].update(duration_seconds=math.nan),
            lambda m: m['directions']['E']['states']['move'][0].update(source_frame=1),
            lambda m: m['directions']['E']['states']['move'][0].update(x=999),
            lambda m: m['directions']['E']['states']['move'].pop(),
            lambda m: m.update(display_offset=[0, 0]),
        ):
            broken = copy.deepcopy(original)
            mutate(broken)
            save(path, broken)
            with self.assertRaises(ValueError):
                atlas.verify(self.root, path)

    def test_resealed_pixel_corruption_still_fails_against_original(self):
        path = self.build()
        manifest = atlas.read(path)
        page = self.root / manifest['directions']['E']['texture']
        image = atlas.rgba(page)
        image.putpixel((0, 0), (1, 2, 3, 0))
        image.save(page)
        manifest['directions']['E']['sha256'] = atlas.sha(page)
        save(path, manifest)
        with self.assertRaisesRegex(ValueError, 'RGBA differs'):
            atlas.verify(self.root, path)

    def test_source_change_is_not_accepted_from_old_checks(self):
        path = self.build()
        source = self.root / 'E/move.png'
        Image.new('RGBA', (4, 16), (200, 0, 0, 255)).save(source)
        with self.assertRaisesRegex(ValueError, 'Original texture changed'):
            atlas.verify(self.root, path)

    def test_rgb_without_real_alpha_is_not_silently_converted(self):
        source = self.root / 'E/idle.png'
        Image.new('RGB', (4, 4), (0, 255, 0)).save(source)
        with self.assertRaisesRegex(ValueError, 'actual RGBA'):
            self.build()

    def test_no_overwrite_or_output_escape(self):
        path = self.build()
        before = atlas.sha(path)
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(atlas.sha(path), before)
        with self.assertRaises(ValueError):
            atlas.pack(self.root, self.desc_path, self.root / 'production')
        self.assertFalse((self.root / 'production').exists())

class PerformanceTests(unittest.TestCase):
    def rows(self):
        row = {'p95_ms': 6.424, 'p99_ms': 19.714, 'squad_count': 3, 'end_hostiles': 3}
        return [dict(row) for _ in range(3)]

    def test_r3_relative_failure_cannot_be_rounded_to_pass(self):
        baseline, candidate = self.rows(), self.rows()
        for row in candidate:
            row['p95_ms'] = 7.106
        result = harness.evaluate_performance(baseline, candidate)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(result['absolute_budget_met'])
        self.assertFalse(result['relative_budget_met'])

    def test_valid_within_budget_data_can_pass(self):
        self.assertEqual(harness.evaluate_performance(self.rows(), self.rows())['status'], 'PASS')

    def test_missing_repeat_invalid_number_and_population_fail(self):
        for mutate in (lambda r: r.pop(), lambda r: r[0].update(p95_ms=float('nan')),
                       lambda r: r[0].update(p99_ms=float('inf')), lambda r: r[0].update(p95_ms=True),
                       lambda r: r[0].update(end_hostiles=2), lambda r: r[0].update(p99_ms=1)):
            candidate = self.rows()
            mutate(candidate)
            with self.assertRaises(ValueError):
                harness.evaluate_performance(self.rows(), candidate)

    def test_empty_and_stale_input_binding_fails(self):
        root = fixture_root('binding_')
        path = root / 'file.txt'
        path.write_text('fixture', encoding='utf-8')
        values = {'file.txt': atlas.sha(path)}
        harness.check_bindings(root, values)
        path.write_text('changed', encoding='utf-8')
        for value in ({}, values, {'../outside': 'invalid'}):
            with self.assertRaises(ValueError):
                harness.check_bindings(root, value)

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.project = fixture_root('handoff_')
        self.lab = self.project / 'motion_lab_v1'
        self.lab.mkdir()
        self.patch = patch.object(workflow, 'ROOT', self.lab)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        for name in handoff.CORE + ('AGENTS.md',):
            path = self.lab / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('technical file fixture only', encoding='utf-8')
        for name in handoff.REFERENCES:
            path = self.project / '.agents/skills/sable-character-studio' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('technical instruction fixture only', encoding='utf-8')
        reference = self.lab / 'art/fixture/identity_reference.png'
        reference.parent.mkdir(parents=True)
        reference.write_bytes(b'not image generation: identity hash fixture')
        self.config = {'id': 'fixture', 'name': 'Technical fixture', 'source': 'art/fixture',
                       'heightMetres': 1.72, 'locomotion': {'walkSpeed': 1.35, 'walkStride': 1.6},
                       'workflowVersion': 1, 'identityReference': 'art/fixture/identity_reference.png',
                       'referenceSHA256': atlas.sha(reference), 'clips': {'walk': {'frames': 6}, 'idle': {'frames': 1}}}
        save(self.lab / 'characters/fixture.json', self.config)
        self.packet_path = self.lab / 'qa/handoff.json'

    def packet(self):
        packet = handoff.make('fixture')
        save(self.packet_path, packet)
        return packet

    def test_packet_has_real_next_slot_not_generation_success(self):
        packet = self.packet()
        self.assertEqual(packet['status'], 'READY_TO_RESUME')
        self.assertEqual(packet['nextSource']['slot'], 'E/idle/0')
        self.assertFalse(packet['lunaGenerationTested'])
        self.assertFalse(packet['reviewedDelivery'])
        self.assertEqual(handoff.verify(str(self.packet_path))['status'], 'CURRENT_HANDOFF')

    def test_code_change_invalidates_packet(self):
        self.packet()
        (self.lab / 'public/atlas-renderer.js').write_text('changed fixture', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_new_missing_source_invalidates_packet(self):
        self.packet()
        (self.lab / 'art/fixture/E_walk_0_master.png').write_bytes(b'new test bytes')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_aim_latency_instruction_change_invalidates_packet(self):
        self.packet()
        path=self.project / '.agents/skills/sable-character-studio/references/aim-response.md'
        path.write_text('Changed aim latency constraint fixture',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_runtime_texture_change_invalidates_packet(self):
        texture = self.lab / 'public/assets/atlas/fixture/E_walk.webp'
        texture.parent.mkdir(parents=True)
        texture.write_bytes(b'non-art texture fixture')
        save(texture.parent / 'profile.json', {'id': 'fixture', 'animation': {'presentation': 'authored_frames'},
             'views': {'E': {'walk': {'image': 'assets/atlas/fixture/E_walk.webp', 'sources': []}}}})
        self.packet()
        texture.write_bytes(b'changed texture fixture')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_changed_claim_or_instruction_is_rejected(self):
        original = self.packet()
        for update in ({'reviewedDelivery': True}, {'lunaGenerationTested': True}, {'nextAction': 'DEPLOY_NOW'}):
            packet = copy.deepcopy(original)
            packet.update(update)
            save(self.packet_path, packet)
            with self.assertRaisesRegex(ValueError, 'instructions or conclusions'):
                handoff.verify(str(self.packet_path))

    def test_known_repair_precedes_missing_pilot_slot(self):
        source = self.lab / 'art/fixture/E_walk_0_master.png'
        Image.new('RGBA',(16,24),(90,110,130,255)).save(source)
        master=source.with_name('technical_original.png');master.write_bytes(source.read_bytes())
        proof = self.lab / 'qa/proof.json'
        returned=str(self.lab/'technical_returned.png')
        save(proof, {'tool':'image_gen.imagegen','returnedPath':returned,'result':{'output_hint':'Synthetic test, not a real invocation: '+returned},'projectCopy':str(master.relative_to(self.lab)),'projectCopySHA256':atlas.sha(master)})
        save(source.with_suffix('.source.json'), {'testFixture': True, 'generator': 'Codex built-in ImageGen',
             'sha256': atlas.sha(source), 'toolResponse': workflow.binding(proof),'sourceMaster':workflow.binding(master),'destination':str(source.relative_to(self.lab))})
        workflow.review_source('fixture', 'E/walk/0', 'repair', str(source),
                               'Technical negative fixture, not actual art review', 'unit-test')
        packet = self.packet()
        self.assertEqual(packet['nextAction'], 'REPAIR_REPORTED_SOURCE')
        self.assertEqual(packet['nextSource']['slot'], 'E/walk/0')

    def test_runtime_rejection_is_the_next_action_not_a_rebuild(self):
        save(self.lab/'qa/fixture/runtime_reviews.json',[{'decision':'repair','notes':'Synthetic rejected gait fixture'}])
        packet=self.packet()
        self.assertEqual(packet['nextAction'],'REPAIR_RUNTIME_VISUAL')
        self.assertTrue(packet['sourceStatus']['runtimeRepairRequired'])
        self.assertFalse(packet['sourceStatus']['ready'])

    def pending_cycle_fixture(self, state='repair'):
        rows=[{'slot':f'SE/walk/{i}','path':f'art/fixture/SE_walk_{i}_master.png',
               'state':'approved','sha256':f'old-{i}'} for i in range(6)]
        missing={'slot':'S/walk/0','path':'art/fixture/S_walk_0_master.png','state':'missing'}
        source={'character':'fixture','mode':'source-authoring','ready':False,'next':missing,
                'requiredFrames':56,'approvedFrames':6,'errors':[],'slots':rows+[missing]}
        cycle={'direction':'SE','action':'walk','state':state}
        cycles={'required':True,'ready':False,'cycles':[{'direction':'E','action':'walk','state':'approved'},cycle]}
        rejection={'direction':'SE','action':'walk','decision':'repair','rejectionScope':'source-art',
                   'failedSlots':['SE/walk/3','SE/walk/4'],'inputs':{'sources':rows[:6]},'notes':'Synthetic cycle-only rejection'}
        return source,cycles,rejection

    def test_non_e_cycle_repair_precedes_unrelated_missing_direction(self):
        source,cycles,rejection=self.pending_cycle_fixture()
        with patch.object(workflow,'source_status',return_value=source), \
             patch('cycle_review.status',return_value=cycles),patch('cycle_review.ledger',return_value=[rejection]):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REPAIR_REPORTED_CYCLE_SOURCE')
            self.assertEqual(packet['nextSource']['slot'],'SE/walk/3')
            self.assertIn('--direction SE',packet['commands']['prepareCycleReview'])
            self.assertFalse(packet['reviewedDelivery'])

    def test_complete_non_e_cycle_review_precedes_new_direction(self):
        source,cycles,_=self.pending_cycle_fixture('needs_cycle_review')
        with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')
            self.assertEqual(packet['nextSource']['direction'],'SE')

    def test_unreviewed_pilot_precedes_complete_non_e_cycle(self):
        source,cycles,_=self.pending_cycle_fixture('needs_cycle_review')
        pilot={'slot':'E/walk/5','path':'art/fixture/E_walk_5_master.png','state':'needs_review'}
        source['slots'].append(pilot);source['next']=pilot
        with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
            packet=self.packet()
            self.assertEqual(packet['nextSource']['slot'],'E/walk/5')
            self.assertNotEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')

    def test_e_cycle_recheck_precedes_non_e_cycle_repair(self):
        for state in ['needs_cycle_review','stale_cycle_review']:
            with self.subTest(state=state):
                source,cycles,rejection=self.pending_cycle_fixture()
                source['slots'] += [{'slot':slot,'path':'art/fixture/'+slot.replace('/','_')+'_master.png',
                                     'state':'approved'} for slot in workflow.PILOT]
                cycles['cycles'][0]['state']=state
                with patch.object(workflow,'source_status',return_value=source), \
                     patch('cycle_review.status',return_value=cycles),patch('cycle_review.ledger',return_value=[rejection]):
                    packet=self.packet()
                    self.assertEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')
                    self.assertEqual(packet['nextSource']['direction'],'E')
                    self.assertEqual(packet['nextSource']['action'],'walk')

    def test_cycle_action_reaches_actual_prepare_cli(self):
        import shlex
        self.config['clips']['run']={'frames':6}
        save(self.lab/'characters/fixture.json',self.config)
        for action in ['walk','run']:
            with self.subTest(action=action):
                source,cycles,_=self.pending_cycle_fixture('needs_cycle_review')
                for row in source['slots'][:6]:row['slot']=row['slot'].replace('/walk/','/'+action+'/')
                cycles['cycles'][1]['action']=action
                with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
                    packet=self.packet()
                    self.assertEqual(packet['nextSource']['action'],action)
                    # Execute the real argument parser/branch. Only artifact generation is stubbed.
                    with patch.object(sys,'argv',shlex.split(packet['commands']['prepareCycleReview'])), \
                         patch('cycle_preview.prepare',return_value={'technicalFixture':True}) as prepare, \
                         contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(workflow.main(),0)
                        prepare.assert_called_once_with('fixture','SE',action)
                    self.assertEqual(packet['commands']['prepareCycleReview'],packet['nextSource']['command'])

    def test_e_repair_scope_keeps_its_own_next_action(self):
        for scope in ['source-art','timing']:
            with self.subTest(scope=scope):
                source,cycles,se_rejection=self.pending_cycle_fixture()
                pilot_rows=[{'slot':slot,'path':'art/fixture/'+slot.replace('/','_')+'_master.png',
                             'state':'approved','sha256':'old-'+slot} for slot in workflow.PILOT]
                source['slots']+=pilot_rows;cycles['cycles'][0]['state']='repair'
                e_rejection={'direction':'E','action':'walk','decision':'repair','rejectionScope':scope,
                             'failedSlots':['E/walk/3'],'inputs':{'sources':pilot_rows},'notes':'Synthetic E rejection'}
                with patch.object(workflow,'source_status',return_value=source), \
                     patch('cycle_review.status',return_value=cycles), \
                     patch('cycle_review.ledger',return_value=[e_rejection,se_rejection]):
                    packet=self.packet()
                    self.assertEqual(packet['nextSource']['direction'],'E')
                    if scope=='source-art':
                        self.assertEqual(packet['nextAction'],'REPAIR_REPORTED_CYCLE_SOURCE')
                        self.assertEqual(packet['nextSource']['slot'],'E/walk/3')
                    else:
                        self.assertEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')
                        self.assertNotIn('slot',packet['nextSource'])

    def test_source_slot_action_and_idle_walk_mapping_reach_cli(self):
        import shlex
        self.config['clips']['run']={'frames':6};save(self.lab/'characters/fixture.json',self.config)
        for action in ['walk','run','idle']:
            with self.subTest(action=action):
                source,cycles,_=self.pending_cycle_fixture('approved')
                row={'slot':f'SE/{action}/0','path':f'art/fixture/SE_{action}_0_master.png','state':'needs_review'}
                source['next']=row;source['slots']=[row]
                with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
                    packet=self.packet();expected='walk' if action=='idle' else action
                    self.assertTrue(packet['commands']['previewAffectedCycle'].endswith('--action '+expected))
                    with patch.object(sys,'argv',shlex.split(packet['commands']['prepareCycleReview'])), \
                         patch('cycle_preview.prepare',return_value={'technicalFixture':True}) as prepare, \
                         contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(workflow.main(),0)
                        prepare.assert_called_once_with('fixture','SE',expected)

    def test_non_art_cycle_rejection_does_not_request_new_source(self):
        source,cycles,rejection=self.pending_cycle_fixture()
        rejection['rejectionScope']='timing'
        with patch.object(workflow,'source_status',return_value=source), \
             patch('cycle_review.status',return_value=cycles),patch('cycle_review.ledger',return_value=[rejection]):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')
            self.assertNotIn('slot',packet['nextSource'])
            self.assertEqual(packet['nextSource']['rejectionScope'],'timing')

    def test_direct_source_repair_still_precedes_cycle_review(self):
        source,cycles,_=self.pending_cycle_fixture('needs_cycle_review')
        source['slots'][-1]['state']='repair'
        with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REPAIR_REPORTED_SOURCE')
            self.assertEqual(packet['nextSource']['slot'],'S/walk/0')

    def test_pose_guide_and_request_change_invalidate_handoff(self):
        guide=self.lab/'reference/guide.png';guide.parent.mkdir(parents=True);guide.write_bytes(b'technical pose guide fixture')
        save(self.lab/'art/fixture/requests.json',[{'poseGuide':'reference/guide.png'}])
        self.packet();guide.write_bytes(b'changed guide fixture')
        with self.assertRaisesRegex(ValueError,'Stale handoff'):
            handoff.verify(str(self.packet_path))

if __name__ == '__main__':
    unittest.main()

```

## FILE: .agents/skills/sable-character-studio/references/reuse-improvements.md
SHA256: bf0a68905b296f7220a6ba8e8616fb287c4e272a5b66f8556b6ec4b16992883e
```text
# Executable reuse and Luna handoff

Use the current Motion Studio. This procedure incorporates tested ROOK R3
mechanics without treating its failed high-resolution art or performance as an
approved production recipe. It does not start a model, generation or deployment.

## Resume from actual files

Run from `motion_lab_v1`, using the installed Python below as read-only input.
Create a task-local folder below `qa/`, set TEMP/TMP there, and set
`PYTHONDONTWRITEBYTECODE=1`. No source-art API is called by these commands.

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py handoff --character rook
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py verify-handoff --packet 'ACTUAL_PRINTED_PACKET_PATH'
```

Replace `rook` with the requested existing character, and the packet argument
with the real first command's output. Do not execute the placeholder literally.
The output names a precise failed/review/missing slot, reference, recipe and
existing commands. A packet with `READY_TO_RESUME` is NOT ready for delivery.
Changed source bytes, a newly supplied missing slot, overrides, review evidence,
runtime code or skill instructions invalidate it. Regenerate it after changes.
The harness prioritizes actual `repair` verdicts before producing other views.
This includes cycle-only source rejections outside E: `REPAIR_REPORTED_CYCLE_SOURCE`
names the failed slot even if its isolated source review was approved. After
replacement, finish/review that complete cycle before filling another direction.
Timing/preview/annotation rejections request cycle work, not new source art.
After explicit source repairs and incomplete E sources, an unreviewed/stale
E/walk cycle must be resolved before non-E cycle repairs. Approved E source
images do not preserve a stale E whole-cycle approval. The selected action
also travels through both preview/prepare commands: a separate `run` cycle
must emit `--action run`; an idle source maps to the following walk review.
Regression tests execute the real CLI parser with an artifact-only callback,
not just a string/hash comparison. A self-consistent wrong command can still
pass handoff byte verification, so that alone is not semantic validation.
It now prioritizes a runtime visual rejection even when individual source
slots are approved. Use [the enforced cycle gate](cycle-review.md); exact-byte
handoffs and R3 packing checks never substitute for that cycle approval.

For a genuinely new character, use `new_character.py` with the actual user's
reference first. Its copied camera/gameplay defaults are scaffolding: inspect
the character's real weapon, magazine, cadence and movement units before
integration. In particular ROOK's art scaffold is not its 10-round/.42s/1.38s
game scattergun. The packet flags this known unresolved gap; it does not silently
adjust production Actor values. Never convert another character's pixels into
the new one to make an incomplete source set build.

## Tested mechanics and where they belong

| Mechanic | Reuse location | Boundary |
|---|---|---|
| Shared mouse/key aim and same whole-body movement/fire phase | `public/keyboard-input.js`, `combat-aim.js`, `simulation.js`, `atlas-renderer.js` | Default new-character route; retain existing tests |
| Exact deduplication with explicit cell rectangles and timing aliases | `compact_atlas.py` | Existing vertical RGBA FastRuntime descriptor imports only; not a replacement authored-frame compiler |
| Selected cell committed before synchronous fire; preserved stationary recoil | R3 `pilot_runtime.gd` | Isolated Godot FastRuntime reference; not a browser script or a production-approved replacement |
| Single resident page per direction; candidate chosen before initial load | R3 loader/test scene | Never load old and new textures together in comparison |
| Exclusive bounded batch, code hashes, same scene population | R3 `run_pilot.py` | Capture and benchmark must not overlap; keep all declared repetitions |
| Exact-green normalization with raw-source/tool binding | `normalize_imagegen_chroma.py` + `intake_derived_frame.py` | Deterministic backdrop derivative only; never a new ImageGen claim or anatomy repair |

The frozen R3 runtime uses its original descriptor timing and art. No new
character should copy its ROOK path constants. For a real FastRuntime migration,
make a separate candidate, adapt its exact descriptor/manifest path and rerun
actual runtime/temporal/performance evidence. Do not relabel the old receipt.

Verify the reference before relying on its claims:

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py verify-improvements
```

This independently compares all 272 stored timing cells with the current
original RGBA, verifies pinned evidence/code hashes, and recalculates the
declared 10/11/12 performance repeats. Expected historical result:
`VERIFIED_LIMITED_REUSE`, controller 216/216, temporal 32/32,
**performance FAIL, sourceVisualStatus HOLD, productionPromotion false**.
That successful verification means the limitations were preserved, not waived.
Missing/stale evidence fails closed; never regenerate retired assets just to
make an old reference path exist.

## Optional lossless atlas import

The new project adapter has no provider dependency and never alters its input.
It preserves decoded RGBA including RGB under alpha=0, frame order, durations,
display offsets/scale and muzzle metadata. Verification reads both original
and packed cells; it does not trust an old `checks: PASS` label.

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B compact_atlas.py pack --descriptor '../data/character_pipeline/rook_runtime.json' --output 'qa/atlas_candidates/ACTUAL_NEW_CANDIDATE_NAME'
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B compact_atlas.py verify --manifest 'ACTUAL_PRINTED_MANIFEST_PATH'
```

Use a fresh named candidate path, not the literal placeholder. No automatic
overwrite, cleanup, production pointer change or deployment occurs. The input
must be an existing regular descriptor-sized vertical sheet, not a failed
generated row that is being disguised by equal slicing. Missing/invalid alpha,
rectangles, original hashes, order and timing are errors. Memory estimates are
not GPU measurements. Packing fewer unique cells does not shorten the loop.

## Art and delivery constraints still apply

- Inspect native alpha channels and light/dark edges; painted checkerboard is
  not transparency. Preserve the failed source, then use a separately keyed
  green fallback when needed. Read ImageGen/identity instructions when doing
  actual art work; these harness utilities do not grant a provider switch.
- Trace each leg from hip to boot with that character's own asymmetric markers.
  Guide colors are not clothing. A neutral guide only avoids color copying;
  it does not prove the opposite support or correct foot contact.
- Inspect the compiled chronological cycle as well as isolated originals.
  Different source framing can change body/weapon proportions after normalizing.
  Keep a valid half of a pair via the existing `intake_pair.py --side` mechanism;
  do not approve the failed half with it.
- Distinguish 8x8 dispatch from authored strafe, speed-up walk from authored
  sprint, and ammo/reload logic from reload-hand art. Stationary recoil should
  preserve verified planted feet; do not discard a valid recoil clip merely
  to force an idle frame.
- Follow `authoring.md` and `browser-check.md` for build and delivery. Full
  strides, native 1080p video, selected-renderer evidence and actual visual
  observations remain mandatory. Static/technical tests cannot approve gait.

## Regression commands

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B -m unittest discover -s tests -p 'test_*.py'
node --test tests/*.test.js
```

The new tests exercise corrupt pixels, timing/order changes, missing repeats,
non-finite performance values, stale/tampered handoffs and known-repair priority.
They are local technical fixtures, not a Luna character-generation run. Do not
claim Luna end-to-end success without that separately authorized actual run.

```

## FILE: qa/stage1_implementation_20260913/r10_workflow_regression.stderr.log
SHA256: 945acc3373670d192a1dbfa0c0aa816cb37bc7ec9051c7f610d81da57e9a4246
```text
.........................................................................................................
----------------------------------------------------------------------
Ran 105 tests in 196.860s

OK
OpenCV: FFMPEG: tag 0x30385056/'VP80' is not supported with codec id 139 and format 'webm / WebM'
[mov,mp4,m4a,3gp,3g2,mj2 @ 0000015ded958cc0] moov atom not found

```
