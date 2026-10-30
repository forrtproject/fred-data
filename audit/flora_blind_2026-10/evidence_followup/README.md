# Full evidence follow-up is active

Current verified snapshot (2026-10-30T22:07:00.633660+00:00): **472 rows with confirmed errors; 2,387 of 2,818 rows fully resolved; 201 source-confirmed genuinely absent pairs**. The separate unresolved export contains 432 candidates. Unresolved evidence covers 135 full-text, 244 abstract/partial and 52 no-text rows; 899 applicable fields remain unverified. Schema/source-hash/literal-quote checks and same-work DOI/title duplicate and represented-pair checks passed. No accepted nonliteral quotation remains. Dataset SHA256 is unchanged.

Initial field execution is terminal: 260/271 requests validated and 11 exhausted, 770 validated decisions plus eight valid partial decisions, 299 spent attempts. Field dispatch is disabled. Scientific accounting covers all793opening keys separately:705 parent-inspected initial expert keys,45 separately recorded canonical source dispositions,36 awaiting new finite original-specific scopes and7 awaiting the current immutable candidate snapshot. Presence of a disposition does not make an unresolved value substantively resolved. The114bundle candidate snapshot currently has {'exhausted': 4, 'validated': 39, 'pending': 71}; 58 late/scoped requests cover 87 keys outside it and require a NEW finite snapshot after v1 ends. Reviews and the exact recovery schedule remain active; this checkpoint is not completion.

Current execution reserves five combined slots: candidate coordinator plus two included Gemini4Argon(High) calls, and one source-only Sol identity task with two slots. Combined maximum10, one validation slot reserved, absolute Argon maximum4. Current source task is primary_identity_0025 (three factual report-chain checks); exact task IDs/statuses in state.json govern. Earlier source0016/0017/0018/0020 tasks are terminal. Never restart old tick.js or terminal field dispatch. Run tick_evidence_followup.js through functions.exec AsyncFunction(tools,text) promptly on native completion; scheduler recovery only, no polling or duplicate task.

Parent inspected candidate bundles0034–0041, preserving earlier confirmed-pair outcomes where independently supported. Existing611wrongChooriginal is corrected to source-namedHampe1999IBD3; that correction is not exported again as an extra missingpair. New completeMazor2021Stage2original establishes its specifically retested detection-sensitivity finding: shipped979original is retained, outcome corrected from neural-study mixed to behavioural successful; separate2020neural original remains a genuine missingpair. Five further original-specific field outcomes were resolved directly from whole-author verdicts and explicit comparisons. All13terminal source-context keys are now accounted for: seven parent source dispositions, six awaiting new material original/current-source questions.

The current Racz2020published body was independently expanded to include references, frozen at SHA2568096cb7a24186dcb8084726e5c6bf24ca9c1eed7735a9867652fea5ea4a8d44d, then coded by a NEW sanitized blindSol child. It is held for necessary new-source scope review and is NOT an eighth approved supplement;233frozen base sources and seven approved supplements remain unchanged. Newly acquired originalHussam2008body and conditionalSutterworkingpaper context support a genuinely changed-evidence scope, preserving all earlier exhausted attempts. PARK11same-cohort expansion is not automatically report-equivalent; actual closest finding remains scoped. Hegerl/OlbrichsameclinicalEEG reuse is established, while distinct published analytic findings remain separately scoped. Nursing journal/pages/year conflation has new original evidence but no recovered current fullbody; final original/correction question remains held.

Parent caught false shipped identities and rownumbers in Argon0041reasons, including a false PMDDself-link. The four affected keys remain withheld; source-only0025checks the actual conspiracy816, oxytocin759andPMDD439input identities and report/data chains. Raw expert replies are immutable. Information-endowment andOXTRnegative labels remain held for precise empirical-finding/closest-chain review; changed methods, posthoc comparison or citation location alone cannot exclude an actual retest. Only source-confirmed genuinely absent pairs enter confirmed_missing_references.csv.

## Earlier bounded field recovery (execution now terminal)

At the end of wave 2, the immutable 271-request field snapshot had 211 validated
requests, 721 decisions, eight exhausted requests, 52 pending requests, and 242
spent attempts. Current bounded-round counts are in `argon/progress.json`.
Wave 2 used one worker and validated ten more requests before SIG15; its origin is
unestablished and all retained calls drained. Execution termination and
`progress.finished` do not establish scientific completion. Exhausted requests retain
their unresolved evidence limits.

The parent inspected the SIG15 termination, retained its original progress receipt,
verified all 271 immutable request/source/history inputs and all 242 spent reservations,
and found no live owned process, running reservation or latched circuit. The signal
sender remains unknown. Bounded one-call rounds are now enabled; the first three
completed normally with no infrastructure failure. See
`integration/field_signal_recovery_0000.json`. This is execution recovery, not scientific
closure. Source/hash, circuit and orphan blockers still require their own parent
diagnosis; there is no automatic circuit reset.

Parent-owned `state.json` uses this opt-in configuration (absent or disabled means
no field task is launched):

```json
"field_dispatch": {
  "enabled": true,
  "workers": 1,
  "max_calls": 1,
  "next_round": 1
}
```

Following explicit diagnosis, the parent enabled the existing
`scripts/tick_evidence_followup.js` through its documented native tool environment.
Each tick reconciles exact owned task statuses, then uses `field-dispatch` to persist
one stable per-round intent. A NEW native `delegate_task` uses Codex
`gpt-6.1-sol`, medium reasoning and default service tier. Lost delegate responses
retry the same `clientRequestId`; active coordinators and pending nested runs block a
new round. Never send to a terminal task's backing child thread.

The controller checks actual finite request statuses, remaining two-attempt budgets,
unchanged source/input/history hashes, persistent infrastructure health and owned
processes. It durably registers the actual returned task/model/options before
publishing `argon/control.json`. The child waits at most 60 seconds for its exact
round's control. This is the exact bounded command it runs from the project root;
`FIELD_OWNER_TASK_ID` is read from the published actual reservation, never invented:

```bash
FIELD_OWNER_TASK_ID="$(python3 -c 'import json; print(json.load(open("audit/flora_blind_2026-10/evidence_followup/argon/control.json"))["reservation"]["taskId"])')"
python3 audit/flora_blind_2026-10/evidence_followup/run_argon.py \
  --workers 1 --max-calls 1 --owner-task-id "$FIELD_OWNER_TASK_ID" \
  --control audit/flora_blind_2026-10/evidence_followup/argon/control.json
```

`--max-calls N` requires a positive integer, `--workers 1` and a stable
`--owner-task-id`. It caps durable reservations, including invalid replies, retries
and interrupted reservations. Same-owner restarts count prior owned reservations;
the immutable owner binding prevents increasing the cap or changing its snapshot.
There are no refunds. A capped restart may collect interrupted output without
spending another call. Terminal requests are skipped. All retained calls/futures
are collected before normal exit. The runner lock and whole-queue orphan preflight
prevent overlap with an exact live reserved process group. Launch metadata now
records its session before waiting; legacy recovery also inspects exact output file
descriptors. An inaccessible possible owned process fails closed for diagnosis.

Infrastructure streaks persist across rounds through retained attempt histories and
progress; five consecutive infrastructure failures latch the circuit. A one-call
round cannot evade that stop. An ordinary quantum boundary has no blocker and is
not full-snapshot completion. A normal valid reply resets the consecutive streak,
while an open circuit remains latched.

The field task retains `argon_runner` slot cost four even with one actual worker,
so the existing candidate guard counts three field calls plus at most one candidate
call. Active T3 tasks and nested Argon reservations together stay at most nine,
reserving one of ten slots for validation; total Argon stays at most four. Parent
candidate `max_workers:1` is unchanged. Exact included model
`Gemini 4 Argon (High)`, sandbox, 660-second external deadline, CLI
`--print-timeout 10m`, old two-attempt ceilings, raw replies, partial-result rules,
source/schema checks and scientific prompts remain unchanged.

Focused verification uses temporary fake state, fake transports and mocked native
tools; no live model or delegation calls are needed:

```bash
python3 -B -m unittest discover -s audit/flora_blind_2026-10/evidence_followup -p test_run_argon.py
python3 -B -m unittest discover -s audit/flora_blind_2026-10/scripts -p test_evidence_followup.py
node audit/flora_blind_2026-10/scripts/test_tick_evidence_followup.js
```

The user explicitly renewed the scope after the bounded audit and cheap pilot: review the 421 outstanding full-text rows, recover full text where it could settle other rows, and finish the Luna approach while listing only genuinely missing original references. Earlier completion markers are historical snapshots; they do not close this follow-up.

The finite opening queues cover:

- 716 non-excluded omitted-target candidates: all 603 outstanding candidates and all 113 previously confirmed omissions, which also need a check for alternate/preliminary reports and duplicate original works. The 91 previously excluded candidates retain their source-backed decisions unless new evidence warrants reopening them.
- 793 actionable unverified fields with usable saved full text, split into 271 requests of at most six fields. These derive from the 421 unresolved full-text rows across 249 works. Thirty-one conditionally inapplicable shipped-scope fields retain their main verdicts and denominator treatment; unusable/scope-incomplete sources go to acquisition.
- 339 distinct replicating works for primary-source acquisition. The unresolved-row baseline comprises 421 full-text rows, 283 abstract/partial rows, and 53 rows without usable evidence. Source work also covers abstract-only omission candidates and overlaps those rows.

## Evidence and delegation

Luna reviews every assigned target and all shipped original identities, including existing positive decisions and prior objections. Both positive and negative labels remain triage. The parent verifies literal quotations and identity coverage; Gemini 4 Argon (High) handles non-obvious final decisions. The parent can integrate an obvious case only after independently checking the primary empirical retest, exact identity, all shipped counterparts and report equivalence; all other cases receive Argon review. A different DOI, year, manuscript, translation, conference abstract or full report does not alone establish a missing original. Positive source evidence must show an empirical retest of that specific finding. Exclusions also require positive context; an absent search result or unseen full text cannot prove absence.

The opening Luna pilot is not a stopping rule. Every batch in the current index must be processed and its scientific dispositions inspected, including replacements and additions after primary-source recovery. Invalid/missing model quotations are flagged, never repaired or promoted automatically. Full-text recovery and original-specific expert evidence can resolve earlier undeterminable cases; exhausted access routes or genuinely ambiguous evidence may remain unverified, with the actual reason recorded.

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

## Current integration and final gates

All 339 source-recovery works and 201 partial-source assessments have been attempted. The parent verified and promoted 19 complete primary papers and one complete conference abstract, keeping the abstract at abstract evidence level. Each promotion used fresh blinded coding, schema/hash/literal checks, archived old evidence and an explicit old-to-new target map. Named earlier original references cannot disappear merely because another coder omitted them. New unmatched targets re-enter Luna; old placeholder packets are superseded with provenance.

Newly recovered-source fields and final source-scope objections now share the native Argon dispatch index with candidate requests, tagged review_kind=fields. Their separate FIELD_REVIEW_INSTRUCTIONS.md governs row fields; candidate instructions govern only missing-reference identity. A bundle contains one review kind, at most six keys. The native lane remains one call while the three-call relay runs, then up to four; combined ceiling stays ten. There are eight new-source requests/18fields, seven scoped Boyce-project fields and three scoped OSC fields. Two OSC field keys exhausted two initial attempts and retain explicit unresolved scientific objections rather than receiving a budget reset. Original attempts/results remain immutable.

Parent review of conflicting original-reference judgments uses integration/review_holds.json: a pending hold removes an older positive from the confirmed export without destroying its earlier identity/outcome. Resolve holds only after the source objection is inspected. Asendorpf and Roter companion-report candidates were excluded on substantive source evidence; Nielsen was confirmed; Bard and Schulman remain undeterminable primary-evidence questions. A further free Bard download attempt failed; a newly recovered Schulman primary abstract does not settle the mark-test pass-rate question. These are evidence limits, not administrative deferrals.

The current confirmed_missing_references.csv contains only integrated, source-supported omissions; unresolved_missing_candidates.csv is separate. Both remain provisional until the exhaustive recheck finishes. Root final_counts.json and prior phase completion metadata are historical; current live counts are in integration/progress.json and run_manifest.evidence_followup.latest_integrated_counts. Refresh remaining_fields.csv using scripts/refresh_followup_progress.py after compare.py. Do not rebuild the running relay snapshot.

Before approval, inspect each exact request key and immutable expert result, full original-specific primary context, whole-author message, literal quote and all shipped identities. Source validators provide independent context checks, not final scientific verdicts. Parent inspection files record both approved keys and withheld scope objections. Native field reviews use the same validation/integrator with review_kind=fields and approved_keys=[file_key,string input_row_index,field]; candidate approvals use [file_key,target_index].

Six additional individual primary reports were recovered after collection-level
source gaps were identified: Paxton2012, OSC Janssen2008Study1, Huck/Seltzer/Wallace2011,
Kuziemko2014Experiment2, Kessler/Roth2012 and Duffy/Puzzello2014. The parent verified
identity/completeness and a NEW blind Sol child coded all six. Their private text
and coding hashes are registered in additional_reports/approved_sources.json.
compare.primary_text appends only approved, hash-checked exact reports while the
233 base sources in the active relay snapshot remain byte-for-byte unchanged.
Four outcome gaps were resolved from explicit whole-author judgments; two existing
decisions were corroborated. No extra missing pair was created. Prior raw reviews
and approval keys remain intact; superseded_keys prevents replay of an older
undeterminable judgment over genuinely new primary evidence. Parent provenance is
additional_reports/parent_decisions.json. verify_integration also checks each of
these six fresh schemas, hashes, literal quotes and report-specific decisions.

All140Luna packets have now been processed, including source replacements/additions.
One six-target packet exhausted its two attempts without usable literal quotes;
its synthetic needs_more_evidence checkpoint is technical triage, not scientific
closure. Every candidate remains subject to source/identity adjudication. Independent
source-context validators process finite nonoverlapping sets of completed Argon
field replies; all model and validation tasks count toward the combined ceiling.


## Literal source proof and current transport

The native candidate transport is paused after repeated harness failures. The finite CLI candidate snapshot freezes114bundles/421requests; its exact task, worker reservation and attempt budgets live in state.json and candidate_cli/control.json. Parent reconciliation can collect completed bundles during execution. Permitted retries receive keyed mechanical feedback; raw replies and earlier budgets remain unchanged. See candidate_cli/README.md and RESUME.md for the active round and two pinned integration paths.

The parent independently recorded128new literal primary quotations for legacy decisions whose scientific passage and verdict are unchanged. The initial inspection temporarily withheld75further quotation/context cases plus one newly exposed target. Current pending scope/proof holds are41after independent parent inspection; their durable dispositions are in integration/strict_literal_parent_pending_0000.json. They remain in the unresolved export or row-field queue with canonical histories preserved. The supporting/objection labels of a technical source inspector never decide scientific correctness. Final verification rejects nonliteral accepted corrections or missing-reference quotations.

A complete primary publisher abstract was recovered where the old saved abstract was empty. Fresh blinded coding and hash/schema/literal checks support that source upgrade at abstract level; it is not full text. Sixty-one other recovered abstracts add no information. Two report/version identity conflicts remain explicit rather than being silently substituted. See integration/abstract_delta_parent_dispositions.json.


## Historical transport and integration checkpoint (17:40 UTC)

The first field relay stopped with201of271requests validated;711decisions retained,8exhausted,1retry pending and61unattempted. Its run termination is not scientific closure. Candidate transport is temporarily circuit-blocked after repeated local print/process timeouts. Diagnosis establishes incomplete turns and lifecycle issues without an established quota/auth failure. A technical child is repairing exact owned-process cleanup and strict complete-answer collection; no deadlines, models or spent budgets are changed. Parent sets max_workers:1 before any diagnosed restart. Bounded native dispatch retains durable one-call rounds and exact task registration; see RESUME.md for current tasks and remaining evidence checks.

Parent integrated47new field keys from sourcevalidator0007, removed duplicate2156while retaining951, and independently verified a publisher article identity despite a post title-word discrepancy. Eleven CLI candidate decisions passed full parent context checks, including three genuinely absent originals; a contrary Mischel1988scope remains for final review. Current provisional counts are414confirmed-error rows,2243fullyresolved,82confirmedmissingpairs and606unresolvedcandidates. Sourcevalidator0008and Jadad table-proof inspection are complete evidence awaiting parent scientific integration. The recovery schedule remainsactive.
