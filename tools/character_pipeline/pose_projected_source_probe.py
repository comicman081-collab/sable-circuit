"""Bounded Blender child for one source-preserving MICA E contact pose.

This is the reviewed builder entrypoint only. The distinct runner owns the
process and creates the fresh output directory; this child cannot be used as an
ungated diagnostic or animation exporter.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
import generation_harness as g
import source_surface_sampling as sampling
import collect_generation_mesh_preflight as collector


def implementation():
    return {
        'builder': __file__,
        'runner': ROOT / 'tools/character_pipeline/run_mica_E_first_contact_pose.py',
        'generation_harness': g.__file__,
        'surface_sampler': sampling.__file__,
        'collector': collector.__file__,
        'handoff_verifier': ROOT / 'tools/character_pipeline/verify_mica_E_blender_child_handoff.py',
        'neutral_reuse_admission': ROOT / 'tools/character_pipeline/historical_neutral_reuse_admission.py',
        'capture_filter': ROOT / 'tools/character_pipeline/capture_neutral_pixel_filter.py',
        'source_verifier': ROOT / 'tools/character_pipeline/verify_existing_source.py',
    }


def _exact_ref(value, expected, error):
    if value != expected:
        raise ValueError(error)


def _verify_child_claim(reference, role, inputs, handoff, direction):
    """Read the external verifier's immutable claim without invoking intake.

    ``g.verify_build_claim`` deliberately re-audits the complete build plan.
    Calling it from Blender would re-enter the Pillow source-intake path that
    the external verifier already owns.  The permit binds the claim's bytes;
    this narrower check confirms its declared role and exact handoff fields.
    """
    path=g.resolve(reference);claim=g.read(path)
    expected={'stage':'build_execution_claim','role':role,'attempt':inputs['build_attempt'],
              'build_receipt':inputs['build_receipt'],
              'executable':inputs[role],'direction':direction,'output_root':handoff['output_root']}
    if claim!=expected:raise ValueError('STALE_OR_FORGED_EXTERNAL_'+role.upper()+'_CLAIM')
    return g.ref(path)


def child(args):
    out = g.local(args.out)
    inputs = g.read(out / 'INPUTS.json')
    for reference in inputs.values():
        g.resolve(reference)
    for key, path in implementation().items():
        _exact_ref(inputs.get(key), g.ref(path), 'EXACT_IMPLEMENTATION_REQUIRED:' + key)
    if args.direction != 'E':
        raise ValueError('THIS_FIRST_POSE_BUILDER_IS_E_ONLY')

    handoff = g.read(g.resolve(inputs['execution_handoff']))
    expected_handoff = {
        'stage': 'reviewed_blender_child_handoff',
        'build_receipt': inputs['build_receipt'],
        'build_attempt': inputs['build_attempt'],
        'runner': g.ref(ROOT / 'tools/character_pipeline/run_mica_E_first_contact_pose.py'),
        'builder': g.ref(__file__),
        'verifier': inputs['handoff_verifier'],
        'direction': args.direction,
        'source_receipt': inputs['source_receipt'],
        'source_green': inputs['source_green'],
        'source_rgba': inputs['source_rgba'],
        'neutral_admission': inputs['neutral_admission'],
    }
    if any(handoff.get(key) != value for key, value in expected_handoff.items()):
        raise ValueError('EXACT_EXTERNAL_REVIEWED_BUILDER_HANDOFF_REQUIRED')
    if not isinstance(handoff.get('readonly_inputs'), list):
        raise ValueError('EXACT_READONLY_INPUT_HANDOFF_REQUIRED')
    runtime=Path(handoff.get('python_runtime',''))
    if not runtime.is_file() or hashlib.sha256(runtime.read_bytes()).hexdigest()!=handoff.get('python_runtime_sha256'):
        raise ValueError('EXACT_EXTERNAL_VERIFIER_RUNTIME_REQUIRED')
    if g.local(handoff.get('child_permit_path',''))!=out/'BLENDER_CHILD_PERMIT.json':
        raise ValueError('EXACT_CHILD_PERMIT_DESTINATION_REQUIRED')
    for item in handoff['readonly_inputs']:
        g.resolve(item['asset'])
        g.resolve(item['license'])

    # Blender deliberately does not import the Pillow-backed source intake.
    # The project Python verifier checks the actual existing ImageGen receipt,
    # current neutral admission and exclusive builder claim, then atomically
    # creates this one-use permit.
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
    result=subprocess.run([str(runtime),'-B',str(g.resolve(inputs['handoff_verifier'])), '--out',str(out)],
                          cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if result.returncode:
        raise ValueError('EXTERNAL_BLENDER_CHILD_HANDOFF_VERIFICATION_FAILED:'+result.stderr[-1000:])
    permit_path=out/'BLENDER_CHILD_PERMIT.json';permit=g.read(permit_path)
    if handoff.get('output_root')!=out.relative_to(ROOT).as_posix():
        raise ValueError('EXACT_CHILD_OUTPUT_ROOT_REQUIRED')
    runner_claim=_verify_child_claim(permit.get('runner_claim'), 'runner', inputs, handoff, args.direction)
    builder_claim=_verify_child_claim(permit.get('builder_claim'), 'builder', inputs, handoff, args.direction)
    expected_permit={'schema':1,'stage':'verified_blender_child_permit','inputs':g.ref(out/'INPUTS.json'),
                     'handoff':g.ref(g.resolve(inputs['execution_handoff'])),'runner_claim':runner_claim,
                     'builder_claim':builder_claim,'source_receipt':inputs['source_receipt'],
                     'source_green':inputs['source_green'],'source_rgba':inputs['source_rgba'],
                     'neutral_admission':inputs['neutral_admission'],'verifier':inputs['handoff_verifier'],
                     'production_ready':False,
                     'note':'Exclusive one-child permit. A crash consumes this build attempt; do not rerun it.'}
    if permit!=expected_permit:raise ValueError('STALE_OR_FORGED_BLENDER_CHILD_PERMIT')
    consumption={'schema':1,'stage':'blender_child_execution_consumption','permit':g.ref(permit_path),
                 'inputs':g.ref(out/'INPUTS.json'),'runner_claim':runner_claim,'builder_claim':builder_claim}
    g.write(out/'BLENDER_CHILD_CONSUMPTION.json',consumption)

    import bpy
    import numpy as np
    from mathutils import Matrix

    neutral = g.read(g.resolve(inputs['neutral']))
    neutral_inputs = g.read(g.resolve(neutral['inputs']))
    anchor = g.read(g.resolve(inputs['anchor']))
    prior = g.read(g.resolve(anchor['inputs']['prior']))
    if (anchor['inputs']['prior'] != neutral_inputs['ik'] or anchor['failures']
            or anchor.get('actual_native_rest') != neutral['actual_native_rest']
            or anchor.get('target_sample_count') != 97):
        raise ValueError('EXACT_FEASIBLE_POSES_ON_SAME_NEUTRAL_REQUIRED')
    if anchor['root_floor_correction'] or anchor['limb_stretch'] or anchor['weights_changed']:
        raise ValueError('SOURCE_PRESERVING_FIXED_LENGTH_POSE_REQUIRED')

    box = g.read(g.resolve(inputs['box_capture']))
    _exact_ref(box.get('inputs'), neutral['inputs'], 'BOX_CAPTURE_NEUTRAL_INPUTS_CHANGED')
    box_inputs = g.read(g.resolve(box['qa_capture_inputs']))
    _exact_ref(box_inputs.get('neutral'), inputs['neutral'], 'BOX_CAPTURE_NEUTRAL_CHANGED')
    _exact_ref(box_inputs.get('blend'), neutral['blend'], 'BOX_CAPTURE_SCENE_CHANGED')
    if (box_inputs.get('source_rgba',{}).get('sha256')!=inputs['source_rgba']['sha256']
            or box.get('source_rgba',{}).get('sha256')!=inputs['source_rgba']['sha256']):
        raise ValueError('BOX_CAPTURE_SOURCE_BYTES_CHANGED')
    _exact_ref(box.get('actual_native_rest'), neutral['actual_native_rest'], 'BOX_REPORT_REST_CHANGED')
    if box.get('pixel_filter_change', {}).get('after') != {'type': 'BOX', 'width': 1.0}:
        raise ValueError('EXACT_BOX_PIXEL_FILTER_REQUIRED')

    native_binding = g.read(g.resolve(inputs['native_binding']))
    _exact_ref(native_binding['inputs'].get('report'), inputs['neutral'], 'NATIVE_BINDING_NEUTRAL_REPORT_CHANGED')
    _exact_ref(native_binding['inputs'].get('blend'), neutral['blend'], 'NATIVE_BINDING_SCENE_CHANGED')
    _exact_ref(native_binding.get('actual_rest'), neutral['actual_native_rest'], 'NATIVE_BINDING_REST_CHANGED')

    # The neutral probe retains its original historical source receipt.  It is
    # admissible only through a separate, current reuse receipt that proves the
    # new reviewed source bytes match that historical neutral mesh; never by
    # rewriting the historical probe or by invoking ImageGen intake in Blender.
    admission = g.read(g.resolve(inputs['neutral_admission']))
    if (admission.get('stage') != 'historical_neutral_source_reuse_admission'
            or admission.get('verdict') != 'PASS_HISTORICAL_NEUTRAL_GEOMETRY_REUSE_ONLY'
            or admission.get('source_receipt') != inputs['source_receipt']
            or admission.get('source_green') != inputs['source_green']
            or admission.get('source_rgba') != inputs['source_rgba']
            or admission.get('neutral') != inputs['neutral']
            or admission.get('anchor') != inputs['anchor']
            or admission.get('box_capture') != inputs['box_capture']
            or admission.get('native_binding') != inputs['native_binding']):
        raise ValueError('CURRENT_REVIEWED_HISTORICAL_NEUTRAL_ADMISSION_REQUIRED')
    if neutral['source_rgba']['sha256'] != inputs['source_rgba']['sha256']:
        raise ValueError('NEUTRAL_RGBA_BYTES_DIFFER_FROM_REVIEWED_SOURCE')

    rest = np.load(g.resolve(neutral['actual_native_rest']), allow_pickle=False)
    poses = np.load(g.resolve(anchor['proposed_poses']), allow_pickle=False)
    support = g.read(g.resolve(prior['inputs']['support']))
    skin = g.read(g.resolve(support['inputs']['skin']))
    bone_count = len(skin['bone_order'])
    count = int(neutral['visible_front_vertex_count'])
    if (rest.shape != (bone_count, 4, 4) or poses.shape != (97, bone_count, 4, 4)
            or not np.isfinite(rest).all() or not np.isfinite(poses).all()):
        raise ValueError('FINITE_EXACT_NATIVE_REST_AND_DENSE_POSES_REQUIRED')

    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(neutral['blend'])), load_ui=False)
    rig, mesh = bpy.data.objects[neutral['rig_name']], bpy.data.objects[neutral['mesh_name']]
    if rig.matrix_world != Matrix.Identity(4) or mesh.matrix_world != Matrix.Identity(4):
        raise ValueError('UNTRANSFORMED_SOURCE_BINDING_REQUIRED')
    if any(ob.type == 'MESH' and ob != mesh and not ob.hide_render for ob in bpy.data.objects):
        raise ValueError('NO_GUIDE_OR_REPLACEMENT_VISIBLE_GEOMETRY')
    images = []
    for material in mesh.data.materials:
        if material and material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    if node.image.packed_file:
                        raise ValueError('NO_PACKED_REPLACEMENT_ART')
                    images.append(g.ref(Path(bpy.path.abspath(node.image.filepath))))
    # The neutral probe is byte-bound to the reviewed RGBA derivative, but it
    # stores a project-local immutable copy.  Check that exact copy first, then
    # bind the new reviewed scene directly to the admitted derivative before it
    # is saved.  This is a pathname change between byte-identical source pixels,
    # never a repaint or a substitute texture.
    if not images or any(image != neutral['source_rgba'] for image in images):
        raise ValueError('NEUTRAL_SOURCE_RGBA_MATERIAL_CHANGED')
    if neutral['source_rgba']['sha256'] != inputs['source_rgba']['sha256']:
        raise ValueError('NEUTRAL_RGBA_BYTES_DIFFER_FROM_REVIEWED_SOURCE')
    for material in mesh.data.materials:
        if material and material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    node.image.filepath = str(g.resolve(inputs['source_rgba']))
                    node.image.reload()
    rebound = []
    for material in mesh.data.materials:
        if material and material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    rebound.append(g.ref(Path(bpy.path.abspath(node.image.filepath))))
    if not rebound or any(image != inputs['source_rgba'] for image in rebound):
        raise ValueError('DIRECT_REVIEWED_RGBA_MATERIAL_BINDING_REQUIRED')
    # The historical neutral already has the strict transparent/emission source
    # graph.  Its image node omitted an explicit Vector connection, however,
    # which leaves Blender free to substitute generated coordinates.  Add only
    # the mesh's existing UV layer to the existing source node; this preserves
    # the ImageGen pixels and makes the original loop UVs the sole mapping.
    active_uv=mesh.data.uv_layers.active
    if active_uv is None:raise ValueError('ACTUAL_SOURCE_SURFACE_UV_REQUIRED')
    source_slots=set();closure_slots=set()
    for slot,material in enumerate(mesh.data.materials):
        if not material or not material.use_nodes:raise ValueError('SOURCE_SURFACE_MATERIAL_GRAPH_REQUIRED')
        texture_nodes=[node for node in material.node_tree.nodes if node.type=='TEX_IMAGE' and node.image]
        if texture_nodes:
            if len(texture_nodes)!=1:raise ValueError('EXACTLY_ONE_SOURCE_IMAGE_NODE_REQUIRED')
            texture=texture_nodes[0];nodes=material.node_tree.nodes;links=material.node_tree.links
            uv_nodes=[node for node in nodes if node.type=='UVMAP']
            if len(uv_nodes)>1:raise ValueError('ONE_DIRECT_SOURCE_UV_MAP_REQUIRED')
            uv_node=uv_nodes[0] if uv_nodes else nodes.new('ShaderNodeUVMap')
            uv_node.uv_map=active_uv.name
            if texture.inputs['Vector'].is_linked:
                if texture.inputs['Vector'].links[0].from_node!=uv_node:
                    raise ValueError('SOURCE_TEXTURE_VECTOR_REMAP_FORBIDDEN')
            else:links.new(uv_node.outputs['UV'],texture.inputs['Vector'])
            if texture.projection!='FLAT' or texture.interpolation not in ('Linear','Closest'):
                raise ValueError('UNREVIEWED_SOURCE_TEXTURE_SAMPLING')
            graph_errors=collector._exact_source_front_material(material,g.resolve(inputs['source_rgba']))
            if graph_errors:raise ValueError('SOURCE_FRONT_GRAPH_NOT_EXACT:'+','.join(graph_errors))
            source_slots.add(slot)
        elif collector._transparent_closure_material(material):
            closure_slots.add(slot)
        else:raise ValueError('UNOBSERVED_CLOSURE_MUST_BE_TRANSPARENT_ONLY')
    if not source_slots or not closure_slots:raise ValueError('EXACT_SOURCE_AND_TRANSPARENT_CLOSURE_MATERIALS_REQUIRED')
    for index, row in enumerate(skin['bone_order']):
        matrix = np.asarray(rig.data.bones[row['name']].matrix_local)
        if matrix.shape != (4, 4) or not np.isfinite(matrix).all() or np.max(np.abs(matrix - rest[index])) > 1e-6:
            raise ValueError('ACTUAL_NEUTRAL_REST_CHANGED')
        rig.pose.bones[row['name']].matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()

    def vertices():
        evaluated_object = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        evaluated_mesh = evaluated_object.to_mesh()
        try:
            return np.asarray([tuple(vertex.co) for vertex in evaluated_mesh.vertices], dtype=float)
        finally:
            evaluated_object.to_mesh_clear()

    actual_neutral = vertices()
    native_positions = np.load(g.resolve(native_binding['actual_positions']), allow_pickle=False)
    if (actual_neutral.ndim != 2 or actual_neutral.shape[1:] != (3,) or actual_neutral.shape[0] < count
            or native_positions.shape != (count, 3) or not np.isfinite(actual_neutral).all()
            or not np.isfinite(native_positions).all()
            or np.max(np.abs(actual_neutral[:count] - native_positions)) > 1e-6):
        raise ValueError('ACTUAL_NEUTRAL_SURFACE_DIFFERS_FROM_R03_NATIVE_BINDING')
    floor = min(float(sampling.sample_positions(actual_neutral, binding)[:, 2].min())
                for binding in prior['visible_sole_bindings'].values())
    if abs(floor - neutral['fixed_native_neutral_sole_floor_m']) > 1e-6:
        raise ValueError('FIXED_NATIVE_REST_FLOOR_CHANGED')

    sample = 46  # Native dense sample 46 is original Tripo source contact 23.
    expected_support = anchor['sides']['l']['rows'][sample]
    if expected_support.get('sample') != sample or expected_support.get('support') is not True:
        raise ValueError('EXACT_LEFT_CONTACT_SAMPLE_REQUIRED')
    # PoseBone.matrix resolves the child basis against the evaluated parent.
    # The reviewed source order is parent-before-child, so update after every
    # parent assignment; batching them reads a stale parent and double-applies
    # its transform. This changes no source pixels, REST matrix, UV, or weights.
    for index, row in enumerate(skin['bone_order']):
        parent = int(row['parent'])
        if parent >= index or parent < -1:
            raise ValueError('PARENT_BEFORE_CHILD_SOURCE_BONE_ORDER_REQUIRED')
        rig.pose.bones[row['name']].matrix = Matrix(poses[sample, index].tolist())
        bpy.context.view_layer.update()
    pose_error = max(float(np.max(np.abs(np.asarray(rig.pose.bones[row['name']].matrix) - poses[sample, index])))
                     for index, row in enumerate(skin['bone_order']))
    if not np.isfinite(pose_error) or pose_error > 5e-5:
        raise ValueError('NATIVE_POSE_DIFFERS_FROM_REVIEWED_NUMERIC_SOLVE')
    actual = vertices()
    weights = np.asarray(skin['weights'], dtype=float).reshape(-1, 4)
    indices = np.asarray(skin['bones'], dtype=int).reshape(-1, 4)
    if (weights.shape != (count, 4) or indices.shape != (count, 4) or not np.isfinite(weights).all()
            or np.any(indices < 0) or np.any(indices >= bone_count)):
        raise ValueError('FINITE_EXACT_SOURCE_SKIN_BINDING_REQUIRED')
    homogeneous = np.c_[actual_neutral[:count], np.ones(count)]
    deformation = poses[sample] @ np.linalg.inv(rest)
    predicted = (np.einsum('nkij,nj->nki', deformation[indices], homogeneous)
                 * weights[:, :, None]).sum(axis=1)[:, :3]
    vertex_error = float(np.max(np.linalg.norm(actual[:count] - predicted, axis=1)))
    if not np.isfinite(vertex_error) or vertex_error > 1e-5:
        raise ValueError('ACTUAL_NATIVE_SKIN_DEFORMATION_DIFFERS_FROM_NUMERIC_SOLVE')
    clearances = {side: float(sampling.sample_positions(actual, binding)[:, 2].min() - floor)
                  for side, binding in prior['visible_sole_bindings'].items()}
    expected_clearance = float(prior['samples'][23]['feet']['l']['desired_clearance_m'])
    if (not np.isfinite(expected_clearance) or not 0.0 <= clearances['l'] <= 0.004
            or abs(clearances['l'] - expected_clearance) > 5e-5):
        raise ValueError('ACTUAL_LEFT_SUPPORT_CLEARANCE_DOES_NOT_MATCH_R03_FIXED_FLOOR')

    scene = bpy.context.scene
    if scene.render.resolution_x != 1920 or scene.render.resolution_y != 1920 or scene.render.resolution_percentage != 100:
        raise ValueError('EXACT_NATIVE_CAPTURE_REQUIRED')
    scene.cycles.pixel_filter_type = 'BOX'
    scene.cycles.filter_width = 1.0
    if scene.cycles.pixel_filter_type != 'BOX' or abs(scene.cycles.filter_width - 1.0) > 1e-9:
        raise ValueError('BOX_FILTER_WAS_NOT_APPLIED_TO_CONTACT_RENDER')
    scene.cycles.samples = 64
    scene.cycles.use_denoising = False
    scene['generation_view'] = args.direction
    contract = {
        'schema': 1,
        'kind': collector.SOURCE_SURFACE_KIND,
        'source': {
            'source_receipt': inputs['source_receipt'],
            'source_green': inputs['source_green'],
            'source_rgba': inputs['source_rgba'],
            'neutral': inputs['neutral'],
            'native_binding': inputs['native_binding'],
            'sole_binding_evidence': anchor['inputs']['prior'],
            'source_skin_snapshot': support['inputs']['skin'],
            'surface_sampler': g.ref(sampling.__file__),
        },
        'surface': {
            'mesh': neutral['mesh_name'],
            'rig': neutral['rig_name'],
            'visible_front_vertex_count': count,
            'fixed_native_neutral_sole_floor_m': floor,
            'source_image_sha256': inputs['source_green']['sha256'],
            'visible_surface_authority': collector.SOURCE_SURFACE_AUTHORITY,
        },
        'construction': {'build_receipt': inputs['build_receipt'], 'build_attempt': inputs['build_attempt']},
    }
    scene['generation_mesh_contract'] = json.dumps(contract, sort_keys=True, separators=(',', ':'))
    blend_path = out / 'PROJECTED_SOURCE_CONTACT_L.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    raw = collector.collect_scene()
    if raw['scene']['view'] != args.direction:
        raise ValueError('COLLECTOR_DID_NOT_CAPTURE_E_DIRECTION')
    preflight = collector.validate_collected(raw)
    if preflight['errors']:
        raise ValueError('SOURCE_SURFACE_PREFLIGHT_FAILED:' + ','.join(preflight['errors']))
    g.write(out / 'MESH_PREFLIGHT_RAW.json', raw)
    construction = {
        'scope': 'one source-preserving E contact pose; no cycle, runtime or promotion',
        'inputs': g.ref(out / 'INPUTS.json'),
        'build_receipt': inputs['build_receipt'],
        'build_attempt': inputs['build_attempt'],
        'blend': raw['blend'],
        'readonly_inputs_after': handoff['readonly_inputs'],
        'execution_claims': {'runner': runner_claim, 'builder': builder_claim},
        'child_consumption': g.ref(out / 'BLENDER_CHILD_CONSUMPTION.json'),
    }
    g.write(out / 'CONSTRUCTION.json', construction)
    scene.render.filepath = str(out / 'CONTACT_L_NATIVE_1920.png')
    bpy.ops.render.render(write_still=True)
    render = {
        'method': 'same_process_native_pose_and_mesh_preflight',
        'scope': 'one E left-contact pose only; no gait or runtime approval',
        'image': g.ref(out / 'CONTACT_L_NATIVE_1920.png'),
        'blend': raw['blend'],
        'view': args.direction,
        'scene_sha256': g.canonical(raw['scene']),
        'mesh_preflight': g.ref(out / 'MESH_PREFLIGHT_RAW.json'),
        'construction': g.ref(out / 'CONSTRUCTION.json'),
    }
    g.write(out / 'FIRST_POSE_RENDER_RECEIPT.json', render)
    np.save(out / 'ACTUAL_EVALUATED_VERTICES_BLENDER.npy', actual, allow_pickle=False)
    g.write(out / 'POSE_REPORT.json', {
        'scope': 'one native source-preserving contact pose, not cycle or runtime approval',
        'inputs': g.ref(out / 'INPUTS.json'),
        'sample_index': sample,
        'original_reference_sample_index': 23,
        'construction': g.ref(out / 'CONSTRUCTION.json'),
        'actual_pose_max_error': pose_error,
        'actual_evaluated_vertex_max_error_m': vertex_error,
        'native_representation_tolerances': {'matrix_component': 5e-5, 'evaluated_vertex_distance_m': 1e-5},
        'fixed_native_neutral_floor_m': floor,
        'r03_left_contact_clearance_target_m': expected_clearance,
        'actual_visible_sole_clearance_m': clearances,
        'evaluated_vertices': g.ref(out / 'ACTUAL_EVALUATED_VERTICES_BLENDER.npy'),
        'render': render['image'],
        'render_receipt': g.ref(out / 'FIRST_POSE_RENDER_RECEIPT.json'),
        'blend': raw['blend'],
        'production_ready': False,
        'root_floor_correction': False,
        'limb_stretch': False,
    })


def run(_args):
    raise ValueError('DISTINCT_REVIEWED_RUNNER_REQUIRED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--inside', action='store_true')
    parser.add_argument('--direction', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None)
    if not args.inside:
        run(args)
    child(args)
