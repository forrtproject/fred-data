"""Build a standalone human spot-checker; no source-sheet writes or PDFs bundled."""
import csv
import hashlib
import json
import random
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
source=ROOT/'claim-review.csv'
sources={r['source_key']:r for r in read(ROOT/'sources.csv')}
rows=[]
for r in read(source):
    f=sources[r['source_key']]
    rows.append(dict(uid=r['effect_uid'],reference=f['reference'],source_key=r['source_key'],old=r['current_claim_text'],quote=r['source_quote'],role=r['review_role'],kind='Table excerpt' if 'table' in r['quote_type'].lower() else 'Prose',locator=r['source_locator'],paper=f['provided_link'] or f['source_url'],alternate=f['source_url'],limitation=r['numerical_matching_limitation'],statistic=r['recorded_statistic'],text_hash=r['source_text_sha256'],quote_hash=hashlib.sha256(r['source_quote'].encode()).hexdigest()))
assert len(rows)==len({r['uid'] for r in rows})==182
rng=random.Random(20261111);groups={}
for r in rows:
    if r['role']!='evidence_only':groups.setdefault(r['source_key'],[]).append(r['uid'])
keys=rng.sample(sorted(groups),10);sample=[rng.choice(sorted(groups[k])) for k in keys]
payload=json.dumps(dict(rows=rows,sample=sample,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),legacy_source_sha256='519ce7417abc2819f2a79c799ae4c4f11a41af0f65b5db30581d406f6e7aef9d'),ensure_ascii=False).replace('<','\\u003c')
html=(ROOT/'quote-spotcheck-template.html').read_text().replace('__REVIEW_DATA__',payload)
(ROOT/'quote-spotcheck.html').write_text(html)
print(f'Built quote-spotcheck.html: {len(rows)} evidence excerpts; clarification sampler from {len(groups)} originals.')
