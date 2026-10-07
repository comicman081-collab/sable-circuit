#!/usr/bin/env python3
"""Render minimal full-body motion frames in Blender from ImageGen direction masters.

This is deliberately a motion-only step: it reads the approved ImageGen
masters plus their binary mattes, uses the licensed UAL1 curve contracts for
timing/pose offsets, and renders plane motion in Blender.  It never calls an
image model, paints pixels, or alters an authority master.

Run through Blender, for example::

  blender.exe --background --python tools/character_pipeline/render_fast_motion_blender_ual.py -- \
    --spec tools/character_pipeline/specs/rook_c02_fast_v1.json \
    --candidate art_src/characters/rook/fast_pipeline/motion/candidate_rook_c02_v1 \
    --ual-locomotion art_src/pilot_v2/aster_v2/animation_360/ual_locomotion_v5/ASTER_UAL1_LOCOMOTION_CURVES_V5.json \
    --ual-fire art_src/pilot_v2/aster_v2/animation_360/ual_fire_upper_v1/ASTER_UAL1_PISTOL_SHOOT_UPPER_CURVES_V1.json
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
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
FACING = {
    "E": (1.0, 0.0),
    "SE": (math.sqrt(0.5), -math.sqrt(0.5)),
    "S": (0.0, -1.0),
    "SW": (-math.sqrt(0.5), -math.sqrt(0.5)),
    "W": (-1.0, 0.0),
    "NW": (-math.sqrt(0.5), math.sqrt(0.5)),
    "N": (0.0, 1.0),
    "NE": (math.sqrt(0.5), math.sqrt(0.5)),
}


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--diagnostic-only", action="store_true", help="MICA legacy cutout rigs are retired; explicitly permit a quarantined diagnostic only")
    parser.add_argument(
        "--source-root",
        type=Path,
        help=(
            "project-local directory containing one immutable ImageGen direction master and "
            "matte per facing.  When omitted, the spec's current authority directory is used."
        ),
    )
    parser.add_argument(
        "--leg-landmarks",
        type=Path,
        help=(
            "per-direction ImageGen-master hip/knee/ankle/toe and low-lift gait contract. "
            "A promotable direction-master motion export must provide this file."
        ),
    )
    parser.add_argument(
        "--move-rig-mode",
        choices=("continuous", "segmented"),
        default="continuous",
        help=(
            "move-only Blender rig topology. segmented keeps torso/coat static and "
            "animates independent rigid source-pixel thigh/calf/boot pieces; it is "
            "not a repair for coat/occlusion/anatomy defects; both modes require independent visual review."
        ),
    )
    parser.add_argument("--ual-locomotion", type=Path, required=True)
    parser.add_argument("--ual-fire", type=Path, required=True)
    return parser.parse_args(argv)


def project_path(path: Path, label: str) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside the project: {resolved}") from exc
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing {label}: {path}")
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise SystemExit(f"{label} must be a JSON object: {path}")
    return parsed


def unit_point(value: object, label: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise SystemExit(f"{label} must be a two-value UV point")
    point = (float(value[0]), float(value[1]))
    if not all(0.0 < component < 1.0 for component in point):
        raise SystemExit(f"{label} must remain inside the source image")
    return point


def load_direction_landmarks(path: Path) -> dict[str, dict[str, object]]:
    """Load explicit MICA-specific lower-body anchors for every facing.

    The retired common-profile renderer accepted a direction value but ignored
    the source image's actual anatomy.  This contract makes the authority
    explicit and fails before Blender starts if even one direction is missing.
    """
    value = load_json(path, "leg landmarks")
    directions = value.get("directions")
    if not isinstance(directions, dict) or set(directions) != set(DIRECTIONS):
        raise SystemExit("leg landmarks must provide exactly E, SE, S, SW, W, NW, N, NE")
    result: dict[str, dict[str, object]] = {}
    for direction in DIRECTIONS:
        entry = directions[direction]
        if not isinstance(entry, dict):
            raise SystemExit(f"{direction} leg landmark entry must be an object")
        legs = entry.get("legs")
        if not isinstance(legs, dict) or set(legs) != {"screen_left", "screen_right"}:
            raise SystemExit(f"{direction} must define screen_left and screen_right landmarks")
        checked: dict[str, object] = {"gait": entry.get("gait"), "front_leg": entry.get("front_leg")}
        if checked["front_leg"] not in {"screen_left", "screen_right"}:
            raise SystemExit(f"{direction}.front_leg must name a screen leg")
        if not isinstance(checked["gait"], dict):
            raise SystemExit(f"{direction}.gait must be an object")
        stride = float(checked["gait"].get("stride_units", -1.0))
        lift = float(checked["gait"].get("swing_lift_units", -1.0))
        # A step needs a visible fore/aft footprint at the 384px runtime
        # scale.  The former 0.110 ceiling limited MICA to roughly ten pixels
        # of boot travel, which reads as a toe tap rather than locomotion.
        # Wider values remain bounded below the articulated leg reach; a
        # separate low lift ceiling protects the grounded-walk contract.
        if not 0.045 <= stride <= 0.360:
            raise SystemExit(f"{direction} stride must be 0.045..0.360 units")
        if not 0.012 <= lift <= 0.055:
            raise SystemExit(f"{direction} swing lift must be 0.012..0.055 units")
        checked["gait"] = {"stride_units": stride, "swing_lift_units": lift}
        checked_legs: dict[str, dict[str, tuple[float, float]]] = {}
        for name in ("screen_left", "screen_right"):
            leg = legs[name]
            if not isinstance(leg, dict):
                raise SystemExit(f"{direction}.{name} must be an object")
            points = {joint: unit_point(leg.get(joint), f"{direction}.{name}.{joint}") for joint in ("hip", "knee", "ankle", "toe")}
            # Source landmark order must run down the body.  This catches a
            # common 90-degree/sideways coordinate transcription immediately.
            if not (points["hip"][1] > points["knee"][1] > points["ankle"][1] > points["toe"][1] - 0.035):
                raise SystemExit(f"{direction}.{name} landmarks are not ordered hip-to-toe")
            checked_legs[name] = points
        checked["legs"] = checked_legs
        result[direction] = checked
    return result


def pair(value: object, label: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise SystemExit(f"{label} must be a pair")
    return float(value[0]), float(value[1])


def triplet(value: object, label: str) -> tuple[float, float, float]:
    if not isinstance(value, list) or len(value) != 3:
        raise SystemExit(f"{label} must be a triplet")
    return float(value[0]), float(value[1]), float(value[2])


def configure_scene(cell_size: int) -> tuple[bpy.types.Scene, bpy.types.Object]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    # Blender 4.5 uses the ``BLENDER_EEVEE_NEXT`` identifier while later
    # bundled builds expose ``BLENDER_EEVEE``.  Select only an engine this
    # installed headless build actually advertises; output remains the same
    # deterministic unlit RGBA cutout pass.
    engine_ids = {item.identifier for item in scene.bl_rna.properties["render"].fixed_type.properties["engine"].enum_items}
    scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engine_ids else "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = cell_size
    scene.render.resolution_y = cell_size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = True
    scene.view_settings.look = "None"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    camera_data = bpy.data.cameras.new("ROOK_FAST_UAL_CAMERA")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 3.92
    camera = bpy.data.objects.new("ROOK_FAST_UAL_CAMERA", camera_data)
    camera.location = (0.0, 0.0, 8.0)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.resolution_percentage = 100
    return scene, camera


def build_subject_plane(
    rgb_path: Path,
    mask_path: Path,
    name: str,
    uv_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
    uv_polygon: tuple[tuple[float, float], ...] | None = None,
    grid_subdivisions: tuple[int, int] | None = None,
) -> bpy.types.Object:
    """Create one source-image cutout layer without altering source pixels.

    ``uv_rect`` is an image-space crop.  ``uv_polygon`` is a project-local
    technical motion matte used for a limb silhouette.  In both cases green
    transparency still comes exclusively from the immutable ImageGen-derived
    mask; this never invents, repaints, or alters source-art pixels.
    """
    color_image = bpy.data.images.load(str(rgb_path), check_existing=False)
    color_image.colorspace_settings.name = "sRGB"
    mask_image = bpy.data.images.load(str(mask_path), check_existing=False)
    mask_image.colorspace_settings.name = "Non-Color"
    if color_image.size[:] != mask_image.size[:]:
        raise SystemExit(f"source/mask size mismatch: {rgb_path} / {mask_path}")
    aspect = float(color_image.size[0]) / float(color_image.size[1])
    half_height = 1.50
    half_width = half_height * aspect
    if uv_polygon is None:
        u0, v0, u1, v1 = uv_rect
        if not (0.0 <= u0 < u1 <= 1.0 and 0.0 <= v0 < v1 <= 1.0):
            raise SystemExit(f"invalid source crop UV: {uv_rect}")
        if grid_subdivisions is None:
            uv_points = ((u0, v0), (u1, v0), (u1, v1), (u0, v1))
            faces = [(0, 1, 2, 3)]
        else:
            columns, rows = grid_subdivisions
            if columns < 2 or rows < 2:
                raise SystemExit(f"invalid grid subdivisions: {grid_subdivisions}")
            uv_points = tuple(
                (
                    u0 + (u1 - u0) * column / columns,
                    v0 + (v1 - v0) * row / rows,
                )
                for row in range(rows + 1)
                for column in range(columns + 1)
            )
            faces = []
            stride = columns + 1
            for row in range(rows):
                for column in range(columns):
                    lower_left = row * stride + column
                    faces.append((lower_left, lower_left + 1, lower_left + stride + 1, lower_left + stride))
    else:
        if grid_subdivisions is not None:
            raise SystemExit("polygon and grid source planes are mutually exclusive")
        if len(uv_polygon) < 3 or any(not (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0) for u, v in uv_polygon):
            raise SystemExit(f"invalid source polygon UV: {uv_polygon}")
        uv_points = uv_polygon
        faces = [tuple(range(len(uv_points)))]
    vertices = [
        (-half_width + 2.0 * half_width * u, -half_height + 2.0 * half_height * v, 0.0)
        for u, v in uv_points
    ]
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.uv_layers.new(name="UVMap")
    uv_data = mesh.uv_layers.active.data
    for loop in mesh.loops:
        uv_data[loop.index].uv = uv_points[loop.vertex_index]
    plane = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(plane)
    material = bpy.data.materials.new(name + "_MATTE")
    material.use_nodes = True
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
    # The ImageGen source is an exact-green chroma master paired with a binary
    # subject matte.  Linear filtering pulls #00FF00 into the sampled subject
    # color at every silhouette edge while the binary matte still marks that
    # sample opaque, producing a visible neon fringe in the RGBA runtime
    # frame.  Nearest sampling preserves the reviewed source pixels and lets
    # the matte, rather than a green/color blend, define the edge.
    color_tex.interpolation = "Closest"
    mask_tex.interpolation = "Closest"
    # The leg mesh must sample the immutable source through its authored UV
    # coordinates.  Generated coordinates lock the image to the changing mesh
    # bounds and turn a real step into an almost-static texture distortion.
    links.new(tex_coord.outputs["UV"], color_tex.inputs["Vector"])
    links.new(tex_coord.outputs["UV"], mask_tex.inputs["Vector"])
    links.new(color_tex.outputs["Color"], emission.inputs["Color"])
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(emission.outputs[0], mix.inputs[2])
    # The supplied binary matte protects the source silhouette, but it may
    # bridge narrow concave spaces (for example between a bent leg and the
    # torso).  Intersect it with the approved exact-green chroma key so a
    # moved UV cutout never carries a green background triangle as body art.
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
    combined_alpha = nodes.new("ShaderNodeMath")
    combined_alpha.operation = "MULTIPLY"
    links.new(color_tex.outputs["Color"], separate.inputs[0])
    links.new(separate.outputs[0], red_low.inputs[0])
    links.new(separate.outputs[1], green_high.inputs[0])
    links.new(separate.outputs[2], blue_low.inputs[0])
    links.new(red_low.outputs[0], green_rg.inputs[0])
    links.new(green_high.outputs[0], green_rg.inputs[1])
    links.new(green_rg.outputs[0], green_exact.inputs[0])
    links.new(blue_low.outputs[0], green_exact.inputs[1])
    links.new(green_exact.outputs[0], non_green.inputs[1])
    links.new(mask_tex.outputs["Color"], combined_alpha.inputs[0])
    links.new(non_green.outputs[0], combined_alpha.inputs[1])
    links.new(combined_alpha.outputs[0], mix.inputs[0])
    links.new(mix.outputs[0], output.inputs["Surface"])
    plane.data.materials.append(material)
    return plane


def normalized_to_plane(uv: tuple[float, float]) -> tuple[float, float]:
    """Convert image UV to the plane's local coordinates."""
    half_height = 1.50
    half_width = 1.00
    return (-half_width + 2.0 * half_width * uv[0], -half_height + 2.0 * half_height * uv[1])


def segment_polygon(
    start: tuple[float, float],
    end: tuple[float, float],
    start_width: float,
    end_width: float,
) -> tuple[tuple[float, float], ...]:
    """Return a source-UV quadrilateral around one unmodified limb segment."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    if length < 0.001:
        raise SystemExit("invalid zero-length lower-body segment")
    perpendicular = (-dy / length, dx / length)

    def point(center: tuple[float, float], width: float, sign: float) -> tuple[float, float]:
        return (
            max(0.001, min(0.999, center[0] + perpendicular[0] * width * sign)),
            max(0.001, min(0.999, center[1] + perpendicular[1] * width * sign)),
        )

    return (point(start, start_width, 1.0), point(end, end_width, 1.0), point(end, end_width, -1.0), point(start, start_width, -1.0))


def pivot_plane(plane: bpy.types.Object, pivot: tuple[float, float], z_index: float) -> None:
    """Move a source-UV limb mesh into pivot-local coordinates without repainting it."""
    for vertex in plane.data.vertices:
        vertex.co.x -= pivot[0]
        vertex.co.y -= pivot[1]
    plane.data.update()
    plane.location = (pivot[0], pivot[1], z_index)


def build_segment(
    rgb_path: Path,
    mask_path: Path,
    name: str,
    start_uv: tuple[float, float],
    end_uv: tuple[float, float],
    crop_start_uv: tuple[float, float],
    crop_end_uv: tuple[float, float],
    start_width: float,
    end_width: float,
    z_index: float,
    root: bpy.types.Object,
) -> dict[str, object]:
    start = normalized_to_plane(start_uv)
    end = normalized_to_plane(end_uv)
    plane = build_subject_plane(
        rgb_path,
        mask_path,
        name,
        # Crop overlap deliberately extends above/below the actual bone ends.
        # It preserves knee/boot pixels when the two independently rotating
        # source cutouts meet, without changing the source image itself.
        uv_polygon=segment_polygon(crop_start_uv, crop_end_uv, start_width, end_width),
    )
    plane.parent = root
    pivot_plane(plane, start, z_index)
    vector = (end[0] - start[0], end[1] - start[1])
    return {
        "plane": plane,
        "start": start,
        "end": end,
        "length": math.hypot(vector[0], vector[1]),
        "angle": math.atan2(vector[1], vector[0]),
        "z_index": z_index,
    }


def build_joint_guard(
    rgb_path: Path,
    mask_path: Path,
    name: str,
    pivot_uv: tuple[float, float],
    crop_uv: tuple[float, float, float, float],
    z_index: float,
    root: bpy.types.Object,
) -> dict[str, object]:
    """Create a small source-pixel knee pad that follows a solved joint.

    It is not painted replacement art: it is an overlapping crop from the
    same approved master, used the way a 2D cutout rig uses an elbow pad to
    prevent a transparent seam while the two rigid bones rotate.
    """
    pivot = normalized_to_plane(pivot_uv)
    plane = build_subject_plane(rgb_path, mask_path, name, uv_rect=crop_uv)
    plane.parent = root
    pivot_plane(plane, pivot, z_index)
    return {"plane": plane, "pivot": pivot, "z_index": z_index}


def build_subject_rig(
    rgb_path: Path,
    mask_path: Path,
    direction: str,
    landmark_entry: dict[str, object] | None = None,
    move_rig_mode: str = "continuous",
) -> dict[str, object]:
    """Build a rigid upper body plus true two-segment source-art leg cutouts.

    V13/V14 warped one continuous lower-body mesh.  V15 keeps source pixels
    rigid within a thigh and a calf/boot segment, then uses Blender pivots and
    a two-bone solve to make the left/right feet genuinely alternate.
    """
    root = bpy.data.objects.new("ROOK_FAST_UAL_RIG_ROOT", None)
    bpy.context.scene.collection.objects.link(root)
    # Idle and Fire are source-master-preserving states.  The full plane is
    # rendered exclusively for them; the articulated cutouts below are hidden
    # rather than reconstructing the master from crops and risking a cut boot.
    full_plane = build_subject_plane(rgb_path, mask_path, "ROOK_FAST_UAL_STATIC_MASTER")
    full_plane.parent = root
    full_plane.location.z = -0.50
    # Move uses one continuous, source-UV mesh.  Unlike the rejected V15–V20
    # cutout planes, it cannot create a detached boot or transparent seam;
    # each leg region receives a rigid two-bone transform inside this mesh.
    deform_plane = build_subject_plane(
        rgb_path,
        mask_path,
        "ROOK_FAST_UAL_CONTINUOUS_TWO_BONE_MESH",
        grid_subdivisions=(64, 96),
    )
    deform_plane.parent = root
    deform_plane.location.z = 0.50
    base_vertices = [vertex.co.copy() for vertex in deform_plane.data.vertices]
    uv_data = deform_plane.data.uv_layers.active.data
    vertex_uvs: list[tuple[float, float]] = [(0.0, 0.0)] * len(deform_plane.data.vertices)
    for loop in deform_plane.data.loops:
        uv = uv_data[loop.index].uv
        vertex_uvs[loop.vertex_index] = (float(uv.x), float(uv.y))
    upper = build_subject_plane(
        rgb_path,
        mask_path,
        "ROOK_FAST_UAL_RIGID_UPPER",
        uv_rect=(0.0, 0.50, 1.0, 1.0),
    )
    upper.parent = root
    upper.location.z = -0.20
    static_lower = build_subject_plane(
        rgb_path,
        mask_path,
        "ROOK_FAST_UAL_STATIC_LOWER",
        uv_rect=(0.0, 0.0, 1.0, 0.50),
    )
    static_lower.parent = root
    static_lower.location.z = -0.10
    # The source's short split coat must remain static while the lower limbs
    # articulate.  This narrow source-UV guard is not painted replacement
    # art: it samples only the immutable master and keeps coat pixels out of
    # the moving thigh/calf topology.
    coat_guard = build_subject_plane(
        rgb_path,
        mask_path,
        "ROOK_FAST_UAL_STATIC_COAT_GUARD",
        uv_rect=(0.24, 0.38, 0.76, 0.56),
    )
    coat_guard.parent = root
    coat_guard.location.z = 0.34
    # A narrow static center guard preserves the south-view vertical scattergun
    # and pelvis while the two source-derived legs move independently around it.
    center_guard = build_subject_plane(
        rgb_path,
        mask_path,
        "ROOK_FAST_UAL_STATIC_CENTER_GUARD",
        uv_polygon=((0.38, 0.56), (0.62, 0.56), (0.62, 0.12), (0.38, 0.12)),
    )
    center_guard.parent = root
    center_guard.location.z = 0.30
    profiles = {
        "screen_left": {
            "joint": "foot_l",
            "hip": (0.40, 0.53), "knee": (0.27, 0.35), "ankle": (0.12, 0.08),
            "thigh_crop": ((0.40, 0.53), (0.25, 0.32)),
            "calf_crop": ((0.29, 0.38), (0.12, 0.08)),
            "thigh_width": (0.075, 0.090), "calf_width": (0.080, 0.120), "z": 0.02,
        },
        "screen_right": {
            "joint": "foot_r",
            "hip": (0.60, 0.53), "knee": (0.70, 0.34), "ankle": (0.88, 0.08),
            "thigh_crop": ((0.60, 0.53), (0.72, 0.31)),
            "calf_crop": ((0.68, 0.39), (0.88, 0.08)),
            "thigh_width": (0.075, 0.090), "calf_width": (0.080, 0.120), "z": 0.08,
        },
    }
    if landmark_entry is not None:
        landmarks = landmark_entry["legs"]
        for name, profile in profiles.items():
            points = landmarks[name]
            hip, knee, ankle = points["hip"], points["knee"], points["ankle"]
            toe = points["toe"]
            profile["hip"] = hip
            profile["knee"] = knee
            profile["ankle"] = ankle
            profile["toe"] = toe
            # The rigid-cutout planes are retained as source-pixel diagnostic
            # layers.  Their crop anchors must follow the explicit profile,
            # even though the continuous mesh is the visible move surface.
            profile["thigh_crop"] = (hip, knee)
            profile["calf_crop"] = (knee, ankle)
    legs: dict[str, dict[str, object]] = {}
    for name, profile in profiles.items():
        hip_uv = profile["hip"]
        knee_uv = profile["knee"]
        ankle_uv = profile["ankle"]
        toe_uv = profile.get("toe", ankle_uv)
        z_index = float(profile["z"])
        legs[name] = {
            "joint": profile["joint"],
            "hip_uv": hip_uv,
            "knee_uv": knee_uv,
            "ankle_uv": ankle_uv,
            "toe_uv": toe_uv,
            "hip": normalized_to_plane(hip_uv),
            "knee": normalized_to_plane(knee_uv),
            "ankle": normalized_to_plane(ankle_uv),
            "toe": normalized_to_plane(toe_uv),
            "thigh": build_segment(rgb_path, mask_path, f"ROOK_FAST_UAL_{name}_THIGH", hip_uv, knee_uv, *profile["thigh_crop"], *profile["thigh_width"], z_index, root),
            "calf": build_segment(rgb_path, mask_path, f"ROOK_FAST_UAL_{name}_CALF", knee_uv, ankle_uv, *profile["calf_crop"], *profile["calf_width"], z_index + 0.01, root),
            "knee_guard": build_joint_guard(
                rgb_path,
                mask_path,
                f"ROOK_FAST_UAL_{name}_KNEE_GUARD",
                knee_uv,
                (knee_uv[0] - 0.095, knee_uv[1] - 0.105, knee_uv[0] + 0.095, knee_uv[1] + 0.105),
                z_index + 0.12,
                root,
            ),
        }
    return {
        "root": root,
        "full_plane": full_plane,
        "deform_plane": deform_plane,
        "upper_plane": upper,
        "static_lower_plane": static_lower,
        "base_vertices": base_vertices,
        "vertex_uvs": vertex_uvs,
        "base_planes": [upper, static_lower, center_guard, coat_guard],
        "coat_guard": coat_guard,
        "move_rig_mode": move_rig_mode,
        "direction": direction,
        "legs": legs,
    }


def clear_subject_rig(rig: dict[str, object]) -> None:
    planes = [rig["full_plane"], rig["deform_plane"], *rig["base_planes"]]
    for leg in rig["legs"].values():  # type: ignore[index]
        planes.extend([leg["thigh"]["plane"], leg["calf"]["plane"], leg["knee_guard"]["plane"]])
    images: list[bpy.types.Image] = []
    materials: list[bpy.types.Material] = []
    for plane in planes:
        material = plane.data.materials[0]
        materials.append(material)
        images.extend(node.image for node in material.node_tree.nodes if node.type == "TEX_IMAGE" and node.image)
    for plane in planes:
        bpy.data.objects.remove(plane, do_unlink=True)
    bpy.data.objects.remove(rig["root"], do_unlink=True)
    for material in materials:
        if material.users == 0:
            bpy.data.materials.remove(material, do_unlink=True)
    for image in images:
        if image.users == 0:
            bpy.data.images.remove(image, do_unlink=True)


def locomotion_transform(sample: dict, direction: str, gain: float) -> tuple[float, float, float]:
    joints = sample["joints"]
    pelvis_delta = triplet(joints["pelvis"]["delta_from_reference_norm_xyz"], "pelvis delta")
    pelvis_screen = pair(joints["pelvis"]["screen_delta_xy"], "pelvis screen delta")
    head_screen = pair(joints["Head"]["screen_delta_xy"], "head screen delta")
    facing_x, facing_y = FACING[direction]
    side_x, side_y = -facing_y, facing_x
    forward = pelvis_screen[0] * gain * 0.62
    vertical = pelvis_screen[1] * gain * 0.88
    lateral = pelvis_delta[0] * gain * 0.90
    x = facing_x * forward + side_x * lateral
    y = facing_y * forward + side_y * lateral + vertical
    rotation = (head_screen[0] - pelvis_screen[0]) * gain * 0.115
    return x, y, rotation


def fire_transform(sample: dict, reference_hands: tuple[float, float, float], direction: str) -> tuple[float, float, float]:
    midpoint = triplet(sample["two_hand_corridor"]["hands_midpoint_norm"], "fire hand midpoint")
    dx, dy, dz = (midpoint[index] - reference_hands[index] for index in range(3))
    facing_x, facing_y = FACING[direction]
    side_x, side_y = -facing_y, facing_x
    # The six UAL Pistol_Shoot samples supply the timing and signed hand
    # displacement.  Rook's heavier scattergun uses an authored amplification
    # while staying on that measured temporal curve.
    forward = dy * 7.4
    lateral = dx * 5.2
    vertical = dz * 5.5
    x = facing_x * forward + side_x * lateral
    y = facing_y * forward + side_y * lateral + vertical
    rotation = lateral * 0.34
    return x, y, rotation


def reset_leg_pose(rig: dict[str, object]) -> None:
    """Return all four rigid source cutouts to their master-art pose."""
    for leg in rig["legs"].values():  # type: ignore[index]
        for segment_name in ("thigh", "calf"):
            segment = leg[segment_name]
            plane = segment["plane"]
            start_x, start_y = segment["start"]
            plane.location = (start_x, start_y, segment["z_index"])
            plane.rotation_euler = (0.0, 0.0, 0.0)
            plane.scale = (1.0, 1.0, 1.0)
        knee_guard = leg["knee_guard"]
        guard_plane = knee_guard["plane"]
        guard_pivot_x, guard_pivot_y = knee_guard["pivot"]
        guard_plane.location = (guard_pivot_x, guard_pivot_y, knee_guard["z_index"])
        guard_plane.rotation_euler = (0.0, 0.0, 0.0)
        guard_plane.scale = (1.0, 1.0, 1.0)
    mesh = rig["deform_plane"].data
    for vertex, base in zip(mesh.vertices, rig["base_vertices"]):
        vertex.co = base
    mesh.update()


def set_segment_pose(
    segment: dict[str, object],
    start: tuple[float, float],
    end: tuple[float, float],
) -> float:
    """Place an authored source-pixel segment between two two-bone joints."""
    delta_x, delta_y = end[0] - start[0], end[1] - start[1]
    target_length = math.hypot(delta_x, delta_y)
    base_length = float(segment["length"])
    if base_length < 0.001 or target_length < 0.001:
        raise SystemExit("invalid two-bone segment target")
    # Constrain stretch to a visually imperceptible amount.  The knee solver
    # produces the actual bend; scale only absorbs rounding/model differences.
    scale = max(0.96, min(1.04, target_length / base_length))
    plane = segment["plane"]
    plane.location = (start[0], start[1], float(segment["z_index"]))
    rotation = math.atan2(delta_y, delta_x) - float(segment["angle"])
    plane.rotation_euler = (0.0, 0.0, rotation)
    plane.scale = (scale, scale, 1.0)
    return rotation


def solve_walk_knee(
    hip: tuple[float, float],
    foot: tuple[float, float],
    thigh_length: float,
    calf_length: float,
    bend_sign: float,
) -> tuple[float, float]:
    """Resolve one deliberately articulated knee for a hip-to-foot target."""
    delta_x, delta_y = foot[0] - hip[0], foot[1] - hip[1]
    distance = math.hypot(delta_x, delta_y)
    if distance < 0.001:
        distance = 0.001
        delta_x, delta_y = 0.0, -distance
    min_reach = abs(thigh_length - calf_length) + 0.012
    max_reach = max(min_reach + 0.012, (thigh_length + calf_length) * 0.985)
    distance = max(min_reach, min(max_reach, distance))
    unit_x, unit_y = delta_x / math.hypot(delta_x, delta_y), delta_y / math.hypot(delta_x, delta_y)
    along = (thigh_length * thigh_length - calf_length * calf_length + distance * distance) / (2.0 * distance)
    height_sq = max(0.0, thigh_length * thigh_length - along * along)
    height = math.sqrt(height_sq)
    return (
        hip[0] + unit_x * along - unit_y * height * bend_sign,
        hip[1] + unit_y * along + unit_x * height * bend_sign,
    )


def rigid_two_bone_transform(
    point: tuple[float, float],
    source_pivot: tuple[float, float],
    target_pivot: tuple[float, float],
    source_end: tuple[float, float],
    target_end: tuple[float, float],
) -> tuple[float, float]:
    """Map one source point by a rigid/scarcely-scaled bone transform."""
    source_dx, source_dy = source_end[0] - source_pivot[0], source_end[1] - source_pivot[1]
    target_dx, target_dy = target_end[0] - target_pivot[0], target_end[1] - target_pivot[1]
    source_length = math.hypot(source_dx, source_dy)
    target_length = math.hypot(target_dx, target_dy)
    if source_length < 0.001 or target_length < 0.001:
        return point
    scale = max(0.96, min(1.04, target_length / source_length))
    rotation = math.atan2(target_dy, target_dx) - math.atan2(source_dy, source_dx)
    sine, cosine = math.sin(rotation), math.cos(rotation)
    local_x, local_y = point[0] - source_pivot[0], point[1] - source_pivot[1]
    return (
        target_pivot[0] + scale * (cosine * local_x - sine * local_y),
        target_pivot[1] + scale * (sine * local_x + cosine * local_y),
    )


def rigid_translation_transform(
    point: tuple[float, float],
    source_anchor: tuple[float, float],
    target_anchor: tuple[float, float],
) -> tuple[float, float]:
    """Move an authored boot with its ankle, retaining its source orientation.

    A 2D calf rotation is correct above the ankle but, if applied to the boot
    pixels, makes a planted boot spin like a 90-degree hinged foot.  The boot
    therefore receives only its ankle's translation.  This is a source-UV
    cutout-rig transform, never a painted replacement or source-art edit.
    """
    return (
        point[0] + target_anchor[0] - source_anchor[0],
        point[1] + target_anchor[1] - source_anchor[1],
    )


def point_segment_influence(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
    radius: float,
) -> float:
    """Return soft but local membership for a leg bone in source UV space."""
    segment_x, segment_y = end[0] - start[0], end[1] - start[1]
    length_sq = segment_x * segment_x + segment_y * segment_y
    if length_sq < 0.000001:
        return 0.0
    projected = ((point[0] - start[0]) * segment_x + (point[1] - start[1]) * segment_y) / length_sq
    projected = max(-0.08, min(1.08, projected))
    closest_x = start[0] + segment_x * projected
    closest_y = start[1] + segment_y * projected
    distance = math.hypot(point[0] - closest_x, point[1] - closest_y)
    return smoothstep01(1.0 - distance / radius)


def apply_continuous_two_bone_mesh(
    rig: dict[str, object],
    pose_layers: dict[str, dict[str, tuple[float, float]]],
) -> None:
    """Deform one continuous key-matted source mesh with two rigid leg bones.

    Strong interior vertices follow a single thigh or calf transform.  Only a
    narrow source-space band blends across the knee/hip borders, so the feet
    take a real alternating path instead of the V14 full-leg wobble while the
    mesh remains continuous and cannot expose alpha seams or ghost cutouts.
    """
    mesh = rig["deform_plane"].data
    for vertex, base, uv in zip(mesh.vertices, rig["base_vertices"], rig["vertex_uvs"]):
        source_point = (float(base.x), float(base.y))
        weighted: list[tuple[float, tuple[float, float]]] = []
        for name, layer in rig["legs"].items():  # type: ignore[index]
            pose = pose_layers[name]
            hip_uv = tuple(float(value) for value in layer["hip_uv"])
            knee_uv = tuple(float(value) for value in layer["knee_uv"])
            ankle_uv = tuple(float(value) for value in layer["ankle_uv"])
            toe_uv = tuple(float(value) for value in layer["toe_uv"])
            thigh_weight = point_segment_influence(uv, hip_uv, knee_uv, 0.105)
            # Calf influence ends at the ankle.  The boot gets a stronger
            # translation-only source-UV transform below, preventing the
            # previous 90-degree ankle/boot spin while preserving a seamless
            # overlap in the small ankle band.
            foot_weight = point_segment_influence(uv, ankle_uv, toe_uv, 0.140)
            calf_weight = point_segment_influence(uv, knee_uv, ankle_uv, 0.105) * (1.0 - foot_weight)
            if thigh_weight > 0.0:
                weighted.append((thigh_weight, rigid_two_bone_transform(source_point, pose["source_hip"], pose["target_hip"], pose["source_knee"], pose["target_knee"])))
            if calf_weight > 0.0:
                weighted.append((calf_weight, rigid_two_bone_transform(source_point, pose["source_knee"], pose["target_knee"], pose["source_ankle"], pose["target_foot"])))
            if foot_weight > 0.0:
                weighted.append((foot_weight * 1.55, rigid_translation_transform(source_point, pose["source_ankle"], pose["target_foot"])))
        if not weighted:
            vertex.co = base
            continue
        weight_total = sum(weight for weight, _target in weighted)
        # Keep torso/pelvis stability where a source point sits just outside a
        # limb; within a limb all available weight belongs to its hard bones.
        strongest = max(weight for weight, _target in weighted)
        motion_weight = smoothstep01(strongest)
        target_x = sum(weight * point[0] for weight, point in weighted) / weight_total
        target_y = sum(weight * point[1] for weight, point in weighted) / weight_total
        vertex.co = (
            base.x + (target_x - base.x) * motion_weight,
            base.y + (target_y - base.y) * motion_weight,
            base.z,
        )
    mesh.update()


def smoothstep01(value: float) -> float:
    clamped = max(0.0, min(1.0, value))
    return clamped * clamped * (3.0 - 2.0 * clamped)


def heel_plant_cycle(phase: float, *, stride: float, swing_lift: float) -> tuple[float, float, bool]:
    """Return a local-space foot path for one heel-heavy walk cycle.

    During stance the body passes over a fixed foot, so that foot travels from
    forward to rear in local space.  During swing it returns forward through a
    raised arc.  The opposite leg is offset by one half-cycle.
    """
    # The source master begins in a deliberately wide breach stance.  A
    # Keep the solved ankle center inside the authority master's planted boot
    # envelope.  The 0.12-unit path remains plainly visible at native scale,
    # while the independent swing lift supplies the clear heel-off phase.
    stance_fraction = 0.62
    if phase < stance_fraction:
        stance_progress = phase / stance_fraction
        return stride - 2.0 * stride * stance_progress, 0.0, True
    swing_progress = (phase - stance_fraction) / (1.0 - stance_fraction)
    forward = -stride + 2.0 * stride * smoothstep01(swing_progress)
    lift = math.sin(math.pi * swing_progress) * swing_lift
    return forward, lift, False


def leg_transform(
    sample: dict,
    direction: str,
    joint_name: str,
    frame_index: int,
    frame_count: int,
    phase_offset: float,
    gait: dict[str, object],
) -> tuple[tuple[float, float, float], dict[str, object]]:
    """Map UAL cadence to alternating planted-foot / swing-foot motion."""
    joints = sample["joints"]
    foot = joints[joint_name]
    calf = joints[joint_name.replace("foot", "calf")]
    thigh = joints[joint_name.replace("foot", "thigh")]
    forward, _lift = pair(foot["screen_delta_xy"], joint_name + ".screen_delta_xy")
    calf_forward, calf_lift = pair(calf["screen_delta_xy"], joint_name + ".calf_screen_delta_xy")
    _thigh_forward, thigh_lift = pair(thigh["screen_delta_xy"], joint_name + ".thigh_screen_delta_xy")
    facing_x, facing_y = FACING[direction]
    side_x, side_y = -facing_y, facing_x
    phase = (float(frame_index) / float(frame_count) + phase_offset) % 1.0
    cycle_forward, cycle_lift, planted = heel_plant_cycle(
        phase,
        stride=float(gait["stride_units"]),
        swing_lift=float(gait["swing_lift_units"]),
    )
    # The authored stance/swing path is primary; measured UAL joints add only
    # a small cadence detail and remain the timing authority for all 24 frames.
    ual_forward_detail = forward * 0.022
    ual_lateral_detail = (calf_forward - forward) * 0.025
    ual_lift_detail = (calf_lift - thigh_lift) * 0.018
    forward_motion = cycle_forward + ual_forward_detail
    x = facing_x * forward_motion + side_x * ual_lateral_detail
    y = facing_y * forward_motion + side_y * ual_lateral_detail + cycle_lift + ual_lift_detail
    # Side views show a readable hip-to-boot rotation; front/back views use
    # the full planted-foot translation without twisting the center weapon.
    # Plane Y grows from the hip toward the boots.  The negative sign makes
    # the hip rotation reinforce the planted-foot advance instead of canceling
    # its translational stride at the ankle.
    rotation = -forward_motion * 0.52 * facing_x + ual_lift_detail * 0.18
    return (x, y, rotation), {
        "phase": round(phase, 6),
        "planted": planted,
        "forward_local": round(cycle_forward, 6),
        "swing_lift": round(cycle_lift, 6),
    }


def apply_leg_pose(
    rig: dict[str, object],
    sample: dict,
    direction: str,
    frame_index: int,
    frame_count: int,
    gait: dict[str, object],
    *,
    apply_continuous_mesh: bool,
) -> tuple[dict[str, list[float]], dict[str, dict[str, object]]]:
    poses: dict[str, list[float]] = {}
    gait_cycle: dict[str, dict[str, object]] = {}
    pose_layers: dict[str, dict[str, tuple[float, float]]] = {}
    for name, layer in rig["legs"].items():  # type: ignore[index]
        phase_offset = 0.0 if name == "screen_left" else 0.5
        (x, y, _rotation), cycle = leg_transform(
            sample,
            direction,
            str(layer["joint"]),
            frame_index,
            frame_count,
            phase_offset,
            gait,
        )
        hip = tuple(float(value) for value in layer["hip"])
        ankle = tuple(float(value) for value in layer["ankle"])
        target_foot = (ankle[0] + x, ankle[1] + y)
        # Mirror the knee bend by screen side.  This is a real two-bone solve:
        # thigh pivots at hip, calf pivots at knee, and the boot follows its
        # own alternating planted/swing target.
        knee = solve_walk_knee(
            hip,
            target_foot,
            float(layer["thigh"]["length"]),
            float(layer["calf"]["length"]),
            -1.0 if name == "screen_left" else 1.0,
        )
        thigh_rotation = set_segment_pose(layer["thigh"], hip, knee)
        calf_rotation = set_segment_pose(layer["calf"], knee, target_foot)
        # The knee pad uses the average local direction of both bones and
        # overlaps their source edges, hiding the otherwise transparent cut
        # boundary while retaining visibly independent thigh/calf rotation.
        guard = layer["knee_guard"]
        guard_plane = guard["plane"]
        guard_plane.location = (knee[0], knee[1], guard["z_index"])
        guard_plane.rotation_euler = (0.0, 0.0, 0.5 * (thigh_rotation + calf_rotation))
        pose_layers[name] = {
            "source_hip": hip,
            "target_hip": hip,
            "source_knee": tuple(float(value) for value in layer["knee"]),
            "target_knee": knee,
            "source_ankle": ankle,
            "source_toe": tuple(float(value) for value in layer["toe"]),
            "target_foot": target_foot,
        }
        poses[name] = [round(target_foot[0] - ankle[0], 7), round(target_foot[1] - ankle[1], 7), 0.0]
        cycle["hip"] = [round(hip[0], 7), round(hip[1], 7)]
        cycle["knee"] = [round(knee[0], 7), round(knee[1], 7)]
        cycle["foot_target"] = [round(target_foot[0], 7), round(target_foot[1], 7)]
        gait_cycle[name] = cycle
    if apply_continuous_mesh:
        apply_continuous_two_bone_mesh(rig, pose_layers)
    return poses, gait_cycle


def render_state(
    scene: bpy.types.Scene,
    rig: dict[str, object],
    output_dir: Path,
    state: str,
    transforms: list[tuple[float, float, float]],
    gait_samples: list[dict] | None = None,
    direction: str | None = None,
    gait: dict[str, object] | None = None,
) -> list[dict]:
    rows: list[dict] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for index, (x, y, rotation) in enumerate(transforms):
        root = rig["root"]
        articulated_move = gait_samples is not None
        segmented_move = articulated_move and rig.get("move_rig_mode") == "segmented"
        # Runtime locomotion owns the actor's world translation and facing.
        # The cutout's root therefore stays at the exact camera origin for
        # every move frame.  Applying UAL pelvis/head offsets to the whole
        # source was the source of the visible body wobble and side-facing
        # waist twist: UAL drives cadence and the independent legs below, not
        # the character's entire rendered body.
        root.location = (0.0, 0.0, 0.0)
        root.rotation_euler = (0.0, 0.0, 0.0)
        fire_upper_only = state == "fire"
        rig["full_plane"].hide_render = articulated_move or fire_upper_only
        rig["deform_plane"].hide_render = not articulated_move or segmented_move
        for plane in rig["base_planes"]:  # type: ignore[index]
            plane.hide_render = True
        upper_plane = rig["upper_plane"]
        upper_plane.location = (0.0, 0.0, -0.20)
        upper_plane.rotation_euler = (0.0, 0.0, 0.0)
        if fire_upper_only:
            upper_plane.hide_render = False
            upper_plane.location = (x, y, -0.20)
            upper_plane.rotation_euler = (0.0, 0.0, rotation)
            rig["static_lower_plane"].hide_render = False
        for leg in rig["legs"].values():  # type: ignore[index]
            leg["thigh"]["plane"].hide_render = not segmented_move
            leg["calf"]["plane"].hide_render = not segmented_move
            leg["knee_guard"]["plane"].hide_render = not segmented_move
        if segmented_move:
            # Keep head, weapon, torso and the short split coat fixed.  Only
            # explicitly cropped limb source pixels are articulated, avoiding
            # the calf ballooning/coat arcs produced by a continuous whole
            # body deformation mesh.
            upper_plane.hide_render = False
            rig["coat_guard"].hide_render = False
        reset_leg_pose(rig)
        leg_poses: dict[str, list[float]] = {}
        gait_cycle: dict[str, dict[str, object]] = {}
        if gait_samples is not None:
            if direction is None or index >= len(gait_samples):
                raise SystemExit("move gait samples require a matching direction and frame index")
            if gait is None:
                raise SystemExit("articulated move requires a direction-specific low-lift gait profile")
            leg_poses, gait_cycle = apply_leg_pose(
                rig,
                gait_samples[index],
                direction,
                index,
                len(gait_samples),
                gait,
                apply_continuous_mesh=not segmented_move,
            )
        output = output_dir / f"{index:02d}.png"
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        if not output.is_file() or output.stat().st_size <= 0:
            raise SystemExit(f"Blender failed to render {state} frame {index}: {output}")
        row = {
            "index": index,
            "path": output.relative_to(ROOT).as_posix(),
            "ual_sample_transform": [round(x, 7), round(y, 7), round(rotation, 7)],
            "root_transform": [0.0, 0.0, 0.0],
            "sha256": sha256(output),
        }
        if leg_poses:
            row["independent_leg_transforms"] = leg_poses
            row["gait_cycle"] = gait_cycle
        rows.append(row)
    return rows


def main() -> int:
    args = parse_args()
    spec_path = project_path(args.spec, "spec")
    candidate = project_path(args.candidate, "candidate")
    locomotion_path = project_path(args.ual_locomotion, "ual-locomotion")
    fire_path = project_path(args.ual_fire, "ual-fire")
    if candidate.exists() and any(candidate.iterdir()):
        # A headless renderer can be interrupted between individual frames.
        # Resuming is safe only while the candidate contains *only* raw frame
        # paths: every expected frame is deterministically rendered again and
        # no packaged/promoted artifact can be replaced by this path.
        entries = {entry.name for entry in candidate.iterdir()}
        if entries != {"blender_frames"}:
            raise SystemExit(f"refusing to overwrite non-resumable candidate: {candidate}")
    spec = load_json(spec_path, "spec")
    art_prefix = str(spec.get("art_prefix", "ROOK_C02"))
    if spec.get("actor_id") == "CHR_PROTO_03" or art_prefix.startswith("MICA"):
        quarantine_root = (ROOT / "artifacts" / "quarantine").resolve()
        if not args.diagnostic_only or not candidate.resolve().is_relative_to(quarantine_root):
            raise SystemExit("MICA_CUTOUT_PRODUCTION_BLOCKED: source-plane slicing/warping is a rejected motion family. Use approved skinned geometry with evaluated vertex QA. Diagnostics require --diagnostic-only and a new artifacts/quarantine subdirectory.")
    source_root = (
        project_path(args.source_root, "source-root")
        if args.source_root is not None
        else ROOT / spec["paths"]["work_root"] / "imagegen" / "current"
    )
    if not source_root.is_dir():
        raise SystemExit(f"ImageGen direction-master root is missing: {source_root}")
    landmarks_path = project_path(args.leg_landmarks, "leg-landmarks") if args.leg_landmarks is not None else None
    if landmarks_path is None:
        raise SystemExit("a promotable direction-master render requires --leg-landmarks")
    landmarks = load_direction_landmarks(landmarks_path)
    review_path = source_root / f"{art_prefix}_COSTUME_CONTINUITY_REVIEW.json"
    review = load_json(review_path, "costume continuity review")
    if review.get("costume_continuity") != "PASS":
        raise SystemExit(f"{art_prefix} source-art costume continuity must PASS before motion")
    locomotion = load_json(locomotion_path, "UAL locomotion")
    samples = locomotion.get("locomotion", {}).get("samples", [])
    if not isinstance(samples, list) or len(samples) != 24:
        raise SystemExit("UAL locomotion must provide exactly 24 samples")
    fire = load_json(fire_path, "UAL fire")
    fire_samples = fire.get("samples", [])
    if not isinstance(fire_samples, list) or len(fire_samples) != 6:
        raise SystemExit("UAL fire must provide exactly six samples")
    runtime = spec["runtime"]
    cell_size = int(runtime["cell_size"])
    if cell_size != 384:
        raise SystemExit("fast pipeline Blender renderer currently requires 384px cells")
    candidate.mkdir(parents=True, exist_ok=True)
    scene, _camera = configure_scene(cell_size)
    records: dict[str, dict[str, list[dict]]] = {}
    # Preserve the exact ImageGen authority chain in the render manifest.  The
    # renderer uses the exact-green technical derivative when available, but
    # promotion must also be able to prove which immutable selected master it
    # came from.  Without these per-direction hashes a later source replacement
    # could silently change a re-render while retaining the same root path.
    source_master_images: dict[str, dict[str, str]] = {}
    idle_indices = (0, 6, 12, 18)
    idle_transforms = [locomotion_transform(samples[index], "E", 0.30) for index in idle_indices]
    fire_reference = triplet(fire_samples[0]["two_hand_corridor"]["hands_midpoint_norm"], "fire reference hands")
    for direction in DIRECTIONS:
        master_rgb = source_root / f"{art_prefix}_{direction}_IMAGEGEN_GREEN.png"
        exact_rgb = source_root / f"{art_prefix}_{direction}_IMAGEGEN_EXACT_GREEN.png"
        rgb = exact_rgb if exact_rgb.is_file() else master_rgb
        mask = source_root / f"{art_prefix}_{direction}_IMAGEGEN_MASK.png"
        if not master_rgb.is_file() or not rgb.is_file() or not mask.is_file():
            raise SystemExit(f"missing direction authority for {direction}")
        source_master_images[direction] = {
            "selected_master": master_rgb.relative_to(ROOT).as_posix(),
            "selected_master_sha256": sha256(master_rgb),
            "render_input": rgb.relative_to(ROOT).as_posix(),
            "render_input_sha256": sha256(rgb),
            "mask": mask.relative_to(ROOT).as_posix(),
            "mask_sha256": sha256(mask),
        }
        direction_landmarks = landmarks[direction]
        rig = build_subject_rig(
            rgb,
            mask,
            direction,
            direction_landmarks,
            move_rig_mode=args.move_rig_mode,
        )
        direction_rows: dict[str, list[dict]] = {}
        direction_rows["idle"] = render_state(
            scene, rig, candidate / "blender_frames" / direction / "idle", "idle",
            [locomotion_transform(samples[index], direction, 0.30) for index in idle_indices],
        )
        direction_rows["move"] = render_state(
            scene, rig, candidate / "blender_frames" / direction / "move", "move",
            [locomotion_transform(sample, direction, 1.85) for sample in samples],
            gait_samples=samples,
            direction=direction,
            gait=direction_landmarks["gait"],
        )
        direction_rows["fire"] = render_state(
            scene, rig, candidate / "blender_frames" / direction / "fire", "fire",
            [fire_transform(sample, fire_reference, direction) for sample in fire_samples],
        )
        records[direction] = direction_rows
        clear_subject_rig(rig)
    blend_path = candidate / "blender_scene" / f"{art_prefix}_FAST_UAL_V1.blend"
    blend_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    manifest = {
        "schema": 1,
        "role": f"{art_prefix} Blender-rendered ImageGen-master motion frames driven by licensed UAL1 timing and separately pivoted two-bone source-art cutouts",
        "source_art": "built-in ImageGen direction masters plus project-local rigid UV limb cutouts",
        "motion_only": True,
        "source_master_root": source_root.relative_to(ROOT).as_posix(),
        "source_master_images": source_master_images,
        "blender": {"version": bpy.app.version_string, "scene": blend_path.relative_to(ROOT).as_posix(), "scene_sha256": sha256(blend_path)},
        "ual": {
            "locomotion_curve": locomotion_path.relative_to(ROOT).as_posix(),
            "locomotion_curve_sha256": sha256(locomotion_path),
            "fire_curve": fire_path.relative_to(ROOT).as_posix(),
            "fire_curve_sha256": sha256(fire_path),
            "license": "CC0-1.0 motion-only reference",
            "locomotion_action": locomotion.get("locomotion", {}).get("action"),
            "fire_action": fire.get("action", {}).get("name"),
        },
        "states": {"idle": 4, "move": 24, "fire": 6},
        "leg_rig": {
            "authoring": (
                "Blender segmented rigid source-pixel thigh/calf/boot rig with a fixed torso/coat guard "
                "and translation-only boot regions below each ankle"
                if args.move_rig_mode == "segmented"
                else "Blender continuous high-density source-UV mesh with per-leg rigid hip-knee-ankle transforms, translation-only boot regions below each ankle, a narrow blended joint band, and exact-green chroma removal from the approved ImageGen master"
            ),
            "move_rig_mode": args.move_rig_mode,
            "source_art_modified": False,
            "separate_leg_controls": ["screen_left", "screen_right"],
            "ual_drivers": ["foot_l", "calf_l", "thigh_l", "foot_r", "calf_r", "thigh_r"],
            "direction_landmarks": landmarks_path.relative_to(ROOT).as_posix(),
            "direction_landmarks_sha256": sha256(landmarks_path),
            "move_frame_contract": "Every move record contains independent left/right foot targets and solved hip-knee-ankle points; left/right support phases differ by one half-cycle, swing phases never overlap, and brief double-support contact is preserved.",
            "foot_orientation_policy": "Boot pixels below each explicit ankle-to-toe segment receive translation only; no frame may rotate a planted boot around the ankle.",
            "root_motion_policy": "Runtime owns actor translation/facing. Every Blender move frame holds the full-body root at [0,0,0]; UAL is used only for cadence and independent-leg timing/detail.",
        },
        "directions": records,
        "frame_output": "RGBA Blender frames; exact-green atlas packaging is a separate deterministic technical step",
    }
    manifest_path = candidate / f"{art_prefix}_BLENDER_UAL_RENDER_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("FAST_BLENDER_UAL_RENDER_PASS=" + json.dumps({"actor_id": spec.get("actor_id"), "candidate": candidate.relative_to(ROOT).as_posix(), "frames": 8 * (4 + 24 + 6), "manifest": manifest_path.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
