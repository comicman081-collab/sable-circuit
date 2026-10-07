"""Exercise the operation-8 seam waivers through the real pixel audit.

Three decks of operation 8 miss the raw seam targets; the user accepted them on 2026-09-30 instead of having them
regenerated (SEAM_WAIVERS in tools/environment/audit_site7_plate_lighting.py). These controls show that exactly those
seams are waived, that a waiver needs its mission, plate and room, stays inside its own limits, needs the shipped seam
light to bring the seam on target, never waives hue, and is still needed (a stale waiver fails here). The test reads the
real plates and the shipped seam light and writes no file.
"""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('plate_audit', ROOT / 'tools/environment/audit_site7_plate_lighting.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
wl = audit.wl

MISSION = 'MIS_CH01_08'
WAIVED = {('S8_C01', 'R01_GATE'), ('S8_C03', 'R04_JUNCTION'), ('S8_C05', 'R05_TERMINAL')}


def named(rows, field):
    """(plate, room) of every seam row that has entries in `field` ('problems' or 'waived')."""
    return {(audit.plate_id(row['asset']), row['room']) for row in rows if row.get(field)}


class SeamWaivers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        art, layouts, floors = wl.load(wl.ART), wl.load(wl.LAYOUTS), wl.load(wl.PLATE_FLOORS)['plates']
        cls.solved = wl.solve(MISSION, art, layouts, floors)
        with patch.object(audit, 'SEAM_WAIVERS', {}):
            cls.raw = audit.seams(cls.solved, MISSION)

    def seams(self, waivers=None, mission=MISSION):
        with patch.object(audit, 'SEAM_WAIVERS', audit.SEAM_WAIVERS if waivers is None else waivers):
            return audit.seams(self.solved, mission)

    def test_the_list_names_only_the_three_operation_8_seams(self):
        self.assertEqual({key[1:] for key in audit.SEAM_WAIVERS}, WAIVED)
        self.assertEqual({key[0] for key in audit.SEAM_WAIVERS}, {MISSION})

    def test_the_waived_seams_pass_and_nothing_else_is_off_target(self):
        rows = self.seams()
        self.assertEqual(named(rows, 'problems'), set())
        self.assertEqual(named(rows, 'waived'), WAIVED)

    def test_without_the_waivers_exactly_these_seams_fail(self):
        # Also the stale-waiver guard: once a deck is repainted inside the targets, its waiver must go.
        self.assertEqual(named(self.raw, 'problems'), WAIVED)

    def test_a_waiver_needs_its_mission_plate_and_room(self):
        moved = {
            'mission': {('MIS_CH01_07',) + key[1:]: limits for key, limits in audit.SEAM_WAIVERS.items()},
            'plate': {(key[0], 'S8_C02', key[2]): limits for key, limits in audit.SEAM_WAIVERS.items()},
            'room': {(key[0], key[1], 'R03_TOWER'): limits for key, limits in audit.SEAM_WAIVERS.items()},
        }
        for what, waivers in moved.items():
            with self.subTest(moved=what):
                self.assertEqual(named(self.seams(waivers), 'problems'), WAIVED)
        # Asked as another mission (or none) the seam light of MIS_CH01_08 stays available, so only the key can refuse.
        real_light = audit.shipped_light
        with patch.object(audit, 'shipped_light', side_effect=lambda mission, index: real_light(MISSION, index)):
            for asked in ('MIS_CH01_07', ''):
                with self.subTest(asked=asked or 'no mission id'):
                    self.assertEqual(named(audit.seams(self.solved, asked), 'problems'), WAIVED)

    def test_a_waiver_stops_at_its_own_limits(self):
        for row in self.raw:
            key = (MISSION, audit.plate_id(row['asset']), row['room'])
            if key[1:] not in WAIVED:
                continue
            wide = {'step': 1.0, 'saturation_ratio': 9.0}
            for field, measured in (('saturation_ratio', row['saturation_ratio']), ('step', abs(row['step']))):
                if field == 'step' and measured <= audit.SEAM_STEP_MAX:
                    continue  # only the seam that misses the step target has a step limit
                with self.subTest(seam=key[1:], field=field):
                    tight = self.seams({key: {**wide, field: measured - 0.005}})
                    self.assertIn(key[1:], named(tight, 'problems'))
                    self.assertTrue(any(p.startswith('past its waiver') for r in tight for p in r['problems']))
                    loose = self.seams({key: {**wide, field: measured + 0.005}})
                    self.assertNotIn(key[1:], named(loose, 'problems'))

    def test_the_shipped_limits_are_a_little_above_what_is_measured(self):
        for row in self.raw:
            key = (MISSION, audit.plate_id(row['asset']), row['room'])
            if key[1:] in WAIVED:
                limits = audit.SEAM_WAIVERS[key]
                self.assertLess(row['saturation_ratio'], limits['saturation_ratio'], key)
                self.assertLess(limits['saturation_ratio'], row['saturation_ratio'] * 1.10, key)
                if 'step' in limits:
                    self.assertLess(abs(row['step']), limits['step'], key)
                    self.assertLess(limits['step'], abs(row['step']) * 1.15, key)

    def test_the_shipped_seam_light_brings_each_waived_seam_on_target(self):
        rows = [row for row in self.seams() if row.get('waived')]
        self.assertEqual(len(rows), 3)
        for row in rows:
            lit = row['with_seam_light']
            self.assertLessEqual(abs(lit['step']), audit.SEAM_STEP_MAX, row['asset'])
            self.assertLessEqual(lit['saturation_ratio'], audit.SEAM_SAT_RATIO, row['asset'])

    def test_a_waiver_fails_when_the_seam_light_is_missing_or_does_nothing(self):
        with patch.object(audit, 'shipped_light', return_value=None):
            rows = self.seams()
            self.assertEqual(named(rows, 'problems'), WAIVED)
            self.assertTrue(any('no seam light ships' in p for r in rows for p in r['problems']))
        identity = np.ones((wl.LIGHT_GRID[1], wl.LIGHT_GRID[0], 2), np.float32)
        with patch.object(audit, 'shipped_light', return_value=identity):
            rows = self.seams()
            self.assertEqual(named(rows, 'problems'), WAIVED)
            self.assertTrue(any(p.startswith('with the seam light') for r in rows for p in r['problems']))

    def test_the_seam_targets_themselves(self):
        # brightness step in stops, deck / room saturation and hue in degrees, as measured on a seam
        self.assertEqual(audit.seam_problems(0.34, 0.10, 0.10, 140, 140), [])
        self.assertEqual(len(audit.seam_problems(-0.36, 0.10, 0.10, 140, 140)), 1)
        self.assertEqual(len(audit.seam_problems(0.0, 0.07, 0.15, 140, 140)), 1)   # 1.9x with one side coloured
        self.assertEqual(audit.seam_problems(0.0, 0.05, 0.14, 140, 140), [])       # both grey: no ratio
        self.assertEqual(audit.seam_problems(0.0, 0.17, 0.20, 140, 140), [])
        self.assertEqual(len(audit.seam_problems(0.0, 0.20, 0.20, 140, 200)), 1)   # 60 degrees apart
        self.assertEqual(audit.seam_problems(0.0, 0.05, 0.20, 140, 250, ratio_limit=9.0), [])  # a grey has no hue

    def test_hue_is_never_waived(self):
        wide = audit.seam_problems(0.0, 0.20, 0.20, 140, 200, step_limit=9.0, ratio_limit=9.0)
        self.assertEqual(len(wide), 1)
        self.assertIn('hue', wide[0])


if __name__ == '__main__':
    unittest.main()
