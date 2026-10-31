const B='/home/lukas/.t3/worktrees/fred-data/audit-fred-stats-2026-10/audit/fred_stats_2026-10';
const read=async name=>{const r=await tools.exec_command({cmd:`cat '${B}/${name}'`,max_output_tokens:50000});if(r.exit_code!==0||r.output.startsWith('Warning: truncated'))throw Error('Cannot read complete adjudication control '+name);return r.output;};
const write=async(name,x)=>tools.exec_command({cmd:`cat > '${B}/${name}' <<'FRED_JSON_EOF'\n${JSON.stringify(x,null,2)}\nFRED_JSON_EOF`,max_output_tokens:100});
const append=async(name,x)=>tools.exec_command({cmd:`cat >> '${B}/${name}' <<'FRED_JSON_EOF'\n${JSON.stringify(x)}\nFRED_JSON_EOF`,max_output_tokens:100});
await tools.exec_command({cmd:`python3 '${B}/scripts/control.py' agy`,max_output_tokens:1000});
const control=JSON.parse(await read('agy_control.json'));const records=control.records;
const cleanup=await tools.exec_command({cmd:`python3 '${B}/scripts/cleanup_argon.py'`,max_output_tokens:1000});if(cleanup.exit_code!==0)throw Error(cleanup.output);
let states=control.states;
const latest={};for(const r of records)latest[r.key]=r;
for(const r of Object.values(latest)){
 if(states[r.key]?.terminal)continue;
 if(Date.now()-Date.parse(r.started_at)>12*60000){
  const stopped=await tools.exec_command({cmd:`python3 '${B}/scripts/stop_argon.py' '${r.key}'`,max_output_tokens:1000});
  if(stopped.exit_code!==0)throw Error(stopped.output);
  states[r.key]={terminal:true,attempt:r.attempt,validation:'failed',validation_error:'12-minute wall ceiling; '+stopped.output};continue;
 }
 try{
  const p=await tools.write_stdin({session_id:r.session_id,chars:'',yield_time_ms:1000,max_output_tokens:500});
  states[r.key]={terminal:p.exit_code!==undefined,exit_code:p.exit_code,attempt:r.attempt};
 }catch(e){states[r.key]={terminal:true,transport_error:String(e),attempt:r.attempt};}
}
await tools.exec_command({cmd:`python3 '${B}/scripts/validate_adjudication.py'`,max_output_tokens:3000});
const validation=JSON.parse(await read('adjudication_validation.json'));
for(const v of validation){if(states[v.key]){states[v.key].validation=v.status;states[v.key].validation_error=v.error;}}
const finished=await tools.exec_command({cmd:`python3 '${B}/scripts/completed_argon.py'`,max_output_tokens:1000});
if(finished.exit_code!==0)throw Error(finished.output);
for(const key of JSON.parse(finished.output)){
 if(states[key]?.terminal)continue;
 const stopped=await tools.exec_command({cmd:`python3 '${B}/scripts/stop_argon.py' '${key}'`,max_output_tokens:1000});
 if(stopped.exit_code!==0)throw Error(stopped.output);
 states[key]={...states[key],terminal:true,completion:'Complete validated final JSON stable for at least30seconds; exact owned CLI exit verified',cleanup:stopped.output};
}
// A queue was built before polling. Defer any bundle whose fields just acquired
// valid answers, even if its key changed with new coding context or regrouping.
// The next integration cycle keeps those answers and rebuilds remaining siblings.
const justResolved=new Set();
for(const v of validation){
 const record=latest[v.key];if(!record?.items || !['valid','partial'].includes(v.status))continue;
 const failed=new Set((v.failed_fields??[]).map(x=>`${x.audit_id}:${x.field}`));
 for(const item of record.items)if(!failed.has(`${item.audit_id}:${item.field}`))justResolved.add(`${!!record.focused_review}:${item.audit_id}:${item.field}`);
}
const manifest=JSON.parse(await read('run_manifest.json'));
const queue=JSON.parse(await read('adjudication_queue.json'));
let active=Object.values(latest).filter(x=>!states[x.key]?.terminal);
const exists=async name=>(await tools.exec_command({cmd:`test -f '${B}/${name}'`,max_output_tokens:100})).exit_code===0;
for(const a of queue){
 if(active.length>=4||Date.now()>=Date.parse(manifest.deadlines.adjudication))break;
 if(a.items.some(x=>justResolved.has(`${!!a.focused_review}:${x.audit_id}:${x.field}`)))continue;
 if(await exists(`adjudications/validated_${a.key}.json`))continue;
 const old=latest[a.key];
 if(old && (!states[a.key]?.terminal || old.attempt>=2))continue;
 if(active.some(x=>x.source_path===a.source_path))continue;
 const attempt=old?old.attempt+1:1;
 if(old)await tools.exec_command({cmd:`cp '${a.output}' '${a.output}.attempt1'`,max_output_tokens:100});
 const fileTransport=a.prompt_bytes>110000;
 const promptArg=fileTransport?`'FRED_AUDIT_PROMPT_FILE: ${a.prompt}
Read the complete task in that file and execute it exactly. End your response with the answer itself under a heading ## Answer. Put your whole result in your reply; do not create files or run commands.'`:`"$(cat '${a.prompt}')"`;
 const p=await tools.exec_command({cmd:`agy -p ${promptArg} --model "Gemini 4 Argon (High)" --sandbox --add-dir '${B}/texts' ${fileTransport?`--add-dir '${B}/adjudications'`:''} --print-timeout 10m > '${a.output}' 2>&1`,yield_time_ms:1000,max_output_tokens:500});
 const record={...a,...p,output:a.output,launcher_output:p.output,transport:fileTransport?'read_only_prompt_file':'inline_argument',attempt,started_at:new Date().toISOString()};latest[a.key]=record;states[a.key]={terminal:p.exit_code!==undefined,attempt,exit_code:p.exit_code};active.push(record);await append('adjudication_tasks.jsonl',record);
 for(const item of a.items)await append('disagreement_decisions.jsonl',{...item,classification:'non_obvious',reason:'Not established as rounding, documented direction reversal, known different target, or visible transcription slip; independent adjudication required.',evidence_location:a.source_path,adjudication_key:a.key});
}
await write('adjudication_status.json',states);
text({argon_active:active.length,validated_this_tick:validation.filter(v=>v.status==='valid').length});
