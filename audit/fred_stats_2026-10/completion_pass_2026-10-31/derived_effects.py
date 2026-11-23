"""Validate documented field-specific calculations against reviewed source inputs."""
import math,re,sys
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'scripts'))
from compare import metric,quote_ok

def reviewed_standardized_beta_copy(receipt,row,decision,source_path):
 """Copy an explicitly standardized reviewed coefficient, without rescaling."""
 assert decision.get('completion_pass')=='2026-10-31' and decision.get('replaces_unverified') is True
 assert decision.get('target_match_confirmed') is True and decision.get('verdict')=='shipped_right'
 field=receipt['field'];assert field in ['es_value_o','es_value_r']
 assert metric(row['es_type_'+field[-1]])==metric(decision.get('correct_metric'))=='beta (std)'
 assert Path(decision['source_path']).resolve()==Path(source_path).resolve()
 value=str(decision['correct_value']);assert re.fullmatch(r'-?\d+\.\d+',value)
 assert 'All other variables are standardized.' in receipt['standardization_quote']
 interpretation=receipt['sd_interpretation_quote']
 assert '1-SD higher perceived similarity' in interpretation and value+'-SD higher concurrent life satisfaction' in interpretation
 assert value+'-SD higher concurrent life satisfaction' in decision['quote']
 for quote in [receipt['standardization_quote'],interpretation,decision['quote']]:
  assert quote_ok({'quote':quote,'source_path':source_path,'value':value,'confident':True,'location':decision['location']})
 printed=receipt['printed_value'];assert re.fullmatch(r'\d*\.\d+',printed)
 assert round(float(value),len(printed.split('.')[1]))==float(printed)
 return value

def documented_proportion_h(receipt,row,decision,source_path):
 """Reproduce an existing signed Cohen's h formula from quoted percentages."""
 assert decision.get('completion_pass')=='2026-10-31' and decision.get('replaces_unverified') is True
 assert decision.get('target_match_confirmed') is True and decision.get('verdict') in ['shipped_right','blind_right','both_wrong']
 field=receipt['field'];assert field in ['es_value_o','es_value_r']
 assert metric(row['es_type_'+field[-1]])==metric(decision.get('correct_metric'))=="cohen's h"
 assert Path(decision['source_path']).resolve()==Path(source_path).resolve()
 values=receipt['proportions'];percentages=receipt['percentages']
 assert len(values)==len(percentages)==len(receipt['input_roles'])==2
 assert all(isinstance(role,str) and role.strip() for role in receipt['input_roles'])
 assert all(re.fullmatch(r'0\.\d+',v) for v in values)
 expression=f'2 * (asin(sqrt({values[0]})) - asin(sqrt({values[1]})))'
 assert receipt['expected_coding_expression']==expression and expression in row['es_repr_'+field[-1]]
 assert quote_ok({**decision,'value':'documented proportions','confident':True})
 for value,percent in zip(values,percentages):
  assert re.fullmatch(r'\d+(?:\.\d+)?',percent) and 0<Fraction(value)<1
  assert Fraction(value)==Fraction(percent)/100
  assert re.search(r'(?<![\d.])'+re.escape(percent)+r'\s*%',decision['quote'])
 p,q=map(float,values);result=2*(math.asin(math.sqrt(p))-math.asin(math.sqrt(q)))
 value=str(decision['correct_value']);assert re.fullmatch(r'-?\d+\.\d+',value)
 assert round(result,len(value.split('.')[1]))==float(value),'Reviewed h does not reproduce the documented calculation'
 return result

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

def _unique_binary_event_count(n,event_percent,other_percent):
 """Require a unique integer count within half a percentage point of both labels.

 Endpoints include either rounding tie choice; no tie convention is inferred.
 """
 assert type(n) is int and n>1
 assert all(type(p) is int and 0<=p<=100 for p in [event_percent,other_percent])
 candidates=[k for k in range(1,n) if abs(Fraction(100*k,n)-event_percent)<=Fraction(1,2) and abs(Fraction(100*(n-k),n)-other_percent)<=Fraction(1,2)]
 assert len(candidates)==1,'Rounded percentages do not identify unique binary counts'
 return candidates[0]

def documented_count_odds_ratio(receipt,row,decision,source_path):
 """Validate the existing Study 1 positive/negative count-odds calculation."""
 assert receipt.get('audit_id')==decision.get('audit_id')==1099
 assert receipt['field']=='es_value_o'
 assert decision.get('completion_pass')=='2026-10-31' and decision.get('replaces_unverified') is True
 assert decision.get('target_match_confirmed') is True and decision.get('verdict')=='both_wrong'
 assert metric(row['es_type_o'])==metric(decision.get('correct_metric'))=='or'
 assert Path(decision['source_path']).resolve()==Path(source_path).resolve()
 groups=receipt['groups'];assert len(groups)==2
 assert [g['source_label'] for g in groups]==['Positive','Negative']
 assert all(g['n']==24 and type(g['n']) is int for g in groups)
 allocation=' '.join(receipt['allocation_quote'].split())
 assert 'randomly assigned to one of three conditions, with 24 participants in each condition and each participant receiving only one vignette' in allocation
 assert all(s in receipt['binary_choice_quote'] for s in ['Remain connected','Go back to reality'])
 assert re.search(r'N\s*(?:¼|=)\s*72\b',receipt['complete_n_quote'])
 for q in [receipt['allocation_quote'],receipt['binary_choice_quote'],receipt['complete_n_quote'],decision['quote']]:
  assert quote_ok({'quote':q,'source_path':source_path,'value':'documented count input','confident':True,'location':decision['location']})
 for g in groups:
  assert type(g['event']) is int and type(g['other']) is int and g['event']+g['other']==g['n']
  assert g['source_label']+' scenario' in g['response_quote']
  assert 'reality' in g['response_quote'] and 'remain connected' in g['response_quote']
  assert quote_ok({'quote':g['response_quote'],'source_path':source_path,'value':'binary response','confident':True,'location':decision['location']})
  for p in [g['event_percent'],g['other_percent']]:
   assert re.search(r'(?<![\d.])'+str(p)+r'%',g['response_quote'])
  assert g['event']==_unique_binary_event_count(g['n'],g['event_percent'],g['other_percent'])
 a,b=groups
 expression=f"({a['event']}/{a['other']}) / ({b['event']}/{b['other']})"
 assert receipt['expected_coding_expression']==expression and expression in row['es_repr_o']
 result=Fraction(a['event'],a['other'])/Fraction(b['event'],b['other'])
 assert re.fullmatch(r'\d+\.\d+',str(decision['correct_value']))
 assert Fraction(decision['correct_value'])==result
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
 half_allocation=receipt.get('allocation_basis')
 if half_allocation is not None:
  # This source spells out the total and assigns one half to each condition.
  # Keep the evidence proof local to the reviewed Study 1a field.
  assert receipt.get('audit_id')==871 and field=='es_value_o'
  assert half_allocation['kind']=='study_1a_explicit_halves' and all(g['n']==32 for g in groups)
  assert 'Sixty-four economics and business administration students' in half_allocation['total_quote']
  allocation=' '.join(half_allocation['allocation_quote'].split())
  assert 'Half of the participants received an organization chart where the line was rather short' in allocation
  assert 'whereas the other half of the participants received an organization chart where the line was rather long' in allocation
  for key in ['total_quote','allocation_quote']:
   assert quote_ok({'quote':half_allocation[key],'source_path':source_path,'value':'equal allocation','confident':True,'location':'Study 1a Method'})
 for g in groups:
  assert Fraction(g['sd'])>0
  for key in ['mean_sd_quote','sample_quote']:
   assert g['source_label'].lower() in g[key].lower()
   assert quote_ok({'quote':g[key],'source_path':source_path,'value':'documented input','confident':True,'location':'documented '+key})
  if half_allocation is None:assert re.search(r'\bn\s*(?:=|5)\s*'+str(g['n'])+r'\b',g['sample_quote'])
  for number in [g['mean'],g['sd']]:
   pattern=r'(?<![\d.])'+re.escape(number)+r'(?![\d.])'
   assert re.search(pattern,g['mean_sd_quote']) and re.search(pattern,decision['quote'])
 a,b=groups
 reverse=receipt.get('coding_convention')=='sample_weighted_recorded_sign_reversal'
 if reverse:
  tokens=receipt['coding_mean_tokens'];assert len(tokens)==2
  assert all(Fraction(token)==Fraction(group['mean']) for token,group in zip(tokens,groups))
  expression=f"MANUALLY REVERSED FROM =({tokens[0]}-{tokens[1]})/SQRT((({a['n']}-1)*{a['sd']}^2+({b['n']}-1)*{b['sd']}^2)/({a['n']}+{b['n']}-2)))"
 else:
  assert receipt.get('coding_convention') is None
  sd_tokens=receipt.get('coding_sd_tokens',[a['sd'],b['sd']]);assert len(sd_tokens)==2
  assert all(Fraction(token)==Fraction(group['sd']) for token,group in zip(sd_tokens,groups))
  expression=f"=({a['mean']}-{b['mean']})/SQRT(({sd_tokens[0]}^2+{sd_tokens[1]}^2)/2)"
 assert receipt['expected_coding_expression']==expression
 assert expression in row['es_repr_'+field[-1]],'Calculation is not documented in original coding'
 result=float(Fraction(a['mean'])-Fraction(b['mean']))/math.sqrt(float((Fraction(a['sd'])**2+Fraction(b['sd'])**2)/2))
 if reverse:result=-result
 value=str(decision['correct_value']);assert re.fullmatch(r'-?\d+\.\d+',value)
 assert round(result,len(value.split('.')[1]))==float(value),'Reviewed value does not reproduce the documented calculation'
 return result
