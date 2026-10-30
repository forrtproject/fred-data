// Run inside functions.exec; only this parent owns dispatch and integration.
const root='/home/lukas/.t3/worktrees/fred-data/audit-fred-stats-2026-10/audit/fred_stats_2026-10';
const quote=s=>"'"+s.replaceAll("'","'\\''")+"'";
const read=async path=>{const r=await tools.exec_command({cmd:'cat '+quote(path),max_output_tokens:16000});if(r.exit_code!==0||r.output.startsWith('Warning: truncated'))throw Error('Cannot read '+path);return r.output;};
const dir=root+'/mac_source_followup';
const queue=JSON.parse(await read(dir+'/validation_queue.json'));
const history=(await read(dir+'/validation_tasks.jsonl')).trim().split('\n').filter(Boolean).map(JSON.parse);
const latest={};for(const r of history)latest[r.batch]=r;
const statuses={};let active=0;
for(const r of Object.values(latest)){
 const result=await tools.mcp__t3_code__task_status({taskId:r.taskId});
 const data=result.structuredContent??JSON.parse(result.content.find(x=>x.type==='text').text);
 if(['running','queued','waiting'].includes(data.status)&&Date.now()-Date.parse(r.started_at)>12*60000){
  await tools.mcp__t3_code__task_cancel({taskId:r.taskId,reason:'12-minute follow-up blind extraction ceiling',clientRequestId:'stop-'+r.batch+'-v1'});
  statuses[r.batch]={status:'cancelled',reason:'12-minute extraction ceiling',taskId:r.taskId};
 }else{statuses[r.batch]={status:data.status,summary:data.summary,taskId:r.taskId};if(['running','queued','waiting'].includes(data.status))active++;}
}
const instructions=await read(root+'/worker_instructions.txt');
const launched=[];
for(const batch of queue){
 if(active>=3)break;
 if(latest[batch.batch])continue;
 const prompt=instructions.replaceAll('write one atomic JSON at audit/fred_stats_2026-10/extractions/<audit_id>.json','write one atomic JSON at YOUR_OUTPUT/<audit_id>.json')+
 '\n\nMAC RECOVERY BLIND VALIDATION OVERRIDES: Fresh BLIND extraction ONLY target_side in '+batch.input+'. Read only assigned input, named primary sources and extraction_schema.json. Respect source_version_note: manuscripts/proofs/supplements retain their version and may not establish missing main-article contents. No repository search, existing extractions/exports/baselines/acquisition ledgers, shipped values, other prompts, downloads, delegation or Git. Save ONLY '+batch.output+'/<audit_id>.json. NEVER canonical extractions/. Full schema required; unassigned side paper_unavailable/null/confident false placeholder. Only extract reported_success for replication targets; original-only leaves it null/paper_unavailable. Exact short quotations, precise page/table/section, uniquely matching study/outcome/sample/test, analytic sample role/exclusions, requested printed metric/test and p-bound. No metric conversions. Hard12minutes; checkpoint each row immediately. Return counts and paths.';
 const result=await tools.mcp__t3_code__delegate_task({task:prompt,title:'Validate recovered FReD source '+batch.batch,target:{providerInstanceId:'codex',model:'gpt-6.1-sol',options:{reasoningEffort:'medium'}},mode:'async',isolation:'shared',role:'research',clientRequestId:'fred-mac-validation-'+batch.batch+'-v1'});
 const data=result.structuredContent??JSON.parse(result.content.find(x=>x.type==='text').text);
 if(data.providerInstanceId!=='codex'||data.model!=='gpt-6.1-sol'||!data.options.some(x=>x.id==='reasoningEffort'&&x.value==='medium'))throw Error('Wrong validation provider/model/options');
 const record={...batch,taskId:data.taskId,childThreadId:data.childThreadId,status:data.status,started_at:new Date().toISOString()};
 const written=await tools.exec_command({cmd:'python3 - '+quote(JSON.stringify(record))+" <<'PY'\nimport json,sys\nfrom pathlib import Path\np=Path('audit/fred_stats_2026-10/source_followup/validation_tasks.jsonl')\nwith p.open('a') as f:f.write(json.dumps(json.loads(sys.argv[1]))+'\\n')\nPY",max_output_tokens:300});
 if(written.exit_code!==0)throw Error('Cannot retain delegated validation task');
 statuses[batch.batch]={status:data.status,taskId:data.taskId};launched.push(batch.batch);active++;
}
const written=await tools.exec_command({cmd:'python3 - '+quote(JSON.stringify(statuses))+" <<'PY'\nimport json,sys\nfrom pathlib import Path\np=Path('audit/fred_stats_2026-10/source_followup/validation_status.json');p.write_text(json.dumps(json.loads(sys.argv[1]),indent=2)+'\\n')\nPY",max_output_tokens:300});
if(written.exit_code!==0)throw Error('Cannot retain validation statuses');
text({active_validation_children:active,launched,undispatched:queue.filter(x=>!latest[x.batch]&&!launched.includes(x.batch)).length});
