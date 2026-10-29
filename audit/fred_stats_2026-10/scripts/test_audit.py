import unittest,json
from pathlib import Path
from consistency import rounding,pinterval,stat_interval
from compare import adjudication_confirms_shipped,comp,source_prefix,original_secondary_source,original_primary_evidence,SOURCE_PROVENANCE
from schema import validate
from retries import failure,atomic
from prepare import locators
from validate_adjudication import validate_batch,parse_response
from protect_enrichment import preserve_completed
from stop_argon import prompt_key
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
 def test_integer_count_grouping_is_formatting_only(self):
  from consistency import analytic_n,number
  for text in ['1,950','1 950','1\u202f950']:
   self.assertEqual(comp('n_o','1950',{'value':text},{}),'agree')
  self.assertEqual(comp('n_r','1036',{'value':'1,032'},{}),'near')
  self.assertIsNone(analytic_n('34;42'));self.assertIsNone(analytic_n('0,25'))
  self.assertIsNone(number('1,950')) # never reinterpret an ES decimal convention
 def test_compatible_bounded_p_not_identical(self):
  self.assertEqual(comp('pval_value_o','.001',{'value':'.01','bound':'l'},{'pval_type_o':'l (<)'}),'compatible')
  self.assertEqual(comp('pval_value_o','.01',{'value':'.01','bound':'ge'},{'pval_type_o':'l (<)'}),'differ')
  self.assertEqual(comp('pval_value_o','.84',{'value':'.084','bound':'e'},{'pval_type_o':'e (=)'}),'differ')
 def test_p_identical_requires_equal_printed_precision_intervals(self):
  r={'pval_type_o':'e (=)'}
  self.assertEqual(comp('pval_value_o','.010',{'value':'.01','bound':'e'},r),'compatible')
  self.assertEqual(comp('pval_value_o','.010',{'value':'1.0e -2','bound':'e'},r),'identical')
 def test_scientific_p_preserves_rounding_and_strict_bounds(self):
  r={'pval_type_o':'e (=)'}
  for v in ['2.2e -16','p = 2.2 × 10^{-16}','2.2e-400']:
   self.assertEqual(comp('pval_value_o','0',{'value':v,'bound':'e'},r),'compatible')
  self.assertEqual(comp('pval_value_o','.001',{'value':'<1.68e -305','bound':'l'},{'pval_type_o':'l (<)'}),'compatible')
  self.assertEqual(comp('pval_value_o','0',{'value':'3.32e -285','bound':'l'},{'pval_type_o':'l (<)'}),'differ')
  self.assertEqual(comp('pval_value_o','1e-400',{'value':'3e-400','bound':'e'},r),'differ')
  self.assertEqual(comp('pval_value_o','.01',{'value':'p >= .01','bound':'ge'},{'pval_type_o':'l (<)'}),'differ')
  self.assertEqual(comp('pval_value_o','.01',{'value':'.01 to .02','bound':'e'},r),'not_comparable')
 def test_wrong_blind_target_can_be_resolved_by_direct_shipped_evidence(self):
  a={'verdict':'shipped_right','correct_value':'2986'}
  self.assertTrue(adjudication_confirms_shipped('n_r','2986',a,{}))
  self.assertFalse(adjudication_confirms_shipped('n_r','2986',{**a,'verdict':'blind_right'},{}))
  a={'verdict':'shipped_right','correct_value':'.03'}
  self.assertFalse(adjudication_confirms_shipped('es_value_o','.03',a,{'es_type_o':'r'}))
  self.assertTrue(adjudication_confirms_shipped('es_value_o','.03',{**a,'correct_metric':'r'},{'es_type_o':'r'}))
 def test_statistic_label_and_degrees_of_freedom(self):
  b={'value':'11.03','metric':'F','test_statistic':'F(1,154)=11.03'};r={'es_type_o':'test statistic'}
  self.assertEqual(comp('es_value_o','F(1, 154) = 11.03',b,r),'agree')
  self.assertEqual(comp('es_value_o','F(1, 156) = 11.03',b,r),'differ')
 def test_aliases_do_not_convert_metrics_or_signs(self):
  self.assertEqual(comp('es_value_o','.30',{'value':'.30','metric':'partial eta squared'},{'es_type_o':'etasq (partial)'}),'agree')
  self.assertEqual(comp('es_value_o','.30',{'value':'.30','metric':'d'},{'es_type_o':'r'}),'not_comparable')
  self.assertEqual(comp('es_value_o','.30',{'value':'-.30','metric':'r'},{'es_type_o':'r'}),'differ')
 def test_equivalent_metric_labels_preserve_substantive_distinctions(self):
  from compare import metric
  for alias,canonical in [('β (standardized SEM coefficient)','beta (std)'),('B (unstandardized)','b (unstd)'),('partial η²','etasq (partial)'),('Cohen’s d (author-derived standardized effect size)','d')]:
   self.assertEqual(metric(alias),canonical)
  self.assertNotEqual(metric('etasq'),metric('partial eta squared'))
  self.assertNotEqual(metric('r'),metric('partial r'))
  self.assertNotEqual(metric('beta (std)'),metric('β (logistic regression coefficient; not explicitly standardised)'))
 def test_es_typography_preserves_metric_sign_and_precision(self):
  self.assertEqual(comp('es_value_r','-.068',{'value':'–0.068','metric':'d'},{'es_type_r':'d'}),'agree')
  self.assertEqual(comp('es_value_r','.00005',{'value':'5.46 e-5','metric':'partial eta squared'},{'es_type_r':'etasq (partial)'}),'compatible')
  self.assertEqual(comp('es_value_o','188000000000',{'value':'1.88 · 10¹¹','metric':'OR'},{'es_type_o':'OR'}),'agree')
  self.assertEqual(comp('es_value_r','.001',{'value':'< .001','metric':'partial eta squared'},{'es_type_r':'etasq (partial)'}),'compatible')
  self.assertEqual(comp('es_value_r','.02',{'value':'< .001','metric':'partial eta squared'},{'es_type_r':'etasq (partial)'}),'differ')
  self.assertEqual(comp('pval_value_o','0',{'value':'2.2 × 10⁻¹⁶','bound':'e'},{'pval_type_o':'e'}),'compatible')
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
 def test_truncated_answer_keeps_only_complete_json_objects(self):
  a={'audit_id':1,'field':'n_o','reason':'A brace } in a string is not an object boundary.'}
  text='## Answer\n```json\n['+json.dumps(a)+', {"audit_id":2,"field":"n'
  parsed,mode=parse_response(text);self.assertEqual(parsed,[a]);self.assertEqual(mode,'complete_object_prefix')
  with self.assertRaises(json.JSONDecodeError):parse_response('[agy] print timeout after 10m')
 def test_original_secondary_source_is_not_primary_verification(self):
  import hashlib
  row={'doi_o':'10.1/original','doi_r':'10.2/replication'};key=hashlib.sha256(row['doi_r'].encode()).hexdigest()[:24]
  self.assertTrue(original_secondary_source({'source_path':'/texts/'+key+'_supp.txt'},row))
  self.assertFalse(original_secondary_source({'source_path':'/texts/'+key+'.txt'},{'doi_o':row['doi_r'],'doi_r':row['doi_r']}))
 def test_source_provenance_is_relative_to_requested_original(self):
  from unittest.mock import patch
  with patch.dict(SOURCE_PROVENANCE,{'/texts/shared.txt':{'work_doi':'10.1/paper'}}):
   e={'source_path':'/texts/shared.txt'}
   self.assertFalse(original_secondary_source(e,{'doi_o':'10.1/paper','doi_r':'10.2/rep'}));self.assertTrue(original_primary_evidence(e,{'doi_o':'10.1/paper'}))
   self.assertTrue(original_secondary_source(e,{'doi_o':'10.3/other','doi_r':'10.1/paper'}));self.assertFalse(original_primary_evidence(e,{'doi_o':'10.3/other'}))
 def test_locator_revisit_preserves_completed_sides(self):
  before=failure(1,'initial');before['replication']['status']='locator_insufficient';before['original']['status']='done';before['original']['n']['value']='20';before['reported_success']['status']='done';before['reported_success']['value']='mixed'
  after=failure(1,'revisit');after['original']['n']['value']='999';after['replication']['status']='done';after['replication']['n']['value']='40';after['reported_success']['value']='failed'
  merged=preserve_completed(before,after);self.assertEqual(merged['original'],before['original']);self.assertEqual(merged['reported_success'],before['reported_success']);self.assertEqual(merged['replication'],after['replication']);self.assertEqual(after['original']['n']['value'],'999')
 def test_missing_coded_fields_require_review_when_source_supplies_value(self):
  self.assertEqual(comp('n_o',None,{'value':'20'},{}),'differ')
  self.assertEqual(comp('es_value_o',None,{'value':'.2','metric':'r'},{'es_type_o':'r'}),'differ')
  self.assertEqual(comp('es_value_o',None,{'value':'.2','metric':'r'},{'es_type_o':None}),'not_comparable')
  self.assertEqual(comp('pval_value_o',None,{'value':'.02','bound':'e'},{'pval_type_o':None}),'differ')
 def test_cli_identity_survives_instruction_changes_and_excludes_other_audits(self):
  import hashlib
  root=str(Path(__file__).resolve().parents[1]/'texts');payload=[{'audit_id':1,'field':'n_o'}];expected=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:16]
  for preamble in ['Initial instruction','Revised instruction']:
   self.assertEqual(prompt_key(['agy','-p',preamble+'\n\n'+json.dumps(payload),'--add-dir',root]),expected)
  self.assertIsNone(prompt_key(['agy','-p','Other\n\n'+json.dumps(payload),'--add-dir','/unrelated/audit/texts']))
 def test_large_prompt_file_identity_is_scoped_and_payload_verified(self):
  import tempfile,hashlib
  root=Path(__file__).resolve().parents[1];payload=[{'audit_id':999999,'field':'n_o'}];key=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:16]
  with tempfile.TemporaryDirectory(dir=root/'adjudications') as temp:
   path=Path(temp)/('prompt_'+key+'.txt');path.write_text('Instruction\n\n'+json.dumps(payload))
   args=['agy','-p','FRED_AUDIT_PROMPT_FILE: '+str(path)+'\nRead it.','--add-dir',str(root/'texts')]
   self.assertEqual(prompt_key(args),key)
   args[2]='FRED_AUDIT_PROMPT_FILE: /unrelated/prompt_'+key+'.txt';self.assertIsNone(prompt_key(args))
 def test_paper_level_success_does_not_certify_unidentified_effect(self):
  from compare import narrative_scope_unknown
  x={'replication':{'status':'locator_insufficient'},'reported_success':{'location':'Discussion'},'notes':'The value records only a paper-level narrative, not an identified individual effect.'}
  self.assertTrue(narrative_scope_unknown(x))
  x['replication']['status']='done';self.assertFalse(narrative_scope_unknown(x))
  x['replication']['status']='locator_insufficient';x['notes']='A target-specific author verdict is available although the exact numerical test is not located.';self.assertFalse(narrative_scope_unknown(x))
 def test_focused_review_survives_old_response_cache_refresh(self):
  import tempfile,os
  from compare import load_adjudications
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'adjudications').mkdir()
   old={'audit_id':1,'field':'n_o','verdict':'blind_right','correct_value':'99'}
   review={**old,'verdict':'shipped_right','correct_value':'100'}
   (root/'adjudications/validated_old.json').write_text(json.dumps([old]))
   (root/'adjudications/validated_review.json').write_text(json.dumps([review]))
   (root/'adjudication_tasks.jsonl').write_text(json.dumps({'key':'old','started_at':'2026-10-29T09:00:00Z','focused_review':False})+'\n'+json.dumps({'key':'review','started_at':'2026-10-29T10:00:00Z','focused_review':True})+'\n')
   os.utime(root/'adjudications/validated_old.json',(2000000000,2000000000))
   self.assertEqual(load_adjudications(root)[1,'n_o'],review)
 def test_flag_confirmation_requires_recomputed_resolution(self):
  from confirm_flags import confirm_flags
  r={'input_row_index':1,'es_value_o':'t(48)=2.1','es_type_o':'test statistic','n_o':'49','nested_o':'no','pval_tails_o':'2','pval_value_o':'.8','pval_type_o':'e'}
  flags=[{'input_row_index':'1','flags':'p_consistency_o'}]
  self.assertEqual(confirm_flags([r],flags,[{'audit_id':1,'field':'es_value_r','correction':'5'}])[0]['confirmation'],'no_relevant_confirmed_correction')
  self.assertEqual(confirm_flags([r],flags,[{'audit_id':1,'field':'pval_value_o','correction':'.04'}])[0]['confirmation'],'resolved_by_confirmed_correction')
  self.assertEqual(confirm_flags([r],flags,[{'audit_id':1,'field':'es_value_o','correction':'t(48)=0.254'}])[0]['confirmation'],'resolved_by_confirmed_correction')
 def test_effect_keys_and_complete_exports(self):
  import csv
  b=Path(__file__).resolve().parents[1]
  rows=list(csv.DictReader((b/'manifest.csv').read_text(encoding='utf-8-sig').splitlines()));self.assertEqual(len(rows),2164);self.assertEqual(len({r['effect_id'] for r in rows}),2164)
  for f in ['consistency.csv','results.csv']:
   rr=list(csv.DictReader((b/f).read_text(encoding='utf-8-sig').splitlines()));self.assertEqual([int(r['input_row_index']) for r in rr],list(range(1,2165)))
if __name__=='__main__':unittest.main()
