"""Regression tests for the FReD application policies (D1-D3, T2) agreed on 7 November 2026."""
import collections
import pytest
import policy_ledger as pl


@pytest.fixture(scope='module')
def ledger():
    return {(r['audit_id'], r['field']): r for r in pl.build_ledger()}


def test_direction_is_signed_only_for_directional_metrics():
    assert pl.direction('t(30) = -2.87', 'test statistic') == -1
    assert pl.direction('t(69) = –0.34', 'test statistic') == -1
    assert pl.direction('F(1, 41) = 7.81', 'test statistic') is None
    assert pl.direction('0.21', 'r') == 1
    assert pl.direction('0.8', 'OR') == -1
    assert pl.direction('0.30', 'etasq (partial)') is None


def test_study_key_matches_pipeline_join():
    row = {'doi_o': ' 10.1/ABC ', 'doi_r': '10.2/X Y', 'url_r': None, 'study_o': '1', 'study_r': None}
    assert pl.study_key(row) == ('10.1/abc', '10.2/xy', '1', '')
    assert pl.study_key({**row, 'url_r': 'https://osf.io/x'})[1] == 'https://osf.io/x'


def test_subsample_gap_ignores_repeated_measures():
    assert pl.subsample_gap(64, 122)        # t(58) with N = 122
    assert not pl.subsample_gap(1, 27)      # F(1, 26) with N = 27
    assert not pl.subsample_gap(-61, 32)    # within-subject df above N


def test_every_finding_has_one_valid_decision(ledger):
    assert len(ledger) == 694
    assert all(r['final_decision'] in pl.DECISIONS for r in ledger.values())
    assert sum(bool(r['sample_check']) for r in ledger.values()) == pl.SAMPLE_SIZE


def test_d1_sign_relative_to_original(ledger):
    assert ledger[(1533, 'es_value_r')]['final_decision'] == 'reject'
    assert ledger[(1533, 'es_value_r')]['policy'] == 'D1-direction'
    for key in [(753, 'es_value_r'), (1278, 'es_value_r')]:
        assert ledger[key]['policy'] == 'D1-direction'
    assert ledger[(29, 'es_value_o')]['policy'] == 'D1-direction'
    # Replication partial eta squared carries no sign, so 1552 is a plain transcription fix.
    assert ledger[(1552, 'es_value_o')]['final_decision'] == 'apply'


def test_d2_reported_success_is_study_level_and_never_automatic(ledger):
    rs = [r for r in ledger.values() if r['field'] == 'reported_success']
    assert {r['auto_decision'] for r in rs} <= {'review', 'not_applicable'}
    assert ledger[(68, 'reported_success')]['final_decision'] == 'not_applicable'
    assert ledger[(71, 'reported_success')]['final_decision'] == 'not_applicable'
    assert ledger[(349, 'reported_success')]['final_decision'] == 'review'


def test_d3_partial_side_switches_are_held(ledger):
    for key in [(57, 'es_value_r'), (58, 'es_value_r'), (57, 'pval_value_r'), (471, 'pval_value_r'),
                (585, 'pval_value_r'), (1019, 'es_value_o'), (1709, 'es_value_o'), (1710, 'es_value_o')]:
        assert ledger[key]['final_decision'] == 'hold', key


def test_d3_same_test_fixes_still_apply(ledger):
    assert ledger[(434, 'n_o')]['final_decision'] == 'apply'          # 577 -> 578, same regression
    assert ledger[(706, 'n_o')]['final_decision'] == 'apply'           # 51 -> 50 after one exclusion
    # Omitted p = .003 matches chi-square(4) but the unverified shipped statistic is chi-square(8).
    assert ledger[(233, 'pval_value_o')]['final_decision'] == 'hold'


def test_t2_changes_need_individual_review(ledger):
    assert ledger[(337, 'es_value_o')]['policy'] == 'T2-model-change'
    assert ledger[(100, 'n_r')]['final_decision'] in {'review', 'hold'}
    counts = collections.Counter(r['policy'] for r in ledger.values() if r['final_decision'] == 'apply')
    assert set(counts) <= {'T1'} | {r['policy'] for r in ledger.values() if r['manual_decision'] == 'apply'}
