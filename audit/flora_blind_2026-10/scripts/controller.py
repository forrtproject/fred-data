import pathlib,json,sys,datetime,subprocess,hashlib,os
R=pathlib.Path(__file__).resolve().parents[1]
NOW=lambda:datetime.datetime.now(datetime.timezone.utc)
def read(p,default=None):
 try:return json.loads(p.read_text())
 except (ValueError,FileNotFoundError):return default

def event(x):
 with (R/'tasks.jsonl').open('a') as f:f.write(json.dumps({'at':NOW().isoformat(),**x})+'\n')
def state():
 s={}
 if (R/'tasks.jsonl').exists():
  for l in (R/'tasks.jsonl').read_text().splitlines():
   e=json.loads(l)
   if 'taskId'in e:s[e['taskId']]={**s.get(e['taskId'],{}),**e}
 return s

def validate(p):
 import jsonschema
 c=read(p)
 if not c:return False
 try:
  if c.get('status') in ['no_text','timeout','error']:
   return isinstance(c.get('work_key'),str) and c['status'] in ['no_text','timeout','error']
  jsonschema.validate(c,read(R/'coding_schema.json'))
  text=R/'texts'/f'{p.stem}.txt'
  return c['status']=='done' and text.exists() and hashlib.sha256(text.read_bytes()).hexdigest()==c['text_sha256']
 except (ValueError,KeyError,jsonschema.ValidationError):return False

def plan():
 m=read(R/'run_manifest.json'); age=(NOW()-datetime.datetime.fromisoformat(m['launch_time'])).total_seconds()
 s=state();active=[e for e in s.values() if e.get('status') in ['running','queued','waiting']]
 limit=3 if age<600 else 5 if age<1200 else 8 if age<1800 else 10
 return {'age_seconds':age,'limit':limit,'active':active,'coding_open':NOW()<datetime.datetime.fromisoformat(m['deadlines']['coding']),'finish_due':NOW()>=datetime.datetime.fromisoformat(m['deadlines']['finish'])}

def prepare():
 pl=plan()
 if not pl['coding_open'] or len(pl['active'])>=pl['limit']:return None
 q=read(R/'work_queue.json');s=state();busy={k for e in pl['active'] for k in e.get('files',[])}
 attempts={}
 for e in s.values():
  for k in e.get('files',[]):attempts[k]=attempts.get(k,0)+1
 def pending(w):
  k=w['file_key'];p=R/'codings'/f'{k}.json';c=read(p,{})
  if k in busy or (validate(p) and c.get('status') in ['done','no_text']):return False
  return attempts.get(k,0)<2
 remaining=[w for w in q if pending(w)]
 if not remaining:return None
 # Reserve a continuously staffed large-project lane once pilot work is underway.
 large_busy=any(e.get('large') for e in pl['active'])
 large=[w for w in remaining if w['row_count']>8]
 chosen=large[:1] if pl['age_seconds']>=600 and large and not large_busy else remaining[:5]
 # No shipped row counts enter the sanitized task.
 n=len(list((R/'batches').glob('*.json')));bid=f'batch_{n:05d}'; payload=[]
 for w in chosen:
  k=w['file_key'];out=R/'texts'/f'{k}.txt'
  if not out.exists() and w['doi_r'].lower() not in ['','na']:
   tmp=out.with_suffix('.cache.tmp')
   try:
    p=subprocess.run(['/home/lukas/audit_inputs_2026-10/tools/cached_text.sh',w['doi_r'].lower(),str(tmp)],capture_output=True,timeout=15)
    if p.returncode==0 and tmp.exists() and tmp.stat().st_size:os.replace(tmp,out)
    elif tmp.exists():tmp.unlink()
   except subprocess.TimeoutExpired:pass
  entry={key:w[key] for key in ['file_key','work_key','doi_r','url_r','title_r','author_r','year_r','journal_r']}
  entry.update(text_path=str(out) if out.exists() else None,output_path=str(R/'codings'/f'{k}.json'),time_cap_seconds=480 if w['row_count']>1 else 180)
  payload.append(entry)
 schema=(R/'coding_schema.json').read_text();book=(R/'codebook.md').read_text()
 prompt='''You are a BLIND paper coding child. Your only task is to code the works below sequentially. Do not open flora.csv, FReD, the FLoRA/FORRT websites or any FORRT dataset. Do not search the repository. Do not read any parent brief, manifest, queue, tasks, results, report, comparison or other coder outputs. Do not delegate further. Do not stage, commit or push. Return only counts and output paths, never paper text. Only write the assigned output paths and their source text paths, plus uniquely named temporary files alongside them. No questions: decide and record uncertainty.

Acquisition route: parent-supplied cached text first; otherwise DOI landing page, Unpaywall, OpenAlex best_oa_location, PMC/Europe PMC, OSF API file listing (including DOCX), PsyArXiv/preprints; then download-paper skill open-access chain WITHOUT signed-in Chrome. Use title_r to verify paper identity and boundaries and authors before full-text coding. Abstracts, previews, supplements are not full text. Budget acquisition 90 seconds plus at most 30 seconds for one promising alternative, no repeated 403/challenge/unchanged miss. If unavailable, use OpenAlex/Crossref abstract and label abstract. No abstract => no_text. Entire ordinary work cap 180 seconds, complex cap 480 seconds including acquisition. On cap write timeout with whatever is known. Save extracted text (including references when full text) through a temp file and atomic rename to audit/flora_blind_2026-10/texts/<file_key>.txt. Record actual source URL, UTC retrieved_at, SHA256 of saved bytes, parser, evidence_level. Parent cached text is the first source: inspect its header for provenance, record cache helper as parser if otherwise unavailable.

Checkpoints: valid done is final, never overwrite it. no_text is final. timeout/error/malformed files get at most one retry (this task may be that retry). JSON output top level contains coding fields plus envelope fields; validate against the supplied schema for done, and require work_key/status for failure records (provenance may be null). Reproductions require BOTH axes and quote fields. Write one JSON per work via temp+atomic rename immediately upon finishing that work, not at batch end. Include elapsed_seconds, acquisition_seconds and skip_reason as extra fields. Code all originals independently, one per original paper, including large projects from primary project files where necessary; no shipped original list exists in this task.

CODEBOOK (verbatim):
'''+book+'\n\nSUCCESS SCHEMA:\n'+schema+'\n\nASSIGNED WORKS:\n'+json.dumps(payload,ensure_ascii=False,indent=2)
 (R/'batches'/f'{bid}.txt').write_text(prompt)
 info={'batch':bid,'files':[w['file_key'] for w in chosen],'large':chosen[0]['row_count']>8,'clientRequestId':'flora-'+bid+'-v1','prompt_path':str(R/'batches'/f'{bid}.txt')}
 (R/'batches'/f'{bid}.json').write_text(json.dumps(info,indent=2))
 return {**info,'task':prompt}

if __name__=='__main__':
 cmd=sys.argv[1]
 if cmd=='plan':print(json.dumps(plan()))
 elif cmd=='prepare':print(json.dumps(prepare()))
 elif cmd=='event':event(json.loads(sys.argv[2]))
 elif cmd=='validate':
  ps=list((R/'codings').glob('*.json'));print(json.dumps({'total':len(ps),'valid':sum(validate(p) for p in ps),'invalid':[p.name for p in ps if not validate(p)]}))
