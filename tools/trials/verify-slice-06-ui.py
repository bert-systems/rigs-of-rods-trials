"""Actual recorder views; attaches Chrome only to the fault run, after benchmarks."""
import argparse,json,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--base',default='http://127.0.0.1:54326');a=p.parse_args()
root=Path(a.session).resolve();out=root/'report'/('ui-06-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
def get():return json.load(urllib.request.urlopen(a.base+'/api/state?compact=true',timeout=20))
end=time.time()+700
while time.time()<end:
 try:state=get()
 except Exception:time.sleep(1);continue
 fault=next((v for v in state['attempts'] if v['definition']['name']=='Slice06 optimized partial-write fault'),None)
 if fault and fault['execution'] in ['Running','Finalizing','Completed']:break
 time.sleep(.4)
else:raise AssertionError('No native fault trial for live UI qualification')
errors=[];checks={};snapshots=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=browser.new_page(viewport=dict(width=1600,height=1100));page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(a.base,wait_until='load');page.locator('.queue-item').filter(has_text=fault['id'][:8]).click()
 panel=page.locator('.recorder-panel');panel.get_by_role('heading',name='Recorder health').wait_for()
 end=time.time()+300
 while time.time()<end:
  state=get();v=next(x for x in state['attempts'] if x['id']==fault['id']);execution=v['execution'];h=v.get('recorderHealth') or {}
  if h and execution not in snapshots:
   page.wait_for_timeout(150);panel.screenshot(path=str(out/(execution.lower()+'-recorder.png')));snapshots.append(execution)
  if execution=='Finalizing':
   checks['finalizingHasDrainNotice']=panel.get_by_text('Physics finished.',exact=False).count()>0
  if execution in ['Completed','Failed','Cancelled']:break
  time.sleep(.15)
 checks['faultShowsStickyLoss']=panel.get_by_text('Required loss is sticky.',exact=False).count()>0
 checks['actualNativeFaultIncomplete']=v['capture']=='Incomplete' and v['validation']=='NotReady'
 checks['finalizingObserved']='Finalizing' in snapshots
 page.screenshot(path=str(out/'desktop-fault-result.png'),full_page=True)
 healthy=next(x for x in state['attempts'] if x['definition']['name']=='Slice06 optimized whole-pilot barrier')
 page.locator('.queue-item').filter(has_text=healthy['id'][:8]).click();page.wait_for_timeout(350)
 panel.screenshot(path=str(out/'healthy-closed-recorder.png'))
 checks['healthyAllWritersClosed']=all(s is None or s['closed'] and s['queued']==0 and s['pendingSync']==0 for k,s in healthy['recorderHealth'].items() if k!='schema')
 page.screenshot(path=str(out/'desktop-healthy-result.png'),full_page=True)
 page.get_by_label('Diagnostic observer phase profiling').check()
 checks['phaseOptionEnablesProbe']=page.get_by_label('Timing / equivalence probe').is_checked()
 page.get_by_label('Observation profile').select_option('off')
 checks['offDisablesPhaseOption']=not page.get_by_label('Diagnostic observer phase profiling').is_checked() and page.get_by_label('Diagnostic observer phase profiling').is_disabled()
 baseline=next((x for x in state['attempts'] if x['definition']['name']=='Slice06 baseline whole-pilot barrier'),None)
 if baseline:
  page.locator('.queue-item').filter(has_text=baseline['id'][:8]).click();page.wait_for_timeout(350)
  checks['legacyUnavailableNotZero']=panel.get_by_text('Recorder diagnostics are unavailable',exact=False).count()>0
 page.locator('.queue-item').filter(has_text=healthy['id'][:8]).click();page.wait_for_timeout(250)
 page.set_viewport_size(dict(width=390,height=844));page.wait_for_timeout(250)
 checks['mobileNoPageOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 page.screenshot(path=str(out/'mobile-recorder.png'),full_page=True)
 checks['noBrowserErrors']=not errors;browser.close()
(out/'checks.json').write_text(json.dumps(dict(checks=checks,snapshots=snapshots,browserErrors=errors,attemptId=fault['id'],evidence=str(out)),indent=2),encoding='utf-8')
print(json.dumps(checks),flush=True);assert all(checks.values()),checks
