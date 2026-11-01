"""Reject incompatible fixes even when individual model outputs are valid."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from build_verified_proposals import BASELINE_SHA, checked_replacements, completed_field_work, current_alignment, digest, ids, metadata_title, original_alignment, original_doi_alignment, original_identifier_alignment, original_replacements, record_removal, retained_target_scope_review, review_field_dispositions, review_row_binding


class ProposalDependencies(unittest.TestCase):
    def setUp(self):
        self.row = {'type': 'replication', 'outcome': 'failed'}
        self.result = {'record_type': 'reproduction'}
        self.target = {'outcome': '', 'outcome_computation': 'computational issues',
                       'outcome_robustness': 'robustness challenges'}

    def sici_fixture(self, directory):
        canonical = '10.1002/(sici)1520-6653(199924)13:1<5::aid-dir2>3.0.co;2-9'
        literal = canonical.replace('1520-6653', '15206653')
        row = {'doi_o': canonical, 'doi_r': '10.1/current'}
        path = Path(directory) / 'publisher.json'
        path.write_text(json.dumps({'message': {'DOI': row['doi_r'], 'reference': [
            {'key': 'bibr37', 'doi-asserted-by': 'publisher', 'DOI': canonical}]}}))
        receipt = {'canonical_doi': canonical, 'literal_extracted_doi': literal,
                   'publisher_reference_key': 'bibr37', 'publisher_reference_metadata': {
                       'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}}
        return row, {'doi': literal}, receipt

    def test_publisher_verified_sici_transcription_preserves_canonical_identifier(self):
        with tempfile.TemporaryDirectory() as directory:
            row, target, receipt = self.sici_fixture(directory)
            before = dict(row)
            original_doi_alignment(row, target, receipt)
            self.assertEqual(row, before)
            with self.assertRaisesRegex(AssertionError, 'verified transcription evidence'):
                original_doi_alignment(row, target)

    def test_sici_transcription_cannot_remove_an_article_identifier_hyphen(self):
        with tempfile.TemporaryDirectory() as directory:
            row, target, receipt = self.sici_fixture(directory)
            target['doi'] = target['doi'].replace('aid-dir2', 'aiddir2')
            receipt['literal_extracted_doi'] = target['doi']
            with self.assertRaisesRegex(AssertionError, 'Only the SICI ISSN'):
                original_doi_alignment(row, target, receipt)

    def test_sici_transcription_requires_the_actual_current_publisher_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            row, target, receipt = self.sici_fixture(directory)
            receipt['publisher_reference_key'] = 'missing'
            with self.assertRaisesRegex(AssertionError, 'canonical reference not established'):
                original_doi_alignment(row, target, receipt)
            receipt['publisher_reference_key'] = 'bibr37'
            row['doi_r'] = '10.1/different-current-work'
            with self.assertRaisesRegex(AssertionError, 'different current work'):
                original_doi_alignment(row, target, receipt)

    def test_source_review_native_field_dictionary_preserves_explicit_identity(self):
        review = {'field_reviews': {'104.original': {
            'input_row_index': 104, 'field_review_id': '104.original',
            'requested_fields': ['original'], 'status': 'supported_correction'}}}
        self.assertEqual(review_field_dispositions(review), [(104, 'original', 'supported_correction')])

    def replacement_review(self):
        return dict(input_row_index=699, field='outcome', current_value='successful',
                    proposed_value='mixed', adjudicated_value='mixed', recommended_value='mixed',
                    value='mixed', status='propose_change_to_mixed',
                    disposition='replace_current_with_proposed', outcome_confident=True,
                    policy_boundary_needed=False)

    def test_deposited_subtitle_is_preserved_without_duplication(self):
        self.assertEqual(metadata_title({'title': ['Main title'], 'subtitle': ['A question?']}),
                         'Main title: A question?')
        self.assertEqual(metadata_title({'title': ['Main title: A question?'], 'subtitle': ['A question?']}),
                         'Main title: A question?')

    def test_ambiguous_deposited_subtitles_are_rejected(self):
        with self.assertRaises(AssertionError):
            metadata_title({'title': ['Main'], 'subtitle': ['One', 'Two']})

    def test_case_table_preserves_explicit_field_identity(self):
        review = {'cases': {'2.original': {'case_id': '2.original', 'input_row_index': 2,
                  'field': 'original', 'status': 'supported_correction'}}}
        self.assertEqual(review_field_dispositions(review), [(2, 'original', 'supported_correction')])
        review['cases']['2.original']['case_id'] = '3.original'
        with self.assertRaisesRegex(AssertionError, 'Conflicting review row'):
            review_field_dispositions(review)

    def test_partial_review_baseline_cannot_name_a_different_current_work(self):
        rows = [{'doi_r': '10.1/current', 'outcome': 'failed'}]
        review = {'cases': [{'input_row_index': 0, 'field': 'outcome',
                            'frozen_csv_baseline': {'doi_r': '10.1/unrelated', 'value': 'failed'}}]}
        with self.assertRaisesRegex(AssertionError, 'baseline identifier'):
            review_row_binding(review, 0, rows)

    def row_binding_fixture(self, directory):
        rows = [{'doi_o': 'old', 'doi_r': 'unrelated'}, {'doi_o': 'target', 'doi_r': 'current'}]
        snapshot = {'\ufeff"doi_o"': 'old', 'doi_r': 'unrelated'}
        review = {'cases': {'1.original': {'case_id': '1.original', 'input_row_index': 1,
                  'field': 'original', 'status': 'supported_correction', 'frozen_row_state': snapshot}}}
        correction = {'review_file_sha256': 'review-hash', 'baseline_sha256': BASELINE_SHA,
            'case_bindings': {'1.original': {'input_row_index': 1,
                'correct_frozen_full_record_sha256': digest(rows[1]),
                'review_snapshot_sha256': digest(snapshot), 'incorrect_snapshot_row_index': 0,
                'correction_kind': 'one_based_index_used_for_zero_based_row'}}}
        path = Path(directory) / 'correction.json'
        path.write_text(json.dumps(correction))
        receipt = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        return rows, review, receipt

    def test_wrong_row_snapshot_requires_exact_parent_correction(self):
        with tempfile.TemporaryDirectory() as directory:
            rows, review, receipt = self.row_binding_fixture(directory)
            with self.assertRaisesRegex(AssertionError, 'another frozen row'):
                review_row_binding(review, 1, rows)
            review_row_binding(review, 1, rows, receipt, 'review-hash')

    def test_row_correction_cannot_authorize_another_review_or_record(self):
        with tempfile.TemporaryDirectory() as directory:
            rows, review, receipt = self.row_binding_fixture(directory)
            with self.assertRaisesRegex(AssertionError, 'another review'):
                review_row_binding(review, 1, rows, receipt, 'different-review')
            rows[1]['doi_r'] = 'different-current'
            with self.assertRaises(AssertionError):
                review_row_binding(review, 1, rows, receipt, 'review-hash')

    def record_removal_fixture(self):
        result = dict(study_status='completed', record_type='not_a_replication', targets=[])
        decision = dict(positive_record_scope_parent_verified=True, action='exclude_nonreplication_record',
                        isolated_field_application_allowed=False, rationale='Within-paper repetition only', limits=[])
        return result, decision

    def test_record_exclusion_archives_the_complete_pair_without_field_patches(self):
        result, decision = self.record_removal_fixture()
        action = record_removal(self.row, 1, result, result, decision, ['proof1', 'proof2'])
        self.assertEqual(action['operations'][0]['operation'], 'remove_row')
        self.assertEqual(action['operations'][0]['archive_before'], self.row)
        self.assertEqual(action['expected_before_full_record_sha256'], digest(self.row))
        self.assertFalse(action['outcome_applicable'])
        self.assertFalse(action['user_approval_recorded'])

    def test_zero_targets_alone_cannot_authorize_record_exclusion(self):
        result, decision = self.record_removal_fixture()
        decision['positive_record_scope_parent_verified'] = False
        with self.assertRaisesRegex(AssertionError, 'Omitted targets alone'):
            record_removal(self.row, 1, result, result, decision, ['proof1', 'proof2'])

    def test_record_exclusion_rejects_isolated_type_application(self):
        result, decision = self.record_removal_fixture()
        decision['isolated_field_application_allowed'] = True
        with self.assertRaisesRegex(AssertionError, 'Whole-record remedy'):
            record_removal(self.row, 1, result, result, decision, ['proof1', 'proof2'])

    def test_explicit_replacement_disposition_preserves_field_identity(self):
        self.assertEqual(review_field_dispositions(self.replacement_review()),
                         [(699, 'outcome', 'supported_correction')])

    def test_replacement_disposition_rejects_conflicting_values(self):
        review = self.replacement_review()
        review['adjudicated_value'] = 'successful'
        with self.assertRaisesRegex(AssertionError, 'Conflicting replacement values'):
            review_field_dispositions(review)

    def test_replacement_disposition_rejects_uncertain_policy(self):
        review = self.replacement_review()
        review['policy_boundary_needed'] = True
        with self.assertRaisesRegex(AssertionError, 'uncertain'):
            review_field_dispositions(review)

    def test_replacement_disposition_rejects_wrong_status(self):
        review = self.replacement_review()
        review['status'] = 'retain_current'
        with self.assertRaisesRegex(AssertionError, 'Conflicting replacement status'):
            review_field_dispositions(review)

    def test_source_review_rejects_conflicting_row_aliases(self):
        review = {'reviews': [{'row_index': 104, 'row_id': 'row:105', 'field': 'original',
                               'status': 'supported_correction'}]}
        with self.assertRaisesRegex(AssertionError, 'Conflicting review row'):
            review_field_dispositions(review)

    def test_source_review_rejects_conflicting_field_aliases(self):
        review = {'field_reviews': {'104.original': {'input_row_index': 104,
            'field_review_id': '104.original', 'field': 'outcome', 'status': 'supported_correction'}}}
        with self.assertRaisesRegex(AssertionError, 'Conflicting review field'):
            review_field_dispositions(review)

    def one_author_abbreviation_fixture(self, directory, printed='Smith SM, et al.'):
        authors = [{'family': 'Smith', 'given': 'Stephen M.'}, {'family': 'Jones', 'given': 'Ann'}]
        row = {'title_o': 'Actual target', 'year_o': '2009', 'doi_o': '10.1/original',
               'author_o': json.dumps(authors)}
        target = {'title': 'Actual target', 'year': '2009', 'doi': '10.1/original', 'authors': printed}
        path = Path(directory) / 'authors.json'
        path.write_text(json.dumps({'message': {'DOI': '10.1/original', 'title': ['Actual target'], 'author': authors}}))
        receipt = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                   'source_printed_authors': printed, 'source_printed_person_count': 1}
        return row, target, receipt

    def test_single_named_author_et_al_requires_matching_source_doi_and_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            row, target, receipt = self.one_author_abbreviation_fixture(directory)
            original_alignment(row, target, author_receipt=receipt)

    def test_single_author_abbreviation_cannot_bypass_missing_source_identifier(self):
        with tempfile.TemporaryDirectory() as directory:
            row, target, receipt = self.one_author_abbreviation_fixture(directory)
            target['doi'] = ''
            with self.assertRaisesRegex(AssertionError, 'printed matching DOI'):
                original_alignment(row, target, author_receipt=receipt)

    def test_single_author_abbreviation_requires_matching_first_author_initials(self):
        with tempfile.TemporaryDirectory() as directory:
            row, target, receipt = self.one_author_abbreviation_fixture(directory, 'Smith SJ, et al.')
            with self.assertRaisesRegex(AssertionError, 'first-author initials differ'):
                original_alignment(row, target, author_receipt=receipt)

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
