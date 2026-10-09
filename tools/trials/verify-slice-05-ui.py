"""Screenshots and browser checks of the actual native-backed transition workbench."""
import argparse,json,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--base',default='http://127.0.0.1:54325');a=p.parse_args()
root=Path(a.session);out=root/'report'/('ui-05-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
state=json.load(urllib.request.urlopen(a.base+'/api/state?compact=true'));checks={};errors=[]
scenarios=['yield-tension-v1','yield-compression-v1','fracture-v1','protected-beam-v1']
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=browser.new_page(viewport=dict(width=1600,height=1100));page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(a.base,wait_until='load');page.get_by_label('Study scenario').wait_for()
 for scenario in scenarios:
  page.get_by_label('Study scenario').select_option(scenario)
  assert page.get_by_label('Release speed · m/s').input_value()=='0'
  assert page.get_by_label('Settling · s').input_value()=='0'
  assert page.get_by_label('Observe · s').get_attribute('max')=='1'
  attempt=next(v for v in state['attempts'] if v['definition']['scenario']==scenario and v['definition']['durationSeconds']==1 and v['validation']=='Passed')
  page.locator('.queue-item').filter(has_text=attempt['id'][:8]).click()
  panel=page.locator('.transition-panel');panel.wait_for();page.wait_for_timeout(250)
  assert 'Material fracture dissipation remains unqualified' in panel.inner_text()
  assert panel.locator('tbody tr').count()==1
  assert panel.get_by_role('button',name='Next transitions').is_disabled()
  panel.screenshot(path=str(out/(scenario+'-ledger.png')))
  if scenario=='protected-beam-v1':
   assert '0 parameter changes · 1 strength changes · 0 removed' in panel.inner_text()
   assert '200 → 400' in panel.inner_text()
  if scenario=='fracture-v1':assert '0 parameter changes · 0 strength changes · 1 removed' in panel.inner_text()
  if scenario=='yield-tension-v1':
   page.locator('.accounting').filter(has=page.get_by_role('heading',name='Scientific qualification')).screenshot(path=str(out/'qualification.png'))
   page.screenshot(path=str(out/'dashboard-desktop.png'),full_page=True)
  checks[scenario]=dict(attempt=attempt['id'],oneExactTransitionVisible=True)
 checks['desktopNoOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 page.set_viewport_size(dict(width=390,height=844));page.wait_for_timeout(300)
 checks['mobileNoOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 page.screenshot(path=str(out/'dashboard-mobile.png'),full_page=True)
 missing=page.request.get(a.base+'/api/attempts/missing/transitions');assert missing.status==404
 checks['missingAttemptRejected']=True;checks['noPageErrors']=not errors
 browser.close()
(out/'checks.json').write_text(json.dumps(dict(checks=checks,errors=errors),indent=2),encoding='utf-8')
assert checks['desktopNoOverflow'] and checks['mobileNoOverflow'] and not errors
print(str(out))
