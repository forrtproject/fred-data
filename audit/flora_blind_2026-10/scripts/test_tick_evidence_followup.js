// No T3 calls: run the actual tick against in-memory tools and parent commands.
const fs=require('fs');
const assert=require('assert/strict');
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
const tick=new AsyncFunction('tools','text',fs.readFileSync(__dirname+'/tick_evidence_followup.js','utf8'));
async function main(){
 let tasks=[], intent=null, next=1, calls=[], events=[], fail=true;
 const pyReply=value=>({exit_code:0,output:JSON.stringify(value)});
 const plan=()=>({status:'active',active:tasks.filter(t=>t.status==='running'),slot_cost:tasks.filter(t=>t.status==='running').reduce((n,t)=>n+t.slot_cost,0),luna_active:0,luna_pending:[],luna_limit:3,luna_completed:0,luna_total:0,additional_infrastructure_slots:0,combined_ceiling:10});
 const tools={exec_command:async({cmd})=>{
  if(cmd.includes("'plan'"))return pyReply(plan());
  if(cmd.includes("'reconcile-candidate-cli'")){events.push('reconcile');return pyReply({});}
  if(cmd.includes("'candidate-cli-dispatch'")){
   if(cmd.includes('ACTUAL')){
    events.push('register-before-control');tasks=[{taskId:'ACTUAL',status:'running',lane:'candidate_cli',slot_cost:5}];intent=null;next++;return pyReply({taskId:'ACTUAL'});
   }
   if(tasks.some(t=>t.status==='running'))return pyReply(null);
   intent ||= {snapshot:'snap',workers:4,round:next,clientRequestId:'round-'+next};
   return pyReply(intent);
  }
  if(cmd.includes("'field-dispatch'"))return pyReply(null);
  if(cmd.includes("'register'")){events.push('status-register');return pyReply({});}
  if(cmd.includes("'prepare-candidate-review'"))return pyReply(null);
  throw Error('Unexpected mock command '+cmd);
 },mcp__t3_code__delegate_task:async request=>{
  calls.push(request);
  if(fail){fail=false;throw Error('mock lost response');}
  return {structuredContent:{taskId:'ACTUAL',status:'running',providerInstanceId:'codex',model:'gpt-6.1-sol',options:[{id:'reasoningEffort',value:'medium'},{id:'serviceTier',value:'default'}]}};
 },mcp__t3_code__task_status:async({taskId})=>({structuredContent:{taskId,status:'running'}})};
 await assert.rejects(tick(tools,()=>{}),/mock lost response/);
 await tick(tools,()=>{});
 assert.equal(calls.length,2);
 assert.equal(calls[0].clientRequestId,calls[1].clientRequestId);
 assert.equal(calls[1].target.model,'gpt-6.1-sol');
 assert.deepEqual(calls[1].target.options,{reasoningEffort:'medium',serviceTier:'default'});
 assert.match(calls[1].task,/FIRST read/);
 assert.match(calls[1].task,/range\(60\)/);
 assert.match(calls[1].task,/'--max-calls',str\(r\['workers'\]\)/);
 assert.match(calls[1].task,/'--owner-task-id',r\['taskId'\]/);
 assert.match(calls[1].task,/clientRequestId/);
 assert.ok(events.indexOf('reconcile')<events.indexOf('register-before-control'));
 await tick(tools,()=>{});
 assert.equal(calls.length,2,'active coordinator must suppress second dispatch');
 assert.equal(next,2);
 const wrongTools={...tools,mcp__t3_code__task_status:async()=>({structuredContent:{taskId:'UNOWNED',status:'completed'}})};
 await assert.rejects(tick(wrongTools,()=>{}),/exact owned task/);
 let collected=0;
 const yieldedTools={...tools,
  exec_command:async request=>request.cmd.includes("'reconcile-candidate-cli'")
   ?{session_id:9123,output:'{"collected":'}:tools.exec_command(request),
  write_stdin:async request=>{
   assert.equal(request.session_id,9123);
   collected++;
   return {exit_code:0,output:'true}'};
  }};
 await tick(yieldedTools,()=>{});
 assert.equal(collected,1,'yielded reconciliation must finish before dispatch');
 // Independent field lifecycle: every tool is an in-memory mock. A missing
 // mock method fails the test; no T3/tool transport is imported or invoked.
 let fieldTasks=[],fieldIntent=null,fieldNext=1,fieldCalls=[],fieldEvents=[],lost=true;
 const fieldTools={exec_command:async({cmd})=>{
  if(cmd.includes("'plan'"))return pyReply({...plan(),active:fieldTasks.filter(t=>t.status==='running'),slot_cost:fieldTasks.some(t=>t.status==='running')?4:0});
  if(cmd.includes("'reconcile-candidate-cli'"))return pyReply(null);
  if(cmd.includes("'candidate-cli-dispatch'"))return pyReply(null);
  if(cmd.includes("'prepare-candidate-review'"))return pyReply(null);
  if(cmd.includes("'register'"))return pyReply({});
  if(cmd.includes("'field-dispatch'")){
   if(cmd.includes('FIELD-ACTUAL')){
    fieldEvents.push('register-actual');
    fieldTasks=[{taskId:'FIELD-ACTUAL',status:'running',lane:'argon_runner',slot_cost:4}];
    fieldEvents.push('publish-control');fieldIntent=null;fieldNext++;
    return pyReply({});
   }
   if(fieldTasks.some(t=>t.status==='running'))return pyReply(null);
   fieldIntent ||= {round:fieldNext,workers:1,max_calls:1,snapshot_sha256:'HASH',clientRequestId:'field-round-'+fieldNext};
   return pyReply(fieldIntent);
  }
  throw Error('Unexpected field mock command '+cmd);
 },mcp__t3_code__delegate_task:async request=>{
  fieldCalls.push(request);
  if(lost){lost=false;throw Error('mock field lost response');}
  return {structuredContent:{taskId:'FIELD-ACTUAL',status:'running',providerInstanceId:'codex',model:'gpt-6.1-sol',options:{reasoningEffort:'medium',serviceTier:'default'}}};
 },mcp__t3_code__task_status:async({taskId})=>({structuredContent:{taskId,status:'running'}})};
 await assert.rejects(tick(fieldTools,()=>{}),/mock field lost response/);
 await tick(fieldTools,()=>{});
 assert.equal(fieldCalls.length,2);
 assert.equal(fieldCalls[0].clientRequestId,fieldCalls[1].clientRequestId);
 assert.equal(fieldCalls[1].target.model,'gpt-6.1-sol');
 assert.deepEqual(fieldCalls[1].target.options,{reasoningEffort:'medium',serviceTier:'default'});
 assert.match(fieldCalls[1].task,/range\(60\)/);
 assert.match(fieldCalls[1].task,/'--workers','1','--max-calls','1','--owner-task-id',r\['taskId'\]/);
 assert.match(fieldCalls[1].task,/'--control',str\(p\)/);
 assert.match(fieldCalls[1].task,/retain and collect/);
 assert.deepEqual(fieldEvents,['register-actual','publish-control']);
 await tick(fieldTools,()=>{});
 assert.equal(fieldCalls.length,2,'active field coordinator suppresses duplicate round');
 fieldTasks[0].status='completed';
 await tick(fieldTools,()=>{});
 assert.equal(fieldCalls.length,3);
 assert.notEqual(fieldCalls[2].clientRequestId,fieldCalls[1].clientRequestId);
 console.log('tick mocked dispatch/retry/identity tests passed');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
