"""Account for this replacement source without rewriting completed passes."""
import csv, datetime, hashlib, io, json, subprocess, sys
from pathlib import Path
S=Path(__file__).resolve().parent;B=S.parent;R=B.parents[1]
sys.path.insert(0,str(B/'scripts'))
from compare import FIELDS
from schema import validate

def save(name,data):
 (S/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def main():
 baseline=json.loads((S/'baseline.json').read_text());commit=baseline['commit']
 for rel,digest in {**baseline['protected_files'],**baseline['completed_pass_markers']}.items():
  assert hashlib.sha256((B/rel).read_bytes()).hexdigest()==digest,rel
 provenance=json.loads((B/'source_provenance.json').read_text())
 assert all(provenance[k]==v for k,v in baseline['old_provenance'].items())
 for aid in [188,1957,1958]:
  before=json.loads((S/'before_extractions'/f'{aid}.json').read_text());after=validate(json.loads((B/'extractions'/f'{aid}.json').read_text()))
  assert before['replication']['status']=='paper_unavailable'
  assert before['original']==after['original']
  if before['reported_success']['status']=='done':assert before['reported_success']==after['reported_success']
 before=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{commit}:audit/fred_stats_2026-10/results.csv'],text=True).lstrip('\ufeff'))))
 after=list(csv.DictReader((B/'results.csv').open(encoding='utf-8-sig')));assert len(before)==len(after)==2164
 changes=[]
 for old,new in zip(before,after):
  aid=int(new['input_row_index']);assert old['effect_id']==new['effect_id']
  for field in FIELDS:
   if old[field+'_final_verdict'] in ('correct','error'):
    assert new[field+'_final_verdict']==old[field+'_final_verdict'],(aid,field)
    assert new[field+'_suggested_correction']==old[field+'_suggested_correction'],(aid,field)
   if old[field+'_final_verdict']!=new[field+'_final_verdict']:
    assert aid in [188,1957,1958] and field in ['n_r','es_value_r','pval_value_r','reported_success'],(aid,field)
    changes.append({'audit_id':aid,'field':field,'before':old[field+'_final_verdict'],'after':new[field+'_final_verdict'],'correction':new[field+'_suggested_correction']})
 new_verified=[x for x in changes if x['after'] in ('correct','error')];new_errors=[x for x in new_verified if x['after']=='error']
 progress=json.loads((B/'progress.json').read_text());assert len(progress['confirmed_errors'])==baseline['errors']+len(new_errors)
 manifest=json.loads((B/'run_manifest.json').read_text());assert hashlib.sha256((R/'output/FReD.xlsx').read_bytes()).hexdigest()==manifest['output_initial_sha256']
 summary={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':commit,'source_key':'6b0931c1fac7d238d367b14a','new_complete_primary_sources':1,'exact_source_coverage':249,'initially_missing_sources':255,'eligible_sides':3,'blind_extraction_records':3,'validation_model':'gpt-6.1-sol','reasoning_effort':'medium','independent_review_model':'Gemini 4 Argon (High)','new_verified_field_instances':len(new_verified),'new_error_fields':len(new_errors),'current_confirmed_errors':len(progress['confirmed_errors']),'current_error_rows':len({x['audit_id'] for x in progress['confirmed_errors']}),'coverage':progress['coverage'],'all_six_numeric_fields_verified_rows':sum(all(r[f+'_final_verdict'] in ('correct','error') for f in FIELDS[:6]) for r in after),'protected_historical_files':len(baseline['protected_files']),'protected_completion_records':len(baseline['completed_pass_markers']),'prior_verified_fields_preserved':True,'prior_provenance_entries_preserved':len(baseline['old_provenance']),'original_sides_preserved':True,'frozen_workbook_sha256':manifest['output_initial_sha256'],'availability_flags':4,'automatic_removals':0,'availability_based_statistical_verdict_changes':0,'new_schedules_created':0,'field_changes':changes}
 save('summary.json',summary);print(json.dumps(summary))
if __name__=='__main__':main()
