import json,shutil,datetime
from pathlib import Path
B=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 queue=json.loads((B/'queue.json').read_text());records=[json.loads(s) for s in (B/'tasks.jsonl').read_text().splitlines() if s];statuses=json.loads((B/'task_status.json').read_text());latest={r['batch']:r for r in records if r['kind']=='extraction'};out=[]
 # Finish dispatching the first pass before revisiting cases with genuinely new locators.
 if all(a['batch'] in latest for a in queue):
  delta=B/'locator_enrichment_changes.json';changes={a['audit_id']:a for a in json.loads(delta.read_text())};revised_at=datetime.datetime.fromtimestamp(delta.stat().st_mtime,datetime.timezone.utc);archive=B/'before_locator_enrichment'
  for batch in queue:
   r=latest[batch['batch']]
   # Later first-pass tasks already received the enriched input, so it is not new evidence for them.
   if r.get('started_at') and datetime.datetime.fromisoformat(r['started_at'].replace('Z','+00:00'))>=revised_at:continue
   new_batch=batch['batch']+'_loc2'
   if new_batch in latest or statuses.get(r['taskId'],{}).get('status') not in ['completed','failed','cancelled','interrupted']:continue
   ids=[]
   for aid in batch['audit_ids']:
    p=B/'extractions'/f'{aid}.json'
    if aid not in changes or not p.exists():continue
    x=json.loads(p.read_text())
    if not any(x['original' if s=='o' else 'replication']['status']=='locator_insufficient' for s in changes[aid]['sides']):continue
    ids.append(aid);archive.mkdir(exist_ok=True);dest=archive/f'{aid}.json'
    if not dest.exists():shutil.copyfile(p,dest)
   if not ids:continue
   original=json.loads(Path(batch['input_path']).read_text());dest=B/'inputs'/f'{new_batch}.json';dest.write_text(json.dumps([a for a in original if a['audit_id'] in ids],indent=2,ensure_ascii=False))
   out.append({'batch':new_batch,'input_path':str(dest),'audit_ids':ids,'large':batch['large'],'attempt':2,'enrichment':True})
 (B/'enrichment_queue.json').write_text(json.dumps(out,indent=2));print({'locator_revisit_batches':len(out),'effects':sum(len(a['audit_ids']) for a in out)})
