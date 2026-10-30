"""Write the immutable first-batch report for Mac-source validation."""
import json
from pathlib import Path
F=Path(__file__).resolve().parent


def main():
    s=json.loads((F/'batch_01_summary.json').read_text());c=s['coverage']
    statuses=s['final_target_statuses']
    records=[json.loads(l) for l in (F/'adjudication_tasks.jsonl').read_text().splitlines()]
    reviews=json.loads((F/'adjudication_status.json').read_text())
    assert all(reviews[r['key']].get('terminal') and reviews[r['key']]['validation']=='valid' for r in records)
    lines=['# Mac source recovery: batch 1 validation','',
           f"The first Mac transfer supplied **34 independently source-reviewed full articles**. Fresh blind checking added **{s['new_verified_field_instances']} verified field instances**, including **{s['new_error_fields']} confirmed errors**, relative to the pre-Mac audit. Current totals are **{s['current_confirmed_errors']} confirmed errors across {s['current_error_rows']} effect rows**.",'',
           f"Any field is verified for **{c['any_field_checked']}/2,164 effects ({c['any_field_checked']/2164:.1%})**, compared with1,605before this pass. All seven fields are verified for **{c['fully_checked_effects']}/2,164**, compared with82before this pass. The80%goal remains unmet. Field counts include repeated original statistics across replication rows and do not estimate a representative error rate for FReD.",'',
           '## Acquisition and evidence','',
           'The Mac pass uses real Chrome, Apple Events JavaScript, and signed-in Birkbeck EBSCO/publisher access. The acquisition pass ended at10:44UTC on30October2026, within its separate11:53UTCceiling. It recovered58full articles after assessing100source groups;42assessed groups remained unresolved and137were not attempted after the active routes stopped. This report covers only private batch01. The additional24articles in batch02are entering separate blind validation; source acceptance alone establishes no audit-field verification.','',
           'All102PDF, text, and neutral-input hashes were checked on receipt. Parent checks independently verified actual PDF page counts and freshly parsed PDF title/header and reference sections, retaining the Mac’s visual identity/completeness evidence and source-version labels. Croninger etal.’s article retains an ARTICLE IN PRESS header despite its full journal pagination, so equivalence to any later revision was not assumed.','',
           'The private batch archive contains104files, including the two manifests. A direct remote content check found104matches and zero differences. All34canonical evidence-text hashes also match acceptance records, and the private cloud upload queue was empty when checked. Original Mac and box artifacts remain available; full texts are excluded from Git.','',
           '## Blind validation and independent review','',
           f"The parent filtered the transferred neutral targets against current checkpoints, retaining only still-paper_unavailable sides. **38fresh T3 Codex gpt-6.1-sol medium batches** examined **188distinct target sides**. Final checkpoint statuses are **{statuses.get('done',0)}done** and **{statuses.get('locator_insufficient',0)}locator-insufficient**. A done status can contain missing fields or a target mismatch; field verification requires the separate evidence, target, sample, metric, and bound checks.",'',
           f"**{len(records)}independent Gemini4Argon(High) calls** reviewed **{sum(len(r['items']) for r in records)}field disagreements** through the Antigravity CLI. Complete responses were collected and passed strict exact-source quotation checks. Parent quote-only repairs are recorded separately and retain the original worker output or raw review plus its hash; no numeric value, verdict, or target was changed by a quotation repair. PDF citations were mapped only to their hash-verified canonical text from the same accepted PDF.",'',
           'The nested country-panel sample-size disagreements remain unverified:12country clusters,324nominal country-years, and the usable post-lag regression sample are different quantities. Repeated neutral locators that do not distinguish accountability contrasts, conflicting study/page metadata, and missing identity-integration targets also remain unverified. Retrieval and numerical agreement did not resolve these ambiguities. Printed metrics were retained without conversions, and author-reported success was not inferred from significance.','',
           '## Confirmed changes','', '| Row index | Field | Shipped | Correction |','|---:|---|---|---|']
    for e in s['new_errors']:
        lines.append(f"| {e['audit_id']} | {e['field']} | {e['shipped'] or '(blank)'} | {e['correction']} |")
    lines += ['', 'Row indices exclude the worksheet header. Exact evidence locations, resolutions, and all newly verified field instances are in [batch_01_field_changes.csv](batch_01_field_changes.csv); machine-readable accounting is in [batch_01_summary.json](batch_01_summary.json).','',
              '## Preservation and remaining work','',
              'All416pre-Mac confirmed errors and every pre-Mac verified field verdict/correction remain intact. Existing completed sides and author verdicts were protected during integration. The original audit completion marker, run manifest/deadlines, six scope holds, and completed Linux follow-up records remain unchanged. The shipped workbook and pipeline were not edited. Workbook SHA256 remains `59545e3fc0c2979d97507097526319ec8c275aae3ac40c0d1a6d327492079e6b`.','',
              'Validation includes44regression tests (33original, seven protected-integration checks, and four quotation-gap safeguards), all2,164checkpoint schemas and export totals, exact retained evidence, baseline preservation assertions, and private content-hash verification.','',
              'Mac acquisition is complete; do not restart it. The verified batch02transfer is being deduplicated against [accepted_sources.json](accepted_sources.json), filtered to eligible still-unavailable sides, and validated through fresh blind batches. Neither historical schedule should be restarted.','']
    # Keep compact metadata spellings out of the reader-facing report.
    text='\n'.join(lines)
    for a,b in [('compared with1,605before','compared with 1,605 before'),('compared with82before','compared with 82 before'),('The80%goal','The 80% goal'),('30October2026,11:53UTC','30 October 2026, 11:53 UTC'),('batch01','batch 01'),('All102PDF','All 102 PDF'),('104files','104 files'),('104matches','104 matches'),('All34canonical','All 34 canonical'),('38fresh','38 fresh'),('188distinct','188 distinct'),('Gemini4Argon(High)','Gemini 4 Argon (High)'),('12country','12 country'),('324nominal','324 nominal'),('All416pre-Mac','All 416 pre-Mac'),('44regression','44 regression'),('33original','33 original'),('all2,164checkpoint','all 2,164 checkpoint'),('separate11:53UTCdeadline','separate 11:53 UTC deadline')]:text=text.replace(a,b)
    import re
    text=text.replace('batch 01completion','batch 01 completion')
    for a,b in [('at10:44UTC on30October2026','at 10:44 UTC on 30 October 2026'),('separate11:53UTCceiling','separate 11:53 UTC ceiling'),('recovered58full','recovered 58 full'),('assessing100source','assessing 100 source'),(';42assessed','; 42 assessed'),('and137were','and 137 were'),('additional24articles','additional 24 articles'),('batch02are','batch 02 are'),('batch02transfer','batch 02 transfer')]:text=text.replace(a,b)
    for a,b in [('of30 October','of 30 October'),('contains104 files','contains 104 files'),('found104 matches','found 104 matches'),('unverified:12 country','unverified: 12 country'),('clusters,324 nominal','clusters, 324 nominal'),('Croninger etal.','Croninger et al.')]:text=text.replace(a,b)
    text=re.sub(r'\*\*(\d+)(done|locator-insufficient)',r'**\1 \2',text)
    text=re.sub(r'\*\*(\d+)(independent|field)',r'**\1 \2',text)
    (F/'REPORT.md').write_text(text)
    print('Wrote Mac batch 1 report')


if __name__=='__main__':main()
