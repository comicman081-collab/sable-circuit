"""A camera may follow ground translation, never gait bob/yaw/scale or framing.

World-travelled sole vertices remain world-space evidence. Following the same
ground translation produces an in-place runtime cell without recropping pixels
or adding the actor's translation a second time in the runtime.
"""
import copy
import math


def matrix(value):
    if not isinstance(value,list) or len(value)!=4 or any(len(row)!=4 for row in value):
        raise ValueError('CAPTURE_EXPECTS_ACTUAL_4X4_TRANSFORMS')
    if any(not math.isfinite(float(x)) for row in value for x in row):
        raise ValueError('CAPTURE_NONFINITE_TRANSFORM')
    if any(abs(value[3][i]-(1 if i==3 else 0))>1e-6 for i in range(4)):
        raise ValueError('CAPTURE_NONAFFINE_TRANSFORM')
    return value


def verify(approved_camera,actual_camera,approved_ground,actual_ground):
    first=matrix(approved_ground); current=matrix(actual_ground)
    for ground in (first,current):
        for i in range(3):
            for j in range(3):
                dot=sum(ground[k][i]*ground[k][j] for k in range(3))
                if abs(dot-(1 if i==j else 0))>1e-5:
                    raise ValueError('GROUND_CAPTURE_FRAME_MUST_BE_UNIT_ORTHOGONAL')
        if any(abs(ground[i][2]-(1 if i==2 else 0))>1e-5 for i in range(3)):
            raise ValueError('GROUND_CAPTURE_UP_MUST_STAY_WORLD_Z')
    if any(abs(first[i][j]-current[i][j])>1e-5 for i in range(3) for j in range(3)):
        raise ValueError('CAMERA_CANNOT_FOLLOW_GAIT_YAW_OR_LEAN')
    delta=[current[i][3]-first[i][3] for i in range(3)]
    if abs(delta[2])>1e-5:
        raise ValueError('CAMERA_CANNOT_FOLLOW_GAIT_BOB')
    expected=copy.deepcopy(approved_camera)
    matrix(expected['matrix']);matrix(actual_camera['matrix'])
    for i in range(3):expected['matrix'][i][3]+=delta[i]
    for key,value in expected.items():
        if key=='matrix':
            if any(abs(value[i][j]-actual_camera[key][i][j])>1e-5 for i in range(4) for j in range(4)):
                raise ValueError('CAPTURE_CAMERA_NOT_EXACT_GROUND_TRANSLATION')
        elif actual_camera.get(key)!=value:
            raise ValueError('CAPTURE_CAMERA_PROJECTION_OR_FRAME_CHANGED:'+key)
    if set(expected)!=set(actual_camera):
        raise ValueError('CAPTURE_CAMERA_FIELDS_CHANGED')
    return delta
