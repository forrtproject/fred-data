#!/usr/bin/env python3
"""Parent-approved missing-reference checks; preserve validated prior outcomes."""
import hashlib
import json
from pathlib import Path

import adjudicate as a
import compare as c

R = Path(__file__).resolve().parents[1]
F = R / 'evidence_followup'


def integrate():
    inspected = json.loads((F / 'candidate_reviews/parent_inspection.json').read_text())['reviews']
    merged = []
    index = json.loads((F / 'candidate_requests/index.json').read_text())
    for rid, inspection in inspected.items():
        if inspection.get('status') != 'approved':
            continue
        assert inspection.get('reason')
        validation = json.loads((F / 'candidate_reviews' / (rid + '.validation.json')).read_text())
        assert validation['valid_envelope']
        approved = {tuple(x) for x in inspection['approved_keys']}
        superseded = {tuple(x) for x in inspection.get('superseded_keys', [])}
        assert superseded <= approved
        if superseded:
            assert inspection.get('supersession_reason'), 'New evidence supersession needs provenance'
        approved -= superseded
        fields = inspection.get('review_kind') == 'fields'
        def approval_key(d):
            return (d['file_key'], str(d['input_row_index']), d['field']) if fields else (d['file_key'], d['target_index'])
        selected = [x for x in validation['records']
                    if approval_key(x['decision']) in approved]
        assert len(selected) == len(approved)
        for item in selected:
            decision = item['decision']
            fk = decision['file_key']
            sourcepath = R / 'texts' / (fk + '.txt')
            source = sourcepath.read_text()
            assert hashlib.sha256(sourcepath.read_bytes()).hexdigest() == item['source_sha256']
            assert item['mechanically_valid'] and c.valid_decision(decision, source)
            target = R / 'adjudications' / (fk + '.json')
            obj = c.read_json(target)[0] or {'decisions': []}
            old = [x for x in obj['decisions'] if a.decision_key(x) == a.decision_key(decision)]
            assert len(old) <= 1
            retain = (not fields and old and old[0]['verdict'] in ('blind_right', 'both_wrong')
                      and decision['verdict'] in ('blind_right', 'both_wrong'))
            # Identity rechecks do not downgrade an independently verified outcome.
            if retain:
                before, after = old[0].get('corrected_value'), decision.get('corrected_value')
                if isinstance(before, dict) and isinstance(after, dict):
                    if c.clean_doi(before.get('doi')) and c.clean_doi(after.get('doi')):
                        assert c.clean_doi(before['doi']) == c.clean_doi(after['doi']), 'Identity disagreement needs explicit review'
            elif old and old[0]['verdict'] != 'undeterminable' and old[0] != decision:
                assert inspection.get('explicit_supersession_reason'), 'Prior substantive omission/exclusion cannot silently change'
            archive = F / 'integration/prior_adjudications' / target.name
            if target.exists() and not archive.exists():
                archive.parent.mkdir(exist_ok=True)
                archive.write_bytes(target.read_bytes())
            if not retain:
                obj['decisions'] = [x for x in obj['decisions'] if a.decision_key(x) != a.decision_key(decision)]
                obj['decisions'].append(decision)
            history = obj.setdefault('evidence_followup_candidate_rechecks', [])
            entry = {'review_id': rid, 'decision_key': list(a.decision_key(decision)),
                     'decision_path': 'evidence_followup/candidate_reviews/' + rid + '.result.json',
                     'prior_outcome_preserved': bool(retain),
                     'parent_inspection': 'evidence_followup/candidate_reviews/parent_inspection.json'}
            if entry not in history:
                history.append(entry)
            a.atomic(target, obj)
            merged.append(approval_key(decision))
        for entry in index:
            if entry.get('review_id') == rid:
                entry['status'] = 'parent_inspected_integrated'
    a.atomic(F / 'candidate_requests/index.json', index)
    return {'approved_rechecks_or_additions': len(merged)}


if __name__ == '__main__':
    print(json.dumps(integrate()))
