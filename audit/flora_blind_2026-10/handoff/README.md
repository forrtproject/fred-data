# Fixes and final source review

All **109 previously unresolved saved-full-text rows across 71 works** received complete, scoped GPT-6.1 Sol source reviews. The assigned fields are settled in **80 rows**; **21 rows retain specific evidence limits**, and **8 require coding-policy decisions**. Four correction bundles have explicit application dependencies. Completed audit work and a recoverable scientific value are recorded separately. No dataset changes have been applied.

The earlier audit used Sol blind coding and cross-model source adjudication. This additional pass checks the previously unresolved full-text fields; it does not claim that every field in all 2,818 rows received another full-source Sol adjudication. The historical export still has 221 partial/abstract rows and 52 without usable text. Those source limits must remain attached to any whole-dataset audit claim.

- [Source-approved fixes](approved_fixes.json): 14 newly approved field corrections, exact frozen before-records and literal proofs. Conditional corrections are excluded.
- [Evidence replacements](evidence_provenance_fixes.json): 14 independently verified primary-report quotation/provenance updates. These are separate from scientific field changes. Existing project attempts and numerical disagreements are retained.
- [Review-required cases](review_required.json): explicit evidence gaps, policy alternatives and correction dependencies, with no forced replacement value.
- [Earlier proposals](fix_proposals.json): the unchanged 545 source-adjudicated field proposals across 500 rows and 441 proposed missing pairs. These retain their earlier evidence and require application review; they are not all automatically approved by this additional pass.
- [New missing-pair addendum](confirmed_missing_pairs_addendum.json): one newly source-confirmed absent pair, DeWitt (2016). No outcome is inferred. The four Lucid pairs already in the earlier export are not added twice; the separate GSS identity remains uncertain.
- [Complete field decisions](sol_review_decisions.json), [missing-pair decisions](missing_pair_review_decisions.json), [progress and task accounting](sol_closure_progress.json), and [input hashes/counts](manifest.json).

## Why saved full text did not settle every value

Some saved files were registrations, masked manuscripts, incomplete collection extracts, or reports without the specific comparison needed by the codebook. The final pass recovered actual results-bearing versions for the ManyLabs5 Crosby, Young–Saxe and cooperation projects; individual student narratives; original reports; supplements; and posted Ku outputs. Each new empirical source was independently identified, then coded by a fresh sanitized Sol child before a separate informed comparison. Reviewers were not reused as blind coders.

Other complete sources still omit a needed result or empirical target. For example, the Flanker project publishes an omnibus effect but not the original-specific pairwise contrasts; the Sanders exploratory histogram does not establish recovery of the original central numerical estimates. Actual public source locations were checked. The colour study attributes an experiment to a review that contains no matching experiment. These are documented reporting or identity limits, not unfinished reading. Source contradictions, unavailable component narratives, and all previous opinions remain preserved.

Policy choices concern the unit of the tested claim, hybrid replication/reproduction workflows, published anecdotal findings, the authors’ “inconclusive” category, or discovery-inclusive pooled evidence. Each has concrete alternatives in the review app. The Nakano SNP proposal was held after a separate Argon High objection review; neither the negative nor positive author framing was discarded.

Primary metadata checks also prevented unnecessary fixes: the correct Margulieux title retains “expository text,” despite a miscitation in the current reference; Lane’s 2011 online/2012 print dates do not require a year correction. Different DOI, year or title wording alone does not establish a missing reference.

## Review and application

Open the private app at **http://100.121.34.85:8876/review.html**. It shows the 109-row pass, earlier correction proposals, evidence limits and policy decisions. Verified primary-report links are supplied where available. Complete queue loading verifies SHA-256. Notes stay in browser storage; **Export decisions** saves them without changing FLoRA. Only the handoff directory is served; private acquired reports and access tokens are not exposed.

Apply only explicit approved fields against their exact frozen before-records. Reconcile original replacements, removals and retained-row evidence before applying dependent outcomes. In particular, preserve both replication attempts when merging the OSC duplicate; do not apply conditional outcomes to the wrong original or duplicate row. The original proposal file and all earlier attempts remain unchanged.

A defensible claim is: **FLoRA was blind-coded by GPT-6.1 Sol under the stated codebook; all previously unresolved saved-full-text fields received complete Sol source review, with cross-model adjudication where needed. Supported corrections, evidence limits and human decisions are separately documented.** This does not mean every field is known, every correction has been applied, or every record has a complete primary report.

Regenerate and validate from the repository root:

```bash
python3 audit/flora_blind_2026-10/scripts/build_review_handoff.py
python3 audit/flora_blind_2026-10/scripts/validate_review_handoff.py
```

The validator checks exact assigned-row coverage, raw hash/Unicode/UTF-8 proofs, baseline preconditions, explicit correction approval, quotation updates and newly introduced pair duplicates. The 88 comparison/follow-up/literal-source regression tests passed. The narrow metadata-format export dry run remains in [its receipt](metadata_format_fix_dryrun.json); it applied no dataset or canonical export changes.
