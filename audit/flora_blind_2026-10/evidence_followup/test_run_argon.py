"""Focused relay contracts; no live model calls."""
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest

spec = importlib.util.spec_from_file_location('relay', Path(__file__).with_name('run_argon.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RelayTests(unittest.TestCase):
    def setUp(self):
        m.OUT.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=m.OUT, prefix='test_')
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
        runner.one(entry)
        final = json.loads(sp.read_text())
        self.assertEqual(final['attempts'],2)
        self.assertEqual(final['status'],'validated')
        self.assertEqual(len(calls),1)
        self.assertIn('RETRY FEEDBACK', calls[0][2])
        runner.one(entry)
        self.assertEqual(len(calls),1)

    def test_scheduler_concurrency_and_finite_snapshot(self):
        snap = {'requests':list(range(17))}
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

    def test_changed_source_prevents_dispatch(self):
        def transport(*args, **kwargs):
            self.fail('changed source must never dispatch')
        runner, entry = self.fixture_runner(transport)
        Path(runner.snap['works']['test']['source_path']).write_text('changed primary source')
        runner.one(entry)
        state = json.loads((self.root/'test_request.state.json').read_text())
        self.assertEqual(state['status'], 'source_changed')
        self.assertEqual(state['attempts'], 0)

    def test_strict_gate_keeps_invalid_transport_alive(self):
        self.output.write_text('## Answer\n'+json.dumps({'decisions':[self.d, self.d]}))
        with self.assertRaises(ValueError):
            m.a.read_response(self.output,self.source,self.requested,require_heading=True)


if __name__ == '__main__':
    unittest.main()
