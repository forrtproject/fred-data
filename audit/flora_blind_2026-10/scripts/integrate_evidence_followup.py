#!/usr/bin/env python3
"""Merge only explicitly parent-approved, source-validated request decisions."""
import copy
import hashlib
import json
from pathlib import Path
import sys

import adjudicate as a
import compare as c

R = Path(__file__).resolve().parents[1]
F = R / 'evidence_followup'


def integrate():
    inspected = json.loads((F / 'integration/parent_inspection.json').read_text())['requests']
    snapshot = json.loads((F / 'argon/snapshot.json').read_text())
    byrequest = {x['request_id']: x for x in snapshot['requests']}
    changes = []
    for rid, inspection in inspected.items():
        if inspection.get('status') != 'approved':
            continue
        assert inspection.get('reason'), rid
        request = byrequest[rid]
        resultpath = F / 'argon' / (rid + '.result.json')
        result = json.loads(resultpath.read_text())
        expected = {tuple(x) for x in inspection['approved_keys']}
        superseded = {tuple(x) for x in inspection.get('superseded_keys', [])}
        assert superseded <= expected
        if superseded:
            assert inspection.get('supersession_reason'), 'New evidence supersession needs provenance'
        expected -= superseded
        decisions = [x for x in result['decisions'] if a.decision_key(x) in expected]
        assert len(decisions) == len(expected) and len({a.decision_key(x) for x in decisions}) == len(expected)
        sourcepath = Path(snapshot['works'][request['file_key']]['source_path'])
        source = sourcepath.read_text()
        assert hashlib.sha256(sourcepath.read_bytes()).hexdigest() == snapshot['works'][request['file_key']]['source_sha256']
        assert all(c.valid_decision(d, source) for d in decisions)
        target = R / 'adjudications' / (request['file_key'] + '.json')
        obj = c.read_json(target)[0] or {'decisions': []}
        archive = F / 'integration/prior_adjudications' / target.name
        if target.exists() and not archive.exists():
            archive.parent.mkdir(exist_ok=True)
            archive.write_bytes(target.read_bytes())
        for decision in decisions:
            key = a.decision_key(decision)
            old = [x for x in obj['decisions'] if a.decision_key(x) == key]
            assert len(old) <= 1, (rid, 'unreconciled duplicate prior decision', key)
            if old == [decision]:
                continue
            if old and c.valid_decision(old[0], source) and old[0]['verdict'] != 'undeterminable':
                oldvalue = (old[0]['verdict'], old[0].get('corrected_value'))
                newvalue = (decision['verdict'], decision.get('corrected_value'))
                assert oldvalue == newvalue or inspection.get('explicit_supersession_reason'), (rid, key, 'prior substantive decision differs')
            obj['decisions'] = [x for x in obj['decisions'] if a.decision_key(x) != key]
            obj['decisions'].append(copy.deepcopy(decision))
            obj.setdefault('evidence_followup_history', []).append({
                'request_id': rid, 'decision_key': list(key), 'prior_decision': old[0] if old else None,
                'parent_inspection': 'evidence_followup/integration/parent_inspection.json'})
            changes.append({'request_id': rid, 'file_key': request['file_key'], 'key': list(key)})
        a.atomic(target, obj)
    a.atomic(F / 'integration/last_merge.json', {'merged_decisions': changes})
    return {'merged_decisions': len(changes), 'works': len({x['file_key'] for x in changes})}


if __name__ == '__main__':
    print(json.dumps(integrate()))
