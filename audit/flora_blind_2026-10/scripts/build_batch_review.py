"""Build conservative approval sets; never apply changes or infer outcomes."""
import csv
import hashlib
import json
from pathlib import Path
B = Path(__file__).resolve().parents[1]
H = B / 'handoff'

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def eligible_case(case, proposals):
    """A batch must include the complete unheld correction bundle for this row."""
    if case.get('row') is None or case.get('requires_review') or case.get('record_action'):
        return False
    if not proposals or set(case['changes']) != {p['field'] for p in proposals}:
        return False
    if any(p['status'] != 'evidence_checked_proposal' or p.get('application_hold') or p.get('application_dependency') or p.get('record_action_dependency') for p in proposals):
        return False
    if any(v.get('disposition') in {'reviewed_unknown','source_needed','policy_decision_required'} for v in case.get('final_review_summary',{}).values()):
        return False
    if not case.get('final_review_summary') and set(case.get('fields', [])) - set(case['changes']):
        return False
    return all(p['proposed_value'] == case['changes'][p['field']] for p in proposals)

def build():
    changes = json.loads((H/'correction_proposals.json').read_text())
    cases = json.loads((H/'review_queue.json').read_text())
    quote_rows = {x['input_row_index'] for x in json.loads((H/'evidence_provenance_fixes.json').read_text())['changes']}
    by_row = {}
    for p in changes['changes']:by_row.setdefault(p['input_row_index'],[]).append(p)
    groups = [dict(id='replication_outcomes',title='Replication outcomes',description='Outcome corrections with an unchanged study type and original-study identity.',items=[]),
              dict(id='reproduction_results',title='Reproduction results',description='Computation and robustness corrections, with the study type and original unchanged.',items=[]),
              dict(id='same_original_reference',title='Reference details for the same original',description='Citation corrections where the original DOI is unchanged; no study is relinked or removed.',items=[]),
              dict(id='confirmed_missing_pairs',title='Confirmed missing-pair identities',description='Source-confirmed absent pairs with complete citation identities and no record-level hold. Outcomes remain unassigned.',items=[])]
    group_map={g['id']:g for g in groups}
    for c in cases:
        ps=by_row.get(c.get('row'),[])
        if not eligible_case(c,ps) or c['row'] in quote_rows:continue
        original = next((p for p in ps if p['field']=='original'),None)
        fields={p['field'] for p in ps}
        group=None
        if fields=={'outcome'} and isinstance(ps[0]['proposed_value'],str):group='replication_outcomes'
        elif fields <= {'outcome_computation','outcome_robustness'} and all(isinstance(p['proposed_value'],str) for p in ps):group='reproduction_results'
        elif fields=={'original'} and isinstance(original['proposed_value'],dict):
            value=original['proposed_value'];before=original['expected_before']
            if value.get('doi') and value['doi'].lower()==before.get('doi_o','').lower() and all(value.get(k) for k in ['title','authors','year']):group='same_original_reference'
        if not group:continue
        operations=[]
        for p in ps:
            expected={k:p['expected_before'][k] for k in (['doi_o','title_o','author_o','year_o'] if p['field']=='original' else ['outcome'] if p['field'].startswith('outcome_') else [p['field']])}
            operations.append(dict(operation='update_original_reference' if p['field']=='original' else 'set_reproduction_axis' if p['field'].startswith('outcome_') else 'set_field',field=p['field'],expected_before=expected,proposed_value=p['proposed_value'],evidence_reference='correction_proposals.json',expected_before_full_record_sha256=p['expected_before_full_record_sha256']))
        group_map[group]['items'].append(dict(id=c['id'],case_id=c['id'],input_row_index=c['row'],title=c['title'],fields=sorted(fields),operations=operations))
    blocked_works={c['work'].lower() for c in cases if c.get('record_action') or any(v.get('disposition')=='policy_decision_required' for v in c.get('final_review_summary',{}).values())}
    with (H/'confirmed_missing_pairs.csv').open(encoding='utf-8-sig') as f:pairs=list(csv.DictReader(f))
    for p in pairs:
        if p['work_key'].lower() in blocked_works or not all(p[k].strip() and p[k].strip().lower() not in {'na','unknown'} for k in ['title','authors','year']):continue
        group_map['confirmed_missing_pairs']['items'].append(dict(id='pair:'+p['file_key']+':'+p['target_index'],title=p['title'],linked_case_id=('missing:'+p['file_key']+':'+p['target_index']) if any(c['id']=='missing:'+p['file_key']+':'+p['target_index'] for c in cases) else None,operations=[dict(operation='add_confirmed_pair',work_key=p['work_key'],file_key=p['file_key'],original={k:p[k] for k in ['doi','title','authors','year']},outcome=None,outcome_status='not_adjudicated',evidence_reference='confirmed_missing_pairs.csv',audit_source_confirmation_sha256=digest(p),target_index=p['target_index'])]))
    for g in groups:
        g['fingerprint']=digest(g['items']);g['item_count']=len(g['items']);g['operation_count']=sum(len(i['operations']) for i in g['items'])
    result=dict(schema_version=1,baseline_sha256=changes['baseline_sha256'],groups=groups,
        exclusions=['Record inclusion, source replacements, duplicates and linked changes','Coding-policy choices and unresolved evidence or identity','Quote replacements: public excerpts must not be applied as full source quotations','Original-study relinks and incomplete missing-pair citations'],
        rule='Approve complete unheld bundles only. Preserve existing user decisions. Apply only after frozen baseline and full-record preconditions pass.',canonical_changes_applied=False)
    (H/'batch_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result
if __name__=='__main__':
    print(json.dumps({g['id']:dict(items=g['item_count'],operations=g['operation_count']) for g in build()['groups']},indent=2))
