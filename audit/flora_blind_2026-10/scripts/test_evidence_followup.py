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


class RegisteredReviewSources(unittest.TestCase):
    save_registry = AdditionalPrimaryReportGuards.save_registry

    def setUp(self):
        AdditionalPrimaryReportGuards.setUp(self)
        import integrate_candidate_reviews as integrator
        self.integrator = integrator
        self.followup = self.root / 'evidence_followup'
        for folder in ('candidate_reviews', 'candidate_requests', 'integration'):
            (self.followup / folder).mkdir()
        (self.root / 'adjudications').mkdir()
        (self.root / 'codings').mkdir()
        self.basecode = self.root / 'codings/abc.json'
        self.basecode.write_text(json.dumps(dict(work_key='work', evidence_level='abstract',
            targets=[{'index': i} for i in range(89)])))
        self.source.write_bytes(b'Primary first line.\r\nPrimary second line.\r\n')
        self.set_level('abstract')
        self.decision = dict(request_id='fresh', file_key='abc', input_row_index=17,
            field='outcome', method='argon', verdict='blind_right', corrected_value='successful',
            quote='Primary first line.\r\nPrimary second line.', location='Abstract',
            reason='Parent inspected primary evidence.')
        self.request = dict(request_id='fresh', file_key='abc', work_key='work',
            source_path=str(self.source), requested_fields=[dict(input_row_index=17, field='outcome')])
        self.write_review('input', dict(requests=[dict(self.request, request_id='old',
            source_path=str(self.root / 'texts/abc.txt')), self.request]))
        self.write_review('result', dict(decisions=[self.decision]))
        (self.followup / 'candidate_reviews/parent_inspection.json').write_text(json.dumps(
            dict(reviews=dict(review=dict(status='approved', review_kind='fields',
                reason='Parent approved.', approved_keys=[['abc', '17', 'outcome']])))))
        (self.followup / 'candidate_requests/index.json').write_text(json.dumps([
            dict(request_id='fresh', review_id='review', review_attempts=2)]))
        self.addCleanup(patch.stopall)
        for module in (ctl, integrator):
            patch.object(module, 'R', self.root).start()
            patch.object(module, 'F', self.followup).start()

    def set_level(self, level):
        self.item['evidence_level'] = level
        code = dict(work_key='work', status='done', evidence_level=level,
            text_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest(),
            targets=[dict(evidence_quote='Primary first line.\r\nPrimary second line.')])
        self.code.write_text(json.dumps(code))
        self.item.update(text_sha256=code['text_sha256'],
            blind_coding_sha256=hashlib.sha256(self.code.read_bytes()).hexdigest())
        self.save_registry()

    def write_review(self, suffix, value):
        (self.followup / ('candidate_reviews/review.' + suffix + '.json')).write_text(json.dumps(value))

    def receipt(self):
        self.write_review('validation', dict(valid_envelope=True, records=[dict(
            decision=self.decision, mechanically_valid=True,
            source_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest())]))

    def test_registered_partial_validates_integrates_and_compares_without_changing_base(self):
        # Validate through the real controller, then integrate through the registry guard.
        # Different row keys keep both source requests distinct in the controller envelope.
        old = dict(self.request, request_id='old', source_path=str(self.root / 'texts/abc.txt'),
            requested_fields=[dict(input_row_index=18, field='outcome')])
        old_decision = dict(self.decision, request_id='old', input_row_index=18,
            quote='Frozen base source.')
        self.write_review('input', dict(requests=[old, self.request]))
        self.write_review('result', dict(decisions=[old_decision, self.decision]))
        frozen = {p: p.read_bytes() for p in (self.basecode, self.root / 'texts/abc.txt',
            self.code, self.source, self.registry)}
        raw_result = (self.followup / 'candidate_reviews/review.result.json').read_bytes()
        self.assertEqual(ctl.validate_candidate_review('review')['mechanically_valid'], 2)
        receipt = (self.followup / 'candidate_reviews/review.validation.json').read_bytes()
        self.assertEqual(self.integrator.integrate()['approved_rechecks_or_additions'], 1)
        actual = json.loads((self.root / 'adjudications/abc.json').read_text())['decisions'][0]
        self.assertEqual(actual['source_report_id'], 'one')
        self.assertEqual(actual['source_text_sha256'], self.item['text_sha256'])
        combined = comparison.primary_text(self.root, 'abc', 'work')
        self.assertIn('VERIFIED ADDITIONAL PRIMARY EVIDENCE:', combined)
        self.assertIn(actual['quote'], combined)
        self.assertTrue(comparison.valid_decision(actual, combined))
        self.assertEqual(json.loads(self.code.read_text())['evidence_level'], 'abstract')
        self.assertEqual(len(json.loads(self.basecode.read_text())['targets']), 89)
        for path, before in frozen.items():
            self.assertEqual(path.read_bytes(), before)
        self.assertEqual((self.followup / 'candidate_reviews/review.result.json').read_bytes(), raw_result)
        self.assertEqual((self.followup / 'candidate_reviews/review.validation.json').read_bytes(), receipt)

    def test_integrator_rejects_unregistered_wrong_work_changed_source_and_code(self):
        for fault in ('unregistered', 'wrong_work', 'source', 'code', 'unrequested', 'wrong_request', 'duplicate'):
            with self.subTest(fault=fault):
                self.set_level('full_text')
                original = {p: p.read_bytes() for p in (self.registry, self.source, self.code)}
                request = dict(self.request)
                if fault == 'unregistered':
                    self.registry.write_text('{"reports": []}')
                elif fault == 'wrong_work':
                    request['work_key'] = 'other-work'
                elif fault in ('source', 'code'):
                    path = self.source if fault == 'source' else self.code
                    path.write_bytes(path.read_bytes() + b' ')
                elif fault == 'unrequested':
                    request['requested_fields'] = [dict(input_row_index=19, field='outcome')]
                elif fault == 'wrong_request':
                    request['request_id'] = 'other'
                self.write_review('input', dict(requests=[request] * (2 if fault == 'duplicate' else 1)))
                self.receipt()  # Even a receipt with the current source hash cannot bypass the registry.
                with self.assertRaises(AssertionError):
                    self.integrator.integrate()
                self.assertFalse((self.root / 'adjudications/abc.json').exists())
                for path, before in original.items():
                    path.write_bytes(before)

    def test_integrator_rejects_lf_repair_of_crlf_quote(self):
        self.set_level('full_text')
        self.decision['quote'] = self.decision['quote'].replace('\r\n', '\n')
        self.receipt()
        with self.assertRaises(AssertionError):
            self.integrator.integrate()

    def test_fresh_code_must_still_be_done_and_bound_to_work_and_source(self):
        for field, value in (('work_key', 'other-work'), ('status', 'pending'),
                             ('text_sha256', '0' * 64), ('evidence_level', 'full_text')):
            with self.subTest(field=field):
                self.set_level('abstract')
                code = json.loads(self.code.read_text())
                code[field] = value
                self.code.write_text(json.dumps(code))
                self.item['blind_coding_sha256'] = hashlib.sha256(self.code.read_bytes()).hexdigest()
                self.save_registry()
                self.receipt()
                with self.assertRaises(AssertionError):
                    self.integrator.integrate()

    def test_registry_does_not_bypass_validation_receipt_source_hash(self):
        self.receipt()
        path = self.followup / 'candidate_reviews/review.validation.json'
        receipt = json.loads(path.read_text())
        receipt['records'][0]['source_sha256'] = '0' * 64
        path.write_text(json.dumps(receipt))
        with self.assertRaises(AssertionError):
            self.integrator.integrate()

    def test_registry_level_must_be_allowed_and_match_fresh_code(self):
        for level in ('abstract', 'unknown'):
            self.set_level('full_text')
            self.item['evidence_level'] = level
            self.save_registry()
            with self.assertRaises(AssertionError):
                comparison.primary_text(self.root, 'abc', 'work')

    def test_missing_registry_level_preserves_legacy_full_text(self):
        self.set_level('full_text')
        del self.item['evidence_level']
        self.save_registry()
        self.receipt()
        self.assertEqual(self.integrator.integrate()['approved_rechecks_or_additions'], 1)

    def test_verifier_checks_partial_crlf_and_rejects_lf_quotes(self):
        import verify_integration as verifier
        (self.root / 'coding_schema.json').write_text(json.dumps(dict(type='object',
            required=['work_key', 'status', 'evidence_level', 'targets'])))
        self.assertEqual(verifier.verify_additional_reports(self.root), 1)
        decision = dict(self.decision, source_report_id='one', source_text_sha256=self.item['text_sha256'])
        path = self.root / 'adjudications/abc.json'
        path.write_text(json.dumps(dict(decisions=[decision])))
        self.assertEqual(verifier.verify_additional_reports(self.root), 1)
        decision['quote'] = decision['quote'].replace('\r\n', '\n')
        path.write_text(json.dumps(dict(decisions=[decision])))
        with self.assertRaises(AssertionError):
            verifier.verify_additional_reports(self.root)
        path.unlink()
        code = json.loads(self.code.read_text())
        code['targets'][0]['evidence_quote'] = code['targets'][0]['evidence_quote'].replace('\r\n', '\n')
        self.code.write_text(json.dumps(code))
        self.item['blind_coding_sha256'] = hashlib.sha256(self.code.read_bytes()).hexdigest()
        self.save_registry()
        with self.assertRaises(AssertionError):
            verifier.verify_additional_reports(self.root)

    def test_verifier_retains_schema_validation(self):
        import jsonschema
        import verify_integration as verifier
        (self.root / 'coding_schema.json').write_text(json.dumps(dict(type='object',
            required=['targets'], properties=dict(targets=dict(type='array')))))
        code = json.loads(self.code.read_text())
        code['targets'] = 'invalid target list'
        self.code.write_text(json.dumps(code))
        self.item['blind_coding_sha256'] = hashlib.sha256(self.code.read_bytes()).hexdigest()
        self.save_registry()
        with self.assertRaises(jsonschema.ValidationError):
            verifier.verify_additional_reports(self.root)


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

    def test_paused_native_transport_cannot_reserve_more_requests(self):
        (self.f / 'state.json').write_text(json.dumps({'tasks': [], 'native_argon_dispatch_paused': True}))
        self.assertIsNone(ctl.prepare_candidate_review())
        self.assertFalse((self.f / 'candidate_reviews').exists())

    def test_native_dispatch_preserves_one_combined_validation_slot(self):
        (self.f / 'state.json').write_text(json.dumps({'tasks': [
            {'lane': 'other', 'status': 'running', 'slot_cost': 9}],
            'max_combined_children_and_infrastructure': 10}))
        self.assertIsNone(ctl.prepare_candidate_review())
        self.assertFalse((self.f / 'candidate_reviews').exists())

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
        decisions[0]['quote'] = 'We  replicated Smith (2001).'
        resultpath.write_text(json.dumps({'decisions': decisions}))
        self.assertEqual(ctl.validate_candidate_review('review_0000')['mechanically_valid'], 1)
        decisions[0]['quote'] = 'We replicated Smith (2001).'
        decisions[1]['input_row_index'] = 3
        resultpath.write_text(json.dumps({'decisions': decisions}))
        self.assertFalse(ctl.validate_candidate_review('review_0000')['valid_envelope'])


class CandidateCLIDispatch(unittest.TestCase):
    def setUp(self):
        from unittest.mock import Mock
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.f = Path(self.temp.name)
        (self.f / 'candidate_cli/snap').mkdir(parents=True)
        self.out = self.f / 'candidate_cli/snap'
        (self.out / 'prepared.json').write_text('{}')
        self.state = dict(status='active', tasks=[], candidate_cli_dispatch=dict(
            enabled=True, snapshot='snap', max_calls_per_worker=1, next_round=1))
        self.relay = Mock(out=self.out)
        self.relay.load.return_value = {'bundles': [{'review_id': 'b'}]}
        self.relay.ledger.return_value = dict(status='pending', attempts=[])
        self.addCleanup(patch.stopall)
        patch.object(ctl, 'F', self.f).start()
        patch.object(ctl, 'candidate_relay', return_value=self.relay).start()
        self.save()

    def save(self):
        ctl.a.atomic(self.f / 'state.json', self.state)

    def actual(self, intent):
        return dict(clientRequestId=intent['clientRequestId'], taskId='ACTUAL-task-123',
                    status='running', providerInstanceId='codex', model='gpt-6.1-sol',
                    options=[dict(id='reasoningEffort', value='medium'), dict(id='serviceTier', value='default')])

    def test_parent_reduced_worker_limit(self):
        self.state['candidate_cli_dispatch']['max_workers'] = 1
        self.save()
        self.assertEqual(ctl.candidate_cli_dispatch()['workers'], 1)

    def test_invalid_parent_worker_limit(self):
        for invalid in [0, 5, True, '1']:
            self.state['candidate_cli_dispatch']['max_workers'] = invalid
            self.save()
            with self.assertRaisesRegex(ValueError, 'max_workers'):
                ctl.candidate_cli_dispatch()

    def test_opt_in_and_actual_identity_publication(self):
        self.state['candidate_cli_dispatch']['enabled'] = False
        self.save()
        self.assertIsNone(ctl.candidate_cli_dispatch())
        self.state['candidate_cli_dispatch']['enabled'] = True
        self.save()
        intent = ctl.candidate_cli_dispatch()
        self.assertEqual(intent['workers'], 4)
        self.assertEqual(ctl.candidate_cli_dispatch(), intent)  # lost tool response retries SAME ID
        real = ctl.a.atomic
        def inspect(path, obj):
            if Path(path).name == 'control.json':
                registered = ctl.read(self.f / 'state.json')['tasks']
                self.assertEqual(registered[0]['taskId'], 'ACTUAL-task-123')
                self.assertEqual(registered[0]['slot_cost'], 5)
            return real(path, obj)
        with patch.object(ctl.a, 'atomic', side_effect=inspect):
            ctl.candidate_cli_dispatch(self.actual(intent))
        control = ctl.read(self.f / 'candidate_cli/control.json')
        self.assertEqual(control['reservation']['taskId'], 'ACTUAL-task-123')
        self.assertEqual(control['clientRequestId'], intent['clientRequestId'])
        self.assertIsNone(ctl.candidate_cli_dispatch())  # active coordinator blocks next notification
        state = ctl.read(self.f / 'state.json')
        state['tasks'][0]['status'] = 'completed'
        ctl.a.atomic(self.f / 'state.json', state)
        next_intent = ctl.candidate_cli_dispatch()
        self.assertEqual(next_intent['round'], 2)
        self.assertNotEqual(next_intent['clientRequestId'], intent['clientRequestId'])

    def test_old_relay_ending_does_not_escalate_running_quantum(self):
        self.state['tasks'] = [dict(taskId='old', lane='argon_runner', status='running', slot_cost=4)]
        self.save()
        intent = ctl.candidate_cli_dispatch()
        self.assertEqual(intent['workers'], 1)
        ctl.candidate_cli_dispatch(self.actual(intent))
        state = ctl.read(self.f / 'state.json')
        state['tasks'][0]['status'] = 'completed'
        ctl.a.atomic(self.f / 'state.json', state)
        self.assertIsNone(ctl.candidate_cli_dispatch())
        state['tasks'][1]['status'] = 'completed'
        ctl.a.atomic(self.f / 'state.json', state)
        self.assertEqual(ctl.candidate_cli_dispatch()['workers'], 4)

    def test_publication_crash_recovery_uses_same_intent_actual_task(self):
        intent = ctl.candidate_cli_dispatch()
        real = ctl.a.atomic
        def fail_control(path, obj):
            if Path(path).name == 'control.json':
                raise OSError('mock crash before control publication')
            return real(path, obj)
        with patch.object(ctl.a, 'atomic', side_effect=fail_control):
            with self.assertRaises(OSError):
                ctl.candidate_cli_dispatch(self.actual(intent))
        recovered = ctl.candidate_cli_dispatch()
        self.assertEqual(recovered['clientRequestId'], intent['clientRequestId'])
        self.assertEqual(recovered['taskId'], 'ACTUAL-task-123')
        ctl.candidate_cli_dispatch(self.actual(intent))
        self.assertEqual(len(ctl.read(self.f / 'state.json')['tasks']), 1)
        self.assertIsNone(ctl.candidate_cli_dispatch())

    def test_ceilings_and_unknown_lanes_fail_closed(self):
        cases = [
            ([dict(lane='argon_runner', slot_cost=4)], 0, 1),
            ([], 0, 4),
            ([dict(lane='luna', slot_cost=4)], 0, 4),
            ([dict(lane='luna', slot_cost=4)], 1, 3),
            ([dict(lane='luna', slot_cost=7)], 1, None),
            ([dict(lane='argon_runner', slot_cost=4), dict(lane='argon_native', slot_cost=1)], 0, None),
            ([dict(lane='unknown_argon', slot_cost=1)], 0, None),
            ([dict(lane='other', model='Gemini 4 Argon (High)', slot_cost=1)], 0, None),
            ([dict(lane='candidate_cli', slot_cost=2)], 0, None),
            ([dict(lane='other', slot_cost=-1)], 0, None),
        ]
        for tasks, metadata, expected in cases:
            with self.subTest(tasks=tasks, metadata=metadata):
                self.state['tasks'] = [dict(t, taskId=str(n), status='running') for n, t in enumerate(tasks)]
                self.state['metadata_infrastructure_slots'] = metadata
                self.save()
                result = ctl.candidate_cli_dispatch()
                self.assertEqual(result['workers'] if result else None, expected)

    def test_terminal_blockers_and_pending_children(self):
        for progress in [dict(blocker='invalid reservation'), dict(blocker='orphan process'),
                         dict(infrastructure_streak=3), dict(infrastructure_circuit_open=True)]:
            ctl.a.atomic(self.out / 'progress.json', progress)
            self.assertIsNone(ctl.candidate_cli_dispatch())
        (self.out / 'progress.json').unlink()
        self.relay.check.side_effect = ValueError('changed input/source hash')
        self.assertIsNone(ctl.candidate_cli_dispatch())
        self.relay.check.side_effect = None
        for status in ['validated', 'exhausted', 'source_changed']:
            self.relay.ledger.return_value = dict(status=status, attempts=[])
            self.assertIsNone(ctl.candidate_cli_dispatch())
        self.relay.ledger.return_value = dict(status='pending', attempts=[])
        self.state['tasks'] = [dict(taskId='nested', lane='candidate_cli', status='completed', hasPendingChildRuns=True, slot_cost=2)]
        self.save()
        self.assertIsNone(ctl.candidate_cli_dispatch())

    def test_wrong_actual_identity_or_options_never_publish(self):
        intent = ctl.candidate_cli_dispatch()
        for overrides in [dict(taskId=''), dict(model='wrong'), dict(options=[]), dict(clientRequestId='wrong')]:
            with self.assertRaises(ValueError):
                ctl.candidate_cli_dispatch(dict(self.actual(intent), **overrides))
        self.assertFalse((self.f / 'candidate_cli/control.json').exists())
        self.assertEqual(ctl.read(self.f / 'state.json')['tasks'], [])


class FieldDispatchGuards(unittest.TestCase):
    def setUp(self):
        from unittest.mock import Mock
        import types
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.f = Path(self.temp.name)
        (self.f/'argon').mkdir()
        (self.f/'candidate_cli').mkdir()
        (self.f/'argon/snapshot.json').write_text('{"finite":271}')
        self.state = dict(status='active', tasks=[], field_dispatch=dict(enabled=True, workers=1, max_calls=1))
        self.save()
        self.runner = Mock(blocker=None, circuit_open=False, infra_streak=0)
        self.runner.snap = dict(requests=[dict(request_id='field'+str(n), file_key='work') for n in range(271)], works={'work':{}})
        self.module = types.SimpleNamespace(digest=lambda raw: hashlib.sha256(raw).hexdigest(),
            TERMINAL={'validated','exhausted','source_changed'}, reserved_process_live=Mock(return_value=False))
        patcher = patch.object(ctl, 'F', self.f)
        patcher.start(); self.addCleanup(patcher.stop)
        patcher = patch.object(ctl, 'field_runner', return_value=(self.module,self.runner))
        patcher.start(); self.addCleanup(patcher.stop)

    def save(self):
        (self.f/'state.json').write_text(json.dumps(self.state))

    def actual(self, intent, **overrides):
        return dict(dict(taskId='FIELD-ACTUAL', status='running', providerInstanceId='codex', model='gpt-6.1-sol',
                         options={'reasoningEffort':'medium','serviceTier':'default'}, clientRequestId=intent['clientRequestId']), **overrides)

    def test_opt_in_stable_round_actual_registration_before_control(self):
        self.state['field_dispatch']['enabled'] = False; self.save()
        self.assertIsNone(ctl.field_dispatch())
        self.state['field_dispatch']['enabled'] = True; self.save()
        intent = ctl.field_dispatch()
        self.assertEqual(ctl.field_dispatch(), intent)
        real = ctl.a.atomic
        def inspect(path, value):
            if Path(path) == self.f/'argon/control.json':
                tasks = ctl.read(self.f/'state.json')['tasks']
                self.assertEqual([(t['taskId'],t['slot_cost'],t['cli_workers']) for t in tasks], [('FIELD-ACTUAL',4,1)])
            return real(path,value)
        with patch.object(ctl.a, 'atomic', side_effect=inspect):
            ctl.field_dispatch(self.actual(intent))
        control = ctl.read(self.f/'argon/control.json')
        self.assertEqual(control['reservation']['max_calls'],1)
        self.assertEqual(control['reservation']['taskId'],'FIELD-ACTUAL')
        self.assertIsNone(ctl.field_dispatch())
        self.state = ctl.read(self.f/'state.json')
        self.state['tasks'][0].update(status='completed', hasPendingChildRuns=True); self.save()
        self.assertIsNone(ctl.field_dispatch())
        self.state['tasks'][0]['hasPendingChildRuns'] = False; self.save()
        next_round = ctl.field_dispatch()
        self.assertEqual(next_round['round'],2)
        self.assertNotEqual(next_round['clientRequestId'],intent['clientRequestId'])

    def test_publication_crash_and_wrong_returned_identity(self):
        intent = ctl.field_dispatch()
        for changes in [dict(taskId=''),dict(options={}),dict(model='wrong'),dict(clientRequestId='wrong')]:
            with self.assertRaises(ValueError):
                ctl.field_dispatch(self.actual(intent,**changes))
        self.assertFalse((self.f/'argon/control.json').exists())
        real = ctl.a.atomic
        def crash(path,value):
            if Path(path) == self.f/'argon/control.json':
                raise OSError('mock crash')
            return real(path,value)
        with patch.object(ctl.a, 'atomic', side_effect=crash), self.assertRaises(OSError):
            ctl.field_dispatch(self.actual(intent))
        retry = ctl.field_dispatch()
        self.assertEqual(retry['taskId'],'FIELD-ACTUAL')
        self.assertEqual(retry['clientRequestId'],intent['clientRequestId'])
        with self.assertRaises(ValueError):
            ctl.field_dispatch(self.actual(intent,taskId='OTHER'))
        ctl.field_dispatch(self.actual(intent))
        self.assertEqual(len(ctl.read(self.f/'state.json')['tasks']),1)
        self.assertIsNone(ctl.field_dispatch())

    def test_combined_argon_and_duplicate_guards(self):
        cases = [([],0,True), ([dict(lane='candidate_cli',cli_workers=1,slot_cost=2)],3,True),
                 ([dict(lane='candidate_cli',cli_workers=1,slot_cost=2)],4,False),
                 ([dict(lane='candidate_cli',cli_workers=2,slot_cost=3)],0,False),
                 ([dict(lane='argon_runner',slot_cost=4)],0,False),
                 ([dict(lane='argon_native',slot_cost=1),dict(lane='argon_native',slot_cost=1)],0,False),
                 ([dict(lane='unknown_argon',slot_cost=1)],0,False),
                 ([dict(lane='other',slot_cost=-1)],0,False)]
        for tasks, metadata, allowed in cases:
            with self.subTest(tasks=tasks,metadata=metadata):
                self.state['tasks'] = [dict(t,taskId=str(n),status='running') for n,t in enumerate(tasks)]
                self.state['metadata_infrastructure_slots'] = metadata
                self.state['field_dispatch'].pop('intent',None); self.save()
                self.assertEqual(ctl.field_dispatch() is not None,allowed)

    def test_scientific_status_budgets_and_blockers_ignore_finished(self):
        ctl.a.atomic(self.f/'argon/progress.json',dict(finished=True))
        self.assertIsNotNone(ctl.field_dispatch())  # still finite pending work
        for attr,value in [('blocker','received signal 15'),('circuit_open',True),('infra_streak',5)]:
            setattr(self.runner,attr,value)
            self.assertIsNone(ctl.field_dispatch())
            setattr(self.runner,attr,0 if attr=='infra_streak' else False if attr=='circuit_open' else None)
        self.runner.check_hashes.side_effect = ValueError('changed source')
        self.assertIsNone(ctl.field_dispatch())
        self.runner.check_hashes.side_effect = None
        for status in ['validated','exhausted','source_changed','retry_pending']:
            for e in self.runner.snap['requests']:
                ctl.a.atomic(self.f/'argon'/(e['request_id']+'.state.json'),dict(status=status,attempts=2))
            self.assertIsNone(ctl.field_dispatch())
        path = self.f/'argon/field0.state.json'
        ctl.a.atomic(path,dict(status='running',attempts=2,history=[dict(output_path='owned')]))
        self.module.reserved_process_live.return_value=True
        self.assertIsNone(ctl.field_dispatch())
        self.module.reserved_process_live.return_value=False
        self.assertIsNotNone(ctl.field_dispatch())  # spent output recovery, no budget refund
