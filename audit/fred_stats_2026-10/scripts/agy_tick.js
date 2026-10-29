const B='/home/lukas/.t3/worktrees/fred-data/audit-fred-stats-2026-10/audit/fred_stats_2026-10';
const read=async name=>{const r=await tools.exec_command({cmd:`cat '${B}/${name}'`,max_output_tokens:50000});if(r.exit_code!==0||r.output.startsWith('Warning: truncated'))throw Error('Cannot read complete adjudication control '+name);return r.output;};
const write=async(name,x)=>tools.exec_command({cmd:`cat > '${B}/${name}' <<'FRED_JSON_EOF'\n${JSON.stringify(x,null,2)}\nFRED_JSON_EOF`,max_output_tokens:100});
const append=async(name,x)=>tools.exec_command({cmd:`cat >> '${B}/${name}' <<'FRED_JSON_EOF'\n${JSON.stringify(x)}\nFRED_JSON_EOF`,max_output_tokens:100});
await tools.exec_command({cmd:`python3 '${B}/scripts/control.py' agy`,max_output_tokens:1000});
const control=JSON.parse(await read('agy_control.json'));const records=control.records;
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
const manifest=JSON.parse(await read('run_manifest.json'));
const queue=JSON.parse(await read('adjudication_queue.json'));
let active=Object.values(latest).filter(x=>!states[x.key]?.terminal);
const exists=async name=>(await tools.exec_command({cmd:`test -f '${B}/${name}'`,max_output_tokens:100})).exit_code===0;
for(const a of queue){
 if(active.length>=4||Date.now()>=Date.parse(manifest.deadlines.adjudication))break;
 if(await exists(`adjudications/validated_${a.key}.json`))continue;
 const old=latest[a.key];
 if(old && (!states[a.key]?.terminal || old.attempt>=2))continue;
 if(active.some(x=>x.source_path===a.source_path))continue;
 const attempt=old?old.attempt+1:1;
 if(old)await tools.exec_command({cmd:`cp '${a.output}' '${a.output}.attempt1'`,max_output_tokens:100});
 const p=await tools.exec_command({cmd:`agy -p "$(cat '${a.prompt}')" --model "Gemini 4 Argon (High)" --sandbox --add-dir '${B}/texts' --print-timeout 10m > '${a.output}' 2>&1`,yield_time_ms:1000,max_output_tokens:500});
 const record={...a,...p,attempt,started_at:new Date().toISOString()};latest[a.key]=record;states[a.key]={terminal:p.exit_code!==undefined,attempt,exit_code:p.exit_code};active.push(record);await append('adjudication_tasks.jsonl',record);
 for(const item of a.items)await append('disagreement_decisions.jsonl',{...item,classification:'non_obvious',reason:'Not established as rounding, documented direction reversal, known different target, or visible transcription slip; independent adjudication required.',evidence_location:a.source_path,adjudication_key:a.key});
}
await write('adjudication_status.json',states);
text({argon_active:active.length,validated_this_tick:validation.filter(v=>v.status==='valid').length});
