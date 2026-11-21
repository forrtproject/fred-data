"""Export confirmed Drive corrections with evidence and explicit metric/bound context."""
import csv
import json
import sys
from pathlib import Path

F = Path(__file__).resolve().parent
B = F.parent
sys.path.insert(0, str(B / 'scripts'))
from compare import load_adjudications, parsed_stat, metric, quote_ok
from consistency import number, p_parts


def main():
    decisions = load_adjudications(B)
    parent_rows = json.loads((B / 'parent_rows.json').read_text())
    changes = json.loads((F / 'summary.json').read_text())['new_errors']
    details = []
    for change in changes:
        aid, field = change['audit_id'], change['field']
        decision = decisions[(aid, field)]
        assert change['correction'] == decision['correct_value']
        assert quote_ok({**decision, 'value': decision['correct_value'], 'confident': True})
        side = None if field == 'reported_success' else 'original' if field.endswith('_o') else 'replication'
        checkpoint = json.loads((B / 'extractions' / f'{aid}.json').read_text())
        blind = checkpoint['reported_success'] if side is None else checkpoint[side][
            'n' if field.startswith('n_') else 'es' if field.startswith('es_') else 'p']
        corrected_metric = corrected_bound = ''
        if field.startswith('pval_'):
            fallback = decision.get('correct_bound')
            parsed = p_parts(decision['correct_value'], fallback)
            if parsed is None and fallback is None and decision['verdict'] == 'blind_right':
                assert number(decision['correct_value']) == number(blind['value'])
                fallback = blind['bound']
                parsed = p_parts(decision['correct_value'], fallback)
            assert parsed is not None, (aid, field, 'Correction bound not established')
            corrected_bound = parsed[1]
        if field.startswith('es_'):
            corrected_metric = decision.get('correct_metric')
            if not corrected_metric and parsed_stat(decision['correct_value']):
                corrected_metric = 'test statistic'
            if not corrected_metric and decision['verdict'] == 'blind_right':
                assert number(decision['correct_value']) == number(blind['value'])
                corrected_metric = blind['metric']
            assert corrected_metric, (aid, field, 'Correction metric not established')
            requested = parent_rows[aid - 1]['es_type_' + field[-1]]
            assert metric(corrected_metric) == metric(requested), (aid, field, corrected_metric, requested)
        details.append({
            'audit_id': aid, 'field': field, 'shipped': change['shipped'],
            'correction': change['correction'], 'corrected_metric': corrected_metric,
            'corrected_p_bound': corrected_bound,
            'blind_counting_unit_observation': blind.get('sample_role', '') if field.startswith('n_') else '',
            'blind_exclusions_observation': blind.get('exclusions', '') if field.startswith('n_') else '',
            'source_path': decision['source_path'], 'location': decision['location'],
            'quote': decision['quote'], 'independent_reason': decision['reason'],
        })
    assert details
    with (F / 'correction_details.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(details[0]))
        writer.writeheader()
        writer.writerows(details)
    print(json.dumps({'confirmed_drive_corrections_exported': len(details),
                      'metric_and_bound_context_checked': True}))


if __name__ == '__main__':
    main()
