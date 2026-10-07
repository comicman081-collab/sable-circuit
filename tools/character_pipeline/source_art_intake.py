"""Admit existing ImageGen direction art without inventing a generation permit.

Historical source reuse is separate from new generation. Exact original and
alpha derivatives, measured landmarks, and current independent reviews are
required. A prior animation HOLD never becomes animation approval here.
"""
from pathlib import Path
import sys
import math
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g

CHECKS=['identity_and_costume','directional_body_and_weapon','source_provenance',
        'native_source_resolution','clean_subject_separation','anatomical_landmarks']


def audit(manifest_path):
    import numpy as np
    from PIL import Image
    manifest=g.read(manifest_path)
    if manifest.get('stage')!='existing_imagegen_source_intake' or manifest.get('schema')!=1:
        raise ValueError('EXPLICIT_EXISTING_SOURCE_INTAKE_REQUIRED')
    bindings={};errors=[]
    def bind(reference):
        path=g.resolve(reference);bindings[reference['path']]=reference['sha256'];return path
    bind(g.ref(manifest_path));bind(g.ref(__file__));bind(g.ref(g.__file__))
    historical=g.read(bind(manifest['historical_source_review']))
    contact=g.read(bind(manifest['historical_source_report']))
    if (historical.get('actor_id')!=manifest['actor_id'] or historical.get('costume_id')!=manifest['costume_id']
            or historical.get('source_author')!='built-in ImageGen'
            or historical.get('motion_handoff')!='APPROVED_FOR_BLENDER_UAL'):
        errors.append('HISTORICAL_IMAGEGEN_SOURCE_AUTHORITY_REQUIRED')
    if historical['review_evidence']['contact_report_sha256']!=manifest['historical_source_report']['sha256']:
        errors.append('HISTORICAL_SOURCE_REVIEW_REPORT_MISMATCH')
    views=manifest.get('views',[])
    if len(views)!=1:errors.append('ONE_DIRECTION_INTAKE_AT_A_TIME')
    for view in views:
        image_path=bind(view['image']);rgba_path=bind(view['rgba']);annotation_path=bind(view['annotations'])
        qa=g.read(bind(view['alpha_qa']));bind(view['alpha_implementation'])
        import derive_chroma_runtime_rgba as chroma
        if view['alpha_implementation']!=g.ref(chroma.__file__):errors.append('EXACT_ALPHA_IMPLEMENTATION_REQUIRED')
        matches=[row for row in contact['directions'] if row['direction']==view['id']]
        if len(matches)!=1 or matches[0]['master']!=view['image']['path'] or matches[0]['master_sha256']!=view['image']['sha256']:
            errors.append('EXACT_HISTORICAL_SOURCE_IMAGE_REQUIRED');continue
        source=np.asarray(Image.open(image_path).convert('RGB'))
        rgba=np.asarray(Image.open(rgba_path).convert('RGBA'))
        if rgba.shape[:2]!=source.shape[:2] or list(Image.open(image_path).size)!=view['native_size']:
            errors.append('NATIVE_SOURCE_SIZE_MISMATCH');continue
        if (qa['input_sha256']!=view['image']['sha256'] or qa['output_sha256']!=view['rgba']['sha256']
                or qa['visible_rgb_byte_exact'] is not True):errors.append('EXACT_ALPHA_RELATIONSHIP_REQUIRED')
        visible=rgba[:,:,3]>0
        expected_background,_=chroma.background_mask(source)
        if not np.array_equal(~visible,expected_background):errors.append('ALPHA_NOT_FROM_REVIEWED_CHROMA_OPERATION')
        if not np.array_equal(source[visible],rgba[visible,:3]):errors.append('VISIBLE_SOURCE_RGB_CHANGED')
        if not set(np.unique(rgba[:,:,3])).issubset({0,255}) or any((visible[0].any(),visible[-1].any(),visible[:,0].any(),visible[:,-1].any())):
            errors.append('CLEAR_BINARY_ALPHA_BORDER_REQUIRED')
        if visible.sum()==0:errors.append('EMPTY_CHARACTER')
        elif np.ptp(np.argwhere(visible)[:,0])+1<1024:errors.append('NATIVE_CHARACTER_HEIGHT_BELOW_1024')
        annotation=g.read(annotation_path)
        if annotation['image_sha256']!=view['image']['sha256'] or annotation['body_facing']!=view['id']:
            errors.append('EXACT_DIRECTION_LANDMARK_BINDING_REQUIRED')
        scale=annotation.get('metres_per_pixel')
        if not isinstance(scale,(int,float)) or not math.isfinite(scale) or scale<=0:errors.append('POSITIVE_FINITE_CHARACTER_SCALE_REQUIRED')
        for name in ('head_top','ground','hip_left','hip_right','shoulder_left','shoulder_right','heel_left','heel_right','toe_left','toe_right'):
            point=annotation.get('points',{}).get(name)
            if (not isinstance(point,list) or len(point)!=2
                    or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in point)
                    or not 0<=point[0]<source.shape[1] or not 0<=point[1]<source.shape[0]):
                errors.append('MEASURED_ANATOMICAL_LANDMARK_REQUIRED:'+name)
        for name,point in annotation.get('points',{}).items():
            if (not isinstance(point,list) or len(point)!=2
                    or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in point)
                    or not 0<=point[0]<source.shape[1] or not 0<=point[1]<source.shape[0]):
                errors.append('INVALID_CONSUMED_POINT:'+name)
    return {'bindings':bindings,'subject_sha256':g.canonical(bindings),'errors':sorted(set(errors)),
            'production_ready':False,'scope':'EXISTING_SOURCE_ONLY_NOT_MOTION_OR_RUNTIME'}


def verify_intake_reviews(reviews,subject):
    errors=g.verify_reviews(reviews,subject,CHECKS,['visual','Ponytail FULL'])
    reviewers=[]
    for row in reviews:
        evidence=g.read(g.resolve(row['reply_evidence']))
        for key in ('subject_sha256','verdict','checks','role','reviewer','reviewed_utc'):
            if evidence.get(key)!=row.get(key):errors.append('ACTUAL_REVIEW_REPLY_MISMATCH:'+key)
        reviewer=str(row.get('reviewer','')).strip().casefold()
        if not reviewer or reviewer in reviewers:errors.append('DISTINCT_REVIEWERS_REQUIRED')
        reviewers.append(reviewer)
        try:
            stamp=datetime.fromisoformat(str(row.get('reviewed_utc','')).replace('Z','+00:00'))
            if stamp.tzinfo is None or stamp.utcoffset()!=timezone.utc.utcoffset(stamp):
                errors.append('REVIEW_UTC_REQUIRED')
        except ValueError:errors.append('VALID_REVIEW_TIMESTAMP_REQUIRED')
    return sorted(set(errors))


def seal_existing_source_intake(manifest_path, review_bundle_path):
    """Create the immutable-source receipt only from a current intake and reviews.

    This mirrors the generic source seal without fabricating a generation request
    for art that already exists.  The caller writes the returned receipt only
    after both independent review records are present.
    """
    manifest_path=g.resolve(g.ref(manifest_path)); review_bundle_path=g.resolve(g.ref(review_bundle_path))
    actual=audit(manifest_path); bundle=g.read(review_bundle_path)
    if bundle.get('manifest')!=g.ref(manifest_path):
        raise ValueError('EXACT_EXISTING_SOURCE_REVIEW_MANIFEST_REQUIRED')
    errors=actual['errors']+verify_intake_reviews(bundle.get('reviews',[]),actual['subject_sha256'])
    if errors:
        raise ValueError('EXISTING_SOURCE_INTAKE_NOT_APPROVED:'+','.join(errors))
    return {'schema':1,'stage':'existing_source_receipt',
            'verdict':'PASS_EXISTING_IMAGEGEN_SOURCE_FOR_BINDING_ONLY',
            'manifest':g.ref(manifest_path),'review_bundle':g.ref(review_bundle_path),
            'bindings':actual['bindings'],'subject_sha256':actual['subject_sha256'],
            'production_ready':False}


def authority(receipt_path):
    receipt=g.read(receipt_path)
    if receipt.get('stage')!='existing_source_receipt':return g.source_authority(receipt_path)
    manifest_path=g.resolve(receipt['manifest']);manifest=g.read(manifest_path);actual=audit(manifest_path)
    if actual['errors'] or receipt.get('verdict')!='PASS_EXISTING_IMAGEGEN_SOURCE_FOR_BINDING_ONLY':
        raise ValueError('EXISTING_SOURCE_NOT_ADMITTED:'+','.join(actual['errors']))
    if receipt['bindings']!=actual['bindings'] or receipt['subject_sha256']!=actual['subject_sha256']:
        raise ValueError('EXISTING_SOURCE_RECEIPT_STALE')
    reviews=g.read(g.resolve(receipt['review_bundle']))
    if reviews.get('manifest')!=receipt['manifest']:raise ValueError('EXACT_SOURCE_REVIEW_SUBJECT_REQUIRED')
    errors=verify_intake_reviews(reviews.get('reviews',[]),actual['subject_sha256'])
    if errors:raise ValueError('INDEPENDENT_SOURCE_REVIEWS_REQUIRED:'+','.join(errors))
    bindings=dict(actual['bindings'])
    for reference in [g.ref(receipt_path),receipt['review_bundle']]+[row['reply_evidence'] for row in reviews['reviews']]:
        g.resolve(reference);bindings[reference['path']]=reference['sha256']
    return {'actor_id':manifest['actor_id'],'costume_id':manifest['costume_id'],
            'sources':[manifest],'bindings':bindings}
