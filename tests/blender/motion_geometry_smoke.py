"""Synthetic skinned sole planes only; never source character art or promotable assets."""
import argparse
import json
import runpy
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser()
p.add_argument("--out",required=True)
p.add_argument("--root-follow",action="store_true")
args = p.parse_args(sys.argv[sys.argv.index("--")+1:])
out = Path(args.out).resolve()
if not out.is_relative_to(ROOT / "artifacts/motion_harness_audit/technical_fixtures"):
    raise ValueError("Synthetic smoke outputs must stay in the dedicated project fixture area")
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
armature = bpy.data.armatures.new("QA_Armature")
rig = bpy.data.objects.new("QA_Rig",armature)
bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bone = armature.edit_bones.new("QA_Foot")
bone.head = (0,0,0)
bone.tail = (0,0,1)
bpy.ops.object.mode_set(mode="OBJECT")
mesh = bpy.data.meshes.new("QA_SolePlanes")
mesh.from_pydata([(-.3,.2,0),(.3,.2,0),(.3,.4,0),(-.3,.4,0),
                  (-.3,-.2,0),(.3,-.2,0),(.3,-.4,0),(-.3,-.4,0)],[],[(0,1,2,3),(4,7,6,5)])
subject = bpy.data.objects.new("QA_SkinnedSoles",mesh)
bpy.context.collection.objects.link(subject)
group = subject.vertex_groups.new(name="QA_Foot")
group.add(list(range(8)),1,"REPLACE")
modifier = subject.modifiers.new("QA_Armature","ARMATURE")
modifier.object = rig
for frame, location in ((1,(0,0,0)),(2,(.2,0,.08))):
    # PoseBone.location is in rest-bone axes, whose Y points along the bone.
    # The fixture's displacement specification is in world axes.
    rig.pose.bones["QA_Foot"].location = armature.bones['QA_Foot'].matrix_local.to_3x3().inverted() @ Vector(location)
    rig.pose.bones["QA_Foot"].keyframe_insert(data_path="location",frame=frame)
body = bpy.data.objects.new("QA_BodyFrame",None)
bpy.context.collection.objects.link(body)
camera_data = bpy.data.cameras.new("QA_Camera")
camera = bpy.data.objects.new("QA_Camera",camera_data)
bpy.context.collection.objects.link(camera)
camera.location = (3,-4,5)
camera.rotation_euler = (-camera.location).to_track_quat("-Z","Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 2.0
scene = bpy.context.scene
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 1
scene.cycles.use_denoising = False
scene.world.color = (.4,.4,.4)
scene.unit_settings.scale_length = 1.0
if args.root_follow:
    # The scene itself authors both actual root travel and camera following.
    # The exporter only validates; it may not silently reposition either one.
    rig.parent=body;subject.parent=body;camera.parent=body
    for frame,location in ((1,(0,0,0)),(2,(1.25,-.5,0))):
        body.location=location;body.keyframe_insert('location',frame=frame)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/"SYNTHETIC_QA_NOT_CHARACTER.blend"))
config = {"skinned_mesh":subject.name,"body_coordinate_frame":body.name,
          "qa_fixture_only":True,
          "camera_space":"root_translation_locked" if args.root_follow else "world_locked",
          "sole_vertex_ids":{"left":[0,1,2,3],"right":[4,5,6,7]},
          "subject_sha256":"SYNTHETIC_QA_NOT_PRODUCTION","output":str(out/"geometry.json"),
          "render_receipt":str(out/"render_receipt.json"),"native_size":1920,"runtime_cell":384,
          "frames":[{"frame":i,"time_s":(i-1)/24,"master_image":str(out/f"native_{i}.png"),
                     "image":str(out/f"runtime_{i}.png")} for i in (1,2)]}
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as generation_gate
generation_gate.write(out/'fixture_provenance.json',{
    'status':'SYNTHETIC_QA_NOT_PRODUCTION','generator':generation_gate.ref(__file__),
    'blend':generation_gate.ref(out/'SYNTHETIC_QA_NOT_CHARACTER.blend')})
config['fixture_provenance']=generation_gate.ref(out/'fixture_provenance.json')
config_path = out/"config.json"
config_path.write_text(json.dumps(config,indent=2),encoding="utf-8")
sys.argv = ["blender","--","--config",str(config_path)]
runpy.run_path(str(ROOT/"tools/character_pipeline/export_evaluated_motion_geometry.py"),run_name="__main__")
print("SYNTHETIC_GEOMETRY_SMOKE_RENDERED")
