import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import compare

class PrintedEffectReview(unittest.TestCase):
 def setUp(self):
  self.row={'es_type_r':'etasq (partial)','es_value_r':'F(1, 821) = 27.539'}
  self.blind={'value':'0.033','metric':'partial eta-squared (η²p)'}
  self.decision={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'blind_right','correct_value':'0.033','correct_metric':'etasq (partial)'}
 def test_direct_printed_coefficient_can_replace_wrong_statistic_in_coefficient_field(self):
  self.assertEqual(compare.comp('es_value_r',self.row['es_value_r'],self.blind,self.row),'not_comparable')
  self.assertTrue(compare.fresh_printed_effect_review(self.decision,'es_value_r',self.row,self.blind))
 def test_legacy_unknown_target_wrong_metric_or_calculated_value_cannot_use_gate(self):
  for change in [{'completion_pass':'old'},{'target_match_confirmed':False},{'replaces_unverified':False},{'verdict':'undeterminable'},{'correct_metric':'beta (std)'},{'correct_value':'0.05'}]:
   with self.subTest(change=change):self.assertFalse(compare.fresh_printed_effect_review({**self.decision,**change},'es_value_r',self.row,self.blind))
  self.assertFalse(compare.fresh_printed_effect_review(self.decision,'es_value_r',self.row,{**self.blind,'metric':'F'}))
  self.assertFalse(compare.fresh_printed_effect_review(self.decision,'es_value_r',{**self.row,'es_type_r':'t'},self.blind))
  self.assertFalse(compare.fresh_printed_effect_review(self.decision,'es_value_r',{**self.row,'es_value_r':'0.04'},self.blind))

if __name__=='__main__':unittest.main()
