#!/usr/bin/env python3
"""Parent-only FLoRA comparison. Never import this into a blind coding child.

CLI: python3 audit/flora_blind_2026-10/scripts/compare.py [--audit-dir DIR]
Adjudications: <file_key>.json with {"decisions": [{"input_row_index": 0,
"field": "type|original|outcome|outcome_computation|outcome_robustness",
"method": "obvious|argon", "verdict": "shipped_right|blind_right|both_wrong|undeterminable",
"corrected_value": ..., "quote": "...", "location": "...", "reason": "..."}]}.
An original decision may specify target_index to resolve a flagged pairing.
An original correction may use {"action": "remove_row"} when the source proves
the entry has no tested original; this releases any proposed pair without
inventing a replacement citation or grading an inapplicable outcome.
Missing targets use target_index and field='missing_row', with the same evidence.
Only a validated decision can establish an error. REPORT.md remains provisional.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
from functools import lru_cache
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path('/home/lukas/audit_inputs_2026-10/flora_b48a7d6.csv')
REPLICATION = {'successful', 'failed', 'mixed', 'descriptive only',
               'statistically successful but flawed', 'uninformative', 'cannot_be_determined'}
COMPUTATION = {'computationally reproducible': 'computationally reproducible',
               'computational issues': 'computational issues', 'technical failure': 'technical failure',
               'computation not checked': 'not checked', 'not checked': 'not checked',
               'cannot_be_determined': 'cannot_be_determined'}
ROBUSTNESS = {'robust': 'robust', 'robustness challenges': 'robustness challenges',
              'robustness not checked': 'not checked', 'not checked': 'not checked',
              'cannot_be_determined': 'cannot_be_determined'}
UNKNOWN = {'', 'unverified', 'unclear', 'cannot_be_determined'}
FIELDS = ('type', 'original', 'outcome', 'outcome_computation', 'outcome_robustness')


def clean_doi(value):
    value = str(value or '').strip().lower()
    if value == 'na':
        return ''
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value).strip()


def surnames(value):
    """Parse the frozen Crossref JSON author list; never split JSON as prose."""
    if not value or value == 'NA':
        return []
    try:
        authors = json.loads(value) if isinstance(value, str) else value
    except (ValueError, TypeError):
        return []
    if not isinstance(authors, list):
        return []
    return [str(a.get('family') or a.get('literal') or '').strip()
            for a in authors if isinstance(a, dict) and (a.get('family') or a.get('literal'))]


def adapt_row(row):
    result = dict(row)
    result['authors_o'] = '; '.join(surnames(row.get('author_o', '')))
    result['outcome_phrase'] = row.get('outcome_quote', '')
    if row.get('type') == 'reproduction':
        parts = str(row.get('outcome', '')).split(',')
        result['outcome_computation'] = COMPUTATION.get(parts[0].strip(), 'unverified') if len(parts) == 2 else 'unverified'
        result['outcome_robustness'] = ROBUSTNESS.get(parts[1].strip(), 'unverified') if len(parts) == 2 else 'unverified'
    elif row.get('outcome') not in REPLICATION:
        result['outcome'] = 'unverified'
    return result


def tokens(value):
    value = unicodedata.normalize('NFKC', str(value or '')).casefold()
    value = re.sub(r'-\s*\n\s*', '', value)
    return re.findall(r'[^\W_]+', value, re.UNICODE)


def surname(value):
    # Codebook citations are surname first; preserve multipart family names.
    first = re.split(r';| and | & |,? et al', str(value or ''), maxsplit=1)[0].strip()
    first = first.split(',')[0].strip()
    first = re.sub(r'\s+[A-Z](?:[.\s-]*[A-Z])*\.?$', '', first)
    return ''.join(tokens(first))


def year(value):
    match = re.search(r'(?:18|19|20)\d\d', str(value or ''))
    return match.group() if match else ''


def original_grade(row, target):
    a, b = set(tokens(row.get('title_o'))), set(tokens(target.get('title')))
    sim = max(len(a & b) / max(len(a | b), 1), len(a & b) / max(min(len(a), len(b)), 1))
    author = surname(row.get('authors_o', ''))
    same_author = bool(author) and author == surname(target.get('authors', ''))
    y = year(row.get('year_o'))
    same_year = bool(y) and y == year(target.get('year'))
    doi = clean_doi(row.get('doi_o'))
    if doi and doi == clean_doi(target.get('doi')):
        return 'doi', sim
    if sim >= .6 and (same_author or same_year):
        return 'title', sim
    if same_author and same_year and (sim >= .3 or not b):
        return 'author_year', sim
    if sim >= .6:
        return 'title_only', sim
    if sim >= .3 and (same_author or same_year):
        return 'partial', sim
    return 'different', sim


def pair_originals(rows, targets):
    """Return proposed one-to-one pairs plus review flags per row and target.

    Unique exact DOI pairs are fixed first. Remaining supported edges maximise
    cardinality, then total strength with scipy's Hungarian assignment. Competing
    candidates remain visible and require adjudication even if an optimum exists.
    """
    from scipy.optimize import linear_sum_assignment
    pairs, row_flags, target_flags = [], collections.defaultdict(set), collections.defaultdict(set)
    remaining_r, remaining_t = set(range(len(rows))), set(range(len(targets)))

    def flag(i, j, reason):
        row_flags[i].add(reason)
        target_flags[j].add(reason)

    exact = [(i, j) for i, r in enumerate(rows) for j, t in enumerate(targets)
             if clean_doi(r.get('doi_o')) and clean_doi(r.get('doi_o')) == clean_doi(t.get('doi'))]
    for i, j in exact:
        if sum(a == i for a, b in exact) == 1 and sum(b == j for a, b in exact) == 1:
            pairs.append((i, j, 'doi', original_grade(rows[i], targets[j])[1]))
            remaining_r.remove(i)
            remaining_t.remove(j)
        else:
            flag(i, j, 'competing_exact_doi')
    candidates = {}
    for i in remaining_r:
        for j in remaining_t:
            grade, sim = original_grade(rows[i], targets[j])
            r, t = rows[i], targets[j]
            same_ay = (surname(r.get('authors_o')) and surname(r.get('authors_o')) == surname(t.get('authors'))
                       and year(r.get('year_o')) and year(r.get('year_o')) == year(t.get('year')))
            if same_ay and grade != 'doi':
                siblings = (sum(surname(x.get('authors_o')) == surname(r.get('authors_o')) and year(x.get('year_o')) == year(r.get('year_o')) for x in rows) > 1
                            or sum(surname(x.get('authors')) == surname(t.get('authors')) and year(x.get('year')) == year(t.get('year')) for x in targets) > 1)
                if siblings or (tokens(t.get('title')) and sim < .3):
                    flag(i, j, 'same_author_year_siblings')
            if grade not in {'doi', 'title', 'author_year'}:
                continue
            candidates[i, j] = (grade, sim)
            a, b = clean_doi(r.get('doi_o')), clean_doi(t.get('doi'))
            if a and b and a != b:
                flag(i, j, 'conflicting_dois')
    for i, j in candidates:
        if sum(a == i for a, b in candidates) > 1 or sum(b == j for a, b in candidates) > 1:
            flag(i, j, 'competing_supported_matches')
    ir, jt = sorted(remaining_r), sorted(remaining_t)
    if ir and jt:
        # A cardinality bonus exceeding ALL possible strength differences.
        bonus = (min(len(ir), len(jt)) + 1) * 5
        scores = [[-bonus for _ in jt] + [0] * len(ir) for _ in ir]
        for a, i in enumerate(ir):
            for b, j in enumerate(jt):
                if (i, j) in candidates:
                    grade, sim = candidates[i, j]
                    scores[a][b] = bonus + {'doi': 4, 'title': 2, 'author_year': 1}[grade] + sim
        aa, bb = linear_sum_assignment(scores, maximize=True)
        for a, b in zip(aa, bb):
            if b < len(jt) and (ir[a], jt[b]) in candidates:
                pairs.append((ir[a], jt[b], *candidates[ir[a], jt[b]]))
    return sorted(pairs), row_flags, target_flags


@lru_cache(maxsize=32)
def normalized_quote_text(value, dehyphenate=True):
    # Reuse document normalization across hundreds of target/field checks.
    value = unicodedata.normalize('NFKC', value).casefold()
    if dehyphenate:
        value = re.sub(r'(?<=\w)-\s*\n\s*(?=\w)', '', value)
    return re.sub(r'\s+', ' ', value).strip()


def quote_present(quote, text):
    """The whole quotation must occur contiguously, allowing Unicode/spacing fixes.

    Unlike the pilot's bag-of-shingles heuristic, this never accepts fragments
    scattered throughout a document. No semantic validation is claimed here.
    """
    if not isinstance(quote, str) or not quote.strip() or not text:
        return False
    # Preserve a literal whitespace-normalized view too: a copied PDF quote may
    # retain its line-end hyphen while changing the line break to a space.
    # Dehyphenating only the source must not erase that exact literal match.
    modes = (False, True)
    sources = [normalized_quote_text(text, mode) for mode in modes]
    return any(normalized_quote_text(quote, mode) and
               normalized_quote_text(quote, mode) in source
               for mode, source in zip(modes, sources))


def outcome_grade(row, target, axis=None):
    if axis:
        a, b = row.get(axis, ''), target.get(axis, '')
    elif row.get('type') == 'reproduction':
        grades = [outcome_grade(row, target, k) for k in ('outcome_computation', 'outcome_robustness')]
        return 'unverified' if 'unverified' in grades else ('exact' if all(g == 'exact' for g in grades) else 'different')
    else:
        a, b = row.get('outcome', ''), target.get('outcome', '')
    allowed = set(COMPUTATION.values()) if axis == 'outcome_computation' else set(ROBUSTNESS.values()) if axis == 'outcome_robustness' else REPLICATION
    if a not in allowed or b not in allowed or a in UNKNOWN or b in UNKNOWN:
        return 'unverified'
    if a == b:
        return 'exact'
    return 'soft' if not axis and {a, b} == {'failed', 'mixed'} else 'different'


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8-sig')), ''
    except FileNotFoundError:
        return None, 'unattempted'
    except (OSError, ValueError) as exc:
        return None, 'malformed: ' + str(exc)


def load_coding(root, file_key, work_key, schema):
    coding, error = read_json(root / 'codings' / (file_key + '.json'))
    if error:
        return {}, error, ''
    if not isinstance(coding, dict):
        return {}, 'malformed coding: expected object', ''
    if coding.get('blind_source_warning'):
        return coding, 'blinding compromised; coding excluded', ''
    if coding.get('identity_warning'):
        return coding, 'paper identity conflict; coding excluded', ''
    if coding.get('text_scope_complete') is False:
        return coding, 'source scope incomplete; coding excluded', ''
    if coding.get('work_key') != work_key:
        return coding, 'work_key mismatch', ''
    if coding.get('status') != 'done':
        # Text acquisition coverage is independent of successful coding.
        text = ''
        try:
            raw = (root / 'texts' / (file_key + '.txt')).read_bytes()
            if coding.get('evidence_level') in ('abstract', 'full_text') and coding.get('text_sha256') == hashlib.sha256(raw).hexdigest():
                text = raw.decode('utf-8-sig', errors='replace')
        except OSError:
            pass
        return coding, str(coding.get('status') or 'malformed status'), text
    import jsonschema
    try:
        jsonschema.validate(coding, schema)
    except jsonschema.ValidationError as exc:
        return coding, 'invalid coding: ' + str(exc.validator) + ' constraint at ' + '.'.join(map(str, exc.absolute_path)), ''
    text_path = root / 'texts' / (file_key + '.txt')
    try:
        raw = text_path.read_bytes()
    except OSError:
        return coding, 'saved text missing', ''
    if coding.get('text_sha256') != hashlib.sha256(raw).hexdigest():
        return coding, 'saved text hash mismatch', ''
    if coding.get('evidence_level') not in {'abstract', 'full_text'}:
        return coding, 'missing evidence level', ''
    return coding, '', primary_text(root, file_key, work_key, raw.decode('utf-8-sig', errors='replace'))


def primary_text(root, file_key, work_key, base=None):
    """Read approved additional primary reports without changing frozen base files.

    Base blind coding/source hashes and in-flight relay inputs stay immutable.
    Additional documents have independent parent verification and fresh blinded
    coding; their exact bytes and work identity are checked before comparison.
    """
    if base is None:
        base = (root / 'texts' / (file_key + '.txt')).read_bytes().decode('utf-8-sig', errors='replace')
    registry = root / 'evidence_followup/additional_reports/approved_sources.json'
    if not registry.exists():
        return base
    value = json.loads(registry.read_text())
    parts = [base]
    seen = set()
    private = (root / 'evidence_followup/private').resolve()
    for item in value['reports']:
        if item['collection_file_key'] != file_key or item['status'] != 'approved_for_comparison':
            continue
        assert item['work_key'] == work_key, 'Additional source belongs to another work'
        assert item['report_id'] not in seen, 'Duplicate supplemental report'
        seen.add(item['report_id'])
        path = Path(item['text_path']).resolve()
        codepath = Path(item['blind_coding_path']).resolve()
        assert path.is_relative_to(private) and codepath.is_relative_to(private), 'Unapproved source location'
        raw = path.read_bytes()
        coderaw = codepath.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item['text_sha256'], 'Additional source hash changed'
        assert hashlib.sha256(coderaw).hexdigest() == item['blind_coding_sha256'], 'Fresh blind coding hash changed'
        code = json.loads(coderaw)
        assert code['work_key'] == work_key and code['status'] == 'done'
        level = item.get('evidence_level', 'full_text')
        assert level in {'abstract', 'full_text'}, 'Invalid additional evidence level'
        assert code['text_sha256'] == item['text_sha256'] and code['evidence_level'] == level
        label = 'PRIMARY REPORT' if level == 'full_text' else 'PRIMARY EVIDENCE'
        parts.append('\n\nVERIFIED ADDITIONAL ' + label + ': ' + item['report_id'] +
                     '\nSOURCE URL: ' + item['source_url'] + '\n' + raw.decode('utf-8-sig', errors='replace'))
    return ''.join(parts)


def valid_decision(decision, text):
    if not isinstance(decision, dict):
        return False
    return (decision.get('method') in {'obvious', 'argon'}
            and decision.get('verdict') in {'shipped_right', 'blind_right', 'both_wrong', 'undeterminable'}
            and bool(str(decision.get('reason') or '').strip())
            and bool(str(decision.get('location') or '').strip())
            and isinstance(decision.get('quote'), str) and len(decision['quote']) <= 6000
            and quote_present(decision.get('quote'), text)
            and (decision.get('verdict') == 'undeterminable'
                 or (decision.get('field') == 'missing_row' and decision.get('verdict') == 'shipped_right')
                 or decision.get('corrected_value') not in (None, '', {}, [])))


def load_decisions(root, file_key):
    value, error = read_json(root / 'adjudications' / (file_key + '.json'))
    if error:
        return [], error if error != 'unattempted' else ''
    if not isinstance(value, dict) or not isinstance(value.get('decisions'), list):
        return [], 'invalid adjudication envelope (expected decisions list)'
    holds_path = root / 'evidence_followup' / 'integration' / 'review_holds.json'
    if holds_path.exists():
        holds, hold_error = read_json(holds_path)
        if hold_error or not isinstance(holds, dict) or not isinstance(holds.get('holds'), list):
            raise ValueError('Malformed parent review hold file')
        pending = [h for h in holds['holds'] if h.get('file_key') == file_key and h.get('status') == 'pending']
        def held(d):
            return any(h.get('field') == d.get('field') and
                       (h.get('target_index') == d.get('target_index') if d.get('field') == 'missing_row'
                        else str(h.get('input_row_index')) == str(d.get('input_row_index')))
                       for h in pending)
        if pending:
            return [d for d in value['decisions'] if not held(d)], 'Parent source-scope recheck pending; held decisions preserved but withheld from confirmed exports.'
    return value['decisions'], ''


def decision_for(decisions, field, text, row_index=None, target_index=None):
    matches = [d for d in decisions if isinstance(d, dict) and d.get('field') == field
               and (str(d.get('input_row_index')) == str(row_index) if row_index is not None
                    else d.get('target_index') == target_index)]
    # Conflicting/duplicate decisions require parent reconciliation.
    return matches[0] if len(matches) == 1 and valid_decision(matches[0], text) else None


def verdict(decision):
    return {'shipped_right': 'correct', 'blind_right': 'error', 'both_wrong': 'error',
            'undeterminable': 'unverified'}[decision['verdict']]


def compare_work(rows, keys, coding, error, text, decisions):
    targets = coding.get('targets', []) if not error else []
    pairs, rf, tf = pair_originals(rows, targets)
    proposed = {i: (j, grade, sim) for i, j, grade, sim in pairs}
    # Explicit adjudicated identities can replace ambiguous proposals, one-to-one.
    identity_decisions = {}
    for i, key in enumerate(keys):
        d = decision_for(decisions, 'original', text, key['input_row_index']) if not error else None
        if (d and d.get('verdict') in ('blind_right', 'both_wrong')
                and d.get('corrected_value') == {'action': 'remove_row'}
                and 'target_index' not in d):
            # A methods-only citation can have no replacement original at all.
            proposed.pop(i, None)
            continue
        if d and d.get('verdict') != 'undeterminable' and 'target_index' in d:
            j = d['target_index']
            if isinstance(j, int) and not isinstance(j, bool) and 0 <= j < len(targets):
                identity_decisions[i] = (j, d)
    counts = collections.Counter(j for j, d in identity_decisions.values())
    for i, (j, d) in identity_decisions.items():
        if counts[j] == 1:
            for other, pair in list(proposed.items()):
                if other == i or pair[0] == j:
                    del proposed[other]
            grade, sim = original_grade(rows[i], targets[j])
            proposed[i] = (j, grade, sim)
    results, disagreements = [], []
    for i, (row, key) in enumerate(zip(rows, keys)):
        pair = proposed.get(i)
        j, grade, sim = pair if pair else (None, 'unmatched', '')
        target = targets[j] if j is not None else {}
        flags = sorted(rf.get(i, set()) | (tf.get(j, set()) if j is not None else set()))
        if target.get('identity_warning'):
            flags = sorted(set(flags) | {'source_original_identity_warning'})
        identity_d = decision_for(decisions, 'original', text, key['input_row_index']) if not error else None
        adjudicated_identity = (i in identity_decisions and counts[identity_decisions[i][0]] == 1)
        identity = bool(pair) and (not flags or adjudicated_identity)
        identity_value = identity_d.get('corrected_value') if identity_d else None
        identity_doi = clean_doi(identity_value.get('doi')) if isinstance(identity_value, dict) else clean_doi(identity_value)
        source_identity = bool(identity_d and identity_d.get('target_index') is None
                               and identity_d.get('verdict') == 'shipped_right'
                               and identity_doi and identity_doi == clean_doi(row.get('doi_o')))
        r = {**key, **{k: row.get(k, '') for k in ('doi_r', 'doi_o', 'type', 'source')},
             'outcome': row.get('_raw_outcome', row.get('outcome', '')),
             'coding_status': coding.get('status', 'unattempted'), 'skip_reason': error,
             'blind_type': coding.get('record_type', ''), 'study_status': coding.get('study_status', ''),
             'blind_target_index': j if j is not None else '', 'blind_doi_o': target.get('doi', ''),
             'blind_title_o': target.get('title', ''), 'blind_authors_o': target.get('authors', ''),
             'blind_year_o': target.get('year', ''),
             'blind_outcome': target.get('outcome', ''),
             'blind_outcome_computation': target.get('outcome_computation', ''),
             'blind_outcome_robustness': target.get('outcome_robustness', ''),
             'evidence_level': coding.get('evidence_level') if coding.get('evidence_level') in ('full_text', 'abstract') else 'none',
             'type_agree': '', 'original_grade': grade if not error else 'unverified',
             'title_similarity': sim, 'identity_resolved': identity or source_identity,
             'identity_resolution_method': 'pairing' if identity else 'source_adjudication' if source_identity else '',
             'pairing_flags': '; '.join(flags), 'outcome_grade': 'unverified',
             'outcome_computation_grade': 'unverified', 'outcome_robustness_grade': 'unverified',
             'confident': target.get('outcome_confident', ''), 'resolution': 'unresolved',
             'shipped_quote_present': quote_present(row.get('outcome_phrase'), text),
             'suggested_correction': '{}', 'correction_evidence': '{}'}
        for field in FIELDS:
            r[field + '_final_verdict'] = 'unverified'
            r[field + '_resolution'] = 'unresolved'
        corrections, evidence = {}, {}
        if not error:
            r['type_agree'] = (row.get('type') == coding.get('record_type')) if coding.get('record_type') != 'unclear' else ''
            valid_identity_quote = quote_present(target.get('evidence_quote'), text)
            if identity and valid_identity_quote:
                r['original_final_verdict'] = 'correct'
                r['original_resolution'] = 'agree'
            if identity and valid_identity_quote and r['type_agree'] is True and quote_present(coding.get('record_type_quote'), text):
                r['type_final_verdict'] = 'correct'
                r['type_resolution'] = 'agree'
            outcome_fields = ('outcome_computation', 'outcome_robustness') if row.get('type') == 'reproduction' else ('outcome',)
            if identity and valid_identity_quote and r['type_agree'] is True:
                for field in outcome_fields:
                    g = outcome_grade(row, target, field if field != 'outcome' else None)
                    r[field + '_grade'] = g
                    qkey = {'outcome': 'outcome_quote', 'outcome_computation': 'outcome_computational_quote',
                            'outcome_robustness': 'outcome_robustness_quote'}[field]
                    if g == 'exact' and quote_present(target.get(qkey), text):
                        r[field + '_final_verdict'] = 'correct'
                        r[field + '_resolution'] = 'agree'
            for field in FIELDS:
                if (row.get('type') != 'reproduction' or corrections.get('type') == 'replication') and field in ('outcome_computation', 'outcome_robustness'):
                    continue
                # Reproduction outcomes are adjudicated per axis only.
                if row.get('type') == 'reproduction' and corrections.get('type') != 'replication' and field == 'outcome':
                    continue
                d = decision_for(decisions, field, text, key['input_row_index'])
                if not d:
                    continue
                if field.startswith('outcome') and not (identity or source_identity):
                    continue
                if field == 'original' and d.get('target_index') is not None and not adjudicated_identity:
                    continue
                value = d.get('corrected_value')
                if d['verdict'] != 'undeterminable':
                    allowed = {'type': {'replication', 'reproduction', 'not_a_replication'},
                               'outcome': REPLICATION - UNKNOWN,
                               'outcome_computation': set(COMPUTATION.values()) - UNKNOWN,
                               'outcome_robustness': set(ROBUSTNESS.values()) - UNKNOWN}
                    changed_to_reproduction = (field == 'outcome' and isinstance(value, dict)
                        and corrections.get('type') == 'reproduction'
                        and value.get('outcome_computation') in set(COMPUTATION.values()) | {'cannot_be_determined'}
                        and value.get('outcome_robustness') in set(ROBUSTNESS.values()) | {'cannot_be_determined'}
                        and (value.get('outcome_computation') in set(COMPUTATION.values()) - UNKNOWN
                             or value.get('outcome_robustness') in set(ROBUSTNESS.values()) - UNKNOWN))
                    if field in allowed and not changed_to_reproduction and (not isinstance(value, str) or value not in allowed[field]):
                        continue
                    shipped = row.get('doi_o') if field == 'original' else row.get(field)
                    if field != 'original' and ((d['verdict'] == 'shipped_right') != (value == shipped)):
                        continue
                    if field == 'original':
                        remove_row = (value == {'action': 'remove_row'}
                                      and d['verdict'] in ('blind_right', 'both_wrong')
                                      and 'target_index' not in d)
                        if not remove_row and (not isinstance(value, (str, dict)) or (isinstance(value, dict) and not (value.get('doi') or value.get('title')))):
                            continue
                        corrected_doi = clean_doi(value.get('doi')) if isinstance(value, dict) else clean_doi(value)
                        if d['verdict'] in ('blind_right', 'both_wrong') and corrected_doi and corrected_doi == clean_doi(shipped):
                            continue
                r[field + '_final_verdict'] = verdict(d)
                r[field + '_resolution'] = d['method'] if verdict(d) != 'unverified' else 'unresolved'
                evidence[field] = {k: d.get(k) for k in ('quote', 'location', 'reason', 'method')}
                if verdict(d) == 'error':
                    corrections[field] = value
                    if field == 'type' and value != row.get('type'):
                        # Agreement in the old type's vocabulary cannot survive a
                        # corrected type. Only a supported subsequent outcome
                        # decision can establish its replacement.
                        for outcome_field in ('outcome', 'outcome_computation', 'outcome_robustness'):
                            r[outcome_field + '_final_verdict'] = 'unverified'
                            r[outcome_field + '_resolution'] = 'unresolved'
                            r[outcome_field + '_grade'] = 'unverified'
            if row.get('type') == 'reproduction' and corrections.get('type') != 'replication':
                axes = ['outcome_computation', 'outcome_robustness']
                values = [r[k + '_final_verdict'] for k in axes]
                r['outcome_final_verdict'] = 'error' if 'error' in values else 'correct' if values == ['correct', 'correct'] else 'unverified'
                grades = [r[k + '_grade'] for k in axes]
                r['outcome_grade'] = 'unverified' if 'unverified' in grades else 'exact' if grades == ['exact', 'exact'] else 'different'
                methods = [r[k + '_resolution'] for k in axes]
                r['outcome_resolution'] = 'unresolved' if 'unverified' in values else 'argon' if 'argon' in methods else 'obvious' if 'obvious' in methods else 'agree'
        overall = [r[k + '_resolution'] for k in ('type', 'original', 'outcome')]
        r['resolution'] = 'unresolved' if 'unresolved' in overall else 'argon' if 'argon' in overall else 'obvious' if 'obvious' in overall else 'agree'
        r['suggested_correction'] = json.dumps(corrections, ensure_ascii=False)
        r['correction_evidence'] = json.dumps(evidence, ensure_ascii=False)
        if not error:
            for field in ('type', 'original', 'outcome_computation', 'outcome_robustness') if row.get('type') == 'reproduction' else ('type', 'original', 'outcome'):
                if r[field + '_final_verdict'] == 'unverified' or r[field + '_final_verdict'] == 'error':
                    disagreements.append({'input_row_index': key['input_row_index'], 'work_key': key['work_key'],
                                          'file_key': key['file_key'], 'target_index': j, 'field': field,
                                          'pairing_flags': flags, 'reason': 'unmatched' if pair is None else 'comparison or evidence requires review',
                                          'final_verdict': r[field + '_final_verdict'], 'resolution': r[field + '_resolution'],
                                          'shipped': {k: row.get(k, '') for k in ('doi_o', 'title_o', 'authors_o', 'year_o', 'type', 'outcome', 'outcome_computation', 'outcome_robustness', 'outcome_quote')},
                                          'blind_type': coding.get('record_type'), 'blind_target': target,
                                          'identity_resolved': identity,
                                          'shipped_quote_present': r['shipped_quote_present']})
        results.append(r)
    used = {p[0] for p in proposed.values()}
    missing = []
    for j, target in enumerate(targets):
        if j in used:
            continue
        d = decision_for(decisions, 'missing_row', text, target_index=j)
        missing.append({'work_key': keys[0]['work_key'], 'file_key': keys[0]['file_key'],
                        'target_index': j, 'doi': target.get('doi', ''), 'title': target.get('title', ''),
                        'authors': target.get('authors', ''), 'year': target.get('year', ''),
                        'evidence_level': coding.get('evidence_level', ''),
                        'pairing_flags': '; '.join(sorted(tf.get(j, set()))),
                        'final_verdict': verdict(d) if d else 'unverified',
                        'resolution': d['method'] if d and verdict(d) != 'unverified' else 'unresolved',
                        'evidence': json.dumps(d or {}, ensure_ascii=False),
                        'blind_target': json.dumps(target, ensure_ascii=False)})
        disagreements.append({'work_key': keys[0]['work_key'], 'file_key': keys[0]['file_key'],
                              'target_index': j, 'field': 'missing_row', 'reason': 'unmatched blind target',
                              'final_verdict': missing[-1]['final_verdict'], 'resolution': missing[-1]['resolution']})
    return results, missing, disagreements


def write_csv(path, rows, columns):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def applicable_rate_rows(rows, field):
    if field == 'outcome':
        return [r for r in rows if r['type'] == 'replication']
    if field in ('outcome_computation', 'outcome_robustness'):
        return [r for r in rows if r['type'] == 'reproduction']
    return rows


def rate_line(rows, field):
    counts = collections.Counter(r[field + '_final_verdict'] for r in rows)
    correct, errors, unresolved = (counts[k] for k in ('correct', 'error', 'unverified'))
    n, total = correct + errors, len(rows)
    rate = f'{100 * errors / n:.1f}%' if n else 'not estimable'
    bounds = f'{100 * errors / total:.1f}%–{100 * (errors + unresolved) / total:.1f}%' if total else 'not estimable'
    return f'{errors} / {n} ({rate}); {unresolved} unverified; all-row unresolved bounds {bounds} (N={total})'


def report(results, missing, works, issues, finalized_at=None, review_summary=None, followup=None):
    followup_active = isinstance(followup, dict) and followup.get('status') == 'active'
    status = (f'Audit finalized at {finalized_at}. Unverified fields remain unresolved within the available evidence and review budget. '
              if finalized_at else 'This report is provisional until the parent finalizes the audit. ')
    lines = ['# FLoRA blind audit' + ('' if finalized_at else ' — provisional'), '',
             status + 'Blind disagreement alone establishes no error. '
             'Agreements require supported identity and quotes found in saved text; confirmed errors require an obvious or Argon decision with a reason, location and verified quote. '
             'The legacy automatic matcher tolerates normalized spacing and removed line-end hyphenation. Parent approval in the active evidence follow-up requires a contiguous literal quotation; a normalized match alone does not authorise integration. Neither check repairs words or mathematical signs.', '']
    errors = sum(any(r[k + '_final_verdict'] == 'error' for k in ('type', 'original', 'outcome')) for r in results)
    resolved = sum(r['resolution'] != 'unresolved' for r in results)
    lines += [f'{errors} input rows have at least one confirmed field error; {resolved} / {len(results)} rows are fully resolved. '
              f'{len(missing)} blind targets have no proposed shipped counterpart; these are not errors by default.', '', '## Coverage', '']
    # Lead with findings; retain the evidence standard immediately after them.
    lines[2:6] = [lines[4], '', lines[2], '']
    if followup_active:
        lines[6:6] = ['The complete evidence follow-up remains active. Earlier phase completion and cutoff figures below are historical. '
                      'New scientific decisions require contiguous literal primary-source quotations. Legacy accepted quotations are being '
                      'checked against exact saved source passages; context objections remain subject to review. '
                      'Candidate rechecks, field reviews and owned recovery work still remain. See '
                      '[evidence_followup/README.md](evidence_followup/README.md) and '
                      '[current progress](evidence_followup/integration/progress.json).', '']
    attempted = sum(w['attempted'] for w in works)
    coded = sum(w['coded'] for w in works)
    evidence = collections.Counter(w['evidence_level'] for w in works if w['text_obtained'])
    lines += [f'Works: {len(works)} total; {attempted} attempted; {sum(evidence.values())} with verified saved text '
              f'({evidence["full_text"]} full text, {evidence["abstract"]} abstract); {coded} with validated usable coding. '
              f'Rows fully resolved: {resolved} / {len(results)}.', '',
              'Coverage is prioritized and depends on text access. This is not a representative sample. '
              'Rates use correct + confirmed-error rows as field-specific evaluable denominators. '
              'Bounds put every unverified row first outside, then inside the error count over all applicable input rows; '
              'they are sensitivity bounds, not binomial confidence intervals. '
              'Confidence is descriptive only. Study status is reported separately and does not change type agreement. '
              'Replication outcome rates use rows shipped as replications; axis-specific rates use rows shipped as reproductions. '
              'Dependent outcome replacements after a type correction remain in results.csv and the error list.', '',
              '## Confirmed field error rates', '']
    if review_summary:
        position = lines.index('## Confirmed field error rates')
        lines[position:position] = [
            f'Cross-model review used {review_summary["call_attempts_consumed"]} call attempts across '
            f'{review_summary["workgroups_with_calls"]} works. '
            f'{review_summary["unresolved_workgroups"]} works ended without a fully validated review reply; '
            'separately supported fields remain usable. Validated replies may also return undeterminable fields. '
            f'{review_summary["prepared_workgroups_without_call"]} prepared works '
            f'({review_summary["prepared_fields_without_call"]} distinct field requests) received no call '
            'before the review cutoff. These requests establish no error. '
            'Other unverified fields also include missing text, ambiguous identity and insufficient evidence.', '']
    if review_summary and review_summary.get('supplemental', {}).get('integrated_verdicts'):
        phase = review_summary['supplemental']
        position = lines.index('## Confirmed field error rates')
        integrated = phase.get('integrated_verdicts', {})
        resolved = integrated.get('correct', 0) + integrated.get('error', 0)
        lines[position:position] = [
            f'After the original bounded run, a user-authorised supplemental review covered '
            f'{phase["requests_reviewed"]} deferred field requests across {phase["works_reviewed"]} works '
            f'using {phase["call_attempts_consumed"]} additional Argon attempts. '
            f'{resolved} requests have a substantive integrated verdict; '
            f'{integrated.get("unverified", 0)} remain unverified after review. '
            'No coding acquisition was restarted and the original run history is preserved in run_manifest.json. '
            'Source inspection additionally excluded one coding whose saved source contained an empty abstract and references only.', '']
    if not followup_active and review_summary and review_summary.get('completion_pass', {}).get('completed_at'):
        phase = review_summary['completion_pass']
        position = lines.index('## Confirmed field error rates')
        lines[position:position] = [
            f'A final cheap omission pilot used {phase["pilot_tasks"]} Luna tasks for '
            f'{phase["pilot_candidates"]} candidates. Parent inspection verified all '
            f'{phase["literal_quotes_verified"]} source quotations and confirmed '
            f'{phase["confirmed_additional_omissions"]} additional omissions; '
            f'{phase["pilot_candidates_deferred"]} pilot cases require publication-level '
            'deduplication or renewed expert interpretation. One background classification '
            'was overturned by explicit replication results in the source. Luna labels '
            'were not accepted without parent source review. Outcomes for the additional '
            'targets were not adjudicated. Wider candidate triage is deferred because '
            'it still requires substantial source and identity checking. See '
            '[completion_pass/README.md](completion_pass/README.md) and its field and '
            'candidate disposition tables. Main field verdicts and shipped-type '
            'denominators are preserved; conditionally inapplicable fields are identified '
            'separately. No model work or audit schedules remain active.', '']
    for field in FIELDS:
        applicable = applicable_rate_rows(results, field)
        lines.append(f'- {field}: {rate_line(applicable, field)}')
    for group in ('source', 'evidence_level'):
        lines += ['', f'### By {group}', '']
        for value in sorted({r[group] for r in results}):
            subset = [r for r in results if r[group] == value]
            lines.append(f'- {value or "(missing)"}:')
            for field in FIELDS:
                applicable = applicable_rate_rows(subset, field)
                lines.append(f'  - {field}: {rate_line(applicable, field)}')
    lines += ['', '## Every confirmed input-row error', '', 'Complete quotes, locations, reasons and corrected values are retained in [results.csv](results.csv), keyed by the immutable, zero-based input row index (0–2817).', '']
    for r in results:
        fields = [k for k in ('type', 'original', 'outcome') if r[k + '_final_verdict'] == 'error']
        if fields:
            doi = clean_doi(r['doi_r'])
            link = (f'[replicating work](https://doi.org/{doi})' if doi else
                    f'[replicating work]({r["work_key"]}) (DOI unavailable)' if r['work_key'].startswith(('https://', 'http://')) else
                    'replicating work (DOI unavailable)')
            corrections = json.loads(r['suggested_correction'])
            changes = []
            for field, value in corrections.items():
                old = r.get('doi_o' if field == 'original' else field, '')
                if isinstance(value, dict):
                    value = ('remove this row' if value == {'action': 'remove_row'} else
                             value.get('doi') or value.get('title') or
                             '; '.join(f'{k}: {v}' for k, v in value.items()))
                label = field.replace('_', ' ')
                changes.append(f'{label}: {old} → {value}' if old else f'{label}: {value}')
            lines.append(f'- Row {r["input_row_index"]}, {link}: {"; ".join(changes)}.')
    if not errors:
        lines.append('No input-row errors are confirmed at this checkpoint.')
    version_notes = {
        '990cdb9f33b9b199': 'Row 891 uses a working-paper DOI for the same study; '
            '[NBER lists the journal version](https://www.nber.org/papers/w6614). '
            'Its reproduction outcomes benchmark the cited 2000 publication; numerical equivalence between versions is not assumed.',
        '9dad580b3423aa2b': 'Row 2238 was checked against the verified 2020 working paper; the final 2022 article was not obtained.',
        '0245b18b007f60d7': 'Row 929 was checked against the verified 2015 draft; the final 2017 article was not obtained.',
        '00319989aba88467': 'Row 1329 identifies the published journal version of the same empirical paper, '
            'but the replication explicitly tests its [2018 proceedings version](https://doi.org/10.5465/AMBPP.2018.51). '
            'Metadata and the source footnote support shared study identity with the '
            '[journal article](https://doi.org/10.1177/1042258719892987); outcome equivalence across versions is not assumed, '
            'so that outcome remains unverified.',
    }
    limits = [note for fk, note in version_notes.items() if any(
        r['file_key'] == fk and (fk == '00319989aba88467' or any(r[k + '_final_verdict'] == 'error' for k in ('type', 'original', 'outcome')))
        for r in results)]
    if limits:
        lines += ['', 'Source-version notes and limits: ' + ' '.join(limits) +
                  ' These judgments describe the supplied versions; changes in unseen final versions cannot be ruled out.']
    lines += ['', '## Unmatched blind targets', '',
              'The [confirmed missing-reference export](confirmed_missing_references.csv) contains only source-supported omissions. '
              '[Unresolved candidates](unresolved_missing_candidates.csv) are kept separately; held or unverified references do not enter the confirmed export.', '']
    for r in missing:
        if r['final_verdict'] == 'error':
            doi = clean_doi(r['doi'])
            name = r['title'] or (r['authors'] + ' (' + r['year'] + ')').strip() or doi
            link = f'[{name}](https://doi.org/{doi})' if doi else name
            lines.append(f'- Confirmed missing target: {link}; work '+(f'[replicating work](https://doi.org/{r["work_key"]})' if r['work_key'].startswith('10.') else r['work_key'])+f', target {r["target_index"]} ({r["resolution"]}).')
    lines += [f'{sum(r["final_verdict"] == "unverified" for r in missing)} unmatched blind targets remain unverified. '
              'Ambiguous proposed pairs remain in results.csv with flags and unverified verdicts.', '', '## Skips and validation issues', '']
    skips = collections.Counter(w['skip_reason'] for w in works if w['skip_reason'])
    lines.extend(f'- {reason}: {n} works.' for reason, n in sorted(skips.items()))
    lines.extend(f'- {issue}' for issue in issues)
    if not skips and not issues:
        lines.append('None.')
    lines += ['', '## Time per work', '']
    timed = [w for w in works if w['elapsed_seconds'] is not None]
    lines.append(f'Elapsed time supplied for {len(timed)} / {len(works)} works; missing times are not imputed. '
                 'Times describe final saved checkpoints and exclude earlier failed or excluded attempts; this is worker time, not wall-clock audit duration.')
    adjusted = [w for w in works if w.get('timing_basis')]
    if adjusted:
        lines.append(f'{len(adjusted)} reported timing correction(s) are applied from [timing_corrections.json](timing_corrections.json); '
                     'the original checkpoint times and correction bases remain in work_times.csv. Clock bounds are reported as bounds, not exact measurements.')
    if timed:
        lines.append(f'Sum of reported final-checkpoint times: {sum(w["elapsed_seconds"] for w in timed):.1f} seconds.')
        lines.append('Per-work elapsed time and skips are recorded in [work_times.csv](work_times.csv).')
    return '\n'.join(lines) + '\n'


def run(input_path=INPUT, audit_dir=ROOT, output_dir=None):
    root = Path(audit_dir)
    output = Path(output_dir) if output_dir else root
    frozen = read_csv(input_path)
    manifest = read_csv(root / 'manifest.csv')
    indices = [int(k['input_row_index']) for k in manifest]
    if sorted(indices) != list(range(len(frozen))):
        raise ValueError('manifest must contain every input row exactly once (zero-based)')
    schema, error = read_json(root / 'coding_schema.json')
    if error or not isinstance(schema, dict):
        raise ValueError('coding_schema.json missing or malformed')
    run_manifest, error = read_json(root / 'run_manifest.json')
    finalized_at = run_manifest.get('audit_finalized_at') if isinstance(run_manifest, dict) else None
    followup_active = isinstance(run_manifest, dict) and run_manifest.get('evidence_followup', {}).get('status') == 'active'
    if followup_active:
        finalized_at = None
    if not error and isinstance(run_manifest, dict):
        expected = run_manifest.get('input_hashes', {}).get(Path(input_path).name)
        if expected and expected != hashlib.sha256(Path(input_path).read_bytes()).hexdigest():
            raise ValueError('input hash differs from run manifest')
    grouped = collections.defaultdict(list)
    file_keys = {}
    for key in manifest:
        fk = key['file_key']
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', fk):
            raise ValueError('unsafe file_key')
        if fk in file_keys and file_keys[fk] != key['work_key']:
            raise ValueError('file_key collision across work_keys')
        file_keys[fk] = key['work_key']
        grouped[key['work_key']].append(key)
    results, missing, disagreements, works, issues = [], [], [], [], []
    timing_path = root / 'timing_corrections.json'
    timing_corrections = json.loads(timing_path.read_text()) if timing_path.exists() else {}
    attempted_files = set()
    if (root / 'tasks.jsonl').exists():
        for line in (root / 'tasks.jsonl').read_text().splitlines():
            try: attempted_files.update(json.loads(line).get('files', []))
            except (ValueError, TypeError): pass
    for state_path in sorted((root / 'argon').glob('*.state.json')):
        state, _ = read_json(state_path)
        if isinstance(state, dict) and state.get('status') == 'unresolved':
            recovered = state.get('partial_recovery', {}).get('recovered_complete_field_objects', 0)
            recovery = f'{recovered} complete field decisions recovered from partial replies. ' if recovered else ''
            issues.append(f"Argon {state.get('file_key', state_path.stem)}: unresolved after {state.get('attempts')} attempts; {state.get('reason', 'failure')}. {recovery}Supported field decisions retained separately remain usable; unresolved fields stay unverified.")
    incidents, _ = read_json(root / 'blinding_incidents.json')
    if incidents:
        affected = len({incident['file_key'] for incident in incidents})
        issues.append(f'Blinding incidents affected {affected} works; excluded judgments remain quarantined. '
                      'Only independent fresh-child retries enter primary results; exhausted retries remain unverified. '
                      'See blinding_incidents.json and post_exposure_exclusions.json for the complete record.')
    for work_key, keys in grouped.items():
        if len({k['file_key'] for k in keys}) != 1:
            raise ValueError('one work_key has multiple file_keys')
        fk = keys[0]['file_key']
        rows = []
        for k in keys:
            raw = frozen[int(k['input_row_index'])]
            rows.append({**adapt_row(raw), '_raw_outcome': raw.get('outcome', '')})
        coding, error, text = load_coding(root, fk, work_key, schema)
        decisions, issue = load_decisions(root, fk)
        if issue:
            issues.append(f'{fk}: {issue}')
        for n, d in enumerate(decisions):
            if not valid_decision(d, text):
                issues.append(f'{fk}: decision {n} failed evidence/shape validation and was ignored.')
        r, m, ds = compare_work(rows, keys, coding, error, text, decisions)
        results.extend(r)
        missing.extend(m)
        disagreements.extend(ds)
        elapsed = next((coding.get(k) for k in ('elapsed_seconds', 'seconds', 'duration_seconds')
                        if isinstance(coding.get(k), (int, float)) and not isinstance(coding.get(k), bool)
                        and 0 <= coding[k] < float('inf')), None)
        checkpoint_elapsed = elapsed
        timing_basis = ''
        if fk in timing_corrections:
            correction = timing_corrections[fk]
            value = correction.get('elapsed_seconds')
            if (correction.get('work_key') != work_key
                    or correction.get('checkpoint_elapsed_seconds') != elapsed
                    or not isinstance(value, (int, float)) or isinstance(value, bool)
                    or not 0 <= value < float('inf') or not correction.get('basis')):
                raise ValueError(f'{fk}: invalid or stale timing correction')
            elapsed, timing_basis = value, correction['basis']
        works.append({'work_key': work_key, 'file_key': fk,
                      'attempted': fk in attempted_files or (root / 'codings' / (fk + '.json')).exists(),
                      'coded': not error, 'text_obtained': bool(text),
                      'evidence_level': coding.get('evidence_level') or 'none',
                      'skip_reason': error, 'elapsed_seconds': elapsed,
                      'checkpoint_elapsed_seconds': checkpoint_elapsed, 'timing_basis': timing_basis})
    results.sort(key=lambda r: int(r['input_row_index']))
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / 'work_times.csv', works, list(works[0]) if works else ['work_key','file_key'])
    # Preserve all-row output even when no coding is present.
    columns = list(results[0]) if results else ['input_row_index', 'work_key', 'file_key']
    write_csv(output / 'results.csv', results, columns)
    missing_columns = ['work_key', 'file_key', 'target_index', 'doi', 'title', 'authors', 'year',
                       'evidence_level', 'pairing_flags', 'final_verdict', 'resolution', 'evidence', 'blind_target']
    write_csv(output / 'missing_rows.csv', missing, missing_columns)
    write_csv(output / 'confirmed_missing_references.csv',
              [r for r in missing if r['final_verdict'] == 'error'], missing_columns)
    write_csv(output / 'unresolved_missing_candidates.csv',
              [r for r in missing if r['final_verdict'] == 'unverified'], missing_columns)
    (output / 'disagreements.json').write_text(json.dumps({'provisional': not bool(finalized_at),
                                                         'finalized_at': finalized_at, 'items': disagreements,
                                                         'validation_issues': issues}, ensure_ascii=False, indent=2) + '\n')
    review_summary = dict(run_manifest.get('review_summary', {})) if isinstance(run_manifest, dict) else None
    if followup_active and review_summary:
        review_summary.pop('completion_pass', None)  # that closed pilot is historical
    report_text = report(results, missing, works, issues, finalized_at, review_summary,
                         run_manifest.get('evidence_followup') if isinstance(run_manifest, dict) else None)
    if followup_active:
        report_text = ('> **Full evidence follow-up is active.** These are the latest integrated results, '
                       'not final follow-up counts. All outstanding full-text fields, primary-source recovery '
                       'and exhaustive omission checks are in progress. See '
                       '[evidence_followup/README.md](evidence_followup/README.md) and its live queues.\n\n' + report_text)
        registry = root / 'evidence_followup/additional_reports/approved_sources.json'
        if registry.exists():
            approved_reports = [x for x in json.loads(registry.read_text())['reports']
                                if x['status'] == 'approved_for_comparison']
            report_text += ('\nAdditional primary evidence includes ' + str(len(approved_reports)) +
                            ' separately recovered individual reports, each independently identity-checked, '
                            'freshly blindly coded and hash-verified. Their exact texts supplement the '
                            'collection evidence without changing the base files used by active reviews. '
                            'Source provenance and parent decisions are in '
                            '[additional_reports](evidence_followup/additional_reports/parent_decisions.json).\n')
    (output / 'REPORT.md').write_text(report_text, encoding='utf-8')
    return {'rows': len(results), 'works': len(works), 'missing_targets': len(missing),
            'disagreements': len(disagreements), 'output_dir': str(output.resolve())}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--input', type=Path, default=INPUT)
    parser.add_argument('--audit-dir', type=Path, default=ROOT)
    parser.add_argument('--output-dir', type=Path, help='Defaults to audit-dir')
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.audit_dir, args.output_dir), indent=2))


if __name__ == '__main__':
    main()
