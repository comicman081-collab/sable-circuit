import copy
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import existing_frame_derivative_admission as admission
import visible_frame_harness_current as current

class ExistingFrameAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.path=ROOT/'artifacts/quarantine/generation_diagnostics/mica_r6_alpha_protection_r01/ADMISSION_MANIFEST.json'

    def altered(self,filename,change):
        read=g.read
        def replacement(path):
            data=read(path)
            if Path(path).name==filename:
                data=copy.deepcopy(data);change(data)
            return data
        return patch.object(g,'read',side_effect=replacement)

    def test_exact_corrected_frame_is_still_review_hold(self):
        result=admission.audit(self.path)
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['verdict'],'HOLD_VISIBLE_FRAME_REVIEW')
        self.assertFalse(result['new_generation_authorized'])
        self.assertTrue(result['request']['path'].endswith('REQUEST_R2.json'))

    def test_second_generation_is_rejected(self):
        with self.altered('ADMISSION_MANIFEST.json',lambda d:d.update(new_generation_authorized=True)):
            self.assertIn('DERIVATIVE_ADMISSION_NOT_A_GENERATION_PERMIT',admission.audit(self.path)['errors'])

    def test_mixed_schema_cannot_drop_admission_review_checks(self):
        with self.altered('ADMISSION_MANIFEST.json',lambda d:d.update(frame_validation_contract=g.ref(current.phase_frame.PHASE_CONTRACT))):
            current.install_current_patches()
            self.assertIn('ADMISSION_AND_NEW_FRAME_SCHEMAS_MUST_NOT_MIX',current.frozen.audit_frame(self.path)['errors'])

    def test_changed_phase_cannot_borrow_authorization(self):
        with self.altered('ADMISSION_MANIFEST.json',lambda d:d.update(phase='contact_r')):
            self.assertIn('DERIVATIVE_CANNOT_CHANGE_POSE_SCOPE',admission.audit(self.path)['errors'])

    def test_missing_historical_dependency_is_rejected(self):
        def change(d):d['files'].pop(next(iter(d['files'])))
        with self.altered('AUTHORIZATION_ARCHIVE.json',change):
            self.assertTrue(admission.audit(self.path)['errors'])

    def test_original_permit_cannot_be_expanded(self):
        archive=g.read(g.resolve(g.read(self.path)['authorization_archive']))
        name=Path(archive['original_permit']['path']).name
        with self.altered(name,lambda d:d.update(max_outputs=2)):
            self.assertIn('ORIGINAL_SINGLE_ATTEMPT_PERMIT_REQUIRED',admission.audit(self.path)['errors'])

    def test_stale_derivative_code_is_rejected(self):
        with self.altered('DERIVATIVE_QA.json',lambda d:d['generator'].update(sha256='0'*64)):
            self.assertIn('EXACT_CURRENT_DERIVATIVE_RECEIPT_REQUIRED',admission.audit(self.path)['errors'])

    def test_current_shared_frame_entrypoint_routes_admission(self):
        current.install_current_patches()
        result=current.frozen.audit_frame(self.path)
        self.assertEqual(result['admission_stage'],admission.STAGE)
        self.assertEqual(result['errors'],[])

    def test_original_review_reply_is_resolved_and_bound(self):
        result=admission.audit(self.path)
        review=g.read(g.resolve(g.read(self.path)['mask_scope_review']))
        reply=review['reply_evidence']
        self.assertEqual(result['bindings'][reply['path']],reply['sha256'])
        resolve=g.resolve
        def rejected(ref):
            if ref==reply:raise ValueError('REVIEW_REPLY_CHANGED')
            return resolve(ref)
        with patch.object(g,'resolve',side_effect=rejected):
            self.assertIn('REVIEW_REPLY_CHANGED',admission.audit(self.path)['errors'])

    def test_current_consumed_code_and_contract_are_bound(self):
        before=admission.audit(self.path)
        for name in ['visible_frame_contract.json','visible_frame_harness.py','generation_harness.py',
                     'derive_chroma_runtime_rgba.py','normalize_imagegen_chroma.py']:
            rel='tools/character_pipeline/'+name
            self.assertEqual(before['bindings'][rel],g.sha(ROOT/rel))
        sha=g.sha
        def changed(path):
            return '0'*64 if g.local(path)==ROOT/'tools/character_pipeline/visible_frame_contract.json' else sha(path)
        with patch.object(g,'sha',side_effect=changed):
            self.assertNotEqual(before['subject_sha256'],admission.audit(self.path)['subject_sha256'])

    def test_review_coordinates_must_match_actual_mask(self):
        def change(d):d['incorrectly_removed_subject_components'][0]['pixel_coordinates_xy'][0]=[0,0]
        with self.altered('PONYTAIL_FULL_REVIEW.json',change):
            self.assertIn('MASK_MUST_EQUAL_EXACT_INDEPENDENTLY_REVIEWED_PIXELS',admission.audit(self.path)['errors'])

    def test_known_archive_and_original_frame_subject_are_pinned(self):
        with self.altered('ADMISSION_MANIFEST.json',lambda d:d['authorization_archive'].update(sha256='0'*64)):
            self.assertIn('EXACT_R6_AUTHORIZATION_ARCHIVE_REQUIRED',admission.audit(self.path)['errors'])
        with self.altered('FRAME_AUDIT.json',lambda d:d.update(subject_sha256='0'*64)):
            self.assertIn('EXACT_HISTORICAL_REPRODUCTION_REQUIRED',admission.audit(self.path)['errors'])

    def test_seal_cannot_reuse_only_old_frame_checks(self):
        current.install_current_patches()
        read=g.read;bundle_path=ROOT/'tests/test_existing_frame_admission.py'
        fake={'frame_manifest':g.ref(self.path),'reviews':[]}
        def fixture_read(path):return fake if g.local(path)==bundle_path else read(path)
        with patch.object(g,'read',side_effect=fixture_read):
            with self.assertRaisesRegex(ValueError,'EXISTING_FRAME_ADMISSION_NOT_APPROVED'):
                current.frozen.seal_frame(bundle_path)

if __name__=='__main__':unittest.main()
