import unittest,json
from pathlib import Path
from consistency import rounding,pinterval,stat_interval
from compare import comp,source_prefix
from schema import validate
from retries import failure,atomic
from prepare import locators
from validate_adjudication import validate_batch
class AuditChecks(unittest.TestCase):
 def test_printed_rounding(self):
  self.assertEqual(rounding('.010'),(.0095,.0105))
  self.assertTrue(pinterval('.01','l (<)')[1]<pinterval('.01','e (=)')[1])
 def test_known_statistics(self):
  pi,method=stat_interval('F(1, 154) = 11.03','test statistic',None,None,None)
  self.assertLess(pi[1],.005)
  pi,method=stat_interval('t(48) = 2.1','test statistic',None,None,'2 (two)')
  self.assertGreater(pi[0],.03);self.assertLess(pi[1],.05)
  one,_=stat_interval('z = 2.48','test statistic',None,None,'1 (one)');two,_=stat_interval('z = 2.48','test statistic',None,None,'2 (two)');self.assertAlmostEqual(one[0]*2,two[0])
 def test_rounded_zero_includes_null_test(self):
  for value,metric,n,nested in [('t(48) = 0.0','test statistic',None,None),('z = 0.0','test statistic',None,None),('0.0','r','100','no')]:
   interval,_=stat_interval(value,metric,n,nested,'2');self.assertAlmostEqual(interval[1],1.0)
  self.assertIsNotNone(stat_interval('1.00','r','100','no','2')[0])
 def test_no_d_or_nested_pearson_inference(self):
  self.assertIsNone(stat_interval('.4','d','100','no','2')[0]);self.assertIsNone(stat_interval('.4','r','100','yes','2')[0]);self.assertIsNotNone(stat_interval('.4','r','100','no','2')[0])
 def test_sample_counts_exact_and_near(self):
  self.assertEqual(comp('n_o','100',{'value':'101'},{}),'near');self.assertEqual(comp('n_o','100',{'value':'106'},{}),'differ')
 def test_compatible_bounded_p_not_identical(self):
  self.assertEqual(comp('pval_value_o','.001',{'value':'.01','bound':'l'},{'pval_type_o':'l (<)'}),'compatible')
  self.assertEqual(comp('pval_value_o','.01',{'value':'.01','bound':'ge'},{'pval_type_o':'l (<)'}),'differ')
  self.assertEqual(comp('pval_value_o','.84',{'value':'.084','bound':'e'},{'pval_type_o':'e (=)'}),'differ')
 def test_statistic_label_and_degrees_of_freedom(self):
  b={'value':'11.03','metric':'F','test_statistic':'F(1,154)=11.03'};r={'es_type_o':'test statistic'}
  self.assertEqual(comp('es_value_o','F(1, 154) = 11.03',b,r),'agree')
  self.assertEqual(comp('es_value_o','F(1, 156) = 11.03',b,r),'differ')
 def test_aliases_do_not_convert_metrics_or_signs(self):
  self.assertEqual(comp('es_value_o','.30',{'value':'.30','metric':'partial eta squared'},{'es_type_o':'etasq (partial)'}),'agree')
  self.assertEqual(comp('es_value_o','.30',{'value':'.30','metric':'d'},{'es_type_o':'r'}),'not_comparable')
  self.assertEqual(comp('es_value_o','.30',{'value':'-.30','metric':'r'},{'es_type_o':'r'}),'differ')
 def test_failure_schema_rejects_fabricated_value(self):
  x=failure(1,'timeout');validate(x);x['original']['n']['value']='100'
  with self.assertRaises(ValueError):validate(x)
 def test_atomic_failure_checkpoint(self):
  import tempfile
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'1.json';atomic(path,failure(1,'timeout'));validate(json.loads(path.read_text()));self.assertEqual(list(Path(directory).iterdir()),[path])
 def test_supplement_locators_without_result_leaks(self):
  text=locators('p. 12; Appendix D- Table I; Table A2; F(1,154)=11.03; p < .005')
  for item in ['p. 12','Appendix D','Table I','Table A2']:self.assertIn(item,text)
  self.assertNotIn('11.03',text);self.assertNotIn('.005',text)
  self.assertEqual(locators('https://rpubs.com/chuqihu8/pilot'),'https://rpubs.com/chuqihu8/pilot')
  self.assertEqual(locators('p. 540, including table'),'p. 540')
 def test_project_prefix_preserves_distinct_projects(self):
  self.assertEqual(source_prefix('Camereretal2016_1'),'Camereretal2016');self.assertEqual(source_prefix('Camereretal2018_1'),'Camereretal2018')
  self.assertEqual(source_prefix('ManyLabs5_1c'),source_prefix('ManyLabs5'));self.assertEqual(source_prefix('bth36'),'bth');self.assertEqual(source_prefix(None),'(missing)')
 def test_statistic_n_annotation_is_compared(self):
  b={'value':'22.771','metric':'chi-square','test_statistic':'X2(1, N = 85) = 22.771'};r={'es_type_o':'test statistic'}
  self.assertEqual(comp('es_value_o','X2(1, N = 40) = 22.77',b,r),'differ')
  self.assertEqual(comp('es_value_o','X2(1, N = 85) = 22.77',b,r),'compatible')
 def test_adjudication_preserves_valid_fields(self):
  import tempfile
  directory=Path(__file__).resolve().parents[1]/'texts'
  with tempfile.TemporaryDirectory(dir=directory) as temp:
   source=Path(temp)/'source.txt';source.write_text('There were 20 participants.')
   base={'audit_id':1,'field':'n_o','verdict':'blind_right','correct_value':'20','location':'p. 1','quote':'There were 20 participants.','source_path':str(source),'reason':'The analytic sample had 20 participants.'}
   bad={**base,'field':'n_r','quote':'Not in the supplied source.'}
   good,failed=validate_batch([base,bad],[{'audit_id':1,'field':'n_o'},{'audit_id':1,'field':'n_r'}]);self.assertEqual(len(good),1);self.assertEqual(len(failed),1);self.assertEqual(good[0]['field'],'n_o')
 def test_effect_keys_and_complete_exports(self):
  import csv
  b=Path(__file__).resolve().parents[1]
  rows=list(csv.DictReader((b/'manifest.csv').read_text(encoding='utf-8-sig').splitlines()));self.assertEqual(len(rows),2164);self.assertEqual(len({r['effect_id'] for r in rows}),2164)
  for f in ['consistency.csv','results.csv']:
   rr=list(csv.DictReader((b/f).read_text(encoding='utf-8-sig').splitlines()));self.assertEqual([int(r['input_row_index']) for r in rr],list(range(1,2165)))
if __name__=='__main__':unittest.main()
