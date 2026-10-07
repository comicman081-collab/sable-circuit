"""Read-only bridge: source PASS does not authorize an unbound new builder.

This does not issue build-plan approval or modify an ImageGen request/permit.
Run before launching a builder after generation_harness next reports mesh stage.
"""
import argparse
import json
import generation_harness as g


def inspect(job_path,builder,out,images):
    job=g.read(job_path)
    result={'stage':'build_handoff','production_ready':False,'allow_batch_generation':False,
            'allowed_next_action':'REPAIR_BUILD_BINDINGS_WITHOUT_IMAGE_GENERATION',
            'errors':[],'job':g.ref(job_path)}
    try:
        source_path=g.resolve(job['source_receipt'])
        authority=g.source_authority(source_path)
        if any(authority[k]!=job[k] for k in ('actor_id','costume_id')):
            raise ValueError('BUILD_HANDOFF_IDENTITY_MISMATCH')
        if g.local(builder).relative_to(g.ROOT).as_posix() not in authority['bindings']:
            result.update(allowed_next_action='AUTHOR_AND_REVIEW_EXACT_BUILD_PLAN',
                errors=['BUILDER_NOT_IN_REVIEWED_SOURCE_BINDINGS'],
                note='Retain the good source and its original permit. A separate reviewed exact-content build-plan route is required; not permission to run this builder.')
            return result
        g.authorize_build(source_path,out,images,builder)
        result.update(allowed_next_action='BUILD_ONE_BOUND_MESH_AND_FIRST_POSE',
                      max_native_pose_renders=1,builder=g.ref(builder))
    except (ValueError,KeyError,TypeError,OSError) as exc:
        result['errors']=[str(exc)]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--job',required=True);p.add_argument('--builder',required=True)
    p.add_argument('--out-root',required=True);p.add_argument('--image',action='append',default=[])
    a=p.parse_args();result=inspect(a.job,a.builder,a.out_root,a.image)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(1 if result['errors'] else 0)
