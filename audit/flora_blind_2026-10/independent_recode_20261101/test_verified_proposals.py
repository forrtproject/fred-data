"""Reject incompatible fixes even when individual model outputs are valid."""
import hashlib
import json
import unittest

from build_verified_proposals import checked_replacements, current_alignment, ids, original_replacements


class ProposalDependencies(unittest.TestCase):
    def setUp(self):
        self.row = {'type': 'replication', 'outcome': 'failed'}
        self.result = {'record_type': 'reproduction'}
        self.target = {'outcome': '', 'outcome_computation': 'computational issues',
                       'outcome_robustness': 'robustness challenges'}

    def test_type_conversion_cannot_ship_as_an_outcome_only_fix(self):
        decision = {'proposal_fields': ['outcome'], 'replacement_fields': {
                    'outcome': 'computational issues, robustness challenges'}}
        with self.assertRaisesRegex(AssertionError, 'joint remedy'):
            checked_replacements(self.row, self.result, self.target, decision)

    def test_joint_conversion_preserves_both_result_axes(self):
        fields = {'type': 'reproduction', 'outcome': 'computational issues, robustness challenges'}
        decision = {'proposal_fields': ['type', 'outcome'], 'replacement_fields': fields}
        self.assertEqual(checked_replacements(self.row, self.result, self.target, decision), fields)

    def test_individually_valid_but_different_outcome_cannot_enter_fix(self):
        decision = {'proposal_fields': ['outcome'], 'replacement_fields': {'outcome': 'successful'}}
        with self.assertRaisesRegex(AssertionError, 'independently coded'):
            checked_replacements(self.row, {'record_type': 'replication'}, {'outcome': 'mixed'}, decision)

    def test_uncertified_identity_change_cannot_hide_in_field_bundle(self):
        decision = {'proposal_fields': ['outcome'], 'replacement_fields': {
                    'outcome': 'mixed', 'doi_o': '10.1/another-original'}}
        with self.assertRaisesRegex(AssertionError, 'Unvalidated field'):
            checked_replacements(self.row, {'record_type': 'replication'}, {'outcome': 'mixed'}, decision)

    def test_axis_fix_preserves_the_other_axis_and_replaces_complete_csv_value(self):
        row = {'type': 'reproduction', 'outcome': 'computational issues, robust'}
        target = {'outcome_computation': 'computationally reproducible', 'outcome_robustness': 'robust'}
        decision = {'proposal_fields': ['outcome_computation'], 'replacement_fields': {
                    'outcome': 'computationally reproducible, robust'}}
        self.assertEqual(checked_replacements(row, self.result, target, decision), decision['replacement_fields'])
        target['outcome_robustness'] = 'robustness challenges'
        with self.assertRaisesRegex(AssertionError, 'dependent reproduction axis'):
            checked_replacements(row, self.result, target, decision)

    def test_axis_fix_requires_both_axes_and_correct_csv_encoding(self):
        row = {'type': 'reproduction', 'outcome': 'computational issues, robustness not checked'}
        decision = {'proposal_fields': ['outcome_computation'], 'replacement_fields': {
                    'outcome': 'computationally reproducible, robustness not checked'}}
        target = {'outcome_computation': 'computationally reproducible', 'outcome_robustness': 'not checked'}
        self.assertEqual(checked_replacements(row, self.result, target, decision), decision['replacement_fields'])
        target['outcome_robustness'] = ''
        with self.assertRaisesRegex(AssertionError, 'Both reproduction axes'):
            checked_replacements(row, self.result, target, decision)

    def test_pair_check_recognizes_doi_and_osf_alias_forms(self):
        a = {'doi_r': 'https://doi.org/10.17605/OSF.IO/ABC12', 'alt_identifier_r': 'https://doi.org/10.1111/Example'}
        b = {'doi_r': 'https://osf.io/abc12/', 'alt_identifier_r': '10.1111/example'}
        self.assertEqual(ids(a, 'r'), ids(b, 'r'))

    def test_non_doi_report_requires_its_exact_registered_source_url(self):
        url = 'https://example.org/Report.pdf'
        row = {'doi_r': 'NA', 'alt_identifier_r': 'NA', 'url_r': url}
        source = {'parent_work_key': url.lower(), 'metadata': {'source_url': url}}
        current_alignment(row, source)
        source['metadata']['source_url'] = 'https://example.org/AnotherReport.pdf'
        with self.assertRaisesRegex(AssertionError, 'source URL differs'):
            current_alignment(row, source)

    def test_url_cannot_bypass_a_disagreeing_current_doi(self):
        row = {'doi_r': '10.1/actual', 'url_r': 'https://example.org/Report.pdf'}
        source = {'parent_work_key': row['url_r'].lower(), 'metadata': {'source_url': row['url_r']}}
        with self.assertRaisesRegex(AssertionError, 'identifier differs'):
            current_alignment(row, source)

    def test_original_remedy_replaces_all_bibliographic_fields_and_clears_old_oa(self):
        metadata = {'DOI': '10.1111/example', 'title': ['Actual retested study.'],
                    'container-title': ['Correct Journal'], 'volume': '53', 'issue': '4', 'page': '579-590',
                    'author': [{'given': 'Nathalie', 'family': 'klein Selle', 'sequence': 'first'}],
                    'published-print': {'date-parts': [[2016, 4]]},
                    'published-online': {'date-parts': [[2015, 11, 30]]}}
        fields = original_replacements(metadata)
        self.assertEqual(fields['year_o'], '2016')
        self.assertEqual(fields['title_o'], 'Actual retested study')
        self.assertEqual(fields['journal_o'], 'Correct Journal')
        self.assertEqual(fields['doi_o_hash'], hashlib.md5(b'10.1111/example').hexdigest()[:3])
        self.assertEqual(fields['oa_url_o'], 'NA')
        self.assertEqual(fields['alt_identifier_o'], 'NA')
        self.assertEqual(json.loads(fields['author_o'])[0]['family'], 'klein Selle')
        for key in ['apa_ref_o', 'bibtex_ref_o', 'url_o']:
            self.assertIn('10.1111/example', fields[key])
        self.assertEqual(set(fields), {'doi_o', 'alt_identifier_o', 'doi_o_hash', 'title_o',
                        'author_o', 'journal_o', 'year_o', 'volume_o', 'issue_o', 'pages_o',
                        'apa_ref_o', 'bibtex_ref_o', 'url_o', 'language_o', 'oa_url_o'})


if __name__ == '__main__':
    unittest.main()
