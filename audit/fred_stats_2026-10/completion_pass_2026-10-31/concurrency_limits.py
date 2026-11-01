"""Shared limits for source, ordinary-review and focused-review dispatch."""
import json
from pathlib import Path
F=Path(__file__).resolve().parent
TERMINAL={'completed','failed','cancelled','interrupted'}

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
