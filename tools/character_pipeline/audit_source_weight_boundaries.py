"""Read actual neutral weights and failed evaluated vertices; never render/edit."""
import json
from pathlib import Path
import sys
import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import continuous_torso_weights as field

args = sys.argv[sys.argv.index('--')+1:]
surface = g.read(args[0]); pose = g.read(args[1]); profile = g.read(args[2])
config = g.read(g.resolve(surface['inputs']))
bpy.ops.wm.open_mainfile(filepath=str(g.resolve(surface['blend'])), load_ui=False)
mesh = bpy.data.objects[surface['mesh_name']]
uv = {}
for face in mesh.data.polygons:
    if face.material_index != 0:
        continue
    for loop in face.loop_indices:
        uv[mesh.data.loops[loop].vertex_index] = mesh.data.uv_layers.active.data[loop].uv.copy()
width, height = config['native_size']
mpp = config['metres_per_pixel']; cx, ground = config['ground_pixel']
invalid = []; arc = []; checked = 0
for index, coord in uv.items():
    x, y = float(coord.x)*width, (1.0-float(coord.y))*height
    weights = {mesh.vertex_groups[v.group].name: float(v.weight) for v in mesh.data.vertices[index].groups}
    if 740 < y < 840:
        checked += 1
        try:
            field.apply(y, weights, profile['torso_transition'])
        except ValueError as error:
            invalid.append({'source_xy': [x,y], 'weights': weights, 'error': str(error)})
    position = pose['actual_evaluated_vertices_m'][index]
    px, py = position[0]/mpp+cx, ground-position[2]/mpp
    if px > 820 and 700 < py < 1100:
        arc.append({'source_xy': [x,y], 'posed_xy': [px,py], 'weights': weights})
report = {'scope': 'read_only_actual_source_skin_weight_diagnostic',
          'surface': g.ref(args[0]), 'pose': g.ref(args[1]), 'profile': g.ref(args[2]),
          'transition_vertices_checked': checked, 'unrepresentable_unions': invalid,
          'outer_arc_vertices': sorted(arc, key=lambda row: -row['posed_xy'][0])[:24],
          'production_ready': False}
g.write(args[3], report)
print('transition vertices', checked, 'unrepresentable', len(invalid), 'arc', len(arc))
