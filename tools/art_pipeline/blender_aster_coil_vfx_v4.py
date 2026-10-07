#!/usr/bin/env python3
"""Render ASTER coil projectile/impact V4 with Blender 5.2.1 headless.

This is original procedural geometry. Blender supplies stable 3D volume,
lighting and camera depth; a separate local finalizer adds controlled optical
bloom, atlas packing and green separation QA.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "art_src/pilot_v2/aster_v2/vfx/coil_projectile_v4_blender/raw"
FRAMES = 8


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.curves, bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def configure(width: int, height: int, ortho: float, camera_location: tuple[float, float, float], target: tuple[float, float, float]) -> bpy.types.Camera:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.image_settings.color_depth = "16"
    scene.render.resolution_percentage = 100
    scene.render.use_file_extension = True
    scene.render.image_settings.compression = 15
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.color = (0.005, 0.007, 0.01)

    bpy.ops.object.camera_add(location=camera_location)
    camera_object = bpy.context.object
    camera_object.data.type = "ORTHO"
    camera_object.data.ortho_scale = ortho
    camera_object.rotation_euler = (Vector(target) - camera_object.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera_object
    return camera_object.data


def material(name: str, colour: tuple[float, float, float, float], metallic: float = 0.0, roughness: float = 0.28, emission: tuple[float, float, float, float] | None = None, strength: float = 0.0) -> bpy.types.Material:
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.diffuse_color = colour
    bsdf = result.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = colour
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = strength
    return result


def assign(obj: bpy.types.Object, mat: bpy.types.Material) -> bpy.types.Object:
    obj.data.materials.append(mat)
    return obj


def cylinder(name: str, x: float, radius: float, depth: float, mat: bpy.types.Material, vertices: int = 48) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=(x, 0, 0), rotation=(0, math.pi / 2, 0))
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    bevel = obj.modifiers.new("Micro bevel", "BEVEL")
    bevel.width = min(radius * 0.18, 0.08)
    bevel.segments = 3
    return obj


def torus(name: str, x: float, major: float, minor: float, mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=64, minor_segments=12, location=(x, 0, 0), rotation=(0, math.pi / 2, 0))
    obj = bpy.context.object
    obj.name = name
    return assign(obj, mat)


def poly_curve(name: str, points: list[tuple[float, float, float]], radius: float, mat: bpy.types.Material) -> bpy.types.Object:
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 2
    data.bevel_depth = radius
    data.bevel_resolution = 3
    spline = data.splines.new("NURBS")
    spline.points.add(len(points) - 1)
    for point, value in zip(spline.points, points):
        point.co = (*value, 1.0)
    spline.order_u = min(3, len(points))
    spline.use_endpoint_u = True
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return assign(obj, mat)


def add_area_light(name: str, location: tuple[float, float, float], colour: tuple[float, float, float], energy: float, size: float, target: tuple[float, float, float]) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.color = colour
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def setup_projectile() -> dict[str, object]:
    gold = material("Coil gold", (0.34, 0.11, 0.018, 1), metallic=0.92, roughness=0.16)
    dark = material("Coil dark", (0.012, 0.02, 0.025, 1), metallic=0.82, roughness=0.23)
    hot = material("White plasma", (1, 0.64, 0.15, 1), roughness=0.08, emission=(1, 0.42, 0.045, 1), strength=18)
    white = material("White core", (1, 0.96, 0.78, 1), roughness=0.05, emission=(1, 0.78, 0.34, 1), strength=35)
    cyan = material("Magnetic sheath", (0.025, 0.38, 0.52, 1), roughness=0.08, emission=(0.015, 0.63, 1, 1), strength=16)
    amber = material("Ion wake", (0.8, 0.09, 0.004, 1), roughness=0.1, emission=(1, 0.12, 0.005, 1), strength=13)

    cylinder("Plasma spine", 0.5, 0.12, 6.2, hot, vertices=32)
    cylinder("White kinetic core", 1.1, 0.052, 5.6, white, vertices=24)
    cylinder("Faceted coil body", 2.45, 0.42, 1.55, dark, vertices=12)
    cylinder("Gold forward collar", 3.28, 0.46, 0.34, gold, vertices=48)
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.46, radius2=0.045, depth=0.92, location=(3.9, 0, 0), rotation=(0, math.pi / 2, 0))
    nose = assign(bpy.context.object, gold)
    nose.name = "Faceted energized dart"
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=(4.37, 0, 0), scale=(0.24, 0.22, 0.22))
    assign(bpy.context.object, white)

    rings = []
    for index, x in enumerate((1.55, 1.95, 2.35, 2.78)):
        rings.append(torus(f"Coil ring {index}", x, 0.58 - index * 0.035, 0.038, cyan if index % 2 == 0 else hot))

    trails = []
    for index, (x, length, radius) in enumerate(((-2.95, 0.8, 0.035), (-2.0, 0.65, 0.052), (-1.12, 0.7, 0.07), (-0.18, 0.78, 0.09))):
        trails.append(cylinder(f"Wake segment {index}", x, radius, length, amber, vertices=20))

    helix_objects = []
    for strand in range(2):
        points = []
        for step in range(48):
            t = step / 47
            x = -1.4 + t * 4.0
            angle = t * math.tau * 3.15 + strand * math.pi
            radius = 0.30 + t * 0.24
            points.append((x, math.cos(angle) * radius, math.sin(angle) * radius))
        helix_objects.append(poly_curve(f"Magnetic helix {strand}", points, 0.021, cyan))

    rng = random.Random(7241)
    sparks = []
    for index in range(20):
        start_x = rng.uniform(-0.7, 3.0)
        side = -1 if index % 2 else 1
        y = side * rng.uniform(0.24, 0.55)
        z = rng.uniform(-0.48, 0.48)
        length = rng.uniform(0.28, 0.9)
        points = [(start_x, y, z), (start_x - length, y + side * rng.uniform(0.06, 0.3), z + rng.uniform(-0.22, 0.22))]
        sparks.append(poly_curve(f"Kinetic spark {index}", points, 0.014 if index % 3 else 0.022, hot if index % 4 else cyan))

    add_area_light("Warm rim", (2, -4.5, 3.2), (1, 0.22, 0.035), 1150, 4.0, (1.6, 0, 0))
    add_area_light("Cyan rim", (2.8, 2.5, 2.2), (0.02, 0.5, 1.0), 900, 3.0, (2.4, 0, 0))
    return {"rings": rings, "trails": trails, "helix": helix_objects, "sparks": sparks, "materials": {"hot": hot, "cyan": cyan, "white": white}}


def update_projectile(state: dict[str, object], frame: int) -> None:
    phase = frame / FRAMES * math.tau
    for index, ring in enumerate(state["rings"]):
        ring.rotation_euler.x = phase * (1.0 if index % 2 else -1.0) + index * 0.4
        ring.scale = Vector((1.0, 1.0 + math.sin(phase + index) * 0.07, 1.0 + math.cos(phase + index) * 0.07))
    for index, trail in enumerate(state["trails"]):
        trail.location.z = math.sin(phase + index * 1.7) * 0.045
        trail.scale.y = 0.82 + 0.18 * math.sin(phase * 2 + index)
    for index, spark in enumerate(state["sparks"]):
        spark.rotation_euler.x = phase * (0.35 if index % 2 else -0.28)
        spark.hide_render = (frame + index) % 4 == 0
    for strand, obj in enumerate(state["helix"]):
        spline = obj.data.splines[0]
        for step, point in enumerate(spline.points):
            t = step / (len(spline.points) - 1)
            x = -1.4 + t * 4.0
            angle = t * math.tau * 3.15 + strand * math.pi + phase
            radius = 0.30 + t * 0.24
            point.co = (x, math.cos(angle) * radius, math.sin(angle) * radius, 1.0)


def render_projectile() -> list[str]:
    reset_scene()
    configure(1024, 320, 10.8, (0, -10.8, 4.1), (0.25, 0, 0))
    state = setup_projectile()
    output = OUT / "projectile"
    output.mkdir(parents=True, exist_ok=True)
    paths = []
    for frame in range(FRAMES):
        update_projectile(state, frame)
        path = output / f"ASTER_COIL_PROJECTILE_V4_{frame:02d}.png"
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path.relative_to(ROOT).as_posix())
    return paths


def setup_impact() -> dict[str, object]:
    white = material("Impact core", (1, 0.92, 0.62, 1), roughness=0.05, emission=(1, 0.75, 0.22, 1), strength=32)
    orange = material("Impact plasma", (0.85, 0.08, 0.003, 1), roughness=0.1, emission=(1, 0.105, 0.004, 1), strength=15)
    cyan = material("Impact refraction", (0.015, 0.33, 0.48, 1), roughness=0.1, emission=(0.01, 0.62, 1, 1), strength=13)
    metal = material("Impact fragment metal", (0.24, 0.07, 0.014, 1), metallic=0.9, roughness=0.18)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=0.48, location=(0, 0, 0.32))
    core = assign(bpy.context.object, white)
    core.name = "Compressed impact core"
    ring = torus("Ground shock ring", 0, 1.05, 0.055, orange)
    ring.rotation_euler = (0, 0, 0)
    ring.location.z = 0.04
    cyan_ring = torus("Cyan refraction ring", 0, 0.78, 0.025, cyan)
    cyan_ring.location.z = 0.09

    rng = random.Random(9951)
    shards = []
    rays = []
    for index in range(28):
        angle = rng.uniform(-math.pi * 0.72, math.pi * 0.72)
        distance = rng.uniform(0.85, 2.65)
        z = rng.uniform(0.08, 0.75)
        bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=rng.uniform(0.045, 0.11), radius2=0.0, depth=rng.uniform(0.28, 0.75), location=(math.cos(angle) * distance, math.sin(angle) * distance, z))
        obj = assign(bpy.context.object, metal if index % 3 else orange)
        obj.rotation_euler = (rng.uniform(-0.9, 0.9), angle + math.pi / 2, rng.uniform(-math.pi, math.pi))
        obj["base_location"] = tuple(obj.location)
        obj["base_scale"] = tuple(obj.scale)
        shards.append(obj)
    for index in range(20):
        angle = rng.uniform(-math.pi * 0.74, math.pi * 0.74)
        length = rng.uniform(1.2, 3.2)
        start = rng.uniform(0.12, 0.42)
        points = [(math.cos(angle) * start, math.sin(angle) * start, 0.2), (math.cos(angle) * length, math.sin(angle) * length, rng.uniform(0.05, 0.5))]
        ray = poly_curve(f"Impact ray {index}", points, 0.018 if index % 4 else 0.035, orange if index % 5 else cyan)
        ray["base_scale"] = tuple(ray.scale)
        rays.append(ray)
    add_area_light("Impact warm", (-1.5, -3, 5), (1, 0.13, 0.02), 1350, 4.0, (0, 0, 0))
    add_area_light("Impact cyan", (2.4, 1.4, 3.2), (0.01, 0.5, 1), 700, 3.0, (0, 0, 0))
    return {"core": core, "ring": ring, "cyan_ring": cyan_ring, "shards": shards, "rays": rays}


def update_impact(state: dict[str, object], frame: int) -> None:
    progress = frame / (FRAMES - 1)
    fade = max(0.04, (1.0 - progress) ** 0.75)
    state["core"].scale = Vector((1.0, 1.0, 1.0)) * (1.2 - progress * 0.92)
    state["ring"].scale = Vector((1.0, 1.0, 0.35)) * (0.48 + progress * 2.65)
    state["cyan_ring"].scale = Vector((1.0, 1.0, 0.35)) * (0.35 + progress * 2.15)
    for index, obj in enumerate(state["shards"]):
        base = Vector(obj["base_location"])
        obj.location = base * (0.32 + progress * 1.28)
        obj.scale = Vector(obj["base_scale"]) * fade * (0.82 + 0.18 * math.sin(frame + index))
        obj.hide_render = frame > 5 and index % 3 == 0
    for index, obj in enumerate(state["rays"]):
        obj.scale = Vector(obj["base_scale"]) * fade * (0.7 + progress * 0.75)
        obj.hide_render = frame > 5 and index % 2 == 0


def render_impact() -> list[str]:
    reset_scene()
    configure(640, 640, 8.1, (0, -8.8, 8.2), (0.55, 0, 0))
    state = setup_impact()
    output = OUT / "impact"
    output.mkdir(parents=True, exist_ok=True)
    paths = []
    for frame in range(FRAMES):
        update_impact(state, frame)
        path = output / f"ASTER_COIL_IMPACT_V4_{frame:02d}.png"
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path.relative_to(ROOT).as_posix())
    return paths


def main() -> int:
    if OUT.exists():
        raise SystemExit("refusing to overwrite current Blender V4 raw render")
    OUT.mkdir(parents=True)
    projectile = render_projectile()
    impact = render_impact()
    manifest = {"schema": 4, "blender_version": bpy.app.version_string, "headless": True, "external_models": False, "frames": FRAMES, "projectile": projectile, "impact": impact, "krea2_used": False}
    (OUT / "ASTER_COIL_VFX_V4_BLENDER_RAW_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("ASTER_COIL_VFX_V4_BLENDER_RAW=" + json.dumps(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
