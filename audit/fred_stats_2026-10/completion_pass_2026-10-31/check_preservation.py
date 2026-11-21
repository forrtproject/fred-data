"""Reject any export that changes a previously verified field or an unscoped gain."""
import csv,json
from pathlib import Path
F=Path(__file__).resolve().parent;B=F.parent
FIELDS=['n_o','es_value_o','pval_value_o','n_r','es_value_r','pval_value_r','reported_success']
def main():
 with (F/'baseline_results.csv').open(encoding='utf-8-sig') as stream:old={r['input_row_index']:r for r in csv.DictReader(stream)}
 with (B/'results.csv').open(encoding='utf-8-sig') as stream:new={r['input_row_index']:r for r in csv.DictReader(stream)}
 assert old.keys()==new.keys()
 scoped={(str(x['audit_id']),x['field']) for x in json.loads((F/'integration.json').read_text()).values()};changed=[];gains=[];unscoped=[];protected=0
 for aid,before in old.items():
  for field in FIELDS:
   a=before[field+'_final_verdict'];b=new[aid][field+'_final_verdict']
   if a in ['correct','error']:
    protected+=1
    for suffix in ['final_verdict','suggested_correction']:
     k=field+'_'+suffix
     if before[k]!=new[aid][k]:changed.append({'audit_id':int(aid),'field':field,'column':suffix,'before':before[k],'after':new[aid][k]})
   elif b in ['correct','error']:
    entry={'audit_id':int(aid),'field':field,'before':a,'after':b};gains.append(entry)
    if (aid,field) not in scoped:unscoped.append(entry)
 report={'protected_baseline_fields':protected,'changed_protected_fields':changed,'new_verified_fields':gains,'unscoped_gains':unscoped,'baseline_all_seven':sum(all(r[f+'_final_verdict'] in ['correct','error'] for f in FIELDS) for r in old.values()),'current_all_seven':sum(all(r[f+'_final_verdict'] in ['correct','error'] for f in FIELDS) for r in new.values())}
 (F/'preservation_check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in report.items()}));assert not changed and not unscoped
if __name__=='__main__':main()
