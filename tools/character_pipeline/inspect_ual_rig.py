"""Read-only Blender inventory of the installed, project-local UAL armature."""
import json
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT / 'assets/external/quaternius/ual1/UAL1_Standard_RM.glb'))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
result = {'rig': rig.name, 'matrix': [list(r) for r in rig.matrix_world],
          'bones': {b.name: {'head': list(b.head_local), 'tail': list(b.tail_local),
                             'parent': b.parent.name if b.parent else None}
                    for b in rig.data.bones},
          'actions': {a.name: list(a.frame_range) for a in bpy.data.actions}}
print('UAL_RIG_INVENTORY ' + json.dumps(result))
