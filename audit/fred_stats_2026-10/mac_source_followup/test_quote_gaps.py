import unittest
from repair_quote_gaps import proposed_quote


class QuoteGapSafeguards(unittest.TestCase):
    def test_interleaved_column_is_marked(self):
        result = proposed_quote('Target effect F(1,20)=3.4',
                                'Target effect unrelated column F(1,20)=3.4')
        self.assertEqual(result, 'Target effect … F(1,20)=3.4')

    def test_changed_number_cannot_be_repaired(self):
        self.assertIsNone(proposed_quote('Target effect F=9', 'Target effect F=8'))

    def test_reordered_words_cannot_be_repaired(self):
        self.assertIsNone(proposed_quote('beta alpha', 'alpha beta'))

    def test_large_source_gap_requires_parent_review(self):
        self.assertIsNone(proposed_quote('Target effect F=9',
                                        'Target effect ' + 'x' * 1600 + ' F=9'))


if __name__ == '__main__':
    unittest.main()
