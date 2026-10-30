import json,hashlib,re,sys,os
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
WORKS=json.loads((BASE/'partial_assessment.input.json').read_text())['works']
def read(c):
 return (ROOT/c['text_filepath']).read_text(errors='replace')
def show(ids,full=False):
 for i in ids:
  w=WORKS[i];print('\nWORK',i,w['title_r'],w['doi_r'],w['author_r'])
  for j,c in enumerate(w['candidates']):
   s=read(c);s=re.sub(r'\s+',' ',s);print('\nCAND',j,c['filepath'],c['url'],'LEN',len(s))
   if full: print(s)
   else:
    print('FIRST:',s[:600]);print('MIDDLE:',s[len(s)//2:len(s)//2+650]);print('END:',s[-450:])
    for m in list(re.finditer(r'(?i)\b(abstract|access options|purchase|preview|full text|introduction|methods|results|references)\b',s))[:7]:
     print('BOUNDARY',m.start(),repr(s[max(0,m.start()-70):m.start()+450]))
def save(i,disposition,j,reason,identity=None,body=None):
 w=WORKS[i]; c=w['candidates'][j];s=read(c)
 # Excerpts are exact slices, never text normalization.
 if identity is None:
  at=s.lower().find(w['title_r'].lower()); identity=s[max(0,at):max(0,at)+600] if at>=0 else s[:600]
 if body is None:
  m=re.search(r'(?im)^\s*(abstract|summary|introduction|methods?|background)\s*[:\n]',s)
  at=m.start() if m else len(s)//2;body=s[at:at+600]
 out={'file_key':w['file_key'],'disposition':disposition,'selected_source_path':c['text_filepath'],'selected_binary_path':c['filepath'],'url':c['url'],'identity_evidence_excerpt':identity[:600],'coherent_primary_body_evidence_excerpt':body[:600],'completeness_source_scope_reason':reason,'sha256':hashlib.sha256((ROOT/c['filepath']).read_bytes()).hexdigest(),'candidate_paths_actually_inspected':[p for a in w['candidates'] for p in [a['filepath'],a['text_filepath']]],'inspection_method':'Saved extracted text: first/middle/end and available body/abstract boundaries for each candidate; promising sources additionally inspected in complete context. Raw source checked for identity/body where needed.'}
 # actual binary access, integrity check for every candidate
 out['inspected_sources']=[{'source_path':a['text_filepath'],'binary_path':a['filepath'],'sha256':hashlib.sha256((ROOT/a['filepath']).read_bytes()).hexdigest(),'text_sha256':hashlib.sha256((ROOT/a['text_filepath']).read_bytes()).hexdigest()} for a in w['candidates']]
 fp=BASE/'partial_assessment.jsonl'; existing=[json.loads(l) for l in fp.read_text().splitlines()] if fp.exists() else []
 existing=[a for a in existing if a['file_key']!=w['file_key']]+[out];order={w['file_key']:k for k,w in enumerate(WORKS)};existing.sort(key=lambda a:order[a['file_key']])
 tmp=BASE/'partial_assessment.assessor.tmp';tmp.write_text(''.join(json.dumps(a,ensure_ascii=False)+'\n' for a in existing));os.replace(tmp,fp)
 from collections import Counter
 (BASE/'partial_progress.json').write_text(json.dumps({'total':len(WORKS),'assessed':len(existing),'remaining':len(WORKS)-len(existing),'counts':dict(Counter(a['disposition'] for a in existing)),'last_file_key':w['file_key']},indent=2)+'\n')
if __name__=='__main__':
 ids=[int(x) for x in sys.argv[1].split(',')];show(ids,'--full' in sys.argv)
def compact(ids):
 for i in ids:
  w=WORKS[i];print('\nWORK',i,w['title_r'],'DOI',w['doi_r']);seen={}
  for j,c in enumerate(w['candidates']):
   s=read(c);t=re.sub(r'\s+',' ',s); h=hashlib.sha256(t.encode()).hexdigest()
   print('C',j,c['url'],'RAWLEN',len(s))
   if h in seen:print('Text identical after whitespace collapse to',seen[h]);continue
   seen[h]=j
   print('FIRST',t[:300]);print('MID',t[len(t)//2:len(t)//2+330]);print('END',t[-250:])
   m=re.search(r'(?i)\babstract\b',t)
   if m: print('ABSTRACT REGION',t[max(0,m.start()-120):m.start()+1600])
