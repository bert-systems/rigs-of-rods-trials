import datetime,hashlib,json,re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
from playwright.sync_api import sync_playwright

root=Path(r'D:\Rigs of Rods\rigs-of-rods-trials')
records=root/'doc/project/design/2026-10-08'
report=root/'doc/project/reports/trial-implementation-spec-2026-10-08.html'
source=root/'doc/project/design/trial-platform-implementation-spec.md'
captures=root.parent/('trial-implementation-review-'+datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S-%f'))
captures.mkdir()
problems=[]
class Links(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if 'id' in attrs:self.ids.append(attrs['id'])
  if tag=='a' and 'href' in attrs:self.links.append(attrs['href'])
parser=Links();parser.feed(report.read_text(encoding='utf-8'))
if len(parser.ids)!=len(set(parser.ids)):problems.append('Duplicate HTML IDs')
local=[]
for href in parser.links:
 if href.startswith('#'):
  if unquote(href[1:]) not in parser.ids:problems.append('Missing report anchor '+href)
 elif not urlsplit(href).scheme:
  resolved=(report.parent/unquote(href.split('#')[0])).resolve()
  local.append({'href':href,'exists':resolved.exists()})
  if not resolved.exists():problems.append('Missing HTML local target '+href)
md=source.read_text(encoding='utf-8')
md_links=[]
for href in re.findall(r'(?<!!)\[[^\]\n]+\]\(([^)]+)\)',md):
 if not urlsplit(href).scheme and not href.startswith('#'):
  target=(source.parent/unquote(href.split('#')[0])).resolve()
  md_links.append({'href':href,'exists':target.exists()})
  if not target.exists():problems.append('Missing Markdown target '+href)
refs=json.loads((records/'references.json').read_text(encoding='utf-8'))
source_checks=[]
for ref in refs:
 if ref['type']=='source' and ref['url'] in md:
  lines=len((root/ref['file']).read_text(encoding='utf-8-sig').splitlines())
  valid=1<=ref['start']<=ref['end']<=lines
  source_checks.append({'id':ref['id'],'file':ref['file'],'start':ref['start'],'end':ref['end'],'lines':lines,'valid':valid})
  if not valid:problems.append('Source range '+ref['id'])
example=json.loads(re.search(r'~~~json\n(.*?)\n~~~',md,re.S).group(1))
if example['schemaVersion']!='proposal-0.1' or example['repeats']!=5:problems.append('Authoring example metadata')
payload=176*2000*4*(9+8*3)
if payload!=46464000 or payload*6!=278784000:problems.append('Calculated payload arithmetic')
result={'evaluationDate':'2026-10-08','sourceDocument':str(source),'report':str(report),'captureDirectory':str(captures),'sourceChecks':source_checks,'localHtmlLinks':local,'markdownLinks':md_links,'exampleJsonParsed':True,'calculatedPayloadBytesPerSimulatedSecond':payload,'browserChecks':{},'screenshots':[]}
expected={
 'complete':('Completed','Complete','Pending automated checks','Continue eligible independent trials'),
 'gap':('Running; may complete normally','Incomplete — required gap retained','Cannot pass','Continue eligible independent trials after finish'),
 'crash':('Failed — process exit','Partial / tail uncertainty assessed','No completed-trial pass','Continue eligible trials; manual retry is a new attempt'),
 'pause':('Paused — acknowledged boundary','Quality retained; no advancing physics ticks','Pending completion and checks','Active attempt retains its slot'),
 'storage':('Queued — preflight blocked','No attempt launched','Not evaluated','Hold new launches'),
 'failedcheck':('Completed','Complete','Failed scoped check','Continue eligible independent trials'),
 'disconnect':('Running under coordinator ownership','Native archive determines quality','Pending automated checks','Coordinator continues eligible queue')
}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=browser.new_page(viewport={'width':1440,'height':1000})
 errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda q:requests.append(q.url))
 page.goto(report.as_uri(),wait_until='load')
 page.emulate_media(reduced_motion='reduce')
 def overflow():return page.evaluate('({width:innerWidth,documentWidth:document.documentElement.scrollWidth})')
 checks={'sections':page.locator('article h2').count(),'navLinks':page.locator('nav a').count(),'tables':page.locator('article table').count(),'diagrams':page.locator('svg[role=img]').count(),'desktopOverflow':overflow(),'policyCases':{}}
 for choice,wanted in expected.items():
  page.select_option('#policy-case',choice)
  actual=tuple(page.locator('#policy-'+k).inner_text() for k in ('execution','capture','validation','queue'))
  valid=actual==wanted
  checks['policyCases'][choice]={'values':actual,'matchesPolicy':valid}
  if not valid:problems.append('Policy explorer '+choice)
 def shot(name,selector=None):
  if selector:page.locator(selector).scroll_into_view_if_needed()
  else:page.evaluate('scrollTo(0,0)')
  destination=captures/name
  page.screenshot(path=str(destination),animations='disabled')
  result['screenshots'].append(str(destination))
 page.select_option('#policy-case','gap')
 shot('desktop-overview.png')
 shot('selected-architecture.png','#implementation-boundaries')
 shot('capture-quality-policy.png','#quality-policy')
 shot('required-gap-explorer.png','#policy-explorer')
 shot('delivery-epics.png','#section-10')
 checks['accessibleDiagrams']=page.locator('svg[role=img]').evaluate_all('(els)=>els.every(e=>e.querySelector("title")&&e.querySelector("desc")&&e.getAttribute("aria-labelledby"))')
 page.set_viewport_size({'width':390,'height':844})
 shot('mobile-navigation.png')
 shot('mobile-overview.png','.hero')
 checks['mobileOverflow']=overflow()
 shot('mobile-policy.png','#policy-explorer')
 checks['mobilePolicyOverflow']=overflow()
 page.select_option('#policy-case','storage')
 checks['mobileStorageOutcome']=page.locator('#policy-queue').inner_text()
 if checks['mobileStorageOutcome']!='Hold new launches':problems.append('Mobile policy control')
 checks['pageErrors']=errors
 checks['externalRequests']=[x for x in requests if not x.startswith('file:')]
 checks['browserVersion']=browser.version
 if errors:problems.extend(errors)
 if checks['externalRequests']:problems.append('External requests')
 if not checks['accessibleDiagrams']:problems.append('SVG accessibility')
 if (checks['sections'],checks['navLinks'],checks['tables'],checks['diagrams'])!=(12,12,10,2):problems.append('Structure counts')
 for key in ('desktopOverflow','mobileOverflow','mobilePolicyOverflow'):
  if checks[key]['documentWidth']>checks[key]['width']:problems.append(key)
 result['browserChecks']=checks
 browser.close()
result['reportSha256']=hashlib.sha256(report.read_bytes()).hexdigest()
result['specificationSha256']=hashlib.sha256(source.read_bytes()).hexdigest()
result['problems']=problems;result['allChecksPassed']=not problems
result['scope']='Documentation links/source ranges, report presentation, illustrative policy outputs and calculated sizing arithmetic. No new build, simulation, implementation or physical validation.'
content=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
(records/'implementation-report-validation.json').write_text(content,encoding='utf-8')
(captures/'report-validation.json').write_text(content,encoding='utf-8')
print(json.dumps({'allChecksPassed':not problems,'problems':problems,'captureDirectory':str(captures),'sourceRanges':len(source_checks),'localHtmlLinks':len(local),'markdownLinks':len(md_links),'browserChecks':checks},indent=2,ensure_ascii=False))
raise SystemExit(0 if not problems else 1)
