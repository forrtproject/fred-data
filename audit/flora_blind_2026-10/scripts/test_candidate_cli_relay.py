#!/usr/bin/env python3
"""Mocked transport only; fixtures are owned and ignored, never the actual queue."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('candidate_cli_relay', ROOT / 'evidence_followup/candidate_cli_relay.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RelayTest(unittest.TestCase):
    def setUp(self):
        private = ROOT / 'evidence_followup/private'
        private.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='test_candidate_cli_', dir=private)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.f = self.root / 'evidence_followup'
        for p in ('candidate_requests', 'candidate_reviews', 'private'):
            (self.f / p).mkdir(parents=True)
        (self.root / 'scripts').mkdir()
        for p in ('compare.py', 'adjudicate.py', 'evidence_followup_controller.py'):
            shutil.copyfile(ROOT / 'scripts' / p, self.root / 'scripts' / p)
        (self.root / 'codebook.md').write_text('verbatim codebook')
        for name in ('REVIEW_INSTRUCTIONS.md', 'FIELD_REVIEW_INSTRUCTIONS.md'):
            (self.f / 'candidate_reviews' / name).write_text('verbatim instructions')
        self.index = []
        self.calls = []
        self.relay = m.Relay(self.root)
        self.control = self.f / 'control.json'
        self.configure()

    def configure(self, workers=1, old=False, extra=0):
        tasks = [dict(taskId='owner', lane='candidate_cli', status='running', slot_cost=1+workers,
                      cli_snapshot='pending-v1', cli_workers=workers)]
        if old:
            tasks.append(dict(taskId='old', lane='argon_runner', status='running', slot_cost=4))
        if extra:
            tasks.append(dict(taskId='infra', lane='other', status='running', slot_cost=extra))
        m.atomic(self.f / 'state.json', dict(tasks=tasks, metadata_infrastructure_slots=0,
                                          max_combined_children_and_infrastructure=10))
        m.atomic(self.control, dict(drain=False, reservation=dict(taskId='owner', snapshot='pending-v1',
                   workers=workers, model=m.MODEL, billing='included_subscription')))

    def add(self, rid='one', baseline=0, fields=None, status='pending', source='primary.txt', **extra):
        path = self.root / source
        if not path.exists():
            path.write_text('Prefix. A contiguous literal primary quote. Suffix.')
        work = dict(request_id=rid, file_key='file', source_path=str(path),
                    source_instruction='Read complete source ' + str(path), shipped_rows=[{'input_row_index': 99}],
                    requested_fields=fields or [dict(field='type', input_row_index='1')],
                    unresolved_objection='preserve objection')
        p = self.f / 'candidate_requests' / (rid + '.json')
        m.atomic(p, work)
        entry = dict(request_id=rid, input_path=str(p), status=status, review_attempts=baseline,
                     field_count=len(work['requested_fields']), review_kind='fields', **extra)
        self.index.append(entry)
        m.atomic(self.relay.index, self.index)
        return work

    def response(self, b):
        decisions = []
        for w in b['envelope']['requests']:
            for field in w['requested_fields']:
                d = dict(field, request_id=w['request_id'], file_key=w['file_key'], method='argon',
                         verdict='blind_right', corrected_value='replication',
                         quote='A contiguous literal primary quote.', location='p1', reason='mock rationale')
                if d['field'] == 'missing_row':
                    d.update(verdict='shipped_right', corrected_value=None)
                decisions.append(d)
        return dict(review_id=b['review_id'], decisions=decisions)

    def transport(self, argv, output, timeout):
        self.calls.append(argv)
        self.assertEqual(argv[argv.index('--model')+1], m.MODEL)
        self.assertIn('--sandbox', argv)
        self.assertNotIn('--dangerously-skip-permissions', argv)
        b = next(b for b in self.relay.load()['bundles'] if b['review_id'] in argv[2])
        output.write_text('## Answer\n' + json.dumps(self.response(b)))
        return 0

    def run_relay(self, **kw):
        return self.relay.run(self.control, 'owner', transport=self.transport, **kw)

    def test_prepare_resume_and_parent_validator(self):
        self.add(baseline=1)
        self.relay.prepare()
        snapshot = (self.relay.out / 'snapshot.json').read_bytes()
        self.relay.prepare()
        self.run_relay()
        self.run_relay()
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(snapshot, (self.relay.out / 'snapshot.json').read_bytes())
        self.assertEqual(m.read(self.relay.index)[0]['review_attempts'], 1)  # runner never writes index
        result = self.relay.reconcile()
        self.assertEqual(result['validations'][0]['mechanically_valid'], 1)
        before = self.relay.index.read_bytes()
        self.relay.reconcile()
        self.assertEqual(before, self.relay.index.read_bytes())
        entry = m.read(self.relay.index)[0]
        self.assertEqual(entry['review_attempts'], 2)
        self.assertEqual(entry['status'], 'expert_review_complete_pending_parent')

    def history_request(self, exists=True):
        work = self.add()
        for key, name in [('prior_adjudication_path', 'adjudication.json'), ('prior_state_path', 'prior-state.json')]:
            path = self.root / name
            if exists:
                path.write_text('original history bytes')
            work[key] = str(path)
        m.atomic(self.index[0]['input_path'], work)
        return work

    def test_retry_gets_keyed_feedback_without_repair_or_budget_refund(self):
        self.add()
        self.relay.prepare()
        def transport(argv, output, timeout):
            result = self.transport(argv, output, timeout)
            if len(self.calls) == 1:
                output.write_text(output.read_text().replace(
                    'A contiguous literal primary quote.', 'A contiguous  literal primary quote.'))
            else:
                self.assertIn('STRICT VALIDATION FEEDBACK', argv[2])
                self.assertIn('nonliteral primary quote for key', argv[2])
                self.assertIn('Previous raw reply (read only)', argv[2])
            return result
        self.relay.run(self.control, 'owner', transport=transport)
        bundle = self.relay.load()['bundles'][0]
        ledger = self.relay.ledger(bundle)
        self.assertEqual(ledger['status'], 'validated')
        self.assertEqual(len(ledger['attempts']), 2)
        self.assertIn('A contiguous  literal', Path(ledger['attempts'][0]['raw_path']).read_text())
        self.assertNotEqual(ledger['attempts'][0]['prompt_sha256'], ledger['attempts'][1]['prompt_sha256'])
        self.run_relay()
        self.assertEqual(len(self.calls), 2)

    def test_existing_repository_relative_history_and_index_paths(self):
        work = self.history_request()
        for key in ('prior_adjudication_path', 'prior_state_path'):
            work[key] = os.path.relpath(work[key])
        work['source_path'] = os.path.relpath(work['source_path'])
        original = self.index[0]['input_path']
        m.atomic(original, work)
        self.index[0]['input_path'] = os.path.relpath(original)
        m.atomic(self.relay.index, self.index)
        self.relay.prepare()
        snap = self.relay.load()
        self.assertTrue(all(Path(path).is_absolute() for path in snap['files']))
        self.assertIn(work['prior_adjudication_path'], snap['history_provenance'])
        self.assertTrue(Path(snap['bundles'][0]['envelope']['requests'][0]['source_path']).is_absolute())
        Path(self.root / 'adjudication.json').write_text('parent integrated later')
        self.relay.check(snap)

    def test_history_updates_and_creation_leave_context_frozen(self):
        for exists in (True, False):
            with self.subTest(exists=exists):
                # Each case has its own immutable snapshot and request reservation.
                self.relay = m.Relay(self.root, 'history-' + str(exists))
                self.index = []
                work = self.history_request(exists)
                if not exists:
                    for key in ('prior_adjudication_path', 'prior_state_path'):
                        Path(work[key]).unlink(missing_ok=True)
                self.relay.prepare()
                snap = self.relay.load()
                b = snap['bundles'][0]
                prompt = b['prompt']
                for key in ('prior_adjudication_path', 'prior_state_path'):
                    frozen = Path(b['envelope']['requests'][0][key])
                    self.assertNotEqual(str(frozen), work[key])
                    self.assertEqual(frozen.read_bytes() if frozen.exists() else None,
                                     b'original history bytes' if exists else None)
                    self.assertEqual(snap['history_provenance'][work[key]]['original_sha256'],
                                     m.sha(b'original history bytes') if exists else None)
                    self.assertNotIn(work[key], snap['files'])
                    self.assertNotIn(work[key], prompt)
                    Path(work[key]).write_text('parent integrated newer history')
                self.relay.check(snap)
                self.assertEqual(self.relay.load()['bundles'][0]['prompt'], prompt)
                # Execute using the frozen snapshot after canonical integration.
                ctl = m.read(self.control)
                ctl['reservation']['snapshot'] = self.relay.name
                m.atomic(self.control, ctl)
                state = m.read(self.f / 'state.json')
                state['tasks'][0]['cli_snapshot'] = self.relay.name
                m.atomic(self.f / 'state.json', state)
                self.run_relay()
                self.relay.reconcile()
                self.assertEqual(self.relay.ledger(b)['status'], 'validated')

    def test_frozen_history_mutation_or_appearance_blocks(self):
        work = self.history_request()
        self.relay.prepare()
        snap = self.relay.load()
        frozen = Path(snap['bundles'][0]['envelope']['requests'][0]['prior_adjudication_path'])
        frozen.write_text('tampered private history')
        with self.assertRaisesRegex(ValueError, 'changed input/source hash'):
            self.relay.check(snap)
        self.assertEqual(Path(work['prior_adjudication_path']).read_text(), 'original history bytes')

    def test_absent_frozen_history_appearance_blocks(self):
        self.history_request(False)
        self.relay.prepare()
        snap = self.relay.load()
        Path(snap['bundles'][0]['envelope']['requests'][0]['prior_state_path']).write_text('new private history')
        with self.assertRaisesRegex(ValueError, 'changed input/source hash'):
            self.relay.check(snap)

    def test_lossless_instruction_path_and_primary_remain_pinned(self):
        work = self.history_request()
        lossless = self.root / 'lossless.txt'
        lossless.write_text('lossless source')
        work['source_instruction'] += ' Read lossless ' + str(lossless)
        m.atomic(self.index[0]['input_path'], work)
        self.relay.prepare()
        snap = self.relay.load()
        self.assertEqual(snap['bundles'][0]['envelope']['requests'][0]['source_instruction'], work['source_instruction'])
        self.assertIn(str(lossless), snap['files'])
        lossless.write_text('changed lossless')
        with self.assertRaisesRegex(ValueError, 'changed input/source hash'):
            self.relay.check(snap)
        lossless.write_text('lossless source')
        Path(work['source_path']).write_text('changed primary')
        with self.assertRaisesRegex(ValueError, 'changed input/source hash'):
            self.relay.check(snap)

    def test_concurrent_partial_reconcile_and_parent_dispositions(self):
        for n in range(3):
            self.add(str(n), baseline=1 if n == 1 else 0,
                     fields=[dict(field='type', input_row_index=str(6*n+i)) for i in range(6)])
        self.relay.prepare()
        entered, release = threading.Event(), threading.Event()
        count = 0
        def paused(argv, output, timeout):
            nonlocal count
            count += 1
            if count == 2:
                # Publish an incomplete in-flight raw file. Reconciliation must
                # never try to parse it or treat the reserved attempt as a failure.
                output.write_text('in-flight partial')
                entered.set()
                if not release.wait(10):
                    raise ValueError('test synchronization timed out')
            return self.transport(argv, output, timeout)
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as pool:
            running = pool.submit(self.relay.run, self.control, 'owner', transport=paused)
            try:
                self.assertTrue(entered.wait(5))
                ledgers_before = {p: p.read_bytes() for p in self.relay.out.glob('*.ledger.json')}
                result = self.relay.reconcile()  # actual runner.lock is held
                self.assertEqual(len(result['validations']), 1)
                entries = m.read(self.relay.index)
                self.assertEqual([e['review_attempts'] for e in entries], [1, 2, 0])
                self.assertEqual([e['status'] for e in entries],
                                 ['expert_review_complete_pending_parent', 'review_prepared', 'review_prepared'])
                self.assertTrue(all(p.read_bytes() == data for p, data in ledgers_before.items()))
                entries[0].update(status='parent_inspected_integrated', parent_note='keep this')
                m.atomic(self.relay.index, entries)
                first = self.relay.load()['bundles'][0]
                validation = self.relay.reviews / (first['review_id'] + '.validation.json')
                before = validation.read_bytes()
                with patch.object(self.relay, 'validate', side_effect=AssertionError('cached validation repeated')):
                    self.relay.reconcile()
                self.assertEqual(validation.read_bytes(), before)
            finally:
                release.set()
            running.result(timeout=10)
        result = self.relay.reconcile()
        self.assertEqual(len(result['validations']), 2)
        self.assertEqual(len(self.calls), 3)
        entries = m.read(self.relay.index)
        self.assertEqual(entries[0]['status'], 'parent_inspected_integrated')
        self.assertEqual(entries[0]['parent_note'], 'keep this')
        entries[1]['status'] = 'parent_rejected_scientific_scope'
        m.atomic(self.relay.index, entries)
        before = self.relay.index.read_bytes()
        with patch.object(self.relay, 'validate', side_effect=AssertionError('cached validation repeated')):
            self.relay.reconcile()
        self.assertEqual(self.relay.index.read_bytes(), before)
        self.run_relay()
        self.assertEqual(len(self.calls), 3)

    def test_parent_disposition_preserved_when_receipt_missing(self):
        self.add()
        self.relay.prepare()
        self.run_relay()
        entries = m.read(self.relay.index)
        entries[0].update(status='parent_inspected_integrated', parent_note='approved')
        m.atomic(self.relay.index, entries)
        self.relay.reconcile()
        entry = m.read(self.relay.index)[0]
        self.assertEqual(entry['status'], 'parent_inspected_integrated')
        self.assertEqual(entry['parent_note'], 'approved')
        self.assertIn('cli_validation', entry)

    def test_cached_reconciliation_still_checks_completed_hashes(self):
        self.add()
        self.relay.prepare()
        self.run_relay()
        self.relay.reconcile()
        b = self.relay.load()['bundles'][0]
        validation = self.relay.reviews / (b['review_id'] + '.validation.json')
        before = validation.read_bytes()
        validation.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'parent validation hash changed'):
            self.relay.reconcile()
        validation.write_bytes(before)
        Path(self.relay.ledger(b)['attempts'][0]['raw_path']).write_text('tampered completed raw')
        with self.assertRaisesRegex(ValueError, 'raw response hash changed'):
            self.relay.reconcile()

    def test_reconcile_checks_only_completed_bundle_inputs(self):
        self.add('complete', baseline=1)
        self.add('pending', source='second.txt', fields=[dict(field='type', input_row_index='2')])
        self.relay.prepare()
        def drain(argv, output, timeout):
            rc = self.transport(argv, output, timeout)
            ctl = m.read(self.control)
            ctl['drain'] = True
            m.atomic(self.control, ctl)
            return rc
        self.relay.run(self.control, 'owner', transport=drain)
        (self.root / 'second.txt').write_text('changed pending source')
        self.assertEqual(len(self.relay.reconcile()['validations']), 1)
        self.assertEqual(m.read(self.relay.index)[1]['review_attempts'], 0)

    def test_reconcile_rejects_reserved_snapshot_hash_change(self):
        self.add()
        self.relay.prepare()
        entries = m.read(self.relay.index)
        entries[0]['cli_snapshot_sha256'] = 'wrong'
        m.atomic(self.relay.index, entries)
        with self.assertRaisesRegex(ValueError, 'ownership/hash'):
            self.relay.reconcile()

    def test_exclude_exhausted_terminal_prepared_and_crashed_native(self):
        self.add('done', baseline=2)
        self.add('prepared', fields=[dict(field='type', input_row_index='2')], status='review_prepared')
        self.add('crashed', fields=[dict(field='type', input_row_index='3')], prior_review_id='review_0016')
        self.add('good', fields=[dict(field='type', input_row_index='4')])
        self.assertEqual(self.relay.prepare()['requests'], 1)
        self.assertEqual(self.relay.load()['bundles'][0]['items'][0]['entry']['request_id'], 'good')

    def test_kind_and_budget_bundles(self):
        self.add('a', fields=[dict(field='type', input_row_index='1')])
        self.add('b', baseline=1, fields=[dict(field='type', input_row_index='2')])
        self.add('c', fields=[dict(field='type', input_row_index='3')])
        self.relay.prepare()
        self.assertEqual(sorted(len(b['items']) for b in self.relay.load()['bundles']), [1, 2])

    def test_duplicate_keys_rejected(self):
        self.add('a')
        self.add('b')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.relay.prepare()
        self.assertEqual(m.read(self.relay.index)[0]['status'], 'pending')

    def test_same_source_subrequests_each_once(self):
        self.add('a')
        self.add('b', fields=[dict(field='type', input_row_index='2')])
        self.relay.prepare()
        self.run_relay()
        result = self.relay.reconcile()
        self.assertEqual(result['validations'][0]['decisions'], 2)
        self.assertEqual(len(self.calls), 1)

    def test_slot_ceilings_and_exact_owner(self):
        self.add()
        self.relay.prepare()
        self.configure(old=True)
        self.assertTrue(self.relay.slots(self.control, 1, 'owner'))
        self.configure(workers=4, old=True)
        with self.assertRaisesRegex(ValueError, 'Argon'):
            self.relay.slots(self.control, 4, 'owner')
        self.configure(workers=4, extra=5)
        with self.assertRaisesRegex(ValueError, 'validation'):
            self.relay.slots(self.control, 4, 'owner')
        self.configure(workers=4, extra=4)
        self.assertTrue(self.relay.slots(self.control, 4, 'owner'))
        with self.assertRaisesRegex(ValueError, 'reservation'):
            self.relay.slots(self.control, 1, 'owner')
        with self.assertRaisesRegex(ValueError, 'reservation'):
            self.relay.slots(self.control, 4, 'different')
        self.configure(old=True, extra=4)
        self.run_relay()
        self.assertEqual(len(self.calls), 0)

    def test_strict_shape_quote_method_value(self):
        self.add()
        self.relay.prepare()
        b = self.relay.load()['bundles'][0]
        good = self.response(b)
        self.relay.validate('## Answer\n' + json.dumps(good), b)
        for k, value in [('quote', 'A contiguous  literal primary quote.'), ('method', 'obvious'),
                         ('location', ''), ('reason', ''), ('corrected_value', 'unknown'),
                         ('verdict', 'unknown'), ('input_row_index', '99')]:
            bad = json.loads(json.dumps(good))
            bad['decisions'][0][k] = value
            with self.subTest(k=k), self.assertRaises(ValueError):
                self.relay.validate('## Answer\n' + json.dumps(bad), b)
        for transform in (lambda o: o['decisions'].append(o['decisions'][0]),
                          lambda o: o['decisions'].clear(), lambda o: o.update(extra=True)):
            bad = json.loads(json.dumps(good))
            transform(bad)
            with self.assertRaises(ValueError):
                self.relay.validate('## Answer\n' + json.dumps(bad), b)
        with self.assertRaises(ValueError):
            self.relay.validate(json.dumps(good), b)
        with self.assertRaises(ValueError):
            self.relay.validate('## Answer\n' + json.dumps(good) + ' trailing', b)
        with self.assertRaisesRegex(ValueError, 'duplicate JSON member'):
            self.relay.validate('## Answer\n' + json.dumps(good).replace('\"method\": \"argon\"', '\"method\": \"obvious\", \"method\": \"argon\"'), b)
        with self.assertRaisesRegex(ValueError, 'non-finite'):
            self.relay.validate('## Answer\n' + json.dumps(good).replace('\"corrected_value\": \"replication\"', '\"corrected_value\": NaN'), b)
        good['decisions'][0].update(verdict='undeterminable', corrected_value=None)
        self.relay.validate('## Answer\n' + json.dumps(good), b)

    def test_literal_quote_does_not_normalize_source_newlines(self):
        self.add()
        (self.root / 'primary.txt').write_bytes(b'First line.\r\nSecond line.')
        self.relay.prepare()
        b = self.relay.load()['bundles'][0]
        obj = self.response(b)
        obj['decisions'][0]['quote'] = 'First line.\nSecond line.'
        with self.assertRaises(ValueError):
            self.relay.validate('## Answer\n' + json.dumps(obj), b)
        obj['decisions'][0]['quote'] = 'First line.\r\nSecond line.'
        self.relay.validate('## Answer\n' + json.dumps(obj), b)

    def test_missing_exclusion_null_and_identity_shape(self):
        self.add(fields=[dict(field='missing_row', target_index=0)])
        self.relay.prepare()
        b = self.relay.load()['bundles'][0]
        obj = self.response(b)
        self.relay.validate('## Answer\n' + json.dumps(obj), b)
        obj['decisions'][0].update(verdict='blind_right', corrected_value={'title': 'incomplete'})
        with self.assertRaises(ValueError):
            self.relay.validate('## Answer\n' + json.dumps(obj), b)

    def test_full_source_hash_change_blocks(self):
        self.add()
        self.relay.prepare()
        (self.root / 'primary.txt').write_text('Changed far outside quote. A contiguous literal primary quote.')
        result = self.run_relay()
        self.assertIn('changed input/source hash', result['blocker'])
        self.assertEqual(len(self.calls), 0)

    def test_immutable_envelope_and_snapshot(self):
        self.add()
        self.relay.prepare()
        b = self.relay.load()['bundles'][0]
        path = self.relay.reviews / (b['review_id'] + '.input.json')
        path.write_text('{}')
        self.assertIn('changed envelope', self.run_relay()['blocker'])
        (self.relay.out / 'snapshot.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'snapshot hash'):
            self.run_relay()

    def test_invalid_outputs_consume_budget_and_are_preserved(self):
        self.add(baseline=1)
        self.relay.prepare()
        def invalid(argv, output, timeout):
            self.calls.append(argv)
            output.write_text('## Answer\n{}')
            return 0
        self.relay.run(self.control, 'owner', transport=invalid)
        self.run_relay()
        self.assertEqual(len(self.calls), 1)
        b = self.relay.load()['bundles'][0]
        ledger = self.relay.ledger(b)
        self.assertEqual(ledger['status'], 'exhausted')
        self.assertEqual(Path(ledger['attempts'][0]['raw_path']).read_text(), '## Answer\n{}')
        self.relay.reconcile()
        self.assertEqual(m.read(self.relay.index)[0]['status'], 'review_failed_terminal')

    def test_three_infrastructure_failures_stop_queue(self):
        for n in range(8):
            self.add(str(n), fields=[dict(field='type', input_row_index=str(n))] * 1)
        self.relay.prepare()
        def denied(argv, output, timeout):
            self.calls.append(argv)
            output.write_text('no output produced — permission auto-denied')
            return 0
        result = self.relay.run(self.control, 'owner', transport=denied)
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(result['infrastructure_streak'], 3)
        self.assertIn('three consecutive', result['blocker'])
        with self.assertRaisesRegex(ValueError, 'circuit open'):
            self.run_relay()

    def test_drain_after_current_call(self):
        for n in range(7):
            self.add(str(n), fields=[dict(field='type', input_row_index=str(n))])
        self.relay.prepare()
        def drain(argv, output, timeout):
            rc = self.transport(argv, output, timeout)
            ctl = m.read(self.control)
            ctl['drain'] = True
            m.atomic(self.control, ctl)
            return rc
        result = self.relay.run(self.control, 'owner', transport=drain)
        self.assertEqual(len(self.calls), 1)
        self.assertIn('drain', result['blocker'])
        self.configure(workers=4)
        with self.assertRaisesRegex(ValueError, 'immutable file differs'):
            self.run_relay(workers=4)
        state = m.read(self.f / 'state.json')
        state['tasks'][0]['taskId'] = 'new-owner'
        m.atomic(self.f / 'state.json', state)
        ctl = m.read(self.control)
        ctl['reservation']['taskId'] = 'new-owner'
        m.atomic(self.control, ctl)
        self.relay.run(self.control, 'new-owner', workers=4, transport=self.transport)
        self.assertEqual(len(self.calls), 2)

    def test_atomic_prepare_recovery(self):
        self.add()
        real = m.atomic
        def fail_index(path, obj):
            if Path(path) == self.relay.index:
                raise OSError('simulated parent crash')
            real(path, obj)
        with patch.object(m, 'atomic', side_effect=fail_index):
            with self.assertRaises(OSError):
                self.relay.prepare()
        self.assertEqual(m.read(self.relay.index)[0]['status'], 'pending')
        self.relay.prepare()
        self.assertEqual(m.read(self.relay.index)[0]['status'], 'review_prepared')
        self.assertEqual(len(list(self.relay.reviews.glob('*.input.json'))), 1)

    def test_interrupted_reservation_stays_spent(self):
        self.add(baseline=1)
        self.relay.prepare()
        b = self.relay.load()['bundles'][0]
        rawpath = self.f / 'private/interrupted.raw'
        rawpath.write_text('partial')
        self.relay.save(b, dict(status='pending', attempts=[dict(attempt=1, status='reserved', raw_path=str(rawpath))]))
        self.run_relay()
        self.assertEqual(self.calls, [])
        self.assertEqual(self.relay.ledger(b)['status'], 'exhausted')

    def test_metadata_recovery_does_not_repeat_completed_call(self):
        self.add()
        self.relay.prepare()
        self.run_relay()
        b = self.relay.load()['bundles'][0]
        ledger = self.relay.ledger(b)
        ledger['status'] = 'pending'
        ledger['attempts'][0]['status'] = 'reserved'
        self.relay.save(b, ledger)
        self.run_relay()
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.relay.ledger(b)['status'], 'validated')

    def test_four_workers_use_retained_futures_under_ceiling(self):
        for n in range(4):
            self.add(str(n), fields=[dict(field='type', input_row_index=str(6*n+i)) for i in range(6)])
        self.relay.prepare()
        self.configure(workers=4, extra=4)
        barrier = threading.Barrier(4, timeout=5)
        guard = threading.Lock()
        active = peak = 0
        def concurrent(argv, output, timeout):
            nonlocal active, peak
            with guard:
                active += 1
                peak = max(active, peak)
            barrier.wait()
            result = self.transport(argv, output, timeout)
            with guard:
                active -= 1
            return result
        self.relay.run(self.control, 'owner', workers=4, transport=concurrent)
        self.assertEqual(peak, 4)
        self.assertEqual(len(self.calls), 4)
        self.assertTrue(all(self.relay.ledger(b)['status'] == 'validated' for b in self.relay.load()['bundles']))

    def test_snapshot_does_not_adopt_new_pending_requests(self):
        self.add()
        self.relay.prepare()
        reserved = m.read(self.relay.index)
        self.add('new', fields=[dict(field='type', input_row_index='9')])
        # Simulate the parent appending, retaining the existing reservation.
        m.atomic(self.relay.index, reserved + [self.index[-1]])
        self.relay.prepare()
        self.run_relay()
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(m.read(self.relay.index)[1]['status'], 'pending')

    def test_source_change_during_call_consumes_attempt_without_result(self):
        self.add(baseline=1)
        self.relay.prepare()
        def changed(argv, output, timeout):
            rc = self.transport(argv, output, timeout)
            (self.root / 'primary.txt').write_text('changed source')
            return rc
        self.relay.run(self.control, 'owner', transport=changed)
        b = self.relay.load()['bundles'][0]
        self.assertEqual(self.relay.ledger(b)['status'], 'source_changed')
        self.assertFalse((self.relay.reviews / (b['review_id'] + '.result.json')).exists())
        self.relay.reconcile()
        self.assertEqual(m.read(self.relay.index)[0]['review_attempts'], 2)

    def test_reconcile_blocks_tampered_raw(self):
        self.add()
        self.relay.prepare()
        self.run_relay()
        b = self.relay.load()['bundles'][0]
        Path(self.relay.ledger(b)['attempts'][0]['raw_path']).write_text('changed')
        with self.assertRaisesRegex(ValueError, 'raw response hash changed'):
            self.relay.reconcile()

    def test_interrupted_live_process_group_blocks_recovery(self):
        self.add()
        self.relay.prepare()
        b = self.relay.load()['bundles'][0]
        rawpath = self.f / 'private/interrupted.raw'
        m.atomic(Path(str(rawpath) + '.process.json'), dict(pid=12345, status='running'))
        self.relay.save(b, dict(status='pending', attempts=[dict(attempt=1, status='reserved', raw_path=str(rawpath))]))
        with patch.object(m.os, 'killpg', return_value=None):
            with self.assertRaisesRegex(ValueError, 'process group still exists'):
                self.run_relay()
        self.assertEqual(self.calls, [])

    def test_real_process_lifecycle_mock_cli_timeout(self):
        # The subprocess is a local Python fixture, never agy/a model.
        output = self.f / 'private/process.raw'
        rc = m.cli_transport([sys.executable, '-c', 'import time; time.sleep(20)'], output, .05)
        self.assertEqual(rc, 124)
        self.assertFalse(m.PROCESSES)
        output2 = self.f / 'private/process2.raw'
        rc = m.cli_transport([sys.executable, '-c', 'print("mock CLI")'], output2, 2)
        self.assertEqual(rc, 0)
        self.assertIn('mock CLI', output2.read_text())


if __name__ == '__main__':
    unittest.main()
