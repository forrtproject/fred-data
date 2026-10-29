const root='/home/lukas/.t3/worktrees/fred-data/audit-fred-stats-2026-10/audit/fred_stats_2026-10';
const cycles=load('parentCycles')??10;
for(let cycle=0;cycle<cycles;cycle++){
 const cmd=`python3 '${root}/scripts/compare.py'\npython3 '${root}/scripts/prepare_adjudication.py'\npython3 '${root}/scripts/log_skips.py'\npython3 '${root}/scripts/report.py'`;
 let result=await tools.exec_command({cmd,max_output_tokens:1700,yield_time_ms:1000});let output=result.output;
 while(result.session_id && result.exit_code===undefined){result=await tools.write_stdin({session_id:result.session_id,chars:'',yield_time_ms:1000,max_output_tokens:1700});output+=result.output;}
 if(result.exit_code!==0)throw Error('Parent integration failed: '+JSON.stringify(result)+' '+output);
 text(output);
 const tick=(await tools.exec_command({cmd:`cat '${root}/scripts/tick.js'`,max_output_tokens:10000})).output;await eval(`(async()=>{${tick}})()`);
 const agy=(await tools.exec_command({cmd:`cat '${root}/scripts/agy_tick.js'`,max_output_tokens:10000})).output;await eval(`(async()=>{${agy}})()`);
 text({parent_cycle:cycle+1,time:new Date().toISOString()});await yield_control();
 if(cycle<cycles-1)await new Promise(r=>setTimeout(r,45000));
}
