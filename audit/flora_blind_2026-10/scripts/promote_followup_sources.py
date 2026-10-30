#!/usr/bin/env python3
"""Parent-only promotion of independently verified, freshly blinded sources.

Preserves old sources/codings and explicitly reconciles old target identities.
No scientific decision is made here. New unmatched targets re-enter review.
"""
import collections
import hashlib
import json
from pathlib import Path
import shutil

import jsonschema
import adjudicate as a
import compare as c

R = Path(__file__).resolve().parents[1]
F = R / 'evidence_followup'


def target_mapping(old, new):
    mapping = []
    for i, target in enumerate(old.get('targets', [])):
        title = c.tokens(target.get('title', ''))
        doi = c.clean_doi(target.get('doi'))
        matches = [j for j, other in enumerate(new['targets'])
                   if (doi and doi == c.clean_doi(other.get('doi')))
                   or (title and title == c.tokens(other.get('title', '')))]
        # A period at the end of a reference is not a different identity.
        if not matches and title:
            raise ValueError(f'Old identified target needs individual reconciliation: {target}')
        if len(matches) > 1:
            raise ValueError('Ambiguous old target mapping')
        mapping.append({'old_target_index': i, 'new_target_index': matches[0] if matches else None,
                        'old_target': target,
                        'basis': 'same DOI or token-identical title' if matches else
                        'unidentified abstract placeholder; retain archived provenance, review all new targets'})
    return mapping


def promote():
    schema = json.loads((R / 'coding_schema.json').read_text())
    verification = json.loads((F / 'acquisition/parent_verification.json').read_text())['works']
    ledgerpath = F / 'integration/source_promotions.json'
    ledger = json.loads(ledgerpath.read_text())
    done = {x['file_key'] for x in ledger['promotions']}
    tasks = json.loads((F / 'state.json').read_text())['tasks']
    active = [x for x in tasks if x['status'] in ('running', 'queued', 'waiting') or x.get('hasPendingChildRuns')]
    lunapath = F / 'luna/index.json'
    luna = json.loads(lunapath.read_text())
    candidatepath = F / 'candidate_requests/index.json'
    candidates = json.loads(candidatepath.read_text())
    promotions = []
    for path in sorted((F / 'private/blind_codings').glob('*.json')):
        fk = path.stem
        if fk in done:
            continue
        assert verification[fk]['status'] in ('verified_full_text', 'verified_primary_abstract'), fk
        new = json.loads(path.read_text())
        jsonschema.validate(new, schema)
        sourcepath = F / 'private/blind_texts' / (fk + '.txt')
        source = sourcepath.read_text()
        assert hashlib.sha256(sourcepath.read_bytes()).hexdigest() == new['text_sha256'], fk
        assert new['evidence_level'] == ('abstract' if verification[fk]['status'] == 'verified_primary_abstract' else 'full_text')
        for target in new['targets']:
            for key in ('evidence_quote', 'outcome_quote', 'outcome_computational_quote', 'outcome_robustness_quote'):
                assert not target.get(key) or target[key] in source, (fk, key)
        # Initial relay snapshot contains old FT works, not these recovered sources.
        snap = json.loads((F / 'argon/snapshot.json').read_text())
        assert fk not in snap['works'], 'Active immutable relay source cannot change'
        for task in active:
            if task.get('lane') == 'luna':
                packet = json.loads((F / 'luna/batches' / (task['batch_id'] + '.input.json')).read_text())
                assert fk not in {w['file_key'] for w in packet['works']}, 'Luna is reading old source'
            elif task.get('lane') == 'argon_native':
                packet = json.loads((F / 'candidate_reviews' / (task['review_id'] + '.input.json')).read_text())
                assert fk not in {w['file_key'] for w in packet['requests']}, 'Argon is reading old source'
        assert not (R / 'adjudications' / path.name).exists(), 'Prior authoritative decisions need explicit carryover'
        assert fk not in json.loads((R / 'timing_corrections.json').read_text()), 'Reconcile old elapsed correction first'
        oldpath = R / 'codings' / path.name
        old = json.loads(oldpath.read_text())
        mapping = target_mapping(old, new)
        for folder, original in [('old_codings', oldpath), ('old_texts', R / 'texts' / (fk + '.txt'))]:
            archive = F / 'private' / folder / original.name
            archive.parent.mkdir(exist_ok=True)
            if original.exists() and not archive.exists():
                shutil.copyfile(original, archive)
        for entry in candidates:
            packet = json.loads(Path(entry['input_path']).read_text())
            if packet['file_key'] == fk:
                assert entry['status'] in ('pending', 'parent_inspection_pending', 'superseded_new_source'), entry
                entry.update(status='superseded_new_source', supersession_reason='New full primary source and fresh blind coding; all newly unmatched identities receive a new review packet. Old input/result retained.')
        # Remove affected old work packets only from not-yet-started Luna batches.
        # Completed reading/results remain immutable and linked in the promotion ledger.
        old_batches = []
        for entry in luna:
            p = Path(entry['input_path'])
            packet = json.loads(p.read_text())
            if fk not in {w['file_key'] for w in packet['works']}:
                continue
            old_batches.append(entry['batch_id'])
            if entry['status'] != 'pending':
                continue
            archive = F / 'private/old_luna_inputs' / p.name
            archive.parent.mkdir(exist_ok=True)
            if not archive.exists():
                shutil.copyfile(p, archive)
            packet['works'] = [w for w in packet['works'] if w['file_key'] != fk]
            entry['candidate_count'] = sum(len(w['candidates']) for w in packet['works'])
            if not packet['works']:
                entry.update(status='superseded_new_source')
            a.atomic(p, packet)
        oldhash = hashlib.sha256((R / 'texts' / (fk + '.txt')).read_bytes()).hexdigest() if (R / 'texts' / (fk + '.txt')).exists() else None
        shutil.copyfile(sourcepath, R / 'texts' / (fk + '.txt'))
        a.atomic(oldpath, new)
        promotion = {'file_key': fk, 'old_text_sha256': oldhash,
                     'new_text_sha256': new['text_sha256'],
                     'old_evidence_level': old.get('evidence_level'),
                     'new_evidence_level': new['evidence_level'],
                     'old_luna_batches': old_batches, 'target_mapping': mapping,
                     'new_targets': len(new['targets']), 'new_review_packets_created': False,
                     'reason': 'Parent verified complete primary identity/body; new blinded coding passed schema/hash/literal quotes; prior identified references explicitly mapped and all new unmatched identities require independent review.'}
        ledger['promotions'].append(promotion)
        promotions.append(fk)
        a.atomic(ledgerpath, ledger)
        a.atomic(lunapath, luna)
        a.atomic(candidatepath, candidates)
    return promotions


def enqueue():
    ledgerpath = F / 'integration/source_promotions.json'
    ledger = json.loads(ledgerpath.read_text())
    missing = c.read_csv(R / 'missing_rows.csv')
    rows = c.read_csv(R / 'results.csv')
    originals = [c.adapt_row(x) for x in c.read_csv(c.INPUT)]
    lunapath = F / 'luna/index.json'
    luna = json.loads(lunapath.read_text())
    bywork = collections.defaultdict(list)
    for row in rows:
        bywork[row['file_key']].append(row)
    for promotion in ledger['promotions']:
        if promotion.get('new_review_packets_created', True):
            continue
        fk = promotion['file_key']
        items = [x for x in missing if x['file_key'] == fk and x['final_verdict'] != 'correct']
        shipped = [{'input_row_index': row['input_row_index'], **{
            k: originals[int(row['input_row_index'])].get(k, '') for k in ('doi_o', 'title_o', 'authors_o', 'year_o')}} for row in bywork[fk]]
        for start in range(0, len(items), 6):
            bid = f'luna_{max(int(x["batch_id"].split("_")[1]) for x in luna)+1:04d}'
            path = F / 'luna/batches' / (bid + '.input.json')
            sourcepath = R / 'texts' / (fk + '.txt')
            packet = {'file_key': fk, 'work_key': bywork[fk][0]['work_key'],
                      'text_path': str(sourcepath), 'coding_path': str(R / 'codings' / (fk + '.json')),
                      'codebook_path': str(R / 'codebook.md'),
                      'source_instruction': a.source_instruction(fk, sourcepath, sourcepath.read_text()),
                      'evidence_level': promotion['new_evidence_level'], 'shipped_originals': shipped,
                      'prior_adjudication_path': str(R / 'adjudications' / (fk + '.json')),
                      'source_version': promotion['new_text_sha256'],
                      'prior_source_target_mapping': promotion['target_mapping'],
                      'candidates': [{'target_index': int(x['target_index']), 'previous_final_verdict': 'new_after_verified_primary_source',
                                      'blind_target': json.loads(x['blind_target']), 'prior_decision': {}} for x in items[start:start+6]]}
            a.atomic(path, {'batch_id': bid, 'works': [packet]})
            luna.append({'batch_id': bid, 'input_path': str(path),
                         'output_path': str(F / 'luna/results' / (bid + '.json')),
                         'candidate_count': len(packet['candidates']), 'status': 'pending', 'priority': 'new_primary_text'})
        promotion['new_unmatched_targets'] = len(items)
        promotion['new_review_packets_created'] = True
    a.atomic(lunapath, luna)
    a.atomic(ledgerpath, ledger)
    return len(luna)


if __name__ == '__main__':
    import sys
    print(json.dumps(enqueue() if sys.argv[1:] == ['enqueue'] else promote()))
