"""Admit an unchanged historical neutral source surface under a current source receipt.

The historical Blender probe keeps its original receipt and hashes intact.  This
tool never rewrites it or invents a generation request: it records a fresh
content-equality bridge from the current E ImageGen intake to that exact neutral
mesh, then requires independent implementation and Ponytail FULL review before
the bridge can be used by a Blender child.
"""
import argparse
from datetime import datetime,timezone
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import source_art_intake as intake

CHECKS=['no_visual_reauthoring','neutral_source_preservation','historical_source_geometry_reuse']
ROLES=['implementation','Ponytail FULL']


def verify_admission_reviews(reviews,subject):
    """Require two distinct, actual review replies for this bridge itself."""
    errors=g.verify_reviews(reviews,subject,CHECKS,ROLES);reviewers=[]
    for row in reviews:
        try:evidence=g.read(g.resolve(row['reply_evidence']))
        except (KeyError,TypeError,ValueError,FileNotFoundError):
            errors.append('ACTUAL_HISTORICAL_REVIEW_REPLY_REQUIRED');continue
        for key in ('subject_sha256','verdict','checks','role','reviewer','reviewed_utc'):
            if evidence.get(key)!=row.get(key):errors.append('ACTUAL_HISTORICAL_REVIEW_REPLY_MISMATCH:'+key)
        reviewer=str(row.get('reviewer','')).strip().casefold()
        if not reviewer or reviewer in reviewers:errors.append('DISTINCT_HISTORICAL_REVIEWERS_REQUIRED')
        reviewers.append(reviewer)
        try:
            stamp=datetime.fromisoformat(str(row.get('reviewed_utc','')).replace('Z','+00:00'))
            if stamp.tzinfo is None or stamp.utcoffset()!=timezone.utc.utcoffset(stamp):
                errors.append('HISTORICAL_REVIEW_UTC_REQUIRED')
        except ValueError:errors.append('VALID_HISTORICAL_REVIEW_TIMESTAMP_REQUIRED')
    return sorted(set(errors))


def audit(source_receipt, neutral, anchor, box_capture, native_binding):
    source_receipt=g.resolve(g.ref(source_receipt));neutral=g.resolve(g.ref(neutral))
    anchor=g.resolve(g.ref(anchor));box_capture=g.resolve(g.ref(box_capture));native_binding=g.resolve(g.ref(native_binding))
    authority=intake.authority(source_receipt)
    views=[view for manifest in authority['sources'] for view in manifest['views'] if view['id']=='E']
    if len(views)!=1 or not views[0].get('rgba'):
        raise ValueError('EXACT_CURRENT_E_SOURCE_AND_RGBA_REQUIRED')
    view=views[0];report=g.read(neutral);box=g.read(box_capture);binding=g.read(native_binding);anchor_data=g.read(anchor)
    errors=[];bindings=dict(authority['bindings'])
    references=[g.ref(__file__),g.ref(source_receipt),g.ref(neutral),g.ref(anchor),
                g.ref(box_capture),g.ref(native_binding),view['image'],view['rgba']]
    try:
        base=g.read(g.resolve(report['base_surface']));config=g.read(g.resolve(base['inputs']))
        references.extend([report['base_surface'],base['inputs'],config['source'],config['rgba'],config['source_receipt']])
        if config['source']['sha256']!=view['image']['sha256'] or config['rgba']['sha256']!=view['rgba']['sha256']:
            errors.append('HISTORICAL_NEUTRAL_SOURCE_PIXELS_DIFFER_FROM_CURRENT_INTAKE')
        if report.get('source_rgba',{}).get('sha256')!=view['rgba']['sha256']:
            errors.append('HISTORICAL_NEUTRAL_RGBA_BYTES_DIFFER_FROM_CURRENT_INTAKE')
    except Exception:
        errors.append('UNREADABLE_HISTORICAL_NEUTRAL_SOURCE_CHAIN')
    if (report.get('original_uv_and_weights_preserved') is not True or report.get('closed_edge_incidence') is not True
            or not isinstance(report.get('visible_front_vertex_count'),int) or report['visible_front_vertex_count']<3
            or not report.get('rig_name') or not report.get('mesh_name')):
        errors.append('HISTORICAL_NEUTRAL_SOURCE_GEOMETRY_EVIDENCE_INCOMPLETE')
    # Historical code is immutable provenance retained in the old INPUTS file;
    # it is not a substitute for this current adapter. Bind the exact input
    # record plus the evaluated geometry evidence that the current bridge uses.
    try:
        references.extend([report['inputs'],report['blend'],report['actual_native_rest'],
                           binding['actual_positions'],anchor_data['proposed_poses'],
                           anchor_data['inputs']['prior'],box['qa_capture_inputs']])
        prior=g.read(g.resolve(anchor_data['inputs']['prior']))
        support=g.read(g.resolve(prior['inputs']['support']))
        references.extend([prior['inputs']['support'],support['inputs']['skin']])
    except (KeyError,TypeError,ValueError,FileNotFoundError):
        errors.append('HISTORICAL_EVALUATED_GEOMETRY_CLOSURE_INCOMPLETE')
    if binding.get('inputs',{}).get('report')!=g.ref(neutral) or binding.get('inputs',{}).get('blend')!=report.get('blend'):
        errors.append('HISTORICAL_NATIVE_BINDING_NOT_EXACT_NEUTRAL')
    if anchor_data.get('actual_native_rest')!=report.get('actual_native_rest'):
        errors.append('HISTORICAL_ANCHOR_NOT_EXACT_NEUTRAL_REST')
    try:
        box_inputs=g.read(g.resolve(box['qa_capture_inputs']))
        if (box.get('inputs')!=report.get('inputs') or box_inputs.get('neutral')!=g.ref(neutral)
                or box_inputs.get('blend')!=report.get('blend')
                or box.get('source_rgba',{}).get('sha256')!=view['rgba']['sha256']
                or box.get('pixel_filter_change',{}).get('after')!={'type':'BOX','width':1.0}):
            errors.append('HISTORICAL_BOX_NEUTRAL_SOURCE_PRESERVATION_MISMATCH')
        references.append(box['qa_capture_inputs'])
    except Exception:
        errors.append('UNREADABLE_HISTORICAL_BOX_CAPTURE_CHAIN')
    for reference in references:
        try:
            path=g.resolve(reference);bindings[reference['path']]=g.sha(path)
        except Exception:
            errors.append('UNRESOLVABLE_HISTORICAL_NEUTRAL_BINDING')
    return {'schema':1,'stage':'historical_neutral_reuse_audit',
            'verdict':'FAIL' if errors else 'HOLD_HISTORICAL_NEUTRAL_REUSE_REVIEW',
            'errors':sorted(set(errors)),'source_receipt':g.ref(source_receipt),
            'source_green':view['image'],'source_rgba':view['rgba'],'neutral':g.ref(neutral),
            'anchor':g.ref(anchor),'box_capture':g.ref(box_capture),'native_binding':g.ref(native_binding),
            'historical_neutral':{'blend':report.get('blend'),'mesh_name':report.get('mesh_name'),
                'rig_name':report.get('rig_name'),'visible_front_vertex_count':report.get('visible_front_vertex_count'),
                'fixed_native_neutral_sole_floor_m':report.get('fixed_native_neutral_sole_floor_m')},
            'bindings':bindings,'subject_sha256':g.canonical(bindings),'production_ready':False,
            'note':'This is a content-equality admission for one historical neutral mesh, never a new ImageGen request or motion approval.'}


def seal(audit_path, review_bundle_path):
    audit_path=g.resolve(g.ref(audit_path));review_bundle_path=g.resolve(g.ref(review_bundle_path))
    data=g.read(audit_path)
    # Audit records refs.  Resolve them before re-auditing; passing the dicts to
    # g.ref would stringify their JSON and turn a valid historical admission
    # into an unrelated path lookup.
    actual=audit(*(g.resolve(data[key]) for key in
                   ('source_receipt','neutral','anchor','box_capture','native_binding')))
    if actual['errors'] or actual['bindings']!=data.get('bindings') or actual['subject_sha256']!=data.get('subject_sha256'):
        raise ValueError('STALE_OR_INCOMPLETE_HISTORICAL_NEUTRAL_AUDIT')
    bundle=g.read(review_bundle_path)
    if bundle.get('audit')!=g.ref(audit_path):raise ValueError('EXACT_HISTORICAL_NEUTRAL_REVIEW_SUBJECT_REQUIRED')
    errors=verify_admission_reviews(bundle.get('reviews',[]),actual['subject_sha256'])
    if errors:raise ValueError('HISTORICAL_NEUTRAL_REUSE_NOT_APPROVED:'+','.join(errors))
    return {'schema':1,'stage':'historical_neutral_source_reuse_admission',
            'verdict':'PASS_HISTORICAL_NEUTRAL_GEOMETRY_REUSE_ONLY',
            **{key:actual[key] for key in ('source_receipt','source_green','source_rgba','neutral','anchor','box_capture','native_binding')},
            'audit':g.ref(audit_path),'review_bundle':g.ref(review_bundle_path),
            'bindings':actual['bindings'],'subject_sha256':actual['subject_sha256'],
            'production_ready':False}


def verify(receipt_path):
    receipt=g.read(receipt_path)
    if receipt.get('stage')!='historical_neutral_source_reuse_admission' or receipt.get('verdict')!='PASS_HISTORICAL_NEUTRAL_GEOMETRY_REUSE_ONLY':
        raise ValueError('APPROVED_HISTORICAL_NEUTRAL_ADMISSION_REQUIRED')
    actual=seal(g.resolve(receipt['audit']),g.resolve(receipt['review_bundle']))
    if actual!=receipt:raise ValueError('STALE_OR_FORGED_HISTORICAL_NEUTRAL_ADMISSION')
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['audit','seal','verify'])
    parser.add_argument('--source-receipt');parser.add_argument('--neutral');parser.add_argument('--anchor')
    parser.add_argument('--box-capture');parser.add_argument('--native-binding');parser.add_argument('--audit');parser.add_argument('--reviews');parser.add_argument('--receipt');parser.add_argument('--out')
    args=parser.parse_args()
    if args.command=='audit':
        result=audit(args.source_receipt,args.neutral,args.anchor,args.box_capture,args.native_binding)
    elif args.command=='seal':result=seal(args.audit,args.reviews)
    else:result=verify(args.receipt)
    if args.out:g.write(args.out,result)
    print(result['verdict'])


if __name__=='__main__':main()
