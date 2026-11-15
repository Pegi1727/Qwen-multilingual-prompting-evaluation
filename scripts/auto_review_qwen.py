#!/usr/bin/env python3
"""Conservative chemical-symbol screening, NOT a semantic judge.
Usage: python auto_review_qwen.py --input results_1200_qwen.csv --output-dir auto_review
Dependencies: pandas. Unknown cases remain unclear; human labels override screening.
"""
import argparse
import json
import re
from pathlib import Path
import pandas as pd

SYMBOLS = set('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og'.split())

def clean(value):
    # Do not casefold chemical symbols: Co and CO are not interchangeable.
    t = str(value).strip()
    if t.startswith('```') and t.endswith('```'):
        body = t[3:-3].strip()
        if '\n' not in body:
            t = body
    return t.strip(' \t\r\n`\"\'«»“”‘’').strip()

def classify(row):
    gold, text = str(row['gold_answer']).strip(), str(row['generated_text']).strip()
    t = clean(text)
    if gold not in SYMBOLS:
        return 'unclear', 'unsupported_gold_not_element_symbol'
    if t == gold:
        return '1', 'standalone_gold_symbol'
    # Only strip a final full stop when the entire remainder is the gold symbol.
    if t == gold + '.':
        return '1', 'gold_symbol_with_final_period'
    if t in SYMBOLS:
        return '0', 'standalone_wrong_element_symbol'
    # A complete chemical formula, e.g. H2O or H₂, is not a single element symbol.
    formula = t.translate(str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789'))
    if re.fullmatch(r'(?:[A-Z][a-z]?[0-9]*)+', formula):
        parts = re.findall(r'([A-Z][a-z]?)([0-9]*)', formula)
        if all(s in SYMBOLS for s, _ in parts) and (len(parts) > 1 or any(n for _, n in parts)):
            return '0', 'standalone_formula_not_element_symbol'
    return 'unclear', 'semantic_or_contradiction_review_required'

def human_label(value):
    t = str(value).strip().lower()
    return {'0':'0','0.0':'0','1':'1','1.0':'1','unclear':'unclear'}.get(t)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output-dir', default='auto_review')
    args = parser.parse_args()
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(args.input, keep_default_na=False)
    required = {'run_id','item_id','condition','language','prompt','context','gold_answer','generated_text'}
    if not required.issubset(d.columns):
        raise ValueError(f'Missing columns: {sorted(required-set(d.columns))}')
    if d.run_id.duplicated().any():
        raise ValueError('Duplicate run_id values')
    # Collapse only verified identical English baselines, not native conditions.
    c1 = d[d.condition.eq('C1')]
    baseline_is_en = len(c1)>0 and 'prompt_language' in c1 and c1.prompt_language.eq('en').all()
    if baseline_is_en:
        for _, group in c1.groupby('item_id'):
            if any(group[c].nunique(dropna=False)>1 for c in ['prompt','context','gold_answer','generated_text']):
                raise ValueError('C1 repetitions differ: cannot safely collapse them')
            if len(group)>1 and 'content_correct_0_1_unclear' in group and any(human_label(v) is not None for v in group.content_correct_0_1_unclear):
                raise ValueError('Repeated C1 rows have human labels; reconcile before deduplication')
        keep = c1.drop_duplicates('item_id').index
        d = d[(d.condition!='C1') | d.index.isin(keep)].copy()
    d['analysis_language'] = d['language']
    if baseline_is_en:
        d.loc[d.condition.eq('C1'),'analysis_language'] = 'en'
    if 'content_correct_0_1_unclear' not in d:
        d['content_correct_0_1_unclear'] = ''
    if 'format_compliant_0_1' not in d:
        d['format_compliant_0_1'] = ''
    labels = d.apply(classify, axis=1)
    d['auto_content_label'] = labels.map(lambda x:x[0])
    d['auto_reason'] = labels.map(lambda x:x[1])
    d['human_content_label'] = d.content_correct_0_1_unclear.map(human_label).fillna('')
    d['effective_content_label'] = d.human_content_label.where(d.human_content_label.ne(''),d.auto_content_label)
    d['label_source'] = d.human_content_label.map(lambda x:'human_supplied' if x else 'rule_screen_not_validated')
    d['needs_content_review'] = d.effective_content_label.eq('unclear')
    # Three or more words is a conservative screen for extra prose, not a semantic verdict.
    d['auto_format_label'] = d.generated_text.map(lambda t:'1' if re.fullmatch(r'[A-Za-z][a-z]?[.]?',clean(t)) else ('0' if len(str(t).split())>=3 else 'unclear'))
    d['effective_format_label'] = [human_label(h) or a for h,a in zip(d.format_compliant_0_1,d.auto_format_label)]
    d['strict_exact_recomputed'] = d.apply(lambda r:bool(str(r.gold_answer).strip()) and str(r.generated_text).strip()==str(r.gold_answer).strip(),axis=1)
    d.to_csv(out/'auto_labeled_review.csv',index=False,encoding='utf-8-sig')
    d[d.needs_content_review].to_csv(out/'needs_human_review.csv',index=False,encoding='utf-8-sig')
    summary=[]
    for (c,l),g in d.groupby(['condition','analysis_language']):
        n=len(g); yes=int(g.effective_content_label.eq('1').sum()); no=int(g.effective_content_label.eq('0').sum()); unknown=n-yes-no
        summary.append(dict(condition=c,language=l,n=n,screen_correct=yes,screen_incorrect=no,unresolved=unknown,strict_exact_percent=100*g.strict_exact_recomputed.mean(),screen_positive_percent=100*yes/n,possible_percent_if_all_unresolved_correct=100*(yes+unknown)/n))
    pd.DataFrame(summary).to_csv(out/'screening_summary.csv',index=False,encoding='utf-8-sig')
    meta={'rows':len(d),'unresolved':int(d.needs_content_review.sum()),'warning':'Rule-based screening is not validated content accuracy. Percent ranges are arithmetic scenarios, NOT confidence intervals. Review uncertain cases and audit rule-labeled cases independently. Human fields are preserved. No bias conclusion is produced.'}
    (out/'screening_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
