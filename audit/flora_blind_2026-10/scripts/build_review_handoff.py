#!/usr/bin/env python3
"""Build proposal files and the shared review app; never apply scientific changes."""
import csv,hashlib,json
from urllib.parse import urlsplit
from collections import Counter
from pathlib import Path
B=Path(__file__).resolve().parents[1]; O=B/'handoff';O.mkdir(exist_ok=True)
def read(n):
 with (B/n).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
source=Path('/home/lukas/audit_inputs_2026-10/flora_b48a7d6.csv')
with source.open(encoding='utf-8-sig') as f:frozen=list(csv.DictReader(f))
fixes=[];cases=[]
for r in read('results.csv'):
 i=int(r['input_row_index']); changes=json.loads(r['suggested_correction']); evidence=json.loads(r['correction_evidence'])
 if changes:fixes.append(dict(id=f'fix:{i}',input_row_index=i,work_key=r['work_key'],file_key=r['file_key'],expected_before=frozen[i],proposed_changes=changes,evidence=json.loads(json.dumps(evidence)),status='proposed_not_applied',signoff='pending'))
 if r['resolution']!='unresolved':continue
 fields=['type','original']+(['outcome_computation','outcome_robustness'] if r['type']=='reproduction' else ['outcome'])
 fields=[f for f in fields if r[f+'_final_verdict']=='unverified']
 route='Substantive source or coding review'
 if changes.get('original')=={'action':'remove_row'}:route='Row removal already proposed'
 elif changes.get('type',r['type'])=='not_a_replication':route='Check field applicability'
 elif r['study_status']=='prospective':route='Plan with no reported results'
 cases.append(dict(id=f'row:{i}',kind='existing row',row=i,work=r['work_key'],file_key=r['file_key'],title=frozen[i].get('title_r') or r['work_key'],level=r['evidence_level'],route=route,fields=fields,changes=changes,evidence=evidence,signoff='pending_final_Sol_review',triage_is_verdict=False))
adds=[]
for r in read('confirmed_missing_references.csv'):
 adds.append(dict(id=f"add:{r['file_key']}:{r['target_index']}",operation='propose_add_pair',work_key=r['work_key'],file_key=r['file_key'],target_index=int(r['target_index']),original={k:r[k] for k in ['doi','title','authors','year']},evidence=json.loads(r['evidence']),blind_target=json.loads(r['blind_target']),status='proposed_not_applied',signoff='pending'))
for r in read('unresolved_missing_candidates.csv'):
 cases.append(dict(id=f"missing:{r['file_key']}:{r['target_index']}",kind='possible missing pair',row=None,work=r['work_key'],file_key=r['file_key'],title=r['title'] or r['work_key'],level=r['evidence_level'],route='Verify missing-pair identity',fields=['missing_row'],changes={},evidence={'missing_row':json.loads(r['evidence'])},signoff='pending_final_Sol_review'))
ft=[c for c in cases if c['kind']=='existing row' and c['level']=='full_text']
assert len(ft)==109 and len({c['id'] for c in cases})==len(cases)
m=dict(status='proposal_only_no_new_scientific_verdicts',baseline_sha256=sha(source),input_sha256={n:sha(B/n) for n in ['results.csv','confirmed_missing_references.csv','unresolved_missing_candidates.csv']},existing_row_proposals=len(fixes),field_proposals=sum(len(x['proposed_changes']) for x in fixes),pair_additions=len(adds),review_cases=len(cases),fulltext_rows=len(ft),fulltext_works=len({c['file_key'] for c in ft}),fulltext_triage=dict(Counter(c['route'] for c in ft)),applied_changes=0)
# Final source-backed signoff is independent of old comparison/export uncertainty.
review_file=O/'sol_review_decisions.json'
reviewed=json.loads(review_file.read_text())['decisions'] if review_file.exists() else []
by_id={d['case_id']:d for d in reviewed}
current_review_file=O/'current_source_decisions.json'
if current_review_file.exists():
 by_id.update({d['case_id']:d for d in json.loads(current_review_file.read_text())['decisions']})
# Keep earlier correction proposals reviewable even when the historical export
# considered their row resolved. Their existing source adjudication is preserved;
# adding them to the interface does not invent a new final Sol signoff.
historical_review_cases=len(cases)
case_ids={c['id'] for c in cases}
for f in fixes:
 i=f['input_row_index'];cid=f'row:{i}'
 if cid in case_ids:continue
 before=frozen[i]
 cases.append(dict(id=cid,kind='earlier correction proposal',row=i,work=f['work_key'],file_key=f['file_key'],title=before.get('title_r') or f['work_key'],level='prior_source_adjudication',route='Review correction proposal',fields=list(f['proposed_changes']),changes=f['proposed_changes'],evidence=f['evidence'],signoff='prior_source_adjudicated_proposal',triage_is_verdict=False))
m['historical_unresolved_review_cases']=historical_review_cases
m['review_cases']=len(cases)
for c in cases:
 if c['id'] in by_id:
  d=by_id[c['id']];c['signoff']=d['audit_status']
  c['changes']=json.loads(json.dumps(c['changes']))
  if d.get('withdraw_earlier_proposals'):
   c['route']='Earlier removal withdrawn after source review';c['withdrawn_proposals']=d['withdraw_earlier_proposals'];c['changes']={f:v for f,v in c['changes'].items() if f not in d['withdraw_earlier_proposals']}
  for field,value in d['fields'].items():
   if value['disposition']=='correction_supported':c['changes'][field]=value['proposed_value']
  c['final_review_summary']={f:{'disposition':v['disposition'],'confirmed_value':v.get('confirmed_value'),'proposed_value':v.get('proposed_value'),'application_dependency':d.get('application_hold'),'policy_choice':v.get('missing_evidence_or_policy_choice') if v['disposition']=='policy_decision_required' else None} for f,v in d['fields'].items()}
  c['final_review_reference']='sol_review_decisions.json'
  urls=[]
  for value in d['fields'].values():
   for proof in value.get('proofs',[]):
    path=Path(proof['source_path']);meta=path.parent/'metadata.json'
    if path.name=='article.txt' and path.parent.name.startswith('sanitized_') and meta.exists():
     url=json.loads(meta.read_text()).get('source_url','')
     if urlsplit(url).scheme=='https' and not urlsplit(url).query:urls.append(url)
  c['primary_evidence_urls']=list(dict.fromkeys(urls))
  for f,v in d['fields'].items():
   proof=v['proofs'][0]
   c['evidence'][f]={'quote':proof['quote'],'location':proof.get('section','Primary source')+'; character '+str(proof['character_start']),'reason':v['rationale'],'method':'Final GPT-6.1 Sol source review'}
missing_review_file=O/'missing_pair_review_decisions.json'
missing_reviews=json.loads(missing_review_file.read_text())['decisions'] if missing_review_file.exists() else []
missing_by_id={d['case_id']:d for d in missing_reviews}
for c in cases:
 if c['kind']=='possible missing pair':c['missing_pair_unresolved']=c['id'] not in missing_by_id or missing_by_id[c['id']]['verdict']=='reviewed_unknown'
 if c['id'] in missing_by_id:
  d=missing_by_id[c['id']];c['signoff']='final_Sol_missing_pair_reviewed';c['final_review_reference']='missing_pair_review_decisions.json';c['route']='Source verified: '+d['verdict'].replace('_',' ')
  c['final_review_summary']={'missing_row':{'disposition':d['verdict'],'confirmed_value':d['identity'],'proposed_value':None,'policy_choice':None}}
  c['evidence']['missing_row']={'quote':'','location':'Complete three-source review; proof locators in missing_pair_review_decisions.json','reason':d['rationale'],'method':'Final GPT-6.1 Sol source review'}
# Only fields with explicit final source-backed correction approval enter this file.
approved=[]
for d in reviewed:
 for field,v in d['fields'].items():
  if v['disposition']=='correction_supported' and field in d.get('approved_for_application_fields',[]):
   assert v.get('proposed_value') is not None
   approved.append(dict(id=f"approved:{d['input_row_index']}:{field}",input_row_index=d['input_row_index'],file_key=d['file_key'],field=field,expected_before=frozen[d['input_row_index']],proposed_value=v['proposed_value'],rationale=v['rationale'],proofs=v['proofs'],status='source_approved_not_applied',scope='Only this field; other proposed changes in the row require their own signoff'))
save('approved_fixes.json',dict(baseline_sha256=sha(source),status='source_approved_not_applied',changes=approved,withdraw_prior_proposals=[{'input_row_index':d['input_row_index'],'withdraw':d['withdraw_earlier_proposals']} for d in reviewed if d.get('withdraw_earlier_proposals')]))
review_required=[]
for d in reviewed:
 uncertain={f:v for f,v in d['fields'].items() if v['disposition'] in ['reviewed_unknown','source_needed','policy_decision_required'] or (v['disposition']=='correction_supported' and f not in d.get('approved_for_application_fields',[]))}
 if uncertain or d.get('application_hold'):
  review_required.append(dict(case_id=d['case_id'],input_row_index=d['input_row_index'],fields=uncertain,application_hold=d.get('application_hold'),status='review_required_no_automatic_change'))
save('review_required.json',dict(baseline_sha256=sha(source),scope='Final Sol source-review evidence limits, policy choices and unapproved conditional corrections. Earlier proposals remain separately reviewable in the app.',cases=review_required,canonical_changes_applied=False))
required_ids={d['case_id'] for d in review_required}
for c in cases:c['requires_review']=c['id'] in required_ids
m['source_approved_fix_fields']=len(approved)
m['final_Sol_reviewed_missing_candidates']=len(missing_reviews)
m['new_source_verified_missing_pairs']=sum(d['verdict']=='genuinely_missing' and not d.get('already_in_earlier_missing_export') for d in missing_reviews)
m['final_Sol_reviewed_fulltext_rows']=sum(c['id'] in by_id for c in ft)
m['remaining_fulltext_rows']=len(ft)-m['final_Sol_reviewed_fulltext_rows']
m['final_review_required_rows']=len(review_required)
m['source_verified_evidence_replacements']=len(json.loads((O/'evidence_provenance_fixes.json').read_text())['changes']) if (O/'evidence_provenance_fixes.json').exists() else 0
from review_record_actions import enrich_cases
enrich_cases(cases,frozen)
m['final_review_required_rows']=len(json.loads((O/'review_required.json').read_text())['cases'])
m['status']='final_source_review_complete_proposals_not_applied' if m['final_Sol_reviewed_fulltext_rows']==109 else 'final_source_review_active_proposals_not_applied'
reliability=json.loads((O/'review_reliability.json').read_text()) if (O/'review_reliability.json').exists() else {}
for c in cases:
 if c['id'] in reliability.get('holds',{}):
  c['requires_review']=True;c['review_hold']=reliability['holds'][c['id']]
  c['evidence']['outcome']['quote']=c['review_hold']['evidence'][0]['quote'];c['evidence']['outcome']['location']='Discussion: explicit attribution to Berinsky (2017)'
  c['evidence']['outcome']['reason']=c['review_hold']['reason']
  required=json.loads((O/'review_required.json').read_text());required['cases'].append(dict(case_id=c['id'],input_row_index=c['row'],application_hold=c['review_hold']['reason'],status='postpublication_objection_unresolved'));save('review_required.json',required)
m['final_review_required_rows']=len(json.loads((O/'review_required.json').read_text())['cases'])
if reliability.get('holds'):m['status']='postpublication_objection_open_proposals_not_applied'
save('fix_proposals.json',dict(baseline_sha256=sha(source),existing_rows=fixes,add_pairs=adds));save('review_queue.json',cases);
if not (O/'fulltext_109_inventory.json').exists():save('fulltext_109_inventory.json',ft)
save('manifest.json',m)
# Review app. The interface lives in review_app_template.html; this block adds
# display-only context (frozen FLoRA values, proposal status, limits). It reads
# the handoff data but never writes a data file or changes a scientific verdict.
import re,sys
PRIVATE_PATH=re.compile(r'(?:/home/lukas/|audit/flora_blind_2026-10/(?:evidence_followup/)?private/)[^\s<>"\']+')
ACCESS_TOKEN=re.compile(r'(?:view_only|access_token|api_key)=[A-Za-z0-9_-]{8,}')
DROP_KEYS={'source_path','source_read_manifest','relevant_context_reads','parent_gate','prior_review_artifact','prior_full_source_Sol_review_artifact','prior_full_source_Sol_review_read_manifest','primary_metadata_receipt','input_sha256'}
def excerpt(text):
 words=list(re.finditer(r'\S+',text));return text[:words[24].end()] if len(words)>25 else text
def safe(value,key=''):
 # Context passes unchanged into the public app, so apply the public-asset rules here.
 if isinstance(value,dict):return {k:safe(v,k) for k,v in value.items() if k not in DROP_KEYS}
 if isinstance(value,list):return [safe(v,key) for v in value]
 if isinstance(value,str):
  value=ACCESS_TOKEN.sub('[access token removed]',PRIVATE_PATH.sub('[private audit artifact]',value))
  return excerpt(value) if key=='quote' or key.endswith('_quote') else value
 return value
def na(v):
 v=(v or '').strip();return '' if v.upper() in {'NA','NAN','NULL'} else v
def names(raw,limit=3):
 try:people=json.loads(raw) if raw.strip().startswith('[') else None
 except ValueError:people=None
 if not isinstance(people,list):return na(raw)
 fam=[f for f in (str(p.get('family') or p.get('literal') or '').strip() for p in people if isinstance(p,dict)) if f]
 if len(fam)>limit:return fam[0]+' et al.'
 return ', '.join(fam[:-1])+' & '+fam[-1] if len(fam)>1 else ''.join(fam)
results={int(r['input_row_index']):r for r in read('results.csv')}
def flora(i,with_trace):
 f=frozen[i];omitted=[]
 def keep(k,limit=None):
  v=f.get(k) or ''
  if PRIVATE_PATH.search(v) or ACCESS_TOKEN.search(v):omitted.append(k);return ''
  return v[:limit].rstrip()+'…' if limit and len(v)>limit else v
 def side(s):
  doi=na(keep('doi_'+s));return {k:v for k,v in dict(title=na(keep('title_'+s)),authors=names(keep('author_'+s)),year=na(keep('year_'+s)),journal=na(keep('journal_'+s)),doi=doi,url='' if doi else na(keep('url_'+s))).items() if v}
 x=dict(r=side('r'),o=side('o'),type=keep('type'),outcome=keep('outcome'),quote=keep('outcome_quote',1200),quote_source=keep('outcome_quote_source'),level=results[i]['evidence_level'],
        sha=hashlib.sha256(json.dumps(f,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest())
 if with_trace:
  r=results[i];original={k:r[f'blind_{k}_o'] for k in ['authors','year','title','doi'] if r[f'blind_{k}_o']}
  trace=dict(skip_reason=r['skip_reason'],blind_type=r['blind_type'],blind_original=original,blind_outcome=r['blind_outcome'],blind_outcome_computation=r['blind_outcome_computation'],blind_outcome_robustness=r['blind_outcome_robustness'],original_grade=r['original_grade'],outcome_grade=r['outcome_grade'],type_agree=r['type_agree'])
  x['trace']=safe({k:v for k,v in trace.items() if v})
 if omitted:x['omitted']=omitted
 return x
POLICY_HOLD='Resolve this row’s coding-policy choice before applying its correction bundle.'
RECORD_HOLD='Resolve the whole-record remedy before applying this field; do not apply it in isolation.'
record_actions={}
if (O/'record_actions.json').exists():
 for a in json.loads((O/'record_actions.json').read_text()).get('actions',[]):
  cid=a.get('case_id') or (f"row:{a['input_row_index']}" if a.get('input_row_index') is not None else None)
  if cid:record_actions[cid]=a
published={}
if (O/'correction_proposals.json').exists():
 published={(x['input_row_index'],x['field']):x for x in json.loads((O/'correction_proposals.json').read_text())['changes']}
derived=[]
def proposal_meta(c):
 # Prefer correction_proposals.json; otherwise mirror its status rules (build_audit_report.py).
 d=by_id.get(c['id']);out={}
 policy=bool(d) and any(v['disposition']=='policy_decision_required' for v in d['fields'].values())
 for field,value in c['changes'].items():
  x=published.get((c['row'],field))
  if x and x['proposed_value']==value:
   out[field]=dict(status=x['status'],review='final_source_review' if x.get('audit_provenance_status') in ('source_approved_not_applied','conditional_review_required') else 'earlier_source_adjudication',conditional=x.get('audit_provenance_status')=='conditional_review_required',hold=x.get('application_hold'),record_dependency=bool(x.get('record_action_dependency')))
   continue
  derived.append((c['row'],field))
  v=d['fields'].get(field) if d else None
  final=bool(v) and v['disposition']=='correction_supported'
  conditional=final and field not in d.get('approved_for_application_fields',[])
  hold=POLICY_HOLD if policy else (d.get('application_hold') if d else None)
  record=bool(c.get('record_action')) or c['id'] in record_actions
  if record:hold=' '.join(filter(None,[hold,RECORD_HOLD]))
  out[field]=dict(status='decision_required' if hold or conditional else 'evidence_checked_proposal',review='final_source_review' if final else 'earlier_source_adjudication',conditional=conditional,hold=hold,record_dependency=record)
 return out
rows,proposals,limits,contrary,review_notes={},{},{},{},{}
caseids={c['id']:c for c in cases}
for c in cases:
 if c['row'] is None:continue
 rows[c['row']]=flora(c['row'],not c['evidence'])
 if c['changes']:proposals[c['row']]=proposal_meta(c)
for d in by_id.values():
 i=d['input_row_index']
 for f,v in d['fields'].items():
  if v.get('missing_evidence_or_policy_choice') not in (None,'',{},[]):limits.setdefault(i,{})[f]=safe(v['missing_evidence_or_policy_choice'])
  if v.get('contrary_evidence') or v.get('strongest_contrary_evidence'):contrary.setdefault(i,{})[f]=safe(v.get('contrary_evidence') or v.get('strongest_contrary_evidence'))
 n={k:safe(d[k]) for k in ['approval_dependency_status','parent_registration_identity_gate','parent_additional_source_inspection','source_identity_followup_pending'] if k in d}
 if n:review_notes[i]=n
candidates={}
for r in read('unresolved_missing_candidates.csv'):
 try:t=json.loads(r['blind_target'] or '{}')
 except ValueError:t={}
 x=dict(authors=r['authors'] or t.get('authors'),year=r['year'] or t.get('year'),title=r['title'] or t.get('title'),doi=r['doi'] or t.get('doi'),identified_by=t.get('identified_by'),study_numbers=t.get('study_numbers'),replication_study_numbers=t.get('replication_study_numbers'),pairing_flags=r['pairing_flags'])
 candidates[f"missing:{r['file_key']}:{r['target_index']}"]=safe({k:v for k,v in x.items() if v})
by_work={}
for i,r in results.items():by_work.setdefault(r['work_key'],[]).append(i)
works={}
for c in cases:
 if c['kind']!='possible missing pair' or c['work'] in works or not by_work.get(c['work']):continue
 ids=sorted(by_work[c['work']]);f=frozen[ids[0]]
 works[c['work']]=safe(dict(title=na(f['title_r']),authors=names(f['author_r']),year=na(f['year_r']),journal=na(f['journal_r']),
  rows=[{k:v for k,v in dict(row=i,authors=names(frozen[i]['author_o']),year=na(frozen[i]['year_o']),title=na(frozen[i]['title_o']),doi=na(frozen[i]['doi_o'])).items() if v!=''} for i in ids]))
quote_fixes={}
if (O/'evidence_provenance_fixes.json').exists():
 for x in json.loads((O/'evidence_provenance_fixes.json').read_text())['changes']:
  b,p=x.get('expected_before',{}),x.get('proposed_evidence',{})
  quote_fixes[x['input_row_index']]=safe(dict(id=x.get('id'),current_text=b.get('outcome_quote',''),current_source=b.get('outcome_quote_source',''),proposed_quote=p.get('outcome_quote',''),proposed_source=p.get('outcome_quote_source',''),outcome_reviewed=x.get('scientific_value_reviewed'),rationale=x.get('rationale','')))
from build_batch_review import build as build_batches
batch_review=build_batches()
from build_batch_evidence import build as build_batch_evidence
build_batch_evidence()
shared_config=json.loads((Path.home()/'.claude/html-comments.config.json').read_text())
shared_review=dict(endpoint=shared_config['endpoint'],project='flora-audit-decisions-2026-10',protocol=1)
context=dict(review_reliability=safe(reliability),batch_evidence_sha256=sha(O/'batch_evidence.json'),shared_review=shared_review,batch_review=batch_review,baseline_sha256=sha(source),rows=rows,proposals=proposals,limits=limits,contrary=contrary,review_notes=review_notes,candidates=candidates,works=works,quote_fixes=quote_fixes,record_actions={k:safe(a) for k,a in record_actions.items() if not caseids.get(k,{}).get('record_action')})
if derived:print(f'Review app: {len(derived)} proposal statuses derived because correction_proposals.json is missing or differs, e.g. {derived[:5]}',file=sys.stderr)
DOWNLOADS=[('correction_proposals.json','Correction proposals (JSON)'),('record_actions.json','Record-level actions (JSON)'),
 ('evidence_provenance_fixes.json','Evidence quote updates (JSON)'),('review_required.json','Limits, policy choices and holds (JSON)'),
 ('confirmed_missing_pairs.csv','Confirmed missing pairs (CSV)'),('planned_study_pairs.csv','Planned-study pairs (CSV)'),
 ('unresolved_missing_pairs.csv','Unresolved missing candidates (CSV)'),('audit_rows.csv','Status of every input row (CSV)'),
 ('sol_review_decisions.json','Field-level source decisions (JSON)'),('current_source_decisions.json','Current-source decisions (JSON)'),
 ('missing_pair_review_decisions.json','Missing-pair source decisions (JSON)'),('review_queue.json','Complete review queue (JSON)'),
 ('review_reliability.json','Current objections and bulk-approval restrictions (JSON)'),('batch_evidence.json','Supporting evidence for batch items (JSON)'),('audit_overview.json','Audit overview (JSON)')]
# The public builder inserts its report link before the first anchor of this paragraph.
downloads='<p>'+''.join(f'<a href="{n}">{label}</a>' for n,label in DOWNLOADS if n=='correction_proposals.json' or (O/n).exists())+'</p>'
display=json.loads(json.dumps(cases))
for c in display:
 c['evidence']={f:{k:e.get(k,'') for k in ['quote','location','reason','method']} for f,e in c['evidence'].items()}
 for e in c['evidence'].values():
  for k in ['reason','quote']:
   if isinstance(e.get(k),str) and len(e[k])>260:e[k]=e[k][:260]+' [Display excerpt; complete evidence is retained in review_queue.json.]'
def embed(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
blob=embed(context)
assert not PRIVATE_PATH.search(blob) and not ACCESS_TOKEN.search(blob) and '.t3/worktrees/' not in blob
template=Path(__file__).with_name('review_app_template.html').read_text()
fill={'/*flora-batch-evidence*/':(B/'scripts'/'review_batch_evidence.js').read_text(),'/*flora-shared-state*/':(B/'scripts'/'review_shared_state.js').read_text(),'/*flora-shared-sync*/':(B/'scripts'/'review_shared_sync.js').read_text(),'/*flora-workflow*/':(B/'scripts'/'review_batch_workflow.js').read_text(),'/*flora-sha256*/':(O/'review_sha256.js').read_text(),'__DATA__':embed(display),'__CONTEXT__':blob,'__HASH__':json.dumps(m['input_sha256']['results.csv']),'__QUEUEHASH__':json.dumps(sha(O/'review_queue.json')),'<!--flora-downloads-->':downloads}
assert all(template.count(k)==1 for k in fill)
html=re.sub('|'.join(map(re.escape,fill)),lambda x:fill[x.group(0)],template)
(O/'review.html').write_text(html)
print(json.dumps(m,indent=2))
