"""Guard failures that could incorrectly add/exclude missing originals."""
import json
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import evidence_followup_controller as ctl
import compare as comparison
from promote_followup_sources import target_mapping
from check_project_endpoints import endpoint


class AdditionalPrimaryReportGuards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'texts').mkdir()
        (self.root / 'texts/abc.txt').write_text('Frozen base source.')
        private = self.root / 'evidence_followup/private'
        private.mkdir(parents=True)
        self.source = private / 'report.txt'
        self.source.write_text('An independently recovered primary report.')
        self.code = private / 'code.json'
        self.code.write_text(json.dumps(dict(work_key='work', status='done',
            text_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest(), evidence_level='full_text')))
        self.item = dict(collection_file_key='abc', report_id='one', work_key='work',
            status='approved_for_comparison', text_path=str(self.source),
            text_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest(),
            blind_coding_path=str(self.code), blind_coding_sha256=hashlib.sha256(self.code.read_bytes()).hexdigest(),
            source_url='https://example.org/primary')
        self.registry = self.root / 'evidence_followup/additional_reports/approved_sources.json'
        self.registry.parent.mkdir()
        self.save_registry()

    def save_registry(self):
        self.registry.write_text(json.dumps({'reports': [self.item]}))

    def test_verified_supplement_preserves_frozen_source_and_exact_report_text(self):
        base = self.root / 'texts/abc.txt'
        before = base.read_bytes()
        combined = comparison.primary_text(self.root, 'abc', 'work')
        self.assertTrue(combined.startswith(before.decode()))
        self.assertTrue(combined.endswith(self.source.read_text()))
        self.assertEqual(base.read_bytes(), before)

    def test_changed_primary_source_or_blind_coding_is_rejected(self):
        for path in (self.source, self.code):
            with self.subTest(path=path.name):
                before = path.read_bytes()
                path.write_bytes(before + b' ')
                with self.assertRaises(AssertionError):
                    comparison.primary_text(self.root, 'abc', 'work')
                path.write_bytes(before)

    def test_wrong_work_and_source_outside_private_directory_are_rejected(self):
        with self.assertRaises(AssertionError):
            comparison.primary_text(self.root, 'abc', 'other-work')
        self.item['text_path'] = str(self.root / 'texts/abc.txt')
        self.save_registry()
        with self.assertRaises(AssertionError):
            comparison.primary_text(self.root, 'abc', 'work')

    def test_old_approved_review_cannot_replay_over_changed_primary_evidence(self):
        import integrate_candidate_reviews as integrator
        followup = self.root / 'evidence_followup'
        reviews = followup / 'candidate_reviews'
        reviews.mkdir()
        requests = followup / 'candidate_requests'
        requests.mkdir()
        (requests / 'index.json').write_text('[]')
        (reviews / 'parent_inspection.json').write_text(json.dumps({'reviews': {'old': {
            'status': 'approved', 'reason': 'Prior source limit was inspected.',
            'approved_keys': [['abc', '1', 'outcome']],
            'superseded_keys': [['abc', '1', 'outcome']],
            'supersession_reason': 'New complete report resolves the earlier source gap.',
            'review_kind': 'fields'}}}))
        (reviews / 'old.validation.json').write_text(json.dumps({'valid_envelope': True, 'records': []}))
        adjs = self.root / 'adjudications'
        adjs.mkdir()
        newer = adjs / 'abc.json'
        newer.write_text('{"decisions": [{"field": "outcome", "new_primary_evidence": true}]}')
        before = newer.read_bytes()
        with patch.object(integrator, 'R', self.root), patch.object(integrator, 'F', followup):
            self.assertEqual(integrator.integrate()['approved_rechecks_or_additions'], 0)
        self.assertEqual(newer.read_bytes(), before)


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

    def test_additional_acquisition_reserves_capacity_and_luna_restores_after_completion(self):
        state = {'status': 'active', 'max_parallel_luna': 3, 'tasks': [
            {'lane': 'additional_acquisition', 'status': 'running', 'slot_cost': 2}]}
        path = self.f / 'state.json'
        path.write_text(json.dumps(state))
        with patch.object(ctl, 'reconcile_files'):
            self.assertEqual(ctl.plan()['luna_limit'], 2)
            self.assertEqual(ctl.plan()['slot_cost'], 2)
            state['tasks'][0]['status'] = 'completed'
            path.write_text(json.dumps(state))
            self.assertEqual(ctl.plan()['luna_limit'], 3)
            self.assertEqual(ctl.plan()['slot_cost'], 0)

    def test_source_upgrade_cannot_silently_drop_an_identified_original(self):
        with self.assertRaises(ValueError):
            target_mapping({'targets': [{'title': 'A specific missing original'}]},
                           {'targets': [{'title': 'Another finding'}]})

    def test_source_upgrade_maps_reference_punctuation_without_losing_identity(self):
        result = target_mapping({'targets': [{'title': 'A specific missing original.'}]},
                                {'targets': [{'title': 'A specific missing original'}]})
        self.assertEqual(result[0]['new_target_index'], 0)

    def test_fractional_author_ratings_do_not_become_categorical_outcomes(self):
        self.assertIsNone(endpoint({'adjudicated_replication_code': '0.5',
            'replicated_instructor_code': '0', 'replicated_report_code': '0'}))
        self.assertIsNone(endpoint({'adjudicated_replication_code': 'NA',
            'replicated_instructor_code': '0', 'replicated_report_code': '1'}))
        self.assertEqual(endpoint({'adjudicated_replication_code': '1',
            'replicated_instructor_code': '0.5', 'replicated_report_code': '0'}), 'successful')

    def test_scope_hold_withholds_export_without_destroying_prior_outcome(self):
        adjs = self.root / 'adjudications'
        adjs.mkdir()
        decision = {'field': 'missing_row', 'target_index': 1,
                    'verdict': 'blind_right', 'corrected_value': {'outcome': 'successful'}}
        p = adjs / 'abc.json'
        p.write_text(json.dumps({'decisions': [decision]}))
        before = p.read_bytes()
        holds = self.root / 'evidence_followup/integration/review_holds.json'
        holds.parent.mkdir(parents=True)
        h = {'file_key': 'abc', 'field': 'missing_row', 'target_index': 1, 'status': 'pending'}
        holds.write_text(json.dumps({'holds': [h]}))
        self.assertEqual(comparison.load_decisions(self.root, 'abc')[0], [])
        h['status'] = 'resolved'
        holds.write_text(json.dumps({'holds': [h]}))
        self.assertEqual(comparison.load_decisions(self.root, 'abc')[0], [decision])
        self.assertEqual(p.read_bytes(), before)

    def test_native_fields_for_same_source_are_validated_once_and_wrong_row_is_rejected(self):
        out = self.f / 'candidate_reviews'
        out.mkdir()
        requests = [{'request_id': f'r{i}', 'file_key': 'abc', 'source_path': str(self.source),
                     'requested_fields': [{'input_row_index': i, 'field': 'outcome'}]} for i in [1, 2]]
        (out / 'review_0000.input.json').write_text(json.dumps({'requests': requests}))
        index = self.f / 'candidate_requests/index.json'
        index.parent.mkdir()
        index.write_text(json.dumps([{'request_id': f'r{i}', 'review_attempts': 1} for i in [1, 2]]))
        decisions = [{'request_id': f'r{i}', 'file_key': 'abc', 'input_row_index': i,
                      'field': 'outcome', 'method': 'argon', 'verdict': 'shipped_right',
                      'corrected_value': 'failed', 'quote': 'We replicated Smith (2001).',
                      'location': 'Results', 'reason': 'Primary author main message.'} for i in [1, 2]]
        resultpath = out / 'review_0000.result.json'
        resultpath.write_text(json.dumps({'decisions': decisions}))
        result = ctl.validate_candidate_review('review_0000')
        self.assertEqual(result['decisions'], 2)
        self.assertEqual(result['mechanically_valid'], 2)
        decisions[1]['input_row_index'] = 3
        resultpath.write_text(json.dumps({'decisions': decisions}))
        self.assertFalse(ctl.validate_candidate_review('review_0000')['valid_envelope'])
