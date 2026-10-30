"""Reconcile follow-up gains against the frozen completed-audit commit."""
import collections
import csv
import datetime
import hashlib
import io
import json
import subprocess
from pathlib import Path

F = Path(__file__).resolve().parent
B = F.parent
BASE = 'c9f81545477aea585e1c3674ab6b8d867595a7ee'
FIELDS = ['n_o', 'es_value_o', 'pval_value_o', 'n_r', 'es_value_r', 'pval_value_r', 'reported_success']


def main():
    old = list(csv.DictReader(io.StringIO(subprocess.check_output(
        ['git', 'show', f'{BASE}:audit/fred_stats_2026-10/results.csv']).decode('utf-8-sig'))))
    new = list(csv.DictReader((B / 'results.csv').open(encoding='utf-8-sig')))
    assert len(old) == len(new) == 2164
    baseline = json.loads((F / 'baseline.json').read_text())
    for name in baseline['files']:
        assert hashlib.sha256((B / name).read_bytes()).hexdigest() == baseline['files'][name], name
    changes = []
    for a, b in zip(old, new):
        assert a['effect_id'] == b['effect_id']
        for field in FIELDS:
            suffix = '_final_verdict'
            if a[field + suffix] in ('correct', 'error'):
                assert a[field + suffix] == b[field + suffix], (a['input_row_index'], field)
                assert a[field + '_suggested_correction'] == b[field + '_suggested_correction']
            if (a[field + suffix], a[field + '_suggested_correction']) != (b[field + suffix], b[field + '_suggested_correction']):
                changes.append({'audit_id': int(b['input_row_index']), 'field': field,
                                'before': a[field + suffix], 'after': b[field + suffix],
                                'shipped': b[field + '_shipped'], 'correction': b[field + '_suggested_correction'],
                                'resolution': b[field + '_resolution'], 'location': b[field + '_location'],
                                'reason': b[field + '_reason']})
    # Completed sides and author verdicts cannot be overwritten by this pass.
    for p in (F / 'before_extractions').glob('*.json'):
        a = json.loads(subprocess.check_output(['git', 'show', f'{BASE}:audit/fred_stats_2026-10/extractions/{p.name}']))
        b = json.loads((B / 'extractions' / p.name).read_text())
        for side in ['original', 'replication', 'reported_success']:
            if a[side]['status'] == 'done':
                assert a[side] == b[side], (p.name, side)
    with (F / 'field_changes.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        w = csv.DictWriter(stream, fieldnames=list(changes[0])); w.writeheader(); w.writerows(changes)
    progress = json.loads((B / 'progress.json').read_text())
    ledger = json.loads((F / 'integration.json').read_text())
    targets = {(int(k.split(':')[-2]), k.split(':')[-1]) for k in ledger}
    statuses = collections.Counter(json.loads((B / 'extractions' / f'{aid}.json').read_text())[side]['status'] for aid, side in targets)
    accepted = json.loads((F / 'accepted_sources.json').read_text())
    gained = [c for c in changes if c['after'] in ('correct', 'error') and c['before'] not in ('correct', 'error')]
    errors = [c for c in gained if c['after'] == 'error']
    summary = {'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'baseline_commit': BASE, 'received_source_groups': len(accepted),
               'independently_reviewed_sources': len(accepted),
               'initial_unavailable_sides': len(targets), 'accepted_full_article_artifacts': sum(not v.get('source_kind') for v in accepted.values()),
               'accepted_primary_supplements': sum(v.get('source_kind') == 'primary_supplement' for v in accepted.values()),
               'accepted_primary_author_tables': sum(v.get('source_kind') == 'primary_author_table' for v in accepted.values()),
               'validation_batches': len(json.loads((F / 'validation_queue.json').read_text())),
               'validation_side_attempts': len(ledger), 'distinct_target_sides': len(targets), 'final_target_statuses': dict(statuses),
               'new_verified_field_instances': len(gained), 'new_verified_fields_by_name': dict(collections.Counter(c['field'] for c in gained)),
               'new_error_fields': len(errors), 'new_errors': errors,
               'current_confirmed_errors': len(progress['confirmed_errors']),
               'current_error_rows': len({e['audit_id'] for e in progress['confirmed_errors']}),
               'coverage': progress['coverage'], 'baseline_verified_fields_preserved': True,
               'baseline_completed_sides_and_verdicts_preserved': True, 'original_deadlines_and_completion_preserved': True}
    (F / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'new_errors'}))


if __name__ == '__main__':
    main()
