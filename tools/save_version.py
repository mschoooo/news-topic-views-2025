"""Immutable HTML snapshot and matching PDF. Preview does not create an archive.
Usage: python tools/save_version.py v4 [--preview]
Requires: playwright (Chromium), pymupdf.
"""
from pathlib import Path
import sys,json,hashlib,shutil,datetime,subprocess
from playwright.sync_api import sync_playwright
import pymupdf as fitz

ROOT=Path(__file__).resolve().parents[1]
version=sys.argv[1] if len(sys.argv)>1 else ''
if not version.startswith('v') or not version[1:].isdigit():raise SystemExit('Use a version such as v4')
preview='--preview' in sys.argv
dest=ROOT/'versions'/version
if not preview and dest.exists() and ('--resume' not in sys.argv or (dest/'manifest.json').exists()):
 raise SystemExit(f'Refusing to overwrite existing version: {dest}')
files=['index.html','style.css','deck.js','research_data.json','source.csv','analysis.py','collection_report.md','README.md']
optional=['improvement_plan.md','appendix.html','analysis_review.py','analysis_review.md','v4_metrics.json','build_v4.py','v4_style.css','v4_deck.js','image_sources.json','image_sources.md','speaker_notes.md','storyboard.json','revision_log.md','qa_report.md']
optional += ['build_v5.py','v5_style.css','v5_deck.js']
optional += ['build_v6.py','v6_style.css','v6_deck.js','v6_revision_plan.md','v6_qa_results.json']
files += [n for n in optional if (ROOT/n).is_file()]
for name in files:
 if not (ROOT/name).is_file():raise SystemExit(f'Missing {name}')
if not preview:
 dest.mkdir(parents=True,exist_ok=True)
 for name in files:
  if not (dest/name).exists():shutil.copy2(ROOT/name,dest/name)
 if not (dest/'assets').exists():shutil.copytree(ROOT/'assets',dest/'assets')
try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
except subprocess.SubprocessError:commit=None
pdf=(ROOT.parent/'output/pdf'/f'news-topics-{version}-preview.pdf') if preview else dest/f'news-topics-{version}.pdf'
pdf.parent.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 page=browser.new_page(viewport={'width':1920,'height':1132},reduced_motion='reduce')
 page.goto(((ROOT if preview else dest)/'index.html').as_uri())
 page.wait_for_function('typeof go === "function"');page.evaluate('go(0)');page.evaluate('document.fonts.ready')
 page.wait_for_function('Array.from(document.images).every(i=>i.complete)')
 assert page.evaluate('Array.from(document.images).every(i=>i.naturalWidth>0)'), 'Broken image in deck'
 count=page.locator('section.slide').count()
 width,height=page.locator('#stage').evaluate('(s)=>[Number(s.dataset.width)||1600,Number(s.dataset.height)||900]')
 page.evaluate('window.finishAllMotion?.()')
 page.evaluate('base=>document.querySelectorAll("a[href]").forEach(a=>{if(a.href.startsWith("file:"))a.href=base+a.getAttribute("href");})', 'https://mschoooo.github.io/news-topic-views-2025/versions/'+version+'/')
 css='''@media print {
 @page { size:WIDTHpx HEIGHTpx; margin:0; }
 html,body {width:WIDTHpx!important;height:auto!important;overflow:visible!important;margin:0!important;background:#101923!important;}
 #stage {position:static!important;width:WIDTHpx!important;height:auto!important;transform:none!important;}
 section.slide {position:relative!important;display:flex!important;flex-direction:column!important;width:WIDTHpx!important;height:HEIGHTpx!important;break-before:auto!important;break-after:page!important;page-break-after:always!important;break-inside:avoid!important;}
 section.slide:last-child {break-after:auto!important;page-break-after:auto!important;}
 .slide h1,.slide .body,.slide .eyebrow,.slide .section-label,.reveal,[data-seq] {opacity:1!important;transform:none!important;}
 .controls,.notes,.overview,.progress,.sr,.landscape-tip {display:none!important;}
 * {-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important;}
 }'''.replace('WIDTH',str(width)).replace('HEIGHT',str(height))
 page.add_style_tag(content=css)
 page.pdf(path=str(pdf),width=f'{width}px',height=f'{height}px',print_background=True,prefer_css_page_size=True,margin={'top':'0','bottom':'0','left':'0','right':'0'},display_header_footer=False)
 browser.close()
doc=fitz.open(pdf)
assert len(doc)==count,(len(doc),count)
for page in doc:
 assert abs(page.rect.width/page.rect.height-16/9)<.001
 assert len(page.get_text().strip())>20
if not preview:
 manifest={'version':version,'saved_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'source_commit':commit,'canvas':{'width':width,'height':height},'slides':count,'pdf':pdf.name,'pdf_pages':len(doc),'files':{p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.rglob('*')) if p.is_file()}}
 (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'version':version,'preview':preview,'pdf':str(pdf),'pages':len(doc),'canvas':[width,height],'source_commit':commit},ensure_ascii=False))
