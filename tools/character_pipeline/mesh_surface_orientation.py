"""Measured closed-component winding; no vertex displacement or skin changes."""
import math


def closed_component_orientation(vertices, faces):
    """Return connected components with signed volume and exact face IDs.

    Reject open, degenerate, nonmanifold or inconsistently wound topology.
    For a closed consistent shell, positive signed volume means outward.
    This is not a self-intersection test or visual approval.
    """
    if not vertices or not faces or any(len(v) != 3 or not all(math.isfinite(x) for x in v) for v in vertices):
        raise ValueError('FINITE_NONEMPTY_CLOSED_SURFACE_REQUIRED')
    edges = {}; neighbors = [set() for _ in faces]
    for index, face in enumerate(faces):
        if len(face) < 3 or len(set(face)) != len(face) or any(type(i) is not int or i < 0 or i >= len(vertices) for i in face):
            raise ValueError('VALID_SURFACE_FACE_IDS_REQUIRED')
        for a, b in zip(face, list(face[1:]) + [face[0]]):
            edges.setdefault(tuple(sorted((a, b))), []).append((index, a, b))
    for pair in edges.values():
        if len(pair) != 2:
            raise ValueError('CLOSED_MANIFOLD_COMPONENT_REQUIRED')
        a, b = pair
        if a[1:] != (b[2], b[1]):
            raise ValueError('CONSISTENT_COMPONENT_WINDING_REQUIRED')
        neighbors[a[0]].add(b[0]); neighbors[b[0]].add(a[0])
    remaining = set(range(len(faces))); result = []
    while remaining:
        first = min(remaining); remaining.remove(first)
        pending = [first]; component = {first}
        while pending:
            for index in neighbors[pending.pop()] & remaining:
                remaining.remove(index); component.add(index); pending.append(index)
        ids = sorted({i for f in component for i in faces[f]})
        origin = [sum(vertices[i][axis] for i in ids) / len(ids) for axis in range(3)]
        volume = 0.
        for index in component:
            points = [[vertices[i][k] - origin[k] for k in range(3)] for i in faces[index]]
            a = points[0]
            for b, c in zip(points[1:-1], points[2:]):
                volume += (a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2])
                           + a[2]*(b[0]*c[1]-b[1]*c[0])) / 6
        if abs(volume) < 1e-10:
            raise ValueError('NONZERO_CLOSED_COMPONENT_VOLUME_REQUIRED')
        result.append({'face_ids': sorted(component), 'vertex_ids': ids, 'signed_volume_m3': volume})
    return result
