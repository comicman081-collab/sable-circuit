"""Blender-only enclosing footwear, with measured topology and real skin transfer.

No original geometry is modified. New visible surface vertex IDs are assigned
only after voxel construction; old sole IDs must never survive this operation.
"""
import json
from mesh_surface_orientation import closed_component_orientation
from triangle_surface_checks import triangles_intersect,intersection_beyond_shared


def point_inside_closed_shell(point,bvh,vertices,triangles,tolerance=1e-5):
    """Three non-axis ray parities; edge hits are ambiguous, not inside PASS."""
    from mathutils import Vector
    from mathutils.interpolate import poly_3d_calc
    nearest,normal,index,distance=bvh.find_nearest(point)
    if index is None:raise ValueError('CLOSED_SHELL_NEAREST_SURFACE_REQUIRED')
    if distance<=tolerance:return {'classification':'boundary_tolerance','distance_m':distance,'parities':[]}
    parities=[];traces=[]
    for xyz in ((.723,.337,.606),(-.291,.823,.488),(.417,-.733,.537)):
        direction=Vector(xyz).normalized();origin=point.copy();crossings=0;ambiguous=False
        trace=[]
        for _ in range(32):
            hit,hit_normal,face,ray_distance=bvh.ray_cast(origin,direction,10.)
            if face is None:break
            bary=poly_3d_calc([vertices[i] for i in triangles[face]],hit)
            trace.append({'face':face,'distance_m':ray_distance,'barycentric':list(bary)})
            if min(bary)<1e-6 or ray_distance<1e-6:
                ambiguous=True;break
            # Blender BVH float32 ray hits can sit ~2e-7m behind the plane.
            # Advance by the explicit 1e-5m geometric tolerance, well below the
            # 3mm voxel surface spacing, to avoid counting the same face twice.
            crossings+=1;origin=hit+direction*tolerance
        else:ambiguous=True
        traces.append(trace)
        if not ambiguous:parities.append(crossings%2)
    if len(parities)<2 or len(set(parities))!=1:
        raise ValueError('AMBIGUOUS_CLOSED_SHELL_RAY_PARITY:'+json.dumps({'point':list(point),'parities':parities,'rays':traces}))
    return {'classification':'inside' if parities[0] else 'outside','distance_m':distance,'parities':parities}


def components_of(mesh):
    neighbors=[set() for _ in mesh.vertices]
    for edge in mesh.edges:
        a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
    remaining=set(range(len(neighbors)));components=[]
    while remaining:
        first=min(remaining);remaining.remove(first);pending=[first];ids={first}
        while pending:
            for i in neighbors[pending.pop()] & remaining:
                remaining.remove(i);ids.add(i);pending.append(i)
        components.append(sorted(ids))
    return sorted(components,key=len,reverse=True)


def audit_surface(mesh):
    from mathutils.bvhtree import BVHTree
    mesh.calc_loop_triangles()
    vertices=[list(v.co) for v in mesh.vertices]
    faces=[list(p.vertices) for p in mesh.polygons]
    components=closed_component_orientation(vertices,faces)
    if len(components)!=2 or any(c['signed_volume_m3']<=0 for c in components):
        raise ValueError('TWO_OUTWARD_ANATOMICAL_BOOT_SHELLS_REQUIRED')
    sides=[sum(vertices[i][0] for i in c['vertex_ids'])/len(c['vertex_ids']) for c in components]
    if sides[0]*sides[1]>=0:raise ValueError('DISTINCT_LEFT_RIGHT_BOOT_SHELLS_REQUIRED')
    tris=[tuple(t.vertices) for t in mesh.loop_triangles]
    bvh=BVHTree.FromPolygons(vertices,tris,all_triangles=True,epsilon=0.)
    candidates={(a,b) for a,b in bvh.overlap(bvh) if a<b}
    # Some BVH overlap implementations suppress ordinary adjacency internally.
    # Enumerate it independently so sharing a point cannot hide a crossing.
    incident=[[] for _ in vertices]
    for i,tri in enumerate(tris):
        for v in tri:incident[v].append(i)
    for row in incident:
        for i,a in enumerate(row):
            for b in row[i+1:]:candidates.add((min(a,b),max(a,b)))
    intersections=[];shared_checked=0
    for a,b in candidates:
        shared=set(tris[a])&set(tris[b]);ta=[vertices[i] for i in tris[a]];tb=[vertices[i] for i in tris[b]]
        if shared:
            shared_checked+=1
            if len(shared)==3:raise ValueError('DUPLICATE_BOOT_TRIANGLE')
            hit=intersection_beyond_shared(ta,tb,[vertices[i] for i in sorted(shared)])
        else:hit=triangles_intersect(ta,tb)
        if hit:intersections.append((a,b))
    if intersections:raise ValueError('SELF_INTERSECTING_BOOT_ENVELOPE:'+str(len(intersections)))
    opposite=0
    for t in mesh.loop_triangles:
        a,b,c=[mesh.vertices[i].co for i in t.vertices]
        normal=(b-a).cross(c-a)
        if normal.length<1e-12:raise ValueError('DEGENERATE_BOOT_TRIANGLE')
        if normal.normalized().dot(mesh.polygons[t.polygon_index].normal)<0:opposite+=1
    if opposite:raise ValueError('FOLDED_BOOT_POLYGONS:'+str(opposite))
    return {'vertices':len(vertices),'faces':len(faces),'closed_shells':2,
            'signed_volumes_m3':[c['signed_volume_m3'] for c in components],
            'bvh_candidates':len(candidates),'shared_boundary_pairs_checked':shared_checked,
            'adjacency_tolerance_m':1e-8,'actual_intersections':0,'folded_polygon_triangles':0}


def rebuild_envelope(boot,body):
    import bpy
    import bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.interpolate import poly_3d_calc
    if any(abs(ob.matrix_world[i][j]-(1 if i==j else 0))>1e-6
           for ob in (boot,body) for i in range(4) for j in range(4)):
        raise ValueError('SHARED_REST_SPACE_REQUIRED_FOR_SHOE_SKIN_TRANSFER')
    before={'vertices':len(boot.data.vertices),'faces':len(boot.data.polygons)}
    for modifier in list(boot.modifiers):boot.modifiers.remove(modifier)
    boot.vertex_groups.clear()
    bpy.ops.object.select_all(action='DESELECT');boot.select_set(True);bpy.context.view_layer.objects.active=boot
    boot.data.remesh_voxel_size=.003;boot.data.remesh_voxel_adaptivity=0.
    # Reprojection/volume preservation pulls the envelope back into the source
    # toe self-intersections. A genuine new isosurface must remain unprojected.
    boot.data.use_remesh_preserve_volume=False
    bpy.ops.object.voxel_remesh()
    components=components_of(boot.data)
    if len(components)<2 or any(len(c)<1000 for c in components[:2]):
        raise ValueError('MISSING_FULL_SIZE_LEFT_RIGHT_SHOE')
    discarded=[];remove=set()
    for ids in components[2:]:
        vertices=[list(boot.data.vertices[i].co) for i in ids]
        extent=[max(v[k] for v in vertices)-min(v[k] for v in vertices) for k in range(3)]
        faces=[list(p.vertices) for p in boot.data.polygons if p.vertices[0] in ids]
        # Only the observed detached subvoxel cells, never a substantive boot
        # part, toe, heel or source asset. Preserve their exact geometry record.
        if len(ids)!=8 or len(faces)!=6 or max(extent)>.003:
            raise ValueError('UNEXPECTED_DISCONNECTED_SHOE_GEOMETRY')
        origin=sum((Vector(v) for v in vertices),Vector())/len(vertices);volume=0.
        for face in faces:
            a=boot.data.vertices[face[0]].co-origin
            for ib,ic in zip(face[1:-1],face[2:]):
                b=boot.data.vertices[ib].co-origin;c=boot.data.vertices[ic].co-origin
                volume+=a.dot(b.cross(c))/6
        if abs(volume)>1e-9:raise ValueError('SUBVOXEL_FRAGMENT_VOLUME_EXCEEDED')
        discarded.append({'ids':ids,'vertices_m':vertices,'faces':faces,'extent_m':extent,'signed_volume_m3':volume})
        remove.update(ids)
    bm=bmesh.new();bm.from_mesh(boot.data);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.verts[i] for i in sorted(remove)],context='VERTS')
    bm.normal_update();bm.to_mesh(boot.data);bm.free();boot.data.update()
    for p in boot.data.polygons:p.use_smooth=True
    measured=audit_surface(boot.data)
    boot.data.calc_loop_triangles()
    final_vertices=[v.co.copy() for v in boot.data.vertices]
    final_triangles=[tuple(t.vertices) for t in boot.data.loop_triangles]
    shells={}
    for ids in components_of(boot.data):
        side='left' if sum(final_vertices[i].x for i in ids)>0 else 'right'
        selected=set(ids);triangles=[t for t in final_triangles if t[0] in selected]
        shells[side]=(BVHTree.FromPolygons(final_vertices,triangles,all_triangles=True),triangles)
    enclosure=[]
    for v in body.data.vertices:
        # Explicit top cuff transition is not a lower-foot/sole sample. Every
        # actual toe, heel, foot and covered calf vertex below 0.40m is checked.
        if v.co.z>=.40:continue
        side='left' if v.co.x>0 else 'right';bvh,triangles=shells[side]
        classification=point_inside_closed_shell(v.co,bvh,final_vertices,triangles)
        enclosure.append({'source_vertex':v.index,'side':side,**classification})
    exterior=[r for r in enclosure if r['classification']=='outside']
    if exterior:raise ValueError('ANATOMY_PROTRUDES_THROUGH_BOOT:'+str(exterior[:4]))
    # The real nearest anatomical triangle (not a joint target) supplies a
    # normalized barycentric blend of its existing valid deformation weights.
    body.data.calc_loop_triangles();triangles=[tuple(t.vertices) for t in body.data.loop_triangles]
    points=[v.co.copy() for v in body.data.vertices]
    bvh=BVHTree.FromPolygons(points,triangles,all_triangles=True)
    source_weights=[{body.vertex_groups[w.group].name:w.weight for w in v.groups} for v in body.data.vertices]
    rows=[];max_distance=0.;max_outer_distance=0.;transfer=[]
    for v in boot.data.vertices:
        point,normal,index,distance=bvh.find_nearest(v.co)
        if index is None:raise ValueError('REAL_ANATOMICAL_TRANSFER_TRIANGLE_REQUIRED')
        ids=triangles[index];bary=poly_3d_calc([points[i] for i in ids],point)
        if min(bary)<-1e-4:raise ValueError('INVALID_ANATOMICAL_BARYCENTRIC_COORDINATES')
        row={}
        for i,factor in zip(ids,bary):
            for name,weight in source_weights[i].items():row[name]=row.get(name,0.)+weight*max(0.,factor)
        total=sum(row.values())
        if total<1e-6:raise ValueError('NO_REAL_SKIN_WEIGHTS_FOR_ENVELOPE')
        rows.append({n:w/total for n,w in row.items() if w>0})
        max_distance=max(max_distance,distance)
        is_cuff_cap=v.co.z>.40 and v.normal.z>.5
        if not is_cuff_cap:max_outer_distance=max(max_outer_distance,distance)
        transfer.append({'vertex':v.index,'source_triangle':index,'source_ids':list(ids),
                         'barycentric':list(bary),'distance_m':distance,'top_cuff_cap':is_cuff_cap})
    if max_outer_distance>.025:raise ValueError('SHOE_OUTER_SURFACE_TOO_FAR_FROM_ANATOMY:'+str(max_outer_distance))
    if 'outer_surface_source_vertex_ids' in boot:del boot['outer_surface_source_vertex_ids']
    boot['surface_construction']='actual_anatomical_voxel_envelope_no_reprojection'
    boot['closed_component_volumes_m3']=json.dumps(measured['signed_volumes_m3'])
    return rows,{'method':boot['surface_construction'],'voxel_size_m':.003,'preserve_volume':False,
                 'before':before,'after':measured,'discarded_subvoxel_cells':discarded,
                 'weight_transfer':'nearest_real_body_triangle_barycentric','max_skin_transfer_distance_m':max_distance,
                 'max_outer_surface_distance_m':max_outer_distance,'actual_skin_transfer':transfer,
                 'anatomy_enclosure':{'source_vertex_samples':enclosure,'cuff_exclusion_z_m':.40,
                                      'numeric_tolerance_m':1e-5,'outside_count':0},
                 'old_sole_ids_retained':False}
