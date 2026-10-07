"""Read a licensed VRM through the installed add-on into an isolated candidate."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g


def main():
    p=argparse.ArgumentParser(); p.add_argument('--out',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]); out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('DIAGNOSTIC_IMPORT_OUTPUT_ONLY')
    inputs=g.read(out/'inputs.json')
    model=g.resolve(inputs['model']); g.resolve(inputs['license'])
    # Re-check the license immediately before the adapter is loaded.
    from inspect_vrm_source import inspect
    if inspect(model,g.resolve(inputs['license']))['errors']: raise ValueError('LICENSE_INTAKE_CHANGED')
    addon=Path(inputs['addon_read_only'])
    for name,sha in inputs['addon_python_files'].items():
        if hashlib.sha256((addon/name).read_bytes()).hexdigest()!=sha: raise ValueError('ADDON_CHANGED_AFTER_RECORDING')
    sys.dont_write_bytecode=True
    sys.path.insert(0,str(addon.parent))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import addon_utils
    if addon_utils.enable('vrm',default_set=True,persistent=False) is None:
        raise ValueError('VRM_ADDON_COULD_NOT_REGISTER')
    bpy.context.preferences.filepaths.temporary_directory=str(out/'cache')
    # Delete only this fresh diagnostic process's startup objects, not a user file.
    # Context-sensitive selection may be changed by the add-on's initialization.
    for ob in list(bpy.data.objects): bpy.data.objects.remove(ob,do_unlink=True)
    if len(bpy.context.scene.objects): raise ValueError('NONEMPTY_IMPORT_STARTUP_SCENE')
    result=bpy.ops.import_scene.vrm(filepath=str(model),use_addon_preferences=False,
        extract_textures_into_folder=False,enable_mtoon_outline_preview=False,
        set_shading_type_to_material_on_import=False)
    if result!={'FINISHED'}: raise ValueError('VRM_IMPORT_NOT_FINISHED:'+str(result))
    rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    if len(rigs)!=1: raise ValueError('EXACTLY_ONE_IMPORTED_HUMANOID_REQUIRED')
    rig=rigs[0]
    roles=rig.data.vrm_addon_extension.vrm1.humanoid.human_bones.human_bone_name_to_human_bone()
    mapping={getattr(name,'value',str(name)):bone.node.bone_name for name,bone in roles.items() if bone.node.bone_name}
    required=('hips','spine','head','leftUpperLeg','leftLowerLeg','leftFoot','rightUpperLeg','rightLowerLeg','rightFoot')
    errors=['MISSING_IMPORTED_ROLE:'+r for r in required if mapping.get(r) not in rig.data.bones]
    meshes=[]
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH': continue
        arms=[m for m in ob.modifiers if m.type=='ARMATURE' and m.object==rig]
        if not arms: errors.append('IMPORTED_MESH_NOT_SKINNED:'+ob.name)
        groups={vg.index:vg.name for vg in ob.vertex_groups}
        used={groups[w.group] for v in ob.data.vertices for w in v.groups if w.weight>0}
        meshes.append({'name':ob.name,'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),
            'armature_modifiers':len(arms),'weighted_bones':sorted(used),
            'unweighted_vertices':sum(not any(w.weight>0 for w in v.groups) for v in ob.data.vertices),
            'world_dimensions':list(ob.dimensions),
            'materials':[m.name for m in ob.data.materials if m]})
    for role in ('leftUpperLeg','leftLowerLeg','leftFoot','rightUpperLeg','rightLowerLeg','rightFoot'):
        if not any(mapping.get(role) in row['weighted_bones'] for row in meshes):
            errors.append('IMPORTED_LEG_BONE_NOT_DRIVING_MESH:'+role)
    blend=out/'licensed_humanoid_import.blend'
    if blend.exists(): raise ValueError('NO_IMPORT_OVERWRITE')
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    g.write(out/'import_result.json',{'status':'HOLD_MATERIAL_RETARGET_AND_VISUAL_REVIEW','errors':errors,
        'blend':g.ref(blend),'model':inputs['model'],'rig':rig.name,'humanoid_mapping':mapping,
        'actual_weighted_meshes':meshes,'production_ready':False,
        'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),
            'parent':b.parent.name if b.parent else None,'matrix_local':[list(r) for r in b.matrix_local]}
            for b in rig.data.bones},
        'note':'No MICA art/costume approval and no UAL retarget claimed; this is a real import compatibility probe.'})
    print('VRM_IMPORT_PROBE_RECORDED',str(blend))


if __name__=='__main__': main()
