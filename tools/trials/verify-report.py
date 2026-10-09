"""Verify evidence HTML media, layout, references and actual video decoding."""
import argparse,json,urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--repo',required=True);a=p.parse_args()
session=Path(a.session);repo=Path(a.repo);errors=[];requests=[]
report=session/'report/index.html';results={}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=browser.new_page(viewport={'width':1600,'height':1050})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:requests.append(r.url))
 page.goto(report.as_uri(),wait_until='load')
 results['desktopNoOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 results['imagesLoaded']=page.locator('img').evaluate_all('(images)=>images.every(i=>i.complete&&i.naturalWidth>0)')
 results['diagrams']=page.locator('svg[role=img]').count()
 results['sections']=page.locator('main>section').count()
 results['videoMetadata']=page.locator('video').evaluate('(v)=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight})')
 page.locator('video').evaluate('async(v)=>{v.muted=true;v.currentTime=1;await v.play()}')
 page.wait_for_timeout(1200)
 results['videoPlayback']=page.locator('video').evaluate('(v)=>({time:v.currentTime,frames:v.getVideoPlaybackQuality().totalVideoFrames,error:v.error?.message??null})')
 page.locator('video').evaluate('(v)=>v.pause()')
 page.screenshot(path=str(session/'report/report-desktop.png'),animations='disabled')
 page.locator('#measure').scroll_into_view_if_needed()
 page.screenshot(path=str(session/'report/report-measurements.png'),animations='disabled')
 page.set_viewport_size({'width':390,'height':844})
 page.evaluate('scrollTo(0,0)')
 results['mobileNoOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.screenshot(path=str(session/'report/report-mobile.png'),animations='disabled')
 missing=[]
 for href in page.locator('a').evaluate_all('(links)=>links.map(a=>a.getAttribute("href"))'):
  if href.startswith(('https:','#')):continue
  path=report.parent/urllib.parse.unquote(href)
  if not path.exists() and path.name!='publication.json':missing.append(str(path))
 results['missingLocalLinks']=missing
 page.set_viewport_size({'width':1600,'height':1050})
 page.goto((repo/'doc/project/reports/trial-slice-01-2026-10-08.html').as_uri(),wait_until='load')
 results['repositoryReportImagesLoaded']=page.locator('img').evaluate_all('(images)=>images.every(i=>i.complete&&i.naturalWidth>0)')
 results['externalRequests']=[r for r in requests if r.startswith(('http:','https:'))]
 results['pageErrors']=errors
 browser.close()
results['pass']=results['desktopNoOverflow'] and results['mobileNoOverflow'] and results['imagesLoaded'] and results['repositoryReportImagesLoaded'] and results['videoPlayback']['time']>1.5 and results['videoPlayback']['frames']>0 and not errors and not results['missingLocalLinks'] and not results['externalRequests']
(session/'report/report-qa.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2));assert results['pass']
