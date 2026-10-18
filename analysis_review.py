"""V4 checks and additional summaries. Run after: python analysis.py.
Reads the original seven-column CSV; derived IDs and flags are not source fields.
"""
from pathlib import Path
import pandas as pd,numpy as np,re,json,collections,hashlib,sys

ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'research_data.json').read_text(encoding='utf-8'))
S=ROOT/'source.csv';d=pd.read_csv(S)
assert list(d)==['채널명','영상 제목','영상 URL','업로드 날짜','조회수','영상 길이','영상 설명']
assert len(d)==1680 and d.isna().sum().sum()==0 and d['영상 URL'].duplicated().sum()==0
assert hashlib.sha256(S.read_bytes()).hexdigest()==D['source_sha256']
dates=pd.to_datetime(d['업로드 날짜']);assert dates.between('2025-01-01','2025-12-31').all()
d['channel']=d['채널명'].str.replace(r' \(.*\)','',regex=True)
d['views']=pd.to_numeric(d['조회수']);d['rank']=d.groupby('channel').views.rank(ascending=False,method='first')
d['quota']=d.groupby('channel').views.transform(lambda s:int(np.ceil(len(s)*.25)));d['hit']=d['rank']<=d['quota']
def clean(s):return re.sub(r'https?://\S+|www\.\S+',' ',str(s).replace('\\n','\n')).lower()
boiler={};boiler_stats=[]
for c,g in d.groupby('channel'):
 counts=collections.Counter(l.strip() for text in g['영상 설명'] for l in clean(text).splitlines() if len(l.strip())>=8)
 threshold=max(10,int(np.ceil(len(g)*.2)));boiler[c]={l for l,n in counts.items() if n>=threshold}
 boiler_stats.append({'channel':c,'threshold_videos':threshold,'distinct_removed_lines':len(boiler[c]),'common_removed_examples':[{'line':l,'videos':n} for l,n in counts.most_common() if l in boiler[c]][:8]})
d['description_clean']=['\n'.join(l for l in clean(s).splitlines() if l.strip() not in boiler[c]) for c,s in zip(d.channel,d['영상 설명'])]
d['core']=d['영상 제목'].str.replace(r'\[(?:EN[^\]]*|ENG[^\]]*)\]','',regex=True).str.replace(r'\s*[/｜|ㅣ]\s*(?:14F|크랩|스브스뉴스|비디오머그).*','',regex=True).str.strip()
for topic,words in D['topics'].items():
 pattern='|'.join(r'\bai\b' if w=='ai' else re.escape(w) for w in words)
 d[topic]=(d['영상 제목'].map(clean)+' '+d.description_clean).str.contains(pattern,regex=True)
 d['title_'+topic]=d['영상 제목'].map(clean).str.contains(pattern,regex=True)
for name,pattern in D['feature_patterns'].items():d[name]=d.core.str.contains(pattern,regex=True)
def cell(g):
 return {'n':len(g),'hits':int(g.hit.sum()),'rate':float(g.hit.mean()) if len(g) else None}
def same(a,b):
 assert a['n']==b['n'] and a['hits']==b['hits']
 assert a['rate']==b['rate']
same(cell(d),D['overall'])
for r in D['feature_results']:
 same(cell(d[d[r['feature']]]),r['with']);same(cell(d[~d[r['feature']]]),r['without'])
for r in D['feature_by_channel']:
 g=d[d.channel==r['channel']];same(cell(g[g[r['feature']]]),r['with']);same(cell(g[~g[r['feature']]]),r['without'])
for r in D['topic_results']:
 g=d[d.channel==r['channel']];same(cell(g[g[r['topic']]]),r['with']);same(cell(g[g['title_'+r['topic']]]),r['title_only'])
assert int(d.hit.sum())==422
assert int((d[list(D['topics'])].sum(axis=1)>1).sum())==723
assert int((d[list(D['topics'])].sum(axis=1)==0).sum())==282
old={v['url']:v for v in D['videos']}
for _,r in d.iterrows():
 v=old[r['영상 URL']]
 assert v['top_quartile']==bool(r.hit)
 assert v['topics']==[t for t in D['topics'] if r[t]]
 assert v['features']==[f for f in D['feature_patterns'] if r[f]]

heat=[]
for c in D['channels']:
 g=d[d.channel==c]
 for t in D['topics']:
  subset=g[g[t]];title=g[g['title_'+t]]
  heat.append({'channel':c,'topic':t,'channel_total':len(g),'tagged':cell(subset),'upload_share':len(subset)/len(g),'title_only':cell(title)})
overview=[]
for t in D['topics']:
 g=d[d[t]];overview.append({'topic':t,**cell(g),'upload_share':len(g)/len(d),'title_only':cell(d[d['title_'+t]])})

A=json.loads((ROOT/'image_sources.json').read_text(encoding='utf-8'))
samples=[]
for item in A['videos']:
 row=d[d['영상 URL']==item['url']].iloc[0]
 matches={}
 for t,words in D['topics'].items():
  if row[t]:matches[t]={'title_words':[w for w in words if re.search(r'\bai\b' if w=='ai' else re.escape(w),clean(row['영상 제목']))],'description_words':[w for w in words if re.search(r'\bai\b' if w=='ai' else re.escape(w),row.description_clean)]}
 samples.append({'video_id_derived_from_url':item['video_id_derived_from_url'],'channel':row.channel,'title':row['영상 제목'],'url':row['영상 URL'],'description':row['영상 설명'],'description_after_repeated_line_removal':row.description_clean,'matches':matches,'top_quartile':bool(row.hit)})

collection=(ROOT/'collection_report.md').read_text(encoding='utf-8')
assert '2026-10-18T17:29:47.614730+09:00' in collection
collection_evidence={'date':'2026-10-18','recorded_timestamp':'2026-10-18T17:29:47.614730+09:00','evidence':'collection_report.md (Firecrawl collection report); local raw/provenance.json also preserves per-video collectedAt. No collected_at column is assumed in CSV.'}
metrics={'version':4,'source_sha256':D['source_sha256'],'original_columns':list(d.columns[:7]),'source_rows':1680,'missing_values':0,'duplicate_urls':0,'multi_label':723,'untagged':282,'top_quartile_count':422,'channel_quota':[{'channel':c,'n':int((d.channel==c).sum()),'quota':int(d.loc[d.channel==c,'quota'].iloc[0])} for c in D['channels']],'collection_evidence':collection_evidence,'topic_overview':overview,'upload_heatmap':heat,'boilerplate_review':boiler_stats,'case_samples':samples,'checks':{'all_1680_topic_and_title_flags_match_v3':True,'all_40_topic_cells_match_v3':True,'all_6_title_features_and_30_channel_cells_match_v3':True}}
metrics['classification_limit']='제목·설명 단어 목록에 의한 탐색 분류. 국가명·다의어·홍보 문구 잔여로 오분류가 있을 수 있다. 수작업으로 코딩한 정답 분류가 아니다.'
(ROOT/'v4_metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
if '--write-audit' in sys.argv:
 out=ROOT.parent/'output/v4_qa';out.mkdir(parents=True,exist_ok=True)
 text=['# 핵심 실제 영상의 제목·설명 표본 검토용 원문','']
 for s in samples:
  text+=['## '+s['channel']+' '+s['video_id_derived_from_url'],s['title'],s['url'],'매칭: '+json.dumps(s['matches'],ensure_ascii=False),'정제 후 설명:',s['description_after_repeated_line_removal'],'']
 (out/'case_texts.md').write_text('\n'.join(text),encoding='utf-8')
 (out/'accuracy.json').write_text(json.dumps({k:metrics[k] for k in ['source_sha256','source_rows','missing_values','duplicate_urls','multi_label','untagged','top_quartile_count','channel_quota','collection_evidence','checks']},ensure_ascii=False,indent=2),encoding='utf-8')
print('V4 independently verified: 1680 rows; 40 topic cells; six title features; 422 top-quartile videos; upload-share heatmap added.')
