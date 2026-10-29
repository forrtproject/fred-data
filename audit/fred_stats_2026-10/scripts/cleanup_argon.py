import json,datetime
from pathlib import Path
import psutil
from stop_argon import prompt_key,stop
B=Path(__file__).resolve().parents[1]
state=json.loads((B/'adjudication_status.json').read_text());latest={}
for line in (B/'adjudication_tasks.jsonl').read_text().splitlines():
 r=json.loads(line);latest[r['key']]=r
stopped=[]
for proc in psutil.process_iter(['pid','cmdline','create_time']):
 key=prompt_key(proc.info['cmdline'] or [])
 if not key:continue
 if key not in latest:raise RuntimeError('Untracked own-audit CLI process; stop dispatch until reviewed')
 record=latest[key];started=datetime.datetime.fromisoformat(record['started_at'].replace('Z','+00:00')).timestamp()
 if state.get(key,{}).get('terminal') or proc.info['create_time']<started-10:
  stopped.extend(stop(key,proc.pid))
if stopped:
 with (B/'run_log.md').open('a') as file:file.write('\n- Verified removal of orphaned own-audit CLI processes: '+json.dumps(stopped)+'. Matched exact paper payload hash and audit text root; unrelated processes excluded.\n')
print(json.dumps({'verified_stopped_orphans':stopped}))
