"""Check report links, actual image pixels and responsive layout in Chrome."""
import argparse,json,time,urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageStat
p=argparse.ArgumentParser();p.add_argument('--session',required=True);a=p.parse_args();root=Path(a.session);report=root/'report';checks={};errors=[]
targets=[report/'index.html',report/'bundle-extracted/report/index.html']
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 for target in targets:
  page=browser.new_page(viewport=dict(width=1500,height=1000));page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(target.as_uri(),wait_until='load');page.locator('details').evaluate_all('(items)=>items.forEach(e=>e.open=true)')
  page.locator('img').evaluate_all('(items)=>items.forEach(e=>e.loading="eager")')
  page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
  imgs=page.locator('img').evaluate_all('(items)=>items.map(e=>e.src)');assert len(imgs)==11
  for uri in imgs:
   path=Path(urllib.parse.unquote(urllib.parse.urlparse(uri).path.lstrip('/')))
   with Image.open(path) as im:assert sum(ImageStat.Stat(im.convert('RGB')).var)>50,path
  for uri in page.locator('a').evaluate_all('(items)=>items.map(e=>e.href)'):
   parsed=urllib.parse.urlparse(uri)
   if parsed.scheme=='file':assert Path(urllib.parse.unquote(parsed.path.lstrip('/'))).exists(),uri
  assert page.locator('svg[role="img"]').count()==1
  desktop=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');assert desktop
  name='portable' if 'bundle-extracted' in str(target) else 'original'
  page.screenshot(path=str(report/('report-'+name+'-desktop.png')),full_page=True)
  page.set_viewport_size(dict(width=390,height=844));page.wait_for_timeout(150)
  mobile=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');assert mobile
  page.screenshot(path=str(report/('report-'+name+'-mobile.png')),full_page=True)
  checks[name]=dict(images=len(imgs),nonblankPixels=True,localLinksExist=True,desktopNoOverflow=desktop,mobileNoOverflow=mobile)
  page.close()
 browser.close()
assert not errors
(report/'report-checks.json').write_text(json.dumps(dict(checks=checks,errors=errors),indent=2),encoding='utf-8');print(json.dumps(checks))
