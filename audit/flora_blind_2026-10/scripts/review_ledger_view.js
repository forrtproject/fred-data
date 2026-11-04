/* Views built from the field ledger. They show status and evidence; they record no approval. */
const BRANCH_URL='https://github.com/forrtproject/fred-data/tree/audit/flora-blind-2026-10/audit/flora_blind_2026-10';
const MISSING_URL='https://github.com/forrtproject/fred-data/blob/audit/flora-blind-2026-10/audit/flora_blind_2026-10/handoff/missing_links_to_add.csv';
const CORRECTIONS_URL='https://github.com/forrtproject/fred-data/blob/audit/flora-blind-2026-10/audit/flora_blind_2026-10/handoff/corrections_to_apply.csv';
function moveLine(change){
  const done=change.relation==='already_equal';
  return h('li',{},change.label+': ',h('span',{class:'from'},clip(change.audited,120)),' to ',h('span',{class:'to'},clip(change.proposed,160)),done?' (already in current FLoRA)':change.relation==='unchanged_from_frozen'?'':' (current FLoRA: '+clip(change.current,80)+')');
}
function bundleBody(b){
  const body=h('div',{class:'body'});
  if(b.summary)body.append(h('p',{},b.summary));
  body.append(h('ul',{},b.provenance.map(x=>h('li',{},x))));
  if((b.kept||[]).length)body.append(h('p',{},'Leave as it is: '+b.kept.join(', ')+'. The evidence does not show this value is wrong.'));
  for(const q of b.quotes||[])body.append(h('blockquote',{class:q.against?'against':''},q.text,h('cite',{},(q.against?'Strongest evidence against the change':'Supporting passage')+(q.section?', '+q.section:'')),q.note?h('cite',{},q.note):null));
  if((b.limits||[]).length)body.append(h('p',{},'Limits: '),h('ul',{},b.limits.map(x=>h('li',{},x))));
  const c=caseById.get(b.id);body.append(h('p',{},c?h('button',{type:'button',class:'row-jump',onclick:()=>{setStage('individual');openCase(b.id)}},'Open the full case'):null,'  Audit row '+b.row));
  return body;
}
function bundleLine(id){
  const b=ledger.bundles[id];
  const d=h('details',{class:'bundle'},h('summary',{},(b.flora_id||'Audit row '+b.row)+'. '+clip(b.title,120),h('ul',{class:'moves'},b.changes.map(moveLine))));
  d.addEventListener('toggle',()=>{if(d.open&&!d.querySelector('.body'))d.append(bundleBody(b))},{once:false});
  return d;
}
function renderStanding(b){
  return h('section',{class:'standing'},h('h3',{},b.status),...b.provenance.map(x=>h('p',{},x)),(b.limits||[]).length?h('ul',{},b.limits.slice(0,4).map(x=>h('li',{},x))):null);
}
function renderOverview(root){
  const ready=ledger.statement.find(s=>s.id==='ready'),types=ledger.sets.find(s=>s.id==='type_and_outcome'),apply=ready.rows-types.rows;
  root.append(h('h2',{},'What should change in FLoRA'),h('p',{class:'since'},`The audit re-read the papers behind FLoRA and proposed ${ledger.totals.fields} changes to values across ${ledger.totals.rows} records. A record is one row in FLoRA: a report paired with the original study it re-tests. Every proposed change is counted once below. None has been applied.`));
  const target={ready:'sets',record_exclusion:'sets',no_edit:'settled',withdraw:'settled',rebind:'settled',needs_reference:'pending',pending_read:'pending',rule:'rules',source_blocked:'blocked'};
  const body=h('tbody');
  for(const line of ledger.statement.filter(s=>s.rows)){
    const go=target[line.id];
    body.append(h('tr',{},h('td',{},h('button',{type:'button',class:'line-title',onclick:()=>setStage(go)},line.label),h('span',{class:'line-note'},line.note)),h('td',{class:'n'},String(line.rows)),h('td',{class:'n'},String(line.fields))));
  }
  root.append(h('table',{class:'statement'},h('thead',{},h('tr',{},h('th',{},'Status'),h('th',{},'Records'),h('th',{},'Values'))),body,h('tfoot',{},h('tr',{},h('td',{},'All proposed changes'),h('td',{class:'n'},String(ledger.totals.rows)),h('td',{class:'n'},String(ledger.totals.fields))))));
  root.append(h('h3',{},'What needs doing'),h('ol',{},
    h('li',{},`Apply ${apply} corrections through flora-validation, re-checking each value first. `,h('a',{href:CORRECTIONS_URL},'The corrections list'),' gives the record, the expected value and the new value.'),
    h('li',{},`Remove ${ledger.record_exclusions.length} records that do not re-test an earlier finding.`),
    h('li',{},`Agree a way to change the study type on ${types.rows} records. flora-validation cannot edit it yet.`),
    h('li',{},'Review the other changes on this page and make a plan for how to address them. Please agree that plan with Lukas before applying any of them.')));
  root.append(h('h3',{},'How a change was checked'),h('ol',{},
    h('li',{},'Two AI models, Claude Opus and GPT Sol, each read the full paper separately, without seeing the value in FLoRA.'),
    h('li',{},'A change went forward only if both backed the same new value.'),
    h('li',{},'A further AI read of the complete paper looked for reasons to reject it.'),
    h('li',{},'Where a reader was unsure, or that read was not confident, the paper got one more read that showed the two values without saying which was in FLoRA. The value changed only if the paper contradicted it.'),
    h('li',{},'A corrected original study also had to match its record in Crossref.'),
    h('li',{},'Current FLoRA had to still hold the old value.')),
  h('p',{class:'since'},`No person has read every record. As a spot check, one more read of 16 randomly chosen changes where a reader was unsure found ${ledger.close_read.sample.results.correct} real corrections, ${ledger.close_read.sample.results.existing_value_defensible} where the existing value was defensible and ${ledger.close_read.sample.results.would_add_an_error} that would have added an error. That is why those changes each got their own read. In the final round, ${ledger.final_read.changed} values changed and ${ledger.final_read.kept} stayed, most of them close calls between labels.`));
  root.append(h('h3',{},'FLoRA has moved on since the audit'),h('p',{class:'since'},`The audit read a saved copy of FLoRA with ${ledger.baseline.rows.toLocaleString('en')} records. The current release has ${ledger.current.rows.toLocaleString('en')}, so audit row numbers do not match it. Each audited record was matched to its current FLoRA record by study identifiers and titles, and any uncertain match is held back. The database may be ahead of the release, which is why each value must be re-checked just before editing.`));
  const outside=ledger.outside_scope;
  root.append(h('h3',{},'Also to cover in the plan'),h('ul',{},
    h('li',{},`${ledger.missing_links.to_add} replications are missing from FLoRA: a report re-tests an original study, but no record pairs them. `,h('a',{href:MISSING_URL},'The list'),' gives each one.'),
    h('li',{},`${ledger.missing_links.unconfirmed_total} more were checked, but the paper did not show clearly that it re-tests the study. No action needed. ${outside.planned_pairs} further studies are planned, with no results yet.`),
    h('li',{},`${outside.quote_updates} records whose value is right but whose supporting quote should be replaced.`),));
  root.append(h('p',{class:'since'},h('a',{href:BRANCH_URL},'All audit files are on this branch.')));
}
function renderSets(root){
  root.append(h('h2',{},'Ready to apply'),h('p',{class:'since'},'Each group below is one kind of change. Open a record to see the quotes and what was checked.'),h('p',{class:'closed-note'},ledger.set_decision_note));
  for(const set of ledger.sets){
    if(!set.rows)continue;
    root.append(h('section',{class:'batch-card'},h('h3',{},set.title),h('p',{class:'set-rule'},set.rule),h('p',{class:'muted'},`${set.rows} records, ${set.fields} values`),set.route_blocked?h('p',{class:'closed-note'},'Cannot be applied yet. flora-validation cannot change a record’s study type, and it offers computation and robustness results only on a reproduction. This needs a new route.'):null,h('div',{},set.items.map(bundleLine))));
  }
  if(ledger.record_exclusions.length)root.append(h('section',{class:'batch-card'},h('h3',{},'Remove the whole record'),h('p',{class:'set-rule'},'The paper re-tests no earlier published finding, so the record should not be in FLoRA.'),h('div',{},ledger.record_exclusions.map(bundleLine))));
  if(batchGroups.some(g=>!g.retired))root.append(h('h3',{},'Separate from the corrections: missing links'));
  for(const g of batchGroups)if(!g.retired)renderPairGroup(root,g);
}
function renderPending(root){
  root.append(h('h2',{},'Needs a verified reference'));
  if(ledger.pending_read.length)root.append(h('section',{class:'batch-card'},h('div',{},ledger.pending_read.map(bundleLine))));
  if(ledger.needs_reference?.length)root.append(h('section',{class:'batch-card'},h('h3',{},'Right study, no verified reference'),h('p',{},'The evidence supports a different original study, but Crossref has no exact record for it. Someone needs to confirm the reference by hand.'),h('div',{},ledger.needs_reference.map(bundleLine))));
}
function renderRules(root){
  root.append(h('h2',{},'Needs a coding decision'),h('p',{class:'since'},'The AI readers disagree on these, or the answer depends on how FLoRA should code the case. Each group shares one question. These are not ready to apply. The plan needs to say how each question gets settled.'));
  for(const g of ledger.rule_groups){
    root.append(h('section',{class:'batch-card'},h('h3',{},g.question),h('p',{class:'muted'},`${g.rows} records, ${g.fields} values`),g.reviewer_questions.length?h('ul',{},g.reviewer_questions.map(q=>h('li',{},q))):null,h('details',{},h('summary',{},'See the cases'),h('div',{},g.items.map(bundleLine)))));
  }
}
function renderBlocked(root){
  const labels=ledger.blocked.labels,kinds=ledger.blocked.kinds;
  root.append(h('h2',{},'On hold: not enough text'),h('p',{class:'since'},'No action needed now. These values stay as they are, and could be checked in future if a better copy of the paper turns up. This says nothing about the study itself.'));
  root.append(h('ul',{},Object.entries(kinds).map(([k,n])=>h('li',{},`${n} ${n===1?'value':'values'}: ${labels[k]}`))));
  root.append(h('section',{class:'batch-card'},h('details',{},h('summary',{},`See all ${ledger.blocked.items.length} records`),h('div',{},ledger.blocked.items.map(bundleLine)))));
}
function renderSettled(root){
  root.append(h('h2',{},'No change needed'));
  for(const [title,note,items] of [['Changed in FLoRA since the audit','The record now holds a value the audit did not see, or could not be matched for certain. Check these by hand before editing.',ledger.rebind],['Keep the existing value','The evidence does not show the existing value is wrong, so the proposal is dropped.',ledger.withdraw],['Already correct in FLoRA','Current FLoRA already holds the proposed value. Nothing to do.',ledger.no_edit]])
    if(items.length)root.append(h('section',{class:'batch-card'},h('h3',{},title),h('p',{},note),h('div',{},items.map(bundleLine))));
}
