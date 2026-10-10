"""Author a real native impact through React; inspect live/retained/required-loss views."""
import argparse,json,time,re,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--base',default='http://127.0.0.1:54328');a=p.parse_args()
root=Path(a.session);out=root/'report'/('ui-07-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir();checks={};errors=[]
def get(path):return json.load(urllib.request.urlopen(a.base+path,timeout=30))
end=time.time()+180
while time.time()<end:
 state=get('/api/state?compact=true')
 if len(state['attempts'])>=17 and all(v['execution'] in ['Completed','Failed','Cancelled'] for v in state['attempts']):break
 time.sleep(.5)
else:raise AssertionError('Native qualification is still active')
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True);page=browser.new_page(viewport=dict(width=1440,height=1000));page.on('pageerror',lambda e:errors.append(str(e)))
 uiName='Slice 07 UI-authored removal '+out.name[-6:]
 page.goto(a.base);page.get_by_label('Study scenario').select_option('impact-fracture-v1');page.get_by_label('Experiment name',exact=True).fill(uiName)
 for label,value in [('Release speed',5),('Observe',7),('Settling',0)]:
  field=page.get_by_label(re.compile(label));assert float(field.input_value())==value and field.is_disabled()
 assert page.get_by_label('Observation profile').is_disabled();checks['frozenAuthoringControls']=True
 page.locator('.author').screenshot(path=str(out/'authoring.png'))
 page.get_by_role('button',name=re.compile('Queue experiment')).click()
 end=time.time()+120;v=None
 while time.time()<end:
  state=get('/api/state?compact=true');matches=[v for v in state['attempts'] if v['definition']['name']==uiName]
  if matches:
   v=matches[0]
   if v['execution']=='Running':
    page.locator('.queue-item').filter(has_text=v['id'][:8]).click();page.locator('.recorder-panel').screenshot(path=str(out/'live-recorder.png'));checks['realLiveRecorder']=True;break
  time.sleep(.2)
 assert v and checks.get('realLiveRecorder')
 while time.time()<end:
  v=get('/api/attempts/'+v['id']+'/status')
  if v['execution'] in ['Completed','Failed']:break
  time.sleep(.25)
 assert v['execution']=='Completed' and v['capture']=='Complete' and v['validation']=='Passed';checks['uiAuthoredSourceWorkerPassed']=True
 state=get('/api/state?compact=true')
 for scenario in ['impact-yield-v1','impact-fracture-v1']:
  value=next(x for x in state['attempts'] if x['definition']['scenario']==scenario and x['definition']['name'].startswith('Slice 07 qualification') and x['definition']['detailFault']=='none')
  page.locator('.queue-item').filter(has_text=value['id'][:8]).click();page.wait_for_timeout(550)
  page.locator('.impact-panel').get_by_text('Observed collision sequence',exact=True).wait_for()
  assert page.locator('.detail-query').count()==1 and page.locator('.transition-panel').count()==1,'duplicate scientific panels after selection'
  assert str(value['metrics']['impactTimeline']['firstContactTick']) in page.locator('.collision-sequence').inner_text()
  page.locator('.impact-panel').screenshot(path=str(out/(scenario+'-sequence.png')))
  page.locator('.transition-panel').screenshot(path=str(out/(scenario+'-ledger.png')))
  panel=page.locator('.accounting').filter(has=page.get_by_role('heading',name='Scientific qualification',exact=True));panel.screenshot(path=str(out/(scenario+'-qualification.png')))
  checks[scenario+'SequenceAndLedger']=True
  tick=value['metrics']['impactTimeline']['firstRemovalTick'] or value['metrics']['impactTimeline']['firstStrengthTick']
  inspector=page.locator('.detail-query');inspector.get_by_label('Tick',exact=True).fill(str(tick));inspector.get_by_role('button',name='Inspect tick').click()
  page.get_by_text(re.compile('Tick '+str(tick)+' . node')).wait_for();checks[scenario+'ExactTickInspection']=True
 loss=next(x for x in state['attempts'] if x['definition']['detailFault']=='storage-error')
 page.locator('.queue-item').filter(has_text=loss['id'][:8]).click();page.wait_for_timeout(550)
 assert 'Required loss is sticky' in page.locator('.recorder-panel').inner_text();page.locator('.recorder-panel').screenshot(path=str(out/'required-loss.png'));checks['stickyLossVisible']=True
 page.set_viewport_size(dict(width=420,height=900));page.wait_for_timeout(200)
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(out/'mobile.png'));checks['mobileNoOverflow']=True
 assert not errors;checks['noBrowserErrors']=True
 (out/'checks.json').write_text(json.dumps(dict(checks=checks,errors=errors,uiAttempt=v),indent=2),encoding='utf-8');browser.close()
print(str(out))
