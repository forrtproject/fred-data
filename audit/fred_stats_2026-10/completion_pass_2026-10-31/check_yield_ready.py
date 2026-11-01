"""Fail closed before handing off: cached 'running' labels do not establish liveness."""
import argparse,datetime,hashlib,json,subprocess,sys
from pathlib import Path
from concurrency_limits import limits,review_launch_paused,recorded_quota_failure
F=Path(__file__).resolve().parent;B=F.parent
TERMINAL={'completed','failed','cancelled','interrupted'}
def read(path,default=None):return json.loads(path.read_text()) if path.exists() else default
def scientific_fingerprint():
 paths=[B/name for name in ['parent_rows.json','target_overrides.json','adjudication_holds.json','metric_equivalences.json','obvious_resolutions.json','adjudication_exhausted.json','source_provenance.json','scripts/compare.py']]
 validated=sorted((B/'adjudications').glob('validated_*.json'))
 paths+=sorted((B/'extractions').glob('*.json'))+validated
 fingerprints={str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.exists()}
 # Comparison precedence consults task history only for existing validated files.
 # Dispatching a future review creates no scientific decision. Once its validated
 # file appears, both its evidence and its full relevant history enter the hash.
 keys={p.stem.removeprefix('validated_') for p in validated};history=B/'adjudication_tasks.jsonl'
 relevant=[json.loads(line) for line in history.read_text().splitlines() if line.strip()] if history.exists() else []
 relevant=[entry for entry in relevant if entry.get('key') in keys]
 fingerprints['validated_adjudication_task_history']=hashlib.sha256(json.dumps(relevant,sort_keys=True).encode()).hexdigest()
 return hashlib.sha256(json.dumps(fingerprints,sort_keys=True).encode()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--refresh-export',action='store_true');args=parser.parse_args()
 if args.refresh_export:
  before=scientific_fingerprint()
  subprocess.run([sys.executable,str(B/'scripts/compare.py')],check=True)
  assert before==scientific_fingerprint(),'Scientific inputs changed during export; retry integration/export serially'
  subprocess.run([sys.executable,str(F/'check_preservation.py')],check=True)
  preserved=read(F/'preservation_check.json');assert not preserved['changed_protected_fields'] and not preserved['unscoped_gains']
  (F/'export_fingerprint.json').write_text(json.dumps({'scientific_inputs_sha256':before,'exported_at':read(B/'progress.json')['updated_at'],'results_sha256':hashlib.sha256((B/'results.csv').read_bytes()).hexdigest()},indent=2)+'\n');return
 now=datetime.datetime.now(datetime.timezone.utc);problems=[];active={'tasks':0,'reviews':0}
 for folder,pattern in [('tasks','*.json'),('reviews','task_*.json')]:
  for path in (F/folder).glob(pattern):
   task=read(path)
   if task.get('status') in ['failed','cancelled','interrupted'] and not task.get('failure_disposition_recorded'):problems.append('Record terminal failure disposition: '+path.name)
   if task.get('hasPendingChildRuns'):problems.append('Resolve unexpected nested child work: '+path.name)
   if task.get('status') not in TERMINAL and task.get('taskId'):
    checked=task.get('last_checked_at') or task.get('started_at');age=(now-datetime.datetime.fromisoformat(checked.replace('Z','+00:00'))).total_seconds() if checked else 999999
    if age>30:problems.append('Refresh stale live-task status: '+path.name)
    active[folder]+=1
   elif folder=='reviews' and task.get('status')=='completed' and not (F/'reviews'/path.name.replace('task_','validated_',1)).exists():
    answer=F/'reviews'/path.name.replace('task_','answer_',1)
    if not recorded_quota_failure(task,answer.exists()):problems.append('Validate completed review: '+path.name)
 queue=read(F/'work_queue.json');collected=read(F/'collected.json',{});queued=0
 for group in queue:
  task=read(F/'tasks'/f"{group['key']}.json",{})
  if not task.get('taskId'):queued+=1;continue
  if task.get('status')=='completed':
   for record in read(Path(group['input'])):
    output=Path(group['output'])/f"{record['audit_id']}.json";saved=collected.get(group['key']+':'+str(record['audit_id']),{})
    if not output.exists() or saved.get('output_sha256')!=hashlib.sha256(output.read_bytes()).hexdigest():problems.append('Collect completed source: '+group['key']);break
 cap=limits();free=cap['max_combined_children']-sum(active.values())
 if free<0:problems.append('Combined child limit exceeded')
 if queued and active['tasks']<cap['source_slots'] and free>0:problems.append('Dispatch queued sources into available slots')
 review_queued=sum(not (F/'reviews'/f"task_{g['key']}_v1.json").exists() for g in read(F/'review_queue.json',[]))
 ordinary_live=sum(read(path).get('taskId') is not None and read(path).get('status') not in TERMINAL for path in (F/'reviews').glob('task_*_v1.json'))
 if review_queued and ordinary_live<cap['review_slots'] and free>0 and not review_launch_paused():problems.append('Dispatch queued independent reviews')
 for name in ['collection_blockers.json','integration_blockers.json']:
  if read(F/name,[]):problems.append('Resolve '+name)
 ledger=read(F/'integration.json',{});holds={(h['audit_id'],h['field']) for h in read(B/'adjudication_holds.json',[]) if h.get('completion_pass')=='2026-10-31-unresolved'}
 for item in read(F/'proposals.json',[]):
  if item['supported']:
   key=item['source_key']+':'+str(item['audit_id'])+':'+item['field'];digest=hashlib.sha256(json.dumps(item,sort_keys=True).encode()).hexdigest()
   if not ledger.get(key,{}).get('signature','').startswith(digest+':'):problems.append('Integrate current proposal: '+key)
  elif (item['audit_id'],item['field']) not in holds:problems.append('Record unresolved field disposition')
 if read(F/'export_fingerprint.json',{}).get('scientific_inputs_sha256')!=scientific_fingerprint():problems.append('Recompute and validate export after scientific changes')
 if read(F/'export_fingerprint.json',{}).get('results_sha256')!=hashlib.sha256((B/'results.csv').read_bytes()).hexdigest():problems.append('Validate current exported results hash')
 if not sum(active.values()) and read(F/'state.json',{}).get('status') not in ['checkpoint_ready','complete']:problems.append('No live children: continue parent work or explicitly record an idle checkpoint; do not claim active continuation')
 result={'ready_to_yield':not problems,'live_tasks_freshly_checked':active,'queued_sources':queued,'queued_reviews':review_queued,'review_launches_paused':review_launch_paused(),'actionable_work':sorted(set(problems))}
 (F/'yield_readiness.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert not problems
if __name__=='__main__':main()
