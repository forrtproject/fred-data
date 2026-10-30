import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from integrate_validation import checked_merge

B = Path(__file__).resolve().parent.parent


class FollowupIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.before = json.loads((Path(__file__).resolve().parent / 'fixtures' / 'integration_before.json').read_text())
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

    @patch('integrate_validation.quote_ok', return_value=True)
    def test_locator_revisit_requires_explicit_new_context(self, _):
        self.before['original']['status'] = 'locator_insufficient'
        with self.assertRaises(AssertionError):
            checked_merge(self.before, self.after, 'original', '/tmp/source.txt')
        result = checked_merge(self.before, self.after, 'original', '/tmp/source.txt', True)
        self.assertEqual(result['original']['n']['value'], '123')
        self.before['original']['status'] = 'done'
        with self.assertRaises(AssertionError):
            checked_merge(self.before, self.after, 'original', '/tmp/source.txt', True)

    def test_failed_retry_preserves_existing_failure(self):
        self.after = copy.deepcopy(self.before)
        self.after['original']['status'] = 'timeout'
        result = checked_merge(self.before, self.after, 'original', '/tmp/source.txt')
        self.assertEqual(result, self.before)

    def test_available_source_with_ambiguous_target_refines_status(self):
        self.after = copy.deepcopy(self.before)
        self.after['original']['status'] = 'locator_insufficient'
        self.after['original']['target_description'] = 'Primary paper obtained; outcome unspecified'
        result = checked_merge(self.before, self.after, 'original', '/tmp/source.txt')
        self.assertEqual(result['original']['status'], 'locator_insufficient')
        self.assertEqual(result['replication'], self.before['replication'])
        self.assertIsNone(result['original']['p']['value'])


if __name__ == '__main__':
    unittest.main()
