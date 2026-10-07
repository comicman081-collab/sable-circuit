"""Verify and exclusively permit one camera-plane MICA E first-pose child.

This runs in the project Python runtime, where the exact existing-source intake
can inspect pixels.  Blender only receives the resulting immutable permit; it
must consume that permit before it imports or changes a scene.
"""
import argparse
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import source_art_intake as intake
import historical_neutral_reuse_admission as neutral_reuse
import pose_projected_source_camera_plane_probe as builder


def verify(out_arg):
    out=g.local(out_arg); inputs_path=out/'INPUTS.json'
    inputs=g.read(inputs_path)
    for reference in inputs.values():g.resolve(reference)
    for key,path in builder.implementation().items():
        if inputs.get(key)!=g.ref(path):
            raise ValueError('EXACT_IMPLEMENTATION_REQUIRED:'+key)
    handoff_path=g.resolve(inputs['execution_handoff']);handoff=g.read(handoff_path)
    expected={'stage':'reviewed_blender_child_handoff',
              'build_receipt':inputs['build_receipt'],'build_attempt':inputs['build_attempt'],
              'runner':g.ref(ROOT/'tools/character_pipeline/run_mica_E_first_contact_camera_plane_pose.py'),
              'builder':g.ref(builder.__file__),'verifier':g.ref(__file__),
              'direction':'E','source_receipt':inputs['source_receipt'],
              'source_green':inputs['source_green'],'source_rgba':inputs['source_rgba'],
              'neutral_admission':inputs['neutral_admission'],
              'calf_width_witness':inputs['calf_width_witness']}
    if any(handoff.get(key)!=value for key,value in expected.items()):
        raise ValueError('EXACT_EXTERNAL_REVIEWED_BUILDER_HANDOFF_REQUIRED')
    attempt=g.resolve(inputs['build_attempt']);receipt=g.resolve(inputs['build_receipt'])
    plan=g.verify_build_attempt(attempt,receipt)
    if plan.get('neutral_admission')!=inputs['neutral_admission']:
        raise ValueError('EXACT_PLAN_NEUTRAL_ADMISSION_REQUIRED')
    if plan.get('calf_width_witness')!=inputs['calf_width_witness']:
        raise ValueError('EXACT_PLAN_CAMERA_PLANE_CALF_WITNESS_REQUIRED')
    if g.local(handoff.get('child_permit_path',''))!=out/'BLENDER_CHILD_PERMIT.json':
        raise ValueError('EXACT_CHILD_PERMIT_DESTINATION_REQUIRED')
    if handoff.get('output_root')!=plan['output_root'] or g.local(handoff['output_root'])!=out:
        raise ValueError('EXACT_CHILD_OUTPUT_ROOT_REQUIRED')
    if not isinstance(handoff.get('readonly_inputs'),list):
        raise ValueError('EXACT_READONLY_INPUT_HANDOFF_REQUIRED')
    for item in handoff['readonly_inputs']:
        g.resolve(item['asset']);g.resolve(item['license'])
    runner_claim=g.verify_build_claim(attempt,receipt,'runner')
    if handoff.get('runner_claim')!=runner_claim:
        raise ValueError('EXACT_RUNNER_EXECUTION_CLAIM_REQUIRED')
    source_receipt=g.resolve(inputs['source_receipt']);source=intake.authority(source_receipt)
    view=next((row for manifest in source['sources'] for row in manifest['views']
               if row['id']=='E'),None)
    if not view or not view.get('rgba') or view['image']!=inputs['source_green'] or view['rgba']!=inputs['source_rgba']:
        raise ValueError('EXACT_REVIEWED_E_GREEN_AND_RGBA_REQUIRED')
    admission=neutral_reuse.verify(g.resolve(inputs['neutral_admission']))
    if (admission['source_receipt']!=inputs['source_receipt'] or admission['source_green']!=view['image']
            or admission['source_rgba']!=view['rgba'] or admission['neutral']!=inputs['neutral']
            or admission['anchor']!=inputs['anchor'] or admission['box_capture']!=inputs['box_capture']
            or admission['native_binding']!=inputs['native_binding']):
        raise ValueError('CURRENT_SOURCE_AND_HISTORICAL_NEUTRAL_ADMISSION_MISMATCH')
    g.authorize_build(source_receipt,out,[g.resolve(view['image']),g.resolve(view['rgba'])],builder.__file__,
                      build_receipt=receipt,build_attempt=attempt,direction='E')
    builder_claim=g.claim_build_execution(attempt,receipt,builder.__file__,'E')
    permit={'schema':1,'stage':'verified_blender_child_permit',
            'inputs':g.ref(inputs_path),'handoff':g.ref(handoff_path),
            'runner_claim':runner_claim,'builder_claim':builder_claim,
            'source_receipt':inputs['source_receipt'],'source_green':view['image'],
            'source_rgba':view['rgba'],'neutral_admission':inputs['neutral_admission'],
            'calf_width_witness':inputs['calf_width_witness'],
            'verifier':g.ref(__file__),'production_ready':False,
            'note':'Exclusive one-child permit. A crash consumes this build attempt; do not rerun it.'}
    g.write(out/'BLENDER_CHILD_PERMIT.json',permit)
    return permit


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True)
    result=verify(parser.parse_args().out)
    print(result['stage'])
