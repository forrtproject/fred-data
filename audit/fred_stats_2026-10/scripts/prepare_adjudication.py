import json,hashlib,collections,csv
from pathlib import Path
from compare import load_adjudications
B=Path(__file__).resolve().parents[1]
rows=json.loads((B/'parent_rows.json').read_text());d=json.loads((B/'disagreements.json').read_text());obvious={(a['audit_id'],a['field']) for a in json.loads((B/'obvious_resolutions.json').read_text())} if (B/'obvious_resolutions.json').exists() else set()
prior=load_adjudications(B)
holds={(a['audit_id'],a['field']):a for a in json.loads((B/'adjudication_holds.json').read_text())} if (B/'adjudication_holds.json').exists() else {}
inputs={a['audit_id']:a for p in (B/'inputs').glob('*.json') for a in json.loads(p.read_text())};groups=collections.defaultdict(list)
attempts=collections.Counter();completed_focus=set();transport_failures=set()
if (B/'adjudication_tasks.jsonl').exists():
 for line in (B/'adjudication_tasks.jsonl').read_text().splitlines():
  if not line:continue
  record=json.loads(line);context=bool(record.get('focused_review'))
  raw=B/'adjudications'/('raw_'+record['key']+'.txt')
  if record.get('exit_code')==126 and raw.exists() and 'Argument list too long' in raw.read_text():
   transport_failures.update((z['audit_id'],z['field']) for z in record.get('items',[]));continue
  if context:
   validated=B/'adjudications'/('validated_'+record['key']+'.json')
   if validated.exists():completed_focus.update((z['audit_id'],z['field']) for z in json.loads(validated.read_text()))
  for item in record.get('items',[]):attempts[(item['audit_id'],item['field'],context)]+=1
exhausted=[]
for a in d:
 if (a['audit_id'],a['field']) in obvious:continue
 if (a['audit_id'],a['field']) in transport_failures:a['transport_repair']='Earlier CLI invocations exceeded the OS argument limit before model launch; same substantive review is now delivered through a read-only prompt file.'
 context=(a['audit_id'],a['field']) in holds
 if context and (a['audit_id'],a['field']) in completed_focus:continue # await parent review of the completed focused response
 used=attempts[(a['audit_id'],a['field'],context)]
 if used>=2:
  exhausted.append({'audit_id':a['audit_id'],'field':a['field'],'attempts':used,'reason':'Two Argon calls already attempted for this field/review context; no further retry.'});continue
 if (a['audit_id'],a['field']) in holds:
  a['review_round']=2;a['prior_adjudication']=prior.get((a['audit_id'],a['field']));a['parent_response']=holds[(a['audit_id'],a['field'])].get('parent_response') or 'Prior verdict challenged: compatible rounding/formatting is correct, and absent printed degrees of freedom alone does NOT prove a coded inferred df wrong. Codebook permits calculations and inferences. Distinguish printed numeric statistic from df and N annotations. Only mark an error when evidence demonstrates a wrong df or N, not merely that it is unprinted. If df inferred consistently or only rounding differs, shipped_right. If inferential design unclear, undeterminable. If error is an annotation, give a FULL corrected statistic with df/N as established, not just a more precise number. Read source context and original locator. Reconcile prior finding with this response explicitly.'
 row=rows[a['audit_id']-1];side='o' if a['field'].endswith('_o') else 'r'
 a['coding_context']={'es_repr':row['es_repr_'+side],'description':row.get('description'),'reported_success_quote':row.get('reported_success_quote'),'pval_tails':row['pval_tails_'+side],'nested':row['nested_'+side],'analytic_n_definition':'sample size used for critical test after exclusions; record sample role'}
 a['locator']=inputs.get(a['audit_id'],{});groups[a['blind']['source_path']].append(a)
flagged={int(z['input_row_index']) for z in csv.DictReader((B/'consistency.csv').open(encoding='utf-8-sig')) if int(z['flag_count'])>0}
queue=[]
for source,items in groups.items():
 key=hashlib.sha256(json.dumps(items,sort_keys=True).encode()).hexdigest()[:16];prompt=B/'adjudications'/f'prompt_{key}.txt';out=B/'adjudications'/f'raw_{key}.txt'
 text='Adjudicate paper-statistics disagreements for a read-only audit. Independently inspect the supplied paper texts and target locators. You can see shipped and blind values. Decide exact study/outcome/sample/test; a pilot sample may differ from final data, and narrative success cannot be inferred from significance alone. Do not treat a wrong-target blind extraction as a shipped error. Inspect coding_context for documented calculation or coding direction; a documented sign reversal or reproducible transformation may be valid, but do not assume one. Compatible rounding or formatting is shipped_right, not a precision error. A formatted test statistic may validly contain inferred df/N even if those annotations are not printed inline; only positive evidence from design, reference distribution, counts or p-values can establish a wrong annotation. If inference cannot be settled, undeterminable. Give the full corrected test-statistic expression for any established annotation error. For analytic n, distinguish participant/cluster counts from repeated observations in nested or panel models. Different valid sample-level counts alone do not prove a shipped error; if the intended unit or exact critical model is unidentified, return undeterminable and preserve the roles separately. Original primary papers are required for original verification; replication-summary values alone do not suffice. For each item return a JSON object with audit_id (int), field, verdict (shipped_right|blind_right|both_wrong|undeterminable), correct_value (string or null), location, quote (verbatim short evidence occurring in the source text), source_path, reason. Return one JSON array, all items, inside ## Answer. Keep each reason to one or two sentences unless additional detail is essential; quote only the shortest exact supporting span copied from the supplied text, preserving its spelling/OCR. Do not repeat shared background in every row. No markdown prose in the array. If a value is undeterminable, still quote the text showing ambiguity. Preserve bound types in correct_value when relevant. For a reported_success item with a nonempty scope_note, the worker explicitly identified only an overall paper narrative with insufficient individual-effect identification. Return effect_specific_verdict_confirmed true ONLY if neutral locator information uniquely identifies this row and the authors narrative applies specifically to it; otherwise false and undeterminable. Do not transfer a global mixed/successful label to all unidentified outcomes in the article. Explain the scope using a source quotation, never numerical coincidence with the shipped values. For effect sizes, preserve the requested metric; never replace a test statistic with an effect-size coefficient. If a different metric is the only available value and no documented transformation is reproducible, return undeterminable and explain not_comparable. Include correct_metric for ES corrections.\n\n'+json.dumps(items,ensure_ascii=False,indent=2)+'\n\nEnd your response with the answer itself under a heading `## Answer`.\nPut your whole result in your reply; do not create files or run commands.'
 prompt.write_text(text);queue.append({'priority_flagged':any(a['audit_id'] in flagged for a in items),'has_value_disagreement':any(a['comparison'] in ['differ','near','soft'] for a in items),'transport_repair':any(a.get('transport_repair') for a in items),'focused_review':any(a.get('review_round')==2 for a in items),'key':key,'prompt_bytes':prompt.stat().st_size,'source_path':source,'prompt':str(prompt),'output':str(out),'items':[{'audit_id':a['audit_id'],'field':a['field']} for a in items]})
queue.sort(key=lambda a:(not a['focused_review'],not a['transport_repair'],not a['priority_flagged'],not a['has_value_disagreement'],-len(a['items'])))
(B/'adjudication_exhausted.json').write_text(json.dumps(exhausted,indent=2))
(B/'adjudication_queue.json').write_text(json.dumps(queue,indent=2));print({'papers':len(queue),'items':sum(len(x['items']) for x in queue)})
