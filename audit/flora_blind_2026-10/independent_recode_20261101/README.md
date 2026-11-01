# Independent recoding of proposed corrections

Current scope: 562 proposed fields across 515 existing rows, covering 469 works. This is a full-cohort reassessment of proposed changes. Missing-pair additions remain a separate evidence stream; a coder omitting a target is not evidence to remove a row.

Current checkpoint: 132 of 677 initial source packets and five additional source views have
passed Opus schema, literal-span and reading checks; fifteen fresh Sol source views
pass the same checks. One layout view is withheld because its quotes interleave
PDF columns; the reading-order replacement has completed both final blind attempts.
The full reassessment remains in progress. Seventeen cases covering nineteen proposed
fields have passed the scientific acceptance gates and are exported in
`automatically_verified_proposals.json`. These are proposals for batch approval;
no user approval or dataset changes are recorded. Other outcome batches remain
suspended.

Two suspected outcome corrections are withdrawn in `withdrawn_proposals.json` after
source adjudication. Their blind disagreements remain visible; these are not labelled
two-model agreement. The finite 60-item source-completeness recovery pass reuses
old attempts and seeks full primary reports. Its preparer never becomes a blind coder.
The first acquisition pass recovered one verified full report. It has completed
both fresh blind roles and primary adjudication. Its simulation classification and low-confidence outcome remain outside automatic acceptance. The
bounded second pass checked saved HTML and new search routes using unused budgets.
Its HTML candidate was rejected as an abstract/reference access page; 59 source
completeness gaps remain. Seven zero-new-request cases had earlier acquisition
records, rather than missing DOI identifiers.
Rate limits remain access limits, not findings about whether a report exists.

Fresh Claude Opus 5.5 children receive only opaque document packets, the codebook, schema and primary-source metadata. They receive no dataset values, proposed fixes, earlier codings, reviewer opinions, or task-selection rationale. They must code the whole document and find its targets independently, with literal source evidence and complete reading coverage. Existing reviewers and technical source preparers never become blind coders.

The parent owns source verification, target alignment, comparison, scientific integration, Git and dispatch. A previous genuine blind Sol result can be compared only when its exact source version/hash and source scope match. Otherwise a fresh blinded Sol pass is required. No prior adjudicator judgment is substituted for independent blind coding.

## Automatic acceptance gates

Agreement is a candidate, not a correctness certificate. A correction enters a proposed automatic fix file only after:

- The primary source identity, report version, completeness and applicable study status are established. Abstract-only or unverified sources cannot establish this high-confidence set.
- Both blind results pass schema, exact metadata/hash, literal contiguous quotation and model-visible reading-coverage checks.
- The same original and retested findings are positively aligned. A shared DOI/year, an omitted target, or a generic whole-paper statement does not establish that alignment.
- The coded value agrees and the evidence identifies the original claim, the corresponding current result, and the authors' comparison/verdict. Attempt language is not outcome evidence; no finding or exception is transferred across originals.
- An independent adversarial source check addresses contrary passages and claim-selection/report-binding issues. This reviewer may see the proposed comparison but must never be reused as a blind coder.
- All dependent fields, record remedies, quotations and duplicate constraints are coherent. Frozen baseline and full-record preconditions remain intact.

Agreement with the existing FLoRA value withdraws the suspected correction when these gates pass. Disagreements go to an automated source-adjudication queue. Unsupported cases stay out of the automatic file; they are not relabelled resolved. Only a genuinely unspecified coding-policy choice requires the user's decision. Existing scientific records and objections remain preserved.

## Continuation

Read state.json and source_inventory.json/dispatch_plan.json when preparation finishes. Reconcile exact owned task IDs. Completion notifications drive integration and the next bounded delegate_task round; no polling/watch loops or schedules. Never restart historical tick.js, tick_evidence_followup.js, coding controllers or their old deadlines for this new cohort. Use a new delegate_task for every blind/review round, not t3_thread_send. Maximum two attempts per packet, preserving every attempt and mechanical failure cause. Keep combined active lanes below ten and reserve validation capacity; currently use at most three model children. Included native usage only, no paid API fallback. The old recovery schedule remains removed.

Active packets and outputs are ignored under evidence_followup/private/independent_recode_20261101/. No source bodies or unpublished coding outputs are deployed to the public app. The suspended outcome batch approvals remain suspended until the acceptance gates are satisfied.

Parent mechanical checks are in `validate_output.py`. Recover the child's actual
durable tool items into a private receipt directory before running it; a child's
reading-manifest assertion is insufficient. Both exact shell output and native
Read content are checked against every source chunk. The validator records
mechanical validity separately from scientific acceptance. Run its failure
controls with:

```sh
python3 -m unittest discover -s audit/flora_blind_2026-10/independent_recode_20261101 -p test_validation.py -v
```

`project_prior_sol.py` creates a separate parent-only projection when an older
blind result transcribed source whitespace. It can replace only whitespace with
the exact, uniquely matched contiguous source span; missing or changed words and
ambiguous matches are rejected. Original files and scientific labels remain
unchanged. The projection ledger preserves both quotations and offsets. Reading
receipts and independent scientific checks are still required.

Use `comparison_review_queue.json` and `prior_sol_receipt_checks.json` for the next
comparison/review round. Complete available comparisons as well as dispatching
new blind groups; do not let an agreement queue substitute for source review.
Documents_0002, _0004 and _0005 have passed source review and parent integration
for their specified type/outcome fields. Document_0007 retains a low-confidence
successful-versus-mixed disagreement. Document_0006 has passed the original-identity
gates and its proposal replaces the complete bibliography, DOI hash and supporting
quote together. Document_0008 has an additional cost-effectiveness-target disagreement;
the clinical identity and that companion-report question stay separate.

After recording a coding completion in state.json, run
`collect_completed_coding.js` through `AsyncFunction(tools, text)`. It collects
only explicitly completed coding tasks, recovers their actual source-reading
tool items, and runs the mechanical validator. It never polls active tasks,
dispatches models, changes scientific judgments, or publishes outputs.
`packet_input_receipts.json` separately freezes the immutable packet files;
`freeze_packet_receipts.py` independently reconstructs those inputs from the
registered original source bytes, including exact collection boundaries.
The validator rejects packet changes even if the result metadata is changed to
match. Native timeline removal of boundary whitespace or a leading byte-order mark is recorded explicitly;
missing substantive characters or altered quote whitespace are rejected.
For an explicitly recorded `cat | fold -w 2000` read of a single long line,
the validator reconstructs the exact UTF-8 byte wrapping and records inserted
line breaks. Arbitrary newline removal cannot satisfy a reading receipt.
Explicit report-boundary descriptions are checked as source ranges and never
counted as quotation proofs. Missing quote data in other evidence entries still
fails validation.

`source_upgrades.json` preserves newly verified report versions separately.
Document_0683 adds the author appendix and errata to document_0001; both fresh blind
Opus and Sol results are validated. Its target-role dispute remains held.
Source-block boundaries and hashes prevent
quotations from joining different documents or inserted navigation headings.

Use `prepare_dispatch.py GROUP_ID --provider opus|sol --attempt 1|2` before
delegating an initial-cohort group. It returns native delegate arguments and a
task-registration record only after checking registry-derived absolute input
paths, every frozen file hash, the owned output root, capacity, duplicate task
history and the attempt limit. Do not construct packet/output prefixes manually.
Parent-supplied invalid paths consumed two preserved technical attempts; their
replacement tasks have distinct IDs and output directories.

`build_verified_proposals.py` rechecks frozen full-record hashes, independently
coded values, validated result hashes, accepted reviewer-file hashes, original
identity and pair uniqueness. A type conversion must travel with compatible
results and literal replacement quotes. Its output cannot approve itself or
enable the other suspended proposals. Original-identity remedies refresh all
original bibliographic fields and clear an unverified link to the old original.
Blank evidence-map placeholders are retained as unproved claims, never counted as
validated quotations or accepted exclusions. Nonempty quotations still require
exact hashes and integer offsets. Alternate extractions of one archived PDF share
the two-attempt budget per model, so a new file ID cannot restart it.
Reproduction-axis fixes replace the complete compound CSV value while preserving
any unchanged axis. A report without a DOI must match its exact registered source
URL; that URL cannot bypass a mismatching DOI. Capacity checks include reserved
technical helpers.
Run all 89 evidence/dependency controls:

```sh
python3 -m unittest discover -s audit/flora_blind_2026-10/independent_recode_20261101 -p 'test_*.py' -v
python3 audit/flora_blind_2026-10/independent_recode_20261101/build_verified_proposals.py
```

The current automatic set also verifies completed study status and authoritative original DOI/title correspondence. Advance-online and print years remain separate provenance for the same publication. A report carrying a plan-only source needs a record remedy, rather than an outcome-only patch. Row 403 retains the directly retested 2000 original: its H4 finding explicitly contradicts the original while other findings agree. The resolved objection and earlier hold remain in `held_acceptance_decisions.json`; the raw second review and verified parent corrections are bound to the proposal. Rows 195 and 869 remain outside automatic acceptance with their joint identity/type/outcome boundaries documented. No review-app rebuild or deployment is inferred from this checkpoint.

Row 104 corrects a dataset/method citation to the explicitly retested Smith et al. (2009) paper, with its complete eleven-author bibliography and literal source citation retained together. A single named author plus “et al.” requires matching printed DOI, exact title, first-author initials and authoritative complete metadata. Source-review field tables may use either an explicit list or keyed entries; conflicting row/field aliases are rejected. Row 1868’s proposed outcome change is withdrawn under the author-overall-verdict rule, with both confident blind readings and the hemispheric contrast preserved. Its full-context quote update remains a separate recommendation.

Row 783 changes successful to mixed from the authors’ explicit original-specific concern-to-usage reversal alongside agreeing findings. Its canonical DOI is retained. A missing SICI ISSN line-break hyphen in the literal extraction is recognized only with an exact one-hyphen transformation, authoritative original metadata and the current publisher’s deposited canonical reference; other DOI differences fail the gate. Both blind citation strings remain unchanged.

Row 2651 remains outside the automatic set after its final source review. The
companion script establishes how the baseline table outputs were generated,
but the reviewer remains unconfident about numerical recovery. Both confident
blind labels, contrary table details and the corrected first-review inference
remain preserved. No further vote is requested to obtain agreement.

Document_0115 is the results-blind version of the Crosby project at row 2362.
Its prospective coding applies to that manuscript only. The completed report
already has a positively bound source packet, document_0479, awaiting its
scheduled independent recoding. The obsolete manuscript cannot justify an
unknown-outcome patch or moving the completed project to planned studies.

Row 351 replaces the wrong Imel (2014) paper with the explicitly retested vocal
synchrony paper, updating its complete bibliography and supporting quote while
retaining the failed outcome. Row 2149's Han (2015) target is also established,
but its citation remedy stays outside the automatic set while authoritative
records disagree on the title suffix and final page. This is a metadata hold,
not a new user policy question. Document_0098 now has two certified fresh blind
reads; its outcome comparison awaits primary-source adjudication.

Row 793 changes successful to mixed: the report explicitly confirms some original
Study 3 findings and identifies failures of the company-interest moderation and
another tested contrast. Row 911 remains held because its blind packet omitted
the abstract containing contrary trend evidence. The complete publisher PDF,
including the abstract and final appendix, is registered as document_0687. It
allows one fresh reading per model; the lower limit applies to every extraction
sharing its PDF hash. Those complete-source reads must pass before any automatic correction. This
newly discovered omission is separate from the finite 60-item recovery queue.

Both complete-source radiation reads now pass mechanically: Opus chooses
successful and Sol mixed, both unconfident. The case remains excluded, with a
final second source review addressing the actual interpretation boundary. No
further blind attempts are allowed. The therapy case-series and secondary
omega-3 news item require record-level scope remedies if confirmed; neither
can enter an isolated field-correction batch. The news item's primary trial is
identified in official metadata, but its full report and original-target binding
remain unresolved.

Row 699 changes successful to mixed because the confirmed rejection-vote finding
is explicitly contrasted with a failed committee-assignment finding. Its smaller
effect and ranking sensitivity remain qualifications. The review's explicit
replacement disposition is read without changing its raw file; inconsistent
value/status aliases or an unresolved policy boundary cannot authorize a change.

Row 1973 changes mixed to failed: the successful lifetime-reading association is
explicitly a baseline control, while all experimental passage-reading comparisons
fail under the authors' whole-study verdict. Row 2308 updates both reproduction
axes together: the authors judge the numerical reproduction essentially the same,
but alternative analyses challenge the four-varieties conclusion. The numerical
discrepancies and scope limited to the 2004 survey remain explicit.

The latest batch adds three mechanically validated readings. Document_0131 needs a fresh blind Sol read because the earlier tool returns omit two source ranges; document_0129 likewise lacks a complete exact-version reading. Document_0130 has a certified complete earlier read but a successful-versus-statistically-successful-but-flawed disagreement. Document_0132 remains unconfident, and document_0133 is abstract-only. None enters the automatic file from this checkpoint.
