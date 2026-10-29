import json,sys
from pathlib import Path
B=Path(__file__).resolve().parents[1]
terminal={'completed','failed','cancelled','interrupted'}
if len(sys.argv)>1 and sys.argv[1]=='merge':
 state=json.loads((B/'task_status.json').read_text()) if (B/'task_status.json').exists() else {};state.update(json.loads((B/'task_status_updates.json').read_text()));(B/'task_status.json').write_text(json.dumps(state,indent=2));sys.exit(0)
if len(sys.argv)>1 and sys.argv[1]=='agy':
 state=json.loads((B/'adjudication_status.json').read_text()) if (B/'adjudication_status.json').exists() else {};latest={}
 for line in (B/'adjudication_tasks.jsonl').read_text().splitlines():
  if line:
   r=json.loads(line);latest[r['key']]=r
 out=[]
 for key,r in latest.items():
  out.append({'key':key,'attempt':r['attempt']} if state.get(key,{}).get('terminal') else r)
 (B/'agy_control.json').write_text(json.dumps({'records':out,'states':state},separators=(',',':')));sys.exit(0)
records=[json.loads(x) for x in (B/'tasks.jsonl').read_text().splitlines() if x];state=json.loads((B/'task_status.json').read_text()) if (B/'task_status.json').exists() else {};out=[];active={}
for r in records:
 st=state.get(r['taskId'],{})
 if st.get('status') in terminal:out.append({k:r[k] for k in ['kind','batch']}|{'terminal':True})
 else:
  out.append({k:r[k] for k in ['kind','batch','attempt','audit_ids','large','started_at','taskId'] if k in r});active[r['taskId']]=st
(B/'control.json').write_text(json.dumps({'records':out,'status':active},separators=(',',':')))
