import json, os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

BASE='/mnt/data'
OUT=os.path.join(BASE,'controlled_multilingual_pilot_1200.xlsx')
# Additional 40 fact items: domain, identifiers (en/tr/az/fa), gold, questions (en/tr/az/fa), source.
raw=[
('chemistry_symbol','Oxygen','Oksijen','Oksigen','اکسیژن','O','What is the chemical symbol for Oxygen?','Oksijenin kimyasal sembolü nedir?','Oksigenin kimyəvi simvolu nədir?','نماد شیمیایی اکسیژن چیست؟','https://iupac.org/what-we-do/periodic-table-of-elements/'),
('chemistry_symbol','Carbon','Karbon','Karbon','کربن','C','What is the chemical symbol for Carbon?','Karbonun kimyasal sembolü nedir?','Karbonun kimyəvi simvolu nədir?','نماد شیمیایی کربن چیست؟','https://iupac.org/what-we-do/periodic-table-of-elements/'),
('chemistry_symbol','Sodium','Sodyum','Natrium','سدیم','Na','What is the chemical symbol for Sodium?','Sodyumun kimyasal sembolü nedir?','Natriumun kimyəvi simvolu nədir?','نماد شیمیایی سدیم چیست؟','https://iupac.org/what-we-do/periodic-table-of-elements/'),
('chemistry_symbol','Potassium','Potasyum','Kalium','پتاسیم','K','What is the chemical symbol for Potassium?','Potasyumun kimyasal sembolü nedir?','Kaliumun kimyəvi simvolu nədir?','نماد شیمیایی پتاسیم چیست؟','https://iupac.org/what-we-do/periodic-table-of-elements/'),
('chemistry_fact','Water','Su','Su','آب','H2O','What is the chemical formula of water?','Suyun kimyasal formülü nedir?','Suyun kimyəvi formulu nədir?','فرمول شیمیایی آب چیست؟','https://iupac.org/what-we-do/periodic-table-of-elements/'),
('chemistry_fact','Neutral aqueous solution','Nötr sulu çözelti','Neytral sulu məhlul','محلول آبی خنثی','7','At 25 °C, what is the pH of a neutral aqueous solution?','25 °C’de nötr sulu çözeltinin pH değeri kaçtır?','25 °C-də neytral sulu məhlulun pH-ı neçədir?','در دمای ۲۵ درجهٔ سلسیوس، pH محلول آبی خنثی چند است؟','https://goldbook.iupac.org/terms/view/P04524'),
('chemistry_fact','Proton','Proton','Proton','پروتون','+1','What is the electric charge of a proton, in units of the elementary charge?','Protonun elektrik yükü, temel yük birimi cinsinden kaçtır?','Protonun elektrik yükü elementar yük vahidi ilə neçədir?','بار الکتریکی پروتون برحسب بار بنیادی چند است؟','https://physics.nist.gov/cuu/Constants/'),
('chemistry_fact','Neutron','Nötron','Neytron','نوترون','0','What is the electric charge of a neutron, in units of the elementary charge?','Nötronun elektrik yükü, temel yük birimi cinsinden kaçtır?','Neytronun elektrik yükü elementar yük vahidi ilə neçədir?','بار الکتریکی نوترون برحسب بار بنیادی چند است؟','https://physics.nist.gov/cuu/Constants/'),
('geography','Pacific Ocean','Pasifik Okyanusu','Sakit okean','اقیانوس آرام','Pacific Ocean','Which ocean is the largest on Earth by area?','Yüzölçümü bakımından Dünya’nın en büyük okyanusu hangisidir?','Sahəsinə görə Yer kürəsinin ən böyük okeanı hansıdır?','بزرگ‌ترین اقیانوس زمین از نظر مساحت کدام است؟','https://www.nationalgeographic.org/encyclopedia/pacific-ocean/'),
('geography','Mount Everest','Everest Dağı','Everest dağı','کوه اورست','Mount Everest','What is the highest mountain above sea level?','Deniz seviyesinden yüksekliği en fazla olan dağ hangisidir?','Dəniz səviyyəsindən ən hündür dağ hansıdır?','بلندترین کوه از سطح دریا کدام است؟','https://www.britannica.com/place/Mount-Everest'),
('geography','Equator','Ekvator','Ekvator','استوا','Equator','What imaginary line divides Earth into the Northern and Southern Hemispheres?','Dünya’yı Kuzey ve Güney Yarımkürelere ayıran hayalî çizgi hangisidir?','Yer kürəsini Şimal və Cənub yarımkürələrinə ayıran xəyali xətt hansıdır?','کدام خط فرضی زمین را به نیمکره‌های شمالی و جنوبی تقسیم می‌کند؟','https://www.nationalgeographic.org/encyclopedia/equator/'),
('geography','Sahara Desert','Sahra Çölü','Sahara səhrası','صحرای بزرگ آفریقا','Sahara Desert','What is the largest hot desert in the world?','Dünyanın en büyük sıcak çölü hangisidir?','Dünyanın ən böyük isti səhrası hansıdır?','بزرگ‌ترین بیابان گرم جهان کدام است؟','https://www.britannica.com/place/Sahara-desert-Africa'),
('geography','Japan','Japonya','Yaponiya','ژاپن','Tokyo','What is the capital of Japan?','Japonya’nın başkenti neresidir?','Yaponiyanın paytaxtı haradır?','پایتخت ژاپن کجاست؟','https://www.cia.gov/the-world-factbook/countries/japan/'),
('geography','Türkiye','Türkiye','Türkiyə','ترکیه','Ankara','What is the capital of Türkiye?','Türkiye’nin başkenti neresidir?','Türkiyənin paytaxtı haradır?','پایتخت ترکیه کجاست؟','https://www.cia.gov/the-world-factbook/countries/turkey-turkiye/'),
('geography','Africa','Afrika','Afrika','آفریقا','Africa','On which continent is the country of Kenya located?','Kenya hangi kıtada yer alır?','Keniya hansı qitədə yerləşir?','کشور کنیا در کدام قاره قرار دارد؟','https://www.un.org/dgacm/en/content/regional-groups'),
('geography','Nile River','Nil Nehri','Nil çayı','رود نیل','Africa','On which continent does the Nile River flow?','Nil Nehri hangi kıtada akar?','Nil çayı hansı qitədə axır?','رود نیل در کدام قاره جریان دارد؟','https://www.britannica.com/place/Nile-River'),
('si_unit','metre','metre','metr','متر','m','What is the SI unit symbol for length, the metre?','Uzunluğun SI birimi metre için kullanılan simge nedir?','Uzunluğun SI vahidi metr üçün işarə nədir?','نماد یکای SI طول، متر، چیست؟','https://www.bipm.org/en/measurement-units'),
('si_unit','kilogram','kilogram','kiloqram','کیلوگرم','kg','What is the SI unit symbol for mass, the kilogram?','Kütlenin SI birimi kilogram için kullanılan simge nedir?','Kütlənin SI vahidi kiloqram üçün işarə nədir?','نماد یکای SI جرم، کیلوگرم، چیست؟','https://www.bipm.org/en/measurement-units'),
('si_unit','second','saniye','saniyə','ثانیه','s','What is the SI unit symbol for time, the second?','Zamanın SI birimi saniye için kullanılan simge nedir?','Zamanın SI vahidi saniyə üçün işarə nədir?','نماد یکای SI زمان، ثانیه، چیست؟','https://www.bipm.org/en/measurement-units'),
('si_unit','ampere','amper','amper','آمپر','A','What is the SI unit symbol for electric current, the ampere?','Elektrik akımının SI birimi amper için kullanılan simge nedir?','Elektrik cərəyanının SI vahidi amper üçün işarə nədir?','نماد یکای SI جریان الکتریکی، آمپر، چیست؟','https://www.bipm.org/en/measurement-units'),
('si_unit','kelvin','kelvin','kelvin','کلوین','K','What is the SI unit symbol for thermodynamic temperature, the kelvin?','Termodinamik sıcaklığın SI birimi kelvin için kullanılan simge nedir?','Termodinamik temperaturun SI vahidi kelvin üçün işarə nədir?','نماد یکای SI دمای ترمودینامیکی، کلوین، چیست؟','https://www.bipm.org/en/measurement-units'),
('si_unit','mole','mol','mol','مول','mol','What is the SI unit symbol for amount of substance, the mole?','Madde miktarının SI birimi mol için kullanılan simge nedir?','Maddə miqdarının SI vahidi mol üçün işarə nədir?','نماد یکای SI مقدار ماده، مول، چیست؟','https://www.bipm.org/en/measurement-units'),
('solar_system','Sun','Güneş','Günəş','خورشید','Sun','What is the star at the center of our Solar System called?','Güneş Sistemi’nin merkezindeki yıldızın adı nedir?','Günəş sisteminin mərkəzindəki ulduzun adı nədir?','نام ستارهٔ مرکز منظومهٔ شمسی چیست؟','https://science.nasa.gov/sun/'),
('solar_system','Earth','Dünya','Yer','زمین','third','What is Earth’s order from the Sun among the planets?','Gezegenler arasında Dünya, Güneş’ten kaçıncı sıradadır?','Planetlər arasında Yer Günəşdən neçənci yerdədir?','زمین در ترتیب سیاره‌ها از خورشید چندمین است؟','https://science.nasa.gov/solar-system/planets/earth/'),
('solar_system','Mars','Mars','Mars','مریخ','Mars','Which planet is commonly called the Red Planet?','Hangi gezegen Kızıl Gezegen olarak bilinir?','Hansı planet Qırmızı Planet adlanır?','کدام سیاره به سیارهٔ سرخ معروف است؟','https://science.nasa.gov/mars/'),
('solar_system','Jupiter','Jüpiter','Yupiter','مشتری','Jupiter','Which is the largest planet in the Solar System?','Güneş Sistemi’ndeki en büyük gezegen hangisidir?','Günəş sistemindəki ən böyük planet hansıdır?','بزرگ‌ترین سیارهٔ منظومهٔ شمسی کدام است؟','https://science.nasa.gov/jupiter/'),
('solar_system','Moon','Ay','Ay','ماه','natural satellite','What is Earth’s natural satellite called?','Dünya’nın doğal uydusunun adı nedir?','Yerin təbii peykinin adı nədir?','قمر طبیعی زمین چه نام دارد؟','https://science.nasa.gov/moon/'),
('solar_system','Mercury','Merkür','Merkuri','عطارد','Mercury','Which planet is closest to the Sun?','Güneş’e en yakın gezegen hangisidir?','Günəşə ən yaxın planet hansıdır?','کدام سیاره به خورشید نزدیک‌تر است؟','https://science.nasa.gov/mercury/'),
('genomics','DNA','DNA','DNT','دی‌ان‌ای','deoxyribonucleic acid','What does DNA stand for in English?','DNA kısaltmasının İngilizce açılımı nedir?','DNT abreviaturasının ingiliscə açılışı nədir?','نام کامل انگلیسی DNA چیست؟','https://www.genome.gov/genetics-glossary/Deoxyribonucleic-Acid'),
('genomics','RNA','RNA','RNT','آر‌ان‌ای','ribonucleic acid','What does RNA stand for in English?','RNA kısaltmasının İngilizce açılımı nedir?','RNT abreviaturasının ingiliscə açılışı nədir?','نام کامل انگلیسی RNA چیست؟','https://www.genome.gov/genetics-glossary/Ribonucleic-Acid'),
('genomics','Adenine','Adenin','Adenin','آدنین','thymine','In DNA, which base pairs with adenine?','DNA’da adenin hangi bazla eşleşir?','DNT-də adenin hansı əsasla cütləşir?','در DNA، آدنین با کدام باز جفت می‌شود؟','https://www.genome.gov/genetics-glossary/Base-Pair'),
('genomics','Cytosine','Sitozin','Sitozin','سیتوزین','guanine','In DNA, which base pairs with cytosine?','DNA’da sitozin hangi bazla eşleşir?','DNT-də sitozin hansı əsasla cütləşir?','در DNA، سیتوزین با کدام باز جفت می‌شود؟','https://www.genome.gov/genetics-glossary/Base-Pair'),
('genomics','Gene','Gen','Gen','ژن','a segment of DNA','What is a gene, in basic terms?','Basitçe gen nedir?','Sadə şəkildə gen nədir?','به‌طور ساده، ژن چیست؟','https://www.genome.gov/genetics-glossary/Gene'),
('genomics','Genome','Genom','Genom','ژنوم','all of an organism’s genetic material','What does the term genome refer to?','Genom terimi neyi ifade eder?','Genom termini nəyi ifadə edir?','اصطلاح ژنوم به چه چیزی اشاره دارد؟','https://www.genome.gov/genetics-glossary/Genome'),
('water_cycle','evaporation','buharlaşma','buxarlanma','تبخیر','evaporation','What is the water-cycle process called when liquid water becomes water vapor?','Sıvı suyun su buharına dönüşmesine su döngüsünde ne ad verilir?','Maye suyun su buxarına çevrilməsi su dövranında necə adlanır?','در چرخهٔ آب، تبدیل آب مایع به بخار آب چه نام دارد؟','https://www.usgs.gov/special-topics/water-science-school/science/water-cycle'),
('water_cycle','condensation','yoğuşma','kondensasiya','میعان','condensation','What is the water-cycle process called when water vapor forms liquid droplets?','Su buharının sıvı damlacıklara dönüşmesine su döngüsünde ne ad verilir?','Su buxarının maye damcılara çevrilməsi su dövranında necə adlanır?','در چرخهٔ آب، تبدیل بخار آب به قطره‌های مایع چه نام دارد؟','https://www.usgs.gov/special-topics/water-science-school/science/water-cycle'),
('water_cycle','precipitation','yağış','yağıntı','بارش','precipitation','What is water falling from clouds as rain, snow, sleet, or hail called?','Bulutlardan yağmur, kar, sulu kar veya dolu olarak düşen suya ne ad verilir?','Buludlardan yağış, qar, sulu qar və ya dolu şəklində düşən su necə adlanır?','فرود آمدن آب از ابرها به شکل باران، برف یا تگرگ چه نام دارد؟','https://www.usgs.gov/special-topics/water-science-school/science/water-cycle'),
('water_cycle','transpiration','terleme','transpirasiya','تعرق','transpiration','What is the release of water vapor from plants called?','Bitkilerin su buharı salmasına ne ad verilir?','Bitkilərin su buxarı buraxması necə adlanır?','آزاد شدن بخار آب از گیاهان چه نام دارد؟','https://www.usgs.gov/special-topics/water-science-school/science/water-cycle'),
('water_cycle','collection','birikme','toplanma','تجمع','collection','What is the water-cycle stage in which water gathers in oceans, lakes, and rivers called?','Suyun okyanus, göl ve nehirlerde biriktiği su döngüsü aşamasına ne ad verilir?','Suyun okean, göl və çaylarda toplandığı su dövranı mərhələsi necə adlanır?','مرحله‌ای از چرخهٔ آب که آب در اقیانوس‌ها، دریاچه‌ها و رودها جمع می‌شود چه نام دارد؟','https://www.usgs.gov/special-topics/water-science-school/science/water-cycle'),
('water_cycle','sublimation','süblimleşme','sublimasiya','تصعید','sublimation','What is the direct change of ice into water vapor called?','Buzun doğrudan su buharına dönüşmesine ne ad verilir?','Buzun birbaşa su buxarına çevrilməsi necə adlanır?','تبدیل مستقیم یخ به بخار آب چه نام دارد؟','https://www.usgs.gov/special-topics/water-science-school/science/water-cycle')]

# Load the 60 reviewed seed records supplied with this task, then add exactly 40.
with open(os.path.join(BASE,'_part1.json'),encoding='utf-8') as f: items=json.load(f)['items']
assert len(items)==60
for j,x in enumerate(raw,61):
 d,ie,it,ia,ifa, gold,qe,qt,qa,qf,src=x
 items.append({'item_id':f'Q{j:03d}','domain':d,'identifier_en':ie,'identifier_tr':it,'identifier_az':ia,'identifier_fa':ifa,
 'gold_en':gold,'gold_tr':gold,'gold_az':gold,'gold_fa':gold,'question_en':qe,'question_tr':qt,'question_az':qa,'question_fa':qf,
 'source_url':src,'source_check_status':'source_to_be_manually_verified','translation_review_status':'native_speaker_review_pending'})
assert len(items)==100

langs={'tr':'Turkish','az':'Azerbaijani','fa':'Persian'}
instruction={'en':'Answer with a single short term only, without any explanation.','tr':'Yanıt olarak yalnızca kısa tek bir terim yaz, açıklama ekleme.','az':'Cavab olaraq yalnız qısa tək bir termin yaz, izah əlavə etmə.','fa':'پاسخ را فقط در قالب یک عبارت کوتاه بنویسید و توضیح ندهید.'}
cond_names=['c1_baseline_en','c2_native_no_context','c3_native_identifier_only_instruction_language_confound','c4_native_with_paraphrased_context_answer_matches_prior']
runs=[]
for it in items:
 for lang in ('tr','az','fa'):
  script='Arabic' if lang=='fa' else 'Latin'
  for c in range(1,5):
   qlang='en' if c in (1,3) else lang
   q=it['question_'+qlang]
   if c==3:
    q=q.replace(it['identifier_en'],it['identifier_'+lang])
   prompt=q+' '+instruction['en' if c in (1,3) else lang]
   context=''
   if c==4:
    gold=it['gold_'+lang]; ident=it['identifier_'+lang]
    context=f"{ident}: {gold}." if lang!='fa' else f"{ident}: {gold}."
   runs.append([f"{it['item_id']}_{lang}_C{c}",it['item_id'],lang,f'C{c}',qlang,script,c==4,prompt,context,it['gold_'+lang],it['gold_'+lang],it['source_url'],cond_names[c-1]])

item_cols=list(items[0].keys())
run_cols=['run_id','item_id','language','condition','prompt_language','script','context_used','prompt','context','gold_answer','prior_answer','source_url','condition_description']
wb=Workbook(); ws=wb.active; ws.title='Items'; wr=wb.create_sheet('Runs_1200'); wn=wb.create_sheet('Design_Notes')
def fill_sheet(sh,headers,rows):
 sh.append(headers)
 for row in rows: sh.append(row)
 sh.freeze_panes='A2'; sh.auto_filter.ref=sh.dimensions
 for c in sh[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='17365D'); c.alignment=Alignment(vertical='center',wrap_text=True)
 for col in sh.columns:
  letter=get_column_letter(col[0].column); sh.column_dimensions[letter].width=min(48,max(14,max((len(str(c.value or '')) for c in col[:100]),default=12)+2))
 for row in sh.iter_rows(min_row=2):
  for c in row: c.alignment=Alignment(vertical='top',wrap_text=True)
fill_sheet(ws,item_cols,[[i.get(k,'') for k in item_cols] for i in items])
fill_sheet(wr,run_cols,runs)
notes=[['Section','English','فارسی'],
 ['Purpose','Controlled multilingual factual-answer pilot: 100 items × 3 languages × 4 conditions = 1,200 runs.','پایلوت کنترل‌شدهٔ پاسخ‌گویی دانشی چندزبانه: ۱۰۰ مورد × ۳ زبان × ۴ وضعیت = ۱۲۰۰ اجرا.'],
 ['Languages','tr = Turkish; az = Azerbaijani; fa = Persian.','tr = ترکی؛ az = آذربایجانی؛ fa = فارسی.'],
 ['C1','English question and instruction; no context.','پرسش و دستور انگلیسی؛ بدون بافت.'],
 ['C2','Native-language question and instruction; no context.','پرسش و دستور به زبان مقصد؛ بدون بافت.'],
 ['C3','English question with localized entity identifier; English instruction. This deliberately varies prompt-language cues.','پرسش انگلیسی با شناسهٔ بومی‌شدهٔ موجودیت؛ دستور انگلیسی. این وضعیت عمداً سرنخ‌های زبانی را تغییر می‌دهد.'],
 ['C4','Native-language question/instruction plus a short answer-bearing context; intended to test contextual support.','پرسش و دستور به زبان مقصد همراه با بافت کوتاهِ حاوی پاسخ؛ برای سنجش کمک بافت.'],
 ['Columns','gold_answer is the target; prior_answer is the supplied answer/context target; source_url gives a reference lead.','gold_answer پاسخ معیار است؛ prior_answer پاسخ/هدف بافت را نگه می‌دارد؛ source_url نشانی منبع پیشنهادی است.'],
 ['Review caveat','Translations and references are machine-prepared and marked pending manual/native-speaker review. Validate before research use.','ترجمه‌ها و منابع به‌صورت ماشینی آماده شده‌اند و نیازمند بازبینی دستی/گویشور بومی هستند؛ پیش از استفادهٔ پژوهشی اعتبارسنجی شوند.']]
for r in notes: wn.append(r)
wn.freeze_panes='A2'; wn.column_dimensions['A'].width=24; wn.column_dimensions['B'].width=72; wn.column_dimensions['C'].width=72
for c in wn[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='17365D')
for row in wn.iter_rows():
 for c in row: c.alignment=Alignment(wrap_text=True,vertical='top')
for r in range(2,wn.max_row+1): wn.row_dimensions[r].height=45
wb.save(OUT)
# Re-open and validate saved workbook, sheet counts, unique run ids, critical fields.
check=load_workbook(OUT,read_only=True,data_only=True)
assert check['Items'].max_row==101 and check['Runs_1200'].max_row==1201
assert check['Design_Notes'].max_row==9
critical_item=['item_id','domain','question_en','gold_en','question_tr','gold_tr','question_az','gold_az','question_fa','gold_fa']
idx={k:item_cols.index(k)+1 for k in critical_item}
assert all(wsrow[idx[k]] is not None and str(wsrow[idx[k]]).strip() for wsrow in check['Items'].iter_rows(min_row=2,values_only=True) for k in critical_item)
ri={k:run_cols.index(k)+1 for k in ['run_id','item_id','language','condition','prompt','gold_answer','source_url']}
rr=list(check['Runs_1200'].iter_rows(min_row=2,values_only=True))
assert len(rr)==1200 and len({r[ri['run_id']-1] for r in rr})==1200
assert all(r[ri[k]-1] is not None and str(r[ri[k]-1]).strip() for r in rr for k in ri)
assert len({r[0] for r in check['Items'].iter_rows(min_row=2,values_only=True)})==100
print('SUCCESS',OUT,'bytes',os.path.getsize(OUT),'items',check['Items'].max_row-1,'runs',len(rr),'notes',check['Design_Notes'].max_row-1)
print('Critical blanks: 0; unique run_ids: 1200; languages tr/az/fa; conditions C1-C4')
