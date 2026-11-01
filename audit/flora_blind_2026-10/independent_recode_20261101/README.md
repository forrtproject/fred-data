# Independent recoding of proposed corrections

Current scope: 562 proposed fields across 515 existing rows, covering 469 works. This is a full-cohort reassessment of proposed changes. Missing-pair additions remain a separate evidence stream; a coder omitting a target is not evidence to remove a row.

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
In particular document_0004 needs the newly dispatched blind Sol pass because its
old reading was incomplete, document_0005 needs an adversarial source check, and
document_0007 has a low-confidence successful-versus-mixed disagreement. The
document_0006 assignment concerns original identity, not outcome agreement.
