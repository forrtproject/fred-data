"""Prepare only disagreements supported by newly retrieved primary sources."""
import ast
import collections
import hashlib
import json
from pathlib import Path

F = Path(__file__).resolve().parent
B = F.parent


def main():
    # Reuse the settled scientific adjudication instructions verbatim.
    tree = ast.parse((B / 'scripts' / 'prepare_adjudication.py').read_text())
    leads = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)
             and isinstance(n.value, str) and n.value.startswith('Adjudicate paper-statistics disagreements')]
    assert len(leads) == 1
    rows = json.loads((B / 'parent_rows.json').read_text())
    inputs = {r['audit_id']: r for p in (B / 'inputs').glob('*.json')
              for r in json.loads(p.read_text())}
    groups = collections.defaultdict(list)
    repairs_path = F / 'quote_repairs' / 'repairs.json'
    repairs = json.loads(repairs_path.read_text()) if repairs_path.exists() else []
    for item in json.loads((B / 'disagreements.json').read_text()):
        path = item.get('blind', {}).get('source_path', '')
        if not Path(path).name.startswith('followup_mac_'):
            continue
        row = rows[item['audit_id'] - 1]
        side = 'o' if item['field'].endswith('_o') else 'r'
        item['coding_context'] = {
            'es_repr': row['es_repr_' + side], 'description': row.get('description'),
            'reported_success_quote': row.get('reported_success_quote'),
            'pval_tails': row['pval_tails_' + side], 'nested': row['nested_' + side],
            'analytic_n_definition': 'sample used for the critical test after exclusions; distinguish counting units'}
        item['locator'] = inputs[item['audit_id']]
        evidence_repairs = [r for r in repairs if r['audit_id'] == item['audit_id']]
        if evidence_repairs:
            item['parent_evidence_review'] = evidence_repairs
        groups[path].append(item)
    queue = []
    for source, items in sorted(groups.items()):
        key = 'macfollowup_' + hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()[:16]
        prompt = B / 'adjudications' / f'prompt_{key}.txt'
        output = B / 'adjudications' / f'raw_{key}.txt'
        text = leads[0] + '\n\n' + json.dumps(items, ensure_ascii=False, indent=2)
        text += ('\n\nThese fields come from a newly retrieved primary source. Do not infer target identity '
                 'from numerical coincidence. If only an author manuscript is available, explicitly '
                 'consider version differences before calling the published coding wrong. '
                 'End your response with the answer itself under a heading ## Answer. '
                 'Put your whole result in your reply; do not create files or run commands.\n')
        if prompt.exists():
            assert prompt.read_text() == text
        else:
            prompt.write_text(text)
        queue.append({'key': key, 'source_path': source, 'prompt': str(prompt.absolute()),
                      'output': str(output.absolute()), 'items': [{'audit_id': i['audit_id'],
                      'field': i['field']} for i in items], 'prompt_bytes': len(text.encode())})
    (F / 'adjudication_queue.json').write_text(json.dumps(queue, indent=2) + '\n')
    print(json.dumps({'source_groups': len(queue), 'fields': sum(len(q['items']) for q in queue)}))


if __name__ == '__main__':
    main()
