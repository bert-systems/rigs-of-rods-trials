
import json,hashlib,re,datetime
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
from playwright.sync_api import sync_playwright
root=Path(r'D:\Rigs of Rods\rigs-of-rods-trials')
records=root/'doc/project/design/2026-10-08'
report=root/'doc/project/reports/trial-architecture-options-2026-10-08.html'
captures=root.parent/('trial-architecture-evaluation-'+datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S'));captures.mkdir()
refs=json.loads((records/'references.json').read_text())
md=(root/'doc/project/design/trial-platform-architecture-options.md').read_text(encoding='utf-8')
problems=[];source_checks=[]
for ref in refs:
 if ref['url'] not in md:problems.append('Missing reference '+ref['id'])
 if ref['type']=='source':
  source=root/ref['file'];lines=len(source.read_text(encoding='utf-8-sig').splitlines());valid=1<=ref['start']<=ref['end']<=lines
  source_checks.append({'id':ref['id'],'file':ref['file'],'start':ref['start'],'end':ref['end'],'lines':lines,'valid':valid})
  if not valid:problems.append('Invalid source range '+ref['id'])
class Links(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a' and 'href' in a:self.links.append(a['href'])
parser=Links();parser.feed(report.read_text(encoding='utf-8'))
if len(parser.ids)!=len(set(parser.ids)):problems.append('Duplicate report IDs')
local=[]
for href in parser.links:
 if href.startswith('#'):
  if href[1:] not in parser.ids:problems.append('Missing report anchor '+href)
 elif not urlsplit(href).scheme:
  resolved=(report.parent/unquote(href.split('#')[0])).resolve();local.append({'href':href,'exists':resolved.exists()})
  if not resolved.exists():problems.append('Missing local HTML target '+href)
result={'evaluationDate':'2026-10-08','report':str(report),'captureDirectory':str(captures),'sourceChecks':source_checks,'localLinks':local,'browserChecks':{},'screenshots':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda q:requests.append(q.url))
 page.goto(report.as_uri(),wait_until='load');page.emulate_media(reduced_motion='reduce')
 checks={'sections':page.locator('article h2').count(),'navLinks':page.locator('nav a').count(),'tables':page.locator('article table').count(),'diagrams':page.locator('svg[role=img]').count()}
 def overflow():return page.evaluate('({width:innerWidth,documentWidth:document.documentElement.scrollWidth})')
 def output():return {k:page.locator('#budget-'+k).inner_text() for k in ('rate','total','lag')}
 checks['desktopOverflow']=overflow();checks['calculatorDefault']=output()
 if checks['calculatorDefault']!={'rate':'72','total':'43.2','lag':'7.46'}:problems.append('Default payload calculation')
 page.locator('#budget-channels').fill('8');checks['calculatorEightChannels']=output()
 if checks['calculatorEightChannels']!={'rate':'264','total':'158.4','lag':'2.03'}:problems.append('Detailed-channel payload calculation')
 page.locator('#budget-hz').fill('2500');checks['invalidRate']=page.locator('#budget-warning').is_visible() and page.locator('#budget-rate').inner_text()=='\u2014'
 if not checks['invalidRate']:problems.append('Invalid calculator rate')
 page.locator('#budget-hz').fill('200');page.locator('#budget-channels').fill('0');checks['mediumRate']=output()
 if checks['mediumRate']['rate']!='7.2' or checks['mediumRate']['total']!='4.32':problems.append('Medium payload calculation')
 page.locator('#budget-hz').fill('2000')
 def shot(name,target=None):
  if target:
   locator=page.locator(target)
   if target.endswith('-title'):locator=locator.locator('..')
   locator.scroll_into_view_if_needed()
  else:page.evaluate('scrollTo(0,0)')
  dest=captures/name;page.screenshot(path=str(dest),animations='disabled');result['screenshots'].append(str(dest))
 shot('desktop-overview.png')
 shot('shared-architecture.png','#architecture-title')
 shot('solver-epochs.png','#epochs-title')
 shot('environment-pipeline.png','#environment-title')
 shot('delivery-epics.png','#delivery-title')
 shot('capture-sizing.png','#budget-nodes')
 checks['accessibleDiagrams']=page.locator('svg[role=img]').evaluate_all('(els)=>els.every(e=>e.querySelector("title")&&e.querySelector("desc")&&e.getAttribute("aria-labelledby"))')
 page.set_viewport_size({'width':390,'height':844});shot('mobile-overview.png');checks['mobileOverflow']=overflow()
 shot('mobile-sizing.png','#budget-nodes');checks['mobileCalculatorOverflow']=overflow()
 checks['pageErrors']=errors;checks['externalRequests']=[x for x in requests if not x.startswith('file:')];checks['browserVersion']=browser.version
 if errors:problems.extend(errors)
 if checks['externalRequests']:problems.append('External requests')
 if (checks['sections'],checks['navLinks'],checks['tables'],checks['diagrams'])!=(14,14,14,4):problems.append('Section/table/diagram counts')
 for key in ('desktopOverflow','mobileOverflow','mobileCalculatorOverflow'):
  if checks[key]['documentWidth']>checks[key]['width']:problems.append(key)
 result['browserChecks']=checks;browser.close()
result['reportSha256']=hashlib.sha256(report.read_bytes()).hexdigest();result['problems']=problems;result['allChecksPassed']=not problems
result['scope']='Static local source/link references, report presentation and illustrative payload calculation only. No engine or physical accuracy tests.'
content=json.dumps(result,indent=2)+'\n';(records/'report-validation.json').write_text(content,encoding='utf-8');(captures/'report-validation.json').write_text(content,encoding='utf-8')
print(json.dumps({'allChecksPassed':not problems,'problems':problems,'captureDirectory':str(captures),'sourceRefs':len(source_checks),'localLinks':len(local),'checks':result['browserChecks']},indent=2))
raise SystemExit(0 if not problems else 1)
