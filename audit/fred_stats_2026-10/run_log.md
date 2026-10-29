# FReD statistics audit run log

Launch: 2026-10-29T09:20:09.891260+00:00. Deadlines UTC: {"extraction": "2026-10-29T17:20:09.891260+00:00", "adjudication": "2026-10-29T18:50:09.891260+00:00", "finish": "2026-10-29T19:20:09.891260+00:00"}.

- Read full brief, repository guidelines and codebook. Worktree branch verified. No pipeline or data edits authorised.
- Workbook dimensions reset; asserted 2,164 effects and required columns. Grouped into 432 works; 197 rows lack replication DOI.
- Preserve cell strings and number formats where available; XLSX display/storage may already have lost precision as printed in papers.
- Sanitiser children receive only effect_id and description; extraction children receive only prepared blind inputs.
- Text is active processing on SSD; completed bulky text will be archived to verified cloud mount. No text committed.
- Launch uses three sanitiser children, then pilots; ramp ceiling gradually to ten in first half hour.

- First 20 sanitised records manually inspected before extraction. Neutral constructs retained; effect 20 is description-insufficient but page/table/study locators may rescue identification. Sanitiser flags are not automatic terminal exclusions.

```json
[
  {
    "effect_id": 1,
    "description": "Relationship between the Gender Empowerment Measure and gender differences in emphasis on a potential spouse's earning capacity (ranking data).",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 2,
    "description": "Perceptions of outcomes above versus below a reference point when outcomes are evaluated relative to goals (part 1 of Problem 1).",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 3,
    "description": "Share of the enriched alternative in Problem 1.",
    "locator_insufficient": false,
    "inspection_note": "Removed the observed numerical result; retained the alternative, share outcome, and identifying problem number."
  },
  {
    "effect_id": 4,
    "description": "Relationship between the Gender Empowerment Measure and gender differences in emphasis on a potential spouse's domestic skills (ranking data).",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 5,
    "description": "Perceptions of outcomes above versus below a reference point when outcomes are evaluated relative to goals (part 2 of Problem 1).",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 6,
    "description": "Choice of the enriched alternative under choose-to-award versus deny instructions in Problem 1.",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 7,
    "description": "Satisfaction when an outcome falls short of a specific goal versus when no specific goal is present.",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 8,
    "description": "Share of the enriched alternative in Problem 2.",
    "locator_insufficient": false,
    "inspection_note": "Removed the observed numerical result; retained the alternative, share outcome, and identifying problem number."
  },
  {
    "effect_id": 9,
    "description": "Relationship between the Gender Empowerment Measure and men's emphasis on a mate's physical attractiveness (ranking data).",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 10,
    "description": "Emotion associated with a loss versus a gain of the same magnitude.",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 11,
    "description": "Choice of the enriched alternative under choose versus cancel instructions in Problem 2.",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 12,
    "description": "Reported shame in explicit public versus implicit public conditions.",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 13,
    "description": "Expected effort to perform an additional unit of work when below versus above a goal.",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 14,
    "description": "Share of the enriched alternative in Problem 3.",
    "locator_insufficient": false,
    "inspection_note": "Removed the observed numerical result; retained the alternative, share outcome, and identifying problem number."
  },
  {
    "effect_id": 15,
    "description": "Shame under low versus high moral beliefs conditions.",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 16,
    "description": "Relationship between the Gender-Related Development Index and gender differences in emphasis on a potential spouse's earning capacity (ranking data).",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 17,
    "description": "Effort to produce the same amount of work when falling behind a goal versus having surpassed a goal.",
    "locator_insufficient": false,
    "inspection_note": "Removed the observed effort ratio and result direction; retained the comparison and equal-work condition."
  },
  {
    "effect_id": 18,
    "description": "The two conditions of the experiment involve ascribing knowledge of the very same proposition (\"rather than\" clause) and they differ only in that they pick out two different contrasts to that proposition: subject or object.",
    "locator_insufficient": false,
    "inspection_note": "Inspected: no observed results, statistical estimates, analytic sample sizes, directional relationship claims, or success verdicts to remove."
  },
  {
    "effect_id": 19,
    "description": "Choice of the enriched alternative under choosing courses to take versus postponing courses in Problem 3.",
    "locator_insufficient": false,
    "inspection_note": "Recast the claim as a neutral relationship; retained constructs and conditions."
  },
  {
    "effect_id": 20,
    "description": "Relationship involving public exposure under high and low moral beliefs conditions.",
    "locator_insufficient": true,
    "inspection_note": "Removed the assertion that an effect was present in both conditions. The outcome is not specified in this description."
  }
]
```

- Part A completed on 2,164 rows: 175 effects flagged. Codebook provides examples rather than an exhaustive es_type enumeration, so es_type check records not_enumerated_in_codebook instead of declaring unfamiliar valid labels errors. Pearson screen uses coded analytic n only with nested=no; tails absent assumes two and is explicitly labelled. No project success rule yet established, so no significance-based success flags.

- First extraction pilots launched before 09:24 UTC, within the 20-minute setup ceiling. Cache-only scan completed: 52 full-text hits across 1,103 unique original/replication DOIs; cache misses were not marked terminal.
- Obvious resolution audit 381 pval_value_o: decimal transcription slip (.84 versus printed .084), p.1754 Study 1 interaction. Saved evidence in obvious_resolutions.json.
- Other early disagreements include pilot versus final sample roles and potential different tests; none are automatically counted as errors. Route to Argon.
- Later sanitisation spot-checks: first/middle/last of batches 01–06 inspected; construct and design numbers retained (including RT condition fractions); no statistical-value leak seen in those checks. 1,400 records ready at 09:31 UTC.
- Large-project pilot independently acquired authors' processed_data.csv. Clarified that explicitly supplied d/p values in a primary author table can be extracted as author-derived values; prohibition is on extractor conversions, not on reading authors' tables. Preserve distinction between linked pilots and final project-table samples.

- Argon validated nine initial disagreements with source-verified quotes: original audit379 p=.01 was correct (blind extraction used a different policy test). For audit380–385 replication target, parent inspected shipped p/statistic and explicit RPubs locator: they refer to the pilot, while the aggregate project table refers to final data. Argon confirms locator-specific pilot target; recorded target overrides without altering blind checkpoints. n=64 is trait observations, whereas pilot participants=4. Source role distinction retained.
- Every still-mismatched target remains unverified even if an adjudication suggests a corrected value; no mismatch enters the error count until target identity is independently resolved.

- All 2,164 descriptions sanitised; first/middle/last records of batches07–10 inspected (including empty/missing descriptions, which remain identification issues rather than guessed targets). Final queue has494 disjoint work slices across432 works.
- Obvious target mismatches: audit201 original lacks the named low-calorie condition; audit1273 located hypothetical-regret rather than lifetime-regret tests. All fields remain unverified, never errors. Audit379 effect also comes from the policy-composite test rather than locator Note1; prior validated Argon evidence establishes shipped t=2.61 is correct.
- Validation checkpoint before first commit: nine tests pass (rounding, strict p-bound endpoints, recognised tests, tails, no d/total-n inference, metric aliases without conversion, sign differences, statistic df mismatches, failure schemas, effect keys and ordered exports). All six audited numeric source columns store strings or blanks in XLSX; imported strings preserve available precision. Dataset SHA256 still equals frozen input. Initial setup checkpoint is committed early to protect the unattended run; subsequent commits will be roughly hourly.
