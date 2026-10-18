"""Build the V4 HTML deck and its separate appendix from verified summaries."""
from pathlib import Path
import json,html,re,shutil

R=Path(__file__).resolve().parent
D=json.loads((R/'research_data.json').read_text(encoding='utf-8'))
M=json.loads((R/'v4_metrics.json').read_text(encoding='utf-8'))
A=json.loads((R/'image_sources.json').read_text(encoding='utf-8'))
CH=D['channels'];TOP=list(D['topics']);V={v['video_id_derived_from_url']:v for v in A['videos']};P={p['channel']:p for p in A['profiles']}
C=dict(zip(CH,['#f36c63','#41b8c6','#8097ff','#c09cef','#f6ad58']))
INK='#152030';MUT='#526174';LIME='#d8f35b';WHITE='#f6f7fa'
T={(r['channel'],r['topic']):r for r in D['topic_results']};F={r['feature']:r for r in D['feature_results']};FC={(r['channel'],r['feature']):r for r in D['feature_by_channel']}
OV={r['topic']:r for r in M['topic_overview']};HEAT={(r['channel'],r['topic']):r for r in M['upload_heatmap']}
S={r['channel']:r for r in D['summary']};BASE='https://mschoooo.github.io/news-topic-views-2025/'
E=lambda s:html.escape(str(s),quote=True)
def percent(x,d=0):return f'{x*100:.{d}f}%'
def text(x,y,s,size=30,color=INK,anchor='start',weight=500):return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{E(s)}</text>'
def rect(x,y,w,h,c,r=0):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" rx="{r}"/>'
def line(x1,y1,x2,y2,c='#ccd4de',w=1,dash=''):return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" stroke-dasharray="{dash}"/>'
def svg(parts,height,label,width=1728):return f'<svg class="dataviz" viewBox="0 0 {width} {height}" role="img" aria-label="{E(label)}" xmlns="http://www.w3.org/2000/svg">'+''.join(parts)+'</svg>'
def dots(n,fill=LIME,empty='#364555'):
 return svg([f'<circle cx="{14+(i%10)*26}" cy="{14+(i//10)*26}" r="8" fill="{fill if i<n else empty}"/>' for i in range(100)],262,f'100개 중 {n}개를 강조한 반올림 비중 도식',262)
def profile(c,small=False):return f'<img class="profile{" small" if small else ""}" src="{E(P[c]["local_path"])}" alt="{E(c)} 공식 채널 프로필" width="108" height="108">'
def core_title(vid):return next(v['core_title'] for v in D['videos'] if v['url']==V[vid]['url'])
def video(vid,title=None,highlight=False,meta=True):
 v=V[vid];title=title or core_title(vid);shown=E(title)
 if highlight:shown=re.sub(r'왜|이유|비밀|정체|원리',lambda m:'<mark>'+m.group()+'</mark>',shown)
 out=f'<a class="video-link" data-video-id="{vid}" href="{E(v["url"])}" target="_blank" rel="noopener" title="{E(v["title"])}"><img src="{E(v["local_path"])}" alt="{E(v["channel"]+": "+v["title"])}" width="1280" height="720"><div class="video-title">{shown}</div></a>'
 if meta:out+=f'<div class="video-meta">{E(v["channel"])} · {v["views_at_collection"]:,}회 · 원문 ↗</div>'
 return out

def dist_chart():
 rows=sorted(M['topic_overview'],key=lambda r:-r['n']);parts=[];x0=300;x1=1390;scale=(x1-x0)/750
 for tick in range(0,751,150):
  x=x0+tick*scale;parts+=[line(x,20,x,586),text(x,630,f'{tick}편',26,MUT,'middle')]
 for i,r in enumerate(rows):
  y=35+i*69;c=INK if i<2 else '#8495a9';end=x0+r['n']*scale
  parts +=[text(0,y+34,r['topic'],32,weight=650),rect(x0,y,r['n']*scale,43,c,2),text(end+15,y+34,f'{r["n"]:,}',33,c,weight=750),text(1715,y+34,percent(r['upload_share'],1),34,INK,'end',700)]
 return svg(parts,650,'전체 1,680편 중 주제별 태그 영상 수와 비중. 복수 태그 허용.')

def heat_chart():
 parts=[];left=290;cw=179;top=85;step=105
 for i,t in enumerate(TOP):parts.append(text(left+i*cw+cw/2,35,t,27,INK,'middle',650))
 for j,c in enumerate(CH):
  y=top+j*step;parts +=[rect(0,y+4,7,80,C[c]),text(26,y+39,c,33,weight=700),text(26,y+75,f'n={S[c]["n"]}편',26,MUT)]
  for i,t in enumerate(TOP):
   r=HEAT[c,t];v=r['upload_share'];mix=min(1,v/.8);start=(234,239,245);end=(52,79,163);rgb=tuple(round(a+(b-a)*mix) for a,b in zip(start,end));col='rgb'+str(rgb)
   x=left+i*cw;parts +=[rect(x,y,cw-7,88,col,3),text(x+(cw-7)/2,y+54,percent(v),43,'#fff' if v>.48 else INK,'middle',730)]
 for i,v in enumerate([0,.2,.4,.6,.8]):
  rgb=tuple(round(a+(b-a)*v/.8) for a,b in zip((234,239,245),(52,79,163)));x=1010+i*130;parts +=[rect(x,625,38,22,'rgb'+str(rgb)),text(x+49,644,percent(v),25,MUT)]
 return svg(parts,665,'채널 안의 전체 영상 중 해당 주제 태그의 비중. 행 합계는 100%가 아님.')

def frequency_vs_performance():
 rows=sorted(M['topic_overview'],key=lambda r:-r['n']);parts=[];a=320;b=1145;w=470;step=64
 for x0 in [a,b]:
  for tick in [0,25,50]:
   x=x0+tick/50*w;parts +=[line(x,20,x,525,'#d7dee7'),text(x,574,f'{tick}%',26,MUT,'middle')]
 x=b+25/50*w;parts.append(line(x,20,x,525,'#9d6739',2,'7 7'))
 for i,r in enumerate(rows):
  y=39+i*step;parts.append(text(0,y+27,r['topic'],29,weight=650))
  for x0,value,col in [(a,r['upload_share'],INK if i==0 else '#8b9caf'),(b,r['rate'],'#be6a25' if r['topic']=='과학·환경' else '#bda38d')]:
   wid=value/.5*w;parts +=[rect(x0,y,wid,34,col,2),text(x0+wid+11,y+27,percent(value,1),30,INK,weight=650)]
 return svg(parts,605,'주제별 제작 비중과 상위권 비중을 별도 축으로 비교. 두 지표의 분모가 다름.')

def dumbbell():
 parts=[];x0=330;width=1000;top=80;step=105
 for tick in [0,10,20,30,40,50]:
  x=x0+tick/50*width;parts +=[line(x,25,x,558,'#344253'),text(x,609,f'{tick}%',27,'#bdc9d9','middle')]
 x=x0+25/50*width;parts +=[line(x,43,x,558,'#92a2b6',2,'6 7'),text(x,30,'약 25% 기준',25,'#bdc9d9','middle')]
 for i,c in enumerate(CH):
  r=FC[c,'설명형 표현'];no=r['without'];yes=r['with'];y=top+i*step;xn=x0+no['rate']/.5*width;xy=x0+yes['rate']/.5*width
  parts +=[rect(0,y-28,7,55,C[c]),text(25,y+11,c,32,WHITE,weight=650),line(xn,y,xy,y,C[c],5),f'<circle cx="{xn}" cy="{y}" r="10" fill="{INK}" stroke="{C[c]}" stroke-width="4"/>',f'<circle cx="{xy}" cy="{y}" r="11" fill="{C[c]}"/>',text(xn,y+39,percent(no['rate']),28,'#bdc9d9','middle'),text(xy,y-23,percent(yes['rate']),30,C[c],'middle',750),text(1710,y-7,f'포함 {yes["hits"]}/{yes["n"]}',26,'#e6edf5','end'),text(1710,y+27,f'미포함 {no["hits"]}/{no["n"]}',26,'#adbbce','end')]
 return svg(parts,635,'5개 채널에서 제목 다섯 단어 포함과 미포함 집단의 상위권 비중 및 분자·분모.')

slides=[]
def add(title,body,notes,cls='',eyebrow='',foot='',custom=False):slides.append(dict(title=title,body=body,notes=notes,cls=cls,eyebrow=eyebrow,foot=foot,custom=custom))
cover_ids=['5-L3V7rGuhk','Sc56962wLrQ','CVWl-HvshVI','njFNSJvm-DM','Jepfk32czqQ']
collage='<div class="collage">'+''.join(f'<figure><a href="{E(V[v]["url"])}" target="_blank" rel="noopener" title="{E(V[v]["title"])}"><img src="{E(V[v]["local_path"])}" alt="{E(V[v]["title"])}" width="1280" height="720"></a><figcaption>{E(V[v]["channel"])} · {E(core_title(v))}</figcaption></figure>' for v in cover_ids)+'</div>'
add('다음 영상, 무슨 주제로 어떤 제목을 쓸까?', '<div class="hero-copy"><div class="eyebrow">뉴미디어 정보 채널 운영자의 탐색</div><h1>다음 영상,<br>무슨 주제로<br><em>어떤 제목을 쓸까?</em></h1><p>내 채널의 다음 기획을 위해<br>방송사 채널에서 단서를 찾았습니다.</p><div class="hero-stat"><b>1,680</b><span>2025년 일반 영상<br>방송사 뉴미디어 5개 채널</span></div></div>'+collage,
 '저는 뉴미디어 정보 유튜브 채널을 운영합니다. 매번 다음 영상의 주제와 제목을 정해야 합니다. 방송사 전문 제작진은 어떤 내용을 다루고 어떻게 소개하는지 궁금해 다섯 채널의 2025년 일반 영상 1,680편을 살펴봤습니다. 방송사 순위가 아니라 내 채널에서 검증할 기획 단서를 찾는 탐색입니다. 오른쪽 이미지는 모두 원본 CSV에 있는 실제 영상입니다. 링크와 전체 원제목은 이미지 출처 목록에도 보존했습니다.\n전환: 먼저 제가 내리려는 두 가지 결정을 말씀드리겠습니다.',cls='dark hero',custom=True)
add('운영자로서, 두 가지가 궁금했습니다', '<p class="motivation-intro">뉴미디어 정보 유튜브 채널을 운영하며, 매번 기획 앞에서 묻습니다.</p><div class="question-board"><div><span>주제 선택</span><b>무엇을 다룰까?</b><p>사람들이 관심을 보일 소재는 무엇인가</p></div><div><span>제목 선택</span><b>어떻게 소개할까?</b><p>같은 정보라도 보고 싶게 만드는 표현은 무엇인가</p></div></div><div class="research-questions"><b>핵심 연구 질문</b><p>방송사 뉴미디어 뉴스 채널에서<br>콘텐츠 주제에 따라 조회수는 어떻게 달라지는가?</p><b>실무적 확장</b><p class="extension">제목 표현과 조회수의 관계도 주제·채널에 따라 달라지는가?</p></div>',
 '기존 핵심 연구 질문은 콘텐츠 주제에 따라 조회수가 어떻게 달라지는가입니다. 이 질문을 바꾸지 않았습니다. 제목 분석은 실제 운영자의 두 번째 결정을 위해 보완한 확장 탐색입니다. 공개 관찰 자료를 보기 때문에 특정 주제나 단어가 조회수를 높이는 원인인지 증명하려는 설계는 아닙니다.\n전환: 이런 결정을 전문적으로 내리는 다섯 채널을 비교 대상으로 삼았습니다.')
wall=''
for c,vid in zip(CH,cover_ids):
 wall+=f'<article class="channel-card" style="--cc:{C[c]}"><a href="{E(P[c]["url"])}" target="_blank" rel="noopener" aria-label="{E(c)} 공식 채널">{profile(c)}</a><div class="channel-name">{E(c)}</div><div class="network">{E(P[c]["network"])}</div><div class="channel-count">{S[c]["n"]}<span>편</span></div>'+video(vid,meta=False)+'</article>'
add('5개 채널의 일반 영상 1,680편', '<div class="channel-heading"><strong>5개 채널 · 1,680편</strong><p>업로드 2025.01.01–12.31<br>조회수 측정 2026.10.18</p></div><div class="channel-wall">'+wall+'</div><p class="channel-notice">쇼츠·라이브 제외 · 공개 접근 가능한 영상 · 영상 URL 중복·7개 항목 결측 0건</p>',
 '방송사 뉴미디어 5개 채널은 MBC14F575편, KBS크랩 370편, SBS스브스뉴스 315편, JTBC소탐대실 47편, SBS비디오머그 373편입니다. 공식 채널ID와 프로필은 기존 Firecrawl 원본의 채널 메타데이터에서 대조했습니다. 2025년 업로드 영상의 2026년 10월 18일 누적 조회수이며 2025년에 발생한 조회수만을 뜻하지 않습니다. 수집보고서의 시각과 원본 provenance의 1,680개 수집일을 대조했습니다. 삭제·비공개 등 현재 목록에서 찾을 수 없는 영상은 범위 밖입니다.\n전환: 채널 규모가 다르기 때문에 같은 방식의 비교 기준이 필요합니다.',cls='dark channels',custom=True)
method='<div class="method-grid"><div><div class="method-label">① 제목·설명 단어로 8개 주제 태그</div>'+video('KtSt2wjckak')+'<div class="tags"><span class="tag">경제·소비</span><span class="tag">기술·디지털</span></div><p class="caption">한 영상에 여러 태그 · 단어 사전 기반 탐색 분류</p></div><div class="metric-demo"><div class="metric-title">② 같은 채널 안에서<br>조회수순 상위 25%를 표시</div><div class="dot-formula">'+dots(25,INK,'#bfcbd8')+'<div><b>상위권</b><span>채널마다 약 4편 중 1편<br>전체 422/1,680편</span></div></div><div class="formula"><strong>상위권 비중</strong><br>상위권에 든 수 ÷ 해당 주제·제목 집단 수</div><p class="caption">그 집단 100편 중 35편이면 35%<br>조회수 증가율·미래 성공확률과 다름</p></div></div>'
add('태그를 붙이고, 채널 안의 상위권을 셉니다',method,
 '주제는 V1부터 고정한 8개 단어 사전으로 제목과 반복 안내 줄을 줄인 설명에서 찾았습니다. 아이패드 사례는 제목의 가격과 설명의 아이폰 등이 매칭돼 경제·소비와 기술·디지털 두 태그를 받았습니다. 모든 내용을 사람이 의미 판정한 정답 분류는 아닙니다. 다음으로 채널별 조회수 순위 상위 25%에 표시합니다. 채널 표본 수×25%를 올림해 144·93·79·12·94편, 총 422편입니다. 동률은 원본 행 순서를 유지한 rank(method=first)로 처리했습니다. 특정 태그/제목 집단에서 이 표시가 있는 수를 그 집단 전체 수로 나눈 값이 상위권 비중입니다.100편 중 35편이면 35%이며 조회수가 35%증가하거나 미래 성공확률 35%라는 뜻이 아닙니다.\n전환: 먼저 성과가 아니라 어떤 태그를 많이 다뤘는지부터 봅니다.',cls='method')
add('정치·국제와 경제·소비를 많이 다뤘습니다','<div class="chart-context"><b>주제 태그가 붙은 영상 수</b><span class="legend">오른쪽 비중의 분모: 전체 1,680편</span></div><div class="reveal">'+dist_chart()+'</div><p class="caption">복수 태그 723편 → 비중 합계는 100%를 넘습니다 · 태그 없는 영상 282편</p>',
 '전체 편성을 먼저 봅니다. 정치·국제 684편 40.7%, 경제·소비 507편 30.2%입니다. 나머지 6개도 빠짐없이 표시했습니다. 모든 비중의 분모는 1,680편이며 중복 태그를 허용합니다.723편에 복수 태그가 있어 합계는 100%가 아닙니다.282편은 사전에 있는 8개 태그가 붙지 않았습니다. 데이터가 누락됐다는 뜻은 아닙니다. 국가명이나 다의어로 넓게 붙은 태그도 있어 분포를 사람이 판정한 모든 콘텐츠 주제의 분포로 해석하지 않습니다.\n전환: 이 전체 분포가 다섯 채널 모두의 편성을 뜻하지는 않습니다.',cls='distribution',eyebrow='먼저, 무엇을 많이 다뤘나')
add('채널마다 제작 편성도 달랐습니다','<div class="chart-context"><b>각 채널 전체 영상 중 해당 주제 태그의 비중</b><span class="legend">진할수록 많이 다룬 태그</span></div>'+heat_chart()+'<p class="caption">비디오머그는 정치·국제 78%, 14F는 음식·외식 27% · 행 합계는 100%가 아님<br>소탐대실은 전체 47편: 작은 표본의 세부 결과는 신중히 해석합니다.</p>',
 '이 장의 색은 조회수 성과가 아니라 제작 비중입니다. 분모가 각 채널의 전체 영상 수로 바뀌었습니다. 비디오머그 정치·국제는 292/373편 78.3%,14F 음식·외식은 154/575편 26.8%입니다. 각 행에도 복수 태그가 있어 합계 100%가 아닙니다. 소탐대실은 전체 47편으로 나머지 채널보다 표본이 작습니다.\n전환: 많이 다룬 주제가 상대 조회수 상위권에도 자주 들었을까요?',cls='heatmap')
add('제작 비중과 상위권 비중은 다른 정보입니다','<div class="metric-defs"><div><strong>제작 비중</strong><span>해당 태그 영상 수 / 전체 1,680편</span></div><div><strong>상위권 비중 · 기준 약 25%</strong><span>상위권 영상 수 / 해당 태그 영상 수</span></div></div>'+frequency_vs_performance()+'<p class="caption">제작은 정치·국제 40.7%, 상위권 비중은 과학·환경 30.4%가 가장 높게 관찰됐습니다.<br>이는 합산 관찰값이며, 가까운 수치의 통계적 우열을 검증한 것은 아닙니다.</p>',
 '같은 주제 행을 두 지표로 보되 분모는 다릅니다. 왼쪽은 제작 비중, 오른쪽은 해당 태그 안의 상위권 비중입니다. 정치·국제는 684/1680편으로 제작 비중 40.7%, 상위권은 196/684편 28.7%입니다. 과학·환경은 158/1680편 9.4%로 제작 비중이 작지만, 상위권은 48/158편 30.4%로 합산에서 가장 높았습니다. 경제·소비 28.8%, 정치·국제 28.7%처럼 가까운 값은 사실상 비슷한 관찰로 보고 우열을 주장하지 않습니다.25%점선은 오른쪽 상위권 지표의 대략적인 채널 내부 기준입니다.\n전환: 전체값을 그대로 우리 채널에 적용하기 전에 같은 태그의 채널 차이를 보겠습니다.',cls='comparison')
pair=''
for c,vid in [('14F','5-L3V7rGuhk'),('스브스뉴스','CVWl-HvshVI')]:
 r=T[c,'음식·외식']['with']
 pair+=f'<article><div class="evidence-top"><div class="channel">{profile(c,True)}{E(c)}</div><div><div class="rate">{percent(r["rate"])}</div><div class="count">상위권 {r["hits"]}/{r["n"]}편</div></div></div>'+video(vid)+'</article>'
add('같은 음식 태그도, 채널 안 성과는 달랐습니다','<p class="topic-caption">음식·외식 태그에서 표본이 가장 큰 두 채널을 비교했습니다.</p><div class="video-pair">'+pair+'</div><p class="case-note">수치는 음식 태그 집단 전체의 상위권 비중 · 두 영상은 각 집단의 실제 사례입니다.</p>',
 '음식·외식 태그 안에서 표본 수가 가장 큰 두 채널을 골랐습니다.14F154편에서 51편이 상위권 33.1%, 스브스뉴스 39편에서 5편이 상위권 12.8%였습니다. 업로드 수·시리즈·구독층·영상형식 등이 다른 채널의 집단 비교이며 같은 음식이면 어디서나 같은 성과라는 가정이 맞지 않음을 보여줍니다. 실제 급식 영상과 식당 영상은 집단의 예시이지 둘만의 성과로 33%와 13%를 계산한 것이 아닙니다. 제목만으로 음식 태그를 붙인 보조 비교에서도 14F41/105편 39.0%, 스브스뉴스 2/17편 11.8%로 관찰 방향은 유지됐지만 분류의 정답성을 입증한 것은 아닙니다.\n전환: 주제만으로 선택을 끝내지 않고, 같은 정보를 어떻게 제목으로 보여주는지도 보겠습니다.',cls='case-food')
cards=''
for vid,label,yes in [('EBQ9ZbFFLuY','포함 · 비밀',True),('5-L3V7rGuhk','포함 · 왜',True),('CVCxJWB_gm8','미포함 · 물음표만 있음',False)]:
 cards+='<article>'+video(vid,highlight=True)+f'<div class="rule-label {"yes" if yes else "no"}">{E(label)}</div></article>'
add('이유·원리를 예고하는 다섯 단어를 찾았습니다','<div class="five-words">왜 · 이유 · 비밀 · 정체 · 원리<span>영상 제목에 하나 이상 있으면 ‘포함’</span></div><div class="definition-cards">'+cards+'</div><p class="caption">의미 전체를 판정한 ‘설명형 제목’ 분류가 아닙니다. ‘…일까?’라도 다섯 단어가 없으면 미포함입니다.</p>',
 '주제를 무엇으로 정할지 보았다면, 이제 제목을 어떻게 표현했는지로 넘어갑니다. 이 분석은 제목에 왜·이유·비밀·정체·원리 중 한 단어라도 있는지 센 문자열 규칙입니다. 언어 접두와 알려진 끝 채널 표기를 제거한 제목 기준이며 시리즈 이름은 남겼습니다. 화면의 PB영상은 비밀, 급식 영상은 왜가 있어 포함입니다. 선글라스 영상은 실제로 이유나 원리를 설명할 법한 내용이어도 이 단어가 없으므로 미포함입니다. PB는 유통사 자체브랜드입니다. 제목의 품질이나 모든 설명적 제목을 완벽히 판정한 범주가 아니며 다의어도 섞일 수 있습니다. 썸네일과 설명의 단어는 이 제목 특징에 포함하지 않았습니다.\n전환: 이 규칙으로 전체 영상을 두 집단으로 나누면 어떤 비중이 관찰될까요?',cls='words-slide',eyebrow='주제 다음에는, 제목을 본다')
r=F['설명형 표현'];blocks=''
for name,key,fill in [('다섯 단어 미포함','without','#9eafc5'),('다섯 단어 포함','with',LIME)]:
 cell=r[key];blocks+=f'<article class="rate-block reveal"><div class="group">{name}</div><div class="rate-body"><div class="percentage">{cell["rate"]*100:.0f}<small>%</small></div><div class="hundred">{dots(round(cell["rate"]*100),fill)}</div></div><div class="count">상위권 {cell["hits"]:,} / {cell["n"]:,}편<span>각 제목 집단 중, 채널 내부 상위권에 든 비중</span></div></article>'
add('포함 집단에서 더 높은 비중이 관찰됐습니다','<div class="rate-comparison">'+blocks+'</div><p class="interpretation"><b>35%</b>는 ‘포함 집단 100편 중 약 35편이 상위권’이라는 뜻입니다.<br>조회수가 35% 증가했다거나 앞으로 성공할 확률이라는 뜻은 아닙니다.</p>',
 '앞 장에서 정의한 동일한 규칙을 적용했습니다. 미포함 1345편 중 306편 22.75%, 포함 335편 중 116편 34.63%가 각 채널 상위권입니다. 화면은 23%와 35%로 반올림했고 점 100개도 그 반올림한 비중을 그린 도식입니다. 이 335편과 1345편은 서로 다른 영상 집단입니다. 제목에 단어를 넣었기 때문에 생긴 변화나 같은 영상을 두 제목으로 실험한 결과가 아닙니다.\n전환: 이 전체 차이가 다섯 채널 모두에서 같았는지 확인하겠습니다.',cls='dark title-finding')
add('이 차이는 모든 채널에서 같지 않았습니다','<div class="chart-context"><div class="metric-key"><span>○ 미포함</span><b>● 포함</b></div><span class="legend">상위권 수 / 각 제목 집단 수</span></div>'+dumbbell()+'<p class="caption">14F는 42% vs21%, 크랩은 27% vs25% · 차이의 크기와 방향이 다릅니다.<br>소탐대실의 포함 집단은 17편으로 작습니다.</p>',
 '14F는 포함 42/100편 42.0%와 미포함 102/475편 21.5%, 비디오머그는 33/79편 41.8%와 61/294편 20.7%로 차이가 컸습니다. 크랩은 21/79편 26.6%와 72/291편 24.7%로 가까웠습니다. 스브스뉴스는 17/60편 28.3%와 62/255편 24.3%, 소탐대실은 3/17편 17.6%와 9/30편 30.0%로 방향도 같지 않았습니다. 소탐대실의 포함 집단 17편이라는 작은 분모에 주의합니다.25%는 대략적인 채널 내부 기준이고 채널별 올림으로 정확한 비중은 조금 다릅니다.\n전환: 제목의 차이가 주제 구성 때문일 수 있으니, 한 채널의 같은 주제 태그 안으로 범위를 좁혀보겠습니다.',cls='dark dumbbell-slide')
combo=next(r for r in D['topic_title_combinations'] if r['channel']=='비디오머그' and r['topic']=='경제·소비');pair=''
for label,key,vid in [('다섯 단어 포함','with','Jepfk32czqQ'),('다섯 단어 미포함','without','kue2O19f1Lg')]:
 r=combo[key];pair+=f'<article><div class="evidence-top"><div class="wordlabel">{label}<mark>경제·소비 태그 안에서</mark></div><div><div class="rate">{percent(r["rate"])}</div><div class="count">상위권 {r["hits"]}/{r["n"]}편</div></div></div>'+video(vid,highlight=(key=='with'))+'</article>'
add('경제·소비 181편 안에서도 차이가 보였습니다','<div class="population"><span>비디오머그 전체</span><b>373편</b><span>→ 경제·소비 태그</span><b>181편</b><span>→ 제목 단어로 나눔</span></div><div class="video-pair">'+pair+'</div><p class="case-note">제목만 분류했습니다. 오른쪽 썸네일에 적힌 ‘이유’는 세지 않았습니다.<br>집단별 관찰 비중이며, 두 영상을 비교 실험한 결과가 아닙니다.</p>',
 '앞선 편성 표에서 확인한 비디오머그 경제·소비 181편으로 좁힙니다. 다섯 단어 포함 51편 중 23편 45.1%, 미포함 130편 중 43편 33.1%가 상위권입니다. 두 집단을 합하면 181편, 상위권 66편입니다. 같은 주제 태그를 가진 영상끼리 범위를 좁혔지만 주제·시기·길이·시리즈·포맷·노출의 차이를 모두 없앤 비교는 아닙니다. 신세계·알리 영상은 제목에 이유가 있고, 애플페이 수수료 영상은 수집 제목에 다섯 단어가 없습니다. 오른쪽 썸네일에는 실제로 이유가 적혀 있습니다. 이는 잘못 짝지은 이미지가 아니라 제목과 썸네일 문구가 서로 다르다는 실제 사례입니다. 제목 문자열만 센 분석의 한계를 보여줍니다.\n전환: 이 결과를 성공 공식으로 외우기보다 기획자가 가져갈 단서로 정리하겠습니다.',cls='nested')
add('기획자가 가져갈 단서는 세 가지입니다','<div class="takeaway-grid"><article><span class="kicker">01 · 제작과 성과</span><h2>많이 만드는 것과<br>상위권 비중은 다르다</h2><div class="take-num">684편</div><p>가장 많이 다룬 정치·국제<br>상위권 비중은 28.7%</p><p class="detail">과학·환경은 158편, 상위권 30.4%<br>두 지표를 구분해 후보를 살펴본다</p></article><article><span class="kicker">02 · 채널의 맥락</span><h2>같은 태그도<br>채널에 따라 다르다</h2><div class="take-num">33% · 13%</div><p>음식 태그의 14F와 스브스뉴스<br>각 채널 내부 상위권 비중</p><p class="detail">다른 채널의 인기 소재를<br>내 채널의 정답으로 바로 옮기지 않는다</p></article><article><span class="kicker">03 · 제목의 가설</span><h2>다섯 단어는<br>비교할 제목의 단서다</h2><div class="take-num">35% · 23%</div><p>단어 포함·미포함 집단<br>전체 관찰 비중</p><p class="detail">답할 수 있는 이유 질문을<br>새 제목의 비교 후보로 만든다</p></article></div>',
 '세 장면만 남기겠습니다. 첫째, 가장 많이 다룬 주제가 상위권 비중에서도 같은 순위였던 것은 아닙니다. 둘째, 같은 음식 태그의 성과도 채널마다 달랐습니다. 셋째, 다섯 단어 포함 집단의 높은 비중은 새 제목을 비교 후보로 만들 단서입니다. 이 세 관찰을 내 채널에서 확인할 가설로 바꿔야 합니다. 채널 순위를 매기거나 유의성이 검증된 주제 추천 순위를 만든 것은 아닙니다.\n전환: 실제 기획 회의 한 번으로 이 단서를 옮겨보겠습니다.',cls='takeaways',foot='각 수치는 앞선 관찰 결과의 요약 · 제목 변경의 인과효과·미래 조회수 예측이 아님')
add('우리 채널에서는 이렇게 시험해 볼 수 있습니다','<div class="planning"><aside><div class="label">출발점이 된 실제 영상</div>'+video('EBQ9ZbFFLuY',title='같은 공장, 가격은 반값? 노브랜드 PB의 비밀')+'<p>‘가격 차이의 이유’라는 질문을<br>우리 독자에게도 확인해 볼까?<br><span class="source-pill">PB = 유통사 자체브랜드</span></p></aside><div class="scenario"><p><span class="tag lime">가상 새 기획</span>PB 과자와 브랜드 과자의 가격 차이</p><div class="scenario-step"><span>취재 질문</span><div><b>가격 차이가 있다면, 어디서 생기는가?</b><br>단위가격·원료·유통 자료를 확보할 수 있을 때 진행</div></div><div class="scenario-step"><span>제목 후보</span><div><div class="option">A　PB 과자와 브랜드 과자의 가격·원료 비교</div><div class="option alt">B　PB 과자와 브랜드 과자, 가격이 다른 이유는?</div></div></div><div class="scenario-step"><span>검증·결정</span><div>가능하면 같은 영상의 제목만 무작위 비교<br>클릭률(노출 중 클릭 비율)·평균 시청시간<br>7일·28일 조회수를 같은 기간에 기록<br><b>반복 확인 후 유지·수정 · 자료가 없으면 기획 보류</b></div></div><p class="note">B는 비교 후보입니다. 이 기획과 두 제목의 성과는 아직 측정하지 않았습니다.</p></div></div>',
 '가상의 생활·소비 정보 기획입니다. PB는 유통사 자체브랜드입니다. 실제 PB영상을 참고했지만 새 기획이나 새 제목의 성과를 이 데이터에서 관찰한 것은 아닙니다. 내 독자에게 필요한 질문인지, 단위가격·원료·유통 자료로 실제 가격 차이를 설명할 수 있는지 확인합니다. 답할 수 없으면 질문을 수정하거나 보류합니다. 같은 취재 내용의 A는 정보 나열, B는 이유를 예고하는 제목으로 비교 후보를 하나 더 만듭니다. 가능한 환경에서는 같은 영상 제목을 무작위 비교하고, 제목·썸네일이 보인 횟수 중 클릭한 비율인 클릭률과 평균 시청시간을 함께 봅니다.7일·28일 조회수도 기록합니다. 이런 지표는 현재 CSV에 없으며 추가 수집 계획입니다. 무작위 비교가 불가능하면 탐색 기록에 한정하고 여러 편에서 반복되는지 봅니다.\n전환: 이 연구가 남긴 것은 확정된 성공 공식보다 다음 검증의 출발점입니다.',cls='planning-slide')
film='<div class="filmstrip">'+''.join('<div>'+video(v,meta=False)+f'<div class="video-meta">{E(V[v]["channel"])}</div></div>' for v in cover_ids)+'</div>'
add('다음 기획에서 검증할 주제와 제목의 단서를 찾았습니다','<h1>다음 기획에서 검증할<br><em>주제와 제목의 단서를 찾았습니다.</em></h1><p class="closing-copy">주제는 내 시청자와 취재 가능성으로 좁히고,<br>실제로 답할 수 있는 ‘이유’ 질문을 제목 후보로 시험합니다.</p><div class="limits">아직 분리하지 못한 것: 노출·썸네일·내용·포맷·시기·제목 수정 이력<br>5개 채널의 관찰 자료입니다. 인과효과나 새 채널의 미래 성과를 뜻하지 않습니다.</div>'+film+'<div class="resource-links"><a href="appendix.html">상세 부록</a><a href="image_sources.md">이미지 출처</a><a href="speaker_notes.md">발표 노트</a><a href="qa_report.md">QA 기록</a><a href="'+BASE+'versions/v4/news-topics-v4.pdf">V4 PDF</a></div>',
 '무엇을 확인했는가: 주제별 상위권 비중과 제목 단어 집단의 비중이 채널마다 다르게 관찰됐습니다. 무엇을 아직 모르는가: 이 차이가 제목 자체, 내용, 썸네일, 시리즈, 시점, 노출, 기존 구독층 때문인지 분리하지 못했습니다. 다음 기획에서 바꿀 것은 내 시청자에게 필요한 주제 후보를 고르는 과정과, 취재로 답할 수 있는 이유 질문을 제목 비교 후보로 만드는 과정입니다. 특정 단어를 넣으면 조회수가 오른다는 성공 공식은 아닙니다. 상세 부록에는 전체 40셀, 제목 특징 6개, 사전, 방법과 한계, 재현 코드, 이미지 출처를 공개했습니다.\n질의응답: 상위권 비중의 분모, 제목과 썸네일의 차이, 내 채널에서 가능한 검증 방식에 대해 이야기할 수 있습니다.',cls='dark closing',custom=True)

assert len(slides)==15
parts=['<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="방송사 뉴미디어 5채널의 1680개 영상에서 주제와 제목의 기획 단서를 찾는 V4 최종 발표"><title>다음 영상의 주제와 제목 | V4 최종본</title><link rel="stylesheet" href="style.css?v=4"><script src="assets/anime.min.js" defer></script><script src="deck.js?v=4" defer></script></head><body><main id="stage" data-width="1920" data-height="1080" aria-label="V4 발표 슬라이드">']
for i,s in enumerate(slides):
 parts += [f'<section class="slide {s["cls"]}{" active" if i==0 else ""}" id="slide-{i+1}" aria-label="슬라이드 {i+1}" aria-hidden="{"false" if i==0 else "true"}">']
 if s['eyebrow']:parts.append('<div class="eyebrow">'+E(s['eyebrow'])+'</div>')
 if not s['custom']:parts.append('<h1>'+E(s['title'])+'</h1>')
 parts.append('<div class="body">'+s['body']+'</div>')
 if s['foot']:parts.append('<footer class="foot">'+E(s['foot'])+'</footer>')
 parts.append(f'<span class="slidenum">{i+1:02} / 15</span></section>')
parts.append('</main><nav class="controls" aria-label="발표 조작"><button id="prev" aria-label="이전 슬라이드">←</button><span id="position" aria-live="polite"></span><button id="next" aria-label="다음 슬라이드">→</button><span class="hint">Space 이동</span><button id="toc">목차</button><button id="notes" aria-pressed="false">노트</button><button id="fullscreen">전체화면</button><a href="'+BASE+'versions/v4/news-topics-v4.pdf">PDF</a><a href="appendix.html" target="_blank" rel="noopener">부록</a></nav><div class="progress"></div><aside class="notes" id="notes-pane" aria-label="발표 노트"><button class="close" aria-label="노트 닫기">×</button><h2></h2><div class="note-text"></div></aside><div class="overview" id="overview"><button aria-label="목차 닫기">×</button><h2>발표 목차 · V4 최종본</h2><div class="toc"></div></div><div class="landscape-tip">가로 화면에서 더 크게 볼 수 있습니다</div><div class="sr" id="announcer" aria-live="polite"></div><script type="application/json" id="slide-meta">'+json.dumps([{'title':s['title'],'notes':s['notes']} for s in slides],ensure_ascii=False).replace('</','<\\/')+'</script></body></html>')
(R/'index.html').write_text('\n'.join(parts),encoding='utf-8')
shutil.copy2(R/'v4_style.css',R/'style.css');shutil.copy2(R/'v4_deck.js',R/'deck.js')
(R/'speaker_notes.md').write_text('# V4 발표 노트\n\n방향키/Space로 이동, N으로 노트, O로 목차, F로 전체화면. 수치는 2026-10-18 누적 조회수 기준이다.\n\n'+'\n\n'.join('## '+str(i+1)+'. '+s['title']+'\n\n'+s['notes'] for i,s in enumerate(slides)),encoding='utf-8')
(R/'storyboard.json').write_text(json.dumps([{'slide':i+1,'title':s['title'],'notes':s['notes']} for i,s in enumerate(slides)],ensure_ascii=False,indent=2),encoding='utf-8')

# Separate, readable detail page: the dense tables no longer extend the talk.
def table(headers,rows):return '<div class="table-scroll"><table><thead><tr>'+''.join('<th>'+E(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
append_css='''@font-face{font-family:Pretendard;src:url(assets/PretendardVariable.woff2)}*{box-sizing:border-box}body{margin:0;background:#f6f7fa;color:#152030;font:20px/1.7 Pretendard,"Malgun Gothic",sans-serif}main{max-width:1450px;margin:auto;padding:70px 45px}h1{font-size:52px;line-height:1.25}h2{font-size:34px;margin-top:65px;padding-top:28px;border-top:2px solid #152030}h3{font-size:25px}a{color:#234e8c;text-underline-offset:4px}nav{display:flex;gap:25px;flex-wrap:wrap}table{width:100%;border-collapse:collapse;font-size:19px;white-space:nowrap}th,td{padding:15px 13px;border-bottom:1px solid #ccd4de;text-align:left}th{background:#e5ebf2}td:first-child{font-weight:600}.table-scroll{overflow:auto}.notes{padding:25px;background:#e6edf4}.gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:30px}.gallery img{width:100%;aspect-ratio:16/9;object-fit:contain}.gallery p{font-size:18px;line-height:1.5}.gallery h3{font-size:21px}code{background:#e5ebf2;padding:3px 7px}details{margin:25px 0}summary{font-size:24px;font-weight:650;cursor:pointer}.dictionary{display:grid;grid-template-columns:1fr 1fr;gap:20px 45px}.dictionary p{font-size:19px}.profile-row{display:flex;gap:30px;flex-wrap:wrap}.profile-row img{width:90px;height:90px;object-fit:contain;border-radius:50%;display:block}.profile-row a{font-size:18px}@media(max-width:750px){main{padding:30px 20px}h1{font-size:36px}.gallery,.dictionary{grid-template-columns:1fr}table{font-size:17px}}'''
append_css+='main{overflow-wrap:anywhere}.gallery{grid-template-columns:repeat(3,minmax(0,1fr))}.gallery img{height:auto}@media(max-width:750px){.gallery{grid-template-columns:1fr}}'
ap=['<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V4 상세 부록 · 주제와 제목의 단서</title><style>'+append_css+'</style></head><body><main><a href="index.html#15">← 발표로 돌아가기</a><h1>V4 상세 부록</h1><p>발표 본문은 15장으로 마칩니다. 전체 표·분류 규칙·출처와 해석의 한계는 여기에서 확인할 수 있습니다.</p><nav><a href="#metrics">지표</a><a href="#topics">주제 전체표</a><a href="#titles">제목 전체표</a><a href="#rules">사전</a><a href="#images">영상 출처</a><a href="#files">재현 자료</a></nav>']
ap+=['<h2 id="metrics">자료와 지표</h2><div class="notes">2025.01.01–12.31 업로드된 일반 영상 1,680편. Firecrawl 수집 당시 누적 조회수(2026.10.18). 쇼츠·라이브 제외, URL 중복 0·원본 7열 결측 0. 삭제·비공개 등 현재 접근할 수 없는 영상은 범위 밖입니다.</div><p><b>원본 7열:</b> 채널명, 영상 제목, 영상 URL, 업로드 날짜, 조회수, 영상 길이, 영상 설명. video_id는 URL에서 파생한 값이며 collected_at/content_format은 원본 컬럼으로 가정하지 않았습니다.</p>']
ap.append(table(['채널','방송사','영상 수','상위권 수','채널 상위권 최소 조회수'],[[E(c),E(P[c]['network']),S[c]['n'],S[c]['hits'],f'{S[c]["cutoff"]:,}'] for c in CH]))
ap+=['<p><b>상위권:</b> 채널별 조회수순 상위 25%. n×0.25를 올림하고 동률은 원본 행 순서를 유지합니다. 전체 422/1,680편(25.1%).</p><p><b>상위권 비중:</b> 해당 주제·제목 집단 중 채널 내부 상위권 수/해당 집단 수. 조회수 증가율이나 미래 성공확률이 아닙니다. 비교 기준 약 25%와 채널별 반올림 차이를 구분합니다.</p><h2 id="topics">5개 채널 × 8개 주제 태그</h2><p>반복 안내 줄을 제거한 설명+제목에 단어 사전을 적용했습니다. 복수 태그 723편, 태그 없음 282편. 국가명·다의어·홍보 잔여로 잘못 붙은 태그가 있을 수 있습니다. 행 합계는 100%가 아닙니다.</p>']
ap.append(table(['채널','주제 태그','태그 수/채널 n','제작 비중','상위권/태그 n','상위권 비중','제목만 태그: 상위권/n'],[[E(c),E(t),f'{HEAT[c,t]["tagged"]["n"]}/{S[c]["n"]}',percent(HEAT[c,t]['upload_share'],1),f'{T[c,t]["with"]["hits"]}/{T[c,t]["with"]["n"]}',percent(T[c,t]['with']['rate'],1) if T[c,t]['with']['n']>=10 else 'n<10 · 비교 유보',f'{T[c,t]["title_only"]["hits"]}/{T[c,t]["title_only"]["n"]}'] for c in CH for t in TOP]))
ap+=['<p>본문 음식 사례는 해당 태그에서 표본이 큰 두 채널(14F154편·스브스뉴스 39편)을 선택했습니다. 전체 40셀을 함께 공개하며 가장 좋은 채널을 판정한 것이 아닙니다. 제목만 태그한 민감도와 9개 실제 사례 수동 검토는 <a href="analysis_review.md">분류·사례 검토 기록</a>을 참조하세요.</p><h2 id="titles">제목 표현: 전체 결과</h2><p><b>이유·원리를 예고하는 5개 단어:</b> 왜|이유|비밀|정체|원리 정규식. 언어 접두와 알려진 끝 채널 표기만 제거하고 시리즈명은 유지했습니다. 문자열 포함 여부이며 의미 판정, 제목 품질 평가, 썸네일 텍스트 분석은 아닙니다. ‘…일까?’라도 다섯 단어가 없으면 미포함입니다.</p>']
name=lambda x:'5개 단어 포함' if x=='설명형 표현' else x
ap.append(table(['특징','미포함:상위권/n','비중','포함:상위권/n','비중','조건 고려 모형 계수'],[[E(name(f)),f'{F[f]["without"]["hits"]}/{F[f]["without"]["n"]}',percent(F[f]['without']['rate'],1),f'{F[f]["with"]["hits"]}/{F[f]["with"]["n"]}',percent(F[f]['with']['rate'],1),f'{D["models"]["adjusted"][f]:+.1f}%p'] for f in D['feature_patterns']]))
ap.append(table(['채널','미포함:상위권/n','비중','포함:상위권/n','비중'],[[E(c),f'{FC[c,"설명형 표현"]["without"]["hits"]}/{FC[c,"설명형 표현"]["without"]["n"]}',percent(FC[c,'설명형 표현']['without']['rate'],1),f'{FC[c,"설명형 표현"]["with"]["hits"]}/{FC[c,"설명형 표현"]["with"]["n"]}',percent(FC[c,'설명형 표현']['with']['rate'],1)] for c in CH]))
ap+=['<details><summary>보조 모형과 해석의 한계</summary><p>V2/V3의 선형확률모형 결과를 그대로 유지했습니다. 상위권 여부 0/1을 채널, 게시 월, log2영상길이와 제곱, 제목 글자 수/10과 제곱, 주제 태그 8개, 제목 특징 6개로 설명한 계수입니다. 5개 단어의 기본 계수는+11.2%p, 주요 시리즈 표기를 추가하면+8.9%p입니다. 관찰상 연관성의 요약이며 단어를 넣어서 발생한 인과효과가 아닙니다. 유의성·외부 예측 성능을 검증했다는 주장을 하지 않습니다. 전체 사양·민감도는JSON과코드로 확인할 수 있습니다.</p><p>노출·썸네일·콘텐츠 내용·시리즈·형식·누적 관찰 기간·제목 수정 이력을 완전히 분리하지 못합니다. 조회수는 같은 수집 날짜의 누적값이어서 게시 시점에 따른 누적 기간 차이가 남습니다. 새 채널에 그대로 적용될지도 알 수 없습니다.</p></details><h2 id="rules">고정한 주제 사전과 제목 규칙</h2><p>V1에서 탐색하며 만든 주제 사전을 이후 고정했습니다. 성과에 유리하게 단어를 재조정하지 않았습니다. 사전 자체가 검증된 정답은 아닙니다.</p><div class="dictionary">']
for t,words in D['topics'].items():ap.append('<div><h3>'+E(t)+'</h3><p>'+E(' · '.join(words))+'</p></div>')
ap.append('</div>'+table(['제목 특징','정규식'],[[E(name(f)),'<code>'+E(pattern)+'</code>'] for f,pattern in D['feature_patterns'].items()]))
ap+=['<h2 id="images">실제 채널·영상과 이미지 출처</h2><p>공식 채널 페이지의 프로필 메타데이터와 영상URL에서 파생한ID를 기존 Firecrawl 원본의videoId/channelId/title로 대조했습니다. 프로필 5개·썸네일 9개 모두 응답과 해상도를 확인했습니다. 썸네일은 모두 1280×720입니다. 이미지 권리는 각 제작사에 있습니다. 분석·비평의 사례 식별을 위한 출처 표시이며 자유 이용 라이선스를 주장하지 않습니다.</p><div class="profile-row">'+''.join('<a href="'+E(P[c]['url'])+'" target="_blank" rel="noopener">'+profile(c)+E(c)+'</a>' for c in CH)+'</div><p><a href="image_sources.md">전체 이미지 출처 목록</a> · <a href="image_sources.json">검증 메타데이터·SHA256</a></p><div class="gallery">']
for vid in V:ap.append('<article><h3>'+E(V[vid]['channel'])+'</h3>'+video(vid,title=V[vid]['title'])+'<p>영상ID(URL에서 파생): '+vid+'<br>수집 당시 조회수 기준일:2026.10.18<br><a href="'+E(V[vid]['image_url'])+'">공식 썸네일 원본</a></p></article>')
ap+=['</div><h2 id="files">재현 자료·수정·QA</h2><p><a href="source.csv">Firecrawl 수집 원본CSV</a> · <a href="collection_report.md">수집 보고서</a> · <a href="research_data.json">기존 전체 집계·영상별 플래그</a> · <a href="v4_metrics.json">추가 집계·분류 검토용 원문</a></p><p><a href="analysis.py">기존 재현 분석 코드</a> → <a href="analysis_review.py">V4 독립 검산·추가 집계</a> → <a href="build_v4.py">발표 HTML 생성 코드</a></p><p><code>python analysis.py</code> 다음 <code>python analysis_review.py</code>, <code>python build_v4.py</code> 순서로 같은 폴더의자료를 사용합니다. pandas/numpy가 필요합니다.</p><p>원본 SHA256: <code>'+E(D['source_sha256'])+'</code></p><p><a href="improvement_plan.md">슬라이드 구성안</a> · <a href="speaker_notes.md">발표 노트</a> · <a href="revision_log.md">V3 대비 수정 기록</a> · <a href="qa_report.md">QA 검증 기록</a> · <a href="'+BASE+'versions/v4/news-topics-v4.pdf">15페이지PDF</a> · <a href="'+BASE+'versions/">V1~V4 버전 기록</a></p></main></body></html>']
(R/'appendix.html').write_text('\n'.join(ap),encoding='utf-8')
print('Built V4:15 main slides, separate appendix, nine real videos, five official profiles, speaker notes.')
