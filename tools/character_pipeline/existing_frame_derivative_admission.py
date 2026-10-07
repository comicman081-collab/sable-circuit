"""Narrow admission of the already-authorized R6 raw into a corrected matte.

No new ImageGen permit, historical code execution or old-error filtering. Exact
historical audits were reproduced before current-code changes and are preserved
with their complete file closure. Fresh independent reviews are still required.
"""
from pathlib import Path
import numpy as np
from PIL import Image
import generation_harness as g
import derive_chroma_runtime_rgba as old_chroma
import normalize_imagegen_chroma as edge
import derive_reviewed_chroma_rgba as derivative

ROOT=Path(__file__).resolve().parents[2]
STAGE='existing_visible_frame_derivative_admission'
RAW_SHA='f9e0156f1762a6e8d75fa7bd88df2d2b509af2f6882645dbcacd9ec790b9c3b0'
REQUEST_SUBJECT='eb3621d62c915eaf57986a615b52090b5a8c7b190f398cd8e89c1c0e7e895776'
FRAME_SUBJECT='d5f0f8cf8cd06e2f7b969891a5bbdfc81ca2594bbf92c4a17df3657a514d4961'
ARCHIVE_SHA='573d6266972839a92a9bdaef6973ef08f42c3e222e58f984e6681110e2adfc0c'
MASK_REVIEW_SHA='2551a6956ee6840eee84372724b68c507412089bd2c6494339194b367ee7cc8b'
SCOPE={'actor_id':'CHR_PROTO_03','costume_id':'MICA_RECON_C03','direction':'E','motion':'run','phase':'contact_l'}
EXTRA_CHECKS=['exact_historical_generation_and_single_attempt','unchanged_existing_raw_and_scope',
              'current_source_and_license_authority','explicit_subject_protection_mask',
              'source_rgb_and_all_unselected_pixels_preserved']


def archive_bindings(archive_ref):
    if archive_ref.get('sha256')!=ARCHIVE_SHA:
        raise ValueError('EXACT_R6_AUTHORIZATION_ARCHIVE_REQUIRED')
    archive=g.read(g.resolve(archive_ref));bindings={archive_ref['path']:archive_ref['sha256']}
    if archive.get('scope')!='EXACT_R6_ALREADY_GENERATED_FRAME_NO_NEW_ATTEMPT' or archive.get('new_generation_authorized') is not False:
        raise ValueError('EXISTING_RAW_ONLY_ARCHIVE_REQUIRED')
    archive_root=g.local(archive['archive_root'])
    if not archive_root.is_relative_to(ROOT/'artifacts/generation_authorization_archives'):
        raise ValueError('PROJECT_AUTHORIZATION_ARCHIVE_REQUIRED')
    for rel,sha in archive['files'].items():
        p=(archive_root/rel).resolve()
        if not p.is_relative_to(archive_root) or g.sha(p)!=sha:raise ValueError('TAMPERED_HISTORICAL_CLOSURE')
        bindings[p.relative_to(ROOT).as_posix()]=sha
    def historical(ref):
        if archive['files'].get(ref['path'])!=ref['sha256']:raise ValueError('HISTORICAL_REFERENCE_NOT_ARCHIVED')
        return g.read(archive_root/ref['path'])
    request=historical(archive['original_request']);request_audit=historical(archive['request_audit'])
    frame=historical(archive['original_frame']);frame_audit=historical(archive['frame_audit'])
    permit=historical(archive['original_permit']);intake=historical(archive['intake'])
    proof=g.read(g.resolve(archive['reproduction']))
    if (proof.get('verdict')!='EXACT_HISTORICAL_REQUEST_AND_FRAME_AUDITS_REPRODUCED' or
        proof.get('request_subject_sha256')!=REQUEST_SUBJECT or proof.get('frame_subject_sha256')!=FRAME_SUBJECT or
        frame_audit.get('subject_sha256')!=FRAME_SUBJECT):
        raise ValueError('EXACT_HISTORICAL_REPRODUCTION_REQUIRED')
    if request_audit['errors'] or frame_audit['errors'] or request_audit['subject_sha256']!=REQUEST_SUBJECT:
        raise ValueError('HISTORICAL_TECHNICAL_AUDITS_FAILED')
    if g.canonical(request_audit['bindings'])!=REQUEST_SUBJECT or g.canonical(frame_audit['bindings'])!=frame_audit['subject_sha256']:
        raise ValueError('HISTORICAL_AUDIT_BINDINGS_INVALID')
    for audit in [request_audit,frame_audit]:
        if any(archive['files'].get(k)!=v for k,v in audit['bindings'].items()):raise ValueError('INCOMPLETE_HISTORICAL_AUDIT_CLOSURE')
    if permit!={'schema':1,'stage':'visible_frame_attempt','verdict':'RESERVED_SINGLE_IMAGEGEN_FRAME_ATTEMPT',
        'request':archive['original_request'],'request_subject_sha256':REQUEST_SUBJECT,
        'output_root':request['output_root'],'expected_raw_path':request['expected_raw_path'],'max_outputs':1}:
        raise ValueError('ORIGINAL_SINGLE_ATTEMPT_PERMIT_REQUIRED')
    if any(request.get(k)!=v or frame.get(k)!=v for k,v in SCOPE.items()):raise ValueError('EXACT_R6_SCOPE_REQUIRED')
    if (archive['raw']['sha256']!=RAW_SHA or frame['raw_image']!=archive['raw'] or intake['raw']!=archive['raw'] or
        archive['raw']['path']!=request['expected_raw_path'] or frame['request']!=archive['original_request'] or
        frame['attempt_permit']!=archive['original_permit'] or intake['request']!=archive['original_request']):
        raise ValueError('ORIGINAL_RAW_INTAKE_OR_SCOPE_CHANGED')
    g.resolve(archive['raw'])
    # Current source authority and licenses remain required; old proofs cannot
    # authorize a revoked source or a renamed failed appearance reconstruction.
    g.assert_production_source_receipt({'source_receipt':request['source_receipt']})
    guide=request['pose_guide']
    for key in ('blend','license','tripo_license','contact_calibration'):g.resolve(guide[key])
    paid=g.read(g.resolve(guide['tripo_license']));licensed=g.read(g.resolve(guide['license']))
    if paid.get('commercial_use')!='ALLOW' or paid.get('derivatives')!='ALLOW' or licensed.get('license')!='CC0-1.0':
        raise ValueError('CURRENT_LICENSE_AUTHORITY_REQUIRED')
    for ref in [archive['raw'],archive['reproduction'],archive['reproduce_code'],request['source_receipt']]:
        g.resolve(ref);bindings[ref['path']]=ref['sha256']
    return archive,frame,request,bindings


def audit(path):
    data=g.read(path);errors=[];bindings={};request_ref=None
    try:
        if data.get('schema')!=1 or data.get('stage')!=STAGE or data.get('new_generation_authorized') is not False:
            raise ValueError('DERIVATIVE_ADMISSION_NOT_A_GENERATION_PERMIT')
        if 'frame_validation_contract' in data:
            raise ValueError('ADMISSION_AND_NEW_FRAME_SCHEMAS_MUST_NOT_MIX')
        if any(data.get(k)!=v for k,v in SCOPE.items()):raise ValueError('DERIVATIVE_CANNOT_CHANGE_POSE_SCOPE')
        archive,frame,request,bindings=archive_bindings(data['authorization_archive'])
        request_ref=archive['original_request']
        if data['original_frame']!=archive['original_frame']:raise ValueError('EXACT_ORIGINAL_FRAME_REQUIRED')
        for ref in [data['original_frame'],data['derivative_qa'],data['runtime_rgba'],data['protection_mask'],data['mask_scope_review']]:
            g.resolve(ref);bindings[ref['path']]=ref['sha256']
        qa=g.read(g.resolve(data['derivative_qa']));mask_review=g.read(g.resolve(data['mask_scope_review']))
        if (data['mask_scope_review']['sha256']!=MASK_REVIEW_SHA or
                mask_review.get('incorrectly_removed_subject_pixel_count')!=82 or mask_review.get('verdict')!='HOLD' or
                mask_review.get('subject_sha256')!=FRAME_SUBJECT or mask_review.get('role')!='Ponytail FULL'):
            raise ValueError('EXACT_RECORDED_ALPHA_DEFECT_REQUIRED')
        reply=mask_review['reply_evidence'];g.resolve(reply);bindings[reply['path']]=reply['sha256']
        rgb=np.asarray(Image.open(g.resolve(frame['normalized_image'])).convert('RGB'))
        original=np.asarray(Image.open(g.resolve(frame['runtime_rgba'])).convert('RGBA'))
        actual=np.asarray(Image.open(g.resolve(data['runtime_rgba'])).convert('RGBA'))
        mask=np.asarray(Image.open(g.resolve(data['protection_mask'])))
        if mask.shape!=rgb.shape[:2] or not set(np.unique(mask)).issubset({0,255}):raise ValueError('EXACT_NATIVE_BINARY_MASK_REQUIRED')
        protect=mask==255
        if int(protect.sum())!=82:raise ValueError('EXACT_82_SUBJECT_PIXELS_REQUIRED')
        reviewed_pixels={tuple(point) for component in mask_review['incorrectly_removed_subject_components']
                         for point in component['pixel_coordinates_xy']}
        actual_pixels={(int(x),int(y)) for y,x in np.argwhere(protect)}
        if len(reviewed_pixels)!=82 or reviewed_pixels!=actual_pixels:
            raise ValueError('MASK_MUST_EQUAL_EXACT_INDEPENDENTLY_REVIEWED_PIXELS')
        # This migration permits only the exact two known interior defect regions.
        permitted=np.zeros_like(protect);permitted[757:762,746:754]=True;permitted[808:816,539:549]=True
        if np.any(protect & ~permitted):raise ValueError('MASK_OUTSIDE_REVIEWED_KNEE_INSETS')
        background,_=old_chroma.background_mask(rgb);edge_bg,_=edge.edge_connected_background(rgb)
        if np.any(protect & (~background | edge_bg)):raise ValueError('MASK_IS_NOT_INTERIOR_SOURCE_SUBJECT')
        expected=original.copy();expected[protect,:3]=rgb[protect];expected[protect,3]=255
        if actual.shape!=expected.shape or not np.array_equal(actual,expected):raise ValueError('UNREVIEWED_DERIVATIVE_PIXEL_CHANGE')
        if (qa['source']!=frame['normalized_image'] or qa['protection_mask']!=data['protection_mask'] or
                qa['output']!=data['runtime_rgba'] or qa['generator']!=g.ref(derivative.__file__) or
                qa['base_generator']!=g.ref(old_chroma.__file__) or qa['edge_classifier']!=g.ref(edge.__file__) or
                qa['protected_subject_pixels']!=82 or qa['visible_rgb_byte_exact'] is not True or
                qa['outside_protection_byte_exact_to_original_derivative'] is not True or qa['border_transparent'] is not True):
            raise ValueError('EXACT_CURRENT_DERIVATIVE_RECEIPT_REQUIRED')
        # Bind current sources actually consumed, never call archived hashes current.
        for ref in [frame['normalized_image'],frame['runtime_rgba'],frame['annotations']]:
            g.resolve(ref);bindings[ref['path']]=ref['sha256']
        for source in [Path(__file__),Path(derivative.__file__),Path(g.__file__),Path(old_chroma.__file__),Path(edge.__file__),
                       ROOT/'tools/character_pipeline/visible_frame_harness_current.py',
                       ROOT/'tools/character_pipeline/visible_frame_harness.py',
                       ROOT/'tools/character_pipeline/visible_frame_contract.json']:
            bindings[source.relative_to(ROOT).as_posix()]=g.sha(source)
        bindings[g.local(path).relative_to(ROOT).as_posix()]=g.sha(path)
    except (KeyError,ValueError,TypeError,OSError) as exc:
        errors.append(str(exc))
    return {'schema':1,'stage':'visible_frame','verdict':'FAIL' if errors else 'HOLD_VISIBLE_FRAME_REVIEW',
        'errors':errors,'bindings':bindings,'subject_sha256':g.canonical(bindings),**SCOPE,
        'request':request_ref,'admission_stage':STAGE,'new_generation_authorized':False,
        'note':'Existing raw re-derivation only. Requires fresh full frame and admission reviews; no new pose, batch or production approval.'}
