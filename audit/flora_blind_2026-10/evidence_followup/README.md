# Full evidence follow-up is active

The user explicitly renewed the scope after the bounded audit and cheap pilot: review the 421 outstanding full-text rows, recover full text where it could settle other rows, and finish the Luna approach while listing only genuinely missing original references. Earlier completion markers are historical snapshots; they do not close this follow-up.

The finite opening queues cover:

- 716 non-excluded omitted-target candidates: all 603 outstanding candidates and all 113 previously confirmed omissions, which also need a check for alternate/preliminary reports and duplicate original works. The 91 previously excluded candidates retain their source-backed decisions unless new evidence warrants reopening them.
- 793 actionable unverified fields with usable saved full text, split into 271 requests of at most six fields. These derive from the 421 unresolved full-text rows across 249 works. Thirty-one conditionally inapplicable shipped-scope fields retain their main verdicts and denominator treatment; unusable/scope-incomplete sources go to acquisition.
- 339 distinct replicating works for primary-source acquisition. The unresolved-row baseline comprises 421 full-text rows, 283 abstract/partial rows, and 53 rows without usable evidence. Source work also covers abstract-only omission candidates and overlaps those rows.

## Evidence and delegation

Luna reviews every assigned target and all shipped original identities, including existing positive decisions and prior objections. Both positive and negative labels remain triage. The parent verifies literal quotations and identity coverage; Gemini 4 Argon (High) handles non-obvious final decisions. A different DOI, year, manuscript, translation, conference abstract or full report does not alone establish a missing original. Positive source evidence must show an empirical retest of that specific finding. Exclusions also require positive context; an absent search result or unseen full text cannot prove absence.

The opening Luna pilot is not a stopping rule. All 132 batches must be processed and their scientific dispositions inspected. Invalid/missing model quotations are flagged, never repaired or promoted automatically. Full-text recovery and original-specific expert evidence can resolve earlier undeterminable cases; exhausted access routes or genuinely ambiguous evidence may remain unverified, with the actual reason recorded.

New primary texts are saved privately, without replacing old evidence. The parent independently verifies identity and completeness, then dispatches NEW blinded coders with only the verbatim codebook/schema and sanitised replicating-study metadata. Reviewers exposed to shipped fields never become blind coders. Old codings, source versions and adjudication histories are preserved before any promotion. The parent owns canonical integration, staging and Git.

The old two-attempt histories are immutable. The user authorised renewed review; new small, target-specific requests have separate durable identities, input/source/prompt hashes, and at most two attempts each. Prior objections must be answered. The two large source collections are split rather than resubmitted as oversized whole-work replies. A scientific decision must be supported by a short contiguous literal quotation, location and reason. No OCR/word/sign repair or splicing across PDF columns is accepted.

## Operation

Run scripts/tick_evidence_followup.js through functions.exec by reading it with tools.exec_command and evaluating AsyncFunction('tools','text',source)(tools,text). It reconciles owned tasks and refills Luna slots after completion notifications. Do not run the original tick.js: its deadlines/completed marker belong to the earlier audit.

The combined ceiling is ten, including infrastructure and nested CLI reviews. The initial Argon relay reserves four slots (one relay plus up to three calls); acquisition reserves two; Luna uses at most three. Keep the remaining slot for subprocess/validation work and do not silently increase these counts. Native task IDs, exact provider/models/options and statuses live in state.json and tasks.jsonl. The two infrastructure children may work for hours; read their atomic progress on ordinary completion/recovery turns rather than starting duplicate runners.

A native Antigravity Gemini 4 Argon (High) candidate-review lane uses at most one additional model call while the three-call CLI field relay is active, keeping the total at four. Once that relay ends, up to four native reviews can run within the combined ten-slot ceiling. Both positive and negative decisions still await parent source inspection. Crossref enrichment completed for 1,189 unique DOIs.

The Argon relay's first finite snapshot is field_requests/index.json. Its outputs go only to argon/, never authoritative adjudications. After it ends, inspect and use a NEW delegate_task round for candidate_requests/index.json and newly available evidence, preserving the original brief, earlier findings and outstanding objections. Do not use t3_thread_send on backing child threads. The candidate queue grows as Luna batches finish.

Acquisition owns acquisition/acquire.py, acquisition/results.jsonl, acquisition/progress.json and private/ files. It uses the download-paper free OA chain without metered Scholar or a signed-in browser. Metadata enrichment in bibliography_metadata.json comes directly from Crossref and proves bibliographic identity only, not independent retesting or outcomes. Source bodies and raw unreviewed provider output remain ignored.

The 15-minute scheduler is recovery only. Its exact ID is recovery_schedule_id in state.json. It must be removed when this follow-up is fully integrated or stopped with an explicit actual blocker. Never claim completion while queues, model tasks, owned processes or this schedule remain active. Do not touch unrelated schedules, FReD, the main checkout, output/flora.csv or pipelines. Checkpoint and push explicit audit paths plus .gitignore hourly; keep draft PR 156 linked and current. The original dataset SHA256 must remain 6d391186dfb57263bbc6bb504e8561e0d1e25997b36417072c023812efaad9f7.

Final integration must export confirmed missing references separately from unresolved candidates, deduplicate only with primary identity evidence, regenerate row/field coverage and rate bounds, verify source/coding schemas and every accepted quotation, run relevant tests, push, and remove the recovery schedule. An administrative deferral does not count as substantive completion of a field.
