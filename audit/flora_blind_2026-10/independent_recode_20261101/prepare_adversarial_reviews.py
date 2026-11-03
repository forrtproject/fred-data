#!/usr/bin/env python3
"""Prepare adversarial review requests from the ledger. No model is called here."""
import hashlib
import json
import random
import re
from collections import defaultdict
from pathlib import Path

import build_field_ledger as L

OUT = L.P / 'adversarial_20261103'
CHUNK = 30000
SEED = 20261103
REASON_KEYS = ('reason', 'comparison_scope_note', 'known_limits', 'source_limits', 'parent_scientific_comparison',
               'field_specific_caution', 'parent_coding_review_note')


def humanize(label):
    return re.sub(r'_+', ' ', label or '').strip()


def role_view(coding_path, field, proposed, identity):
    if not coding_path:
        return None
    coding = L.read(L.resolve(coding_path))
    view = dict(record_type=coding.get('record_type'), study_status=coding.get('study_status'),
                evidence_level=coding.get('evidence_level'), targets=[])
    for target in coding.get('targets', []):
        if L.target_binding(target, identity):
            view['targets'].append({k: target.get(k) for k in (
                'authors', 'year', 'title', 'doi', 'identified_by', 'study_numbers', 'replication_study_numbers',
                'evidence_quote', 'outcome', 'outcome_quote', 'outcome_quote_section', 'outcome_computation',
                'outcome_computational_quote', 'outcome_robustness', 'outcome_robustness_quote', 'outcome_confident')})
    view['other_target_count'] = len(coding.get('targets', [])) - len(view['targets'])
    return view


def request_for(art, row_index, members, queue, overrides=None):
    overrides = overrides or {}
    row = art.frozen[row_index]
    relink = next((m['proposed_value'] for m in members if m['field'] == 'original' and 'title' in (m['proposed_value'] or {})), None)
    identity = L.identity_of_proposal(relink) if relink else L.identity_of_row(row)
    document = members[0]['document_id']
    entry = queue.get(document, {})
    fields = []
    for member in members:
        fields.append(dict(field=member['field'], frozen_value=member['frozen_value'],
                           proposed_value=overrides.get('proposed_value', member['proposed_value'])))
    notes = {k: entry[k] for k in REASON_KEYS if entry.get(k)}
    opus = role_view(members[0]['opus']['path'], members[0]['field'], members[0]['proposed_value'], identity)
    sol = role_view(members[0]['sol']['path'], members[0]['field'], members[0]['proposed_value'], identity)
    if overrides.get('coded_value') is not None:
        for view in (opus, sol):
            for target in view['targets']:
                target['outcome'] = overrides['coded_value']
    return dict(
        document_id=document, input_row_index=row_index,
        frozen_record=dict(original=dict(doi=row['doi_o'], title=row['title_o'], authors=row['author_o'], year=row['year_o']),
                           report=dict(doi=row['doi_r'], title=row['title_r'], year=row['year_r']), type=row['type'], outcome=row['outcome']),
        proposed_changes=fields,
        role_one_reading=opus, role_two_reading=sol,
        recorded_flag=humanize(entry.get('status')) if L.parent_flag(entry.get('status') or '') else None,
        recorded_notes=notes)


def main():
    ledger = L.read(L.OUTPUT)
    art = L.Artifacts()
    by_row = defaultdict(list)
    for field in ledger['fields']:
        by_row[field['input_row_index']].append(field)
    pool = [row for row, members in sorted(by_row.items())
            if {m['state'] for m in members} == {'agreement_pending_adversarial_review'}
            and {m['current']['relation'] for m in members} == {'unchanged_from_frozen'}]
    requests = [dict(kind='candidate', row=row, payload=request_for(art, row, by_row[row], art.queue)) for row in pool]
    negatives = [by_row[802], by_row[1868]]
    for members in negatives:
        requests.append(dict(kind='negative_canary', row=members[0]['input_row_index'],
                             payload=request_for(art, members[0]['input_row_index'], members, art.queue)))
    planted = [members for row, members in sorted(by_row.items())
               if {m['state'] for m in members} == {'withdraw_both_roles_confirm_frozen'} and members[0]['field'] == 'outcome'
               and members[0]['frozen_value'] == 'successful']
    for members in planted[:2]:
        requests.append(dict(kind='negative_canary_planted', row=members[0]['input_row_index'],
                             payload=request_for(art, members[0]['input_row_index'], members, art.queue,
                                                 dict(proposed_value='failed', coded_value='failed'))))
    positives = [c for c in art.export['cases'] if c['proposal_fields'] == ['outcome']][:2]
    for case in positives:
        members = by_row[case['input_row_index']]
        requests.append(dict(kind='positive_canary', row=case['input_row_index'],
                             payload=request_for(art, case['input_row_index'], members, art.queue)))
    random.Random(SEED).shuffle(requests)
    private_map, batches, current = {}, [], []
    size = 0
    for index, item in enumerate(requests, 1):
        request_id = f'r{index:04d}'
        document = item['payload']['document_id']
        assert document not in L.PROVIDER_HELD | L.SOURCE_ORDER_HELD | L.HEADER_ONLY
        source = art.documents[document]['packet_path']
        text = (L.resolve(source) / 'article.txt').read_text()
        chunks = max(1, (len(text) + CHUNK - 1) // CHUNK)
        directory = OUT / request_id
        directory.mkdir(parents=True, exist_ok=True)
        payload = dict(item['payload'], request_id=request_id, source_chunks=chunks, source_characters=len(text),
                       source_sha256=hashlib.sha256(text.encode()).hexdigest())
        (directory / 'request.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n')
        private_map[request_id] = dict(kind=item['kind'], row=item['row'], document_id=document, characters=len(text), chunks=chunks)
        if current and (size + len(text) > 180000 or len(current) >= 3):
            batches.append(current)
            current, size = [], 0
        current.append(request_id)
        size += len(text)
    if current:
        batches.append(current)
    (OUT / 'parent_map.json').write_text(json.dumps(dict(requests=private_map, batches=batches), indent=1) + '\n')
    print(json.dumps(dict(requests=len(requests), pool=len(pool), batches=len(batches),
                          characters=sum(v['characters'] for v in private_map.values())), indent=1))


if __name__ == '__main__':
    main()
