"""Synthetic images only: enforce the user's native-alpha admission rule."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import character_workflow as w
import intake_frame
import intake_pair
import intake_derived_frame
import source_alpha_policy as policy


class SourceAlphaTests(unittest.TestCase):
    def setUp(self):
        base = LAB / 'qa/technical_tests'
        base.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix='native_alpha_', dir=base))
        self.addCleanup(shutil.rmtree, self.root, True)
        for module in (w, intake_frame, intake_pair):
            p = patch.object(module, 'ROOT', self.root)
            p.start()
            self.addCleanup(p.stop)
        self.art = self.root / 'art/fixture'
        self.art.mkdir(parents=True)
        self.master = self.art / 'returned.png'
        self.proof = self.art / 'actual-response-fixture.json'
        self.image = Image.new('RGBA', (1024, 1536), (0, 0, 0, 0))
        self.image.paste((70, 80, 90, 254), (260, 100, 760, 1450))
        self.image.putpixel((260, 100), (70, 80, 90, 127))
        self.config = {'id': 'fixture', 'source': 'art/fixture', 'workflowVersion': 1,
                       'identityReference': 'art/fixture/returned.png',
                       'clips': {'idle': {'frames': 1}, 'walk': {'frames': 6}}}
        self.publish(self.image)

    def publish(self, image):
        image.save(self.master)
        returned = str((self.root / 'technical-fixture-returned.png').resolve())
        w.write(self.proof, {'tool': 'image_gen.imagegen', 'returnedPath': returned,
                            'result': {'output_hint': 'Synthetic test, no provider invocation: ' + returned},
                            'projectCopy': 'art/fixture/returned.png',
                            'projectCopySHA256': w.sha(self.master)})
        self.config['referenceSHA256'] = w.sha(self.master)
        w.write(self.root / 'characters/fixture.json', self.config)

    def test_native_alpha_0_to_254_passes_without_mutation(self):
        before = self.master.read_bytes()
        result = policy.inspect_master(self.master)
        self.assertEqual((result['alphaMin'], result['alphaMax']), (0, 254))
        self.assertEqual(result['status'], 'PASS_ALPHA_FORMAT_ONLY')
        self.assertFalse(result['visualApproved'])
        self.assertEqual(self.master.read_bytes(), before)

    def test_generation_references_must_be_project_owned(self):
        outside = self.root.parent / 'other-project-reference.png'
        Image.new('RGBA', (8, 8), (0, 0, 0, 0)).save(outside)
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        with self.assertRaisesRegex(ValueError, 'PROJECT_REFERENCE_REQUIRED'):
            policy.validate_request_references(
                {'reference': str(outside)}, self.root.parent / 'sable-project')
        owned = self.root / 'owned-reference.png'
        Image.new('RGBA', (8, 8), (0, 0, 0, 0)).save(owned)
        self.assertTrue(policy.validate_request_references(
            {'reference': 'owned-reference.png'}, self.root))

    def test_rgb_checkerboard_and_green_are_rejected(self):
        for color in ((180, 180, 180), (0, 255, 0)):
            self.publish(Image.new('RGB', (1024, 1536), color))
            with self.assertRaisesRegex(ValueError, 'actual RGBA'):
                policy.inspect_master(self.master)

    def test_native_alpha_255_interior_passes_without_mutation(self):
        # The user allowed alpha-255 interiors on 2026-09-28.
        self.image.paste((70, 80, 90, 255), (300, 200, 700, 1300))
        self.publish(self.image)
        before = self.master.read_bytes()
        result = policy.inspect_master(self.master)
        self.assertEqual((result['alphaMin'], result['alphaMax']), (0, 255))
        self.assertEqual(result['status'], 'PASS_ALPHA_FORMAT_ONLY')
        self.assertEqual(self.master.read_bytes(), before)

    def test_uniform_opaque_canvas_does_not_fake_transparency(self):
        for a in (254, 255):
            self.publish(Image.new('RGBA', (1024, 1536), (150, 150, 150, a)))
            with self.assertRaisesRegex(ValueError, 'TRANSPARENT_BACKGROUND'):
                policy.inspect_master(self.master)

    def test_single_transparent_pixel_is_not_a_background(self):
        image = Image.new('RGBA', (1024, 1536), (150, 150, 150, 254))
        image.putpixel((0, 0), (0, 0, 0, 0))
        self.publish(image)
        with self.assertRaisesRegex(ValueError, 'TRANSPARENT_BACKGROUND'):
            policy.inspect_master(self.master)

    def test_empty_or_translucent_body_is_rejected(self):
        for a in (0, 128):
            image = Image.new('RGBA', (1024, 1536))
            image.paste((70, 80, 90, a), (260, 100, 760, 1450))
            self.publish(image)
            with self.assertRaisesRegex(ValueError, 'SUBJECT_OPACITY'):
                policy.inspect_master(self.master)

    def test_intake_accepts_native_original_without_approving_art(self):
        target = intake_frame.intake('fixture', 'E', 'idle', 0, self.master, self.proof)
        self.assertEqual(target.read_bytes(), self.master.read_bytes())
        row = next(row for row in w.source_status('fixture')['slots'] if row['slot'] == 'E/idle/0')
        self.assertEqual(row['state'], 'needs_review')
        self.assertFalse((self.root / 'qa/fixture/source_reviews.json').exists())

    def test_bad_single_intake_preserves_old_slot(self):
        target = self.art / 'E_idle_0_master.png'
        target.write_bytes(b'protected old slot')
        self.publish(Image.new('RGB', (1024, 1536), (0, 255, 0)))
        with self.assertRaisesRegex(ValueError, 'NATIVE_ALPHA_REQUIRED'):
            intake_frame.intake('fixture', 'E', 'idle', 0, self.master, self.proof)
        self.assertEqual(target.read_bytes(), b'protected old slot')

    def test_bad_pair_rejected_before_any_copy(self):
        self.publish(Image.new('RGB', (1536, 1024), (0, 255, 0)))
        with self.assertRaisesRegex(ValueError, 'NATIVE_ALPHA_REQUIRED'):
            intake_pair.intake('fixture', 'E', 'walk', 0, self.master, self.proof)
        self.assertFalse((self.art / 'gait_v8').exists())
        self.assertFalse((self.art / 'E_walk_0_master.png').exists())

    def test_legacy_green_intake_is_closed_before_any_write(self):
        with self.assertRaisesRegex(ValueError, 'new green/chroma derivative intake is disabled'):
            intake_derived_frame.intake('fixture', 'E', 'walk', 0,
                                       self.master, self.master, self.proof, self.master, self.master)
        self.assertFalse((self.art / 'E_walk_0_master.png').exists())

    def test_manual_unapproved_green_slot_cannot_bypass_review_gate(self):
        self.publish(Image.new('RGB', (1024, 1536), (0, 255, 0)))
        target = self.art / 'E_idle_0_master.png'
        target.write_bytes(self.master.read_bytes())
        w.write(target.with_suffix('.source.json'), {
            'generator': 'Codex built-in ImageGen', 'sha256': w.sha(target),
            'destination': str(target.relative_to(self.root)),
            'toolResponse': w.binding(self.proof), 'sourceMaster': w.binding(self.master)})
        row = next(row for row in w.source_status('fixture')['slots'] if row['slot'] == 'E/idle/0')
        self.assertEqual(row['state'], 'source_alpha_repair')
        with self.assertRaisesRegex(ValueError, 'provenance/readiness'):
            w.review_source('fixture', 'E/idle/0', 'approved', str(target), 'synthetic fixture only', 'unit test')


if __name__ == '__main__':
    unittest.main()
