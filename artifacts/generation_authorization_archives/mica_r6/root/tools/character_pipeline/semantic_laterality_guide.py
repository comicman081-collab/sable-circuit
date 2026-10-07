"""Independent exact-content gate for colored anatomical pose annotations."""
from pathlib import Path
import generation_harness as g
import tripo_pose_guide_gate as tripo
ROOT=Path(__file__).resolve().parents[2]
CHECKS=['exact_anatomical_deform_group_mapping','unchanged_evaluated_pose_and_fixed_floor',
        'native_annotations_match_actual_limbs','geometry_only_no_sable_appearance']
ROLES=['visual','Ponytail FULL']


def bindings(manifest,guide):
    files=tripo.closure(guide)
    for path in [Path(__file__),ROOT/'tools/character_pipeline/capture_tripo_laterality_guide.py']:
        files[path.relative_to(ROOT).as_posix()]=g.sha(path)
    visited=set()
    def visit(value):
        if isinstance(value,dict):
            if 'path' in value and 'sha256' in value:
                p=g.resolve(value);rel=p.relative_to(ROOT).as_posix();files[rel]=g.sha(p)
                if p.suffix=='.json' and rel not in visited:
                    visited.add(rel);visit(g.read(p))
            else:
                for v in value.values():visit(v)
        elif isinstance(value,list):
            for v in value:visit(v)
    visit(manifest['completion'])
    return files


def subject(manifest,guide):
    return g.canonical({'bindings':bindings(manifest,guide),'direction':'E','motion':'run','phase':'contact_l',
                        'checks':CHECKS,'base_guide_subject':tripo.subject(guide,'E','run','contact_l')})


def audit(manifest_ref,guide,direction,motion,phase):
    errors=[];files={}
    try:
        manifest=g.read(g.resolve(manifest_ref));files=bindings(manifest,guide)
        files[manifest_ref['path']]=manifest_ref['sha256']
        if (direction,motion,phase)!=('E','run','contact_l'):errors.append('SEMANTIC_GUIDE_EXACT_E_CONTACT_L_ONLY')
        completion=g.read(g.resolve(manifest['completion']));geometry=g.read(g.resolve(completion['geometry']))
        if completion['generator']!=g.ref(ROOT/'tools/character_pipeline/capture_tripo_laterality_guide.py'):
            errors.append('SEMANTIC_GUIDE_CURRENT_GENERATOR_REQUIRED')
        if completion['scope']!='POSE_GUIDE_ANNOTATION_NEEDS_INDEPENDENT_REVIEW' or completion['production_ready'] is not False:
            errors.append('SEMANTIC_GUIDE_REFERENCE_SCOPE_REQUIRED')
        if completion['owned_child_exited'] is not True or completion['source_scale']!=1 or completion['native_resolution']!=[1920,1080]:
            errors.append('SEMANTIC_GUIDE_NATIVE_OWNED_CAPTURE_REQUIRED')
        if geometry['scope']!='ANATOMICAL_LATERALITY_REFERENCE_ONLY_NOT_SABLE_ART' or geometry['pose_or_geometry_modified'] is not False:
            errors.append('SEMANTIC_GUIDE_NO_POSE_OR_APPEARANCE_REBUILD')
        if (geometry['direction'],geometry['motion'],geometry['phase'])!=(direction,motion,phase):errors.append('SEMANTIC_GUIDE_PHASE_MISMATCH')
        report=g.read(g.resolve(guide['contact_calibration']))
        row=next(r for r in report['samples'] if r['sample']==report['phase_candidates'][phase])
        if (geometry['calibration']!=guide['contact_calibration'] or geometry['blend']!=guide['blend'] or
                geometry['frame']!=guide['capture_frame'] or geometry['sample']!=row['sample'] or
                geometry['actual_sole_vertices_world_m']!=row['sole_vertices_world_m'] or
                geometry['fixed_floor_world_z_m']!=report['fixed_floor']['world_z_m']):
            errors.append('SEMANTIC_GUIDE_CHANGED_EXACT_POSE_OR_SOLES')
        if geometry['leg_colors']!={'left':'blue','right':'orange'} or min(geometry['polygon_counts'].values())<=0:
            errors.append('SEMANTIC_GUIDE_ACTUAL_TWO_LEG_LABELS_REQUIRED')
        if manifest['image']!=completion['image']:errors.append('SEMANTIC_GUIDE_EXACT_IMAGE_REQUIRED')
        bundle=g.read(g.resolve(manifest['review_bundle']))
        current=subject(manifest,guide)
        if bundle['subject_sha256']!=current:errors.append('SEMANTIC_GUIDE_REVIEW_SUBJECT_MISMATCH')
        errors.extend(g.verify_reviews(bundle.get('reviews',[]),current,CHECKS,ROLES))
        files[manifest['review_bundle']['path']]=manifest['review_bundle']['sha256']
        for review in bundle.get('reviews',[]):
            ref=review['reply_evidence'];g.resolve(ref);files[ref['path']]=ref['sha256']
    except (KeyError,ValueError,TypeError,StopIteration):
        errors.append('EXACT_SEMANTIC_GUIDE_AND_INDEPENDENT_REVIEWS_REQUIRED')
    return sorted(set(errors)),files
