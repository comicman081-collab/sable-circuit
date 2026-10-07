"""Exercise source-surface collector helpers inside the actual Blender API.

This produces only a synthetic technical fixture. It is not character art, not
a mesh candidate and never enters a runtime asset directory.
"""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import collect_generation_mesh_preflight as collector


def source_material(name,image,reverse=False,strength=1.0,recolour=False):
    material=bpy.data.materials.new(name);material.use_nodes=True
    nodes=material.node_tree.nodes;nodes.clear();links=material.node_tree.links
    output=nodes.new('ShaderNodeOutputMaterial');mix=nodes.new('ShaderNodeMixShader')
    transparent=nodes.new('ShaderNodeBsdfTransparent');emission=nodes.new('ShaderNodeEmission')
    texture=nodes.new('ShaderNodeTexImage');texture.image=image;uv=nodes.new('ShaderNodeUVMap')
    uv.uv_map='UVMap';emission.inputs['Strength'].default_value=strength
    links.new(uv.outputs['UV'],texture.inputs['Vector'])
    if recolour:
        rgb=nodes.new('ShaderNodeRGB');rgb.outputs['Color'].default_value=(.2,.8,.1,1)
        links.new(rgb.outputs['Color'],emission.inputs['Color'])
    else:
        links.new(texture.outputs['Color'],emission.inputs['Color'])
    links.new(texture.outputs['Alpha'],mix.inputs[0])
    links.new(emission.outputs[0],mix.inputs[1 if reverse else 2])
    links.new(transparent.outputs[0],mix.inputs[2 if reverse else 1])
    links.new(mix.outputs[0],output.inputs['Surface'])
    return material


def transparent_closure(name):
    material=bpy.data.materials.new(name);material.use_nodes=True
    nodes=material.node_tree.nodes;nodes.clear();links=material.node_tree.links
    out=nodes.new('ShaderNodeOutputMaterial');trans=nodes.new('ShaderNodeBsdfTransparent')
    links.new(trans.outputs[0],out.inputs['Surface']);return material


def opaque_closure(name):
    material=bpy.data.materials.new(name);material.use_nodes=True
    nodes=material.node_tree.nodes;nodes.clear();links=material.node_tree.links
    out=nodes.new('ShaderNodeOutputMaterial');principled=nodes.new('ShaderNodeBsdfPrincipled')
    links.new(principled.outputs[0],out.inputs['Surface']);return material


def bindings(left_pixel,right_pixel):
    return {'l':{'vertices':[[0,1,2]],'barycentric':[[1.,0.,0.]],'pixels':[left_pixel]},
            'r':{'vertices':[[3,4,5]],'barycentric':[[1.,0.,0.]],'pixels':[right_pixel]}}


def main(out_arg):
    out=g.local(out_arg)
    if out.exists():raise ValueError('FRESH_SYNTHETIC_QA_OUTPUT_REQUIRED')
    out.mkdir(parents=True);image_path=out/'SYNTHETIC_QA_RGBA.png'
    image=bpy.data.images.new('SyntheticSourceRGBA',4,4,alpha=True,float_buffer=False)
    pixels=np.zeros((4,4,4),dtype=np.float32)
    # Blender's buffer is bottom-up. Declared source pixels are top-down [x,y].
    pixels[4-1-1,1]=[.8,.2,.1,1.];pixels[4-1-1,2]=[.1,.7,.9,1.]
    image.pixels[:]=pixels.reshape(-1);image.filepath_raw=str(image_path);image.file_format='PNG';image.save()
    mesh=bpy.data.meshes.new('SourceSoleUVFixture')
    mesh.from_pydata([(0,0,0),(1,0,0),(0,1,0),(2,0,0),(3,0,0),(2,1,0)],[],[(0,1,2),(3,4,5)])
    uv=mesh.uv_layers.new(name='UVMap')
    for loop in mesh.polygons[0].loop_indices:uv.data[loop].uv=(.25,.75)
    for loop in mesh.polygons[1].loop_indices:uv.data[loop].uv=(.50,.75)
    ob=bpy.data.objects.new('SourceSoleUVFixture',mesh);bpy.context.collection.objects.link(ob)
    correct=source_material('CorrectSourceFront',image);mesh.materials.append(correct)
    good=collector._source_sole_uv_checks(mesh,{0},image_path,bindings([1,1],[2,1]),6)
    bad_opaque=collector._source_sole_uv_checks(mesh,{0},image_path,bindings([0,0],[2,1]),6)
    for loop in mesh.polygons[1].loop_indices:uv.data[loop].uv=(.25,.75)
    bad_left_right=collector._source_sole_uv_checks(mesh,{0},image_path,bindings([1,1],[1,1]),6)
    direct=collector._exact_source_front_material(correct,image_path)
    recolour=collector._exact_source_front_material(source_material('Recoloured',image,recolour=True),image_path)
    bright=collector._exact_source_front_material(source_material('Brightened',image,strength=20.),image_path)
    inverted=collector._exact_source_front_material(source_material('InvertedAlpha',image,reverse=True),image_path)
    normal_closure=collector._transparent_closure_material(transparent_closure('TransparentClosure'))
    opaque_closure_result=collector._transparent_closure_material(opaque_closure('OpaqueClosure'))
    if (good[1] or direct or not bad_opaque[1] or not bad_left_right[1] or not recolour or not bright or not inverted
            or not normal_closure or opaque_closure_result):
        raise ValueError('SOURCE_SURFACE_COLLECTOR_HELPER_REGRESSION')
    g.write(out/'COLLECTOR_HELPER_BLENDER_SMOKE.json',{
        'schema':1,'stage':'synthetic_blender_collector_helper_smoke','verdict':'PASS_TECHNICAL_HELPERS_ONLY',
        'synthetic_qa_not_production':True,'source_image':g.ref(image_path),
        'normal_direct_source_graph_errors':direct,'normal_transparent_closure':normal_closure,
        'opaque_principled_closure_rejected':not opaque_closure_result,
        'recolour_graph_errors':recolour,'emission_strength_counterexample_errors':bright,
        'alpha_order_counterexample_errors':inverted,'opaque_pixel_counterexample_errors':bad_opaque[1],
        'left_right_distinct_counterexample_errors':bad_left_right[1],
        'collector':g.ref(collector.__file__),'production_ready':False})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    main(parser.parse_args(sys.argv[sys.argv.index('--')+1:]).out)
