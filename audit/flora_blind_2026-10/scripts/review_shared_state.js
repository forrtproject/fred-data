/* Append-only shared decision protocol. No browser clock determines a winner. */
(function(root){
  'use strict';
  const collections=['records','pairs','batch_approvals','resolutions'];
  const copy=x=>JSON.parse(JSON.stringify(x));
  const canonical=x=>Array.isArray(x)?x.map(canonical):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x;
  const equal=(a,b)=>JSON.stringify(canonical(a??null))===JSON.stringify(canonical(b??null));
  function comparable(value){if(!value||typeof value!=='object')return value;const v=copy(value);for(const key of ['recorded_at','updated_at','reviewer','shared_event_id','shared_saved_at','decision_label'])delete v[key];return v}
  function empty(){return {records:{},pairs:{},batch_approvals:{},resolutions:{},heads:{},conflicts:[],events:[]}}
  function changes(before,after){const out=[];for(const collection of collections){const a=before[collection]||{},b=after[collection]||{};for(const key of new Set([...Object.keys(a),...Object.keys(b)])){if(!equal(a[key],b[key]))out.push({collection,key,value:copy(b[key]??null)})}}return out}
  function makeEvent(before,after,heads,reviewer,baseline,id,time){const patch=changes(before,after);if(!patch.length)return null;return {schema:1,id,baseline,reviewer,created_at:time,parents:Object.fromEntries(patch.map(p=>[p.collection+':'+p.key,heads[p.collection+':'+p.key]||null])),changes:patch}}
  function valid(event,baseline){return event&&event.schema===1&&event.baseline===baseline&&typeof event.id==='string'&&event.id.length<160&&typeof event.reviewer==='string'&&event.reviewer.length<=120&&Array.isArray(event.changes)&&event.changes.length<2000&&event.changes.every(p=>collections.includes(p.collection)&&typeof p.key==='string'&&p.key.length<250&&!['__proto__','prototype','constructor'].includes(p.key)&&(p.value===null||(typeof p.value==='object'&&!Array.isArray(p.value))))&&event.parents&&typeof event.parents==='object'}
  function reduce(events,baseline){
    const state=empty(),seen=new Set();
    for(const event of events){if(!valid(event,baseline)||seen.has(event.id))continue;seen.add(event.id);state.events.push(event);
      const mismatches=event.changes.filter(p=>{const key=p.collection+':'+p.key;return (event.parents[key]||null)!==(state.heads[key]||null)&&!equal(comparable(state[p.collection][p.key]),comparable(p.value))});
      if(mismatches.length){state.conflicts.push({event,mismatches});continue}
      for(const p of event.changes){const key=p.collection+':'+p.key;
        // Repeated identical approvals commute and retain the first author's record.
        if(equal(comparable(state[p.collection][p.key]),comparable(p.value)))continue;
        if(p.value===null)delete state[p.collection][p.key];else state[p.collection][p.key]=copy(p.value);
        state.heads[key]=event.id;
      }
    }
    state.conflicts=state.conflicts.filter(c=>!state.resolutions[c.event.id]);return state;
  }
  function parts(event,project,session){const text=JSON.stringify(event),size=12000,n=Math.ceil(text.length/size);return Array.from({length:n},(_,i)=>({project,itemId:event.id+':'+i,vote:'flora-decision-log-v1',note:JSON.stringify({event_id:event.id,index:i,total:n,text:text.slice(i*size,(i+1)*size)}),voter:/^[=+\-@\t\r\n]/.test(event.reviewer)?"\'"+event.reviewer:event.reviewer,session}))}
  function assemble(rows){const groups=new Map();for(let order=0;order<rows.length;order++){const row=rows[order];if(row.vote!=='flora-decision-log-v1')continue;try{const p=JSON.parse(row.note);if(!Number.isInteger(p.total)||p.total<1||p.total>200||!Number.isInteger(p.index)||p.index<0||p.index>=p.total||typeof p.text!=='string')continue;let g=groups.get(p.event_id);if(!g){g={order,total:p.total,parts:new Map(),ts:row.ts};groups.set(p.event_id,g)}if(p.total!==g.total)continue;if(!g.parts.has(p.index))g.parts.set(p.index,p.text)}catch(e){}}
    const out=[];for(const [id,g] of [...groups].sort((a,b)=>a[1].order-b[1].order)){if(g.parts.size!==g.total)continue;try{const event=JSON.parse(Array.from({length:g.total},(_,i)=>g.parts.get(i)).join(''));if(event.id===id)out.push({...event,server_timestamp:g.ts})}catch(e){}}return out;
  }
  const api={empty,changes,makeEvent,valid,reduce,parts,assemble,equal};root.FloraSharedState=api;if(typeof module!=='undefined')module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
