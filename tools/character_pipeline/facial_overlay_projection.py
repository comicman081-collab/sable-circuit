"""Keep resolved approved front projection only; never erase actual anatomy."""
import hashlib
import json


def content_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()


def corner_set(head):
    uv=head.data.uv_layers.active.data
    return { (tuple(head.data.vertices[loop.vertex_index].co),tuple(uv[loop.index].uv),
              tuple(sorted((w.group,w.weight) for w in head.data.vertices[loop.vertex_index].groups)))
             for loop in head.data.loops }


def projected_area2(uv,width,height):
    a,b,c=uv
    return abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))*width*height


def resolve_front_overlay(head,body,width,height):
    import bmesh
    if head.get('generation_role')!='facial_surface' or body.get('generation_role')!='body':
        raise ValueError('FRONT_OVERLAY_AND_PRESERVED_REAL_BODY_REQUIRED')
    if not head.data.uv_layers.active:raise ValueError('ACTUAL_PROJECTED_UV_REQUIRED')
    body_before=([(tuple(v.co),[(w.group,w.weight) for w in v.groups]) for v in body.data.vertices],
                 [tuple(p.vertices) for p in body.data.polygons])
    corners_before=corner_set(head)
    bm=bmesh.new();bm.from_mesh(head.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
    bm.to_mesh(head.data);bm.free();head.data.update()
    uv=head.data.uv_layers.active.data;omitted=[]
    for face in head.data.polygons:
        values=[list(uv[i].uv) for i in face.loop_indices]
        area=projected_area2(values,width,height)
        if area<.25:
            omitted.append({'face':face.index,'source_pixel_area2':area,'uv':values,
                            'vertex_positions_m':[list(head.data.vertices[i].co) for i in face.vertices]})
    if len(omitted)>len(head.data.polygons)*.10:
        raise ValueError('FACE_PROJECTION_NOT_SUITABLE_FOR_THIS_ANATOMY')
    bm=bmesh.new();bm.from_mesh(head.data);bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.faces[r['face']] for r in omitted],context='FACES')
    bm.to_mesh(head.data);bm.free();head.data.update()
    body_after=([(tuple(v.co),[(w.group,w.weight) for w in v.groups]) for v in body.data.vertices],
                [tuple(p.vertices) for p in body.data.polygons])
    if body_before!=body_after:raise ValueError('ACTUAL_BODY_WAS_MUTATED_BY_OVERLAY_FIX')
    corners_after=corner_set(head)
    if not corners_after.issubset(corners_before):raise ValueError('RETAINED_FACE_UV_OR_SKIN_CHANGED')
    return {'method':'resolved_front_projection_over_preserved_opaque_anatomy',
            'omitted_overlay_triangles':omitted,'remaining_overlay_triangles':len(head.data.polygons),
            'body_vertices':len(body.data.vertices),'body_polygons':len(body.data.polygons),
            'actual_body_geometry_and_weights_unchanged':True,
            'body_geometry_and_weights_sha256_before':content_hash(body_before),
            'body_geometry_and_weights_sha256_after':content_hash(body_after),
            'retained_uv_and_weight_corners_unchanged':True,
            'retained_corners_sha256':content_hash(sorted(corners_after)),
            'limits':{'minimum_source_pixel_area2':.25,'maximum_omitted_overlay_fraction':.10},
            'visual_review_required':True}
