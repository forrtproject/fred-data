import json,re,hashlib,csv,random,subprocess,concurrent.futures
from pathlib import Path
B=Path(__file__).resolve().parents[1]
def key(doi):return hashlib.sha256(str(doi).strip().lower().encode()).hexdigest()[:24]
def locators(v):
 s=str(v or ''); urls=re.findall(r'https?://[^\s<>"\]\)]+',s)
 # A primary URL may encode a fragment but its text is retained; all result prose discarded.
 refs=re.findall(r'\b(?:pp?\.?|pages?|tables?|fig(?:ure)?s?\.?)\s*\d+[A-Za-z]?(?:\s*[-–,]\s*\d+[A-Za-z]?)*',s,re.I)
 return '; '.join(dict.fromkeys(refs+urls))
def cache(doi):
 if not doi:return None
 dest=B/'texts'/f'{key(doi)}.txt'
 if dest.exists():return str(dest)
 try:
  p=subprocess.run(['/home/lukas/audit_inputs_2026-10/tools/cached_text.sh',str(doi).strip().lower(),str(dest)],capture_output=True,timeout=30)
  return str(dest) if p.returncode==0 else None
 except subprocess.TimeoutExpired:return None

def main():
 rows=json.loads((B/'parent_rows.json').read_text());clean={}
 for p in sorted((B/'sanitisation').glob('clean_*.json')):
  for x in json.loads(p.read_text()):
   assert x['effect_id'] not in clean;clean[x['effect_id']]=x
 flags={int(r['input_row_index']):int(r['flag_count']) for r in csv.DictReader((B/'consistency.csv').open(encoding='utf-8-sig'))}
 groups={}
 for r in rows:groups.setdefault(r['work_key'],[]).append(r)
 # Only complete sanitised slices can enter the queue. Preserve grouping across sanitiser boundaries.
 eligible=[]
 for k,rr in groups.items():
  for start in range(0,len(rr),15):
   chunk=rr[start:start+15]
   if all(r['effect_id'] in clean for r in chunk):eligible.append((k,rr,chunk,start))
 random.Random(1).shuffle(eligible)
 eligible.sort(key=lambda x:(not any(flags[r['input_row_index']] for r in x[2]),len(x[1])>30))
 todos=[]
 for k,rr,chunk,start in eligible:
  batch=f'{rr[0]["file_key"]}_{start:03}';path=B/'inputs'/f'{batch}.json'
  data=[]
  for r in chunk:
   z={a:r[a] for a in ['ref_o','doi_o','study_o','ref_r','doi_r','url_r','study_r','es_type_o','es_type_r']}
   z.update(audit_id=r['input_row_index'],description=clean[r['effect_id']]['description'],locators_o=locators(r['es_repr_o']),locators_r=locators(r['es_repr_r']),text_paths={})
   for side in ['o','r']:
    p=B/'texts'/f'{key(r["doi_"+side])}.txt'
    if p.exists():z['text_paths'][side]=str(p)
   data.append(z)
  path.write_text(json.dumps(data,ensure_ascii=False,indent=2))
  todos.append({'batch':batch,'input_path':str(path),'audit_ids':[r['input_row_index'] for r in chunk],'large':len(rr)>30,'work_key':k,'priority':sum(flags[r['input_row_index']] for r in chunk)})
 (B/'queue.json').write_text(json.dumps(todos,indent=2));print({'clean':len(clean),'batches_ready':len(todos)})
if __name__=='__main__':main()
