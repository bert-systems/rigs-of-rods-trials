
"""Verify visible pixels, not only video timestamps; inspect image fallback progression."""
import argparse,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageStat
p=argparse.ArgumentParser();p.add_argument('--directory',required=True);a=p.parse_args();directory=Path(a.directory).resolve()
checks={}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((directory/'playback.html').as_uri(),wait_until='load')
 image=page.locator('#sequence');image.evaluate('(e)=>e.decode()')
 initial=image.get_attribute('src')
 page.locator('#play').click();page.wait_for_timeout(900);page.locator('#play').click();image.evaluate('(e)=>e.decode()')
 checks['imageFallbackAdvances']=image.get_attribute('src')!=initial
 page.screenshot(path=str(directory/'image-player-verified.png'),full_page=True)
 page.locator('summary').click()
 video=page.locator('video')
 video.evaluate('async(v)=>{v.muted=true;await v.play();v.pause();}')
 pixels=[]
 for timestamp in [1,3,5]:
  result=video.evaluate('''async(v,t)=>{
   await new Promise((resolve,reject)=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=Math.min(t,v.duration-.1);setTimeout(()=>reject(Error('seek timeout')),8000)});
   await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
   return {time:v.currentTime,width:v.videoWidth,height:v.videoHeight};
  }''',timestamp)
  screenshot=directory/('webm-at-'+str(timestamp)+'s.png')
  video.screenshot(path=str(screenshot))
  with Image.open(screenshot) as im:
   w,h=im.size;stat=ImageStat.Stat(im.convert('RGB').crop((w//4,h//4,3*w//4,3*h//4)))
   result['mean']=sum(stat.mean)/3;result['variance']=sum(stat.var)/3
  pixels.append(result)
 checks['webmVisiblePixels']=all(x['mean']>10 and x['variance']>50 for x in pixels)
 checks['webmDecodedPixels']=pixels
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(directory/'mobile-player.png'),full_page=True)
 checks['mobileNoHorizontalOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 checks['browserErrors']=errors;checks['viewer']='Headless system Chrome; does not prove Codex in-app GPU video rendering'
 browser.close()
(directory/'playback-check.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
assert checks['imageFallbackAdvances'] and checks['webmVisiblePixels'] and checks['mobileNoHorizontalOverflow'] and not errors,checks
print(json.dumps(checks))
