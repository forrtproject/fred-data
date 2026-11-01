"""Attach record-level remedies without modifying historical field adjudications."""
import hashlib
import json
from pathlib import Path

B = Path(__file__).resolve().parents[1]
H = B / 'handoff'


def record_actions(frozen):
    proposals = json.loads((H / 'correction_proposals.json').read_text())['changes']
    actions = []
    for item in proposals:
        if item['field'] != 'type' or item['proposed_value'] != 'not_a_replication':
            continue
        i = item['input_row_index']
        held = bool(item.get('application_hold'))
        actions.append(dict(
            input_row_index=i, case_id=f'row:{i}',
            status='decision_required' if held else 'proposed',
            action='Exclude this record from the replication/reproduction dataset',
            reason=('The source does not report an empirical retest of a specific published finding. '
                    'Exclude it from replication/reproduction records and preserve its audit history.'
                    if not held else 'Whether the published observations qualify as an original finding needs a coding-policy decision. Decide that rule before excluding this record.'),
            proposed_changes={'record_inclusion': 'exclude_from_replication_reproduction_dataset'},
            dependencies=[item['application_hold']] if held else [],
            evidence=item['evidence'],
            decision_reference=item['decision_reference'],
            preserves='Retain the source, excluded record and all prior decisions in the audit history.',
            operation='exclude_nonreplication_record'))
    assert len(actions) == 9
    source = B / 'publication/record_scope_review_20261101.json'
    if source.exists():
        review = json.loads(source.read_text())
        current_file = H / 'current_source_decisions.json'
        current = {d['input_row_index']: d for d in json.loads(current_file.read_text())['decisions']} if current_file.exists() else {}
        for finding in review['findings']:
            i = finding['input_row_index']
            actions.append(dict(
                input_row_index=i, case_id=f'row:{i}', status='proposed',
                action={
                    'move_plan_out_of_completed_results_pool': 'Move this registration to planned studies',
                    'replace_r_with_verified_results_report_and_refresh_dependencies': 'Replace the Stage 1 draft with the completed report',
                    'bind_current_completed_report_and_refresh_r_bibliography': 'Update the record to identify the completed report',
                    'preserve_existing_remove_row_decision_keep_empirical_target_row464': 'Remove this incorrect pair and retain row 464',
                }[finding['record_action']],
                operation=finding['record_action'], reason=finding['reason'],
                proposed_changes=finding.get('proposed_changes', []),
                exact_source_pdf_sha256=finding.get('report_pdf_sha256'),
                server_pdf_hash_matches=finding.get('server_pdf_hash_matches'),
                required_together=finding.get('dependent_fields_to_refresh', []),
                source_limits=('The completed report’s citation year remains unverified; do not carry over the registration year.' if i==1710 else
                    'No verified completed report was located. The linked parent project returned HTTP 401; this does not establish that the study was never completed.' if i==0 else []),
                evidence=[{('quote' if k == 'literal_contiguous_quote' else k): v
                           for k, v in proof.items()} for proof in finding['evidence']],
                source_urls=finding.get('report_links', []),
                dependencies=['Apply report identity, bibliography and quotations together; keep the registration/version history.']
                    if 'completed_report' in finding['record_action'] or 'results_report' in finding['record_action'] else [],
                decision_reference='../publication/record_scope_review_20261101.json'))
            if i == 0:
                actions[-1]['reason'] = ('The linked document registers a future study. The quoted 2022 result describes a different, earlier experiment. '
                    'Move this planned attempt out of completed-result records, and preserve the registration and its intended targets in planned studies.')
                actions[-1]['proposed_changes'][0]['preserve'] = 'Keep the registration, its intended original-study links, and the old record in the audit history.'
            elif i == 1852:
                actions[-1]['reason'] = 'The record cites a registration, but its failed outcome is supported by the completed report. Replace the registration citation with that report’s title, authors, year and evidence quotation.'
            elif i == 2362:
                actions[-1]['reason'] = 'The record cites a results-blind registration. The completed published report supports a successful replication. Use the publication’s citation and evidence, and keep the registration as study history.'
            elif i == 2388:
                actions[-1]['reason'] = 'The project contains an old simulated draft and a completed report. Identify the exact completed report and correct the author names. Its successful outcome is already source-verified.'
            elif i == 533:
                actions[-1]['reason'] = 'This pair links a completed replication to a protocol rather than the empirical original. The correct pair already exists at row 464. Remove this incorrect pair and retain row 464.'
            if i in current:
                outcome = current[i]['fields']['outcome']
                actions[-1]['confirmed_completed_report_outcome'] = outcome['confirmed_value']
                actions[-1]['reason'] = ('The saved source was a draft with simulated results. The completed report supports the ' + outcome['confirmed_value'] +
                    ' outcome already in FLoRA. Update the report reference, citation and evidence quotation together; preserve the registration as study history.')
                actions[-1]['proposed_changes'].append(dict(field='outcome_quote', old=frozen[i]['outcome_quote'],
                    proposed=outcome['proofs'][0]['quote'], proof=outcome['proofs'][0]))
                actions[-1]['current_source_decision_reference'] = 'current_source_decisions.json'
    existing_holds = {
        381: ('Remove the duplicate pair and retain row 315', 'merge_duplicate_pair', 315),
        428: ('Remove the duplicate pair and retain row 814', 'merge_duplicate_pair', 814),
        1698: ('Merge both replication attempts into row 1697, then remove this duplicate', 'merge_attempt_evidence_then_remove_duplicate', 1697),
        937: ('Correct the original-study binding and outcome together', 'correct_pair_binding_together', None),
    }
    hold_summaries = {
        381: 'The corrected original is Gao et al. (2013), already represented by row 315. Keep that pair and remove this duplicate. The failed outcome must not remain attached to the incorrectly linked Klein study.',
        428: 'The correct original is Simonovits, Guess and Nagler (2019), already represented by row 814. Keep that pair and remove this duplicate. Apply any outcome update to the retained pair.',
        1698: 'This duplicates row 1697 but contains another replication attempt. Preserve both attempts’ evidence in row 1697 before removing this duplicate.',
        937: 'The failed outcome applies to the Seidel (2010) target. Correct the original-study link and outcome together; preserve the old Vrijsen (2014) pairing in the audit history.',
    }
    final = {d['input_row_index']: d for d in json.loads((H / 'sol_review_decisions.json').read_text())['decisions']}
    for i, (title, operation, retained) in existing_holds.items():
        d = final[i]
        actions.append(dict(input_row_index=i, case_id=f'row:{i}', status='decision_required',
            action=title, operation=operation, reason=hold_summaries[i],
            dependencies=['Apply the coordinated record change and preserve the retained pair’s source evidence.'],
            audit_application_hold=d['application_hold'],
            proposed_changes=([dict(operation=operation, remove_input_row_index=i,
                retain_input_row_index=retained, preserve='Merge the distinct attempt evidence before removal.' if i==1698 else 'Keep the already represented empirical pair; do not create another copy.')]
                if retained is not None else {x['field']: x['proposed_value'] for x in proposals if x['input_row_index']==i}),
            retained_row_index=retained,
            retained_before_sha256=hashlib.sha256(json.dumps(frozen[retained], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest() if retained is not None else None,
            decision_reference='sol_review_decisions.json'))
    for a in actions:
        i = a['input_row_index']
        a['expected_before_full_record_sha256'] = hashlib.sha256(json.dumps(
            frozen[i], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        a['current_record'] = {k: frozen[i][k] for k in
                               ['doi_r', 'title_r', 'year_r', 'type', 'outcome']}
        a['canonical_dataset_changes_applied'] = False
    assert len({a['input_row_index'] for a in actions}) == len(actions)
    (H / 'record_actions.json').write_text(json.dumps(dict(
        status='record_level_proposals_not_applied', actions=actions,
        note='Record remedies take priority over isolated field edits. Historical field verdicts remain source-bound evidence.'),
        ensure_ascii=False, indent=2)+'\n')
    return {a['input_row_index']: a for a in actions}


def enrich_cases(cases, frozen):
    """Use current results sources and make whole-record dependencies explicit."""
    actions = record_actions(frozen)
    current_path = H / 'current_source_decisions.json'
    current = {d['input_row_index']: d for d in json.loads(current_path.read_text())['decisions']} if current_path.exists() else {}
    for c in cases:
        i = c.get('row')
        if i in current:
            d = current[i]
            for f, value in d['fields'].items():
                if f in c['changes']:
                    c.setdefault('superseded_source_proposals', {})[f] = c['changes'].pop(f)
                proof = value['proofs'][0]
                c['evidence'][f] = dict(quote=proof['quote'], location=proof['section'],
                                        reason=value['rationale'], method='Independent current-report blind coding and source review')
            c['final_review_summary'] = {f: dict(disposition=v['disposition'],
                confirmed_value=v.get('confirmed_value'), proposed_value=v.get('proposed_value'),
                application_dependency=d.get('application_hold'), policy_choice=None)
                for f, v in d['fields'].items()}
            c['final_review_reference'] = 'current_source_decisions.json'
            c['signoff'] = 'current_completed_source_reviewed'
        if i in actions:
            c['record_action'] = actions[i]
            c['requires_review'] = True
            c['primary_evidence_urls'] = list(dict.fromkeys(c.get('primary_evidence_urls', []) + actions[i].get('source_urls', [])))
    required_path = H / 'review_required.json'
    if required_path.exists():
        required = json.loads(required_path.read_text())
        by_id = {c['case_id']: c for c in required['cases']}
        for i, action in actions.items():
            c = by_id.setdefault(f'row:{i}', dict(case_id=f'row:{i}', input_row_index=i,
                                                 fields={}, status='record_action_required'))
            if i in current:
                c['fields'] = current[i]['fields']
            c['record_action'] = action
            c['application_hold'] = 'Resolve the whole-record remedy before isolated field edits.'
        required['cases'] = list(by_id.values())
        required['scope'] = 'Current field limits, coding-policy choices and whole-record remedies; no automatic dataset changes.'
        required_path.write_text(json.dumps(required, ensure_ascii=False, indent=2)+'\n')
    return actions
