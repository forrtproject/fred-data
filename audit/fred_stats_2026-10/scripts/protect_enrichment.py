import json,copy
from pathlib import Path
B=Path(__file__).resolve().parents[1]
def preserve_completed(before,after):
 merged=copy.deepcopy(after)
 for side in ['original','replication']:
  if before[side]['status']!='locator_insufficient':merged[side]=copy.deepcopy(before[side])
 if before['reported_success']['status']=='done':merged['reported_success']=copy.deepcopy(before['reported_success'])
 return merged
if __name__=='__main__':
 from retries import atomic,failure
 from schema import validate
 state=B/'enrichment_protected.json';done=set(json.loads(state.read_text())) if state.exists() else set();statuses=json.loads((B/'task_status.json').read_text());events=[]
 for line in (B/'tasks.jsonl').read_text().splitlines():
  r=json.loads(line)
  if not r.get('enrichment') or r['taskId'] in done or statuses.get(r['taskId'],{}).get('status') not in ['completed','failed','cancelled','interrupted']:continue
  for aid in r['audit_ids']:
   old=B/'before_locator_enrichment'/f'{aid}.json';dest=B/'extractions'/f'{aid}.json'
   if not old.exists():continue
   before=json.loads(old.read_text())
   try:after=validate(json.loads(dest.read_text()))
   except Exception:
    if dest.exists():
     q=B/'invalid_checkpoints';q.mkdir(exist_ok=True);dest.replace(q/f'{aid}_locator_revisit.json')
    after=failure(aid,'Locator revisit terminated or invalid; completed prior fields preserved.');after['original']['status']='error';after['replication']['status']='error';after['reported_success']['status']='error'
   merged=preserve_completed(before,after);validate(merged)
   if merged!=after:events.append(aid)
   atomic(dest,merged)
  done.add(r['taskId'])
 if events:
  with (B/'run_log.md').open('a') as file:file.write('\n- Locator revisit protection restored previously completed sides/verdicts for rows '+', '.join(map(str,events))+'. New unfinished-side extractions retained.\n')
 state.write_text(json.dumps(sorted(done),indent=2));print({'revisit_tasks_protected':len(done),'restored_rows':events})
