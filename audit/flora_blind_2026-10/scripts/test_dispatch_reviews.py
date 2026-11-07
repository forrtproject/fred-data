import datetime
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest

import dispatch_reviews as d


class DispatcherTests(unittest.TestCase):
    def fixture(self, root, past=False):
        (root / 'argon').mkdir()
        stamp = d.utcnow() + datetime.timedelta(hours=-1 if past else 1)
        (root / 'run_manifest.json').write_text(json.dumps({'deadlines': {'adjudication': stamp.isoformat()}}))
        items = [{'file_key': str(i), 'field': 'outcome', 'input_row_index': i} for i in range(12)]
        path = root / 'selection.json'
        path.write_text(json.dumps({'items': items + items[:2]}))
        return path

    def test_ceiling_deduplication_and_scopes_precede_remaining_work(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            selection = self.fixture(root)
            guard, active, peak, calls = threading.Lock(), 0, 0, []

            def worker(fk, items=None):
                nonlocal active, peak
                with guard:
                    active += 1
                    peak = max(peak, active)
                    calls.append(('base' if items else 'scope', fk))
                if items and fk == '0':
                    d.a.atomic(root / 'argon/0.state.json', {'status': 'scope_review_pending', 'attempts': 1})
                time.sleep(.02)
                if not items:
                    d.a.atomic(root / 'argon/0.state.json', {'status': 'validated', 'attempts': 2})
                with guard:
                    active -= 1
                return {'file_key': fk, 'status': 'validated'}

            summary = d.run([selection], root, worker, worker, emit=lambda *args, **kwargs: None)
            self.assertLessEqual(peak, 4)
            self.assertEqual(len([x for x in calls if x[0] == 'base']), 12)
            self.assertEqual(calls.count(('scope', '0')), 1)
            self.assertLess(calls.index(('scope', '0')), calls.index(('base', '11')))
            self.assertEqual(summary['not_dispatched_before_deadline'], [])

    def test_expired_deadline_dispatches_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            selection = self.fixture(root, past=True)
            def forbidden(*args):
                self.fail('A model call was dispatched after the deadline')
            summary = d.run([selection], root, forbidden, forbidden, emit=lambda *args, **kwargs: None)
            self.assertEqual(len(summary['not_dispatched_before_deadline']), 12)
            self.assertEqual(summary['review_results'], [])

    def test_continuation_deadline_applies_only_while_active(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.fixture(root, past=True)
            path = root / 'run_manifest.json'
            manifest = json.loads(path.read_text())
            original = d.a.adjudication_deadline(root)
            renewed = d.utcnow() + datetime.timedelta(hours=1)
            manifest['continuation'] = {'status': 'active',
                                        'adjudication_deadline': renewed.isoformat()}
            path.write_text(json.dumps(manifest))
            self.assertEqual(d.a.adjudication_deadline(root), renewed)
            manifest['continuation']['status'] = 'complete'
            path.write_text(json.dumps(manifest))
            self.assertEqual(d.a.adjudication_deadline(root), original)

    def test_final_state_cannot_be_redispatched(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            selection = self.fixture(root)
            for i in range(12):
                d.a.atomic(root / 'argon' / f'{i}.state.json', {'status': 'unresolved', 'attempts': 2})
            def forbidden(*args):
                self.fail('An exhausted work was redispatched')
            d.run([selection], root, forbidden, forbidden, emit=lambda *args, **kwargs: None)
