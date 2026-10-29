import json,hashlib,collections
from pathlib import Path
B=Path(__file__).resolve().parents[1]
d=json.loads((B/'disagreements.json').read_text());obvious={(a['audit_id'],a['field']) for a in json.loads((B/'obvious_resolutions.json').read_text())} if (B/'obvious_resolutions.json').exists() else set()
inputs={a['audit_id']:a for p in (B/'inputs').glob('*.json') for a in json.loads(p.read_text())};groups=collections.defaultdict(list)
for a in d:
 if (a['audit_id'],a['field']) in obvious:continue
 a['locator']=inputs.get(a['audit_id'],{});groups[a['blind']['source_path']].append(a)
queue=[]
for source,items in groups.items():
 key=hashlib.sha256(json.dumps(items,sort_keys=True).encode()).hexdigest()[:16];prompt=B/'adjudications'/f'prompt_{key}.txt';out=B/'adjudications'/f'raw_{key}.txt'
 text='Adjudicate paper-statistics disagreements for a read-only audit. Independently inspect the supplied paper texts and target locators. You can see shipped and blind values. Decide exact study/outcome/sample/test; a pilot sample may differ from final data, and narrative success cannot be inferred from significance alone. Do not treat a wrong-target blind extraction as a shipped error. For each item return a JSON object with audit_id (int), field, verdict (shipped_right|blind_right|both_wrong|undeterminable), correct_value (string or null), location, quote (verbatim short evidence occurring in the source text), source_path, reason. Return one JSON array, all items, inside ## Answer. No markdown prose in the array. If a value is undeterminable, still quote the text showing ambiguity. Preserve bound types in correct_value when relevant.\n\n'+json.dumps(items,ensure_ascii=False,indent=2)+'\n\nEnd your response with the answer itself under a heading `## Answer`.\nPut your whole result in your reply; do not create files or run commands.'
 prompt.write_text(text);queue.append({'key':key,'source_path':source,'prompt':str(prompt),'output':str(out),'items':[{'audit_id':a['audit_id'],'field':a['field']} for a in items]})
(B/'adjudication_queue.json').write_text(json.dumps(queue,indent=2));print({'papers':len(queue),'items':sum(len(x['items']) for x in queue)})
