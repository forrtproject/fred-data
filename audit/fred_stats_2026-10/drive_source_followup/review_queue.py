"""Finite, four-client Argon transport with exact-owned process groups and receipts."""
import asyncio,datetime,json,os,signal,sys
from pathlib import Path
F=Path(__file__).resolve().parent;B=F.parent

def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,x):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2)+'\n');t.replace(p)
async def main():
 snapshot=Path(sys.argv[1]);queue=json.loads(snapshot.read_text());history=[json.loads(l) for l in (F/'adjudication_tasks.jsonl').read_text().splitlines() if l];used={r['key'] for r in history};queue=[r for r in queue if r['key'] not in used];semaphore=asyncio.Semaphore(min(4,max(1,int(os.environ.get('FRED_ARGON_CLIENTS','2')))));statuses={};stop_event=asyncio.Event();failures=0;save(F/(snapshot.stem+'_status.json'),statuses);save(F/'review_round_status.json',statuses)
 async def one(r):
  async with semaphore:
   nonlocal failures
   if stop_event.is_set():return
   key=r['key'];out=Path(r['output']);prompt=Path(r['prompt']).read_text();record={**r,'started_at':stamp(),'model':'Gemini 4 Argon (High)','status':'running','session_id':None,'transport':'finite_owned_CLI'}
   with out.open('w') as f:
    proc=await asyncio.create_subprocess_exec('agy','-p',prompt,'--model','Gemini 4 Argon (High)','--sandbox',*(['--dangerously-skip-permissions'] if r.get('allow_read_commands') else []),'--add-dir',str(B/'texts'),'--add-dir',str((B/'texts').resolve()),'--add-dir','/home/lukas/work/fred-mac-recovery-20261030','--print-timeout','10m',stdout=f,stderr=asyncio.subprocess.STDOUT,start_new_session=True)
    record.update(pid=proc.pid,owned_process_group=proc.pid)
    for p in [F/'adjudication_tasks.jsonl',B/'adjudication_tasks.jsonl']:
     with p.open('a') as h:h.write(json.dumps(record)+'\n')
    statuses[key]={'status':'running','pid':proc.pid,'started_at':record['started_at']};save(F/(snapshot.stem+'_status.json'),statuses);save(F/'review_round_status.json',statuses);print('started',key,len(r.get('items',[])),flush=True)
    try:await asyncio.wait_for(proc.wait(),720)
    except asyncio.TimeoutError:
     assert os.getpgid(proc.pid)==proc.pid
     os.killpg(proc.pid,signal.SIGTERM)
     try:await asyncio.wait_for(proc.wait(),5)
     except asyncio.TimeoutError:os.killpg(proc.pid,signal.SIGKILL);await proc.wait()
     statuses[key]={'status':'timeout','exit_code':proc.returncode,'terminal':True,'stopped_at':stamp(),'exact_owned_process_group':proc.pid}
    else:statuses[key]={'status':'transport_complete' if proc.returncode==0 else 'transport_failed','exit_code':proc.returncode,'terminal':True,'stopped_at':stamp()}
   try:
    sys.path.insert(0,str(B/'scripts'));from validate_adjudication import parse_response
    data,mode=parse_response(out.read_text());expected={(x['audit_id'],x['field']) for x in r['items']};actual={(x['audit_id'],x['field']) for x in data}
    candidate=mode=='complete_json' and len(data)==len(r['items']) and expected==actual
   except (Exception,):candidate=False
   statuses[key]['complete_reply_candidate']=candidate
   failures=0 if candidate else failures+1
   if failures>=2:stop_event.set();print('STOP: two consecutive infrastructure/incomplete replies',flush=True)
   save(F/(snapshot.stem+'_status.json'),statuses);save(F/'review_round_status.json',statuses);print('finished',key,statuses[key]['status'],'complete_reply',candidate,flush=True)
 await asyncio.gather(*(one(r) for r in queue));print('finite round complete',len(queue),flush=True)
if __name__=='__main__':asyncio.run(main())
