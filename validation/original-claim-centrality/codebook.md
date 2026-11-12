# Validation codebook

These fields describe LLM-coded, unvalidated research artifacts. They are not production FReD columns. Every effect-level file joins on the permanent `effect_uid`; row position never identifies an effect. Blank CSV cells represent missing or withheld values, not zero.

## classifications.csv

| Field | Meaning |
|---|---|
| `effect_uid` | Permanent FReD effect identifier. |
| `classification` | `central`: failure of this claim would materially change a main substantive conclusion of the original article, including a mechanism or boundary condition. `not_central`: failure would remove only subsidiary support. `unclear`: the claim is identified but its centrality is substantively uncertain (0 rows). Empty: claim identity or source access prevented coding (100 rows). Empty and `unclear` are not intermediate levels of centrality. Several claims from one article may be central. |
| `status` | `assessed` accompanies `central` or `not_central`; `substantive_uncertainty` accompanies `unclear` (unused). Empty classifications have `claim_ambiguous` (no unique substantive target or incompatible prose/statistics), `claim_not_located`, `full_text_unavailable`, or `original_only_source_restriction`. The last status means the assigned source or claim requires replication evidence excluded by the original-only task; fe05438 has this status. |
| `identified_claim` | Coder's description of the substantive claim, or the unresolved identification problem. It does not replace the source claim text. |
| `rationale` | Brief reasoning for the centrality decision or reason no decision was possible. |
| `claim_locator` | Location of the claim in the original article, or an explicit access/identification limitation. |
| `argument_locator` | Location of the framing or conclusions used to assess the claim's place in the original argument. |
| `doi_o` | Original-source grouping key joining `sources.source_key`. Some keys are literal identifiers rather than verified DOIs. |
| `numerical_matching_limitation` | Unmatched numbers or other limitations in identifying the statistical contrast. These are notes, not verified data errors or numerical corrections. |
| `source_text_sha256` | SHA-256 of the actual extracted text read; equals `sources.text_sha256` for the source key. Empty when no full text was available. |
| `model`, `reasoning_effort`, `coding_date` | Centrality coder model, requested/observed reasoning setting and ISO coding date. Runtime and billing visibility caveats are in `summary.json`. |
| `independent_identity_status` | Corresponding `identity-checks.decision`, or `not_in_completed_identity_check` when no completed comparison exists for this row. It is not centrality agreement. |
| `review_action` | `retained_Sol_record`: final Sol classification retained. `empty_Sol_record_retained`: unresolved Sol record retained. `withheld_after_independent_identity_comparison`: an earlier nonempty Sol classification is withheld because the comparison left incompatible targets. |

## identity-checks.csv

| Field | Meaning |
|---|---|
| `effect_uid` | Permanent identifier joining classifications. |
| `decision` | `same_substantive_target`: compatible independent identities. `same_substantive_target_after_blind_recode`: compatible after a fresh blind Sol reread. Only these two are counted as compatible (324). `unresolved`: no settled common target. `unresolved_coder_difference`: coders differ on target or identifiability. `claim_not_located`: the target was not located. `source_identity_unresolved`: the supplied source/version could not be settled. `full_text_unavailable`: the original full text was unavailable. |
| `reason` | Integration rationale for the comparison result, including unresolved alternatives. |
| `sol_locator`, `opus_locator` | Each coder's source locator or explicit identification/access limitation. |
| `text_sha256` | Actual text hash; equals the classification row's `source_text_sha256`. |

## claim-review.csv

| Field | Meaning |
|---|---|
| `effect_uid` | Permanent identifier joining classifications. |
| `review_role` | `fill_missing_claim`: propose the excerpt for an empty source claim. `append_identification`: retain the full current text, then a blank line and the excerpt to identify missing target/context. `evidence_only`: supporting evidence, with no claim-text change proposed. No proposal is automatically applied. |
| `reason` | Why the excerpt has this review role. |
| `current_claim_text` | Existing source claim wording, unchanged. |
| `source_quote` | Source wording or a faithful labelled table excerpt. Selected table cells retain their labels without a generic notice that other rows/columns are omitted. Omissions within prose are marked. |
| `quote_type` | `direct_quotation`, `table_excerpt`, or `direct_quotation_with_table_excerpt`. These describe format, not validation status. |
| `source_key` | Joins `sources.source_key` and the classification's `doi_o`. |
| `source_locator` | Exact original-article location of the excerpt. |
| `recorded_statistic` | Frozen input statistics provided for identification; unchanged and not audited here. |
| `numerical_matching_limitation` | Matching caveat; does not assert a verified data error. |
| `source_text_sha256` | Hash of the actual text read, matching `sources.text_sha256`. |
| `status` | Explicitly LLM-coded, unvalidated, requiring human review and not applied. |

## sources.csv and pilot-sample.csv

| File / field | Meaning |
|---|---|
| sources: `source_key` | Original-reference grouping key used by the effect-level files. |
| sources: `reference` | Supplied bibliographic reference. |
| sources: `source_url`, `provided_link` | Retrieval URL and supplied source-sheet link. A link does not establish source identity on its own. |
| sources: `source_sha256`, `text_sha256` | Hashes of actual PDF/source bytes and extracted text read. Both are empty for the unavailable original. Full files remain private. |
| pilot-sample: `effect_uid` | Historical 50-row random pilot sample in frozen draw order, seed 20261111. It is not a new draw from the full-run frame. |

`provenance.json` records source, code and overlay versions; `summary.json` records counts, model provenance and artifact hashes. Frozen prompts and detailed private logs are identified by the README and archive manifest.
