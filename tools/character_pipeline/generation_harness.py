"""Pre-generation/source/mesh/first-pose gates. No generation service is invoked.

ImageGen is probabilistic: this gate cannot guarantee its first output is correct.
It prevents unreviewed source, wrong semantic UVs and bad first poses from being
expanded into animation batches. The final motion harness still owns promotion.
Imports stay stdlib-only until pixel inspection so Blender can verify receipts.
"""
import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/'tools/character_pipeline/generation_contract.json'
# A source-art receipt must bind the code that actually audited that source,
# but must not recursively bind mutable downstream adapter registries.  The
# motion-adapter policy is reviewed and bound later by ``audit_build_plan``.
# Keeping it out of the source receipt also avoids the impossible cycle
# policy -> adapter subject -> source receipt -> policy hash.
SOURCE_AUDIT_CODE=(Path(__file__),CONTRACT)


def local(value):
    p=Path(str(value).removeprefix('res://'))
    p=(p if p.is_absolute() else ROOT/p).resolve()
    if p==ROOT or not p.is_relative_to(ROOT):
        raise ValueError('PROJECT_LOCAL_NON_ROOT_PATH_REQUIRED')
    return p


def read(p):
    def bad(value):
        raise ValueError('NON_FINITE_JSON:'+value)
    data=json.loads(local(p).read_text(encoding='utf-8-sig'),parse_constant=bad)
    if not isinstance(data,dict):
        raise ValueError('JSON_OBJECT_REQUIRED')
    return data


def sha(p):
    return hashlib.sha256(local(p).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def ref(p):
    p=local(p)
    return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}


def resolve(r):
    p=local(r['path'])
    if sha(p)!=r['sha256']:
        raise ValueError('STALE_OR_SWAPPED_INPUT:'+str(p))
    return p


def finite(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError('FINITE_NUMBER_REQUIRED')
    return float(value)


def write(p,data):
    p=local(p)
    if p.exists():
        raise ValueError('RETAIN_EXISTING_EVIDENCE_USE_FRESH_OUTPUT')
    p.parent.mkdir(parents=True,exist_ok=True)
    # Publish a complete file atomically without ever replacing prior evidence.
    # link() fails if another process has already claimed this output name.
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=p.parent,
                                     prefix='.'+p.name+'.',suffix='.pending',delete=False) as out:
        temporary=Path(out.name)
        out.write(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
        out.flush(); os.fsync(out.fileno())
    try:
        os.link(temporary,p)
    finally:
        temporary.unlink()


def pixels(p):
    import numpy as np
    try:
        from PIL import Image
    except ImportError:
        # Blender ships numpy but not necessarily Pillow. Read the actual image
        # through its native decoder, with unmodified non-color sample values.
        import bpy
        image=bpy.data.images.load(str(local(p)),check_existing=False)
        try:
            image.colorspace_settings.name='Non-Color'
            w,h=image.size
            values=np.array(image.pixels[:],dtype=np.float32).reshape(h,w,4)
            return np.flipud(np.rint(values*255).clip(0,255).astype(np.uint8)).copy()
        finally:
            bpy.data.images.remove(image)
    else:
        with Image.open(local(p)) as image:
            image.load()
            return np.asarray(image.convert('RGBA')).copy()


def green(image):
    import numpy as np
    rgb=image[...,:3].astype(np.float32)
    return (rgb[...,1]>rgb[...,0]*1.35)&(rgb[...,1]>rgb[...,2]*1.35)&(rgb[...,1]>60)


def audit_native_alpha(image):
    """Actual decoded alpha, not a filename/prompt or painted checkerboard.

    This establishes usable transparency only. Hair loss, halos and holes still
    require original-scale visual review on light and dark backgrounds.
    """
    import numpy as np
    alpha=image[...,3]; errors=[]
    if not np.any(alpha==0) or not np.any(alpha==255):
        errors.append('REAL_ZERO_AND_OPAQUE_ALPHA_REQUIRED')
    border=read(CONTRACT)['source']['alpha_clear_border_pixels']
    if (alpha[:border].any() or alpha[-border:].any() or
            alpha[:,:border].any() or alpha[:,-border:].any()):
        errors.append('ALPHA_BACKGROUND_NOT_CLEAR_AT_BORDER')
    if np.count_nonzero(alpha==0)/alpha.size<.01:
        errors.append('INSUFFICIENT_TRANSPARENT_BACKGROUND')
    if np.count_nonzero(alpha>=250)/alpha.size<.01:
        errors.append('MISSING_OPAQUE_SUBJECT')
    return {'errors':errors,'native_size':[image.shape[1],image.shape[0]],
            'alpha_min':int(alpha.min()),'alpha_max':int(alpha.max()),
            'transparent_pixels':int(np.count_nonzero(alpha==0)),
            'partial_alpha_pixels':int(np.count_nonzero((alpha>0)&(alpha<255))),
            'opaque_pixels':int(np.count_nonzero(alpha==255)),
            'verdict':'FAIL' if errors else 'HOLD_ALPHA_VISUAL_REVIEW'}


def audit_request(path):
    data=read(path)
    errors=[]
    if type(data.get('qa_fixture_only',False)) is not bool:
        errors.append('QA_FIXTURE_FLAG_MUST_BE_BOOLEAN')
    if data.get('schema')!=1 or data.get('generator')!='built_in_ImageGen':
        errors.append('BUILT_IN_IMAGEGEN_REQUEST_REQUIRED')
    if not data.get('actor_id') or not data.get('costume_id'):
        errors.append('IDENTITY_CONTRACT_REQUIRED')
    if data.get('max_unreviewed_outputs')!=1:
        errors.append('ONE_UNREVIEWED_PROBE_ONLY')
    output=local(data.get('output_root','artifacts/invalid'))
    if not output.is_relative_to(ROOT/'art_src/characters'):
        errors.append('PROJECT_CHARACTER_SOURCE_DESTINATION_REQUIRED')
    refs=data.get('references',[])
    if not refs or not any(r.get('role')=='identity_authority' for r in refs):
        errors.append('HASHED_IDENTITY_AUTHORITY_REQUIRED')
    for r in refs:
        resolve(r)
    implementation=data.get('implementation',[])
    if not implementation:
        errors.append('CONSUMING_GENERATOR_BINDINGS_REQUIRED')
    for r in implementation:
        resolve(r)
    views=data.get('views',[])
    if not views or len({v['id'] for v in views})!=len(views):
        errors.append('UNIQUE_EXPECTED_VIEWS_REQUIRED')
    for v in views:
        if v.get('projection')!='orthographic' or v.get('body_facing')!=v.get('id'):
            errors.append(v['id']+':WHOLE_BODY_DIRECTION_REQUIRED_NOT_GUN_ONLY')
        if v.get('pose') not in ('neutral_combat','neutral_rig'):
            errors.append(v['id']+':SINGLE_NEUTRAL_POSE_REQUIRED_BEFORE_GAIT')
        if len(v.get('minimum_canvas',[]))!=2 or min(map(finite,v['minimum_canvas']))<1024:
            errors.append(v['id']+':EXPLICIT_NATIVE_SOURCE_FLOOR_REQUIRED')
        if not v.get('regions'):
            errors.append(v['id']+':TEXTURE_OR_UPPER_REGION_PURPOSE_REQUIRED')
    if data.get('background') not in ('uniform_chroma_green','transparent_alpha'):
        errors.append('EXPLICIT_CHROMA_OR_NATIVE_ALPHA_BACKGROUND_REQUIRED')
    previous_attempt = data.get('previous_attempt')
    if previous_attempt:
        previous = read(resolve(previous_attempt))
        if previous.get('verdict') not in ('FAIL', 'REJECTED') or not previous.get('errors'):
            errors.append('PREVIOUS_ATTEMPT_MUST_BE_REVIEWED_BEFORE_RETRY')
        if (previous.get('actor_id') != data.get('actor_id') or
                previous.get('costume_id') != data.get('costume_id')):
            errors.append('PREVIOUS_ATTEMPT_IDENTITY_MISMATCH')
        # A painted checkerboard is an observed failure of the requested alpha
        # mechanism.  A renamed request must not turn it into another alpha
        # retry.  An independent reviewer has to bind the exact failed attempt
        # and state that the green master is the changed mechanism.
        if previous.get('category') == 'native_alpha_response':
            if data.get('background') != 'uniform_chroma_green':
                errors.append('NATIVE_ALPHA_FAILURE_REQUIRES_CHROMA_FALLBACK')
            review_ref = data.get('previous_failure_review')
            if not review_ref:
                errors.append('NATIVE_ALPHA_FAILURE_REQUIRES_INDEPENDENT_CAUSE_REVIEW')
            else:
                review = read(resolve(review_ref))
                if (review.get('stage') != 'independent_failure_cause_review' or
                        review.get('failure_attempt') != previous_attempt or
                        review.get('verdict') != 'PASS_CHROMA_GREEN_FALLBACK' or
                        not review.get('reviewer')):
                    errors.append('INVALID_NATIVE_ALPHA_FAILURE_REVIEW')
                checks = review.get('checks', {})
                required = ('failure_reproduced', 'transparent_alpha_retry_prohibited',
                            'uniform_chroma_green_changed_mechanism')
                if any(checks.get(key) != 'PASS' for key in required):
                    errors.append('INCOMPLETE_NATIVE_ALPHA_FAILURE_REVIEW')
    prompt=resolve(data['prompt'])
    if not prompt.read_text(encoding='utf-8').strip():
        errors.append('EMPTY_IMAGEGEN_PROMPT')
    return {'stage':'request','verdict':'FAIL' if errors else 'PASS_REQUEST_ONLY',
            'errors':sorted(set(errors)),'request':ref(path),
            'note':'Allows one source attempt only; not source/visual PASS.'}


def source_bindings(path):
    data=read(path)
    refs=[ref(path),data['request']]
    request=read(resolve(data['request']))
    refs.extend(request['references']); refs.append(request['prompt'])
    refs.extend(request.get('implementation',[]))
    refs.append(data['attempt_permit'])
    for view in data.get('views',[]):
        refs.extend([view['image'],view['annotations']])
    for region in data.get('regions',[]):
        refs.append(region['mask'])
        refs.extend(region.get('exclusions',[]))
    normalization=data.get('matte_normalization')
    if normalization:
        refs.extend([normalization['raw_image'],normalization['normalized_master'],
                     normalization['background_mask'],normalization['normalization_qa'],
                     normalization['normalizer']])
    refs.extend(ref(p) for p in SOURCE_AUDIT_CODE)
    files={}
    for r in refs:
        p=resolve(r); files[p.relative_to(ROOT).as_posix()]=sha(p)
    return files


def audit_source(path):
    import numpy as np
    data=read(path); contract=read(CONTRACT)['source']
    request=read(resolve(data['request']))
    errors=audit_request(resolve(data['request']))['errors'][:]
    permit=read(resolve(data['attempt_permit']))
    if permit.get('verdict')!='RESERVED_SINGLE_SOURCE_ATTEMPT' or permit.get('request')!=data['request']:
        errors.append('SOURCE_HAS_NO_MATCHING_PRE_GENERATION_PERMIT')
    if len({v['image']['sha256'] for v in data.get('views',[])})!=1:
        errors.append('UNREVIEWED_MULTI_OUTPUT_EXPANSION')
    bindings=source_bindings(path)
    if data.get('actor_id')!=request.get('actor_id') or data.get('costume_id')!=request.get('costume_id'):
        errors.append('SOURCE_IDENTITY_MISMATCH')
    if data.get('source_author')!='built_in_ImageGen':
        errors.append('SOURCE_AUTHOR_MISMATCH')
    wanted={v['id']:v for v in request['views']}
    observed={v['id']:v for v in data.get('views',[])}
    normalization=data.get('matte_normalization')
    normalized_master=None
    if normalization:
        try:
            normalized_master=normalization['normalized_master']
            raw_image=normalization['raw_image']
            background_mask=normalization['background_mask']
            normalization_qa=read(resolve(normalization['normalization_qa']))
            normalizer=resolve(normalization['normalizer'])
            if normalizer != ROOT/'tools/character_pipeline/normalize_imagegen_chroma.py':
                errors.append('UNSUPPORTED_MATTE_NORMALIZER')
            if (normalization_qa.get('input') != raw_image['path'] or
                    normalization_qa.get('input_sha256') != raw_image['sha256'] or
                    normalization_qa.get('output') != normalized_master['path'] or
                    normalization_qa.get('output_sha256') != normalized_master['sha256'] or
                    normalization_qa.get('mask') != background_mask['path'] or
                    normalization_qa.get('mask_sha256') != background_mask['sha256'] or
                    normalization_qa.get('subject_pixels_byte_exact') is not True):
                errors.append('INVALID_MATTE_NORMALIZATION_BINDING')
        except (KeyError, ValueError, OSError):
            errors.append('INVALID_MATTE_NORMALIZATION_BINDING')
    if set(wanted)!=set(observed) or len(observed)!=len(data.get('views',[])):
        errors.append('SOURCE_VIEW_COVERAGE')
    heights=[]; images={}
    for direction,view in observed.items():
        image=pixels(resolve(view['image'])); images[direction]=image
        h,w=image.shape[:2]
        spec=wanted.get(direction,{})
        if normalization and (len(observed) != 1 or view['image'] != normalized_master):
            errors.append(direction+':MATTE_NORMALIZED_MASTER_MISMATCH')
        if normalization:
            matte=pixels(resolve(normalization['background_mask']))
            if matte.shape[:2] != image.shape[:2]:
                errors.append(direction+':MATTE_NORMALIZATION_MASK_DIMENSIONS')
            else:
                matte_background=matte[...,0] < 128
                if not matte_background.any() or not np.all(image[matte_background,:3] == [0,255,0]):
                    errors.append(direction+':MATTE_NORMALIZATION_NOT_EXACT_GREEN')
        minimum=spec.get('minimum_canvas',[1024,1536])
        if w<minimum[0] or h<minimum[1] or view.get('native_size')!=[w,h]:
            errors.append(direction+':SOURCE_NATIVE_RESOLUTION')
        annotation=read(resolve(view['annotations']))
        if annotation.get('image_sha256')!=view['image']['sha256']:
            errors.append(direction+':STALE_SOURCE_LANDMARKS')
        if annotation.get('body_facing')!=direction:
            errors.append(direction+':BODY_FACING_NOT_GUN_FACING')
        x,y,pw,ph=view['panel']
        if any(isinstance(a,bool) or not isinstance(a,int) for a in (x,y,pw,ph)) or x<0 or y<0 or pw<1 or ph<1 or x+pw>w or y+ph>h:
            raise ValueError('INVALID_SOURCE_PANEL')
        panel_image=image[y:y+ph,x:x+pw]
        if request.get('background')=='transparent_alpha':
            errors.extend(direction+':'+e for e in audit_native_alpha(panel_image)['errors'])
            foreground=panel_image[...,3]>127
        else:
            foreground=(~green(panel_image))&(panel_image[...,3]>127)
        yy,xx=np.where(foreground)
        if len(yy)==0:
            errors.append(direction+':EMPTY_SOURCE'); continue
        native_height=int(yy.max()-yy.min()+1)
        if native_height<contract['min_subject_pixels']:
            errors.append(direction+':INSUFFICIENT_NATIVE_SUBJECT_DETAIL')
        if xx.min()==0 or xx.max()==pw-1 or yy.min()==0 or yy.max()==ph-1:
            errors.append(direction+':CLIPPED_SOURCE_SILHOUETTE')
        points=annotation.get('points',{})
        for key in ('head_top','ground','hip_left','hip_right','shoulder_left','shoulder_right','heel_left','heel_right','toe_left','toe_right'):
            if key not in points or len(points[key])!=2:
                errors.append(direction+':MISSING_LANDMARK:'+key)
        if any(k not in points for k in ('head_top','ground','hip_left','hip_right','shoulder_left','shoulder_right','heel_left','heel_right','toe_left','toe_right')):
            continue
        for point in points.values():
            if len(point)!=2 or not (0<=finite(point[0])<w and 0<=finite(point[1])<h):
                raise ValueError('LANDMARK_OUTSIDE_IMAGE')
        height=math.dist(points['head_top'],points['ground'])
        if height<=0:
            raise ValueError('INVALID_ANNOTATED_HEIGHT')
        if abs(height-native_height)/native_height>.12:
            errors.append(direction+':LANDMARK_SILHOUETTE_HEIGHT_DISAGREEMENT')
        heights.append(height*finite(annotation.get('metres_per_pixel',0)))
        if direction in ('E','W'):
            for feature,limit in [('hip',contract['profile_hip_width_over_height_max']),('shoulder',contract['profile_shoulder_width_over_height_max'])]:
                if math.dist(points[feature+'_left'],points[feature+'_right'])/height>limit:
                    errors.append(direction+':FRONT_FACING_'+feature.upper()+'_IN_PROFILE')
            for side in ('left','right'):
                heel,toe=points['heel_'+side],points['toe_'+side]
                dx=(toe[0]-heel[0])*(1 if direction=='E' else -1)
                dy=toe[1]-heel[1]
                if dx<=0 or abs(math.degrees(math.atan2(dy,dx)))>contract['profile_toe_axis_error_degrees_max']:
                    errors.append(direction+':BOOT_NOT_FACING_PROFILE:'+side)
    if not heights or min(heights)<=0 or (max(heights)-min(heights))/max(heights)>contract['registered_height_relative_error_max']:
        errors.append('CROSS_VIEW_BODY_SCALE_MISMATCH')
    regions=data.get('regions',[])
    expected_regions={(v['id'],region) for v in request['views'] for region in v['regions']}
    if {(r['view'],r['id']) for r in regions}!=expected_regions or len(regions)!=len(expected_regions):
        errors.append('SEMANTIC_SOURCE_REGION_COVERAGE')
    for r in regions:
        image=images[r['view']]; mask=pixels(resolve(r['mask']))
        if mask.shape[:2]!=image.shape[:2]:
            errors.append(r['id']+':MASK_DIMENSIONS'); continue
        included=mask[...,0]>127
        if not np.any(included):
            errors.append(r['id']+':EMPTY_SEMANTIC_MASK'); continue
        if request.get('background')=='transparent_alpha' and np.any(included&(image[...,3]<250)):
            errors.append(r['id']+':MATERIAL_MASK_INCLUDES_TRANSPARENCY')
        if request.get('background')!='transparent_alpha' and (green(image)&included).sum()/included.sum()>contract['green_mask_contamination_fraction_max']:
            errors.append(r['id']+':MASK_INCLUDES_CHROMA')
        if r.get('purpose') not in ('volumetric_texture','unwarped_upper') or not r.get('allowed_mesh_parts'):
            errors.append(r['id']+':EXPLICIT_REGION_USAGE_REQUIRED')
        if r.get('purpose')=='unwarped_upper':
            annotation=read(resolve(observed[r['view']]['annotations']))
            points=annotation.get('points',{})
            waist=points.get('waist')
            if not waist or len(waist)!=2 or not .35<(finite(waist[1])-points['head_top'][1])/(points['ground'][1]-points['head_top'][1])<.65:
                errors.append(r['id']+':ANATOMICAL_UPPER_WAIST_CUTOFF_REQUIRED')
            elif np.any(included[int(waist[1])+1:]):
                errors.append(r['id']+':UPPER_MASK_INCLUDES_LOWER_BODY')
        for exclusion in r.get('exclusions',[]):
            excluded=pixels(resolve(exclusion))
            if excluded.shape!=mask.shape or np.any(included&(excluded[...,0]>127)):
                errors.append(r['id']+':FOREIGN_PART_IN_TEXTURE_REGION')
    return {'stage':'source','verdict':'FAIL' if errors else 'HOLD_SOURCE_VISUAL_REVIEW',
            'errors':sorted(set(errors)),'bindings':bindings,'subject_sha256':canonical(bindings),
            'note':'Masks/landmarks must be independently visually reviewed; numbers cannot recognize ghost hands.'}


def verify_reviews(reviews,subject,checks,roles=None):
    roles=roles or read(CONTRACT)['independent_review_roles']; errors=[]; seen=[]
    for r in reviews:
        role=r.get('role'); seen.append(role)
        if r.get('subject_sha256')!=subject or r.get('verdict')!='PASS':
            errors.append('REVIEW_FAIL_HOLD_OR_STALE:'+str(role))
        if not r.get('reviewer') or not r.get('reviewed_utc'):
            errors.append('REVIEW_ATTRIBUTION_REQUIRED:'+str(role))
        if set(r.get('checks',{}))!=set(checks) or any(v!='PASS' for v in r.get('checks',{}).values()):
            errors.append('INCOMPLETE_REVIEW_CHECKS:'+str(role))
        evidence=resolve(r['reply_evidence'])
        if not evidence.read_text(encoding='utf-8').strip():
            errors.append('EMPTY_REVIEW_EVIDENCE')
    if set(seen)!=set(roles) or len(seen)!=len(roles):
        errors.append('INDEPENDENT_REVIEW_COVERAGE')
    return errors


def seal_source(bundle):
    data=read(bundle); source=resolve(data['source_manifest'])
    audit=audit_source(source)
    errors=audit['errors']+verify_reviews(data.get('reviews',[]),audit['subject_sha256'],read(CONTRACT)['source_review_checks'])
    if errors:
        raise ValueError('SOURCE_NOT_APPROVED:'+','.join(errors))
    return {'schema':1,'stage':'source','verdict':'PASS_SOURCE_FOR_RIG_CONSTRUCTION_ONLY',
            'source_manifest':ref(source),'review_bundle':ref(bundle),'bindings':audit['bindings'],
            'subject_sha256':audit['subject_sha256']}


def verify_receipt(path,stage='source'):
    receipt=read(path)
    expected='PASS_SOURCE_FOR_RIG_CONSTRUCTION_ONLY' if stage=='source' else 'PASS_FIRST_POSE_FOR_ANIMATION_ONLY'
    if receipt.get('stage')!=stage or receipt.get('verdict')!=expected:
        raise ValueError('WRONG_OR_UNAPPROVED_GENERATION_STAGE')
    bindings=receipt.get('bindings',{})
    if not bindings or canonical(bindings)!=receipt.get('subject_sha256'):
        raise ValueError('INVALID_GENERATION_RECEIPT_BINDING')
    for p,hash_value in bindings.items():
        if sha(p)!=hash_value:
            raise ValueError('STALE_GENERATION_RECEIPT:'+p)
    resolve(receipt['review_bundle'])
    if stage=='source':
        actual=audit_source(resolve(receipt['source_manifest']))
        if actual['errors'] or actual['bindings']!=bindings:
            raise ValueError('INCOMPLETE_SOURCE_BINDING_CLOSURE')
        checks=read(CONTRACT)['source_review_checks']
    else:
        actual=audit_pose_bundle(resolve(receipt['pose_bundle']))
        if actual['errors'] or any(actual.get(k)!=receipt.get(k) for k in
                ('bindings','approved_scope','source_receipt','blend','scene_sha256')):
            raise ValueError('INCOMPLETE_OR_FORGED_FIRST_POSE_BINDING')
        checks=read(CONTRACT)['pose_review_checks']
    reviews=read(resolve(receipt['review_bundle']))
    expected_key='source_manifest' if stage=='source' else 'pose_bundle'
    if reviews.get(expected_key)!=receipt[expected_key]:
        raise ValueError('REVIEW_BUNDLE_SUBJECT_MISMATCH')
    errors=verify_reviews(reviews.get('reviews',[]),receipt['subject_sha256'],checks)
    if errors:
        raise ValueError('INVALID_SOURCE_REVIEW:'+','.join(errors))
    return receipt


def source_authority(path):
    """Compose already reviewed sources, never unreviewed multi-image output."""
    data=read(path)
    if data.get('stage') == 'existing_source_receipt':
        # Existing ImageGen art has a separate, immutable-source intake gate.
        # It is not a generic source receipt and must retain its own visual and
        # alpha proof before an adapter may consume it.
        from source_art_intake import authority
        return authority(path)
    if data.get('stage')=='source':
        receipts=[verify_receipt(path)]; receipt_paths=[ref(path)]
    elif data.get('stage')=='source_set':
        receipt_paths=data.get('receipts',[])
        if not receipt_paths or len({r['path'] for r in receipt_paths})!=len(receipt_paths):
            raise ValueError('DISTINCT_APPROVED_SOURCE_RECEIPTS_REQUIRED')
        receipts=[verify_receipt(resolve(r)) for r in receipt_paths]
    else:
        raise ValueError('APPROVED_SOURCE_OR_SOURCE_SET_REQUIRED')
    sources=[read(resolve(r['source_manifest'])) for r in receipts]
    if len({(s['actor_id'],s['costume_id']) for s in sources})!=1:
        raise ValueError('CROSS_CHARACTER_SOURCE_SET_FORBIDDEN')
    bindings={}
    for r in receipts:
        bindings.update(r['bindings'])
        bindings[r['review_bundle']['path']]=r['review_bundle']['sha256']
        for review in read(resolve(r['review_bundle']))['reviews']:
            evidence=review['reply_evidence']; resolve(evidence)
            bindings[evidence['path']]=evidence['sha256']
    for r in receipt_paths+[ref(path)]:
        bindings[r['path']]=r['sha256']
    return {'sources':sources,'bindings':bindings,'actor_id':sources[0]['actor_id'],
            'costume_id':sources[0]['costume_id']}


def authority_is_fixture(authority):
    """Existing reviewed ImageGen intake is production-source evidence, never a QA fixture.

    Generic source manifests carry a generation request.  Existing-source intake
    deliberately does not: inventing one would fabricate an ImageGen permit.
    """
    sources=authority.get('sources',[])
    if not sources:return False
    flags=[]
    for source in sources:
        request=source.get('request')
        if not request:return False
        flags.append(read(resolve(request)).get('qa_fixture_only') is True)
    return all(flags)


def assert_authority_is_production_source(authority):
    """Reject synthetic requests while admitting separately reviewed existing intake."""
    sources=authority.get('sources',[])
    if not sources:raise ValueError('EMPTY_SOURCE_AUTHORITY')
    existing=[s.get('stage')=='existing_imagegen_source_intake' for s in sources]
    if all(existing):return authority
    if any(existing):raise ValueError('MIXED_EXISTING_AND_GENERATED_SOURCE_SET_FORBIDDEN')
    flags=[]
    for source in sources:
        if 'request' not in source:raise ValueError('UNCLASSIFIED_SOURCE_AUTHORITY')
        flags.append(read(resolve(source['request'])).get('qa_fixture_only',False))
    if (not flags or any(type(flag) is not bool for flag in flags)
            or any(flag is not False for flag in flags)):
        raise ValueError('SYNTHETIC_GENERATION_FIXTURE_NOT_PRODUCTION')
    return authority


def audit_build_plan(path):
    """Freeze a new adapter after source approval; never rewrite its old permit."""
    plan=read(path); errors=[]
    if plan.get('schema')!=1 or plan.get('stage')!='build_plan':
        raise ValueError('EXPLICIT_BUILD_PLAN_REQUIRED')
    from art_authority import retirement_errors, production_errors
    denied=retirement_errors(plan)
    if denied:
        return {'stage':'build_plan','verdict':'FAIL','errors':denied,
                'bindings':{},'subject_sha256':canonical({'plan':ref(path),'errors':denied}),
                'note':'Keep ImageGen art unchanged. Repair the motion-only implementation; do not renew this retired recipe.'}
    authority=source_authority(resolve(plan['source_receipt']))
    errors.extend(production_errors(plan,authority))
    if any(plan.get(k)!=authority[k] for k in ('actor_id','costume_id')):
        errors.append('BUILD_PLAN_SOURCE_IDENTITY_MISMATCH')
    # A reviewed source may retain its immutable ImageGen green master while
    # binding an exact, independently checked RGBA derivative for runtime and
    # source-preserving Blender materials.  Both are approved appearance inputs;
    # neither permits a replacement image.
    approved={}
    for source in authority['sources']:
        for view in source['views']:
            for image in (view['image'],view.get('rgba')):
                if image:
                    approved[image['path']]=image['sha256']
    images=plan.get('source_images',[])
    if not images or len({r['path'] for r in images})!=len(images) or any(approved.get(r['path'])!=r['sha256'] for r in images):
        errors.append('BUILD_PLAN_READS_UNAPPROVED_SOURCE_IMAGES')
    directions={v['id'] for s in authority['sources'] for v in s['views']}
    if plan.get('direction') not in directions:
        errors.append('BUILD_PLAN_DIRECTION_NOT_IN_SOURCE_SCOPE')
    limits=plan.get('limits',{})
    if (type(limits.get('max_native_poses')) is not int or limits['max_native_poses']!=1 or
            type(limits.get('max_motion_frames')) is not int or limits['max_motion_frames']!=0 or
            type(limits.get('threads')) is not int or not 1<=limits['threads']<=2 or
            type(limits.get('timeout_seconds')) is not int or not 1<=limits['timeout_seconds']<=240):
        errors.append('BUILD_PLAN_ONE_BOUNDED_FIRST_POSE_ONLY')
    output=local(plan['output_root'])
    fixture=authority_is_fixture(authority)
    if fixture and not output.is_relative_to(ROOT/'artifacts/generation_harness_audit/unit_fixtures'):
        errors.append('BUILD_FIXTURE_CANNOT_ESCAPE_INTO_PRODUCTION')
    if not fixture and not output.is_relative_to(ROOT/'art_src/characters'):
        errors.append('BUILD_PLAN_CHARACTER_OUTPUT_ROOT_REQUIRED')
    if resolve(plan['builder'])==resolve(plan['runner']):
        errors.append('DISTINCT_RUNNER_AND_BUILDER_REQUIRED')
    scope=resolve(plan['scope'])
    if not scope.read_text(encoding='utf-8').strip():errors.append('BUILD_SCOPE_REQUIRED')
    dependencies=plan.get('dependencies',[])
    if not any(resolve(r)==ROOT/'tools/character_pipeline/collect_generation_mesh_preflight.py' for r in dependencies):
        errors.append('ACTUAL_COLLECTOR_DEPENDENCY_REQUIRED')
    calf_witness=plan.get('calf_width_witness')
    if calf_witness is not None:
        try:
            resolve(calf_witness)
        except (KeyError, TypeError, ValueError, FileNotFoundError):
            errors.append('CAMERA_PLANE_CALF_WITNESS_REQUIRED')
    inputs=plan.get('readonly_inputs',[])
    if not inputs:errors.append('LICENSE_BOUND_BODY_OR_RIG_INPUT_REQUIRED')
    # The source receipt intentionally excludes the mutable downstream adapter
    # registry.  Bind the scope guard and its exact policy here instead so a
    # policy/code change always invalidates the build-plan review without
    # creating a source-receipt dependency cycle.
    build_authority=[ref(ROOT/'tools/character_pipeline/art_authority.py'),
                     ref(ROOT/'tools/character_pipeline/art_authority_policy.json')]
    refs=[ref(path),plan['source_receipt'],plan['builder'],plan['runner'],plan['scope'],
          *images,*dependencies,*build_authority]
    if calf_witness is not None:
        refs.append(calf_witness)
    for item in inputs:
        asset=resolve(item['asset']);license_path=resolve(item['license'])
        if item.get('readonly') is not True or not license_path.read_bytes():
            errors.append('READONLY_INPUT_AND_LICENSE_EVIDENCE_REQUIRED')
        refs.extend([item['asset'],item['license']])
    bindings=dict(authority['bindings'])
    for r in refs:
        p=resolve(r)
        if p.is_relative_to(output):errors.append('BUILD_OUTPUT_OVERLAPS_REVIEWED_INPUT')
        bindings[p.relative_to(ROOT).as_posix()]=sha(p)
    return {'stage':'build_plan','verdict':'FAIL' if errors else 'HOLD_BUILD_PLAN_REVIEW',
            'errors':sorted(set(errors)),'bindings':bindings,'subject_sha256':canonical(bindings),
            'note':'License meaning and adapter behavior require independent code review; no ImageGen retry needed.'}


def seal_build_plan(path):
    bundle=read(path);plan=resolve(bundle['build_plan']);audit=audit_build_plan(plan)
    contract=read(CONTRACT)
    errors=audit['errors']+verify_reviews(bundle.get('reviews',[]),audit['subject_sha256'],
        contract['build_review_checks'],contract['build_review_roles'])
    if errors:raise ValueError('BUILD_PLAN_NOT_APPROVED:'+','.join(errors))
    return {'schema':1,'stage':'build_plan','verdict':'PASS_ONE_MESH_AND_FIRST_POSE_ONLY',
        'build_plan':ref(plan),'review_bundle':ref(path),'bindings':audit['bindings'],
        'subject_sha256':audit['subject_sha256']}


def verify_build_plan(path):
    receipt=read(path)
    if receipt.get('stage')!='build_plan' or receipt.get('verdict')!='PASS_ONE_MESH_AND_FIRST_POSE_ONLY':
        raise ValueError('APPROVED_BUILD_PLAN_REQUIRED')
    actual=seal_build_plan(resolve(receipt['review_bundle']))
    if actual!=receipt:raise ValueError('STALE_OR_FORGED_BUILD_PLAN_RECEIPT')
    return read(resolve(receipt['build_plan']))


def reserve_build_attempt(receipt_path):
    plan=verify_build_plan(receipt_path)
    if local(plan['output_root']).exists():raise ValueError('FRESH_BUILD_OUTPUT_REQUIRED')
    output=ROOT/'artifacts/generation_harness_audit/build_attempts'/(sha(receipt_path)+'.json')
    write(output,{'stage':'build_attempt','build_receipt':ref(receipt_path),
        'output_root':plan['output_root'],'direction':plan['direction'],'max_native_poses':1})
    return ref(output)


def verify_build_attempt(attempt,receipt):
    record=read(attempt);plan=verify_build_plan(receipt)
    expected=ROOT/'artifacts/generation_harness_audit/build_attempts'/(sha(receipt)+'.json')
    if local(attempt)!=expected or record!={'stage':'build_attempt','build_receipt':ref(receipt),
            'output_root':plan['output_root'],'direction':plan['direction'],'max_native_poses':1}:
        raise ValueError('WRONG_OR_FORGED_BUILD_ATTEMPT')
    return plan


def build_claim_path(attempt,role):
    if role not in ('runner','builder'):raise ValueError('UNKNOWN_BUILD_ENTRYPOINT')
    return local(attempt).with_suffix('.'+role+'.claim.json')


def verify_build_claim(attempt,receipt,role):
    plan=verify_build_attempt(attempt,receipt); path=build_claim_path(attempt,role)
    expected={'stage':'build_execution_claim','role':role,'attempt':ref(attempt),
        'build_receipt':ref(receipt),'executable':plan[role],'direction':plan['direction'],
        'output_root':plan['output_root']}
    if read(path)!=expected:raise ValueError('WRONG_OR_FORGED_BUILD_EXECUTION_CLAIM')
    return ref(path)


def claim_build_execution(attempt,receipt,executable,direction):
    """Distinct exclusive runner/child claims; a used or crashed attempt is spent."""
    plan=verify_build_attempt(attempt,receipt)
    role=next((r for r in ('runner','builder') if ref(executable)==plan[r]),None)
    if not role or direction!=plan['direction']:raise ValueError('BUILD_CLAIM_ENTRYPOINT_OR_DIRECTION_MISMATCH')
    if role=='runner':
        if local(plan['output_root']).exists():raise ValueError('FRESH_BUILD_OUTPUT_REQUIRED')
    else:
        verify_build_claim(attempt,receipt,'runner')
    path=build_claim_path(attempt,role)
    write(path,{'stage':'build_execution_claim','role':role,'attempt':ref(attempt),
        'build_receipt':ref(receipt),'executable':plan[role],'direction':direction,
        'output_root':plan['output_root']})
    return ref(path)


def authorize_build(receipt,out,images,generator,diagnostic=False,build_receipt=None,build_attempt=None,direction=None):
    from art_authority import assert_executable_not_retired
    assert_executable_not_retired(generator)
    out=local(out)
    if type(diagnostic) is not bool:
        raise ValueError('DIAGNOSTIC_FLAG_MUST_BE_BOOLEAN')
    if diagnostic:
        if not out.is_relative_to(ROOT/read(CONTRACT)['diagnostic_root']):
            raise ValueError('UNGATED_DIAGNOSTICS_ARE_QUARANTINE_ONLY')
        # Control-rig measurements have separate bounded entrypoints. A
        # character builder cannot become authorized by calling itself a probe.
        raise ValueError('CHARACTER_BUILD_HAS_NO_DIAGNOSTIC_BYPASS')
    if not receipt:
        raise ValueError('SOURCE_RECEIPT_REQUIRED_BEFORE_BLENDER_START')
    if build_receipt:
        if not build_attempt:raise ValueError('BUILD_ATTEMPT_REQUIRED')
        plan=verify_build_attempt(build_attempt,build_receipt)
        if plan['source_receipt']!=ref(receipt) or out!=local(plan['output_root']):
            raise ValueError('BUILD_PLAN_SOURCE_OR_DESTINATION_MISMATCH')
        if direction!=plan['direction']:raise ValueError('BUILD_EXECUTION_DIRECTION_MISMATCH')
        if ref(generator) not in (plan['builder'],plan['runner']):
            raise ValueError('EXECUTABLE_NOT_REVIEWED_BUILD_ENTRYPOINT')
        if any(ref(p) not in plan['source_images'] for p in images):
            raise ValueError('BUILD_EXECUTION_READS_UNAPPROVED_IMAGE')
        return
    r=source_authority(receipt)
    approved=set()
    for source in r['sources']:
        for view in source['views']:
            for image in (view['image'],view.get('rgba')):
                if image:
                    approved.add(str(resolve(image)))
    if not {str(local(p)) for p in images}.issubset(approved):
        raise ValueError('GENERATOR_READS_UNREVIEWED_SOURCE_ART')
    # Source approval alone is never authority for a new visual construction.
    raise ValueError('MOTION_ONLY_BUILD_PLAN_REQUIRED')


def reserve_request(path):
    audit=audit_request(path)
    if audit['errors']:
        raise ValueError('REQUEST_NOT_READY:'+','.join(audit['errors']))
    data=read(path)
    digest=audit['request']['sha256']
    permit=local(data['output_root'])/'generation_requests'/(digest+'.permit.json')
    # Exclusive creation prevents a second unreviewed retry using the same
    # request. A revision must explicitly carry its rejected predecessor.
    if data.get('previous_attempt'):
        previous=read(resolve(data['previous_attempt']))
        if previous.get('verdict') not in ('FAIL','REJECTED') or not previous.get('errors'):
            raise ValueError('PREVIOUS_ATTEMPT_MUST_BE_REVIEWED_BEFORE_RETRY')
    record={'schema':1,'verdict':'RESERVED_SINGLE_SOURCE_ATTEMPT','request':audit['request'],
            'output_root':data['output_root'],'max_outputs':1,
            'note':'Agent must consume this permit before the built-in tool call; this script cannot intercept the tool itself.'}
    write(permit,record)
    return {'stage':'request_reservation','verdict':record['verdict'],'permit':ref(permit)}


def audit_pose_bundle(path):
    from collect_generation_mesh_preflight import validate_collected,is_source_preserving_surface_kind
    bundle=read(path); source_receipt=resolve(bundle['source_receipt'])
    source=source_authority(source_receipt)
    mesh_path=resolve(bundle['mesh_preflight']); collected=read(mesh_path)
    mesh_audit=validate_collected(collected); errors=mesh_audit['errors'][:]
    approved_regions=[]; source_views=set()
    for s in source['sources']:
        view_images={v['id']:v['image'] for v in s['views']}
        source_views.update(view_images)
        approved_regions.extend({**r,'image':view_images[r['view']]} for r in s.get('regions',[]))
    for chart in collected.get('charts',{}).values():
        if not any(chart['mask']==r['mask'] and chart['image']==r['image'] and chart.get('purpose')==r.get('purpose') and
                   chart['allowed_mesh_parts']==r['allowed_mesh_parts'] for r in approved_regions):
            errors.append('MESH_CHART_NOT_APPROVED_SOURCE_REGION')
    bindings=dict(source['bindings'])
    construction_binding=collected.get('contract',{}).get('construction')
    source_surface=is_source_preserving_surface_kind(collected.get('contract',{}).get('kind'))
    fixture=authority_is_fixture(source)
    fixture_root=ROOT/'artifacts/generation_harness_audit/unit_fixtures'
    fixture_paths=[path,mesh_path,resolve(collected['blend'])]
    fixture_paths.extend(resolve(v[k]) for v in bundle.get('views',[]) for k in ('image','render_receipt'))
    fixture=fixture and all(local(p).is_relative_to(fixture_root) for p in fixture_paths)
    if not construction_binding and not fixture:
        errors.append('ACTUAL_BUILD_CONSTRUCTION_REQUIRED')
    if construction_binding:
        construction=read(resolve(bundle['construction']))
        plan=verify_build_attempt(resolve(construction['build_attempt']),resolve(construction['build_receipt']))
        if (construction['build_receipt']!=construction_binding['build_receipt'] or
                construction['build_attempt']!=construction_binding['build_attempt'] or
                construction['blend']!=collected['blend'] or plan['source_receipt']!=bundle['source_receipt'] or
                plan['direction']!=collected['scene']['view']):
            errors.append('FIRST_POSE_CONSTRUCTION_BINDING_MISMATCH')
        if construction.get('readonly_inputs_after')!=plan['readonly_inputs']:
            errors.append('BUILD_READONLY_INPUTS_CHANGED')
        for item in construction.get('readonly_inputs_after',[]):
            resolve(item['asset']);resolve(item['license'])
        claims={role:verify_build_claim(resolve(construction['build_attempt']),
            resolve(construction['build_receipt']),role) for role in ('runner','builder')}
        if construction.get('execution_claims')!=claims:errors.append('BUILD_EXECUTION_CLAIMS_REQUIRED')
        child_refs=[]
        if source_surface:
            # The Blender child is allowed to touch the scene only after the
            # project-Python verifier writes an immutable permit and the child
            # consumes it. Bind both records into the first-pose evidence so a
            # later receipt cannot merely assert that this happened.
            try:
                consumption_path=resolve(construction['child_consumption'])
                consumption=read(consumption_path);permit_path=resolve(consumption['permit'])
                permit=read(permit_path)
                expected_consumption={'schema':1,'stage':'blender_child_execution_consumption',
                    'permit':ref(permit_path),'inputs':construction['inputs'],
                    'runner_claim':claims['runner'],'builder_claim':claims['builder']}
                if consumption!=expected_consumption:
                    errors.append('SOURCE_SURFACE_CHILD_EXECUTION_CONSUMPTION_INVALID')
                if (permit.get('stage')!='verified_blender_child_permit' or permit.get('inputs')!=construction['inputs']
                        or permit.get('runner_claim')!=claims['runner'] or permit.get('builder_claim')!=claims['builder']
                        or permit.get('source_receipt')!=bundle['source_receipt']
                        or permit.get('source_rgba')!=collected['contract']['source']['source_rgba']):
                    errors.append('SOURCE_SURFACE_CHILD_PERMIT_BINDING_INVALID')
                handoff_path=resolve(permit['handoff']);handoff=read(handoff_path)
                if (handoff.get('builder')!=plan['builder'] or handoff.get('runner')!=plan['runner']
                        or handoff.get('build_receipt')!=construction['build_receipt']
                        or handoff.get('build_attempt')!=construction['build_attempt']):
                    errors.append('SOURCE_SURFACE_CHILD_HANDOFF_BINDING_INVALID')
                child_refs.extend([construction['child_consumption'],consumption['permit'],permit['inputs'],
                                   permit['handoff'],permit['verifier']])
            except (KeyError,TypeError,ValueError,FileNotFoundError):
                errors.append('SOURCE_SURFACE_CHILD_EXECUTION_CONSUMPTION_REQUIRED')
        output=local(plan['output_root'])
        actual_outputs=[mesh_path,resolve(collected['blend']),resolve(bundle['construction'])]
        actual_outputs.extend(resolve(v[k]) for v in bundle.get('views',[]) for k in ('image','render_receipt'))
        if any(not local(p).is_relative_to(output) for p in actual_outputs):
            errors.append('FIRST_POSE_OUTSIDE_APPROVED_BUILD_OUTPUT')
        allowed_images={str(resolve(r)) for r in plan['source_images']}
        consumed={str(resolve(c['image'])) for c in collected.get('charts',{}).values()}
        consumed.update(str(local(p)) for ob in collected.get('objects',[]) for p in ob.get('source_images',[]))
        if not consumed.issubset(allowed_images):errors.append('FIRST_POSE_OUTSIDE_APPROVED_BUILD_SOURCE_IMAGES')
        build_receipt=read(resolve(construction['build_receipt']))
        bindings.update(build_receipt['bindings'])
        refs=[bundle['construction'],construction['build_receipt'],construction['build_attempt'],build_receipt['review_bundle']]
        refs.extend(claims.values())
        refs.extend(child_refs)
        refs.extend(r['reply_evidence'] for r in read(resolve(build_receipt['review_bundle']))['reviews'])
        for r in refs:
            resolve(r);bindings[r['path']]=r['sha256']
    for item in [ref(path),ref(source_receipt),ref(mesh_path),collected['blend'],collected['collector']]:
        p=resolve(item); bindings[p.relative_to(ROOT).as_posix()]=sha(p)
    views=bundle.get('views',[])
    if len(views)!=1:
        errors.append('EXACTLY_ONE_FIRST_POSE_PER_SCENE_RECEIPT_REQUIRED')
    for view in views:
        if view['id'] not in source_views:
            errors.append('FIRST_POSE_UNAPPROVED_DIRECTION')
        if view['id']!=collected['scene'].get('view'):
            errors.append('FIRST_POSE_VIEW_NOT_REGISTERED_IN_SCENE')
        image=resolve(view['image']); errors.extend(view['id']+':'+e for e in audit_pose(image)['errors'])
        receipt=read(resolve(view['render_receipt']))
        # Same-process receipt binds the displayed pose to the actual scene,
        # camera, materials (.blend bytes), source and Blender frame.
        if receipt.get('method')!='same_process_native_pose_and_mesh_preflight' or receipt.get('image')!=view['image'] or receipt.get('blend')!=collected['blend'] or receipt.get('view')!=view['id']:
            errors.append(view['id']+':FIRST_POSE_RENDER_BINDING_MISMATCH')
        if receipt.get('scene_sha256')!=canonical(collected['scene']):
            errors.append(view['id']+':FIRST_POSE_CAMERA_OR_SCENE_CHANGED')
        if receipt.get('mesh_preflight')!=ref(mesh_path):
            errors.append(view['id']+':FIRST_POSE_WRONG_MESH_PREFLIGHT')
        for item in (view['image'],view['render_receipt']):
            p=resolve(item); bindings[p.relative_to(ROOT).as_posix()]=sha(p)
    return {'stage':'first_pose','verdict':'FAIL' if errors else 'HOLD_FIRST_POSE_VISUAL_REVIEW',
            'errors':sorted(set(errors)),'bindings':bindings,'subject_sha256':canonical(bindings),
            'approved_scope':[v['id'] for v in views],'source_receipt':ref(source_receipt),
            'blend':collected['blend'],'scene_sha256':canonical(collected['scene'])}


def seal_pose(path):
    data=read(path); audit=audit_pose_bundle(resolve(data['pose_bundle']))
    errors=audit['errors']+verify_reviews(data.get('reviews',[]),audit['subject_sha256'],read(CONTRACT)['pose_review_checks'])
    if errors:
        raise ValueError('FIRST_POSE_NOT_APPROVED:'+','.join(errors))
    return {**audit,'schema':1,'verdict':'PASS_FIRST_POSE_FOR_ANIMATION_ONLY',
            'pose_bundle':data['pose_bundle'],'review_bundle':ref(path)}


def assert_production_source_receipt(receipt):
    """A technical fixture receipt can never be relabelled as production later."""
    source=source_authority(resolve(receipt['source_receipt']))
    return assert_authority_is_production_source(source)


def authorize_animation(config,blend_path,scene_fingerprint=None):
    if type(config.get('qa_fixture_only',False)) is not bool:
        raise ValueError('QA_FIXTURE_FLAG_MUST_BE_BOOLEAN')
    if config.get('qa_fixture_only') is True:
        # Fixtures must retain their provenance AND original isolated path.
        root=ROOT/'artifacts/motion_harness_audit/technical_fixtures'
        outputs=[config['output'],config['render_receipt']]
        outputs.extend(p for row in config['frames'] for p in (row['image'],row['master_image']))
        if (config.get('subject_sha256')!='SYNTHETIC_QA_NOT_PRODUCTION' or
                not local(blend_path).is_relative_to(root) or
                any(not local(p).is_relative_to(root) for p in outputs)):
            raise ValueError('FIXTURE_CANNOT_ESCAPE_INTO_PRODUCTION')
        provenance=read(resolve(config['fixture_provenance']))
        if provenance.get('generator')!=ref(ROOT/'tests/blender/motion_geometry_smoke.py') or provenance.get('blend')!=ref(blend_path) or provenance.get('status')!='SYNTHETIC_QA_NOT_PRODUCTION':
            raise ValueError('INVALID_FIXTURE_PROVENANCE')
        return
    if not config.get('generation_receipt'):
        raise ValueError('FIRST_POSE_RECEIPT_REQUIRED_BEFORE_ANIMATION_RENDER')
    receipt=verify_receipt(config['generation_receipt'],stage='first_pose')
    assert_production_source_receipt(receipt)
    resolve(receipt['blend'])
    if receipt['blend']!=ref(blend_path):
        raise ValueError('SCENE_OR_MATERIALS_CHANGED_AFTER_FIRST_POSE_REVIEW')
    if config.get('direction') not in receipt['approved_scope']:
        raise ValueError('FIRST_POSE_REVIEW_DOES_NOT_COVER_REQUESTED_DIRECTION')
    if scene_fingerprint is not None and receipt['scene_sha256']!=scene_fingerprint:
        raise ValueError('LIVE_CAMERA_OR_SCENE_CHANGED_AFTER_FIRST_POSE_REVIEW')
    collected=read(resolve(read(resolve(receipt['pose_bundle']))['mesh_preflight']))
    semantic=collected['contract']
    if config.get('skinned_mesh')!=semantic.get('sole_mesh') or config.get('sole_vertex_ids')!=semantic.get('sole_vertex_ids'):
        raise ValueError('ANIMATION_CANNOT_SUBSTITUTE_REVIEWED_SOLE_GEOMETRY')
    if config.get('body_coordinate_frame')!=semantic.get('body_coordinate_frame'):
        raise ValueError('ANIMATION_CANNOT_SUBSTITUTE_REVIEWED_BODY_FRAME')
    if [config.get('native_size',1920)]*2+[100]!=collected['scene']['render']:
        raise ValueError('ANIMATION_CANNOT_CHANGE_REVIEWED_NATIVE_RESOLUTION')


def motion_build_bindings(receipt_paths,actor_id,costume_id):
    """Final packaging must inherit generation approval for all eight views."""
    directions={'E','SE','S','SW','W','NW','N','NE'}
    if not isinstance(receipt_paths,list) or len(receipt_paths)!=8:
        raise ValueError('EIGHT_REVIEWED_FIRST_POSE_RECEIPTS_REQUIRED')
    files={}; covered=[]; images=set(); scenes=set()
    for path in receipt_paths:
        r=verify_receipt(path,stage='first_pose')
        source=assert_production_source_receipt(r)
        if (source['actor_id'],source['costume_id'])!=(actor_id,costume_id):
            raise ValueError('GENERATION_APPROVAL_FOR_DIFFERENT_CHARACTER')
        covered.extend(r['approved_scope']); files.update(r['bindings'])
        for value in [ref(path),r['review_bundle']]:
            files[value['path']]=value['sha256']
        for review in read(resolve(r['review_bundle']))['reviews']:
            evidence=review['reply_evidence']; resolve(evidence)
            files[evidence['path']]=evidence['sha256']
        images.update(v['image']['path'] for s in source['sources'] for v in s['views'])
        scenes.add(r['blend']['path'])
    if set(covered)!=directions or len(covered)!=8:
        raise ValueError('GENERATION_APPROVAL_DIRECTION_COVERAGE')
    return {'files':files,'source_art':images,'blender_scene':scenes}


def assert_camera_lock(approved,actual):
    if not approved or canonical(approved)!=canonical(actual):
        raise ValueError('ANIMATION_CAMERA_CHANGED_AFTER_FIRST_POSE_REVIEW')


def check_uv_triangles(triangles,charts):
    """Check area samples, not just UV vertices. Cross-chart faces are forbidden."""
    import numpy as np
    errors=[]; cache={}
    for chart_id,c in charts.items():
        mask=pixels(resolve(c['mask']))[...,0]>127
        texture=pixels(resolve(c['image']))
        if mask.shape!=texture.shape[:2]:
            raise ValueError('UV_MASK_TEXTURE_SIZE_MISMATCH')
        # Native-alpha textures do not have a key color. Do not throw away
        # legitimate green material; reject empty/soft pixels in opaque UVs.
        native_alpha=bool(np.any(texture[...,3]<255))
        chroma=(texture[...,3]<250) if native_alpha else green(texture)
        if c.get('purpose')=='unwarped_upper':
            # The unwarped image plane may cover key-green background, but not
            # any unapproved non-green limb/hand/garment outside its upper mask.
            empty=(texture[...,3]==0) if native_alpha else chroma
            mask=mask|empty; chroma=np.zeros_like(chroma)
        cache[chart_id]=(mask,chroma,c['allowed_mesh_parts'])
    for tri in triangles:
        ids=tri.get('chart_ids',[])
        if len(ids)!=3 or len(set(ids))!=1 or ids[0] not in cache:
            errors.append('UV_FACE_CROSSES_CHART_OR_UNASSIGNED'); continue
        mask,chroma,parts=cache[ids[0]]
        if tri['part'] not in parts:
            errors.append('WRONG_SEMANTIC_TEXTURE_PART'); continue
        coords=np.asarray(tri['uv'],dtype=float)
        if coords.shape!=(3,2) or not np.isfinite(coords).all():
            raise ValueError('INVALID_UV_TRIANGLE')
        # Sample at <=1/2 texture-pixel intervals along the longest UV edge.
        # Bound pathological huge charts: reject instead of silently undersampling.
        h,w=mask.shape
        edge_a=coords[1]-coords[0]; edge_b=coords[2]-coords[0]
        if abs(edge_a[0]*edge_b[1]-edge_a[1]*edge_b[0])*w*h<.25:
            errors.append('DEGENERATE_UV_TRIANGLE'); continue
        span=max(np.linalg.norm((coords[i]-coords[j])*[w,h]) for i,j in [(0,1),(1,2),(2,0)])
        steps=max(2,int(math.ceil(span*2)))
        if steps>512:
            errors.append('UV_TRIANGLE_TOO_LARGE_FOR_RELIABLE_PREFLIGHT'); continue
        invalid=False
        for a in range(steps+1):
            b=np.arange(steps+1-a,dtype=float)/steps
            uv=coords[0]*(a/steps)+b[:,None]*coords[1]+(1-a/steps-b)[:,None]*coords[2]
            x=np.floor(uv[:,0]*w).astype(int); y=np.floor((1-uv[:,1])*h).astype(int)
            if np.any((x<1)|(x>=w-1)|(y<1)|(y>=h-1)):
                invalid=True; break
            # Conservative 3x3 footprint covers bilinear filtering at edges.
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    if np.any(~mask[y+dy,x+dx]|chroma[y+dy,x+dx]):
                        invalid=True; break
                if invalid: break
            if invalid:
                break
        if invalid:
            errors.append('UV_INTERIOR_SAMPLES_CHROMA_OR_FOREIGN_REGION')
    return sorted(set(errors))


def audit_pose(image_path):
    import numpy as np
    image=pixels(image_path); limits=read(CONTRACT)['pose']; h,w=image.shape[:2]
    errors=[]; opaque=image[...,3]>127
    if w<limits['native_min_width'] or h<limits['native_min_height']:
        errors.append('FIRST_POSE_NOT_NATIVE_1080P')
    if not opaque.any():
        errors.append('EMPTY_FIRST_POSE')
    elif np.count_nonzero(green(image)&opaque)/np.count_nonzero(opaque)>limits['opaque_chroma_fraction_max']:
        errors.append('OPAQUE_SOURCE_GREEN_ON_CHARACTER')
    border=limits['transparent_border_pixels']
    if opaque[:border].any() or opaque[-border:].any() or opaque[:,:border].any() or opaque[:,-border:].any():
        errors.append('FIRST_POSE_CLIPPED')
    return {'stage':'first_pose','verdict':'FAIL' if errors else 'HOLD_FIRST_POSE_VISUAL_REVIEW',
            'errors':errors,'image':ref(image_path),'native_size':[w,h],
            'note':'Cannot detect likeness, fake hands or all disconnected seams automatically. Independent reviews still required.'}


def completion_record(out,direction=None):
    """Call only after the owned child has exited successfully; never on timeout."""
    from collect_generation_mesh_preflight import validate_collected
    out=local(out); manifest=read(out/'rig_manifest.json')
    blend=manifest['blend']; resolve(blend)
    raw_path=out/'MESH_PREFLIGHT_RAW.json'; raw=read(raw_path)
    report=validate_collected(raw)
    if report['errors'] or raw['blend']!=blend:
        raise ValueError('COMPLETION_MESH_PREFLIGHT_FAILED')
    files=[ref(out/'rig_manifest.json'),ref(raw_path),blend]
    if direction:
        image_path=out/f'MICA_{direction}_NATIVE_1920.png'
        image_ref=ref(image_path); render_path=out/'FIRST_POSE_RENDER_RECEIPT.json'
        render=read(render_path)
        if (audit_pose(image_path)['errors'] or render.get('image')!=image_ref or
                render.get('blend')!=blend or render.get('mesh_preflight')!=ref(raw_path) or
                render.get('scene_sha256')!=canonical(raw['scene']) or render.get('view')!=direction or
                raw['scene'].get('view')!=direction or render.get('method')!='same_process_native_pose_and_mesh_preflight'):
            raise ValueError('COMPLETION_FIRST_POSE_FAILED_OR_INCOMPLETE')
        files.extend([image_ref,ref(render_path)])
    return {'status':'COMPLETE_CONSTRUCTION_ONLY_NOT_VISUAL_PASS','files':files,
            'source_receipt':manifest.get('source_receipt'),'requested_probe':direction,
            'diagnostic_only':manifest.get('diagnostic_only',False),'owned_child_exited':True}


def next_action(job_path):
    """Read-only stage router. The model does not decide whether HOLD is PASS."""
    job=read(job_path)
    allowed={'schema','actor_id','costume_id','request','permit','source_manifest','source_receipt',
             'build_plan','build_receipt','mesh_preflight','pose_bundle','pose_receipt','motion_descriptor','motion_receipt'}
    if job.get('schema')!=1 or set(job)-allowed or not job.get('actor_id') or not job.get('costume_id'):
        raise ValueError('INVALID_GENERATION_JOB_SCHEMA')
    def result(stage,action,errors=(),**extra):
        return {'job':ref(job_path),'stage':stage,'allowed_next_action':action,'errors':list(errors),
                'production_ready':False,'allow_batch_generation':False,**extra}
    def path(key): return resolve(job[key])
    try:
        if job.get('build_plan'):
            from art_authority import retirement_errors
            errors=retirement_errors(read(path('build_plan')))
            if errors:
                return result('art_authority','REPAIR_MOTION_ADAPTER_WITHOUT_REAUTHORING_ART',errors)
        if not job.get('request'):
            return result('request','AUTHOR_REQUEST_AND_PROMPT')
        request=read(path('request')); audit=audit_request(path('request'))
        if any(request.get(k)!=job[k] for k in ('actor_id','costume_id')):
            raise ValueError('JOB_REQUEST_IDENTITY_MISMATCH')
        if audit['errors']: return result('request','REPAIR_REQUEST',audit['errors'])
        if not job.get('permit'): return result('request','RESERVE_ONE_SOURCE_ATTEMPT')
        permit=read(path('permit'))
        if permit.get('request')!=job['request'] or permit.get('verdict')!='RESERVED_SINGLE_SOURCE_ATTEMPT':
            raise ValueError('JOB_PERMIT_MISMATCH')
        if not job.get('source_manifest'):
            return result('source','GENERATE_ONE_IMAGEGEN_SOURCE',prompt=request['prompt'],
                          source_destination=request['output_root'],max_outputs=1)
        source=read(path('source_manifest'))
        if source['request']!=job['request'] or source['attempt_permit']!=job['permit']:
            raise ValueError('JOB_SOURCE_REQUEST_OR_PERMIT_MISMATCH')
        audit=audit_source(path('source_manifest'))
        if audit['errors']: return result('source','QUARANTINE_AND_REPAIR_SOURCE',audit['errors'])
        if not job.get('source_receipt'): return result('source','REQUEST_INDEPENDENT_SOURCE_REVIEWS')
        authority=source_authority(path('source_receipt'))
        if source not in authority['sources']: raise ValueError('JOB_SOURCE_RECEIPT_MISMATCH')
        if not job.get('build_plan'):
            return result('build_plan','AUTHOR_EXACT_BUILD_PLAN_WITHOUT_IMAGE_GENERATION')
        plan=read(path('build_plan'))
        if plan['source_receipt']!=job['source_receipt']:raise ValueError('JOB_BUILD_SOURCE_MISMATCH')
        audit=audit_build_plan(path('build_plan'))
        if audit['errors']:return result('build_plan','REPAIR_BUILD_PLAN_WITHOUT_IMAGE_GENERATION',audit['errors'])
        if not job.get('build_receipt'):return result('build_plan','REQUEST_INDEPENDENT_BUILD_PLAN_REVIEW')
        verified=verify_build_plan(path('build_receipt'))
        if verified!=plan:raise ValueError('JOB_BUILD_RECEIPT_MISMATCH')
        if not job.get('mesh_preflight'):
            return result('mesh','BUILD_ONE_MESH_AND_FIRST_POSE',max_native_pose_renders=1)
        from collect_generation_mesh_preflight import validate_collected
        collected=read(path('mesh_preflight'))
        construction=collected.get('contract',{}).get('construction',{})
        if construction.get('build_receipt')!=job['build_receipt']:raise ValueError('JOB_MESH_BUILD_RECEIPT_MISMATCH')
        attempt=resolve(construction['build_attempt'])
        verify_build_attempt(attempt,path('build_receipt'))
        for role in ('runner','builder'):verify_build_claim(attempt,path('build_receipt'),role)
        if collected['scene']['view']!=plan['direction'] or any(not p.is_relative_to(local(plan['output_root']))
                for p in (path('mesh_preflight'),resolve(collected['blend']))):
            raise ValueError('JOB_MESH_OUTSIDE_BUILD_SCOPE')
        audit=validate_collected(collected)
        if audit['errors']: return result('mesh','REPAIR_MESH_WITHOUT_ANIMATION_RENDER',audit['errors'])
        if not job.get('pose_bundle'): return result('first_pose','ASSEMBLE_FIRST_POSE_REVIEW_BUNDLE')
        bundle=read(path('pose_bundle'))
        if bundle['source_receipt']!=job['source_receipt'] or bundle['mesh_preflight']!=job['mesh_preflight']:
            raise ValueError('JOB_FIRST_POSE_INPUT_MISMATCH')
        audit=audit_pose_bundle(path('pose_bundle'))
        if audit['errors']: return result('first_pose','QUARANTINE_AND_REPAIR_FIRST_POSE',audit['errors'])
        if not job.get('pose_receipt'): return result('first_pose','REQUEST_INDEPENDENT_FIRST_POSE_REVIEWS')
        receipt=verify_receipt(path('pose_receipt'),'first_pose')
        if receipt['pose_bundle']!=job['pose_bundle']: raise ValueError('JOB_POSE_RECEIPT_MISMATCH')
        if not job.get('motion_descriptor'):
            return result('motion','AUTHOR_ONE_BOUNDED_MOTION_PILOT',approved_directions=receipt['approved_scope'],
                          max_frames=49,note='One direction/clip. This does not approve its motion or any other direction.')
        import motion_harness as motion
        validate_job_motion_chain(job,path('motion_descriptor'))
        audit=motion.audit(path('motion_descriptor'))
        if audit['errors']:
            return result('motion','REPAIR_OR_COMPLETE_MOTION_EVIDENCE',audit['errors']+audit['holds'])
        if not job.get('motion_receipt'):
            return result('motion','REQUEST_FULL_RUNTIME_AND_VISUAL_REVIEWS',audit['holds'])
        motion.require_seal(path('motion_receipt'),path('motion_descriptor'))
        return result('promotion','PROMOTE_EXACT_REVIEWED_CANDIDATE',production_ready=True)
    except (ValueError,KeyError,TypeError,OSError) as exc:
        return result('invalid_or_stale','REPAIR_BINDINGS_WITHOUT_GENERATION',[str(exc)])


def validate_job_motion_chain(job,descriptor_path):
    descriptor_path=local(descriptor_path)
    descriptor=read(descriptor_path)
    build=read(descriptor_path.parent/'MOTION_BUILD_INPUTS.json')
    for item in (descriptor,build):
        if any(item.get(k)!=job[k] for k in ('actor_id','costume_id')):
            raise ValueError('JOB_MOTION_IDENTITY_MISMATCH')
    current=job['pose_receipt']; resolve(current)
    approved=build.get('roles',{}).get('generation_receipt',[])
    if current not in [ref(p) for p in approved]:
        raise ValueError('JOB_CURRENT_POSE_NOT_IN_FINAL_GENERATION_CHAIN')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['request','reserve','source','seal-source','verify','build-plan','seal-build-plan','reserve-build','pose','pose-bundle','seal-pose','mesh','next'])
    p.add_argument('--input',required=True); p.add_argument('--out')
    a=p.parse_args()
    if a.command=='next': result=next_action(a.input)
    elif a.command=='request': result=audit_request(a.input)
    elif a.command=='reserve': result=reserve_request(a.input)
    elif a.command=='source': result=audit_source(a.input)
    elif a.command=='seal-source': result=seal_source(a.input)
    elif a.command=='verify': result=verify_receipt(a.input)
    elif a.command=='build-plan':result=audit_build_plan(a.input)
    elif a.command=='seal-build-plan':result=seal_build_plan(a.input)
    elif a.command=='reserve-build':result=reserve_build_attempt(a.input)
    elif a.command=='pose': result=audit_pose(a.input)
    elif a.command=='pose-bundle': result=audit_pose_bundle(a.input)
    elif a.command=='seal-pose': result=seal_pose(a.input)
    else:
        from collect_generation_mesh_preflight import validate_collected
        result=validate_collected(read(a.input))
    if a.out: write(a.out,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(1 if result.get('errors') else 0)


if __name__=='__main__':
    main()
