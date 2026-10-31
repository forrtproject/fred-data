#!/usr/bin/env python3
"""Validate handoff evidence and correction preconditions without editing FLoRA."""
import csv,hashlib,json,importlib.util
from pathlib import Path
from collections import Counter
B=Path(__file__).resolve().parents[1];O=B/'handoff'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=Path('/home/lukas/audit_inputs_2026-10/flora_b48a7d6.csv')
assert sha(baseline)=='6d391186dfb57263bbc6bb504e8561e0d1e25997b36417072c023812efaad9f7'
with baseline.open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
spec=importlib.util.spec_from_file_location('flora_handoff_compare',B/'scripts/compare.py');comparison=importlib.util.module_from_spec(spec);spec.loader.exec_module(comparison)
inventory=read(O/'fulltext_109_inventory.json');assert len(inventory)==109 and len({x['id'] for x in inventory})==109
decisions=read(O/'sol_review_decisions.json');ds=decisions['decisions'];assert len({x['case_id'] for x in ds})==len(ds);assert {x['case_id'] for x in ds}<={x['id'] for x in inventory}
proof_count=0
def proof(q):
 global proof_count
 p=Path(q['source_path']);raw=p.read_bytes();txt=raw.decode();assert sha(p)==q.get('sha256',q.get('raw_sha256'));assert txt[q['character_start']:q['character_end']]==q['quote'];assert raw[q['utf8_byte_start']:q['utf8_byte_end']].decode()==q['quote'];proof_count+=1
for d in ds:
 assert d['audit_status']=='final_Sol_reviewed' and d['canonical_dataset_changes_applied'] is False
 assigned=set(next(x for x in inventory if x['id']==d['case_id'])['fields'])
 assert assigned<=set(d['fields'])
 assert not set(d['fields'])-assigned or (d['case_id']=='row:462' and set(d['fields'])-assigned=={'original'}), 'Unregistered field-scope expansion'
 for v in d['fields'].values():
  assert v['disposition'] in ['confirmed_correct','correction_supported','not_applicable','reviewed_unknown','policy_decision_required','source_needed'];assert v['rationale'] and v['proofs']
  for q in v['proofs']:proof(q)
approved=read(O/'approved_fixes.json');assert approved['baseline_sha256']==sha(baseline);seen=set();staged={i:comparison.adapt_row(r) for i,r in enumerate(rows)}
for c in approved['changes']:
 i=c['input_row_index'];field=c['field'];assert (i,field) not in seen;seen.add((i,field));assert c['expected_before']==rows[i]
 d=next(x for x in ds if x['input_row_index']==i);assert field in d['approved_for_application_fields'];v=d['fields'][field];assert v['disposition']=='correction_supported' and c['proposed_value']==v['proposed_value'];assert not d.get('application_hold')
 assert c['proposed_value']!=staged[i].get(field)
 for q in c['proofs']:proof(q)
 staged[i][field]=c['proposed_value']
 if field=='original':
  assert set(c['proposed_value'])=={'doi','title','authors','year'}
  for k,value in c['proposed_value'].items():staged[i][k+'_o']=value
def pair(r):return (str(r.get('work_key') or r.get('doi_r') or r.get('url_r')).strip().lower(),str(r.get('doi_o')).strip().lower())
before=Counter(pair(comparison.adapt_row(r)) for r in rows if str(r.get('doi_o','')).lower() not in ['', 'na','nan'])
after=Counter(pair(r) for r in staged.values() if str(r.get('doi_o','')).lower() not in ['', 'na','nan'])
assert not {p:n for p,n in after.items() if n>1 and n>before[p]},'Approved changes introduce a duplicate pair'
def identifier(x):return str(x).strip().lower().removeprefix('https://doi.org/').removeprefix('http://doi.org/')
with (B/'confirmed_missing_references.csv').open(encoding='utf-8-sig') as f:old_missing=list(csv.DictReader(f))
additions=read(O/'confirmed_missing_pairs_addendum.json')['pairs'];new_keys=set()
for a in additions:
 key=(identifier(a['work_key']),identifier(a['original']['doi']));assert key not in new_keys;new_keys.add(key)
 assert not any(identifier(x['work_key'])==key[0] and identifier(x['doi'])==key[1] for x in old_missing)
 assert not any(identifier(x.get('doi_r') or x.get('url_r'))==key[0] and identifier(x.get('doi_o'))==key[1] for x in rows)
 assert a['outcome'] is None and a['outcome_status']=='not_adjudicated_in_this_scope'
 assert a['all_shipped_and_alternate_report_check']['matches']==[]
 for q in a['source_proof_locators']:
  raw=Path(q['source_path']).read_bytes();txt=raw.decode();assert hashlib.sha256(raw).hexdigest()==q['sha256'];assert raw[q['utf8_byte_start']:q['utf8_byte_end']].decode()==txt[q['character_start']:q['character_end']]
evidence=read(O/'evidence_provenance_fixes.json');assert len(evidence['changes'])==len({x['input_row_index'] for x in evidence['changes']})==14
for c in evidence['changes']:
 assert c['expected_before']=={k:rows[c['input_row_index']][k] for k in c['expected_before']};proof(c['proof']);assert c['proposed_evidence']['outcome_quote']==c['proof']['quote']
assert sha(O/'fix_proposals.json')=='0e43a796b260ece0f7e1b8078b3341024131ab456ddbe0f15ffe6c3726e7821e'
queue=read(O/'review_queue.json');assert len(queue)==len({x['id'] for x in queue})
manifest=read(O/'manifest.json');assert manifest['source_approved_fix_fields']==len(approved['changes']);assert manifest['final_Sol_reviewed_fulltext_rows']==len(ds)
print(json.dumps({'status':'passed','reviewed_rows':len(ds),'remaining_review_rows':109-len(ds),'raw_quote_checks':proof_count,'source_approved_fields':len(approved['changes']),'evidence_provenance_updates':len(evidence['changes']),'new_duplicate_pairs':0,'baseline_sha256':sha(baseline),'initial_proposals_unchanged':True,'canonical_changes_applied':False},indent=2))
