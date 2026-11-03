"""Coverage recognition must fail closed on altered or unqualified evidence."""
import copy
import unittest
from pathlib import Path
from unittest.mock import patch

import resolve_sol_completion as coverage


class PriorCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior = coverage.read(coverage.T / 'prior_sol_receipt_checks.json')['documents']
        cls.queue = coverage.read(coverage.T / 'comparison_review_queue.json')['documents']

    def qualify(self, doc, record=None):
        return coverage.qualify_prior(doc, record or self.prior[doc], self.queue[doc])

    def test_recognizes_verified_status_without_old_prefix(self):
        entry = self.qualify('document_0388')
        self.assertTrue(entry['registered_literal_reading_verified'])
        self.assertFalse(entry['scientific_acceptance'])

    def test_alternate_layout_is_never_relabelled_literal(self):
        entry = self.qualify('document_0022')
        self.assertFalse(entry['registered_literal_reading_verified'])
        self.assertTrue(entry['source_qualification_requires_field_gate_review'])
        self.assertIn('export_limit', entry['coverage_class'])

    def test_normalized_body_keeps_qualification(self):
        entry = self.qualify('document_0264')
        self.assertFalse(entry['registered_literal_reading_verified'])
        self.assertIn('normalization', entry['coverage_class'])

    def test_unproven_reading_cannot_enter_allowlist(self):
        record = copy.deepcopy(self.prior['document_0388'])
        record['status'] = 'complete_registered_source_reading_unproven_fresh_Sol_required'
        with self.assertRaisesRegex(AssertionError, 'Unrecognized'):
            self.qualify('document_0388', record)

    def test_unresolved_quote_blocks_reuse(self):
        record = copy.deepcopy(self.prior['document_0388'])
        record['quote_check_failures'] = ['planted failure']
        with self.assertRaisesRegex(AssertionError, 'quote'):
            self.qualify('document_0388', record)

    def test_wrong_source_hash_blocks_reuse(self):
        record = copy.deepcopy(self.prior['document_0388'])
        record['source_sha256'] = '0' * 64
        with self.assertRaises(AssertionError):
            self.qualify('document_0388', record)

    def test_coding_change_blocks_reuse(self):
        record = copy.deepcopy(self.prior['document_0388'])
        record['prior_coding_sha256'] = '0' * 64
        with self.assertRaises(AssertionError):
            self.qualify('document_0388', record)

    def test_projection_scientific_drift_blocks_reuse(self):
        real_project = coverage.project

        def drift(*args):
            result, ledger = real_project(*args)
            result['targets'][0]['outcome'] = 'planted wrong outcome'
            return result, ledger

        with patch.object(coverage, 'project', drift):
            with self.assertRaisesRegex(AssertionError, 'Projection drift'):
                self.qualify('document_0388')

    def test_all_original_gaps_have_one_route(self):
        result = coverage.build()
        self.assertEqual(len(result['documents']), 46)
        self.assertEqual(sum(result['route_counts'].values()), 46)
        self.assertEqual(result['route_counts']['reuse_existing_prior'], 27)
        self.assertEqual(result['route_counts']['first_eligible_fresh_comparison'], 13)
        self.assertEqual(result['route_counts']['same_report_body_reuse_after_0660'], 1)
        self.assertFalse(result['all_fields_scientifically_accepted'])
        self.assertTrue(all(not x['scientific_acceptance'] for x in result['documents'].values()))


if __name__ == '__main__':
    unittest.main()
