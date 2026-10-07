"""One raw import diagnostic; no rendering or saved model."""
import json
import sys
from pathlib import Path
import bpy
source, output = sys.argv[sys.argv.index("--")+1:]
root = Path(__file__).resolve().parents[2]
source, output = Path(source).resolve(), Path(output).resolve()
if not source.is_relative_to(root) or not output.is_relative_to(root) or output.exists():
    raise ValueError("FRESH_PROJECT_LOCAL_IMPORT_DIAGNOSTIC_REQUIRED")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source), import_pack_images=True)
rows = []
for obj in bpy.data.objects:
    rows.append({"name": obj.name, "type": obj.type, "users_scene": [s.name for s in obj.users_scene],
        "hide_render": obj.hide_render, "parent": obj.parent.name if obj.parent else None,
        "vertices": len(obj.data.vertices) if obj.type == "MESH" else None,
        "modifiers": [{"type": m.type, "object": getattr(m, "object", None).name if getattr(m, "object", None) else None} for m in obj.modifiers]})
output.write_text(json.dumps({"scene": bpy.context.scene.name,"objects": rows,
    "actions": [{"name": a.name,"frame_range": list(a.frame_range)} for a in bpy.data.actions]},indent=2), encoding="utf-8")
