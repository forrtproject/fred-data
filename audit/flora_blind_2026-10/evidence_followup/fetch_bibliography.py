#!/usr/bin/env python3
"""Free, bounded Crossref identity enrichment; never infer study outcomes."""
import concurrent.futures
import datetime
import json
from pathlib import Path
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

F = Path(__file__).resolve().parent
R = F.parent
sys.path.insert(0, str(R / 'scripts'))
import adjudicate as a
import compare as c

gate = threading.Lock()
next_request = 0.0


def fetch(doi):
    global next_request
    with gate:
        pause = max(0, next_request - time.monotonic())
        if pause:
            time.sleep(pause)
        next_request = time.monotonic() + .35
    url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='/')
    request = urllib.request.Request(url, headers={'User-Agent': 'FLoRA-identity-audit/1.0', 'Accept': 'application/json'})
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(request, timeout=20) as stream:
            message = json.load(stream)['message']
        return doi, {'status': 'verified_metadata', 'source_url': url, 'retrieved_at': stamp,
            'doi': c.clean_doi(message.get('DOI')), 'title': message.get('title', []),
            'authors': [{'given': x.get('given', ''), 'family': x.get('family', ''),
                         'literal': x.get('literal', '')} for x in message.get('author', [])],
            'published': message.get('published', {}), 'type': message.get('type'),
            'relation': message.get('relation', {}), 'container_title': message.get('container-title', []),
            'volume': message.get('volume', ''), 'issue': message.get('issue', ''),
            'page': message.get('page', ''),
            'scope': 'Bibliographic identity only; different DOI/title/year alone does not prove a distinct original finding.'}
    except (urllib.error.URLError, ValueError, KeyError, TimeoutError) as exc:
        return doi, {'status': 'unavailable', 'source_url': url, 'retrieved_at': stamp,
                     'error': str(exc)[:300]}


def run():
    dois = set()
    works = set()
    for path in (F / 'luna/batches').glob('*.input.json'):
        for work in json.loads(path.read_text())['works']:
            works.add(work['file_key'])
            dois.update(c.clean_doi(x.get('doi_o')) for x in work['shipped_originals'])
            dois.update(c.clean_doi(x['blind_target'].get('doi')) for x in work['candidates'])
    for path in (F / 'field_requests').glob('fields_*.json'):
        work = json.loads(path.read_text())
        dois.update(c.clean_doi(x.get('doi_o')) for x in work['shipped_rows'])
    dois = {x for x in dois if x.startswith('10.')}
    target = F / 'bibliography_metadata.json'
    obj = json.loads(target.read_text()) if target.exists() else {'records': {}}
    pending = sorted(dois - obj['records'].keys())
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch, doi) for doi in pending]
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            doi, metadata = future.result()
            obj['records'][doi] = metadata
            if i % 20 == 0:
                obj.update(status='active', requested=len(dois), completed=len(obj['records']))
                a.atomic(target, obj)
    obj.update(status='complete', requested=len(dois), completed=len(obj['records']),
               completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    a.atomic(target, obj)
    return {k: v for k, v in obj.items() if k != 'records'}


if __name__ == '__main__':
    print(json.dumps(run()))
