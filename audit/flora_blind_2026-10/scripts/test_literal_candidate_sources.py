"""Exercise candidate validation/integration against the actual source bytes."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import evidence_followup_controller as controller
import integrate_candidate_reviews as integrator


class LiteralCandidateSources(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.followup = self.root / 'evidence_followup'
        for folder in ['texts', 'adjudications', 'evidence_followup/candidate_reviews',
                       'evidence_followup/candidate_requests']:
            (self.root / folder).mkdir(parents=True)
        self.source = self.root / 'texts/abc.txt'
        self.source.write_bytes(b'First line.\r\nSecond line.\r\n')
        self.original = self.source.read_bytes()
        self.decision = dict(request_id='request', file_key='abc', target_index=0,
                             field='missing_row', method='argon', verdict='undeterminable',
                             corrected_value=None, quote='First line.\r\nSecond line.',
                             location='Abstract', reason='Original identity is unavailable.')
        self.write('candidate_requests/index.json', [dict(request_id='request', review_id='review',
                   review_attempts=2, status='expert_review_complete_pending_parent')])
        self.write('candidate_reviews/review.input.json', dict(requests=[dict(
            request_id='request', file_key='abc', source_path=str(self.source),
            requested_fields=[dict(target_index=0, field='missing_row')])]))
        self.write('candidate_reviews/parent_inspection.json', dict(reviews=dict(review=dict(
            status='approved', approved_keys=[['abc', 0]], reason='Primary source inspected.'))))
        self.addCleanup(patch.stopall)
        for module in [controller, integrator]:
            patch.object(module, 'R', self.root).start()
            patch.object(module, 'F', self.followup).start()

    def write(self, relative, value):
        (self.followup / relative).write_text(json.dumps(value))

    def test_exact_crlf_quote_passes_controller(self):
        self.write('candidate_reviews/review.result.json', dict(decisions=[self.decision]))
        result = controller.validate_candidate_review('review')
        self.assertEqual(result['mechanically_valid'], 1)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_changed_line_endings_are_rejected(self):
        self.decision['quote'] = self.decision['quote'].replace('\r\n', '\n')
        self.write('candidate_reviews/review.result.json', dict(decisions=[self.decision]))
        self.assertEqual(controller.validate_candidate_review('review')['mechanically_valid'], 0)

    def test_parent_integration_preserves_exact_quote_and_source(self):
        self.write('candidate_reviews/review.validation.json', dict(valid_envelope=True, records=[dict(
            decision=self.decision, mechanically_valid=True,
            source_sha256=hashlib.sha256(self.original).hexdigest())]))
        self.assertEqual(integrator.integrate()['approved_rechecks_or_additions'], 1)
        actual = json.loads((self.root / 'adjudications/abc.json').read_text())['decisions'][0]
        self.assertEqual(actual['quote'].encode(), b'First line.\r\nSecond line.')
        self.assertEqual(self.source.read_bytes(), self.original)


if __name__ == '__main__':
    unittest.main()
