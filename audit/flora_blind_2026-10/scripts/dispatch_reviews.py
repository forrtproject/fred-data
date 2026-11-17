#!/usr/bin/env python3
"""Drain parent-triaged queues and final scopes through one four-call pool."""
import collections
import concurrent.futures
import datetime
import fcntl
import json
from pathlib import Path
import sys

import adjudicate as a


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def run(selections, root=a.R, base_worker=a.one, scope_worker=a.final_scope_one,
        emit=print, now=utcnow):
    root = Path(root)
    lock = (root / 'argon/runner.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        deadline = a.adjudication_deadline(root)
        groups, keys = {}, collections.defaultdict(set)
        for selection in selections:
            for item in json.loads(Path(selection).read_text())['items']:
                fk, key = item['file_key'], a.decision_key(item)
                if key not in keys[fk]:
                    groups.setdefault(fk, []).append(item)
                    keys[fk].add(key)
        queue = collections.deque(groups)
        scope_started, active, results = set(), {}, []

        def state(fk):
            return a.c.read_json(root / 'argon' / (fk + '.state.json'))[0] or {}

        def next_scope():
            for path in sorted((root / 'argon').glob('*.state.json')):
                fk = path.name.split('.')[0]
                if fk not in scope_started:
                    s = state(fk)
                    if s.get('status') == 'scope_review_pending' and s.get('attempts') == 1:
                        return fk

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            while True:
                while len(active) < 4 and now() < deadline:
                    fk = next_scope()
                    if fk:
                        scope_started.add(fk)
                        future = executor.submit(scope_worker, fk)
                        kind = 'final_scope'
                    else:
                        while queue:
                            fk = queue.popleft()
                            s = state(fk)
                            if s.get('status') not in ('validated', 'unresolved', 'scope_review_pending',
                                                       'scope_review_running', 'running', 'retry_pending') and s.get('attempts', 0) < 2:
                                break
                        else:
                            break
                        future = executor.submit(base_worker, fk, groups[fk])
                        kind = 'initial_review'
                    active[future] = (kind, fk)
                    emit(json.dumps({'event': 'dispatched', 'kind': kind, 'file_key': fk,
                                     'at': now().isoformat()}), flush=True)
                if not active:
                    break
                done, _ = concurrent.futures.wait(active, return_when=concurrent.futures.FIRST_COMPLETED)
                for future in done:
                    kind, fk = active.pop(future)
                    try:
                        result = future.result()
                    except Exception as error:
                        result = {'file_key': fk, 'status': 'runner_error', 'reason': str(error)}
                    results.append({'kind': kind, **result})
                    emit(json.dumps(results[-1]), flush=True)
        summary = {'finished_at': now().isoformat(), 'review_results': results,
                   'not_dispatched_before_deadline': list(queue)}
        a.atomic(root / 'review_dispatch_summary.json', summary)
        return summary
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit('Pass prepared selection JSON paths, in priority order.')
    run(sys.argv[1:])
