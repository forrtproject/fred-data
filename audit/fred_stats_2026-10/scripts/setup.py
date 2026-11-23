import openpyxl,json,csv,hashlib,re,datetime,collections,random
from pathlib import Path
B=Path(__file__).resolve().parents[1]
if (B/'run_manifest.json').exists():
 import sys
 old=json.loads((B/'run_manifest.json').read_text())
 actual=hashlib.sha256(Path('/home/lukas/audit_inputs_2026-10/FReD_b48a7d6.xlsx').read_bytes()).hexdigest()
 assert actual==old['input_sha256'], 'Frozen input hash changed'
 print('Manifest already exists; preserving original deadlines and checkpoints.');sys.exit(0)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(v):return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)','',str(v or '').strip().lower()).rstrip('/')
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str))
w=openpyxl.load_workbook('/home/lukas/audit_inputs_2026-10/FReD_b48a7d6.xlsx',read_only=True);s=w.active;s.reset_dimensions();it=iter(s.values);cols=next(it);rows=[dict(zip(cols,x)) for x in it]; assert len(rows)==2164
assert set(['effect_id','n_o','n_r','es_value_o','es_value_r','pval_value_o','pval_value_r','reported_success'])<=set(cols)
groups=collections.defaultdict(list)
for i,r in enumerate(rows,1):
 r['input_row_index']=i;k=norm(r['doi_r']) or str(r['url_r'] or '').strip() or str(r['ref_r'] or '').strip();r['work_key']=k;r['file_key']=hashlib.sha256(k.encode()).hexdigest()[:16];groups[k].append(r)
with (B/'manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
 z=csv.DictWriter(f,fieldnames=['input_row_index','effect_id','work_key','file_key']);z.writeheader();z.writerows({k:r[k] for k in z.fieldnames} for r in rows)
now=datetime.datetime.now(datetime.timezone.utc)
m={'launch_time':now.isoformat(),'deadlines':{k:(now+datetime.timedelta(hours=h)).isoformat() for k,h in [('extraction',8),('adjudication',9.5),('finish',10)]},'input_sha256':digest('/home/lukas/audit_inputs_2026-10/FReD_b48a7d6.xlsx'),'codebook_sha256':digest('pipelines/fred/fred_codebook.xlsx'),'output_initial_sha256':digest('output/FReD.xlsx'),'effect_count':len(rows),'work_count':len(groups),'missing_doi_r':sum(not norm(r['doi_r']) for r in rows),'large_groups':{k:len(v) for k,v in groups.items() if len(v)>30},'seed':1}
dump(B/'run_manifest.json',m)
# Shipped values are parent-only. Children explicitly forbidden to open this file.
dump(B/'parent_rows.json',rows)
for j,start in enumerate(range(0,len(rows),200)):
 dump(B/'sanitisation'/f'raw_{j:02}.json',[{'effect_id':r['effect_id'],'description':r['description']} for r in rows[start:start+200]])
(B/'run_log.md').write_text(f'# FReD statistics audit run log\n\nLaunch: {now.isoformat()}. Deadlines UTC: {json.dumps(m["deadlines"])}.\n\n- Read full brief, repository guidelines and codebook. Worktree branch verified. No pipeline or data edits authorised.\n- Workbook dimensions reset; asserted 2,164 effects and required columns. Grouped into {len(groups)} works; {m["missing_doi_r"]} rows lack replication DOI.\n- Preserve cell strings and number formats where available; XLSX display/storage may already have lost precision as printed in papers.\n- Sanitiser children receive only effect_id and description; extraction children receive only prepared blind inputs.\n- Text is active processing on SSD; completed bulky text will be archived to verified cloud mount. No text committed.\n- Launch uses three sanitiser children, then pilots; ramp ceiling gradually to ten in first half hour.\n')
print(json.dumps(m,indent=2))
