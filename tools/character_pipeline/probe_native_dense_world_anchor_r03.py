"""Numeric-only actual source-sole XY anchoring with fixed hip and limb lengths."""
from pathlib import Path
import numpy as np
import generation_harness as g
from limb_target_solver import solve
from probe_source_rest_axis_alignment import minimal_rotation
from source_surface_sampling import sample_positions
from dense_native_pose_targets import densify

ROOT = Path(__file__).resolve().parents[2]


def run():
    prior_path = ROOT/'artifacts/quarantine/generation_diagnostics/mica_E_projected_visible_sole_math_r01/PROBE.json'
    diagnosis_path = ROOT/'artifacts/tripo_reference_review/motion_r13/projected_numeric_audit_r01/SLIP_ISOLATION_R2.json'
    prior, diagnosis = g.read(prior_path), g.read(diagnosis_path)
    for reference in prior['inputs'].values():
        g.resolve(reference)
    support = g.read(g.resolve(prior['inputs']['support']))
    skin = g.read(g.resolve(support['inputs']['skin']))
    source = g.read(g.resolve(prior['inputs']['source']))
    positions = np.load(g.resolve(support['proposed_positions']),allow_pickle=False)
    base = np.load(g.resolve(prior['proposed_poses']),allow_pickle=False)
    rest = np.load(g.resolve(prior['proposed_rest']),allow_pickle=False)
    native_path = ROOT/'artifacts/quarantine/generation_diagnostics/mica_E_native_binding_inspection_r01/BINDING_INSPECTION.json'
    native = g.read(native_path)
    native_rest = np.load(g.resolve(native['actual_rest']),allow_pickle=False)
    positions = np.load(g.resolve(native['actual_positions']),allow_pickle=False)
    base = densify(base,[row['parent'] for row in skin['bone_order']],rest,native_rest)
    rest = native_rest
    old_samples = prior['samples']
    prior['samples'] = []
    for number in range(97):
        a,b = min(number//2,48),min(number//2+1,48)
        u = .5 if number%2 else 0
        prior['samples'].append({'feet':{side:{'desired_clearance_m':(1-u)*old_samples[a]['feet'][side]['desired_clearance_m']+u*old_samples[b]['feet'][side]['desired_clearance_m']} for side in ['l','r']}})
    inverse = np.linalg.inv(rest)
    points = np.c_[positions,np.ones(len(positions))]
    weights = np.asarray(skin['weights']).reshape(-1,4)
    bones = np.asarray(skin['bones']).reshape(-1,4)
    lookup = {row['name']:i for i,row in enumerate(skin['bone_order'])}
    clip = source['clips']['run/forward']
    count = len(base)-1
    if count != 96 or not np.allclose(base[0],base[-1],atol=1e-12):
        raise ValueError('EXACT_CLOSED_97_SAMPLE_TARGET_CURVE_REQUIRED')
    distance = float(clip['distance_m'])*prior['scale_ratio']
    speed = distance/float(clip['duration_s'])
    if abs(speed-diagnosis['derived_speed_m_s']) > 1e-9:
        raise ValueError('EXACT_SOURCE_DERIVED_TRAVEL_REQUIRED')
    output = base.copy()
    evidence, failures = {}, []
    floor = min(float(sample_positions(positions,binding)[:,2].min()) for binding in prior['visible_sole_bindings'].values())
    for side in ['l','r']:
        hi,ki,fi,bi = [lookup[name+'_'+side] for name in ['thigh','calf','foot','ball']]
        lengths = [np.linalg.norm(rest[b,:3,3]-rest[a,:3,3]) for a,b in [(hi,ki),(ki,fi)]]
        binding = prior['visible_sole_bindings'][side]
        vertices = np.unique(np.asarray(binding['vertices']).ravel())
        remap = {int(v):i for i,v in enumerate(vertices)}
        local_binding = dict(binding)
        local_binding['vertices'] = [[remap[v] for v in face] for face in binding['vertices']]
        def samples(matrices):
            deform = matrices@inverse
            evaluated = (np.einsum('nkij,nj->nki',deform[bones[vertices]],points[vertices])*weights[vertices,:,None]).sum(axis=1)
            return sample_positions(evaluated,local_binding)[:,:3]
        window = diagnosis['sides'][side]['support_window']
        start,end = window['contact']*2,window['toeoff']*2
        duration = (end-start)%count
        while duration < count-6 and prior['samples'][(start+duration+1)%count]['feet'][side]['desired_clearance_m'] <= .004:
            duration += 1
        release_span = 8
        release_end = (start+duration+release_span)%count
        baseline = np.asarray([samples(m) for m in base])
        anchor_index = int(np.argmin(baseline[start,:,2]))
        anchor_start = baseline[start,anchor_index,:2]
        release_position = anchor_start-np.array([distance*duration/count,0])
        release_target = baseline[release_end,anchor_index,:2]
        release_velocity = (baseline[(release_end+1)%count,anchor_index,:2]-baseline[(release_end-1)%count,anchor_index,:2])/2
        rows = []
        for number in range(count):
            elapsed = (number-start)%count
            target = baseline[number,anchor_index,:2].copy()
            support_active = elapsed <= duration
            if support_active:
                target = anchor_start-np.array([distance*elapsed/count,0])
            elif elapsed < duration+release_span:
                u = (elapsed-duration)/release_span
                target = ((2*u**3-3*u**2+1)*release_position
                    +(u**3-2*u**2+u)*release_span*np.array([-distance/count,0])
                    +(-2*u**3+3*u**2)*release_target
                    +(u**3-u**2)*release_span*release_velocity)
            wanted_z = floor+prior['samples'][number]['feet'][side]['desired_clearance_m']
            hip = base[number,hi,:3,3].copy()
            knee_hint = base[number,ki,:3,3].copy()
            def evaluate(goal):
                solved = solve(hip,goal,knee_hint,*lengths)
                matrices = output[number].copy()
                for index,a,b,ra,rb in [(hi,hip,solved['knee'],rest[hi,:3,3],rest[ki,:3,3]),
                    (ki,solved['knee'],goal,rest[ki,:3,3],rest[fi,:3,3])]:
                    matrices[index,:3,:3] = minimal_rotation(rb-ra,b-a)@rest[index,:3,:3]
                    matrices[index,:3,3] = a
                matrices[fi,:3,3] = goal
                matrices[bi,:3,3] = (matrices[fi]@inverse[fi]@rest[bi,:,3])[:3]
                visible = samples(matrices)
                error = np.r_[visible[anchor_index,:2]-target,visible[:,2].min()-wanted_z]
                return matrices,error
            goal = base[number,fi,:3,3].copy()
            try:
                for iteration in range(10):
                    matrices,error = evaluate(goal)
                    if np.linalg.norm(error) < 1e-7:
                        break
                    jacobian = np.column_stack([(evaluate(goal+np.eye(3)[axis]*1e-6)[1]-error)/1e-6 for axis in range(3)])
                    goal -= np.linalg.solve(jacobian,error)
                if np.linalg.norm(error) >= 1e-7:
                    raise ValueError('VISIBLE_ANCHOR_SOLVE_DID_NOT_CONVERGE')
                output[number] = matrices
                rows.append({'sample':number,'support':support_active,'anchor_xy_residual_m':float(np.linalg.norm(error[:2])),
                    'sole_height_residual_m':float(abs(error[2])),
                    'ankle_correction_m':(goal-base[number,fi,:3,3]).tolist(),
                    'remaining_reach_m':float(sum(lengths)-np.linalg.norm(goal-hip))})
            except (ValueError,np.linalg.LinAlgError) as error:
                failures.append({'side':side,'sample':number,'error':str(error)})
        evidence[side] = {'window':window,'effective_support_end':(start+duration)%count,'release_span_samples':release_span,'anchor_binding_index':anchor_index,
            'anchor_source_pixel':binding['pixels'][anchor_index] if 'pixels' in binding else None,
            'rows':rows,'maximum_ankle_correction_m':max((np.linalg.norm(r['ankle_correction_m']) for r in rows),default=None)}
    output[-1] = output[0]
    out = ROOT/'artifacts/quarantine/generation_diagnostics/mica_E_native_dense_world_anchor_math_r03'
    out.mkdir(exist_ok=False)
    np.save(out/'PROPOSED_GLOBAL_MATRICES.npy',output,allow_pickle=False)
    g.write(out/'PROBE.json',{'scope':'numeric source-visible anchor hypothesis only; no native or runtime approval',
        'inputs':{'prior':g.ref(prior_path),'diagnosis':g.ref(diagnosis_path),'probe':g.ref(__file__),
            'solver':g.ref(ROOT/'tools/character_pipeline/limb_target_solver.py'),
            'sampler':g.ref(ROOT/'tools/character_pipeline/source_surface_sampling.py'),
            'native_binding':g.ref(native_path),'densifier':g.ref(ROOT/'tools/character_pipeline/dense_native_pose_targets.py'),'rotation_helper':g.ref(ROOT/'tools/character_pipeline/probe_source_rest_axis_alignment.py')},
        'target_sample_count':97,'measured_reference_sample_count':49,'actual_native_rest':native['actual_rest'],'source_derived_speed_m_s':speed,'cycle_distance_m':distance,'fixed_neutral_floor_m':floor,
        'root_floor_correction':False,'limb_stretch':False,'weights_changed':False,'sides':evidence,
        'failures':failures,'proposed_poses':g.ref(out/'PROPOSED_GLOBAL_MATRICES.npy'),
        'production_ready':False,'endpoint_policy':'sample96 is exact cyclic sample0; interval derivatives require independent review'})
    print('VISIBLE_SOURCE_ANCHOR_NUMERIC_FAILURES',len(failures))


if __name__ == '__main__':
    run()
