import json,hashlib,collections
from pathlib import Path
B=Path(__file__).resolve().parents[1]
rows=json.loads((B/'parent_rows.json').read_text());d=json.loads((B/'disagreements.json').read_text());obvious={(a['audit_id'],a['field']) for a in json.loads((B/'obvious_resolutions.json').read_text())} if (B/'obvious_resolutions.json').exists() else set()
prior={}
for path in sorted((B/'adjudications').glob('validated_*.json'),key=lambda p:p.stat().st_mtime_ns):
 for a in json.loads(path.read_text()):prior.setdefault((a['audit_id'],a['field']),a)
holds={(a['audit_id'],a['field']):a for a in json.loads((B/'adjudication_holds.json').read_text())} if (B/'adjudication_holds.json').exists() else {}
inputs={a['audit_id']:a for p in (B/'inputs').glob('*.json') for a in json.loads(p.read_text())};groups=collections.defaultdict(list)
attempts=collections.Counter()
if (B/'adjudication_tasks.jsonl').exists():
 for line in (B/'adjudication_tasks.jsonl').read_text().splitlines():
  if not line:continue
  record=json.loads(line);context=bool(record.get('focused_review'))
  for item in record.get('items',[]):attempts[(item['audit_id'],item['field'],context)]+=1
exhausted=[]
for a in d:
 if (a['audit_id'],a['field']) in obvious:continue
 context=(a['audit_id'],a['field']) in holds
 used=attempts[(a['audit_id'],a['field'],context)]
 if used>=2:
  exhausted.append({'audit_id':a['audit_id'],'field':a['field'],'attempts':used,'reason':'Two Argon calls already attempted for this field/review context; no further retry.'});continue
 if (a['audit_id'],a['field']) in holds:
  a['review_round']=2;a['prior_adjudication']=prior.get((a['audit_id'],a['field']));a['parent_response']=holds[(a['audit_id'],a['field'])].get('parent_response') or 'Prior verdict challenged: compatible rounding/formatting is correct, and absent printed degrees of freedom alone does NOT prove a coded inferred df wrong. Codebook permits calculations and inferences. Distinguish printed numeric statistic from df and N annotations. Only mark an error when evidence demonstrates a wrong df or N, not merely that it is unprinted. If df inferred consistently or only rounding differs, shipped_right. If inferential design unclear, undeterminable. If error is an annotation, give a FULL corrected statistic with df/N as established, not just a more precise number. Read source context and original locator. Reconcile prior finding with this response explicitly.'
 row=rows[a['audit_id']-1];side='o' if a['field'].endswith('_o') else 'r'
 a['coding_context']={'es_repr':row['es_repr_'+side],'pval_tails':row['pval_tails_'+side],'nested':row['nested_'+side],'analytic_n_definition':'sample size used for critical test after exclusions; record sample role'}
 a['locator']=inputs.get(a['audit_id'],{});groups[a['blind']['source_path']].append(a)
queue=[]
for source,items in groups.items():
 key=hashlib.sha256(json.dumps(items,sort_keys=True).encode()).hexdigest()[:16];prompt=B/'adjudications'/f'prompt_{key}.txt';out=B/'adjudications'/f'raw_{key}.txt'
 text='Adjudicate paper-statistics disagreements for a read-only audit. Independently inspect the supplied paper texts and target locators. You can see shipped and blind values. Decide exact study/outcome/sample/test; a pilot sample may differ from final data, and narrative success cannot be inferred from significance alone. Do not treat a wrong-target blind extraction as a shipped error. Inspect coding_context for documented calculation or coding direction; a documented sign reversal or reproducible transformation may be valid, but do not assume one. Original primary papers are required for original verification; replication-summary values alone do not suffice. For each item return a JSON object with audit_id (int), field, verdict (shipped_right|blind_right|both_wrong|undeterminable), correct_value (string or null), location, quote (verbatim short evidence occurring in the source text), source_path, reason. Return one JSON array, all items, inside ## Answer. Keep each reason to one or two sentences unless additional detail is essential; quote only the shortest exact supporting span copied from the supplied text, preserving its spelling/OCR. Do not repeat shared background in every row. No markdown prose in the array. If a value is undeterminable, still quote the text showing ambiguity. Preserve bound types in correct_value when relevant. For effect sizes, preserve the requested metric; never replace a test statistic with an effect-size coefficient. If a different metric is the only available value and no documented transformation is reproducible, return undeterminable and explain not_comparable. Include correct_metric for ES corrections.\n\n'+json.dumps(items,ensure_ascii=False,indent=2)+'\n\nEnd your response with the answer itself under a heading `## Answer`.\nPut your whole result in your reply; do not create files or run commands.'
 prompt.write_text(text);queue.append({'focused_review':any(a.get('review_round')==2 for a in items),'key':key,'source_path':source,'prompt':str(prompt),'output':str(out),'items':[{'audit_id':a['audit_id'],'field':a['field']} for a in items]})
queue.sort(key=lambda a:not a['focused_review'])
(B/'adjudication_exhausted.json').write_text(json.dumps(exhausted,indent=2))
(B/'adjudication_queue.json').write_text(json.dumps(queue,indent=2));print({'papers':len(queue),'items':sum(len(x['items']) for x in queue)})
