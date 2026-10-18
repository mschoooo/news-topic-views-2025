from pathlib import Path
import pandas as pd,numpy as np,re,json,collections,hashlib
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'source.csv' if (ROOT/'source.csv').exists() else ROOT/'output/youtube_2025.csv'
OUT=ROOT if (ROOT/'source.csv').exists() else ROOT/'output/deck_v3'
OUT.mkdir(exist_ok=True,parents=True)
d=pd.read_csv(SRC);assert len(d)==1680 and not d['영상 URL'].duplicated().any()
channels=['14F','크랩 KLAB','스브스뉴스','소탐대실','비디오머그'];d['channel']=d['채널명'].str.replace(r' \(.*\)','',regex=True);d['month']=pd.to_datetime(d['업로드 날짜']).dt.month;d['minutes']=pd.to_timedelta(d['영상 길이']).dt.total_seconds()/60;d['views']=pd.to_numeric(d['조회수']);assert d['views'].ge(0).all() and d['minutes'].gt(0).all()
# V1 topic dictionary is frozen. V2 does not retune topic words against views.
topics={
'정치·국제':['트럼프','대통령','정치','탄핵','국회','선거','전쟁','러시아','우크라이나','관세','이란','이스라엘','북한','외교','군사','군대','미군','중국','일본','미국'],
'경제·소비':['가격','물가','주식','투자','경제','부동산','월급','소비','가성비','브랜드','기업','금리','연금','저축','대출','환율','상가','권리금','중고거래','보험'],
'기술·디지털':['인공지능','챗gpt','챗지피티','스마트폰','아이폰','반도체','로봇','알고리즘','ai','보안문자','공기청정기','배터리','전기차','드론'],
'음식·외식':['음식','식당','맛집','커피','라면','맥주','위스키','돈슐랭','셰프','급식','요리','감칠맛','돼지껍데기','소껍데기','국물','수박','우유','쌈채소','상추','환타'],
'건강·의학':['건강','다이어트','비만','수면','운동','질병','병원','의사','약물','치료','혈액','감기','엑스레이','가려','알약','무릎','노화','달리기','뼈소리','수술'],
'사회·생활':['청년','학교','교육','학생','세대','결혼','출산','직장','노동','문화','유행','샤워','이불','양말','선글라스','배달','기관사','첫차','출근','물결표'],
'과학·환경':['과학','실험','플라스틱','분리수거','환경','기후','생태','동물','타조','참새','눈동자','알루미늄','중력','우주','행성','반려','강아지','고양이','양들은','개는'],
'문화·연예':['공연','영화','가수','아이돌','뉴진스','이찬혁','시상식','청룡','콘서트','드라마','배우','케이팝','k팝','미술','만화','작품','문화유산']}
features={'물음표':r'[?？]','설명형 표현':r'왜|이유|비밀|정체|원리','직접 체험':r'직접|해봤|해 봤|먹어봤|먹어 봤|가봤|가 봤|씻겨봤|찍어봤|물어봤','숫자':r'\d','강한 감정 표현':r'충격|역대|소름|실화|레전드|미친|난리|경악|발칵|초유|대박','효용·주의':r'방법|꿀팁|절약|주의|위험|해야|하지\s?마|금지|비법|잘못'}
def clean(s):return re.sub(r'https?://\S+|www\.\S+',' ',str(s).replace('\\n','\n')).lower()
boiler={}
for c,g in d.groupby('channel'):
 freq=collections.Counter(l.strip() for s in g['영상 설명'] for l in clean(s).splitlines() if len(l.strip())>=8);boiler[c]={l for l,n in freq.items() if n>=max(10,int(np.ceil(len(g)*.2)))}
d['desc']=['\n'.join(l for l in clean(s).splitlines() if l.strip() not in boiler[c]) for c,s in zip(d.channel,d['영상 설명'])]
# Remove only language prefixes and known trailing channel branding. Series names remain.
d['core']=d['영상 제목'].str.replace(r'\[(?:EN[^\]]*|ENG[^\]]*)\]','',regex=True).str.replace(r'\s*[/｜|ㅣ]\s*(?:14F|크랩|스브스뉴스|비디오머그).*','',regex=True).str.strip()
for k,pattern in features.items():d[k]=d.core.str.contains(pattern,regex=True)
for t,words in topics.items():
 pattern='|'.join(r'\bai\b' if x=='ai' else re.escape(x) for x in words);d[t]=(d['영상 제목'].map(clean)+' '+d.desc).str.contains(pattern,regex=True);d['title_'+t]=d['영상 제목'].map(clean).str.contains(pattern,regex=True)
d['rank']=d.groupby('channel').views.rank(ascending=False,method='first');d['quota']=d.groupby('channel').views.transform(lambda s:int(np.ceil(len(s)*.25)));d['hit']=d['rank']<=d['quota']
def cell(g):return {'n':len(g),'hits':int(g.hit.sum()),'rate':float(g.hit.mean()) if len(g) else None,'median_views':float(g.views.median()) if len(g) else None}
summ=[]
for c in channels:
 g=d[d.channel==c];s=cell(g);s.update(channel=c,cutoff=int(g[g.hit].views.min()),median_minutes=float(g.minutes.median()));summ.append(s)
topic_rows=[]
for c in channels:
 for t in topics:
  g=d[d.channel==c];yes=cell(g[g[t]]);no=cell(g[~g[t]]);title=cell(g[g['title_'+t]]);topic_rows.append({'channel':c,'topic':t,'with':yes,'without':no,'title_only':title})
feature_rows=[];feature_channels=[]
for f in features:
 a=cell(d[d[f]]);b=cell(d[~d[f]]);feature_rows.append({'feature':f,'with':a,'without':b,'difference_pp':(a['rate']-b['rate'])*100})
 for c in channels:
  g=d[d.channel==c];a=cell(g[g[f]]);b=cell(g[~g[f]]);feature_channels.append({'feature':f,'channel':c,'with':a,'without':b,'difference_pp':(a['rate']-b['rate'])*100 if a['n'] and b['n'] else None})
four=[{'explanation':e,'question':q,**cell(d[(d['설명형 표현']==e)&(d['물음표']==q)])} for e,q in [(False,False),(False,True),(True,False),(True,True)]]
combos=[]
for c,t in [('14F','음식·외식'),('비디오머그','경제·소비'),('비디오머그','기술·디지털')]:
 g=d[(d.channel==c)&d[t]];combos.append({'channel':c,'topic':t,'with':cell(g[g['설명형 표현']]),'without':cell(g[~g['설명형 표현']])})
# Exploratory linear probability models. Coefficients are adjusted associations,
# not changes produced by changing a title. No significance/causal claims.
X=pd.concat([pd.get_dummies(d.channel,prefix='channel',drop_first=True,dtype=float),pd.get_dummies(d.month,prefix='month',drop_first=True,dtype=float)],axis=1)
X['log2_minutes']=np.log2(d.minutes);X['log2_minutes_squared']=X.log2_minutes**2;X['chars_per_10']=d.core.str.len()/10;X['chars_squared']=X.chars_per_10**2
for t in topics:X[t]=d[t].astype(float)
for f in features:X[f]=d[f].astype(float)
def fit(frame,mask):
 a=np.column_stack([np.ones(int(mask.sum())),frame.loc[mask].to_numpy(float)]);y=d.loc[mask,'hit'].to_numpy(float);coef=np.linalg.lstsq(a,y,rcond=None)[0];return {f:float(coef[frame.columns.get_loc(f)+1]*100) for f in features}
allmask=pd.Series(True,index=d.index);basecoef=fit(X,allmask)
Xs=X.copy();series_counts={}
for name,pattern in {'돈슐랭':'돈슐랭','교양이':'교양이를\\s?부탁해','지식뉴스':'지식뉴스','귀에빡종원':'귀에빡종원','아마겟돈':'아마겟돈','주락이월드':'주락이월드','선발대':'선발대','타이머':'타이머','오그랲':'오그랲'}.items():
 mask=d['영상 제목'].str.contains(pattern,regex=True);series_counts[name]=int(mask.sum())
 if mask.sum()>=20:Xs['series_'+name]=mask.astype(float)
models={'adjusted':basecoef,'with_series':fit(Xs,allmask),'without_top1pct':fit(X,d.views<d.groupby('channel').views.transform(lambda s:s.quantile(.99))),'leave_one_channel_out':{c:fit(X,d.channel!=c) for c in channels},'series_counts':series_counts,'design_columns':list(X.columns),'series_design_columns':list(Xs.columns)}
lengths=[]
for lo,hi,label in [(0,25,'25자 이하'),(25,40,'26–40자'),(40,55,'41–55자'),(55,1000,'56자 이상')]:lengths.append({'label':label,**cell(d[d.core.str.len().gt(lo)&d.core.str.len().le(hi)])})
videos=[]
for _,r in d.iterrows():videos.append({'channel':r.channel,'title':r['영상 제목'],'core_title':r.core,'url':r['영상 URL'],'date':r['업로드 날짜'],'views':int(r.views),'minutes':float(r.minutes),'channel_rank':int(r['rank']),'top_quartile':bool(r.hit),'topics':[t for t in topics if r[t]],'features':[f for f in features if r[f]]})
res={'schema_version':2,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'channels':channels,'topics':topics,'feature_patterns':features,'summary':summ,'overall':cell(d),'topic_results':topic_rows,'feature_results':feature_rows,'feature_by_channel':feature_channels,'explanation_question_groups':four,'topic_title_combinations':combos,'models':models,'title_lengths':lengths,'videos':videos,'classification':{'unclassified':int((~d[list(topics)].any(axis=1)).sum()),'multi_label':int((d[list(topics)].sum(axis=1)>1).sum())},'period':'2025-01-01 / 2025-12-31','views_collected_at':'2026-10-18'}
res['schema_version']=3
res['topic_overview']=[{'topic':t,**cell(d[d[t]]),'share_of_all':float(d[t].mean())} for t in topics]
res['topic_overview'].sort(key=lambda r:-r['n'])
res['total_topic_assignments']=int(d[list(topics)].to_numpy().sum())
(OUT/'research_data.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print('overall',res['overall']);print('FEATURES',[(r['feature'],r['with']['n'],round(r['with']['rate']*100,1),round(r['without']['rate']*100,1)) for r in feature_rows]);print('adjusted',models['adjusted']);print('series-adjusted',models['with_series']);print('series',series_counts)
