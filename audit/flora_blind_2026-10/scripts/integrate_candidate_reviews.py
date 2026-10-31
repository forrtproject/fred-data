#!/usr/bin/env python3
"""Parent-approved missing-reference checks; preserve validated prior outcomes."""
import hashlib
import json
from pathlib import Path

import adjudicate as a
import compare as c

R = Path(__file__).resolve().parents[1]
F = R / 'evidence_followup'


def mark_parent_coverage(entry, records, inspected_keys, fields=False):
    """A partial parent approval must not close other requests in its envelope."""
    def key(d):
        return ((d['file_key'], str(d['input_row_index']), d['field']) if fields
                else (d['file_key'], d['target_index']))
    expected = {key(x['decision']) for x in records
                if x['decision'].get('request_id') == entry['request_id']}
    if not expected:
        raise ValueError('No validated keys for parent request ' + entry['request_id'])
    covered = expected & inspected_keys
    pending = expected - covered
    entry['parent_inspected_keys'] = [list(k) for k in sorted(covered, key=str)]
    entry['parent_pending_keys'] = [list(k) for k in sorted(pending, key=str)]
    entry['status'] = ('expert_review_complete_pending_parent' if pending
                       else 'parent_inspected_integrated')


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
        if selected:
            payload = json.loads((F / 'candidate_reviews' / (rid + '.input.json')).read_text())
        for item in selected:
            decision = dict(item['decision'])
            fk = decision['file_key']
            requests = [w for w in payload['requests']
                        if w['request_id'] == decision['request_id'] and w['file_key'] == fk]
            assert len(requests) == 1, 'Decision needs one matching immutable input request'
            request = requests[0]
            assert a.decision_key(decision) in {a.decision_key(x) for x in request['requested_fields']}, 'Unrequested decision key'
            sourcepath = Path(request['source_path']).resolve()
            raw = sourcepath.read_bytes()
            source = raw.decode('utf-8')
            sourcehash = hashlib.sha256(raw).hexdigest()
            assert sourcehash == item['source_sha256']
            if sourcepath != (R / 'texts' / (fk + '.txt')).resolve():
                registry = F / 'additional_reports/approved_sources.json'
                assert registry.exists(), 'Unregistered review source'
                reports = [report for report in json.loads(registry.read_text())['reports']
                           if report['status'] == 'approved_for_comparison'
                           and report['collection_file_key'] == fk
                           and report['work_key'] == request['work_key']
                           and Path(report['text_path']).resolve() == sourcepath
                           and report['text_sha256'] == sourcehash]
                assert len(reports) == 1, 'Review source needs one exact approved report'
                # Reuse all private-path, work, raw-hash and fresh blind-code guards.
                c.primary_text(R, fk, request['work_key'])
                decision.update(source_report_id=reports[0]['report_id'], source_text_sha256=sourcehash)
            assert item['mechanically_valid'] and c.valid_decision(decision, source) and decision['quote'] in source
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
                # Explicitly superseded keys retain their parent inspection;
                # unapproved keys still require their own scientific disposition.
                mark_parent_coverage(entry, validation['records'], approved | superseded, fields)
    a.atomic(F / 'candidate_requests/index.json', index)
    return {'approved_rechecks_or_additions': len(merged)}


if __name__ == '__main__':
    print(json.dumps(integrate()))
