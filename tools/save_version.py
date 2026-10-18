"""Save an immutable HTML snapshot and matching slide PDF.
Usage: python tools/save_version.py v2
Requires: playwright (Chromium), pymupdf.
"""
from pathlib import Path
import sys,json,hashlib,shutil,datetime,subprocess
from playwright.sync_api import sync_playwright
import pymupdf as fitz
ROOT=Path(__file__).resolve().parents[1]
version=sys.argv[1] if len(sys.argv)>1 else ''
if not version.startswith('v') or not version[1:].isdigit():raise SystemExit('Use a version such as v1 or v2')
dest=ROOT/'versions'/version
if dest.exists() and ('--resume' not in sys.argv or (dest/'manifest.json').exists()):raise SystemExit(f'Refusing to overwrite existing version: {dest}')
files=['index.html','style.css','deck.js','research_data.json','source.csv','analysis.py','collection_report.md','README.md']
for name in files:
 if not (ROOT/name).is_file():raise SystemExit(f'Missing {name}')
dest.mkdir(parents=True,exist_ok=True)
for name in files:
 if not (dest/name).exists():shutil.copy2(ROOT/name,dest/name)
if not (dest/'assets').exists():shutil.copytree(ROOT/'assets',dest/'assets')
try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
except subprocess.SubprocessError:commit=None
pdf=dest/f'news-topics-{version}.pdf'
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 page=browser.new_page(viewport={'width':1600,'height':950},reduced_motion='reduce')
 page.goto((dest/'index.html').as_uri());page.wait_for_function('typeof go === "function"')
 page.evaluate('go(0)');page.evaluate('document.fonts.ready');count=page.locator('section.slide').count()
 page.evaluate('base=>document.querySelectorAll("a[href]").forEach(a=>{if(a.href.startsWith("file:"))a.href=base+a.getAttribute("href");})', 'https://mschoooo.github.io/news-topic-views-2025/versions/'+version+'/')
 page.add_style_tag(content='''@media print {
 @page { size:1600px 900px; margin:0; }
 html,body {width:1600px!important;height:auto!important;overflow:visible!important;margin:0!important;background:#f8f7f2!important;}
 #stage {position:static!important;width:1600px!important;height:auto!important;transform:none!important;}
 section.slide {position:relative!important;display:flex!important;flex-direction:column!important;width:1600px!important;height:900px!important;break-before:auto!important;break-after:page!important;page-break-after:always!important;break-inside:avoid!important;}
 section.slide:last-child {break-after:auto!important;page-break-after:auto!important;}
 .slide h1,.slide .body,.slide .eyebrow {opacity:1!important;transform:none!important;}
 .controls,.notes,.overview,.progress,.sr {display:none!important;}
 * {-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important;}
 }''')
 page.pdf(path=str(pdf),width='1600px',height='900px',print_background=True,prefer_css_page_size=True,margin={'top':'0','bottom':'0','left':'0','right':'0'},display_header_footer=False)
 browser.close()
doc=fitz.open(pdf)
assert len(doc)==count,(len(doc),count)
for page in doc:
 assert abs(page.rect.width/page.rect.height-16/9)<.001
 assert len(page.get_text().strip())>20
manifest={'version':version,'saved_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'source_commit':commit,'slides':count,'pdf':pdf.name,'pdf_pages':len(doc),'files':{str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.rglob('*')) if p.is_file()}}
(dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'version':version,'pdf':str(pdf),'pages':len(doc),'source_commit':commit},ensure_ascii=False))
