"""Read-only inspection renders of third-party models; never runtime/source art."""
from pathlib import Path
import json
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "renders"
OUT.mkdir(exist_ok=True)
selected = json.loads((ROOT / "shortlist.json").read_text(encoding="utf-8"))
receipts = []

for index, item in enumerate(selected):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.temporary_directory = str(ROOT / "tmp")
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.world = bpy.data.worlds.new("Inspection background")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.12, 0.15, 0.20, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
    scene.view_settings.view_transform = "AgX"
    bpy.ops.import_scene.gltf(filepath=item["local_path"])
    meshes = [o for o in scene.objects if o.type == "MESH"]
    corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lower = Vector([min(p[a] for p in corners) for a in range(3)])
    upper = Vector([max(p[a] for p in corners) for a in range(3)])
    center = (lower + upper) / 2
    extent = max(upper - lower)
    camera_data = bpy.data.cameras.new("Inspection orthographic camera")
    camera = bpy.data.objects.new("Inspection orthographic camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = center + Vector((4.5, -7.0, 5.0)).normalized() * extent * 5
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.clip_end = max(100, extent * 20)
    # Camera ortho_scale is image width; compute frame from actual view bounds.
    view = camera.matrix_world.inverted() if False else camera.rotation_euler.to_matrix().inverted()
    projected = [view @ (p - center) for p in corners]
    width = max(p.x for p in projected) - min(p.x for p in projected)
    height = max(p.y for p in projected) - min(p.y for p in projected)
    camera_data.ortho_scale = max(width, height * 1920 / 1080) * 1.17
    scene.camera = camera
    for name, offset, power, size in [("Key", (3, -4, 6), 600, 4), ("Fill", (-4, -1, 3), 220, 3), ("Rim", (1, 4, 5), 450, 3)]:
        light_data = bpy.data.lights.new(name, "AREA")
        light_data.energy = power * extent * extent
        light_data.shape = "DISK"
        light_data.size = size * extent
        light = bpy.data.objects.new(name, light_data)
        scene.collection.objects.link(light)
        light.location = center + Vector(offset) * extent
        light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
    output = OUT / f"{index + 1:02d}_{item['id']}.png"
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    receipts.append({"id": item["id"], "source_sha256": item["sha256"], "output": str(output),
                     "native_resolution": [1920, 1080], "render_engine": "Cycles CPU", "samples": 12,
                     "geometry_dimensions": list(upper - lower), "mesh_objects": len(meshes),
                     "image_dimensions": [{"name": i.name, "size": list(i.size)} for i in bpy.data.images if i.size[0] > 0],
                     "status": "INSPECTION_ONLY_NOT_PRODUCTION_APPROVAL"})
    (ROOT / "render_receipts.json").write_text(json.dumps(receipts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"KARCHIVE_RENDER_COMPLETE {index + 1}/{len(selected)} {item['id']}", flush=True)
