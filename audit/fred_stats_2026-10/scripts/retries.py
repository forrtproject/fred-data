import json
from pathlib import Path
from schema import validate
B=Path(__file__).resolve().parents[1]
def failure(aid,reason):
 def ev():return {'value':None,'location':'','quote':'','source_path':'','confident':False}
 def side():return {'status':'timeout','target_match':None,'target_description':reason,'n':{**ev(),'sample_role':'','exclusions':''},'es':{**ev(),'metric':None,'test_statistic':None},'p':{**ev(),'bound':None}}
 return {'audit_id':aid,'original':side(),'replication':side(),'reported_success':{**ev(),'status':'timeout'},'notes':reason}
if __name__=='__main__':
 records=[json.loads(x) for x in (B/'tasks.jsonl').read_text().splitlines() if x];statuses=json.loads((B/'task_status.json').read_text());latest={}
 for r in records:
  if r['kind']=='extraction':latest[r['batch']]=r
 queue=[]
 for batch,r in latest.items():
  status=statuses.get(r['taskId'],{}).get('status')
  if status not in ['completed','failed','cancelled','interrupted']:continue
  ids=[]
  for aid in r['audit_ids']:
   p=B/'extractions'/f'{aid}.json'
   if not p.exists():
    x=failure(aid,'Parent checkpoint: child terminated without effect output; one retry allowed.');p.write_text(json.dumps(x,indent=2))
   try:x=validate(json.loads(p.read_text()))
   except Exception:
    # Never silently discard invalid output. Archive then retry.
    q=B/'invalid_checkpoints';q.mkdir(exist_ok=True);p.rename(q/f'{aid}_attempt{r.get("attempt",1)}.json');x=failure(aid,'Parent checkpoint: child output failed schema validation.');p.write_text(json.dumps(x,indent=2))
   if any(x[s]['status'] in ['timeout','error'] for s in ['original','replication','reported_success']):ids.append(aid)
  if ids and r.get('attempt',1)<2:
   original=json.loads((B/'inputs'/f'{batch}.json').read_text());dest=B/'inputs'/f'{batch}_retry.json';dest.write_text(json.dumps([a for a in original if a['audit_id'] in ids],indent=2,ensure_ascii=False));queue.append({'batch':batch,'input_path':str(dest),'audit_ids':ids,'large':r.get('large',False),'attempt':2})
 (B/'retry_queue.json').write_text(json.dumps(queue,indent=2));print({'retries_ready':len(queue)})
