"""Validate documented field-specific calculations against reviewed source inputs."""
import math,re,sys
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'scripts'))
from compare import metric,quote_ok

def documented_proportion_odds_ratio(receipt,row,decision,source_path):
 """Reproduce an existing coding formula from explicitly quoted percentages."""
 assert decision.get('completion_pass')=='2026-10-31' and decision.get('replaces_unverified') is True
 assert decision.get('target_match_confirmed') is True and decision.get('verdict') in ['shipped_right','blind_right','both_wrong']
 field=receipt['field'];assert field in ['es_value_o','es_value_r']
 assert metric(row['es_type_'+field[-1]])==metric(decision.get('correct_metric'))=='or'
 assert Path(decision['source_path']).resolve()==Path(source_path).resolve()
 values=receipt['proportions'];inputs=receipt['quoted_inputs']
 assert len(values)==len(inputs)==len(receipt['input_roles'])==2
 assert all(isinstance(role,str) and role.strip() for role in receipt['input_roles'])
 assert all(re.fullmatch(r'0\.\d+',v) for v in values)
 expression=f'({values[0]}/(1-{values[0]}))/({values[1]}/(1-{values[1]}))'
 assert receipt['expected_coding_expression']==expression and expression in row['es_repr_'+field[-1]]
 assert quote_ok({**decision,'value':'documented proportions','confident':True})
 probabilities=list(map(Fraction,values))
 for probability,item in zip(probabilities,inputs):
  assert 0<probability<1 and isinstance(item['complement'],bool)
  assert re.fullmatch(r'\d+(?:\.\d+)?',item['percent'])
  percent=Fraction(item['percent'])/100;assert 0<percent<1
  assert probability==(1-percent if item['complement'] else percent)
  assert re.search(r'(?<![\d.])'+re.escape(item['percent'])+r'\s*%',decision['quote'])
 p,q=probabilities;result=(p/(1-p))/(q/(1-q))
 value=str(decision['correct_value']);assert re.fullmatch(r'\d+\.\d+',value)
 assert round(float(result),len(value.split('.')[1]))==float(value),'Reviewed OR does not reproduce the documented calculation'
 return result

def reviewed_ocr_minus_copy(receipt,row,decision,source_path):
 """Normalize one reviewed numeric token; do not alter the global parser."""
 assert decision.get('completion_pass')=='2026-10-31' and decision.get('replaces_unverified') is True
 assert decision.get('target_match_confirmed') is True and decision.get('verdict')=='blind_right'
 field=receipt['field'];assert field in ['es_value_o','es_value_r']
 assert metric(row['es_type_'+field[-1]])==metric(decision.get('correct_metric'))=='b (unstd)'
 assert Path(decision['source_path']).resolve()==Path(source_path).resolve()
 token=receipt['printed_value'];assert re.fullmatch(r'⫺(?:\d+(?:\.\d+)?|\.\d+)',token)
 normalized='-'+token[1:];assert decision['correct_value']==normalized
 assert receipt['source_label'] in receipt['statistic_quote'] and receipt['source_label'] in decision['quote']
 assert token in receipt['statistic_quote'] and token in decision['quote']
 assert 'negative' in receipt['negative_context_quote'].lower()
 for key in ['statistic_quote','negative_context_quote']:
  assert quote_ok({'quote':receipt[key],'source_path':source_path,'value':token,'confident':True,'location':decision['location']})
 return normalized

def documented_f_to_r_to_d(receipt,row,decision,source_path):
 """Reproduce an existing coding convention, without assuming group sizes."""
 assert decision.get('completion_pass')=='2026-10-31' and decision.get('replaces_unverified') is True
 assert decision.get('target_match_confirmed') is True and decision.get('verdict') in ['shipped_right','blind_right','both_wrong']
 field=receipt['field'];assert field in ['es_value_o','es_value_r']
 assert metric(row['es_type_'+field[-1]])==metric(decision.get('correct_metric'))=='d'
 assert Path(decision['source_path']).resolve()==Path(source_path).resolve()
 assert receipt['df1']==1 and isinstance(receipt['df2'],int) and not isinstance(receipt['df2'],bool) and receipt['df2']>0
 f=float(receipt['f']);assert math.isfinite(f) and f>=0
 statistic=f"F(1, {receipt['df2']}) = {receipt['f']}"
 expression='esc::cohens_d(r = FReD:::convert_effect_sizes("'+statistic+'", "test statistic"))'
 assert receipt['expected_coding_expression']==expression and expression in row['es_repr_'+field[-1]]
 assert quote_ok({'quote':receipt['statistic_quote'],'source_path':source_path,'value':statistic,'confident':True,'location':decision['location']})
 pattern=r'F\(1,\s*'+str(receipt['df2'])+r'\)\s*(?:=|5)\s*'+re.escape(receipt['f'])+r'(?![\d.])'
 assert re.search(pattern,receipt['statistic_quote']) and re.search(pattern,decision['quote'])
 r=math.sqrt(f/(f+receipt['df2']));result=2*r/math.sqrt(1-r*r)
 value=str(decision['correct_value']);assert re.fullmatch(r'\d+\.\d+',value)
 assert round(result,len(value.split('.')[1]))==float(value)
 return result

def documented_equal_group_d(receipt,row,decision,source_path):
 assert decision.get('completion_pass')=='2026-10-31' and decision.get('replaces_unverified') is True
 assert decision.get('target_match_confirmed') is True and decision.get('verdict') in ['shipped_right','blind_right','both_wrong']
 field=receipt['field'];assert field in ['es_value_o','es_value_r']
 assert metric(row['es_type_'+field[-1]])==metric(decision.get('correct_metric'))=='d'
 assert Path(decision['source_path']).resolve()==Path(source_path).resolve()
 groups=receipt['groups'];assert len(groups)==2
 assert all(isinstance(g['n'],int) and not isinstance(g['n'],bool) and g['n']>1 for g in groups)
 assert groups[0]['n']==groups[1]['n'],'Pooled SD requires explicit equal group sizes'
 for g in groups:
  assert Fraction(g['sd'])>0
  for key in ['mean_sd_quote','sample_quote']:
   assert g['source_label'].lower() in g[key].lower()
   assert quote_ok({'quote':g[key],'source_path':source_path,'value':'documented input','confident':True,'location':'documented '+key})
  assert re.search(r'\bn\s*(?:=|5)\s*'+str(g['n'])+r'\b',g['sample_quote'])
  for number in [g['mean'],g['sd']]:
   pattern=r'(?<![\d.])'+re.escape(number)+r'(?![\d.])'
   assert re.search(pattern,g['mean_sd_quote']) and re.search(pattern,decision['quote'])
 a,b=groups
 expression=f"=({a['mean']}-{b['mean']})/SQRT(({a['sd']}^2+{b['sd']}^2)/2)"
 assert receipt['expected_coding_expression']==expression
 assert expression in row['es_repr_'+field[-1]],'Calculation is not documented in original coding'
 result=float(Fraction(a['mean'])-Fraction(b['mean']))/math.sqrt(float((Fraction(a['sd'])**2+Fraction(b['sd'])**2)/2))
 value=str(decision['correct_value']);assert re.fullmatch(r'-?\d+\.\d+',value)
 assert round(result,len(value.split('.')[1]))==float(value),'Reviewed value does not reproduce the documented calculation'
 return result
