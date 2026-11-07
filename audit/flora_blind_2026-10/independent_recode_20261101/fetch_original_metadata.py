#!/usr/bin/env python3
"""Fetch authoritative Crossref records for adversary-supported original corrections. Reruns reuse saved records."""
import difflib
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import build_field_ledger as L
from build_verified_proposals import metadata_title, norm, original_replacements

OUT = L.P / 'authoritative_originals_20261103'
REGISTRY = L.T / 'authoritative_original_metadata.json'


def fetch(doi):
    path = OUT / (hashlib.sha256(doi.encode()).hexdigest()[:16] + '.json')
    if not path.exists():
        url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='')
        request = urllib.request.Request(url, headers={'User-Agent': 'flora-audit-metadata-check'})
        path.write_bytes(urllib.request.urlopen(request, timeout=40).read())
        time.sleep(0.2)
    return path


def check(proposed, message):
    """Exact target identity: the record must name the proposed work, by DOI, title and first author."""
    problems = []
    if L.identifier(message.get('DOI')) != L.identifier(proposed.get('doi')):
        problems.append('doi')
    # The DOI must match exactly, so a title may differ only by a typo carried over from a reference list.
    title, found = norm(proposed.get('title')), norm(metadata_title(message))
    if title != found and not (title and title in found) and difflib.SequenceMatcher(None, title, found).ratio() < 0.97:
        problems.append('title')
    families = [a.get('family', '') for a in message.get('author', [])]
    if not families or norm(L.surname(proposed.get('authors'))) != norm(families[0]):
        problems.append('first_author')
    return problems


def search_by_title(proposed):
    """Find a DOI for a proposal without one. Only an exact title, first author and year match counts."""
    title = str(proposed.get('title') or '')
    key = hashlib.sha256(('search:' + title).encode()).hexdigest()[:16]
    path = OUT / (key + '.json')
    if not path.exists():
        query = urllib.parse.urlencode({'query.bibliographic': f"{title} {proposed.get('authors', '')[:60]}", 'rows': 8})
        request = urllib.request.Request('https://api.crossref.org/works?' + query, headers={'User-Agent': 'flora-audit-metadata-check'})
        path.write_bytes(urllib.request.urlopen(request, timeout=40).read())
        time.sleep(0.2)
    for item in json.loads(path.read_text())['message']['items']:
        families = [a.get('family', '') for a in item.get('author', [])]
        issued = (item.get('issued', {}).get('date-parts') or [[None]])[0][0]
        if norm(metadata_title(item)) == norm(title) and families and norm(L.surname(proposed.get('authors'))) == norm(families[0]) \
                and str(issued) == str(proposed.get('year')):
            return item['DOI']
    return None


def main():
    OUT.mkdir(exist_ok=True)
    ledger = L.read(L.OUTPUT)
    rows, skipped = {}, {}
    for field in ledger['fields']:
        if field['field'] != 'original' or 'adversary_pending' in field['reasons']:
            continue
        review = field.get('adversarial_review')
        close = field.get('close_read') or {}
        proposed = dict(field['proposed_value'] or {})
        supported = (review and review['verdict'] == 'supported' and review.get('confidence') == 'high') or close.get('verdict') == 'correct'
        if not supported or field['state'] not in ('agreement_needs_authoritative_metadata', 'adversary_supported_candidate', 'close_read_supported_candidate'):
            continue
        row = str(field['input_row_index'])
        try:
            if not L.identifier(proposed.get('doi')):
                proposed['doi'] = search_by_title(proposed)
                if not proposed['doi']:
                    skipped[row] = 'no_doi_in_proposal_and_no_exact_crossref_match'
                    continue
            path = fetch(proposed['doi'])
            message = json.loads(path.read_text())['message']
            problems = check(proposed, message)
            if problems:
                skipped[row] = 'mismatch:' + ','.join(problems)
                continue
            rows[row] = dict(doi=message['DOI'], source='Crossref', path=str(path.relative_to(L.ROOT)),
                             sha256=hashlib.sha256(path.read_bytes()).hexdigest(), replacements=original_replacements(message))
        except Exception as error:  # A record we cannot verify stays held.
            skipped[row] = 'unverified:' + type(error).__name__
    REGISTRY.write_text(json.dumps(dict(schema_version=1, source='Crossref REST API', rows=rows, held=skipped), ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(dict(verified=len(rows), held=skipped), indent=1))


if __name__ == '__main__':
    sys.exit(main())
