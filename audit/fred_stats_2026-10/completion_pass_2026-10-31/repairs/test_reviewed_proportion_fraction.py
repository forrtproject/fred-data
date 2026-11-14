import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from compare import fresh_proportion_fraction_review

class ReviewedProportionFraction(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  root=Path(self.tmp.name);(root/'texts').mkdir();self.source=str(root/'texts/primary.txt')
  Path(self.source).write_text('Experiment 5: shape (68.75% of choices).')
  p=patch('compare.B',root);p.start();self.addCleanup(p.stop)
  self.row={'es_type_o':'proportion','es_value_o':'99/144'}
  self.blind={'value':'68.75','metric':'percentage of choices','source_path':self.source}
  self.review={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_value':'99/144','correct_metric':'proportion','quote':'shape (68.75% of choices)','location':'Experiment 5 Results','source_path':self.source}
 def test_exact_reviewed_identity_without_changing_global_number_parser(self):
  self.assertTrue(fresh_proportion_fraction_review(self.review,'es_value_o',self.row,self.blind))
  self.assertTrue(fresh_proportion_fraction_review(self.review,'es_value_o',{**self.row,'es_value_o':'proportion: 99/144'},self.blind))
  from consistency import number
  self.assertIsNone(number('99/144'))
 def test_unreviewed_wrong_units_nonidentical_fraction_and_unquoted_values_rejected(self):
  for change in [{'completion_pass':'old'},{'replaces_unverified':False},{'target_match_confirmed':False},{'verdict':'blind_right'},{'correct_metric':'d'},{'correct_value':'98/144'},{'quote':'shape (68.74% of choices)'},{'source_path':'other.txt'}]:
   with self.subTest(review=change):self.assertFalse(fresh_proportion_fraction_review({**self.review,**change},'es_value_o',self.row,self.blind))
  for raw in ['98/144','144/99','99/0','0.6875','99/144 extra','d: 99/144','proportion 99/144']:
   with self.subTest(raw=raw):self.assertFalse(fresh_proportion_fraction_review({**self.review,'correct_value':raw},'es_value_o',{**self.row,'es_value_o':raw},self.blind))
  for change in [{'value':'.6875'},{'metric':'d'},{'source_path':'other.txt'}]:
   with self.subTest(blind=change):self.assertFalse(fresh_proportion_fraction_review(self.review,'es_value_o',self.row,{**self.blind,**change}))

if __name__=='__main__':unittest.main()
