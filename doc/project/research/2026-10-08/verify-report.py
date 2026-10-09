
import json,re,hashlib,datetime
from pathlib import Path
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
root=Path(r'D:\Rigs of Rods\rigs-of-rods-trials')
research=root/'doc/project/research/2026-10-08'
report=root/'doc/project/reports/platform-evaluation-2026-10-08.html'
evidence=Path(r'D:\Rigs of Rods')/('platform-evaluation-'+datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S'))
evidence.mkdir()
refs=json.loads((research/'references.json').read_text(encoding='utf-8'))
problems=[]
source_refs=[]
for ref in refs:
 if ref['type']=='source':
  source=root/ref['file'];n=len(source.read_text(encoding='utf-8-sig').splitlines())
  valid=1<=ref['start']<=ref['end']<=n
  source_refs.append({'id':ref['id'],'file':ref['file'],'start':ref['start'],'end':ref['end'],'lineCount':n,'valid':valid})
  if not valid:problems.append('Invalid source anchor '+ref['id'])
class Links(HTMLParser):
 def __init__(self):super().__init__();self.hrefs=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a' and 'href' in a:self.hrefs.append(a['href'])
parser=Links();parser.feed(report.read_text(encoding='utf-8'))
local=[]
from urllib.parse import unquote,urlsplit
for href in parser.hrefs:
 if href.startswith('#'):
  valid=unquote(href[1:]) in parser.ids
  if not valid:problems.append('Missing anchor '+href)
 elif not urlsplit(href).scheme:
  target=(report.parent/unquote(href.split('#')[0])).resolve();valid=target.exists()
  local.append({'href':href,'exists':valid})
  if not valid:problems.append('Missing local file '+str(target))
if len(parser.ids)!=len(set(parser.ids)):problems.append('Duplicate HTML ids')
result={'researchDate':'2026-10-08','report':str(report),'captureDirectory':str(evidence),'sourceReferenceChecks':source_refs,'localLinks':local,'problems':problems,'browserChecks':{},'screenshots':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 context=browser.new_context(viewport={'width':1440,'height':1000},device_scale_factor=1)
 page=context.new_page();errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda req:requests.append(req.url))
 page.goto(report.as_uri(),wait_until='load')
 page.emulate_media(reduced_motion='reduce')
 checks={'pageErrors':errors,'sectionCount':page.locator('article h2').count(),'navLinks':page.locator('nav a').count(),'svgCount':page.locator('svg[role="img"]').count(),'tableCount':page.locator('article table').count()}
 def overflow():
  return page.evaluate('({width:innerWidth,documentWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth})')
 checks['desktopOverflow']=overflow()
 calc={key:page.locator('#calc-'+key).inner_text() for key in ('momentum','energy','force')}
 checks['calculatorDefault']=calc
 if calc!={'momentum':'10,000','energy':'50,000','force':'100,000'}:problems.append('Default calculator result')
 page.locator('#calc-speed').fill('20')
 checks['calculatorSpeed20']={key:page.locator('#calc-'+key).inner_text() for key in ('momentum','energy','force')}
 if checks['calculatorSpeed20']!={'momentum':'20,000','energy':'200,000','force':'200,000'}:problems.append('Calculator speed20 result')
 page.locator('#calc-stop').fill('0')
 checks['calculatorInvalid']=page.locator('#calc-warning').is_visible() and page.locator('#calc-force').inner_text()=='\u2014'
 if not checks['calculatorInvalid']:problems.append('Calculator invalid input')
 page.locator('#calc-stop').fill('100');page.locator('#calc-speed').fill('10')
 page.locator('#coverage-search').fill('wind')
 checks['filterWind']=page.locator('#coverage-table tbody tr:visible').count()
 checks['filterWindRows']=page.locator('#coverage-table tbody tr:visible').all_inner_texts()
 if checks['filterWind']!=1:problems.append('Wind filter')
 page.locator('#coverage-search').fill('');page.locator('#coverage-status').select_option(label='Extend')
 checks['filterExtend']=page.locator('#coverage-table tbody tr:visible').count()
 if not all('extend' in row.lower() for row in page.locator('#coverage-table tbody tr:visible').all_inner_texts()):problems.append('Extend filter rows')
 page.locator('#coverage-search').fill('nonexistent dimension xyz')
 checks['emptyFilter']=page.locator('#coverage-empty').is_visible()
 if not checks['emptyFilter']:problems.append('Empty filter')
 page.locator('#coverage-search').fill('');page.locator('#coverage-status').select_option('all')
 checks['coverageRows']=page.locator('#coverage-table tbody tr:visible').count()
 def capture(name,target=None):
  if target:
   locator=page.locator(target)
   if target.endswith('-title'):locator=locator.locator('..')
   locator.scroll_into_view_if_needed()
  else:page.evaluate('scrollTo(0,0)')
  target_path=evidence/name;page.screenshot(path=str(target_path),animations='disabled')
  result['screenshots'].append(str(target_path))
 capture('desktop-overview.png')
 capture('platform-map.png','#platform-title')
 capture('sampling-and-telemetry.png','#timing-title')
 capture('energy-ledger.png','#energy-title')
 capture('trial-coverage.png','#coverage-search')
 capture('trial-lifecycle.png','#lifecycle-title')
 checks['accessibleDiagrams']=page.locator('svg[role="img"]').evaluate_all('(els)=>els.every(e=>e.querySelector("title")&&e.querySelector("desc")&&e.getAttribute("aria-labelledby"))')
 checks['externalRequests']=[u for u in requests if not u.startswith('file:')]
 page.set_viewport_size({'width':390,'height':844})
 capture('mobile-overview.png')
 checks['mobileOverflow']=overflow()
 page.locator('#coverage-search').scroll_into_view_if_needed();checks['mobileCoverageOverflow']=overflow()
 capture('mobile-coverage.png','#coverage-search')
 page.locator('#calc-mass').scroll_into_view_if_needed();checks['mobileCalculatorOverflow']=overflow()
 checks['browserVersion']=browser.version;checks['browserExecutable']=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
 for name in ('desktopOverflow','mobileOverflow','mobileCoverageOverflow','mobileCalculatorOverflow'):
  if checks[name]['documentWidth']>checks[name]['width']:problems.append(name)
 if errors:problems.extend(errors)
 if checks['externalRequests']:problems.append('External requests')
 if checks['sectionCount']!=12 or checks['navLinks']!=12 or checks['svgCount']!=4:problems.append('Report section/diagram count')
 result['browserChecks']=checks
 browser.close()
result['reportSha256']=hashlib.sha256(report.read_bytes()).hexdigest()
result['allChecksPassed']=not problems
result['verificationScope']='Static source anchors, local HTML links, report UI, formula examples and responsiveness. No native simulator run or physical accuracy validation.'
(evidence/'report-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(research/'report-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'allChecksPassed':not problems,'problems':problems,'evidence':str(evidence),'browserChecks':result['browserChecks'],'sourceRefs':len(source_refs),'localLinks':len(local)},indent=2))
raise SystemExit(0 if not problems else 1)
