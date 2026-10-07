import copy
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import semantic_laterality_guide as s


class SemanticGuideTests(unittest.TestCase):
    def setUp(self):
        self.guide=g.read(ROOT/'art_src/motion_reference/tripo_run_20260908/pose_guide_r01/E_CONTACT_L_GUIDE_DRAFT.json')
        self.path=ROOT/'art_src/motion_reference/tripo_run_20260908/pose_guide_r02/SEMANTIC_GUIDE_DRAFT.json'

    def test_geometry_cannot_substitute_for_independent_reviews(self):
        errors,_=s.audit(g.ref(self.path),self.guide,'E','run','contact_l')
        self.assertIn('EXACT_SEMANTIC_GUIDE_AND_INDEPENDENT_REVIEWS_REQUIRED',errors)

    def test_changed_sole_array_is_rejected_even_with_valid_file_hashes(self):
        read=g.read
        def changed(path):
            data=read(path)
            if Path(path).name=='GEOMETRY.json':
                data=copy.deepcopy(data);data['actual_sole_vertices_world_m']['left'][0][2]+=.01
            return data
        with patch.object(g,'read',side_effect=changed):
            errors,_=s.audit(g.ref(self.path),self.guide,'E','run','contact_l')
        self.assertIn('SEMANTIC_GUIDE_CHANGED_EXACT_POSE_OR_SOLES',errors)

    def test_other_phase_cannot_borrow_labels(self):
        errors,_=s.audit(g.ref(self.path),self.guide,'E','run','contact_r')
        self.assertIn('SEMANTIC_GUIDE_PHASE_MISMATCH',errors)
        self.assertIn('SEMANTIC_GUIDE_PHASE_MISMATCH',errors)

    def test_closure_binds_actual_colored_geometry_and_generator(self):
        files=s.bindings(g.read(self.path),self.guide)
        self.assertIn('tools/character_pipeline/capture_tripo_laterality_guide.py',files)
        self.assertIn('artifacts/quarantine/generation_diagnostics/tripo_laterality_guide_r01/ANNOTATED_CONTACT_L_1920.png',files)
        self.assertIn('artifacts/quarantine/generation_diagnostics/tripo_support_anchor_r02/TRIPO_SUPPORT_ANCHORED_REFERENCE.blend',files)

    def test_inline_reviews_bind_their_reply_evidence(self):
        # Isolated mock of the shared review verifier, never a production reply.
        read=g.read; evidence=g.ref(Path(__file__))
        manifest=read(self.path);manifest['review_bundle']=evidence
        bundle={'subject_sha256':s.subject(manifest,self.guide),'reviews':[{'reply_evidence':evidence}]}
        def fixture_read(path):
            if g.local(path)==self.path:return copy.deepcopy(manifest)
            if g.local(path)==Path(__file__).resolve():return copy.deepcopy(bundle)
            return read(path)
        with patch.object(g,'read',side_effect=fixture_read),patch.object(g,'verify_reviews',return_value=[]) as verifier:
            errors,files=s.audit(g.ref(self.path),self.guide,'E','run','contact_l')
        self.assertEqual(errors,[])
        verifier.assert_called_once()
        self.assertIn(evidence['path'],files)


if __name__=='__main__':unittest.main()
