import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from compare import fresh_scientific_p_review
from consistency import p_parts

class ReviewedScientificP(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  root=Path(self.tmp.name);(root/'texts').mkdir();self.source=str(root/'texts/primary.txt')
  quote='Condition × trial × size: p = 1.09 × 10−23.'
  Path(self.source).write_text(quote)
  p=patch('compare.B',root);p.start();self.addCleanup(p.stop)
  self.row={'pval_value_o':'1.09E-23','pval_type_o':'e (=)'}
  self.blind={'value':'1.09 × 10−23','bound':'e','source_path':self.source}
  self.review={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_value':'1.09E-23','correct_bound':'e','quote':quote,'location':'Results','source_path':self.source}
 def test_current_literal_exact_identity_preserves_global_parser(self):
  self.assertTrue(fresh_scientific_p_review(self.review,'pval_value_o',self.row,self.blind))
  self.assertIsNone(p_parts('1.09 × 10−23','e'))
 def test_current_review_confirms_quoted_ascii_exponent_without_global_parser_change(self):
  quote='H* focal interaction: p =\n1.26 x 10-5 in the predicted direction.'
  Path(self.source).write_text(quote)
  row={'pval_value_r':'1.26e-05','pval_type_r':'e (=)'}
  blind={**self.blind,'value':'1.26 x 10-5'}
  review={**self.review,'correct_value':'1.26e-05','quote':quote}
  self.assertTrue(fresh_scientific_p_review(review,'pval_value_r',row,blind))
  self.assertIsNone(p_parts('1.26 x 10-5','e'))
  for value in ['1.26 x 10-4','1.26 x 10 - 5','1.26 * 10-5','1.26 x 10-5 extra']:
   with self.subTest(value=value):self.assertFalse(fresh_scientific_p_review(review,'pval_value_r',row,{**blind,'value':value}))
  self.assertFalse(fresh_scientific_p_review({**review,'quote':quote.replace('p =','p <')},'pval_value_r',row,blind))
  self.assertFalse(fresh_scientific_p_review(review,'pval_value_r',{**row,'pval_value_r':'1.26e-4'},blind))
  for wrong_quote in [quote.replace('10-5','10-50'),quote.replace('10-5','10-5.0')]:
   Path(self.source).write_text(wrong_quote)
   with self.subTest(quote=wrong_quote):self.assertFalse(fresh_scientific_p_review({**review,'quote':wrong_quote},'pval_value_r',row,blind))
 def test_no_unreviewed_wrong_bound_changed_exponent_or_source_override(self):
  for change in [{'completion_pass':'old'},{'replaces_unverified':False},{'target_match_confirmed':False},{'verdict':'blind_right'},{'correct_bound':'l'},{'correct_value':'1.09e-22'},{'quote':'1.09 × 10−23'},{'source_path':'other.txt'}]:
   with self.subTest(review=change):self.assertFalse(fresh_scientific_p_review({**self.review,**change},'pval_value_o',self.row,self.blind))
  for change in [{'value':'1.09 × 10−22'},{'value':'1.09 × 10-23'},{'value':'1.09 × 10−23 extra'},{'bound':'l'},{'source_path':'other.txt'}]:
   with self.subTest(blind=change):self.assertFalse(fresh_scientific_p_review(self.review,'pval_value_o',self.row,{**self.blind,**change}))
  for change in [{'pval_value_o':'1.09e-22'},{'pval_type_o':'l (<)'}]:
   with self.subTest(row=change):self.assertFalse(fresh_scientific_p_review(self.review,'pval_value_o',{**self.row,**change},self.blind))

if __name__=='__main__':unittest.main()
