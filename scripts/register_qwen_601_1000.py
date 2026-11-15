import pandas as pd
from pathlib import Path
correct='601 602 606 611 613 614 616 620 621 626 631 636 641 643 644 646 647 648 649 650 651 653 654 656 657 658 659 671 673 676 679 681 683 686 687 689 690 691 693 694 696 699 710 711 713 714 716 719 721 722 723 724 726 727 729 731 733 734 736 739 741 743 746 747 749 750 751 754 756 759 761 763 764 766 768 769 771 773 776 778 779 781 783 786 789 791 792 793 796 797 799 801 803 805 806 807 809 811 813 814 816 819 821 823 824 826 827 829 837 841 843 844 846 847 849 851 853 854 856 857 859 861 863 864 866 869 870 871 873 876 877 879 880 881 883 887 890 891 893 894 898 901 903 906 909 921 923 926 929 931 933 936 939 941 943 946 947 949 950 957 960 974 977 997'
mixed='604 610 625 640 684 697 700 720 737 777 780 782 788 790 795 810 820 830 845 855 860 897 900 920 944'
unclear='605 607 615 617 627 637 645 668 670 695 705 707 725 735 745 755 765 775 787 815 828 840 867 904 907 910 914 917 925 927 945 955 965 975 985 995'
groups={k:set(map(int,s.split())) for k,s in [('درست',correct),('ترکیبی',mixed),('نامفهوم',unclear)]}
assert sum(map(len,groups.values()))==len(set.union(*groups.values()))
assert all(601<=n<=1000 for s in groups.values() for n in s)
x=pd.read_csv('/mnt/data/results_1200_qwen.csv',keep_default_na=False)
x=x[(x.condition!='C1')|(x.language=='tr')].reset_index(drop=True)
x['review_number']=range(1,1001)
y=x.iloc[600:].copy()
y['user_content_label']=[next((k for k,s in groups.items() if n in s),'غلط') for n in y.review_number]
y['label_source']='user_final_revision'
y['format_compliance']='not_evaluated'
y['label_note']=''
y.loc[y.review_number==971,'label_note']='Final user decision: غلط, overriding preliminary ترکیبی in same entry.'
y.to_csv('/mnt/data/qwen_labels_601_1000_final.csv',index=False,encoding='utf-8-sig')
first=pd.read_csv('/mnt/data/qwen_first100_review_revised.csv',keep_default_na=False)
print('first100 counts',first.user_label.value_counts().to_dict())
second=pd.read_csv('/mnt/data/qwen_labels_101_600_final.csv',keep_default_na=False)
labels=pd.concat([first[['review_number','user_label']].rename(columns={'user_label':'user_content_label'}),second[['review_number','user_content_label']],y[['review_number','user_content_label']]],ignore_index=True)
assert len(labels)==1000 and labels.review_number.nunique()==1000 and set(labels.review_number)==set(range(1,1001))
full=x.merge(labels,on='review_number',validate='one_to_one')
full['format_compliance']='not_evaluated'
full['label_source']='user; first100 agreed revision, subsequent final submissions'
full.to_csv('/mnt/data/qwen_1000_user_content_labels.csv',index=False,encoding='utf-8-sig')
summary=[]
for name,d in [('601–1000',y),('1–1000',full)]:
 print(name,d.user_content_label.value_counts().to_dict())
 for label in ['درست','غلط','ترکیبی','نامفهوم']:
  n=int((d.user_content_label==label).sum());summary.append({'range':name,'label':label,'count':n,'percent':100*n/len(d)})
pd.DataFrame(summary).to_csv('/mnt/data/qwen_user_content_summary.csv',index=False,encoding='utf-8-sig')
for n in [782,784,788,790,802,861,888,924,950]:
 r=full[full.review_number==n].iloc[0]
 print('\n',n,'PROMPT',r.prompt,'GOLD',r.gold_answer,'OUTPUT',r.generated_text)
