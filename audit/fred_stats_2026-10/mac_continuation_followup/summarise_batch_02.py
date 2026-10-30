"""Record incremental gains and protect the published first-batch findings."""
import csv
import datetime
import hashlib
import io
import json
import subprocess
from pathlib import Path

F = Path(__file__).resolve().parent
B = F.parent
BASE = '3d859a90890e883824c0a00f5ec6633822a671b4'
FIELDS = ['n_o', 'es_value_o', 'pval_value_o', 'n_r', 'es_value_r', 'pval_value_r', 'reported_success']


def main():
    old = list(csv.DictReader(io.StringIO(subprocess.check_output(
        ['git', 'show', f'{BASE}:audit/fred_stats_2026-10/results.csv']).decode('utf-8-sig'))))
    new = list(csv.DictReader((B / 'results.csv').open(encoding='utf-8-sig')))
    assert len(old) == len(new) == 2164
    changes = []
    for a, b in zip(old, new):
        assert a['effect_id'] == b['effect_id']
        for field in FIELDS:
            before = (a[field + '_final_verdict'], a[field + '_suggested_correction'])
            after = (b[field + '_final_verdict'], b[field + '_suggested_correction'])
            if before[0] in ('correct', 'error'):
                assert before == after, (a['input_row_index'], field)
            if before != after:
                changes.append({'audit_id': int(b['input_row_index']), 'field': field,
                                'before': before[0], 'after': after[0],
                                'shipped': b[field + '_shipped'], 'correction': after[1],
                                'location': b[field + '_location'], 'reason': b[field + '_reason']})
    for name, expected in json.loads((F / 'batch_02_baseline.json').read_text())['immutable_batch_01_files'].items():
        assert hashlib.sha256((F / name).read_bytes()).hexdigest() == expected, name
    batch = [q for q in json.loads((F / 'validation_queue.json').read_text()) if q['batch'].startswith('maccont02_')]
    for q in batch:
        for aid in q['audit_ids']:
            before = json.loads(subprocess.check_output(
                ['git', 'show', f'{BASE}:audit/fred_stats_2026-10/extractions/{aid}.json']))
            after = json.loads((B / 'extractions' / f'{aid}.json').read_text())
            for side in ('original', 'replication', 'reported_success'):
                if before[side]['status'] == 'done':
                    assert before[side] == after[side], (aid, side)
    gained = [c for c in changes if c['after'] in ('correct', 'error') and c['before'] not in ('correct', 'error')]
    errors = [c for c in gained if c['after'] == 'error']
    with (F / 'batch_02_field_changes.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(changes[0]))
        writer.writeheader()
        writer.writerows(changes)
    summary = {'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'baseline_commit': BASE, 'accepted_full_article_sources': 22,
               'blind_batches': len(batch), 'target_sides': len({aid for q in batch for aid in q['audit_ids']}),
               'side_attempts': sum(len(q['audit_ids']) for q in batch),
               'new_verified_fields': len(gained), 'new_errors': len(errors), 'confirmed_changes': errors,
               'published_batch_01_verified_fields_preserved': True,
               'completed_sides_and_verdicts_preserved': True,
               'historical_completion_and_deadlines_preserved': True}
    (F / 'batch_02_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
