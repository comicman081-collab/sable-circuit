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


# This adapter deliberately has a separate contract from the generic anatomical
# mesh collector below.  A source-preserving surface is one continuous, closed
# carrier of approved ImageGen pixels; inventing generic body/coat/attachment
# declarations for it would make the review record less truthful, not safer.
SOURCE_SURFACE_KIND='source_preserving_surface_v1'
SOURCE_SURFACE_CAMERA_PLANE_KIND='source_preserving_surface_camera_plane_v1'
SOURCE_SURFACE_METHOD='actual_Blender_source_preserving_surface'
SOURCE_SURFACE_AUTHORITY='Exact full ImageGen source; no newly colored closure faces'


def is_source_preserving_surface_kind(kind):
    """Keep every source-surface trust boundary on the same closed kind set."""
    return kind in (SOURCE_SURFACE_KIND,SOURCE_SURFACE_CAMERA_PLANE_KIND)


def _closed_mesh_summary(mesh):
    edge_faces={}; degenerate=[]
    for face in mesh.polygons:
        if face.area<1e-12:
            degenerate.append(face.index)
        ids=list(face.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):
            key=tuple(sorted((a,b)));edge_faces[key]=edge_faces.get(key,0)+1
    return {'boundary_edges':sum(v==1 for v in edge_faces.values()),
            'nonmanifold_edges':sum(v>2 for v in edge_faces.values()),
            'degenerate_faces':len(degenerate)}


def _skin_summary(ob):
    """Inspect actual source-surface weights without assigning body-part roles."""
    armatures=[m for m in ob.modifiers if m.type=='ARMATURE' and m.show_render
               and m.object and m.object.type=='ARMATURE']
    arm=armatures[0] if len(armatures)==1 else None
    bones=set(arm.object.data.bones.keys()) if arm else set()
    groups={i:v.name for i,v in enumerate(ob.vertex_groups)}
    limits=g.read(g.CONTRACT)['mesh']; unweighted=[]; invalid=[]; bad_sums=[]
    for vertex in ob.data.vertices:
        total=0.
        for row in vertex.groups:
            name=groups.get(row.group,'')
            if name not in bones and row.weight>0:invalid.append(vertex.index)
            if name in bones:total+=row.weight
        if total<1e-6:unweighted.append(vertex.index)
        elif abs(total-1)>limits['weight_sum_tolerance']:bad_sums.append(vertex.index)
    return {'armature':arm.object.name if arm else None,
            'armature_modifier_count':len(armatures),
            'unweighted_vertices':len(unweighted),
            'invalid_bone_weights':len(set(invalid)),
            'bad_weight_sums':len(bad_sums),
            'vertex_groups':len(ob.vertex_groups)}


def _source_binding_samples(positions, bindings, count):
    """Evaluate the independently bound opaque-pixel sole samples on the mesh."""
    import numpy as np
    import source_surface_sampling as sampling
    samples={}; errors=[]
    if set(bindings)!= {'l','r'}:
        return {},['DISTINCT_LEFT_RIGHT_SOURCE_SOLE_BINDINGS_REQUIRED']
    for side,binding in bindings.items():
        try:
            vertices=np.asarray(binding.get('vertices'),dtype=int)
            bary=np.asarray(binding.get('barycentric'),dtype=float)
            pixels=np.asarray(binding.get('pixels'),dtype=float)
            if (vertices.ndim!=2 or vertices.shape[1:]!=(3,) or bary.shape!=vertices.shape
                    or pixels.shape!=(len(vertices),2) or not len(vertices)
                    or np.any(vertices<0) or np.any(vertices>=count)
                    or not np.isfinite(bary).all() or not np.isfinite(pixels).all()
                    or np.any(bary<-1e-6) or np.max(np.abs(bary.sum(axis=1)-1))>1e-5):
                raise ValueError('INVALID_SOURCE_SOLE_BARYCENTRIC_BINDING')
            actual=sampling.sample_positions(positions,binding)
            if actual.shape!=(len(vertices),3) or not np.isfinite(actual).all():
                raise ValueError('NONFINITE_ACTUAL_SOURCE_SOLE_SAMPLE')
            samples[side]={'sample_count':int(len(vertices)),
                           'min_world_z_m':float(actual[:,2].min()),
                           'max_world_z_m':float(actual[:,2].max()),
                           'positions_world_m':actual.tolist()}
        except Exception as exc:
            errors.append(side+':'+str(exc))
    return samples,errors


def _transparent_closure_material(material):
    """A hidden closure may only close the volume; it cannot paint a substitute."""
    if not material or not material.use_nodes:return False
    nodes=material.node_tree.nodes
    outputs=[n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]
    if len(outputs)!=1 or not outputs[0].inputs['Surface'].is_linked:return False
    reachable={};pending=[outputs[0]]
    while pending:
        node=pending.pop()
        if node.name in reachable:continue
        reachable[node.name]=node
        for socket in node.inputs:
            pending.extend(link.from_node for link in socket.links)
    surface=outputs[0].inputs['Surface'].links[0].from_node
    return surface.type=='BSDF_TRANSPARENT' and {n.type for n in reachable.values()}=={'OUTPUT_MATERIAL','BSDF_TRANSPARENT'}


def _exact_source_front_material(material, expected_rgba):
    """Allow only the unmodified source RGBA-to-emission/alpha graph.

    A source image merely being connected is insufficient: Principled, RGB,
    Math or colour nodes can silently recolour the approved art.  The narrow
    graph below preserves the source image's Color and Alpha sockets verbatim.
    """
    import bpy
    if not material or not material.use_nodes:return ['SOURCE_FRONT_MATERIAL_REQUIRED']
    nodes=material.node_tree.nodes;outputs=[n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]
    if len(outputs)!=1 or not outputs[0].inputs['Surface'].is_linked:return ['SOURCE_FRONT_ACTIVE_OUTPUT_REQUIRED']
    reachable={};pending=[outputs[0]]
    while pending:
        node=pending.pop()
        if node.name in reachable:continue
        reachable[node.name]=node
        for socket in node.inputs:pending.extend(link.from_node for link in socket.links)
    types={node.type for node in reachable.values()}
    allowed={'OUTPUT_MATERIAL','MIX_SHADER','BSDF_TRANSPARENT','EMISSION','TEX_IMAGE','UVMAP'}
    errors=[]
    if not types.issubset(allowed):errors.append('SOURCE_FRONT_SHADER_RECOLOUR_OR_UNSUPPORTED_NODE')
    if any(outputs[0].inputs[key].is_linked for key in ('Volume','Displacement')):
        errors.append('SOURCE_FRONT_VOLUME_OR_DISPLACEMENT_FORBIDDEN')
    images=[node for node in reachable.values() if node.type=='TEX_IMAGE']
    emissions=[node for node in reachable.values() if node.type=='EMISSION']
    mixers=[node for node in reachable.values() if node.type=='MIX_SHADER']
    transparent=[node for node in reachable.values() if node.type=='BSDF_TRANSPARENT']
    if len(images)!=1 or len(emissions)!=1 or len(mixers)!=1 or len(transparent)!=1:
        errors.append('EXACT_SOURCE_RGBA_EMISSION_ALPHA_GRAPH_REQUIRED');return errors
    texture=images[0];emission=emissions[0];mix=mixers[0];trans=transparent[0]
    if (not texture.image or texture.image.packed_file or texture.image.source!='FILE'
            or str(Path(bpy.path.abspath(texture.image.filepath)).resolve())!=str(expected_rgba)):
        errors.append('SOURCE_FRONT_TEXTURE_DIFFERS_FROM_REVIEWED_RGBA')
    if not emission.inputs['Color'].is_linked or emission.inputs['Color'].links[0].from_node!=texture or emission.inputs['Color'].links[0].from_socket.name!='Color':
        errors.append('SOURCE_FRONT_COLOR_NOT_DIRECT_IMAGE_COLOR')
    if not mix.inputs[0].is_linked or mix.inputs[0].links[0].from_node!=texture or mix.inputs[0].links[0].from_socket.name!='Alpha':
        errors.append('SOURCE_FRONT_ALPHA_NOT_DIRECT_IMAGE_ALPHA')
    # Alpha=0 must select Transparent and Alpha=1 must select the unmodified
    # source emission.  Accepting the two shader inputs as an unordered set
    # would silently invert the alpha matte.
    if (not mix.inputs[1].is_linked or mix.inputs[1].links[0].from_node!=trans
            or not mix.inputs[2].is_linked or mix.inputs[2].links[0].from_node!=emission
            or not outputs[0].inputs['Surface'].is_linked or outputs[0].inputs['Surface'].links[0].from_node!=mix):
        errors.append('SOURCE_FRONT_TRANSPARENT_EMISSION_COMPOSITION_REQUIRED')
    strength=emission.inputs.get('Strength')
    if strength is None or strength.is_linked or abs(float(strength.default_value)-1.0)>1e-9:
        errors.append('SOURCE_FRONT_EMISSION_STRENGTH_MUST_BE_UNMODIFIED_ONE')
    return errors


def _source_surface_snapshot_checks(ob, rig, source_material_slots, source, count, bindings):
    """Compare actual front topology/UV/weights to the consumed source snapshots."""
    import numpy as np
    from collections import Counter
    errors=[]; result={}
    try:
        skin=g.read(g.resolve(source['source_skin_snapshot']))
        native=g.read(g.resolve(source['native_binding']))
        expected_positions=np.load(g.resolve(native['actual_positions']),allow_pickle=False)
        expected_uv=np.asarray(skin['uv'],dtype=float).reshape(-1,2)
        # The consumed source-skin snapshot is exported for Godot (V down),
        # while Blender loop UVs retain their native V up convention.  Convert
        # only the comparison coordinates; never rewrite either asset.
        expected_uv=expected_uv*np.asarray([1.,-1.])+np.asarray([0.,1.])
        expected_indices=np.asarray(skin['indices'],dtype=int).reshape(-1,3)
        expected_bones=np.asarray(skin['bones'],dtype=int).reshape(-1,4)
        expected_weights=np.asarray(skin['weights'],dtype=float).reshape(-1,4)
        bone_order=[row['name'] for row in skin['bone_order']]
        if (skin.get('representation')!='source_surface_skin' or expected_positions.shape!=(count,3)
                or expected_uv.shape!=(count,2) or expected_bones.shape!=(count,4)
                or expected_weights.shape!=(count,4) or len(bone_order)!=len(rig.data.bones)
                or not np.isfinite(expected_positions).all() or not np.isfinite(expected_uv).all()
                or not np.isfinite(expected_weights).all() or np.any(expected_indices<0)
                or np.any(expected_indices>=count) or np.any(expected_bones<0)
                or np.any(expected_bones>=len(bone_order))):
            raise ValueError('INVALID_CONSUMED_SOURCE_SKIN_SNAPSHOT')
        base=np.asarray([tuple(v.co) for v in ob.data.vertices[:count]],dtype=float)
        if base.shape!=(count,3) or not np.allclose(base,expected_positions,atol=1e-6):
            errors.append('ACTUAL_FRONT_POSITIONS_DIFFER_FROM_NATIVE_SNAPSHOT')
        if set(bone_order)!=set(rig.data.bones.keys()):
            errors.append('ACTUAL_RIG_BONES_DIFFER_FROM_SOURCE_SKIN_SNAPSHOT')
        # Mesh UVs are loop-domain values.  Every actual source-facing use of a
        # front vertex must retain its exact source UV, including seams.
        mesh=ob.data;uv_layer=mesh.uv_layers.active
        if uv_layer is None:errors.append('ACTUAL_SOURCE_SURFACE_UV_REQUIRED')
        front_triangles=[];uv_by_vertex={i:[] for i in range(count)}
        mesh.calc_loop_triangles()
        for tri in mesh.loop_triangles:
            if mesh.polygons[tri.polygon_index].material_index not in source_material_slots:continue
            ids=tuple(int(i) for i in tri.vertices)
            if any(i<0 or i>=count for i in ids):
                errors.append('SOURCE_FACING_TRIANGLE_OUTSIDE_FRONT_SNAPSHOT');continue
            front_triangles.append(ids)
            if uv_layer:
                for vertex,loop in zip(ids,tri.loops):uv_by_vertex[vertex].append(np.asarray(uv_layer.data[loop].uv,dtype=float))
        if Counter(tuple(sorted(row)) for row in front_triangles)!=Counter(tuple(sorted(row)) for row in expected_indices):
            errors.append('ACTUAL_SOURCE_FRONT_TOPOLOGY_DIFFERS_FROM_SNAPSHOT')
        if uv_layer:
            for index,rows in uv_by_vertex.items():
                if not rows or any(not np.allclose(row,expected_uv[index],atol=1e-6) for row in rows):
                    errors.append('ACTUAL_SOURCE_UV_DIFFERS_FROM_SNAPSHOT');break
        # Rebuild all weights by the exact bone-name order rather than trusting a
        # vertex-group count or a four-influence declaration.
        groups={row.name:row.index for row in ob.vertex_groups}
        actual=np.zeros((count,len(bone_order)),dtype=float)
        for index,vertex in enumerate(ob.data.vertices[:count]):
            for row in vertex.groups:
                name=ob.vertex_groups[row.group].name
                if name in bone_order:actual[index,bone_order.index(name)]=row.weight
        expected=np.zeros_like(actual)
        for influence in range(4):expected[np.arange(count),expected_bones[:,influence]]+=expected_weights[:,influence]
        if not np.allclose(actual,expected,atol=1e-6):errors.append('ACTUAL_SOURCE_WEIGHTS_DIFFER_FROM_SNAPSHOT')
        result={'source_skin_snapshot':source['source_skin_snapshot'],
                'front_triangle_count':len(front_triangles),'snapshot_triangle_count':len(expected_indices),
                'front_uv_and_topology_match':not any(e in errors for e in (
                    'ACTUAL_SOURCE_FRONT_TOPOLOGY_DIFFERS_FROM_SNAPSHOT','ACTUAL_SOURCE_UV_DIFFERS_FROM_SNAPSHOT')),
                'front_weights_match':'ACTUAL_SOURCE_WEIGHTS_DIFFER_FROM_SNAPSHOT' not in errors,
                'front_positions_match':'ACTUAL_FRONT_POSITIONS_DIFFER_FROM_NATIVE_SNAPSHOT' not in errors}
    except Exception as exc:
        errors.append('UNREADABLE_OR_INVALID_SOURCE_SKIN_SNAPSHOT:'+str(exc))
    return result,errors


def _source_sole_uv_checks(mesh, source_material_slots, rgba_path, bindings, count):
    """Prove each sole sample still lands on its original opaque source pixel."""
    import numpy as np
    errors=[];checks={}
    try:
        # Blender's bundled Python does not guarantee Pillow.  Read the exact
        # file image that the material graph resolved above through bpy instead.
        import bpy
        image=next((row for row in bpy.data.images
                    if row.source=='FILE' and not row.packed_file
                    and str(Path(bpy.path.abspath(row.filepath)).resolve())==str(rgba_path)),None)
        if image is None:image=bpy.data.images.load(str(rgba_path),check_existing=False)
        width,height=image.size
        rgba=np.asarray(image.pixels[:],dtype=float).reshape(height,width,4)
        uv=mesh.uv_layers.active
        if uv is None:raise ValueError('ACTUAL_SOURCE_SURFACE_UV_REQUIRED')
        mesh.calc_loop_triangles(); lookup={}
        for tri in mesh.loop_triangles:
            if mesh.polygons[tri.polygon_index].material_index not in source_material_slots:continue
            key=tuple(sorted(int(v) for v in tri.vertices))
            values={int(vertex):np.asarray(uv.data[loop].uv,dtype=float)
                    for vertex,loop in zip(tri.vertices,tri.loops)}
            lookup.setdefault(key,[]).append(values)
        opaque_pixels={}
        for side,binding in bindings.items():
            vertices=np.asarray(binding.get('vertices'),dtype=int); bary=np.asarray(binding.get('barycentric'),dtype=float)
            pixels=np.asarray(binding.get('pixels'),dtype=float); passed=0
            if vertices.shape!=(len(pixels),3) or bary.shape!=vertices.shape:raise ValueError('INVALID_SOURCE_SOLE_BINDING')
            for row,weights,pixel in zip(vertices,bary,pixels):
                if np.any(row<0) or np.any(row>=count):raise ValueError('SOURCE_SOLE_OUTSIDE_FRONT_SNAPSHOT')
                candidates=lookup.get(tuple(sorted(int(v) for v in row)),[])
                if len(candidates)!=1:raise ValueError('SOURCE_SOLE_TRIANGLE_NOT_UNIQUELY_ON_ACTUAL_FRONT')
                source_uv=np.asarray([candidates[0][int(v)] for v in row])
                actual=(source_uv*weights[:,None]).sum(axis=0)
                expected=np.asarray([pixel[0]/width,1-pixel[1]/height])
                x,y=np.floor(pixel).astype(int)
                if (not np.allclose(actual,expected,atol=1e-6) or not (0<=x<width and 0<=y<height)
                        # Blender's image buffer is bottom-up; source pixels use
                        # the usual top-left raster origin.
                        or rgba[height-1-y,x,3]<0.99999):raise ValueError('SOURCE_SOLE_NOT_BOUND_TO_ORIGINAL_OPAQUE_PIXEL')
                passed+=1
            checks[side]={'sample_count':passed,'original_opaque_pixel_binding':True}
            opaque_pixels[side]={tuple(map(int,row)) for row in pixels}
        # Both feet must keep independently bound source pixels.  Reusing the
        # left binding for the right foot would otherwise make a copied sole
        # declaration appear valid without measuring the actual right sole.
        if set(opaque_pixels)=={'l','r'} and opaque_pixels['l'].intersection(opaque_pixels['r']):
            errors.append('SOURCE_LEFT_RIGHT_OPAQUE_PIXEL_SAMPLES_NOT_DISTINCT')
    except Exception as exc:
        errors.append(str(exc))
    return checks,errors


def collect_source_preserving_surface(scene,contract):
    """Collect actual scene facts for a reviewed ImageGen source surface.

    The contract contains source references and independent barycentric sole
    bindings.  It never turns source-image regions into invented generic anatomy
    parts, and it accepts no extra render-visible geometry or texture.
    """
    import bpy
    import numpy as np
    errors=[]; source=contract.get('source',{}); surface=contract.get('surface',{})
    camera=scene.camera
    for key in ('source_receipt','source_green','source_rgba','neutral',
                'native_binding','sole_binding_evidence','source_skin_snapshot',
                'surface_sampler'):
        try:g.resolve(source[key])
        except Exception:errors.append('MISSING_OR_UNRESOLVABLE_SOURCE_BINDING:'+key)
    for key in ('mesh','rig','visible_front_vertex_count','fixed_native_neutral_sole_floor_m'):
        if key not in surface:errors.append('MISSING_SOURCE_SURFACE_DECLARATION:'+key)
    mesh_name=surface.get('mesh','');rig_name=surface.get('rig','')
    ob=bpy.data.objects.get(mesh_name); rig=bpy.data.objects.get(rig_name)
    if camera is None:errors.append('NO_REGISTERED_CAMERA')
    if ob is None or ob.type!='MESH':errors.append('SOURCE_SURFACE_MESH_REQUIRED')
    if rig is None or rig.type!='ARMATURE':errors.append('SOURCE_SURFACE_RIG_REQUIRED')
    visible_meshes=[row.name for row in scene.objects if row.type=='MESH' and not object_hidden(row)]
    if visible_meshes!=[mesh_name]:errors.append('EXTRA_OR_MISSING_RENDER_VISIBLE_SOURCE_SURFACE')
    objects=[]; source_sole={}; actual_images=[]; snapshot={}; sole_uv={}
    if ob is not None and ob.type=='MESH':
        mesh=ob.data;mesh.calc_loop_triangles(); closed=_closed_mesh_summary(mesh)
        skin=_skin_summary(ob)
        material_errors=[]; front_faces=[]; closure_faces=[]; source_material_slots=set(); closure_material_slots=set()
        expected_rgba=None
        try:expected_rgba=str(g.resolve(source['source_rgba']))
        except Exception:expected_rgba=None
        for slot_index,slot in enumerate(ob.material_slots):
            images,graph_errors=material_graph(slot.material,'source_surface')
            material_errors.extend(graph_errors)
            slot_paths=[]
            for node in images:
                if not node.image:
                    material_errors.append('UNBOUND_SOURCE_TEXTURE_NODE');continue
                if node.image.packed_file or node.image.source!='FILE':
                    material_errors.append('PACKED_OR_GENERATED_SOURCE_TEXTURE')
                path=str(Path(bpy.path.abspath(node.image.filepath)).resolve())
                actual_images.append(path)
                slot_paths.append(path)
                if expected_rgba is None or path!=expected_rgba:
                    material_errors.append('SOURCE_TEXTURE_DIFFERS_FROM_REVIEWED_RGBA')
                if node.inputs['Vector'].is_linked:
                    upstream=node.inputs['Vector'].links[0].from_node
                    if not mesh.uv_layers.active or upstream.type!='UVMAP' or upstream.uv_map!=mesh.uv_layers.active.name:
                        material_errors.append('UNRESOLVED_SOURCE_SURFACE_UV')
                if node.projection!='FLAT' or node.interpolation not in ('Linear','Closest'):
                    material_errors.append('UNSUPPORTED_SOURCE_TEXTURE_SAMPLING')
            exact_front_errors=[]
            if slot_paths:
                exact_front_errors=_exact_source_front_material(slot.material,expected_rgba)
                material_errors.extend(exact_front_errors)
                if (len(slot_paths)!=1 or slot_paths[0]!=expected_rgba or graph_errors or exact_front_errors):
                    material_errors.append('INVALID_REVIEWED_SOURCE_FRONT_MATERIAL')
                else:
                    source_material_slots.add(slot_index)
            elif _transparent_closure_material(slot.material):
                closure_material_slots.add(slot_index)
            else:
                material_errors.append('UNOBSERVED_CLOSURE_MUST_BE_TRANSPARENT_ONLY')
        for polygon in mesh.polygons:
            if polygon.material_index>=len(ob.material_slots):
                material_errors.append('INVALID_SOURCE_SURFACE_MATERIAL_INDEX');continue
            if polygon.material_index in source_material_slots:front_faces.append(polygon.index)
            elif polygon.material_index in closure_material_slots:closure_faces.append(polygon.index)
            else:material_errors.append('UNCLASSIFIED_SOURCE_SURFACE_FACE_MATERIAL')
        depsgraph=bpy.context.evaluated_depsgraph_get(); evaluated=ob.evaluated_get(depsgraph)
        evaluated_mesh=evaluated.to_mesh()
        try:
            positions=np.asarray([tuple(v.co) for v in evaluated_mesh.vertices],dtype=float)
        finally:evaluated.to_mesh_clear()
        binding_data={}; binding_ref=source.get('sole_binding_evidence')
        try:
            evidence=g.read(g.resolve(binding_ref));binding_data=evidence.get('visible_sole_bindings',{})
        except Exception:
            errors.append('UNREADABLE_INDEPENDENT_SOURCE_SOLE_BINDINGS')
        count=surface.get('visible_front_vertex_count',0)
        if not isinstance(count,int) or count<3 or positions.shape[0]<count:
            errors.append('INVALID_VISIBLE_FRONT_VERTEX_COUNT')
        else:
            source_sole,sample_errors=_source_binding_samples(positions[:count],binding_data,count)
            errors.extend(sample_errors)
            snapshot, snapshot_errors=_source_surface_snapshot_checks(
                ob,rig,source_material_slots,source,count,binding_data)
            errors.extend(snapshot_errors)
            sole_uv,sole_uv_errors=_source_sole_uv_checks(
                mesh,source_material_slots,g.resolve(source['source_rgba']),binding_data,count)
            errors.extend(sole_uv_errors)
        if not isinstance(count,int) or count<3 or positions.shape[0]<count:
            snapshot={};sole_uv={}
        front_vertices=sorted({index for face in mesh.polygons if face.index in front_faces for index in face.vertices})
        objects=[{'name':ob.name,'role':'source_preserving_surface','hidden':object_hidden(ob),
                  'vertices':len(mesh.vertices),'polygon_count':len(mesh.polygons),
                  'front_material_faces':len(front_faces),'closure_faces':len(closure_faces),
                  'front_vertices':len(front_vertices),'front_vertex_min':front_vertices[0] if front_vertices else None,
                  'front_vertex_max':front_vertices[-1] if front_vertices else None,
                  'source_images':sorted(set(actual_images)),
                  'material_errors':sorted(set(material_errors)),
                  'source_image_sha256':ob.get('source_image_sha256'),
                  'visible_surface_authority':ob.get('visible_surface_authority'),
                  'modifier_types':[m.type for m in ob.modifiers if m.show_render],
                  **closed,**skin}]
    return {'schema':1,'method':SOURCE_SURFACE_METHOD,'collector':g.ref(__file__),
            'blend':g.ref(bpy.data.filepath),'scene':{'name':scene.name,'frame':scene.frame_current,
            'unit_scale':scene.unit_settings.scale_length,'view':scene.get('generation_view'),
            'camera':camera_state(scene),'render':[scene.render.resolution_x,scene.render.resolution_y,
            scene.render.resolution_percentage]},'contract':contract,'charts':{},'triangles':[],
            'objects':objects,'source_sole_samples':source_sole,
            'source_snapshot':snapshot,'source_sole_uv_checks':sole_uv,
            'source_sole_binding_evidence':source.get('sole_binding_evidence'),
            'errors':sorted(set(errors))}


def collect_scene():
    import bpy
    scene=bpy.context.scene
    contract=json.loads(scene.get('generation_mesh_contract','{}'))
    if is_source_preserving_surface_kind(contract.get('kind')):
        return collect_source_preserving_surface(scene,contract)
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


def validate_source_preserving_surface(data):
    """Validate a measured source-surface scene without generic anatomy claims."""
    import numpy as np
    errors=data.get('errors',[])[:]
    if data.get('schema')!=1 or data.get('method')!=SOURCE_SURFACE_METHOD:
        raise ValueError('ACTUAL_SOURCE_SURFACE_PREFLIGHT_REQUIRED')
    if g.resolve(data['collector'])!=Path(__file__).resolve():
        raise ValueError('WRONG_SOURCE_SURFACE_COLLECTOR')
    g.resolve(data['blend'])
    contract=data.get('contract',{})
    kind=contract.get('kind')
    if contract.get('schema')!=1 or kind not in (SOURCE_SURFACE_KIND,SOURCE_SURFACE_CAMERA_PLANE_KIND):
        errors.append('EXPLICIT_SOURCE_SURFACE_CONTRACT_REQUIRED')
    if data.get('charts') or data.get('triangles'):
        errors.append('GENERIC_UV_CHART_SCHEMA_FORBIDDEN_FOR_SOURCE_SURFACE')
    if contract.get('required_parts') or contract.get('attachments') or contract.get('sole_vertex_ids'):
        errors.append('GENERIC_ANATOMICAL_PART_SCHEMA_FORBIDDEN_FOR_SOURCE_SURFACE')
    source=contract.get('source',{}); surface=contract.get('surface',{})
    required_source={'source_receipt','source_green','source_rgba','neutral',
                     'native_binding','sole_binding_evidence','source_skin_snapshot',
                     'surface_sampler'}
    if kind==SOURCE_SURFACE_CAMERA_PLANE_KIND:
        # Camera-plane first poses carry two additional, independently measured
        # inputs.  Give them a separate exact schema rather than weakening the
        # original source-surface contract or accepting arbitrary metadata.
        required_source |= {'camera_plane_calf_witness','raw_tripo_pose_matrices'}
    if set(source)!=required_source:
        errors.append('EXACT_SOURCE_SURFACE_BINDING_SCHEMA_REQUIRED')
    else:
        for key in required_source:
            try:g.resolve(source[key])
            except Exception:errors.append('UNRESOLVABLE_SOURCE_SURFACE_BINDING:'+key)
        if source['surface_sampler']!=g.ref(ROOT/'tools/character_pipeline/source_surface_sampling.py'):
            errors.append('EXACT_SOURCE_SURFACE_SAMPLER_REQUIRED')
        if kind==SOURCE_SURFACE_CAMERA_PLANE_KIND:
            try:
                witness=g.read(g.resolve(source['camera_plane_calf_witness']))
                skin=g.read(g.resolve(source['source_skin_snapshot']))
                matrices=np.load(g.resolve(source['raw_tripo_pose_matrices']),allow_pickle=False)
                bone_count=len(skin.get('bone_order',[]))
                sections=witness.get('cross_sections')
                if (witness.get('kind')!='MICA_E_camera_plane_calf_width_witness'
                        or witness.get('source_rgba')!=source['source_rgba']
                        or witness.get('source_skin')!=source['source_skin_snapshot']
                        or not isinstance(sections,list) or len(sections)!=3
                        or not 0.90<=float(witness.get('minimum_retained_width_ratio',0.0))<=1.0
                        or matrices.shape!=(97,bone_count,4,4)
                        or not np.isfinite(matrices).all()):
                    errors.append('EXACT_CAMERA_PLANE_SOURCE_EVIDENCE_REQUIRED')
            except Exception:
                errors.append('EXACT_CAMERA_PLANE_SOURCE_EVIDENCE_REQUIRED')
    required_surface={'mesh','rig','visible_front_vertex_count','fixed_native_neutral_sole_floor_m',
                      'source_image_sha256','visible_surface_authority'}
    if set(surface)!=required_surface:
        errors.append('EXACT_SOURCE_SURFACE_DECLARATION_REQUIRED')
    count=surface.get('visible_front_vertex_count')
    if isinstance(count,bool) or not isinstance(count,int) or count<3:
        errors.append('VALID_VISIBLE_FRONT_VERTEX_COUNT_REQUIRED')
    try:floor=g.finite(surface.get('fixed_native_neutral_sole_floor_m'))
    except Exception:floor=float('nan');errors.append('FINITE_FIXED_NATIVE_REST_FLOOR_REQUIRED')
    if not np.isfinite(floor):errors.append('FINITE_FIXED_NATIVE_REST_FLOOR_REQUIRED')
    if surface.get('visible_surface_authority')!=SOURCE_SURFACE_AUTHORITY:
        errors.append('EXACT_VISIBLE_SOURCE_AUTHORITY_REQUIRED')
    if source and 'neutral' in source and 'native_binding' in source:
        try:
            neutral=g.read(g.resolve(source['neutral']))
            binding=g.read(g.resolve(source['native_binding']))
            if (neutral.get('rig_name')!=surface.get('rig') or neutral.get('mesh_name')!=surface.get('mesh')
                    or neutral.get('visible_front_vertex_count')!=count
                    or not np.isclose(g.finite(neutral.get('fixed_native_neutral_sole_floor_m')),floor,atol=1e-9)
                    or binding.get('inputs',{}).get('report')!=source['neutral']
                    or binding.get('inputs',{}).get('blend')!=neutral.get('blend')):
                errors.append('NEUTRAL_AND_NATIVE_BINDING_SURFACE_MISMATCH')
        except Exception:
            errors.append('UNREADABLE_NEUTRAL_OR_NATIVE_BINDING_EVIDENCE')
    expected_binding=source.get('sole_binding_evidence')
    if data.get('source_sole_binding_evidence')!=expected_binding:
        errors.append('INDEPENDENT_SOURCE_SOLE_EVIDENCE_MISMATCH')
    evidence_bindings={}
    try:
        evidence_bindings=g.read(g.resolve(expected_binding)).get('visible_sole_bindings',{})
    except Exception:
        errors.append('UNREADABLE_INDEPENDENT_SOURCE_SOLE_EVIDENCE')
    samples=data.get('source_sole_samples',{})
    if set(samples)!= {'l','r'} or set(evidence_bindings)!= {'l','r'}:
        errors.append('DISTINCT_LEFT_RIGHT_SOURCE_SOLE_SAMPLES_REQUIRED')
    for side in ('l','r'):
        row=samples.get(side,{});binding=evidence_bindings.get(side,{})
        try:
            expected_count=len(binding['vertices'])
            positions=np.asarray(row['positions_world_m'],dtype=float)
            if (row.get('sample_count')!=expected_count or expected_count<3
                    or positions.shape!=(expected_count,3) or not np.isfinite(positions).all()
                    or not np.isclose(float(row['min_world_z_m']),float(positions[:,2].min()),atol=1e-9)
                    or not np.isclose(float(row['max_world_z_m']),float(positions[:,2].max()),atol=1e-9)):
                errors.append('ACTUAL_BARYCENTRIC_SOURCE_SOLE_COVERAGE:'+side)
        except Exception:
            errors.append('ACTUAL_BARYCENTRIC_SOURCE_SOLE_COVERAGE:'+side)
    snapshot=data.get('source_snapshot',{})
    if (snapshot.get('source_skin_snapshot')!=source.get('source_skin_snapshot')
            or snapshot.get('front_triangle_count')!=snapshot.get('snapshot_triangle_count')
            or snapshot.get('front_uv_and_topology_match') is not True
            or snapshot.get('front_weights_match') is not True
            or snapshot.get('front_positions_match') is not True):
        errors.append('ACTUAL_SOURCE_SNAPSHOT_PRESERVATION_REQUIRED')
    uv_checks=data.get('source_sole_uv_checks',{})
    for side in ('l','r'):
        expected_count=len(evidence_bindings.get(side,{}).get('vertices',[]))
        if (uv_checks.get(side,{}).get('sample_count')!=expected_count
                or uv_checks.get(side,{}).get('original_opaque_pixel_binding') is not True):
            errors.append('ACTUAL_SOURCE_SOLE_UV_OPAQUE_BINDING_REQUIRED:'+side)
    observed=data.get('objects',[])
    if len(observed)!=1:
        errors.append('EXACTLY_ONE_SOURCE_SURFACE_MESH_REQUIRED')
    else:
        ob=observed[0]; expected_rgba=[]
        try:expected_rgba=[str(g.resolve(source['source_rgba']))]
        except Exception:pass
        if (ob.get('name')!=surface.get('mesh') or ob.get('role')!='source_preserving_surface'
                or ob.get('hidden') or ob.get('armature')!=surface.get('rig')
                or ob.get('armature_modifier_count')!=1 or ob.get('modifier_types')!=['ARMATURE']
                or ob.get('unweighted_vertices') or ob.get('invalid_bone_weights') or ob.get('bad_weight_sums')
                or ob.get('boundary_edges') or ob.get('nonmanifold_edges') or ob.get('degenerate_faces')
                or ob.get('source_images')!=expected_rgba or ob.get('material_errors')
                or ob.get('source_image_sha256')!=surface.get('source_image_sha256')
                or ob.get('visible_surface_authority')!=SOURCE_SURFACE_AUTHORITY):
            errors.append('ACTUAL_SOURCE_SURFACE_OR_SKIN_MISMATCH')
        if (not isinstance(count,int) or ob.get('vertices')!=count*2
                or ob.get('front_vertices')!=count or ob.get('front_vertex_min')!=0
                or ob.get('front_vertex_max')!=count-1 or not ob.get('front_material_faces')
                or not ob.get('closure_faces')):
            errors.append('ACTUAL_CLOSED_SOURCE_FRONT_AND_CLOSURE_MISMATCH')
    scene=data.get('scene',{});camera=scene.get('camera') or {}
    if (scene.get('unit_scale')!=1 or scene.get('render')!=[1920,1920,100]
            or camera.get('render')!=[1920,1920,100] or camera.get('film_transparent') is not True
            or camera.get('type')!='ORTHO' or not scene.get('view')):
        errors.append('SOURCE_SURFACE_NATIVE_ORTHOGRAPHIC_CAPTURE_REQUIRED')
    construction=contract.get('construction')
    if not isinstance(construction,dict) or set(construction)!={'build_receipt','build_attempt'}:
        errors.append('SOURCE_SURFACE_BUILD_CONSTRUCTION_REQUIRED')
    return {'stage':'mesh','verdict':'FAIL' if errors else 'HOLD_NATIVE_FIRST_POSE',
            'errors':sorted(set(errors)),'blend':data['blend'],
            'scene_sha256':g.canonical(scene),
            'note':'Measured source-preserving surface preflight permits only one independently reviewed native pose.'}


def validate_collected(data):
    if data.get('method')==SOURCE_SURFACE_METHOD:
        return validate_source_preserving_surface(data)
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
