#!/usr/bin/env python3
"""Write the final list of replications missing from FLoRA. Applies nothing."""
import csv
import json
import re

import build_field_ledger as L
import fetch_original_metadata as M

CHECK = L.P / 'missing_check_20261104'
OUT = L.B / 'handoff/missing_links_to_add.csv'
RECORD = L.T / 'missing_link_check_20261104.json'
# Each of these is in FLoRA already. The ids were found by a stricter match and confirmed by eye.
CONFIRMED_ALREADY = {
    'Anchor precision influences the amount of adjustment': 'FLORA-002142',
    "Preschoolers' perspective taking in word learning": 'FLORA-002148',
    'Errors Are Aversive: Defensive Motivation': 'FLORA-002139',
    'The sunny side of fairness': 'FLORA-002813',
    'Handedness and specific language impairment': 'VAL-000446',
    'Cerebral dominance for language function in adults': 'VAL-000346',
}
READ_ALREADY = {'m0002': 'FLORA-002290', 'm0003': 'FLORA-000916', 'm0004': 'FLORA-002861', 'm0005': 'FLORA-002278', 'm0007': 'FLORA-002284', 'm0008': 'FLORA-000334',
                'm0009': 'FLORA-002276', 'm0011': 'FLORA-002137', 'm0014': 'FLORA-002158', 'm0015': 'FLORA-002361', 'm0016': 'FLORA-002226', 'm0019': 'FLORA-002317',
                'm0020': 'FLORA-002268', 'm0021': 'FLORA-000588', 'm0022': 'FLORA-002142', 'm0024': 'FLORA-002146', 'm0025': 'FLORA-002135'}
READ_CONFIRMED = ['m0010', 'm0013', 'm0018']
READ_UNCONFIRMED = {'m0001': 'Named among earlier findings, but not the main target.', 'm0006': 'Only the abstract and references were available.',
                    'm0012': 'A re-assessment of a systematic review, not a re-test of a finding.', 'm0017': 'Not the main target; used as a basis for a hypothesis.',
                    'm0023': 'Not the main target; the report mainly replicates a later paper.'}


def nt(text):
    return re.sub(r'[^a-z0-9]', '', (text or '').lower())


def main():
    ledger = L.read(L.OUTPUT)
    art = L.Artifacts()
    mapping = json.loads((CHECK / 'parent_map.json').read_text())['requests']
    with (L.B / 'handoff/confirmed_missing_pairs.csv').open(encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    already, keep = [], []
    for row in rows:
        hit = next((flora for start, flora in CONFIRMED_ALREADY.items() if nt(row['title']).startswith(nt(start))), None)
        if hit and row['work_key']:
            already.append(dict(title=row['title'], work_key=row['work_key'], flora_id=hit))
        else:
            keep.append(row)
    assert len(already) == 6, len(already)
    added, read_records = [], {}
    for request_id, entry in mapping.items():
        review = json.loads((CHECK / request_id / 'review.json').read_text())
        status = 'already_in_flora' if request_id in READ_ALREADY else 'confirmed_missing' if request_id in READ_CONFIRMED else 'unconfirmed'
        read_records[entry['document_id']] = dict(status=status, flora_id=READ_ALREADY.get(request_id), note=READ_UNCONFIRMED.get(request_id, ''),
                                                  reader_answer=review['retests'], reader_confidence=review['confidence'], title=entry['title'], year=entry['year'], work_key=entry['work_key'])
        if status == 'confirmed_missing':
            doi = ''
            proposal = dict(title=entry['title'], authors=entry['authors'], year=entry['year'], doi=entry['doi'])
            try:
                candidate = entry['doi'] or M.search_by_title(proposal)
                if candidate and not M.check(dict(proposal, doi=candidate), json.loads(M.fetch(candidate).read_text())['message']):
                    doi = candidate
            except Exception:  # An unverified DOI is left out.
                doi = ''
            added.append(dict(work_key=entry['work_key'], title=entry['title'], authors=entry['authors'], year=entry['year'], doi=doi, source='final read 2026-11-04'))
    fieldnames = ['work_key', 'title', 'authors', 'year', 'doi', 'evidence_level', 'source']
    with OUT.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for row in keep:
            writer.writerow(dict(row, source='audit, confirmed against the paper'))
        for row in added:
            writer.writerow(dict(row, evidence_level='full_text'))
    candidates = ledger['outside_proposal_scope']['new_two_role_target_candidates']['examples']
    by_title = [dict(document_id=c['document_id'], title=c['title'], year=c['year'], work_key=c['work_key'], status='already_in_flora_by_title_match_not_read')
                for c in candidates if c['document_id'] not in read_records]
    data = dict(schema_version=1, date='2026-11-04',
                totals=dict(to_add=len(keep) + len(added), from_audit=len(keep), from_final_read=len(added), audit_already_in_flora=len(already),
                            later_candidates=len(candidates), later_already_by_title=len(by_title), later_already_after_read=len(READ_ALREADY), later_confirmed=len(READ_CONFIRMED), later_unconfirmed=len(READ_UNCONFIRMED),
                            unconfirmed_total=ledger['outside_proposal_scope']['pairs']['unresolved_missing_candidate']['items'] + len(READ_UNCONFIRMED)),
                audit_list_already_in_flora=already, later_candidates_read=read_records, later_candidates_by_title=by_title, added=added,
                limit='The check for duplicates matches on report link, title, author and year. It reduces false alarms but cannot rule them all out.')
    RECORD.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(data['totals']), json.dumps(added, ensure_ascii=False)[:600])


if __name__ == '__main__':
    main()
