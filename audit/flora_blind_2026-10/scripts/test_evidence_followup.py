"""Guard failures that could incorrectly add/exclude missing originals."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import evidence_followup_controller as ctl


class OmissionEvidenceGuards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.f = self.root / 'followup'
        for name in ('luna/results', 'luna/batches'):
            (self.f / name).mkdir(parents=True)
        self.addCleanup(patch.stopall)
        patch.object(ctl, 'F', self.f).start()
        patch.object(ctl, 'R', self.root).start()
        self.source = self.root / 'source.txt'
        self.source.write_text('We replicated Smith (2001). Smith (2001), Prior empirical finding.\n')
        self.input = self.f / 'luna/batches/luna_0000.input.json'
        self.work = {'file_key': 'abc', 'work_key': '10.1234/retest',
                     'text_path': str(self.source), 'coding_path': 'coding.json',
                     'prior_adjudication_path': 'prior.json', 'source_instruction': 'Read source',
                     'shipped_originals': [{'input_row_index': '1', 'doi_o': '10.1234/other'}],
                     'candidates': [{'target_index': 0, 'previous_final_verdict': 'unverified', 'blind_target': {}}]}
        self.input.write_text(json.dumps({'works': [self.work]}))
        self.output = self.f / 'luna/results/luna_0000.json'
        self.index = self.f / 'luna/index.json'
        self.index.write_text(json.dumps([{'batch_id': 'luna_0000', 'input_path': str(self.input),
            'output_path': str(self.output), 'status': 'completed', 'attempts': 1}]))

    def result(self, **changes):
        item = dict(file_key='abc', target_index=0, disposition='likely_omission',
            reason='Explicit empirical retest of another original.', location='Results',
            omission_quote='We replicated Smith (2001).', identity_quote='Smith (2001), Prior empirical finding.',
            duplicate_quote='', matched_input_row_index=None, shipped_rows_checked=['1'])
        item.update(changes)
        self.output.write_text(json.dumps({'records': [item]}))

    def test_invented_or_repaired_quote_cannot_pass_mechanical_evidence_gate(self):
        self.result(identity_quote='Smith (2001), A repaired empirical finding.')
        result = ctl.validate_luna('luna_0000')
        self.assertEqual(result['mechanically_valid'], 0)
        self.assertTrue((self.f / 'candidate_requests/index.json').exists())
        self.assertFalse((self.root / 'adjudications').exists())

    def test_ignoring_a_shipped_counterpart_is_flagged_before_expert_review(self):
        self.result(shipped_rows_checked=[])
        result = ctl.validate_luna('luna_0000')
        self.assertEqual(result['mechanically_valid'], 0)

    def test_missing_output_retries_without_marking_candidates_scientifically_reviewed(self):
        first = ctl.validate_luna('luna_0000')
        self.assertTrue(first['retry_queued'])
        entry = json.loads(self.index.read_text())[0]
        entry.update(attempts=2, status='completed')
        self.index.write_text(json.dumps([entry]))
        second = ctl.validate_luna('luna_0000')
        self.assertEqual(second['mechanically_valid'], 0)
        validation = json.loads((self.f / 'luna/results/luna_0000.validation.json').read_text())
        self.assertTrue(validation['records'][0]['luna_not_completed'])

    def test_existing_native_argon_lane_prevents_a_fifth_total_argon_call(self):
        (self.f / 'state.json').write_text(json.dumps({'tasks': [
            {'lane': 'argon_runner', 'status': 'running', 'slot_cost': 4},
            {'lane': 'argon_native', 'status': 'running', 'slot_cost': 1}]}))
        self.assertIsNone(ctl.prepare_candidate_review())
