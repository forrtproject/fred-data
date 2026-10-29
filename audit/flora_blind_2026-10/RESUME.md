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
