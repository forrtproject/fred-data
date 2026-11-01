"""Reject incompatible fixes even when individual model outputs are valid."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from build_verified_proposals import checked_replacements, completed_field_work, current_alignment, ids, original_alignment, original_identifier_alignment, original_replacements, retained_target_scope_review


class ProposalDependencies(unittest.TestCase):
    def setUp(self):
        self.row = {'type': 'replication', 'outcome': 'failed'}
        self.result = {'record_type': 'reproduction'}
        self.target = {'outcome': '', 'outcome_computation': 'computational issues',
                       'outcome_robustness': 'robustness challenges'}

    def scope_fixture(self, directory, original_status='retain_current'):
        row = {'doi_o': '10.1/original', 'title_o': 'Actual retested study', 'type': 'replication'}
        review = {'field_reviews': [
            {'field_id': '403.original', 'status': original_status,
             'recommended_value': {'doi_o': row['doi_o'], 'title_o': row['title_o']}},
            {'field_id': '403.type', 'status': 'retain_current', 'recommended_value': 'replication'},
            {'field_id': '403.outcome', 'status': 'supported_correction', 'recommended_value': 'mixed'}]}
        directory = Path(directory)
        (directory / 'review.json').write_text(json.dumps(review))
        validation = {'proof_count_verified': 1,
                      'review_file_sha256': hashlib.sha256((directory / 'review.json').read_bytes()).hexdigest(),
                      'parent_corrections': ['Raw reviewer provenance error preserved and corrected.']}
        for name, value in [('parent_validation.json', validation), ('sources_and_proofs.json', {}),
                            ('reading_manifest.json', {})]:
            (directory / name).write_text(json.dumps(value))
        receipt = {'directory': str(directory), 'file_hashes': {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()}}
        return receipt, row

    def test_resolved_target_objection_keeps_raw_review_and_parent_corrections_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt, row = self.scope_fixture(directory)
            retained_target_scope_review(receipt, 403, row, 'mixed')
            with self.assertRaisesRegex(AssertionError, 'disposition differs'):
                retained_target_scope_review(receipt, 403, row, 'successful')

    def test_matching_conditional_outcome_does_not_resolve_target_policy_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt, row = self.scope_fixture(directory, 'policy_boundary')
            with self.assertRaisesRegex(AssertionError, 'objection remains unresolved: original'):
                retained_target_scope_review(receipt, 403, row, 'mixed')

    def test_target_scope_parent_corrections_cannot_change_after_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt, row = self.scope_fixture(directory)
            (Path(directory) / 'parent_validation.json').write_text('{}')
            with self.assertRaisesRegex(AssertionError, 'evidence changed: parent_validation'):
                retained_target_scope_review(receipt, 403, row, 'mixed')

    def test_field_set_requires_both_coders_to_establish_a_completed_study(self):
        completed_field_work({'study_status': 'completed'}, {'study_status': 'completed'})

    def test_job_completion_cannot_substitute_for_empirical_study_completion(self):
        for status in ['planned', 'in_progress', 'unclear', None]:
            with self.subTest(status=status), self.assertRaisesRegex(AssertionError, 'record-level remedy'):
                completed_field_work({'status': 'done', 'study_status': status},
                                     {'status': 'done', 'study_status': 'completed'})

    def test_printed_or_retained_doi_still_requires_authoritative_title_verification(self):
        row = {'doi_o': '10.1/original', 'title_o': 'Actual paper'}
        with self.assertRaisesRegex(AssertionError, 'authoritative metadata'):
            original_identifier_alignment(row, None)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'metadata.json'
            path.write_text(json.dumps({'message': {'DOI': '10.1/original', 'title': ['Actual paper']}}))
            receipt = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            original_identifier_alignment(row, receipt)
            path.write_text(json.dumps({'message': {'DOI': '10.1/original', 'title': ['Different paper']}}))
            receipt['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(AssertionError, 'different title'):
                original_identifier_alignment(row, receipt)

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

    def test_abbreviated_author_list_requires_registered_metadata(self):
        row = {'title_o': 'Actual paper', 'year_o': '2015', 'doi_o': '10.1/original',
               'author_o': json.dumps([{'given': 'A', 'family': 'One'}, {'given': 'B', 'family': 'Two'},
                                       {'given': 'C', 'family': 'Three'}])}
        target = {'title': 'Actual paper', 'year': '2015', 'doi': '10.1/original', 'authors': 'One A, Two B'}
        with self.assertRaisesRegex(AssertionError, 'abbreviated'):
            original_alignment(row, target)

    def test_metadata_verifies_abbreviation_and_known_consortium_name_loss(self):
        authors = [{'name': 'Consortium', 'sequence': 'first'}, {'given': 'A', 'family': 'One'},
                   {'given': 'B', 'family': 'Two'}, {'given': 'C', 'family': 'Three'}]
        frozen = [{'sequence': 'first'}] + authors[1:]
        row = {'title_o': 'Actual paper', 'year_o': '2015', 'doi_o': '10.1/original',
               'author_o': json.dumps(frozen)}
        target = {'title': 'Actual paper', 'year': '2015', 'doi': '10.1/original', 'authors': 'One A, Two B'}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'metadata.json'
            path.write_text(json.dumps({'message': {'DOI': '10.1/original', 'title': ['Actual paper'], 'author': authors}}))
            receipt = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                       'source_printed_authors': 'One A Two B', 'source_printed_person_count': 2}
            original_alignment(row, target, author_receipt=receipt)
            self.assertEqual(json.loads(row['author_o']), frozen)
            authors[0] = {'given': 'Missing', 'family': 'Person'}
            path.write_text(json.dumps({'message': {'DOI': '10.1/original', 'title': ['Actual paper'], 'author': authors}}))
            receipt['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(AssertionError, 'verified group'):
                original_alignment(row, target, author_receipt=receipt)

    def test_author_metadata_cannot_authorize_a_different_paper(self):
        row = {'title_o': 'Actual paper', 'year_o': '2015', 'doi_o': '10.1/original',
               'author_o': json.dumps([{'given': 'A', 'family': 'One'}, {'given': 'B', 'family': 'Two'}])}
        target = {'title': 'Actual paper', 'year': '2015', 'doi': '10.1/original', 'authors': 'One A'}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'metadata.json'
            path.write_text(json.dumps({'message': {'DOI': '10.1/different', 'title': ['Actual paper'], 'author': []}}))
            receipt = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            with self.assertRaisesRegex(AssertionError, 'metadata DOI differs'):
                original_alignment(row, target, author_receipt=receipt)

    def test_advance_year_requires_primary_publisher_evidence_for_later_issue(self):
        row = {'title_o': 'Actual paper', 'year_o': '2015', 'doi_o': '10.1/original',
               'volume_o': 'NA', 'issue_o': 'NA', 'pages_o': 'muu053',
               'author_o': json.dumps([{'family': 'Marvel'}])}
        target = {'title': 'Actual paper', 'year': '2016', 'doi': '10.1/original', 'authors': 'Marvel JD'}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = root / 'crossref.json'
            metadata.write_text(json.dumps({'message': {'DOI': '10.1/original', 'title': ['Actual paper'],
                'published-online': {'date-parts': [[2015, 1, 30]]}, 'page': 'muu053',
                'resource': {'primary': {'URL': 'https://publisher.example/article/10.1/original'}}}}))
            year = {'path': str(metadata), 'sha256': hashlib.sha256(metadata.read_bytes()).hexdigest()}
            with self.assertRaisesRegex(AssertionError, 'publisher issue evidence required'):
                original_alignment(row, target, year)
            source = root / 'publisher.txt'
            quote = 'Actual paper. Marvel JD. Volume 26, Issue 1, January 2016, Pages 143–158. 10.1/original'
            source.write_text(quote)
            printed = root / 'print.json'
            record = {'doi': '10.1/original', 'title': 'Actual paper', 'year': '2016',
                      'volume': '26', 'issue': '1', 'page': '143-158',
                      'source_url': 'https://publisher.example/issue/26/1', 'source_path': str(source),
                      'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'quote': quote}
            printed.write_text(json.dumps(record))
            year['publisher_print_metadata_receipt'] = {'path': str(printed), 'sha256': hashlib.sha256(printed.read_bytes()).hexdigest()}
            original_alignment(row, target, year)
            row['volume_o'] = '26'
            with self.assertRaisesRegex(AssertionError, 'advance-publication metadata differs'):
                original_alignment(row, target, year)
            row['volume_o'] = 'NA'
            record['source_url'] = 'https://unrelated.example/issue/26/1'
            printed.write_text(json.dumps(record))
            year['publisher_print_metadata_receipt']['sha256'] = hashlib.sha256(printed.read_bytes()).hexdigest()
            with self.assertRaisesRegex(AssertionError, 'registered publisher'):
                original_alignment(row, target, year)

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
