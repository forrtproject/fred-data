import csv,json,hashlib,datetime,collections,random,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
INPUT=pathlib.Path('/home/lukas/audit_inputs_2026-10')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):
 s=s.strip().lower()
 if s in ('na',''):return ''
 for prefix in ('https://doi.org/','http://doi.org/','http://dx.doi.org/','https://dx.doi.org/','doi:'):
  if s.startswith(prefix):s=s[len(prefix):]
 return s.strip()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
rows=list(csv.DictReader((INPUT/'flora_b48a7d6.csv').open(encoding='utf-8-sig')))
works={};manifest=[]
for i,r in enumerate(rows):
 key=norm(r['doi_r']) or norm(r['url_r']) or '|'.join(norm(r[k]) for k in ['title_r','author_r','year_r'])
 if not key.strip('|'):key='unidentified_row:'+str(i)
 fk=hashlib.sha256(key.encode()).hexdigest()[:16]
 manifest.append({'input_row_index':i,'work_key':key,'file_key':fk})
 if key not in works:works[key]={'work_key':key,'file_key':fk,'row_count':0,**{k:r[k] for k in ['doi_r','url_r','title_r','author_r','year_r','journal_r']}}
 works[key]['row_count']+=1
with (ROOT/'manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(manifest[0]));w.writeheader();w.writerows(manifest)
if not (ROOT/'run_manifest.json').exists():
 now=datetime.datetime.now(datetime.timezone.utc)
 dump(ROOT/'run_manifest.json',{'launch_time':now.isoformat(),'deadlines':{k:(now+datetime.timedelta(hours=h)).isoformat() for k,h in [('coding',8),('adjudication',9.5),('finish',10)]},'input_hashes':{n:sha(INPUT/n) for n in ['flora_b48a7d6.csv','flora_blind_schema.json','flora_pilot_final_check.py']},'codebook_sha256':sha(INPUT/'flora_blind_codebook.md'),'output_flora_sha256':sha(pathlib.Path('output/flora.csv')),'seed':1,'index_base':0,'rows':len(rows),'works':len(works)})
ws=list(works.values());single=[w for w in ws if w['row_count']==1];random.Random(1).shuffle(single)
ordered=single+[w for w in ws if 1<w['row_count']<=8]+[w for w in ws if w['row_count']>8]
dump(ROOT/'work_queue.json',ordered)
schema=json.loads((INPUT/'flora_blind_schema.json').read_text())
schema['properties'].update({'work_key':{'type':'string'},'status':{'enum':['done','timeout','no_text','error']},'evidence_level':{'enum':['full_text','abstract',None]},**{k:{'type':['string','null']} for k in ['source_url','retrieved_at','text_sha256','parser']}})
schema['required']+=['work_key','status','evidence_level','source_url','retrieved_at','text_sha256','parser']
schema['properties']['targets']['items']['allOf']=[{'if':{'properties':{'outcome':{'const':''}}},'then':{'required':['outcome_computation','outcome_computational_quote','outcome_robustness','outcome_robustness_quote']}}]
dump(ROOT/'coding_schema.json',schema)
(ROOT/'codebook.md').write_bytes((INPUT/'flora_blind_codebook.md').read_bytes())
print('rows',len(rows),'works',len(works),'single',len(single),'large',sum(w['row_count']>8 for w in ws))
