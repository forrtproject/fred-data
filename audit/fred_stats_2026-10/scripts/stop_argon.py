import json,sys
from pathlib import Path
import psutil
B=Path(__file__).resolve().parents[1];key=sys.argv[1];prompt=(B/'adjudications'/f'prompt_{key}.txt').read_text().rstrip('\n');pids=[];owned=[]
for proc in psutil.process_iter(['pid','cmdline']):
 args=proc.info['cmdline'] or []
 if '--add-dir' not in args or str(B/'texts') not in args or '-p' not in args:continue
 try:
  if args[args.index('-p')+1]==prompt:pids.append(proc.pid);owned.append(proc);proc.terminate()
 except (ValueError,IndexError,psutil.NoSuchProcess):pass
_,alive=psutil.wait_procs(owned,timeout=5)
for proc in alive:proc.kill()
_,alive=psutil.wait_procs(alive,timeout=5)
if alive:raise RuntimeError('Exact audit CLI processes did not exit; do not release their slots')
print(json.dumps({'key':key,'terminated_exact_prompt_pids':pids}))
