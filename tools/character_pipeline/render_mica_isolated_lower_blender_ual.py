#!/usr/bin/env python3
"""Render a fixed-upper MICA E gait with isolated, volume-stable leg meshes.

Run through Blender.  The approved ImageGen pixels are sampled unchanged.
Blender supplies only rigid two-bone motion, alternating UAL cadence, layer
ordering, and the fixed upper/lower composite.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]


def args_after_dash() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--cell-size", type=int, default=384)
    parser.add_argument(
        "--frame-indices",
        default="",
        help="Optional comma-separated diagnostic subset. Empty renders the full cycle.",
    )
    return parser.parse_args(args_after_dash())


def project_path(value: str, label: str) -> Path:
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain below the project root: {path}") from exc
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def configure_scene(cell_size: int) -> tuple[bpy.types.Scene, bpy.types.Object]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    engine_ids = {
        item.identifier
        for item in scene.bl_rna.properties["render"].fixed_type.properties["engine"].enum_items
    }
    scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engine_ids else "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = cell_size
    scene.render.resolution_y = cell_size
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    # Unlit source-art plates must retain their authored RGB values.  AgX
    # darkens the costume and invalidates the source-pixel continuity claim.
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    camera_data = bpy.data.cameras.new("MICA_ISOLATED_LOWER_CAMERA")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 3.92
    camera = bpy.data.objects.new("MICA_ISOLATED_LOWER_CAMERA", camera_data)
    camera.location = (0.0, 0.0, 8.0)
    scene.collection.objects.link(camera)
    scene.camera = camera
    return scene, camera


def build_material(rgb_path: Path, mask_path: Path, name: str) -> bpy.types.Material:
    color_image = bpy.data.images.load(str(rgb_path), check_existing=False)
    color_image.colorspace_settings.name = "sRGB"
    mask_image = bpy.data.images.load(str(mask_path), check_existing=False)
    mask_image.colorspace_settings.name = "Non-Color"
    if color_image.size[:] != mask_image.size[:]:
        raise SystemExit(f"source/mask size mismatch: {rgb_path} / {mask_path}")

    material = bpy.data.materials.new(name + "_MAT")
    material.use_nodes = True
    # Transparent BSDFs still behave as depth-writing opaque surfaces in
    # Eevee unless the material render method is explicitly enabled.  With
    # three stacked source plates that caused the front plate's transparent
    # limb mask to turn the rear leg into a solid black silhouette.
    try:
        material.surface_render_method = "DITHERED"
    except (AttributeError, TypeError):
        pass
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    mix = nodes.new("ShaderNodeMixShader")
    tex_coord = nodes.new("ShaderNodeTexCoord")
    color_tex = nodes.new("ShaderNodeTexImage")
    mask_tex = nodes.new("ShaderNodeTexImage")
    color_tex.image = color_image
    mask_tex.image = mask_image
    color_tex.interpolation = "Closest"
    mask_tex.interpolation = "Closest"
    links.new(tex_coord.outputs["UV"], color_tex.inputs["Vector"])
    links.new(tex_coord.outputs["UV"], mask_tex.inputs["Vector"])
    links.new(color_tex.outputs["Color"], emission.inputs["Color"])
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(emission.outputs[0], mix.inputs[2])

    separate = nodes.new("ShaderNodeSeparateColor")
    separate.mode = "RGB"
    red_low = nodes.new("ShaderNodeMath")
    red_low.operation = "LESS_THAN"
    red_low.inputs[1].default_value = 0.25
    green_high = nodes.new("ShaderNodeMath")
    green_high.operation = "GREATER_THAN"
    green_high.inputs[1].default_value = 0.50
    blue_low = nodes.new("ShaderNodeMath")
    blue_low.operation = "LESS_THAN"
    blue_low.inputs[1].default_value = 0.25
    green_rg = nodes.new("ShaderNodeMath")
    green_rg.operation = "MULTIPLY"
    green_exact = nodes.new("ShaderNodeMath")
    green_exact.operation = "MULTIPLY"
    non_green = nodes.new("ShaderNodeMath")
    non_green.operation = "SUBTRACT"
    non_green.inputs[0].default_value = 1.0
    combined = nodes.new("ShaderNodeMath")
    combined.operation = "MULTIPLY"
    links.new(color_tex.outputs["Color"], separate.inputs[0])
    links.new(separate.outputs[0], red_low.inputs[0])
    links.new(separate.outputs[1], green_high.inputs[0])
    links.new(separate.outputs[2], blue_low.inputs[0])
    links.new(red_low.outputs[0], green_rg.inputs[0])
    links.new(green_high.outputs[0], green_rg.inputs[1])
    links.new(green_rg.outputs[0], green_exact.inputs[0])
    links.new(blue_low.outputs[0], green_exact.inputs[1])
    links.new(green_exact.outputs[0], non_green.inputs[1])
    links.new(mask_tex.outputs["Color"], combined.inputs[0])
    links.new(non_green.outputs[0], combined.inputs[1])
    links.new(combined.outputs[0], mix.inputs[0])
    links.new(mix.outputs[0], output.inputs["Surface"])
    return material


def build_grid_plane(
    rgb_path: Path,
    mask_path: Path,
    name: str,
    *,
    uv_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
    subdivisions: tuple[int, int] = (1, 1),
) -> bpy.types.Object:
    image = bpy.data.images.load(str(rgb_path), check_existing=True)
    aspect = float(image.size[0]) / float(image.size[1])
    half_height = 1.5
    half_width = half_height * aspect
    u0, v0, u1, v1 = uv_rect
    columns, rows = subdivisions
    uv_points = [
        (u0 + (u1 - u0) * column / columns, v0 + (v1 - v0) * row / rows)
        for row in range(rows + 1)
        for column in range(columns + 1)
    ]
    vertices = [
        (-half_width + 2.0 * half_width * u, -half_height + 2.0 * half_height * v, 0.0)
        for u, v in uv_points
    ]
    faces: list[tuple[int, int, int, int]] = []
    stride = columns + 1
    for row in range(rows):
        for column in range(columns):
            lower_left = row * stride + column
            faces.append((lower_left, lower_left + 1, lower_left + stride + 1, lower_left + stride))
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.uv_layers.new(name="UVMap")
    uv_data = mesh.uv_layers.active.data
    for loop in mesh.loops:
        uv_data[loop.index].uv = uv_points[loop.vertex_index]
    plane = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(plane)
    plane.data.materials.append(build_material(rgb_path, mask_path, name))
    return plane


def px_to_uv(point: list[float], width: int, height: int) -> tuple[float, float]:
    return (float(point[0]) / width, 1.0 - float(point[1]) / height)


def uv_to_plane(point: tuple[float, float], aspect: float) -> tuple[float, float]:
    return (-1.5 * aspect + 3.0 * aspect * point[0], -1.5 + 3.0 * point[1])


def rigid_map(
    point: tuple[float, float],
    source_start: tuple[float, float],
    source_end: tuple[float, float],
    target_start: tuple[float, float],
    target_end: tuple[float, float],
) -> tuple[float, float]:
    source_angle = math.atan2(source_end[1] - source_start[1], source_end[0] - source_start[0])
    target_angle = math.atan2(target_end[1] - target_start[1], target_end[0] - target_start[0])
    angle = target_angle - source_angle
    sine, cosine = math.sin(angle), math.cos(angle)
    local_x = point[0] - source_start[0]
    local_y = point[1] - source_start[1]
    return (
        target_start[0] + cosine * local_x - sine * local_y,
        target_start[1] + sine * local_x + cosine * local_y,
    )


def solve_knee(
    hip: tuple[float, float],
    foot: tuple[float, float],
    thigh: float,
    calf: float,
    bend_sign: float,
) -> tuple[float, float]:
    dx, dy = foot[0] - hip[0], foot[1] - hip[1]
    raw_distance = max(0.001, math.hypot(dx, dy))
    minimum = abs(thigh - calf) + 0.002
    maximum = thigh + calf - 0.002
    distance = max(minimum, min(maximum, raw_distance))
    ux, uy = dx / raw_distance, dy / raw_distance
    along = (thigh * thigh - calf * calf + distance * distance) / (2.0 * distance)
    height = math.sqrt(max(0.0, thigh * thigh - along * along))
    return (
        hip[0] + ux * along - uy * height * bend_sign,
        hip[1] + uy * along + ux * height * bend_sign,
    )


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def foot_cycle(phase: float, stride: float, lift: float, stance_fraction: float) -> tuple[float, float, bool]:
    phase %= 1.0
    if phase < stance_fraction:
        progress = phase / stance_fraction
        return stride - 2.0 * stride * progress, 0.0, True
    progress = (phase - stance_fraction) / (1.0 - stance_fraction)
    return -stride + 2.0 * stride * smoothstep(progress), math.sin(math.pi * progress) * lift, False


def build_leg(
    name: str,
    entry: dict,
    rgb_path: Path,
    mask_path: Path,
    width: int,
    height: int,
) -> dict[str, object]:
    aspect = width / height
    plane = build_grid_plane(rgb_path, mask_path, f"MICA_E_{name}", subdivisions=(48, 72))
    uv_data = plane.data.uv_layers.active.data
    vertex_uvs: list[tuple[float, float]] = [(0.0, 0.0)] * len(plane.data.vertices)
    for loop in plane.data.loops:
        uv = uv_data[loop.index].uv
        vertex_uvs[loop.vertex_index] = (float(uv.x), float(uv.y))
    points_uv = {key: px_to_uv(entry[f"{key}_px"], width, height) for key in ("hip", "knee", "ankle", "toe")}
    points = {key: uv_to_plane(value, aspect) for key, value in points_uv.items()}
    return {
        "name": name,
        "plane": plane,
        "base_vertices": [vertex.co.copy() for vertex in plane.data.vertices],
        "vertex_uvs": vertex_uvs,
        "uv": points_uv,
        **points,
        "thigh_length": math.dist(points["hip"], points["knee"]),
        "calf_length": math.dist(points["knee"], points["ankle"]),
        "bend_sign": float(entry.get("knee_bend_sign", 1.0)),
    }


def deform_leg(
    leg: dict[str, object],
    target_ankle: tuple[float, float],
    motion_mode: str,
    target_knee_override: tuple[float, float] | None = None,
    sole_lock_shift: tuple[float, float] = (0.0, 0.0),
) -> tuple[float, float]:
    source_hip = leg["hip"]
    source_knee = leg["knee"]
    source_ankle = leg["ankle"]
    plane = leg["plane"]
    if motion_mode == "rigid_plate":
        for vertex, base in zip(plane.data.vertices, leg["base_vertices"]):
            vertex.co = base
        plane.data.update()
        delta = (target_ankle[0] - source_ankle[0], target_ankle[1] - source_ankle[1])
        plane.location.x = delta[0]
        plane.location.y = delta[1]
        return (source_knee[0] + delta[0], source_knee[1] + delta[1])
    if motion_mode not in {"two_bone", "front_back_limited"}:
        raise SystemExit(
            "deformation_mode must be two_bone, front_back_limited, or rigid_plate"
        )
    plane.location.x = 0.0
    plane.location.y = 0.0
    if motion_mode == "front_back_limited":
        if target_knee_override is None:
            raise SystemExit("front_back_limited requires an explicit knee target")
        target_knee = target_knee_override
    else:
        target_knee = solve_knee(
            source_hip,
            target_ankle,
            leg["thigh_length"],
            leg["calf_length"],
            leg["bend_sign"],
        )
    knee_v = leg["uv"]["knee"][1]
    ankle_v = leg["uv"]["ankle"][1]
    mesh = plane.data
    for vertex, base, uv in zip(mesh.vertices, leg["base_vertices"], leg["vertex_uvs"]):
        point = (float(base.x), float(base.y))
        thigh_point = rigid_map(point, source_hip, source_knee, source_hip, target_knee)
        calf_point = rigid_map(point, source_knee, source_ankle, target_knee, target_ankle)
        foot_point = (
            point[0] + target_ankle[0] - source_ankle[0],
            point[1] + target_ankle[1] - source_ankle[1],
        )
        if uv[1] >= knee_v + 0.025:
            result = thigh_point
        elif uv[1] >= knee_v - 0.025:
            blend = smoothstep((uv[1] - (knee_v - 0.025)) / 0.05)
            result = (
                calf_point[0] * (1.0 - blend) + thigh_point[0] * blend,
                calf_point[1] * (1.0 - blend) + thigh_point[1] * blend,
            )
        elif uv[1] >= ankle_v + 0.055:
            result = calf_point
        elif uv[1] >= ankle_v + 0.015:
            blend = smoothstep((uv[1] - (ankle_v + 0.015)) / 0.04)
            result = (
                foot_point[0] * (1.0 - blend) + calf_point[0] * blend,
                foot_point[1] * (1.0 - blend) + calf_point[1] * blend,
            )
        else:
            result = foot_point
        # Keep the hip and seam fixed while allowing a tiny, authored lower
        # limb translation to land the rasterized outsole on the continuous
        # root cadence.  The weight ramps from zero at the knee to one at the
        # ankle/foot, so this is a joint/stance correction rather than a leg
        # scale or whole-body translation.
        if sole_lock_shift != (0.0, 0.0):
            knee_v = float(leg["uv"]["knee"][1])
            ankle_v = float(leg["uv"]["ankle"][1])
            span = max(0.001, knee_v - ankle_v)
            if uv[1] >= knee_v:
                shift_weight = 0.0
            elif uv[1] <= ankle_v:
                shift_weight = 1.0
            else:
                shift_weight = smoothstep((knee_v - uv[1]) / span)
            result = (
                result[0] + sole_lock_shift[0] * shift_weight,
                result[1] + sole_lock_shift[1] * shift_weight,
            )
        vertex.co = (result[0], result[1], float(base.z))
    mesh.update()
    return target_knee


def main() -> None:
    args = parse_args()
    spec_path = project_path(args.spec, "spec")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    direction = str(spec.get("direction", "E")).upper()
    if direction not in {"E", "SE", "S", "SW", "W", "NW", "N", "NE"}:
        raise SystemExit(f"unsupported direction: {direction}")
    source_rgb = project_path(spec["source_rgb"], "source rgb")
    upper_rgb = project_path(spec["upper_rgb"], "upper rgb")
    ual_path = project_path(spec["ual_curve"], "UAL curve")
    technical_root = project_path(spec["output_dir"], "technical output")
    upper_mask = technical_root / "UPPER_FIXED_MASK.png"
    if not upper_mask.is_file():
        raise SystemExit(f"missing fixed upper mask: {upper_mask}")
    candidate_root = (
        project_path(spec["candidate_root"], "candidate root")
        if "candidate_root" in spec
        else technical_root.parent
    )
    frame_root = candidate_root / "blender_frames" / direction / "move"
    frame_root.mkdir(parents=True, exist_ok=True)
    component_root = candidate_root / "blender_components" / direction / "move"
    component_root.mkdir(parents=True, exist_ok=True)
    scene, _camera = configure_scene(args.cell_size)

    color_image = bpy.data.images.load(str(source_rgb), check_existing=True)
    width, height = int(color_image.size[0]), int(color_image.size[1])
    lower_root = bpy.data.objects.new("MICA_E_LOWER_ROOT", None)
    scene.collection.objects.link(lower_root)
    composite = spec["composite"]
    scale = float(composite["lower_uniform_scale"])
    tx, ty = (float(v) for v in composite["lower_translation_xy"])
    lower_root.scale = (scale, scale, 1.0)
    lower_root.location = (tx, ty, 0.0)

    upper_plane = build_grid_plane(
        upper_rgb,
        upper_mask,
        "MICA_E_FIXED_UPPER",
        uv_rect=tuple(float(v) for v in composite["upper_crop_uv"]),
    )
    upper_plane.location.z = 0.60

    limbs: dict[str, dict[str, object]] = {}
    for name, entry in spec["limbs"].items():
        mask_path = technical_root / f"{name.upper()}_ISOLATED_MASK.png"
        if not mask_path.is_file():
            raise SystemExit(f"missing isolated mask: {mask_path}")
        leg = build_leg(name, entry, source_rgb, mask_path, width, height)
        leg["plane"].parent = lower_root
        limbs[name] = leg

    gait = spec["gait"]
    frame_count = int(gait["frame_count"])
    stride = float(gait["stride_units"])
    lift = float(gait["swing_lift_units"])
    stance_fraction = float(gait["stance_fraction"])
    center_x = float(gait["foot_center_x"])
    center_mode = str(gait.get("foot_center_mode", "shared"))
    if center_mode not in {"shared", "source_relative"}:
        raise SystemExit("foot_center_mode must be shared or source_relative")
    foot_center_offsets = gait.get("foot_center_offsets_units", {})
    if not isinstance(foot_center_offsets, dict):
        raise SystemExit("foot_center_offsets_units must be an object keyed by leg name")
    sole_lock_corrections = gait.get("sole_lock_correction_units", {})
    if not isinstance(sole_lock_corrections, dict):
        raise SystemExit("sole_lock_correction_units must be an object keyed by leg name")
    checked_sole_lock_corrections: dict[str, list[float]] = {}
    for name in limbs:
        values = sole_lock_corrections.get(name, [0.0] * frame_count)
        if not isinstance(values, list) or len(values) != frame_count:
            raise SystemExit(
                f"sole_lock_correction_units[{name}] must contain exactly {frame_count} values"
            )
        checked_values = [float(value) for value in values]
        if any(not math.isfinite(value) or abs(value) > 0.05 for value in checked_values):
            raise SystemExit(
                f"sole_lock_correction_units[{name}] contains a non-finite or unsafe correction"
            )
        checked_sole_lock_corrections[name] = checked_values
    depth = float(gait["depth_offset_units"])
    # For diagonal walks the two feet must be separated across the travel
    # axis, not by reusing their screen-space source X coordinates.  The
    # latter makes the support handoff look like a root teleport because one
    # source foot is already many pixels ahead along the diagonal.  A lateral
    # offset is optional and defaults to zero for the established cardinal
    # candidates, preserving their authored placement.
    lateral_offset = float(gait.get("lateral_offset_units", 0.0))
    motion_mode = str(gait.get("deformation_mode", "two_bone"))
    knee_inward = float(gait.get("knee_inward_units", 0.0))
    ankle_inward = float(gait.get("ankle_inward_units", 0.0))
    knee_raise = float(gait.get("knee_raise_units", 0.0))
    knee_ankle_follow = float(gait.get("knee_ankle_follow", 0.45))
    forward_axis = tuple(float(value) for value in gait.get("forward_axis_xy", [1.0, 0.0]))
    if len(forward_axis) != 2 or not 0.95 <= math.hypot(*forward_axis) <= 1.05:
        raise SystemExit("forward_axis_xy must be a normalized two-value direction")
    ual = json.loads(ual_path.read_text(encoding="utf-8"))
    if int(ual["locomotion"]["sample_count"]) != frame_count:
        raise SystemExit("UAL sample count does not match gait frame count")

    mesh_objects = [upper_plane, *(leg["plane"] for leg in limbs.values())]

    def render_component(visible: bpy.types.Object, output_path: Path) -> None:
        for mesh_object in mesh_objects:
            mesh_object.hide_render = mesh_object is not visible
        scene.render.filepath = str(output_path)
        bpy.ops.render.render(write_still=True)

    upper_component_path = component_root.parent / "upper_fixed.png"
    render_component(upper_plane, upper_component_path)

    frames: list[dict[str, object]] = []
    requested_indices = (
        sorted({int(value.strip()) for value in args.frame_indices.split(",") if value.strip()})
        if args.frame_indices
        else list(range(frame_count))
    )
    if not requested_indices or any(index < 0 or index >= frame_count for index in requested_indices):
        raise SystemExit(f"frame indices must be within 0..{frame_count - 1}")
    for index in requested_indices:
        phase = index / frame_count
        frame_entry: dict[str, object] = {"index": index, "phase": round(phase, 6), "legs": {}}
        for name, leg in limbs.items():
            offset = 0.0 if name == "screen_left" else 0.5
            leg_phase = (phase + offset) % 1.0
            forward, vertical, planted = foot_cycle(leg_phase, stride, lift, stance_fraction)
            swing_progress = (
                0.0
                if planted
                else (leg_phase - stance_fraction) / (1.0 - stance_fraction)
            )
            source_ankle = leg["ankle"]
            foot_center = (
                source_ankle[0] if center_mode == "source_relative" else center_x
            ) + float(foot_center_offsets.get(name, 0.0))
            lateral_axis = (-forward_axis[1], forward_axis[0])
            # Keep the two boots separated in screen space for every travel
            # direction.  A fixed +/- sign is wrong on NE/NW because the
            # perpendicular travel axis points toward the opposite side of
            # the raster.  Derive the sign from the horizontal component so
            # screen_left always receives the negative-x offset (and
            # screen_right the positive-x offset) whenever the lateral axis
            # has a horizontal projection.  Cardinal E/W remains unchanged
            # because its lateral x component is zero.
            lateral_x_sign = 1.0 if lateral_axis[0] >= 0.0 else -1.0
            lateral_sign = -lateral_x_sign if name == "screen_left" else lateral_x_sign
            target_ankle = (
                foot_center
                + forward * forward_axis[0]
                + lateral_sign * lateral_offset * lateral_axis[0]
                + (-depth if name == "screen_left" else depth),
                source_ankle[1]
                + forward * forward_axis[1]
                + lateral_sign * lateral_offset * lateral_axis[1]
                + vertical,
            )
            # The source plates are rasterized at 384px, so a mathematically
            # linear stance can quantize into a 1–2px sole wobble.  These tiny
            # per-frame corrections are authored in the Blender/UAL candidate
            # (not applied by the review capture) and keep the support outsole
            # on the continuous runtime root trajectory without changing scale,
            # boot rotation, or the upper body.  Apply them after the two-bone
            # solve as a lower-limb joint shift so the hip/seam remains fixed.
            sole_correction = checked_sole_lock_corrections[name][index]
            target_knee_override = None
            if motion_mode == "front_back_limited":
                inward_sign = 1.0 if source_ankle[0] < 0.0 else -1.0
                # The knee enters the passing lane before the boot.  Keeping
                # the two bell curves out of phase makes a frontal walk read
                # as a real step instead of a symmetric vertical tap.
                knee_phase = max(0.0, min(1.0, swing_progress + 0.08))
                ankle_phase = max(0.0, min(1.0, (swing_progress - 0.08) / 0.92))
                knee_ratio = 0.0 if planted else math.sin(math.pi * knee_phase)
                ankle_ratio = 0.0 if planted else math.sin(math.pi * ankle_phase)
                target_ankle = (
                    target_ankle[0] + inward_sign * ankle_inward * ankle_ratio,
                    target_ankle[1],
                )
                ankle_delta_y = target_ankle[1] - source_ankle[1]
                target_knee_override = (
                    leg["knee"][0] + inward_sign * knee_inward * knee_ratio,
                    leg["knee"][1] + ankle_delta_y * knee_ankle_follow + knee_raise * knee_ratio,
                )
            target_knee = deform_leg(
                leg,
                target_ankle,
                motion_mode,
                target_knee_override=target_knee_override,
                sole_lock_shift=(
                    sole_correction * forward_axis[0],
                    sole_correction * forward_axis[1],
                ),
            )
            # The active swing leg comes forward in depth, making near/far leg
            # identity alternate without rotating either boot texture.
            leg["plane"].location.z = 0.34 if not planted else 0.24
            frame_entry["legs"][name] = {
                "planted": planted,
                "target_ankle": [round(v, 7) for v in target_ankle],
                "target_knee": [round(v, 7) for v in target_knee],
                "foot_center_offset_units": round(float(foot_center_offsets.get(name, 0.0)), 7),
                "sole_lock_correction_units": round(sole_correction, 7),
                "boot_rotation_degrees": 0.0,
                "mesh_scale": 1.0,
                "deformation_mode": motion_mode,
                "render_depth": float(leg["plane"].location.z),
            }
        frame_components: dict[str, object] = {}
        for name, leg in limbs.items():
            output_path = component_root / f"{index:02d}_{name}.png"
            render_component(leg["plane"], output_path)
            frame_components[name] = {
                "path": output_path.relative_to(ROOT).as_posix(),
                "sha256": sha256(output_path),
            }
        frame_entry["components"] = frame_components
        frames.append(frame_entry)

    for mesh_object in mesh_objects:
        mesh_object.hide_render = False

    scene_root = candidate_root / "blender_scene"
    scene_root.mkdir(parents=True, exist_ok=True)
    blend_path = scene_root / f"MICA_C03_{direction}_ISOLATED_LOWER_UAL.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    manifest = {
        "schema": 1,
        "role": f"MICA C03 {direction} fixed-upper isolated-leg Blender+UAL candidate",
        "direction": direction,
        "candidate_status": "UNREVIEWED_DO_NOT_PROMOTE",
        "source_art_modified": False,
        "boot_rotation_degrees": 0.0,
        "limb_scale_policy": "rigid 1.0; no non-uniform scale and no cross-leg weights",
        "spec": spec_path.relative_to(ROOT).as_posix(),
        "spec_sha256": sha256(spec_path),
        "source_rgb": source_rgb.relative_to(ROOT).as_posix(),
        "source_rgb_sha256": sha256(source_rgb),
        "upper_rgb": upper_rgb.relative_to(ROOT).as_posix(),
        "upper_rgb_sha256": sha256(upper_rgb),
        "ual_curve": ual_path.relative_to(ROOT).as_posix(),
        "ual_curve_sha256": sha256(ual_path),
        "blend": blend_path.relative_to(ROOT).as_posix(),
        "blend_sha256": sha256(blend_path),
        "cell_size": args.cell_size,
        "runtime_integration": spec.get("runtime_integration", {}),
        "sole_lock_correction_units": checked_sole_lock_corrections,
        "upper_component": {
            "path": upper_component_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(upper_component_path),
        },
        "frames": frames,
    }
    manifest_path = candidate_root / f"MICA_C03_{direction}_ISOLATED_LOWER_UAL_RENDER_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
