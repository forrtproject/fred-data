#!/usr/bin/env python3
"""Prepare blind A/B reads for records waiting for one more read. No model is called here."""
import hashlib
import json
import random
import sys
from collections import defaultdict

import build_field_ledger as L

sys.path.insert(0, str(L.B / 'scripts'))
import build_ledger_review as R  # noqa: E402

OUT = L.P / 'final_read_20261104'
CHUNK = 30000
SEED = 20261104
CHECKS = {802: None, 1868: None, 1927: ['outcome'], 1537: ['outcome'], 577: ['outcome'], 2655: ['outcome_computation'],
          726: ['outcome'], 1554: ['outcome'], 313: ['outcome'], 1246: ['outcome']}


def citation(authors, year, title):
    return ' '.join(x for x in [R.first_author(authors or ''), f'({year})' if year else '', title or ''] if x)


def readable(field, value, row=None):
    """One value as a reader should see it, with nothing that tells it apart as existing or proposed."""
    if field == 'original':
        return citation(row['author_o'], row['year_o'], row['title_o']) if row is not None else citation(value['authors'], value['year'], value['title'])
    if isinstance(value, dict):
        return {k: v for k, v in value.items()}
    return value


def order_for(request_id, field, salt=''):
    """Seeded, so the letters can be rebuilt but do not follow any pattern a reader could learn."""
    return random.Random(f'{SEED}:{request_id}:{field}:{salt}').random() < 0.5


def request_for(art, row, members, request_id, salt=''):
    source = art.frozen[row]
    relink = next((m['proposed_value'] for m in members if m['field'] == 'original' and (m['proposed_value'] or {}).get('title')), None)
    judged = citation(relink['authors'], relink['year'], relink['title']) if relink else citation(source['author_o'], source['year_o'], source['title_o'])
    fields, key = [], {}
    for member in members:
        field = member['field']
        existing = readable(field, member['frozen_value'], source if field == 'original' else None)
        proposed = readable(field, member['proposed_value'])
        swap = order_for(request_id, field, salt)
        fields.append(dict(field=field, value_A=proposed if swap else existing, value_B=existing if swap else proposed))
        key[field] = 'A' if swap else 'B'
    return dict(request_id=request_id, document_id=members[0]['document_id'], input_row_index=row,
                report=dict(title=source['title_r'], doi=source['doi_r'], year=source['year_r']),
                original_study_to_judge=judged, fields=fields), key


def write_request(art, payload, out):
    document = payload['document_id']
    assert document not in L.PROVIDER_HELD | L.SOURCE_ORDER_HELD | L.HEADER_ONLY, document
    text = (L.resolve(art.documents[document]['packet_path']) / 'article.txt').read_text()
    chunks = max(1, (len(text) + CHUNK - 1) // CHUNK)
    directory = out / payload['request_id']
    directory.mkdir(parents=True, exist_ok=True)
    payload = dict(payload, source_chunks=chunks, source_characters=len(text), source_sha256=hashlib.sha256(text.encode()).hexdigest())
    (directory / 'request.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n')
    return len(text), chunks


def batches_of(requests):
    batches, current, size = [], [], 0
    for request_id, characters in requests:
        if current and (size + characters > 180000 or len(current) >= 3):
            batches.append(current)
            current, size = [], 0
        current.append(request_id)
        size += characters
    if current:
        batches.append(current)
    return batches


def main():
    ledger = L.read(L.OUTPUT)
    art = L.Artifacts()
    by_row = defaultdict(list)
    for field in ledger['fields']:
        by_row[field['input_row_index']].append(field)
    pool = [(r, 'record', R.edits_of(m)) for r, m in sorted(by_row.items()) if R.bundle_view(m) == 'pending_read']
    assert len(pool) == 98
    for row, names in CHECKS.items():
        members = by_row[row] if names is None else [m for m in by_row[row] if m['field'] in names]
        pool.append((row, 'check', members))
    random.Random(SEED).shuffle(pool)
    OUT.mkdir(parents=True, exist_ok=True)
    mapping, sizes = {}, []
    for index, (row, kind, members) in enumerate(pool, 1):
        request_id = f'f{index:04d}'
        payload, key = request_for(art, row, members, request_id)
        characters, chunks = write_request(art, payload, OUT)
        mapping[request_id] = dict(kind=kind, row=row, document_id=members[0]['document_id'], proposed_letter=key,
                                   fields=[m['field'] for m in members], characters=characters, chunks=chunks)
        sizes.append((request_id, characters))
    batches = batches_of(sizes)
    (OUT / 'parent_map.json').write_text(json.dumps(dict(requests=mapping, batches=batches), indent=1) + '\n')
    print(json.dumps(dict(requests=len(pool), batches=len(batches), characters=sum(c for _, c in sizes)), indent=1))


if __name__ == '__main__':
    main()
