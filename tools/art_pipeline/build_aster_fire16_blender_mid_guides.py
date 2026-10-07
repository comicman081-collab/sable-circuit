"""Render four mesh-only spatial guides for ASTER's axial-adjacent aim views.

The proxy is authored inside Blender and is never a character asset.  It only
locks screen-space rifle direction, the two-hand corridor, head/ponytail side,
and front/back occlusion order for local image editing.  No downloaded base
character or UAL preview mesh is used or rendered.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_v1_pose_guides_v3"
DIRECTIONS = {"SSE": 67.5, "SSW": 112.5, "NNW": 247.5, "NNE": 292.5}
# Image authoring has repeatedly flattened the exact 67.5-degree guide toward
# ~50 degrees.  This extra guide is an authoring-only bias-compensation input;
# it is never direction authority and cannot enter a runtime manifest.
SSE_AUTHORING_COMPENSATION_DEGREES = 107.0
RESOLUTION = 1254


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def material(name: str, rgba: tuple[float, float, float, float]):
    result = bpy.data.materials.new(name)
    result.diffuse_color = rgba
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Roughness"].default_value = 0.68
    shader.inputs["Emission Color"].default_value = rgba
    shader.inputs["Emission Strength"].default_value = 0.85
    return result


def ellipse(name: str, xy: tuple[float, float], scale: tuple[float, float], depth: float, mat, parent):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=24, location=(xy[0], xy[1], depth))
    item = bpy.context.object
    item.name = name
    item.scale = (scale[0], scale[1], 0.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    item.data.materials.append(mat)
    item.parent = parent
    return item


def beam(name: str, start: tuple[float, float], end: tuple[float, float], radius: float, depth: float, mat, parent):
    a, b = Vector((start[0], start[1], depth)), Vector((end[0], end[1], depth))
    delta = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=delta.length, location=(a + b) * 0.5)
    item = bpy.context.object
    item.name = name
    item.rotation_mode = "QUATERNION"
    item.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(delta.normalized())
    item.rotation_mode = "XYZ"
    item.data.materials.append(mat)
    item.parent = parent
    return item


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    green = (0.0, 1.0, 0.0, 1.0)
    navy = material("GuideBody", (0.02, 0.09, 0.18, 1.0))
    silver = material("GuideHair", (0.72, 0.78, 0.86, 1.0))
    skin = material("GuideHands", (0.72, 0.48, 0.40, 1.0))
    rifle = material("GuideRifle", (0.035, 0.045, 0.055, 1.0))
    cyan = material("GuideAxis", (0.0, 0.88, 1.0, 1.0))

    root = bpy.data.objects.new("ASTER_FIRE16_GUIDE_ROTATION_ROOT", None)
    bpy.context.scene.collection.objects.link(root)
    # E-facing screen-space proxy.  Rotation around Z supplies the four exact
    # 22.5-degree target views; higher Z is rendered in front.
    ellipse("Torso", (0.0, 0.0), (0.55, 0.78), 0.10, navy, root)
    ellipse("Head", (-0.18, 0.62), (0.35, 0.40), 0.22, silver, root)
    # Do not include a white armor proxy.  V2's white shoulder ellipse was
    # copied into generated source art as an unauthorized pauldron.  A small,
    # flush navy shoulder volume keeps anatomy readable without inventing a
    # costume part.
    ellipse("FittedShoulder", (0.15, 0.34), (0.27, 0.21), 0.28, navy, root)
    beam("PonytailA", (-0.38, 0.72), (-1.10, 1.05), 0.20, 0.05, silver, root)
    beam("PonytailB", (-1.02, 1.02), (-1.45, 0.70), 0.16, 0.04, silver, root)
    # The complete rifle + both hands + both connected forearms is one visual
    # corridor in the guide, matching the runtime upper-layer ownership rule.
    beam("RearForearm", (-0.30, 0.18), (0.35, 0.20), 0.16, 0.24, navy, root)
    beam("ForwardForearm", (0.0, -0.16), (0.88, -0.03), 0.15, 0.25, navy, root)
    beam("Rifle", (-0.58, 0.11), (1.72, 0.11), 0.095, 0.32, rifle, root)
    ellipse("TriggerHand", (0.30, 0.16), (0.13, 0.11), 0.36, skin, root)
    ellipse("SupportHand", (0.86, 0.02), (0.13, 0.11), 0.36, skin, root)
    beam("BarrelAxis", (0.18, 0.11), (1.80, 0.11), 0.018, 0.39, cyan, root)
    ellipse("MuzzleSocket", (1.80, 0.11), (0.08, 0.08), 0.40, cyan, root)

    bpy.ops.object.camera_add(location=(0.0, 0.0, 10.0))
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 4.6
    camera.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.scene.camera = camera
    world = bpy.data.worlds.new("ExactChromaGreen")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = green
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    scene = bpy.context.scene
    scene.world = world
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = RESOLUTION
    scene.render.resolution_y = RESOLUTION
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"

    records = []
    for direction, angle in DIRECTIONS.items():
        # Image-space Y points down; Blender Y points up.
        root.rotation_euler[2] = math.radians(-angle)
        output = OUTPUT / f"ASTER_FIRE_{direction}_BLENDER_POSE_OCCLUSION_GUIDE_GREEN.png"
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        records.append({
            "direction": direction,
            "angle_degrees": angle,
            "image": output.relative_to(ROOT).as_posix(),
            "sha256": digest(output),
            "resolution": [RESOLUTION, RESOLUTION],
            "rifle_hands_forearms_one_corridor": True,
            "final_character_asset": False,
            "unauthorized_white_shoulder_proxy_present": False,
        })

    root.rotation_euler[2] = math.radians(-SSE_AUTHORING_COMPENSATION_DEGREES)
    compensation = OUTPUT / "ASTER_FIRE_SSE_AUTHORING_BIAS_COMPENSATION_GUIDE_GREEN.png"
    scene.render.filepath = str(compensation)
    bpy.ops.render.render(write_still=True)

    blend = OUTPUT / "ASTER_FIRE16_MID_POSE_GUIDES__NONFINAL.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    manifest = {
        "schema": 1,
        "role": "headless-Blender spatial/occlusion guide only",
        "blender_version": bpy.app.version_string,
        "external_base_character_used": False,
        "ual_preview_mesh_used": False,
        "final_character_rendered": False,
        "source_background": "#00FF00",
        "records": records,
        "authoring_bias_compensation": {
            "direction": "SSE",
            "guide_angle_degrees": SSE_AUTHORING_COMPENSATION_DEGREES,
            "target_runtime_angle_degrees": DIRECTIONS["SSE"],
            "image": compensation.relative_to(ROOT).as_posix(),
            "sha256": digest(compensation),
            "runtime_direction_authority": False,
            "reason": "calibrated from 67.5->50.6 and 85.0->58.1 measured authoring responses; exact 67.5-degree guide remains authority",
        },
        "costume_safety": {
            "unauthorized_white_shoulder_proxy_present": False,
            "fitted_navy_shoulder_proxy_only": True,
        },
        "blend": blend.relative_to(ROOT).as_posix(),
        "blend_sha256": digest(blend),
    }
    manifest_path = OUTPUT / "ASTER_FIRE16_MID_POSE_GUIDES_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_FIRE16_GUIDES=" + json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
