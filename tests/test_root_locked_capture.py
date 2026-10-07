"""Camera registration unit oracles; numeric fixtures are not art approval."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/character_pipeline'))
import root_locked_capture as c

class CaptureTest(unittest.TestCase):
    def setUp(self):
        self.ground=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
        self.camera={'matrix':[[1,0,0,4],[0,1,0,3],[0,0,1,2],[0,0,0,1]],'ortho_scale':2.5,'type':'ORTHO'}
    def test_actual_translation_is_allowed_without_crop_or_zoom(self):
        ground=copy.deepcopy(self.ground);ground[0][3]=2
        camera=copy.deepcopy(self.camera);camera['matrix'][0][3]+=2
        self.assertEqual(c.verify(self.camera,camera,self.ground,ground),[2,0,0])
        with self.assertRaisesRegex(ValueError,'NOT_EXACT_GROUND_TRANSLATION'):
            c.verify(self.camera,self.camera,self.ground,ground)
    def test_bob_yaw_zoom_and_scale_are_not_normalization(self):
        ground=copy.deepcopy(self.ground);ground[2][3]=.03
        with self.assertRaisesRegex(ValueError,'GAIT_BOB'):c.verify(self.camera,self.camera,self.ground,ground)
        ground=copy.deepcopy(self.ground);ground[0][0]=0;ground[0][1]=-1;ground[1][0]=1;ground[1][1]=0
        with self.assertRaisesRegex(ValueError,'GAIT_YAW'):c.verify(self.camera,self.camera,self.ground,ground)
        camera=copy.deepcopy(self.camera);camera['ortho_scale']=2.4
        with self.assertRaisesRegex(ValueError,'PROJECTION_OR_FRAME'):c.verify(self.camera,camera,self.ground,self.ground)
        ground=copy.deepcopy(self.ground);ground[0][0]=1.2
        with self.assertRaisesRegex(ValueError,'UNIT_ORTHOGONAL'):c.verify(self.camera,self.camera,self.ground,ground)

if __name__=='__main__':unittest.main(verbosity=2)
