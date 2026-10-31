#!/usr/bin/env python3
"""Independent checks for Argon decisions quoting primary project CSV endpoints.

This verifies evidence, not a new outcome inference: the expert must already have
returned the same outcome, identity must already be resolved, and the original
authors' final codes must be unambiguous 0/1 endpoints. Everything else stays for
individual source review. Model confidence is never used.
"""
import collections
import csv
import io
import json
from pathlib import Path
import re

import adjudicate as a
import compare as c

R = Path(__file__).resolve().parents[1]
F = R / 'evidence_followup'
FK = '2736b815e9f115a4'


def endpoint(row):
    value = row.get('adjudicated_replication_code', '').strip()
    if value.lower() in ('na', 'n/a', ''):
        first, second = (row.get(x, '').strip() for x in
                         ('replicated_instructor_code', 'replicated_report_code'))
        if first != second:
            return None
        value = first
    return {'0': 'failed', '1': 'successful'}.get(value)


def check():
    source = (R / 'texts' / (FK + '.txt')).read_text()
    header = next(line for line in source.splitlines() if line.startswith('target_lastauthor_year,student_name_shared,'))
    names = next(csv.reader([header]))
    start = source.index(header) + len(header) + 1
    records = []
    for row in csv.reader(io.StringIO(source[start:])):
        if not row:
            continue
        if len(row) != len(names):
            break
        records.append(dict(zip(names, row)))
    assert len(records) > 100, 'Primary project table not identified'
    citation_key = lambda row: ' '.join(c.tokens(row.get('target_cite', '')))
    citations = collections.Counter(citation_key(x) for x in records)
    links = collections.Counter(x.get('article_link', '').strip().lower().rstrip('/') for x in records)
    rows = {x['input_row_index']: x for x in c.read_csv(R / 'results.csv')}
    coding = json.loads((R / 'codings' / (FK + '.json')).read_text())
    snapshot = json.loads((F / 'argon/snapshot.json').read_text())
    checked = []
    for request in snapshot['requests']:
        if request['file_key'] != FK:
            continue
        path = F / 'argon' / (request['request_id'] + '.result.json')
        statepath = F / 'argon' / (request['request_id'] + '.state.json')
        if not path.exists() or not statepath.exists():
            continue
        state = json.loads(statepath.read_text())
        if state['status'] != 'validated':
            continue  # do not inspect a reply while a retry can replace it
        obj = json.loads(path.read_text())
        for decision in obj['decisions']:
            errors = []
            row = rows[str(decision['input_row_index'])]
            if not (row['original_final_verdict'] == 'correct' and row['identity_resolved'] == 'True'):
                errors.append('original identity not already source-resolved')
            if decision['field'] != 'outcome' or not c.valid_decision(decision, source):
                errors.append('not a validated original-specific replication outcome')
            parsed = list(csv.reader(io.StringIO(decision['quote'])))
            record = dict(zip(names, parsed[0])) if len(parsed) == 1 and len(parsed[0]) == len(names) else None
            if record not in records:
                errors.append('quotation is not exactly one complete primary CSV record')
            if record in records:
                if record.get('replication_report_included', '').lower() != 'no':
                    errors.append('included primary replication report needs its own overall-verdict check')
                if citations[citation_key(record)] != 1 or links[record['article_link'].strip().lower().rstrip('/')] != 1:
                    errors.append('original appears in more than one primary project record')
                target = coding['targets'][int(row['blind_target_index'])]
                family, year = c.surname(target.get('authors', '')), str(target.get('year', ''))
                if not family or not year or c.tokens(family)[0] not in c.tokens(record['target_cite']) or year not in record['target_cite']:
                    errors.append('primary citation does not establish the paired blind original identity')
                study = str(target.get('study_numbers', '')).strip()
                if study and re.sub(r'\.0$', '', study).lower() != re.sub(r'\.0$', '', record['study_number']).lower():
                    errors.append('specific original-study number differs or is not a singleton')
                if endpoint(record) is None or endpoint(record) != decision.get('corrected_value'):
                    errors.append('not an unambiguous matching author-coded 0/1 endpoint')
            checked.append({'request_id': request['request_id'], 'decision_key': list(a.decision_key(decision)),
                'input_row_index': decision['input_row_index'], 'verdict': decision['verdict'],
                'value': decision.get('corrected_value'), 'primary_record': record.get('target_lastauthor_year') if record else None,
                'primary_citation': record.get('target_cite') if record else None,
                'author_final_code': record.get('adjudicated_replication_code') if record else None,
                'author_report_code': record.get('replicated_report_code') if record else None,
                'checks_passed': not errors, 'requires_individual_review': errors})
    a.atomic(F / 'integration/project_endpoint_checks.json', {'records': checked,
        'basis': 'Primary OSF table plus article section4.3.1; original identity already resolved; exact one-record quote; unique original; matching expert verdict and explicit authors 0/1 endpoint only. No intermediate or conflicting scores are classified.'})
    return checked


if __name__ == '__main__':
    records = check()
    print(json.dumps({'checked': len(records), 'passed': sum(x['checks_passed'] for x in records),
                      'passed_rows': [(x['input_row_index'], x['primary_record'], x['value']) for x in records if x['checks_passed']],
                      'exceptions': [(x['input_row_index'], x['requires_individual_review']) for x in records if not x['checks_passed']]}))
