import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from compare import reviewed_correction_value,fresh_sample_annotation_review

class ReviewedValuesAndSample(unittest.TestCase):
 def setUp(self):
  self.a={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'effect_specific_verdict_confirmed':True,'verdict':'both_wrong','correct_value':'success'}
  self.z={**self.a,'correct_value':'Z = 2.6, N = 150','correct_metric':'z'}
  self.row={'es_type_o':'test statistic','es_value_o':'Z = 2.6, N = 92'}
 def test_success_serialization_keeps_raw_answer_unchanged(self):
  self.assertEqual(reviewed_correction_value(self.a,'reported_success'),'successful');self.assertEqual(self.a['correct_value'],'success')
 def test_success_serialization_requires_current_confirmed_effect_scope(self):
  for change in [{'completion_pass':'old'},{'replaces_unverified':False},{'target_match_confirmed':False},{'effect_specific_verdict_confirmed':False},{'verdict':'undeterminable'}]:
   with self.subTest(change=change):self.assertEqual(reviewed_correction_value({**self.a,**change},'reported_success'),'success')
 def test_no_other_value_or_field_is_relabeled(self):
  for value in ['successful','mixed','failed',None]:self.assertEqual(reviewed_correction_value({**self.a,'correct_value':value},'reported_success'),value)
  self.assertEqual(reviewed_correction_value(self.a,'es_value_o'),'success')
 def test_current_review_can_correct_only_existing_z_n_annotation(self):
  self.assertTrue(fresh_sample_annotation_review(self.z,'es_value_o',self.row))
 def test_annotation_review_cannot_change_statistic_or_invent_missing_n(self):
  for value in ['Z = 2.7, N = 150','t(148) = 2.6, N = 150','Z = 2.6','Z = 2.6, N = 92']:
   with self.subTest(value=value):self.assertFalse(fresh_sample_annotation_review({**self.z,'correct_value':value},'es_value_o',self.row))
  self.assertFalse(fresh_sample_annotation_review(self.z,'es_value_o',{**self.row,'es_value_o':'Z = 2.6'}))
 def test_annotation_review_needs_current_target_metric_and_correction_verdict(self):
  for change in [{'completion_pass':'old'},{'replaces_unverified':False},{'target_match_confirmed':False},{'verdict':'shipped_right'},{'correct_metric':'r'}]:
   with self.subTest(change=change):self.assertFalse(fresh_sample_annotation_review({**self.z,**change},'es_value_o',self.row))
  self.assertFalse(fresh_sample_annotation_review(self.z,'es_value_o',{**self.row,'es_type_o':'r'}))

if __name__=='__main__':unittest.main()
