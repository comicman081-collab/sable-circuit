"""Reject forged/stale existing-art review envelopes using actual reply files."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
import source_art_intake as intake


class ExistingSourceReviewTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / 'artifacts/technical_tests/source_art_intake'
        scratch.mkdir(parents=True, exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.directory.cleanup)
        self.subject = 'a' * 64
        self.rows = []
        for index, role in enumerate(('visual', 'Ponytail FULL')):
            row = dict(subject_sha256=self.subject, verdict='PASS',
                       checks={key: 'PASS' for key in intake.CHECKS},
                       role=role, reviewer=f'test reviewer {index}',
                       reviewed_utc='2026-09-08T00:00:00Z')
            self.rows.append(row)
            self.write_reply(index, row)

    def write_reply(self, index, actual):
        path = Path(self.directory.name) / f'synthetic_reply_{index}.json'
        content = {key: value for key, value in actual.items() if key != 'reply_evidence'}
        content['synthetic_fixture_not_production_review'] = True
        path.write_text(json.dumps(content), encoding='utf-8')
        self.rows[index]['reply_evidence'] = intake.g.ref(path)

    def test_matching_distinct_replies(self):
        self.assertEqual([], intake.verify_intake_reviews(self.rows, self.subject))

    def test_inline_pass_cannot_hide_actual_hold(self):
        actual = copy.deepcopy(self.rows[0])
        actual['verdict'] = 'HOLD'
        self.write_reply(0, actual)
        self.assertIn('ACTUAL_REVIEW_REPLY_MISMATCH:verdict',
                      intake.verify_intake_reviews(self.rows, self.subject))

    def test_reply_for_another_asset_is_rejected(self):
        actual = copy.deepcopy(self.rows[1])
        actual['subject_sha256'] = 'b' * 64
        self.write_reply(1, actual)
        self.assertIn('ACTUAL_REVIEW_REPLY_MISMATCH:subject_sha256',
                      intake.verify_intake_reviews(self.rows, self.subject))

    def test_one_reviewer_cannot_fill_both_roles(self):
        self.rows[1]['reviewer'] = '  TEST REVIEWER 0  '
        self.write_reply(1, self.rows[1])
        self.assertIn('DISTINCT_REVIEWERS_REQUIRED',
                      intake.verify_intake_reviews(self.rows, self.subject))

    def test_naive_timestamp_is_rejected(self):
        self.rows[0]['reviewed_utc'] = '2026-09-08T00:00:00'
        self.write_reply(0, self.rows[0])
        self.assertIn('REVIEW_UTC_REQUIRED',
                      intake.verify_intake_reviews(self.rows, self.subject))

    def test_actual_check_cannot_be_replaced_inline(self):
        actual = copy.deepcopy(self.rows[1])
        actual['checks']['anatomical_landmarks'] = 'HOLD'
        self.write_reply(1, actual)
        self.assertIn('ACTUAL_REVIEW_REPLY_MISMATCH:checks',
                      intake.verify_intake_reviews(self.rows, self.subject))

    def test_reply_bytes_cannot_change_after_binding(self):
        path = intake.g.resolve(self.rows[0]['reply_evidence'])
        path.write_text('{}', encoding='utf-8')
        with self.assertRaises(ValueError):
            intake.verify_intake_reviews(self.rows, self.subject)


if __name__ == '__main__':
    unittest.main()
