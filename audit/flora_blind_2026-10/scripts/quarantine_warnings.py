#!/usr/bin/env python3
"""Parent-only exclusion of exposed coding; one fresh-child retry maximum."""
import pathlib,json,re,datetime
R=pathlib.Path(__file__).resolve().parents[1];Q=R/'quarantine';Q.mkdir(exist_ok=True)
p=R/'blinding_incidents.json'
incidents=json.loads(p.read_text()) if p.exists() else [];changed=[]
for f in (R/'codings').glob('*.json'):
 if not re.fullmatch(r'[0-9a-f]{16}',f.stem):continue
 try:c=json.loads(f.read_text())
 except (OSError,ValueError):continue
 if not c.get('blind_source_warning') or c.get('terminal_blinding_failure'):continue
 number=len(list(Q.glob(f'{f.stem}.attempt*.json')))+1
 dest=Q/f'{f.stem}.attempt{number}.json';f.rename(dest)
 row={'file_key':f.stem,'excluded_coding':str(dest),'warning':c.get('blind_source_warning'),'detail':c.get('skip_reason',''),'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'action':'fresh-child retry' if number==1 else 'terminal unverified after exposed retry'}
 # Never pass a prior exposed attempt's text (including warning placeholders)
 # into the fresh child's source slot. Preserve it privately for the audit trail.
 source=R/'texts'/f'{f.stem}.txt'
 if source.exists():
  excluded=source.with_name(f'{f.stem}.excluded-attempt{number}.txt')
  source.rename(excluded);row['excluded_text']=str(excluded)
 incidents.append(row);changed.append(row)
 if number>=2:
  failure={'work_key':c['work_key'],'status':'error','blind_source_warning':True,'terminal_blinding_failure':True,'skip_reason':'Both allowed coding attempts compromised by source exposure; no further retry.','evidence_level':None,'source_url':None,'retrieved_at':None,'text_sha256':None,'parser':None}
  tmp=f.with_suffix('.quarantine.tmp');tmp.write_text(json.dumps(failure,indent=2)+'\n');tmp.replace(f)
 if changed:
  with (R/'run_log.md').open('a') as log:log.write(f"- Blinding exclusion {row['at']}: {f.stem}, attempt {number}, {row['action']}; archived at {dest}.\n")
if changed:
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(incidents,indent=2,ensure_ascii=False)+'\n');tmp.replace(p)
print(json.dumps({'quarantined':changed}))
