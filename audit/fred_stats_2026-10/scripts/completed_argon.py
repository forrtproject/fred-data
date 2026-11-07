"""Identify fully validated, stable final replies whose CLI can be closed."""
import hashlib,json,time
from pathlib import Path
B=Path(__file__).resolve().parents[1]
def ready_reply(root,record,now=None):
 now=time.time() if now is None else now
 key=record['key'];raw=root/'adjudications'/f'raw_{key}.txt';validation=root/'adjudications'/f'validation_{key}.json'
 try:
  v=json.loads(validation.read_text())
  return (v.get('status')=='valid' and v.get('parse_mode')=='complete_json'
   and v.get('items')==len(record['items']) and now-raw.stat().st_mtime>=30
   and v.get('raw_sha256')==hashlib.sha256(raw.read_bytes()).hexdigest())
 except (OSError,ValueError,KeyError):return False
if __name__=='__main__':
 state=json.loads((B/'adjudication_status.json').read_text());latest={}
 for line in (B/'adjudication_tasks.jsonl').read_text().splitlines():
  if line:
   r=json.loads(line);latest[r['key']]=r
 print(json.dumps([r['key'] for r in latest.values() if not state.get(r['key'],{}).get('terminal') and ready_reply(B,r)]))
