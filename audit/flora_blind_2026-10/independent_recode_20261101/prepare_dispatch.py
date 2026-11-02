#!/usr/bin/env python3
"""Parent preflight only: build a blind task from frozen IDs, never start it."""
import argparse
import hashlib
import json
from pathlib import Path

from prepare_packets import OUT, PACKETS


def read(path):
    return json.loads(path.read_text())


def identical_source_budget(document_ids, role, tasks, registry, upgrades):
    """Charge byte-identical registered articles to one role/source budget."""
    documents = set(document_ids)
    hashes = []
    for doc in document_ids:
        digest = registry.get(doc, {}).get('article.txt', '')
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Missing or invalid frozen article hash: ' + doc)
        if digest in hashes:
            raise ValueError('Group contains identical source aliases')
        hashes.append(digest)
    limits = {}
    for digest in hashes:
        aliases = {doc for doc, files in registry.items() if files.get('article.txt') == digest}
        documents.update(aliases)
        caps = [item.get('max_attempts_per_role', 2) for item in upgrades
                if item['document_id'] in aliases]
        if any(type(cap) is not int or not 1 <= cap <= 2 for cap in caps):
            raise ValueError('Invalid source-specific attempt limit')
        limit = min([2] + caps)
        prior = [task for task in tasks if task.get('role') == role
                 and aliases.intersection(task.get('packet_ids', []))]
        if any(task['status'] in ('running', 'queued', 'waiting',
                                  'completed_pending_parent_validation')
               or task['status'].startswith('cancel_requested') for task in prior):
            raise ValueError('Identical source role still active or awaiting validation')
        if len(prior) >= limit:
            raise ValueError('Identical source attempt budget exhausted')
        limits[digest] = {'document_ids': sorted(aliases), 'max_attempts': limit,
                          'prior_role_tasks': len(prior)}
    return documents, min(value['max_attempts'] for value in limits.values()), limits


def prepare(group_id, provider, attempt):
    if attempt not in (1, 2):
        raise ValueError('Two attempts maximum')
    state = read(OUT / 'state.json')
    upgrade = None
    plan = read(OUT / 'dispatch_plan.json')['groups']
    group = next((g for g in plan if g['group_id'] == group_id), None)
    if group is None:
        upgrade = next((d for d in read(OUT / 'source_upgrades.json')['upgrades']
                        if d['document_id'] == group_id), None)
        if upgrade is None and not any(group_id in g['document_ids'] for g in plan):
            raise ValueError('Group or source version absent from parent registry')
        group = {'group_id': group_id, 'document_ids': [upgrade['document_id'] if upgrade else group_id]}
    if PACKETS.is_symlink():
        raise ValueError('Active packet root must stay on local SSD')
    role = 'blind_coder' if provider == 'opus' else 'blind_comparison_coder'
    budget_documents = set(group['document_ids'])
    if upgrade and upgrade.get('primary_pdf_sha256'):
        budget_documents.update(d['document_id'] for d in read(OUT / 'source_upgrades.json')['upgrades']
                                if d.get('primary_pdf_sha256') == upgrade['primary_pdf_sha256']
                                and d['parent_work_key'] == upgrade['parent_work_key'])
    if upgrade and upgrade.get('attempt_history_document_ids'):
        versions = {d['document_id']: d for d in read(OUT / 'source_upgrades.json')['upgrades']}
        for doc_id in upgrade['attempt_history_document_ids']:
            previous = versions[doc_id]
            if (previous['parent_work_key'] != upgrade['parent_work_key']
                    or not previous.get('primary_pdf_sha256')
                    or previous['primary_pdf_sha256'] != upgrade.get('primary_pdf_sha256')):
                raise ValueError('Cannot borrow an attempt from another primary report')
            budget_documents.add(doc_id)
    if upgrade:
        limits = [d.get('max_attempts_per_role', 2)
                  for d in read(OUT / 'source_upgrades.json')['upgrades']
                  if d['document_id'] in budget_documents]
        if not all(type(limit) is int and 1 <= limit <= 2 for limit in limits):
            raise ValueError('Invalid source-specific attempt limit')
        if attempt > min(limits):
            raise ValueError('Source-specific attempt budget exhausted')
    validated_key = 'validated_opus_documents' if provider == 'opus' else 'validated_fresh_sol_documents'
    if set(group['document_ids']) & set(state.get(validated_key, [])):
        raise ValueError('Already validated packet; never duplicate this role/source version')
    prior = [t for t in state['tasks'] if t['role'] == role and
             (t.get('group_id') == group_id or set(t.get('packet_ids', [])) & budget_documents)]
    if any(t['status'] in ('running', 'queued', 'waiting') or t['status'].startswith('cancel_requested') for t in prior):
        raise ValueError('Owned task still active or cancellation unconfirmed')
    if any(t['status'] == 'completed_parent_mechanically_validated'
           and set(t.get('packet_ids', [])) & set(group['document_ids']) for t in prior):
        raise ValueError('Already validated; never duplicate this role/group')
    if attempt == 2 and not any(t.get('attempt') == 1 for t in prior):
        raise ValueError('Retry requires preserved first attempt')
    if any(t.get('attempt') == attempt for t in prior):
        raise ValueError('Attempt already registered; reconcile exact task instead')
    active = [t for t in state['tasks'] if t['status'] in ('running', 'queued', 'waiting')
              or t['status'].startswith('cancel_requested')]
    occupied_slots = sum(t.get('reserved_slots', 1) for t in active)
    if occupied_slots >= state['max_active_model_children']:
        raise ValueError('No free model slot')
    registry = read(OUT / 'packet_input_receipts.json')['documents']
    identical_documents, identical_limit, identical_limits = identical_source_budget(
        group['document_ids'], role, state['tasks'], registry,
        read(OUT / 'source_upgrades.json')['upgrades'])
    budget_documents.update(identical_documents)
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
                                'attempt_budget_document_ids': sorted(budget_documents),
                                'identical_source_budgets': identical_limits,
                                'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                                'output_dir': str(output), 'output_layout': 'per_document'},
            'preflight': {'registered_absolute_inputs_verified': True, 'frozen_input_hashes_verified': True,
                          'owned_output_root_verified': True,
                          'max_attempts': min([identical_limit] + (limits if upgrade else [2])),
                          'active_model_children': len(active),
                          'occupied_model_and_helper_slots': occupied_slots}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('group_id')
    parser.add_argument('--provider', choices=['opus', 'sol'], default='opus')
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    print(json.dumps(prepare(args.group_id, args.provider, args.attempt)))
