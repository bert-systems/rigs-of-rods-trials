
"""Check local report links, figures, nested native frame playback and portable export."""
import argparse,json,hashlib,zipfile,shutil,time,urllib.parse
from pathlib import Path
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--repo',required=True);a=p.parse_args()
session=Path(a.session).resolve();repo=Path(a.repo).resolve();report=session/'report'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['src','href'] and v:self.links.append(v)
def localcheck(path):
 links=Links();links.feed(path.read_text(encoding='utf-8'));missing=[]
 for link in links.links:
  url=urllib.parse.urlparse(link)
  if not url.scheme and not url.netloc and url.path:
   target=(path.parent/urllib.parse.unquote(url.path)).resolve()
   if not target.exists():missing.append(str(target))
  elif url.scheme=='file':
   target=Path(urllib.parse.unquote(url.path).lstrip('/'))
   if not target.exists():missing.append(str(target))
 return missing
checks={'reportMissingLinks':localcheck(report/'index.html'),'repoReportMissingLinks':localcheck(repo/'doc/project/reports/trial-slice-02-2026-10-08.html')}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((report/'index.html').as_uri(),wait_until='load')
 checks['allImagesDecoded']=page.locator('img').evaluate_all('(images)=>images.every(i=>i.complete&&i.naturalWidth>0)')
 page.screenshot(path=str(report/'report-desktop.png'),full_page=True)
 page.locator('#fixtures').scroll_into_view_if_needed();page.screenshot(path=str(report/'report-fixture-panel.png'))
 page.locator('iframe').scroll_into_view_if_needed()
 frame=page.frame_locator('iframe');initial=frame.locator('#sequence').get_attribute('src')
 frame.locator('#play').click();page.wait_for_timeout(800);frame.locator('#play').click()
 checks['embeddedImagePlayerAdvances']=frame.locator('#sequence').get_attribute('src')!=initial
 page.set_viewport_size({'width':390,'height':844});page.goto((report/'index.html').as_uri(),wait_until='load')
 checks['mobileNoOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 page.screenshot(path=str(report/'report-mobile.png'),full_page=True);checks['browserErrors']=errors
 b.close()
checks['protectedBaselineHash']=hashlib.sha256(Path(r'D:\Rigs of Rods\source-build-2026-10-08\build\bin\RoR.exe').read_bytes()).hexdigest().upper()
assert not checks['reportMissingLinks'] and not checks['repoReportMissingLinks'] and checks['allImagesDecoded'] and checks['embeddedImagePlayerAdvances'] and checks['mobileNoOverflow'] and not checks['browserErrors'],checks
# Relative paths from report/index.html resolve to media siblings in the standalone bundle.
package=session/'package';(package/'report').mkdir(parents=True,exist_ok=True)
shutil.copy2(report/'index.html',package/'report/index.html');shutil.copytree(report/'images',package/'report/images',dirs_exist_ok=True)
shutil.copytree(session/'media',package/'media',dirs_exist_ok=True)
shutil.copy2(repo/'doc/project/slices/slice-02-results.json',package/'report/slice-02-results.json')
manifest={}
for f in package.rglob('*'):
 if f.is_file() and f.name!="sha256-manifest.json":manifest[f.relative_to(package).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
(package/'sha256-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
archive=report/'slice-02-evidence.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in package.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(package).as_posix())
extract=session/'package-verified'
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None;z.extractall(extract)
checks['extractedMissingLinks']=localcheck(extract/'report/index.html')
checks['archiveFileCount']=len(manifest)+1;checks['archiveBytes']=archive.stat().st_size
checks['extractedHashesMatch']=all(hashlib.sha256((extract/name).read_bytes()).hexdigest()==digest for name,digest in manifest.items())
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=b.new_page();page.goto((extract/'report/index.html').as_uri(),wait_until='load')
 checks['extractedImagesDecoded']=page.locator('img').evaluate_all('(images)=>images.every(i=>i.complete&&i.naturalWidth>0)')
 b.close()
assert not checks['extractedMissingLinks'] and checks['extractedHashesMatch'] and checks['extractedImagesDecoded'],checks
(report/'report-checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');print(json.dumps(checks))
