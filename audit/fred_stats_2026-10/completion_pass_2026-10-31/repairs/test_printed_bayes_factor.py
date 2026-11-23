import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from compare import fresh_printed_effect_review,metric

class PrintedBayesFactor(unittest.TestCase):
 def setUp(self):
  self.row={'es_type_r':'Bayes factor','es_value_r':'10.35'}
  self.blind={'metric':'Bayes factor BF01 (null / alternative)','value':'10.35'}
  self.review={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_metric':'Bayes factor BF01','correct_value':'10.35','quote':'The Bayesian t-test yielded BF01 = 10.35 after including 908 participants.'}
 def test_current_exact_direction_and_value_are_confirmed(self):
  self.assertTrue(fresh_printed_effect_review(self.review,'es_value_r',self.row,self.blind))
  self.assertNotEqual(metric('Bayes factor BF01'),metric('Bayes factor'))
  self.assertNotEqual(metric('Bayes factor BF01'),metric('Bayes factor BF10'))
 def test_reciprocal_other_values_and_missing_direction_are_rejected(self):
  for change in [{'correct_metric':'Bayes factor BF10'},{'correct_metric':'Bayes factor'},{'correct_value':'10.84'},{'quote':'BF10 = 10.35'},{'quote':'BF01 = 10.84'},{'quote':'Bayes factor = 10.35'}]:
   with self.subTest(change=change):self.assertFalse(fresh_printed_effect_review({**self.review,**change},'es_value_r',self.row,self.blind))
  for change in [{'metric':'Bayes factor BF10 (alternative / null)'},{'value':'0.0966183575'},{'metric':'Bayes factor'}]:
   with self.subTest(change=change):self.assertFalse(fresh_printed_effect_review(self.review,'es_value_r',self.row,{**self.blind,**change}))
 def test_fresh_target_confirmed_shipped_review_and_generic_requested_bf_required(self):
  for change in [{'completion_pass':'old'},{'replaces_unverified':False},{'target_match_confirmed':False},{'verdict':'undeterminable'},{'verdict':'blind_right'}]:
   with self.subTest(change=change):self.assertFalse(fresh_printed_effect_review({**self.review,**change},'es_value_r',self.row,self.blind))
  for change in [{'es_type_r':'test statistic'},{'es_type_r':'Bayes factor BF10'},{'es_value_r':'10.84'}]:
   with self.subTest(change=change):self.assertFalse(fresh_printed_effect_review(self.review,'es_value_r',{**self.row,**change},self.blind))

if __name__=='__main__':unittest.main()
