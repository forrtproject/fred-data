"""Planted answers for the final-read rule: only a clear, high-confidence 'contradicted' may change a value."""
import unittest

import validate_final_read as V


def answer(**changes):
    return {**dict(field='outcome', better='B', other_value='contradicted', confidence='high'), **changes}


class FinalDecisions(unittest.TestCase):
    def test_every_read_field_is_decided_and_no_record_waits(self):
        import sys
        sys.path.insert(0, str(V.L.B / 'scripts'))
        import build_ledger_review as R
        decisions = V.L.read(V.L.T / 'final_read_decisions.json')['reviews']
        self.assertEqual(sum(r['verdict'] == 'correct' for r in decisions.values()), 17)
        built = R.build()
        self.assertEqual(built['pending_read'], [])
        for row in (292, 726, 1729, 195):
            self.assertNotIn(built['bundles'][f'row:{row}']['view'], ('ready', 'pending_read'))

    def test_quotes_on_the_list_are_clean(self):
        data = V.L.read(V.L.B / 'handoff/corrections_to_apply.json')
        bad = __import__('re').compile('[\ufb00-\ufb04\ue01e\u2afd\u2429\u00ad]|Hum Genet \\(2014\\)|Ethnicity-education .14')
        for correction in data['corrections']:
            for key, value in correction['set']['new'].items():
                if 'quote' in key:
                    self.assertFalse(bad.search(value), (correction['flora_id'], key))
                    self.assertLessEqual(len(value), 1500)


class FieldRule(unittest.TestCase):
    def test_clear_answer_is_a_correction(self):
        self.assertEqual(V.field_verdict(answer(), 'B', True, True), 'correct')

    def test_everything_short_of_clear_keeps_the_value(self):
        for changes, letter, same, quote in (
                (dict(other_value='defensible'), 'B', True, True),
                (dict(confidence='medium'), 'B', True, True),
                (dict(confidence='low'), 'B', True, True),
                (dict(better='A'), 'B', True, True),
                (dict(better='cannot_tell', other_value='not_applicable'), 'B', True, True),
                (dict(), 'A', True, True),
                (dict(), 'B', False, True),
                (dict(), 'B', True, False)):
            self.assertEqual(V.field_verdict(answer(**changes), letter, same, quote), 'keep_existing', (changes, letter, same, quote))

    def test_third_value_needs_high_confidence(self):
        self.assertEqual(V.field_verdict(answer(better='neither', other_value='not_applicable'), 'B', True, True), 'other_value')
        self.assertEqual(V.field_verdict(answer(better='neither', other_value='not_applicable', confidence='medium'), 'B', True, True), 'keep_existing')


class RecordRule(unittest.TestCase):
    def test_type_and_results_apply_together(self):
        verdicts = V.record_verdicts(['type', 'outcome'], dict(type='keep_existing', outcome='correct'))
        self.assertEqual(verdicts, dict(type='keep_existing', outcome='keep_existing'))

    def test_outcome_depends_on_the_original(self):
        verdicts = V.record_verdicts(['original', 'outcome'], dict(original='keep_existing', outcome='correct'))
        self.assertEqual(verdicts['outcome'], 'keep_existing')

    def test_correct_lead_field_leaves_others_alone(self):
        verdicts = dict(original='correct', outcome='keep_existing')
        self.assertEqual(V.record_verdicts(['original', 'outcome'], verdicts), verdicts)


class Mechanics(unittest.TestCase):
    request = dict(request_id='f1', input_row_index=5, source_chunks=2, fields=[dict(field='outcome')])
    source = 'alpha beta gamma delta'

    def review(self, **changes):
        return {**dict(request_id='f1', input_row_index=5, fields=[answer()], supporting_quotes=[dict(quote='beta gamma')], replacement_quote='alpha beta'), **changes}

    def test_clean_review_passes(self):
        self.assertEqual(V.mechanical_problems(self.request, self.review(), [dict(chunk=0), dict(chunk=1)], self.source), [])

    def test_missing_chunk_fails(self):
        self.assertIn('missing_chunk_receipts', V.mechanical_problems(self.request, self.review(), [dict(chunk=0)], self.source))

    def test_invented_quotes_fail(self):
        receipts = [dict(chunk=0), dict(chunk=1)]
        self.assertIn('replacement_quote_not_literal', V.mechanical_problems(self.request, self.review(replacement_quote='invented text'), receipts, self.source))
        self.assertIn('supporting_quote_not_literal', V.mechanical_problems(self.request, self.review(supporting_quotes=[dict(quote='invented')]), receipts, self.source))

    def test_medium_confidence_is_not_a_mechanical_failure(self):
        receipts = [dict(chunk=0), dict(chunk=1)]
        self.assertEqual(V.mechanical_problems(self.request, self.review(fields=[answer(confidence='medium')]), receipts, self.source), [])


if __name__ == '__main__':
    unittest.main()
