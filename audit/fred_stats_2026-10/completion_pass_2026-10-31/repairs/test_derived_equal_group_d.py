import copy,sys,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from derived_effects import documented_equal_group_d

class DocumentedEffect(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  source_dir=Path(self.tmp.name)/'texts';source_dir.mkdir();self.source=str(source_dir/'primary.txt')
  patched=patch('compare.B',Path(self.tmp.name));patched.start();self.addCleanup(patched.stop)
  groups=[{'source_label':'Cleanliness priming','mean':'4.98','sd':'1.26','n':20,'mean_sd_quote':'Cleanliness priming (M = 4.98, SD = 1.26)','sample_quote':'Cleanliness priming (n = 20)'},{'source_label':'Neutral priming','mean':'5.81','sd':'1.47','n':20,'mean_sd_quote':'Neutral priming (M = 5.81, SD = 1.47)','sample_quote':'Neutral priming (n = 20)'}]
  Path(self.source).write_text('\n'.join(g[k] for g in groups for k in ['mean_sd_quote','sample_quote']))
  self.receipt={'field':'es_value_o','groups':groups,'expected_coding_expression':'=(4.98-5.81)/SQRT((1.26^2+1.47^2)/2)'}
  self.row={'es_type_o':'d','es_repr_o':self.receipt['expected_coding_expression']}
  self.decision={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_metric':'d','correct_value':'-0.606','quote':groups[0]['mean_sd_quote']+' ... '+groups[1]['mean_sd_quote'],'source_path':self.source}
 def test_documented_source_inputs_and_explicit_equal_counts_reproduce_review(self):
  self.assertAlmostEqual(documented_equal_group_d(self.receipt,self.row,self.decision,self.source),-0.60627,places=5)
 def test_unknown_counts_wrong_source_metric_review_or_formula_cannot_verify(self):
  for change in [{'completion_pass':'old'},{'target_match_confirmed':False},{'correct_metric':'etasq'},{'correct_value':'0.606'},{'quote':'4.98 5.81 1.26'},{'source_path':'other.txt'}]:
   with self.subTest(change=change),self.assertRaises(AssertionError):documented_equal_group_d(self.receipt,self.row,{**self.decision,**change},self.source)
  for change in [{'es_repr_o':''},{'es_type_o':'dz'}]:
   with self.subTest(change=change),self.assertRaises(AssertionError):documented_equal_group_d(self.receipt,{**self.row,**change},self.decision,self.source)
  for change in [{'n':None},{'n':19},{'n':True},{'mean':'4.99'},{'sd':'0'},{'sample_quote':'Cleanliness priming (n = 21)'}]:
   r=copy.deepcopy(self.receipt);r['groups'][0].update(change)
   with self.subTest(change=change),self.assertRaises(AssertionError):documented_equal_group_d(r,self.row,self.decision,self.source)

if __name__=='__main__':unittest.main()
