"""Validate report references, visible images/player progression, desktop/mobile.
Run against the portable report, repository report and extracted portable copy."""
import argparse,json,time
from pathlib import Path
from urllib.parse import urlparse,unquote
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
from PIL import Image,ImageStat
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--repo',required=True);a=p.parse_args()
root=Path(a.session).resolve();repo=Path(a.repo).resolve();reports=[root/'report/index.html',repo/'doc/project/reports/trial-slice-03-2026-10-09.html']
if (root/'bundle-extracted/report/index.html').exists():reports.append(root/'bundle-extracted/report/index.html')
checks=[];errors=[]
class Links(HTMLParser):
 def __init__(self):super().__init__();self.values=[]
 def handle_starttag(self,t,attrs):
  for k,v in attrs:
   if k in ['src','href']:self.values.append(v)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 for i,path in enumerate(reports):
  parser=Links();text=path.read_text(encoding='utf-8');parser.feed(text)
  for ref in parser.values:
   uri=urlparse(ref)
   if uri.scheme in ['http','https'] or ref.startswith('#'):continue
   target=Path(unquote(uri.path.lstrip('/'))) if uri.scheme=='file' else path.parent/unquote(ref)
   if ref=="slice-03-evidence.zip" and "bundle-extracted" in path.parts:continue # archive is the external container, not nested into itself
   assert target.exists(),(path,ref,target)
  page=browser.new_page(viewport=dict(width=1440,height=1050));page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(path.as_uri(),wait_until='load')
  assert page.locator('main > section').count()>=7
  imgs=page.locator('img');assert imgs.count()>=8
  for image in imgs.all():
   image.evaluate('(e)=>e.decode()');assert image.evaluate('(e)=>e.naturalWidth>0')
  iframe=page.locator('iframe');iframe.scroll_into_view_if_needed()
  frame=page.frame_locator('iframe');sequence=frame.locator('#sequence');sequence.wait_for()
  sequence.evaluate('(e)=>e.decode()');before=sequence.get_attribute('src');frame.locator('#play').click()
  page.wait_for_timeout(950);frame.locator('#play').click();assert sequence.get_attribute('src')!=before
  page.screenshot(path=str(root/'report'/f'html-{i}-desktop.png'),full_page=True)
  page.set_viewport_size(dict(width=390,height=844));page.wait_for_timeout(200)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.screenshot(path=str(root/'report'/f'html-{i}-mobile.png'),full_page=True)
  checks.append(dict(path=str(path),localReferences=len(parser.values),images=imgs.count(),imagePlayerAdvances=True,mobileNoOverflow=True))
  page.close()
 browser.close()
assert not errors,errors
result=dict(reports=checks,browserErrors=errors,viewer='System Chrome; does not establish Codex GPU video playback')
(root/'report/html-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
