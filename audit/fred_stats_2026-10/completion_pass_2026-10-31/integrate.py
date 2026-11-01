"""Merge only unfinished fields, retaining every baseline-verified field and scope."""
import copy,csv,hashlib,json,sys
from fractions import Fraction
from pathlib import Path
F=Path(__file__).resolve().parent;B=F.parent;sys.path.insert(0,str(B/'scripts'))
from schema import validate
from compare import quote_ok,metric
from consistency import number
from validate_adjudication import validate_batch
from derived_effects import documented_equal_group_d

def atomic(p,x):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n');t.replace(p)
def dedupe_overrides(records):
 old=[r for r in records if r.get('pass')!='completion_2026-10-31']
 own={}
 for r in records:
  if r.get('pass')=='completion_2026-10-31':own[r['audit_id'],r['field']]=r
 return old+list(own.values())
def main():
 base={int(r['input_row_index']):r for r in csv.DictReader((F/'baseline_results.csv').open(encoding='utf-8-sig'))};proposals=json.loads((F/'proposals.json').read_text());ledger=json.loads((F/'integration.json').read_text()) if (F/'integration.json').exists() else {};overrides=json.loads((B/'target_overrides.json').read_text());changes=[];blocked=[];decisions={};equivalences=[]
 for file in sorted((F/'reviews').glob('answer_*_v*.json')):
  stem=file.stem.removeprefix('answer_');key,version=stem.rsplit('_v',1);task=F/'reviews'/f'task_{key}_v{version}.json'
  if not task.exists() or json.loads(task.read_text())['status']!='completed':continue
  data=json.loads(file.read_text())
  for repair in json.loads((F/'repairs/review_evidence_repairs.json').read_text()) if (F/'repairs/review_evidence_repairs.json').exists() else []:
   if repair['file']!=file.name:continue
   assert hashlib.sha256(file.read_bytes()).hexdigest()==repair['raw_sha256']
   d=next(a for a in data if (a['audit_id'],a['field'])==(repair['audit_id'],repair['field']));assert d['quote']==repair['original_quote'];d['quote']=repair['repaired_quote']
  payload=json.loads((F/'reviews'/f'payload_{key}_v{version}.json').read_text());good,failed=validate_batch(data,payload)
  if failed:blocked.append({'review':key,'fields':failed});continue
  for d in good:
   expected=next(a for a in payload if (a['audit_id'],a['field'])==(d['audit_id'],d['field']));assert Path(d['source_path']).resolve()==Path(expected['source_path']).resolve(),'Review used an unassigned source'
   assert isinstance(d.get('target_match_confirmed'),bool)
   assert base[d['audit_id']][d['field']+'_final_verdict'] not in ['correct','error']
   d['completion_pass']='2026-10-31';d['replaces_unverified']=True
  atomic(F/'reviews'/f'validated_{key}_v{version}.json',good)
  atomic(B/'adjudications'/f'validated_completion_{key}_v{version}.json',good)
  for d in good:decisions[d['audit_id'],d['field']]=d
 challenges=json.loads((F/'review_challenges.json').read_text()) if (F/'review_challenges.json').exists() else []
 for c in challenges:
  final=F/'reviews'/f"validated_{c['key']}_v2.json"
  if not final.exists():decisions.pop((c['audit_id'],c['field']),None)
 review_fields={(x['audit_id'],x['field']) for g in json.loads((F/'review_queue.json').read_text()) for x in g['items']}
 holds=json.loads((B/'adjudication_holds.json').read_text());holds=[h for h in holds if h.get('completion_pass') not in ['2026-10-31-pending','2026-10-31-unresolved']]
 for aid,field in sorted(review_fields-set(decisions)):
  holds.append({'audit_id':aid,'field':field,'completion_pass':'2026-10-31-pending','parent_response':'Fresh source evidence is awaiting independent review; do not apply a stale adjudication to the changed blind observation.'})
 for item in proposals:
  if not item['supported']:
   aid,field=item['audit_id'],item['field'];assert base[aid][field+'_final_verdict'] not in ['correct','error']
   holds.append({'audit_id':aid,'field':field,'completion_pass':'2026-10-31-unresolved','parent_response':'Fresh blind source completion remains unresolved ('+item['disposition']['code']+'): '+item['disposition']['reason']})
   continue
  aid,field=item['audit_id'],item['field'];key=item['source_key']+':'+str(aid)+':'+field
  digest=hashlib.sha256(json.dumps(item,sort_keys=True).encode()).hexdigest();decision=decisions.get((aid,field));signature=digest+(':review_required' if (aid,field) in review_fields else ':direct')+(':'+hashlib.sha256(json.dumps(decision,sort_keys=True).encode()).hexdigest() if decision else '')
  signature+=':metric-copy-v1'
  if decision and decision.get('target_match_confirmed') is True and decision['verdict']!='undeterminable' and field.startswith('es_') and metric(decision.get('correct_metric'))==metric(item['input']['es_type_o' if item['side']=='original' else 'es_type_r']) and number(item['blind']['value']) is not None and number(item['blind']['value'])==number(decision.get('correct_value')):
   equivalences.append({'audit_id':aid,'field':field,'printed_value':item['blind']['value'],'printed_metric':item['blind']['metric'],'source_path':item['blind']['source_path'],'comparison_metric':decision['correct_metric'],'reason':decision['reason'],'location':decision['location'],'quote':decision['quote'],'completion_pass':'2026-10-31'})
  if ledger.get(key,{}).get('signature')==signature:continue
  assert base[aid][field+'_final_verdict'] not in ['correct','error']
  dest=B/'extractions'/f'{aid}.json';before=validate(json.loads(dest.read_text()));merged=copy.deepcopy(before);side=item['side'];e=copy.deepcopy(item['blind'])
  if not (F/'before_extractions'/dest.name).exists():atomic(F/'before_extractions'/dest.name,before)
  if field=='reported_success':merged[field]=e
  else:
   sub='n' if field.startswith('n_') else 'es' if field.startswith('es_') else 'p';merged[side][sub]=e;merged[side]['status']='done'
  # Existing side-level identity remains unchanged. Confirmation is narrowly field scoped.
  needs_review=(aid,field) in review_fields;confirmed=item['worker_target_match'] is True and not needs_review
  if decision:confirmed=decision.get('target_match_confirmed') is True and decision['verdict']!='undeterminable' and (field!='reported_success' or decision.get('effect_specific_verdict_confirmed') is True)
  ev=decision if confirmed and decision else e
  assert quote_ok({**ev,'value':'field scope','confident':True})
  overrides.append({'audit_id':aid,'field':field,'side':side,'target_match':True if confirmed else False if field=='reported_success' else None,'location':ev['location'],'quote':ev['quote'],'source_path':ev['source_path'],'reason':('Independent completion review confirms field target; ' if decision and confirmed else 'Fresh blind completion identifies this field target; ' if confirmed else 'Completion field is pending independent target/sample/metric review; ')+item['worker_target_description'],'pass':'completion_2026-10-31'})
  # Promoting one numeric field cannot turn an old broad narrative into a verified outcome.
  if field!='reported_success' and side=='replication' and before[side]['status']!='done' and base[aid]['reported_success_final_verdict'] not in ['correct','error'] and merged['reported_success'].get('value') is not None:
   overrides.append({'audit_id':aid,'field':'reported_success','side':'replication','target_match':False,'location':e['location'],'quote':e['quote'],'source_path':e['source_path'],'reason':'Only a numeric field was completed; individual author-verdict scope remains unreviewed.','pass':'completion_2026-10-31'})
  merged['notes']=merged['notes']+'\nCompletion source review ('+field+'): '+item['disposition']['reason'];validate(merged)
  # Field masks ensure untouched and already verified evidence blocks remain exact.
  for f in ['n_o','es_value_o','pval_value_o','n_r','es_value_r','pval_value_r','reported_success']:
   if base[aid][f+'_final_verdict'] not in ['correct','error']:continue
   if f=='reported_success':assert before[f]==merged[f]
   else:
    w='original' if f.endswith('_o') else 'replication';z='n' if f.startswith('n_') else 'es' if f.startswith('es_') else 'p';assert before[w][z]==merged[w][z]
  atomic(dest,merged);ledger[key]={'signature':signature,'audit_id':aid,'field':field,'source_key':item['source_key'],'reviewed':bool(decision),'field_target_confirmed':confirmed};changes.append([aid,field])
 for receipt in json.loads((F/'repairs/derived_effects.json').read_text()) if (F/'repairs/derived_effects.json').exists() else []:
  aid,field=receipt['audit_id'],receipt['field'];decision=decisions.get((aid,field))
  if not decision or decision['verdict']=='undeterminable' or decision.get('target_match_confirmed') is not True:continue
  item=next(a for a in proposals if (a['audit_id'],a['field'])==(aid,field));row=json.loads((B/'parent_rows.json').read_text())[aid-1]
  assert receipt['expected_coding_expression'] in row['es_repr_'+field[-1]],'Calculation is not documented in original coding'
  assert metric(decision['correct_metric'])==metric(row['es_type_'+field[-1]])
  if receipt['calculation']=='reported_proportion_odds_ratio':
   p,q=map(Fraction,receipt['proportions']);result=(p/(1-p))/(q/(1-q));assert abs(result-Fraction(decision['correct_value']))<Fraction(1,10**9)
   assert '70%' in decision['quote'] and '65%' in decision['quote'],'Primary reported input proportions missing'
  elif receipt['calculation']=='documented_equal_group_cohens_d':result=documented_equal_group_d(receipt,row,decision,item['blind']['source_path'])
  else:raise AssertionError('Unsupported documented calculation')
  equivalences.append({'audit_id':aid,'field':field,'printed_value':item['blind']['value'],'printed_metric':item['blind']['metric'],'source_path':item['blind']['source_path'],'comparison_metric':decision['correct_metric'],'comparison_value':decision['correct_value'],'reason':decision['reason'],'location':decision['location'],'quote':decision['quote'],'derivation':{**receipt,'exact_result':str(result)},'completion_pass':'2026-10-31'})
 atomic(B/'metric_equivalences.json',equivalences);atomic(B/'adjudication_holds.json',holds);atomic(B/'target_overrides.json',dedupe_overrides(overrides));atomic(F/'integration.json',ledger);atomic(F/'integration_blockers.json',blocked);print(json.dumps({'integrated_fields':len(ledger),'changed_this_run':changes,'review_blockers':blocked}))
if __name__=='__main__':main()
