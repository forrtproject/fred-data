import json,datetime,csv
from pathlib import Path
B=Path(__file__).resolve().parents[1]
state=B/'logged_skips.json';seen=set(json.loads(state.read_text())) if state.exists() else set();new=[]
for path in (B/'extractions').glob('*.json'):
 try:x=json.loads(path.read_text())
 except:continue
 for side in ['original','replication']:
  a=x[side]
  if a['status']=='done':continue
  key=f'{x["audit_id"]}:{side}:{a["status"]}'
  if key in seen:continue
  seen.add(key);new.append(f'- Skip/unfinished row {x["audit_id"]} {side}: {a["status"]}. '+a['target_description'].replace('\n',' '))
if (B/'results.csv').exists():
 for row in csv.DictReader((B/'results.csv').read_text(encoding='utf-8-sig').splitlines()):
  aid=int(row['input_row_index'])
  if not (B/'extractions'/f'{aid}.json').exists():continue
  fields=[]
  for field in ['n_o','es_value_o','pval_value_o','n_r','es_value_r','pval_value_r','reported_success']:
   verdict=row[field+'_final_verdict'];comparison=row[field+'_comparison']
   if verdict not in ['unverified','not_comparable']:continue
   key=f'{aid}:{field}:{verdict}:{comparison}'
   if key not in seen:seen.add(key);fields.append(f'{field} ({comparison})')
  if fields:new.append(f'- Partial/unevaluable row {aid}: '+', '.join(fields)+f'. Evidence/reasons: extractions/{aid}.json and results.csv.')
if new:
 with (B/'run_log.md').open('a') as f:f.write('\nPaper-side skips/checkpoints logged '+datetime.datetime.now(datetime.timezone.utc).isoformat()+':\n\n'+'\n'.join(new)+'\n')
state.write_text(json.dumps(sorted(seen),indent=2));print({'new_skip_log_records':len(new)})
