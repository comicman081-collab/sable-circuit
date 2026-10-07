"""Color actual licensed reference limb weights, without changing their pose.

One bounded diagnostic Blender child. This is geometry evidence only, never
SABLE appearance. Original reference blend and all source models stay read-only.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g


def child(a):
    import bpy
    from mathutils import Vector
    from bpy_extras.object_utils import world_to_camera_view
    from build_tripo_locomotion_guide import sample_vertices
    out=g.local(a.out); inputs=g.read(out/'INPUTS.json')
    expected={'builder':g.ref(__file__),'result':g.ref(a.result),'calibration':g.ref(a.calibration),
              'helper':g.ref(ROOT/'tools/character_pipeline/build_tripo_locomotion_guide.py')}
    if inputs!=expected:raise ValueError('EXACT_CHILD_CLI_INPUTS_REQUIRED')
    for ref in inputs.values():g.resolve(ref)
    with (out/'CHILD_CLAIM.json').open('x',encoding='utf8') as f:
        import json
        json.dump({'inputs':g.ref(out/'INPUTS.json'),'args':{'result':inputs['result'],'calibration':inputs['calibration'],'out':out.relative_to(ROOT).as_posix()}},f,indent=2)
    result=g.read(a.result); report=g.read(a.calibration)
    if report['input_result']!=inputs['result'] or report['input_blend']!=result['output_blend']:
        raise ValueError('EXACT_CALIBRATION_REQUIRED')
    license_data=g.read(g.resolve(result['target_license']))
    if license_data['license']!='CC0-1.0' or license_data['source_blend']!=result['target_model']:
        raise ValueError('EXACT_CC0_LICENSE_REQUIRED')
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(result['output_blend'])),load_ui=False)
    scene=bpy.context.scene; mesh=bpy.data.objects[result['sole_mesh']]
    rig=next(m.object for m in mesh.modifiers if m.type=='ARMATURE')
    floor=report['fixed_floor']['world_z_m']; bounds=[]
    for row in report['samples']:
        frame=row['frame'];scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
        ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());data=ev.to_mesh()
        try:bounds.extend(ev.matrix_world@v.co for v in data.vertices)
        finally:ev.to_mesh_clear()
    ymin=min(v.y for v in bounds);ymax=max(v.y for v in bounds)
    zmin=min(floor,min(v.z for v in bounds));zmax=max(v.z for v in bounds)
    center=Vector((0,(ymin+ymax)/2,(zmin+zmax)/2));scene.camera.location=center+Vector((-4,0,0))
    scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=max((zmax-zmin)*1920/1080,ymax-ymin)*1.15
    row=next(r for r in report['samples'] if r['sample']==report['phase_candidates']['contact_l'])
    frame=row['frame'];scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
    soles=sample_vertices(mesh,result['sole_vertex_ids'])
    if soles!=row['sole_vertices_world_m']:raise ValueError('EVALUATED_SOLES_CHANGED')
    # Color polygon labels from actual anatomical deform-group weights only.
    # No new body, costume, footwear or weapon geometry is constructed.
    mesh.data.materials.clear()
    for name,color in [('Reference neutral',(.4,.43,.5,1)),('LEFT blue',(.025,.35,1,1)),('RIGHT orange',(1,.2,.025,1))]:
        mat=bpy.data.materials.new(name);mat.diffuse_color=color;mesh.data.materials.append(mat)
    groups={side:{v.index for v in mesh.vertex_groups if v.name in [stem+'_'+suffix for stem in ('thigh','calf','foot','ball')]} for side,suffix in [('left','l'),('right','r')]}
    if any(len(ids)!=4 for ids in groups.values()):raise ValueError('EXACT_ANATOMICAL_DEFORM_GROUPS_REQUIRED')
    weights={v.index:{side:sum(x.weight for x in v.groups if x.group in ids) for side,ids in groups.items()} for v in mesh.data.vertices}
    counts={'neutral':0,'left':0,'right':0}
    for poly in mesh.data.polygons:
        totals={side:sum(weights[i][side] for i in poly.vertices)/len(poly.vertices) for side in groups}
        side=max(totals,key=totals.get)
        label=side if totals[side]>.25 else 'neutral'
        poly.material_index={'neutral':0,'left':1,'right':2}[label];counts[label]+=1
    scene.display.shading.color_type='MATERIAL';scene.display.shading.light='STUDIO'
    scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
    scene.render.engine='BLENDER_WORKBENCH';scene.render.film_transparent=False
    scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.threads_mode='FIXED';scene.render.threads=2
    bpy.context.view_layer.update()
    def project(v):
        p=world_to_camera_view(scene,scene.camera,v)
        return [p.x*1920,(1-p.y)*1080]
    projected={side:{stem:project(rig.matrix_world@rig.pose.bones[stem+'_'+suffix].head) for stem in ('thigh','calf','foot','ball')} for side,suffix in [('left','l'),('right','r')]}
    projected_soles={side:[project(Vector(v)) for v in vv] for side,vv in soles.items()}
    image=out/'COLORED_CONTACT_L_1920.png';scene.render.filepath=str(image);bpy.ops.render.render(write_still=True)
    if sample_vertices(mesh,result['sole_vertex_ids'])!=soles:raise ValueError('RENDER_CHANGED_SOLES')
    g.write(out/'GEOMETRY.json',{'schema':1,'scope':'ANATOMICAL_LATERALITY_REFERENCE_ONLY_NOT_SABLE_ART','production_ready':False,
        'inputs':g.ref(out/'INPUTS.json'),'retarget_result':inputs['result'],'calibration':inputs['calibration'],
        'target_license':result['target_license'],'blend':result['output_blend'],'phase':'contact_l','direction':'E','motion':'run',
        'sample':row['sample'],'frame':frame,'native_resolution':[1920,1080],'image':g.ref(image),
        'projected_joints_px':projected,'projected_soles_px':projected_soles,'actual_sole_vertices_world_m':soles,
        'fixed_floor_world_z_m':floor,'floor_y_px':project(Vector((0,center.y,floor)))[1],
        'polygon_counts':counts,'leg_colors':{'left':'blue','right':'orange'},'pose_or_geometry_modified':False})


def main(a):
    out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):raise ValueError('DIAGNOSTIC_ONLY')
    out.mkdir(parents=True,exist_ok=False);cache=out/'cache';cache.mkdir()
    inputs={'builder':g.ref(__file__),'result':g.ref(a.result),'calibration':g.ref(a.calibration),'helper':g.ref(ROOT/'tools/character_pipeline/build_tripo_locomotion_guide.py')}
    g.write(out/'INPUTS.json',inputs)
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME','BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[key]=str(cache)
    env['PYTHONDONTWRITEBYTECODE']='1';env['OMP_NUM_THREADS']='2'
    cmd=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2','--python',__file__,'--','--result',str(g.local(a.result)),'--calibration',str(g.local(a.calibration)),'--out',str(out),'--inside']
    with (out/'blender.log').open('w',encoding='utf8') as log:
        p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if p.returncode:raise ValueError('LATERALITY_CAPTURE_FAILED:'+str(out/'blender.log'))
    for ref in inputs.values():g.resolve(ref)
    # Native annotation: no resizing, posed joints come from the actual rig.
    from PIL import Image,ImageDraw,ImageFont
    data=g.read(out/'GEOMETRY.json');im=Image.open(g.resolve(data['image'])).convert('RGB');draw=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26)
    draw.line([(0,data['floor_y_px']),(1920,data['floor_y_px'])],fill=(195,195,195),width=2)
    for side,x,y,color in [('left',1280,710,(90,175,255)),('right',65,605,(255,150,80))]:
        text='LEFT / BLUE: support, forward' if side=='left' else 'RIGHT / ORANGE: trailing, raised'
        draw.text((x,y),text,font=font,fill=color)
        target=data['projected_joints_px'][side]['calf']
        draw.line([(x+150,y+40),target],fill=color,width=3)
        draw.ellipse([target[0]-5,target[1]-5,target[0]+5,target[1]+5],fill=color)
    draw.text((40,35),'E / CONTACT_L - POSE GEOMETRY ONLY',font=font,fill='white')
    draw.text((40,75),'Limb colors are labels, never costume or runtime pixels.',font=font,fill=(205,210,220))
    annotated=out/'ANNOTATED_CONTACT_L_1920.png';im.save(annotated)
    g.write(out/'COMPLETION.json',{'schema':1,'generator':g.ref(__file__),'geometry':g.ref(out/'GEOMETRY.json'),'image':g.ref(annotated),'source_scale':1,'native_resolution':[1920,1080],'owned_child_exited':True,'production_ready':False,'scope':'POSE_GUIDE_ANNOTATION_NEEDS_INDEPENDENT_REVIEW'})
    print('LATERALITY_GUIDE_COMPLETE')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',required=True);p.add_argument('--calibration',required=True);p.add_argument('--out',required=True);p.add_argument('--inside',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(a) if a.inside else main(a)
