#!/usr/bin/env python3
"""Planted-failure and accounting tests for the field ledger."""
import copy
import json
import unittest
from collections import Counter
from pathlib import Path

import build_field_ledger as L

T = Path(__file__).resolve().parent


def good():
    """A field passing every gate up to the adversarial read."""
    coder = dict(present=True, eligible_for_comparison=True, evidence_level='full_text', study_status='completed',
                 binding_count=1, relation='proposed', confident=True, literal_quote_ok=True, validator_clean=True,
                 value='mixed', qualification=None)
    return dict(field='outcome', proposed_value='mixed', standing_reasons=[], document_id='document_9999',
                provider_held=False, source_order_held=False, header_only=False, withdrawn=False, formal_hold=False,
                reliability_hold=False, in_record_actions=False, in_export=False, remove_row=False, record_dependency=False,
                application_hold=False, full_text_gap=False, relink_duplicate=False, type_has_axis_partner=False,
                opus=copy.deepcopy(coder), sol=copy.deepcopy(coder), coders_agree_exactly=True,
                proposed_is_cannot_be_determined=False, adversary=None)


def with_(**changes):
    facts = good()
    for path, value in changes.items():
        if '__' in path:
            role, key = path.split('__')
            facts[role][key] = value
        else:
            facts[path] = value
    return L.classify_field(facts)


class PlantedFailures(unittest.TestCase):
    def assert_state(self, expected, **changes):
        state, reasons = with_(**changes)
        self.assertEqual(state, expected, changes)
        self.assertNotIn(state, L.READY_STATES)
        return reasons

    def test_clean_field_still_needs_the_adversary(self):
        self.assertEqual(with_()[0], 'agreement_pending_adversarial_review')

    def test_supported_review_with_verified_quote_is_the_only_new_ready_route(self):
        review = dict(verdict='supported', quote_verified=True, authoritative_metadata_verified=False, confidence='high')
        self.assertEqual(with_(adversary=review)[0], 'adversary_supported_candidate')
        self.assertIn('adversary_below_high_confidence', self.assert_state('adversary_held', adversary=dict(review, confidence='medium')))
        self.assert_state('adversary_held', adversary=dict(review, verdict='policy_boundary'))
        self.assert_state('adversary_held', adversary=dict(review, verdict='not_supported'))
        self.assert_state('adversary_held', adversary=dict(review, quote_verified=False))

    def test_original_relink_needs_authoritative_metadata_after_review(self):
        review = dict(verdict='supported', quote_verified=True, authoritative_metadata_verified=False, confidence='high')
        self.assert_state('agreement_needs_authoritative_metadata', field='original', adversary=review)
        ok = dict(review, authoritative_metadata_verified=True)
        self.assertEqual(with_(field='original', adversary=ok)[0], 'adversary_supported_candidate')

    def test_unconfident_role_blocks(self):
        self.assert_state('unconfident', opus__confident=False)
        self.assert_state('unconfident', sol__confident=False)

    def test_model_disagreement_blocks(self):
        self.assert_state('disagreement_confident', sol__relation='frozen', sol__value='failed', coders_agree_exactly=False)

    def test_confident_third_value_is_not_a_proposal_match(self):
        self.assert_state('third_value_agreement', opus__relation='other', sol__relation='other')

    def test_two_different_other_values_are_disagreement(self):
        self.assert_state('disagreement_confident', opus__relation='other', sol__relation='other', coders_agree_exactly=False)

    def test_both_confident_on_frozen_withdraws(self):
        self.assert_state('withdraw_both_roles_confirm_frozen', opus__relation='frozen', sol__relation='frozen')

    def test_frozen_agreement_with_low_confidence_does_not_withdraw(self):
        self.assert_state('unconfident', opus__relation='frozen', sol__relation='frozen', opus__confident=False)

    def test_abstract_evidence_blocks_even_when_confident(self):
        self.assert_state('source_gap', sol__evidence_level='abstract')
        self.assert_state('source_gap', opus__evidence_level='abstract')
        self.assert_state('source_gap', full_text_gap=True)

    def test_multibound_or_unbound_target_blocks(self):
        self.assert_state('target_not_bound', opus__binding_count=2)
        self.assert_state('target_not_bound', sol__binding_count=0)

    def test_no_comparator_blocks(self):
        self.assert_state('no_eligible_comparator', sol__present=False)
        self.assert_state('no_eligible_comparator', opus__present=False)
        self.assert_state('no_eligible_comparator', sol__eligible_for_comparison=False)

    def test_qualified_comparators_do_not_turn_green(self):
        for qualification, code in (('alternate_layout', 'comparator_alternate_layout'),
                                    ('normalization_chain', 'comparator_normalization_chain')):
            reasons = self.assert_state('agreement_qualified_comparator', sol__qualification=qualification,
                                        adversary=dict(verdict='supported', quote_verified=True, authoritative_metadata_verified=True))
            self.assertIn(code, reasons)

    def test_failed_literal_recheck_blocks(self):
        reasons = self.assert_state('no_eligible_comparator', sol__literal_quote_ok=False)
        self.assertIn('literal_recheck_failed', reasons)
        reasons = self.assert_state('no_eligible_comparator', opus__validator_clean=False)
        self.assertIn('validator_unproved_evidence', reasons)

    def test_cannot_be_determined_is_never_automatic(self):
        self.assert_state('policy_cannot_be_determined', proposed_is_cannot_be_determined=True,
                          adversary=dict(verdict='supported', quote_verified=True, authoritative_metadata_verified=True))

    def test_holds_and_record_rules_beat_agreement(self):
        review = dict(verdict='supported', quote_verified=True, authoritative_metadata_verified=True)
        self.assert_state('provider_hold', provider_held=True, adversary=review)
        self.assert_state('source_order_hold', source_order_held=True, adversary=review)
        self.assert_state('header_only_hold', header_only=True, adversary=review)
        self.assert_state('withdrawn_source_adjudicated', withdrawn=True, in_export=False)
        self.assert_state('individual_policy_hold', formal_hold=True, adversary=review)
        self.assert_state('record_level_rule', remove_row=True, adversary=review)
        self.assert_state('record_level_rule', record_dependency=True, adversary=review)
        self.assert_state('record_level_rule', application_hold=True, adversary=review)
        self.assert_state('record_level_rule', relink_duplicate=True, adversary=review)
        self.assert_state('record_level_rule', opus__study_status='prospective')
        self.assert_state('binding_unresolved_document', document_id=None)

    def test_type_changes_have_their_own_rules(self):
        self.assert_state('record_level_rule', field='type', proposed_value='not_a_replication')
        self.assert_state('record_level_rule', field='type', proposed_value='reproduction', type_has_axis_partner=False)

    def test_held_beats_export_membership(self):
        self.assert_state('individual_policy_hold', formal_hold=True, in_export=True)
        self.assert_state('provider_hold', provider_held=True, in_export=True)


class Binding(unittest.TestCase):
    identity = dict(ids={'10.1/abc'}, title='A study of many things', year='2010', author='Smith, J.')

    def test_identifier_or_corroborated_title_binds(self):
        self.assertEqual(L.target_binding(dict(doi='https://doi.org/10.1/ABC', title='x'), self.identity), 'identifier')
        self.assertEqual(L.target_binding(dict(doi='', title='A study of many things!'), self.identity), 'title_exact')

    def test_short_or_uncorroborated_titles_do_not_bind(self):
        self.assertIsNone(L.target_binding(dict(doi='', title='A study of many things and places', year='1999', authors='Jones'), self.identity))
        self.assertIsNone(L.target_binding(dict(doi='', title='', year='2010', authors='Smith'), self.identity))

    def test_other_doi_does_not_bind_by_position(self):
        self.assertIsNone(L.target_binding(dict(doi='10.1/other', title='Something else entirely', year='2010', authors='Smith'), self.identity))

    def test_frozen_axes_parse(self):
        self.assertEqual(L.parse_axes('computational issues, robustness not checked'),
                         dict(outcome_computation='computational issues', outcome_robustness='not checked'))
        self.assertEqual(L.parse_axes('not checked, robustness challenges'),
                         dict(outcome_computation='not checked', outcome_robustness='robustness challenges'))
        self.assertEqual(L.parse_axes('computation not checked, robust'),
                         dict(outcome_computation='not checked', outcome_robustness='robust'))

    def test_current_relation_is_exact(self):
        row = dict(type='replication', outcome='mixed', doi_o='', title_o='', year_o='', author_o='')
        self.assertEqual(L.current_relation('outcome', 'mixed', 'failed', row), 'already_equal')
        self.assertEqual(L.current_relation('outcome', 'mixed', 'mixed', dict(row, outcome='failed')), 'third_value')
        self.assertEqual(L.current_relation('outcome', 'successful', 'mixed', row), 'unchanged_from_frozen')

    def test_identity_is_not_row_position(self):
        frozen = dict(doi_o='10.1/a', alt_identifier_o='NA', doi_r='10.1/b', alt_identifier_r='NA', title_o='Original study title here',
                      title_r='Replication study title here', year_r='2020', url_r='NA')
        moved = dict(frozen)
        other = dict(frozen, doi_o='10.1/x', doi_r='10.1/y', title_o='Different original', title_r='Different replication')
        fi = L.build_identity_index([frozen])
        ci = L.build_identity_index([other, moved])
        self.assertEqual(L.bind_current(frozen, fi, ci, [other, moved])[0], 1)

    def test_conflicting_titles_stay_unbound(self):
        frozen = dict(doi_o='10.1/a', alt_identifier_o='NA', doi_r='10.1/b', alt_identifier_r='NA', title_o='Original study title here',
                      title_r='Replication study title here', year_r='2020', url_r='NA')
        changed = dict(frozen, title_o='Nothing like the first one at all', title_r='Also entirely unrelated wording')
        fi, ci = L.build_identity_index([frozen]), L.build_identity_index([changed])
        self.assertEqual(L.bind_current(frozen, fi, ci, [changed])[:2], (None, 'identifiers_match_titles_conflict'))

    def test_ambiguous_pairs_stay_unbound(self):
        frozen = dict(doi_o='10.1/a', alt_identifier_o='NA', doi_r='10.1/b', alt_identifier_r='NA', title_o='Original study title here',
                      title_r='Replication study title here', year_r='2020', url_r='NA')
        fi, ci = L.build_identity_index([frozen]), L.build_identity_index([frozen, dict(frozen)])
        self.assertEqual(L.bind_current(frozen, fi, ci, [frozen, dict(frozen)])[:2], (None, 'ambiguous_identifier_pair'))

    def test_literal_check_needs_every_part(self):
        source = L.spaced('the effect did not\nreplicate at all in the sample')
        self.assertTrue(L.literal_in_source('the effect did not replicate', source))
        self.assertTrue(L.literal_in_source('the effect did || in the sample', source))
        self.assertFalse(L.literal_in_source('the effect did || made up clause', source))
        self.assertFalse(L.literal_in_source('', source))


class RealLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = L.build_ledger()
        cls.fields = cls.ledger['fields']

    def by(self, row, field):
        return next(f for f in self.fields if f['input_row_index'] == row and f['field'] == field)

    def test_totals_are_asserted(self):
        totals = self.ledger['totals']
        self.assertEqual((totals['fields'], totals['rows'], totals['works']), (562, 515, 469))
        self.assertEqual(sum(totals['state_counts'].values()), 562)
        self.assertEqual(sum(totals['current_relations'].values()), 562)
        self.assertEqual(len({f['field_id'] for f in self.fields}), 562)

    def test_baseline_and_current_are_bound(self):
        self.assertEqual(self.ledger['baseline']['sha256'], L.BASELINE_SHA)
        self.assertEqual((self.ledger['baseline']['rows'], self.ledger['baseline']['columns']), (2818, 35))
        self.assertEqual((self.ledger['current']['rows'], self.ledger['current']['columns']), (2850, 51))

    def test_export_rederives(self):
        export = self.ledger['export_reconciliation']
        self.assertEqual((export['cases'], export['fields'], export['operations']), (39, 42, 194))
        self.assertEqual(export['families'], dict(original_reference=8, outcome_only=26, reproduction_axis=3, type_and_outcome=2))
        self.assertEqual(export['record_actions'], [107, 169, 267])
        self.assertEqual(export['gate_differences'], [])
        self.assertFalse(export['user_approval_recorded'])
        self.assertFalse(export['canonical_changes_applied'])

    def test_withdrawn_cases_are_withdrawn(self):
        self.assertEqual(self.by(802, 'outcome')['state'], 'withdrawn_source_adjudicated')
        self.assertEqual(self.by(1868, 'outcome')['state'], 'withdrawn_source_adjudicated')
        self.assertEqual(self.by(2320, 'original')['state'], 'withdrawn_source_adjudicated')

    def test_protected_sources_stay_held(self):
        held = {f['document_id'] for f in self.fields if f['state'] == 'provider_hold'}
        self.assertLessEqual(held, L.PROVIDER_HELD)
        for field in self.fields:
            if field['document_id'] in L.PROVIDER_HELD:
                self.assertEqual(field['state'], 'provider_hold')
                self.assertFalse(field['opus']['literal_quote_ok'])
            if field['document_id'] in L.SOURCE_ORDER_HELD:
                self.assertEqual(field['state'], 'source_order_hold')
            if field['document_id'] == 'document_0662':
                self.assertEqual(field['state'], 'header_only_hold')

    def test_alternate_layout_never_ready(self):
        for field in self.fields:
            if field['document_id'] in ('document_0022', 'document_0023'):
                self.assertFalse(field['ready'], field['field_id'])
                if field['sol']['present']:
                    self.assertEqual(field['sol']['qualification'], 'alternate_layout')

    def test_normalization_comparators_keep_qualification(self):
        for document in ('document_0190', 'document_0234', 'document_0240', 'document_0264', 'document_0336'):
            for field in self.fields:
                if field['document_id'] == document:
                    self.assertFalse(field['ready'])
                    self.assertEqual(field['sol']['qualification'], 'normalization_chain')

    def test_duplicate_views_are_one_pair(self):
        for field in self.fields:
            if field['document_id'] == 'document_0661':
                self.assertEqual(field['sol']['kind'], 'identical_body_one_pair')
        documents = Counter(f['document_id'] for f in self.fields if f['document_id'])
        self.assertLessEqual(set(documents), set(L.Artifacts().documents))

    def test_no_new_ready_without_review(self):
        for field in self.fields:
            if field['ready']:
                self.assertTrue(field['state'] == 'reviewed_export_candidate' or field['adversarial_review'], field['field_id'])

    def test_formal_holds_cover_their_rows(self):
        art = L.Artifacts()
        for case in art.held:
            if case['status'].startswith('resolved_') or case.get('input_row_index') is None:
                continue
            for field in self.fields:
                if field['input_row_index'] == case['input_row_index']:
                    self.assertFalse(field['ready'], field['field_id'])

    def test_bundles_are_atomic(self):
        for bundle in self.ledger['bundles']:
            members = [f for f in self.fields if f['input_row_index'] == bundle['input_row_index']]
            self.assertEqual(sorted(bundle['fields']), sorted(f['field'] for f in members))
            self.assertEqual(bundle['ready'], all(f['ready'] for f in members))

    def test_multi_report_fields_bind_positively(self):
        for field in self.fields:
            if field['document_binding'] == 'unique_report_naming_this_original':
                self.assertGreaterEqual(max(field['opus']['binding_count'] or 0, field['sol']['binding_count'] or 0), 1)
            if field['document_id'] is None:
                self.assertFalse(field['ready'])

    def test_outside_scope_is_counted(self):
        outside = self.ledger['outside_proposal_scope']
        self.assertEqual(outside['pairs']['confirmed_missing_pair']['items'], 440)
        self.assertEqual(outside['formal_individual_holds']['cases'], 43)
        self.assertEqual(outside['source_gaps'], 59)

    def test_ledger_has_no_source_quotations(self):
        text = json.dumps(self.ledger)
        self.assertNotIn('outcome_quote":', text)
        self.assertNotIn('evidence_quote":', text)


if __name__ == '__main__':
    unittest.main()
