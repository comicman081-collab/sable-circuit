"""Numeric source-support feasibility only. Does not create a Blender/runtime asset."""
from pathlib import Path
import math
import numpy as np
from PIL import Image
from scipy.interpolate import LinearNDInterpolator
import generation_harness as g
from source_projection_binding import unproject

ROOT = Path(__file__).resolve().parents[2]


def run():
    joint_path = ROOT / 'artifacts/quarantine/generation_diagnostics/mica_E_depth_binding_math_r01/PROBE.json'
    skin_path = ROOT / 'artifacts/quarantine/generation_diagnostics/mica_E_forward_clip_r02/SOURCE_SKIN.json'
    joint = g.read(joint_path)
    skin = g.read(skin_path)
    for reference in joint['inputs'].values():
        g.resolve(reference)
    profile = g.read(g.resolve(joint['inputs']['profile']))
    rgba_path = g.resolve(skin['source_rgba'])
    rgba = np.asarray(Image.open(rgba_path).convert('RGBA'))
    height, width = rgba.shape[:2]
    configuration = joint['configuration']
    ground_x, ground_y = configuration['ground_pixel']
    original_scale = configuration['original_metres_per_pixel']
    angle = math.radians(configuration['elevation_degrees'])
    sine, cosine = math.sin(angle), math.cos(angle)
    scale = original_scale * cosine
    controls = {}
    for name, pixel in profile['bone_points_px'].items():
        controls[tuple(pixel)] = float(joint['blender_world_bone_heads'][name][2])
    for x, y in [(0,0),(width,0),(0,height),(width,height)]:
        controls[(x,y)] = (ground_y-y)*original_scale
    # Original alpha contour samples on the actual boot-bottom regions.
    # These are proposed sole constraints, not a certified neutral floor.
    regions = {'left': [600,1390,801,1478], 'right': [165,1430,268,1493]}
    sole_controls = {}
    for side, (x0,y0,x1,y1) in regions.items():
        selected = []
        for x in range(x0,x1):
            ys = np.flatnonzero(rgba[y0:y1,x,3] == 255)
            if len(ys):
                pixel = (x+.5, float(y0+ys[-1])+.5)
                controls[pixel] = 0.0
                selected.append(list(pixel))
        if len(selected) < 20:
            raise ValueError('ACTUAL_ALPHA_SOLE_CONTOUR_REQUIRED')
        sole_controls[side] = selected
    field = LinearNDInterpolator(np.asarray(list(controls)), np.asarray(list(controls.values())))
    uv = np.asarray(skin['uv']).reshape(-1,2)
    pixels = uv * [width,height]
    z = np.asarray(field(pixels))
    if not np.isfinite(z).all():
        raise ValueError('COMPLETE_CONTINUOUS_SOURCE_FIELD_REQUIRED')
    image_height = (ground_y-pixels[:,1])*scale
    x = (pixels[:,0]-ground_x)*scale
    y = (image_height-z*cosine)/sine
    positions = np.column_stack((x,y,z))
    old = np.asarray(skin['positions']).reshape(-1,3)
    # Carry existing surface curvature along the new viewing ray. Its screen
    # projection is identically zero; it does not author visible side pixels.
    positions += old[:,2,None] * np.array([0,-cosine,sine])
    projected = np.column_stack((positions[:,0]/scale+ground_x,
        ground_y-(positions[:,1]*sine+positions[:,2]*cosine)/scale))
    error = float(np.max(np.abs(projected-pixels)))
    if error > 1e-8:
        raise ValueError('ORIGINAL_PIXEL_PROJECTION_CHANGED')
    heads = {k:np.asarray(v) for k,v in joint['blender_world_bone_heads'].items()}
    lengths = {side:{name:float(np.linalg.norm(heads[b+'_'+side]-heads[a+'_'+side]))
        for name,a,b in [('thigh','thigh','calf'),('calf','calf','foot'),('ankle_to_ball','foot','ball')]}
        for side in ['l','r']}
    out = ROOT / 'artifacts/quarantine/generation_diagnostics/mica_E_projection_surface_math_r01'
    out.mkdir(exist_ok=False)
    np.save(out/'PROPOSED_FRONT_POSITIONS_BLENDER.npy',positions,allow_pickle=False)
    camera = {'elevation_degrees':30,'elevation_authority':'explicit rig hypothesis, not measured original camera',
        'blender_right':[1,0,0], 'blender_up':[0,sine,cosine], 'blender_forward':[0,cosine,-sine],
        'godot_right':[1,0,0], 'godot_up':[0,cosine,-sine], 'godot_forward':[0,-sine,-cosine],
        'orthographic_size_for_1920_square_native_source':1920*scale,
        'source_metres_per_pixel':scale,
        'required_sprite_scale':'camera_orthographic_size * shared_world_pixels_per_metre / viewport_pixels',
        'independent_display_or_motion_scale_allowed':False}
    g.write(out/'PROBE.json',{'inputs':{'joints':g.ref(joint_path),'skin':g.ref(skin_path),
        'rgba':g.ref(rgba_path),'probe':g.ref(__file__),'projection':g.ref(ROOT/'tools/character_pipeline/source_projection_binding.py')},
        'camera':camera,'front_vertex_count':len(positions),'maximum_front_projection_error_px':error,
        'physical_lengths_m':lengths,'world_depth_range_m':[float(positions[:,1].min()),float(positions[:,1].max())],
        'sole_source_regions_px':regions,'proposed_sole_alpha_contours_px':sole_controls,
        'depth_field':'single continuous piecewise-linear original-coordinate field shared by all semantic regions',
        'proposed_positions':g.ref(out/'PROPOSED_FRONT_POSITIONS_BLENDER.npy'),
        'scope':'numeric support hypothesis only; no scene/render/motion export or source pixel modification',
        'actual_neutral_floor':'NOT_YET_EVALUATED','fixed_length_49_pose_reach':'PENDING',
        'production_ready':False})
    print('FRONT_PROJECTION_ERROR_PX',error,'LENGTHS',lengths)


if __name__ == '__main__':
    run()
