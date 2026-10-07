"""One-view implementation probe for an original-art carrying skinned surface.

The image defines the entire visible surface. No generic body, replacement
face/costume, texture swatches, mirrored art, or missing-pixel filling is used.
Unobserved closure faces are transparent. They are NOT approved hidden artwork.
Only a neutral preservation probe is emitted; motion and eight-view use require
separate review of this new adapter and exact source coverage.
"""
from __future__ import annotations
import argparse
from collections import Counter, deque
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
import generation_harness as g
import surface_region_topology as topology

SOURCE = ROOT / 'art_src/characters/mica/rigged_v2/source_front_r1'


def split_vertex_fans(vertices, uvs, faces):
    """Separate silhouette cells that touch at only one grid corner.

    Otherwise two independent closure walls meet on one vertical edge and the
    resulting volume has four faces on that edge. No source UV/pixel is changed.
    """
    incidence = [[] for _ in vertices]
    mutable = [list(face) for face in faces]
    for index, face in enumerate(faces):
        for vertex in face: incidence[vertex].append(index)
    for vertex, adjacent in enumerate(incidence):
        unseen = set(adjacent); components = []
        while unseen:
            connected = {unseen.pop()}; pending = list(connected)
            while pending:
                first = pending.pop()
                for other in list(unseen):
                    if len(set(faces[first]).intersection(faces[other])) >= 2:
                        unseen.remove(other); connected.add(other); pending.append(other)
            components.append(connected)
        for component in components[1:]:
            new = len(vertices); vertices.append(vertices[vertex]); uvs.append(uvs[vertex])
            for face in component:
                mutable[face] = [new if old == vertex else old for old in mutable[face]]
    return [tuple(face) for face in mutable]


def edge_only_matte(rgb):
    """The same source-to-alpha operation runs before and inside Blender."""
    import numpy as np
    values = rgb.astype(np.int16)
    family = ((values[:, :, 1] >= 12) & (values[:, :, 1] - values[:, :, 0] >= 16)
              & (values[:, :, 1] - values[:, :, 2] >= 16)
              & (values[:, :, 1] * 4 >= values[:, :, 0] * 5)
              & (values[:, :, 1] * 4 >= values[:, :, 2] * 5))
    background = np.zeros(family.shape,dtype=bool)
    background[0]=family[0];background[-1]=family[-1]
    background[:,0]=family[:,0];background[:,-1]=family[:,-1]
    queue=deque(map(tuple,np.argwhere(background)))
    height,width=family.shape
    while queue:
        y,x=queue.popleft()
        for ny,nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0<=ny<height and 0<=nx<width and family[ny,nx] and not background[ny,nx]:
                background[ny,nx]=True;queue.append((ny,nx))
    return background


def inside_polygon(x,y,polygon):
    inside=False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return inside


def prepare(out, profile_path):
    import numpy as np
    from PIL import Image
    from scipy.ndimage import distance_transform_edt

    profile = g.read(profile_path)
    receipt = g.resolve(profile['source_receipt'])
    authority = g.source_authority(receipt)
    image_path = g.resolve(profile['source'])
    rgb = np.asarray(Image.open(image_path).convert('RGB'))
    background = edge_only_matte(rgb)
    alpha = (~background).astype(np.uint8) * 255
    rgba = np.dstack((rgb, alpha))
    # RGB is preserved even underneath transparent pixels, enabling direct
    # source-byte comparison without any ambiguity about visual reauthoring.
    Image.fromarray(rgba).save(out / 'SOURCE_RGBA.png')
    Image.fromarray(alpha).save(out / 'VISIBLE_SOURCE_MASK.png')
    depth = distance_transform_edt(alpha > 0)
    np.save(out / 'SURFACE_DEPTH.npy', depth.astype(np.float32), allow_pickle=False)
    annotation = g.read(g.resolve(profile['annotation']))
    config = {'source_receipt': g.ref(receipt), 'source': g.ref(image_path),
        'annotation': profile['annotation'], 'profile': g.ref(profile_path),
        'rgba': g.ref(out / 'SOURCE_RGBA.png'), 'mask': g.ref(out / 'VISIBLE_SOURCE_MASK.png'),
        'depth': g.ref(out / 'SURFACE_DEPTH.npy'), 'native_size': [rgb.shape[1], rgb.shape[0]],
        'metres_per_pixel': annotation['metres_per_pixel'], 'ground_pixel': annotation['points']['ground'],
        'grid_pixels': 8, 'max_surface_depth_m': .065,
        'source_rgb_byte_exact': bool(np.array_equal(rgba[:, :, :3], rgb)),
        'matte_scope': 'Only image-edge-connected green; interior costume pixels retained.',
        'source_authority_bindings': authority['bindings'],
        'scope': profile['direction'] + '_NEUTRAL_ADAPTER_IMPLEMENTATION_PROBE_ONLY',
        'production_ready': False}
    g.write(out / 'SURFACE_INPUTS.json', config)


def child(args):
    import bpy
    import numpy as np
    from mathutils import Vector

    out = g.local(args.out)
    inputs = g.read(out / 'INPUTS.json')
    for reference in inputs.values(): g.resolve(reference)
    if inputs['builder'] != g.ref(__file__): raise ValueError('EXACT_BUILDER_REQUIRED')
    config = g.read(g.resolve(inputs['surface']))
    for key in ('source_receipt', 'source', 'annotation', 'rgba', 'mask', 'depth'): g.resolve(config[key])
    authority = g.source_authority(g.resolve(config['source_receipt']))
    views = [view for source in authority['sources'] for view in source['views']]
    if not any(view['id']==g.read(g.resolve(config['profile']))['direction'] and view['image']==config['source'] and view['annotations']==config['annotation'] for view in views):
        raise ValueError('EXACT_APPROVED_SOURCE_AND_ANNOTATION_REQUIRED')
    if config['source_authority_bindings'] != authority['bindings']:
        raise ValueError('SOURCE_AUTHORITY_CHANGED')
    annotation = g.read(g.resolve(config['annotation']))
    if (config['metres_per_pixel'] != annotation['metres_per_pixel'] or
            config['ground_pixel'] != annotation['points']['ground']):
        raise ValueError('SOURCE_SCALE_AND_GROUND_CHANGED')
    g.write(out / 'CHILD_CLAIM.json', {'inputs': g.ref(out / 'INPUTS.json')})
    bpy.ops.wm.read_factory_settings(use_empty=True)
    profile = g.read(g.resolve(config['profile']))
    if profile['source'] != config['source'] or profile['source_receipt'] != config['source_receipt'] or profile['annotation'] != config['annotation']:
        raise ValueError('EXACT_CHARACTER_PROFILE_SOURCE_REQUIRED')
    if profile['actor_id'] != authority['actor_id'] or profile['costume_id'] != authority['costume_id']:
        raise ValueError('CROSS_CHARACTER_PROFILE_FORBIDDEN')
    width, height = config['native_size']
    step = config['grid_pixels']; mpp = config['metres_per_pixel']
    cx, ground = config['ground_pixel']
    depth = np.load(g.resolve(config['depth']), allow_pickle=False)
    original = g.pixels(g.resolve(config['source']))
    pixels = g.pixels(g.resolve(config['rgba']))
    mask = g.pixels(g.resolve(config['mask']))
    if (original.shape != (height,width,4) or pixels.shape != original.shape or mask.shape != original.shape
            or not np.array_equal(original[:,:,:3],pixels[:,:,:3])
            or not set(np.unique(pixels[:,:,3])).issubset({0,255})
            or not np.array_equal(mask[:,:,0],pixels[:,:,3])
            or not np.array_equal(mask[:,:,:3],np.repeat(mask[:,:,:1],3,axis=2))):
        raise ValueError('SOURCE_RGB_OR_ALPHA_MASK_RELATIONSHIP_FAILED')
    alpha = pixels[:,:,3] > 0
    if not np.array_equal(alpha,~edge_only_matte(original[:,:,:3])):
        raise ValueError('ALPHA_IS_NOT_EXACT_SOURCE_EDGE_CONNECTED_MATTE')
    if depth.shape != alpha.shape or not np.isfinite(depth).all() or np.any(depth[~alpha] != 0) or np.any(depth[alpha] <= 0):
        raise ValueError('SOURCE_SILHOUETTE_DEPTH_RELATIONSHIP_FAILED')
    source_image = bpy.data.images.load(str(g.resolve(config['rgba'])), check_existing=False)
    vertices = []; uv_points = []; front_faces = []; vertex_index = {}
    xs = list(range(0, width, step)) + [width]
    ys = list(range(0, height, step)) + [height]

    compiled_regions=topology.compile_regions(profile.get('weight_regions',[]))

    def vertex(x, y, region):
        key = (x, y, region)
        if key not in vertex_index:
            vertex_index[key] = len(vertices)
            # Depth is a deformation support inferred from source silhouette;
            # it is never colored as newly invented side/back appearance.
            px,py=min(round(x),width-1),min(round(y),height-1)
            radius=int(np.ceil(config['max_surface_depth_m']/mpp))
            y0,y1=max(0,py-radius),min(height,py+radius+1)
            x0,x1=max(0,px-radius),min(width,px+radius+1)
            background_y,background_x=np.where(~alpha[y0:y1,x0:x1])
            actual_distance=(float(np.sqrt(np.min((background_x+x0-px)**2+(background_y+y0-py)**2)))
                             if len(background_x) else radius)
            d = min(config['max_surface_depth_m'], float(depth[py,px]) * mpp)
            if abs(d-min(config['max_surface_depth_m'],actual_distance*mpp))>1e-7:
                raise ValueError('CONSUMED_SURFACE_DEPTH_NOT_FROM_SOURCE_SILHOUETTE')
            vertices.append(((x-cx)*mpp, -d, (ground-y)*mpp))
            uv_points.append((x/width, 1-y/height, region))
        return vertex_index[key]

    pieces=[]
    for y0, y1 in zip(ys, ys[1:]):
        for x0, x1 in zip(xs, xs[1:]):
            if not alpha[y0:y1, x0:x1].any(): continue
            pieces.extend(topology.partition_cell(x0,y0,x1,y1,compiled_regions))
    for region,triangle in topology.conforming_triangles(pieces,step):
        ids=[vertex(x,y,region) for x,y in triangle]
        front_faces.append(tuple(reversed(ids)))
    front_faces = split_vertex_fans(vertices,uv_points,front_faces)
    count = len(vertices)
    back_vertices = [(x, max(.008, -y), z) for x,y,z in vertices]
    faces = list(front_faces) + [tuple(i+count for i in reversed(face)) for face in front_faces]
    edge_counts = Counter(tuple(sorted((a,b))) for face in front_faces for a,b in zip(face, face[1:]+face[:1]))
    for (a,b), uses in edge_counts.items():
        if uses == 1: faces.append((a,b,b+count,a+count))
    mesh = bpy.data.meshes.new('OriginalArtContinuousSurface')
    mesh.from_pydata(vertices+back_vertices, [], faces); mesh.update()
    carrier = bpy.data.objects.new(profile['actor_id']+'_SourceSurface_'+profile['direction'], mesh)
    bpy.context.collection.objects.link(carrier)
    uv = mesh.uv_layers.new(name='ExactSourcePixels')
    for polygon in mesh.polygons:
        for loop in polygon.loop_indices:
            uv.data[loop].uv = uv_points[mesh.loops[loop].vertex_index % count][:2]
    material = bpy.data.materials.new('ApprovedSourceImageOnly'); material.use_nodes = True
    nodes = material.node_tree.nodes; nodes.clear()
    texture = nodes.new('ShaderNodeTexImage'); texture.image = source_image; texture.interpolation = 'Closest'
    emission = nodes.new('ShaderNodeEmission'); transparent = nodes.new('ShaderNodeBsdfTransparent')
    mix = nodes.new('ShaderNodeMixShader'); output = nodes.new('ShaderNodeOutputMaterial')
    links = material.node_tree.links
    links.new(texture.outputs['Color'],emission.inputs['Color'])
    links.new(texture.outputs['Alpha'],mix.inputs[0])
    links.new(transparent.outputs[0],mix.inputs[1]); links.new(emission.outputs[0],mix.inputs[2])
    links.new(mix.outputs[0],output.inputs['Surface'])
    closure = bpy.data.materials.new('UnobservedClosure_NoArtwork'); closure.use_nodes = True
    closure.node_tree.nodes.clear()
    trans = closure.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    output2 = closure.node_tree.nodes.new('ShaderNodeOutputMaterial')
    closure.node_tree.links.new(trans.outputs[0],output2.inputs['Surface'])
    carrier.data.materials.append(material); carrier.data.materials.append(closure)
    for polygon in mesh.polygons: polygon.material_index = 0 if polygon.index < len(front_faces) else 1
    # Anatomical landmarks locate a new deformation rig. They never define or
    # replace the visible costume and face, which remain the complete source.
    points = {name:tuple(point) for name,point in profile['bone_points_px'].items()}
    parents = {'pelvis':None,'spine_01':'pelvis','spine_02':'spine_01','spine_03':'spine_02',
               'neck_01':'spine_03','Head':'neck_01'}
    for side in ('l','r'):
        parents.update({f'thigh_{side}':'pelvis',f'calf_{side}':f'thigh_{side}',f'foot_{side}':f'calf_{side}',
                        f'ball_{side}':f'foot_{side}',f'clavicle_{side}':'spine_03',f'upperarm_{side}':f'clavicle_{side}',
                        f'lowerarm_{side}':f'upperarm_{side}',f'hand_{side}':f'lowerarm_{side}'})
    tails = {'pelvis':'spine_01','spine_01':'spine_02','spine_02':'spine_03','spine_03':'neck_01','neck_01':'Head'}
    for side in ('l','r'):
        tails.update({f'thigh_{side}':f'calf_{side}',f'calf_{side}':f'foot_{side}',f'foot_{side}':f'ball_{side}',
                      f'clavicle_{side}':f'upperarm_{side}',f'upperarm_{side}':f'lowerarm_{side}',f'lowerarm_{side}':f'hand_{side}'})
    def world(point): return Vector(((point[0]-cx)*mpp,0,(ground-point[1])*mpp))
    rig_data = bpy.data.armatures.new('ReusableHumanoidBinding')
    rig = bpy.data.objects.new(profile['actor_id']+'_SourceRig',rig_data); bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig; rig.select_set(True); bpy.ops.object.mode_set(mode='EDIT')
    for name, point in points.items():
        bone = rig_data.edit_bones.new(name); bone.head = world(point)
        bone.tail = world(points[tails[name]]) if name in tails else bone.head + Vector((0,0,.07))
    for name, parent in parents.items():
        if parent: rig_data.edit_bones[name].parent = rig_data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    names = list(points)
    for name in names: carrier.vertex_groups.new(name=name)
    # Smooth spatial weights on the continuous source surface. The neutral
    # probe does not approve moving coat/limb ownership; that is measured next.
    segments = [(world(points[name]),world(points[tails[name]]) if name in tails else world(points[name])+Vector((0,0,.07))) for name in names]
    for i, co in enumerate(vertices):
        position = Vector(co)
        distances = []
        for a,b in segments:
            t = max(0.,min(1.,(position-a).dot(b-a)/(b-a).length_squared))
            distances.append(max(.008,(position-(a+(b-a)*t)).length))
        region=uv_points[i][2]
        allowed=set(profile['weight_regions'][region]['bones']) if region>=0 else set(names)
        if not allowed or not allowed.issubset(names):raise ValueError('VALID_SEMANTIC_BONE_REGION_REQUIRED')
        nearest = sorted([n for n,name in enumerate(names) if name in allowed],key=lambda n:distances[n])[:4]
        raw = [1/distances[n]**4 for n in nearest]; total = sum(raw)
        for n, weight in zip(nearest,raw): carrier.vertex_groups[n].add([i,i+count],weight/total,'REPLACE')
    modifier = carrier.modifiers.new('ContinuousSurfaceSkin','ARMATURE'); modifier.object=rig
    carrier['source_image_sha256'] = config['source']['sha256']
    carrier['visible_surface_authority'] = 'Exact full ImageGen source; no newly colored closure faces'
    scene = bpy.context.scene
    camera = bpy.data.objects.new('SourceLockedCamera',bpy.data.cameras.new('SourceLockedCamera'))
    bpy.context.collection.objects.link(camera); scene.camera = camera
    center = Vector(((width*.5-cx)*mpp,0,(ground-height*.5)*mpp))
    camera.location = center + Vector((0,-6,0)); camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'; camera.data.ortho_scale=1920*mpp
    scene.render.engine='CYCLES'; scene.cycles.samples=1; scene.cycles.use_denoising=False
    scene.render.resolution_x=1920; scene.render.resolution_y=1920; scene.render.resolution_percentage=100
    scene.render.film_transparent=True; scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'
    scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
    scene.render.threads_mode='FIXED'; scene.render.threads=2
    scene.render.filepath=str(out/'NEUTRAL_SOURCE_PRESERVATION_1920.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'SOURCE_SURFACE_NEUTRAL.blend'))
    counts = Counter(tuple(sorted((a,b))) for face in faces for a,b in zip(face,face[1:]+face[:1]))
    g.write(out/'SURFACE_REPORT.json',{'scope':config['scope'],'production_ready':False,
        'inputs':g.ref(out/'SURFACE_INPUTS.json'),'builder':g.ref(__file__),
        'blend':g.ref(out/'SOURCE_SURFACE_NEUTRAL.blend'),
        'render':g.ref(out/'NEUTRAL_SOURCE_PRESERVATION_1920.png'),
        'profile':config['profile'],'rig_name':rig.name,'mesh_name':carrier.name,
        'vertices':len(mesh.vertices),'faces':len(faces),'bones':len(names),
        'closed_edge_incidence':all(value==2 for value in counts.values()),
        'source_uv_mapping':'front u=x/source_width,v=1-y/source_height; exact source RGB',
        'semantic_topology_boundaries_split':True,'front_triangles_cross_semantic_regions':sum(len({uv_points[v][2] for v in face})!=1 for face in front_faces),
        'unobserved_closure_visible':False,'native_render_size':[1920,1920],
        'motion_approved':False,'all_directions_approved':False})


def run(args):
    out = g.local(args.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('IMPLEMENTATION_DIAGNOSTIC_ROOT_REQUIRED')
    out.mkdir(parents=True,exist_ok=False); (out/'cache').mkdir()
    prepare(out,args.profile)
    g.write(out/'INPUTS.json',{'builder':g.ref(__file__),'surface':g.ref(out/'SURFACE_INPUTS.json'),
        'generation_harness':g.ref(ROOT/'tools/character_pipeline/generation_harness.py'),
        'semantic_topology':g.ref(topology.__file__)})
    env = os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'): env[key]=str(out/'cache')
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',OMP_NUM_THREADS='2')
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup',
        '--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2',
        '--python',str(Path(__file__).resolve()),'--','--inside','--out',str(out)]
    with (out/'blender.log').open('w',encoding='utf8') as log:
        process=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
            timeout=240,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if process.returncode: raise ValueError('SOURCE_SURFACE_PROBE_FAILED:'+str(out/'blender.log'))
    print('NEUTRAL_SURFACE_PROBE_CREATED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--out',required=True)
    parser.add_argument('--profile');parser.add_argument('--inside',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(args) if args.inside else run(args)
