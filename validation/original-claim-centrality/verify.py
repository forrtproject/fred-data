"""Check the compact published artifacts; no inference or source-sheet writes."""
import collections
import csv
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(name):
    with (ROOT/name).open(newline='') as f:return list(csv.DictReader(f))
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
summary=json.loads((ROOT/'summary.json').read_text())
for name,value in summary['artifact_sha256'].items():assert sha(name)==value,name
rows=read('classifications.csv');sources={r['source_key']:r for r in read('sources.csv')}
by_uid={r['effect_uid']:r for r in rows}
assert len(rows)==len(by_uid)==2050 and len(sources)==704
assert dict(collections.Counter(r['classification'] or 'empty' for r in rows))==summary['classification_counts']
for r in rows:
    assert r['classification'] in ['central','not_central','unclear','']
    assert r['model']=='gpt-6.1-sol' and r['reasoning_effort']=='medium'
    assert r['source_text_sha256']==sources[r['doi_o']]['text_sha256']
    assert r['rationale'] and r['status']
reviews=read('claim-review.csv');assert len(reviews)==len({r['effect_uid'] for r in reviews})==182
assert dict(collections.Counter(r['review_role'] for r in reviews))==summary['claim_review_roles']
for r in reviews:
    assert r['effect_uid'] in by_uid and r['source_quote'] and r['source_locator']
    assert r['source_text_sha256']==sources[r['source_key']]['text_sha256']
    if r['review_role']=='fill_missing_claim':assert not r['current_claim_text'].strip()
    elif r['review_role']=='append_identification':
        old=r['current_claim_text'];proposed=old+'\n\n'+r['source_quote']
        assert old.strip() and proposed.startswith(old) and len(proposed)>len(old)
    else:assert r['review_role']=='evidence_only'
checks=read('identity-checks.csv');assert len(checks)==len({r['effect_uid'] for r in checks})==422
assert {r['effect_uid'] for r in checks}<=set(by_uid)
pilot=read('pilot-sample.csv');assert len(pilot)==len({r['effect_uid'] for r in pilot})==50
assert {r['effect_uid'] for r in pilot}<=set(by_uid)
assert summary['claim_text_updates_applied']==0
print('PASS: 2,050 unchanged classifications; 704 source records; 422 identity checks; 182 source excerpts; 131 context-preserving clarification candidates. LLM-coded and unvalidated.')
