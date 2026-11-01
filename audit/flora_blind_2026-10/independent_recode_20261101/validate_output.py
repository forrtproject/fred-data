#!/usr/bin/env python3
"""Parent-only mechanical checks. Passing never accepts a scientific correction."""
import argparse
import hashlib
import json
from pathlib import Path

from prepare_packets import reading_coverage, strict_result


def read(path):
    return json.loads(Path(path).read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check(condition, message):
    if not condition:
        raise ValueError(message)


def first(obj, names):
    for name in names:
        if name in obj:
            return obj[name]
    raise ValueError('Missing proof key: ' + '/'.join(names))


def validate_proofs(obj, raw, source_hash):
    text = raw.decode('utf-8')
    proofs = []

    def walk(value, path='$'):
        if isinstance(value, dict):
            if any(k in value for k in ('character_start', 'char_start', 'unicode_start')):
                quote = first(value, ('quote', 'text'))
                a = first(value, ('character_start', 'char_start', 'unicode_start'))
                z = first(value, ('character_end', 'char_end', 'unicode_end'))
                ba = first(value, ('utf8_start', 'utf8_byte_start', 'byte_start'))
                bz = first(value, ('utf8_end', 'utf8_byte_end', 'byte_end'))
                check(all(type(x) is int for x in (a, z, ba, bz)), path + ': noninteger offsets')
                check(isinstance(quote, str) and bool(quote), path + ': empty proof')
                check(0 <= a < z <= len(text) and text[a:z] == quote, path + ': character mismatch')
                check(ba == len(text[:a].encode()) and bz == len(text[:z].encode()), path + ': UTF8 mismatch')
                check(raw[ba:bz] == quote.encode(), path + ': raw byte mismatch')
                proof_source = next((value[k] for k in ('source_text_sha256', 'source_sha256', 'text_sha256')
                                     if k in value), source_hash)
                check(proof_source == source_hash,
                      path + ': source hash mismatch')
                if 'quote_sha256' in value:
                    check(value['quote_sha256'] == sha(quote.encode()), path + ': quote hash mismatch')
                proofs.append({'path': path, 'field': value.get('field_path', value.get('field')),
                               'quote': quote, 'character_start': a, 'character_end': z})
            for key, child in value.items():
                walk(child, path + '.' + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, path + '[' + str(index) + ']')

    walk(obj)
    check(bool(proofs), 'No source proofs')
    return proofs


def coding_quotes(value, path=''):
    result = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = path + ('.' if path else '') + key
            if key.endswith('_quote') and child:
                result.append((child_path, child))
            result.extend(coding_quotes(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.extend(coding_quotes(child, path + '[' + str(index) + ']'))
    return result


def contains_exact_chunk(item, packet, chunk_path, chunk_raw):
    if item.get('textTruncated', True):
        return False
    body = item.get('text', '')
    if item.get('type') == 'dynamic_tool':
        # Native Read's durable record includes raw file content, without line
        # decoration. Verify actual returned content, not just input path/length.
        try:
            call = json.loads(body)
            output = call['output']['file']
            return (call['toolName'] == 'Read'
                    and Path(call['input']['file_path']).resolve() == chunk_path.resolve()
                    and Path(output['filePath']).resolve() == chunk_path.resolve()
                    and output['startLine'] == 1
                    and output['numLines'] == output['totalLines']
                    and output['content'].encode() == chunk_raw)
        except (KeyError, TypeError, ValueError):
            return False
    if item.get('type') == 'command_execution':
        command, _, displayed = body.partition('\n')
        return (packet.name in command and chunk_path.relative_to(packet).as_posix() in command
                and (displayed == chunk_raw.decode()
                     or (chunk_raw.decode() in displayed and '=====END' in displayed))
                and 'Output truncated' not in body)
    return False


def field_key(path):
    if not isinstance(path, str):
        return path
    if path.startswith('/'):
        parts = [p.replace('~1', '/').replace('~0', '~') for p in path[1:].split('/')]
        return ''.join('[' + p + ']' if p.isdigit() else ('.' if i else '') + p
                       for i, p in enumerate(parts))
    return path.removeprefix('$.')


def validate(packet, output, receipts):
    packet, output, receipts = map(Path, (packet, output, receipts))
    result = read(output / 'coding.json')
    literal = strict_result(packet, result)
    manifest = read(output / 'reading_manifest.json')
    reading_coverage(packet, manifest)
    raw = (packet / 'article.txt').read_bytes()
    source_hash = sha(raw)
    maps = {}
    for filename in ('quote_spans.json', 'evidence_map.json'):
        data = read(output / filename)
        check(first(data, ('text_sha256', 'source_sha256')) == source_hash, filename + ': source mismatch')
        maps[filename] = validate_proofs(data, raw, source_hash)
    proof_quotes = {(field_key(x['field']), x['quote']) for x in maps['quote_spans.json']}
    for field, quote in coding_quotes(result):
        check((field, quote) in proof_quotes,
              'Coding quote absent from field-specific span map: ' + field)
    # Actual durable tool outputs, recovered by the parent, must contain every exact
    # source chunk. A coder's own assertion or hash list cannot satisfy this check.
    tool_items = [(p, read(p)) for p in receipts.glob('item_*.json')]
    check(bool(tool_items), 'No recovered tool receipts')
    chunks = read(packet / 'chunks.json')['chunks']
    evidence = []
    for chunk in chunks:
        chunk_path = packet / chunk['file']
        chunk_raw = chunk_path.read_bytes()
        check(sha(chunk_raw) == chunk['sha256'], 'Chunk changed')
        matches = [(p, item) for p, item in tool_items
                   if contains_exact_chunk(item, packet, chunk_path, chunk_raw)]
        check(bool(matches), 'Missing exact untruncated tool output for ' + chunk['file'])
        p, item = matches[0]
        evidence.append({'chunk': chunk['file'], 'range': [chunk['character_start'], chunk['character_end']],
                         'chunk_sha256': chunk['sha256'], 'threadId': item['threadId'],
                         'itemId': item['itemId'], 'position': item['position'],
                         'receipt_path': str(p), 'receipt_sha256': sha(p.read_bytes())})
    return {'status': 'mechanically_validated_pending_scientific_comparison', 'document_id': packet.name,
            'source_sha256': source_hash, 'unicode_characters': len(raw.decode()),
            'coding_quote_fields': len(literal), 'span_map_proofs': len(maps['quote_spans.json']),
            'evidence_map_proofs': len(maps['evidence_map.json']),
            'full_model_visible_reading_receipts_verified': True, 'reading_receipts': evidence,
            'output_hashes': {p.name: sha(p.read_bytes()) for p in output.glob('*.json')
                              if p.name != 'parent_validation.json'},
            'automatic_scientific_acceptance': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('receipts', type=Path)
    args = parser.parse_args()
    validated = validate(args.packet, args.output, args.receipts)
    (args.output / 'parent_validation.json').write_text(json.dumps(validated, indent=2) + '\n')
    print(json.dumps({k: v for k, v in validated.items() if k not in ('reading_receipts', 'output_hashes')}, indent=2))
