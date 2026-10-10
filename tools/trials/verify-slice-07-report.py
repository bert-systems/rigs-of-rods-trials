"""Check canonical/extracted HTML links, actual rendered evidence and fallback playback."""
import argparse,json,time,re,urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageStat
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--repo',required=True);a=p.parse_args();root=Path(a.session).resolve();repo=Path(a.repo).resolve()
out=root/'report'/('report-qa-07-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir();checks=[]
targets=[repo/'doc/project/reports/trial-slice-07-2026-10-10.html',root/'report/review-extracted/report/index.html']
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 for index,target in enumerate(targets):
  page=browser.new_page(viewport=dict(width=1440,height=1050));errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(target.as_uri(),wait_until='load');images=page.locator('figure img');stats=[];assert images.count()>=7
  for i in range(images.count()):
   image=images.nth(i);image.scroll_into_view_if_needed();image.evaluate('(e)=>e.decode()');shot=out/f'{index}-image-{i}.png';image.screenshot(path=str(shot))
   with Image.open(shot) as im:s=ImageStat.Stat(im.convert('RGB'));stats.append(dict(mean=sum(s.mean)/3,variance=sum(s.var)/3))
  assert all(s['mean']>10 and s['variance']>50 for s in stats)
  frame=page.frame_locator('iframe');seq=frame.locator('#sequence');seq.evaluate('(e)=>e.decode()');before=seq.get_attribute('src')
  frame.locator('#play').click();page.wait_for_timeout(800);assert seq.get_attribute('src')!=before;frame.locator('#play').click();seq.evaluate('(e)=>e.decode()')
  seq.screenshot(path=str(out/f'{index}-fallback-frame.png'))
  urls=page.locator('a[href],img[src],iframe[src]').evaluate_all('(els)=>els.map(e=>e.href||e.src)')
  urls+=frame.locator('a[href],img[src],source[src]').evaluate_all('(els)=>els.map(e=>e.href||e.src)')
  missing=[]
  for url in urls:
   parsed=urllib.parse.urlparse(url)
   if parsed.scheme=='file':
    path=urllib.parse.unquote(parsed.path)
    if re.match(r'^/[A-Za-z]:',path):path=path[1:]
    if not Path(path).exists():missing.append(path)
  assert not missing,missing;assert page.locator('svg[role=img]').count()==1
  page.evaluate('scrollTo(0,0)');page.screenshot(path=str(out/f'{index}-desktop.png'),full_page=True)
  page.set_viewport_size(dict(width=390,height=844));page.wait_for_timeout(100)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.screenshot(path=str(out/f'{index}-mobile.png'),full_page=True)
  assert not errors,errors;checks.append(dict(report=str(target),images=len(stats),visiblePixels=stats,localLinks=len(urls),missing=missing,fallbackProgression=True,mobileNoOverflow=True,browserErrors=errors));page.close()
 browser.close()
(out/'checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');print(str(out),flush=True)
