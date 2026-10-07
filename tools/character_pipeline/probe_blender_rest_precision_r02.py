"""In-memory bone-matrix diagnostic only; no render, saved blend, or source edits."""
import json
from pathlib import Path
import sys
import bpy
import numpy as np
from mathutils import Matrix,Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g

out=Path(sys.argv[sys.argv.index('--')+1])
base=ROOT/'artifacts/quarantine/generation_diagnostics/mica_E_connected_surface_r01/SOURCE_SURFACE_NEUTRAL.blend'
probe=ROOT/'artifacts/quarantine/generation_diagnostics/mica_E_projected_visible_sole_math_r01/PROBE.json'
r=g.read(probe)
rest=np.load(g.resolve(r['proposed_rest']),allow_pickle=False)
support=g.read(g.resolve(r['inputs']['support']))
skin=g.read(g.resolve(support['inputs']['skin']))
joint=g.read(g.resolve(support['inputs']['joints']))
heads=joint['blender_world_bone_heads']
bpy.ops.wm.open_mainfile(filepath=str(base),load_ui=False)
rig=bpy.data.objects['CHR_PROTO_03_SourceRig']
bpy.context.view_layer.objects.active=rig
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
tails={'pelvis':'spine_01','spine_01':'spine_02','spine_02':'spine_03','spine_03':'neck_01','neck_01':'Head'}
for side in ['l','r']:
    tails.update({a+'_'+side:b+'_'+side for a,b in [('thigh','calf'),('calf','foot'),('foot','ball'),('clavicle','upperarm'),('upperarm','lowerarm'),('lowerarm','hand')]})
edited={}
for i,row in enumerate(skin['bone_order']):
    bone=rig.data.edit_bones[row['name']]
    length=float(np.linalg.norm(np.asarray(heads[tails[row['name']]])-heads[row['name']])) if row['name'] in tails else .07
    bone.head=Vector(rest[i,:3,3])
    bone.tail=bone.head+Vector(rest[i,:3,1])*length
    bone.align_roll(Vector(rest[i,:3,2]))
    edited[row['name']]={'edit_error':float(np.abs(np.asarray(bone.matrix)-rest[i]).max()),'use_connect':bone.use_connect}
bpy.ops.object.mode_set(mode='OBJECT')
for i,row in enumerate(skin['bone_order']):
    edited[row['name']].update(actual_error=float(np.abs(np.asarray(rig.data.bones[row['name']].matrix_local)-rest[i]).max()),
        actual_matrix=np.asarray(rig.data.bones[row['name']].matrix_local).tolist(),expected_matrix=rest[i].tolist())
g.write(out/'DIAGNOSTIC.json',{'inputs':{'blend':g.ref(base),'probe':g.ref(probe),'diagnostic':g.ref(__file__)},'bones':edited,
    'scope':'in-memory REST setter numerical diagnosis only; no assets authored'})
