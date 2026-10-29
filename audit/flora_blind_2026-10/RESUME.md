# Parent orchestration resume

Authorized unattended until 2026-10-29 19:19:58 UTC. Never ask questions. Full brief is `/home/lukas/audit_inputs_2026-10/brief_flora_v3.md`. Only this worktree/branch. Keep FReD/main checkout untouched.

Run the T3-native dispatcher from `functions.exec`:

```js
const r = await tools.exec_command({cmd:'cat audit/flora_blind_2026-10/scripts/tick.js',max_output_tokens:6000});
await new (Object.getPrototypeOf(async function(){}).constructor)('tools','text',r.output)(tools,text);
```

Tasks/statuses/model selections are recorded in tasks.jsonl; batch prompts contain sanitized metadata and verbatim codebook. The infrastructure child has seen shipped values and MUST NEVER code papers. Coding workers never read comparisons. No child commits. First coder batches 00000 and 00001 dispatched after adapter check passed.

Parent next steps during runs:

1. Finish reviewing comparison infrastructure, run tests and validate outputs. `python3 scripts/controller.py validate` reports coding structural/hash validation. Improve quote validation if needed without exposing comparisons to coders.
2. Refill workers promptly on completion notifications using tick.js; scheduler every 5 minutes is recovery. Ramp total task limit 3 before +10min, 5 before +20min, 8 before +30min, then10. After +10min reserve one large-project lane continuously. Already implemented.
3. At +30min measure valid coded works per wall-clock / worker time and project coverage by +8h. Tighten acquisition if necessary; log decisions.
4. Parent must adjudicate disagreements from compare.py. Obvious needs one-line reason and confirmed source quote/location. Every non-obvious goes through `agy` Gemini 4 Argon (High), at most4 simultaneous, one retry for failure. Read agy-delegate skill. Verify JSON and quote occurs in source. Never establish error from an unmatched row or blind disagreement alone.
5. Integrate and rerun results/report, keep unverified rows explicit. Hourly commit/push `.gitignore` and explicit audit paths (texts ignored). Avoid git add -A or unrelated files. Verify source data hash. Open draft PR main only after final report and register using link_pull_request.
6. Stop coding +8h, new adjudications +9.5h. At +10h cancel outstanding tasks, finish/checkpoint report, push, draft PR, REMOVE recovery schedule. Schedule ID is in run_log.md. Remove early if audit complete. Discovery via ALL_TOOLS for scheduler update/delete tools.

Never let recurring schedule continue beyond authorized audit. Never claim complete while work remains. Terminal failures after one retry and access failures stay unverified; all 2,818 input rows must appear in results.

Parent integration updates:
- `scripts/adjudicate.py` implements retained `agy` calls, max4 via process lock, one retry, JSON+source-quote validation and input-signature checkpoints. Invoke with selected file keys after triage; no args processes all unresolved work groups. Collect its retained terminal session before ending a turn, per skill. Check `argon/*.state.json` and `adjudications/*.json`, then rerun compare.py. Never launch a second runner while an earlier nonlocking runner is active.
- Parent reviewed engine and improved surname-first reference matching (initials and multipart names), dispatched-attempt accounting and compact time report linked to work_times.csv. 26 tests pass. `scripts/tick.js` now cancels future batches that exceed summed paper caps plus180s checkpoint overhead.
- Initial Argon runner session 68861 COMPLETED and was collected. No initial nonlocking runner remains. Next parent should triage new disagreement works and invoke adjudicate.py for up to4 work groups, collect result, rerun comparison. Validated undeterminable adjudications are final; do not repeatedly call Argon on them.
- First accepted type correction changes a replication row to reproduction; engine now accepts a validated outcome object with BOTH axes following that type correction (27 tests pass). Check any future reverse type corrections carefully as outcome vocabulary also changes.
- When staging codings, select only names matching `[0-9a-f]{16}.json`; workers also create metadata scratch JSONs that must stay ignored. Source texts remain gitignored; integrity checked.
- Tick now runs scripts/progress.py: counts exact-name valid codings, records progress.jsonl, and at +30min writes forecast.json from measured ordinary task worker-minutes. It conservatively projects nine ordinary workers to the coding deadline. If projected coverage <80%, controller shortens acquisition to60+20 seconds for subsequent batches while preserving coding standards; otherwise90+30 stays. User requested projection is therefore persisted once +30min is reached.
- Current Argon runner retained session92785 (four works:37f000537de70d42,7113daab150388e1,e340bb8dc4ca59b5,4d22f5a1242960d7). Collect before ending current turn or starting another runner; lock also prevents overlap.
- Thirty-minute throughput check completed: forecast.json now accounts for observed no_text yield and projects about2,172 coded works (~92.7%) by coding cutoff; retained90+30-second acquisition. Ten workers reached at+30min; limit remains10. Hourly progress counts append automatically in progress.py.
- Quote normalisation is cached; full comparison including the1.88MB/165-target project takes2.25 seconds;28 tests pass. Many project outcomes match but have no complete-sentence source quote, so they remain unverified pending adjudication.
- Genetics37f000537de70d42 Argon reply recovered and validated after a harmless missing_row/shipped_right empty-value format issue; no new model call needed. Parent allows absent replacement for that no-addition verdict only, still requires quote/reason/location. Runner92785 still waiting on4d22f5a1242960d7 retry: first attempt wrote a complete valid answer but CLI did not exit before660s and was retried. First three work results collected; initial4d text can be recovered/validated if retry transport fails. Do not repeat a third call. Current session92785 remains the one Argon runner; do not launch a second until collected.
- Runner92785 COMPLETED and collected. No Argon runner remains active. All four work replies validated:37f identity corrected,711 outcome mixed and one omitted Wynn target,e340 mixed,4d four omitted targets.4d CLI lingered after complete reply; parent stopped its exact owned PID, reaped it, verified all quote/DOI evidence, and recovered output. Future wrapper accepts a fully validated complete reply even if subprocess timeout killed the lingering CLI; incomplete output still retries once. No third call for these works.
- Blinding incident: ba34c6d310f46998 initial coding had incidental FORRT search-snippet exposure, reported by coder. Excluded/quarantined at quarantine/ba34c6d310f46998.attempt1.json, with blinding_incidents.json. Fresh child batch00051 receives only cached primary text and sanitized task; never sees old coding or warning. This one justified validity retry overrides done-is-final. Guard rejects blind_source_warning in controller and comparison; regression test added (29 pass). Future searches require FORRT domain exclusions. If fresh coding is done and warning-free, it is the final blind record; do not retry again. Report lists incident for transparency.
