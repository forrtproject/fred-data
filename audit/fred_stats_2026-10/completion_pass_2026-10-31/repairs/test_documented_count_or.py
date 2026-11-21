import copy,sys,tempfile,unittest
from pathlib import Path
from fractions import Fraction
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from derived_effects import documented_count_odds_ratio,_unique_binary_event_count

class DocumentedCountOR(unittest.TestCase):
 def setUp(self):
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
  root=Path(tmp.name);(root/'texts').mkdir();self.source=str(root/'texts/primary.txt')
  p=patch('compare.B',root);p.start();self.addCleanup(p.stop)
  allocation='Participants were randomly assigned to one of three conditions, with 24 participants in each condition and each participant receiving only one vignette.'
  choices='Choose one of two options: Remain connected or Go back to reality.'
  complete='The omnibus test reports N=72.'
  positive='In the Positive scenario, 50% chose to go back to reality and 50% would remain connected.'
  negative='For the Negative scenario, 13% preferred reality and 87% would remain connected.'
  Path(self.source).write_text('\n'.join([allocation,choices,complete,positive,negative]))
  self.receipt={'audit_id':1099,'field':'es_value_o','allocation_quote':allocation,'binary_choice_quote':choices,'complete_n_quote':complete,'expected_coding_expression':'(12/12) / (3/21)','groups':[{'source_label':'Positive','n':24,'event':12,'other':12,'event_percent':50,'other_percent':50,'response_quote':positive},{'source_label':'Negative','n':24,'event':3,'other':21,'event_percent':13,'other_percent':87,'response_quote':negative}]}
  self.row={'es_type_o':'OR','es_repr_o':'p.48, OR: = (12/12) / (3/21) = 7.00'}
  self.decision={'audit_id':1099,'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'both_wrong','correct_metric':'OR','correct_value':'7.00','source_path':self.source,'quote':positive+' ... '+negative,'location':'Study 1'}
 def test_documented_binary_counts_reproduce_seven_without_using_rounded_percentages_as_exact(self):
  self.assertEqual(documented_count_odds_ratio(self.receipt,self.row,self.decision,self.source),Fraction(7))
  self.assertNotEqual(Fraction(50,50)/Fraction(13,87),Fraction(7))
 def test_half_percent_boundaries_do_not_assume_a_tie_rule_and_ambiguous_counts_fail(self):
  self.assertEqual(_unique_binary_event_count(24,13,87),3)
  self.assertEqual(_unique_binary_event_count(24,50,50),12)
  with self.assertRaises(AssertionError):_unique_binary_event_count(200,13,87)
  with self.assertRaises(AssertionError):_unique_binary_event_count(24,14,86)
 def test_unknown_target_metric_source_field_or_undocumented_formula_fail(self):
  for change in [{'audit_id':1100},{'completion_pass':'old'},{'target_match_confirmed':False},{'correct_metric':'d'},{'correct_value':'6.69'},{'source_path':'other.txt'},{'verdict':'undeterminable'}]:
   with self.subTest(change=change),self.assertRaises(AssertionError):documented_count_odds_ratio(self.receipt,self.row,{**self.decision,**change},self.source)
  for change in [{'es_type_o':'d'},{'es_repr_o':''},{'es_repr_o':'(3/21) / (12/12)'}]:
   with self.subTest(change=change),self.assertRaises(AssertionError):documented_count_odds_ratio(self.receipt,{**self.row,**change},self.decision,self.source)
  with self.assertRaises(AssertionError):documented_count_odds_ratio({**self.receipt,'field':'es_value_r'},self.row,self.decision,self.source)
 def test_omitted_design_evidence_wrong_roles_counts_and_percentages_fail(self):
  for key in ['allocation_quote','binary_choice_quote','complete_n_quote']:
   r=copy.deepcopy(self.receipt);r[key]=''
   with self.subTest(key=key),self.assertRaises(AssertionError):documented_count_odds_ratio(r,self.row,self.decision,self.source)
  for change in [{'n':25},{'event':4,'other':20},{'source_label':'Neutral'},{'event_percent':12},{'response_quote':'Negative scenario: 13% reality,87% remain connected'}]:
   r=copy.deepcopy(self.receipt);r['groups'][1].update(change)
   with self.subTest(change=change),self.assertRaises(AssertionError):documented_count_odds_ratio(r,self.row,self.decision,self.source)

if __name__=='__main__':unittest.main()
