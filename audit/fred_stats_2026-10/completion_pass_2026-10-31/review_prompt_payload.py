"""Lossless row context shared by field reviews of the same audit row."""
import copy

SHARED=('source_key','side','input','worker_target_match','worker_target_description',
        'worker_notes','source_path','parent_response','coding_context')

def pack(items):
 rows={}
 for item in items:rows.setdefault(str(item['audit_id']),[]).append(item)
 context={}
 for aid,group in rows.items():
  context[aid]={key:copy.deepcopy(group[0][key]) for key in SHARED
                if key in group[0] and all(key in x and x[key]==group[0][key] for x in group)}
 fields=[{k:copy.deepcopy(v) for k,v in item.items() if k not in context[str(item['audit_id'])]}
         for item in items]
 # Validate real dispatched content as well as fixtures. No evidence, prior finding,
 # objection, value or ordering may disappear through the presentation change.
 assert [{**context[str(x['audit_id'])],**x} for x in fields]==items
 return {'row_context':context,'field_reviews':fields}
