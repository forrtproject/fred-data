"""Focused relay contracts; no live model calls."""
import importlib.util
import json
import sys
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('relay', Path(__file__).with_name('run_argon.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RelayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='test_argon_')
        self.root = Path(self.tmp.name)
        self.source = 'The original finding was confirmed.\nThe numbers agreed.'
        self.d = dict(input_row_index=1, field='outcome', method='argon', verdict='shipped_right',
                      corrected_value='successful', quote='The original finding was confirmed.',
                      location='results', reason='The overall verdict confirms this original.')
        self.requested = {m.key(self.d)}
        self.output = self.root / 'answer.txt'

    def tearDown(self):
        self.tmp.cleanup()

    def reply(self, decisions):
        self.output.write_text('## Answer\n' + json.dumps({'decisions': decisions}))
        return m.strict_response(self.output, self.source, self.requested)

    def test_exact_keys(self):
        self.assertEqual(len(self.reply([self.d])['decisions']), 1)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.reply([self.d, self.d])
        with self.assertRaisesRegex(ValueError, 'extra'):
            self.reply([self.d, dict(self.d, input_row_index=2)])
        with self.assertRaisesRegex(ValueError, 'missing'):
            self.reply([])

    def test_literal_not_normalized_quote(self):
        with self.assertRaises(ValueError):
            self.reply([dict(self.d, quote='The original finding was confirmed. The numbers agreed.')])
        with self.assertRaises(ValueError):
            self.reply([dict(self.d, quote='The original finding was confirmed...The numbers agreed.')])
        self.assertTrue(self.reply([dict(self.d, quote=self.source)]))

    def test_partial_preserves_complete_objects_without_repair(self):
        self.output.write_text('## Answer\n{"decisions":[' + json.dumps(self.d) + ',{"field":"outco')
        self.assertEqual(m.partial_response(self.output, self.source, self.requested), [self.d])
        with self.assertRaises(ValueError):
            m.strict_response(self.output, self.source, self.requested)
        self.output.write_text('## Answer\n{"decisions":[' + json.dumps(self.d) + ',' + json.dumps(self.d))
        self.assertEqual(m.partial_response(self.output, self.source, self.requested), [])

    def test_durable_reservation_and_no_overwrite(self):
        state = dict(request_id='test_request', attempts=0, history=[], input_sha256='input', source_sha256='source')
        sp = self.root / 'state.json'
        rec, output = m.reserve(state, sp, 'original prompt', self.root)
        self.assertEqual(json.loads(sp.read_text())['attempts'], 1)
        self.assertEqual(rec['status'], 'reserved')
        output.write_text('prior immutable response')
        resumed = json.loads(sp.read_text())
        rec2, out2 = m.reserve(resumed, sp, 'changed retry feedback', self.root)
        self.assertEqual(rec2['attempt'], 2)
        self.assertNotEqual(output, out2)
        self.assertEqual(output.read_text(), 'prior immutable response')
        with self.assertRaisesRegex(ValueError, 'budget'):
            m.reserve(json.loads(sp.read_text()), sp, 'third', self.root)
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            m.reserve(dict(state, attempts=0), sp, 'reset', self.root)

    def fixture_runner(self, transport):
        source = self.root / 'source.txt'; source.write_text(self.source)
        ip = self.root / 'input.json'
        m.write_json(ip, dict(requested_fields=[self.d]))
        entry = dict(request_id='test_request', file_key='test', input_path=str(ip), input_sha256=m.digest(ip.read_bytes()))
        work = dict(source_path=str(source), source_sha256=m.digest(source.read_bytes()), prior=[], files={},
                    source_instruction='Read '+str(source), coding=str(ip))
        snap = dict(requests=[entry], works={'test':work}, codebook_sha256=m.digest((m.ROOT/'codebook.md').read_bytes()))
        return m.Runner(snap, transport=transport, outdir=self.root), entry

    def test_resume_spends_reserved_attempt_then_skips_terminal(self):
        calls = []
        def transport(argv, output, source, requested, timeout):
            calls.append(argv)
            output.write_text('## Answer\n'+json.dumps({'decisions':[self.d]}))
            return dict(returncode=0, timed_out=False, closed_after_valid_answer=False)
        runner, entry = self.fixture_runner(transport)
        work = runner.snap['works']['test']
        state = dict(request_id='test_request', attempts=0, history=[], input_sha256=entry['input_sha256'], source_sha256=work['source_sha256'])
        sp = self.root/'test_request.state.json'
        m.reserve(state, sp, 'interrupted first call', self.root)
        with mock.patch.object(m, 'reserved_process_live', return_value=False):
            runner.one(entry)
        final = json.loads(sp.read_text())
        self.assertEqual(final['attempts'],2)
        self.assertEqual(final['status'],'validated')
        self.assertEqual(len(calls),1)
        self.assertIn('RETRY FEEDBACK', calls[0][2])
        runner.one(entry)
        self.assertEqual(len(calls),1)

    def test_scheduler_concurrency_and_finite_snapshot(self):
        snap = {'requests':[dict(request_id=str(n)) for n in range(17)]}
        runner = m.Runner(snap, outdir=self.root)
        guard = threading.Lock()
        active = peak = total = 0
        def one(entry):
            nonlocal active, peak, total
            with guard:
                active += 1; peak = max(peak, active); total += 1
            time.sleep(.015)
            with guard:
                active -= 1
        runner.one = one
        runner.progress = lambda finished=False: None
        (self.root/'progress.json').write_text('{}')
        self.assertEqual(runner.run(),0)
        self.assertEqual(peak,3)
        self.assertEqual(total,17)
        self.assertEqual(active,0)

    def test_single_worker_transport_resume_budgets_and_terminal_skip(self):
        calls = []
        guard = threading.Lock()
        active = peak = 0
        def transport(argv, output, source, requested, timeout):
            nonlocal active, peak
            with guard:
                active += 1
                peak = max(peak, active)
            try:
                state = json.loads(output.with_name(output.name.split('.attempt')[0]+'.state.json').read_text())
                self.assertEqual(state['status'], 'running')
                self.assertEqual(state['history'][-1]['status'], 'reserved')
                self.assertEqual(state['attempts'], int(output.name.split('.attempt')[1].split('.')[0]))
                self.assertTrue(output.with_suffix('.reservation.json').exists())
                self.assertEqual(timeout, 660)
                self.assertEqual(argv[argv.index('--model')+1], 'Gemini 4 Argon (High)')
                self.assertEqual(argv[argv.index('--print-timeout')+1], '10m')
                self.assertIn('--sandbox', argv)
                calls.append(output.name)
                time.sleep(.015)
                # Complete schema failure spends the first fresh attempt without
                # tripping the infrastructure circuit; its retry must still fit.
                decisions = [] if output.name == 'fresh.attempt1.txt' else [self.d]
                output.write_text('## Answer\n'+json.dumps({'decisions': decisions}))
                return dict(returncode=0, timed_out=False, closed_after_valid_answer=False)
            finally:
                with guard:
                    active -= 1
        original, entry = self.fixture_runner(transport)
        entries = [dict(entry, request_id=rid) for rid in ('validated', 'exhausted', 'retry', 'fresh', 'pending')]
        original.snap['requests'] = entries
        work = original.snap['works']['test']
        for rid, status, attempts in [('validated', 'validated', 1), ('exhausted', 'exhausted', 2), ('retry', 'retry_pending', 1)]:
            state = dict(request_id=rid, attempts=0, history=[], input_sha256=entry['input_sha256'],
                         source_sha256=work['source_sha256'])
            sp = self.root / (rid+'.state.json')
            for _ in range(attempts):
                _, output = m.reserve(state, sp, 'retained old prompt', self.root)
                output.write_text('retained old response')
            state.update(status=status, reason='retained failure' if status == 'retry_pending' else None)
            m.write_json(sp, state)
        old = {p: p.read_bytes() for p in self.root.iterdir()
               if '.attempt' in p.name or p.name in ('validated.state.json', 'exhausted.state.json')}
        runner = m.Runner(original.snap, transport=transport, outdir=self.root, workers=1)
        self.assertEqual(runner.run(), 0)
        self.assertEqual(calls, ['retry.attempt2.txt', 'fresh.attempt1.txt', 'fresh.attempt2.txt', 'pending.attempt1.txt'])
        self.assertEqual((peak, active, runner.peak), (1, 0, 1))
        for p, raw in old.items():
            self.assertEqual(p.read_bytes(), raw)
        states = [json.loads((self.root/(e['request_id']+'.state.json')).read_text()) for e in entries]
        self.assertEqual([s['attempts'] for s in states], [1, 2, 2, 2, 1])
        self.assertEqual([s['status'] for s in states], ['validated', 'exhausted', 'validated', 'validated', 'validated'])
        for state in states:
            self.assertEqual(state['input_sha256'], entry['input_sha256'])
            self.assertEqual(state['source_sha256'], work['source_sha256'])
        self.assertEqual(json.loads((self.root/'progress.json').read_text())['attempts'], 8)
        # A new execution task has no old stop event, but retains all disk budgets.
        resumed = m.Runner(original.snap, transport=transport, outdir=self.root, workers=1)
        self.assertEqual(resumed.run(), 0)
        self.assertEqual(len(calls), 4)

    def test_cli_passes_worker_cap_and_preserves_default(self):
        with mock.patch.object(m, 'OUT', self.root), mock.patch.object(m, 'snapshot', return_value={}), \
                mock.patch.object(m, 'Runner') as runner, mock.patch.object(m.signal, 'signal'):
            runner.return_value.run.return_value = 0
            for argv, expected in [([], 3), (['--workers', '1'], 1),
                                   (['--workers', '2'], 2), (['--workers', '3'], 3)]:
                with self.subTest(argv=argv):
                    self.assertEqual(m.main(argv), 0)
                    runner.assert_called_with({}, workers=expected, max_calls=None, owner_task_id=None, control=None)

    def test_invalid_workers_rejected_before_dispatch_or_output(self):
        for workers in (0, 4, -1, 1.5, True, '1', None):
            with self.subTest(workers=workers), self.assertRaisesRegex(ValueError, 'workers'):
                m.Runner({}, transport=lambda *args: self.fail('must not dispatch'), workers=workers)
        with mock.patch.object(m, 'OUT') as out, mock.patch.object(m, 'snapshot') as snapshot, \
                mock.patch.object(m, 'Runner') as runner, mock.patch('sys.stderr'):
            for value in ('0', '4', '-1', '1.5', 'invalid'):
                with self.subTest(value=value), self.assertRaises(SystemExit) as raised:
                    m.main(['--workers', value])
                self.assertEqual(raised.exception.code, 2)
            out.mkdir.assert_not_called()
            snapshot.assert_not_called()
            runner.assert_not_called()

    def test_infrastructure_breaker_stops_unchanged_failure_wave(self):
        calls = []
        def transport(argv, output, source, requested, timeout):
            calls.append(argv)
            output.write_text('model configuration unavailable: synthetic test')
            return dict(returncode=1, timed_out=False, closed_after_valid_answer=False)
        runner, entry = self.fixture_runner(transport)
        runner.snap['requests'] = [dict(entry, request_id='test_request_'+str(i)) for i in range(20)]
        self.assertEqual(runner.run(), 2)
        self.assertGreaterEqual(len(calls), 5)
        self.assertLessEqual(len(calls), 7)  # at most the two already-active calls
        self.assertIn('model configuration unavailable', runner.blocker)
        self.assertTrue(runner.stop.is_set())
        self.assertEqual(runner.active, 0)

    def test_exhausted_zero_valid_objects_has_explicit_partial_result(self):
        def transport(argv, output, source, requested, timeout):
            output.write_text('synthetic unavailable model')
            return dict(returncode=1, timed_out=False, closed_after_valid_answer=False)
        runner, entry = self.fixture_runner(transport)
        runner.one(entry)
        state = json.loads((self.root/'test_request.state.json').read_text())
        result = json.loads((self.root/'test_request.result.json').read_text())
        self.assertEqual(state['status'], 'exhausted')
        self.assertEqual(state['attempts'], 2)
        self.assertTrue(result['partial'])
        self.assertEqual(result['decisions'], [])
        self.assertEqual(result['provenance']['attempt'], 2)
        self.assertTrue((self.root/'test_request.attempt1.result.json').exists())

    def test_changed_source_prevents_dispatch(self):
        def transport(*args, **kwargs):
            self.fail('changed source must never dispatch')
        runner, entry = self.fixture_runner(transport)
        Path(runner.snap['works']['test']['source_path']).write_text('changed primary source')
        runner.one(entry)
        state = json.loads((self.root/'test_request.state.json').read_text())
        self.assertEqual(state['status'], 'source_changed')
        self.assertEqual(state['attempts'], 0)

    def test_transport_early_close_uses_runner_strict_validator(self):
        for name, decisions, valid in [('valid', [self.d], True),
                                       ('duplicate', [self.d, self.d], False),
                                       ('quote', [dict(self.d, quote='invented')], False)]:
            with self.subTest(name=name):
                output = self.root / (name + '.raw')
                output.touch()  # Match the real runner's durable empty reservation.
                raw = '## Answer\n' + json.dumps({'decisions': decisions})
                argv = [sys.executable, '-c', 'import time; print(' + repr(raw) + ',flush=True); time.sleep(30)']
                meta = m.a.run_transport(argv, output, self.source, self.requested,
                                         timeout=.3, quiet_seconds=.03)
                self.assertEqual(meta['closed_after_valid_answer'], valid)
                self.assertEqual(meta['timed_out'], not valid)

    def test_strict_gate_keeps_invalid_transport_alive(self):
        self.output.write_text('## Answer\n'+json.dumps({'decisions':[self.d, self.d]}))
        with self.assertRaises(ValueError):
            m.a.read_response(self.output,self.source,self.requested,require_heading=True)


    def bounded(self, original, owner='round-1', limit=1):
        return m.Runner(original.snap, transport=original.transport, outdir=self.root,
                        workers=1, max_calls=limit, owner_task_id=owner)

    def test_bounded_failure_retry_and_same_owner_restart(self):
        calls = []
        def transport(argv, output, *args, **kwargs):
            calls.append(output.name)
            output.write_text('## Answer\n{"decisions":[]}')  # invalid schema still spends a call
            return dict(returncode=0, timed_out=False, closed_after_valid_answer=False)
        original, entry = self.fixture_runner(transport)
        first = self.bounded(original)
        self.assertEqual(first.run(), 0)
        self.assertEqual(calls, ['test_request.attempt1.txt'])
        state = json.loads((self.root/'test_request.state.json').read_text())
        self.assertEqual(state['status'], 'retry_pending')
        self.assertEqual(state['history'][0]['owner_task_id'], 'round-1')
        self.assertEqual(self.bounded(original).run(), 0)
        self.assertEqual(len(calls), 1)
        with self.assertRaisesRegex(ValueError, 'binding changed'):
            self.bounded(original, limit=2)
        self.assertEqual(self.bounded(original, owner='round-2').run(), 0)
        self.assertEqual(len(calls), 2)
        self.assertEqual(self.bounded(original, owner='round-3').run(), 0)
        self.assertEqual(len(calls), 2)  # exhausted cannot spend another round

    def test_max_two_counts_invalid_retry_and_collects_all_calls(self):
        calls = []
        def transport(argv, output, *args, **kwargs):
            calls.append(output.name)
            output.write_text('## Answer\n'+json.dumps({'decisions': [] if len(calls)==1 else [self.d]}))
            return dict(returncode=0, timed_out=False, closed_after_valid_answer=False)
        original, entry = self.fixture_runner(transport)
        original.snap['requests'].append(dict(entry, request_id='unstarted'))
        runner = self.bounded(original, limit=2)
        self.assertEqual(runner.run(),0)
        self.assertEqual(calls,['test_request.attempt1.txt','test_request.attempt2.txt'])
        self.assertEqual(runner.active,0)
        self.assertEqual(self.bounded(original, limit=2).run(),0)
        self.assertEqual(len(calls),2)
        self.assertFalse((self.root/'unstarted.state.json').exists())

    def test_bounded_interrupted_reservation_counts_and_collects_without_extra(self):
        original, entry = self.fixture_runner(mock.Mock(side_effect=AssertionError('no dispatch')))
        self.bounded(original)  # durable execution binding, before reservation
        work = original.snap['works']['test']
        state = dict(request_id='test_request', attempts=0, history=[], input_sha256=entry['input_sha256'], source_sha256=work['source_sha256'])
        rec, output = m.reserve(state, self.root/'test_request.state.json', 'interrupted', self.root, 'round-1')
        output.write_text('## Answer\n'+json.dumps({'decisions':[self.d]}))
        with mock.patch.object(m, 'reserved_process_live', return_value=False):
            self.assertEqual(self.bounded(original).run(), 0)
        final = json.loads((self.root/'test_request.state.json').read_text())
        self.assertEqual((final['status'], final['attempts']), ('validated', 1))
        original.transport.assert_not_called()
        self.assertEqual(self.bounded(original, owner='round-2').run(), 0)
        original.transport.assert_not_called()

    def test_exact_owned_live_process_prevents_recovery(self):
        original, entry = self.fixture_runner(mock.Mock(side_effect=AssertionError('no dispatch')))
        work = original.snap['works']['test']
        state = dict(request_id='test_request', attempts=0, history=[], input_sha256=entry['input_sha256'], source_sha256=work['source_sha256'])
        rec, output = m.reserve(state, self.root/'test_request.state.json', 'interrupted', self.root, 'round-1')
        m.write_json(Path(str(output)+'.process.json'), dict(pid=913, pgid=913))
        before = (self.root/'test_request.state.json').read_bytes()
        original.snap['requests'].insert(0, dict(entry, request_id='fresh_before_orphan'))
        with mock.patch.object(m.os, 'killpg') as probe:
            self.assertEqual(self.bounded(original, owner='round-2').run(), 2)
            probe.assert_called_once_with(913, 0)
        self.assertEqual((self.root/'test_request.state.json').read_bytes(), before)
        original.transport.assert_not_called()

    def test_persistent_five_failure_circuit_across_one_call_rounds(self):
        calls = []
        def transport(argv, output, *args, **kwargs):
            calls.append(output.name)
            output.write_text('infrastructure failure')
            return dict(returncode=1, timed_out=False, closed_after_valid_answer=False)
        original, entry = self.fixture_runner(transport)
        original.snap['requests'] = [dict(entry, request_id='request'+str(n)) for n in range(4)]
        for n in range(5):
            runner = self.bounded(original, owner='round-'+str(n))
            self.assertEqual(runner.run(), 2 if n == 4 else 0)
            self.assertEqual(runner.infra_streak, n+1)
        self.assertEqual(len(calls), 5)
        runner = self.bounded(original, owner='round-next')
        self.assertEqual(runner.run(), 2)
        self.assertEqual(len(calls), 5)
        self.assertTrue(json.loads((self.root/'progress.json').read_text())['infrastructure_circuit_open'])

    def test_control_requires_actual_active_registration_before_reservation(self):
        transport = mock.Mock(side_effect=AssertionError('no model call'))
        original, entry = self.fixture_runner(transport)
        m.write_json(self.root/'snapshot.json',original.snap)
        control = self.root/'control.json'
        reservation = dict(taskId='round-1',workers=1,max_calls=1,
            snapshot_sha256=m.digest((self.root/'snapshot.json').read_bytes()),model=m.MODEL,billing='included_subscription')
        m.write_json(control,dict(drain=False,reservation=reservation))
        m.write_json(self.root/'state.json',dict(tasks=[]))
        runner = self.bounded(original)
        runner.control = control
        with mock.patch.object(m,'HERE',self.root), self.assertRaisesRegex(ValueError,'registration'):
            runner.one(entry)
        self.assertFalse((self.root/'test_request.attempt1.reservation.json').exists())
        transport.assert_not_called()
        m.write_json(self.root/'state.json',dict(tasks=[dict(taskId='round-1',status='running',lane='argon_runner',slot_cost=4)]))
        with mock.patch.object(m,'HERE',self.root):
            runner.check_control()
        reservation['taskId']='unowned'
        m.write_json(control,dict(drain=False,reservation=reservation))
        with mock.patch.object(m,'HERE',self.root), self.assertRaisesRegex(ValueError,'ownership'):
            runner.check_control()

    def test_default_transport_records_owned_group_at_launch(self):
        def transport(argv, output, timeout, **kwargs):
            kwargs['on_start'](mock.Mock(pid=918))
            self.assertEqual(json.loads(Path(str(output)+'.process.json').read_text())['pgid'],918)
            self.assertEqual(timeout,660)
            self.assertTrue(kwargs['reserved_output'])
            return dict(returncode=0)
        with mock.patch.object(m.a,'owned_transport',side_effect=transport):
            self.assertEqual(m.field_transport(['fake'],self.output,self.source,self.requested),dict(returncode=0))

    def test_runner_failure_still_collects_other_retained_futures(self):
        runner = m.Runner(dict(requests=[dict(request_id=str(n)) for n in range(3)]),outdir=self.root)
        ready = threading.Barrier(3)
        collected = []
        def one(entry):
            ready.wait(timeout=2)
            if entry['request_id']=='0':
                raise ValueError('mock coordinator failure')
            time.sleep(.02)
            collected.append(entry['request_id'])
        runner.one = one
        runner.progress = lambda finished=False: None
        (self.root/'progress.json').write_text('{}')
        self.assertEqual(runner.run(),2)
        self.assertEqual(sorted(collected),['1','2'])

    def test_invalid_bounded_cli_rejected_before_outputs(self):
        for args in [ ['--max-calls','0'], ['--max-calls','1'],
                     ['--workers','2','--max-calls','1','--owner-task-id','owner'] ]:
            with mock.patch.object(m, 'OUT') as out, mock.patch.object(m, 'Runner') as runner:
                with self.assertRaises(SystemExit):
                    m.main(args)
                out.mkdir.assert_not_called()
                runner.assert_not_called()


if __name__ == '__main__':
    unittest.main()
