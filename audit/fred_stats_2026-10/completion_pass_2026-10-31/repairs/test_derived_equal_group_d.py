import copy,sys,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from derived_effects import documented_equal_group_d,documented_f_to_r_to_d

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
 def test_reviewed_study_1a_explicit_halves_support_equal_counts(self):
  r=copy.deepcopy(self.receipt);r['audit_id']=871
  r['allocation_basis']={'kind':'study_1a_explicit_halves','total_quote':'Sixty-four economics and business administration students participated.','allocation_quote':'Half of the participants received an organization chart where the line was rather short whereas the other half of the participants received an organization chart where the line was rather long.'}
  for g in r['groups']:g['n']=32;g['sample_quote']=g['source_label']+' participants'
  Path(self.source).write_text('\n'.join([*(g[k] for g in r['groups'] for k in ['mean_sd_quote','sample_quote']),r['allocation_basis']['total_quote'],r['allocation_basis']['allocation_quote']]))
  self.assertAlmostEqual(documented_equal_group_d(r,self.row,self.decision,self.source),-0.60627,places=5)
  r['coding_sd_tokens']=['1.260','1.47'];r['expected_coding_expression']='=(4.98-5.81)/SQRT((1.260^2+1.47^2)/2)'
  row={**self.row,'es_repr_o':r['expected_coding_expression']}
  self.assertAlmostEqual(documented_equal_group_d(r,row,self.decision,self.source),-0.60627,places=5)
  bad=copy.deepcopy(r);bad['coding_sd_tokens'][0]='1.25'
  with self.assertRaises(AssertionError):documented_equal_group_d(bad,row,self.decision,self.source)
  for total,allocation in [('Sixty-five economics and business administration students participated.',r['allocation_basis']['allocation_quote']),(r['allocation_basis']['total_quote'],'Half of the participants received an organization chart where the line was rather short.')]:
   bad=copy.deepcopy(r);bad['allocation_basis'].update(total_quote=total,allocation_quote=allocation)
   with self.subTest(total=total,allocation=allocation),self.assertRaises(AssertionError):documented_equal_group_d(bad,row,self.decision,self.source)
  bad=copy.deepcopy(r);bad['audit_id']=872
  with self.assertRaises(AssertionError):documented_equal_group_d(bad,self.row,self.decision,self.source)
  bad=copy.deepcopy(r);bad['groups'][0]['n']=31
  with self.assertRaises(AssertionError):documented_equal_group_d(bad,self.row,self.decision,self.source)

class DocumentedF(unittest.TestCase):
 setUp=DocumentedEffect.setUp
 def test_explicit_coding_convention_and_rejection_guards(self):
  q='F(1, 132) = 160.5';Path(self.source).write_text(q)
  expression='esc::cohens_d(r = FReD:::convert_effect_sizes("'+q+'", "test statistic"))'
  receipt={'field':'es_value_o','df1':1,'df2':132,'f':'160.5','statistic_quote':q,'expected_coding_expression':expression}
  row={'es_type_o':'d','es_repr_o':expression}
  decision={**self.decision,'correct_value':'2.21','quote':q,'location':'Results'}
  self.assertAlmostEqual(documented_f_to_r_to_d(receipt,row,decision,self.source),2.205365358,places=8)
  for change in [{'df1':2},{'df2':None},{'df2':0},{'df2':131},{'f':'160.6'},{'statistic_quote':'F(1, 131) = 160.5'}]:
   with self.subTest(change=change),self.assertRaises(AssertionError):documented_f_to_r_to_d({**receipt,**change},row,decision,self.source)
  for change in [{'target_match_confirmed':False},{'correct_metric':'F'},{'correct_value':'2.20'},{'source_path':'other.txt'}]:
   with self.subTest(change=change),self.assertRaises(AssertionError):documented_f_to_r_to_d(receipt,row,{**decision,**change},self.source)
  with self.assertRaises(AssertionError):documented_f_to_r_to_d(receipt,{**row,'es_repr_o':''},decision,self.source)

if __name__=='__main__':unittest.main()
