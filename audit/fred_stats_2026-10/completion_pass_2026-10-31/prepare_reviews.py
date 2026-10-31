import ast,json,sys
from pathlib import Path
F=Path(__file__).resolve().parent;B=F.parent;sys.path.insert(0,str(B/'scripts'))
from compare import load_adjudications
lead=next(n.value for n in ast.walk(ast.parse((B/'scripts/prepare_adjudication.py').read_text())) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith('Adjudicate paper-statistics disagreements'))
prior=load_adjudications(B, exclude_prefixes=("validated_completion_",))
for group in json.loads((F/'review_queue.json').read_text()):
 key=group['key']
 if (F/'reviews'/f'task_{key}_v1.json').exists():continue
 items=[]
 for item in group['items']:
  item={**item,'prior_adjudication':prior.get((item['audit_id'],item['field'])),'parent_response':'New separately authorised source-grouped completion. Fresh blind extraction and exact evidence now supplied. Reconcile prior findings/holds explicitly; numeric agreement alone is not target identification. Do not infer unknown sample roles or individual author verdicts from a shared paper-level label.'};items.append(item)
 note='''\n\nAdditional completion requirements: Review ONLY the supplied primary text/PDF and payload. No acquisition, dataset/repository search, Git or edits outside your named answer file. PDF target-page rendering, if needed, ONLY under /home/lukas/.cache/fred-completion-review-renders/KEY. Use explicit true/false target_match_confirmed for each field. For author-reported success include effect_specific_verdict_confirmed true ONLY with positive row-specific mapping; a paper-level label cannot certify an unspecified ANOVA term. For analytic N check the intended critical test and counting unit, exclusions and any explicit component sum; df alone does not establish N. For ES preserve requested metric and give correct_metric; never call different metrics equivalent just because values agree. A documented source statement may establish metric equivalence; otherwise undeterminable. Include correct_bound for every p correction. Preserve literal short canonical-text evidence or ordered ... fragments; do not fabricate flattened tables. Return a COMPLETE JSON array, all items; no partial replies accepted. Fields: audit_id,field,verdict(shipped_right|blind_right|both_wrong|undeterminable),correct_value(string|null),correct_metric(string|null),correct_bound(e|l|g|le|ge|null),target_match_confirmed(boolean),effect_specific_verdict_confirmed(boolean),location,quote,source_path,reason. For undeterminable correct_value null. Write only ANSWERFILE and put the same JSON under ## Answer in your reply. Aim8min hard12min. No delegation, no paid API calls.\n'''
 answer=F/'reviews'/f'answer_{key}_v1.json';prompt=lead+'\n\n'+json.dumps(items,indent=2,ensure_ascii=False)+note.replace('KEY',key).replace('ANSWERFILE',str(answer))
 (F/'reviews'/f'prompt_{key}_v1.txt').write_text(prompt);(F/'reviews'/f'payload_{key}_v1.json').write_text(json.dumps(items,indent=2,ensure_ascii=False)+'\n')
print('Prepared',len(json.loads((F/'review_queue.json').read_text())),'source reviews')
