"""Ensure every batch item is inspectable without changing approved operations."""
import json
import unittest
from build_batch_evidence import H, build

class BatchEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=(H/'batch_review.json').read_bytes()
        cls.data=build()
        cls.batch=json.loads(cls.before)

    def test_exact_coverage_and_approval_fingerprints_preserved(self):
        expected={i['id'] for g in self.batch['groups'] for i in g['items']}
        self.assertEqual(set(self.data['items']),expected)
        self.assertEqual((H/'batch_review.json').read_bytes(),self.before)

    def test_every_item_has_quote_and_reasoning(self):
        for key,item in self.data['items'].items():
            with self.subTest(item=key):
                if item['kind']=='row':
                    for field in item['fields'].values():
                        self.assertTrue(field.get('reason') or field.get('rationale'))
                        self.assertTrue(field['proofs'] or field['quoted_passages'])
                else:
                    self.assertTrue(item['reason']);self.assertTrue(item['proofs'])
                    self.assertEqual(item['outcome_status'],'not_adjudicated')
                    self.assertTrue(item['replication']);self.assertTrue(item['original'])
                    self.assertTrue(item['already_in_flora'])
                    self.assertNotIn('outcome',item['original'])

    def test_retired_outcome_batches_are_gone(self):
        self.assertEqual({g['id'] for g in self.batch['groups']},{'confirmed_missing_pairs'})
        self.assertFalse([k for k,v in self.data['items'].items() if v['kind']=='row'])

if __name__=='__main__':unittest.main()
