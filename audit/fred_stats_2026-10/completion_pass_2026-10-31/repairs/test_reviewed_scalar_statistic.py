import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import compare

class ReviewedScalarStatistic(unittest.TestCase):
 def test_fresh_source_review_can_confirm_correct_scalar_without_forcing_prefix(self):
  row={'es_type_o':'test statistic','es_value_o':'1.56'}
  decision={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_value':'1.56','correct_metric':'F'}
  self.assertTrue(compare.fresh_test_review(decision,'es_value_o',row))
 def test_fresh_review_accepts_explicit_f_ratio_table_label(self):
  row={'es_type_o':'test statistic','es_value_o':'F-Ratio = 2.866'}
  decision={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'blind_right','correct_value':'F-Ratio = 3.145','correct_metric':'F-Ratio'}
  self.assertTrue(compare.fresh_test_review(decision,'es_value_o',row))
  self.assertFalse(compare.fresh_test_review({**decision,'completion_pass':'old'},'es_value_o',row))
  self.assertFalse(compare.fresh_test_review({**decision,'target_match_confirmed':False},'es_value_o',row))
  self.assertIsNone(compare.parsed_stat('F-Ratio = 3.145'))
 def test_scalar_confirmation_needs_current_review_positive_kind_and_exact_value(self):
  row={'es_type_o':'test statistic','es_value_o':'1.56'}
  base={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_value':'1.56','correct_metric':'F'}
  for changes in [{'completion_pass':'old'},{'target_match_confirmed':False},{'verdict':'blind_right'},{'correct_value':'2.56'},{'correct_metric':'test statistic'}]:
   with self.subTest(changes=changes):self.assertFalse(compare.fresh_test_review({**base,**changes},'es_value_o',row))

if __name__=='__main__':unittest.main()
