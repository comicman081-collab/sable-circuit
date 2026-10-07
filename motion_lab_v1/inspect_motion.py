import bpy, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT.parent/'art_src/motion_reference/tripo_run_20260908/source/ORIGINAL_Run.glb'))
arm=next(o for o in bpy.data.objects if o.type=='ARMATURE')
rows=[]
for frame in [1,4,8,12,16,20,24]:
    bpy.context.scene.frame_set(frame)
    rows.append({'frame':frame,'bones':{n:list(arm.matrix_world@arm.pose.bones[n].head) for n in ['Root','Hip','L_Thigh','L_Calf','L_Foot','L_ToeBase','R_Thigh','R_Calf','R_Foot','R_ToeBase','Spine02','Head','L_Upperarm','R_Upperarm','L_Forearm','R_Forearm','L_Hand','R_Hand']}})
out={'actions':[(a.name,list(a.frame_range)) for a in bpy.data.actions],'samples':rows}
(ROOT/'reference/tripo_joints.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
