from pathlib import Path
import json,pandas as pd,numpy as np,re,collections
D=Path(__file__).resolve().parent;D.mkdir(exist_ok=True)
d=pd.read_csv(Path(__file__).resolve().parent/'source.csv');d['channel']=d.채널명.str.replace(r' \(.*\)','',regex=True);d['month']=pd.to_datetime(d['업로드 날짜']).dt.month;d['minutes']=pd.to_timedelta(d['영상 길이']).dt.total_seconds()/60;d['log']=np.log2(d.조회수+1)
channels=['14F','크랩 KLAB','스브스뉴스','소탐대실','비디오머그']
# Explicit exploratory, multi-label topic dictionary. Description boilerplate cleaning follows prior EDA.
def clean(x):return re.sub(r'https?://\S+|www\.\S+',' ',str(x).replace('\\n','\n')).lower()
boiler={}
for c,g in d.groupby('channel'):
 counts=collections.Counter(l.strip() for s in g['영상 설명'] for l in clean(s).splitlines() if len(l.strip())>=8);boiler[c]={l for l,n in counts.items() if n>=max(10,int(np.ceil(len(g)*.2)))}
d['description']=['\n'.join(l for l in clean(s).splitlines() if l.strip() not in boiler[c]) for c,s in zip(d.channel,d['영상 설명'])]
topics={
'정치·국제':['트럼프','대통령','정치','탄핵','국회','선거','전쟁','러시아','우크라이나','관세','이란','이스라엘','북한','외교','군사','군대','미군','중국','일본','미국'],
'경제·소비':['가격','물가','주식','투자','경제','부동산','월급','소비','가성비','브랜드','기업','금리','연금','저축','대출','환율','상가','권리금','중고거래','보험'],
'기술·디지털':['인공지능','챗gpt','챗지피티','스마트폰','아이폰','반도체','로봇','알고리즘','ai','보안문자','공기청정기','배터리','전기차','드론'],
'음식·외식':['음식','식당','맛집','커피','라면','맥주','위스키','돈슐랭','셰프','급식','요리','감칠맛','돼지껍데기','소껍데기','국물','수박','우유','쌈채소','상추','환타'],
'건강·의학':['건강','다이어트','비만','수면','운동','질병','병원','의사','약물','치료','혈액','감기','엑스레이','가려','알약','무릎','노화','달리기','뼈소리','수술'],
'사회·생활':['청년','학교','교육','학생','세대','결혼','출산','직장','노동','문화','유행','샤워','이불','양말','선글라스','배달','기관사','첫차','출근','물결표'],
'과학·환경':['과학','실험','플라스틱','분리수거','환경','기후','생태','동물','타조','참새','눈동자','알루미늄','중력','우주','행성','반려','강아지','고양이','양들은','개는'],
'문화·연예':['공연','영화','가수','아이돌','뉴진스','이찬혁','시상식','청룡','콘서트','드라마','배우','케이팝','k팝','미술','만화','작품','문화유산']}
base=d.groupby(['channel','month'])['log'].transform('median');celln=d.groupby(['channel','month'])['log'].transform('size');d['residual']=d['log']-base;d.loc[celln<5,'residual']=np.nan
records=[];masks={};titlemasks={}
for topic,words in topics.items():
 pat='|'.join(r'\bai\b' if w=='ai' else re.escape(w) for w in words)
 masks[topic]=(d['영상 제목'].map(clean)+' '+d.description).str.contains(pat);titlemasks[topic]=d['영상 제목'].map(clean).str.contains(pat)
 for c in channels:
  g=d[d.channel==c];yes=masks[topic][g.index];t=yes&titlemasks[topic][g.index];ty=titlemasks[topic][g.index];sub=g[yes];other=g[~yes]
  rec={'channel':c,'topic':topic,'n':len(sub),'share':len(sub)/len(g),'median':float(sub.조회수.median()) if len(sub) else None,'ratio':float(sub.조회수.median()/g.조회수.median()) if len(sub)>=10 else None,'title_n':int(ty.sum()),'title_ratio':float(g[ty].조회수.median()/g.조회수.median()) if ty.sum()>=10 else None,'adjusted_n':int(sub.residual.notna().sum()),'adjusted':float(2**(sub.residual.median()-other.residual.median())) if sub.residual.notna().sum()>=10 and other.residual.notna().sum()>=10 else None}
  records.append(rec)
summary=[]
for c in channels:
 g=d[d.channel==c];summary.append({'channel':c,'n':len(g),'median':float(g.조회수.median()),'mean':float(g.조회수.mean()),'duration':float(g.minutes.median()),'top10_share':float(g.조회수.nlargest(int(np.ceil(len(g)*.1))).sum()/g.조회수.sum())})
video=[]
for i,r in d.iterrows():video.append({'channel':r.channel,'title':r['영상 제목'],'url':r['영상 URL'],'date':r['업로드 날짜'],'views':int(r.조회수),'minutes':float(r.minutes),'topics':[t for t in topics if masks[t][i]]})
result={'topics':topics,'channels':channels,'summary':summary,'comparisons':records,'videos':video,'coverage':float(pd.DataFrame(masks).any(axis=1).mean()),'unclassified':int((~pd.DataFrame(masks).any(axis=1)).sum()),'multi_label':int((pd.DataFrame(masks).sum(axis=1)>1).sum()),'excluded_month_baseline':int((celln<5).sum()),'collected_at':'2026-10-18','period':'2025-01-01 / 2025-12-31'}
(D/'research_data.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(pd.DataFrame(records).pivot(index='channel',columns='topic',values='ratio').round(2).to_string());print('counts');print(pd.DataFrame(records).pivot(index='channel',columns='topic',values='n').to_string());print('coverage',result['coverage'],'unclassified',result['unclassified'])
print(pd.DataFrame(records).query("(channel=='14F' and topic=='음식·외식') or (channel=='스브스뉴스' and topic=='정치·국제') or (channel=='비디오머그' and topic=='경제·소비')").to_string(index=False))
