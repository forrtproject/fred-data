#!/usr/bin/env python3
"""Export only parent-adjudicated cases passing independent evidence gates."""
import csv
import hashlib
import html
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


def metadata_title(metadata):
    """Crossref may deposit a subtitle separately from the title."""
    titles, subtitles = metadata['title'], metadata.get('subtitle', [])
    assert isinstance(titles, list) and len(titles) == 1 and isinstance(titles[0], str) and titles[0]
    assert isinstance(subtitles, list) and len(subtitles) <= 1
    title = html.unescape(re.sub(r'</?(?:i|b|em|strong|sub|sup)>', '', titles[0], flags=re.I))
    if subtitles:
        subtitle = subtitles[0]
        assert isinstance(subtitle, str) and subtitle.strip(), 'Invalid deposited subtitle'
        if not norm(title).endswith(norm(subtitle)):
            title = title.rstrip(' .:') + ': ' + subtitle
    return title


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
    case_table = 'reviews' not in review and 'field_reviews' not in review and 'cases' in review
    entries = review.get('reviews', review.get('field_reviews', review.get('cases')))
    if 'assigned_fields' in review:
        assert entries is None, 'Conflicting source review field tables'
        entries = review['assigned_fields']
    if entries is None and review.get('disposition') == 'replace_current_with_proposed':
        value = review.get('recommended_value')
        assert isinstance(value, str) and value, 'Missing replacement value'
        assert review.get('field') == 'outcome', 'Replacement disposition is not an outcome review'
        assert review.get('status') == 'propose_change_to_' + value, 'Conflicting replacement status'
        assert all(review.get(key) == value for key in ('proposed_value', 'adjudicated_value', 'value')), \
            'Conflicting replacement values'
        assert review.get('current_value') != value, 'Replacement does not change the current value'
        assert review.get('outcome_confident') is True and review.get('policy_boundary_needed') is False, \
            'Replacement disposition is uncertain'
        entries = [dict(review, status='supported_correction', disposition='supported_correction')]
    assert isinstance(entries, (list, dict)), 'Missing field-specific source review'
    entries = entries.values() if isinstance(entries, dict) else entries
    if case_table:
        expanded = []
        for entry in entries:
            if 'status' not in entry and isinstance(entry.get('field_reviews'), dict):
                match = re.fullmatch(r'(\d+)\.([a-z_]+)', entry.get('case_id', ''))
                assert match and entry.get('record_id') == match[1] and entry.get('focus') == match[2], \
                    'Conflicting nested case identity'
                for field, detail in entry['field_reviews'].items():
                    assert re.fullmatch(r'[a-z_]+', field) and isinstance(detail, dict)
                    assert not set(detail) & {'row', 'row_id', 'row_index', 'input_row_index', 'field',
                                              'case_id', 'field_review_id'}, 'Nested field overrides case identity'
                    expanded.append(dict(detail, case_id=match[1] + '.' + field,
                                         input_row_index=int(match[1]), field=field))
            else:
                expanded.append(entry)
        entries = expanded
    result = []
    for entry in entries:
        rows = [entry[k] for k in ('row_index', 'input_row_index', 'row_id', 'row') if entry.get(k) is not None]
        fields = [entry[k] for k in ('field', 'field_reviewed') if entry.get(k) is not None]
        if entry.get('requested_fields') is not None:
            assert len(entry['requested_fields']) == 1, 'Review is not field-specific'
            fields.extend(entry['requested_fields'])
        for identity in (('field_review_id', 'case_id') if case_table else ('field_review_id',)):
            if not entry.get(identity):
                continue
            match = re.fullmatch(r'(\d+)\.([a-z_]+)', entry[identity])
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


def review_row_binding(review, row_index, rows, receipt=None, review_sha256=None,
                       snapshot_receipt=None):
    """Wrong embedded row snapshots require a separately hashed correction."""
    snapshots = review.get('baseline_snapshot', {})
    csv_reference = review.get('frozen_csv')
    external_name = csv_reference.get('baseline_snapshot') if isinstance(csv_reference, dict) else None
    if external_name is not None:
        assert not snapshots, 'Conflicting embedded and external review snapshots'
        assert isinstance(external_name, str) and Path(external_name).name == external_name, \
            'External snapshot must be a named file'
        assert snapshot_receipt, 'External review snapshot needs a bound receipt'
        path = Path(snapshot_receipt['path'])
        assert path.name == external_name, 'External snapshot filename differs'
        assert sha(path.read_bytes()) == snapshot_receipt['sha256'], 'External snapshot changed'
        assert review_sha256 and snapshot_receipt['review_file_sha256'] == review_sha256, \
            'External snapshot receipt belongs to another review'
        external = read(path)
        assert external['frozen_csv_sha256'] == BASELINE_SHA and external['rows_total'] == len(rows), \
            'External snapshot belongs to another baseline'
        snapshots = external['rows']
        assert isinstance(snapshots, dict) and str(row_index) in snapshots, 'External snapshot omits the reviewed row'
    if 'input_row_index_zero_based' in snapshots:
        assert snapshots['input_row_index_zero_based'] == row_index
        literal = {field['field']: field['value'] for field in snapshots['fields']}
        assert len(literal) == len(snapshots['fields']) and set(literal) == set(rows[row_index]), \
            'Review snapshot does not cover the complete frozen row'
        for field in snapshots['fields']:
            assert field['row'] == field['input_row_index_zero_based'] == row_index
            value = field['value'].replace('\r\n', '\n').replace('\r', '\n')
            assert value == rows[row_index][field['field']], 'Review baseline field differs'
            assert field['value_sha256'] == sha(field['value'].encode()), 'Review baseline value hash differs'
        assert snapshots['row_sha256'] == digest(literal), 'Review snapshot hash differs'
        if literal != rows[row_index]:
            assert "newline=''" in snapshots.get('reader', ''), 'Undeclared CSV newline representation'
    if str(row_index) in snapshots:
        snapshot = snapshots[str(row_index)]
        assert snapshot['input_row_index_zero_based'] == row_index
        assert snapshot['row'] == rows[row_index], 'Review snapshot belongs to another frozen row'
        assert snapshot['row_sha256_sorted_json'] == sha(json.dumps(
            rows[row_index], ensure_ascii=False, sort_keys=True).encode()), 'Review snapshot hash differs'
    cases = review.get('cases', {})
    cases = cases.values() if isinstance(cases, dict) else cases
    for case in cases:
        if case.get('input_row_index') != row_index:
            continue
        baseline = case.get('frozen_csv_baseline', {})
        for key, value in baseline.items():
            if key in rows[row_index]:
                assert value == rows[row_index][key], 'Review baseline identifier or value differs'
        if 'value' in baseline and case.get('field') in rows[row_index]:
            assert baseline['value'] == rows[row_index][case['field']], 'Review baseline value differs'
        if 'frozen_row_state' not in case:
            continue
        snapshot = case['frozen_row_state']
        normalized = {('doi_o' if key == '\ufeff"doi_o"' else key): value
                      for key, value in snapshot.items()}
        if normalized == rows[row_index]:
            continue
        assert receipt, 'Review snapshot belongs to another frozen row'
        path = Path(receipt['path'])
        assert sha(path.read_bytes()) == receipt['sha256'], 'Row-binding correction changed'
        correction = read(path)
        assert correction['review_file_sha256'] == review_sha256, 'Row correction names another review'
        assert correction['baseline_sha256'] == BASELINE_SHA
        binding = correction['case_bindings'][case['case_id']]
        assert binding['input_row_index'] == row_index
        assert binding['correct_frozen_full_record_sha256'] == digest(rows[row_index])
        assert binding['review_snapshot_sha256'] == digest(snapshot)
        assert row_index > 0 and normalized == rows[row_index - 1], 'Not the verified one-based indexing error'
        assert binding['incorrect_snapshot_row_index'] == row_index - 1
        assert binding['correction_kind'] == 'one_based_index_used_for_zero_based_row'


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


def current_alignment(row, source, file_receipt=None):
    key = identifier(source['parent_work_key'])
    if key in ids(row, 'r'):
        return
    source_url = source.get('metadata', {}).get('source_url', '')
    assert not ids(row, 'r'), 'Current DOI or alternate identifier differs'
    if source_url != row.get('url_r'):
        assert file_receipt, 'Current source URL differs'
        path = Path(file_receipt['path'])
        assert sha(path.read_bytes()) == file_receipt['sha256'], 'Current file metadata changed'
        file = read(path)['data']
        guid = file['attributes']['guid']
        assert re.fullmatch(r'[a-z0-9]{5}', guid) and file['id'] == guid and file['type'] == 'files'
        assert file['attributes']['kind'] == 'file'
        assert file['links']['self'] == 'https://api.osf.io/v2/files/' + guid + '/'
        assert file['links']['iri'] == row.get('url_r') == 'https://osf.io/' + guid, \
            'Current file metadata names another source'
        assert source_url == file['links']['download'] == 'https://osf.io/download/' + guid + '/', \
            'Current download is not the registered file'
        assert key == identifier(file['links']['iri']), 'Current file work key differs'
        return
    assert key == identifier(source_url), 'Current URL work key differs'


def original_identifier_alignment(row, receipt):
    if not ids(row, 'o'):
        return
    assert receipt, 'Original identifier needs authoritative metadata verification'
    path = Path(receipt['path'])
    assert sha(path.read_bytes()) == receipt['sha256']
    metadata = read(path)['message']
    assert identifier(metadata['DOI']) in ids(row, 'o'), 'Registered original identifier differs'
    assert norm(metadata_title(metadata)) == norm(row['title_o']), 'Original identifier resolves to a different title'


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
        assert norm(metadata_title(metadata)) == norm(target['title'])
        if year_receipt.get('kind') == 'conflicting_deposited_date_fields_same_work':
            assert year_receipt['scope'] == 'identity_only_preserve_frozen_year'
            online = metadata['published-online']['date-parts'][0][0]
            printed = metadata['published-print']['date-parts'][0][0]
            assert printed < online and row['year_o'] == str(printed) and target['year'] == str(online), \
                'Declared date conflict does not match deposited years'
            assert identifier(target['doi']) in ids(row, 'o'), 'Date conflict needs a printed matching DOI'
            for key, field in [('volume', 'volume_o'), ('issue', 'issue_o'), ('page', 'pages_o')]:
                assert norm(metadata[key]) == norm(row[field]), 'Date conflict citation differs'
            reference = year_receipt['literal_reference']
            source = Path(reference['source_path'])
            assert sha(source.read_bytes()) == reference['source_sha256'], 'Date conflict source changed'
            quote = reference['quote']
            assert quote and quote in source.read_text(), 'Date conflict reference is not literal'
            assert sha(quote.encode()) == reference['quote_sha256'], 'Date conflict quote changed'
            assert norm(target['title']) in norm(quote) and target['doi'].casefold() in quote.casefold(), \
                'Date conflict reference identifies another work'
            citation = f"{target['year']};{metadata['volume']}({metadata['issue']}):{metadata['page']}"
            assert norm(citation) in norm(quote), 'Date conflict printed year or issue differs'
        elif metadata.get('published-print'):
            assert row['year_o'] == str(metadata['published-online']['date-parts'][0][0])
            assert target['year'] == str(metadata['published-print']['date-parts'][0][0])
            assert metadata['volume'] == row['volume_o'] and metadata['issue'] == row['issue_o']
            assert norm(metadata['page']) == norm(row['pages_o'])
        else:
            assert row['year_o'] == str(metadata['published-online']['date-parts'][0][0])
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
        assert norm(metadata_title(metadata)) == norm(target['title']), 'Author metadata title differs'
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
        families = [a['family'] for a in named[:count]]
        transcription = author_receipt.get('source_author_transcription')
        if transcription:
            assert count == len(named), 'Author transcription requires the complete printed author list'
            assert set(transcription) == {'author_index', 'canonical_family', 'printed_family', 'kind'}
            index = transcription['author_index']
            assert type(index) is int and 0 <= index < count
            canonical, literal = transcription['canonical_family'], transcription['printed_family']
            assert canonical == families[index] and transcription['kind'] == 'missing_final_character'
            assert len(literal) >= 5 and literal == canonical[:-1], 'Unverified author transcription'
            families[index] = literal
        positions = [norm(printed).find(norm(family)) for family in families]
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


def original_alias_replacements(row, metadata, receipt):
    """Canonicalize one registered DOI alias without replacing the same work's bibliography."""
    path = Path(receipt['path'])
    assert sha(path.read_bytes()) == receipt['sha256'], 'DOI alias receipt changed'
    handle = read(path)
    canonical = metadata['DOI']
    assert handle['responseCode'] == 1 and handle['handle'] == row['doi_o'], 'DOI alias names another identifier'
    aliases = [entry['data']['value'] for entry in handle['values'] if entry['type'] == 'HS_ALIAS']
    assert aliases == [canonical] and identifier(canonical) != identifier(row['doi_o']), \
        'Registered DOI alias does not name the canonical identifier'
    assert norm(metadata_title(metadata)) == norm(row['title_o']), 'DOI alias title differs'
    for key, column in [('volume', 'volume_o'), ('issue', 'issue_o'), ('page', 'pages_o')]:
        assert str(metadata[key]) == row[column], 'DOI alias bibliography differs'
    assert norm(metadata['container-title'][0]) == norm(row['journal_o'])
    date = metadata.get('published-print') or metadata.get('published-online') or metadata['issued']
    assert str(date['date-parts'][0][0]) == row['year_o'], 'DOI alias year differs'
    frozen_authors = json.loads(row['author_o'])
    assert [(norm(a.get('given', '')), norm(a['family'])) for a in frozen_authors] == [
        (norm(a.get('given', '')), norm(a['family'])) for a in metadata['author']], 'DOI alias authors differ'
    assert all(canonical.casefold() in row[column].casefold() for column in ('apa_ref_o', 'bibtex_ref_o')), \
        'Existing bibliography does not establish canonical DOI'
    assert row['doi_o_hash'] == hashlib.md5(row['doi_o'].encode()).hexdigest()[:3], 'Frozen DOI hash differs'
    return dict(doi_o=canonical, doi_o_hash=hashlib.md5(canonical.encode()).hexdigest()[:3])


def original_replacements(metadata):
    """Replace the complete original bibliography; never retain another paper's fields."""
    authors = [{k: a[k] for k in ('given', 'family', 'sequence', 'ORCID') if k in a}
               for a in metadata['author']]
    assert authors and all(a.get('family') for a in authors)
    date = metadata.get('published-print') or metadata.get('published-online') or metadata['published']
    year = str(date['date-parts'][0][0])
    title, journal = metadata_title(metadata).rstrip('.'), metadata['container-title'][0]
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


def record_removal(row, row_index, opus, sol, decision, evidence):
    completed_field_work(opus, sol)
    assert opus['record_type'] == sol['record_type'] == 'not_a_replication'
    assert opus['targets'] == sol['targets'] == []
    assert decision['positive_record_scope_parent_verified'] is True, 'Omitted targets alone do not authorize removal'
    assert decision['action'] == 'exclude_nonreplication_record'
    assert decision['isolated_field_application_allowed'] is False, 'Whole-record remedy required'
    assert len(evidence) >= 2, 'Positive record-scope evidence required'
    return dict(case_id='row:' + str(row_index), input_row_index=row_index,
                status='ready_for_batch_approval', action=decision['action'],
                expected_before_full_record_sha256=digest(row), expected_before=row,
                proposed_record_type='not_a_replication', original_pair_applicable=False,
                outcome_applicable=False, isolated_field_application_allowed=False,
                operations=[dict(operation='remove_row', input_row_index=row_index,
                    expected_before_full_record_sha256=digest(row), archive_before=row)],
                evidence=evidence, rationale=decision['rationale'], limits=decision['limits'],
                canonical_changes_applied=False, user_approval_recorded=False)


def build():
    assert sha(BASELINE.read_bytes()) == BASELINE_SHA, 'Frozen baseline changed'
    with BASELINE.open(encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    proposals = read(B / 'handoff/correction_proposals.json')['changes']
    holds = read(B / 'handoff/review_reliability.json').get('holds', {})
    inventory = read(OUT / 'source_inventory.json')
    prior_checks = read(OUT / 'prior_sol_receipt_checks.json')['documents']
    acceptance = read(OUT / 'parent_acceptance_decisions.json')
    decisions = acceptance['cases']
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
        current_alignment(row, source, decision.get('current_report_metadata_receipt'))
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
            metadata = read(metadata_path)['message']
            if decision.get('original_remedy_kind') == 'canonical_doi_alias':
                identity_fields = original_alias_replacements(row, metadata, decision['original_doi_alias_receipt'])
            else:
                assert decision.get('original_remedy_kind') is None, 'Unknown original remedy'
                identity_fields = original_replacements(metadata)
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
        review_row_binding(review, row_index, rows, decision.get('review_row_binding_correction'),
                           sha((reviewer / 'review.json').read_bytes()),
                           decision.get('review_external_snapshot_receipt'))
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
        if decision.get('review_row_binding_correction'):
            result[-1]['review_row_binding_correction'] = decision['review_row_binding_correction']
        if decision.get('review_external_snapshot_receipt'):
            result[-1]['review_external_snapshot_receipt'] = decision['review_external_snapshot_receipt']
        if decision.get('original_doi_alias_receipt'):
            result[-1]['original_doi_alias_alignment'] = decision['original_doi_alias_receipt']
        if decision.get('current_report_metadata_receipt'):
            result[-1]['current_report_metadata_alignment'] = decision['current_report_metadata_receipt']
    record_actions = []
    for decision in acceptance.get('record_cases', []):
        row_index, doc = decision['input_row_index'], decision['document_id']
        row, packet = rows[row_index], PACKETS / doc
        assert decision['disposition'] == 'accepted_for_automatic_record_proposal'
        assert 'row:' + str(row_index) not in holds, 'Live scientific hold'
        source = next(d for d in inventory['documents'] if d['document_id'] == doc)
        current_alignment(row, source)
        opus_dir = Path(decision['opus_output'])
        opus, ov = read(opus_dir / 'coding.json'), read(opus_dir / 'parent_validation.json')
        assert ov['output_hashes']['coding.json'] == sha((opus_dir / 'coding.json').read_bytes())
        assert ov['full_model_visible_reading_receipts_verified'] and ov['frozen_packet_inputs_verified']
        assert decision['sol_kind'] == 'prior', 'Record proposal needs a certified comparison'
        prior = prior_checks[doc]
        assert prior['status'].startswith('exact_source_complete_tool_receipt_verified')
        assert sha(Path(prior['prior_coding_path']).read_bytes()) == prior['prior_coding_sha256']
        sol, _ = project(packet, read(Path(prior['prior_coding_path'])))
        assert opus['evidence_level'] == sol['evidence_level'] == 'full_text'
        assert opus['text_sha256'] == sol['text_sha256'] == sha((packet / 'article.txt').read_bytes())
        reviewer = Path(decision['review_dir'])
        for name, expected in decision['accepted_review_file_hashes'].items():
            assert sha((reviewer / name).read_bytes()) == expected
        review, validation = read(reviewer / 'review.json'), read(reviewer / 'parent_validation.json')
        assert validation['proof_count_verified'] > 0
        assert (row_index, 'type', 'supported_correction') in review_field_dispositions(review)
        review_row_binding(review, row_index, rows, decision.get('review_row_binding_correction'),
                           sha((reviewer / 'review.json').read_bytes()),
                           decision.get('review_external_snapshot_receipt'))
        prop = next(p for p in proposals if int(p['input_row_index']) == row_index and p['field'] == 'type')
        assert prop['expected_before_full_record_sha256'] == digest(row)
        dependency = prop['record_action_dependency']
        assert dependency['operation'] == decision['action'] and dependency['isolated_field_application_allowed'] is False
        evidence = [proof(packet, quote) for quote in decision['supporting_literal_quotes']]
        action = record_removal(row, row_index, opus, sol, decision, evidence)
        action['resolved_field_only_hold'] = prop.get('application_hold')
        action['independent_inputs'] = dict(opus=str(opus_dir / 'coding.json'),
            sol=prior['prior_coding_path'], reviewer=str(reviewer / 'review.json'))
        action['review_row_binding_correction'] = decision.get('review_row_binding_correction')
        record_actions.append(action)
    output = dict(schema_version=1, status='incremental_verified_proposals_cohort_in_progress',
                  baseline_sha256=BASELINE_SHA, canonical_changes_applied=False, user_approval_recorded=False,
                  automatic_fields_verified=sum(len(c['proposal_fields']) for c in result),
                  case_count=len(result), cases=result,
                  record_action_count=len(record_actions), record_actions=record_actions,
                  implementation_rules=['Obtain batch approval before implementation; this file records verified proposals, not approvals.',
                                        'Plans and unfinished studies require record-level actions; they cannot enter this field-only set.',
                                        'Verify the frozen file and complete row hash; apply all fields of each case atomically.',
                                        'Keep prior decisions and source histories. Apply original-identity changes with their complete bibliography, identifiers and source evidence.',
                                        'Record exclusions remove the complete pair and archive its frozen record; never apply only their type field.',
                                        'Preflight every frozen record before mutation; use stable record hashes when exclusions change row positions.',
                                        'Do not re-enable other outcome proposals from this incremental file.'])
    (OUT / 'automatically_verified_proposals.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: output[k] for k in ('case_count', 'automatic_fields_verified', 'record_action_count', 'canonical_changes_applied')}))
    return output


if __name__ == '__main__':
    build()
