"""Read-only VRoid/VRM intake. Never treats a humanoid label as a verified rig.

No addon download, app launch, scene import, material conversion or production
promotion. Embedded geometry and weights are decoded before Blender adaptation.
"""
import argparse
import json
import math
import struct
from pathlib import Path
import generation_harness as g

REQUIRED=('hips','spine','head','leftUpperLeg','leftLowerLeg','leftFoot',
          'rightUpperLeg','rightLowerLeg','rightFoot','leftUpperArm','leftLowerArm',
          'leftHand','rightUpperArm','rightLowerArm','rightHand')


def decode_glb(path):
    data=g.local(path).read_bytes()
    if len(data)<20: raise ValueError('TRUNCATED_GLB')
    magic,version,total=struct.unpack_from('<4sII',data)
    if magic!=b'glTF' or version!=2 or total!=len(data): raise ValueError('VALID_GLB2_CONTAINER_REQUIRED')
    offset=12; document=None; binary=None
    while offset<len(data):
        length,kind=struct.unpack_from('<II',data,offset); offset+=8
        if length%4 or offset+length>len(data): raise ValueError('INVALID_GLB_CHUNK')
        chunk=data[offset:offset+length]; offset+=length
        if kind==0x4E4F534A:
            if document is not None: raise ValueError('DUPLICATE_GLB_JSON')
            document=json.loads(chunk.decode('utf-8'),parse_constant=lambda v:(_ for _ in ()).throw(ValueError('NON_FINITE_VRM')))
        elif kind==0x004E4942:
            if binary is not None: raise ValueError('DUPLICATE_GLB_BINARY')
            binary=chunk
    if not document or binary is None: raise ValueError('EMBEDDED_VRM_JSON_AND_BINARY_REQUIRED')
    buffers=document.get('buffers',[])
    if len(buffers)!=1 or buffers[0].get('uri') or buffers[0].get('byteLength',len(binary)+1)>len(binary):
        raise ValueError('EXTERNAL_OR_INVALID_VRM_BUFFER')
    if any(im.get('uri') for im in document.get('images',[])):
        raise ValueError('EXTERNAL_VRM_TEXTURE_NOT_CONTENT_BOUND')
    return document,binary


def accessor(doc,binary,index):
    formats={5121:('B',1),5123:('H',2),5125:('I',4),5126:('f',4)}
    widths={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
    a=doc['accessors'][index]
    if 'sparse' in a or a.get('normalized') or a['componentType'] not in formats:
        raise ValueError('UNSUPPORTED_VRM_ACCESSOR_REQUIRES_EXPLICIT_ADAPTER')
    fmt,size=formats[a['componentType']]; width=widths[a['type']]
    view=doc['bufferViews'][a['bufferView']]
    stride=view.get('byteStride',size*width); start=view.get('byteOffset',0)+a.get('byteOffset',0)
    count=a['count']; end=start+(count-1)*stride+size*width
    if view.get('buffer',0)!=0 or not 0<count<=1000000 or stride<size*width or start<0 or end>len(binary) or end>view.get('byteOffset',0)+view['byteLength']:
        raise ValueError('VRM_ACCESSOR_OUTSIDE_BOUND_BUFFER')
    rows=[struct.unpack_from('<'+fmt*width,binary,start+i*stride) for i in range(count)]
    if any(not math.isfinite(v) for row in rows for v in row): raise ValueError('NON_FINITE_VRM_GEOMETRY')
    return rows


def inspect(path,license_path):
    doc,binary=decode_glb(path); errors=[]
    extensions=doc.get('extensions',{})
    if 'VRMC_vrm' in extensions:
        ext=extensions['VRMC_vrm']; version='1.0'
        bones={k:v['node'] for k,v in ext.get('humanoid',{}).get('humanBones',{}).items()}
    elif 'VRM' in extensions:
        ext=extensions['VRM']; version='0.x'
        values=ext.get('humanoid',{}).get('humanBones',[])
        bones={v['bone']:v['node'] for v in values}
        if len(bones)!=len(values): errors.append('DUPLICATE_VRM_HUMAN_BONE_ROLE')
    else:
        raise ValueError('VRM_HUMANOID_EXTENSION_REQUIRED')
    if missing:=set(REQUIRED)-set(bones): errors.append('MISSING_HUMANOID_BONES:'+','.join(sorted(missing)))
    nodes=doc.get('nodes',[]); indices=list(bones.values())
    if len(indices)!=len(set(indices)) or any(type(i) is not int or i<0 or i>=len(nodes) for i in indices):
        errors.append('INVALID_OR_ALIASED_HUMANOID_NODES')
    record=g.read(license_path)
    if record.get('model')!=g.ref(path): errors.append('LICENSE_NOT_BOUND_TO_EXACT_VRM')
    if (record.get('commercial_use')!='ALLOW' or record.get('derivatives')!='ALLOW' or
            record.get('rendered_game_distribution')!='ALLOW' or not record.get('reviewer') or
            not record.get('reviewed_utc') or not record.get('evidence')):
        errors.append('MODEL_AND_ALL_INCLUDED_ITEMS_LICENSE_REVIEW_REQUIRED')
    for evidence in record.get('evidence',[]): g.resolve(evidence)
    if not record.get('all_included_items_reviewed'): errors.append('THIRD_PARTY_ITEMS_NOT_REVIEWED')
    if record.get('intended_use')!='internal_rigging_and_rendered_game_assets': errors.append('NO_PUBLIC_AVATAR_GENERATOR_LICENSE_ASSUMPTION')
    weighted=0; vertex_count=0; used_joints=set()
    for node in nodes:
        if 'mesh' not in node: continue
        if 'skin' not in node:
            errors.append('UNSKINNED_VISIBLE_MESH_REQUIRES_REVIEW'); continue
        skin=doc['skins'][node['skin']]; joints=skin['joints']
        if any(type(i) is not int or i<0 or i>=len(nodes) for i in joints): raise ValueError('INVALID_SKIN_JOINT_NODE')
        for primitive in doc['meshes'][node['mesh']]['primitives']:
            attrs=primitive.get('attributes',{})
            if not {'POSITION','JOINTS_0','WEIGHTS_0'}.issubset(attrs):
                errors.append('ACTUAL_VERTEX_SKIN_ATTRIBUTES_REQUIRED'); continue
            positions=accessor(doc,binary,attrs['POSITION']); joint_rows=accessor(doc,binary,attrs['JOINTS_0']); weights=accessor(doc,binary,attrs['WEIGHTS_0'])
            if len(positions)!=len(joint_rows) or len(weights)!=len(positions): raise ValueError('VERTEX_SKIN_COUNT_MISMATCH')
            if any(len(p)!=3 for p in positions) or any(len(j)!=4 or len(w)!=4 for j,w in zip(joint_rows,weights)):
                raise ValueError('VERTEX_SKIN_COMPONENT_SHAPE_MISMATCH')
            weighted+=1; vertex_count+=len(positions)
            for joint,weight in zip(joint_rows,weights):
                if any(w<0 or w>1 for w in weight) or abs(sum(weight)-1)>.001:
                    errors.append('INVALID_OR_UNNORMALIZED_SKIN_WEIGHTS')
                for i,w in zip(joint,weight):
                    if type(i) is not int or i<0 or i>=len(joints): raise ValueError('JOINT_INDEX_OUTSIDE_SKIN')
                    if w>0: used_joints.add(joints[i])
    if weighted==0: errors.append('NO_ACTUAL_WEIGHTED_GEOMETRY')
    for side in ('left','right'):
        for part in ('UpperLeg','LowerLeg','Foot'):
            name=side+part
            if bones.get(name) not in used_joints: errors.append('HUMANOID_BONE_NOT_DRIVING_MESH:'+name)
    meta=ext.get('meta',{})
    # This is a conservative intake check, not a replacement for the exact
    # item's license. A contradictory model tag cannot be overridden by a label.
    commercial=meta.get('commercialUsage','personalNonProfit') if version=='1.0' else meta.get('commercialUssageName')
    if commercial not in ('corporation','Allow'):
        errors.append('VRM_METADATA_RESTRICTS_OR_DOES_NOT_ESTABLISH_COMMERCIAL_USE')
    if version=='1.0':
        if meta.get('modification','prohibited') not in ('allowModification','allowModificationRedistribution'):
            errors.append('VRM_METADATA_DOES_NOT_ALLOW_DERIVATIVES')
        if meta.get('avatarPermission','onlyAuthor')!='everyone':
            errors.append('VRM_AVATAR_PERMISSION_REQUIRES_SEPARATE_LICENSE')
        if meta.get('creditNotation','required')=='required' and not record.get('credit_notice'):
            errors.append('VRM_REQUIRED_CREDIT_NOTICE_MISSING')
    if meta.get('otherLicenseUrl') and meta['otherLicenseUrl'] not in record.get('reviewed_license_urls',[]):
        errors.append('ADDITIONAL_MODEL_LICENSE_NOT_REVIEWED')
    return {'stage':'vroid_intake','verdict':'FAIL' if errors else 'HOLD_BLENDER_RETARGET_AND_VISUAL_REVIEW',
        'errors':sorted(set(errors)),'model':g.ref(path),'license_manifest':g.ref(license_path),
        'vrm_version':version,'embedded_license_settings':meta,'humanoid_nodes':bones,'weighted_primitives':weighted,'decoded_vertices':vertex_count,
        'automatic_ual_transfer_verified':False,'production_ready':False,
        'next':'Import a project-local copy through a license-verified VRM adapter; preserve ImageGen art authority, then source/mesh/pose/motion gates.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True); p.add_argument('--license',required=True); p.add_argument('--out',required=True)
    a=p.parse_args(); result=inspect(a.input,a.license); g.write(a.out,result)
    print(json.dumps(result,ensure_ascii=False,indent=2)); raise SystemExit(1 if result['errors'] else 0)
