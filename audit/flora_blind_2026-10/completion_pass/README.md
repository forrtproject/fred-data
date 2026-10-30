# Completion pass: source-checked omissions and explicit deferrals

The requested completion pass is closed. The 102-request Argon continuation was already fully reviewed and integrated: 73 fields confirmed errors, 18 confirmed shipped values, and 11 remained unverified. This final pass adds six source-checked omitted targets. The audit now records 401 confirmed-error input rows, 2,061 fully resolved rows, and 113 confirmed omitted targets. The dataset corrections remain proposals.

## Decisions to review

Six obvious paper-level omissions enter the audit after parent inspection of the primary text, original reference identity, and shipped pairs. Their replication outcomes remain unadjudicated. Luna supplied triage; the parent made each accepted decision. No additional Argon calls or paid API requests were made.

The wider omission queue is deferred as the user permitted if cheap Luna triage was insufficient. The pilot took 300 reported worker-seconds across three parallel tasks, but parent checking was necessary: all nine quotations were literal, while one background classification contradicted an explicit replication result. Three cases still require publication-level scope or deduplication. The convenience pilot cannot estimate precision or recall for the full queue.

Main field verdicts and rate denominators retain their original shipped-type definitions. The separate field disposition table flags fields that become inapplicable if an accepted row-removal or type correction is applied. These conditional dispositions do not convert unverified fields into correct or resolved fields.

## Pilot decisions

| Candidate original | Parent decision | Source basis |
|---|---|---|
| Coleman et al. (1966), educational opportunity | Confirmed omission | Results explicitly replicate the Coleman Report ICCs, separately from the shipped Bryk and Raudenbush original. Luna's background classification was overturned. |
| Strand and Eldevik (2018), synthesised analysis and treatment | Confirmed omission | Independent treatment results explicitly replicate the prior EIBI study; the shipped original is Hanley et al. (2014). |
| Le Pelley et al. (2015), reward-related attentional capture | Confirmed omission | Results explicitly reproduce the trial-wise effect, separately from the shipped Watson et al. (2019) target. |
| Moodie (2023), ELT commitment | Confirmed omission | Hypothesis 6 retests the qualification-related commitment finding; the shipped original is McInerney et al. (2015). |
| Lanovaz and Hranchuk (2021), machine learning and visual inspection | Confirmed omission | A stated secondary replication uses new clinical data, separately from the shipped Wolfe et al. (2018) comparison. |
| Miyake et al. (2012), the 775 CE radiocarbon increase | Confirmed omission | New measurements directly retest the 775 CE increase, separately from the shipped Brehm 1052 CE comparison. |
| Ebbinghaus (1885) | Deferred | The 1880 manuscript and 1885 book may report the same experiment. Separate citations do not alone settle the target unit. |
| Maticka-Tyndale et al. (2010), HIV intervention follow-up | Deferred | An earlier Argon decision raises a same-study follow-up objection. Luna did not resolve that objection. |
| Han et al. (2021), ENIGMA brain age | Deferred | Crossref identifies the shipped 2018 DOI as an ENIGMA MDD brain-age report by Schmaal, Han, and Dinga. It may be a preliminary report of the same original work. |

[parent_inspection.json](parent_inspection.json) retains all nine Luna classifications and source quotations, the parent's reasons, and the six authoritative decisions. [crossref_identity_checks.json](crossref_identity_checks.json) records the two supplementary metadata checks. Raw pilot responses and task metadata remain in [luna](luna/).

## Deferred evidence work

[candidate_dispositions.csv](candidate_dispositions.csv) enumerates all 603 remaining unverified candidates. Three received parent inspection in this pilot; 600 were not individually reviewed in this pass. None is labelled an error or excluded merely from Luna's output or an absent search result.

[field_dispositions.csv](field_dispositions.csv) accounts for all 1,677 fields still unverified under shipped-type scope: 31 are conditionally inapplicable, 170 need usable source or identity evidence, 683 need more than the available abstract/partial evidence, and 793 need further source review. These are administrative completion dispositions, not new scientific verdicts.

Two large collections account for 149 unresolved input rows: the 140-row work at DOI 10.1098/rsos.231240 has about 1.9 million source characters, and the 93-row work at DOI 10.1126/science.aac4716 has about 2.2 million. Earlier review attempts timed out or truncated; 25 complete field objects from the first were already recovered. No unchanged request was repeated and no attempt history was reset. A renewed pass would need a bounded, target-level extraction and review design; it was deferred at closure.

Finishing every substantive field would additionally require the missing primary sources and original-specific results described in [COMPLETION_PLAN.md](../COMPLETION_PLAN.md), including the 11 fields left open by Argon. Exhausting the authorised review does not establish that an inaccessible or ambiguous finding is correct, wrong, or absent.

All three Luna tasks are terminal. No review processes or owned audit schedules remain active; the two original audit schedules remain removed. The main checkout, FReD work, shipped FLoRA file, and pipelines were not changed. See [verification.json](verification.json) and [state.json](state.json) for counts, hashes, and task accounting.
