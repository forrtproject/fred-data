#!/usr/bin/env python3
"""Turn the final reads and the lead reader's decisions into one tracked file. Quotes stay in the private reviews."""
import json
import re

import build_field_ledger as L
import validate_final_read as V

OUT = L.T / 'final_read_decisions.json'
# The lead session read every field where the blind reader called the existing value contradicted.
LEAD_DECISIONS = {
    'row:2714:outcome': ('correct', "The authors say the attrition problem compromised the test, that the jury is still out, and call the whole thing inconclusive."),
    'row:568:outcome': ('correct', "The report compares its results with the original repeatedly, so 'descriptive only' cannot hold. Some results agree and others are marked as different."),
    'row:177:original': ('correct', "The report attributes the association it re-tests to this study. The study on record is cited only as background."),
    'row:2681:outcome_computation': ('correct', "The report's tables say the re-run of the original specification matches the published results. The errors it discusses change results only once corrected."),
    'row:2049:outcome': ('correct', "The report names this study among its four successful replications. Its mixed picture describes the whole set of 20 studies."),
    'row:2667:outcome_computation': ('correct', "The report says the code is computationally reproducible, with only last-digit differences in some standard errors."),
    'row:1678:outcome': ('correct', "The replication team says it partially replicated the original results."),
    'row:1450:outcome_robustness': ('correct', "The report runs robustness checks, and all of them keep a significant effect of similar size, so 'not checked' is wrong."),
    'row:1347:outcome_computation': ('correct', "The report first checks that its re-fit recovers the original results and says it does, so 'not checked' is wrong."),
    'row:2711:outcome': ('correct', "The authors say the results are mixed: the effect was significant in one replication and not in the other."),
    'row:127:original': ('correct', "The paper says it replicates Mechling, Gast and Fields (2008), and the study on record is not in its references."),
    'row:1205:outcome': ('correct', "The original also found no engagement difference, so finding none again agrees with it. 'Failed' reads a repeated null result as a failure."),
    'row:2651:outcome_computation': ('correct', "The authors say they replicated all results using the code provided. The differing coefficient comes from their own new specification."),
    'row:1921:outcome': ('correct', "The replication team says one result replicated and the other did not."),
    'row:2445:outcome': ('correct', "The model reproduced the sorting results from form alone, and the authors' main message is that this undercuts the original's reading of them."),
    'row:67:outcome': ('correct', "The original found no decrease, and this paper finds one and calls that a stark contrast."),
    'row:1695:outcome': ('correct', "The interaction replicated, but the pattern of means did not, so the authors' own stated criterion for success was not met."),
    'row:121:outcome': ('keep_existing', "This repeats a survey five years on. Some results match and prevalence rose, but a change over time does not show the earlier result was wrong, so no value is clearly right."),
    'row:173:outcome': ('keep_existing', "This follows the same children a year later and the loss has faded. That does not make either value clearly right for the original first-grade finding."),
    'row:2170:outcome': ('keep_existing', "The paper says the main result failed to reproduce, which the existing outcome already reflects. The study type is a close call."),
    'row:2170:type': ('keep_existing', "The paper uses both words. It rebuilds the analysis from the same named sources but had no access to the original files, so 'replication' is defensible."),
    'row:195:outcome': ('keep_existing', "This depends on changing the original study, and the existing original stands."),
    'row:195:original': ('keep_existing', "The paper says it replicated the protocol of the study on record, so the existing original is defensible."),
    'row:1796:outcome': ('keep_existing', "The text we have lacks the abstract and conclusion, so an overall verdict could be missing."),
    'row:1729:outcome': ('keep_existing', "The paper's appendix labels this study unsuccessful, but the project's data file codes it as successful, and the appendix is inconsistent elsewhere. This needs checking against the project's data."),
    'row:568:original': ('keep_existing', "The paper treats the 2018 and 2021 papers together as the original, so the existing original is defensible."),
}
REFUSED_BY_OPUS = {'f0011': 'deepseek/deepseek-v4-flash'}


def build():
    mapping = json.loads((V.OUT / 'parent_map.json').read_text())['requests']
    out = V.main()
    assert not out['failures'] and not out['missing'], (out['failures'], out['missing'])
    decisions = {}
    for request_id, result in out['results'].items():
        entry = mapping[request_id]
        if entry['kind'] != 'record':
            continue
        review = json.loads((V.OUT / request_id / 'review.json').read_text())
        for field in entry['fields']:
            field_id = f"row:{entry['row']}:{field}"
            answer = next(a for a in review['fields'] if a['field'] == field)
            proposed = answer['better'] == entry['proposed_letter'][field]
            contradicted = proposed and answer['other_value'] == 'contradicted'
            if field_id in LEAD_DECISIONS:
                verdict, reason = LEAD_DECISIONS[field_id]
                decided_by = 'lead_read'
            else:
                assert not contradicted or request_id in REFUSED_BY_OPUS, field_id
                verdict, decided_by = 'keep_existing', 'final_read_rule'
                reason = "A final read, which did not say which value was in FLoRA, found the existing value defensible, so it stays." if proposed else "A final read, which did not say which value was in FLoRA, preferred the existing value."
            if request_id in REFUSED_BY_OPUS:
                reason = "Claude's safeguards stopped this paper, so DeepSeek V4 Flash read it. It found the existing value defensible, so it stays."
            decisions[field_id] = dict(verdict=verdict, reason=reason, decided_by=decided_by, request_id=request_id, sampled=False,
                                       reader=REFUSED_BY_OPUS.get(request_id, 'claude-opus-5-5'), reader_preferred='proposed' if proposed else 'existing',
                                       reader_called_existing=answer['other_value'], reader_confidence=answer['confidence'])
    assert set(LEAD_DECISIONS) <= set(decisions), set(LEAD_DECISIONS) - set(decisions)
    checks = {str(r['row']): r['verdicts'] for r in out['results'].values() if r['kind'] == 'check'}
    data = dict(schema_version=1, date='2026-11-04',
                how_decided="Lukas Wallrich asked the lead session to read the values the blind reader called contradicted and decide, in place of the predeclared confidence rule and the 12 second reads. Everything else keeps its existing value.",
                reviews=decisions, known_answer_checks=checks,
                earlier_reads_kept_as_corrections=[1927, 1537, 577, 2655])
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    return data


if __name__ == '__main__':
    built = build()
    verdicts = [r['verdict'] for r in built['reviews'].values()]
    print(len(verdicts), verdicts.count('correct'), verdicts.count('keep_existing'))
