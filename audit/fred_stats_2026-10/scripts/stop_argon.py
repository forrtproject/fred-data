import json,sys,hashlib,re
from pathlib import Path
import psutil
B=Path(__file__).resolve().parents[1]
def prompt_key(args):
 if '--add-dir' not in args or str(B/'texts') not in args or '-p' not in args:return None
 try:
  prompt=args[args.index('-p')+1]
  if prompt.startswith('FRED_AUDIT_PROMPT_FILE: '):
   path=Path(prompt.splitlines()[0].split(': ',1)[1])
   if not path.resolve().is_relative_to((B/'adjudications').resolve()) or not re.fullmatch(r'prompt_[0-9a-f]{16}\.txt',path.name):return None
   prompt=path.read_text()
  start=prompt.index('\n\n[')+2;payload=json.JSONDecoder().raw_decode(prompt[start:])[0]
  return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:16]
 except (OSError,ValueError,IndexError,json.JSONDecodeError):return None
def stop(key,pid=None):
 owned=[]
 for proc in psutil.process_iter(['pid','cmdline']):
  if (pid is None or proc.pid==pid) and prompt_key(proc.info['cmdline'] or [])==key:
   try:owned.append(proc);proc.terminate()
   except psutil.NoSuchProcess:pass
 _,alive=psutil.wait_procs(owned,timeout=5)
 for proc in alive:proc.kill()
 _,alive=psutil.wait_procs(alive,timeout=5)
 if alive:raise RuntimeError('Owned audit CLI did not exit; do not release its slot')
 return [proc.pid for proc in owned]
if __name__=='__main__':print(json.dumps({'key':sys.argv[1],'verified_stopped_pids':stop(sys.argv[1],int(sys.argv[2]) if len(sys.argv)>2 else None)}))
