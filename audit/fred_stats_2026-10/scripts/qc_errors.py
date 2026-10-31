"""Read-only parent triage of adjudicated error proposals; never changes verdicts."""
import json,sys,subprocess
from pathlib import Path
from compare import comp,load_adjudications
B=Path(__file__).resolve().parents[1]
def main():
 rows=json.loads((B/'parent_rows.json').read_text());progress=json.loads((B/'progress.json').read_text());adjud=load_adjudications(B)
 for a in json.loads((B/'obvious_resolutions.json').read_text()):adjud[a['audit_id'],a['field']]=a
 unusual=[]
 for error in progress['confirmed_errors']:
  aid=error['audit_id'];f=error['field'];row=rows[aid-1];x=json.loads((B/'extractions'/f'{aid}.json').read_text());side='original' if f.endswith('_o') else 'replication'
  blind=x['reported_success'] if f=='reported_success' else x[side]['n' if f.startswith('n_') else 'p' if f.startswith('pval') else 'es'];a=adjud.get((aid,f),{})
  value={**blind,'value':error['correction']}
  if f.startswith('es'):value['test_statistic']=error['correction'];value['metric']=a.get('correct_metric') or blind.get('metric')
  if f.startswith('pval'):value['bound']=a.get('correct_bound') or blind.get('bound')
  check=comp(f,error['shipped'],value,row)
  if check in ['agree','identical','compatible','not_comparable']:unusual.append({**error,'correction_comparison':check})
 print(json.dumps({'confirmed_errors':len(progress['confirmed_errors']),'needs_parent_review':unusual},indent=2))
 if '--new-success' in sys.argv:
  result=subprocess.run(['git','show','HEAD:'+str(B.relative_to(B.parents[1])/'progress.json')],capture_output=True,text=True,check=True);old=json.loads(result.stdout);known={(a['audit_id'],a['field']) for a in old['confirmed_errors']}
  for e in progress['confirmed_errors']:
   if e['field']=='reported_success' and (e['audit_id'],e['field']) not in known:print(json.dumps({**e,'quote':adjud[e['audit_id'],e['field']]['quote']},ensure_ascii=False))
if __name__=='__main__':main()
