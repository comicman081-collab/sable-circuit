"""Run one reviewed MICA E contact pose through the exact build-plan gate."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
import generation_harness as g
import pose_projected_source_probe as builder
import source_art_intake as intake
import historical_neutral_reuse_admission as neutral_reuse


def run(args):
    out = g.local(args.out)
    if args.direction != 'E':
        raise ValueError('THIS_FIRST_POSE_RUNNER_IS_E_ONLY')
    source_receipt = g.resolve(g.ref(args.source_receipt))
    build_receipt = g.resolve(g.ref(args.build_receipt))
    build_attempt = g.resolve(g.ref(args.build_attempt))
    plan = g.verify_build_attempt(build_attempt, build_receipt)
    if plan.get('neutral_admission') != g.ref(args.neutral_admission):
        raise ValueError('EXACT_PLAN_NEUTRAL_ADMISSION_REQUIRED')
    source = intake.authority(source_receipt)
    view = next((item for manifest in source['sources'] for item in manifest['views']
                 if item['id'] == args.direction), None)
    if not view or not view.get('rgba'):
        raise ValueError('EXACT_REVIEWED_E_GREEN_AND_RGBA_REQUIRED')
    admission=neutral_reuse.verify(g.resolve(g.ref(args.neutral_admission)))
    if (admission['source_receipt']!=g.ref(source_receipt) or admission['source_green']!=view['image']
            or admission['source_rgba']!=view['rgba'] or admission['neutral']!=g.ref(args.neutral)
            or admission['anchor']!=g.ref(args.anchor) or admission['box_capture']!=g.ref(args.box_capture)
            or admission['native_binding']!=g.ref(args.native_binding)):
        raise ValueError('CURRENT_SOURCE_AND_HISTORICAL_NEUTRAL_ADMISSION_MISMATCH')
    # Reject a swapped source receipt or output root before Blender launches.
    # The external verifier repeats this later for its permit, but the runner
    # owns process creation and must fail a malformed invocation at this edge.
    g.authorize_build(source_receipt,out,[g.resolve(view['image']),g.resolve(view['rgba'])],__file__,
                      build_receipt=build_receipt,build_attempt=build_attempt,direction=args.direction)
    runner_claim = g.claim_build_execution(build_attempt, build_receipt, __file__, args.direction)
    # Blender is only launched after this runner has created an immutable input
    # handoff.  The child calls the project-Python verifier before importing a
    # scene; that verifier repeats intake/admission checks and claims the child.
    out.mkdir(parents=True, exist_ok=False)
    (out / 'cache').mkdir()
    inputs = {key: g.ref(path) for key, path in builder.implementation().items()}
    inputs.update(
        source_receipt=g.ref(source_receipt),
        source_green=view['image'],
        source_rgba=view['rgba'],
        build_receipt=g.ref(build_receipt),
        build_attempt=g.ref(build_attempt),
        neutral=g.ref(args.neutral),
        anchor=g.ref(args.anchor),
        box_capture=g.ref(args.box_capture),
        native_binding=g.ref(args.native_binding),
        neutral_admission=g.ref(args.neutral_admission),
    )
    runtime=Path(sys.executable).resolve()
    handoff = {'stage':'reviewed_blender_child_handoff','build_receipt':g.ref(build_receipt),
               'build_attempt':g.ref(build_attempt),'runner':g.ref(__file__),
               'builder':g.ref(builder.__file__),'verifier':inputs['handoff_verifier'],'direction':args.direction,
               'source_receipt':g.ref(source_receipt),'source_green':view['image'],
               'source_rgba':view['rgba'],'runner_claim':runner_claim,'readonly_inputs':plan['readonly_inputs'],
               'neutral_admission':g.ref(args.neutral_admission),
               'output_root':plan['output_root'],
               'python_runtime':str(runtime),'python_runtime_sha256':hashlib.sha256(runtime.read_bytes()).hexdigest(),
               'child_permit_path':(out/'BLENDER_CHILD_PERMIT.json').relative_to(ROOT).as_posix()}
    g.write(out / 'EXECUTION_HANDOFF.json', handoff)
    inputs['execution_handoff'] = g.ref(out / 'EXECUTION_HANDOFF.json')
    g.write(out / 'INPUTS.json', inputs)
    env = os.environ.copy()
    for key in ('TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA', 'XDG_CACHE_HOME', 'XDG_DATA_HOME',
                'BLENDER_USER_CONFIG', 'BLENDER_USER_SCRIPTS', 'PYTHONPYCACHEPREFIX'):
        env[key] = str(out / 'cache')
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', OMP_NUM_THREADS='2')
    with (out / 'blender.log').open('w', encoding='utf8') as log:
        subprocess.run([
            str(ROOT / 'tools/blender/5.2.1/blender.exe'), '--background', '--factory-startup', '--disable-autoexec',
            '--offline-mode', '--threads', '2', '--python-exit-code', '2', '--python',
            str(ROOT / 'tools/character_pipeline/pose_projected_source_probe.py'), '--', '--inside', '--out', str(out),
            '--direction', args.direction,
        ], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=240, check=True,
           creationflags=subprocess.CREATE_NO_WINDOW)
    print('ONE_REVIEWED_MICA_E_CONTACT_POSE_CAPTURED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-receipt', required=True)
    parser.add_argument('--build-receipt', required=True)
    parser.add_argument('--build-attempt', required=True)
    parser.add_argument('--neutral', required=True)
    parser.add_argument('--anchor', required=True)
    parser.add_argument('--box-capture', required=True)
    parser.add_argument('--native-binding', required=True)
    parser.add_argument('--neutral-admission', required=True)
    parser.add_argument('--direction', required=True)
    parser.add_argument('--out', required=True)
    run(parser.parse_args())
