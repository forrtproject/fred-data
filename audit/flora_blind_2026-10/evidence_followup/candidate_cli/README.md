# Finite candidate CLI transport

`../candidate_cli_relay.py` transports parent-prepared candidate, recovered-source
and scoped-field requests. It does not interpret papers or integrate decisions.
Preparation and reconciliation belong to the parent. A **new** Sol execution task
runs the finite snapshot. No live calls or real preparations were made during
implementation.

From the repository root:

```bash
python3 audit/flora_blind_2026-10/scripts/test_candidate_cli_relay.py
python3 audit/flora_blind_2026-10/evidence_followup/candidate_cli_relay.py --prepare --snapshot candidate-20261030-cli-v1
```

Preparation freezes only currently pending `candidate_requests/index.json`
entries, with baseline review_attempts below two, without any existing CLI
reservation. Entries associated with review_0014/review_0016 are excluded even
if subsequently mislabeled pending. All other statuses, including prepared,
terminal and exhausted, are excluded. New arrivals require another named snapshot;
a resume never scans them into the old snapshot. An empty snapshot stays empty.

The snapshot retains entire request payloads and original index entries, all
shipped rows, objections, baseline attempts and prior experts. At preparation,
only explicit `prior_adjudication_path`, `prior_state_path` and
`prior_expert_result_path` references in the reviewer envelope are rewritten to
private frozen context under
`evidence_followup/private/candidate_cli/<snapshot>/context/`. Existing history
bytes are copied unchanged. Absent optional history gets a frozen nonexistent
private path, which must remain absent even if the canonical history later
appears. Original paths, SHA256s or absence, and frozen paths are recorded in
`snapshot.json`'s `history_provenance`, outside the reviewer envelope. Original
request payloads remain intact outside that envelope as provenance.

Parent integration may update/create canonical adjudication and state history
throughout execution; these changes do not alter the prepared reviewer context
or stop dispatch. Frozen context changes or unexpected appearance still block.
All other reference files, including primary source text, coding, codebook,
instructions and lossless-view/index paths embedded in source instructions,
remain pinned by SHA256. Source instruction strings and their paths are
preserved verbatim; primary source bytes and model outputs are never rewritten.
Required sources, codebook and instructions must exist. Files must reside in
this audit worktree. Preparation journals are recovered using the original
frozen snapshot, never by refreshing history from canonical paths.

Existing repository-relative path fields are resolved from the repository working
directory and checked against the same audit boundary. Original payload paths
remain in snapshot provenance. The duplicate prompt snapshot itself is ignored;
its SHA256, preparation record, durable ledgers and reviewer envelopes are retained.

Bundles contain one review kind and one baseline attempt count, with at most six
exact field keys. Duplicate keys anywhere in the snapshot fail preparation,
including duplicates across separate requests; same-source requests with distinct
keys are permitted and are validated once each. Requests over six keys fail
preparation; the transport does not rewrite/split the scientific request.
`cli_review_<snapshot>_<number>.input.json` envelopes are compatible with the
existing controller. Preparation reserves the index once as `review_prepared`,
with `cli_relay`, `cli_snapshot_sha256`, `review_id` and baseline provenance.
It does **not** increment attempts. Repeating preparation is idempotent; a crash
between snapshot creation, envelope publication and index reservation recovers
from that snapshot. Changed selected entries block recovery. The parent remains
the sole queue writer: do not run native preparation/queue mutation concurrently
with these parent commands. The relay parent lock only serializes this helper.

## Parent slot reservation and control

Before execution, the parent must register the actual NEW execution task in
`evidence_followup/state.json`. Its active task entry must have:

```json
{
  "taskId": "the actual newly returned delegate taskId",
  "lane": "candidate_cli",
  "status": "running",
  "slot_cost": 2,
  "cli_snapshot": "candidate-20261030-cli-v1",
  "cli_workers": 1
}
```

The parent must also create an atomic control JSON file at
`evidence_followup/candidate_cli/control.json` with this shape (use that same
actual taskId):

```json
{
  "drain": false,
  "reservation": {
    "taskId": "the actual newly returned delegate taskId",
    "snapshot": "candidate-20261030-cli-v1",
    "workers": 1,
    "model": "Gemini 4 Argon (High)",
    "billing": "included_subscription"
  }
}
```

The worker does not create/update either parent file. The parent must keep
`state.json` current and reserve all infrastructure and nested model calls.
An active `argon_runner` reserves at least four slots and counts as three Argon
workers. While it is active this relay requires exactly one worker. Native Argon
workers each count as one; unknown concurrent Argon lanes fail closed. The global
Argon ceiling is four, and combined reserved slots plus metadata infrastructure
must fit at most nine of the ten slots, preserving one validation slot. This
relay's exact reservation must include one coordinator **plus** the fixed worker
count, even when fewer calls are currently running. Checks occur before durable
reservation and again immediately before invoking the CLI. The reservation must
match the owner, snapshot, worker count, exact model and included subscription
billing. A reservation change or ceiling violation drains to a diagnosed blocker.

The NEW execution task can run this command, which reads its real owner ID from
the parent-created control file:

```bash
python3 audit/flora_blind_2026-10/evidence_followup/candidate_cli_relay.py \
  --run --snapshot candidate-20261030-cli-v1 \
  --control audit/flora_blind_2026-10/evidence_followup/candidate_cli/control.json \
  --owner-task-id "$(python3 -c 'import json; print(json.load(open("audit/flora_blind_2026-10/evidence_followup/candidate_cli/control.json"))["reservation"]["taskId"])')"
```

Default concurrency is one. To drain, the parent atomically changes control
`drain` to true. Current retained futures finish and are collected, then the
coordinator exits. This creates no watcher, timer, schedule or polling loop; the
parent receives the ordinary terminal T3 task notification.

After the original three-call relay is terminal, the parent may reserve a NEW
execution task with `cli_workers:4`, `slot_cost:5`, update the control reservation
to that taskId/workers:4, reset drain, and run the same command with `--workers 4`.
All other active tasks and infrastructure must still fit the ceiling. Each owner
ID is durably bound to its initial worker count; changing it requires a new
execution task. There is no automatic escalation. Worker counts two/three are
also accepted after the old relay ends, with the corresponding reservation.

## Transport, durability and recovery

The only model route is subscription `agy -p ... --model 'Gemini 4 Argon (High)'
--sandbox --print-timeout 10m`, with Read permissions and explicit named input
directories. The parent attests included-subscription routing in the control
file; the helper does not provision credentials, call a paid API, substitute a
model or add Run permissions. It uses a direct argv list, never a shell.
Instructions asking for file output are overridden solely for transport: the
reviewer must put the complete JSON under `## Answer`, with no writes/commands.
The complete scientific instructions and original objections remain supplied.

Each bundle has a durable ledger. Each reservation consumes one remaining
attempt for **every** request in that bundle; baseline + reserved calls never
exceeds two. Uncertain interrupted reservations stay spent. Prompt/raw paths,
input/source/prompt/response SHA256s, owner and timestamps are retained. Raw
responses, process records and prompts live only in ignored
`evidence_followup/private/candidate_cli/<snapshot>/`. Snapshot, ledgers,
progress, per-attempt metadata and execution bindings live next to this README
in the named snapshot directory. Source changes block rather than reusing stale
evidence. No old raw/source/history file is rewritten.

Every reply needs the exact assigned keyset, request_id, method, verdict, value
vocabulary, reason, location, and a nonempty contiguous literal quote from its
own primary source. This includes undeterminable decisions, whose replacement
must be null. Missing-row exclusions also require null. Missing identity
corrections require authors/year/title, record_type and
outcome=cannot_be_determined. Strict parsing rejects missing/extra/duplicate
keys, trailing prose, invalid field values and quote/schema repairs. There is
no partial-result salvage or quote normalization. Invalid, empty, denied and
nonzero/timeout responses remain raw and consume an attempt. Retries use only
the remaining budget and never merge responses into an invented complete reply.

Three consecutive infrastructure failures (empty/denied/no answer heading,
nonzero exit or transport exception) stop dispatch with a progress blocker.
Already-running futures are collected. Schema/evidence failures are consumed
but are not classified as transport failures. The streak persists on resume;
a circuit-open snapshot refuses further execution. Parent diagnosis is required:
after inspecting raw/metadata and fixing the transport, the parent may archive
and explicitly clear the progress streak in these relay-owned outputs before a
NEW execution round. No automatic circuit reset or exhausted-key requeue exists.

The coordinator retains subprocess handles, starts process groups, enforces a
660-second default outer timeout (`--timeout` accepts 1..900), kills its owned
process group and reaps its child on timeout, normal return, SIGINT or SIGTERM.
No nohup or detached launcher is used. Process metadata supports conservative
recovery: a still-existing group after an interrupted reservation blocks resume
until parent inspection. SIGKILL/host failure cannot execute cleanup; avoid
force-killing the coordinator. As with any userspace launcher, death in the tiny
spawn-to-PID-record window needs external process inspection before recovery.
A saved successful metadata/result checkpoint is recovered without another call;
ambiguous reservations are never refunded. Raw outputs are never overwritten.

Any permitted retry appends the previous mechanical error, affected key and raw
reply path to the unchanged scientific brief. The model must reread the source
and return a new complete reply. This feedback never supplies a repaired quote,
changes the frozen source or refunds an attempt. Effective prompts and their
distinct hashes remain durable. Exhausted bundles still require parent diagnosis;
invalid replies are never automatically salvaged or promoted.

## Parent reconciliation

While the execution task is running, and again after it is terminal, the parent
can collect completed bundles with:

```bash
python3 audit/flora_blind_2026-10/evidence_followup/candidate_cli_relay.py --reconcile --snapshot candidate-20261030-cli-v1
```

Reconciliation takes only `candidate_cli/parent.lock`; it does not acquire the
runner lock or pause dispatch. The parent remains the sole candidate-index
writer: serialize these commands and other parent index/integration writes.
The runner never writes that index, scientific state or adjudications.

Each reconciliation reads each atomically published ledger once. It verifies
reserved queue ownership, snapshot hash and baseline provenance, then propagates
baseline plus consumed/reserved attempts conservatively. Pending or reserved
attempts stay `review_prepared`, even if the final allowed attempt is currently
in flight. No raw/result/metadata file for an incomplete bundle is read or
changed, and no partial reply is claimed. A bundle that completes after its
ledger was read is collected by the next reconciliation. Exhausted bundles become
`review_failed_terminal`; source-change bundles require parent inspection.

Only completed validated bundles have their own pinned inputs, envelope, raw
response hash and result checked. The first reconciliation also runs the strict
relay validator and existing parent validator, then stores a receipt containing
snapshot, response, result and validation hashes in the reserved index entries.
Subsequent reconciliations verify those hashes without rerunning validation for
an unchanged receipt. Explicit parent dispositions, including
`parent_inspected_integrated`, and other parent entry fields are preserved,
including when a receipt must be recovered. Successful reviews initially become
`expert_review_complete_pending_parent`. The parent can inspect and integrate
these completed bundles immediately, then repeat partial reconciliation as more
bundles finish. Do not invoke the controller's `validate-candidate` command
separately for already integrated bundles: that standalone validator resets
statuses and does not use this helper's receipt.

Ledger and result publication is atomic. Reconciliation never changes runner
ledgers, in-flight raw outputs or attempt counts, launches calls or requeues
exhausted work. Repeating reconciliation has no extra call or attempt effects.
It writes only parent-owned reserved candidate-index entries, candidate-review
validation files and its reconciliation summary. It never writes canonical
adjudications, main queue/state, datasets, old runner outputs or schedules. The
runner writes only its new transport artifacts and reserved candidate-review
results; parent source inspection and integration remain separate commands.

Source/hash blockers and rejected outputs need parent inspection. This helper
proves mechanical transport/schema consistency, not paper identity, adequacy of
scientific reasoning, report scope or correctness of a verdict. Parent source
inspection and scientific integration remain mandatory.
