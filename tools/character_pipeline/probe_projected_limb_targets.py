"""Fixed-length 49-phase feasibility on proposed support; not native motion export."""
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
import generation_harness as g
from probe_source_rest_axis_alignment import global_rows, minimal_rotation
from limb_target_solver import solve

ROOT = Path(__file__).resolve().parents[2]


def bone_matrix(head, tail):
    y = np.asarray(tail)-head
    y /= np.linalg.norm(y)
    hint = np.array([1.,0,0]) if abs(y[0]) < .95 else np.array([0.,1,0])
    x = hint-y*np.dot(hint,y)
    x /= np.linalg.norm(x)
    result = np.eye(4)
    result[:3,:3] = np.column_stack((x,y,np.cross(x,y)))
    result[:3,3] = head
    return result


def run():
    support_path = ROOT/'artifacts/quarantine/generation_diagnostics/mica_E_projection_surface_math_r01/PROBE.json'
    support = g.read(support_path)
    for reference in support['inputs'].values():
        g.resolve(reference)
    joint = g.read(g.resolve(support['inputs']['joints']))
    source_path = g.resolve(joint['inputs']['reference'])
    source = g.read(source_path)
    skin = g.read(g.resolve(support['inputs']['skin']))
    calibration_path = ROOT/'artifacts/quarantine/generation_diagnostics/tripo_support_anchor_calibration_r02/contact_calibration.json'
    calibration = g.read(calibration_path)
    positions = np.load(g.resolve(support['proposed_positions']),allow_pickle=False)
    points = np.c_[positions,np.ones(len(positions))]
    weights = np.asarray(skin['weights']).reshape(-1,4)
    indices = np.asarray(skin['bones']).reshape(-1,4)
    uv = np.asarray(skin['uv']).reshape(-1,2)*[1024,1536]
    # Original-rubber regions measured in the previous independent audit. Their
    # proposed neutral physical geometry defines one fixed floor for this probe.
    rois = {'l':np.where((uv[:,0]>600)&(uv[:,0]<801)&(uv[:,1]>1450)&(uv[:,1]<1478))[0],
            'r':np.where((uv[:,0]>165)&(uv[:,0]<268)&(uv[:,1]>1470)&(uv[:,1]<1493))[0]}
    floor = min(float(positions[v,2].min()) for v in rois.values())
    rows = skin['bone_order']
    lookup = {r['name']:i for i,r in enumerate(rows)}
    heads = {k:np.asarray(v) for k,v in joint['blender_world_bone_heads'].items()}
    tails = {'pelvis':'spine_01','spine_01':'spine_02','spine_02':'spine_03',
             'spine_03':'neck_01','neck_01':'Head'}
    for side in ['l','r']:
        tails.update({a+'_'+side:b+'_'+side for a,b in [('thigh','calf'),('calf','foot'),
            ('foot','ball'),('clavicle','upperarm'),('upperarm','lowerarm'),('lowerarm','hand')]})
    rest = []
    for row in rows:
        name = row['name']
        if name in tails:
            tail = heads[tails[name]]
        elif name.startswith('ball_'):
            forward = heads[name]-heads['foot_'+name[-1]]
            forward[2] = 0
            tail = heads[name]+forward/np.linalg.norm(forward)*.07
        else:
            tail = heads[name]+[0,0,.07]
        rest.append(bone_matrix(heads[name],tail))
    inverse = np.linalg.inv(rest)
    axes = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],dtype=float)
    align = np.eye(4)
    align[:3,:3] = Rotation.from_euler('z',90,degrees=True).as_matrix()
    def reference_global(poses):
        return {r['name']:align@axes.T@m@axes for r,m in zip(source['bone_order'],global_rows(source['bone_order'],poses))}
    source_rest = reference_global([r['rest'] for r in source['bone_order']])
    def leg_length(data,side):
        return sum(np.linalg.norm(data[b+'_'+side][:3,3]-data[a+'_'+side][:3,3])
                   for a,b in [('thigh','calf'),('calf','foot')])
    rest_dict = {r['name']:rest[i] for i,r in enumerate(rows)}
    ratio = sum(leg_length(rest_dict,s) for s in ['l','r'])/sum(leg_length(source_rest,s) for s in ['l','r'])
    lengths = {s:[np.linalg.norm(heads['calf_'+s]-heads['thigh_'+s]),
                  np.linalg.norm(heads['foot_'+s]-heads['calf_'+s])] for s in ['l','r']}
    samples, failures, matrices_out = [], [], []
    for number,frame in enumerate(source['clips']['run/forward']['frames']):
        ref = reference_global(frame['poses'])
        current = []
        for i,row in enumerate(rows):
            name,parent = row['name'],row['parent']
            matrix = rest[i].copy()
            if parent < 0:
                matrix[:3,3] += (ref['pelvis'][:3,3]-source_rest['pelvis'][:3,3])*ratio
                matrix[:3,:3] = ref['pelvis'][:3,:3]@np.linalg.inv(source_rest['pelvis'][:3,:3])@matrix[:3,:3]
            else:
                matrix[:3,3] = (current[parent]@inverse[parent]@rest[i][:,3])[:3]
            current.append(matrix)
        row_result = {'sample':number,'feet':{}}
        for side,label in [('l','left'),('r','right')]:
            hi,ki,fi,bi = [lookup[name+'_'+side] for name in ['thigh','calf','foot','ball']]
            hip = current[hi][:3,3].copy()
            goal = heads['thigh_'+side]+(ref['foot_'+side][:3,3]-source_rest['thigh_'+side][:3,3])*ratio
            knee_hint = hip+(ref['calf_'+side][:3,3]-ref['thigh_'+side][:3,3])*ratio
            foot_rotation = minimal_rotation(rest[fi][:3,1],ref['foot_'+side][:3,1])@rest[fi][:3,:3]
            ball_rotation = minimal_rotation(rest[bi][:3,1],ref['ball_'+side][:3,1])@rest[bi][:3,:3]
            selected = rois[side]
            rigid_offset = (foot_rotation@(inverse[fi]@points[selected].T)[:3]).T[:,2].min()
            wanted = calibration['samples'][number]['sole_clearance_m'][label]*ratio
            goal[2] = floor+wanted-rigid_offset
            residual = None
            for iteration in range(6):
                try:
                    solved = solve(hip,goal,knee_hint,*lengths[side])
                except ValueError as error:
                    failures.append({'sample':number,'side':side,'error':str(error),
                        'reach_ratio':float(np.linalg.norm(goal-hip)/sum(lengths[side]))})
                    break
                for index,start,end,rest_start,rest_end in [(hi,hip,solved['knee'],heads['thigh_'+side],heads['calf_'+side]),
                        (ki,solved['knee'],goal,heads['calf_'+side],heads['foot_'+side])]:
                    current[index][:3,:3] = minimal_rotation(rest_end-rest_start,end-start)@rest[index][:3,:3]
                    current[index][:3,3] = start
                current[fi][:3,:3] = foot_rotation
                current[fi][:3,3] = goal
                current[bi][:3,:3] = ball_rotation
                current[bi][:3,3] = (current[fi]@inverse[fi]@rest[bi][:,3])[:3]
                deform = np.asarray(current)@inverse
                evaluated = (np.einsum('nkij,nj->nki',deform[indices[selected]],points[selected]) * weights[selected,:,None]).sum(axis=1)
                measured = float(evaluated[:,2].min()-floor)
                residual = wanted-measured
                if abs(residual) <= .0001:
                    break
                goal[2] += residual
            row_result['feet'][side] = {'desired_clearance_m':wanted,'residual_m':residual,
                'knee':current[ki][:3,3].tolist(),'ankle':current[fi][:3,3].tolist()}
        samples.append(row_result)
        matrices_out.append(np.asarray(current))
    output = ROOT/'artifacts/quarantine/generation_diagnostics/mica_E_projected_ik_math_r01'
    output.mkdir(exist_ok=False)
    np.save(output/'PROPOSED_GLOBAL_MATRICES.npy',matrices_out,allow_pickle=False)
    np.save(output/'PROPOSED_REST_MATRICES.npy',rest,allow_pickle=False)
    g.write(output/'PROBE.json',{'inputs':{'support':g.ref(support_path),'source':g.ref(source_path),
        'calibration':g.ref(calibration_path),'probe':g.ref(__file__),'solver':g.ref(ROOT/'tools/character_pipeline/limb_target_solver.py')},
        'scale_ratio':ratio,'fixed_neutral_floor_m':floor,'root_floor_correction':False,'limb_stretch':False,
        'failures':failures,'samples':samples,'maximum_residual_m':max(abs(f['residual_m']) for s in samples for f in s['feet'].values() if f['residual_m'] is not None),
        'loop_global_matrix_max_error':float(np.abs(matrices_out[-1]-matrices_out[0]).max()),
        'proposed_rest':g.ref(output/'PROPOSED_REST_MATRICES.npy'),
        'proposed_poses':g.ref(output/'PROPOSED_GLOBAL_MATRICES.npy'),
        'scope':'numeric hypothesis only, actual Blender/independent unused sole validation still required',
        'production_ready':False})
    print('UNREACHABLE_SOLVES',len(failures),'FIXED_FLOOR',floor)


if __name__ == '__main__':
    run()
