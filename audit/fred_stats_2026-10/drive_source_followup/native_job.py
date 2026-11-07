"""Prepare and retain bounded neutral jobs for available native Codex delegation."""
import datetime,hashlib,json,sys
from pathlib import Path
F=Path(__file__).resolve().parent

def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
 mode=sys.argv[1];tasks=F/'validation_tasks.jsonl';history=[json.loads(l) for l in tasks.read_text().splitlines() if l];queue=json.loads((F/'validation_queue.json').read_text());statuses=json.loads((F/'validation_status.json').read_text())
 if mode=='next':
  used={r['batch'] for r in history};pending=[r for r in queue if r['batch'] not in used];job=[];rows=0
  for r in pending:
   if job and (rows+len(r['audit_ids'])>15 or len(job)>=8):continue
   job.append(r);rows+=len(r['audit_ids'])
   if rows>=15 or len(job)>=8:break
  key=hashlib.sha256(json.dumps([r['batch'] for r in job]).encode()).hexdigest()[:12];p=F/'jobs'/f'{key}.json';p.parent.mkdir(exist_ok=True);save(p,job);print(json.dumps({'job':str(p),'rows':rows,'batches':len(job),'key':key}))
 elif mode=='record':
  job=json.loads(Path(sys.argv[2]).read_text());task=sys.argv[3]
  for r in job:
   assert not any(x['batch']==r['batch'] for x in history),r['batch']
   record={**r,'taskId':task,'transport':'native_codex_subagent','model':'gpt-6.1-sol','reasoningEffort':'medium','status':'running','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()};tasks.open('a').write(json.dumps(record)+'\n');statuses[r['batch']]={'status':'running','taskId':task}
  save(F/'validation_status.json',statuses)
 elif mode=='complete':
  for r in history:
   if r['taskId']==sys.argv[2]:statuses[r['batch']]={'status':'completed','taskId':r['taskId']}
  save(F/'validation_status.json',statuses)
if __name__=='__main__':main()
