"""Render licensed prop geometry for the 2.5D app; no AI artwork or model mutation."""
from pathlib import Path
import hashlib
import json
import sys
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[2]
INTAKE=ROOT/'third_party/karchive/site7_props_20260919'
OUT=ROOT/'assets/environments/site7/karchive_props_v1'
QA=ROOT/'qa/karchive_props_20260919'
OUT.mkdir(parents=True,exist_ok=True)
license_manifest=json.loads((INTAKE/'model-license-manifest.json').read_text('utf-8'))
spec={'schema':1, 'source':'licensed kArchive GLB renders, user-authorized 2026-09-19',
      'native_resolution':[1920,1080], 'attribution':license_manifest['attribution'], 'props':{}}
for item in license_manifest['assets']:
    source=ROOT/item['copy']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==item['sha256']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.temporary_directory=str(QA/'tmp')
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.device='CPU'
    scene.cycles.samples=24
    scene.cycles.use_denoising=True
    scene.cycles.max_bounces=4
    scene.render.threads_mode='FIXED'
    scene.render.threads=6
    scene.render.resolution_x=1920
    scene.render.resolution_y=1080
    scene.render.resolution_percentage=100
    scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGBA'
    scene.world=bpy.data.worlds.new('SITE7 ambient')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.17,.20,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.38
    scene.view_settings.view_transform='AgX'
    bpy.ops.import_scene.gltf(filepath=str(source))
    meshes=[o for o in scene.objects if o.type=='MESH']
    points=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo=Vector([min(p[a] for p in points) for a in range(3)])
    hi=Vector([max(p[a] for p in points) for a in range(3)])
    center=(lo+hi)/2
    extent=max(hi-lo)
    camera_data=bpy.data.cameras.new('Isometric prop camera')
    camera=bpy.data.objects.new('Isometric prop camera',camera_data)
    scene.collection.objects.link(camera)
    camera.location=center+Vector((4.5,-7,5)).normalized()*extent*5
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.type='ORTHO'
    camera_data.clip_end=max(100,extent*20)
    view=camera.rotation_euler.to_matrix().inverted()
    projected=[view@(p-center) for p in points]
    w=max(p.x for p in projected)-min(p.x for p in projected)
    h=max(p.y for p in projected)-min(p.y for p in projected)
    camera_data.ortho_scale=max(w,h*1920/1080)*1.18
    scene.camera=camera
    for name,offset,power,color in [('Key',(3,-4,6),480,(.76,.89,1)),('Fill',(-4,-1,3),130,(.54,.74,.83)),('Rim',(1,4,5),240,(.58,.91,1))]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power*extent*extent;data.shape='DISK';data.size=3*extent;data.color=color
        light=bpy.data.objects.new(name,data);scene.collection.objects.link(light)
        light.location=center+Vector(offset)*extent
        light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    foot=world_to_camera_view(scene,camera,Vector((center.x,center.y,lo.z)))
    ground=[]
    for x,y in [(lo.x,lo.y),(hi.x,lo.y),(hi.x,hi.y),(lo.x,hi.y)]:
        p=world_to_camera_view(scene,camera,Vector((x,y,lo.z)))
        ground.append([p.x*1920,(1-p.y)*1080])
    path=OUT/(item['id']+'.png')
    if '--metadata-only' in sys.argv:
        if not path.is_file(): raise FileNotFoundError(path)
    else:
        if path.exists(): raise FileExistsError('Do not overwrite a retained render: '+str(path))
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
    spec['props'][item['id']]={'texture':'res://'+path.relative_to(ROOT).as_posix(),
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'source_sha256':item['sha256'],
        'root_px':[foot.x*1920,(1-foot.y)*1080], 'ground_px':ground, 'projected_width_px':w/camera_data.ortho_scale*1920,
        'geometry_dimensions':list(hi-lo),'native_resolution':[1920,1080]}
    (OUT/'spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),'utf-8')
    print('KARCHIVE_PROP_DONE '+item['id'],flush=True)
