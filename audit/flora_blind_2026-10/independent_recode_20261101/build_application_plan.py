#!/usr/bin/env python3
"""Write a dry-run plan for candidate bundles against current FLoRA. Contacts nothing and applies nothing."""
import hashlib
import json
import re
from pathlib import Path

import csv
import sys

import build_field_ledger as L

sys.path.insert(0, str(L.B / 'scripts'))
import build_ledger_review as R  # noqa: E402

PRIVATE_PLAN = L.P / 'application_plan_dryrun_private.json'
SUMMARY = L.T / 'application_plan_summary.json'
CORRECTIONS_JSON = L.B / 'handoff/corrections_to_apply.json'
CORRECTIONS_CSV = L.B / 'handoff/corrections_to_apply.csv'
AXIS_COLUMNS = {'outcome_computation': ('outcome_computation', 'outcome_computational_quote', 'out_quote_computational_source'),
                'outcome_robustness': ('outcome_robustness', 'outcome_robustness_quote', 'out_quote_robust_source')}


def review_of(row, registry):
    entry = registry.get('bundles', {}).get(f'row:{row}')
    if not entry:
        return None
    return L.read(L.P / 'adversarial_20261103' / entry['request_id'] / 'review.json')


def reader_quote(member, frozen_row, art):
    """The literal quote behind a change settled by one more read of the paper."""
    field, close = member['field'], member['close_read']
    if close.get('request_id'):
        review = L.read(L.P / 'final_read_20261104' / close['request_id'] / 'review.json')
        return review['replacement_quote'], review['replacement_quote_section']
    role = close.get('quote_role') or next((r for r in ('sol', 'opus') if member[r]['literal_quote_ok']), None)
    assert role and member[role]['literal_quote_ok'], member['field_id']
    targets = [t for t in art.coding(member[role]['path'])['targets'] if t.get(field) == member['proposed_value']]
    if len(targets) > 1:
        targets = [t for t in targets if L.target_binding(t, L.identity_of_row(frozen_row))]
    assert len(targets) == 1, member['field_id']
    return targets[0][L.QUOTE_KEY[field]], close.get('quote_section') or targets[0].get('outcome_quote_section') or 'full_text'


def plan_bundle(row, members, current, export_case, review, metadata, frozen_row=None, art=None):
    """Turn a frozen-schema proposal into current-schema fields with preconditions."""
    names = {m['field'] for m in members}
    if 'type' in names:
        wanted = {}
        for m in members:
            if isinstance(m['proposed_value'], dict):
                wanted.update(m['proposed_value'])
            else:
                wanted[m['field']] = m['proposed_value']
        return dict(status='blocked_no_route', reason='type is not an editable field in flora-validation', fields={}, preconditions={},
                    intended=wanted, current={k: current.get(k) for k in wanted})
    fields = {}
    quote, section = None, None
    if export_case:
        quote = export_case['replacements'].get('outcome_quote')
        section = export_case['replacements'].get('outcome_quote_source')
    elif review:
        quote, section = review.get('replacement_quote'), review.get('replacement_quote_section')
    for member in members:
        name = member['field']
        if member.get('close_read') and name != 'original':
            quote, section = reader_quote(member, frozen_row, art)
        if name == 'outcome':
            fields['outcome'] = member['proposed_value']
            if quote:
                fields.update(outcome_quote=quote, outcome_quote_source=section)
        elif name in AXIS_COLUMNS:
            value, quote_column, source_column = AXIS_COLUMNS[name]
            fields[value] = member['proposed_value']
            if quote:
                fields.update({quote_column: quote, source_column: section})
        elif name == 'original':
            replacements = export_case['replacements'] if export_case else (metadata or {}).get('replacements')
            if not replacements:
                return dict(status='blocked_needs_authoritative_metadata', fields={}, preconditions={})
            fields.update({k: v for k, v in replacements.items() if k in current and k.endswith('_o')})
    for key, value in list(fields.items()):
        if isinstance(value, str):
            if key.endswith(('_quote', '_o')):
                # PDF line breaks and soft hyphens are not part of the quote a reader sees in FLoRA.
                fields[key] = R.clean_quote(value)
            continue
        return dict(status='blocked_unexpected_value', reason=key, fields={}, preconditions={})
    unknown = sorted(k for k in fields if k not in current)
    if unknown:
        return dict(status='blocked_unknown_column', reason=unknown, fields={}, preconditions={})
    return dict(status='patchable', fields=fields, preconditions={k: current[k] for k in fields})


def write_corrections(ledger, bundles, exclusions, ledger_sha):
    """The list a maintainer works from. It needs nothing from this machine's private audit files."""
    patch = [b for b in bundles if b['status'] == 'patchable']
    route = [b for b in bundles if b['status'] == 'blocked_no_route']
    assert len(patch) + len(route) == len(bundles), [b['status'] for b in bundles]
    data = dict(
        schema_version=1,
        status='Not applied. Check each expected value against the live record first, because the database may be ahead of this release.',
        quote_note='Each new quote is a literal passage from the paper. The only edits repair PDF damage: line breaks, broken characters and, in three quotes, text from a neighbouring column or page header.',
        audit_ledger_sha256=ledger_sha, checked_against=dict(release_commit=ledger['current']['commit'], flora_csv_sha256=ledger['current']['sha256']),
        how_to_apply='Read the record through GET /api/admin/flora/{id}. If every expected value matches, send all fields of that entry in one PATCH with the record version and the note. If any value differs, skip that entry and report it.',
        corrections=[dict(flora_id=b['flora_id'], source_record_id=b['source_record_id'], audit_row=int(b['bundle_id'].split(':')[1]),
                          set={'expected': b['preconditions'], 'new': b['fields']}, note=f"FLoRA audit 2026-10: {', '.join(b['ledger_fields'])}; ledger {ledger_sha[:12]}") for b in patch],
        study_type_changes_needing_a_route=[dict(flora_id=b['flora_id'], source_record_id=b['source_record_id'], audit_row=int(b['bundle_id'].split(':')[1]),
                                                 current=b['current'], intended=b['intended'], reason=b['reason']) for b in route],
        record_removals=[{k: e[k] for k in ('flora_id', 'exclusion_key', 'status', 'rows_sharing_key')} for e in exclusions])
    CORRECTIONS_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    with CORRECTIONS_CSV.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['flora_id', 'source_record_id', 'column', 'expected_current_value', 'new_value', 'note'])
        for c in data['corrections']:
            for column, value in c['set']['new'].items():
                writer.writerow([c['flora_id'], c['source_record_id'], column, c['set']['expected'][column], value, c['note']])


def build():
    ledger = L.read(L.OUTPUT)
    art = L.Artifacts()
    registry_path = L.T / 'adversarial_review_registry.json'
    registry = L.read(registry_path) if registry_path.exists() else {}
    current_by_id = {row['id']: row for row in art.current}
    export_cases = {c['input_row_index']: c for c in art.export['cases']}
    by_row = {}
    for field in ledger['fields']:
        by_row.setdefault(field['input_row_index'], []).append(field)
    bundles = []
    for row, members in sorted(by_row.items()):
        if R.bundle_view(members) != 'ready':
            continue
        members = R.edits_of(members)
        flora_id = members[0]['current']['flora_id']
        current = current_by_id[flora_id]
        outcome = plan_bundle(row, members, current, export_cases.get(row), review_of(row, registry), art.authoritative.get(str(row)), art.frozen[row], art)
        bundles.append(dict(bundle_id=f'row:{row}', flora_id=flora_id, source_record_id=current['source_record_id'],
                            ledger_fields=[m['field_id'] for m in members], **outcome))
    exclusions = []
    for case in art.export['record_actions']:
        row = case['input_row_index']
        member = by_row[row][0]
        flora_id = member['current'].get('flora_id')
        current = current_by_id.get(flora_id)
        key = current and (L.identifier(current['doi_r']) or L.norm(current['url_r']))
        sharing = [c['id'] for c in art.current if current and (L.identifier(c['doi_r']) or L.norm(c['url_r'])) == key]
        exclusions.append(dict(bundle_id=f'row:{row}', flora_id=flora_id, exclusion_key=key, rows_sharing_key=sharing,
                               status='check_shared_key' if len(sharing) != 1 else 'single_row_key'))
    ledger_sha = hashlib.sha256(L.OUTPUT.read_bytes()).hexdigest()
    plan = dict(schema_version=1, dry_run_only=True, ledger_sha256=ledger_sha, current_commit=ledger['current']['commit'],
                current_sha256=ledger['current']['sha256'], bundles=bundles, record_exclusions=exclusions,
                user_approval_recorded=False, canonical_changes_applied=False)
    PRIVATE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n')
    counts = {}
    for bundle in bundles:
        counts[bundle['status']] = counts.get(bundle['status'], 0) + 1
    summary = dict(schema_version=1, dry_run_only=True, ledger_sha256=ledger_sha, current_commit=ledger['current']['commit'],
                   bundle_status_counts=dict(sorted(counts.items())), blocked=[b['bundle_id'] for b in bundles if b['status'] != 'patchable'],
                   record_exclusions=[{k: e[k] for k in ('bundle_id', 'flora_id', 'status')} for e in exclusions],
                   plan_sha256=hashlib.sha256(PRIVATE_PLAN.read_bytes()).hexdigest(),
                   user_approval_recorded=False, canonical_changes_applied=False)
    SUMMARY.write_text(json.dumps(summary, indent=1) + '\n')
    write_corrections(ledger, bundles, exclusions, ledger_sha)
    return summary


if __name__ == '__main__':
    print(json.dumps(build(), indent=1))
