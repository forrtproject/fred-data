/* Shared Google-backed decision log; browser storage is a pending-write cache. */
function createSharedReview(config){
  const newId=()=>globalThis.crypto?.randomUUID?.()||Date.now().toString(36)+'-'+Array.from(globalThis.crypto.getRandomValues(new Uint32Array(4)),x=>x.toString(16)).join('-');
  const S=FloraSharedState,scope=config.project,baseline=CONTEXT.baseline_sha256;
  let tab=readSession('flora-review-tab');if(!tab){tab=newId();try{sessionStorage.setItem('flora-review-tab',tab)}catch(e){}}
  const prefix='flora-shared-outbox-'+scope+':',key=prefix+tab,legacyKey='flora-browser-backup-'+scope;
  function readSession(key){try{return sessionStorage.getItem(key)}catch(e){return null}}
  let outbox=readJSON(key,[])||[],events=[],model=S.empty(),ready=false,busy=false,error='',timer=null,again=false,prepared=null,lastSync=null,currentSync=null;
  let client=readJSON('flora-review-client-id',null);if(!client){client=newId();try{localStorage.setItem('flora-review-client-id',JSON.stringify(client))}catch(e){}}
  let carryover=readJSON(legacyKey,null);
  if(store.shared_scope!==scope){
    if(Object.keys(store.records||{}).length||Object.keys(store.pairs||{}).length){carryover={...store};try{localStorage.setItem(legacyKey,JSON.stringify(carryover))}catch(e){}}
    store={version:4,shared_scope:scope,records:{},pairs:{},batch_approvals:{},resolutions:{},workflow:{stage:'batch'}};persist();
  }
  function writeOutbox(value){const payload=JSON.stringify(value);localStorage.setItem(key,payload);if(localStorage.getItem(key)!==payload)throw Error('Pending-write storage failed');outbox=value}
  function pendingAll(){const seen=new Set(),all=[];for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(!k.startsWith(prefix))continue;for(const event of readJSON(k,[])||[]){if(!seen.has(event.id)){seen.add(event.id);all.push(event)}}}return all.sort((a,b)=>a.created_at.localeCompare(b.created_at))}
  function stateWithPending(){return S.reduce(events.concat(pendingAll()),baseline)}
  function display(){
    const status=$('save-status');
    if(savingFailed){status.textContent='Not saved — browser storage failed. Export a backup before closing.';return}
    if(!ready)status.textContent=error?'Shared review unavailable: '+error+'. Retry to load decisions.':'Loading shared decisions…';
    else if(model.conflicts.length)status.textContent=`${model.conflicts.length} conflicting change${model.conflicts.length===1?' needs':'s need'} review. Shared decisions are preserved.`;
    else if(pendingAll().length)status.textContent=`${pendingAll().length} change${pendingAll().length===1?'':'s'} waiting for shared confirmation`+(error?' · '+error:'…');
    else status.textContent='Saved for all reviewers'+(lastSync?' · checked '+new Date(lastSync).toLocaleTimeString():'')+(busy?' · refreshing…':error?' · refresh failed: '+error:'');
    const carry=$('publish-browser');if(carry){carry.hidden=!carryover;carry.disabled=!ready;carry.textContent='Publish previous browser decisions'+(carryover?' ('+(Object.keys(carryover.records||{}).length+Object.keys(carryover.pairs||{}).length)+')':'')}
    const banner=$('shared-conflicts');if(!banner)return;banner.replaceChildren();banner.hidden=!model.conflicts.length;
    for(const conflict of model.conflicts){const event=conflict.event;
      const card=h('section',{class:'batch-card'},h('h3',{},'Conflicting change by '+event.reviewer),h('p',{},'Another reviewer changed the same decision before this change arrived. Nothing from this conflicting action has been applied. Choose which version to keep.'));
      const list=h('ul');for(const p of conflict.mismatches){const current=model[p.collection][p.key];list.append(h('li',{},p.key+': shared '+(current?.decision||current?.resolution||'batch decision')+' ('+(current?.reviewer||'earlier reviewer')+') → attempted '+(p.value?.decision||p.value?.resolution||'batch decision')))}card.append(list);
      card.append(h('details',{},h('summary',{},'Compare full changes'),h('pre',{},JSON.stringify({shared:conflict.mismatches.map(p=>({key:p.key,value:model[p.collection][p.key]??null})),attempted:event.changes},null,2))));
      card.append(h('button',{class:'batch-button secondary',type:'button',onclick:()=>resolve(event,false)},'Keep shared version'),h('button',{class:'batch-button',type:'button',onclick:()=>resolve(event,true)},'Use attempted version instead'));banner.append(card);
    }
  }
  function apply(){
    flushNote();model=stateWithPending();
    for(const collection of ['records','pairs','batch_approvals','resolutions'])store[collection]=JSON.parse(JSON.stringify(model[collection]));
    store.shared_scope=scope;persist();
    if(workflowReady){if(document.activeElement?.id==='note'){renderQueues();renderList()}else renderAll()}
    display();
  }
  async function json(url,options={}){const control=new AbortController(),timeout=setTimeout(()=>control.abort(),30000);try{const response=await fetch(url,{...options,signal:control.signal});if(!response.ok)throw Error('HTTP '+response.status);const data=await response.json();if(data.ok!==true)throw Error(data.error||'Shared service rejected the request');return data}finally{clearTimeout(timeout)}}
  async function read(){let failure;for(let attempt=0;attempt<3;attempt++){try{const url=new URL(config.endpoint);url.searchParams.set('action','rows');url.searchParams.set('project',scope);url.searchParams.set('_',Date.now());const data=await json(url.toString(),{cache:'no-store'});if(!Array.isArray(data.rows))throw Error('Shared service returned no log');return S.assemble(data.rows)}catch(e){failure=e;if(attempt<2)await new Promise(r=>setTimeout(r,1200*(attempt+1)))}}throw failure}
  function observe(server){events=server;const seen=new Set(events.map(e=>e.id));for(const k of Object.keys(localStorage).filter(k=>k.startsWith(prefix))){const rest=(readJSON(k,[])||[]).filter(e=>!seen.has(e.id));localStorage.setItem(k,JSON.stringify(rest))}outbox=readJSON(key,[])||[];ready=true;lastSync=stamp();error='';apply()}
  function sync(){if(currentSync){again=true;return currentSync}currentSync=runSync().finally(()=>{currentSync=null});return currentSync}
  async function runSync(){
    if(busy){again=true;return false}busy=true;display();
    try{
      observe(await read());
      if(pendingAll().length){const sent=pendingAll();try{await json(config.endpoint,{method:'POST',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify({records:sent.flatMap(e=>S.parts(e,scope,client))})})}catch(e){error=e.message}
        // A redirect response can fail after a successful write. Read-back is authoritative.
        observe(await read());if(pendingAll().length)error='Some changes are still queued; retry shared save';
      }
      return pendingAll().length===0&&model.conflicts.length===0;
    }catch(e){error=e.name==='AbortError'?'Shared service timed out':e.message;display();return false}
    finally{busy=false;display();if(again){again=false;schedule()}}
  }
  function schedule(){clearTimeout(timer);timer=setTimeout(sync,500)}
  function prepare(previous,next){
    const patch=S.changes(previous,next);prepared=null;if(!patch.length)return true;
    if(patch.length>=2000||patch.some(p=>p.value!==null&&(typeof p.value!=='object'||Array.isArray(p.value)))){notice('Invalid decision import or too many changes in one action. Import a smaller valid decision file.');return false}
    if(!ready){notice('Load the shared review before recording a decision. Use “Refresh shared decisions”.');return false}
    const reviewer=($('reviewer-name')?.value||prefs.reviewer||'').trim();if(!reviewer){notice('Enter your name once so other reviewers can see who made the decision.');$('reviewer-name').focus();return false}
    if(reviewer.length>120){notice('Use a name of at most 120 characters.');return false}
    // Preserve original imported attribution and record who published the change.
    for(const p of patch){if(p.value!==null){const value=next[p.collection][p.key];value.reviewer=reviewer}}
    const event=S.makeEvent(previous,next,model.heads,reviewer,baseline,newId(),stamp());
    if(!S.valid(event,baseline)){notice('This shared decision could not be validated; no change was queued.');return false}
    try{writeOutbox([...outbox,event]);prepared=event;return true}catch(e){notice('Could not queue the shared save: '+e.message);return false}
  }
  function committed(){if(prepared){prepared=null;model=stateWithPending();schedule()}display()}
  function rollback(){if(prepared){const id=prepared.id;prepared=null;try{writeOutbox(outbox.filter(e=>e.id!==id))}catch(e){}}display()}
  function resolve(event,useAttempt){
    if(!transaction(()=>{if(useAttempt)for(const p of event.changes){if(p.value===null)delete store[p.collection][p.key];else store[p.collection][p.key]=JSON.parse(JSON.stringify(p.value))}store.resolutions=store.resolutions||{};store.resolutions[event.id]={resolution:useAttempt?'use_attempt':'keep_shared',recorded_at:stamp()}}))return;
    apply();
  }
  function attribution(id,collection='records'){const event_id=model.heads[collection+':'+id];const event=events.find(e=>e.id===event_id);return event?{shared_event_id:event_id,shared_saved_at:event.server_timestamp}:{} }
  function canDownload(){return ready&&!pendingAll().length&&!model.conflicts.length&&!savingFailed}
  function history(id){return events.filter(e=>e.changes.some(p=>p.collection==='records'&&p.key===id)).map(e=>({reviewer:e.reviewer,saved_at:e.server_timestamp,decision:e.changes.find(p=>p.collection==='records'&&p.key===id)?.value?.decision||'withdrawn',event_id:e.id,conflict:!S.equal(model.resolutions[e.id],undefined)?'resolved':model.conflicts.some(c=>c.event.id===e.id)?'needs resolution':null}))}
  function publishBrowser(){if(!carryover)return;let skipped=0;if(!transaction(()=>{for(const collection of ['records','pairs','batch_approvals'])for(const [id,value] of Object.entries(carryover[collection]||{})){if(store[collection][id]){skipped++;continue}store[collection][id]=value}}))return;carryover=null;try{localStorage.removeItem(legacyKey)}catch(e){}renderAll();display();notice('Previous browser decisions queued for sharing; '+skipped+' existing shared entries kept.')}
  $('reviewer-name').value=prefs.reviewer||'';$('reviewer-name').onchange=e=>{prefs.reviewer=e.target.value.trim();savePrefs()};
  $('shared-refresh').onclick=()=>{flushNote();sync()};$('publish-browser').onclick=publishBrowser;
  window.addEventListener('online',sync);window.addEventListener('focus',()=>{if(!document.hidden)sync()});
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)sync()});
  // UI refresh only: server appends and read-back retain pending writes across reloads.
  setInterval(()=>{if(!document.hidden&&!busy)sync()},30000);
  return {prepare,committed,rollback,sync,display,canDownload,history,attribution,status:()=>({scope,ready,busy,pending:pendingAll().length,conflicts:model.conflicts.length,lastSync,error,server_events:events.length}),pending:()=>pendingAll().length,conflicts:()=>model.conflicts.length,model:()=>model};
}
