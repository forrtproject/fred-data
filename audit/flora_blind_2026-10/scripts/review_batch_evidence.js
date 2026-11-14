/* Inspect a batch item in place; opening evidence never records an approval. */
const batchEvidenceState={item:null,group:null,data:null,promise:null,error:'',drafts:new Map()};
const batchExpanded=new Set(),batchScroll=new Map();
let lastWorkflowStage=null;
async function loadBatchEvidence(){
  if(batchEvidenceState.data)return batchEvidenceState.data;
  if(batchEvidenceState.promise)return batchEvidenceState.promise;
  batchEvidenceState.promise=(async()=>{const response=await fetch('batch_evidence.json',{cache:'no-store'});if(!response.ok)throw Error('Evidence file returned HTTP '+response.status);const raw=await response.text();if(await reviewHash(raw)!==CONTEXT.batch_evidence_sha256)throw Error('Evidence file does not match this app. Reload the app to get the current version.');const data=JSON.parse(raw);if(data.baseline_sha256!==CONTEXT.baseline_sha256||batchGroups.some(g=>g.items.some(i=>!data.items[i.id])))throw Error('Evidence coverage does not match the approved sets.');batchEvidenceState.data=data;batchEvidenceState.error='';return data})().catch(error=>{batchEvidenceState.promise=null;batchEvidenceState.error=error.message;throw error});
  return batchEvidenceState.promise;
}
function openBatchEvidence(item,group){
  batchEvidenceState.item=item;batchEvidenceState.group=group;
  const dialog=$('batch-evidence');if(!dialog.open)dialog.showModal();renderBatchEvidence();
  loadBatchEvidence().then(()=>{if(dialog.open)renderBatchEvidence()}).catch(()=>{if(dialog.open)renderBatchEvidence()});
}
function navigateBatchEvidence(delta){const group=batchEvidenceState.group,index=group.items.findIndex(i=>i.id===batchEvidenceState.item.id);const next=group.items[index+delta];if(next)openBatchEvidence(next,group)}
function batchPassages(proofs){
  const section=h('div',{class:'batch-passages'}),seen=new Set();
  for(const proof of proofs||[]){if(!proof.quote||seen.has(proof.quote))continue;seen.add(proof.quote);
    const label=unique([proof.section,proof.location].map(locText)).join(' · ')||'Supporting passage';
    const concise=label.length>150&&label.indexOf('(')>0?label.slice(0,label.indexOf('(')).trim():label;
    section.append(h('figure',{class:'batch-passage'},h('figcaption',{},concise),concise!==label?h('details',{class:'more-text'},h('summary',{},'All cited locations'),h('p',{class:'quote-loc'},label)):null,quoteBlock(proof.quote,[proof.quote_is_excerpt?'Literal source excerpt':'Cited passage']),proof.source_verified?h('small',{class:'muted'},'Source hash and quote offsets checked.'):null));
  }
  return section;
}
function batchEvidenceContent(item,data){
  const body=h('div',{class:'batch-evidence-copy'});
  if(item.case_id){
    const c=caseById.get(item.case_id),rc=rowCtx(c),profileData=profile(c);
    body.append(h('section',{},h('h3',{},'What would change'),h('p',{},item.operations.map(op=>fieldName(op.field)+': '+shortValue(op.field,current(c,op.field))+' → '+shortValue(op.field,op.proposed_value)).join('; '))));
    body.append(h('section',{},h('h3',{},'Original study being retested'),citation(rc?.o),h('div',{class:'links'},byline(c))));
    for(const field of item.fields){const review=data?.fields?.[field]||{},audit=c.evidence?.[field]||{};
      const section=h('section',{'aria-label':'Evidence for '+fieldName(field)},h('h3',{},'Why change the '+fieldName(field)+'?'));
      const reason=review.rationale||review.reason||audit.reason;
      const cited=[...(review.quoted_passages||[])].sort((a,b)=>Number(String(b.section).toLowerCase().includes('end of cited passage'))-Number(String(a.section).toLowerCase().includes('end of cited passage')));
      const proofs=[...cited,...(review.proofs||[])];
      if(!proofs.length&&audit.quote)proofs.push({quote:audit.quote,location:audit.location});
      section.append(batchPassages(proofs.slice(0,1)));
      if(proofs.length>1)section.append(h('details',{class:'more-text'},h('summary',{},'More quoted evidence ('+(proofs.length-1)+')'),batchPassages(proofs.slice(1))));
      section.append(h('h4',{},'How the review reached this value'));
      if(reason)section.append(reasonBlock(reason));
      else section.append(h('p',{class:'muted'},'No separate reasoning was recorded. Inspect the source passages and linked audit record.'));
      if(review.reason&&review.reason!==reason)section.append(h('details',{class:'more-text'},h('summary',{},'Earlier source reasoning'),h('p',{class:'reason'},rich(review.reason))));
      const contrary=review.contrary_evidence||(CONTEXT.contrary||{})[c.row]?.[field];if(contrary?.length)section.append(h('details',{class:'more-text'},h('summary',{},'Contrary evidence and how it was addressed'),renderDetail(contrary)));
      if(review.limits||review.missing_evidence_or_policy_choice)section.append(h('details',{class:'more-text'},h('summary',{},'Scope and limits'),renderDetail(review.limits||review.missing_evidence_or_policy_choice)));
      body.append(section);
    }
    const record=renderCard(c,profileData);record.querySelectorAll('.include').forEach(control=>control.remove());const context=h('details',{class:'more-text'},h('summary',{},'Study identity, classification and full record'),record,renderEvidence(c,profileData));body.append(context);
    body.append(h('p',{class:'links'},doiLink(c.work),...(c.primary_evidence_urls||[]).map(url=>extLink(url,'Open verified primary report'))));
  }else{
    const op=item.operations[0];body.append(h('section',{},h('h3',{},'Proposed missing pair'),h('p',{class:'sub'},'Replicating work'),citation(data?.replication||{doi:op.work_key}),h('p',{class:'sub'},'Original study to add'),citation(op.original),h('p',{class:'callout'},'This approval adds the pair’s identity. Its replication outcome remains unassigned.')));
    const pairProofs=data?.proofs||[];const why=h('section',{},h('h3',{},'Source evidence for the missing pair'),batchPassages(pairProofs.slice(0,1)));if(pairProofs.length>1)why.append(h('details',{class:'more-text'},h('summary',{},'More quoted evidence ('+(pairProofs.length-1)+')'),batchPassages(pairProofs.slice(1))));why.append(h('h4',{},'Why this is a distinct, missing original'),reasonBlock(data?.reason||'Loading the source-confirmation reasoning…'));body.append(why);
    if(data?.already_in_flora)body.append(h('details',{class:'more-text'},h('summary',{},'Pairs FLoRA already has for this work ('+data.already_in_flora.length+')'),h('ul',{class:'plain'},data.already_in_flora.map(r=>h('li',{},'Row '+r.row+': ',citation(r))))));
    body.append(h('p',{class:'links'},doiLink(op.work_key),doiLink(op.original.doi)));
  }
  if(data)body.append(h('p',{class:'muted'},'Published quotes are excerpts. Source locations are shown above; open the linked reports to read the surrounding text.'));
  for(const a of body.querySelectorAll('a[href^="#row:"]')){const target=a.getAttribute('href').slice(1);const group=batchGroups.find(g=>g.items.some(i=>i.case_id===target));if(group)a.onclick=e=>{e.preventDefault();openBatchEvidence(group.items.find(i=>i.case_id===target),group)};else a.replaceWith(document.createTextNode(a.textContent))}
  return body;
}
function renderBatchEvidence(){
  const item=batchEvidenceState.item,group=batchEvidenceState.group;if(!item||!group)return;
  const data=batchEvidenceState.data?.items[item.id],index=group.items.findIndex(i=>i.id===item.id),body=$('batch-evidence-body');
  $('batch-evidence-title').textContent=item.case_id?'Row '+item.input_row_index+' · '+item.title:item.title;
  $('batch-evidence-position').textContent=group.title+' · '+(index+1)+' of '+group.items.length;
  $('batch-evidence-prev').disabled=index===0;$('batch-evidence-next').disabled=index===group.items.length-1;
  body.replaceChildren();
  if(batchEvidenceState.error)body.append(h('p',{class:'callout'},batchEvidenceState.error),h('button',{type:'button',class:'tool',onclick:()=>{loadBatchEvidence().then(renderBatchEvidence).catch(renderBatchEvidence)}},'Retry evidence download'));
  else if(!data)body.append(h('p',{class:'muted',role:'status'},'Loading the detailed source passages…'));
  body.append(batchEvidenceContent(item,data));body.scrollTop=0;
  const decision=item.case_id?store.records[item.case_id]:store.pairs[item.id];
  const controls=$('batch-evidence-controls');controls.replaceChildren();
  const name=h('input',{id:'batch-evidence-reviewer',type:'text',maxlength:120,placeholder:'Name shown to other reviewers',oninput:e=>{$('reviewer-name').value=e.target.value;prefs.reviewer=e.target.value;savePrefs()}});name.value=$('reviewer-name').value;
  const note=h('textarea',{id:'batch-evidence-note',rows:2,placeholder:'Optional note, saved with your decision',oninput:e=>batchEvidenceState.drafts.set(item.id,e.target.value)});note.value=batchEvidenceState.drafts.get(item.id)??decision?.notes??'';
  controls.append(h('details',{class:'batch-item-note'},h('summary',{},'Add a note or check your reviewer name'),h('label',{for:name.id},'Your name'),name,h('label',{for:note.id},'Note'),note));
  const codes=item.case_id?[['approve','Approve this change'],['keep_current','Keep FLoRA as it is'],['follow_up','Needs follow-up']]:[['add_pair','Add this pair'],['reject_pair','Do not add this pair'],['follow_up','Needs follow-up']];
  controls.append(h('div',{class:'batch-item-actions'},codes.map(([code,label])=>h('button',{type:'button',class:'batch-button'+(code==='approve'||code==='add_pair'?'':' secondary'),disabled:!data,'aria-pressed':decision?.decision===code?'true':'false',onclick:()=>decideBatchEvidence(code,label)},label))));
  controls.append(h('p',{id:'batch-evidence-save',class:'muted',role:'status'},decision?.decision?'Current decision: '+statusLabel(decision.decision)+' · '+(decision.reviewer||'reviewer'): 'Opening evidence records no decision. Individual choices are preserved when the rest of the batch is approved.'));
}
function decideBatchEvidence(code,label){
  const item=batchEvidenceState.item,group=batchEvidenceState.group;if(!batchEvidenceState.data?.items[item.id])return;
  const reviewer=$('batch-evidence-reviewer');if(!reviewer.value.trim()){$('batch-evidence-controls').querySelector('details').open=true;$('batch-evidence-save').textContent='Enter your name before recording a decision.';reviewer.focus();return}
  const when=stamp(),note=$('batch-evidence-note').value;
  const saved=transaction(()=>{
    if(item.case_id){const c=caseById.get(item.case_id);const record={...(store.records[c.id]||{}),case_id:c.id,row:c.row,decision:code,decision_label:label,approved_fields:code==='approve'?item.fields:[],option:null,record_action:null,proposal:proposalOf(c,item.fields),proposal_fingerprint:snapshotOf(c),expected_before_full_record_sha256:rowCtx(c)?.sha,notes:note,recorded_at:when,applied:false};delete record.batch_id;delete record.group_fingerprint;store.records[c.id]=record}
    else{store.pairs[item.id]={case_id:item.id,decision:code,decision_label:label,group_id:group.id,group_fingerprint:group.fingerprint,notes:note,recorded_at:when,applied:false};if(item.linked_case_id){const c=caseById.get(item.linked_case_id);store.records[c.id]={case_id:c.id,row:c.row,decision:code,decision_label:label,proposal_fingerprint:snapshotOf(c),notes:note,recorded_at:when,applied:false}}}
  });
  if(!saved){$('batch-evidence-save').textContent=$('notice').textContent;return}
  renderAll();renderBatchEvidence();$('batch-evidence-save').textContent='Decision queued for shared save. The batch will preserve this choice.';
}
$('batch-evidence-close').onclick=()=>$('batch-evidence').close();
$('batch-evidence-prev').onclick=()=>navigateBatchEvidence(-1);$('batch-evidence-next').onclick=()=>navigateBatchEvidence(1);
$('batch-evidence').addEventListener('close',()=>{const id=batchEvidenceState.item?.id;batchEvidenceState.item=null;const button=[...document.querySelectorAll('[data-batch-item]')].find(b=>b.dataset.batchItem===id);button?.focus({preventScroll:true})});

$('batch-evidence-quotes').onclick=()=>{const body=$('batch-evidence-body'),quote=body.querySelector('.batch-passage');if(quote)body.scrollTop+=quote.getBoundingClientRect().top-body.getBoundingClientRect().top-12};
