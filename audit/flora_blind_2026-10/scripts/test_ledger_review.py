"""The app's plan must follow the ledger, keep protected cases out and hold no private material."""
import json
import re
import unittest

import build_ledger_review as R

CURRENT_MARKERS = re.compile(r'/home/lukas|\.t3/worktrees|evidence_followup/private')


class LedgerReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = R.build()
        cls.bundles = cls.data['bundles']

    def test_statement_is_exhaustive_and_each_row_appears_once(self):
        self.assertEqual(sum(s['rows'] for s in self.data['statement']), 515)
        self.assertEqual(sum(s['fields'] for s in self.data['statement']), 562)
        self.assertEqual(len(self.bundles), 515)
        listed = [i for s in self.data['sets'] for i in s['items']] + self.data['record_exclusions'] + self.data['no_edit'] \
            + self.data['withdraw'] + self.data['rebind'] + self.data['needs_reference'] + self.data['pending_read'] + self.data['blocked']['items'] \
            + [i for g in self.data['rule_groups'] for i in g['items']]
        self.assertEqual(sorted(listed), sorted(self.bundles))

    def test_nothing_is_open_or_approved(self):
        self.assertFalse(self.data['set_decisions_open'])
        self.assertFalse(self.data['user_approval_recorded'])
        self.assertFalse(self.data['canonical_changes_applied'])

    def test_withdrawn_cases_are_not_candidates(self):
        for row in (802, 1868, 2320):
            self.assertEqual(self.bundles[f'row:{row}']['view'], 'withdraw')

    def test_row_462_and_provider_holds_are_not_in_sets(self):
        in_sets = {i for s in self.data['sets'] for i in s['items']}
        self.assertNotIn('row:462', in_sets)
        for bundle in self.bundles.values():
            if any(c['state'] == 'provider_hold' for c in bundle['changes']):
                self.assertEqual(bundle['view'], 'source_blocked')
                self.assertFalse(bundle['quotes'])

    def test_ready_needs_old_value_still_in_current(self):
        for i in (i for s in self.data['sets'] for i in s['items']):
            self.assertEqual({c['relation'] for c in self.bundles[i]['changes']}, {'unchanged_from_frozen'})

    def test_public_quotes_are_short(self):
        for bundle in self.bundles.values():
            for quote in bundle['quotes']:
                self.assertLessEqual(len(quote['text'].replace(' …', '').split()), 25)

    def test_no_private_paths(self):
        self.assertFalse(CURRENT_MARKERS.search(json.dumps(self.data)))

    def test_set_fingerprints_are_stable(self):
        again = R.build()
        self.assertEqual([s['fingerprint'] for s in again['sets']], [s['fingerprint'] for s in self.data['sets']])


if __name__ == '__main__':
    unittest.main()
