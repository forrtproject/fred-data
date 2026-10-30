"""Report the completed finite continuation and its protected incremental gains."""
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
    first=json.loads((F/'batch_01_summary.json').read_text())
    second=json.loads((F/'batch_02_summary.json').read_text())
    lines = ['# Mac continuation: final source validation', '',
        f"Fresh blind validation of **{s['accepted_full_article_artifacts']} additional complete primary texts** added **{s['new_verified_field_instances']} verified field instances**, including **{s['new_error_fields']} confirmed errors**, relative to the completed first Mac pass. The integrated audit now contains **{s['current_confirmed_errors']} confirmed errors across {s['current_error_rows']} rows**.", '',
        f"Any field is verified for **{c['any_field_checked']}/2,164 effects ({c['any_field_checked']/2164:.1%})**; all seven fields for **{c['fully_checked_effects']}/2,164**. The baseline was 433 errors across 335 rows, 1,625 effects with any verified field, and 89 with all seven. Repeated original statistics count as separate field instances; these results do not estimate a representative error rate for FReD.", '',
        '## Sources and scope', '',
        'The continuation retained **43 complete full texts: 41 published-article copies, one author manuscript, and one typeset article/proof**. Two primary appendix sections remain embedded with their own pagination. The 43 keys do not overlap the preceding 58 Mac sources, giving 101 Mac sources in total; 18 earlier Linux full-article groups were excluded from acquisition. Parent checks independently verified all listed transfer hashes, PDF page counts, fresh title/header and reference sections, retaining the Mac visual identity/completeness checks. All 43 final PDF/text pairs and neutral inputs were rehashed on the box. Full texts and browser/session details stay private.', '',
        'Both private batch archives and the portable mappings/receipts are verified: **760 files with zero content differences**. The authoritative final mapping SHA256 is `4cff0bd4722864f3231003ba1fe4f8cd96df8b50171cbbeea932a6c34865268f`. The original Mac artifacts remain retained.', '',
        'The Nadelhoffer source is a 31-page author manuscript rather than the 17-page typeset journal article; version differences cannot by themselves establish errors in the published coding. The Preference for Indirect Harm copy retains its typeset/proof label and production marks; equivalence to a later published revision is not assumed. The Gerber combined PDF starts with a 26-page appendix, with the 14-page main article at PDF pages 27–40. The Zhu and Ratner PDF contains a 14-page main article followed by a ten-page author Web Appendix. These sections do not count as additional complete main articles. Numerical scan/OCR evidence requires rendered target-page checks; exact canonical quotation glyphs and explicit omissions are retained.', '',
        'Acquisition ran from 12:03:33 to 12:40:14 UTC on 30 October 2026, about 37 minutes within its separate 100-minute ceiling. **All 137 groups were assessed: 43 recovered, 94 unrecovered, zero unattempted.** A 21-slide presentation and a two-page citation report were rejected. Twenty-five interrupted browser observations were invalidated and retained separately; 15 image-only end pages were checked as copy/copyright notices. No historical monitor, deadline, or completion marker was restarted or modified.', '',
        'For the Disjunction Effect article, the scan ends on printed page 309 with full concluding discussion, acknowledgments, all 11 references, and acceptance dates; PDF page 6 is solely a scanned-copy notice. The [publisher article record](https://journals.sagepub.com/doi/10.1111/j.1467-9280.1992.tb00678.x) lists 305–310, while the [issue contents](https://journals.sagepub.com/toc/pssa/3/5) starts the next article at 310. Parent visual and publisher checks support complete content, with the pagination discrepancy retained rather than asserting a corrected bibliographic range. This source-only acceptance establishes no audit statistic.', '',
        '## Blind validation and adjudication', '',
        f"**{s['validation_batches']} fresh T3 Codex gpt-6.1-sol medium batches** examined **{s['distinct_target_sides']} previously paper-unavailable sides**, ending with {statuses.get('done', 0)} done and {statuses.get('locator_insufficient', 0)} locator-insufficient checkpoints. A done checkpoint can retain missing fields or a target mismatch. Source retrieval alone establishes no verified statistic.", '',
        f"**{len(records)} independent Gemini 4 Argon (High) calls** completed **{sum(len(r['items']) for r in records)} field reviews** through the Antigravity CLI. Reviewers receive the original scientific brief, full co-field coding context, version notes, and prior findings/objections; extractors receive neutral targets and named primary sources only. Complete replies require exact source quotations. Parent quote-only repairs retain original outputs/raw replies and do not change values, targets, metrics, bounds, or verdicts.", '',
        'Unidentified tests, sample counting units, missing analytic N, incompatible metrics, and broad narrative success without a defensible individual-effect mapping remain unverified. No conversion, numerical-coincidence target matching, or significance-derived narrative success is used.', '',
        'The focused review of row 1076 verified the paper’s explicit Table 1 conceptual mapping from school maths grades to average university grades and the authors’ no-support narrative for subsequent transitions. The second-year p-value and author verdict can be checked; the requested unstandardized slope remains unverified. For row 1282, a field-specific target resolution links the supplied body-sway plot page to the preceding omnibus results page; it does not alter the sample-N target.', '',
        'For row 1396, a focused review confirms the coded across-scenario t(7) = 3.47 and one-tailed p = .0052; the same source sentence also reports a valid across-participant analysis. The intended analytic-N unit remains unresolved. For row 1990, primary condition denominators are 66, 67, and 67, but the supplied original Table 1 locator concerns another study and the vacation omnibus statistic is reconstructed only in the replication. The proposed combined N = 200 remains unverified; neither numerical agreement nor a reconstructed secondary statistic resolves that original target.', '',
        '## Gains by transfer batch', '',
        '| Batch | Full texts | Target sides | Newly verified fields | New confirmed errors |',
        '|---|---:|---:|---:|---:|',
        f"| 01 | 21 | 54 | {first['new_verified_field_instances']} | {first['new_error_fields']} |",
        f"| 02 | 22 | 22 | {second['new_verified_fields']} | {second['new_errors']} |", '',
        'The immutable first-batch report, summary, field changes and completion marker retain the first published checkpoint. Batch 02 increments are in [batch_02_summary.json](batch_02_summary.json) and [batch_02_field_changes.csv](batch_02_field_changes.csv). Cumulative findings are relative to the completed first Mac-pass commit c9f81545.', '',
        '## Confirmed changes', '', '| Row index | Field | Shipped | Correction |', '|---:|---|---|---|']
    for e in s['new_errors']:
        lines.append(f"| {e['audit_id']} | {e['field']} | {e['shipped'] or '(blank)'} | {e['correction']} |")
    if not s['new_errors']:
        lines.append('| — | No new confirmed errors | — | — |')
    lines += ['', 'Row indices exclude the worksheet header. Exact locations, reasons, and all newly verified fields are in [field_changes.csv](field_changes.csv), with machine-readable accounting in [summary.json](summary.json).', '',
        '## Preservation and checks', '',
        'All 433 pre-continuation errors and all 440 errors at the first-batch checkpoint, every previously verified verdict/correction, completed sides/author verdicts, established scope holds, historical completion/deadline records, and the first Mac pass records remain intact. The parent owns Git and exports. The shipped workbook/pipeline, main checkout, and FLoRA were not edited.', '',
        'Validation includes 44 regression tests, all 2,164 checkpoint/export checks, exact retained adjudication evidence, baseline file-hash and protected-side assertions, canonical source hashes, and private archive content checks. No paid acquisition or incremental model spend was used.', '']
    (F / 'REPORT.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
