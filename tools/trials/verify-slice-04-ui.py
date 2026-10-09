"""Playwright evidence for the actual native-backed dashboard and verified tick inspector."""
import argparse,json,time,urllib.request,re
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--base',default='http://127.0.0.1:54324');a=p.parse_args()
root=Path(a.session);out=root/'report'/('ui-04-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
state=json.load(urllib.request.urlopen(a.base+'/api/state?compact=true'))
attempt=next(v for v in reversed(state['attempts']) if v['execution']=='Completed' and v['definition']['name'].startswith('Barrier ') and 'repeat matrix' in v['definition']['name'])
errors=[];checks={}
focused=json.load(urllib.request.urlopen(a.base+'/api/state?compact=true&selected='+attempt['id']))
history=next(v for v in focused['attempts'] if v['id']==attempt['id'])['impactHistory']
assert abs(max(v['peakNetBarrierForceN'] for v in history)-attempt['metrics']['impactDetail']['peakNetBarrierForceN'])<1e-8
checks['displayEnvelopePreservesRawPeak']=True
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=browser.new_page(viewport=dict(width=1600,height=1100));page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(a.base,wait_until='load');page.get_by_label('Scenario').wait_for()
 page.locator('.queue-item').filter(has_text=attempt['id'][:8]).click()
 page.get_by_role('heading',name='Archived tick inspector').wait_for()
 page.get_by_label('Node ID',exact=True).fill('73');page.get_by_label('Beam ID',exact=True).fill('0')
 page.get_by_role('button',name='Inspect tick',exact=True).click()
 page.get_by_role('heading',name='Actual terrain/object applications',exact=False).wait_for()
 assert page.locator('.accounting').filter(has_text='Archived tick inspector').inner_text().find('barrier')>=0
 page.screenshot(path=str(out/'dashboard-desktop.png'),full_page=True)
 page.locator('.impact-panel').screenshot(path=str(out/'impact-panel.png'))
 page.locator('.accounting').filter(has_text='Archived tick inspector').screenshot(path=str(out/'tick-inspector.png'))
 checks['indexedFrameVisible']=True
 checks['desktopNoPageOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 response=page.request.get(a.base+f"/api/attempts/{attempt['id']}/detail?tick={attempt['metrics']['impactDetail']['triggerTick']}&node=73&beam=0")
 frame=response.json();assert frame['tick']==attempt['metrics']['impactDetail']['triggerTick'] and any(c['barrier'] for c in frame['contacts'])
 assert len(frame['node']['channels'])==16
 (out/'inspected-native-frame.json').write_text(json.dumps(frame,indent=2),encoding='utf-8')
 bad=page.request.get(a.base+f"/api/attempts/{attempt['id']}/detail?tick={frame['tick']}&node=999&beam=0");assert bad.status==400
 missing=page.request.get(a.base+f"/api/attempts/{attempt['id']}/detail?tick=1&node=0&beam=0");assert missing.status==404
 checks['boundsAndMissingTickRejected']=True
 page.set_viewport_size(dict(width=390,height=844));page.wait_for_timeout(500)
 checks['mobileNoPageOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 page.screenshot(path=str(out/'dashboard-mobile.png'),full_page=True)
 page.set_viewport_size(dict(width=1600,height=1100))
 # Authoring rejects impossible capture conditions without a new worker.
 page.get_by_label('Observe · s').fill('1');page.get_by_role('button',name=re.compile('Queue experiment')).click()
 page.get_by_text('Barrier duration must be at least 6 s',exact=False).wait_for();checks['invalidDefinitionRejected']=True
 browser.close()
checks['browserErrors']=errors
(out/'checks.json').write_text(json.dumps(dict(attemptId=attempt['id'],checks=checks),indent=2),encoding='utf-8')
assert all(v for k,v in checks.items() if k!='browserErrors') and not errors,checks
print(json.dumps(dict(evidence=str(out),checks=checks)),flush=True)
