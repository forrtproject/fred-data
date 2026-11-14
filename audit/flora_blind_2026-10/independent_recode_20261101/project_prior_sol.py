#!/usr/bin/env python3
"""Preserve old blind labels; document whitespace-only quotation transcription."""
import copy
import hashlib
import json
import re

from prepare_packets import BAD, strict_result


def literal_whitespace_span(text, quote):
    """Only whitespace may differ. Reject missing/changed words or ambiguity."""
    if quote in text:
        a = text.index(quote)
        return a, a + len(quote)
    tokens = list(re.finditer(r'\S+', text))
    normalized, starts, ends = [], [], []
    for index, token in enumerate(tokens):
        if index:
            normalized.append(' ')
            starts.append(tokens[index - 1].end())
            ends.append(token.start())
        normalized.extend(token.group())
        starts.extend(range(token.start(), token.end()))
        ends.extend(range(token.start() + 1, token.end() + 1))
    haystack, needle = ''.join(normalized), ' '.join(quote.split())
    a = haystack.find(needle)
    if not needle or a < 0 or haystack.find(needle, a + 1) >= 0:
        raise ValueError('No unique whitespace-only literal source match')
    start, end = starts[a], ends[a + len(needle) - 1]
    if ' '.join(text[start:end].split()) != needle:
        raise ValueError('Whitespace transcription changed content')
    return start, end


def project(packet, original):
    """Return a derived copy and explicit changes; never edit the original coding."""
    raw = (packet / 'article.txt').read_bytes()
    source_hash = hashlib.sha256(raw).hexdigest()
    if original.get('text_sha256') != source_hash:
        raise ValueError('Prior coding uses another source')
    result = copy.deepcopy(original)
    excluded = {k: result.pop(k) for k in ('elapsed_seconds', 'acquisition_seconds', 'skip_reason') if k in result}
    if 'parent_provenance_completion' in result:
        provenance = result['parent_provenance_completion']
        if (not isinstance(provenance, dict)
                or not set(provenance.get('filled_fields', [])).issubset({'source_url', 'retrieved_at', 'parser'})
                or not set(provenance.get('original_values', {})).issubset({'source_url', 'retrieved_at', 'parser'})
                or not set(provenance).issubset({'filled_fields', 'original_values', 'source_url_basis',
                                               'retrieved_at_basis', 'cache_parser'})):
            raise ValueError('Unrecognized parent provenance; do not discard scientific changes')
        excluded['parent_provenance_completion'] = result.pop('parent_provenance_completion')
    old_work_key = result['work_key']
    result['work_key'] = packet.name
    metadata = json.loads((packet / 'metadata.json').read_text())
    parser = result.get('parser')
    if (metadata.get('parser') is None and isinstance(parser, str)
            and (BAD.search(parser) or re.search(r'blind|audit|parent|coding|verdict|target', parser, re.I))):
        excluded['opaque_packet_parser_redaction'] = {
            'original_value': parser, 'packet_value': None,
            'reason': 'Same metadata redaction rule used to prepare the opaque blind packet.'}
        result['parser'] = None
    text, transcriptions = raw.decode(), []

    def walk(value, path=''):
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = path + ('.' if path else '') + key
                if key.endswith('_quote') and child and child not in text:
                    start, end = literal_whitespace_span(text, child)
                    replacement = text[start:end]
                    transcriptions.append({'field': child_path, 'original_quote': child,
                                           'literal_quote': replacement, 'character_start': start,
                                           'character_end': end, 'utf8_start': len(text[:start].encode()),
                                           'utf8_end': len(text[:end].encode()), 'source_sha256': source_hash,
                                           'quote_sha256': hashlib.sha256(replacement.encode()).hexdigest(),
                                           'only_whitespace_differs': True})
                    value[key] = replacement
                else:
                    walk(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, path + '[' + str(index) + ']')

    walk(result)
    strict_result(packet, result)
    return result, {'original_work_key': old_work_key, 'opaque_document_id': packet.name,
                    'excluded_technical_metadata': excluded, 'quote_transcriptions': transcriptions,
                    'scientific_labels_modified': False,
                    'note': 'A derived transcription for exact literal validation. Original blind coding remains unchanged. This does not establish reading completeness, target alignment, or scientific correctness.'}
