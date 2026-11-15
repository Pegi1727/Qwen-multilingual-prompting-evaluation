from pathlib import Path
import pandas as pd
import json
root=Path('/mnt/data')
# Transcribed strictly from the user's four explicit format decisions.
blocks={
1:'''1 2 3 4 6 9 11 13 16 19 21 22 23 26 29 30 31 32 33 34 36 39 43 44 46 48 49 50 51 53 54 56 59 61 63 66 69 76 79 81 84 86 89 90 98 99 100 101 103 104 106 109 113 114 118 119 122 123 124 126 129 131 133 136 139 143 146 148 149 151 153 154 156 159 161 163 164 168 169 171 173 174 179 181 182 183 186 189 191 193 194 196 199 201 202 203 204 206 209 213 219 221 223 226 229 233 236 239''',
251:'''253 255 256 259 263 266 269 276 279 289 295 299 303 305 309 313 316 319 323 325 329 334 335 343 345 346 349 352 353 354 356 359 361 363 366 369 375 376 379 381 383 385 389 393 396 399 409 416 419 424 426 429 432 434 439 441 442 443 444 449 452 453 456 459 462 464 467 472 474 478 479 480 482 483 484 492 494 496''',
501:'''502 504 507 510 512 513 514 516 519 522 523 524 526 529 539 542 543 544 546 549 554 556 557 559 560 563 564 569 572 573 574 576 579 580 589 592 593 594 596 599 600 609 611 613 616 619 621 623 626 629 631 633 634 636 641 643 644 646 649 651 653 656 659 661 663 664 666 669 674 681 683 686 689 691 692 693 694 696 699 702 704 721 722 723 724 726 729 731 733 736 739 741 743 744 746 749''',
751:'''751 753 756 759 771 773 776 779 784 792 799 801 802 803 804 806 809 811 813 814 816 819 821 823 826 829 832 836 841 843 844 846 849 850 851 853 856 859 861 863 864 866 869 871 873 876 879 881 882 883 884 886 889 899 924 932 941 943 946 949 951 952 953 956 959 961 963 966 969 971 973 974 976 979 981 982 983 986 988 989 991 992 993 996 999'''
}
labels={}
for start,text in blocks.items():
 yes=list(map(int,text.split()));assert len(yes)==len(set(yes));assert all(start<=n<start+250 for n in yes)
 labels.update({n:'رعایت‌شده' if n in yes else 'رعایت‌نشده' for n in range(start,start+250)})
x=pd.read_csv(root/'qwen_1000_user_content_labels.csv',keep_default_na=False)
assert len(x)==1000 and set(x.review_number)==set(range(1,1001))
original_content=x.user_content_label.copy()
expected=x.review_number.map(labels)
conflicts=x.loc[x.format_compliance.ne('') & x.format_compliance.ne(expected),['review_number','format_compliance']]
assert conflicts.empty,conflicts.to_string()
x['format_compliance']=expected
assert x.user_content_label.equals(original_content)
x.to_csv(root/'qwen_1000_user_content_labels.csv',index=False,encoding='utf-8-sig')
x[['review_number','run_id','format_compliance']].to_csv(root/'qwen_user_format_labels_1000_confirmed.csv',index=False,encoding='utf-8-sig')
f=pd.read_csv(root/'qwen_format_review_1000.csv',keep_default_na=False)
f['format_label']=f.review_number.map(labels)
f.to_csv(root/'qwen_format_review_1000.csv',index=False,encoding='utf-8-sig')
# C1 is an English baseline; the retained tr tag reflects its duplicate source, not a Turkish prompt.
x['analysis_language']=x.language.where(x.condition.ne('C1'),'en')
def summary(g):
 n=len(g);d={'n':n}
 for key,label in [('correct','درست'),('incorrect','غلط'),('mixed','ترکیبی'),('unintelligible','نامفهوم')]:
  d[key+'_n']=int(g.user_content_label.eq(label).sum());d[key+'_pct']=100*d[key+'_n']/n
 for key,mask in [('format_compliant',g.format_compliance.eq('رعایت‌شده')),('correct_and_compliant',g.user_content_label.eq('درست') & g.format_compliance.eq('رعایت‌شده'))]:
  d[key+'_n']=int(mask.sum());d[key+'_pct']=100*mask.mean()
 return d
for name,cols in [('by_condition',['condition']),('by_condition_language',['condition','analysis_language']),('by_language',['analysis_language'])]:
 rows=[]
 for keys,g in x.groupby(cols):
  if not isinstance(keys,tuple):keys=(keys,)
  rows.append(dict(zip(cols,keys))|summary(g))
 pd.DataFrame(rows).to_csv(root/f'qwen_final_{name}.csv',index=False,encoding='utf-8-sig')
pd.DataFrame([summary(x)]).to_csv(root/'qwen_final_overall.csv',index=False,encoding='utf-8-sig')
pd.crosstab(x.user_content_label,x.format_compliance).to_csv(root/'qwen_content_by_format.csv',encoding='utf-8-sig')
audit={'rows':len(x),'unique_review_numbers':x.review_number.nunique(),'format_missing':int(x.format_compliance.eq('').sum()),'existing_format_conflicts':len(conflicts),'content_counts':x.user_content_label.value_counts().to_dict(),'format_counts':x.format_compliance.value_counts().to_dict(),'C1_analysis_language':'en; source language tag tr retained unchanged','scope':'Descriptive summaries only; language aggregates are not causal language comparisons.'}
(root/'qwen_final_validation.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(audit,ensure_ascii=False,indent=2))
for name in ['by_condition','by_condition_language','by_language']:
 print('\n'+name);print(pd.read_csv(root/f'qwen_final_{name}.csv').to_string(index=False))
