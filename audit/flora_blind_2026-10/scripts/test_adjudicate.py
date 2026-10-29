import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('adjudicate', Path(__file__).with_name('adjudicate.py'))
a = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(a)
SOURCE = 'The result replicated.'
REQUESTED = {('0', None, 'outcome')}


def answer(quote=SOURCE):
    return {'decisions': [{'input_row_index': 0, 'field': 'outcome', 'method': 'argon',
                          'verdict': 'shipped_right', 'corrected_value': 'successful',
                          'quote': quote, 'location': 'results', 'reason': 'An explicit source verdict.'}]}


class TransportTests(unittest.TestCase):
    def run_fixture(self, obj, requested=REQUESTED, heading=True):
        with tempfile.TemporaryDirectory(prefix='flora-transport-test-') as directory:
            output = Path(directory) / 'reply.txt'
            raw = ('## Answer\n' if heading else '') + json.dumps(obj)
            command = [sys.executable, '-c',
                       'import time; print(' + repr(raw) + ', flush=True); time.sleep(10)']
            meta = a.run_transport(command, output, SOURCE, requested, timeout=0.7, quiet_seconds=0.05)
            return meta, output.read_text()

    def test_complete_valid_answer_closes_hung_owned_transport(self):
        meta, raw = self.run_fixture(answer())
        self.assertTrue(meta['closed_after_valid_answer'])
        self.assertFalse(meta['timed_out'])
        self.assertIn(SOURCE, raw)

    def test_invalid_quote_cannot_trigger_early_close(self):
        meta, _ = self.run_fixture(answer('A nonexistent quotation.'))
        self.assertFalse(meta['closed_after_valid_answer'])
        self.assertTrue(meta['timed_out'])

    def test_incomplete_field_coverage_cannot_trigger_early_close(self):
        meta, _ = self.run_fixture(answer(), REQUESTED | {('1', None, 'outcome')})
        self.assertFalse(meta['closed_after_valid_answer'])
        self.assertTrue(meta['timed_out'])

    def test_live_reply_without_final_heading_cannot_trigger_early_close(self):
        meta, _ = self.run_fixture(answer(), heading=False)
        self.assertFalse(meta['closed_after_valid_answer'])
        self.assertTrue(meta['timed_out'])


class RetryTests(unittest.TestCase):
    def test_final_scope_consumes_only_one_remaining_call_and_cannot_repeat(self):
        for invalid in (False, True):
            with self.subTest(invalid=invalid):
                self.exercise_final_scope(invalid)

    def exercise_final_scope(self, invalid):
        with tempfile.TemporaryDirectory(prefix='flora-final-scope-') as directory:
            root = Path(directory)
            for name in ('texts', 'argon', 'adjudications'):
                (root / name).mkdir()
            requested = [{'input_row_index': 0, 'field': 'outcome'}]
            statepath = root/'argon/file.state.json'
            statepath.write_text(json.dumps({'status': 'scope_review_pending', 'attempts': 1,
                                            'scope_requested_fields': requested}))
            (root/'argon/file.scope_review.input.json').write_text(json.dumps({'requested_fields': requested}))
            (root/'argon/file.scope_review.prompt.txt').write_text('A final source-scope objection.')
            (root/'adjudications/file.json').write_text(json.dumps({'decisions': [], 'scope_review': {'parent_objection': 'Retained.'}}))
            (root/'texts/file.txt').write_text(SOURCE)
            deadline = datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=1)
            (root/'run_manifest.json').write_text(json.dumps({'deadlines': {'adjudication': deadline.isoformat()}}))
            def transport(argv, output, source, fields):
                self.assertEqual(fields, REQUESTED)
                self.assertEqual(argv[argv.index('--model')+1], 'Gemini 4 Argon (High)')
                output.write_text(json.dumps(answer('Not present in source.' if invalid else SOURCE)))
                return {'returncode': 0, 'closed_after_valid_answer': False, 'timed_out': False}
            with patch.object(a, 'R', root), patch.object(a, 'run_transport', side_effect=transport) as calls:
                self.assertEqual(a.final_scope_one('file')['validated'], not invalid)
                self.assertEqual(a.final_scope_one('file')['status'], 'not_pending_or_exhausted')
            self.assertEqual(calls.call_count, 1)
            self.assertEqual(json.loads(statepath.read_text())['attempts'], 2)
            self.assertEqual(json.loads((root/'adjudications/file.json').read_text())['scope_review']['parent_objection'], 'Retained.')

    def test_existing_final_or_pending_work_cannot_dispatch_again(self):
        for status, attempts in [('validated', 1), ('unresolved', 2),
                                 ('scope_review_pending', 1), ('unknown', 2)]:
            with self.subTest(status=status), tempfile.TemporaryDirectory(prefix='flora-resume-test-') as directory:
                root = Path(directory)
                (root / 'argon').mkdir()
                (root / 'argon/file.state.json').write_text(json.dumps({
                    'status': status, 'attempts': attempts, 'input_sha256': 'prior-input'}))
                with patch.object(a, 'R', root), patch.object(a, 'run_transport') as transport:
                    result = a.one('file', [{'input_row_index': '99', 'field': 'type'}])
                transport.assert_not_called()
                self.assertIn(result['status'], ['already_final', 'scope_review_pending'])

    def exercise(self, invalid_both=False, resume=False):
        with tempfile.TemporaryDirectory(prefix='flora-review-test-') as directory:
            root = Path(directory)
            for name in ('texts', 'codings', 'argon', 'adjudications'):
                (root / name).mkdir()
            deadline = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
            (root / 'run_manifest.json').write_text(json.dumps({'deadlines': {'adjudication': deadline.isoformat()}}))
            (root / 'texts/file.txt').write_text(SOURCE)
            (root / 'codings/file.json').write_text(json.dumps({'work_key': 'work', 'evidence_level': 'full_text'}))
            if resume:
                (root/'argon/file.state.json').write_text(json.dumps({
                    'status': 'running', 'attempts': 1, 'reason': 'Runner terminated during first call.'}))
                (root/'argon/file.attempt1.txt').write_text('Retained first-attempt output.')
                (root/'argon/file.prompt.txt').write_text('Retained first-attempt prompt.')
            calls = []

            def csv_rows(path):
                if path.name == 'manifest.csv':
                    return [{'file_key': 'file', 'input_row_index': '0'}]
                return [{key: '' for key in ('doi_r', 'title_r', 'doi_o', 'title_o', 'author_o',
                                             'year_o', 'type', 'outcome', 'outcome_quote', 'source')}]

            def transport(argv, output, source, requested):
                calls.append(argv[2])
                reserved = json.loads((root/'argon/file.state.json').read_text())
                self.assertEqual(reserved['status'], 'running')
                self.assertEqual(reserved['attempts'], 2 if resume else len(calls))
                output.write_text(json.dumps(answer('A nonexistent quotation.' if invalid_both else SOURCE)))
                # An otherwise valid reply with an unexplained nonzero exit is still rejected.
                return {'returncode': 0 if resume or invalid_both or len(calls) == 2 else 7,
                        'timed_out': False, 'closed_after_valid_answer': False}

            with patch.object(a, 'R', root), patch.object(a.c, 'read_csv', side_effect=csv_rows), \
                    patch.object(a, 'run_transport', side_effect=transport):
                result = a.one('file', [{'input_row_index': '0', 'field': 'outcome'}])
            if resume:
                self.assertEqual(len(calls), 1)
                self.assertIn('RETRY FEEDBACK', calls[0])
                self.assertEqual((root/'argon/file.attempt1.txt').read_text(), 'Retained first-attempt output.')
                self.assertEqual((root/'argon/file.before_resume.prompt.txt').read_text(), 'Retained first-attempt prompt.')
                self.assertEqual(result['resume_history'][0]['attempts'], 1)
            else:
                self.assertEqual(len(calls), 2)
                self.assertNotIn('RETRY FEEDBACK', calls[0])
                self.assertIn('RETRY FEEDBACK', calls[1])
            self.assertEqual(result['attempts'], 2)
            self.assertTrue((root / 'argon/file.retry.prompt.txt').exists())
            return result

    def test_unexplained_nonzero_exit_requires_single_retry(self):
        self.assertEqual(self.exercise()['status'], 'validated')

    def test_two_invalid_replies_remain_unresolved_without_third_call(self):
        self.assertEqual(self.exercise(invalid_both=True)['status'], 'unresolved')

    def test_interrupted_call_resumes_only_remaining_attempt_without_overwrite(self):
        self.assertEqual(self.exercise(resume=True)['status'], 'validated')
        self.assertEqual(self.exercise(invalid_both=True, resume=True)['status'], 'unresolved')


class SourceViewTests(unittest.TestCase):
    def fixture(self, root, mode):
        source = 'Original β\x00 text.\nSecond paragraph.'
        original = root / 'source.txt'
        original.write_bytes(source.encode())
        view = root / 'view.json'
        view.write_text(json.dumps({'chunks': ['Original β\x00 ', 'text.\nSecond paragraph.']}))
        metadata = {'format': 'json_chunks', 'view_path': str(view),
                    'original_sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
                    'view_sha256': hashlib.sha256(view.read_bytes()).hexdigest(),
                    'index_path': str(root / 'index.json')}
        if mode != 'valid':
            view.write_text(json.dumps({'chunks': ['A changed source.']}))
            if mode == 'false_roundtrip':
                metadata['view_sha256'] = hashlib.sha256(view.read_bytes()).hexdigest()
        (root / 'lossless_source_views.json').write_text(json.dumps({'file': metadata}))
        return original, source

    def test_lossless_view_preserves_unicode_control_characters_and_spacing(self):
        with tempfile.TemporaryDirectory(prefix='flora-source-view-') as directory:
            root = Path(directory)
            original, source = self.fixture(root, 'valid')
            before = original.read_bytes()
            with patch.object(a, 'R', root):
                instruction = a.source_instruction('file', original, source)
            self.assertIn('lossless JSON chunk view', instruction)
            self.assertEqual(original.read_bytes(), before)

    def test_changed_view_hash_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='flora-source-view-') as directory:
            root = Path(directory)
            original, source = self.fixture(root, 'changed_hash')
            with patch.object(a, 'R', root), self.assertRaisesRegex(ValueError, 'hash mismatch'):
                a.source_instruction('file', original, source)

    def test_changed_words_are_rejected_even_with_updated_view_hash(self):
        with tempfile.TemporaryDirectory(prefix='flora-source-view-') as directory:
            root = Path(directory)
            original, source = self.fixture(root, 'false_roundtrip')
            with patch.object(a, 'R', root), self.assertRaisesRegex(ValueError, 'round-trip'):
                a.source_instruction('file', original, source)


if __name__ == '__main__':
    unittest.main()
