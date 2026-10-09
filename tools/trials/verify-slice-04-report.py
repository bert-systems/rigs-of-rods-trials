"""Check report images, links, responsive layout and portable image playback in Chrome."""
import argparse,json,time,urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--html',required=True);p.add_argument('--output',required=True);p.add_argument('--allow-publication-pending',action='store_true');a=p.parse_args()
path=Path(a.html).resolve();out=Path(a.output).resolve();out.mkdir(exist_ok=True);errors=[];checks={}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=browser.new_page(viewport=dict(width=1600,height=1100));page.on('pageerror',lambda e:errors.append(str(e)));page.goto(path.as_uri(),wait_until='load')
 page.locator('img').evaluate_all("async(es)=>{for(const e of es){e.loading='eager';await e.decode();}}")
 checks['loadedImages']=page.locator('img').count();assert checks['loadedImages']>=8
 missing=[]
 for href in page.locator('a[href]').evaluate_all('(es)=>es.map(e=>e.href)'):
  parsed=urllib.parse.urlsplit(href)
  if parsed.scheme=='file':
   name=urllib.parse.unquote(parsed.path).lstrip('/')
   if not Path(name).exists() and not (a.allow_publication_pending and Path(name).name in ['publication.json','bundle-check.json','slice-04-evidence.zip']):missing.append(href)
 checks['missingLinks']=missing;assert not missing,missing
 checks['svgPipeline']=page.locator('svg[role=img]').count()==1
 checks['desktopNoPageOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 page.screenshot(path=str(out/'desktop.png'),full_page=True)
 frame=page.frame_locator('iframe');image=frame.locator('#sequence');image.evaluate('(e)=>e.decode()');initial=image.get_attribute('src');frame.locator('#play').click();page.wait_for_timeout(900);frame.locator('#play').click();image.evaluate('(e)=>e.decode()');checks['embeddedImagePlayerAdvances']=initial!=image.get_attribute('src')
 page.set_viewport_size(dict(width=390,height=844));page.wait_for_timeout(300);checks['mobileNoPageOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'mobile.png'),full_page=True)
 checks['browserErrors']=errors;browser.close()
(out/'checks.json').write_text(json.dumps(dict(html=str(path),checks=checks),indent=2),encoding='utf-8')
assert checks['desktopNoPageOverflow'] and checks['mobileNoPageOverflow'] and checks['svgPipeline'] and checks['embeddedImagePlayerAdvances'] and not errors,checks
print(json.dumps(checks),flush=True)
