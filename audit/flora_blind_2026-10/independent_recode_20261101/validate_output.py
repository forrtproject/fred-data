#!/usr/bin/env python3
"""Parent-only mechanical checks. Passing never accepts a scientific correction."""
import argparse
import hashlib
import json
import re
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


def validate_proofs(obj, raw, source_hash, require_source_hash=False, unproved_entries=None):
    text = raw.decode('utf-8')
    proofs = []

    def walk(value, path='$'):
        if isinstance(value, dict):
            if any(k in value for k in ('character_start', 'char_start', 'unicode_start')):
                quote_names = ('quote', 'text', 'literal_quote', 'literal_proof')
                quote = first(value, quote_names)
                if 'literal_proof' in value:
                    check(all(value[name] == value['literal_proof'] for name in quote_names if name in value),
                          path + ': conflicting literal quote aliases')
                a = first(value, ('character_start', 'char_start', 'unicode_start'))
                z = first(value, ('character_end', 'char_end', 'unicode_end'))
                ba = first(value, ('utf8_start', 'utf8_byte_start', 'byte_start'))
                bz = first(value, ('utf8_end', 'utf8_byte_end', 'byte_end'))
                if quote == '' and all(x is None for x in (a, z, ba, bz)):
                    check(unproved_entries is not None, path + ': missing quotation is not a proof')
                    check(first(value, ('quote_sha256', 'sha256')) is None,
                          path + ': empty quotation claims a hash')
                    check(first(value, ('source_text_sha256', 'source_sha256', 'text_sha256')) == source_hash,
                          path + ': unproved entry source mismatch')
                    unproved_entries.append({'path': path, 'claim': value.get('work', value.get('claim')),
                                            'reason': value.get('reason'),
                                            'status': 'unproved_not_accepted_as_exclusion_or_evidence'})
                    return
                check(all(type(x) is int for x in (a, z, ba, bz)), path + ': noninteger offsets')
                check(isinstance(quote, str) and bool(quote), path + ': empty proof')
                check(0 <= a < z <= len(text) and text[a:z] == quote, path + ': character mismatch')
                check(ba == len(text[:a].encode()) and bz == len(text[:z].encode()), path + ': UTF8 mismatch')
                check(raw[ba:bz] == quote.encode(), path + ': raw byte mismatch')
                if require_source_hash:
                    check(any(k in value for k in ('source_text_sha256', 'source_sha256', 'text_sha256')),
                          path + ': missing proof source hash')
                proof_source = next((value[k] for k in ('source_text_sha256', 'source_sha256', 'text_sha256')
                                     if k in value), source_hash)
                check(proof_source == source_hash,
                      path + ': source hash mismatch')
                check(first(value, ('quote_sha256', 'sha256')) == sha(quote.encode()),
                      path + ': quote hash mismatch')
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


def command_chunk_trim_loss(command, displayed, text, filename):
    """Only terminal-boundary trivia may disappear; source words stay exact."""
    if text in displayed:
        return (0, 0)
    core = text.lstrip('\ufeff \t\r\n\f\v')
    leading = len(text) - len(core)
    cat = re.search(r'\bcat\s+[^;\n]*' + re.escape(filename), command)
    if cat and core and core in displayed:
        return (leading, 0)
    terminal_cat = re.search(r'\bcat\s+[^;\n]*' + re.escape(filename) + r"['\"]?\s*$", command)
    if terminal_cat:
        if text.rstrip() and displayed.rstrip().endswith(text.rstrip()):
            return (0, len(text) - len(text.rstrip()))
        if core.rstrip() and displayed.rstrip().endswith(core.rstrip()):
            return (leading, len(text) - len(text.rstrip()))
    return None


def command_chunk_utf8_wrap_loss(command, displayed, text, filename):
    """Recognize the declared cat | fold -w 2000 rendering of one long line."""
    if '\n' in text or len(text.encode()) <= 2000:
        return None
    if not re.search(r'\bcat\s+[^;|\n]*' + re.escape(filename)
                     + r"['\"]?\s*\|\s*fold\s+-w\s+2000\s*$", command):
        return None
    raw = text.encode()
    try:
        lines = [raw[start:start + 2000].decode() for start in range(0, len(raw), 2000)]
    except UnicodeDecodeError:
        return None
    rendered = '\n'.join(lines)
    if displayed == rendered:
        return (0, len(lines) - 1)
    if displayed == rendered.rstrip() and rendered.rstrip():
        return (len(rendered) - len(rendered.rstrip()), len(lines) - 1)
    return None


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
        if packet.name not in command or chunk_path.relative_to(packet).as_posix() not in command:
            return False
        if 'Output truncated' in body:
            return False
        return (command_chunk_trim_loss(command, displayed, chunk_raw.decode(), chunk_path.name) is not None
                or command_chunk_utf8_wrap_loss(command, displayed, chunk_raw.decode(), chunk_path.name) is not None)
    return False


def field_key(path):
    if not isinstance(path, str):
        return path
    if path.startswith('/'):
        parts = [p.replace('~1', '/').replace('~0', '~') for p in path[1:].split('/')]
        return ''.join('[' + p + ']' if p.isdigit() else ('.' if i else '') + p
                       for i, p in enumerate(parts))
    return path.removeprefix('$.')


def validate(packet, output, receipts, expected_inputs=None):
    packet, output, receipts = map(Path, (packet, output, receipts))
    if expected_inputs is None:
        registry = read(Path(__file__).with_name('packet_input_receipts.json'))
        check(packet.name in registry['documents'], 'Packet absent from parent input registry')
        expected_inputs = registry['documents'][packet.name]
    for name, expected_hash in expected_inputs.items():
        check(sha((packet / name).read_bytes()) == expected_hash, 'Frozen packet input changed: ' + name)
    check(('source_blocks.json' in expected_inputs) == (packet / 'source_blocks.json').exists(),
          'Unregistered source-block map')
    result = read(output / 'coding.json')
    literal = strict_result(packet, result)
    manifest = read(output / 'reading_manifest.json')
    reading_coverage(packet, manifest)
    raw = (packet / 'article.txt').read_bytes()
    source_hash = sha(raw)
    maps = {}
    unproved_entries = []
    for filename in ('quote_spans.json', 'evidence_map.json'):
        data = read(output / filename)
        root_hash = next((data[k] for k in ('text_sha256', 'source_sha256') if k in data), None)
        if root_hash is not None:
            check(root_hash == source_hash, filename + ': source mismatch')
        maps[filename] = validate_proofs(data, raw, source_hash, require_source_hash=root_hash is None,
                                        unproved_entries=unproved_entries if filename == 'evidence_map.json' else None)
    if (packet / 'source_blocks.json').exists():
        block_map = read(packet / 'source_blocks.json')
        check(block_map['text_sha256'] == source_hash, 'Source-block map hash mismatch')
        text = raw.decode()
        for block in block_map['blocks']:
            part = text[block['character_start']:block['character_end']].encode()
            check(sha(part) == block['source_raw_sha256'], 'Original source block changed')
        for proofs in maps.values():
            for proof in proofs:
                check(any(block['character_start'] <= proof['character_start']
                          < proof['character_end'] <= block['character_end'] for block in block_map['blocks']),
                      'Quotation crosses source boundary or includes an inserted heading')
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
        leading, trailing = (0, 0)
        inserted_breaks = 0
        if item.get('type') == 'command_execution':
            command, _, displayed = item['text'].partition('\n')
            trim = command_chunk_trim_loss(command, displayed, chunk_raw.decode(), chunk_path.name)
            if trim is not None:
                leading, trailing = trim
            else:
                trailing, inserted_breaks = command_chunk_utf8_wrap_loss(
                    command, displayed, chunk_raw.decode(), chunk_path.name)
        evidence.append({'chunk': chunk['file'], 'range': [chunk['character_start'], chunk['character_end']],
                         'chunk_sha256': chunk['sha256'], 'threadId': item['threadId'],
                         'itemId': item['itemId'], 'position': item['position'],
                         'receipt_path': str(p), 'receipt_sha256': sha(p.read_bytes()),
                         'leading_whitespace_or_bom_not_preserved_by_timeline': leading,
                         'trailing_whitespace_not_preserved_by_timeline': trailing,
                         'line_breaks_inserted_by_declared_fold': inserted_breaks})
    return {'status': 'mechanically_validated_pending_scientific_comparison', 'document_id': packet.name,
            'source_sha256': source_hash, 'unicode_characters': len(raw.decode()),
            'coding_quote_fields': len(literal), 'span_map_proofs': len(maps['quote_spans.json']),
            'evidence_map_proofs': len(maps['evidence_map.json']),
            'unproved_evidence_entries': unproved_entries,
            'full_model_visible_reading_receipts_verified': True, 'reading_receipts': evidence,
            'frozen_packet_inputs_verified': True,
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
