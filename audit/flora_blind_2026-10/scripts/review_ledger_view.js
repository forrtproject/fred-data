/* Views built from the field ledger. They show status and evidence; they record no approval. */
function moveLine(change){
  const moved=change.relation==='already_equal';
  return h('li',{},change.label+': ',h('span',{class:'from'},clip(change.audited,120)),' to ',h('span',{class:'to'},clip(change.proposed,160)),moved?' (already in current FLoRA)':change.relation==='unchanged_from_frozen'?'':' (current FLoRA: '+clip(change.current,80)+')');
}
function bundleBody(b){
  const body=h('div',{class:'body'});
  if(b.summary)body.append(h('p',{},b.summary));
  if(b.scope_question)body.append(h('p',{},'Question raised during comparison: ',b.scope_question+'.'));
  for(const q of b.quotes||[])body.append(h('blockquote',{class:q.against?'against':''},q.text,h('cite',{},(q.against?'Strongest evidence against':'Supporting passage')+(q.section?', '+q.section:'')),q.note?h('cite',{},q.note):null));
  if((b.limits||[]).length)body.append(h('p',{},'Limits: '),h('ul',{},b.limits.map(x=>h('li',{},x))));
  const c=caseById.get(b.id);body.append(h('p',{},c?h('button',{type:'button',class:'row-jump',onclick:()=>{setStage('individual');openCase(b.id)}},'Open this case'):null,b.flora_id?'  Current record '+b.flora_id:''));
  return body;
}
function bundleLine(id){
  const b=ledger.bundles[id];
  const d=h('details',{class:'bundle'},h('summary',{},'Row '+b.row+'. '+clip(b.title,120),h('ul',{class:'moves'},b.changes.map(moveLine))));
  d.addEventListener('toggle',()=>{if(d.open&&!d.querySelector('.body'))d.append(bundleBody(b))},{once:false});
  return d;
}
function renderStanding(b){
  return h('section',{class:'standing'},h('h3',{},b.status),...b.provenance.map(x=>h('p',{},x)),b.scope_question?h('p',{},'Question raised during comparison: '+b.scope_question+'.'):null,(b.limits||[]).length?h('ul',{},b.limits.slice(0,4).map(x=>h('li',{},x))):null);
}
function renderOverview(root){
  const short=x=>x.slice(0,10);
  root.append(h('h2',{},'Where things stand'),h('p',{class:'since'},`Every one of the ${ledger.totals.fields} proposed field changes, across ${ledger.totals.rows} rows, is counted once below. Nothing here has been approved or applied.`));
  const target={ready:'sets',record_exclusion:'sets',no_edit:'settled',withdraw:'settled',rebind:'settled',pending_read:'pending',rule:'rules',source_blocked:'blocked'};
  const body=h('tbody');
  for(const line of ledger.statement){
    const go=target[line.id];
    body.append(h('tr',{},h('td',{},h('button',{type:'button',class:'line-title',onclick:()=>setStage(go)},line.label),h('span',{class:'line-note'},line.note)),h('td',{class:'n'},String(line.rows)),h('td',{class:'n'},String(line.fields))));
  }
  root.append(h('table',{class:'statement'},h('thead',{},h('tr',{},h('th',{},'Status'),h('th',{},'Rows'),h('th',{},'Fields'))),body,h('tfoot',{},h('tr',{},h('td',{},'All proposed changes'),h('td',{class:'n'},String(ledger.totals.rows)),h('td',{class:'n'},String(ledger.totals.fields))))));
  root.append(h('h3',{},'FLoRA has moved on since this audit'),h('p',{class:'since'},`The audit read a frozen copy with ${ledger.baseline.rows} rows. The current release has ${ledger.current.rows} rows and new columns, so earlier row numbers and record hashes no longer apply. Each row is matched to its current record by its study identifiers, and anything uncertain stays held.`));
  const outside=ledger.outside_scope;
  root.append(h('h3',{},'Outside these proposed changes'),h('ul',{},
    h('li',{},`${outside.confirmed_missing_pairs.items} confirmed missing study–original pairs (${outside.confirmed_missing_pairs.current.already_in_current||0} now appear in current FLoRA)`),
    h('li',{},`${outside.unresolved_candidates} unresolved possible omissions and ${outside.planned_pairs} planned-study pairs`),
    h('li',{},`${outside.quote_updates} verified evidence-quote updates`),
    h('li',{},`${outside.unreviewed_two_reader_targets} further originals that both readings named and no row covers. These have not been reviewed.`)));
}
function renderSets(root){
  root.append(h('h2',{},'Candidate sets'),h('p',{class:'since'},'Each set has one rule. Open a row to see the quoted evidence and what was checked.'),h('p',{class:'closed-note'},ledger.set_decision_note));
  for(const set of ledger.sets){
    if(!set.rows)continue;
    root.append(h('section',{class:'batch-card'},h('h3',{},set.title),h('p',{class:'set-rule'},set.rule),h('p',{class:'muted'},`${set.rows} rows, ${set.fields} fields`),h('div',{},set.items.map(bundleLine))));
  }
  if(ledger.record_exclusions.length)root.append(h('section',{class:'batch-card'},h('h3',{},'Whole-record exclusions'),h('p',{class:'set-rule'},'Remove the whole record because the paper re-tests no earlier published finding. Kept apart from field edits.'),h('div',{},ledger.record_exclusions.map(bundleLine))));
  for(const g of batchGroups)if(!g.retired)renderPairGroup(root,g);
}
function renderPending(root){
  const reviews=ledger.adversary?.reviews||{};
  root.append(h('h2',{},'Awaiting a source review'),h('p',{class:'since'},`Two confident readings agree with these proposals. A separate review now reads each complete source looking for reasons to reject the change; only then can a row join a candidate set. ${reviews.valid||0} reviews have passed their checks so far.`));
  root.append(h('section',{class:'batch-card'},h('div',{},ledger.pending_read.map(bundleLine))));
}
function renderRules(root){
  root.append(h('h2',{},'Rule questions'),h('p',{class:'since'},'One decision on a question can settle every case that shares it. No rule has been decided; these are listed so you can see the questions and the cases behind them.'));
  for(const g of ledger.rule_groups){
    root.append(h('section',{class:'batch-card'},h('h3',{},g.question),h('p',{class:'muted'},`${g.rows} rows, ${g.fields} fields`),g.reviewer_questions.length?h('ul',{},g.reviewer_questions.map(q=>h('li',{},q))):null,h('details',{},h('summary',{},'See the cases'),h('div',{},g.items.map(bundleLine)))));
  }
}
function renderBlocked(root){
  const labels=ledger.blocked.labels,kinds=ledger.blocked.kinds;
  root.append(h('h2',{},'Blocked by the source'),h('p',{class:'since'},'The available text cannot settle these fields. They stay as they are until a better source exists.'));
  root.append(h('ul',{},Object.entries(kinds).map(([k,n])=>h('li',{},`${n} fields: ${labels[k]}`))));
  root.append(h('section',{class:'batch-card'},h('details',{},h('summary',{},`See all ${ledger.blocked.items.length} rows`),h('div',{},ledger.blocked.items.map(bundleLine)))));
}
function renderSettled(root){
  root.append(h('h2',{},'No edit needed yet'));
  for(const [title,note,items] of [['Proposal should be withdrawn','Source review or both readings keep the existing value.',ledger.withdraw],['Already right in current FLoRA','Current FLoRA holds the proposed value, so these need no edit.',ledger.no_edit],['Current FLoRA changed','The row now holds a third value or could not be matched with certainty. Earlier evidence stays on record, and these need checking against current data.',ledger.rebind]])
    if(items.length)root.append(h('section',{class:'batch-card'},h('h3',{},title),h('p',{},note),h('div',{},items.map(bundleLine))));
}
