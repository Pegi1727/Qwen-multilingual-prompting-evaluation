from pathlib import Path
import hashlib, json
from itertools import combinations
import pandas as pd
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'analysis_99_items'
OUT.mkdir(exist_ok=True)
raw = pd.read_csv(ROOT/'inputs_original/results_1200_qwen.csv', keep_default_na=False)
human = pd.read_csv(ROOT/'inputs_original/qwen_1000_user_content_labels.csv', keep_default_na=False)
assert len(raw)==1200 and len(human)==1000
assert raw.run_id.is_unique and human.run_id.is_unique
r=raw.loc[raw.item_id.ne('Q087')].copy()
h=human.loc[human.item_id.ne('Q087')].copy()
assert len(r)==1188 and len(h)==990
assert r.item_id.nunique()==h.item_id.nunique()==99
assert r.groupby(['condition','language']).size().eq(99).all()
assert raw.exact_match_strict.astype(int).eq(raw.generated_text.eq(raw.gold_answer).astype(int)).all()
assert set(h.run_id)<=set(r.run_id)
for lang in ['az','fa']:
 a=r.loc[(r.condition=='C1') & (r.language=='tr')].set_index('item_id').generated_text.sort_index()
 b=r.loc[(r.condition=='C1') & (r.language==lang)].set_index('item_id').generated_text.sort_index()
 pd.testing.assert_series_equal(a,b)
r.to_csv(OUT/'retained_executions_1188.csv',index=False,encoding='utf-8-sig')
h.to_csv(OUT/'retained_human_annotations_990.csv',index=False,encoding='utf-8-sig')
raw.loc[raw.item_id.eq('Q087')].to_csv(OUT/'excluded_Q087_executions_12.csv',index=False,encoding='utf-8-sig')
human.loc[human.item_id.eq('Q087')].to_csv(OUT/'excluded_Q087_annotations_10.csv',index=False,encoding='utf-8-sig')
h['analysis_language']=h.language.where(h.condition.ne('C1'),'en')
def summary(g):
 d={'n':len(g)}
 for k,v in [('correct','درست'),('incorrect','غلط'),('mixed','ترکیبی'),('unintelligible','نامفهوم')]:
  d[k+'_n']=int(g.user_content_label.eq(v).sum());d[k+'_pct']=100*d[k+'_n']/len(g)
 for k,m in [('format_compliant',g.format_compliance.eq('رعایت‌شده')),('correct_and_compliant',g.user_content_label.eq('درست') & g.format_compliance.eq('رعایت‌شده'))]:
  d[k+'_n']=int(m.sum());d[k+'_pct']=100*m.mean()
 return d
pd.DataFrame([summary(h)]).to_csv(OUT/'qwen_final_overall.csv',index=False)
for name,cols in [('by_condition',['condition']),('by_condition_language',['condition','analysis_language']),('by_language',['analysis_language'])]:
 rows=[]
 for keys,g in h.groupby(cols):
  if not isinstance(keys,tuple): keys=(keys,)
  rows.append(dict(zip(cols,keys))|summary(g))
 pd.DataFrame(rows).to_csv(OUT/f'qwen_final_{name}.csv',index=False)
pd.crosstab(h.user_content_label,h.format_compliance).to_csv(OUT/'qwen_content_by_format.csv',encoding='utf-8-sig')
groups={}
for (c,l),g in r.groupby(['condition','language']):
 if c=='C1' and l!='tr': continue
 groups[c+('_en' if c=='C1' else '_'+l)]=g.set_index('item_id').exact_match_strict.astype(int)
rows=[]
def compare(a,b):
 x,y=groups[a].align(groups[b],join='inner');assert len(x)==99
 w=int(((x==1)&(y==0)).sum());v=int(((x==0)&(y==1)).sum())
 rows.append(dict(A=a,B=b,n=len(x),A_correct=int(x.sum()),B_correct=int(y.sum()),difference_pp=100*(x.mean()-y.mean()),A_only_correct=w,B_only_correct=v,p_exact_mcnemar=binomtest(w,w+v,.5).pvalue if w+v else 1.))
for c in ['C2','C3','C4']:
 for a,b in combinations(['tr','az','fa'],2): compare(c+'_'+a,c+'_'+b)
for c in ['C2','C3','C4']:
 for l in ['tr','az','fa']: compare('C1_en',c+'_'+l)
tests=pd.DataFrame(rows);prev=0.
for k,i in enumerate(tests.p_exact_mcnemar.sort_values().index):
 prev=max(prev,min(1.,(len(tests)-k)*tests.loc[i,'p_exact_mcnemar']));tests.loc[i,'p_holm_18_tests']=prev
tests['significant_05_holm']=tests.p_holm_18_tests<.05
tests.to_csv(OUT/'qwen_paired_tests_holm.csv',index=False)
cirows=[]
for name,g in groups.items():
 ci=binomtest(int(g.sum()),len(g)).proportion_ci(confidence_level=.95,method='exact')
 cirows.append(dict(group=name,n=len(g),correct=int(g.sum()),accuracy_percent=100*g.mean(),ci95_lower_percent=100*ci.low,ci95_upper_percent=100*ci.high))
pd.DataFrame(cirows).to_csv(OUT/'qwen_accuracy_exact_ci95.csv',index=False)
def emrow(name,g):
 return dict(group=name,n=len(g),correct=int(g.exact_match_strict.astype(int).sum()),accuracy_percent=100*g.exact_match_strict.astype(int).mean())
dedup=r.loc[r.condition.ne('C1') | r.language.eq('tr')]
em=[emrow('all_executions_weighted',r),emrow('C1_deduplicated',dedup)]
for c,g in r.groupby('condition'):em.append(emrow(c,g))
pd.DataFrame(em).to_csv(OUT/'exact_match_summary.csv',index=False)
audit={'excluded_item':'Q087','exclusion_reason':'Question asks for the name of Earth’s natural satellite, but original gold is natural satellite; original C4 contexts carry the defective reference. Exclusion applies to all conditions and languages.','decision_timing':'Post-hoc, following inspection of the original results and an external review conversation; not preregistered.','original_executions':1200,'retained_executions':len(r),'original_human_annotations':1000,'retained_human_annotations':len(h),'retained_items':99,'paired_n':99,'new_reruns_integrated':False,'labels_changed':False,'strict_comparison_verified':True,'baseline_significant_holm':int(tests.loc[tests.A.eq('C1_en'),'significant_05_holm'].sum()),'within_condition_language_significant_holm':int(tests.loc[tests.A.ne('C1_en'),'significant_05_holm'].sum()),'human_summary':summary(h)}
(OUT/'validation.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
# Manifest excludes itself; the original files are preserved byte-for-byte.
manifest=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file() and p.name!='MANIFEST_SHA256.csv':
  manifest.append(dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
pd.DataFrame(manifest).to_csv(ROOT/'MANIFEST_SHA256.csv',index=False)
print(json.dumps(audit,ensure_ascii=False,indent=2))
print(pd.DataFrame(em).to_string(index=False))
