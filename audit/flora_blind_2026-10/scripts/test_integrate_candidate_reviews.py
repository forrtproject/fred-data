"""Parent coverage contracts for envelopes mixing approved and held requests."""
import unittest

from integrate_candidate_reviews import mark_parent_coverage


class ParentCoverageTests(unittest.TestCase):
    def test_other_request_in_envelope_remains_pending(self):
        records = [dict(decision=dict(request_id=rid, file_key=fk, target_index=0))
                   for rid, fk in [('approved', 'a'), ('held', 'b')]]
        first = dict(request_id='approved')
        held = dict(request_id='held', status='parent_inspected_integrated')
        mark_parent_coverage(first, records, {('a', 0)})
        mark_parent_coverage(held, records, {('a', 0)})
        self.assertEqual(first['status'], 'parent_inspected_integrated')
        self.assertEqual(held['status'], 'expert_review_complete_pending_parent')
        self.assertEqual(held['parent_pending_keys'], [['b', 0]])

    def test_partial_target_request_stays_open_until_every_target_inspected(self):
        records = [dict(decision=dict(request_id='r', file_key='a', target_index=i))
                   for i in [1, 2]]
        entry = dict(request_id='r')
        mark_parent_coverage(entry, records, {('a', 2)})
        self.assertEqual(entry['status'], 'expert_review_complete_pending_parent')
        self.assertEqual(entry['parent_pending_keys'], [['a', 1]])
        mark_parent_coverage(entry, records, {('a', 1), ('a', 2)})
        self.assertEqual(entry['status'], 'parent_inspected_integrated')
        self.assertEqual(entry['parent_pending_keys'], [])

    def test_row_field_coverage_uses_string_indices_and_ignores_other_requests(self):
        records = [dict(decision=dict(request_id='r', file_key='a',
                                      input_row_index=7, field=field))
                   for field in ['original', 'outcome']]
        entry = dict(request_id='r')
        mark_parent_coverage(entry, records, {('a', '7', 'original')}, fields=True)
        self.assertEqual(entry['parent_pending_keys'], [['a', '7', 'outcome']])

    def test_unmatched_request_cannot_be_marked_complete(self):
        with self.assertRaisesRegex(ValueError, 'No validated keys'):
            mark_parent_coverage(dict(request_id='missing'), [], set())


if __name__ == '__main__':
    unittest.main()
