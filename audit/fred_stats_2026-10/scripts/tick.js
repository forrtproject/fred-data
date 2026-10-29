const B='/home/lukas/.t3/worktrees/fred-data/audit-fred-stats-2026-10/audit/fred_stats_2026-10';
const parse=r=>r.structuredContent??JSON.parse(r.content.find(x=>x.type==='text').text);
const read=async name=>(await tools.exec_command({cmd:`cat '${B}/${name}'`,max_output_tokens:50000})).output;
const append=async (name,x)=>tools.exec_command({cmd:`cat >> '${B}/${name}' <<'FRED_JSON_EOF'\n${JSON.stringify(x)}\nFRED_JSON_EOF`,max_output_tokens:100});
const records=(await read('tasks.jsonl')).trim().split('\n').filter(Boolean).map(JSON.parse);
const manifest=JSON.parse(await read('run_manifest.json'));
let status={};try{status=JSON.parse(await read('task_status.json'));}catch{}
for(const r of records){
 if(['completed','failed','cancelled','interrupted'].includes(status[r.taskId]?.status))continue;
 const x=parse(await tools.mcp__t3_code__task_status({taskId:r.taskId}));status[r.taskId]={status:x.status,summary:x.summary,hasPendingQuestion:x.hasPendingQuestion,pendingApproval:x.pendingApproval};
 if(!['completed','failed','cancelled','interrupted'].includes(x.status) && r.started_at && Date.now()-Date.parse(r.started_at)>15*60000){
  const cancelled=parse(await tools.mcp__t3_code__task_cancel({taskId:r.taskId,clientRequestId:'fred-timeout-'+r.batch,reason:'15-minute hard worker ceiling'}));
  status[r.taskId].cancel_result=cancelled;
 }
 if(x.providerInstanceId!=='codex'||x.model!=='gpt-6.1-sol'||!x.options?.some(v=>v.id==='reasoningEffort'&&v.value==='medium'))throw Error('Requested child identity mismatch');
}
await tools.exec_command({cmd:`cat > '${B}/task_status.json' <<'FRED_JSON_EOF'\n${JSON.stringify(status,null,2)}\nFRED_JSON_EOF`,max_output_tokens:100});
const terminal=['completed','failed','cancelled','interrupted'];
let active=records.filter(r=>!terminal.includes(status[r.taskId].status));
const elapsed=(Date.now()-Date.parse(manifest.launch_time))/60000;
const cap=Math.min(10,3+Math.floor(elapsed/4));
const q=JSON.parse(await read('queue.json'));
await tools.exec_command({cmd:`python3 '${B}/scripts/retries.py'`,max_output_tokens:1000});
const retryQueue=JSON.parse(await read('retry_queue.json'));
for(const r of active){r.large=q.find(x=>x.batch===r.batch)?.large??false;}
const ins=await read('worker_instructions.txt');
const existing=new Set(records.filter(r=>r.kind==='extraction').map(r=>r.batch));
const existingSan=new Set(records.filter(r=>r.kind==='sanitisation').map(r=>r.batch));
let dispatched=[];
while(active.length<cap && Date.now()<Date.parse(manifest.deadlines.extraction)){
 let task,kind,batch,ids;
 // Reserve a continuous slot for large projects after pilots. Other slots prioritise flagged and small works.
 const largeActive=active.some(r=>r.large);
 let candidate=retryQueue.find(x=>!active.some(r=>r.batch===x.batch))??q.find(x=>!existing.has(x.batch)&&x.large&&!largeActive);
 const nextSan=Array.from({length:11},(_,j)=>String(j).padStart(2,'0')).find(j=>!existingSan.has(j));
 if(!candidate && nextSan && active.filter(r=>r.kind==='sanitisation').length<2){
  kind='sanitisation';batch=nextSan;ids=[];existingSan.add(batch);
  task=`You are a description sanitiser in a blind audit. Read ONLY ${B}/sanitisation/raw_${batch}.json, which contains only effect_id and description. Write ${B}/sanitisation/clean_${batch}.json, a JSON array of {effect_id,description,locator_insufficient:boolean,inspection_note:string}. Keep constructs, conditions and outcome, and design numbers identifying conditions, doses, durations or scenarios (240-buyer vs 160-buyer stays). Remove observed results, analytic sample sizes, statistical estimates, result directions and success verdicts. Recast directional claims as neutral relationships. Review p <, n =, estimates and replicated/confirms but don't automatically reject legitimate design numbers. Inspect every record semantically. Mark unidentifiable neutral descriptions locator_insufficient. Time limit 10 minutes. Do not open other files, datasets, spreadsheets or repository instructions; do not search the repository; do not delegate further or commit. Return only counts and output paths, never source text.`;
 }else{
  candidate=candidate??q.find(x=>!existing.has(x.batch)&&!x.large)??q.find(x=>!existing.has(x.batch));
  if(!candidate)break;
  kind='extraction';batch=candidate.batch;ids=candidate.audit_ids;existing.add(batch);
  task=`${ins}\nAssigned input: ${candidate.input_path}\nAssigned audit_ids: ${ids.join(', ')}.\nThis is ${candidate.large?'a large-project primary-table extraction':'an ordinary work'}. ${candidate.attempt===2?'This is the ONE retry. Read existing assigned checkpoints, preserve completed fields, retry ONLY timeout/error fields. Any failures now remain terminal and unverified.':''} Output only the assigned IDs.`;
 }
 const result=parse(await tools.mcp__t3_code__delegate_task({clientRequestId:`fred-${kind}-${batch}-${candidate?.attempt===2?'retry1':'v1'}`,mode:'async',isolation:'shared',target:{providerInstanceId:'codex',model:'gpt-6.1-sol',options:{reasoningEffort:'medium'}},title:`${kind} ${batch}`,task}));
 if(result.providerInstanceId!=='codex'||result.model!=='gpt-6.1-sol'||!result.options?.some(v=>v.id==='reasoningEffort'&&v.value==='medium'))throw Error('Dispatch model mismatch');
 const record={kind,batch,attempt:candidate?.attempt??1,audit_ids:ids,large:candidate?.large??false,started_at:new Date().toISOString(),...result};
 await append('tasks.jsonl',record);active.push(record);const ri=retryQueue.findIndex(x=>x.batch===batch);if(ri>=0)retryQueue.splice(ri,1);dispatched.push({kind,batch,ids:ids.length});
}
text({active:active.length,cap,dispatched});
