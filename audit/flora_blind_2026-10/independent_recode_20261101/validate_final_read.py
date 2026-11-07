#!/usr/bin/env python3
"""Check final reads mechanically and apply the predeclared decision rule. The rule lives here, not in the readers."""
import json
import os
import sys
from collections import Counter

import build_field_ledger as L

OUT = L.P / os.environ.get('FINAL_READ_FOLDER', 'final_read_20261104')
ANSWERS = {'better': {'A', 'B', 'neither', 'cannot_tell'}, 'other_value': {'contradicted', 'defensible', 'not_applicable'},
           'confidence': {'high', 'medium', 'low'}}


def mechanical_problems(request, review, receipts, source):
    problems = []
    if review.get('request_id') != request['request_id'] or review.get('input_row_index') != request['input_row_index']:
        problems.append('wrong_request')
    served = {r['chunk'] for r in receipts}
    if served != set(range(request['source_chunks'])):
        problems.append('missing_chunk_receipts')
    answers = {a.get('field'): a for a in review.get('fields', [])}
    if set(answers) != {f['field'] for f in request['fields']}:
        problems.append('wrong_fields')
    for answer in answers.values():
        for key, allowed in ANSWERS.items():
            if answer.get(key) not in allowed:
                problems.append('invalid_' + key)
    for quote in review.get('supporting_quotes', []):
        if not L.literal_in_source(quote.get('quote', ''), source):
            problems.append('supporting_quote_not_literal')
    replacement = review.get('replacement_quote')
    if replacement and not L.literal_in_source(replacement, source):
        problems.append('replacement_quote_not_literal')
    return sorted(set(problems))


def field_verdict(answer, proposed_letter, same_finding, quote_ok):
    """Apply the protocol to one field. Anything short of a clear 'correct' keeps the existing value."""
    if answer['better'] == 'neither' and answer['confidence'] == 'high' and same_finding:
        return 'other_value'
    if (answer['better'] == proposed_letter and answer['other_value'] == 'contradicted'
            and answer['confidence'] == 'high' and same_finding and quote_ok):
        return 'correct'
    return 'keep_existing'


def record_verdicts(fields, verdicts):
    """A type and its results apply together, and an original comes before an outcome judged against it."""
    for lead in ('type', 'original'):
        if lead in fields and verdicts[lead] != 'correct':
            return {f: ('keep_existing' if f != lead else verdicts[f]) for f in fields}
    return verdicts


def decide(request, review, entry, source_ok=True):
    same = review.get('same_finding') is True
    quote_ok = source_ok and bool(review.get('replacement_quote') or set(entry['fields']) <= {'original', 'type'})
    answers = {a['field']: a for a in review['fields']}
    verdicts = {f: field_verdict(answers[f], entry['proposed_letter'][f], same, quote_ok) for f in entry['fields']}
    return record_verdicts(entry['fields'], verdicts)


def main(folder=OUT):
    mapping = json.loads((folder / 'parent_map.json').read_text())['requests']
    artifacts = L.Artifacts()
    results, missing, failures = {}, [], {}
    for request_id, entry in sorted(mapping.items()):
        directory = folder / request_id
        if not (directory / 'review.json').exists():
            missing.append(request_id)
            continue
        request = json.loads((directory / 'request.json').read_text())
        try:
            review = json.loads((directory / 'review.json').read_text())
        except ValueError:
            failures[request_id] = ['invalid_json']
            continue
        receipts_path = directory / 'read_receipts.jsonl'
        receipts = [json.loads(x) for x in receipts_path.read_text().splitlines()] if receipts_path.exists() else []
        source = L.spaced((L.resolve(artifacts.documents[entry['document_id']]['packet_path']) / 'article.txt').read_text())
        problems = mechanical_problems(request, review, receipts, source)
        if problems:
            failures[request_id] = problems
            continue
        results[request_id] = dict(kind=entry['kind'], row=entry['row'], verdicts=decide(request, review, entry),
                                   confidence={a['field']: a['confidence'] for a in review['fields']},
                                   summary=review.get('plain_language_summary', ''), integrity=review.get('source_integrity_note', ''))
    return dict(results=results, missing=missing, failures=failures)


if __name__ == '__main__':
    out = main()
    field_counts = Counter(v for r in out['results'].values() if r['kind'] == 'record' for v in r['verdicts'].values())
    checks = {r['row']: r['verdicts'] for r in out['results'].values() if r['kind'] == 'check'}
    print(json.dumps(dict(done=len(out['results']), missing=len(out['missing']), failures=out['failures'],
                          field_verdicts=field_counts, checks=checks), indent=1))
    sys.exit(0)
