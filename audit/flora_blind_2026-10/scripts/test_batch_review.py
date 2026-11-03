"""Guards for bulk approvals, where one bad dependency affects many rows."""
import copy
import json
import unittest
from build_batch_review import H, build, candidate_groups, eligible_case

class BatchReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=candidate_groups()
        cls.queue={c['id']:c for c in json.loads((H/'review_queue.json').read_text())}
        cls.proposals=json.loads((H/'correction_proposals.json').read_text())['changes']

    def test_record_remedies_and_quotes_never_batched(self):
        excluded={x['input_row_index'] for x in json.loads((H/'evidence_provenance_fixes.json').read_text())['changes']}
        for group in self.data['groups']:
            for item in group['items']:
                if not item.get('case_id'):continue
                c=self.queue[item['case_id']]
                self.assertFalse(c.get('record_action'));self.assertFalse(c['requires_review'])
                self.assertNotIn(c['row'],excluded)
                ps=[p for p in self.proposals if p['input_row_index']==c['row']]
                self.assertTrue(eligible_case(c,ps))
                self.assertEqual(set(item['fields']),{p['field'] for p in ps})
                for op in item['operations']:
                    self.assertEqual(len(op['expected_before_full_record_sha256']),64)
                    self.assertNotIn(op['field'],{'type','outcome_quote'})

    def test_dependency_hold_and_unknown_cannot_sneak_in(self):
        item=next(g for g in self.data['groups'] if g['id']=='replication_outcomes')['items'][0]
        c=self.queue[item['case_id']];ps=[p for p in self.proposals if p['input_row_index']==c['row']]
        for key in ['application_hold','application_dependency','record_action_dependency']:
            changed=copy.deepcopy(ps);changed[0][key]='dependent correction'
            self.assertFalse(eligible_case(c,changed))
        changed=copy.deepcopy(c);changed['final_review_summary']={'original':{'disposition':'reviewed_unknown'}}
        self.assertFalse(eligible_case(changed,ps))
        changed=copy.deepcopy(c);changed['record_action']={'action':'remove_row'}
        self.assertFalse(eligible_case(changed,ps))

    def test_missing_pairs_have_no_assigned_outcomes_and_no_plans(self):
        import csv
        with (H/'planned_study_pairs.csv').open(encoding='utf-8-sig') as handle:planned=list(csv.DictReader(handle))
        keys={(p['work_key'],p['doi']) for p in planned}
        items=next(g for g in self.data['groups'] if g['id']=='confirmed_missing_pairs')['items']
        self.assertEqual(len(items),len({i['id'] for i in items}))
        for item in items:
            op=item['operations'][0]
            self.assertIsNone(op['outcome']);self.assertEqual(op['outcome_status'],'not_adjudicated')
            self.assertNotIn((op['work_key'],op['original']['doi']),keys)
            self.assertTrue(op['original']['authors']);self.assertTrue(op['original']['title']);self.assertTrue(op['original']['year'])

    def test_reproduction_operations_preserve_other_axis(self):
        group=next(g for g in self.data['groups'] if g['id']=='reproduction_results')
        for item in group['items']:
            for op in item['operations']:
                self.assertEqual(op['operation'],'set_reproduction_axis')
                self.assertIn('outcome',op['expected_before'])
                self.assertNotIn('outcome_computation',op['expected_before'])

if __name__=='__main__':unittest.main()
