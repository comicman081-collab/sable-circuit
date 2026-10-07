import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/character_pipeline'))
from continuous_torso_weights import apply


class TorsoAttachmentTests(unittest.TestCase):
    contract = {'source_y_knots_px': [560, 740, 840], 'upper_bone': 'spine_03', 'pelvis_bone': 'pelvis'}

    def test_separate_regions_share_identical_torso_boundary_motion(self):
        for y in (553, 560, 650, 739, 740):
            self.assertEqual(apply(y, {'thigh_l': 1.0}, self.contract),
                             apply(y, {'spine_01': 0.4, 'pelvis': 0.6}, self.contract))

    def test_weapon_and_hands_above_transition_remain_one_rigid_binding(self):
        for y in (420, 467, 549):
            self.assertEqual({'spine_03': 1.0}, apply(y, {'hand_l': 1.0}, self.contract))

    def test_actual_lower_weights_are_preserved_below_transition(self):
        original = {'calf_l': 0.8, 'thigh_l': 0.2}
        self.assertEqual(original, apply(1000, original, self.contract))

    def test_attachment_is_continuous_at_both_joins(self):
        for join in (560, 740, 840):
            before = apply(join-0.001, {'thigh_l': 1.0}, self.contract)
            after = apply(join+0.001, {'thigh_l': 1.0}, self.contract)
            self.assertLess(sum(abs(before.get(k, 0)-after.get(k, 0))
                                for k in before.keys() | after.keys()), 1e-6)

    def test_five_influence_union_is_rejected_instead_of_switching_bones(self):
        with self.assertRaisesRegex(ValueError, 'EXCEEDS_FOUR'):
            apply(790, {'thigh_l': 0.4, 'calf_l': 0.3, 'foot_l': 0.2, 'ball_l': 0.1}, self.contract)


if __name__ == '__main__':
    unittest.main()
