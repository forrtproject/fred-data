import json
from pathlib import Path
import jsonschema
B=Path(__file__).resolve().parents[1]
status={'enum':['done','paper_unavailable','locator_insufficient','timeout','error']}
nullable={'type':['string','null']}
def obj(props):return {'type':'object','properties':props,'required':list(props),'additionalProperties':False}
evidence={'location':{'type':'string'},'quote':{'type':'string'},'source_path':{'type':'string'},'confident':{'type':'boolean'}}
n=obj({'value':nullable,'sample_role':{'type':'string'},'exclusions':{'type':'string'},**evidence})
es=obj({'value':nullable,'metric':nullable,'test_statistic':nullable,**evidence})
p=obj({'value':nullable,'bound':{'enum':['e','l','g','le','ge',None]},**evidence})
side=obj({'status':status,'target_match':{'type':['boolean','null']},'target_description':{'type':'string'},'n':n,'es':es,'p':p})
schema=obj({'audit_id':{'type':'integer','minimum':1,'maximum':2164},'original':side,'replication':side,'reported_success':obj({'value':{'enum':['successful','failed','mixed','uninformative','statistically successful but flawed','descriptive only',None]},**evidence,'status':status}),'notes':{'type':'string'}})
validator=jsonschema.Draft202012Validator(schema)
def validate(x):
 validator.validate(x)
 for s in ['original','replication']:
  if x[s]['status']!='done':
   for f in ['n','es','p']:
    if x[s][f]['value'] is not None:raise ValueError('Failure side has value: '+s+'.'+f)
    if x[s][f]['confident']:raise ValueError('Failure side marked confident')
 return x
if __name__=='__main__':
 (B/'extraction_schema.json').write_text(json.dumps(schema,indent=2));good=0;errors=[]
 for f in (B/'extractions').glob('*.json'):
  try:validate(json.loads(f.read_text()));good+=1
  except Exception as e:errors.append({'path':str(f),'error':str(e)[:500]})
 (B/'validation_errors.json').write_text(json.dumps(errors,indent=2));print({'valid':good,'invalid':len(errors)})
