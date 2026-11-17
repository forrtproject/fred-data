FLoRA contains misidentified originals and incorrectly classified outcomes. This audit checks the 2,818 shipped rows against independent blind coding and primary evidence, and identifies replication–original pairs absent from the shipped references.

The full evidence follow-up is **active**. Current integrated results are provisional: **419 rows with a confirmed field error; 2,195 rows fully resolved; 110 confirmed missing pairs; 607 unresolved omission candidates**. The confirmed-reference export and unresolved-candidate export are separate. All earlier positive omission judgments are being rechecked for alternate reports, shared original findings and duplicates.

Artifacts:

- `audit/flora_blind_2026-10/REPORT.md`: findings, field denominators, coverage and uncertainty bounds.
- `results.csv`: every immutable input row and its field-level evidence/corrections.
- `confirmed_missing_references.csv`: only integrated, source-supported missing references.
- `unresolved_missing_candidates.csv`: candidates requiring further evidence or scope resolution.
- `evidence_followup/`: finite review queues, source provenance, parent inspections and current progress.

Primary-source recovery attempted 339 works and assessed 201 partial sources. Nineteen complete papers and one conference abstract were independently verified, coded afresh by blinded children and integrated with archived prior evidence and target mappings. Luna labels remain triage; the parent checks primary quotations, tested findings and all shipped counterparts, using Gemini 4 Argon (High) for non-obvious cases. Rechecks excluded an Asendorpf benchmark attribution and a represented Roter companion report, confirmed Nielsen, and left Bard/Schulman unresolved rather than inferring absence from unseen evidence.

Validation: 68 parent tests pass; all 2,344 coding envelopes validate; 453 correction fields and 110 current omissions have source-checked evidence. Confirmed-only and unresolved exports are checked against the complete candidate table. The original `output/flora.csv` SHA256 remains `6d391186dfb57263bbc6bb504e8561e0d1e25997b36417072c023812efaad9f7`. The audit applies no corrections to the dataset.

Text access determines coverage, so this is not a representative error-rate sample. Remaining source gaps and disputed findings stay unverified. The draft remains open while exhaustive reviews and parent integration continue; final closure requires all owned work and the recovery schedule to be stopped.
