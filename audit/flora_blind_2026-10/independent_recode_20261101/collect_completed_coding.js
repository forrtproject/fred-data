// Parent-only, finite completion collection. Run via AsyncFunction(tools, text).
// No dispatch, schedules, active-task polling, scientific decisions or exports.
const root = '/home/lukas/.t3/worktrees/fred-data/audit-flora-blind-2026-10';
const cohort = root + '/audit/flora_blind_2026-10/independent_recode_20261101';
const privateRoot = root + '/audit/flora_blind_2026-10/evidence_followup/private/independent_recode_20261101';
const quote = s => "'" + s.replaceAll("'", "'\\''") + "'";
async function command(cmd, max_output_tokens = 1000) {
  const result = await tools.exec_command({cmd, max_output_tokens, yield_time_ms: 10000});
  if (result.session_id || result.exit_code !== 0) throw Error(result.output);
  return result.output;
}
function unpack(result) {
  if (result.isError) throw Error(JSON.stringify(result));
  return result.structuredContent ?? JSON.parse(result.content.find(x => x.type === 'text').text);
}
async function writeImmutable(path, value) {
  const body = JSON.stringify(value, null, 2) + '\n';
  await command('python3 -c ' + quote(`import pathlib,json
p=pathlib.Path(${JSON.stringify(path)});body=json.loads(${JSON.stringify(JSON.stringify(body))})
p.parent.mkdir(parents=True,exist_ok=True)
if p.exists():
 assert p.read_text()==body,'Existing receipt changed: '+str(p)
else:p.write_text(body)
`));
}
const statePath = cohort + '/state.json';
// Project the small pending set in Python: the full finite history may grow to
// hundreds of task records and must never be truncated while reading JSON.
const snapshot = JSON.parse(await command('python3 -c ' + quote(`import pathlib,json,hashlib
p=pathlib.Path(${JSON.stringify(statePath)});raw=p.read_bytes();s=json.loads(raw)
keys=['taskId','childThreadId','clientRequestId','role','output_dir','output_layout','packet_ids']
pending=[{k:t.get(k) for k in keys} for t in s['tasks'] if t['status']=='completed_pending_parent_validation' and t['role'] in ['blind_coder','blind_comparison_coder']]
print(json.dumps({'sha256':hashlib.sha256(raw).hexdigest(),'pending':pending}))
`), 18000));
const pending = snapshot.pending;
if (!pending.length) {
  text({collected_groups: 0, scientific_acceptance: false});
  return;
}
if (pending.length > 4) throw Error('Collect at most four completed coding groups per invocation');
const reports = [];
for (const task of pending) {
  if (!task.childThreadId || !task.clientRequestId || !task.output_dir?.startsWith(privateRoot + '/outputs/'))
    throw Error('Missing exact owned task/output identity');
  if (!task.packet_ids?.every(id => /^document_\d{4}$/.test(id))) throw Error('Invalid packet IDs');
  const dir = privateRoot + '/parent_receipts/' + task.clientRequestId;
  const items = [];
  let afterPosition;
  // Pagination through one completed timeline, never waiting or polling.
  for (let page = 0; page < 3; page++) {
    const data = unpack(await tools.mcp__t3_code__t3_thread_read({threadId: task.childThreadId,
      view: 'activity', limit: 100, maxCharsPerItem: 50000, runLimit: 1, afterPosition}));
    if (data.thread.status !== 'completed' || data.thread.activeRunId)
      throw Error('Task notification does not establish terminal completion: ' + task.taskId);
    for (const item of data.items) {
      let sourceRead = false;
      if (item.type === 'dynamic_tool' && !item.textTruncated) {
        try {
          const call = JSON.parse(item.text);
          sourceRead = call.toolName === 'Read' && task.packet_ids.some(id =>
            call.input?.file_path?.startsWith(privateRoot + '/' + id + '/chunks/'));
        } catch (_) { /* Not a source-file Read record. */ }
      } else if (item.type === 'command_execution') {
        const firstLine = item.text?.split('\n', 1)[0] ?? '';
        sourceRead = firstLine.includes('cat ') && firstLine.includes('chunk_')
          && task.packet_ids.some(id => firstLine.includes(id));
      }
      if (sourceRead) {
        if (item.textTruncated) throw Error('Recover the full source-read item before validation: ' + item.itemId);
        const receipt = {threadId: data.thread.threadId, model: data.thread.model,
          terminal_status: data.thread.status, ...item};
        await writeImmutable(dir + '/item_' + item.position + '.json', receipt);
        items.push({itemId: item.itemId, position: item.position, type: item.type});
      }
    }
    if (!data.hasMore) break;
    if (page === 2) throw Error('Timeline exceeds finite collection budget; inspect explicitly');
    afterPosition = data.nextPosition;
  }
  await writeImmutable(dir + '/index.json', {taskId: task.taskId, items});
  const docs = [];
  for (const id of task.packet_ids) {
    const output = task.output_dir + '/' + id;
    // Single-document Sol tasks historically write directly under attempt_N.
    const actual = task.role === 'blind_comparison_coder' && task.output_layout !== 'per_document'
      ? task.output_dir : output;
    const validation = JSON.parse(await command('python3 ' + quote(cohort + '/validate_output.py')
      + ' ' + quote(privateRoot + '/' + id) + ' ' + quote(actual) + ' ' + quote(dir), 2500));
    docs.push(validation);
  }
  reports.push({taskId: task.taskId, documents: docs});
}
// Parent is the sole state writer. Detect unexpected concurrent mutation.
const qreports = JSON.stringify(JSON.stringify(reports));
await command('python3 -c ' + quote(`import pathlib,json,datetime,hashlib
p=pathlib.Path(${JSON.stringify(statePath)});raw=p.read_bytes();s=json.loads(raw)
assert hashlib.sha256(raw).hexdigest()==${JSON.stringify(snapshot.sha256)},'Parent state changed during collection'
reports=json.loads(${qreports})
for r in reports:
 t=next(t for t in s['tasks'] if t['taskId']==r['taskId'])
 t['status']='completed_parent_mechanically_validated';t['validation_documents']=[d['document_id'] for d in r['documents']]
 k='validated_fresh_sol_documents' if t['role']=='blind_comparison_coder' else 'validated_opus_documents'
 s[k]=sorted(set(s.get(k,[])+t['validation_documents']))
s['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
p.write_text(json.dumps(s,indent=2)+chr(10))
cohort=p.parent;plan=json.loads((cohort/'dispatch_plan.json').read_text());initial={'document_0001'}|{d for g in plan['groups'] for d in g['document_ids']}
validated=set(s.get('validated_opus_documents',[]));launched={t.get('group_id') for t in s['tasks'] if t.get('role')=='blind_coder'}
progress_path=cohort/'progress.json';progress=json.loads(progress_path.read_text()) if progress_path.exists() else {}
progress.update(updated_at=s['updated_at'],scope=s['scope'],initial_document_packets=len(initial),initial_Opus_documents_parent_validated=len(validated&initial),upgraded_Opus_documents_parent_validated=len(validated-initial),fresh_Sol_documents_parent_validated=len(s.get('validated_fresh_sol_documents',[])),active_tasks=[{k:t.get(k) for k in ['taskId','role','packet_ids']} for t in s['tasks'] if t['status'] in ['running','queued','waiting']],initial_Opus_groups_validated=sum(set(g['document_ids'])<=validated for g in plan['groups']),initial_Opus_groups_total=len(plan['groups']),next_prepared_group=next((g['group_id'] for g in plan['groups'] if g['group_id'] not in launched),None),automatic_corrections_accepted=s.get('automatic_corrections_accepted',0),scientific_completion=False)
progress_path.write_text(json.dumps(progress,indent=2)+chr(10))
`));
text({collected_groups: reports.length, reports, scientific_acceptance: false});
