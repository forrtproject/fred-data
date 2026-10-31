#!/usr/bin/env python3
"""Build an explicit, public-safe asset set for the FLoRA review app."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

B = Path(__file__).resolve().parents[1]
H = B / 'handoff'
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
assert not any(out.iterdir()), 'Use an empty staging directory.'

json_files = ['review_queue.json', 'audit_overview.json', 'correction_proposals.json',
              'evidence_provenance_fixes.json', 'review_required.json',
              'sol_review_decisions.json', 'missing_pair_review_decisions.json']
csv_files = ['audit_rows.csv', 'confirmed_missing_pairs.csv', 'unresolved_missing_pairs.csv']
drop_keys = {'source_path', 'source_read_manifest', 'relevant_context_reads', 'parent_gate',
             'prior_review_artifact', 'prior_full_source_Sol_review_artifact',
             'prior_full_source_Sol_review_read_manifest', 'primary_metadata_receipt',
             'input_sha256'}
private_path = re.compile(r'(?:/home/lukas/|audit/flora_blind_2026-10/(?:evidence_followup/)?private/)[^\s<>"\']+')
token = re.compile(r'(?:view_only|access_token|api_key)=[A-Za-z0-9_-]{8,}')

def clean_text(text):
    return private_path.sub('[private audit artifact]', text)

def excerpt(text):
    words = list(re.finditer(r'\S+', text))
    return text[:words[24].end()] if len(words) > 25 else text

def public(value, in_before=False):
    if isinstance(value, list):
        return [public(x, in_before) for x in value]
    if isinstance(value, str):
        if in_before:
            return value
        # CSV evidence columns hold JSON, which needs the same filtering.
        if value.startswith(('{', '[')):
            try:
                return json.dumps(public(json.loads(value), in_before), ensure_ascii=False)
            except json.JSONDecodeError:
                pass
        return clean_text(value)
    if not isinstance(value, dict):
        return value
    result = {}
    for key, item in value.items():
        if key in drop_keys:
            continue
        if key == 'expected_before' and isinstance(item, dict):
            omitted = [k for k, text in item.items() if isinstance(text, str) and
                       (private_path.search(text) or token.search(text))]
            result[key] = {k: text for k, text in item.items() if k not in omitted}
            if omitted:
                result['publication_omitted_private_fields'] = omitted
            continue
        before = in_before or key == 'expected_before'
        if isinstance(item, str) and (key == 'quote' or key.endswith('_quote')) and not before:
            short = excerpt(item)
            if private_path.search(short):
                short = ''
            result[key] = short
            if short != item:
                result['quote_is_excerpt'] = True
                result['complete_quote_sha256'] = hashlib.sha256(item.encode()).hexdigest()
                if key == 'quote' and 'character_start' in value:
                    result['complete_proof_span'] = {k: value[k] for k in
                        ['character_start', 'character_end', 'utf8_byte_start', 'utf8_byte_end']}
            continue
        result[key] = public(item, before)
    if result.get('quote_is_excerpt') and 'quote' in result and 'character_start' in result:
        result['character_end'] = result['character_start'] + len(result['quote'])
        result['utf8_byte_end'] = result['utf8_byte_start'] + len(result['quote'].encode())
    return result

published = {}
for name in json_files:
    value = public(json.loads((H / name).read_text()))
    published[name] = value
    (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
for name in csv_files:
    with (H / name).open(encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = [public(row) for row in reader]
    with (out / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, columns, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

cases = published['review_queue.json']
assert len(cases) == 980
display = json.loads(json.dumps(cases))
for case in display:
    for evidence in case['evidence'].values():
        for key in ['reason', 'quote']:
            if isinstance(evidence.get(key), str) and len(evidence[key]) > 260:
                evidence[key] = evidence[key][:260] + ' [Load the published evidence record for more.]'
html = (H / 'review.html').read_text()
start_marker, end_marker = '/*flora-cases-start*/', '/*flora-cases-end*/'
start = html.index(start_marker) + len(start_marker)
end = html.index(end_marker, start)
html = html[:start] + json.dumps(display, ensure_ascii=False).replace('<', '\\u003c') + html[end:]
old_hash = hashlib.sha256((H / 'review_queue.json').read_bytes()).hexdigest()
new_hash = hashlib.sha256((out / 'review_queue.json').read_bytes()).hexdigest()
assert old_hash in html
html = html.replace(old_hash, new_hash)
html = html.replace('Complete evidence loaded and hash verified.', 'Published evidence loaded and hash verified.')
html = html.replace('Explore field decisions, supporting evidence, and correction proposals.',
                    'Explore field decisions, supporting evidence excerpts, and correction proposals.')
html = html.replace('<p><a href="correction_proposals.json">',
                    '<p><a href="https://github.com/forrtproject/fred-data/blob/audit/flora-blind-2026-10/audit/flora_blind_2026-10/REPORT.md">Full audit report</a> · <a href="correction_proposals.json">')
assert 'Source-approved subset' not in html and 'approved_fixes.json' not in html
(out / 'index.html').write_text(html)

files = []
for path in sorted(out.iterdir()):
    assert path.is_file() and not path.is_symlink() and not path.name.startswith('.')
    raw = path.read_bytes()
    text = raw.decode('utf-8-sig')
    assert not token.search(text), path.name
    assert not private_path.search(text), path.name
    assert '100.121.34.85' not in text and '.t3/worktrees/' not in text, path.name
    assert len(raw) < 25 * 1024 * 1024, path.name
    if path.name != 'index.html':
        files.append(dict(path=path.name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
manifest = dict(status='public_asset_set_checked', files=files,
                private_source_files_included=False, private_paths_included=False,
                source_quotes_are_excerpts=True, automatic_dataset_changes=False,
                html_integrity='The deployment helper verifies the final HTML, including its report identity marker.')
(out / 'publication_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(dict(output=str(out), files=len(list(out.iterdir())),
                     correction_proposals=len(published['correction_proposals.json']['changes']),
                     review_cases=len(cases), status=manifest['status']), indent=2))
