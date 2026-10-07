"""Bind opaque source pixels to actual exported front triangles for measurement."""
import numpy as np


def bind_pixels(skin, rgba, pixels):
    height,width = rgba.shape[:2]
    uv = np.asarray(skin['uv']).reshape(-1,2)*[width,height]
    faces = np.asarray(skin['indices'],dtype=int).reshape(-1,3)
    triangle = uv[faces]
    minimum,maximum = triangle.min(axis=1),triangle.max(axis=1)
    bound_faces,barycentric = [],[]
    for pixel in pixels:
        point = np.asarray(pixel,dtype=float)
        if point.shape != (2,) or not np.isfinite(point).all():
            raise ValueError('FINITE_SOURCE_PIXEL_REQUIRED')
        x,y = np.floor(point).astype(int)
        if not (0 <= x < width and 0 <= y < height) or rgba[y,x,3] != 255:
            raise ValueError('OPAQUE_ORIGINAL_PIXEL_REQUIRED')
        candidates = np.flatnonzero(np.all(point >= minimum-1e-7,axis=1)&np.all(point <= maximum+1e-7,axis=1))
        found = False
        for index in candidates:
            a,b,c = triangle[index]
            basis = np.column_stack((b-a,c-a))
            if abs(np.linalg.det(basis)) < 1e-10:
                continue
            v,w = np.linalg.solve(basis,point-a)
            weights = np.array([1-v-w,v,w])
            if weights.min() < -1e-7:
                continue
            bound_faces.append(faces[index].tolist())
            barycentric.append(weights.tolist())
            found = True
            break
        if not found:
            raise ValueError('SOURCE_PIXEL_NOT_ON_ACTUAL_FRONT_TRIANGLE')
    return {'vertices':bound_faces,'barycentric':barycentric,'pixels':pixels}


def sample_positions(vertex_positions,binding):
    return (np.asarray(vertex_positions)[np.asarray(binding['vertices'])]*
            np.asarray(binding['barycentric'])[:,:,None]).sum(axis=1)
