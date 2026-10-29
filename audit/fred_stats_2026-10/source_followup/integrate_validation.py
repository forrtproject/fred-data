"""Integrate only newly examined sides; retain every previously completed side."""
import copy
import hashlib
import json
import sys
from pathlib import Path

F = Path(__file__).resolve().parent
B = F.parent
sys.path.insert(0, str(B / 'scripts'))
from compare import quote_ok
from schema import validate


def checked_merge(before, after, side, source_path):
    validate(after)
    assert before['audit_id'] == after['audit_id']
    assert side in ('original', 'replication')
    assert before[side]['status'] == 'paper_unavailable', 'Previously examined side is protected'
    merged = copy.deepcopy(before)
    examined = after[side]
    if examined['status'] == 'done':
        for field in ('n', 'es', 'p'):
            evidence = examined[field]
            if evidence['value'] is not None or evidence.get('test_statistic'):
                assert Path(evidence['source_path']).resolve() == Path(source_path).resolve()
                value = evidence['value'] or evidence.get('test_statistic')
                if evidence['confident']:
                    assert quote_ok({**evidence, 'value': value}), ('Unsupported quote', field)
        merged[side] = copy.deepcopy(examined)
    verdict = after['reported_success']
    if (side == 'replication' and before['reported_success']['status'] != 'done'
            and verdict['status'] == 'done' and verdict['value'] is not None):
        assert Path(verdict['source_path']).resolve() == Path(source_path).resolve()
        if verdict['confident']:
            assert quote_ok(verdict), 'Unsupported author verdict quote'
        merged['reported_success'] = copy.deepcopy(verdict)
    if merged != before:
        merged['notes'] = before['notes'] + '\nSource follow-up: ' + after['notes']
    return validate(merged)


def atomic(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)


def main():
    accepted = json.loads((F / 'accepted_sources.json').read_text())
    queue = json.loads((F / 'validation_queue.json').read_text())
    ledger_path = F / 'integration.json'
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    changed = []
    for batch in queue:
        records = json.loads(Path(batch['input']).read_text())
        for record in records:
            aid, side = record['audit_id'], record['target_side']
            result_path = Path(batch['output']) / f'{aid}.json'
            ledger_key = f"{batch['batch']}:{aid}:{side}"
            if not result_path.exists() or ledger_key in ledger:
                continue
            after = json.loads(result_path.read_text())
            dest = B / 'extractions' / f'{aid}.json'
            before = json.loads(dest.read_text())
            source = accepted[batch['source_key']]['text_path']
            merged = checked_merge(before, after, side, source)
            if merged != before:
                backup = F / 'before_extractions' / dest.name
                backup.parent.mkdir(exist_ok=True)
                if not backup.exists():
                    atomic(backup, before)
                atomic(dest, merged)
                changed.append([aid, side])
            ledger[ledger_key] = {'changed': merged != before,
                                  'source_key': batch['source_key'],
                                  'result_sha256': hashlib.sha256(result_path.read_bytes()).hexdigest()}
            atomic(ledger_path, ledger)
    print(json.dumps({'integrated_sides': len(ledger), 'changed_sides': changed}))


if __name__ == '__main__':
    main()
