#!/usr/bin/env python3
"""Stage explicit audit artifacts only, rejecting source-body/overlong-quote leaks."""
import pathlib,json,re,subprocess
import controller
R=controller.R
bad=[]
def check(v,path):
 if isinstance(v,dict):
  for k,x in v.items():
   if isinstance(x,str) and len(x)>6000 and (k.endswith('_quote') or k=='quote' or k in ['raw_text','full_text','article_text','document_text','source_text','body','html','content']):bad.append(path+':'+k)
   check(x,path)
 elif isinstance(v,list):
  for x in v:check(x,path)
paths=[pathlib.Path('.gitignore')]+[p for p in R.iterdir() if p.is_file()]+list((R/'scripts').glob('*.py'))+list((R/'scripts').glob('*.js'))+list((R/'batches').glob('*.json'))+list((R/'batches').glob('*.txt'))+list((R/'adjudications').glob('*.json'))+list((R/'quarantine').glob('*.json'))+list((R/'argon').glob('*.prompt.txt'))+list((R/'argon').glob('*.state.json'))+list((R/'argon').glob('*.input.json'))
followup=R/'evidence_followup'
if followup.exists():
 for name in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','--',str(followup)],text=True).splitlines():
  p=pathlib.Path(name)
  if not p.exists():continue
  if '/private/' in p.as_posix() or '/snapshot/' in p.as_posix():raise SystemExit('Private source/snapshot in public staging set: '+str(p))
  raw=p.read_text(errors='replace')
  if re.search(r'[?&](api_key|access_token|x-amz-signature|signature|token)=',raw,re.I):raise SystemExit('Ephemeral credential/query token in public metadata: '+str(p))
  if p.suffix=='.jsonl':
   for line in raw.splitlines():
    if line.strip():check(json.loads(line),str(p))
  paths.append(p)
skipped=[]
for p in (R/'codings').glob('*.json'):
 if not re.fullmatch('[0-9a-f]{16}',p.stem):continue
 if controller.validate(p):paths.append(p)
 else:skipped.append(p.name)
for p in paths:
 if p.suffix=='.json':
  try:check(json.loads(p.read_text()),str(p))
  except ValueError:raise SystemExit('Malformed audit JSON; not staged: '+str(p))
if bad:raise SystemExit('Source-body/overlong-quote preflight failed: '+', '.join(bad))
assert not subprocess.check_output(['git','ls-files',str(R/'texts')],text=True).strip()
subprocess.run(['git','add','--',*[str(p) for p in paths]],check=True)
print(json.dumps({'staged_paths':len(paths),'invalid_codings_not_staged':skipped,'full_text_paths_staged':0}))
