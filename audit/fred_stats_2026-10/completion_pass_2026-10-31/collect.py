"""Validate blind source-grouped outputs; build field-scoped integration/review proposals."""
import ast,copy,csv,hashlib,json,sys,datetime
from pathlib import Path
F=Path(__file__).resolve().parent;B=F.parent;sys.path.insert(0,str(B/'scripts'))
from compare import quote_ok,comp,metric
from schema import validate

def atomic(p,x):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n');t.replace(p)
def main():
 queue=json.loads((F/('work_queue.json' if (F/'work_queue.json').exists() else 'pilot_queue.json')).read_text());rows=json.loads((B/'parent_rows.json').read_text());baseline={int(r['input_row_index']):r for r in csv.DictReader((F/'baseline_results.csv').open(encoding='utf-8-sig'))};ledger=json.loads((F/'collected.json').read_text()) if (F/'collected.json').exists() else {};proposals=[];review=[];blockers=[]
 for batch in queue:
  state=F/'tasks'/f"{batch['key']}.json"
  if not state.exists() or json.loads(state.read_text())['status']!='completed':continue
  records=json.loads(Path(batch['input']).read_text());dp=Path(batch['output'])/'dispositions.json'
  if not dp.exists():blockers.append({'source':batch['key'],'reason':'Missing dispositions'});continue
  dispositions=json.loads(dp.read_text());expected={(r['audit_id'],f) for r in records for f in r['unfinished_fields']};actual={(d['audit_id'],d['field']) for d in dispositions};assert expected==actual and len(actual)==len(dispositions),(batch['key'],'Disposition accounting')
  by={(d['audit_id'],d['field']):d for d in dispositions};source_reviews=[]
  for record in records:
   aid=record['audit_id'];path=Path(batch['output'])/f'{aid}.json';x=validate(json.loads(path.read_text()));side=record['target_side'];source=next(iter(record['text_paths'].values()));old=json.loads((B/'extractions'/f'{aid}.json').read_text())
   for field in record['unfinished_fields']:
    assert baseline[aid][field+'_final_verdict'] not in ['correct','error']
    e=x['reported_success'] if field=='reported_success' else x[side]['n' if field.startswith('n_') else 'es' if field.startswith('es_') else 'p'];dis=by[aid,field];supported=False
    repairs_path=F/'repairs/evidence_repairs.json'
    repairs=json.loads(repairs_path.read_text()) if repairs_path.exists() else []
    for repair in repairs:
     if (repair['audit_id'],repair['field'])==(aid,field):
      assert repair['raw_output_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
      assert e['quote']==repair['original_quote']
      e={**e,'quote':repair['repaired_quote']}
    value=e.get('test_statistic') if field.startswith('es_') and metric(rows[aid-1]['es_type_'+field[-1]])=='test statistic' and e.get('test_statistic') else e['value']
    if value is not None and e['confident']:
     assert Path(e['source_path']).resolve()==Path(source).resolve(),(aid,field,'wrong source')
     supported=quote_ok({**e,'value':value})
     if not supported:blockers.append({'source':batch['key'],'audit_id':aid,'field':field,'reason':'Literal source evidence failed'});continue
    item={'source_key':batch['key'],'audit_id':aid,'field':field,'side':side,'input':record,'blind':e,'disposition':dis,'worker_target_match':x[side]['target_match'],'worker_target_description':x[side]['target_description'],'worker_notes':x['notes'],'supported':supported,'source_path':source}
    proposals.append(item)
    if not supported:continue
    comparison=comp(field,rows[aid-1][field],{**e,'value':value},rows[aid-1])
    needs_review=(comparison not in ['agree','identical','compatible'] or field=='reported_success' or dis['code']=='extracted_documented_n_sum' or x[side]['target_match'] is not True or old[side]['target_match'] is not True)
    if needs_review:
     item={**item,'shipped':rows[aid-1][field],'comparison':comparison,'coding_context':{k:rows[aid-1].get(k) for k in ['description','es_repr_o','es_repr_r','es_type_o','es_type_r','pval_type_o','pval_type_r','pval_tails_o','pval_tails_r','nested_o','nested_r','reported_success_quote']}}
     source_reviews.append(item)
   ledger[batch['key']+':'+str(aid)]={'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'fields':record['unfinished_fields']}
  if source_reviews:review.append({'key':batch['key'],'source':batch['source'],'source_path':source,'items':source_reviews})
 atomic(F/'collected.json',ledger);atomic(F/'proposals.json',proposals);atomic(F/'review_queue.json',review);atomic(F/'collection_blockers.json',blockers)
 print(json.dumps({'collected_rows':len(ledger),'proposed_fields':len(proposals),'supported_fields':sum(x['supported'] for x in proposals),'review_sources':len(review),'review_items':sum(len(x['items']) for x in review),'blocked_fields':len(blockers)}))
if __name__=='__main__':main()
