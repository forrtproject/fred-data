#!/usr/bin/env python3
"""Parent-only input receipts, independently rebuilt from registered source bytes."""
import hashlib
import json
import re
from pathlib import Path

from prepare_packets import B, BAD, INSTRUCTIONS, META, OUT, PACKETS


def read(path):
    return json.loads(path.read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def freeze():
    entries = {}
    inventory = read(OUT / 'source_inventory.json')
    for doc in inventory['documents']:
        if not doc['active'] or doc['status'] != 'ready':
            continue
        packet = Path(doc['packet_path'])
        original = Path(doc['source_paths'][0]).read_bytes()
        expected = original
        if 'source_character_range' in doc:
            parent_hashes = [r['parent_source_checks']['raw_sha256'] for r in doc['source_receipts']
                             if 'parent_source_checks' in r]
            assert parent_hashes and all(sha(original) == h for h in parent_hashes), 'Parent collection changed'
            a, z = doc['source_character_range']
            expected = original.decode()[a:z].encode()
        assert sha(expected) == doc['source_checks']['raw_sha256'], doc['document_id'] + ': original source changed'
        assert (packet / 'article.txt').read_bytes() == expected, doc['document_id'] + ': packet differs from original'
        metadata = {k: doc['metadata'].get(k) for k in META}
        metadata.update(work_key=doc['document_id'], status='done', text_sha256=sha(expected))
        parser = metadata.get('parser')
        if parser and (BAD.search(parser) or re.search(r'blind|audit|parent|coding|verdict|target', parser, re.I)):
            metadata['parser'] = None
        assert read(packet / 'metadata.json') == metadata, doc['document_id'] + ': metadata changed'
        assert (packet / 'instructions.txt').read_text() == INSTRUCTIONS
        for name in ('codebook.md', 'coding_schema.json'):
            assert (packet / name).read_bytes() == (B / name).read_bytes()
        manifest = read(packet / 'chunks.json')
        expected_chunks = []
        text = expected.decode()
        for index, start in enumerate(range(0, len(text), 12000), 1):
            end = min(start + 12000, len(text))
            name = f'chunks/chunk_{index:05d}.txt'
            raw = text[start:end].encode()
            assert (packet / name).read_bytes() == raw
            expected_chunks.append(dict(file=name, character_start=start, character_end=end, sha256=sha(raw)))
        assert manifest == dict(text_sha256=sha(expected), unicode_characters=len(text), chunks=expected_chunks)
        assert not (packet / 'source_blocks.json').exists()
        entries[packet.name] = hashes(packet)
    reserved = PACKETS / 'document_0001'
    if reserved.exists():
        assert (reserved / 'article.txt').read_bytes() == (B / 'texts/6070e18087845e69.txt').read_bytes()
        assert read(reserved / 'metadata.json')['text_sha256'] == sha((reserved / 'article.txt').read_bytes())
        entries[reserved.name] = {name: sha((reserved / name).read_bytes())
                                 for name in ('article.txt', 'metadata.json', 'codebook.md', 'schema.json')}
    # Source upgrades have their own parent source registry; they do not alter
    # the frozen initial cohort or invalidate historical versions.
    upgrades_path = OUT / 'source_upgrades.json'
    if upgrades_path.exists():
        for doc in read(upgrades_path)['upgrades']:
            packet = Path(doc['packet_path'])
            raw = (packet / 'article.txt').read_bytes()
            assert sha(raw) == doc['source_sha256']
            block_map = read(packet / 'source_blocks.json')
            assert block_map == dict(text_sha256=sha(raw), blocks=doc['source_blocks'])
            text = raw.decode()
            for block, source in zip(doc['source_blocks'], doc['parent_sources'], strict=True):
                source_raw = Path(source['path']).read_bytes()
                assert sha(source_raw) == source['source_raw_sha256'] == block['source_raw_sha256']
                assert text[block['character_start']:block['character_end']].encode() == source_raw
            metadata = read(packet / 'metadata.json')
            assert metadata['work_key'] == packet.name and metadata['text_sha256'] == sha(raw)
            for name in ('codebook.md', 'coding_schema.json'):
                assert (packet / name).read_bytes() == (B / name).read_bytes()
            manifest = read(packet / 'chunks.json')
            assert b''.join((packet / c['file']).read_bytes() for c in manifest['chunks']) == raw
            entries[packet.name] = hashes(packet)
    result = {'parent_only': True, 'source_identity_decision': False, 'documents': entries}
    path = OUT / 'packet_input_receipts.json'
    if path.exists():
        old = read(path)
        for doc, entry in old['documents'].items():
            assert entries[doc] == entry, 'Frozen input receipt changed: ' + doc
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'registered_packets': len(entries), 'initial_packets': 677,
                      'new_source_upgrades': len(entries) - 677}))


def hashes(packet):
    names = ['article.txt', 'metadata.json', 'coding_schema.json', 'codebook.md', 'instructions.txt', 'chunks.json']
    names += [c['file'] for c in read(packet / 'chunks.json')['chunks']]
    if (packet / 'source_blocks.json').exists():
        names.append('source_blocks.json')
    return {name: sha((packet / name).read_bytes()) for name in names}


if __name__ == '__main__':
    freeze()
