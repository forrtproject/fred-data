// Run from functions.exec using AsyncFunction('tools','text', source)(tools,text).
const base='audit/flora_blind_2026-10';
const q=s=>"'"+s.replaceAll("'","'\\''")+"'";
const cmd=async s=>{let r=await tools.exec_command({cmd:s,max_output_tokens:16000});if(r.exit_code!==0)throw Error(r.output);return r.output;};
const py=async (...args)=>JSON.parse(await cmd('python3 '+base+'/scripts/controller.py '+args.map(q).join(' ')));
const record=async x=>{await cmd('python3 '+base+'/scripts/controller.py event '+q(JSON.stringify(x)));};
let p=await py('plan');
for(const e of p.active){
 let r=await tools.mcp__t3_code__task_status({taskId:e.taskId});let s=r.structuredContent;
 if(e.budget_seconds && ['running','queued','waiting'].includes(s?.status) && Date.now()-Date.parse(e.launched_at||e.at)>e.budget_seconds*1000){
  await tools.mcp__t3_code__task_cancel({taskId:e.taskId,reason:'Batch exceeded paper time budgets plus checkpoint overhead',clientRequestId:e.taskId+'-budget-cancel'});
  s={...s,status:'cancelled',summary:'Time budget exceeded; valid outputs retained and missing/failed works eligible for one retry.'};
 }
 if(!s){text(r);continue;}
 await record({taskId:e.taskId,status:s.status,summary:s.summary,pendingApproval:s.pendingApproval,hasPendingQuestion:s.hasPendingQuestion});
 if(s.status!=='running'&&s.status!=='queued')text({taskId:e.taskId,status:s.status,summary:s.summary});
}
p=await py('plan');
if(p.finish_due){text({finish_due:true,active:p.active});return;}
// Never dispatch before the adapter checks have passed.
let ok=await cmd('test -f '+base+'/adapter_check.json && cat '+base+'/adapter_check.json || true');
if(!ok || !JSON.parse(ok).passed){text('Waiting for adapter tests before coding dispatch.');return;}
while(p.coding_open && p.active.length<p.limit){
 let b=await py('prepare');if(!b)break;
 const r=await tools.mcp__t3_code__delegate_task({clientRequestId:b.clientRequestId,title:'Blind FLoRA '+b.batch,mode:'async',isolation:'shared',target:{providerInstanceId:'codex',model:'gpt-6.1-sol',options:{reasoningEffort:'medium'}},task:b.task});
 const s=r.structuredContent;
 if(!s){text(r);break;}
 await record({...b,task:undefined,taskId:s.taskId,status:s.status,launched_at:new Date().toISOString(),providerInstanceId:s.providerInstanceId,model:s.model,options:s.options});
 if(s.providerInstanceId!=='codex'||s.model!=='gpt-6.1-sol'||!s.options?.some(x=>x.id==='reasoningEffort'&&x.value==='medium'))throw Error('Requested model/options mismatch');
 text({batch:b.batch,status:s.status,taskId:s.taskId,files:b.files});
 p=await py('plan');
}
text({active:p.active.length,limit:p.limit,age_seconds:p.age_seconds,coding_open:p.coding_open});
