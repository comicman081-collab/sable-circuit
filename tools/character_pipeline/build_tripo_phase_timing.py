"""Convert measured Tripo phase events into explicit runtime frame boundaries.

Timing implementation input only. A technical contact report cannot approve
visible art, foot slip, walk animation, firing poses, or production pointers.
"""
import argparse
from pathlib import Path
import generation_harness as g
import calibrate_vrm_ual_ground_contact as contact

ROOT=Path(__file__).resolve().parents[2]
PHASES=('contact_l','down_l','passing_l','flight_l','contact_r','down_r','passing_r','flight_r')


def build(calibration_path):
    report=g.read(calibration_path)
    if report['status']!='PASS_TECHNICAL_PHASE_GUIDE_CANDIDATES_ONLY' or report['errors']:
        raise ValueError('TECHNICAL_PHASE_DISCOVERY_REQUIRED')
    for key in ('input_result','input_blend','contract','generator'):g.resolve(report[key])
    if report['generator']!=g.ref(Path(contact.__file__)):
        raise ValueError('CURRENT_CALIBRATOR_REQUIRED')
    phases,errors=contact._classify(report['samples'],g.read(g.resolve(report['contract'])))
    if errors or phases!=report['phase_candidates']:raise ValueError('PHASE_ROWS_DO_NOT_REPRODUCE')
    result=g.read(g.resolve(report['input_result']))
    if result.get('scope')!='TRIPO_PERIODIC_RETARGET_REFERENCE_NOT_SABLE_ART':raise ValueError('TRIPO_DERIVED_RESULT_REQUIRED')
    if report['input_blend']!=result['output_blend']:raise ValueError('BLEND_MISMATCH')
    rows={r['sample']:r for r in report['samples']}
    duration=rows[max(rows)]['time_s']-rows[0]['time_s']
    if abs(duration-result['derived_period_s'])>1e-8:raise ValueError('CYCLE_DURATION_MISMATCH')
    origin=rows[phases['contact_l']]['time_s']
    starts=[((rows[phases[phase]]['time_s']-origin)/duration)%1 for phase in PHASES]
    if starts[0]!=0 or any(b<=a for a,b in zip(starts,starts[1:])):raise ValueError('ORDERED_PHASE_EVENTS_REQUIRED')
    # Three distinct temporal samples per named interval, not repeated pixels.
    # Future art must provide its own distinct reviewed frames at these times.
    frame_starts=[start+(end-start)*j/3 for start,end in zip(starts,starts[1:]+[1.]) for j in range(3)]
    speeds=g.read(ROOT/'tools/character_pipeline/motion_contract.json')['actors']['CHR_PROTO_03']
    return {'schema':1,'scope':'TRIPO_RUN_TIMING_FOR_IMPLEMENTATION_TESTS',
        'production_ready':False,'generator':g.ref(__file__),'calibration':g.ref(calibration_path),
        'retarget_result':report['input_result'],'source_pack':result['source_pack'],
        'cycle_duration_s':duration,'phase_names':list(PHASES),'phase_event_starts':starts,
        'source_sample_indices':[phases[name] for name in PHASES],
        'frames':len(frame_starts),'fps':len(frame_starts)/duration,'phase_starts':frame_starts,
        'actor_id':'CHR_PROTO_03','independent_actor_run_speed_px_s':speeds['run'],
        'runtime_cycle_distance_px':speeds['run']*duration,
        'limitations':['Timing only; no supplied walk clip.',
            'Contact height PASS does not establish horizontal no-slip or visual gait PASS.',
            'Every visible SABLE frame and move/aim/fire channel still requires its own art and review.']}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--calibration',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    out=g.local(a.out)
    if out.exists():raise ValueError('FRESH_TIMING_OUTPUT_REQUIRED')
    g.write(out,build(a.calibration));print(out)
