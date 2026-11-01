/* Batch-first workflow. Approval records are persistent; application is always separate. */
const batchGroups=(CONTEXT.batch_review?.groups||[]).filter(g=>g.items.length);
let workflowReady=false;
function initializeWorkflow(){
  store.batch_approvals=store.batch_approvals||{};store.pairs=store.pairs||{};
  store.workflow=store.workflow||{stage:'batch'};workflowReady=true;renderSaveStatus();
}
function untouched(item){
  if(item.case_id){const r=store.records[item.case_id];return !r||(!r.decision&&!r.notes&&!r.legacy)}
  const linked=item.linked_case_id&&store.records[item.linked_case_id];return !store.pairs[item.id]&&(!linked||(!linked.decision&&!linked.notes&&!linked.legacy));
}
function bulkOutcomeSuspended(group){return ['replication_outcomes','reproduction_results'].includes(group.id)&&CONTEXT.review_reliability?.bulk_outcome_approval_enabled===false}
function approvedItem(item,group){
  if(CONTEXT.review_reliability?.holds?.[item.case_id])return false;
  if(item.case_id){const c=caseById.get(item.case_id),r=store.records[item.case_id];return c&&r&&!(r.batch_id&&bulkOutcomeSuspended(group))&&statusOf(c)==='approve'&&item.fields.every(f=>r.approved_fields?.includes(f))}
  if(item.linked_case_id&&store.records[item.linked_case_id]?.decision&&store.records[item.linked_case_id].decision!=='add_pair')return false;
  const r=store.pairs[item.id];return r?.decision==='add_pair'&&r.group_fingerprint===group.fingerprint;
}
function approvedOperations(){
  return batchGroups.flatMap(g=>g.items.filter(i=>approvedItem(i,g)).flatMap(i=>i.operations.map(op=>({...op,...(sharedReview?.attribution(i.case_id||i.id,i.case_id?'records':'pairs')||{}),approval_item_id:i.id,input_row_index:i.input_row_index??null,approved_at:(i.case_id?store.records[i.case_id]:store.pairs[i.id]).recorded_at}))));
}
function implementationFingerprint(){return fnv(JSON.stringify(approvedOperations()))}
function backupData(){flushNote();return {schema_version:3,app:'flora-audit-decision-review',review_reliability:CONTEXT.review_reliability||null,shared_review:sharedReview?.status()||null,baseline_sha256:CONTEXT.baseline_sha256,input_hash:INPUT_HASH,queue_sha256:QUEUE_HASH,exported_at:stamp(),canonical_changes_applied:false,decisions:exportRecords(),batch_approvals:store.batch_approvals,approved_missing_pairs:store.pairs,workflow:store.workflow}}
function implementationBundle(){
  const operations=approvedOperations(),safeIds=new Set(operations.map(x=>x.approval_item_id));
  return {...backupData(),bundle_type:'approved_flora_changes',implementation_fingerprint:implementationFingerprint(),
    implementation_rules:[
      'Bulk-approved replication/reproduction outcomes are suspended. Replace earlier downloaded bulk outcome bundles. Row 462 outcome correction is withheld.',
      'Check the baseline SHA-256 before applying any operation. Row indices are zero-based in that frozen snapshot.',
      'Check each full-record SHA-256 before applying all operations for that row atomically. Stop on a mismatch; do not rebase by row number.',
      'set_field replaces its named column. set_reproduction_axis updates only its named axis in the comma-separated outcome, preserving the other axis. Stop if the two-axis value cannot be parsed.',
      'add_confirmed_pair adds the specified study–original identity after checking for an existing pair. Its outcome is deliberately unassigned.',
      'Approvals outside operations are review instructions only. Resolve their dependencies and retrieve full source quotations before implementation. Public quote excerpts are not replacement quotations.',
      'Refresh dependent bibliography and derived identifiers together; never treat a registration-only source as a completed replication.'
    ],operations,operation_count:operations.length,
    additional_decisions_for_implementation_review:exportRecords().filter(r=>r.decision&&!safeIds.has(r.case_id)),
    skipped_stale_decisions:exportRecords().filter(r=>r.stale).map(r=>r.case_id)};
}
function approveBatch(group){
  if(bulkOutcomeSuspended(group)){notice(CONTEXT.review_reliability.bulk_outcome_reason);return}
  const pending=group.items.filter(untouched);if(!pending.length)return;
  const when=stamp(),prior=JSON.stringify(store);
  if(!transaction(()=>{
    for(const item of pending){
      if(item.case_id){const c=caseById.get(item.case_id);store.records[c.id]={case_id:c.id,row:c.row,decision:'approve',decision_label:'Approved in '+group.title,approved_fields:item.fields,proposal:proposalOf(c,item.fields),proposal_fingerprint:snapshotOf(c),expected_before_full_record_sha256:rowCtx(c)?.sha,batch_id:group.id,group_fingerprint:group.fingerprint,recorded_at:when,applied:false}}
      else store.pairs[item.id]={case_id:item.id,decision:'add_pair',group_id:group.id,group_fingerprint:group.fingerprint,recorded_at:when,applied:false};
    }
    store.batch_approvals[group.id]={fingerprint:group.fingerprint,item_ids:pending.map(i=>i.id),recorded_at:when};
  }))return;
  lastUndo=()=>{const previous=JSON.parse(prior);if(!transaction(()=>{
    for(const item of pending){const records=item.case_id?store.records:store.pairs,key=item.case_id||item.id;if(records[key]?.recorded_at!==when)return;const old=(item.case_id?previous.records:previous.pairs)?.[key];if(old)records[key]=old;else delete records[key]}
    if(store.batch_approvals[group.id]?.recorded_at===when){if(previous.batch_approvals?.[group.id])store.batch_approvals[group.id]=previous.batch_approvals[group.id];else delete store.batch_approvals[group.id]}
  }))return;lastUndo=null;renderAll();showToast('Batch approval undone. Later individual decisions kept.')};
  renderAll();showToast(`${pending.length} approvals queued for shared save.`,lastUndo);
}
function undoBatch(group){
  const approval=store.batch_approvals[group.id];if(!approval)return;
  if(!transaction(()=>{
    for(const id of approval.item_ids){const r=store.records[id]||store.pairs[id];if(!r||r.recorded_at!==approval.recorded_at||!(r.batch_id===group.id||r.group_id===group.id))continue;if(store.records[id])delete store.records[id];else delete store.pairs[id]}
    delete store.batch_approvals[group.id];
  }))return;renderAll();
}
function setStage(stage){
  if(stage==='individual'&&approvedOperations().length&&store.workflow.downloaded_fingerprint!==implementationFingerprint())stage='download';
  if(!transaction(()=>{store.workflow.stage=stage}))return;
  if(stage==='individual'){state.show='open';$('show').value='open';state.queue='remaining'}
  renderAll();$('workflow').scrollTop=0;
}
async function downloadImplementation(){
  flushNote();if(sharedReview){const synced=await sharedReview.sync();if(!synced||!sharedReview.canDownload()){notice('Confirm all shared saves and resolve conflicts before downloading approved changes.');return}}
  const fingerprint=implementationFingerprint(),when=stamp();
  if(!transaction(()=>{store.workflow.downloaded_fingerprint=fingerprint;store.workflow.downloaded_at=when}))return;
  download('flora-approved-changes-'+when.slice(0,10)+'.json',JSON.stringify(implementationBundle(),null,2),'application/json');
  renderWorkflow();notice('Approved changes downloaded. Apply this file to FLoRA separately; the app has not applied it.');
}
function batchItemLine(item,group){
  const li=h('li',{},h('button',{class:'batch-item-title',type:'button','data-batch-item':item.id,onclick:()=>openBatchEvidence(item,group)},item.case_id?'Row '+item.input_row_index+' · '+item.title:item.title));
  for(const op of item.operations){
    if(op.operation==='add_confirmed_pair')li.append(h('small',{},op.work_key+' → '+op.original.authors+' ('+op.original.year+'). Outcome unassigned.'));
    else{const old=op.expected_before[op.field]??op.expected_before.outcome??op.expected_before.title_o;li.append(h('small',{},fieldName(op.field)+': '+shortValue(op.field,old)+' → '+shortValue(op.field,op.proposed_value)))}
  }
  li.append(h('button',{class:'batch-item-evidence',type:'button',onclick:()=>openBatchEvidence(item,group)},'Quotes & evidence'));
  return li;
}
function renderWorkflow(){
  if(!workflowReady)return;
  const stage=store.workflow.stage||'batch',individual=stage==='individual';
  $('workspace').hidden=!individual;$('queues').hidden=!individual;$('workflow').hidden=individual;
  const nav=$('workflow-nav');nav.replaceChildren();
  for(const [id,title] of [['batch','1. Review grouped proposals'],['download','2. Download to implement'],['individual','3. Individual decisions']])nav.append(h('button',{type:'button','aria-current':stage===id?'step':null,onclick:()=>setStage(id)},title));
  renderSaveStatus();if(individual)return;
  const root=$('workflow'),scroll=root.scrollTop,windowScroll=window.scrollY,keepScroll=lastWorkflowStage===stage;for(const list of root.querySelectorAll('[data-batch-group]'))batchScroll.set(list.dataset.batchGroup,list.scrollTop);lastWorkflowStage=stage;root.replaceChildren();
  if(stage==='batch'){
    root.append(h('p',{class:'callout'},CONTEXT.review_reliability?.bulk_outcome_reason||''));
    root.append(h('h2',{},'Review grouped proposals'),h('p',{class:'intro'},'Outcome changes require individual review of the evidence for the named original. Bulk approval is suspended for replication and reproduction outcomes. Confirmed missing-pair identities remain separately reviewable. Open any title to inspect quotes, the original-study identity and the reasoning. Individual choices you make there are kept when you approve the remaining batch.'));
    for(const g of batchGroups){
      const pending=g.items.filter(untouched),approved=g.items.filter(i=>approvedItem(i,g)),protectedCount=g.items.length-pending.length-approved.length;
      const card=h('section',{class:'batch-card'},h('h3',{},g.title),h('p',{},g.description),h('p',{},`${g.items.length} items · ${approved.length} approved · ${pending.length} available`+(protectedCount?` · ${protectedCount} with earlier decisions or notes`:'')));
      if(store.batch_approvals[g.id]&&store.batch_approvals[g.id].fingerprint!==g.fingerprint)card.append(h('p',{class:'notice'},'This set changed after your earlier approval. Earlier choices are kept; changed proposals require re-checking.'));
      const list=h('ol',{class:'batch-list','data-batch-group':g.id,onscroll:e=>{if(e.target.isConnected)batchScroll.set(g.id,e.target.scrollTop)}});for(const item of g.items)list.append(batchItemLine(item,g));const details=h('details',{open:batchExpanded.has(g.id),ontoggle:e=>{if(e.target.open)batchExpanded.add(g.id);else batchExpanded.delete(g.id)}},h('summary',{},'Inspect '+g.items.length+' items and their evidence'),list);card.append(details);const savedListScroll=batchScroll.get(g.id)||0;requestAnimationFrame(()=>{if(list.isConnected)list.scrollTop=savedListScroll});
      card.append(h('div',{class:'batch-controls'},h('button',{type:'button',class:'batch-button',disabled:!pending.length||bulkOutcomeSuspended(g),onclick:()=>approveBatch(g)},bulkOutcomeSuspended(g)?'Review outcome changes individually':pending.length?'Approve '+pending.length+' available items':'No untouched items to approve'),store.batch_approvals[g.id]?h('button',{type:'button',class:'tool',onclick:()=>undoBatch(g)},'Undo latest batch'):null));
      root.append(card);
    }
    root.append(h('p',{class:'intro'},'Individual review covers original-study relinks, type changes, record removals, source replacements, quote updates and policy choices. Missing-pair approval confirms identity only; it does not assign a replication result.'),h('footer',{},h('button',{type:'button',class:'batch-button',onclick:()=>setStage('download')},'Continue to download')));
  }else{
    const ops=approvedOperations(),rows=new Set(ops.filter(o=>o.input_row_index!=null).map(o=>o.input_row_index)).size,pairs=ops.filter(o=>o.operation==='add_confirmed_pair').length,current=store.workflow.downloaded_fingerprint===implementationFingerprint();
    root.append(h('h2',{},'Download approved changes'),h('p',{class:'intro'},'Download one implementation bundle before reviewing individual cases. It includes exact proposed values, checks against the audited snapshot, your approvals, and a backup of all decisions. Downloading does not change FLoRA.'),h('section',{class:'batch-card'},h('h3',{},`${rows} rows to correct · ${pairs} missing pairs to add`),h('p',{},ops.length+' operations ready. Quotes, policy choices and record actions remain explicit review instructions, outside these ready operations.'),h('button',{type:'button',class:'batch-button',onclick:downloadImplementation},'Download approved changes + decision backup'),h('p',{class:'muted'},current?'This version has been downloaded'+(store.workflow.downloaded_at?' · '+new Date(store.workflow.downloaded_at).toLocaleString():'')+'.':ops.length?'Download this version before continuing.':'No ready operations selected. You can download a backup or continue.')));
    root.append(h('footer',{},h('button',{type:'button',class:'batch-button secondary',onclick:()=>setStage('batch')},'Back to proposals'),h('button',{type:'button',class:'batch-button',disabled:!!ops.length&&!current,onclick:()=>setStage('individual')},'Continue to individual decisions')));
  }
  if(keepScroll){root.scrollTop=scroll;if(narrow())window.scrollTo({top:windowScroll,behavior:'instant'})}
}
function restoreBatchBackup(data){
  if(data.baseline_sha256&&data.baseline_sha256!==CONTEXT.baseline_sha256)throw Error('Backup belongs to a different audited snapshot.');
  for(const [key,value] of Object.entries(data.batch_approvals||{})){const old=store.batch_approvals[key];if(!old||String(value.recorded_at)>String(old.recorded_at))store.batch_approvals[key]=value}
  const items=new Set(batchGroups.flatMap(g=>g.items.map(i=>i.id)));
  for(const [key,value] of Object.entries(data.approved_missing_pairs||{})){if(!items.has(key))continue;const old=store.pairs[key];if(!old||String(value.recorded_at)>String(old.recorded_at))store.pairs[key]=value}
  // Keep this browser's current step. Imported approvals must be downloaded here.
}
QUEUES.unshift({id:'remaining',label:'Remaining decisions',test:c=>{const p=profile(c);return p.needs||p.items.length>0||p.missingOpen},note:'Cases with proposals or an unresolved decision. Batch-approved rows disappear when “Not decided” is selected.'});
queueById.remaining=QUEUES[0];
