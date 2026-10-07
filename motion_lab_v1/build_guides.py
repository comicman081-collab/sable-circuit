"""Export actual UAL joints and render six distinct pose guides in Blender.

These neutral mannequins are construction references, never character artwork.
"""
import bpy, math, json, sys
from mathutils import Vector, Quaternion
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'reference/ual_guides'; OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT.parent/'assets/external/quaternius/ual1/UAL1_Standard.glb'))
arm=next(o for o in bpy.data.objects if o.type=='ARMATURE')
mesh=next(o for o in bpy.data.objects if o.type=='MESH')
scene=bpy.context.scene
print('ACTION',[(a.name,list(a.frame_range)) for a in bpy.data.actions],flush=True)
print('REST',[(n,list(arm.matrix_world@arm.data.bones[n].head_local)) for n in ['pelvis','Head','thigh_l','calf_l','foot_l','ball_l','hand_r','hand_l']],flush=True)
# Strip the importer-created NLA tracks before selecting exact actions.
for t in list(arm.animation_data.nla_tracks):arm.animation_data.nla_tracks.remove(t)
names=['root','pelvis','spine_01','spine_02','spine_03','neck_01','Head','clavicle_l','upperarm_l','lowerarm_l','hand_l','clavicle_r','upperarm_r','lowerarm_r','hand_r','thigh_l','calf_l','foot_l','ball_l','thigh_r','calf_r','foot_r','ball_r']
tracks={}
for clip in ['Walk_Loop','Jog_Fwd_Loop','Sprint_Loop','Pistol_Aim_Neutral','Pistol_Reload','Pistol_Shoot']:
    action=bpy.data.actions[clip];arm.animation_data.action=action
    if action.slots:arm.animation_data.action_slot=action.slots[0]
    start,end=action.frame_range;rows=[]
    for i in range(60):
        value=start+(end-start)*i/60
        scene.frame_set(int(value),subframe=value%1)
        rows.append({n:list(arm.matrix_world@arm.pose.bones[n].head) for n in names})
    tracks[clip]={'frameRange':[start,end],'fps':scene.render.fps,'joints':rows}
(OUT/'motion_tracks.json').write_text(json.dumps(tracks,separators=(',',':')))
if '--inspect-only' in sys.argv:raise SystemExit
# Render simple, anatomically connected capsules from sampled real joints. This
# also avoids transferring any mannequin design into the final artwork request.
for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
grey=mat('Neutral upper body',(.49,.51,.53));near=mat('Right leg',(.68,.39,.26));far=mat('Left leg',(.25,.48,.66));gun=mat('Rifle alignment only',(.15,.17,.18))
created=[]
def sphere(p,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=p);o=bpy.context.object;o.scale=scale;o.data.materials.append(material);created.append(o);return o
def bone(a,b,r,material):
    d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=r*.88,radius2=r,depth=d.length,location=(Vector(a)+Vector(b))*.5);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);created.append(o);sphere(a,(r,r,r),material);return o
def box(p,scale,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.scale=scale;o.data.materials.append(material);created.append(o);return o
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('White');scene.world.color=(.95,.95,.95)
scene.render.resolution_x=768;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=2.05
metadata={}
for clip in ['Walk_Loop','Jog_Fwd_Loop']:
  for direction,angle in [('E',0),('SE',45),('S',90),('SW',135),('W',180),('NW',225),('N',270),('NE',315)]:
    if '--east-only' in sys.argv and direction!='E':continue
    # World body forward is -Y; camera at -X gives forward screen-right.
    theta=math.radians(angle);camera.location=(-5*math.cos(theta),-5*math.sin(theta),3.23);look=Vector((0,0,.9));camera.rotation_euler=(look-camera.location).to_track_quat('-Z','Y').to_euler()
    for i in range(6):
      for o in created:bpy.data.objects.remove(o,do_unlink=True)
      created=[]
      row=tracks[clip]['joints'][i*10];hip=Vector(row['pelvis']);offset=Vector((hip.x,hip.y,0))
      # UAL is already metre-scaled; maintain source ground, limb lengths and bob.
      points={n:Vector(p)-offset for n,p in row.items()};z=points['pelvis'].z
      sphere(points['pelvis'],(.145,.105,.13),grey)
      torso0=Vector((0,0,z+.06));torso1=Vector((0,-.025,z+.43));bone(torso0,torso1,.16,grey)
      sphere((0,-.07,z+.65),(.10,.112,.145),grey)
      for suffix,material in [('l',far),('r',near)]:
        h,k,a,t=[points[n+'_'+suffix] for n in ['thigh','calf','foot','ball']]
        bone(h,k,.073,material);bone(k,a,.055,material);bone(a,t,.045,material)
        v=Vector(t)-Vector(a);centre=(a+t)*.5;centre.z-=.022;shoe=sphere(centre,(.051,.13,.048),material)
      # Fixed two-handed rifle aim over the genuine animated lower-body samples.
      sr=Vector((-.19,-.01,z+.40));sl=Vector((.19,-.01,z+.40))
      er=Vector((-.23,-.13,z+.18));el=Vector((.23,-.23,z+.19))
      hr=Vector((-.045,-.33,z+.37));hl=Vector((.015,-.52,z+.35))
      for a,b,c in [(sr,er,hr),(sl,el,hl)]:bone(a,b,.049,grey);bone(b,c,.039,grey);sphere(c,(.041,.043,.043),grey)
      box((-.025,-.42,z+.405),(.055,.68,.08),gun);box((-.025,-.16,z+.39),(.075,.19,.12),gun)
      path=OUT/f'{direction}_{clip}_{i}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    metadata[f'{direction}_{clip}']={'nativeFrame':[768,1024],'frames':6,'source':'UAL1_Standard.glb','action':clip,'samples':[0,10,20,30,40,50]}
(OUT/'guide_manifest.json').write_text(json.dumps(metadata,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'guide_scene.blend'))
