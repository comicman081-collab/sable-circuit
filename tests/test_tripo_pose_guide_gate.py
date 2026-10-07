import copy
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import tripo_pose_guide_gate as gate
import visible_frame_harness_current as current


class TripoGuideGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide=g.read(ROOT/'art_src/motion_reference/tripo_run_20260908/pose_guide_r01/E_CONTACT_L_GUIDE_DRAFT.json')

    def test_height_pass_cannot_bypass_missing_independent_reviews(self):
        errors=current._audit_pose_guide_current(self.guide,'E','run','contact_l')
        self.assertIn('EXACT_TRIPO_GUIDE_PROVENANCE_AND_INDEPENDENT_REVIEWS_REQUIRED',errors)
        self.assertIn('FIXED_FLOOR_CONTACT_CALIBRATION_INVALID',errors)

    def test_actual_closure_binds_glb_blender_scripts_and_all_captured_frames(self):
        files=gate.closure(self.guide)
        self.assertIn('art_src/motion_reference/tripo_run_20260908/source/ORIGINAL_Run.glb',files)
        self.assertIn('tools/character_pipeline/lock_tripo_support_anchors.py',files)
        self.assertIn('tools/character_pipeline/visible_frame_harness_current.py',files)
        self.assertEqual(sum(path.startswith('artifacts/quarantine/generation_diagnostics/tripo_support_capture_r02/frame_') for path in files),49)

    def test_other_direction_or_action_cannot_borrow_side_guide(self):
        for field,value,error in [('screen_direction','W','TRIPO_GUIDE_DIRECTION_PHASE_MISMATCH'),('action','Sprint_Loop','EXPLICIT_TRIPO_GUIDE_ACTION_REQUIRED')]:
            guide=copy.deepcopy(self.guide);guide[field]=value
            self.assertIn(error,gate.audit(guide,'E','run','contact_l'))
        self.assertIn('TRIPO_GUIDE_ONLY_REVIEWED_E_RUN_ADAPTER',gate.audit(self.guide,'N','run','contact_l'))

    def test_paid_license_cannot_be_replaced_with_cc0_geometry_license(self):
        guide=copy.deepcopy(self.guide);guide['tripo_license']=guide['license']
        self.assertIn('TRIPO_LICENSE_SOURCE_MISMATCH',gate.audit(guide,'E','run','contact_l'))


if __name__=='__main__':unittest.main()
