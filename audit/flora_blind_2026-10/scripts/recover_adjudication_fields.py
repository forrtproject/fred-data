#!/usr/bin/env python3
"""Recover independently complete JSON field objects; never repair truncated text."""
import pathlib,json,importlib.util,sys,collections
R=pathlib.Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('compare',R/'scripts/compare.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
def key(d):return (str(d.get('input_row_index','')),d.get('target_index') if d.get('field')=='missing_row' else None,d.get('field'))
selection=json.loads((R/'adjudication_selection_003.json').read_text())['items']
for fk in sys.argv[1:]:
 statepath=R/'argon'/f'{fk}.state.json';state=json.loads(statepath.read_text());assert state['status']=='unresolved' and state['attempts']==2
 requested={key(d) for d in selection if d['file_key']==fk};text=(R/'texts'/f'{fk}.txt').read_text();candidates=collections.defaultdict(list);invalid=0
 for attempt in [1,2]:
  raw=(R/'argon'/f'{fk}.attempt{attempt}.txt').read_text().rsplit('## Answer',1)[-1]
  try:pos=raw.index('[',raw.index('"decisions"'))+1
  except ValueError:continue
  while pos<len(raw):
   while pos<len(raw) and raw[pos] in ' \n\r\t,':pos+=1
   try:d,end=json.JSONDecoder().raw_decode(raw[pos:])
   except ValueError:break
   pos+=end
   if not isinstance(d,dict):break
   if key(d) in requested and c.valid_decision(d,text):candidates[key(d)].append(d)
   else:invalid+=1
 decisions=[];conflicts=[]
 for k,ds in candidates.items():
  signatures={json.dumps([d['verdict'],d.get('corrected_value')],sort_keys=True) for d in ds}
  if len(signatures)==1:decisions.append(ds[-1])
  else:conflicts.append(k)
 # Parent-selected consecutive excerpts preserve verdicts while shortening quotes.
 for d in decisions:
  if str(d.get('input_row_index'))=='1940':d['quote']=d['quote'][d['quote'].index('We failed to replicate'):]
  if str(d.get('input_row_index'))=='2046':d['quote']=d['quote'][d['quote'].index('This seriously complicates'):]
  assert c.valid_decision(d,text)
 metadata={'recovered_complete_field_objects':len(decisions),'invalid_complete_objects':invalid,'conflicting_fields':conflicts,'requested_fields_not_recovered':len(requested-{key(d) for d in decisions}),'note':'Whole reply failed/truncated. Only independently complete JSON objects with requested keys, valid shape and exact source quotes recovered. No missing JSON or words repaired; no further model calls.'}
 (R/'adjudications'/f'{fk}.json').write_text(json.dumps({'decisions':decisions,'partial_recovery':metadata},indent=2,ensure_ascii=False)+'\n')
 state['partial_recovery']=metadata;statepath.write_text(json.dumps(state,indent=2)+'\n');print(fk,json.dumps(metadata))
