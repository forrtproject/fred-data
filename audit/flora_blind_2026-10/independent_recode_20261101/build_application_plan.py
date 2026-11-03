#!/usr/bin/env python3
"""Write a dry-run plan for candidate bundles against current FLoRA. Contacts nothing and applies nothing."""
import hashlib
import json
from pathlib import Path

import build_field_ledger as L

PRIVATE_PLAN = L.P / 'application_plan_dryrun_private.json'
SUMMARY = L.T / 'application_plan_summary.json'
AXIS_COLUMNS = {'outcome_computation': ('outcome_computation', 'outcome_computational_quote', 'out_quote_computational_source'),
                'outcome_robustness': ('outcome_robustness', 'outcome_robustness_quote', 'out_quote_robust_source')}


def review_of(row, registry):
    entry = registry.get('bundles', {}).get(f'row:{row}')
    if not entry:
        return None
    return L.read(L.P / 'adversarial_20261103' / entry['request_id'] / 'review.json')


def plan_bundle(row, members, current, export_case, review, metadata):
    """Turn a frozen-schema proposal into current-schema fields with preconditions."""
    names = {m['field'] for m in members}
    if 'type' in names:
        return dict(status='blocked_no_route', reason='type is not an editable field in flora-validation', fields={}, preconditions={})
    fields = {}
    quote, section = None, None
    if export_case:
        quote = export_case['replacements'].get('outcome_quote')
        section = export_case['replacements'].get('outcome_quote_source')
    elif review:
        quote, section = review.get('replacement_quote'), review.get('replacement_quote_section')
    for member in members:
        name = member['field']
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
            continue
        return dict(status='blocked_unexpected_value', reason=key, fields={}, preconditions={})
    unknown = sorted(k for k in fields if k not in current)
    if unknown:
        return dict(status='blocked_unknown_column', reason=unknown, fields={}, preconditions={})
    return dict(status='patchable', fields=fields, preconditions={k: current[k] for k in fields})


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
        if not all(m['ready'] for m in members) or {m['current']['relation'] for m in members} != {'unchanged_from_frozen'}:
            continue
        flora_id = members[0]['current']['flora_id']
        current = current_by_id[flora_id]
        outcome = plan_bundle(row, members, current, export_cases.get(row), review_of(row, registry), art.authoritative.get(str(row)))
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
    return summary


if __name__ == '__main__':
    print(json.dumps(build(), indent=1))
