import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from integrate_validation import checked_merge

B = Path(__file__).resolve().parent.parent


class FollowupIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.before = json.loads((B / 'extractions' / '1426.json').read_text())
        self.after = copy.deepcopy(self.before)
        self.after['original']['status'] = 'done'
        self.after['original']['target_match'] = True
        self.after['original']['n'].update(value='123', source_path='/tmp/source.txt',
                                          confident=True, quote='Participants', location='p. 2')

    @patch('integrate_validation.quote_ok', return_value=True)
    def test_only_target_side_changes(self, _):
        self.before['replication']['status'] = 'done'
        self.before['reported_success'].update(status='done', value='mixed')
        result = checked_merge(self.before, self.after, 'original', '/tmp/source.txt')
        self.assertEqual(result['original']['n']['value'], '123')
        self.assertEqual(result['replication'], self.before['replication'])
        self.assertEqual(result['reported_success'], self.before['reported_success'])

    @patch('integrate_validation.quote_ok', return_value=False)
    def test_unmatched_quote_is_rejected(self, _):
        with self.assertRaises(AssertionError):
            checked_merge(self.before, self.after, 'original', '/tmp/source.txt')

    def test_unaccepted_source_is_rejected(self):
        with self.assertRaises(AssertionError):
            checked_merge(self.before, self.after, 'original', '/tmp/other.txt')

    def test_previously_completed_target_is_protected(self):
        self.before['original']['status'] = 'done'
        with self.assertRaises(AssertionError):
            checked_merge(self.before, self.after, 'original', '/tmp/source.txt')

    def test_failed_retry_preserves_existing_failure(self):
        self.after = copy.deepcopy(self.before)
        self.after['original']['status'] = 'timeout'
        result = checked_merge(self.before, self.after, 'original', '/tmp/source.txt')
        self.assertEqual(result, self.before)


if __name__ == '__main__':
    unittest.main()
