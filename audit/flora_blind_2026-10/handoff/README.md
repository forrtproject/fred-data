# Fix proposals and final review

This handoff packages the existing audit. It does not constitute a new final Sol review, claim certainty, change the codebook, or apply any changes to FLoRA. The earlier follow-up completed its finite queues; that is different from settling every scientific value.

- `fix_proposals.json`: 545 existing source-adjudicated field proposals across 500 rows, plus 441 proposed missing-pair additions. Existing rows include the exact frozen `expected_before` record. These are proposals, not an automatically approved patch. Original-identity objects and row-removal instructions require explicit interpretation by an eventual application step.
- `review_queue.json`: complete evidence for 382 unresolved existing rows and 127 possible missing pairs. A row can have both a supported correction and an unresolved field; the two files intentionally overlap by row while serving different purposes.
- `fulltext_109_inventory.json`: the 109 unresolved saved-full-text rows across 71 works, without dropping any original export uncertainty.
- `review.html`: searchable local review interface. Starts with the 109 full-text rows. Long passages are labelled display excerpts; The private tailnet page automatically loads `review_queue.json` and verifies its SHA-256; the file picker provides the same check for downloaded copies. Decisions stay in the browser; **Export decisions** saves them. They never apply changes to FLoRA. This is an initial review interface, not yet an evidence-complete adjudication workspace: it links the work DOI and existing evidence, but does not embed privately acquired full reports or every historical objection.
- `manifest.json`: input hashes and exact packaging counts.

## Why full text can still leave a value unresolved

The export currently conflates audit completion, substantive value, and applicability. Its 109 unresolved full-text rows include 17 with existing removal proposals, 8 requiring applicability checks after a not-a-replication judgment, 6 prospective plans without reported results, and 78 requiring substantive source or coding review. These routes are deterministic screening flags; they do not prove a final decision or imply the other 78 are all resolvable.

Saved full text can be a protocol, incomplete collection extract, or a complete current paper without the necessary original, supplement, report version, or target-specific comparison. It can also reveal a genuine coding-policy ambiguity. Not applicable and a confidently reviewed unknown must not be presented as unreviewed work.

## Proposed final Sol closure

1. Review all 109 rows grouped into 71 works, using current source, original-specific evidence, prior objections and the codebook. This is informed final adjudication, not a new blind coding. Any newly acquired primary source needing fresh coding gets a separate sanitized blind child.
2. Resolve applicability and prospective status explicitly. Preserve the codebook's `cannot_be_determined` where appropriate, with a separate final audit status. Do not silently change the definition of `uninformative`, aggregate mixed replication/reproduction workflows, or substitute a working paper for an unverified journal version.
3. Give genuine policy choices to the user with concrete alternatives. Route actual access gaps to source acquisition; show the precise missing evidence rather than merely saying full text is available.
4. For every proposed correction/addition, record final source-backed signoff, literal proof, original/report identity, confidence qualification, and dependencies. Review disputed corrections as well as currently unresolved cases. Model agreement alone does not make a fix safe.
5. Produce separate approved fixes and review-required records. Validate baseline preconditions, row removals, original replacements, type/outcome dependencies and pair deduplication in a dry run before applying anything. Preserve the immutable baseline and all old judgments.

The claim to aim for is: **Every record was reviewed by GPT-6.1 Sol under the stated codebook; supported corrections are separated from explicit evidence limits and decisions requiring human review.** “Every field is known” or “100% correct” is not supported by having a complete PDF or by a model's confidence.

Regenerate from the repository root:

```bash
python3 audit/flora_blind_2026-10/scripts/build_review_handoff.py
```

## Final Sol review progress

`sol_review_decisions.json` separates completed, parent-checked field judgments from the historical unresolved export. Exact reviewed/remaining counts, dispositions and owned task IDs are in `manifest.json` and `sol_closure_progress.json`. A completed review may record an explicitly unknowable value or a human policy choice; it is not necessarily an approved substantive correction. Partial large-lane results remain private, and unfinished cases are being recovered in single-work scopes. This is ongoing review, not a whole-dataset completion claim.

`metadata_format_fix_dryrun.json` documents a tested audit-export issue: supported retained-original decisions using only shipped metadata column names were not decoded into the comparison schema. The narrow fix clears 14 original-field verification flags in a private dry run, with no other field-verdict changes. It changes no raw evidence, dataset or published export. Canonical citation objects retain precedence and are never combined with preserved shipped metadata. Final Sol source-review coverage remains separately measured.

The private review page is served at http://100.121.34.85:8876/review.html. Only this handoff directory is served; no full acquired source texts or PDFs are exposed. `approved_fixes.json` contains only fields with explicit final Sol source-backed correction approval, exact frozen before-records, and proof. It is not an applied patch. `confirmed_missing_pairs_addendum.json` contains newly source-verified absent pairs, with outcome grading outside that identity-only scope. `missing_pair_review_decisions.json` preserves represented-versus-absent reasoning, including shared samples and alternate reports. Earlier exports remain unchanged.
