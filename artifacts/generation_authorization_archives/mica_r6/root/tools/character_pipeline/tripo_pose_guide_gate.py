"""Exact Tripo/CC0 guide inlet; never pretend supplied Tripo motion is UAL."""
from pathlib import Path
import generation_harness as g
import tripo_motion_reference as inlet

ROOT=Path(__file__).resolve().parents[2]
KIND='tripo_run_cc0_geometry_guide'
ACTION='Tripo_Run_World_Anchored_REFERENCE_ONLY'


def closure(guide):
    bindings={}; visited=set()
    def visit(value):
        if isinstance(value,dict):
            if set(('path','sha256')).issubset(value):
                path=g.resolve(value); rel=path.relative_to(ROOT).as_posix()
                bindings[rel]=g.sha(path)
                if path.suffix.lower()=='.json' and rel not in visited:
                    visited.add(rel);visit(g.read(path))
            else:
                for item in value.values():visit(item)
        elif isinstance(value,list):
            for item in value:visit(item)
    # Review bundles refer to the subject; exclude them from the subject itself.
    for key in ('image','capture','blend','license','tripo_license','contact_calibration'):
        visit(guide[key])
    for path in (Path(__file__),ROOT/'tools/character_pipeline/visible_frame_harness_current.py',ROOT/'tools/character_pipeline/visible_frame_contract.json'):
        bindings[path.relative_to(ROOT).as_posix()]=g.sha(path)
    return bindings


def subject(guide,direction,motion,phase):
    return g.canonical({'bindings':closure(guide),'direction':direction,'motion':motion,
        'phase':phase,'phase_definition':guide.get('phase_definition'),
        'capture_frame':guide.get('capture_frame'),'source_kind':KIND,'action':ACTION})


def audit(guide,direction,motion,phase):
    errors=[]
    try:
        if direction!='E' or motion!='run':errors.append('TRIPO_GUIDE_ONLY_REVIEWED_E_RUN_ADAPTER')
        if guide.get('source_kind')!=KIND or guide.get('action')!=ACTION:errors.append('EXPLICIT_TRIPO_GUIDE_ACTION_REQUIRED')
        if guide.get('screen_direction')!=direction or guide.get('phase')!=phase:errors.append('TRIPO_GUIDE_DIRECTION_PHASE_MISMATCH')
        if guide.get('visual_role')!='pose_guide_only_not_runtime_art':errors.append('TRIPO_PIXELS_MUST_NOT_BECOME_SABLE_ART')
        contract=g.read(ROOT/'tools/character_pipeline/visible_frame_contract.json')
        if guide.get('phase_definition')!=contract['phase_semantics'][motion][phase]:errors.append('EXACT_TRIPO_PHASE_SEMANTICS_REQUIRED')
        capture=g.read(g.resolve(guide['capture']));result=g.read(g.resolve(capture['retarget_result']))
        if capture.get('scope')!='TRIPO_CC0_GEOMETRY_GUIDE_ONLY_NOT_SABLE_PIXELS' or capture.get('production_ready') is not False:errors.append('TRIPO_CAPTURE_SCOPE_INVALID')
        if capture.get('generator')!=g.ref(ROOT/'tools/character_pipeline/capture_tripo_locomotion_guide.py'):errors.append('EXACT_TRIPO_CAPTURE_GENERATOR_REQUIRED')
        if capture.get('native_resolution')!=[1920,1080] or capture.get('camera_fit')!='actual_evaluated_entire_cycle_with_15_percent_margin':errors.append('TRIPO_FULL_CYCLE_NATIVE_CAPTURE_REQUIRED')
        if guide['blend']!=capture['blend'] or guide['blend']!=result['output_blend']:errors.append('TRIPO_CAPTURE_BLEND_MISMATCH')
        matches=[r for r in capture.get('frames',[]) if r.get('phase')==phase and r.get('frame')==guide.get('capture_frame') and r.get('image')==guide['image']]
        if len(matches)!=1 or len(capture.get('frames',[]))!=49:errors.append('EXACT_TRIPO_FULL_CYCLE_AND_PHASE_REQUIRED')
        if result.get('scope')!='TRIPO_PERIODIC_RETARGET_REFERENCE_NOT_SABLE_ART' or result.get('production_ready') is not False:errors.append('TRIPO_RETARGET_SCOPE_INVALID')
        anchored=result.get('support_anchor',{})
        if anchored.get('per_frame_root_translation') is not False or anchored.get('max_unreachable_distance_m',1)>.0001:errors.append('REACHABLE_TRIPO_SUPPORT_WITHOUT_ROOT_CORRECTION_REQUIRED')
        if not anchored.get('measurements') or any(max(row['horizontal_anchor_error_m'].values())>.001 for row in anchored.get('measurements',[])):errors.append('TRIPO_SUPPORT_ANCHOR_DID_NOT_CONVERGE')
        target_license=g.read(g.resolve(guide['license']))
        if guide['license']!=result['target_license'] or target_license.get('license')!='CC0-1.0' or target_license.get('source_blend')!=result['target_model']:errors.append('EXACT_CC0_TARGET_LICENSE_REQUIRED')
        paid=g.read(g.resolve(guide['tripo_license']))
        if paid.get('commercial_use')!='ALLOW' or paid.get('derivatives')!='ALLOW' or paid.get('paid_at_generation_user_attested') is not True:errors.append('PAID_TRIPO_SOURCE_LICENSE_REQUIRED')
        source=inlet.verify(g.resolve(result['source_pack']))
        completion=g.read(g.resolve(result['source_pack']))
        # Verify the exact user's GLB license, not an unrelated paid asset.
        if paid.get('model')!=g.ref(ROOT/'art_src/motion_reference/tripo_run_20260908/source/ORIGINAL_Run.glb'):errors.append('TRIPO_LICENSE_SOURCE_MISMATCH')
        if source.get('production_ready') is not False:errors.append('TRIPO_REFERENCE_CANNOT_APPROVE_ART')
        closure(guide)
        current_subject=subject(guide,direction,motion,phase)
        bundle=g.read(g.resolve(guide['review_bundle']))
        if bundle.get('pose_guide_subject_sha256')!=current_subject:errors.append('TRIPO_GUIDE_REVIEW_SUBJECT_MISMATCH')
        errors.extend(g.verify_reviews(bundle.get('reviews',[]),current_subject,contract['pose_guide_review_checks'],contract['pose_guide_review_roles']))
    except (KeyError,ValueError,TypeError):
        errors.append('EXACT_TRIPO_GUIDE_PROVENANCE_AND_INDEPENDENT_REVIEWS_REQUIRED')
    return sorted(set(errors))
