"""Bind approved weapon pixels to the actual source-carrying mesh triangles."""


def export(mesh, rgba, profile, axes):
    from mathutils import Vector
    contract = profile['weapon_binding']
    bone = contract['bone']
    group = mesh.vertex_groups.get(bone)
    if group is None:
        raise ValueError('SOURCE_WEAPON_BONE_MISSING')
    height, width = rgba.shape[:2]
    evidence = {}

    def point(label, pixel):
        x, y = pixel
        if not isinstance(x, int) or not isinstance(y, int) or not 0 <= x < width or not 0 <= y < height:
            raise ValueError('WEAPON_POINT_MUST_ADDRESS_A_SOURCE_PIXEL')
        if rgba[y,x,3] != 255:
            raise ValueError('WEAPON_POINT_ON_TRANSPARENT_BACKGROUND:'+label)
        target = Vector(((x+0.5)/width, 1-(y+0.5)/height))
        for face in mesh.data.polygons:
            if face.material_index != 0 or len(face.vertices) != 3:
                continue
            u, v, w = [mesh.data.uv_layers.active.data[i].uv for i in face.loop_indices]
            a, b, c = v-u, w-u, target-u
            determinant = a.x*b.y-a.y*b.x
            if abs(determinant) < 1e-12:
                continue
            second = (c.x*b.y-c.y*b.x)/determinant
            third = (a.x*c.y-a.y*c.x)/determinant
            weights = [1-second-third, second, third]
            if min(weights) < -1e-7:
                continue
            position = Vector((0,0,0))
            for index, amount in zip(face.vertices, weights):
                vertex = mesh.data.vertices[index]
                binding = {item.group: item.weight for item in vertex.groups}
                if abs(binding.get(group.index,0)-1) > 1e-6:
                    raise ValueError('VISIBLE_WEAPON_TRIANGLE_NOT_COHERENTLY_BOUND:'+label)
                position += (mesh.matrix_world @ vertex.co)*amount
            evidence[label] = {'source_pixel': pixel, 'face_index': face.index,
                               'vertex_indices': list(face.vertices), 'barycentric': weights}
            return list(axes @ position)
        raise ValueError('WEAPON_PIXEL_HAS_NO_ACTUAL_VISIBLE_TRIANGLE:'+label)

    result = {'coordinate_system': 'godot_y_up_mesh_rest', 'bone': bone,
              'muzzle': point('muzzle', contract['muzzle_point_px']),
              'barrel_rear': point('barrel_rear', contract['barrel_axis_point_px']),
              'right_grip': point('right_grip', contract['right_grip_px']),
              'left_grip': point('left_grip', contract['left_grip_px']),
              'actual_source_triangle_binding': evidence,
              'independent_visible_barrel_review_required': True}
    return result
