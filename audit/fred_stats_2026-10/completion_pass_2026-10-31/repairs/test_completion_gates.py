"""Pending review and precedence regressions using a one-row comparison export."""
import contextlib,csv,importlib.util,io,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
F=Path(__file__).resolve().parents[1];B=F.parent
sys.path.insert(0,str(B/'scripts'));sys.path.insert(0,str(F))
import compare
from retries import failure
from integrate import dedupe_overrides
if os.environ.get('FRED_COMPARE_REFERENCE'):
 spec=importlib.util.spec_from_file_location('reference_compare',os.environ['FRED_COMPARE_REFERENCE']);compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)

class CompletionGates(unittest.TestCase):
 def test_pending_review_blocks_even_numeric_agreement_and_success(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'extractions').mkdir();x=failure(1,'fixture')
   for side in ['original','replication']:
    x[side].update(status='done',target_match=True,target_description='Identified test')
    for sub in ['n','es','p']:
     x[side][sub].update(value='10',confident=True,location='p. 1',quote='Ten',source_path='fixture.txt')
    x[side]['es']['metric']='d';x[side]['p']['value']='0.1';x[side]['p']['bound']='e'
   x['reported_success'].update(value='failed',confident=True,quote='Failed',location='p. 1',source_path='fixture.txt')
   r={'input_row_index':1,'effect_id':'test','fred_id':'fixture_1','es_type_o':'d','es_type_r':'d','pval_type_o':'e','pval_type_r':'e','doi_o':'','doi_r':'','study_o':'1','study_r':'1','work_key':'fixture'}
   for field in compare.FIELDS:r[field]='failed' if field=='reported_success' else '0.1' if field.startswith('pval') else '10'
   (root/'parent_rows.json').write_text(json.dumps([r]));(root/'extractions/1.json').write_text(json.dumps(x))
   (root/'adjudication_holds.json').write_text(json.dumps([{'audit_id':1,'field':field,'completion_pass':'2026-10-31-pending'} for field in ['n_o','reported_success']]))
   with patch.object(compare,'B',root),patch.object(compare,'quote_ok',return_value=True),contextlib.redirect_stdout(io.StringIO()):compare.main()
   with (root/'results.csv').open(encoding='utf-8-sig') as stream:result=next(csv.DictReader(stream))
   self.assertEqual(result['n_o_final_verdict'],'unverified');self.assertEqual(result['reported_success_final_verdict'],'unverified')
   self.assertEqual(result['n_r_final_verdict'],'correct')
 def test_fresh_unverified_review_replaces_obvious_but_old_precedence_stays(self):
  key=(1,'n_o');old={'audit_id':1,'field':'n_o','verdict':'blind_right'}
  fresh={**old,'verdict':'undeterminable','replaces_unverified':True}
  self.assertEqual(compare.combine_obvious({key:fresh},[old])[key],fresh)
  self.assertEqual(compare.combine_obvious({key:{'verdict':'shipped_right'}},[old])[key],old)
 def test_prompt_priors_can_exclude_this_pass_without_losing_old_decisions(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'adjudications').mkdir()
   old={'audit_id':1,'field':'n_o','verdict':'shipped_right'};fresh={**old,'verdict':'undeterminable'}
   (root/'adjudications/validated_a.json').write_text(json.dumps([old]))
   (root/'adjudications/validated_completion_x_v1.json').write_text(json.dumps([fresh]))
   self.assertEqual(compare.load_adjudications(root,exclude_prefixes=('validated_completion_',))[(1,'n_o')],old)
 def test_dedupe_keeps_historical_records_exact_and_last_field_decision(self):
  historical={'audit_id':1,'side':'original','target_match':False}
  a={'audit_id':1,'field':'n_o','pass':'completion_2026-10-31','target_match':False};b={**a,'target_match':True}
  self.assertEqual(dedupe_overrides([historical,a,b]),[historical,b])
if __name__=='__main__':unittest.main()
