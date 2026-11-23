"""Shared limits for source, ordinary-review and focused-review dispatch."""
import json
from pathlib import Path
F=Path(__file__).resolve().parent
TERMINAL={'completed','failed','cancelled','interrupted'}

def review_launch_paused(path=None):
 p=path or F/'review_service_hold.json'
 if not p.exists():return False
 d=json.loads(p.read_text())
 assert d['provider']=='antigravity' and d['model']=='gemini-4-argon-high'
 assert d['reason']=='quota_exhausted' and isinstance(d['active'],bool)
 return d['active']

def recorded_quota_failure(task,answer_exists):
 return (not answer_exists and task.get('status')=='completed'
         and task.get('failure_disposition_recorded') is True
         and task.get('output_failure_code')=='quota_exhausted'
         and task.get('output_contract')=='failed'
         and 'Usage Limit Reached' in (task.get('summary') or ''))

def limits():
 d=json.loads((F/'worker_limits.json').read_text())
 assert all(isinstance(d[k],int) and d[k]>0 for k in ['source_slots','review_slots','max_combined_children'])
 assert d['max_combined_children']<=10
 return d

def live_count(folder,pattern,exclude_suffix=None):
 return sum(bool(d.get('taskId')) and (d.get('status') not in TERMINAL or bool(d.get('hasPendingChildRuns')))
            for p in folder.glob(pattern) if not exclude_suffix or not p.name.endswith(exclude_suffix)
            for d in [json.loads(p.read_text())])

def slot_ceiling(kind,other_active,config=None):
 d=config or limits()
 return max(0,min(d[kind+'_slots'],d['max_combined_children']-other_active))

def review_capacity_available(review_active,source_active,config=None):
 return review_active<slot_ceiling('review',source_active,config)

def ordinary_review_ceiling(source_active,focused_active,config=None):
 d=config or limits()
 return max(0,min(d['review_slots']-focused_active,d['max_combined_children']-source_active-focused_active))

def awaits_native_callback(task):
 return (bool(task.get('taskId')) and task.get('status') in ['queued','running','waiting']
         and not task.get('hasPendingChildRuns')
         and task.get('next')=='Completion wakes this thread, so end your turn. Do not wait on it or poll it.')
