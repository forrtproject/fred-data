#!/usr/bin/env python3
"""Verify saved audit deliverables without modifying the dataset or evidence."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

import compare
import controller


def verify():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'run_manifest.json').read_text())
    paths = [root / 'results.csv', root / 'missing_rows.csv']
    before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    rows = compare.read_csv(paths[0])
    assert [int(r['input_row_index']) for r in rows] == list(range(manifest['rows']))
    correction_fields = 0
    for row in rows:
        evidence = json.loads(row['correction_evidence'])
        for field in json.loads(row['suggested_correction']):
            item = evidence[field]
            source = (root / 'texts' / (row['file_key'] + '.txt')).read_text()
            assert item['reason'] and item['location'], (row['input_row_index'], field)
            assert compare.quote_present(item['quote'], source), (row['input_row_index'], field)
            correction_fields += 1
    confirmed_missing = 0
    for row in compare.read_csv(paths[1]):
        if row['final_verdict'] != 'error':
            continue
        item = json.loads(row['evidence'])
        source = (root / 'texts' / (row['file_key'] + '.txt')).read_text()
        assert compare.valid_decision(item, source) and item['reason'] and item['location']
        confirmed_missing += 1
    codings = [p for p in (root / 'codings').glob('*.json')
               if re.fullmatch(r'[0-9a-f]{16}', p.stem)]
    assert len(codings) == manifest['works']
    assert all(controller.validate(p) for p in codings), 'Invalid coding checkpoint'
    dataset = root.parents[1] / 'output/flora.csv'
    data_hash = hashlib.sha256(dataset.read_bytes()).hexdigest()
    assert data_hash == manifest['output_flora_sha256'], 'FLoRA changed'
    assert not subprocess.check_output(['git', 'ls-files', str(root / 'texts')], text=True).strip()
    for path in (root / 'argon').glob('*.state.json'):
        state = json.loads(path.read_text())
        assert state.get('attempts', 0) <= 2, ('Call budget exceeded', path.name)
        if manifest.get('audit_finalized_at'):
            assert state.get('status') not in ('running', 'retry_pending', 'scope_review_running', 'scope_review_pending'), path.name
            assert not state.get('requires_parent_scope_inspection'), path.name
    assert before == [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths], 'Deliverables changed during verification'
    return {'rows': len(rows), 'validated_codings': len(codings),
            'source_checked_correction_fields': correction_fields,
            'source_checked_missing_targets': confirmed_missing, 'flora_sha256': data_hash,
            'deliverable_sha256': dict(zip([p.name for p in paths], before))}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
