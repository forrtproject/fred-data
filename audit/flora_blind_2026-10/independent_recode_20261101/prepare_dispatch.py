#!/usr/bin/env python3
"""Parent preflight only: build a blind task from frozen IDs, never start it."""
import argparse
import hashlib
import json
from pathlib import Path

from prepare_packets import OUT, PACKETS


def read(path):
    return json.loads(path.read_text())


def prepare(group_id, provider, attempt):
    if attempt not in (1, 2):
        raise ValueError('Two attempts maximum')
    state = read(OUT / 'state.json')
    group = next(g for g in read(OUT / 'dispatch_plan.json')['groups'] if g['group_id'] == group_id)
    if PACKETS.is_symlink():
        raise ValueError('Active packet root must stay on local SSD')
    role = 'blind_coder' if provider == 'opus' else 'blind_comparison_coder'
    prior = [t for t in state['tasks'] if t.get('group_id') == group_id and t['role'] == role]
    if any(t['status'] in ('running', 'queued', 'waiting') or t['status'].startswith('cancel_requested') for t in prior):
        raise ValueError('Owned task still active or cancellation unconfirmed')
    if any(t['status'] == 'completed_parent_mechanically_validated' for t in prior):
        raise ValueError('Already validated; never duplicate this role/group')
    if attempt == 2 and not any(t.get('attempt') == 1 for t in prior):
        raise ValueError('Retry requires preserved first attempt')
    if any(t.get('attempt') == attempt for t in prior):
        raise ValueError('Attempt already registered; reconcile exact task instead')
    active = [t for t in state['tasks'] if t['status'] in ('running', 'queued', 'waiting')
              or t['status'].startswith('cancel_requested')]
    if len(active) >= state['max_active_model_children']:
        raise ValueError('No free model slot')
    registry = read(OUT / 'packet_input_receipts.json')['documents']
    packets = []
    for doc in group['document_ids']:
        packet = PACKETS / doc
        if not packet.is_dir() or doc not in registry:
            raise ValueError('Missing registered input packet: ' + doc)
        if not packet.resolve().is_relative_to(PACKETS.resolve()):
            raise ValueError('Packet escapes active source root')
        for name, expected in registry[doc].items():
            if hashlib.sha256((packet / name).read_bytes()).hexdigest() != expected:
                raise ValueError('Frozen packet changed: ' + doc + '/' + name)
        packets.append(str(packet.resolve()) + '/')
    output = PACKETS / 'outputs' / provider / group_id / f'attempt_{attempt}'
    if not output.resolve().is_relative_to((PACKETS / 'outputs').resolve()):
        raise ValueError('Output escapes private owned root')
    if any((output / doc / 'coding.json').exists() for doc in group['document_ids']):
        raise ValueError('Output already exists; inspect it instead of dispatching')
    prompt = (OUT / 'blind_task_prompt.txt').read_text()
    prompt = prompt.replace('{packet_directories}', '\n'.join(packets)).replace('{output_dir}', str(output))
    if '{packet_directories}' in prompt or '{output_dir}' in prompt:
        raise ValueError('Unexpanded prompt paths')
    target = ({'providerInstanceId': 'claudeAgent', 'model': 'claude-opus-5-5',
               'options': {'effort': 'high', 'fastMode': False}} if provider == 'opus'
              else {'providerInstanceId': 'codex', 'model': 'gpt-6.1-sol',
                    'options': {'reasoningEffort': 'medium'}})
    request_id = f"flora-independent-{provider}-{group_id.replace('_', '')}-20261101-attempt{attempt}"
    return {'delegate_args': {'clientRequestId': request_id, 'title': 'Independent primary-source coding ' + group_id,
                             'role': 'research', 'mode': 'async', 'target': target, 'task': prompt},
            'dispatch_record': {'clientRequestId': request_id, 'role': role, 'group_id': group_id,
                                'packet_ids': group['document_ids'], 'attempt': attempt,
                                'output_dir': str(output), 'output_layout': 'per_document'},
            'preflight': {'registered_absolute_inputs_verified': True, 'frozen_input_hashes_verified': True,
                          'owned_output_root_verified': True, 'max_attempts': 2, 'active_model_children': len(active)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('group_id')
    parser.add_argument('--provider', choices=['opus', 'sol'], default='opus')
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    print(json.dumps(prepare(args.group_id, args.provider, args.attempt)))
