"""Propose raw bounds only; scientific dispositions are recorded after inspection."""
import json, hashlib, pathlib, unicodedata, re, difflib, sys
ROOT=pathlib.Path(__file__).resolve().parent
INPUT=ROOT/'strict_literal_quote_audit.input.json'
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def norm(s):
 out=[]; mapping=[]
 for j,c in enumerate(s):
  for d in unicodedata.normalize('NFKD',c):
   if d.isalnum():out.append(d.lower());mapping.append(j)
 return ''.join(out),mapping
def candidate(i):
 p=pathlib.Path(i['source_path']);assert digest(p)==i['source_sha256']
 s=p.read_bytes().decode('utf-8');n,m=norm(s);q,_=norm(i['existing_evidence']['quote']);k=n.find(q)
 if k>=0:return s,m[k],m[k+len(q)-1]+1,1
 blocks=difflib.SequenceMatcher(None,q,n,autojunk=False).get_matching_blocks()
 b=max(blocks,key=lambda b:b.size);k=b.b-b.a;k=max(0,k);end=min(len(n),k+len(q));return s,m[k],m[end-1]+1,b.size/len(q)
def show(a,b):
 for z in range(a,b):
  i=json.loads(INPUT.read_text())['issues'][z];s,a0,b0,r=candidate(i)
  print('\nISSUE',z,i['file_key'],i['field'],i['target_index'],'MATCH',round(r,3),'BOUNDS',a0,b0)
  print('REASON:',i['existing_evidence']['reason']);print('RAW CONTEXT:',repr(s[max(0,a0-450):min(len(s),b0+800)]))
if __name__=='__main__' and len(sys.argv)==3:show(int(sys.argv[1]),int(sys.argv[2]))

# Independent inspector notes, indexed only against immutable input membership.
NOTES={
0:('scope_objection','The local girls/boys contrast is real, but the later author conclusion says the study largely replicated the findings, particularly theory–practice and gender gaps. The claimed absence of a governing broad verdict needs scientific resolution.'),
1:('literal_primary_supported','Discussion explicitly contrasts decreasing CVs here with the absence of a decrease in Hulstijn et al.; the population/exposure difference is an explanatory limitation, not erased.'),
2:('literal_primary_supported','Main experiment and within-paper replication are introduced together; the replication examines alternative explanations for this main experiment.'),
3:('literal_primary_supported','Discussion names the Sabourin retest and reports agreement for cognitive/affective reactions alongside absent low-AS somatic decline; low group size and floor effects qualify inference.'),
4:('literal_primary_supported','Study 2 Discussion explicitly calls the intervention results a partial replication of the named prior studies.'),
5:('literal_primary_supported','Discussion compares acceptance policies directly with Yeung: similar silence/discouragement, differing explicit acceptance. This is a cross-domain survey comparison, not a causal experiment.'),
6:('literal_primary_supported','Discussion explicitly marks supportive-profile mother/father proportions inconsistent with Volling and Ryan; interpretation remains specific to profiles and the play task.'),
7:('literal_primary_supported','Conclusion confirms high CEO effect while contrasting industry and firm effects; use conclusion to avoid abstract sidebar intrusion.'),
8:('literal_primary_supported','Comparison section explicitly presents both common autonomy emphasis and differences in justice/explicability, including contextual Nigerian explanations.'),
9:('literal_primary_supported','Abstract names Maurer replication and directly states discrepant results with equal effectiveness across conditions.'),
10:('literal_primary_supported','Discussion explicitly replicates the delayed-reinforcement findings in Replication rats while challenging their interpretation via the added Delay condition.'),
11:('literal_primary_supported','General Discussion gives on-balance evidence for primacy despite smaller effects and failures with custom materials; success claim is bounded to original primacy effect.'),
12:('literal_primary_supported','Wave 2 discussion explicitly disallows meaningful statistical inference and warns graphical differences may be random, despite a tentative U-shaped conclusion.'),
13:('literal_primary_supported','Research questions concern curriculum effectiveness and retention in local classrooms; passage supports evaluation scope, not any claim that all prior work was exhaustively excluded.'),
14:('literal_primary_supported','Abstract describes philosophical application to a published case and theory debate, supporting commentary scope.'),
15:('scope_objection','Abstract reports age-driven mortality prediction and construct critique; it does not explicitly say the original mortality/criterion associations replicated as claimed. New MIDUS associations cannot alone establish full original replication.'),
16:('literal_primary_supported','Discussion explicitly states no helper preference and failure to replicate Hamlin, Wynn, and Bloom; agreement on age nulls does not reverse the target result.'),
17:('literal_primary_supported','Body identifies Kroch and Small 1978 social-role hypothesis and its retest; reference entry identifies the Sankoff chapter. Primary alone cannot authenticate external erroneous DOI metadata.'),
18:('literal_primary_supported','Results narrate nonreplicated vulnerability effects and replicated small immediate anxiety effect under Bayesian criterion, rather than relying on significance alone.'),
19:('literal_primary_supported','Abstract and experiment introduction identify Boroditsky et al. 2003 adjective/gender retest; reference entry supplies chapter identity. External Clark DOI mismatch is not independently authenticated here.'),
20:('literal_primary_supported','Methods transition explicitly names close replication of Prior 2008 in eight magpies with matching stages; Gallup paradigm origin is distinct from tested magpie result.'),
21:('literal_primary_supported','Conclusion says Sicherman results replicated under his approach but contrasts career prospects and questions indicator/specification validity.'),
22:('literal_primary_supported','Figure narrative explicitly attributes stronger sleep/dissociation correlation to including healthy controls; additional discussion needed for whole methodological critique, rather than table cells.'),
23:('literal_primary_supported','Abstract directly juxtaposes failure of main effects with replicated age moderation in Skurka retest.'),
24:('literal_primary_supported','Cross-study synthesis narrates agreement on fault concentration but explicitly contrasts original rejection of H4 with replication support.'),
25:('literal_primary_supported','Abstract links RASV to Gebauer Sedikides Neberich 2012b and describes three replication studies; external mislinked record requires separate bibliographic evidence.'),
26:('scope_objection','The main author synthesis affirms verbal overshadowing in both large replications. The contrasting secondary error-type distribution is real but the existing reason assumes it overrides that whole-target conclusion; scientific scope review is required.'),
27:('literal_primary_supported','Comparison explicitly identifies common guilt pathways and divergent direct guilt and pride pathways against Hofmann and Fisher.'),
28:('literal_primary_supported','Discussion identifies promising support-vector performance and explicitly contrasts stochastic-gradient false positives with Lanovaz and Hranchuk.'),
29:('literal_primary_supported','Introduction frames replication of quantitative/qualitative analyses with notable model differences; need result-specific passage for partial agreement, not an aim alone.'),
30:('literal_primary_supported','Synthesis explicitly calls multisite results partial confirmation of Ulrich; physiological differences qualify the restoration result.'),
31:('literal_primary_supported','Discussion reconciles Strack and Wagenmakers via camera presence; author cautions inference is probabilistic. Successful scope is the no-camera original procedure.'),
32:('literal_primary_supported','Replication Findings explicitly calls matching direction/magnitude without significance a partial replication; small sample and methodological differences qualify it.'),
33:('literal_primary_supported','Overall synthesis explicitly states partial confirmation and contrasts two findings with Ionin; no isolated significance interpretation needed.'),
34:('scope_objection','Authors apply preregistered criteria and call temporal effect direction consistent but magnitude inconsistent, in an overall limited-support synthesis. Treating this solely as smaller-but-successful suppresses their stated replication qualification.'),
35:('literal_primary_supported','Summary agrees on no forecast bias but explicitly contrasts teacher-effect sorting by race and prior achievement with CFR.'),
36:('literal_primary_supported','Discussion confirms DBDM underrepresentation but contrasts ordering of general versus conducting CBM categories; this is content comparison across materials.'),
37:('literal_primary_supported','General Discussion explicitly states replication of L2–L1 and failure of absent L1–L2 priming in the same named original task.'),
38:('literal_primary_supported','Need result-summary passage naming validated and unvalidated loci; legacy proposed passage is only caveats/pathway context and is insufficient by itself.'),
39:('literal_primary_supported','Discussion explicitly contrasts moderate/high graphic equivalence with Kees; broader pattern replicates many cessation conclusions rather than an unqualified all-results verdict.'),
40:('literal_primary_supported','Abstract explicitly qualifies confirmation of eye-gaze predictors with opposite direction for L2 gaze duration.'),
41:('literal_primary_supported','Introduction synthesis explicitly combines consistency with Milne/Boza and shifting privacy/direct-marketing relationships.'),
42:('literal_primary_supported','Conclusion explicitly validates differential PD VOC profiles but says original putative analytes could not be validated.'),
43:('literal_primary_supported','Synthesis explicitly contrasts moderation now with no original interaction while affirming correlated predictors and partial mediation.'),
44:('literal_primary_supported','Discussion restricts support for H1 to nonoffending subgroup and single question; full-sample endorsement differs.'),
45:('scope_objection','Appendix says the same sources were accessed but original sample could not be matched: 2054 rather than 1993 cumulative years because newer TFR data were included. Existing exact-original-data rationale overstates sample identity.'),
46:('literal_primary_supported','Empirical Strategy explicitly reproduces AJR with AJR data before alternative ancestry constructions.'),
47:('literal_primary_supported','Introduction explicitly reproduces territorial reversal but reverses conclusion for descendants; base-sample exact reproduction is separately stated in empirical strategy.'),
48:('literal_primary_supported','Discussion explicitly confirms false-tweet rating result in all four studies but shows true-tweet decline and conservative bias rather than discrimination.'),
49:('literal_primary_supported','Discussion explicitly reproduces money/no-money email result, then identifies potentially culturally biased single measure and underestimation of honesty.'),
50:('literal_primary_supported','Abstract explicitly replicates hedonic benefits independent of disposition, while cognitive cost is a different extension.'),
51:('literal_primary_supported','Author explicitly confirms overall earlier pattern while acknowledging total interaction-time and marital differences; confirmation is qualified in general.'),
52:('scope_objection','Abstract distinguishes nonsignificant Spanish independent sample from supportive pooled meta-analysis including previous data. The broad gene-risk conclusion is not an unqualified verdict on the independent retest.'),
53:('literal_primary_supported','General discussion explicitly confirms original questionnaire results but rejects illusory-learning inference using direct learning questions.'),
54:('literal_primary_supported','Abstract explicitly describes reproducing/assessing Piketty historical time series, supporting reproduction scope.'),
}
NOTES.update({
55:('literal_primary_supported','Author identifies unrecovered claimed averages and arithmetic errors, while surrounding source-construction critique concerns robustness; this is a reproduction critique, not new-sample evidence.'),
56:('literal_primary_supported','Named conceptual replication model 2a closely resembles Jokela; subsequent added covariates and symptom sets are distinct analyses.'),
57:('literal_primary_supported','Discussion explicitly says none of 13 classroom competencies reliably increased; unreliable subscales and pedagogical alternatives qualify the failure.'),
58:('literal_primary_supported','Abstract explicitly replicates effect with original awareness criterion but not three alternatives, and warns against unaware-conditioning claims.'),
59:('literal_primary_supported','Introduction explicitly reimplements author code to reproduce computational experiments; compute-limited settings and extra dataset limit strict equivalence.'),
60:('scope_objection','Discussion reports inferior performance and code/method discrepancies, but under adapted Colab execution and reduced training/resolution. This does not establish failure of identical original computation; existing reason must preserve this non-equivalence when assigning computation issues.'),
61:('literal_primary_supported','Methods reconstruct estimation sample from original primary databases and author Stata kit; reconstruction, rather than supplied processed data, is explicit.'),
62:('literal_primary_supported','Summary challenges common-ownership causal inference; separate baseline narrative explicitly reports perfect/second-decimal replication, so need a baseline quote as well as robustness context.'),
63:('literal_primary_supported','Discussion explicitly distinguishes close baseline-time match from strikingly different extended-period results. Exact data identity is not established by same time window alone.'),
64:('literal_primary_supported','Introduction states return to primary sources and construction of datasets modeled on originals to reproduce tables before specification reanalysis.'),
65:('literal_primary_supported','Introduction explicitly records nearly matching output with important graphical exception and distinguishes later robustness reanalysis.'),
66:('literal_primary_supported','Discussion explicitly supports H1 and partially H2 before adding NOSQ; the new control changes incremental effects and remains an important validity qualification.'),
67:('scope_objection','Author says search costs may explain overbidding and rejection of standard model is premature; existing reason overstates this as demonstration that search costs explain it. Raw text even contains an apparent missing negation; no OCR/sign repair is permissible.'),
68:('literal_primary_supported','Abstract confines identical-data/method reproduction to public quasi-experiments, explicitly allowing augmentation; proprietary core data are outside this test.'),
69:('literal_primary_supported','Conclusion of monthly analysis explicitly reports unexpected numerical discrepancy and incompatible economic effect after broader specification.'),
70:('literal_primary_supported','General discussion explicitly contrasts learning with original methods against absence with rigorous trial-level awareness checks, motivating validity critique.'),
71:('literal_primary_supported','Abstract reports null engagement differences and same-race preference, but original-specific comparison in discussion is needed to support agreement rather than isolated findings.'),
72:('literal_primary_supported','Introduction explicitly uses same data and models to recreate original tables before alternative specification for regression-to-mean concern.'),
73:('literal_primary_supported','Conclusion explicitly finds no shift in original replication and confound-addressing extension; computation claim remains limited to reconstructed data.'),
74:('literal_primary_supported','Discussion directly names Hille/Schupp retest and contrasts cognition/achievement while corroborating personality literature; personality agreement with exact original requires detailed comparison.'),
75:('literal_primary_supported','Evaluation explicitly calls primary analysis partial replication but failure of central condition-by-block claim; own brief evaluation must retain this distinction.'),
76:('literal_primary_supported','Conclusion combines support for human capital with new gender/context findings; inspect hypothesis narrative for original three-hypothesis support, not table joins.'),
77:('literal_primary_supported','Discussion directly contrasts Stoffer modulation with replication and affirms matching precue pattern; effect-specific mixed scope is explicit.'),
78:('literal_primary_supported','Layer-specific conclusion directly agrees for Ideal L2 but not ought selves relative to Papi/Khajavy; not all paths are asserted to agree.'),
79:('literal_primary_supported','Regression comparison narrates rank, return-applicant and coauthor differences; author expressly warns coauthor operationalization may make comparison ineffective.'),
80:('literal_primary_supported','Abstract records six of twelve original comparisons and absent frequent-flyer effect; body partial-replication judgment needed rather than p values alone.'),
81:('literal_primary_supported','Discussion affirms broad iconic memory account but explicitly contrasts ordering effect with Sperling and notes design differences.'),
82:('literal_primary_supported','Author explicitly concludes very close replication from pattern and effect sizes despite nonsignificant interaction; qualification retained.'),
83:('literal_primary_supported','Configuration discussion explicitly identifies similarities and differences and confirms positive Types 1/4 effects; further text supplies opposite Types 2/3.'),
84:('literal_primary_supported','Discussion explicitly calls preregistered item-set result conceptual replication while qualifying weaker strict reconstruction by item-count reliability.'),
85:('literal_primary_supported','Estimation explicitly reports equivalent mathematical model with non-centered implementation and closely reproduced estimates; this is author judgment, not independently rerun computation.'),
86:('literal_primary_supported','Narrative explicitly gives differing coefficients and sample sizes while calling SCORE inference successful; numerical recovery and inference criteria are distinguished.'),
87:('literal_primary_supported','Deviations explicitly says newly downloaded stochastic Google Trends sample differs from unavailable original sample; same period/source is not same observations.'),
88:('literal_primary_supported','Results explicitly says original Panic Buying Index association replicated; novel keyword operationalization is retained in preceding method.'),
89:('literal_primary_supported','Author explicitly calls results partly consistent with Chowdhury after null average framing, absent main gender contrast and aligned extreme-allocation analysis.'),
90:('literal_primary_supported','Discussion contrasts absent friendship-quality and parent-rated significance with original PEERS; confirmatory knowledge/get-together context should accompany this contrast.'),
91:('literal_primary_supported','Discussion directly names original and agrees on aggregated reading courses while no other teacher characteristics are significant.'),
92:('literal_primary_supported','Normative/resource discussion explicitly agrees with Harper/Kim on norms and differs on journal pressure and facilitating conditions; raw printed p sign is preserved, not corrected.'),
93:('literal_primary_supported','Many Labs discussion explicitly places imagined-contact overestimate among replicated effects, distinguishing two named nonreplications.'),
94:('literal_primary_supported','Discussion explicitly says Ert Study 1 findings do not replicate; city, covariate and sample differences are explanatory limits.'),
95:('literal_primary_supported','Conclusion explicitly retains within-subject robustness but attributes first-impression failure to demand characteristics; inference is stated as suggests, not causal proof.'),
96:('literal_primary_supported','Limitations directly contrasts original college-education association with absence here and notes power limit; main partisan replication needs separate context.'),
97:('literal_primary_supported','Discussion says no moderators associated with adjustment and treats normal anchoring magnitude as a data-quality argument; online design caveat is retained.'),
98:('literal_primary_supported','Summary explicitly restricts Southgate replication to FB1 and states not fully replicated; added narration may change task process.'),
99:('literal_primary_supported','General conclusion explicitly finds no short-term causal literary-fiction effect and separates ART lifetime-exposure correlation.'),
100:('literal_primary_supported','Discussion explicitly scopes convergence to main effects and two conditions, then contrasts word-pair/generic result; statistical significance difference is author-described and not inferred here.'),
101:('literal_primary_supported','Discussion explicitly defines partial replication across tasks and distinguishes equivalence tests from nonsignificant group effects.'),
102:('literal_primary_supported','General Discussion names Forster/Denzler retest and says no hypothesis support in either experiment, distinguishing indecisive first and null-supporting second.'),
103:('literal_primary_supported','Discussion explicitly enumerates two replications, two opposite and four null results; its consistent-support conclusion is qualified and not all-findings failure.'),
104:('literal_primary_supported','Abstract explicitly affirms most Mavletova/Couper findings while contrasting trust/confidentiality results across countries.'),
105:('literal_primary_supported','Abstract explicitly contrasts failed/reversed partner devotion with consistently higher presumed financial contribution in two retests.'),
106:('literal_primary_supported','Results explicitly says pragmatic-failure retest hypothesis was unsupported; successful language performance is not replication success.'),
107:('literal_primary_supported','Abstract explicitly distinguishes DeYoung et al. 2014 replicated empirical study from 2007 personality-aspect taxonomy.'),
108:('literal_primary_supported','Summary explicitly supports named JK predictions except 9 and contrasts post-ideal fertility trend; new prediction 8 is separate.'),
109:('literal_primary_supported','Discussion explicitly agrees overall with Neumann/Hopf while recognizing exceptions and challenging Fukushima explanation; broad agreement is qualified.'),
110:('literal_primary_supported','Abstract explicitly replicates logical-status liking while attributing it to conclusion content rather than logicality, supporting validity critique.'),
})
NOTES.update({
111:('literal_primary_supported','Author explicitly calls remaining fit-statistic differences minor and essentially same results, while sample/residual/weight decisions are discussed before the quote.'),
112:('literal_primary_supported','Alternative-model synthesis explicitly finds non-sparse models neither fit data nor confirm four varieties; no isolated fit threshold is used as a verdict.'),
113:('scope_objection','Discussion explicitly says similar to Smaby and compares MSA viability, then compares suitability with Cividini-Motta/Ahearn. Existing reason says only general viability rather than an empirical comparison; descriptive-only scope needs resolution.'),
114:('literal_primary_supported','Final discussion explicitly says findings replicate and extend prior work immediately after acknowledging no third uncertain-nonbeliever group.'),
115:('literal_primary_supported','Discussion explicitly states absent critical original interaction with strong null-model evidence; no spliced legacy string is used.'),
116:('literal_primary_supported','Conclusion explicitly confirms around 90 percent precision/recall and qualifies it by granularity and practical file recommendation limits.'),
117:('literal_primary_supported','Results explicitly contrasts SRMR sensitivity with Hu/Bentler; extension tests more model conditions, not a claim of universal index failure.'),
118:('literal_primary_supported','General discussion explicitly contrasts no individual-validity differences with support for two named key Seli findings, qualifying within-subject evidence as weak.'),
119:('scope_objection','Paper explicitly targets Hulstijn partial conceptual replication, but abstract also evaluates Segalowitz hypothesis and says no counterevidence. Treating Segalowitz as exclusively methodological background overstates the primary text; original empirical retest versus theoretical validation needs resolution.'),
120:('literal_primary_supported','Methods explicitly repeats assessments of included Discordant Reviews and evaluates agreement, supporting reanalysis scope rather than a new test of the algorithm-development paper.'),
121:('no_support','Methods confirms reanalysis of reviews; citation 13 identifies Bakdach, but the exact target mapping to that first review is not established in a short contiguous judgment. Table 2 columns separate identities from decisions; joining them is disallowed.'),
122:('scope_objection','Thesis abstract establishes Sonbul/Schmitt retest but cannot establish equality of two repository DOI records, source downloads and shipped rows. Existing duplicate-removal rationale relies on external provenance rather than this primary passage.'),
123:('literal_primary_supported','Experiment 1 Discussion explicitly replicates rare-onset cue capture but contrasts original trial-lag dependence; extension frequency scope is separately qualified.'),
124:('literal_primary_supported','Likelihood section explicitly says no suitable original study on BIF and identifies Wakslak as manipulation source; paradigmatic design is distinguished from a specific prior empirical retest.'),
125:('literal_primary_supported','Discussion explicitly contrasts temporal SDE trend with Ramirez, while comparing low prevalence; publication windows differ.'),
126:('literal_primary_supported','Abstract explicitly calls top-ten ratings different, rather than inferring success from partial item overlap.'),
127:('scope_objection','Authors replicate under successive-gains criterion but immediately say statistical analysis failed for A, procedure needs refinement, and group design demands statistically significant differences. Existing reason understates this methodological qualification.'),
128:('literal_primary_supported','Results explicitly replicates focal low-price slope but not high-price slope; staged stopping and corrected inference-criteria wording limit interpretation.'),
129:('literal_primary_supported','Combined-sample summary explicitly says partially failed: Hebrew mapping replicates, overall and English ANOVAs do not.'),
130:('literal_primary_supported','Study design explicitly calls the computational Racine-only part reanalysis and separates a new contemporary-corpus follow-up.'),
131:('literal_primary_supported','Racine reanalysis models only 24 of roughly 50 stylistic patterns; claims cannot extend to unmodeled context-dependent patterns. Need actual results confirmation rather than aim alone.'),
132:('literal_primary_supported','Conclusion explicitly separates partial original-data reconciliation across axioms from new online IIA-only confirmation of all three results.'),
133:('scope_objection','Authors call direct results very close and attribute minor differences to alternative dataset construction. This supports nonidentity, but not failure to rerun identical original observations; computation-axis interpretation must retain reconstructed sample limitation.'),
134:('literal_primary_supported','Results explicitly reproduces HMOR with reported data and distinguishes corrected performance/price data from numerical rerun.'),
135:('literal_primary_supported','Introduction explicitly replicates all provided-code results before alternative specifications; original model recovery is separate from later robustness.'),
136:('literal_primary_supported','Section explicitly reproduces major estimates with simulation discrepancies below .01; following text says Figure 3 could not be recovered, so support is bounded to central table estimates.'),
137:('literal_primary_supported','Abstract explicitly reproduces main findings then removes multiple-treatment counties, distinguishes later NIBRS new-data test.'),
138:('literal_primary_supported','Appendix-table discussion explicitly identifies material attenuation rather than published strengthening; not a technical inability to generate comparable output.'),
139:('literal_primary_supported','Introduction explicitly recovers main-body results after package issues, retaining unrecovered appendix/missing-data qualification.'),
140:('literal_primary_supported','Main results section explicitly reproduces worker-equity estimates; later correction of duplicated data and sample restriction is separate from rerun.'),
141:('literal_primary_supported','Computational section explicitly reproduces all tables with .001 standard-error differences; subsequent coding errors concern published implementation validity.'),
142:('literal_primary_supported','Direct reproduction section explicitly recovers main paper figures/tables with cosmetic differences, retaining uncompiled supplementary tables and weighted-N discrepancy.'),
143:('literal_primary_supported','Conclusion explicitly questions confident mass/elite similarity because manipulations seldom worked and successful ones show larger gaps; broad inference is qualified.'),
144:('literal_primary_supported','Computational section explicitly recovers main and appendix outputs in Stata 17 before correcting two published-code errors.'),
145:('literal_primary_supported','A single prose table-note sentence states original results exactly or closely matched; no table cells or columns are concatenated.'),
146:('literal_primary_supported','Computational section explicitly reproduces all tables from published code/data before identifying wrong-variable construction in Table 4.'),
147:('literal_primary_supported','Conclusion explicitly calls output response fairly robust, retaining lower peak-impact z scores and bootstrap procedure explanation.'),
148:('literal_primary_supported','Introduction explicitly recovers main Table 2/Figure 2 with original code before minor leap-day correction.'),
149:('literal_primary_supported','Introduction explicitly resolves Conley discrepancy by supplied older ado version, reproducing reported standard errors.'),
150:('literal_primary_supported','Author explicitly says no additional robustness checks due to time limit, despite using robustness language for consistent baseline reconstructions.'),
151:('literal_primary_supported','Abstract explicitly recovers focal test in both original-data studies and says discovered errors did not change main results.'),
152:('literal_primary_supported','Conclusion explicitly says main findings successfully reproduced and minor code/reporting issues did not clash with narrative; frequentist extension is separate.'),
153:('literal_primary_supported','Final-stage narrative explicitly judges SCORE claim unsuccessful, despite descriptive causal-correction advantage.'),
154:('scope_objection','Report explicitly says all seven significant effects replicated and four newly significant effects had size/direction consistent with original trends, likely power differences. Existing reason treats this solely as contradictory findings and suppresses their concordance interpretation.'),
155:('literal_primary_supported','Results explicitly confirms focal SCORE claim then contrasts another transition with original hypotheses; success is local rather than paper-wide.'),
156:('literal_primary_supported','Results directly names Coleman ICC replication alongside Bryk/Raudenbush; supports empirical target relationship, not an adjudicated overall outcome.'),
157:('literal_primary_supported','Introduction explicitly reanalyses Imai and rejects his estimate in new experiment; target is an earlier reanalysis, distinct from original treatment study.'),
158:('literal_primary_supported','Intervention design explicitly replicates research including Hulleman 2010; Study 2 Discussion supplies partial-replication outcome for named pair.'),
159:('literal_primary_supported','Study 2 design explicitly identifies conceptual retest of Makel/Plucker/Hegarty in BITRA; later comparison needed for outcome scope.'),
160:('literal_primary_supported','Introduction explicitly tests Robst with both objective/subjective training measures and confirms original training pattern.'),
161:('literal_primary_supported','Discussion explicitly repeats both Strack and Wagenmakers procedures; result synthesis separately confirms camera/null pairing.'),
162:('literal_primary_supported','Introduction explicitly reproduces Rothstein relationship but interprets it mechanically because estimates share data; retest is distinct from mere citation.'),
163:('literal_primary_supported','Experiment 3 setup and Discussion explicitly retest native-speaker old/new masked priming benchmark attributed to Forster 1985; language-group extension is distinct.'),
164:('literal_primary_supported','Experiment 3 setup and Discussion explicitly retest old/new native-speaker priming benchmark also attributed to Rajaram/Neely 1992; not solely a task-method citation.'),
165:('literal_primary_supported','Discussion explicitly attributes H6 qualification/commitment prediction to Moodie 2023 and says it did not replicate; target relationship only.'),
166:('literal_primary_supported','Introduction attributes Western age/pass benchmark to named studies including Nielsen 2003, then frames cross-cultural simplified mark-test challenge; original-specific protocol evidence is additionally inspected.'),
167:('literal_primary_supported','Introduction explicitly retests negative-affect state-by-trait null of McNiel/Fleeson, changing design and power; actual null result is in subsequent discussion.'),
168:('literal_primary_supported','Introduction explicitly retests same null also attributed to McNiel/Lowman/Fleeson 2010; outcome support comes from counterdispositional negative-affect discussion.'),
169:('literal_primary_supported','Results explicitly tests Karban UC risk hypothesis in entire sample and finds no association, distinguishing modest pooled evidence from independent retest.'),
170:('literal_primary_supported','Named numbered sunk-cost experiment identifies Oppenheimer target and design; discussion includes it among eleven replicated effects, while two failures are separately named.'),
171:('literal_primary_supported','Named numbered reciprocity experiment identifies Hyman/Sheatsley target and updates target country; broad result synthesis includes it among replicated effects.'),
172:('literal_primary_supported','Named numbered allowed/forbidden experiment identifies Rugg target and country wording adaptation; broad result synthesis includes it among replicated effects.'),
173:('literal_primary_supported','Named quote-attribution experiment identifies Lorge/Curtis, with changed liked/disliked individuals; original effect accessed through Moskowitz, so exact procedural identity is limited.'),
174:('literal_primary_supported','Conclusion explicitly says Edelman/Luca lower-price finding for Black hosts replicated; no race-price causal identification is claimed.'),
175:('literal_primary_supported','Introduction explicitly identifies Kakar among host-race price targets; discussion contrasts absent Asian-host price difference, so target inclusion does not imply overall success.'),
176:('literal_primary_supported','Discussion explicitly contrasts absent Asian price effect with Wang and Kakar; original cities differ from present New York listings.'),
177:('scope_objection','Passage establishes Kim 2006 and Kim/White retest but concerns control-group summer loss, not an overall failed treatment-effect verdict. Heterogeneous effects by school poverty require outcome scope review.'),
178:('literal_primary_supported','Study list explicitly identifies Epley/Gilovich 2005 Study 2 forewarning retest; overall discussion says no moderator predicted adjustment.'),
179:('literal_primary_supported','Discussion explicitly reports failure of Surian/Geraci pattern even with narration; added narration and gaze-window sensitivity qualify procedural comparability.'),
180:('scope_objection','Introduction cites Kuziemko for background redistributive-preference puzzle and promises documentation; this alone does not establish deliberate retest of that exact report rather than overlapping descriptive series. Need original-specific empirical comparison.'),
181:('literal_primary_supported','Summary juxtaposes supported additional Chakravarty prediction 4 with absent birth-order peak after correcting omitted gender main effect; supports mixed-scope claim.'),
182:('scope_objection','Discussion explicitly compares MSA suitability with Cividini-Motta/Ahearn, not merely task adoption. Descriptive-only outcome rationale needs to account for author empirical comparison.'),
})
for _z in range(183,203):
 _i=json.loads(INPUT.read_text())['issues'][_z]
 NOTES[_z]=('no_support',_i['existing_evidence']['reason'].split(' is reassessed')[0]+': inclusion and bibliographic identity are present in Tables 1–2 and References, and the general methods confirm reassessment. The specific review-selection/step comparison is distributed across table columns; no concise contiguous raw author judgment supports that exact target-specific reason. No column join is promoted. This is a quotation-support limitation, not a finding that this review was not reassessed; per-target outcomes remain unverified.')
NOTES[166]=('scope_objection','Introduction attributes the Western pass-rate benchmark to Nielsen, Dissanayake and Kashima 2003, but the inspected Methods sticker-procedure citation is Nielsen and Dissanayake 2003 (two authors), alongside Nielsen et al. 2006. Existing reason conflates these identities when claiming method corroboration. Benchmark attribution remains present; original-specific empirical target status needs resolution.')
NOTES[180]=('literal_primary_supported','Introduction attributes flat/decreasing redistribution demand to Kuziemko et al. 2013; Section I explicitly aims to replicate this earlier finding before extending subgroup trends. This is overlapping historical-survey replication/reanalysis, not evidence of an independent experimental sample.')
# Selections below identify newly inspected RAW passages; normalized lookup locates
# bounds only. The output always comes directly from the immutable source slice.
SELECT={
0:('Furthermore, the fact that this study largely replicated','particularly concerning the findings concerning the theory–practice and gender gaps'),
7:('We generally confirm H&Q\'s finding of a high CEO effect, but find a smaller industry effect','and a larger firm effect in our larger sample'),
17:('Here, we ask: Can Kroch and Small’s host/guest vs. caller difference be replicated','on a larger data set using more modern statistical methods'),
19:('Abstract: In this paper, we present two attempts to replicate','(Boroditsky et al. 2003)'),
22:('Interestingly, when including the HC group to mimic the design of the previous study','we did replicate the highly significant finding for the sleep deprivation-dissociation association'),
29:('This study presents a replication and extension of the original study (Spadini et al. 2018)','compared to other platforms'),
38:('the Prata Village, 23 were not associated','indicating leprosy protection (Table 2)'),
62:('We replicate AST’s results perfectly','specifications'),
76:('All in all, these results suggest the existence of an ‘U’ shaped relationship','consistent with that stated in our Hypothesis 3'),
113:('This study systematically replicated the use','MSA to be suitable to determine the relative reinforcing efficacy of tokens and other social consequences'),
119:('The results revealed that, consistent with findings','no counterevidence against Segalowitz and Segalowitz’ (1993) hypothesis was found'),
127:('However, the statistical analysis did not confirm','this analysis demands a demonstration that the differences are statistically significant'),
131:('Regarding Racine and the Classical Age','are even more frequent in Racine’s work than Spitzer showed'),
155:('These results are not in line','participants would judge anger as appearing significantly sooner on an old than on a young face'),
163:('However, it might be argued that masked repetition priming','and hence must be treated as a reliable phenomenon'),
164:('However, it might be argued that masked repetition priming','and hence must be treated as a reliable phenomenon'),
166:('Typically, marking is done with rouge','(Nielsen & Dissanayake, 2003; Nielsen et al., 2006; Povinelli, Landau, & Perilloux, 1996; Skouteris, Spatero, & Lazaridis, 2006; Suddendorf, Simcock, & Nielsen, 2007)'),
177:('The effects of the treatments were positive for high poverty schools','the effects of the treatments were negative'),
180:('To ensure that our heterogeneous patterns are not driven','flat aggregate demand using our survey measures'),
182:('This study systematically replicated the use','MSA to be suitable to determine the relative reinforcing efficacy of tokens and other social consequences'),
}

def locate(s,start,end,after=0):
 n,m=norm(s);a,_=norm(start);b,_=norm(end)
 k=n.find(a)
 while k>=0 and m[k]<after:k=n.find(a,k+1)
 assert k>=0,('start not found',start)
 j=n.find(b,k);assert j>=0,('end not found',end)
 aa,bb=m[k],m[j+len(b)-1]+1
 if bb<len(s) and s[bb] in '.?!':bb+=1
 return aa,bb

def chosen(z,i):
 s,a,b,r=candidate(i)
 if z in SELECT:a,b=locate(s,*SELECT[z],after=90000 if z==7 else 0)
 elif b<len(s) and s[b] in '.?!':b+=1
 return s,a,b
NOTES.update({
22:('literal_primary_supported','Discussion explicitly says including healthy controls to mimic the original reproduced its highly significant association; its separate author judgment calls the original effect spurious due to that inclusion. No intervening table is joined to complete the sentence.'),
29:('literal_primary_supported','Discussion confirms production-code attention while qualifying its strength on GitHub; introduction explicitly states notable differences from Spadini across review models. Both sides of the comparison are separately quoted.'),
38:('literal_primary_supported','Results narrates 23 unassociated discovery markers and identifies associated NOD2/CCDC122-LACC1 markers; Discussion confirms both loci. The four-locus design and nonvalidated-gene caveat were inspected. This supports the two-versus-four pattern; it is not an unqualified author statement that the entire Chinese GWAS failed.'),
62:('literal_primary_supported','Baseline narrative explicitly reports perfect/second-decimal reproduction of HHI-delta estimates; separate summary challenges common-ownership causal inference. Distinct computation and robustness passages are retained.'),
71:('literal_primary_supported','Abstract author synthesis reports null engagement differences and same-race preference in the systematic replication. The separately quoted Hardy 2020 benchmark reports negligible engagement effects and same-skin preference. Agreement is a comparison of these narrated patterns, not an explicit whole-study success label.'),
76:('literal_primary_supported','Results narrative explicitly supports H1 education, H2 age and H3 gender in consecutive prose. Conclusion distinguishes established human-capital features from new gender/context findings; no table-cell concatenation is used.'),
80:('literal_primary_supported','Abstract narrates six of twelve original comparisons and absence of frequent-flyer effect while affirming evidence for inaction inertia. This is limited replication support; the extracted two-column discussion is not spliced to obtain its partial-replication wording.'),
90:('literal_primary_supported','Discussion contrasts absent friendship-quality and parent-rated significance with original PEERS, while its opening explicitly says most hypotheses replicate and describes gains in knowledge and hosted get-togethers. Both contexts were inspected and separately bounded.'),
131:('literal_primary_supported','Concluding synthesis explicitly finds modeled Spitzer patterns more frequent in Racine than originally shown. Only 24 of roughly 50 patterns were modeled; whole reenactment is separately called partially successful, and comparative-corpus distinctiveness is a different question.'),
159:('literal_primary_supported','Study 2 explicitly identifies a conceptual retest of Makel/Plucker/Hegarty in BITRA. Discussion compares lower TIS replication prevalence and differing self-replication proportions, with more similar exact-replication proportions. The quoted comparison is bounded to the stated disciplines and databases.'),
})

# Separate, independently bounded corroborating/contrary passages are never joined.
EXTRA={
0:[('local difference','However, in the present study, whereas the Hong Kong participants’ratings of boys','their ratings of girls were not')],
4:[('mechanism qualification','In contrast to the findings of Hulleman','success expectancies')],
17:[('reference identity','Kroch, Anthony, and Cathy Small. 1978','Academic Press')],
19:[('reference identity','Boroditsky, Lera, Lauren Schmidt & Webb Phillips. 2003','Cambridge, MA: MIT Press')],
22:[('validity critique','with our hypothesis that the original results were','based on a spurious effect due to the inclusion of an HC group')],
26:[('main target verdict','The results of this large scale, multiple lab direct replication','successful selection of that person from a subsequent lineup')],
29:[('contrasting synthesis','Our findings reveal notable differences from the original study','integrated CI tools such as GHA')],
38:[('confirmed-locus synthesis','A second consistent association signal was observed','The results confirmed the host resistance effect for both loci')],
44:[('replicated trait relationship','In line with Meldrum','absent (H2)')],
62:[('robustness conclusion','Taken together, our results suggest that common ownership','average prices')],
71:[('original-specific benchmark','In a recent investigation (Hardy et al., 2020)','shared the child’s skin color')],
75:[('brief overall evaluation','4.3 Brief Evaluation','□ inconclusive')],
83:[('opposite configurations','At the same time, the illustration shows two configurations, Types 2 and 3','a negative effect on business performance')],
90:[('replicated targets','Most hypotheses were supported in this study','increase in hosted')],
96:[('central target verdict','In the present study we replicated the central finding','which of two photos has more people')],
119:[('declared target','The study was a partial conceptual replication of Hulstijn','using the same analyses on a subset of the same speeded tasks')],
127:[('conditional original success','If, as in Vichi et al (2009) and Lopes (2010)','since all groups reached these criteria')],
131:[('whole reenactment qualification','I believe that attempting to repeat or reenact Spitzer’s earlier study has been partially successful','in the sense')],
155:[('focal success','Thus, the replication of the claim was successful according to','the SCORE criteria')],
158:[('outcome judgment','The results of Study 2 partially replicated prior research','Hulleman et al., 2010)')],
159:[('contrasted outcome','the overall rate of published replications','Makel')],
161:[('outcome judgment','Our results suggest that the original findings of a facial feedback','were warned that their performance was being monitored')],
163:[('original benchmark and design','As explained earlier, it has been found that in an episodic recognition task','the priming is L1–L1')],
164:[('original benchmark and design','As explained earlier, it has been found that in an episodic recognition task','the priming is L1–L1')],
166:[('benchmark attribution','Numerous developmental studies','raising questions regarding the meaning and universal validity of this test as an ontogenetic benchmark of self-concept')],
167:[('observed affect result','This lack of significant interaction (for both NA and PA)','there was not an affective cost for acting out of character')],
168:[('observed affect result','This lack of significant interaction (for both NA and PA)','there was not an affective cost for acting out of character')],
170:[('author outcome synthesis','A large scale replication with 36 samples successfully replicated eleven','currency priming influencing system justification – did not replicate')],
171:[('author outcome synthesis','A large scale replication with 36 samples successfully replicated eleven','currency priming influencing system justification – did not replicate')],
172:[('author outcome synthesis','A large scale replication with 36 samples successfully replicated eleven','currency priming influencing system justification – did not replicate')],
173:[('author outcome synthesis','A large scale replication with 36 samples successfully replicated eleven','currency priming influencing system justification – did not replicate')],
175:[('original-specific comparison','However, in contrast to previous studies that analyzed Airbnb','we did not find that Asian hosts charge less for their apartments')],
177:[('full-sample failure qualification','Thus the effect of matched books and teacher scaffolding','was not replicated in the full sample of schools')],
178:[('outcome judgment','Most importantly, none of the moderators','were associated with adjustment from anchors')],
180:[('named prior finding','In reality, demand for income redistribution in the United States','as we document later in this paper')],
}
EXTRA[4]=[('mechanism qualification','However, our investigation led to a surprising finding','intervention effects')]
EXTRA[44]=[('replicated trait relationship','Consistent with differential deterrability and Meldrum','absent (H2)')]
EXTRA[159]=[('comparative context','In psychology, a discipline in which replication is more common','Makel, Plucker, and Hegarty 2012)')]
SELECT[0]=('the fact that this study largely replicated','suggests the people’s conceptions of creativity are complex')
SELECT[177]=('The effects of the treatments were positive for high poverty schools','The results underscore the importance of looking at patterns of treatment effects across different contexts, settings, and populations')

# Include closing punctuation exactly as it occurs in the file.
_locate=locate
def locate(s,start,end,after=0):
 a,b=_locate(s,start,end,after)
 while b<len(s) and s[b] in '.)]?!’”': b+=1
 return a,b

def passage(s,a,b,p,sha,label):
 q=s[a:b];assert q
 return dict(purpose=label,source_path=str(p),source_sha256=sha,literal_quote=q,
             start_offset=a,end_offset=b,offset_unit='Unicode code points; UTF-8 decoded without newline translation; end exclusive',
             quote_sha256=hashlib.sha256(q.encode('utf-8')).hexdigest(),
             location=dict(start_line=s.count('\n',0,a)+1,end_line=s.count('\n',0,b)+1,
                           form_feed_page=s.count('\f',0,a)+1))

def build():
 import collections,datetime,os
 raw=INPUT.read_bytes();payload=json.loads(raw);items=payload['issues'];assert len(items)==203
 assert set(NOTES)==set(range(203));out=[];verified={}
 for z,i in enumerate(items):
  sha=digest(i['source_path']);assert sha==i['source_sha256'];verified[i['source_path']]=sha
  s,a,b=chosen(z,i);disposition,rationale=NOTES[z]
  support=[]
  for label,start,end in EXTRA.get(z,[]):
   aa,bb=locate(s,start,end);assert bb-aa<1500,(z,bb-aa)
   support.append(passage(s,aa,bb,i['source_path'],sha,label))
  old=i['existing_evidence']
  row={k:i[k] for k in ['file_key','input_row_index','field','target_index','work_key']}
  row.update(issue_index=z,old_quote=old['quote'],old_evidence=old.copy(),
             source_path=i['source_path'],source_sha256=sha,
             disposition=disposition,contextual_rationale=rationale,
             primary_identity_checked={'status':'checked_in_supplied_primary_text',
                 'replicating_work_key':i['work_key'],
                 'basis':'Front matter and the cited empirical/theoretical context were inspected; target identity limits are stated in contextual_rationale. No external DOI-resolution or canonical-row adjudication is asserted.',
                 'front_matter_inspected_offsets':[0,min(len(s),1300)]},
             actual_limitations=['Inspection concerns the registered extracted primary text; no OCR, missing-symbol, word or column-order correction was made.',
                 'Technical quotation support does not change or finally adjudicate the existing scientific verdict.'],
             supporting_passages=support,
             context_inspected={'quote_neighborhood_offsets':[max(0,a-450),min(len(s),b+800)],
                                'additional_passage_neighborhoods':[[max(0,p['start_offset']-180),min(len(s),p['end_offset']+500)] for p in support]})
  if disposition=='no_support':
   row.update(literal_quote=None,start_offset=None,end_offset=None,quote_sha256=None,location=None)
   row['actual_limitations'].append('No compliant short contiguous author judgment for the exact target-specific reason; generic reassessment methods and separated table evidence are not positive quotation support.')
   row['context_inspected']['additional_sections']=['Methods 2.9','Results 3.2–3.3; Tables 1–3','Discussion 4.1','References 6, 13, 15, 17–18, 26, 30–44']
   # Retain a raw contextual passage as explicitly non-supporting, without promotion.
   row['non_supporting_context']=passage(s,a,b,i['source_path'],sha,'Generic methods; insufficient for exact target identity/comparison')
  else:
   p=passage(s,a,b,i['source_path'],sha,'Independent author judgment' if disposition=='literal_primary_supported' else 'Scope qualification / contrary primary text')
   row.update({k:p[k] for k in ['literal_quote','start_offset','end_offset','quote_sha256','location','offset_unit']})
   assert b-a<1500,(z,b-a)
   if disposition=='scope_objection':row['actual_limitations'].append(rationale)
  out.append(row)
 registry=ROOT.parent/'additional_reports'/'approved_sources.json';approved=json.loads(registry.read_bytes());supp=[]
 for r in approved['reports']:
  for pk,hk in [('text_path','text_sha256'),('blind_coding_path','blind_coding_sha256')]:assert digest(r[pk])==r[hk]
  overlaps=[z for z,i in enumerate(items) if i['file_key']==r['collection_file_key']]
  assert not overlaps,'Supplementary issue requires direct report-specific inspection'
  supp.append({'report_id':r['report_id'],'collection_file_key':r['collection_file_key'],
               'registered_text_path':r['text_path'],'registered_text_sha256':r['text_sha256'],
               'registered_blind_coding_sha256':r['blind_coding_sha256'],'hashes_checked':True,
               'matching_issue_indices':overlaps,'use':'No issue in this 203-member inventory concerns this collection; no legacy collection source was substituted for this report.'})
 result={'schema_version':1,'inspection_role':'source quote technical inspector; not blind coding or final scientific adjudication',
         'input_path':str(INPUT),'input_sha256':hashlib.sha256(raw).hexdigest(),
         'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'quotation_provenance':'NEW independently inspected raw primary-source quotations. Legacy evidence/model strings remain unchanged in old_evidence and old_quote; no repaired model quotation is asserted.',
         'offset_convention':'Unicode code-point offsets in source bytes decoded as UTF-8 without newline translation; [start,end). Quote hashes use exact UTF-8 bytes of the slice.',
         'membership_fields':['file_key','input_row_index','field','target_index'],
         'counts':dict(collections.Counter(r['disposition'] for r in out)),
         'issues_inspected':len(out),'inventory_sources_hash_checked':len(verified),
         'source_hash_checks':verified,'supplement_registry_path':str(registry),
         'supplement_registry_sha256':digest(registry),'supplementary_source_checks':supp,
         'remaining_scientific_objections':[{'issue_index':r['issue_index'],**{k:r[k] for k in ['file_key','input_row_index','field','target_index']},'objection':r['contextual_rationale']} for r in out if r['disposition']=='scope_objection'],
         'global_limitations':['All dispositions are technical source/context assessments, not new scientific verdicts.',
             'no_support means no permissible concise raw passage for the exact existing reason under this audit; it does not establish that a table-supported retest never occurred.',
             'Named original identities were checked within the replicating primary report; assertions about external misresolved DOI records, duplicate repository versions or canonical shipped membership are not independently proven by such primary text alone.',
             'Registered additional reports have no issue membership here; their text and coding hashes were checked, but no report-specific scientific review is claimed.'],
         'issues':out}
 validate(result,items)
 target=ROOT/'strict_literal_quote_inspection.result.json';tmp=target.with_suffix('.json.tmp')
 with tmp.open('w',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,target)
 validate(json.loads(target.read_bytes()),items)
 return {k:result[k] for k in ['counts','issues_inspected','inventory_sources_hash_checked']}

def validate(result,items=None):
 import collections
 if items is None:items=json.loads(INPUT.read_bytes())['issues']
 keys=lambda r:tuple(r[k] for k in ['file_key','input_row_index','field','target_index'])
 assert len(result['issues'])==len(items)==203
 assert collections.Counter(map(keys,result['issues']))==collections.Counter(map(keys,items))
 assert len(set(map(keys,items)))==203
 assert result['input_sha256']==digest(INPUT)
 for r,i in zip(result['issues'],items):
  assert keys(r)==keys(i);assert r['old_quote']==i['existing_evidence']['quote'];assert r['old_evidence']==i['existing_evidence']
  assert digest(r['source_path'])==r['source_sha256']==i['source_sha256']
  ps=list(r['supporting_passages'])
  if r['literal_quote'] is not None:ps.append(r)
  if 'non_supporting_context' in r:ps.append(r['non_supporting_context'])
  if r['disposition']=='literal_primary_supported':assert r['literal_quote']
  for p in ps:
   assert digest(p['source_path'])==p['source_sha256'];s=pathlib.Path(p['source_path']).read_bytes().decode('utf-8')
   assert p['literal_quote']==s[p['start_offset']:p['end_offset']]
   assert hashlib.sha256(p['literal_quote'].encode('utf-8')).hexdigest()==p['quote_sha256']
 assert dict(collections.Counter(r['disposition'] for r in result['issues']))==result['counts']
 return True

if __name__=='__main__' and sys.argv[1:]==['--write']:print(json.dumps(build()))
if __name__=='__main__' and sys.argv[1:]==['--validate']:
 validate(json.loads((ROOT/'strict_literal_quote_inspection.result.json').read_bytes()));print('membership/hash/raw-slice validation passed: 203 issues')
