import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from review_prompt_payload import pack

class ReviewPayload(unittest.TestCase):
 def test_field_evidence_and_prior_objections_survive_row_sharing(self):
  shared={'audit_id':1,'input':{'reference':'Primary article','unfinished_fields':['n_r','pval_value_r']},'worker_notes':'Two candidate tests','source_path':'canonical-primary.txt'}
  items=[{**copy.deepcopy(shared),'field':'n_r','blind':{'value':'42','quote':'Forty-two observations'},'prior_adjudication':None},
         {**copy.deepcopy(shared),'field':'pval_value_r','blind':{'value':'.032','quote':'p = .032'},'prior_adjudication':{'reason':'Wrong previous outcome'}}]
  before=copy.deepcopy(items);p=pack(items)
  self.assertEqual([{**p['row_context'][str(x['audit_id'])],**x} for x in p['field_reviews']],before)
  self.assertEqual(items,before);self.assertIn('input',p['row_context']['1']);self.assertNotIn('input',p['field_reviews'][0])
 def test_context_that_differs_between_fields_is_not_shared(self):
  items=[{'audit_id':7,'field':'n_o','worker_notes':'participants'}, {'audit_id':7,'field':'es_value_o','worker_notes':'cluster model'}, {'audit_id':8,'field':'n_o','worker_notes':'other paper'}]
  p=pack(items);self.assertNotIn('worker_notes',p['row_context']['7']);self.assertEqual(p['field_reviews'][1]['worker_notes'],'cluster model')

if __name__=='__main__':unittest.main()
