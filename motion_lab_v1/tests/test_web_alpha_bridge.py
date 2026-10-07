import hashlib
import json
from pathlib import Path

import numpy as np
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

import sys
LAB = Path(__file__).resolve().parents[1]
# Package imports need the repository root; the modules' own flat imports need LAB.
sys.path[:0] = [str(LAB.parent), str(LAB)]

from motion_lab_v1 import web_alpha_bridge as bridge


def _green_png(path: Path, size=(32, 24)):
    pixels = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    pixels[:, :] = (0, 255, 0)
    pixels[6:18, 10:22] = (40, 55, 70)
    Image.fromarray(pixels, mode='RGB').save(path, format='PNG')


class WebAlphaBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'motion_lab_v1'
        self.project = self.root.parent
        quarantine = self.root / 'qa' / 'site7_rifle' / 'quarantine' / 'green'
        quarantine.mkdir(parents=True)
        self.quarantine = quarantine
        self.root_patch = patch.object(bridge, 'ROOT', self.root)
        self.project_patch = patch.object(bridge, 'PROJECT', self.project)
        self.root_patch.start()
        self.project_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.addCleanup(self.project_patch.stop)

    def test_green_master_is_bridge_only_and_unchanged(self):
        quarantine = self.quarantine
        source = quarantine / 'S_walk_0_green.png'
        _green_png(source)
        before = hashlib.sha256(source.read_bytes()).hexdigest()

        facts = bridge.inspect_green_master(source)

        self.assertEqual(facts['status'], 'GREEN_BRIDGE_INPUT_ONLY')
        self.assertFalse(facts['directIntakeAllowed'])
        self.assertFalse(facts['localKeyingAllowed'])
        self.assertGreater(facts['greenPixelFraction'], 0.8)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)

    def test_non_green_source_is_rejected(self):
        quarantine = self.quarantine
        source = quarantine / 'not_green.png'
        Image.new('RGB', (16, 16), (18, 28, 38)).save(source, format='PNG')

        with self.assertRaisesRegex(ValueError, 'GREEN_CORNERS'):
            bridge.inspect_green_master(source)

    def test_generator_perturbed_green_is_still_quarantine_only(self):
        source = self.quarantine / 'near_green.png'
        pixels = np.zeros((24, 32, 3), dtype=np.uint8)
        pixels[:, :] = (20, 241, 18)
        pixels[6:18, 10:22] = (40, 55, 70)
        Image.fromarray(pixels, mode='RGB').save(source, format='PNG')

        facts = bridge.inspect_green_master(source)

        self.assertEqual(facts['backgroundUniformity'], 'NEAR_GREEN_NON_UNIFORM')
        self.assertEqual(facts['exactGreenPixelFraction'], 0.0)
        self.assertFalse(facts['directIntakeAllowed'])

    def test_manifest_binds_quarantined_source_and_actual_response(self):
        project_root, quarantine = self.project, self.quarantine
        source = quarantine / 'S_walk_0_green.png'
        response = project_root / 'qa' / 'site7_rifle' / 'handoffs' / 'actual-response.json'
        output = project_root / 'qa' / 'site7_rifle' / 'handoffs' / 'web-alpha-bridge.json'
        response.parent.mkdir(parents=True)
        _green_png(source)
        response.write_text(json.dumps({'tool': 'chatgpt.web', 'conversation': 'existing'}), encoding='utf-8')

        manifest = bridge.make_manifest(
            'site7_rifle', 'S/walk/0', source, response,
            reference_order=['motion_lab_v1/art/site7_rifle/identity_reference.png',
                             'motion_lab_v1/reference/ual_guides/S_Walk_Loop_0.png'],
        )

        self.assertEqual(manifest['status'], 'WEB_ALPHA_BRIDGE_ONLY')
        self.assertFalse(manifest['directIntakeAllowed'])
        self.assertEqual(manifest['actualToolResponse']['sha256'], hashlib.sha256(response.read_bytes()).hexdigest())
        self.assertTrue(manifest['referenceOrder'][0].endswith('identity_reference.png'))
        output.write_text(json.dumps(manifest), encoding='utf-8')
        self.assertEqual(json.loads(output.read_text(encoding='utf-8'))['source']['status'], 'GREEN_BRIDGE_INPUT_ONLY')

    def test_source_outside_quarantine_is_rejected(self):
        project_root, quarantine = self.project, self.quarantine
        source = project_root / 'green.png'
        response = quarantine / 'response.json'
        _green_png(source)
        response.write_text('{}', encoding='utf-8')

        with self.assertRaisesRegex(ValueError, 'QUARANTINE'):
            bridge.make_manifest('site7_rifle', 'S/walk/0', source, response)


if __name__ == '__main__':
    unittest.main()
