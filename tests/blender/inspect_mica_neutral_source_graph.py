"""Read the historical neutral material graph without changing its blend file."""
import argparse
from pathlib import Path
import sys

import bpy

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import collect_generation_mesh_preflight as collector


def main(neutral_arg,rgba_arg,out_arg):
    neutral=g.local(neutral_arg);rgba=g.local(rgba_arg);out=g.local(out_arg)
    if out.exists():raise ValueError('FRESH_NEUTRAL_GRAPH_DIAGNOSTIC_REQUIRED')
    before=g.sha(neutral);report=g.read(neutral)
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(report['blend'])),load_ui=False)
    mesh=bpy.data.objects[report['mesh_name']]
    materials=[]
    for slot,material in enumerate(mesh.data.materials):
        images=[] if not material or not material.use_nodes else [
            g.ref(Path(bpy.path.abspath(node.image.filepath))) for node in material.node_tree.nodes
            if node.type=='TEX_IMAGE' and node.image]
        materials.append({'slot':slot,'name':material.name if material else None,
            'nodes':sorted(node.type for node in material.node_tree.nodes) if material and material.use_nodes else [],
            'images':images,'exact_current_rgba_errors':collector._exact_source_front_material(material,rgba),
            'transparent_closure':collector._transparent_closure_material(material)})
    source=mesh.data.materials[0];texture=next(node for node in source.node_tree.nodes
                                                if node.type=='TEX_IMAGE' and node.image)
    texture.image.filepath=str(rgba);texture.image.reload()
    uv=source.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map=mesh.data.uv_layers.active.name
    source.node_tree.links.new(uv.outputs['UV'],texture.inputs['Vector'])
    exact_after_rebind=collector._exact_source_front_material(source,rgba)
    if exact_after_rebind:raise ValueError('STRICT_GRAPH_REBIND_NOT_IMPLEMENTABLE:'+','.join(exact_after_rebind))
    if g.sha(neutral)!=before:raise ValueError('READ_ONLY_NEUTRAL_BLEND_CHANGED')
    g.write(out,{'schema':1,'stage':'read_only_neutral_material_graph_diagnostic','production_ready':False,
        'neutral':g.ref(neutral),'current_rgba':g.ref(rgba),'materials':materials,
        'exact_rebound_source_graph_errors':exact_after_rebind,
        'neutral_blend_unchanged':True,'collector':g.ref(collector.__file__)})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--neutral',required=True);parser.add_argument('--rgba',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.neutral,args.rgba,args.out)
