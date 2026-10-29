import unittest,json
from pathlib import Path
from consistency import rounding,pinterval,stat_interval
from compare import comp
from schema import validate
from retries import failure
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
 def test_effect_keys_and_complete_exports(self):
  import csv
  b=Path(__file__).resolve().parents[1]
  rows=list(csv.DictReader((b/'manifest.csv').read_text(encoding='utf-8-sig').splitlines()));self.assertEqual(len(rows),2164);self.assertEqual(len({r['effect_id'] for r in rows}),2164)
  for f in ['consistency.csv','results.csv']:
   rr=list(csv.DictReader((b/f).read_text(encoding='utf-8-sig').splitlines()));self.assertEqual([int(r['input_row_index']) for r in rr],list(range(1,2165)))
if __name__=='__main__':unittest.main()
