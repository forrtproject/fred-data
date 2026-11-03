#!/usr/bin/env python3
"""Check adversarial reviews mechanically and register results for the ledger."""
import hashlib
import json
from collections import Counter
from pathlib import Path

import build_field_ledger as L

OUT = L.P / 'adversarial_20261103'
REGISTRY = L.T / 'adversarial_review_registry.json'
VERDICTS = {'supported', 'not_supported', 'policy_boundary', 'evidence_limit'}
GROUPS = set(L.POLICY_GROUPS) | set(L.EXTRA_POLICY_QUESTIONS) | {'other_individual', None}
MAX_REPLACEMENT = 1500


def validate(review, request, source, receipts):
    """Return a list of failures; an empty list means the review is mechanically sound."""
    failures = []
    if review.get('request_id') != request['request_id']:
        failures.append('request_id')
    if review.get('document_id') != request['document_id'] or review.get('input_row_index') != request['input_row_index']:
        failures.append('identity')
    verdict = review.get('verdict')
    if verdict not in VERDICTS:
        return failures + ['verdict']
    if review.get('confidence') not in ('high', 'medium', 'low'):
        failures.append('confidence')
    if {r.get('chunk') for r in receipts} != set(range(request['source_chunks'])):
        failures.append('incomplete_read')
    if review.get('policy_group') not in GROUPS:
        failures.append('policy_group')
    if verdict != 'supported':
        return failures
    if review.get('confidence') != 'high':
        failures.append('supported_without_high_confidence')
    if review.get('same_finding') is not True:
        failures.append('same_finding')
    named = {c['field']: c['proposed_value'] for c in request['proposed_changes']}
    addressed = {f.get('field'): f.get('supported_value') for f in review.get('fields', [])}
    if set(addressed) != set(named):
        failures.append('fields_not_addressed')
    for name, value in named.items():
        if name != 'original' and addressed.get(name) != value:
            failures.append('field_value_differs:' + name)
    if request.get('recorded_flag') and not (review.get('flag_answer') or '').strip():
        failures.append('flag_not_answered')
    supporting = review.get('supporting_quotes') or []
    counter = review.get('strongest_counterevidence') or {}
    replacement = review.get('replacement_quote') or ''
    if not supporting or not all(L.literal_in_source(q.get('quote'), source) for q in supporting):
        failures.append('supporting_quote_not_literal')
    if not L.literal_in_source(counter.get('quote'), source):
        failures.append('counterevidence_not_literal')
    if not L.literal_in_source(replacement, source) or len(replacement) > MAX_REPLACEMENT or '||' in replacement:
        failures.append('replacement_quote')
    if not (review.get('replacement_quote_section') or '').strip():
        failures.append('replacement_section')
    return failures


def collect():
    plan = json.loads((OUT / 'parent_map.json').read_text())
    bundles, canaries, states = {}, {}, Counter()
    for request_id, item in sorted(plan['requests'].items()):
        directory = OUT / request_id
        path = directory / 'review.json'
        if not path.exists():
            states['pending'] += 1
            continue
        request = json.loads((directory / 'request.json').read_text())
        review = json.loads(path.read_text())
        art_source = L.resolve(next(iter([request])) and _packet(request['document_id'])) / 'article.txt'
        source = L.spaced(art_source.read_text())
        receipts_path = directory / 'read_receipts.jsonl'
        receipts = [json.loads(line) for line in receipts_path.read_text().splitlines()] if receipts_path.exists() else []
        failures = validate(review, request, source, receipts)
        states['valid' if not failures else 'failed'] += 1
        record = dict(request_id=request_id, document_id=request['document_id'], verdict=review.get('verdict'),
                      confidence=review.get('confidence'), policy_group=review.get('policy_group'),
                      quote_verified=not failures, failures=failures, summary=review.get('plain_language_summary', '')[:600],
                      review_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        if item['kind'] == 'candidate':
            bundles['row:%d' % item['row']] = record
        else:
            canaries[request_id] = dict(record, kind=item['kind'], row=item['row'])
    outcome = dict(
        schema_version=1, protocol_sha256=hashlib.sha256((L.T / 'adversarial_review_protocol.json').read_bytes()).hexdigest(),
        states=dict(states), verdicts=dict(Counter(b['verdict'] for b in bundles.values())),
        stop_rule_S1_tripped=[r for r, c in canaries.items() if c['kind'].startswith('negative') and c['verdict'] == 'supported'],
        positive_canaries_rejected=[r for r, c in canaries.items() if c['kind'] == 'positive_canary' and c['verdict'] != 'supported'],
        canaries=canaries, bundles=bundles, adds_blind_votes=False, user_approval_recorded=False)
    REGISTRY.write_text(json.dumps(outcome, ensure_ascii=False, indent=1) + '\n')
    return outcome


def _packet(document):
    upgrades = {u['document_id']: u for u in L.read(L.T / 'source_upgrades.json')['upgrades']}
    inventory = {d['document_id']: d for d in L.read(L.T / 'source_inventory.json')['documents']}
    return (upgrades.get(document) or inventory[document])['packet_path']


if __name__ == '__main__':
    result = collect()
    print(json.dumps({k: result[k] for k in ('states', 'verdicts', 'stop_rule_S1_tripped', 'positive_canaries_rejected')}, indent=1))
