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
 def test_fresh_review_accepts_explicit_chi_square_symbol(self):
  row={'es_type_o':'test statistic','es_value_o':'X2(2, N = 133) = 8.07'}
  decision={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'both_wrong','correct_value':'X2(1, N = 133) = 8.07','correct_metric':'X2'}
  self.assertTrue(compare.fresh_test_review(decision,'es_value_o',row))
  self.assertFalse(compare.fresh_test_review({**decision,'completion_pass':'old'},'es_value_o',row))
  self.assertFalse(compare.fresh_test_review({**decision,'target_match_confirmed':False},'es_value_o',row))
 def test_fresh_review_confirms_literal_q_without_global_parser_alias(self):
  row={'es_type_o':'test statistic','es_value_o':'q(2, 50) = 3.31'}
  decision={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_value':'q(2, 50) = 3.31','correct_metric':'test statistic'}
  self.assertTrue(compare.fresh_test_review(decision,'es_value_o',row))
  self.assertFalse(compare.fresh_test_review({**decision,'completion_pass':'old'},'es_value_o',row))
  self.assertFalse(compare.fresh_test_review({**decision,'verdict':'blind_right'},'es_value_o',row))
  self.assertFalse(compare.fresh_test_review({**decision,'correct_value':'q(2, 51) = 3.31'},'es_value_o',row))
  self.assertIsNone(compare.parsed_stat(row['es_value_o']))
 def test_current_review_accepts_explicit_one_df_chi_square_label(self):
  row={'es_type_o':'test statistic','es_value_o':'X2(1, N = 106) = 5.5'}
  decision={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'blind_right','correct_value':'X2(1) = 5.50','correct_metric':'chi-square (1 df)'}
  self.assertTrue(compare.fresh_test_review(decision,'es_value_o',row))
  self.assertFalse(compare.fresh_test_review({**decision,'completion_pass':'old'},'es_value_o',row))
  self.assertFalse(compare.fresh_test_review({**decision,'correct_value':'X2(2) = 5.50'},'es_value_o',row))
 def test_current_chi_square_label_preserves_reviewed_sample_annotation(self):
  row={'es_type_o':'test statistic','es_value_o':'X2(1, N = 72) = 0.0'}
  decision={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'both_wrong','correct_value':'X2(1, N = 48) = 0.0','correct_metric':'chi-square'}
  self.assertTrue(compare.fresh_test_review(decision,'es_value_o',row))
  self.assertEqual(compare.comp('es_value_o',row['es_value_o'],{'value':decision['correct_value'],'test_statistic':decision['correct_value']},row),'differ')
  for changes in [{'completion_pass':'old'},{'target_match_confirmed':False},{'replaces_unverified':False},{'verdict':'undeterminable'},{'correct_value':'F(1, 48) = 0.0'},{'correct_value':'0.0'}]:
   self.assertFalse(compare.fresh_test_review({**decision,**changes},'es_value_o',row),changes)
  self.assertFalse(compare.fresh_test_review(decision,'es_value_o',{**row,'es_type_o':'r'}))
  self.assertEqual(compare.metric('chi-square'),'chi-square')
  self.assertIsNone(compare.parsed_stat('chi-square = 0.0'))
 def test_current_review_confirms_identical_bounded_statistic_only(self):
  row={'es_type_o':'test statistic','es_value_o':'t(49) > 3'}
  decision={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_value':'t(49) > 3','correct_metric':'test statistic'}
  self.assertTrue(compare.fresh_test_review(decision,'es_value_o',row))
  for changed in [{'completion_pass':'old'},{'target_match_confirmed':False},{'verdict':'blind_right'},{'correct_value':'t(49) > 2'},{'correct_value':'t(48) > 3'},{'correct_value':'t(49) < 3'},{'correct_value':'F(49) > 3'},{'correct_metric':'r'}]:
   self.assertFalse(compare.fresh_test_review({**decision,**changed},'es_value_o',row),changed)
  self.assertIsNone(compare.parsed_stat(row['es_value_o']))
 def test_scalar_confirmation_needs_current_review_positive_kind_and_exact_value(self):
  row={'es_type_o':'test statistic','es_value_o':'1.56'}
  base={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_value':'1.56','correct_metric':'F'}
  for changes in [{'completion_pass':'old'},{'target_match_confirmed':False},{'verdict':'blind_right'},{'correct_value':'2.56'},{'correct_metric':'test statistic'}]:
   with self.subTest(changes=changes):self.assertFalse(compare.fresh_test_review({**base,**changes},'es_value_o',row))

if __name__=='__main__':unittest.main()
