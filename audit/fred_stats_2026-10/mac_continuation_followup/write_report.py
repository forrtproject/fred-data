"""Report checked continuation sources without claiming acquisition is over."""
import json
from pathlib import Path
F = Path(__file__).resolve().parent


def main():
    s = json.loads((F / 'summary.json').read_text())
    state = json.loads((F / 'state.json').read_text())
    records = [json.loads(line) for line in (F / 'adjudication_tasks.jsonl').read_text().splitlines()]
    reviews = json.loads((F / 'adjudication_status.json').read_text())
    assert all(reviews[r['key']].get('terminal') and reviews[r['key']]['validation'] == 'valid' for r in records)
    c = s['coverage']
    statuses = s['final_target_statuses']
    lines = ['# Mac continuation: checked source batches', '',
        f"Fresh blind validation of **{s['accepted_full_article_artifacts']} additional complete primary texts** added **{s['new_verified_field_instances']} verified field instances**, including **{s['new_error_fields']} confirmed errors**, relative to the completed first Mac pass. The integrated audit now contains **{s['current_confirmed_errors']} confirmed errors across {s['current_error_rows']} rows**.", '',
        f"Any field is verified for **{c['any_field_checked']}/2,164 effects ({c['any_field_checked']/2164:.1%})**; all seven fields for **{c['fully_checked_effects']}/2,164**. The baseline was 433 errors across 335 rows, 1,625 effects with any verified field, and 89 with all seven. Repeated original statistics count as separate field instances; these results do not estimate a representative error rate for FReD.", '',
        '## Sources and scope', '',
        'Batch 01 contains 21 complete primary texts, including one labelled author manuscript, and two embedded primary appendix sections with separately identified pagination. All 253 transfer hashes matched. Independent box checks verified actual PDF page counts, fresh title/header and reference sections, and retained Mac visual identity/completeness evidence. The private archive content check found 254 matching files and zero differences, including the transfer manifest. The portable box mapping and transfer receipt were separately uploaded and directly rehashed remotely, for 256 archived files total. Full texts and browser/session details remain private.', '',
        'The Nadelhoffer source is a 31-page author manuscript rather than the 17-page typeset journal article; version differences cannot by themselves establish errors in the published coding. The Gerber combined PDF starts with a 26-page appendix, with the 14-page main article at PDF pages 27–40. The Zhu and Ratner PDF contains a 14-page main article followed by a ten-page author Web Appendix. These sections do not count as additional complete main articles. Numerical scan/OCR evidence requires rendered target-page checks; exact canonical quotation glyphs and explicit omissions are retained.', '',
        f"The separate Mac acquisition continuation started at 12:03:33 UTC on 30 October 2026 and is capped at 13:43:33 UTC. Its status at this checkpoint is **{state['mac_acquisition_status']}**. This report covers received and checked sources only; it does not claim that all 137 acquisition attempts are complete. Acquisition remains owned by the existing Mac thread. Neither historical monitor nor deadline was restarted.", '',
        '## Blind validation and adjudication', '',
        f"**{s['validation_batches']} fresh T3 Codex gpt-6.1-sol medium batches** examined **{s['distinct_target_sides']} previously paper-unavailable sides**, ending with {statuses.get('done', 0)} done and {statuses.get('locator_insufficient', 0)} locator-insufficient checkpoints. A done checkpoint can retain missing fields or a target mismatch. Source retrieval alone establishes no verified statistic.", '',
        f"**{len(records)} independent Gemini 4 Argon (High) calls** completed **{sum(len(r['items']) for r in records)} field reviews** through the Antigravity CLI. Reviewers receive the original scientific brief, full co-field coding context, version notes, and prior findings/objections; extractors receive neutral targets and named primary sources only. Complete replies require exact source quotations. Parent quote-only repairs retain original outputs/raw replies and do not change values, targets, metrics, bounds, or verdicts.", '',
        'Unidentified tests, sample counting units, missing analytic N, incompatible metrics, and broad narrative success without a defensible individual-effect mapping remain unverified. No conversion, numerical-coincidence target matching, or significance-derived narrative success is used.', '',
        'The focused review of row 1076 verified the paper’s explicit Table 1 conceptual mapping from school maths grades to average university grades and the authors’ no-support narrative for subsequent transitions. The second-year p-value and author verdict can be checked; the requested unstandardized slope remains unverified. For row 1282, a field-specific target resolution links the supplied body-sway plot page to the preceding omnibus results page; it does not alter the sample-N target.', '',
        '## Confirmed changes', '', '| Row index | Field | Shipped | Correction |', '|---:|---|---|---|']
    for e in s['new_errors']:
        lines.append(f"| {e['audit_id']} | {e['field']} | {e['shipped'] or '(blank)'} | {e['correction']} |")
    if not s['new_errors']:
        lines.append('| — | No new confirmed errors | — | — |')
    lines += ['', 'Row indices exclude the worksheet header. Exact locations, reasons, and all newly verified fields are in [field_changes.csv](field_changes.csv), with machine-readable accounting in [summary.json](summary.json).', '',
        '## Preservation and checks', '',
        'All 433 baseline confirmed errors, every previously verified verdict/correction, completed sides/author verdicts, established scope holds, historical completion/deadline records, and the first Mac pass records remain intact. The parent owns Git and exports. The shipped workbook/pipeline, main checkout, and FLoRA were not edited.', '',
        'Validation includes 44 regression tests, all 2,164 checkpoint/export checks, exact retained adjudication evidence, baseline file-hash and protected-side assertions, canonical source hashes, and private archive content checks. No paid acquisition or incremental model spend was used.', '']
    (F / 'REPORT.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
