"""Conservative error triage, not full semantic evaluation. Requires pandas."""
from pathlib import Path
import re
import pandas as pd
from auto_review_qwen import classify, clean

ROOT=Path(__file__).resolve().parent
source=ROOT/'results_1200_qwen.csv'
d=pd.read_csv(source,keep_default_na=False)
c1=d[d.condition.eq('C1')]
assert c1.prompt_language.eq('en').all()
for _,g in c1.groupby('item_id'):
    assert all(g[c].nunique(dropna=False)==1 for c in ['prompt','context','gold_answer','generated_text'])
d=d[(d.condition!='C1') | d.index.isin(c1.drop_duplicates('item_id').index)].copy()
d['analysis_language']=d.language.where(d.condition.ne('C1'),'en')

def triage(r):
    gold=str(r.gold_answer).strip(); text=str(r.generated_text).strip()
    if text==gold:
        return 'exact_correct','Exact answer, requested minimal format.'
    if clean(text) in (gold,gold+'.'):
        return 'correct_minor_format','Only outer quotes/backticks or final period differ.'
    label,reason=classify(r)
    if label=='0':
        return 'wrong_standalone_symbol_or_formula',reason
    # Literal gold presence is a queueing aid only: contradictions, negation and
    # quoted question/context can all contain the reference answer.
    pattern=r'(?<!\w)'+re.escape(gold)+r'(?!\w)'
    if gold and re.search(pattern,text):
        return 'gold_present_semantics_unresolved','Gold text occurs, but endorsement/contradiction and full content require review.'
    return 'other_semantics_unresolved','Could be a synonym, translation, wrong answer or omission; human review required.'

pairs=d.apply(triage,axis=1)
d['error_triage']=pairs.map(lambda p:p[0]);d['triage_reason']=pairs.map(lambda p:p[1])
d['human_content_label']='';d['human_format_label']='';d['human_error_category']='';d['human_notes']=''
out=ROOT/'qwen_error_analysis';out.mkdir(exist_ok=True)
d.to_csv(out/'error_analysis_1000.csv',index=False,encoding='utf-8-sig')
counts=d.error_triage.value_counts().rename_axis('category').reset_index(name='n');counts['percent']=counts.n/len(d)*100
counts.to_csv(out/'error_category_counts.csv',index=False,encoding='utf-8-sig')
d.groupby(['condition','analysis_language','error_triage']).size().unstack(fill_value=0).to_csv(out/'error_categories_by_group.csv',encoding='utf-8-sig')
print(counts.to_string(index=False));print('Total:',len(d))
