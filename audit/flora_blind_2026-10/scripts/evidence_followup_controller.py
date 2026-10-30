#!/usr/bin/env python3
"""Parent-owned follow-up accounting and strict Luna output validation."""
import collections
import datetime
import json
import importlib.util
import os
from pathlib import Path
import sys

import adjudicate as a
import compare as c

R = Path(__file__).resolve().parents[1]
F = R / 'evidence_followup'
ACTIVE = {'running', 'queued', 'waiting'}


def read(path, default=None):
    value, error = c.read_json(path)
    return default if error else value


def register(task):
    state = read(F / 'state.json')
    old = next((x for x in state['tasks'] if x['taskId'] == task['taskId']), {})
    value = dict(old, **task)
    state['tasks'] = [x for x in state['tasks'] if x['taskId'] != task['taskId']] + [value]
    state['updated_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    a.atomic(F / 'state.json', state)
    if value.get('lane') == 'luna':
        index = read(F / 'luna/index.json')
        entry = next(x for x in index if x['batch_id'] == value['batch_id'])
        prior_task = entry.get('taskId')
        entry.setdefault('attempts', 1)
        if prior_task and prior_task != value['taskId']:
            entry['attempts'] += 1
        entry.update(status=value['status'], taskId=value['taskId'])
        a.atomic(F / 'luna/index.json', index)
    with (F / 'tasks.jsonl').open('a') as stream:
        stream.write(json.dumps(dict(at=state['updated_at'], **value)) + '\n')
    return {'taskId': value['taskId'], 'status': value['status']}


def reconcile_files():
    state = read(F / 'state.json')
    known = {x['taskId'] for x in state['tasks']}
    paths = list((F / 'luna/batches').glob('*.task.json'))
    paths += list((F / 'argon').glob('*.task.json')) + list((F / 'acquisition').glob('*.task.json'))
    for p in paths:
        task = read(p)
        if task['taskId'] in known:
            continue
        if 'lane' not in task:
            task.update(lane='luna', slot_cost=1, batch_id=p.name.replace('.task.json', ''))
        register(task)


def validate_luna(bid):
    index = read(F / 'luna/index.json')
    entry = next(x for x in index if x['batch_id'] == bid)
    payload = read(Path(entry['input_path']))
    output = read(Path(entry['output_path']))
    expected = {(w['file_key'], x['target_index']) for w in payload['works'] for x in w['candidates']}
    if isinstance(output, dict) and isinstance(output.get('records'), list):
        observed = [(x.get('file_key'), x.get('target_index')) for x in output['records'] if isinstance(x, dict)]
        if set(observed) != expected or len(observed) != len(expected):
            output = None
    if not isinstance(output, dict) or not isinstance(output.get('records'), list):
        error = 'missing/invalid result envelope; earlier child did not produce a complete checkpoint'
        if entry.get('attempts', 1) < 2:
            entry.update(status='pending', retry_feedback=error)
            a.atomic(F / 'luna/index.json', index)
            return {'batch_id': bid, 'valid': False, 'error': error, 'retry_queued': True}
        output = {'batch_id': bid, 'records': [dict(file_key=w['file_key'],
            target_index=x['target_index'], disposition='needs_more_evidence',
            reason='Luna technical failure after two attempts; expert must inspect primary evidence directly.',
            location='technical failure; no scientific classification', omission_quote='',
            identity_quote='', duplicate_quote='', matched_input_row_index=None,
            shipped_rows_checked=[r['input_row_index'] for r in w['shipped_originals']],
            source_sections_reviewed=[], luna_not_completed=True)
            for w in payload['works'] for x in w['candidates']]}
    observed = [(x.get('file_key'), x.get('target_index')) for x in output['records']]
    if set(observed) != expected or len(observed) != len(expected):
        return {'batch_id': bid, 'valid': False, 'error': 'missing, duplicate or extra candidate keys'}
    validated, requests = [], []
    requestdir = F / 'candidate_requests'
    requestdir.mkdir(exist_ok=True)
    for work in payload['works']:
        source = Path(work['text_path']).read_text()
        rows = {str(x['input_row_index']) for x in work['shipped_originals']}
        selected = [x for x in output['records'] if x['file_key'] == work['file_key']]
        for item in selected:
            errors = []
            if item.get('luna_not_completed'):
                errors.append('Luna technical failure; no scientific review')
            if item.get('disposition') not in {'likely_omission', 'represented', 'not_a_target', 'needs_more_evidence'}:
                errors.append('invalid disposition')
            if not item.get('reason') or not item.get('location'):
                errors.append('missing reason/location')
            if {str(x) for x in item.get('shipped_rows_checked', [])} != rows:
                errors.append('not all shipped rows checked')
            for field in ('omission_quote', 'identity_quote', 'duplicate_quote'):
                quote = item.get(field, '')
                if quote and (not isinstance(quote, str) or len(quote) > 2000 or quote not in source):
                    errors.append(field + ' is not a valid literal quote')
            if item.get('disposition') == 'likely_omission' and not (item.get('omission_quote') and item.get('identity_quote')):
                errors.append('positive missing retest/identity quotation')
            if item.get('disposition') == 'represented' and str(item.get('matched_input_row_index')) not in rows:
                errors.append('duplicate row absent from assignment')
            validated.append(dict(item, validation_errors=errors, mechanically_valid=not errors))
        rid = bid + '_' + work['file_key']
        path = requestdir / (rid + '.json')
        a.atomic(path, {'request_id': rid, 'file_key': work['file_key'],
            'work_key': work['work_key'], 'source_path': work['text_path'],
            'source_instruction': work['source_instruction'],
            'coding_path': work['coding_path'], 'prior_adjudication_path': work['prior_adjudication_path'],
            'prior_state_path': str(R / 'argon' / (work['file_key'] + '.state.json')),
            'shipped_rows': work['shipped_originals'],
            'requested_fields': [{'field': 'missing_row', 'target_index': x['target_index'],
                'previous_final_verdict': x['previous_final_verdict']} for x in work['candidates']],
            'candidate_identities': work['candidates'],
            'luna_triage': [x for x in validated if x['file_key'] == work['file_key']],
            'bibliography_metadata_path': str(F / 'bibliography_metadata.json'),
            'quality_gate': 'Luna is triage only. Independently establish actual empirical retesting and absence under ALL shipped identities/alternate reports. Read prior objections. No paper outcome is being requested.'})
        requests.append({'request_id': rid, 'input_path': str(path),
                         'field_count': len(selected), 'status': 'pending'})
    a.atomic(F / 'luna/results' / (bid + '.validation.json'),
             {'batch_id': bid, 'valid_envelope': True, 'records': validated})
    # Parent is sole writer of this dynamically growing candidate queue.
    old = read(requestdir / 'index.json', [])
    known = {x['request_id'] for x in old}
    a.atomic(requestdir / 'index.json', old + [x for x in requests if x['request_id'] not in known])
    entry['validated'] = True
    entry['mechanically_valid_records'] = sum(x['mechanically_valid'] for x in validated)
    a.atomic(F / 'luna/index.json', index)
    return {'batch_id': bid, 'valid': True, 'records': len(validated),
            'mechanically_valid': entry['mechanically_valid_records'],
            'triage': dict(collections.Counter(x['disposition'] for x in validated))}


def validate_candidate_review(rid):
    outdir = F / 'candidate_reviews'
    payload = read(outdir / (rid + '.input.json'))
    result = read(outdir / (rid + '.result.json'))
    expected = {(w['file_key'], a.decision_key(x))
                for w in payload['requests'] for x in w['requested_fields']}
    entries = read(F / 'candidate_requests/index.json')
    selected_ids = {w['request_id'] for w in payload['requests']}
    malformed = not isinstance(result, dict) or not isinstance(result.get('decisions'), list)
    if not malformed:
        keys = [(d.get('file_key'), a.decision_key(d)) for d in result['decisions']]
        malformed = set(keys) != expected or len(keys) != len(expected)
    if malformed:
        for item in entries:
            if item['request_id'] in selected_ids:
                item.update(status='pending' if item.get('review_attempts', 1) < 2 else 'review_failed_terminal',
                            prior_review_id=rid,
                            review_objection='Earlier expert did not return a complete valid envelope. Read previous result if it exists; independently return every requested field.')
        a.atomic(F / 'candidate_requests/index.json', entries)
        return {'review_id': rid, 'valid_envelope': False, 'requires_parent_attention': True}
    checked = []
    for work in payload['requests']:
        source = Path(work['source_path']).read_text()
        requested_keys = {a.decision_key(x) for x in work['requested_fields']}
        for decision in result['decisions']:
            if decision['file_key'] != work['file_key'] or a.decision_key(decision) not in requested_keys:
                continue
            checked.append({'decision': decision,
                'mechanically_valid': c.valid_decision(decision, source) and decision['quote'] in source,
                'source_sha256': __import__('hashlib').sha256(Path(work['source_path']).read_bytes()).hexdigest()})
    a.atomic(outdir / (rid + '.validation.json'), {'review_id': rid, 'valid_envelope': True,
             'parent_inspection_pending': True, 'records': checked})
    for item in entries:
        if item['request_id'] in selected_ids:
            item['status'] = 'expert_review_complete_pending_parent'
    a.atomic(F / 'candidate_requests/index.json', entries)
    return {'review_id': rid, 'valid_envelope': True, 'decisions': len(checked),
            'mechanically_valid': sum(x['mechanically_valid'] for x in checked), 'parent_inspection_pending': True}


def candidate_relay(snapshot):
    spec = importlib.util.spec_from_file_location('candidate_cli_relay', R / 'evidence_followup/candidate_cli_relay.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Relay(R, snapshot)


def candidate_cli_dispatch(result=None):
    """Parent-only intent/commit; delegate_task itself belongs to the native tick.

    The existing parent lock serializes intent writes and publication. A lost tool
    response is retried with the SAME clientRequestId, never a new round.
    """
    if read(F / 'state.json').get('candidate_cli_dispatch', {}).get('enabled') is not True:
        return None
    with _candidate_parent_lock():
        state = read(F / 'state.json')
        config = state.get('candidate_cli_dispatch', {})
        if state.get('status') != 'active' or config.get('enabled') is not True:
            return None
        snapshot = config['snapshot']
        relay = candidate_relay(snapshot)
        intent = config.get('intent')
        if result is not None:
            if not intent or result.get('clientRequestId') != intent['clientRequestId']:
                raise ValueError('dispatch intent identity mismatch')
            options = result.get('options', [])
            options = options if isinstance(options, dict) else {x['id']: x['value'] for x in options}
            if (not result.get('taskId') or result.get('providerInstanceId') != 'codex' or
                    result.get('model') != 'gpt-6.1-sol' or
                    options.get('reasoningEffort') != 'medium' or options.get('serviceTier') != 'default'):
                raise ValueError('candidate CLI actual task/model/options mismatch; parent diagnosis required')
            if intent.get('taskId') and intent['taskId'] != result['taskId']:
                raise ValueError('dispatch returned different actual taskId')
            workers = intent['workers']
            # Register ACTUAL returned identity durably BEFORE publishing control.
            register(dict(result, lane='candidate_cli', cli_snapshot=snapshot,
                          cli_workers=workers, slot_cost=workers + 1))
            state = read(F / 'state.json')
            intent['taskId'] = result['taskId']
            state['candidate_cli_dispatch']['intent'] = intent
            _candidate_atomic(F / 'state.json', state)
            _candidate_atomic(F / 'candidate_cli/control.json', dict(drain=False, clientRequestId=intent['clientRequestId'], reservation=dict(
                taskId=result['taskId'], snapshot=snapshot, workers=workers,
                model='Gemini 4 Argon (High)', billing='included_subscription')))
            config = state['candidate_cli_dispatch']
            config['last_round'] = intent
            config['next_round'] = intent['round'] + 1
            config.pop('intent', None)
            _candidate_atomic(F / 'state.json', state)
            return intent
        if intent:
            if intent['snapshot'] != snapshot:
                raise ValueError('pending dispatch intent snapshot changed; parent diagnosis required')
            return intent
        active = [t for t in state['tasks'] if t.get('status') in ACTIVE or t.get('hasPendingChildRuns')]
        if any(t.get('lane') == 'candidate_cli' for t in active):
            return None
        progress = read(relay.out / 'progress.json', {})
        if progress.get('blocker') or progress.get('infrastructure_circuit_open') or progress.get('infrastructure_streak', 0) >= 3:
            return None  # Includes drain, source, reservation and orphan blockers: parent diagnoses.
        try:
            snap = relay.load()
            if not (relay.out / 'prepared.json').exists():
                return None
            relay.check(snap)
        except (ValueError, OSError):
            return None  # Immutable source/snapshot blockers require parent diagnosis.
        work = False
        for bundle in snap['bundles']:
            ledger = relay.ledger(bundle)
            if ledger['status'] == 'source_changed':
                return None
            if ledger['status'] not in {'validated', 'exhausted'} and (
                    bundle.get('baseline', 0) + len(ledger['attempts']) < 2 or
                    any(x['status'] == 'reserved' for x in ledger['attempts'])):
                work = True  # Includes spent reservations needing conservative recovery.
            for attempt in ledger['attempts']:
                if attempt['status'] != 'reserved':
                    continue
                process = read(Path(attempt['raw_path'] + '.process.json'), {})
                if process.get('status') == 'running':
                    try:
                        os.killpg(process['pid'], 0)
                    except ProcessLookupError:
                        pass
                    else:
                        return None
        if not work:
            return None
        argon = 0
        old = False
        for t in active:
            lane = t.get('lane', '')
            if lane == 'argon_runner':
                if t.get('slot_cost', 0) < 4:
                    return None
                old = True
                argon += 3
            elif lane == 'argon_native':
                argon += 1
            elif 'argon' in lane or 'argon' in str(t.get('model', '')).lower():
                return None
        costs = [t.get('slot_cost', 1) for t in active]
        metadata = state.get('metadata_infrastructure_slots', 0)
        if any(type(x) is not int or x < 1 for x in costs) or type(metadata) is not int or metadata < 0:
            return None
        available = min(10, state.get('max_combined_children_and_infrastructure', 10)) - 1 - sum(costs) - metadata
        worker_limit = config.get('max_workers', 4)
        if type(worker_limit) is not int or not 1 <= worker_limit <= 4:
            raise ValueError('candidate CLI max_workers must be 1..4')
        workers = min(worker_limit, 1 if old else 4, 4 - argon, available - 1)
        if workers < 1:
            return None
        if config.get('max_calls_per_worker') != 1:
            raise ValueError('bounded dispatch requires max_calls_per_worker:1')
        round_number = config.get('next_round', 1)
        if type(round_number) is not int or round_number < 1:
            raise ValueError('invalid candidate CLI next_round')
        intent = dict(round=round_number, snapshot=snapshot, workers=workers,
                      clientRequestId='flora-candidate-cli-' + snapshot + '-round-' + str(round_number))
        config['intent'] = intent
        _candidate_atomic(F / 'state.json', state)
        return intent


def _candidate_atomic(path, value):
    # Reuse parent publication, then persist both bytes and rename before any
    # delegate/control side effect. Intent recovery must survive host loss.
    a.atomic(path, value)
    with Path(path).open('rb') as stream:
        os.fsync(stream.fileno())
    fd = os.open(Path(path).parent, os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _candidate_parent_lock():
    # Same serialization domain as parent snapshot preparation/reconciliation.
    import contextlib
    import fcntl
    @contextlib.contextmanager
    def locked():
        with (F / 'candidate_cli/parent.lock').open('a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
    return locked()


def reconcile_candidate_cli():
    state = read(F / 'state.json')
    config = state.get('candidate_cli_dispatch', {})
    if config.get('enabled') is not True:
        return None
    return candidate_relay(config['snapshot']).reconcile()


def plan():
    reconcile_files()
    state = read(F / 'state.json')
    active = [x for x in state['tasks'] if x['status'] in ACTIVE or x.get('hasPendingChildRuns')]
    index = read(F / 'luna/index.json')
    return {'status': state['status'], 'active': active,
            'slot_cost': sum(x.get('slot_cost', 1) for x in active),
            'luna_limit': min(state.get('max_parallel_luna', 3), 2)
                if any(x.get('lane') == 'additional_acquisition' for x in active)
                else state.get('max_parallel_luna', 3),
            'additional_infrastructure_slots': state.get('metadata_infrastructure_slots', 0),
            'combined_ceiling': min(10, state.get('max_combined_children_and_infrastructure', 10)),
            'luna_active': sum(x.get('lane') == 'luna' for x in active),
            'luna_pending': [x for x in index if x['status'] == 'pending'],
            'luna_completed': sum(x.get('validated', False) for x in index),
            'luna_total': len(index)}


def prepare_candidate_review():
    state = read(F / 'state.json')
    if state.get('native_argon_dispatch_paused') or state.get('candidate_cli_dispatch', {}).get('enabled') is True:
        return None
    active = [x for x in state['tasks'] if x['status'] in ACTIVE or x.get('hasPendingChildRuns')]
    relays = any(x.get('lane') == 'argon_runner' for x in active)
    limit = 1 if relays else 4
    if sum(x.get('lane') == 'argon_native' for x in active) >= limit:
        return None
    if sum(x.get('slot_cost', 1) for x in active) + state.get('metadata_infrastructure_slots', 0) >= state.get('max_combined_children_and_infrastructure', 10) - 1:
        return None
    indexpath = F / 'candidate_requests/index.json'
    index = read(indexpath, [])
    selected, count = [], 0
    pending = []
    acquisition_finished = read(F / 'acquisition/progress.json', {}).get('queue_complete', False)
    for entry in index:
        if entry['status'] != 'pending':
            continue
        payload = read(Path(entry['input_path']))
        coding = read(Path(payload['coding_path']), {})
        if coding.get('evidence_level') != 'full_text' and not acquisition_finished:
            continue  # allow acquisition to finish before adjudicating abstract limits
        prior_positive = any(x.get('previous_final_verdict') == 'error' for x in payload['requested_fields'])
        priority = 0 if entry.get('priority') == 'parent_scope_objection' else 1 if entry.get('review_kind') == 'fields' else 2
        pending.append(((priority, coding.get('evidence_level') != 'full_text', not prior_positive), entry, payload))
    for _, entry, payload in sorted(pending, key=lambda x: (x[0], x[1]['request_id'])):
        if selected and entry.get('review_kind', 'candidates') != selected[0][0].get('review_kind', 'candidates'):
            continue
        if count + entry['field_count'] > 6:
            continue
        if entry.get('prior_review_id'):
            payload = dict(payload, prior_expert_result_path=str(F / 'candidate_reviews' / (entry['prior_review_id'] + '.result.json')),
                           unresolved_objection=entry.get('review_objection'))
        selected.append((entry, payload))
        count += entry['field_count']
        if count == 6:
            break
    if not selected:
        return None
    outdir = F / 'candidate_reviews'
    outdir.mkdir(exist_ok=True)
    rid = 'review_' + str(len(list(outdir.glob('*.input.json')))).zfill(4)
    inputpath = outdir / (rid + '.input.json')
    outputpath = outdir / (rid + '.result.json')
    kind = selected[0][0].get('review_kind', 'candidates')
    instructions = 'FIELD_REVIEW_INSTRUCTIONS.md' if kind == 'fields' else 'REVIEW_INSTRUCTIONS.md'
    a.atomic(inputpath, {'review_id': rid, 'review_kind': kind, 'requests': [x[1] for x in selected],
        'codebook_path': str(R / 'codebook.md'),
        'metadata_path': str(F / 'bibliography_metadata.json'),
        'instructions_path': str(F / 'candidate_reviews' / instructions)})
    for entry, _ in selected:
        entry.update(status='review_prepared', review_id=rid,
                     review_attempts=entry.get('review_attempts', 0) + 1)
    a.atomic(indexpath, index)
    return {'review_id': rid, 'input_path': str(inputpath.resolve()),
            'output_path': str(outputpath.resolve()), 'candidates': count,
            'request_ids': [x[0]['request_id'] for x in selected], 'review_kind': kind,
            'instructions_path': str((F / 'candidate_reviews' / instructions).resolve())}


if __name__ == '__main__':
    command = sys.argv[1]
    result = candidate_cli_dispatch(json.loads(sys.argv[2]) if len(sys.argv) > 2 else None) if command == 'candidate-cli-dispatch' else reconcile_candidate_cli() if command == 'reconcile-candidate-cli' else plan() if command == 'plan' else register(json.loads(sys.argv[2])) if command == 'register' else prepare_candidate_review() if command == 'prepare-candidate-review' else validate_candidate_review(sys.argv[2]) if command == 'validate-candidate' else validate_luna(sys.argv[2])
    print(json.dumps(result))
