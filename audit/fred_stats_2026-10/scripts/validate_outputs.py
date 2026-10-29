"""Final accounting check; run after stopping the parent integration loop."""
import csv,json,hashlib,collections
from pathlib import Path
from compare import FIELDS,source_prefix,quote_ok
from schema import validate
B=Path(__file__).resolve().parents[1]
def main():
 manifest=json.loads((B/'run_manifest.json').read_text());progress=json.loads((B/'progress.json').read_text());rows=list(csv.DictReader((B/'results.csv').open(encoding='utf-8-sig')))
 assert [int(r['input_row_index']) for r in rows]==list(range(1,2165))
 assert len({r['effect_id'] for r in rows})==2164
 expected_errors=set();actual={f:collections.Counter() for f in FIELDS};projects=collections.defaultdict(lambda:{f:collections.Counter() for f in FIELDS})
 for r in rows:
  aid=int(r['input_row_index']);x=validate(json.loads((B/'extractions'/f'{aid}.json').read_text()));assert x['audit_id']==aid
  for f in FIELDS:
   verdict=r[f+'_final_verdict'];assert verdict in ['correct','error','not_comparable','unverified']
   assert r[f+'_resolution'] in ['agree','obvious','argon','unresolved']
   actual[f][verdict]+=1;projects[source_prefix(r['fred_id'])][f][verdict]+=1
   if verdict=='error':
    expected_errors.add((aid,f));assert r[f+'_location'] and r[f+'_suggested_correction'] not in ['',None]
 assert {f:dict(v) for f,v in actual.items()}==progress['field_counts']
 assert {p:{f:dict(c) for f,c in fs.items()} for p,fs in projects.items()}==progress['project_counts']
 assert expected_errors=={(a['audit_id'],a['field']) for a in progress['confirmed_errors']}
 for path in [*(B/'adjudications').glob('validated_*.json'),B/'obvious_resolutions.json']:
  for a in json.loads(path.read_text()):assert quote_ok({**a,'value':a['correct_value'] if a['correct_value'] is not None else 'undeterminable','confident':True}),(path,a['audit_id'],a['field'])
 consistency=list(csv.DictReader((B/'consistency.csv').open(encoding='utf-8-sig')));flags=list(csv.DictReader((B/'flag_confirmation.csv').open(encoding='utf-8-sig')))
 assert len(consistency)==2164 and len(flags)==sum(int(r['flag_count']) for r in consistency)
 summary=list(csv.DictReader((B/'field_summary_by_project.csv').open(encoding='utf-8-sig')))
 for f in FIELDS:
  ss=[r for r in summary if r['field']==f];assert sum(int(r['total']) for r in ss)==2164
  assert sum(int(r['errors']) for r in ss)==actual[f]['error']
  assert sum(int(r['evaluable']) for r in ss)==actual[f]['correct']+actual[f]['error']
 repo=B.parents[1];assert hashlib.sha256((repo/'output/FReD.xlsx').read_bytes()).hexdigest()==manifest['output_initial_sha256']
 print(json.dumps({'effect_rows':len(rows),'valid_checkpoints':len(rows),'confirmed_field_errors':len(expected_errors),'validated_evidence':'all retained adjudications and obvious resolutions','screen_flags':len(flags),'dataset_sha256':manifest['output_initial_sha256']}))
if __name__=='__main__':main()
