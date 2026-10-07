"""Import a user-supplied Tripo GLB as motion geometry, never SABLE artwork.

Run through tripo_motion_reference.py so inputs, cache and child lifetime are bound.
The source rig, topology, UVs, textures and native action are preserved. A standing
pose is a separate action; it never rewrites the original bind pose or Run keys.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import generation_harness as g


def vec(v):
    return [float(x) for x in v]


ROLE_MAP = {"root": "Root", "hips": "Hip", "pelvis": "Pelvis", "spine": "Waist",
    "chest": "Spine01", "upperChest": "Spine02", "neck": "NeckTwist01", "head": "Head",
    **{side + role: prefix + bone for side, prefix in [("left", "L_"), ("right", "R_")]
       for role, bone in [("UpperLeg", "Thigh"), ("LowerLeg", "Calf"), ("Foot", "Foot"),
                          ("Toes", "ToeBase"), ("Shoulder", "Clavicle"),
                          ("UpperArm", "Upperarm"), ("LowerArm", "Forearm"), ("Hand", "Hand")]}}


def evaluated_vertices(mesh):
    evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    actual = evaluated.to_mesh()
    try:
        if len(actual.vertices) != len(mesh.data.vertices):
            raise ValueError("SOLE_VERTEX_IDENTITY_CHANGED")
        return [vec(evaluated.matrix_world @ v.co) for v in actual.vertices]
    finally:
        evaluated.to_mesh_clear()


def action_digest(action):
    # Blender 5.x layered actions; exact points, handles and interpolation.
    return g.canonical([{"path": f.data_path, "index": f.array_index,
        "points": [{"co": vec(k.co), "left": vec(k.handle_left), "right": vec(k.handle_right),
                    "interpolation": k.interpolation} for k in f.keyframe_points]}
        for layer in action.layers for strip in layer.strips
        for bag in strip.channelbags for f in bag.fcurves])


def make_pack(rig, mesh, action, scene, out, source_ref, intake):
    """Standing and run assets share unchanged bind data and a geometry ledger."""
    run_sha = action_digest(action)
    topology = g.canonical({"vertices": [vec(v.co) for v in mesh.data.vertices],
        "polygons": [list(p.vertices) for p in mesh.data.polygons],
        "uv": [[vec(v.uv) for v in layer.data] for layer in mesh.data.uv_layers],
        "weights": [[[w.group, w.weight] for w in v.groups] for v in mesh.data.vertices]})
    # No pose-as-rest, mesh surgery or rebinding. Identity pose matrices expose
    # the native standing bind surface while the original Run is a separate asset.
    slot = rig.animation_data.action_slot
    rig.animation_data.action = None
    for track in rig.animation_data.nla_tracks:
        track.mute = True
    standing = bpy.data.actions.new("SABLE_REFERENCE_Standing_NativeBind")
    standing.use_fake_user = True
    rig.animation_data.action = standing
    for bone in rig.pose.bones:
        bone.matrix_basis = Matrix.Identity(4)
        bone.keyframe_insert("location", frame=1)
        bone.keyframe_insert("rotation_quaternion", frame=1)
        bone.keyframe_insert("scale", frame=1)
    standing.asset_mark()
    standing.asset_data.description = "Native standing bind pose; Tripo geometry reference only."
    action.asset_mark()
    action.asset_data.description = "Unmodified supplied Run keys at 24 Hz, frames 1..31; reference only."
    rig.data.pose_position = "REST"
    scene.frame_set(1)
    bpy.context.view_layer.update()
    raw = evaluated_vertices(mesh)
    native_height = max(v[2] for v in raw)-min(v[2] for v in raw)
    # One declared global unit conversion; no per-frame ground correction.
    scale = 1.70/native_height
    rig.scale *= scale
    bpy.context.view_layer.update()
    rest = evaluated_vertices(mesh)
    sole_ids = {}
    for side, prefix in [("left", "L_"), ("right", "R_")]:
        group_ids = {mesh.vertex_groups[prefix + name].index for name in ("Foot", "ToeBase")}
        candidates = [v.index for v in mesh.data.vertices
                      if sum(w.weight for w in v.groups if w.group in group_ids) >= .5]
        if not candidates:
            raise ValueError("ACTUAL_FOOT_WEIGHTED_SURFACE_REQUIRED:" + side)
        low = min(rest[i][2] for i in candidates)
        sole_ids[side] = [i for i in candidates if rest[i][2] <= low + .002]
    if set(sole_ids["left"]) & set(sole_ids["right"]):
        raise ValueError("SOLE_SIDES_ALIAS")
    rest_soles = {s: [rest[i] for i in ids] for s, ids in sole_ids.items()}
    floor_z = min(v[2] for pts in rest_soles.values() for v in pts)
    rest_min = {s: min(v[2] for v in pts) for s, pts in rest_soles.items()}
    bone_map = {role: {"bone": name, "parent": rig.data.bones[name].parent.name if rig.data.bones[name].parent else None,
        "head_world_m": vec(rig.matrix_world @ rig.data.bones[name].head_local),
        "tail_world_m": vec(rig.matrix_world @ rig.data.bones[name].tail_local),
        "rest_matrix_armature": [vec(row) for row in rig.data.bones[name].matrix_local]}
        for role, name in ROLE_MAP.items()}
    g.write(out / "HUMANOID_MAP.json", {"schema": 1, "source": source_ref, "roles": bone_map,
        "source_bone_count": len(rig.data.bones), "native_to_reference_scale": scale,
        "reference_height_m": 1.70, "native_units": "GLB coordinates; 1.70m reference height is an explicit working convention",
        "bind_pose_rewritten": False, "appearance_authority": "none"})
    rig.data.pose_position = "POSE"
    scene.frame_set(1)
    bpy.context.view_layer.update()
    if max(abs(a-b) for p,q in zip(evaluated_vertices(mesh), rest) for a,b in zip(p,q)) > 1e-5:
        raise ValueError("STANDING_ACTION_MUST_REPRODUCE_NATIVE_BIND")
    # Save pack in standing pose. Switch to the preserved Run asset to animate.
    center = Vector((-.08 * scale, 0, .85))
    camera = scene.camera
    camera.data.ortho_scale = 2.38
    camera.location = center + Vector((3.5, 0, .2))
    camera.rotation_euler = (center-camera.location).to_track_quat("-Z", "Y").to_euler()
    for area in bpy.context.screen.areas if bpy.context.screen else []:
        if area.type == "VIEW_3D":
            area.spaces.active.region_3d.view_distance = 3
            area.spaces.active.region_3d.view_location = center
    scene["SABLE_REFERENCE_ONLY"] = True
    scene["visible_art_authority"] = "none"
    scene["source_sha256"] = source_ref["sha256"]
    scene["native_run_action"] = action.name
    scene["standing_action"] = standing.name
    scene["fixed_floor_z_m"] = floor_z
    scene["reference_scale_applied_once"] = scale
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "STANDING_BODY_PACK.blend"))
    pack_ref = g.ref(out / "STANDING_BODY_PACK.blend")
    # Native source motion, no inferred cycle naming or copied terminal sample.
    rig.animation_data.action = action
    rig.animation_data.action_slot = slot
    start, end = map(float, action.frame_range)
    rows = []
    for index in range(49):
        frame = start + (end-start)*index/48
        scene.frame_set(int(frame), subframe=frame-int(frame))
        bpy.context.view_layer.update()
        vertices = evaluated_vertices(mesh)
        world = {role: vec(rig.matrix_world @ rig.pose.bones[name].head) for role,name in ROLE_MAP.items()}
        soles = {s: [vertices[i] for i in ids] for s,ids in sole_ids.items()}
        centers = {s: [sum(p[i] for p in pts)/len(pts) for i in range(3)] for s,pts in soles.items()}
        from calibrate_vrm_ual_ground_contact import _angle_degrees
        rows.append({"sample": index, "frame": frame, "source_time_s": frame/24,
            "time_s": (frame-start)/24, "joints_world_m": world,
            "sole_vertices_world_m": soles, "sole_centres_world_m": centers,
            "sole_clearance_m": {s: min(p[2] for p in pts)-floor_z for s,pts in soles.items()},
            "pelvis_world_m": world["hips"],
            "left_minus_right_travel_m": -centers["left"][1]+centers["right"][1],
            "foot_yaw_from_travel_degrees": {s: _angle_degrees(
                [b-a for a,b in zip(world[s+"Foot"],world[s+"Toes"])], [0,-1,0]) for s in ("left","right")}})
    from calibrate_vrm_ual_ground_contact import _classify
    contract_path = ROOT / "tools/character_pipeline/pose_guide_contact_contract.json"
    contract = g.read(contract_path)
    phases, errors = _classify(rows, contract)
    if abs(rest_min["left"]-rest_min["right"]) > contract["neutral_sole_side_delta_max_m"]:
        errors.append("NEUTRAL_REST_SOLES_DO_NOT_DEFINE_ONE_LEVEL_FLOOR")
    if action_digest(action) != run_sha:
        raise ValueError("SOURCE_RUN_KEYS_MUTATED")
    seam = max(math.dist(a,b) for s in ("left","right")
               for a,b in zip(rows[0]["sole_vertices_world_m"][s],rows[-1]["sole_vertices_world_m"][s]))
    g.write(out / "RUN_GEOMETRY.json", {"schema": 1, "stage": "raw_tripo_run_geometry",
        "source": source_ref, "pack": pack_ref, "extractor": g.ref(__file__),
        "source_action_key_sha256": run_sha, "mesh_topology_uv_skin_sha256": topology,
        "native_time_range_s": intake["native_time_range_s"], "duration_s": (end-start)/24,
        "sample_count": 49, "actual_terminal_sample_retained": True, "samples": rows,
        "travel_axis_world": [0,-1,0], "source_rest_soles": rest_soles,
        "fixed_floor": {"method": "actual_neutral_REST_pose_sole_vertex_minimum_before_action_evaluation",
                        "world_z_m": floor_z, "neutral_side_min_z_m": rest_min},
        "sole_vertex_ids": sole_ids, "sole_mesh": mesh.name,
        "endpoint_sole_seam_m": seam, "technical_phase_candidates": phases,
        "contact_contract": g.ref(contract_path),
        "classifier": g.ref(ROOT / "tools/character_pipeline/calibrate_vrm_ual_ground_contact.py"),
        "visual_promotion_contract": g.ref(ROOT / "tools/character_pipeline/pose_guide_visual_promotion_contract.json"),
        "contact_errors": errors, "status": "HOLD_CONTACT_AND_CYCLE_REVIEW",
        "production_ready": False, "visible_art_authority": "none"})
    # Calibrator-compatible input uses a Run-active scene, not standing action.
    scene.frame_set(int(start))
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "RUN_REFERENCE.blend"))
    target_to_ual = {"Hip":"pelvis", "L_Thigh":"thigh_l", "L_Calf":"calf_l", "L_Foot":"foot_l",
        "L_ToeBase":"ball_l", "R_Thigh":"thigh_r", "R_Calf":"calf_r", "R_Foot":"foot_r", "R_ToeBase":"ball_r"}
    g.write(out / "CALIBRATOR_INPUT.json", {"schema":1,"scope":"TRIPO_NATIVE_RUN_GEOMETRY_ONLY_NOT_UAL_RETARGET",
        "output_blend":g.ref(out / "RUN_REFERENCE.blend"),"mapping":target_to_ual,
        "baked_frame_range":[start,end],"sole_mesh":mesh.name,"sole_vertex_ids":sole_ids,
        "source":source_ref,"run_geometry":g.ref(out / "RUN_GEOMETRY.json")})
    return {"standing_pack": pack_ref, "run_reference": g.ref(out / "RUN_REFERENCE.blend"),
        "humanoid_map": g.ref(out / "HUMANOID_MAP.json"), "run_geometry": g.ref(out / "RUN_GEOMETRY.json"),
        "calibrator_input": g.ref(out / "CALIBRATOR_INPUT.json"),
        "contact_errors": errors, "native_run_keys_unchanged": True}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--license", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args(sys.argv[sys.argv.index("--") + 1:])
    source, out = g.local(a.input), g.local(a.out)
    from tripo_motion_reference import inspect
    intake = inspect(source, a.license)
    if not out.is_relative_to(ROOT / "art_src/motion_reference"):
        raise ValueError("MOTION_REFERENCE_OUTPUT_ROOT_REQUIRED")
    inputs = g.read(out / "EXECUTION_INPUTS.json")
    for reference in inputs.values():
        g.resolve(reference)
    if (inputs.get("builder") != g.ref(__file__) or inputs.get("source") != g.ref(source) or
        inputs.get("license") != g.ref(a.license) or
        inputs.get("runner") != g.ref(ROOT / "tools/character_pipeline/tripo_motion_reference.py")):
        raise ValueError("EXACT_RUNNER_INPUTS_REQUIRED")
    # Exclusive write is atomic. A failed attempt stays consumed; direct child
    # execution cannot overwrite an earlier partial scene or render.
    g.write(out / "CHILD_CLAIM.json", {"schema":1,"inputs":g.ref(out / "EXECUTION_INPUTS.json"),
        "builder":g.ref(__file__),"source":g.ref(source),"max_samples":49})
    source_ref = g.ref(source)
    if (out / "INSPECTION.json").exists():
        raise ValueError("FRESH_OUTPUT_REQUIRED")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = 24
    scene.render.fps_base = 1.0
    bpy.ops.import_scene.gltf(filepath=str(source), import_pack_images=True, disable_bone_shape=True)
    # glTF may activate a newly imported scene; never retain the factory scene.
    scene = bpy.context.scene
    scene.render.fps = 24
    scene.render.fps_base = 1.0
    rigs = [o for o in scene.objects if o.type == "ARMATURE"]
    if len(rigs) != 1:
        raise ValueError("ONE_BOUND_RIG_AND_MESH_REQUIRED")
    rig = rigs[0]
    shapes = {b.custom_shape for b in rig.pose.bones if b.custom_shape is not None}
    meshes = [o for o in scene.objects if o.type == "MESH" and o not in shapes]
    if len(meshes) != 1 or not any(m.type == "ARMATURE" and m.object == rig for m in meshes[0].modifiers):
        raise ValueError("ONE_ACTUAL_SKIN_MODIFIER_BOUND_MESH_REQUIRED")
    for shape in shapes:
        shape.hide_render = True
    mesh = meshes[0]
    action = rig.animation_data.action
    if action is None:
        raise ValueError("ACTUAL_RUN_ACTION_REQUIRED")
    action.use_fake_user = True
    start, end = map(float, action.frame_range)
    scene.frame_start, scene.frame_end = int(start), int(end)
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y = 1920, 1920
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.threads_mode, scene.render.threads = "FIXED", 2
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_cavity = True
    scene.display.shading.background_type = "WORLD"
    scene.world = bpy.data.worlds.new("MotionReferenceWorld")
    scene.world.color = (.045, .055, .07)
    rig.show_in_front = True
    rig.data.pose_position = "REST"
    scene.frame_set(int(start))
    bpy.context.view_layer.update()
    dep = bpy.context.evaluated_depsgraph_get()
    evaluated = mesh.evaluated_get(dep)
    actual = evaluated.to_mesh()
    coords = [evaluated.matrix_world @ v.co for v in actual.vertices]
    evaluated.to_mesh_clear()
    lo = Vector(tuple(min(v[i] for v in coords) for i in range(3)))
    hi = Vector(tuple(max(v[i] for v in coords) for i in range(3)))
    center = (lo + hi) * .5
    cam_data = bpy.data.cameras.new("MotionReferenceCamera")
    cam = bpy.data.objects.new("MotionReferenceCamera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = max(hi - lo) * 1.4
    def camera_at(offset):
        cam.location = center + Vector(offset) * max(hi - lo) * 3
        cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
    images = []
    for name, offset in [("REST_FRONT", (0, -1, .1)), ("REST_SIDE", (1, 0, .1))]:
        camera_at(offset)
        scene.render.filepath = str(out / (name + ".png"))
        bpy.ops.render.render(write_still=True)
        images.append(g.ref(scene.render.filepath))
    bones = {b.name: {"parent": b.parent.name if b.parent else None,
        "head_world": vec(rig.matrix_world @ b.head_local),
        "tail_world": vec(rig.matrix_world @ b.tail_local)} for b in rig.data.bones}
    rig.data.pose_position = "POSE"
    scene.frame_set(int(start))
    camera_at((1, 0, .1))
    scene.render.filepath = str(out / "RUN_START.png")
    bpy.ops.render.render(write_still=True)
    images.append(g.ref(scene.render.filepath))
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "SOURCE_RUN.blend"))
    pack = make_pack(rig, mesh, action, scene, out, source_ref, intake)
    if source_ref != g.ref(source):
        raise ValueError("SOURCE_MUTATED")
    g.write(out / "INSPECTION.json", {"schema": 1, "production_ready": False,
        "stage": "tripo_motion_geometry_inspection", "source": source_ref,
        "builder": g.ref(__file__), "blend": g.ref(out / "SOURCE_RUN.blend"),
        "rig": rig.name, "mesh": mesh.name, "vertices": len(mesh.data.vertices),
        "polygons": len(mesh.data.polygons), "bones": bones,
        "rest_bounds": [vec(lo), vec(hi)], "action": action.name,
        "frame_range": [start, end], "fps": scene.render.fps,
        "duration_s": (end-start)/24, "images": images,
        "native_resolution": [1920, 1920], "visible_art_authority": "none", "pack": pack})


if __name__ == "__main__":
    main()
