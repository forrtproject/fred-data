#!/usr/bin/env python3
"""Planted failures: a sound-looking review must not pass without literal evidence and a complete read."""
import unittest

import validate_adversarial_reviews as V

SOURCE = 'the replication failed overall in the sample and the authors say the original effect did not hold'
REQUEST = dict(request_id='r1', document_id='d1', input_row_index=5, source_chunks=2, recorded_flag='scope question',
               proposed_changes=[dict(field='outcome', proposed_value='failed')])
RECEIPTS = [dict(chunk=0), dict(chunk=1)]


def good():
    return dict(request_id='r1', document_id='d1', input_row_index=5, verdict='supported', confidence='high', same_finding=True,
                fields=[dict(field='outcome', supported_value='failed')], flag_answer='The scope matches the original claim.',
                supporting_quotes=[dict(quote='the replication failed overall', section='Discussion')],
                strongest_counterevidence=dict(quote='in the sample', section='Results', why_not_decisive='Narrow'),
                replacement_quote='the authors say the original effect did not hold', replacement_quote_section='discussion', policy_group=None)


class Planted(unittest.TestCase):
    def fails(self, expected, **change):
        review = dict(good(), **change)
        self.assertIn(expected, V.validate(review, REQUEST, SOURCE, RECEIPTS))

    def test_clean_review_passes(self):
        self.assertEqual(V.validate(good(), REQUEST, SOURCE, RECEIPTS), [])

    def test_fabricated_quotes_fail(self):
        self.fails('supporting_quote_not_literal', supporting_quotes=[dict(quote='made up sentence', section='x')])
        self.fails('counterevidence_not_literal', strongest_counterevidence=dict(quote='invented counterpoint'))
        self.fails('replacement_quote', replacement_quote='no such passage')
        self.fails('supporting_quote_not_literal', supporting_quotes=[])

    def test_joined_or_long_replacements_fail(self):
        self.fails('replacement_quote', replacement_quote='the replication failed || did not hold')
        long_source = 'x ' * 2000
        review = dict(good(), replacement_quote=long_source.strip())
        self.assertIn('replacement_quote', V.validate(review, REQUEST, long_source, RECEIPTS))

    def test_skipped_chunk_fails(self):
        self.assertIn('incomplete_read', V.validate(good(), REQUEST, SOURCE, [dict(chunk=0)]))
        self.assertIn('incomplete_read', V.validate(dict(good(), verdict='not_supported'), REQUEST, SOURCE, []))

    def test_wrong_identity_fails(self):
        self.fails('identity', input_row_index=6)
        self.fails('identity', document_id='d2')
        self.fails('request_id', request_id='r2')

    def test_field_mismatch_fails(self):
        self.fails('field_value_differs:outcome', fields=[dict(field='outcome', supported_value='mixed')])
        self.fails('fields_not_addressed', fields=[])

    def test_same_finding_and_flag_are_required(self):
        self.fails('same_finding', same_finding=False)
        self.fails('flag_not_answered', flag_answer='')

    def test_unknown_verdict_and_group_fail(self):
        self.assertEqual(V.validate(dict(good(), verdict='approved'), REQUEST, SOURCE, RECEIPTS), ['verdict'])
        self.fails('policy_group', policy_group='invented_rule')

    def test_medium_confidence_is_sound_but_not_high(self):
        self.assertEqual(V.validate(dict(good(), confidence='medium'), REQUEST, SOURCE, RECEIPTS), [])


class QualityCheck(unittest.TestCase):
    def test_qa_status(self):
        self.assertEqual(V.classify_qa(good(), []), 'agreed')
        self.assertEqual(V.classify_qa(dict(good(), confidence='medium'), []), 'softened')
        self.assertEqual(V.classify_qa(dict(good(), verdict='not_supported'), []), 'flip')
        self.assertEqual(V.classify_qa(dict(good(), verdict='policy_boundary'), []), 'flip')
        self.assertEqual(V.classify_qa(good(), ['incomplete_read']), 'unusable')


if __name__ == '__main__':
    unittest.main()
