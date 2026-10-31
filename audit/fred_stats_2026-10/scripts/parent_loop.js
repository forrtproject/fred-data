const root='/home/lukas/.t3/worktrees/fred-data/audit-fred-stats-2026-10/audit/fred_stats_2026-10';
const cycles=load('parentCycles')??60;
const manifest=JSON.parse((await tools.exec_command({cmd:`cat '${root}/run_manifest.json'`,max_output_tokens:3000})).output);
const adjudicationCutoff=Date.parse(manifest.deadlines.adjudication),hardFinish=Date.parse(manifest.deadlines.finish);
for(let cycle=0;cycle<cycles;cycle++){
 if(Date.now()>=hardFinish){text('Hard finish reached; parent must finalise immediately.');break;}
 const cmd=`python3 '${root}/scripts/compare.py'\npython3 '${root}/scripts/prepare_adjudication.py'\npython3 '${root}/scripts/log_skips.py'\npython3 '${root}/scripts/report.py'`;
 let result=await tools.exec_command({cmd,max_output_tokens:1700,yield_time_ms:1000});let output=result.output;
 while(result.session_id && result.exit_code===undefined){result=await tools.write_stdin({session_id:result.session_id,chars:'',yield_time_ms:1000,max_output_tokens:1700});output+=result.output;}
 if(result.exit_code!==0)throw Error('Parent integration failed: '+JSON.stringify(result)+' '+output);
 // All blind extraction and locator-revisit children are complete; only adjudication remains.
 const agy=(await tools.exec_command({cmd:`cat '${root}/scripts/agy_tick.js'`,max_output_tokens:10000})).output;await eval(`(async()=>{${agy}})()`);
 const state=await tools.exec_command({cmd:`python3 - <<'PY'\nimport json\nfrom pathlib import Path\nb=Path('${root}');p=json.loads((b/'progress.json').read_text());q=json.loads((b/'adjudication_queue.json').read_text());s=json.loads((b/'adjudication_status.json').read_text())\nprint(json.dumps({'coverage':p['coverage'],'confirmed_errors':len(p['confirmed_errors']),'queued_papers':len(q),'queued_fields':sum(len(a['items']) for a in q),'active':sum(not a.get('terminal') for a in s.values())}))\nPY`,max_output_tokens:1000});
 if(state.exit_code!==0)throw Error(state.output);
 const progress=JSON.parse(state.output);text({parent_cycle:cycle+1,time:new Date().toISOString(),...progress});await yield_control();
 if(!progress.active && (!progress.queued_papers || Date.now()>=adjudicationCutoff))break;
 if(cycle<cycles-1)await new Promise(r=>setTimeout(r,25000));
}
