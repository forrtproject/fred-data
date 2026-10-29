#!/usr/bin/env python3
"""Parent progress accounting and one-time 30-minute acquisition decision."""
import collections,datetime,json,pathlib,re
import controller
R=controller.R
now=controller.NOW();m=controller.read(R/'run_manifest.json');launch=datetime.datetime.fromisoformat(m['launch_time']);age=(now-launch).total_seconds()
queue=controller.read(R/'work_queue.json');q={w['file_key']:w for w in queue}
cs={p.stem:controller.read(p,{}) for p in (R/'codings').glob('*.json') if re.fullmatch(r'[0-9a-f]{16}',p.stem)}
valid={k:c for k,c in cs.items() if controller.validate(R/'codings'/f'{k}.json')}
starts={};ends={}
if (R/'tasks.jsonl').exists():
 for line in (R/'tasks.jsonl').read_text().splitlines():
  e=json.loads(line);tid=e.get('taskId');stamp=datetime.datetime.fromisoformat(e['at'])
  if e.get('files'):starts.setdefault(tid,(stamp,e))
  if e.get('status') in ['completed','failed','cancelled','interrupted']:ends.setdefault(tid,stamp)
ordinary_minutes=sum(max(0,((ends.get(tid,now))-start).total_seconds())/60 for tid,(start,e) in starts.items() if not e.get('large'))
done=sum(c.get('status')=='done' for c in valid.values());ordinary_done=sum(c.get('status')=='done' and q[k]['row_count']<=8 for k,c in valid.items())
remaining=(datetime.datetime.fromisoformat(m['deadlines']['coding'])-now).total_seconds()/60
rate=ordinary_done/ordinary_minutes if ordinary_minutes else 0
# Conservative: reserve one worker for large projects for the remaining run.
completed_ordinary=sum(c.get('status') in ['done','no_text'] and q[k]['row_count']<=8 for k,c in valid.items())
yield_rate=ordinary_done/completed_ordinary if completed_ordinary else 0
terminal_no_text=sum(c.get('status')=='no_text' for c in valid.values())
completion_rate=completed_ordinary/ordinary_minutes if ordinary_minutes else 0
remaining_works=max(0,len(queue)-done-terminal_no_text)
projected=done+min(remaining_works,max(0,remaining)*9*completion_rate)*yield_rate
primary_usable_done=sum(c.get('status')=='done' and not c.get('identity_warning') and c.get('text_scope_complete') is not False and not c.get('blind_source_warning') for c in valid.values())
x={'primary_usable_done':primary_usable_done,'projection_method':'completion_rate_times_observed_text_yield','ordinary_done':ordinary_done,'completed_ordinary':completed_ordinary,'observed_coding_yield':yield_rate,'at':now.isoformat(),'age_minutes':age/60,'attempted_files':len(cs),'valid_records':len(valid),'done':done,'status_counts':dict(collections.Counter(c.get('status','malformed') for c in cs.values())),'evidence_counts':dict(collections.Counter(c.get('evidence_level') for c in valid.values() if c.get('status')=='done')),'ordinary_worker_minutes':ordinary_minutes,'ordinary_done_per_worker_minute':rate,'projected_coded_works_by_coding_deadline':round(projected),'projected_fraction':projected/len(queue)}
with (R/'progress.jsonl').open('a') as f:f.write(json.dumps(x)+'\n')
forecast=R/'forecast.json'
if age>=1800 and (not forecast.exists() or not controller.read(forecast,{}).get('projection_method')):
 x['acquisition_budget']={'first_pass_seconds':60,'alternative_seconds':20} if projected/len(queue)<.8 else {'first_pass_seconds':90,'alternative_seconds':30}
 x['decision']='Tighten acquisition to 60+20 seconds; preserve evidence standards.' if projected/len(queue)<.8 else 'Retain acquisition budget; projected coding coverage is at least 80%.'
 forecast.write_text(json.dumps(x,indent=2)+'\n')
 with (R/'run_log.md').open('a') as f:f.write(f"- 30-minute projection at {now.isoformat()}: {done} coded; {ordinary_minutes:.1f} observed ordinary worker-minutes; projected {projected:.0f}/{len(queue)} coded by coding deadline at nine ordinary workers. {x['decision']} This forecast is operational, not a statistical estimate.\n")
hour=int(age//3600)
hours_path=R/'progress_hours.json'
hours=controller.read(hours_path,[])
if hour>=1 and hour not in hours:
 with (R/'run_log.md').open('a') as f:f.write(f"- Hour {hour} checkpoint {now.isoformat()}: {len(cs)} records attempted, {done} validated done, evidence {x['evidence_counts']}, statuses {x['status_counts']}.\n")
 hours_path.write_text(json.dumps(hours+[hour])+'\n')
print(json.dumps(x))
