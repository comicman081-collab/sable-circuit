"""Explicit target-curve resampling, not new measured reference animation."""
import numpy as np
from scipy.spatial.transform import Rotation,Slerp


def densify(global_poses, parents, old_rest, native_rest):
    # Preserve the authored deformation while changing to the measured bind basis.
    rebased = global_poses@np.linalg.inv(old_rest)@native_rest
    result=[]
    for number in range(len(rebased)-1):
        result.append(rebased[number])
        midpoint=[]
        for index,parent in enumerate(parents):
            local=[]
            for frame in rebased[number:number+2]:
                local.append(np.linalg.inv(frame[parent])@frame[index] if parent>=0 else frame[index])
            scales=np.asarray([np.linalg.norm(matrix[:3,:3],axis=0) for matrix in local])
            rotations=Rotation.from_matrix(np.asarray([matrix[:3,:3]/scale for matrix,scale in zip(local,scales)]))
            matrix=np.eye(4)
            matrix[:3,:3]=Slerp([0,1],rotations)(.5).as_matrix()*scales.mean(axis=0)
            matrix[:3,3]=(local[0][:3,3]+local[1][:3,3])*.5
            midpoint.append(midpoint[parent]@matrix if parent>=0 else matrix)
        result.append(np.asarray(midpoint))
    result.append(rebased[-1])
    return np.asarray(result)
