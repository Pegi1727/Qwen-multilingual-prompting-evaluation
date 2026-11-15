from pathlib import Path
import pandas as pd
from scipy.stats import binomtest
from itertools import combinations
p=Path('/mnt/data');d=pd.read_csv(p/'results_1200_qwen.csv',keep_default_na=False)
groups={}
for (c,l),g in d.groupby(['condition','language']):
 if c=='C1' and l!='tr':continue
 groups[c+('_en' if c=='C1' else '_'+l)]=g.set_index('item_id').exact_match_strict.astype(int)
rows=[]
def compare(a,b):
 x,y=groups[a].align(groups[b],join='inner');w=int(((x==1)&(y==0)).sum());v=int(((x==0)&(y==1)).sum());n=len(x)
 rows.append(dict(A=a,B=b,n=n,A_correct=int(x.sum()),B_correct=int(y.sum()),difference_pp=100*(x.mean()-y.mean()),A_only_correct=w,B_only_correct=v,p_exact_mcnemar=binomtest(w,w+v,.5).pvalue if w+v else 1.))
for c in ['C2','C3','C4']:
 for a,b in combinations(['tr','az','fa'],2):compare(c+'_'+a,c+'_'+b)
for c in ['C2','C3','C4']:
 for l in ['tr','az','fa']:compare('C1_en',c+'_'+l)
r=pd.DataFrame(rows);order=r.p_exact_mcnemar.sort_values().index;prev=0.
for k,i in enumerate(order):
 prev=max(prev,min(1.,(len(r)-k)*r.loc[i,'p_exact_mcnemar']));r.loc[i,'p_holm_18_tests']=prev
r['significant_05_holm']=r.p_holm_18_tests<.05;r.to_csv(p/'qwen_paired_tests_holm.csv',index=False,encoding='utf-8-sig')
s=[]
for name,g in groups.items():
 ci=binomtest(int(g.sum()),len(g)).proportion_ci(confidence_level=.95,method='exact');s.append(dict(group=name,n=len(g),correct=int(g.sum()),accuracy_percent=100*g.mean(),ci95_lower_percent=100*ci.low,ci95_upper_percent=100*ci.high))
pd.DataFrame(s).to_csv(p/'qwen_accuracy_exact_ci95.csv',index=False,encoding='utf-8-sig')
print(r.to_string(index=False));print(pd.DataFrame(s).to_string(index=False))
