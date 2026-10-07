"""Small synthetic GLB fixtures for the optional licensed VRM inlet."""
import json
import struct
import sys
import unittest
import uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import inspect_vrm_source as v

class VrmTests(unittest.TestCase):
    def setUp(self):
        self.work=ROOT/'artifacts/generation_harness_audit/vrm_unit_fixtures'/uuid.uuid4().hex
        self.work.mkdir(parents=True)

    def model(self,mutate=None):
        joints=[list(v.REQUIRED).index(k) for k in ('leftUpperLeg','leftLowerLeg','leftFoot','rightUpperLeg','rightLowerLeg','rightFoot')]
        binary=struct.pack('<18f',*[i*.01 for i in range(18)])
        binary+=b''.join(struct.pack('<4H',i,0,0,0) for i in joints)
        binary+=struct.pack('<24f',*([1,0,0,0]*6))
        doc={'asset':{'version':'2.0'},'buffers':[{'byteLength':len(binary)}],
            'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':72},{'buffer':0,'byteOffset':72,'byteLength':48},{'buffer':0,'byteOffset':120,'byteLength':96}],
            'accessors':[{'bufferView':0,'componentType':5126,'count':6,'type':'VEC3'},
                         {'bufferView':1,'componentType':5123,'count':6,'type':'VEC4'},
                         {'bufferView':2,'componentType':5126,'count':6,'type':'VEC4'}],
            'nodes':[{'name':k} for k in v.REQUIRED]+[{'mesh':0,'skin':0}],
            'meshes':[{'primitives':[{'attributes':{'POSITION':0,'JOINTS_0':1,'WEIGHTS_0':2}}]}],
            'skins':[{'joints':list(range(len(v.REQUIRED)))}],
            'extensions':{'VRMC_vrm':{'humanoid':{'humanBones':{k:{'node':i} for i,k in enumerate(v.REQUIRED)}},
                'meta':{'commercialUsage':'corporation','modification':'allowModificationRedistribution','avatarPermission':'everyone','creditNotation':'required'}}}}
        if mutate: mutate(doc)
        encoded=json.dumps(doc).encode(); encoded+=b' '*((-len(encoded))%4)
        payload=struct.pack('<I4s',len(encoded),b'JSON')+encoded+struct.pack('<I4s',len(binary),b'BIN\0')+binary
        path=self.work/'synthetic.vrm'; path.write_bytes(struct.pack('<4sII',b'glTF',2,12+len(payload))+payload)
        evidence=self.work/'SYNTHETIC_LICENSE_TEST_ONLY.txt'; evidence.write_text('Synthetic legal fixture, not an actual model license.',encoding='utf-8')
        license_path=self.work/'license.json'
        g.write(license_path,{'model':g.ref(path),'commercial_use':'ALLOW','derivatives':'ALLOW','rendered_game_distribution':'ALLOW',
            'all_included_items_reviewed':True,'reviewer':'SYNTHETIC TEST','reviewed_utc':'2026-09-07','credit_notice':'SYNTHETIC TEST',
            'evidence':[g.ref(evidence)],'intended_use':'internal_rigging_and_rendered_game_assets'})
        return path,license_path

    def test_valid_geometry_is_hold_not_automatic_retarget(self):
        result=v.inspect(*self.model()); self.assertEqual(result['errors'],[])
        self.assertFalse(result['production_ready']); self.assertFalse(result['automatic_ual_transfer_verified'])

    def test_missing_commercial_tag_uses_restrictive_default(self):
        paths=self.model(lambda d:d['extensions']['VRMC_vrm']['meta'].pop('commercialUsage'))
        self.assertTrue(any('COMMERCIAL' in e for e in v.inspect(*paths)['errors']))

    def test_missing_modification_permission_is_rejected(self):
        paths=self.model(lambda d:d['extensions']['VRMC_vrm']['meta'].pop('modification'))
        self.assertIn('VRM_METADATA_DOES_NOT_ALLOW_DERIVATIVES',v.inspect(*paths)['errors'])

    def test_missing_humanoid_bone_is_rejected(self):
        paths=self.model(lambda d:d['extensions']['VRMC_vrm']['humanoid']['humanBones'].pop('leftFoot'))
        self.assertTrue(any('MISSING_HUMANOID_BONES' in e for e in v.inspect(*paths)['errors']))

    def test_external_texture_is_rejected(self):
        paths=self.model(lambda d:d.update(images=[{'uri':'unbound.png'}]))
        with self.assertRaisesRegex(ValueError,'EXTERNAL_VRM_TEXTURE'): v.inspect(*paths)

    def test_out_of_range_accessor_is_rejected(self):
        paths=self.model(lambda d:d['accessors'][0].update(count=100000))
        with self.assertRaisesRegex(ValueError,'ACCESSOR_OUTSIDE'): v.inspect(*paths)

    def test_license_not_for_model_is_rejected(self):
        model,license_path=self.model(); record=g.read(license_path); record['model']['sha256']='0'*64
        changed=self.work/'wrong_license.json'; g.write(changed,record)
        self.assertIn('LICENSE_NOT_BOUND_TO_EXACT_VRM',v.inspect(model,changed)['errors'])

if __name__=='__main__': unittest.main(verbosity=2)
