"""Read actual Blender scene/skin/topology/material UVs without rendering or saving.

Run inside Blender with -- --out <project.json>. Missing semantic declarations
are a HOLD/FAIL, not an invitation to infer them from a filename. The collector
can inspect old failed scenes for regression evidence; it never promotes them.
"""
import argparse
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g


def material_graph(material,role):
    """Only inspect paths feeding the active output; decoy textures do not count.

    Unsupported node groups/procedural geometry fail closed. This is an explicit
    small shader dialect, not a claim that arbitrary Blender graphs are audited.
    """
    if not material or not material.use_nodes:
        return [],['MATERIAL_GRAPH_REQUIRED']
    nodes=material.node_tree.nodes
    outputs=[n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]
    if len(outputs)!=1 or not outputs[0].inputs['Surface'].is_linked:
        return [],['ONE_CONNECTED_ACTIVE_MATERIAL_OUTPUT_REQUIRED']
    if any(outputs[0].inputs[k].is_linked for k in ('Volume','Displacement')):
        return [],['UNREVIEWED_MATERIAL_VOLUME_OR_DISPLACEMENT']
    allowed={'OUTPUT_MATERIAL','BSDF_PRINCIPLED','EMISSION','TEX_IMAGE','UVMAP',
             'BSDF_TRANSPARENT','MIX_SHADER','MATH','SEPRGB','SEPARATE_COLOR','RGB','VALUE'}
    reachable={}; pending=[outputs[0]]; errors=[]
    while pending:
        node=pending.pop()
        if node.name in reachable: continue
        reachable[node.name]=node
        if node.type not in allowed:
            errors.append('UNSUPPORTED_CONNECTED_SHADER_NODE:'+node.type)
        for socket in node.inputs:
            pending.extend(link.from_node for link in socket.links)
    images=[n for n in reachable.values() if n.type=='TEX_IMAGE']
    if any(n.type=='TEX_IMAGE' and n.name not in reachable for n in nodes):
        errors.append('DISCONNECTED_DECOY_TEXTURE')
    if len(images)>1:
        errors.append('MULTIPLE_SHADER_IMAGES_REQUIRE_EXPLICIT_ADAPTER')
    if role in ('body','legs','boots','pelvis'):
        for node in reachable.values():
            if node.type in ('BSDF_TRANSPARENT','MIX_SHADER'):
                errors.append('ANATOMICAL_MESH_CANNOT_BE_ALPHA_ERASED')
            if node.type=='BSDF_PRINCIPLED' and (node.inputs['Alpha'].is_linked or node.inputs['Alpha'].default_value!=1):
                errors.append('ANATOMICAL_MESH_CANNOT_BE_ALPHA_ERASED')
    return images,sorted(set(errors))


def object_hidden(ob):
    return bool(ob.hide_render or not ob.visible_camera or
                any(c.hide_render for c in ob.users_collection) or
                (ob.parent and object_hidden(ob.parent)))


def camera_state(scene):
    import bpy
    camera=scene.camera
    if camera is None: return None
    actual=camera.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return {'name':camera.name,'matrix':[list(r) for r in actual.matrix_world],
            'ortho_scale':actual.data.ortho_scale,'type':actual.data.type,
            'lens':actual.data.lens,'shift':[actual.data.shift_x,actual.data.shift_y],
            'render':[scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage],
            'pixel_aspect':[scene.render.pixel_aspect_x,scene.render.pixel_aspect_y],
            'border':[scene.render.use_border,scene.render.use_crop_to_border],
            'film_transparent':scene.render.film_transparent}


def collect_scene():
    import bpy
    scene=bpy.context.scene
    contract=json.loads(scene.get('generation_mesh_contract','{}'))
    chart_table=json.loads(scene.get('generation_source_charts','{}'))
    objects=[]; triangles=[]; errors=[]
    camera=scene.camera
    limits=g.read(g.CONTRACT)['mesh']
    if not contract:
        errors.append('MISSING_SEMANTIC_MESH_CONTRACT')
    if camera is None:
        errors.append('NO_REGISTERED_CAMERA')
    for ob in scene.objects:
        if ob.type!='MESH':
            continue
        mesh=ob.data; mesh.calc_loop_triangles()
        role=ob.get('generation_role','unassigned')
        supported={'ARMATURE'} if role in ('body','legs','boots','pelvis') else {'ARMATURE','SOLIDIFY','SUBSURF'}
        if any(m.show_render and m.type not in supported for m in ob.modifiers):
            errors.append(ob.name+':UNSUPPORTED_GEOMETRY_MODIFIER')
        hidden=object_hidden(ob)
        weights_bad=[]; sums_bad=[]; unweighted=[]
        mods=[m for m in ob.modifiers if m.type=='ARMATURE']
        arm=next((m for m in mods if m.show_render and m.object and m.object.type=='ARMATURE'),None)
        bones=set(arm.object.data.bones.keys()) if arm else set()
        groups={i:v.name for i,v in enumerate(ob.vertex_groups)}
        for vertex in mesh.vertices:
            total=0.
            for weight in vertex.groups:
                name=groups.get(weight.group,'')
                if name not in bones and weight.weight>0:
                    weights_bad.append(vertex.index)
                if name in bones:
                    total+=weight.weight
            if total<1e-6:
                unweighted.append(vertex.index)
            elif abs(total-1)>limits['weight_sum_tolerance']:
                sums_bad.append(vertex.index)
        edge_faces={}; degenerate=[]
        for face in mesh.polygons:
            if face.area<1e-12:
                degenerate.append(face.index)
            ids=list(face.vertices)
            for a,b in zip(ids,ids[1:]+ids[:1]):
                key=tuple(sorted((a,b))); edge_faces[key]=edge_faces.get(key,0)+1
        boundary=sum(count==1 for count in edge_faces.values())
        nonmanifold=sum(count>2 for count in edge_faces.values())
        normal_errors=0
        if role=='coat' or 'Split_Coat' in ob.name:
            for face in mesh.polygons:
                # Outer surface before thickness modifier. Intentional fold
                # exceptions must have separate, independently reviewed regions.
                radial=face.center.copy(); radial.z=0
                if radial.length>.001 and face.normal.dot(radial)<-.00001:
                    normal_errors+=1
        dimensions=[(max(v.co[i] for v in mesh.vertices)-min(v.co[i] for v in mesh.vertices))*abs(ob.matrix_world.to_scale()[i])*scene.unit_settings.scale_length for i in range(3)] if mesh.vertices else [0,0,0]
        attribute=mesh.attributes.get('generation_chart_id')
        chart_ids=json.loads(ob.get('generation_chart_table','{}'))
        material_images=[]; material_errors=[]
        for slot in ob.material_slots:
            material=slot.material
            actual_images,graph_errors=material_graph(material,role)
            material_errors.extend(graph_errors)
            for node in actual_images:
                if node.type=='TEX_IMAGE' and node.image:
                    image_path=Path(bpy.path.abspath(node.image.filepath)).resolve()
                    material_images.append(str(image_path))
                    if node.inputs['Vector'].is_linked:
                        source=node.inputs['Vector'].links[0].from_node
                        if not mesh.uv_layers.active or source.type!='UVMAP' or source.uv_map!=mesh.uv_layers.active.name:
                            material_errors.append('UNRESOLVED_SHADER_UV_TRANSFORM')
                    if node.projection!='FLAT' or node.interpolation not in ('Linear','Closest'):
                        material_errors.append('UNSUPPORTED_TEXTURE_PROJECTION_OR_FILTER')
                    if node.image.packed_file or node.image.source!='FILE':
                        material_errors.append('PACKED_OR_GENERATED_IMAGE_NOT_BOUND_TO_SOURCE')
                    if node.extension!='REPEAT':
                        # Explicitly supported CLIP/EXTEND still cannot sample
                        # outside source masks; repeat-outside-[0,1] is forbidden.
                        if node.extension not in ('CLIP','EXTEND'):
                            material_errors.append('UNSUPPORTED_TEXTURE_ADDRESS_MODE')
                if role in ('body','legs','boots','pelvis') and node.type in ('BSDF_TRANSPARENT','HOLDOUT'):
                    material_errors.append('ANATOMICAL_MESH_CANNOT_BE_ALPHA_ERASED')
        if material_images:
            if not attribute or attribute.domain!='FACE' or not chart_ids:
                errors.append(ob.name+':MISSING_ACTUAL_FACE_UV_REGION_ASSIGNMENT')
            elif not mesh.uv_layers.active:
                errors.append(ob.name+':NO_ACTIVE_UV')
            else:
                uv=mesh.uv_layers.active.data
                for tri in mesh.loop_triangles:
                    chart_id=chart_ids.get(str(attribute.data[tri.polygon_index].value),'unassigned')
                    chart=chart_table.get(chart_id,{})
                    face=mesh.polygons[tri.polygon_index]
                    material=ob.material_slots[face.material_index].material if face.material_index<len(ob.material_slots) else None
                    if not material or not material.use_nodes:
                        errors.append(ob.name+':INVALID_FACE_MATERIAL'); continue
                    nodes,_=material_graph(material,role)
                    images=[str(Path(bpy.path.abspath(n.image.filepath)).resolve()) for n in nodes if n.image]
                    if not chart or images!=[str(g.local(chart['image']['path']))]:
                        errors.append(ob.name+':CHART_NOT_ACTUAL_MATERIAL_IMAGE')
                    if chart.get('purpose')== 'unwarped_upper' and role!='unwarped_upper':
                        errors.append(ob.name+':UPPER_CHART_ON_VOLUMETRIC_PART')
                    triangles.append({'part':ob.name,'chart_ids':[chart_id]*3,
                                      'uv':[list(uv[i].uv) for i in tri.loops]})
        objects.append({'name':ob.name,'role':role,'hidden':hidden,'vertices':len(mesh.vertices),
                        'armature':arm.object.name if arm else None,
                        'unweighted_vertices':len(unweighted),'invalid_bone_weights':len(set(weights_bad)),
                        'bad_weight_sums':len(sums_bad),'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,
                        'degenerate_faces':len(degenerate),'dimensions':dimensions,
                        'outward_normal_errors':normal_errors,'material_errors':sorted(set(material_errors)),
                        'source_images':sorted(set(material_images)),
                        'polygon_count':len(mesh.polygons),'modifier_types':[m.type for m in ob.modifiers if m.show_render],
                        'vertex_groups':len(ob.vertex_groups),
                        'vertices_in_faces':sorted({int(i) for f in mesh.polygons for i in f.vertices})})
    attachment_distances=[]
    depsgraph=bpy.context.evaluated_depsgraph_get()
    for pair in contract.get('attachments',[]):
        sides=[]
        for endpoint in ('a','b'):
            spec=pair[endpoint]; ob=bpy.data.objects[spec['object']]
            if not spec['vertices']:
                raise ValueError('EMPTY_ATTACHMENT_VERTEX_SET')
            evaluated=ob.evaluated_get(depsgraph); mesh=evaluated.to_mesh()
            try:
                sides.append([evaluated.matrix_world@mesh.vertices[int(i)].co for i in spec['vertices']])
            finally:
                evaluated.to_mesh_clear()
        # Symmetric point-set distance avoids hiding a gap with one close vertex.
        distance=max(max(min((p-q).length for q in sides[1]) for p in sides[0]),
                     max(min((q-p).length for p in sides[0]) for q in sides[1]))
        attachment_distances.append({'id':pair['id'],'distance_m':distance*scene.unit_settings.scale_length})
    sole_samples={}
    sole_object=bpy.data.objects.get(contract.get('sole_mesh',''))
    for side,ids in contract.get('sole_vertex_ids',{}).items():
        if sole_object is None or sole_object.type!='MESH' or not ids or any(isinstance(i,bool) or not isinstance(i,int) or i<0 or i>=len(sole_object.data.vertices) for i in ids):
            errors.append('INVALID_ACTUAL_SOLE_VERTEX_IDS:'+side); continue
        evaluated=sole_object.evaluated_get(depsgraph); evaluated_mesh=evaluated.to_mesh()
        try:
            sole_samples[side]=[{'id':i,'world_m':list((evaluated.matrix_world@evaluated_mesh.vertices[i].co)*scene.unit_settings.scale_length),
                                 'weights':{sole_object.vertex_groups[w.group].name:w.weight for w in sole_object.data.vertices[i].groups}}
                                for i in ids]
        finally:
            evaluated.to_mesh_clear()
    body_frame=bpy.data.objects.get(contract.get('body_coordinate_frame',''))
    frame_matrix=[list(row) for row in body_frame.matrix_world] if body_frame else None
    return {'schema':1,'method':'actual_Blender_scene_skin_topology_uv',
            'collector':g.ref(__file__),'blend':g.ref(bpy.data.filepath),
            'scene':{'name':scene.name,'frame':scene.frame_current,'unit_scale':scene.unit_settings.scale_length,
                     'view':scene.get('generation_view'),
                     'camera':camera_state(scene),
                     'render':[scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage]},
            'contract':contract,'charts':chart_table,'objects':objects,'triangles':triangles,
            'attachments':attachment_distances,'sole_samples':sole_samples,'body_frame_matrix':frame_matrix,
            'errors':sorted(set(errors))}


def validate_collected(data):
    errors=data.get('errors',[])[:]
    if data.get('schema')!=1 or data.get('method')!='actual_Blender_scene_skin_topology_uv':
        raise ValueError('ACTUAL_SCENE_PREFLIGHT_REQUIRED')
    if g.resolve(data['collector'])!=Path(__file__).resolve():
        raise ValueError('WRONG_MESH_COLLECTOR')
    g.resolve(data['blend'])
    contract=data.get('contract',{}); limits=g.read(g.CONTRACT)['mesh']
    height=g.finite(contract.get('body_height_m',1.78))
    if not .5<height<3:
        errors.append('INVALID_BODY_HEIGHT_CONTRACT')
    frame=data.get('body_frame_matrix'); axes=contract.get('body_axes_world',{})
    if not frame or not contract.get('body_coordinate_frame') or set(axes)!={'forward','left','up'} or len(contract.get('ground_origin_world_m',[]))!=3:
        errors.append('REVIEWED_GROUND_BODY_FRAME_REQUIRED')
    else:
        import numpy as np
        matrix=np.asarray(frame,dtype=float)
        expected=np.column_stack([axes[k] for k in ('forward','left','up')]).astype(float)
        origin=np.asarray(contract['ground_origin_world_m'],dtype=float)
        if (matrix.shape!=(4,4) or expected.shape!=(3,3) or not np.isfinite(matrix).all() or
                not np.isfinite(expected).all() or not np.isfinite(origin).all() or
                not np.allclose(matrix[3],[0,0,0,1]) or
                not np.allclose(matrix[:3,:3].T@matrix[:3,:3],np.eye(3),atol=.001) or
                not np.isclose(np.linalg.det(matrix[:3,:3]),1,atol=.001) or
                not np.allclose(matrix[:3,:3],expected,atol=.001) or
                not np.allclose(matrix[:3,3]*data['scene']['unit_scale'],origin,atol=.001) or
                not np.allclose(expected[:,2],[0,0,1],atol=.001)):
            errors.append('BODY_FRAME_AXES_OR_GROUND_ORIGIN_MISMATCH')
    declared=contract.get('required_parts',{})
    if not declared or not contract.get('attachments') or not contract.get('sole_mesh'):
        errors.append('ANATOMICAL_PARTS_ATTACHMENTS_AND_SOLES_REQUIRED')
    observed={o['name']:o for o in data.get('objects',[])}
    if not observed:
        errors.append('EMPTY_SCENE')
    for name,role in declared.items():
        if name not in observed or observed[name]['role']!=role:
            errors.append(name+':MISSING_OR_MISCLASSIFIED_REQUIRED_PART')
    sole=observed.get(contract.get('sole_mesh'),{})
    if not sole or sole.get('hidden') or not sole.get('armature') or sole.get('role') not in ('body','legs','boots'):
        errors.append('VISIBLE_ACTUAL_SKINNED_SOLE_MESH_REQUIRED')
    ids=contract.get('sole_vertex_ids',{})
    if (set(ids)!= {'left','right'} or any(not isinstance(v,list) or len(v)<3 or len(set(v))!=len(v) for v in ids.values()) or
            set(ids.get('left',[]))&set(ids.get('right',[]))):
        errors.append('DISTINCT_ANATOMICAL_SOLE_VERTEX_SETS_REQUIRED')
    for side in ('left','right'):
        samples=data.get('sole_samples',{}).get(side,[])
        if [r['id'] for r in samples]!=ids.get(side) or not samples:
            errors.append('ACTUAL_SOLE_VERTEX_COVERAGE:'+side)
        if any(r['id'] not in sole.get('vertices_in_faces',[]) or not r.get('weights') or
               any(not math.isfinite(float(v)) for v in r['world_m']) for r in samples):
            errors.append('SOLE_SAMPLE_NOT_ON_REAL_WEIGHTED_SURFACE:'+side)
    for ob in observed.values():
        prefix=ob['name']+':'
        if ob['role']=='unassigned':
            errors.append(prefix+'UNREVIEWED_MESH_ROLE')
        if ob['name'] not in declared:
            errors.append(prefix+'MESH_NOT_IN_REVIEWED_PART_CONTRACT')
        if ob['role']=='unwarped_upper' and (ob['vertices']!=4 or ob['polygon_count']!=1 or ob['modifier_types'] or ob['vertex_groups']):
            errors.append(prefix+'UPPER_IMAGE_MUST_BE_UNDEFORMED_SINGLE_QUAD')
        if ob['role'] in ('body','legs','boots','pelvis'):
            if ob['hidden'] or not ob['armature'] or ob['unweighted_vertices'] or ob['invalid_bone_weights'] or ob['bad_weight_sums']:
                errors.append(prefix+'INVALID_OR_INVISIBLE_REAL_SKIN')
            if ob['boundary_edges'] or ob['nonmanifold_edges']:
                errors.append(prefix+'OPEN_OR_NONMANIFOLD_ANATOMY')
            if min(map(g.finite,ob['dimensions']))/height<limits['volume_depth_over_height_min']:
                errors.append(prefix+'ANATOMICAL_PLANE_NOT_VOLUME')
        if ob['degenerate_faces']:
            errors.append(prefix+'DEGENERATE_FACES')
        if ob['outward_normal_errors']:
            errors.append(prefix+'INVERTED_COAT_OUTER_NORMALS')
        errors.extend(prefix+e for e in ob.get('material_errors',[]))
    expected={p['id'] for p in contract.get('attachments',[])}
    if {p['id'] for p in data.get('attachments',[])}!=expected:
        errors.append('ATTACHMENT_COVERAGE')
    for pair in data.get('attachments',[]):
        if g.finite(pair['distance_m'])/height>limits['attachment_gap_over_height_max']:
            errors.append(pair['id']+':DISCONNECTED_ATTACHMENT')
    if not data.get('charts'):
        errors.append('APPROVED_SEMANTIC_UV_CHARTS_REQUIRED')
    elif data.get('triangles'):
        errors.extend(g.check_uv_triangles(data['triangles'],data['charts']))
    else:
        errors.append('ACTUAL_UV_TRIANGLE_COVERAGE_REQUIRED')
    return {'stage':'mesh','verdict':'FAIL' if errors else 'HOLD_NATIVE_FIRST_POSE',
            'errors':sorted(set(errors)),'blend':data['blend'],
            'scene_sha256':g.canonical(data['scene']),
            'note':'A clean mesh preflight permits only a reviewed native pose, not an animation batch.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    data=collect_scene(); g.write(a.out,data)
    print('MESH_PREFLIGHT_COLLECTED_WITHOUT_RENDER '+str(a.out))


if __name__=='__main__':
    main()
