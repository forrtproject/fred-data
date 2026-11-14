"""Exact bounded tests and reviewed metric identities preserve printed evidence."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import compare
class MetricEvidence(unittest.TestCase):
 def test_same_explicit_bounded_test_statistic(self):
  row={'es_type_o':'test statistic'}
  self.assertEqual(compare.comp('es_value_o','F < 1',{'value':'< 1','test_statistic':'F < 1','metric':'F'},row),'agree')
 def test_bound_direction_and_test_type_must_match(self):
  row={'es_type_o':'test statistic'}
  for statistic in ['F > 1','t < 1','F <= 1','F < 2','F(1, 30) < 1']:
   self.assertNotIn(compare.comp('es_value_o','F < 1',{'value':'< 1','test_statistic':statistic,'metric':'F'},row),['agree','compatible'])
 def test_reviewed_identity_changes_comparison_copy_only(self):
  e={'value':'.08','metric':'partial eta squared','source_path':'primary.txt','quote':'eta .08','location':'one-way ANOVA','confident':True}
  rule={'printed_value':'.08','printed_metric':'partial eta squared','source_path':'primary.txt','comparison_metric':'etasq','reason':'Source-defined unadjusted one-factor between-subjects ANOVA identity','quote':'one-way ANOVA','location':'p. 3','confident':True}
  with patch.object(compare,'quote_ok',return_value=True):changed=compare.comparison_evidence(1039,'es_value_o',e,{(1039,'es_value_o'):rule})
  self.assertEqual(changed['metric'],'etasq');self.assertEqual(e['metric'],'partial eta squared')
  self.assertEqual(compare.comparison_evidence(1040,'es_value_o',e,{(1039,'es_value_o'):rule}),e)
  with patch.object(compare,'quote_ok',return_value=True):self.assertEqual(compare.comparison_evidence(1039,'es_value_o',{**e,'value':'.09'},{(1039,'es_value_o'):rule})['metric'],'partial eta squared')
 def test_bounded_statistic_does_not_resolve_legacy_unknown_target(self):
  a={'verdict':'shipped_right','correct_value':'F < 1','correct_metric':'test statistic'}
  row={'es_type_o':'test statistic'}
  self.assertFalse(compare.adjudication_confirms_shipped('es_value_o','F < 1',a,row))
  self.assertTrue(compare.adjudication_confirms_shipped('es_value_o','F < 1',{**a,'target_match_confirmed':True},row))
 def test_derived_value_requires_explicit_calculation_receipt_and_preserves_printed(self):
  e={'value':'4.91','metric':'chi-squared','source_path':'primary.txt','quote':'70% and 65%','location':'p. 187','confident':True}
  rule={'printed_value':'4.91','printed_metric':'chi-squared','source_path':'primary.txt','comparison_metric':'OR','comparison_value':'4.333333333','reason':'Documented proportions odds-ratio formula','quote':'70% and 65%','location':'p. 187'}
  with patch.object(compare,'quote_ok',return_value=True):
   self.assertEqual(compare.comparison_evidence(880,'es_value_o',e,{(880,'es_value_o'):rule}),e)
   changed=compare.comparison_evidence(880,'es_value_o',e,{(880,'es_value_o'):{**rule,'derivation':{'result':'13/3','formula':'(7/10)/(3/10) / ((35/100)/(65/100))'}}})
   self.assertEqual(changed['value'],'4.333333333');self.assertEqual(e['value'],'4.91')
 def test_fresh_review_can_resolve_printed_test_notation_or_wrong_test_kind(self):
  row={'es_type_o':'test statistic'}
  a={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'blind_right','correct_value':'F(1, 94) = 9.57','correct_metric':'F'}
  self.assertTrue(compare.fresh_test_review(a,'es_value_o',row))
  for changes in [{'completion_pass':None},{'target_match_confirmed':False},{'verdict':'undeterminable'},{'correct_metric':'d'}]:
   self.assertFalse(compare.fresh_test_review({**a,**changes},'es_value_o',row))
  self.assertFalse(compare.fresh_test_review(a,'es_value_o',{'es_type_o':'d'}))
if __name__=='__main__':unittest.main()
