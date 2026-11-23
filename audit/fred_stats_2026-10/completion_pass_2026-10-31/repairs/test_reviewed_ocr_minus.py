import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from derived_effects import reviewed_ocr_minus_copy
from consistency import number

class ReviewedMinus(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  source_dir=Path(self.tmp.name)/'texts';source_dir.mkdir();self.source=str(source_dir/'primary.txt')
  patched=patch('compare.B',Path(self.tmp.name));patched.start();self.addCleanup(patched.stop)
  self.receipt={'field':'es_value_o','printed_value':'⫺2.38','source_label':'Motherhood interactiona','statistic_quote':'Motherhood interactiona ⫺2.38','negative_context_quote':'the motherhood penalty interaction is significant and negative across all four models'}
  Path(self.source).write_text(self.receipt['statistic_quote']+'\n'+self.receipt['negative_context_quote'])
  self.row={'es_type_o':'b (unstd)'}
  self.review={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'blind_right','correct_metric':'b (unstd)','correct_value':'-2.38','source_path':self.source,'quote':self.receipt['statistic_quote'],'location':'Table 4'}
 def test_exact_reviewed_coefficient_with_explicit_negative_context(self):
  self.assertEqual(reviewed_ocr_minus_copy(self.receipt,self.row,self.review,self.source),'-2.38')
  self.assertIsNone(number('⫺2.38'))
  self.assertIn('⫺2.38',Path(self.source).read_text())
 def test_missing_context_wrong_target_source_metric_sign_or_value_cannot_verify(self):
  for change in [{'completion_pass':'old'},{'replaces_unverified':False},{'target_match_confirmed':False},{'verdict':'shipped_right'},{'correct_metric':'d'},{'correct_value':'2.38'},{'correct_value':'-2.39'},{'source_path':'other.txt'},{'quote':'Parent ⫺2.38'}]:
   with self.subTest(change=change),self.assertRaises(AssertionError):reviewed_ocr_minus_copy(self.receipt,self.row,{**self.review,**change},self.source)
  for change in [{'printed_value':'2.38'},{'printed_value':'⫺2.39'},{'negative_context_quote':'the coefficient was positive'},{'negative_context_quote':'different negative claim'},{'source_label':'Parent'},{'statistic_quote':'Motherhood interactiona 2.38'}]:
   with self.subTest(change=change),self.assertRaises(AssertionError):reviewed_ocr_minus_copy({**self.receipt,**change},self.row,self.review,self.source)
  with self.assertRaises(AssertionError):reviewed_ocr_minus_copy(self.receipt,{'es_type_o':'d'},self.review,self.source)

if __name__=='__main__':unittest.main()
