import copy,sys,tempfile,unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from derived_effects import documented_proportion_odds_ratio

class DocumentedProportionOR(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  directory=Path(self.tmp.name)/'texts';directory.mkdir();self.source=str(directory/'primary.txt')
  p=patch('compare.B',Path(self.tmp.name));p.start();self.addCleanup(p.stop)
 def fixture(self,values,percentages,complements,answer):
  quote=f'First condition: {percentages[0]}% preferred the reported outcome. Second condition: {percentages[1]}% preferred the reported outcome.'
  Path(self.source).write_text(quote)
  expression=f'({values[0]}/(1-{values[0]}))/({values[1]}/(1-{values[1]}))'
  receipt={'field':'es_value_o','proportions':values,'quoted_inputs':[{'percent':p,'complement':c} for p,c in zip(percentages,complements)],'input_roles':['first-condition outcome','second-condition outcome'],'expected_coding_expression':expression}
  row={'es_type_o':'OR','es_repr_o':'p. 7, ='+expression}
  decision={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_metric':'OR','correct_value':answer,'source_path':self.source,'quote':quote,'location':'Results'}
  return receipt,row,decision
 def test_documented_direct_percentages_reproduce_reported_rounding(self):
  args=self.fixture(['0.89','0.11'],['89','11'],[False,False],'65.46280992')
  self.assertEqual(documented_proportion_odds_ratio(*args,self.source),Fraction(7921,121))
  args=self.fixture(['0.72','0.56'],['72','56'],[False,False],'2.02')
  self.assertEqual(documented_proportion_odds_ratio(*args,self.source),Fraction(99,49))
 def test_existing_complement_coding_keeps_exact_thirteen_thirds(self):
  args=self.fixture(['0.7','0.35'],['70','65'],[False,True],'4.333333333')
  self.assertEqual(documented_proportion_odds_ratio(*args,self.source),Fraction(13,3))
  receipt,row,decision=args;receipt['quoted_inputs'][1]['complement']=False
  with self.assertRaises(AssertionError):documented_proportion_odds_ratio(receipt,row,decision,self.source)
 def test_source_target_metric_formula_and_rounding_are_required(self):
  receipt,row,decision=self.fixture(['0.89','0.11'],['89','11'],[False,False],'65.46280992')
  for change in [{'completion_pass':'old'},{'replaces_unverified':False},{'target_match_confirmed':False},{'verdict':'undeterminable'},{'correct_metric':'w'},{'correct_value':'65.47'},{'source_path':'other.txt'},{'quote':'89% and 12%'}]:
   with self.subTest(change=change),self.assertRaises(AssertionError):documented_proportion_odds_ratio(receipt,row,{**decision,**change},self.source)
  for change in [{'es_repr_o':''},{'es_type_o':'test statistic'}]:
   with self.subTest(change=change),self.assertRaises(AssertionError):documented_proportion_odds_ratio(receipt,{**row,**change},decision,self.source)
  for change in [{'percent':'88'},{'complement':True},{'complement':1}]:
   changed=copy.deepcopy(receipt);changed['quoted_inputs'][0].update(change)
   with self.subTest(change=change),self.assertRaises(AssertionError):documented_proportion_odds_ratio(changed,row,decision,self.source)

if __name__=='__main__':unittest.main()
