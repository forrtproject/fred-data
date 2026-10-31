"""Build stable blind batches from sources explicitly accepted by the parent."""
import hashlib
import json
from pathlib import Path

F = Path(__file__).resolve().parent
B = F.parent


def main():
    accepted_path = F / 'accepted_sources.json'
    accepted = json.loads(accepted_path.read_text()) if accepted_path.exists() else {}
    inputs = {r['audit_id']: r for p in (B / 'inputs').glob('*.json')
              for r in json.loads(p.read_text())}
    manifest = json.loads((F / 'missing_sources.json').read_text())
    output = F / 'validation_inputs'
    output.mkdir(exist_ok=True)
    previous = json.loads((F / 'validation_queue.json').read_text()) if (F / 'validation_queue.json').exists() else []
    queue = []
    for source in manifest:
        key = source['key']
        if key not in accepted:
            continue
        proof = accepted[key]
        path = Path(proof['text_path'])
        assert path.resolve().is_relative_to((B / 'texts').resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest() == proof['text_sha256']
        records = []
        for target in source['targets']:
            aid, side = target['audit_id'], target['side']
            row = dict(inputs[aid])
            row['target_side'] = side
            row['text_paths'] = {side[0]: str(path.absolute())}
            if proof.get('source_version'):
                row['source_version_note'] = proof['source_version']
            if proof.get('source_pdf_path'):
                row['source_pdf_path'] = proof['source_pdf_path']
            records.append(row)
        for start in range(0, len(records), 15):
            batch = f'{key}_{start:03d}'
            dest = output / f'{batch}.json'
            payload = json.dumps(records[start:start + 15], ensure_ascii=False, indent=2) + '\n'
            if dest.exists():
                assert dest.read_text() == payload, ('Input changed after preparation', batch)
            else:
                dest.write_text(payload)
            queue.append({'batch': batch, 'source_key': key, 'input': str(dest.absolute()),
                          'output': str((F / 'validation_extractions' / batch).absolute()),
                          'audit_ids': [r['audit_id'] for r in records[start:start + 15]],
                          'source_sha256': proof['text_sha256']})
    # Exact locator variants have separately reviewed immutable inputs. Keep them
    # across regeneration without silently reopening any completed side.
    queue.extend(q for q in previous if q.get('new_primary_context'))
    (F / 'validation_queue.json').write_text(json.dumps(queue, indent=2) + '\n')
    print(json.dumps({'accepted_sources': len(accepted), 'batches': len(queue),
                      'target_sides': sum(len(q['audit_ids']) for q in queue)}))


if __name__ == '__main__':
    main()
