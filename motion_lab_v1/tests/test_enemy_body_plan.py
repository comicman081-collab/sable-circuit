"""Real scoped routing calls; no generation and no production file mutation."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import character_workflow as workflow
import character_handoff as handoff
import enemy_body_plan as body_plan
import new_character

class EnemyBodyPlanTests(unittest.TestCase):
    def test_roster_has_no_humanoid(self):
        policy = json.loads(body_plan.POLICY.read_text(encoding='utf-8'))
        humans = [key for key, row in policy['roles'].items() if row['body_plan']=='humanoid']
        self.assertEqual(humans, [])
        self.assertEqual(policy['humanoid_enemy_limit'], 0)
        self.assertEqual(set(policy['roles']), set(policy['active_enemy_ids']))
        self.assertTrue(all(row['body_plan']=='robot' for row in policy['roles'].values()))
        # The shield role became the BULWARK tracked crawler, the aberrant role the CINDER hover ram.
        self.assertEqual(policy['roles']['ENM_SITE7_BULWARK_01']['locomotion'], 'tracked')
        self.assertEqual(policy['roles']['ENM_SITE7_RAM_01']['locomotion'], 'hover_charge')

    def test_retired_shield_recipe_cannot_generate_resume_packet(self):
        with self.assertRaisesRegex(ValueError, 'ROBOT_ONLY_ENEMY'):
            handoff.make('site7_shield')

    def test_retired_shield_cannot_select_gait_slots(self):
        with self.assertRaisesRegex(ValueError, 'ROBOT_ONLY_ENEMY'):
            workflow.source_status('site7_shield')

    def test_new_enemy_biped_is_blocked_before_reference_or_output_access(self):
        with self.assertRaisesRegex(ValueError, 'ROBOT_ONLY_ENEMY'):
            new_character.scaffold('site7_new_humanoid', 'forbidden', LAB/'missing_reference.png')
        self.assertFalse((LAB/'characters/site7_new_humanoid.json').exists())
        self.assertFalse((LAB/'art/site7_new_humanoid').exists())

    def test_policy_missing_fails_closed_for_enemy(self):
        with patch.object(body_plan, 'POLICY', LAB/'qa/absent_body_plan_policy.json'):
            with self.assertRaises(FileNotFoundError):
                body_plan.require_biped_authoring('site7_rifle')

    def test_rifle_is_blocked_and_players_unchanged(self):
        with self.assertRaisesRegex(ValueError, 'ROBOT_ONLY_ENEMY'):
            handoff.make('site7_rifle')
        for character in ['mica','aster','rook']:
            with self.subTest(character=character):
                self.assertEqual(workflow.recipe(character)['id'], character)

    def test_historical_source_and_recipe_retained(self):
        config=json.loads((LAB/'characters/site7_shield.json').read_text(encoding='utf-8'))
        self.assertTrue(config['productionRetired'])
        reference=LAB/config['identityReference']
        self.assertTrue(reference.is_file())
        self.assertEqual(workflow.sha(reference), config['referenceSHA256'])

    def test_registry_only_activates_reviewed_robots(self):
        policy=json.loads(body_plan.POLICY.read_text(encoding='utf-8'))
        profiles=json.loads((LAB.parent/'data/art_profiles/enemy_profiles.json').read_text(encoding='utf-8'))['profiles']
        self.assertEqual(set(row['enemy_id'] for row in profiles), set(policy['active_enemy_ids']))
        for row in profiles:
            self.assertEqual(row['body_plan'], 'robot')
            self.assertTrue(row['runtime_enabled'])
            self.assertIn('machine_asset', row)
            self.assertNotIn('biped_asset', row)
        self.assertTrue((LAB.parent/'assets/enemies/recon_drone/authored_yaw8_v1/spec.json').is_file())
        self.assertTrue((LAB.parent/'assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json').is_file())

    def test_all_encounters_and_reinforcements_exclude_retired_bodies(self):
        allowed = set(json.loads(body_plan.POLICY.read_text('utf-8'))['active_enemy_ids'])
        def walk(value):
            if isinstance(value, dict):
                if 'enemy_id' in value:
                    self.assertIn(value['enemy_id'], allowed)
                for child in value.values(): walk(child)
            elif isinstance(value, list):
                for child in value: walk(child)
        for path in (LAB.parent/'data/missions').glob('MIS_CH01_*.json'):
            walk(json.loads(path.read_text('utf-8')))

if __name__=='__main__':
    unittest.main()
