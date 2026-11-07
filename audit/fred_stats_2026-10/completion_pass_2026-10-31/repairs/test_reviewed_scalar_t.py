import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from compare import fresh_test_review

class ReviewedScalarT(unittest.TestCase):
 def setUp(self):
  self.row={'es_type_o':'test statistic','es_value_o':'2.144927246'}
  self.review={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'blind_right','correct_metric':'t','correct_value':'2.56','quote':'Frame (t ¼ 2.56, p < .02)'}
 def test_literal_labelled_t_accepts_scalar_without_required_prefix(self):
  self.assertTrue(fresh_test_review(self.review,'es_value_o',self.row))
  self.assertTrue(fresh_test_review({**self.review,'quote':'Frame (t = 2.56, p < .02)'},'es_value_o',self.row))
 def test_unlabelled_mismatched_or_other_statistic_quote_does_not_confirm(self):
  for quote in ['OR = 2.56','F = 2.56','t ¼ 4.59','t ¼ -2.56','p = 2.56','2.56']:
   with self.subTest(quote=quote):self.assertFalse(fresh_test_review({**self.review,'quote':quote},'es_value_o',self.row))
 def test_current_target_requested_metric_and_review_verdict_required(self):
  for change in [{'completion_pass':'old'},{'replaces_unverified':False},{'target_match_confirmed':False},{'verdict':'undeterminable'},{'correct_metric':'OR'}]:
   with self.subTest(change=change):self.assertFalse(fresh_test_review({**self.review,**change},'es_value_o',self.row))
  self.assertFalse(fresh_test_review(self.review,'es_value_o',{**self.row,'es_type_o':'OR'}))

if __name__=='__main__':unittest.main()
