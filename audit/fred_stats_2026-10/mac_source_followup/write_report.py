"""Write the cumulative Mac recovery report; retain immutable batch snapshots."""
import json
from pathlib import Path
F = Path(__file__).resolve().parent


def main():
    s = json.loads((F / 'summary.json').read_text())
    first = json.loads((F / 'batch_01_summary.json').read_text())
    c = s['coverage']
    records = [json.loads(line) for line in (F / 'adjudication_tasks.jsonl').read_text().splitlines()]
    reviews = json.loads((F / 'adjudication_status.json').read_text())
    assert all(reviews[r['key']].get('terminal') and reviews[r['key']]['validation'] == 'valid' for r in records)
    status = s['final_target_statuses']
    queue = json.loads((F / 'validation_queue.json').read_text())
    second_batches = sum(q['batch'].startswith('mac02_') for q in queue)
    lines = [
        '# Mac source recovery and targeted validation', '',
        f"The Mac pass recovered **58 full articles**. Fresh blind validation added **{s['new_verified_field_instances']} verified field instances**, including **{s['new_error_fields']} confirmed errors**, relative to the pre-Mac audit. The integrated audit now contains **{s['current_confirmed_errors']} confirmed errors across {s['current_error_rows']} effect rows**.", '',
        f"Any field is verified for **{c['any_field_checked']}/2,164 effects ({c['any_field_checked']/2164:.1%})**, compared with 1,605 before the Mac pass. All seven fields are verified for **{c['fully_checked_effects']}/2,164**, compared with 82 before this pass. The 80% verification goal remains unmet. Repeated original statistics across replication rows count as separate field instances; these results do not estimate a representative error rate for FReD.", '',
        '## Acquisition and private evidence', '',
        'The separately authorised Mac pass used real Chrome, Apple Events JavaScript, and signed-in Birkbeck EBSCO/publisher access. Acquisition stopped at 10:44 UTC on 30 October 2026, within its 11:53 UTC ceiling. It assessed 100 source groups: 58 yielded full articles and 42 remained unresolved. Another 137 groups were not attempted after the finite routes stopped. The pass skipped 18 full-article groups recovered earlier on Linux. One incomplete preview was rejected and six stale browser-DOM route observations were marked invalid. No paid API or model spend was incurred.', '',
        'Parent checks independently verified PDF page counts, freshly parsed title/header and reference sections, and exact transferred PDF/text/neutral-input hashes, retaining the Mac visual identity/completeness evidence. The Croninger article retains an ARTICLE IN PRESS header despite full journal pagination; equivalence to a later revision was not assumed. Source acceptance alone establishes no audit-field verification.', '',
        'The private archives contain **394 files**: 104 in batch 01 and 290 in batch 02. Direct remote content checks found zero differences. All 58 canonical evidence-text hashes match accepted-source records. Original Mac and box artifacts remain available. Full texts are excluded from Git.', '',
        '## Blind checks and independent review', '',
        f"**{len(queue)} fresh T3 Codex gpt-6.1-sol medium batches** examined **212 distinct previously paper-unavailable target sides**, with {s['validation_side_attempts']} side attempts including one target-selection recheck. Checkpoints ended with **{status.get('done', 0)} done** and **{status.get('locator_insufficient', 0)} locator-insufficient** sides. A done checkpoint can retain missing fields or a target mismatch; field verification separately requires matching evidence, target, analytic sample, metric, and p-value bound.", '',
        f"**{len(records)} independent Gemini 4 Argon (High) calls** completed **{sum(len(r['items']) for r in records)} field reviews** through the Antigravity CLI. Complete replies were collected and passed strict exact-source quotation checks. Evidence-only repairs retain original worker outputs or hash-bound raw replies. They preserve numerical values, metrics, targets, bounds, and verdicts. Exact PDF citations were mapped only to canonical text from the same hash-verified PDF.", '',
        'Unresolved country-panel sample sizes remain unverified: 12 country clusters, 324 nominal country-years, and usable post-lag regression observations are different quantities. Neutral locators that cannot distinguish study/outcome contrasts remain unresolved. Retrieval and numerical agreement did not establish target identity. Printed metrics were retained without conversions, and author-reported success was not inferred from significance.', '',
        '## Gains by transfer batch', '',
        '| Transfer | Full articles | Target sides | Newly verified fields | New confirmed errors |',
        '|---|---:|---:|---:|---:|',
        f"| Batch 01 | 34 | 188 | {first['new_verified_field_instances']} | {first['new_error_fields']} |",
        f"| Batch 02 | 24 | 24 | {s['new_verified_field_instances']-first['new_verified_field_instances']} | {s['new_error_fields']-first['new_error_fields']} |", '',
        'The immutable [batch 01 report](batch_01_REPORT.md), [summary](batch_01_summary.json), and [field changes](batch_01_field_changes.csv) retain the first published checkpoint. Cumulative accounting is in [summary.json](summary.json) and [field_changes.csv](field_changes.csv); the incremental batch 02 files are [batch_02_summary.json](batch_02_summary.json) and [batch_02_field_changes.csv](batch_02_field_changes.csv).', '',
        'The final cross-field check found that row 1961’s initial blind extraction selected a paired comparison rather than the coded heart-attack MANOVA. A fresh neutral primary-context extraction and a new independent review addressed that objection. The original output and superseded proposal remain retained; recruitment counts and condition sizes are not automatically analytic N.', '',
        '## Confirmed changes', '',
        '| Row index | Field | Shipped | Correction |',
        '|---:|---|---|---|',
    ]
    for e in s['new_errors']:
        lines.append(f"| {e['audit_id']} | {e['field']} | {e['shipped'] or '(blank)'} | {e['correction']} |")
    lines += ['',
        'Row indices exclude the worksheet header. Exact evidence locations, resolutions, and all newly verified fields are retained in the cumulative field-change export and canonical checkpoints.', '',
        '## Preservation and checks', '',
        'All 416 pre-Mac confirmed errors and every pre-Mac verified verdict/correction remain intact. Existing completed sides and author verdicts were protected during integration. The original completion marker, run manifest/deadlines, six scope holds, and completed Linux follow-up records remain unchanged. The shipped workbook and pipeline were not edited. Workbook SHA256 remains `59545e3fc0c2979d97507097526319ec8c275aae3ac40c0d1a6d327492079e6b`.', '',
        'Checks cover 44 regression tests, all 2,164 checkpoint schemas and export totals, exact retained adjudication evidence, baseline preservation assertions, transfer hashes, and private archive content. Acquisition and validation are complete. Historical schedules remain disabled; no deadline was restarted or extended.', '']
    (F / 'REPORT.md').write_text('\n'.join(lines))
    print('Wrote cumulative Mac recovery report')


if __name__ == '__main__':
    main()
