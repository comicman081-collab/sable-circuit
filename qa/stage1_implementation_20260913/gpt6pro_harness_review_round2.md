# GPT 6 Pro review round 2 — implemented subset, not final approval

Round 1 was read in the same user-requested chat. Its original observed text is
retained at motion_lab_v1/qa/stage1_enemies_20260913/cycle_capture/gpt6pro_review_round1.json.

Please review ONLY the actual changed subset below, focusing on new regressions
or insufficient fixes. Do not repeat the whole original report or treat this as
a request for final art/MVP approval. No image/video or Luna validation is claimed.

Implemented and tested:
- prepare_enemy_asset validates project copy path/hash and actual returned path
  in tool output; rejects path-like ids before outputs; code-hash candidate paths
  preserve prior processing versions. This is consistency, not signed attestation.
- Derived normalization now decodes original+output, verifies native RGB size,
  subject existence and exact subject pixels, and recomputes edge-connected mask.
  Four synthetic corruption tests passed.
- Source review refuses unchanged rejected bytes and invalid provenance status.
  intake_frame no longer silently returns a stale source receipt.
- Actual video character-panel pixels are compared to the chronological atlas
  with VP8 tolerance; 1/4 and 2/5 annotated chain repetitions are rejected.
  11 cycle tests passed. This does not yet recompile source->atlas independently.
- Rapid aim rows now retain reversal samples, actor before/after, old velocities,
  initial ammo/reload/cooldown; eligibility is recalculated against the recipe.
  24 workflow tests passed. Live browser recapture is pending.
- NPC roles use explicit current ids; unknown roles stop, not ranged fallback.
- Lunge draw and damage use the same frozen swept capsule, including speed boosts.
  World warnings use top-level identity transform and local shape tests.
  217 actual Godot geometry assertions passed under transformed parents.
- Old duplicate boss volley owner disabled; normal 6-room/10-kill mission was
  rerun to extraction; all three operators survived (4/106/88 HP at boss exit).
- Nonwalking machine source preview: rigid-body hover vs anchored body, emission
  from observed image orb/iris, no old SVG death fragments. 178 Godot checks passed.
  Raster candidates are still isolated and NOT registry-promoted.
- Updated the existing skill narrowly from the actual failures; no new framework.

Still open / intentionally not claimed fixed:
- Complete common response->captured master->derivation->slot provenance validation
  and receipt binding at every current source/delivery consumer.
- Pixel-content rejection hashes, reason-scoped rejection and required affected-slot
  changes; current unchanged-file rejection alone is not a metadata-reencode defense.
- Source->atlas independent recompilation, observation time-category coverage,
  browser 1x/no-seek playback evidence and observed anatomical labels.
- Atomic renderer load / missing modern-presentation fallback and importer two-half
  transaction + delivery invalidation.
- Four-limb motion contract and final enemy cycles, live QA, Stage 1 raster promotion.

Do not recommend changing accepted ASTER/MICA/ROOK appearance, gait or weapon cadence.
Please identify any definite bugs in the changes and give the smallest targeted test.

## FILE: motion_lab_v1/prepare_enemy_asset.py
SHA256: 16b244536edd99537d5a4d72eaf2c2905b875ab4cf695e2bda278fa79d1c07fb
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
    proof=json.loads(response.read_text(encoding='utf-8-sig'))
    result=proof.get('result')
    if proof.get('tool')!='image_gen.imagegen' or not isinstance(result,dict) or not result:
        raise ValueError('Actual ImageGen metadata missing')
    copied=proof.get('projectCopy')
    if not isinstance(copied,str) or (ROOT/copied).resolve()!=source:
        raise ValueError('Tool response must bind this exact project copy')
    if proof.get('projectCopySHA256')!=sha(source):
        raise ValueError('Generated master copy hash does not match tool response')
    returned=proof.get('returnedPath')
    if not isinstance(returned,str) or not returned or not Path(returned).is_absolute():
        raise ValueError('Missing actual returned source path')
    # The saved tool output must identify the same generated file. The source
    # copy remains usable after separately authorized managed-staging cleanup.
    hint=result.get('output_hint','').replace('\\','/')
    if returned.replace('\\','/') not in hint:
        raise ValueError('Returned source path differs from actual tool metadata')
    return proof

def prepare(ident, source, response):
    if not re.fullmatch(r'[a-z0-9_-]+',ident):
        raise ValueError('Use an asset id, not a path')
    source=source.resolve(); response=response.resolve()
    if not source.is_relative_to(ROOT) or not response.is_relative_to(ROOT):
        raise ValueError('Project-local source and actual tool response required')
    verify_source(source,response)
    raw=Image.open(source)
    if max(raw.size)<1024:
        raise ValueError('Native high-resolution generated master required')
    rgba=key_image(source)
    yy,xx=np.where(rgba[:,:,3]>30)
    if not len(xx):
        raise ValueError('Empty separated subject; retain as failed source')
    # Keep previous QA bytes when the preparation implementation changes.
    implementation=sha(Path(__file__))[:8]
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
            'resampling':False,'anatomicalWarp':False,'runtimePromotion':False}
    (out/'preparation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--tool-response',type=Path,required=True)
    a=p.parse_args();prepare(a.id,a.source,a.tool_response)

```

## FILE: motion_lab_v1/intake_derived_frame.py
SHA256: 87a4b94ad56f653d3a7971a6c30d4a6679c59ec38c45e746b0c93f96417eb848
```text
"""Import a deterministic source-art derivative without faking an ImageGen receipt.

The ImageGen result remains the appearance authority.  This importer is for a
project-local, byte-preserving matte normalization (for example, replacing a
near-green exterior with exact ``#00FF00``).  It binds the original generated
master, the untouched tool response, and the normalization report so a
derived frame cannot masquerade as a fresh generation result.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import shutil
import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image

from character_workflow import DIRECTIONS, ROOT, binding, local, recipe, sha, slots, write


GREEN = (0, 255, 0)


def _actual_background(rgb):
    path=Path(__file__).resolve().parents[1]/'tools/character_pipeline/normalize_imagegen_chroma.py'
    spec=importlib.util.spec_from_file_location('sable_chroma_verification',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.edge_connected_background(rgb)[0]


def _path(value: str | Path, label: str) -> Path:
    path = Path(value).resolve()
    if not path.is_file():
        raise ValueError(f"{label} is missing: {path}")
    return path


def _verify_derivative(derived: Path, source_master: Path, tool_response: Path, report: Path, mask: Path) -> dict[str, object]:
    if not source_master.is_relative_to(ROOT):
        raise ValueError("source master must be copied below motion_lab_v1")
    if not tool_response.is_relative_to(ROOT) or not report.is_relative_to(ROOT) or not mask.is_relative_to(ROOT):
        raise ValueError("provenance and QA files must be below motion_lab_v1")
    response = json.loads(tool_response.read_text(encoding="utf-8-sig"))
    if response.get("tool") != "image_gen.imagegen" or not response.get("result"):
        raise ValueError("tool response is not the actual ImageGen response")
    project_copy = response.get("projectCopy")
    if project_copy is None or local(project_copy) != source_master:
        raise ValueError("tool response must bind the project copy of the generated master")
    if response.get("projectCopySHA256") != sha(source_master):
        raise ValueError("generated master copy hash does not match tool response")

    normalize = json.loads(report.read_text(encoding="utf-8-sig"))
    if normalize.get("operation") != "edge-connected green matte normalization only; no source-art redraw":
        raise ValueError("unexpected normalization operation")
    if normalize.get("input_sha256") != sha(source_master):
        raise ValueError("normalization input is not the bound generated master")
    if normalize.get("output_sha256") != sha(derived):
        raise ValueError("normalization output hash is stale")
    if normalize.get("mask_sha256") != sha(mask) or normalize.get("subject_pixels_byte_exact") is not True:
        raise ValueError("normalization mask/report is stale")
    if normalize.get("alpha_ready") is not True:
        raise ValueError("normalization did not produce an alpha-ready source")

    with Image.open(derived) as image:
        image.load()
        if image.mode != "RGB":
            raise ValueError("normalized green source must remain RGB")
        if min(image.size) < 1024:
            raise ValueError("a native high-resolution source is required")
        rgb = np.asarray(image)
    with Image.open(mask) as mask_image:
        mask_image.load()
        mask_array = np.asarray(mask_image.convert("L"))
    if mask_array.shape != rgb.shape[:2] or not set(np.unique(mask_array)).issubset({0, 255}):
        raise ValueError("normalization mask must be native binary")
    with Image.open(source_master) as original:
        original.load()
        if original.mode != 'RGB' or original.size != (rgb.shape[1],rgb.shape[0]):
            raise ValueError('normalization must preserve original RGB mode and dimensions')
        original_rgb=np.asarray(original)
    subject=mask_array==255
    if not subject.any() or not np.array_equal(rgb[subject],original_rgb[subject]):
        raise ValueError('normalization changed protected subject pixels')
    background = mask_array == 0
    if not np.array_equal(background,_actual_background(original_rgb)):
        raise ValueError('normalization mask differs from original edge-connected background')
    if not background.any() or not np.all(rgb[background] == np.asarray(GREEN, dtype=np.uint8)):
        raise ValueError("derived background is not exact uniform green")
    return {
        "toolResponse": binding(tool_response),
        "sourceMaster": binding(source_master),
        "normalization": binding(report),
        "mask": binding(mask),
        "native": [int(rgb.shape[1]), int(rgb.shape[0])],
        "backgroundPixels": int(background.sum()),
    }


def intake(character: str, direction: str, action: str, frame: int, derived: Path, source_master: Path,
           tool_response: Path, report: Path, mask: Path) -> dict[str, object]:
    config = recipe(character)
    if direction not in DIRECTIONS or action not in config["clips"]:
        raise ValueError("invalid recipe slot")
    if not 0 <= frame < config["clips"][action]["frames"]:
        raise ValueError("invalid recipe frame")
    from cycle_review import require_pilot
    require_pilot(character, direction, action)
    source_master = _path(source_master, "source master")
    derived = _path(derived, "derived frame")
    tool_response = _path(tool_response, "tool response")
    report = _path(report, "normalization report")
    mask = _path(mask, "normalization mask")
    provenance = _verify_derivative(derived, source_master, tool_response, report, mask)

    target = dict(slots(config))[(f"{direction}/{action}/{frame}")]
    if target.exists():
        old_hash = sha(target)
        previous = ROOT / "qa" / character / "quarantine" / old_hash
        previous.mkdir(parents=True, exist_ok=True)
        for old in (target, target.with_suffix(".source.json")):
            if old.exists() and not (previous / old.name).exists():
                shutil.copy2(old, previous / old.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(derived, target)
    digest = sha(target)
    if digest != sha(derived):
        raise ValueError("derived frame copy hash mismatch")
    receipt = {
        "generator": "Codex built-in ImageGen",
        "importedUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sha256": digest,
        "native": provenance["native"],
        "destination": target.relative_to(ROOT).as_posix(),
        "toolResponse": provenance["toolResponse"],
        "sourceMaster": provenance["sourceMaster"],
        "derivation": {
            "kind": "edge-connected green matte normalization only; no source-art redraw",
            "normalization": provenance["normalization"],
            "mask": provenance["mask"],
            "resampling": False,
            "anatomicalWarp": False,
            "subjectPixelsByteExact": True,
            "backgroundPixels": provenance["backgroundPixels"],
        },
    }
    write(target.with_suffix(".source.json"), receipt)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--character", required=True)
    parser.add_argument("--direction", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--frame", type=int, required=True)
    parser.add_argument("--derived", required=True)
    parser.add_argument("--source-master", required=True)
    parser.add_argument("--tool-response", required=True)
    parser.add_argument("--normalization-report", required=True)
    parser.add_argument("--mask", required=True)
    args = parser.parse_args()
    print(json.dumps(intake(args.character, args.direction, args.action, args.frame,
                            Path(args.derived), Path(args.source_master), Path(args.tool_response),
                            Path(args.normalization_report), Path(args.mask)), ensure_ascii=False))

```

## FILE: motion_lab_v1/character_workflow.py
SHA256: fec8bc52457eececee51872d6a46989f671b6fb4b28c932047217fa2999f24fa
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
                if r.get('sha256')!=digest or r.get('generator')!='Codex built-in ImageGen' or not binding_valid(r.get('toolResponse')):row['state']='stale_provenance'
                if r.get('sourceMaster') and not binding_valid(r['sourceMaster']):row['state']='stale_provenance'
            if digest in seen:row['state']='duplicate_source';errors.append(f'{name}: same source as {seen[digest]}')
            seen[digest]=name
            current=[r for r in reviews if r['slot']==name]
            if row['state']=='needs_review' and current:
                review=current[-1]
                if review.get('sourceSHA256')==digest and review.get('referenceSHA256')==c['referenceSHA256'] and binding_valid(review.get('evidence')):
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
        if any(r.get('decision')=='repair' and r.get('sourceSHA256')==sha(path) for r in reviews):
            raise ValueError('Rejected source bytes are unchanged; notes cannot repair source art')
        state=next(r['state'] for r in source_status(character)['slots'] if r['slot']==slot)
        if state not in ('needs_review','approved'):
            raise ValueError('Source provenance/readiness must pass before approval: '+state)
    row={'recordedAt':stamp(),'slot':slot,'decision':decision,'reviewer':reviewer,'notes':notes,'sourceSHA256':sha(path),'referenceSHA256':c['referenceSHA256'],'evidence':binding(proof)}
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
        expected_budget=(reload if reload>0 else cooldown+weapon['reloadSeconds'] if ammo==0 else cooldown)+1/120
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
            x,y=(sample['target'][i]-sample['muzzle'][i] for i in (0,1))
            difference=math.atan2(y,x)-angle
            if math.hypot(x,y)<1e-8 or abs(math.atan2(math.sin(difference),math.cos(difference)))>math.radians(1e-5):raise ValueError('A reversal sample used stale aim')
        before,after=row.get('locomotionBefore'),row.get('locomotionAfterInput')
        if (not isinstance(before,list) or len(before)!=8 or before!=after or
                any(type(v) not in (int,float) or not math.isfinite(v) for v in before)):
            raise ValueError('Immediate input changed locomotion or weapon state')
        if before[5]!=ammo or max(0,before[6])!=cooldown:raise ValueError('Initial weapon state differs from sampled actor')
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
    a=p.parse_args()
    try:
        if a.command=='status':result=workflow_status(a.character)
        elif a.command=='prepare-cycle':
            from cycle_preview import prepare
            result=prepare(a.character,a.direction,a.action)
        elif a.command=='review-cycle':
            from cycle_review import record
            result=record(a.character,a.direction,a.action,a.decision,a.packet,a.evidence,a.notes,a.reviewer)
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
SHA256: 5b4e2e7167b980f8706db35c172abb7338ebc08f9e145e3f6e5dd44db1551589
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
            'reviewCodeSHA256': w.sha(Path(__file__)),
            'sources': [dict(slot=name, **w.binding(path)) for name, path in zip(names, files)]}


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def source_content(value):
    return {row['slot']:row['sha256'] for row in value['sources']}


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
        state = 'repair' if source_content(latest['inputs']) == source_content(expected) else 'needs_cycle_review'
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
        atlas=np.asarray(image.convert('RGBA'))
    expected=[]
    for i in range(6):
        rgba=atlas[i//columns*ch:(i//columns+1)*ch,i%columns*cw:(i%columns+1)*cw]
        if rgba.shape!=(ch,cw,4):raise ValueError('Incomplete chronological atlas')
        a=rgba[:,:,3:4].astype(float)/255
        expected.append((rgba[:,:,:3]*a+np.array([16,30,39])*(1-a)).astype(np.float32))
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


def record(character, direction, action, decision, packet_path=None, evidence=None, notes=None, reviewer=None):
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
        rejected_sources = [source_content(r['inputs']) for r in previous
                            if r['direction'] == direction and r['action'] == action and r['decision'] == 'repair']
        if source_content(expected) in rejected_sources:
            raise ValueError('Rejected cycle source bytes are unchanged; metadata edits cannot repair art')
        packet = w.read(w.local(packet_path))
        validate_packet(packet, expected)
        row.update(packet=w.binding(w.local(packet_path)), reviewer=packet['reviewer'])
    else:
        if not notes or not reviewer or not evidence or not w.local(evidence).is_file():
            raise ValueError('Record real rejection observations and evidence')
        row.update(notes=notes, reviewer=reviewer, evidence=w.binding(w.local(evidence)))
    previous.append(row)
    w.write(w.ROOT / 'qa' / character / 'cycle_reviews.json', previous)
    if decision != 'approved':
        w.invalidate_delivery(character, f'Cycle rejected: {direction}/{action}; {notes}')
    return row

```

## FILE: motion_lab_v1/public/qa/combat-checks.js
SHA256: 6ab24ab3b31c816ac5f8a176ae0eac90f753640ddfafd42946da6ac9c918524a
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
  const locomotion=()=>JSON.stringify([d.actor.time,d.actor.phase,d.actor.distance,d.actor.x,d.actor.y,d.actor.ammo,d.actor.cooldown,d.actor.lastShot]);
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
        const budget=(reload>0?reload:d.actor.ammo<=0?cooldown+d.profile.weapon.reloadSeconds:cooldown)+1/120;
        const r=effects.getBoundingClientRect();let screen;const inputSamples=[];
        // Several coalesced-style samples in one event-loop turn: last wins.
        for(const sample of [(dir+4)%8,(dir+2)%8,dir]){
          const a=sample*Math.PI/4;
          screen=d.project(d.actor.x+4*Math.cos(a),d.actor.y+4*Math.sin(a),d.profile.weapon.height);
          effects.dispatchEvent(new PointerEvent('pointermove',{pointerId:1,pointerType:'mouse',clientX:r.left+screen[0],clientY:r.top+screen[1],buttons:1,bubbles:true}));
          inputSamples.push({sector:sample,offsetMs:performance.now()-start,actorTime:d.actor.time,
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
        row.pass=row.heldMouse&&inputError<1e-5&&renderError<1e-5&&shotError<1e-5&&immediateMs<=1000/120&&firstFrameMs<=50&&
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

## FILE: scripts/combat/site7_enemy_tactics.gd
SHA256: bff0483acbbb9792be7fe8d1c7a77d779776626b55d7334c5b21096fc1c947bb
```text
extends Node2D
## Enemy attack controller. Authored art reads these states; it never supplies AI.
const Warning := preload("res://scripts/combat/site7_attack_warning.gd")
const ROLES := {"ENM_SITE7_RIFLE_01":"rifle", "ENM_SITE7_SHIELD_01":"shield",
    "ENM_SITE7_DRONE_01":"drone", "ENM_SITE7_ABERRANT_01":"melee", "BOSS_SITE7_ANCHOR_01":"boss"}
const LUNGE_SPEED := 360.0
const LUNGE_DURATION := 0.42
const LUNGE_RADIUS := 58.0

var actor: EnemyActor
var state := "REPOSITION"
var state_left := 0.7
var state_duration := 0.7
var locked_aim := Vector2.LEFT
var locked_ground := Vector2.LEFT
var burst_left := 0
var burst_clock := 0.0
var phase := 1
var attack_serial := 0
var shots_fired := 0
var lunges := 0
var _struck: Array[int] = []
var _age := 0.0
var _lunge_origin := Vector2.ZERO
var _lunge_reach := 0.0

func _ready() -> void:
    actor = get_parent() as EnemyActor
    top_level = true
    z_index = 1

func _enter(next_state: String, duration: float) -> void:
    state = next_state
    state_left = duration
    state_duration = maxf(duration, 0.001)

func interrupt() -> void:
    burst_left = 0
    _struck.clear()
    _enter("RECOVER", 0.55)

func step(target: OperatorActor, delta: float) -> void:
    global_transform = Transform2D(0.0, actor.global_position)
    var role := str(ROLES.get(actor.enemy_id,""))
    if role.is_empty():
        actor.velocity = Vector2.ZERO
        _enter("UNSUPPORTED_ROLE",1.0)
        return
    _age += delta
    state_left -= delta
    var offset := target.global_position - actor.global_position
    var dist := offset.length()
    var toward := offset.normalized() if dist > 0.01 else Vector2.LEFT
    var aim := (target.get_combat_aim_point() - actor.get_combat_aim_point()).normalized()
    var boss := role == "boss"
    var rifle := role == "rifle"
    var shield := role == "shield"
    var drone := role == "drone"
    var melee := role == "melee"
    phase = 1 if actor.health > actor.max_health * 0.66 else (2 if actor.health > actor.max_health * 0.33 else 3)
    actor.velocity = Vector2.ZERO
    actor._aim_dir = locked_aim if state in ["WINDUP", "BURST", "LUNGE"] else aim
    if state == "REPOSITION":
        if drone:
            var tangent := toward.orthogonal() * actor._orbit_sign
            actor.velocity = (tangent * 0.72 + toward * clampf((dist - 280.0) / 160.0, -0.7, 0.7)).limit_length(1.0) * 118.0
        elif melee:
            actor.velocity = toward * 112.0 if dist > 85.0 else Vector2.ZERO
        elif shield:
            actor.velocity = toward * 62.0 if dist > 190.0 else Vector2.ZERO
        elif rifle:
            var radial := 1.0 if dist > 360.0 else (-0.7 if dist < 220.0 else 0.0)
            actor.velocity = (toward * radial + toward.orthogonal() * actor._orbit_sign * 0.38).limit_length(1.0) * 86.0
        if state_left <= 0.0 and (not melee or dist < 250.0):
            locked_aim = aim
            locked_ground = toward
            _lunge_origin = actor.global_position
            _lunge_reach = LUNGE_SPEED * LUNGE_DURATION * actor.run_speed_multiplier
            actor._aim_dir = locked_aim
            actor.velocity = Vector2.ZERO
            _enter("WINDUP", 0.95 if boss else (0.7 if shield else (0.6 if melee else 0.48)))
    elif state == "WINDUP":
        if state_left <= 0.0:
            attack_serial += 1
            if melee:
                lunges += 1
                _struck.clear()
                _enter("LUNGE", LUNGE_DURATION)
            elif boss:
                _boss_attack(target)
                _enter("RECOVER", (1.8 - float(phase) * 0.20) * actor.run_attack_interval_multiplier)
            else:
                burst_left = 3 if rifle else 1
                burst_clock = 0.0
                _enter("BURST", 0.5)
    elif state == "BURST":
        burst_clock -= delta
        if burst_left > 0 and burst_clock <= 0.0:
            _fire(locked_aim)
            burst_left -= 1
            burst_clock += 0.14
        if burst_left <= 0:
            _enter("RECOVER", (1.4 if shield else 0.85) * actor.run_attack_interval_multiplier)
    elif state == "LUNGE":
        actor.velocity = locked_ground * LUNGE_SPEED
        for victim in get_tree().get_nodes_in_group("operators"):
            if not victim is OperatorActor or victim.is_downed() or _struck.has(victim.get_instance_id()):
                continue
            if lunge_contains(victim.global_position) and actor.global_position.distance_to(victim.global_position) < LUNGE_RADIUS:
                victim.apply_damage(18.0 * actor.run_damage_multiplier)
                _struck.append(victim.get_instance_id())
        if state_left <= 0.0:
            actor.velocity = Vector2.ZERO
            _enter("RECOVER", 1.1 * actor.run_attack_interval_multiplier)
    elif state == "RECOVER":
        if drone:
            actor.velocity = toward.orthogonal() * actor._orbit_sign * 62.0
        if state_left <= 0.0:
            _enter("REPOSITION", 0.9 if not boss else 0.45)
    queue_redraw()

func _fire(direction: Vector2) -> void:
    shots_fired += 1
    CombatFeedback.play_fire(get_tree(), actor.art_profile)
    actor._spawn_projectile(direction)

func _boss_attack(target: OperatorActor) -> void:
    # Slow readable fan in phase one; frozen impact zones in two; cross lanes
    # in three. Large gaps are intentional. These are damaging, not fake decals.
    if phase >= 2 and attack_serial % 2 == 0:
        _warning("circle", target.global_position, Vector2.RIGHT)
        if phase == 3:
            var origin := actor.global_position
            for i in range(4):
                var ray := locked_ground.rotated(float(i) * PI * 0.5)
                _warning("lane", origin + ray * 100.0, ray)
    else:
        var count := 3 if phase == 1 else 5
        for i in range(count):
            _fire(locked_aim.rotated((float(i) - float(count - 1) * 0.5) * 0.22))

func _warning(kind: String, location: Vector2, direction: Vector2) -> void:
    var warning := Warning.new()
    warning.source = actor
    warning.kind = kind
    warning.top_level = true
    warning.ray = direction
    warning.windup = 1.15 if kind == "circle" else 1.35
    warning.damage = 20.0
    actor.get_parent().add_child(warning)
    warning.global_transform = Transform2D(0.0,location)

func lunge_contains(point: Vector2) -> bool:
    var offset := point - _lunge_origin
    var nearest := _lunge_origin + locked_ground * clampf(offset.dot(locked_ground),0.0,_lunge_reach)
    return point.distance_to(nearest) <= LUNGE_RADIUS

func _draw() -> void:
    if not is_instance_valid(actor) or actor.health <= 0.0 or state != "WINDUP":
        return
    var progress := 1.0 - clampf(state_left / state_duration, 0.0, 1.0)
    var color := Color("ef907e", 0.30 + progress * 0.42)
    if "ABERRANT" in actor.enemy_id:
        var base := to_local(_lunge_origin)
        var side := locked_ground.orthogonal() * LUNGE_RADIUS
        var tip := base + locked_ground * _lunge_reach
        draw_colored_polygon(PackedVector2Array([base-side,base+side,tip+side,tip-side]),Color(color,0.12))
        draw_circle(base,LUNGE_RADIUS,Color(color,0.12))
        draw_circle(tip,LUNGE_RADIUS,Color(color,0.12))
        draw_line(base-side,tip-side,color,1.8)
        draw_line(base+side,tip+side,color,1.8)
        var angle := locked_ground.angle()
        draw_arc(base,LUNGE_RADIUS,angle+PI/2,angle+3*PI/2,32,color,1.8)
        draw_arc(tip,LUNGE_RADIUS,angle-PI/2,angle+PI/2,32,color,1.8)
    else:
        var origin := actor.get_combat_aim_point() - actor.global_position
        draw_line(origin + locked_aim * 40.0, origin + locked_aim * 340.0, color, 1.1)
    draw_arc(Vector2(0,6), 23.0, -PI * 0.5, -PI * 0.5 + TAU * progress, 32, color, 2.0)

func contract() -> Dictionary:
    return {"state": state, "state_left": state_left, "locked_aim": locked_aim,
        "phase": phase, "attacks": attack_serial, "shots": shots_fired, "lunges": lunges,
        "contract_is_intent_not_validation":true,
        "role":ROLES.get(actor.enemy_id,"unsupported"),"lunge_radius":LUNGE_RADIUS,"lunge_reach":_lunge_reach}

```

## FILE: scripts/combat/site7_attack_warning.gd
SHA256: a2b237db6016c2dd85ed0c346784723ae53a0bbd1cd81a463291df267a3b4f39
```text
extends Node2D
## A floor warning and its damage share the same frozen geometry and clock.
## No invisible homing: moving out of the marked region always evades the hit.

var source: EnemyActor
var kind := "circle"
var radius := 58.0
var ray := Vector2.RIGHT
var reach := 430.0
var half_width := 16.0
var windup := 1.05
var damage := 16.0
var elapsed := 0.0
var fired := false

func _ready() -> void:
    z_index = -2
    add_to_group("site7_attack_warnings")

func _physics_process(delta: float) -> void:
    if not is_instance_valid(source) or source.health <= 0.0:
        queue_free()
        return
    elapsed += delta
    if elapsed >= windup and not fired:
        fired = true
        for actor in get_tree().get_nodes_in_group("operators"):
            if actor is OperatorActor and not actor.is_downed() and contains(actor.global_position):
                actor.apply_damage(damage * source.run_damage_multiplier)
    if elapsed > windup + 0.26:
        queue_free()
    queue_redraw()

func contains(point: Vector2) -> bool:
    var offset := to_local(point)
    if kind == "circle":
        return offset.length() <= radius
    var forward := offset.dot(ray)
    return forward >= 0.0 and forward <= reach and absf(offset.dot(ray.orthogonal())) <= half_width

func _draw() -> void:
    var progress := clampf(elapsed / windup, 0.0, 1.0)
    var color := Color("f48caa")
    if fired:
        color = Color("eee2ff")
    var fill := Color(color, 0.12 if not fired else 0.36)
    if kind == "circle":
        draw_circle(Vector2.ZERO, radius, fill)
        draw_arc(Vector2.ZERO, radius, 0.0, TAU, 64, Color(color, 0.75), 1.8)
        draw_arc(Vector2.ZERO, radius - 5.0, -PI * 0.5, -PI * 0.5 + TAU * progress, 64, color, 2.4)
        draw_line(Vector2(-7,0), Vector2(7,0), color, 1.3)
        draw_line(Vector2(0,-7), Vector2(0,7), color, 1.3)
    else:
        var side := ray.orthogonal() * half_width
        draw_colored_polygon(PackedVector2Array([-side, side, ray * reach + side, ray * reach - side]), fill)
        draw_line(-side, ray * reach - side, Color(color, 0.8), 1.5)
        draw_line(side, ray * reach + side, Color(color, 0.8), 1.5)
        draw_line(Vector2.ZERO, ray * reach * progress, color, 2.2 if not fired else 6.0)

```

## FILE: scripts/animation/site7_machine_sprite.gd
SHA256: 9430b07fde8d4e1a9965b2afc647fb42ed87ef6a5033e663cfee20fb2e418b44
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
    var origin := sprite.to_global(image_size * Vector2(0.12,0.15))
    return Rect2(origin, image_size * Vector2(0.76,0.70) * render_scale)

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

## FILE: tests/smoke/site7_attack_geometry_smoke.gd
SHA256: 13f823ccb84d07e1b2f7db937a0efd77c25f663c40851af5e60f491cf7548b94
```text
extends SceneTree
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
var checks := 0
var failures: Array[String] = []
func _init() -> void:call_deferred("run")
func check(value: bool, label: String) -> void:
    checks += 1
    if not value:failures.append(label);push_error(label)
func run() -> void:
    var parent := Node2D.new();root.add_child(parent)
    parent.transform = Transform2D(0.7,Vector2(170,-230)).scaled_local(Vector2(1.8,0.7))
    var actor := ENEMY.instantiate() as EnemyActor
    actor.configure("ENM_SITE7_ABERRANT_01",100)
    parent.add_child(actor);actor.set_physics_process(false)
    actor.global_position=Vector2(150,200)
    var victim := OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
    root.add_child(victim);victim.set_physics_process(false)
    victim.global_position=actor.global_position+Vector2(140,0)
    actor.tactics.state_left=0
    actor.tactics.step(victim,1.0/60)
    check(actor.tactics.state=="WINDUP","Actual lunge windup")
    for x in range(-70,230,10):
        for y in [-59.0,-58.0,-40.0,0.0,40.0,58.0,59.0]:
            var point := actor.global_position+Vector2(x,y)
            var axis_x := clampf(float(x),0.0,151.2)
            var expected := Vector2(x-axis_x,y).length() <= 58.0
            check(actor.tactics.lunge_contains(point)==expected,"Warning capsule equals swept damage envelope")
    actor.tactics._warning("lane",Vector2(440,330),Vector2.RIGHT)
    var warning: Node2D = parent.get_child(parent.get_child_count()-1)
    check(warning.global_position.distance_to(Vector2(440,330))<.001,"World warning position under transformed parent")
    check(warning.contains(Vector2(650,340)),"Visible lane interior receives hit")
    check(not warning.contains(Vector2(650,347)),"Visible lane exterior evades")
    parent.rotation += 0.5
    parent.scale *= 1.4
    check(warning.global_position.distance_to(Vector2(440,330))<.001,"Frozen warning survives parent transform")
    check(warning.contains(Vector2(650,340)),"Frozen world geometry preserved")
    actor.enemy_id="QUADRUPED_01"
    actor.tactics.step(victim,1.0)
    check(actor.tactics.state=="UNSUPPORTED_ROLE" and actor.velocity==Vector2.ZERO,"Unknown role cannot become a rifle fallback")
    victim.free();parent.free()
    print("SITE7_ATTACK_GEOMETRY_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)

```

## FILE: motion_lab_v1/tests/test_cycle_review.py
SHA256: f608a5246bd66771d764f7c84259b65261ddf4b2633aa8bb293c4e00047c98d6
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

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import character_workflow as w
import cycle_review as cycle
import gait_contract as contract
import intake_frame


class CycleGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import cv2
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        cls.video_fixture=Path(tempfile.mkdtemp(prefix='cycle_video_',dir=base))/'synthetic_1080p.mp4'
        writer=cv2.VideoWriter(str(cls.video_fixture),cv2.VideoWriter_fourcc(*'mp4v'),30,(1920,1080))
        if not writer.isOpened():raise RuntimeError('Local cycle video encoder unavailable')
        try:
            for i in range(108):
                page=np.full((1080,1920,3),(39,30,16),dtype=np.uint8)
                page[170:938,30:798]=(130,120,90)
                writer.write(page)
        finally:writer.release()

    def setUp(self):
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='cycle_',dir=base))
        for module in (w,intake_frame):
            p=patch.object(module,'ROOT',self.root);p.start();self.addCleanup(p.stop)
        reference=self.root/'art/fixture/identity.png';reference.parent.mkdir(parents=True);reference.write_bytes(b'identity fixture')
        c={'id':'fixture','name':'Fixture','source':'art/fixture','workflowVersion':1,
           'identityReference':'art/fixture/identity.png','referenceSHA256':w.sha(reference),
           'clips':{'walk':{'frames':6},'idle':{'frames':1}},'locomotion':{'walkSpeed':1.35,'walkStride':1.6}}
        w.write(self.root/'characters/fixture.json',c)
        reviews=[]
        proof=self.root/'qa/tool-fixture.json';w.write(proof,{'technicalFixture':True,'notActualToolResponse':True})
        for i,(slot,path) in enumerate(w.slots(c)):
            path.write_bytes(('non-art fixture '+str(i)).encode())
            w.write(path.with_suffix('.source.json'),{'generator':'Codex built-in ImageGen','sha256':w.sha(path),'toolResponse':w.binding(proof)})
            reviews.append({'slot':slot,'decision':'approved','sourceSHA256':w.sha(path),'referenceSHA256':c['referenceSHA256'],'evidence':w.binding(path)})
        w.write(self.root/'qa/fixture/source_reviews.json',reviews)
        self.expected=cycle.inputs('fixture','E')
        self.out=self.root/'qa/cycle';self.out.mkdir(parents=True)
        self.clip={'cell':[768,768],'height':656,'columns':3,'frames':6}
        atlas_path=self.out/'atlas.png';Image.new('RGBA',(2304,1536),(90,120,130,255)).save(atlas_path)
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
        with self.assertRaisesRegex(ValueError,'video pixels'):
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
        (self.root/'art/fixture/E_walk_3_master.png').write_bytes(b'replacement source')
        self.assertNotEqual(cycle.current('fixture','E')['state'],'approved')

    def test_rejected_pixels_cannot_be_reapproved_by_notes(self):
        cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Actual fixture rejection',reviewer='unit fixture')
        with self.assertRaisesRegex(ValueError,'source bytes are unchanged'):
            cycle.record('fixture','E','walk','approved',str(self.packet_path))
        self.assertEqual(w.read(self.root/'dist/fixture.delivery.json')['status'],'HOLD_VISUAL_REPAIR')

    def test_renaming_rejected_sources_does_not_clear_rejection(self):
        cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Synthetic rejection fixture',reviewer='unit fixture')
        for i in range(6):
            path=self.root/f'art/fixture/E_walk_{i}_master.png'
            shutil.copy2(path,path.with_name(f'E_walk_{i}_override.png'))
        self.assertEqual(cycle.current('fixture','E')['state'],'repair')

    def test_missing_pilot_blocks_non_e_intake_before_any_source_copy(self):
        source=self.root/'qa/not-read.png';source.write_bytes(b'invalid image proves guard runs first')
        before=(self.root/'art/fixture/SE_walk_0_master.png').read_bytes()
        with self.assertRaisesRegex(ValueError,'E full-cycle review'):
            intake_frame.intake('fixture','SE','walk',0,source)
        self.assertEqual((self.root/'art/fixture/SE_walk_0_master.png').read_bytes(),before)


if __name__=='__main__':unittest.main()

```

## FILE: motion_lab_v1/tests/test_character_workflow.py
SHA256: 4383feb98d41e1e0016d3a2da22c5c422c4aab29cc696b26d87130a71a4d2131
```text
"""Deterministic technical fixtures only; no generated game art or API calls."""
import copy,hashlib,json,sys,tempfile,unittest
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
            path.write_bytes(('non-art fixture '+str(index)).encode())
            proof=self.art/f'proof_{index}.json';save(proof,{'testFixture':True})
            save(path.with_suffix('.source.json'),{'generator':'Codex built-in ImageGen','sha256':digest(path),'toolResponse':workflow.binding(proof)})
            reviews.append({'slot':slot,'decision':'approved','sourceSHA256':digest(path),'referenceSHA256':self.config['referenceSHA256'],'evidence':workflow.binding(path)})
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
            r['inputSamples']=[dict(sector=s,offsetMs=.01*i,actorTime=0,muzzle=[0,0],target=[1,0],aim=0) for i,s in enumerate([(sector+4)%8,(sector+2)%8,sector])]
            r['locomotionBefore']=[0,0,0,0,0,1,.1-1/120,-10]
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

## FILE: .agents/skills/sable-character-studio/references/gait-repair.md
SHA256: f8b1826fceb2d4c09019db2f3a539c553d7a492ead2bae1aa63710b3e45e69c8
```text
# Diagnose the visible gait, not only actor position

The 2026-09-11 ASTER failure had three independent causes:

- `fullBodyFrame()` handled only `move` as locomotion. Newly added `walk` and
  `run` fell into recoil recovery and returned frame 5 for every phase.
- Firing switched from the new realistic walk art to an unrelated old 24-frame
  raster leg warp. More frame indices did not make that a real walk.
- The input QA ran only short moving-fire cases. Source hashes, distance and a
  static 1080p screenshot all passed while actual walking stayed frozen.

## Repair order

1. Record the selected action/texture and frame index over a complete stride,
   both firing and not firing. Use `atlas-renderer.test.js` and the live
   `motionDebug.current` state. A profile atlas is not evidence if another
   bundle overrides it in `AtlasRenderer.load()`.
2. Check source pixels using `gait_contract.py`: 0/3 opposite contacts,
   1/4 opposite swings behind and 2/5 opposite forward passing poses.
   Follow the anatomical leg by its costume
   marker: ASTER's LEFT white/cyan leg versus RIGHT thigh-pouch leg. Six new
   file hashes or six pictures of the same forward foot fail this check.
3. Preserve the approved whole-body look. For actual missing phases, ImageGen
   may use one native opposite-pose pair at a time: put the corresponding
   `reference/ual_guides/D_walk_pairN.png` first as CAMERA/POSE authority and
   the character's identity reference as APPEARANCE authority. Explicitly
   specify each leg's role in both figures. Inspect before the next attempt.
   A six-figure sheet copied EAST into SE and repeated S support legs; do not
   treat it as success. Use a direction-specific aimed reference if weapon
   foreshortening drifts. Do not fix missing leg poses with a raster warp.
4. A native 1536x1024 pair contains larger figures than a six-cell sheet.
   `intake_pair.py --character ID --direction D --pair N --generated PATH
   --tool-response PROOF` preserves the real master and separates complete
   connected figures without resizing. It imports phases N and N+3, preserves
   previous sources in quarantine and binds the exact tool response. Never
   pad/upscale a small six-cell output and call it a native high-res master.
5. Run `character_workflow.py prepare-cycle --character ID --direction D`.
   Follow [the enforced cycle gate](cycle-review.md). Inspect the generated
   native-scale light/dark pair panels AND the chronological cycle. Record
   `review-source` and the whole-cycle `review-cycle` only after actually viewing that evidence. Observe rifle
   axis/muzzle, identity, contacts, passing knees and alpha. The command does
   not approve or activate anything by itself.

## Source failure patterns actually observed

- **SITE-7 rifle pilot, 2026-09-13:** two opposite-pose pairs repeated the same
  planted right leg. For this repair line use ONE pose per image, the exact
  UAL phase guide FIRST and the appearance reference SECOND. Do not repeat the
  failed pair approach. The right-thigh holster belongs to the anatomical
  right leg; inspect hip-to-boot continuity, not just the pouch location.
  Retain the valid half via `--side` only after viewing it. Existing approved
  pair sources are unaffected. E1/E2 improvements are not an approved cycle.

- A moving seed can preserve the same support leg despite opposite-leg text.
  Use the direction's reviewed planted aimed master to separate camera/weapon
  authority from the phase guide. Mannequin colors are labels, never costume.
- Follow the cyan leg from its anatomical hip through knee to boot. A cyan
  calf or white stripe on the other leg does not repair swapped hips. A third
  leg, missing panel or brown guide material on trousers is a source failure.
- Single portrait replacements can become thinner/longer than adjacent pair
  sources. Compare their normalized chronological cycle, not isolated beauty.
  The square SW replacement improved this observed proportion mismatch.
- When one half of a pair is valid, `intake_pair.py --side 0` or `--side 1`
  can retain just that observed half. The other half remains unapproved; the
  complete native master and failed-half evidence are retained.
- Low toe clearance is distinct from a high marching knee. Inspect the
  actual game-size moving cycle before expanding a pilot to all directions.

## Runtime invariants and evidence

### ROOK source repair findings (2026-09-13)

- ROOK's anatomical RIGHT thigh carries the paired black/gold cylinders; the
  LEFT forearm has the gold support gauntlet. Trace hip, knee and boot separately.
  In rear views right is screen-right; in front views it is screen-left. In
  three-quarter views a lifted boot crossing the silhouette does not change
  its anatomical side. A hidden cylinder alone cannot identify a passing leg.
- A whole moving-body reference repeatedly copied its old support pose into a
  requested opposite phase. Use the approved direction-specific upper-body
  crop as appearance/camera reference and the phase guide for the whole pose.
  This crop is a reference only: every accepted visible frame is newly authored
  whole-body art, never a runtime upper/lower cut-and-paste assembly.
- SW frame 4 and W frame 2 required a second repair after the chronological
  review exposed the wrong support leg. Inspect the actual recompiled frame,
  not the requested pose name or an earlier review packet. New source hashes
  require a fresh preview, annotations and whole-cycle review.
- Put observed hip/knee/sole points on the native compiled cell. If a landmark
  falls outside the silhouette, inspect the native grid before correcting it;
  do not move a point just to satisfy a threshold. State when a joint is partly
  occluded. On-subject points are a diagnostic, not an anatomy PASS.
- Straight front/rear muzzle heuristics can select hair or a hand. Annotate the
  visible muzzle in raw-source pixels per affected slot, then inspect its
  compiled location and live shot. Do not fix a bad socket by moving artwork.
- The cycle preview now uses VP8/WebM. OpenCV decoding of mp4v was insufficient:
  the Chromium review page could not play that codec. Check real browser
  playback at 1x as well as sequentially decoded samples. Preview videos remain
  source diagnostics, not delivered-runtime evidence.

- Preserve the working physical-code input and shared aim solution.
- The generic authored renderer selects walk/run by actual traveled-distance
  phase, independent of shot cadence. Fire applies the existing continuous
  upper-body recoil and uses the same transform for the muzzle. The lower body
  stays on the same gait; at rest it stays on the same planted idle source.
- Keep `runSpeed` and `walkSpeed` independent. Reusing the walk source with a
  faster distance cadence is the accepted MICA prototype capability, NOT a
  separately authored sprint clip. State this limit explicitly.
- Run the 17-case held-mouse input test AND the 40-case temporal locomotion
  test. The latter checks all eight directions for walk, run, moving fire and
  stationary fire, hashes the actual selected lower-body pixels, and rejects
  fixed/duplicate frames. It does not automatically judge anatomy or sliding.
- The report validator now checks chronological frame/phase agreement, increasing
  sample times, measured position deltas, shot counters and, with the current
  profile, phase-to-distance and speed bounds. A six-element set is insufficient.
- Watch native 1080p runtime video spanning complete strides, turns, stopping,
  speed change and fire transitions. Compare visible foot support to ground
  motion, not a speed HUD. A character at the world boundary is not running
  evidence. Still-image review alone cannot authorize `deliver`.
- Cycle validation also compares the decoded native character panel to the
  expected authored atlas phase with codec tolerance. A moving timer or grid
  over a frozen body is not gait evidence. Opposite 1/4 and 2/5 chain checks
  catch repeated annotated poses, but cannot prove that the reviewer labeled
  the actual anatomical legs correctly. Uncertain limbs remain unapproved.
- Do not report a Luna reproduction unless a real authorized Luna run occurred.
  Regression tests prevent the reproduced bugs, not every possible future
  artistic or implementation error.
- `capture-motion.js` saves a sibling JSON binding the actual video hash,
  current build, capture script and time-stamped full cycles/transitions.
  `motion_evidence.py` rejects stale footage and missing phases. Never create
  that metadata by hand to rehabilitate unrelated footage. Review the video
  and its native decoded sequential frames; index-seeking an unindexed WebM
  can silently display a different moment (`inspect_video.py` decodes forward).
- A source or runtime rejection invalidates the current delivery JSON to HOLD
  while preserving its prior receipt. Never leave an older REVIEWED_DELIVERY
  label as the apparent current result of a failed repair.

```

## FILE: .agents/skills/sable-character-studio/references/aim-response.md
SHA256: 5d15e0f7d435e0d5ed670a26476cc173fa3b1887807ed2a17b31bddef385e076
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
cannot enlarge its own allowed delay. Old summary-only reports need an actual
rerun, not manually inserted sample arrays. Keep NPC telegraph-locked aim
separate: enemies must not home their announced lunge onto new player input.

Node tests independently cover 30/60/120 Hz reversals, unchanged accepted gait,
ammo/recoil/cadence, latest-sample emission and non-homing flight. Retain the 40
locomotion cases and exact-build native temporal review for delivery. Preserve
prior accepted art/cycle reviews; new runtime bytes need new runtime evidence.

This repair and its tests are reusable by Luna, not an actual Luna reproduction
or a guarantee that every future character will pass without inspection.

```
