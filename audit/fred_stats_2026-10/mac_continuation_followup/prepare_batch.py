"""Accept a transferred Mac batch and prepare immutable blind target inputs."""
import collections
import datetime
import hashlib
import json
import subprocess
import sys
import re
from pathlib import Path

F = Path(__file__).resolve().parent
B = F.parent


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    manifest_path = Path(sys.argv[1]).resolve()
    manifest = json.loads(manifest_path.read_text())
    manifest['batch'] = re.fullmatch(r'batch_(\d+)_box_manifest.json', manifest_path.name)[1]
    handoff = Path(manifest['manifest'])
    transfer = handoff.parent
    hashes = json.loads(handoff.read_text())['files']
    for relative, digest in hashes.items():
        path = (transfer / relative).resolve()
        assert path.is_relative_to(transfer)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, relative
    checks = {r['key']: r for r in json.loads((F / f"batch_{manifest['batch']}_parent_source_checks.json").read_text())}
    inputs = {r['audit_id']: r for path in (B / 'inputs').glob('*.json') for r in json.loads(path.read_text())}
    accepted_path = F / 'accepted_sources.json'
    accepted = json.loads(accepted_path.read_text()) if accepted_path.exists() else {}
    queue_path = F / 'validation_queue.json'
    queue = json.loads(queue_path.read_text()) if queue_path.exists() else []
    old_batches = {q['batch'] for q in queue}
    reserved = {(r['audit_id'], r['target_side']) for q in queue for r in json.loads(Path(q['input']).read_text())}
    (F / 'validation_inputs').mkdir(exist_ok=True)
    skipped = collections.Counter()
    subprocess.run(['mountpoint', '-q', '/home/lukas/cloud-data'], check=True)
    prior_keys={key for folder in ['mac_source_followup','source_followup'] for key in json.loads((B/folder/'accepted_sources.json').read_text())}
    for key, s in manifest['sources'].items():
        if key in prior_keys:
            skipped['previously_accepted_source'] += 1
            continue
        check = checks[key]
        assert s['acceptance'] == 'verified_complete_article'
        if key in accepted:
            assert accepted[key]['text_sha256'] == s['text_sha256']
            continue
        assert check['reference_section'] and check['pages'] == s['pages']
        assert check['title_token_match'] >= .9
        dest = B / 'texts' / f'followup_maccont_{key}.txt'
        payload = Path(s['text_path']).read_bytes()
        if dest.exists():
            assert hashlib.sha256(dest.read_bytes()).hexdigest() == s['text_sha256']
        else:
            dest.write_bytes(payload)
        version = s['source_version'] + '; ' + s['identity_completeness_evidence']
        accepted[key] = {**{k: s[k] for k in ['doi', 'reference', 'pages', 'artifact_path', 'artifact_sha256', 'text_sha256', 'retrieval_url', 'identity_completeness_evidence']},
                         'text_path': str(dest.absolute()), 'source_version': version,
                         'transfer_batch': manifest['batch'], 'source_pdf_path': s['artifact_path'],
                         'parent_review': 'Transferred hashes, actual PDF page count, freshly parsed PDF title/header and reference section checked independently; Mac visual identity/completeness review retained. This is source acceptance only.'}
        neutral = json.loads(Path(s['neutral_input_path']).read_text())
        assert neutral['key'] == key and neutral['doi'] == s['doi']
        by_side = collections.defaultdict(list)
        for target in neutral['targets']:
            aid, side = target['audit_id'], target['side']
            before = json.loads((B / 'extractions' / f'{aid}.json').read_text())
            if before[side]['status'] != 'paper_unavailable':
                skipped[before[side]['status']] += 1
                continue
            if (aid, side) in reserved:
                continue
            row = dict(inputs[aid])
            row.update(target_side=side, description=target['description'],
                       source_version_note=version, source_pdf_path=s['artifact_path'],
                       text_paths={side[0]: str(dest.absolute())})
            row['locators_' + side[0]] = target['locator']
            row['es_type_' + side[0]] = target['requested_metric']
            by_side[side].append(row)
            reserved.add((aid, side))
        for side, records in by_side.items():
            for start in range(0, len(records), 15):
                batch = f"maccont{manifest['batch']}_{key}_{side}_{start:03d}"
                if batch in old_batches:
                    continue
                path = F / 'validation_inputs' / f'{batch}.json'
                save(path, records[start:start + 15])
                queue.append({'batch': batch, 'source_key': key, 'transfer_batch': manifest['batch'],
                              'chunk': start, 'input': str(path.absolute()),
                              'output': str((F / 'validation_extractions' / batch).absolute()),
                              'audit_ids': [r['audit_id'] for r in records[start:start + 15]],
                              'source_sha256': s['text_sha256']})
    queue.sort(key=lambda q: (q['chunk'], -len(q['audit_ids']), q['batch']))
    provenance=json.loads((B/'source_provenance.json').read_text())
    for source in accepted.values():
        provenance[source['text_path']]={'work_doi':source['doi'],'kind':'primary source recovered on Mac continuation','evidence':source['identity_completeness_evidence'],'version':source['source_version'],'text_sha256':source['text_sha256']}
    save(B/'source_provenance.json',provenance)
    save(accepted_path, accepted)
    save(queue_path, queue)
    save(F / f"batch_{manifest['batch']}_receipt.json", {'received_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'manifest_path': str(manifest_path), 'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
         'files_verified': len(hashes), 'sources': len(manifest['sources']), 'skipped_statuses': dict(skipped)})
    print(json.dumps({'accepted_sources': len(accepted), 'batches': len(queue), 'eligible_sides': len(reserved), 'skipped': dict(skipped)}))


if __name__ == '__main__':
    main()
