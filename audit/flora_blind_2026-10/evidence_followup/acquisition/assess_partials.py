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
 import uuid
 tmp=BASE/('partial_assessment.assessor.'+uuid.uuid4().hex+'.tmp');tmp.write_text(''.join(json.dumps(a,ensure_ascii=False)+'\n' for a in existing));os.replace(tmp,fp)
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
   if m: print('ABSTRACT REGION',t[max(0,m.start()-120):m.start()+850])

def finalize():
 from collections import Counter
 fp=BASE/'partial_assessment.jsonl'
 rows=[json.loads(l) for l in fp.read_text().splitlines()]
 assert len(rows)==len(WORKS)==201
 for i,(w,r) in enumerate(zip(WORKS,rows)):
  assert w['file_key']==r['file_key']
  c=next(c for c in w['candidates'] if c['text_filepath']==r['selected_source_path'])
  s=read(c)
  metadata_only=all(len(re.sub(r'\s+',' ',read(x)))<700 for x in w['candidates']) and any('api.elsevier.com' in read(x) for x in w['candidates'])
  if metadata_only or i in (155,176):
   r['disposition']='landing_or_reference_page'
   r['completeness_source_scope_reason']='Exact requested title/DOI present in Elsevier bibliographic metadata only; saved text inspected in full. No abstract or primary body. Other listed alternatives, where supplied, are redirect, bot challenge or unloaded application shells.'
  if i==67:r['completeness_source_scope_reason']='MUSE page explicitly says URL Has Changed, then supplies new URL and general publisher mission/navigation/footer. No requested primary abstract or body loaded; new URL was not acquired.'
  if i==161:r['completeness_source_scope_reason']=r['completeness_source_scope_reason'].replace(', one reference,', ',')
  # Choose contiguous original-text excerpts; whitespace is never repaired in artifacts.
  pat=r'\s+'.join(re.escape(x) for x in w['title_r'].split())
  matches=list(re.finditer(pat,s,re.I))
  if matches:
   authors=json.loads(w['author_r']); families=[x.get('family','').lower() for x in authors if x.get('family')]
   def score(m):
    ctx=s[m.start():m.start()+1300].lower()
    return sum(2 for f in families if f in ctx)+(3 if 'published online' in ctx else 0)-(3 if '| cambridge core' in ctx[:len(w['title_r'])+100] else 0)
   m=max(matches,key=score);r['identity_evidence_excerpt']=s[m.start():m.start()+600]
  if i==25:
   at=s.find('Replication of CD58');r['identity_evidence_excerpt']=s[at:at+600]
  if i==115:
   at=s.find('Sweet delusion.',s.find('Research report'));r['identity_evidence_excerpt']=s[at:at+600]
  if i in (76,141):
   ms=list(re.finditer(r'(?im)^\s*Abstract\s*\n',s))
   for m in ms:
    after=s[m.end():m.end()+200]
    if re.match(r'\s*Background',after,re.I):r['coherent_primary_body_evidence_excerpt']=s[m.start():m.start()+600];break
  if i==166:
   at=s.find('Following differential fear conditioning');r['coherent_primary_body_evidence_excerpt']=s[at:at+600]
  r['source_sha256']=hashlib.sha256((ROOT/c['text_filepath']).read_bytes()).hexdigest()
  r['binary_sha256']=hashlib.sha256((ROOT/c['filepath']).read_bytes()).hexdigest()
  r['sha256']=r['binary_sha256']
  r['sha256_path']=c['filepath']
  r['source_path_base']=str(ROOT)
  r['identity_status']='Unresolved concern explicitly retained in completeness_source_scope_reason where applicable; disposition is source-scope assessment only.'
  r['inspection_method']='Each listed saved extracted source checked at first/middle/end and relevant abstract/body boundary; identical extracted variants compared. Short application/error/metadata shells read in full. Promising manuscript/PDF sources checked additionally across front identity, section/body context and ending. Raw files hashed; XML structure and mismatched image signature checked; image candidate visually inspected. No acquisition or outcome coding.'
  for z,x in zip(r['inspected_sources'],w['candidates']):
   txt=read(x);assert z['sha256']==hashlib.sha256((ROOT/x['filepath']).read_bytes()).hexdigest()
   assert z['sha256']==x['sha256']
   z['text_characters']=len(txt)
   z.pop('sampled_text_ranges',None)
   z['samples_checked']='First/middle/end and relevant boundaries; large-source displays collapsed whitespace for viewing only, with verbatim original excerpts retained in output; short shells checked completely.'
   z['inspection_scope']='Saved text samples plus relevant boundaries; short shells complete; see work reason for substantive source-scope finding.'
  for k in ['identity_evidence_excerpt','coherent_primary_body_evidence_excerpt']:
   assert len(r[k])<=600
   assert r[k] in s or r[k]==''
  assert r['candidate_paths_actually_inspected']==[p for x in w['candidates'] for p in [x['filepath'],x['text_filepath']]]
 import uuid
 tmp=BASE/('partial_assessment.finalize.'+uuid.uuid4().hex+'.tmp')
 tmp.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows));os.replace(tmp,fp)
 counts={k:Counter(r['disposition'] for r in rows).get(k,0) for k in ['full_text_candidate','primary_abstract','landing_or_reference_page','wrong_identity','insufficient_source']}
 (BASE/'partial_progress.json').write_text(json.dumps({'total':201,'assessed':201,'remaining':0,'counts':counts,'status':'complete','candidate_sources_inspected':sum(len(w['candidates']) for w in WORKS),'integrity_checks':'201 unique file keys; all 391 original source hashes match supplied SHA256; selected text and binary hashes independently calculated; excerpts are exact source substrings <=600 characters; source-path coverage checked.'},indent=2)+'\n')
 print(json.dumps(counts));print('validated',len(rows),'works')
