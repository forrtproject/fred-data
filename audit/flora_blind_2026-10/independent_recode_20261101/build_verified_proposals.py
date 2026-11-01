#!/usr/bin/env python3
"""Export only parent-adjudicated cases passing independent evidence gates."""
import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from prepare_packets import B, OUT, PACKETS
from project_prior_sol import project

BASELINE = Path('/home/lukas/audit_inputs_2026-10/flora_b48a7d6.csv')
BASELINE_SHA = '6d391186dfb57263bbc6bb504e8561e0d1e25997b36417072c023812efaad9f7'


def read(path):
    return json.loads(path.read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def norm(value):
    return re.sub(r'[^\w]', '', value.casefold())


def identifier(value):
    value = value.strip().casefold()
    if value in ('', 'na', 'nan', 'null'):
        return ''
    value = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:\s*)', '', value).rstrip('/')
    match = re.fullmatch(r'(?:10\.17605/|https?://)?osf\.io/([a-z0-9]+)', value)
    return 'osf:' + match[1] if match else value


def ids(row, role):
    return {v for k in ('doi_' + role, 'alt_identifier_' + role)
            if (v := identifier(row.get(k, '')))}


def review_field_dispositions(review):
    """Read explicit field identities; conflicting aliases cannot authorize a fix."""
    entries = review.get('reviews', review.get('field_reviews'))
    assert isinstance(entries, (list, dict)), 'Missing field-specific source review'
    entries = entries.values() if isinstance(entries, dict) else entries
    result = []
    for entry in entries:
        rows = [entry[k] for k in ('row_index', 'input_row_index', 'row_id', 'row') if entry.get(k) is not None]
        fields = [entry[k] for k in ('field', 'field_reviewed') if entry.get(k) is not None]
        if entry.get('requested_fields') is not None:
            assert len(entry['requested_fields']) == 1, 'Review is not field-specific'
            fields.extend(entry['requested_fields'])
        if entry.get('field_review_id'):
            match = re.fullmatch(r'(\d+)\.([a-z_]+)', entry['field_review_id'])
            assert match, 'Invalid review field identity'
            rows.append(match[1])
            fields.append(match[2])
        assert rows and all(type(value) in (int, str) and re.fullmatch(r'(?:row:)?\d+', str(value)) for value in rows)
        rows = {int(str(value).removeprefix('row:')) for value in rows}
        assert len(rows) == 1, 'Conflicting review row identities'
        assert fields and len(set(fields)) == 1, 'Conflicting review field identities'
        statuses = {entry[k] for k in ('status', 'disposition') if entry.get(k) is not None}
        assert len(statuses) == 1, 'Conflicting or missing review dispositions'
        result.append((rows.pop(), fields[0], statuses.pop()))
    return result


def retained_target_scope_review(receipt, row_index, row, outcome):
    """Bind a resolved target objection to its raw review and parent corrections."""
    directory = Path(receipt['directory'])
    required = {'review.json', 'sources_and_proofs.json', 'reading_manifest.json', 'parent_validation.json'}
    assert set(receipt['file_hashes']) == required, 'Target scope review files incomplete'
    for name, expected in receipt['file_hashes'].items():
        assert sha((directory / name).read_bytes()) == expected, 'Target scope evidence changed: ' + name
    review, validation = read(directory / 'review.json'), read(directory / 'parent_validation.json')
    assert validation['proof_count_verified'] > 0
    assert validation['review_file_sha256'] == receipt['file_hashes']['review.json']
    fields = review['field_reviews']
    for field, status in [('original', 'retain_current'), ('type', 'retain_current'),
                          ('outcome', 'supported_correction')]:
        matches = [f for f in fields if f['field_id'] == f'{row_index}.{field}' and f['status'] == status]
        assert len(matches) == 1, 'Target scope objection remains unresolved: ' + field
        value = matches[0]['recommended_value']
        if field == 'original':
            assert identifier(value['doi_o']) in ids(row, 'o') and norm(value['title_o']) == norm(row['title_o'])
        else:
            assert value == (row['type'] if field == 'type' else outcome), 'Target scope disposition differs'


def current_alignment(row, source):
    key = identifier(source['parent_work_key'])
    if key in ids(row, 'r'):
        return
    source_url = source.get('metadata', {}).get('source_url', '')
    assert not ids(row, 'r'), 'Current DOI or alternate identifier differs'
    assert source_url and source_url == row.get('url_r'), 'Current source URL differs'
    assert key == identifier(source_url), 'Current URL work key differs'


def original_identifier_alignment(row, receipt):
    if not ids(row, 'o'):
        return
    assert receipt, 'Original identifier needs authoritative metadata verification'
    path = Path(receipt['path'])
    assert sha(path.read_bytes()) == receipt['sha256']
    metadata = read(path)['message']
    assert identifier(metadata['DOI']) in ids(row, 'o'), 'Registered original identifier differs'
    assert norm(metadata['title'][0]) == norm(row['title_o']), 'Original identifier resolves to a different title'


def original_doi_alignment(row, target, transcription_receipt=None):
    literal = identifier(target.get('doi', ''))
    if not literal or literal in ids(row, 'o'):
        return
    assert transcription_receipt, 'Original DOI differs; verified transcription evidence required'
    canonical = identifier(transcription_receipt['canonical_doi'])
    assert canonical in ids(row, 'o') and literal == identifier(transcription_receipt['literal_extracted_doi'])
    without_issn_hyphen = re.sub(r'(\(sici\)\d{4})-(\d{4}\()', r'\1\2', canonical, count=1)
    assert without_issn_hyphen != canonical and literal == without_issn_hyphen, \
        'Only the SICI ISSN line-break hyphen may differ'
    receipt = transcription_receipt['publisher_reference_metadata']
    path = Path(receipt['path'])
    assert sha(path.read_bytes()) == receipt['sha256']
    metadata = read(path)['message']
    assert identifier(metadata['DOI']) in ids(row, 'r'), 'Publisher reference belongs to a different current work'
    refs = [ref for ref in metadata.get('reference', [])
            if ref.get('key') == transcription_receipt['publisher_reference_key']
            and ref.get('doi-asserted-by') == 'publisher' and identifier(ref.get('DOI', '')) == canonical]
    assert len(refs) == 1, 'Publisher-deposited canonical reference not established'


def original_alignment(row, target, year_receipt=None, author_receipt=None, doi_receipt=None):
    assert norm(row['title_o']) == norm(target['title']), 'Original title is not positively aligned'
    if row['year_o'] != target['year']:
        assert year_receipt, 'Original year/version needs separate adjudication'
        path = Path(year_receipt['path'])
        assert sha(path.read_bytes()) == year_receipt['sha256']
        metadata = read(path)['message']
        assert identifier(metadata['DOI']) in ids(row, 'o')
        assert norm(metadata['title'][0]) == norm(target['title'])
        assert row['year_o'] == str(metadata['published-online']['date-parts'][0][0])
        if metadata.get('published-print'):
            assert target['year'] == str(metadata['published-print']['date-parts'][0][0])
            assert metadata['volume'] == row['volume_o'] and metadata['issue'] == row['issue_o']
            assert norm(metadata['page']) == norm(row['pages_o'])
        else:
            ref = year_receipt.get('publisher_print_metadata_receipt')
            assert ref, 'Print date absent; publisher issue evidence required'
            path = Path(ref['path'])
            assert sha(path.read_bytes()) == ref['sha256']
            printed = read(path)
            publisher = urlparse(metadata['resource']['primary']['URL']).hostname
            assert publisher and urlparse(printed['source_url']).hostname == publisher, 'Print evidence is not from the registered publisher'
            source_path = Path(printed['source_path'])
            assert sha(source_path.read_bytes()) == printed['source_sha256']
            quote = printed['quote']
            assert quote and len(quote) <= 2000 and quote in source_path.read_text()
            assert identifier(printed['doi']) in ids(row, 'o') and printed['doi'] in quote
            assert norm(printed['title']) == norm(target['title']) and norm(printed['title']) in norm(quote)
            assert str(printed['year']) == target['year']
            context = norm(quote)
            volume = context.find(norm('Volume ' + printed['volume']))
            issue = context.find(norm('Issue ' + printed['issue']), volume)
            pages = context.find(norm('Pages ' + printed['page']), issue)
            assert 0 <= volume < issue < pages and target['year'] in context[issue:pages], 'Publisher issue citation differs'
            for key, field in [('volume', 'volume_o'), ('issue', 'issue_o'), ('page', 'pages_o')]:
                assert norm(str(metadata.get(key) or 'NA')) == norm(row[field]), 'Frozen advance-publication metadata differs'
    authors = json.loads(row['author_o'])
    complete_author_match = authors and all(a.get('family') and norm(a['family']) in norm(target['authors'])
                                            for a in authors)
    if not complete_author_match:
        assert author_receipt, 'Original authors differ or citation is abbreviated'
        metadata_path = Path(author_receipt['path'])
        assert sha(metadata_path.read_bytes()) == author_receipt['sha256']
        metadata = read(metadata_path)['message']
        assert identifier(metadata['DOI']) in ids(row, 'o'), 'Author metadata DOI differs'
        assert norm(metadata['title'][0]) == norm(target['title']), 'Author metadata title differs'
        registered = metadata['author']
        assert len(authors) == len(registered), 'Registered author count differs'
        for frozen, actual in zip(authors, registered, strict=True):
            if frozen.get('family'):
                assert norm(frozen['family']) == norm(actual.get('family', '')), 'Registered author differs'
                assert norm(frozen.get('given', '')) == norm(actual.get('given', '')), 'Registered author given name differs'
            else:
                assert set(frozen) <= {'sequence'} and actual.get('name'), 'Unnamed author is not a verified group'
        printed = author_receipt['source_printed_authors']
        assert norm(target['authors']) == norm(printed), 'Abbreviated citation differs from its source receipt'
        count = author_receipt['source_printed_person_count']
        named = [a for a in registered if a.get('family')]
        assert 1 <= count <= len(named)
        if count == 1:
            assert (target.get('doi') and identifier(target['doi']) in ids(row, 'o')
                    and re.search(r'\bet\s*\.?\s*al\b', printed, re.I)), \
                'Single-author abbreviation requires a printed matching DOI and et al.'
            initials = ''.join(word[0] for word in re.findall(r'[^\W\d_]+', named[0].get('given', '')))
            assert initials and norm(named[0]['family'] + initials) in norm(printed), \
                'Abbreviated first-author initials differ'
        positions = [norm(printed).find(norm(a['family'])) for a in named[:count]]
        assert all(i >= 0 for i in positions) and positions == sorted(positions), 'Citation is not the registered author prefix'
    original_doi_alignment(row, target, doi_receipt)


def proof(packet, quote):
    raw = (packet / 'article.txt').read_bytes()
    text = raw.decode()
    assert quote and quote in text
    start = text.index(quote)
    end = start + len(quote)
    return dict(quote=quote, source_path=str(packet / 'article.txt'), source_sha256=sha(raw),
                character_start=start, character_end=end, utf8_start=len(text[:start].encode()),
                utf8_end=len(text[:end].encode()), quote_sha256=sha(quote.encode()))


def completed_field_work(opus, sol):
    assert opus.get('study_status') == sol.get('study_status') == 'completed', \
        'Plans and unfinished studies need a record-level remedy before field approval'


def checked_replacements(row, result, target, decision):
    replacements = decision['replacement_fields'].copy()
    fields = set(decision['proposal_fields'])
    axes = ('outcome_computation', 'outcome_robustness')
    if fields and fields <= set(axes):
        assert row['type'] == result['record_type'] == 'reproduction', 'Axis fix requires a reproduction record'
        assert set(replacements) == {'outcome'}, 'Axis fix must replace the complete CSV outcome'
        before = row['outcome'].split(', ')
        assert len(before) == 2, 'Ambiguous compound outcome'
        after = [target[k] for k in axes]
        assert all(after), 'Both reproduction axes must be established'
        after = [('computation not checked' if i == 0 else 'robustness not checked')
                 if value == 'not checked' else value for i, value in enumerate(after)]
        for i, key in enumerate(axes):
            if key not in fields:
                assert after[i] == before[i], 'Unreviewed dependent reproduction axis changed'
        assert replacements['outcome'] == ', '.join(after), 'Replacement differs from independently coded axes'
        return replacements
    assert set(replacements) == fields <= {'type', 'outcome'}, 'Unvalidated field replacement'
    if 'type' in replacements:
        assert replacements['type'] == result['record_type']
    else:
        assert row['type'] == result['record_type'], 'Record type requires a joint remedy'
    if 'outcome' in replacements:
        expected = (target['outcome'] if result['record_type'] == 'replication' else
                    ', '.join(target[k] for k in ('outcome_computation', 'outcome_robustness') if target.get(k)))
        assert replacements['outcome'] == expected, 'Replacement differs from independently coded value'
    return replacements


def original_replacements(metadata):
    """Replace the complete original bibliography; never retain another paper's fields."""
    authors = [{k: a[k] for k in ('given', 'family', 'sequence', 'ORCID') if k in a}
               for a in metadata['author']]
    assert authors and all(a.get('family') for a in authors)
    date = metadata.get('published-print') or metadata.get('published-online') or metadata['published']
    year = str(date['date-parts'][0][0])
    title, journal = metadata['title'][0].rstrip('.'), metadata['container-title'][0]
    doi = metadata['DOI']
    volume, issue, pages = (str(metadata.get(k, 'NA')) for k in ('volume', 'issue', 'page'))
    def initials(given):
        return ' '.join(x[0] + '.' for x in re.findall(r'[^\W\d_]+', given))
    names = [a['family'] + (', ' + initials(a['given']) if a.get('given') else '') for a in authors]
    author_text = names[0] if len(names) == 1 else ', '.join(names[:-1]) + ', & ' + names[-1]
    location = volume + ('(' + issue + ')' if issue != 'NA' else '')
    if pages != 'NA':
        location += ', ' + pages.replace('-', '–')
    apa = f'{author_text} ({year}). {title}. {journal}, {location}. https://doi.org/{doi}'
    bib_authors = ' and '.join(a['family'] + (', ' + a['given'] if a.get('given') else '') for a in authors)
    fields = {'title': title, 'author': bib_authors, 'journal': journal, 'year': year, 'doi': doi}
    fields.update({k: v for k, v in [('volume', volume), ('number', issue), ('pages', pages)] if v != 'NA'})
    bibtex = '@article{original_' + re.sub(r'\W', '', doi) + ',\n' + ',\n'.join(
        '  ' + k + ' = {' + v + '}' for k, v in fields.items()) + '\n}\n'
    return dict(doi_o=doi, alt_identifier_o='NA', doi_o_hash=hashlib.md5(doi.encode()).hexdigest()[:3],
                title_o=title, author_o=json.dumps(authors, ensure_ascii=False, separators=(',', ':')),
                journal_o=journal, year_o=year, volume_o=volume, issue_o=issue, pages_o=pages,
                apa_ref_o=apa, bibtex_ref_o=bibtex, url_o='https://doi.org/' + doi,
                language_o=metadata.get('language', 'NA'), oa_url_o='NA')


def build():
    assert sha(BASELINE.read_bytes()) == BASELINE_SHA, 'Frozen baseline changed'
    with BASELINE.open(encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    proposals = read(B / 'handoff/correction_proposals.json')['changes']
    holds = read(B / 'handoff/review_reliability.json').get('holds', {})
    inventory = read(OUT / 'source_inventory.json')
    prior_checks = read(OUT / 'prior_sol_receipt_checks.json')['documents']
    decisions = read(OUT / 'parent_acceptance_decisions.json')['cases']
    result = []
    for decision in decisions:
        row_index, doc = decision['input_row_index'], decision['document_id']
        row, packet = rows[row_index], PACKETS / doc
        assert decision['disposition'] == 'accepted_for_automatic_proposal'
        assert decision['positive_claim_alignment_parent_verified'] is True
        assert decision['counterevidence_parent_adjudicated'] is True
        assert decision['dependent_fields_parent_verified'] is True
        if decision.get('target_scope_review'):
            retained_target_scope_review(decision['target_scope_review'], row_index, row,
                                        decision['replacement_fields']['outcome'])
        assert 'row:' + str(row_index) not in holds, 'Live scientific hold'
        source = next((d for d in inventory['documents'] if d['document_id'] == doc), None)
        if source is None:
            source = next(d for d in read(OUT / 'source_upgrades.json')['upgrades'] if d['document_id'] == doc)
        assert not source.get('status', '').startswith('withheld'), 'Primary source view is withheld'
        current_alignment(row, source)
        opus_dir = Path(decision['opus_output'])
        opus = read(opus_dir / 'coding.json')
        opus_valid = read(opus_dir / 'parent_validation.json')
        assert opus_valid['output_hashes']['coding.json'] == sha((opus_dir / 'coding.json').read_bytes()), 'Opus coding changed after validation'
        assert opus['evidence_level'] == 'full_text', 'Abstracts cannot establish this set'
        assert opus_valid['full_model_visible_reading_receipts_verified'] is True
        assert opus_valid['frozen_packet_inputs_verified'] is True
        if decision['sol_kind'] == 'prior':
            check = prior_checks[doc]
            assert check['status'].startswith('exact_source_complete_tool_receipt_verified')
            assert sha(Path(check['prior_coding_path']).read_bytes()) == check['prior_coding_sha256']
            sol, transcription = project(packet, read(Path(check['prior_coding_path'])))
            assert transcription['scientific_labels_modified'] is False
            sol_path = check['prior_coding_path']
        else:
            sol_dir = Path(decision['sol_output'])
            sol, sol_valid = read(sol_dir / 'coding.json'), read(sol_dir / 'parent_validation.json')
            assert sol_valid['output_hashes']['coding.json'] == sha((sol_dir / 'coding.json').read_bytes()), 'Sol coding changed after validation'
            assert sol_valid['full_model_visible_reading_receipts_verified'] is True
            assert sol_valid['frozen_packet_inputs_verified'] is True
            sol_path = str(sol_dir / 'coding.json')
        assert opus['text_sha256'] == sol['text_sha256'] == sha((packet / 'article.txt').read_bytes())
        completed_field_work(opus, sol)
        oi, si = decision['opus_target_index'], decision['sol_target_index']
        ot, st = opus['targets'][oi], sol['targets'][si]
        if decision['proposal_fields'] == ['original']:
            receipt = decision['replacement_original_metadata_receipt']
            metadata_path = Path(receipt['path'])
            assert sha(metadata_path.read_bytes()) == receipt['sha256']
            identity_fields = original_replacements(read(metadata_path)['message'])
            aligned_row = dict(row, **identity_fields)
        else:
            identity_fields, aligned_row = None, row
        original_alignment(aligned_row, ot, decision.get('original_year_metadata_receipt'),
                           decision.get('original_author_metadata_receipt'),
                           decision.get('original_doi_transcription_receipt'))
        original_alignment(aligned_row, st, decision.get('original_year_metadata_receipt'),
                           decision.get('original_author_metadata_receipt'),
                           decision.get('original_doi_transcription_receipt'))
        identifier_receipt = next((decision[k] for k in (
            'replacement_original_metadata_receipt', 'original_identifier_metadata_receipt',
            'original_year_metadata_receipt', 'original_author_metadata_receipt') if decision.get(k)), None)
        original_identifier_alignment(aligned_row, identifier_receipt)
        assert ot['outcome_confident'] is True and st['outcome_confident'] is True
        for key, expected in decision['agreed_target_values'].items():
            assert ot[key] == st[key] == expected, 'Independent target labels disagree: ' + key
        assert opus['record_type'] == sol['record_type'] == decision['agreed_record_type']
        reviewer = Path(decision['review_dir'])
        review, validation = read(reviewer / 'review.json'), read(reviewer / 'parent_validation.json')
        for name, expected in decision['accepted_review_file_hashes'].items():
            assert sha((reviewer / name).read_bytes()) == expected, 'Reviewed evidence changed: ' + name
        assert validation['proof_count_verified'] > 0
        for field in decision['proposal_fields']:
            expected = (row_index, decision.get('review_field_names', {}).get(field, field), 'supported_correction')
            matches = [entry for entry in review_field_dispositions(review) if entry == expected]
            assert len(matches) == 1, 'Missing independent adversarial support'
            prop = next(p for p in proposals if int(p['input_row_index']) == row_index and p['field'] == field)
            assert prop['expected_before_full_record_sha256'] == digest(row)
            assert not prop.get('application_hold'), 'Unresolved proposal dependency'
        duplicate_rows = [i for i, other in enumerate(rows) if i != row_index
                          and (ids(other, 'r') & ids(row, 'r') or norm(other['title_r']) == norm(row['title_r']))
                          and (ids(other, 'o') & ids(aligned_row, 'o')
                               or norm(other['title_o']) == norm(aligned_row['title_o']))]
        assert not duplicate_rows, 'Existing pair duplicate requires a joint remedy: ' + str(duplicate_rows)
        if identity_fields is not None:
            assert row['type'] == opus['record_type']
            assert row['outcome'] == ot['outcome'] == st['outcome'], 'Identity remedy needs compatible dependent outcome'
            replacements = identity_fields
        else:
            replacements = checked_replacements(row, opus, ot, decision)
        quote = ot[decision['replacement_quote_field']]
        replacements['outcome_quote'] = quote
        replacements['outcome_quote_source'] = decision['replacement_quote_section']
        assert set(replacements).issubset(row), 'Unknown CSV columns'
        evidence = [proof(packet, quote)]
        for key in decision['supporting_quote_fields']:
            evidence.append(proof(packet, opus[key] if key == 'record_type_quote' else ot[key]))
        for quote in decision.get('supporting_literal_quotes', []):
            evidence.append(proof(packet, quote))
        if decision.get('original_author_metadata_receipt'):
            evidence.append(proof(packet, decision['original_author_metadata_receipt']['source_printed_authors']))
        operations = [dict(operation='set_field', field=field, expected_before={field: row[field]},
                           proposed_value=value, input_row_index=row_index,
                           expected_before_full_record_sha256=digest(row), atomic_group='row:' + str(row_index))
                      for field, value in replacements.items() if value != row[field]]
        result.append(dict(case_id='row:' + str(row_index), input_row_index=row_index,
                           status='ready_for_batch_approval', proposal_fields=decision['proposal_fields'],
                           independently_verified_study_status='completed',
                           expected_before_full_record_sha256=digest(row), expected_before=row,
                           replacements=replacements, operations=operations,
                           apply_all_fields_atomically=True, original_pair_duplicate_rows=duplicate_rows,
                           evidence=evidence, rationale=decision['rationale'], limits=decision['limits'],
                           independent_inputs=dict(opus=str(opus_dir / 'coding.json'), sol=sol_path,
                                                   reviewer=str(reviewer / 'review.json'),
                                                   target_scope_review=decision.get('target_scope_review')),
                           bibliography_metadata=decision.get('replacement_original_metadata_receipt'),
                           original_author_metadata_alignment=decision.get('original_author_metadata_receipt'),
                           original_year_metadata_alignment=decision.get('original_year_metadata_receipt'),
                           original_doi_transcription_alignment=decision.get('original_doi_transcription_receipt'),
                           original_identifier_metadata_alignment=identifier_receipt))
    output = dict(schema_version=1, status='incremental_verified_proposals_cohort_in_progress',
                  baseline_sha256=BASELINE_SHA, canonical_changes_applied=False, user_approval_recorded=False,
                  automatic_fields_verified=sum(len(c['proposal_fields']) for c in result),
                  case_count=len(result), cases=result,
                  implementation_rules=['Obtain batch approval before implementation; this file records verified proposals, not approvals.',
                                        'Plans and unfinished studies require record-level actions; they cannot enter this field-only set.',
                                        'Verify the frozen file and complete row hash; apply all fields of each case atomically.',
                                        'Keep prior decisions and source histories. Apply original-identity changes with their complete bibliography, identifiers and source evidence.',
                                        'Do not re-enable other outcome proposals from this incremental file.'])
    (OUT / 'automatically_verified_proposals.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: output[k] for k in ('case_count', 'automatic_fields_verified', 'canonical_changes_applied')}))
    return output


if __name__ == '__main__':
    build()
