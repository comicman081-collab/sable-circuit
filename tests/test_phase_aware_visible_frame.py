"""In-memory fixtures only; no permits or review receipts are manufactured."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import phase_aware_visible_frame as p


class PhaseFrameTests(unittest.TestCase):
    def test_support_phases_are_not_forced_into_wide_contact_silhouettes(self):
        for motion,phase in [('run','down_l'),('run','passing_l'),('run','down_r'),('run','passing_r'),('walk','up_l')]:
            self.assertFalse(p.stride_floor_applies('E',motion,phase))
        for phase in ['contact_l','contact_r','flight_l','flight_r']:
            self.assertTrue(p.stride_floor_applies('E','run',phase))
            self.assertTrue(p.stride_floor_applies('W','run',phase))
        self.assertFalse(p.stride_floor_applies('S','run','contact_l'))

    def fixture(self, mutate=None, repaint=False):
        # Exercise actual native source/normalization/derivative pixels, with a
        # deliberately mocked request audit and in-memory permit. This is not
        # a way to generate, seal or authorize an existing production frame.
        base=ROOT/'art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r6_e_contact_l_semantic_pose_primary'
        corrected=ROOT/'artifacts/quarantine/generation_diagnostics/mica_r6_alpha_protection_r01'
        manifest=copy.deepcopy(g.read(base/'FRAME_MANIFEST.json'))
        request=copy.deepcopy(g.read(g.resolve(manifest['request'])))
        request['output_root']='.'
        request['frame_validation_contract']=g.ref(p.PHASE_CONTRACT)
        manifest.update(frame_validation_contract=g.ref(p.PHASE_CONTRACT),runtime_matting_policy='explicit_reviewed_interior_subject_protection',
                        runtime_rgba=g.ref(corrected/'RUNTIME_RGBA.png'),runtime_rgba_qa=g.ref(corrected/'DERIVATIVE_QA.json'),
                        protection_mask=g.ref(corrected/'PROTECT_KNEE_INSETS.png'))
        if mutate:mutate(manifest)
        permit={'schema':1,'stage':'visible_frame_attempt','verdict':'RESERVED_SINGLE_IMAGEGEN_FRAME_ATTEMPT',
                'request':manifest['request'],'request_subject_sha256':'unit-test-only',
                'output_root':'.','expected_raw_path':request['expected_raw_path'],'max_outputs':1}
        read=g.read;pixels=g.pixels;local=g.local
        # Input files occupy two real candidate roots. Mock only the virtual
        # fixture root; production g.local still forbids repository-root jobs.
        def fixture_local(path):return ROOT if path=='.' else local(path)
        def fixture_read(path):
            path=g.local(path)
            if path==base/'FRAME_MANIFEST.json':return manifest
            if path==g.local(manifest['request']['path']):return request
            if path==g.local(manifest['attempt_permit']['path']):return permit
            return read(path)
        def fixture_pixels(path):
            value=pixels(path)
            if repaint and g.local(path)==corrected/'RUNTIME_RGBA.png':
                value=value.copy();value[500,800,0]^=1
            return value
        with patch.object(g,'read',side_effect=fixture_read),patch.object(g,'pixels',side_effect=fixture_pixels),patch.object(g,'local',side_effect=fixture_local):
            return p.audit_frame(base/'FRAME_MANIFEST.json',lambda _: {'errors':[],'bindings':{},'subject_sha256':'unit-test-only'})

    def test_exact_protected_rgba_reproduces_and_stays_review_hold(self):
        result=self.fixture()
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['verdict'],'HOLD_VISIBLE_FRAME_REVIEW')
        for source in p.consumed_code():
            self.assertEqual(result['bindings'][source.relative_to(ROOT).as_posix()],g.sha(source))

    def test_visible_rgb_repaint_is_rejected(self):
        self.assertIn('VISIBLE_FRAME_RUNTIME_RGBA_NOT_REPRODUCIBLE',self.fixture(repaint=True)['errors'])

    def test_undeclared_protection_is_rejected(self):
        result=self.fixture(lambda m:m.update(runtime_matting_policy='connected_chroma_green_costume_excludes_chroma_green'))
        self.assertIn('VISIBLE_FRAME_RUNTIME_RGBA_NOT_REPRODUCIBLE',result['errors'])

    def test_contract_cannot_be_added_only_after_generation(self):
        result=self.fixture(lambda m:m['frame_validation_contract'].update(sha256='0'*64))
        self.assertIn('EXACT_PREGENERATION_PHASE_FRAME_CONTRACT_REQUIRED',result['errors'])


if __name__=='__main__':unittest.main()
