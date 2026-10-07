"""Read saved neutral binding arrays; no edits, pose, render, or saved scene."""
import sys
from pathlib import Path
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g

out=Path(sys.argv[sys.argv.index('--')+1])
report_path=ROOT/'artifacts/quarantine/generation_diagnostics/mica_E_projected_neutral_r02/NEUTRAL_REPORT.json'
r=g.read(report_path)
bpy.ops.wm.open_mainfile(filepath=str(g.resolve(r['blend'])),load_ui=False)
mesh=bpy.data.objects[r['mesh_name']]
rig=bpy.data.objects[r['rig_name']]
if any(not bone.matrix_basis.is_identity for bone in rig.pose.bones):
    raise ValueError('SAVED_ACTUAL_NEUTRAL_REQUIRED')
evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
data=evaluated.to_mesh()
try:
    points=np.asarray([tuple(v.co) for v in data.vertices])[:r['visible_front_vertex_count']]
finally:
    evaluated.to_mesh_clear()
np.save(out/'ACTUAL_FRONT_POSITIONS_BLENDER.npy',points,allow_pickle=False)
g.write(out/'BINDING_INSPECTION.json',{'scope':'read-only native neutral surface inspection',
    'inputs':{'report':g.ref(report_path),'blend':r['blend'],'inspector':g.ref(__file__)},
    'actual_rest':r['actual_native_rest'],'actual_positions':g.ref(out/'ACTUAL_FRONT_POSITIONS_BLENDER.npy'),
    'production_ready':False})
