"""Exercise the real local workbench and fresh source-built workers; keep evidence outside Git."""
import argparse,json,time,subprocess,urllib.request,urllib.error,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser()
parser.add_argument('--session',required=True)
parser.add_argument('--base',default='http://127.0.0.1:54321')
args=parser.parse_args()
session=Path(args.session).resolve()
evidence=session/'report'/('verification-'+time.strftime('%Y%m%d-%H%M%S'))
evidence.mkdir(parents=True,exist_ok=False)
base=args.base
def get(path):return json.load(urllib.request.urlopen(base+path,timeout=15))
token=get('/api/session')['session']
def post(path,value=None,authorized=True,origin=None):
 headers={'Content-Type':'application/json'}
 if authorized:headers['X-Trials-Session']=token
 if origin:headers['Origin']=origin
 request=urllib.request.Request(base+path,data=json.dumps(value or {}).encode(),headers=headers,method='POST')
 try:
  with urllib.request.urlopen(request,timeout=15) as response:return response.status,json.load(response)
 except urllib.error.HTTPError as e:return e.code,e.read().decode()
def attempt(id):return next(a for a in get('/api/state')['attempts'] if a['id']==id)
def wait(id,predicate,seconds=150):
 end=time.time()+seconds
 while time.time()<end:
  a=attempt(id)
  if predicate(a):return a
  time.sleep(.1)
 raise AssertionError('Attempt did not reach requested state: '+id+' '+str(a['execution']))
def enqueue(name,**kw):
 code,result=post('/api/experiments',{'name':name,**kw})
 assert code==200,(code,result)
 return result['attemptIds']
def completed(id):
 a=wait(id,lambda a:a['execution'] in ('Completed','Failed','Cancelled'))
 assert a['execution']=='Completed',a
 assert a['capture']=='Complete',a['metrics']
 assert a['validation']=='NotReady',a['validation']
 return a
checks={};errors=[];recorder=None;video_log=None
checks['missingSessionRejected']=post('/api/experiments',{'name':'blocked'},False)[0]==403
checks['foreignOriginRejected']=post('/api/experiments',{'name':'blocked'},True,'https://untrusted.example')[0]==403
checks['unsupportedAssetRejected']=post('/api/experiments',{'name':'wrong asset','vehicle':'other.truck'})[0]==400
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=browser.new_page(viewport={'width':1600,'height':1050})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(base,wait_until='load')
 page.get_by_role('button',name='Queue experiment').wait_for()
 page.screenshot(path=str(evidence/'workbench-ready.png'),animations='disabled')
 name=page.get_by_label('Experiment name')
 name.fill('Verified coast / pause / resume')
 name.focus();page.wait_for_timeout(500)
 checks['formFocusSurvivesUpdates']=name.evaluate('(e)=>document.activeElement===e')
 old_ids={a['id'] for a in get('/api/state')['attempts']}
 page.get_by_label('Observe · s').fill('12')
 page.get_by_role('button',name='Queue experiment').click()
 end=time.time()+10
 while time.time()<end:
  new=[a for a in get('/api/state')['attempts'] if a['id'] not in old_ids]
  if new:break
  time.sleep(.1)
 assert len(new)==1
 id=new[0]['id']
 active=wait(id,lambda a:a['execution']=='Running' and (a.get('workerStatus') or {}).get('timeSeconds',0)>1)
 try:
  title=subprocess.check_output(['powershell.exe','-NoProfile','-Command','(Get-Process -Id '+str(active['processId'])+').MainWindowTitle'],text=True).strip()
  assert title
  video_log=open(evidence/'native-video.log','wb')
  recorder=subprocess.Popen([r'C:\Users\berts\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe','-hide_banner','-n','-f','gdigrab','-framerate','30','-draw_mouse','0','-i','title='+title,'-vf','scale=1280:-2','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-t','45','-movflags','+faststart',str(evidence/'native-coast.mp4')],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=video_log)
 except Exception as e:checks['videoError']=str(e)
 active=wait(id,lambda a:a['execution']=='Running' and (a.get('latest') or {}).get('phase')=='coast' and a['latest']['timeSeconds']>4)
 page.screenshot(path=str(evidence/'workbench-running.png'),animations='disabled')
 checks['pauseAccepted']=post('/api/attempts/'+id+'/pause')[0]==200
 paused=wait(id,lambda a:a['execution']=='Paused' and (a.get('workerStatus') or {}).get('paused'))
 page.wait_for_timeout(250)
 page.screenshot(path=str(evidence/'workbench-paused.png'),animations='disabled')
 before=attempt(id)['workerStatus']['tick']
 time.sleep(.8)
 after=attempt(id)['workerStatus']['tick']
 checks['pauseStopsNativeClock']=before==after
 checks['pausedTick']=after
 checks['resumeAccepted']=post('/api/attempts/'+id+'/resume')[0]==200
 primary=completed(id)
 if recorder:
  if recorder.poll() is None:
   try:recorder.communicate(input=b'q\n',timeout=12)
   except subprocess.TimeoutExpired:recorder.kill();recorder.wait()
  checks['videoExitCode']=recorder.returncode
  if video_log:video_log.close()
 events=[json.loads(s) for s in (Path(primary['archivePath'])/'native-events.jsonl').read_text(encoding='utf-8').splitlines()]
 pause=next(e for e in events if e['event']=='pause')
 resume=next(e for e in events if e['event']=='resume')
 checks['pauseResumeAppliedAtSameTick']=pause['tick']==resume['tick']
 checks['nativePauseEvents']=events
 page.screenshot(path=str(evidence/'workbench-result.png'),animations='disabled')
 shots=list((Path(primary['archivePath'])/'worker/config/screenshots').glob('*.png'))
 for i,shot in enumerate(shots):shutil.copy2(shot,evidence/('native-coast-'+str(i+1)+'.png'))
 checks['nativeScreenshots']=len(shots)
 page.set_viewport_size({'width':390,'height':844})
 checks['mobileNoOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.screenshot(path=str(evidence/'workbench-mobile.png'),animations='disabled')
 page.set_viewport_size({'width':1600,'height':1050})
 wind_ids=enqueue('Steady wind / lower density / repeats',durationSeconds=4,repeats=2,
  environment={'gravity':-8,'temperatureK':300,'density':1,'windX':3,'windY':0,'windZ':-1})
 wind=[completed(i) for i in wind_ids]
 checks['environmentAdopted']=all(a['latest']['gravityMps2']==-8 and a['latest']['densityKgM3']==1 and a['latest']['windMps']==[3,0,-1] for a in wind)
 checks['freshRepeatPids']=wind[0]['processId']!=wind[1]['processId']
 checks['privateRepeatProfiles']=wind[0]['processPath']!=wind[1]['processPath']
 checks['sharedImmutableRevision']=wind[0]['revisionId']==wind[1]['revisionId'] and wind[0]['definitionSha256']==wind[1]['definitionSha256']
 checks['serialRepeatOrdering']=wind[1]['events'][1]['time']>=wind[0]['events'][-1]['time']
 cancel_ids=enqueue('Cancel active / independent next',durationSeconds=6,repeats=2)
 wait(cancel_ids[0],lambda a:a['execution']=='Running' and (a.get('workerStatus') or {}).get('timeSeconds',0)>1)
 checks['cancelAccepted']=post('/api/attempts/'+cancel_ids[0]+'/cancel')[0]==200
 cancelled=wait(cancel_ids[0],lambda a:a['execution']=='Cancelled')
 following=completed(cancel_ids[1])
 checks['cancelRetainsArchive']=(Path(cancelled['archivePath'])/'steps.rort').exists()
 checks['queueContinuesAfterCancel']=following['execution']=='Completed'
 old_ids={a['id'] for a in get('/api/state')['attempts']}
 checks['manualRetryAccepted']=post('/api/attempts/'+cancel_ids[0]+'/retry')[0]==200
 state=get('/api/state')
 retry_id=next(a['id'] for a in state['attempts'] if a['id'] not in old_ids)
 retry=completed(retry_id)
 checks['retryIsSeparateAttempt']=retry['retryOf']==cancelled['id'] and retry['processPath']!=cancelled['processPath']
 checks['archiveMarkAccepted']=post('/api/attempts/'+cancelled['id']+'/archive')[0]==200
 checks['archiveRetainsFiles']=attempt(cancelled['id'])['archived'] and (Path(cancelled['archivePath'])/'steps.rort').exists()
 checks['allBuiltExecutableHashesAgree']=len({a['executableSha256'] for a in [primary,*wind,cancelled,following,retry]})==1
 checks['attempts']=[{k:a.get(k) for k in ['id','definition','revisionId','processId','processPath','executableSha256','execution','capture','validation','metrics','archivePath']} for a in [primary,*wind,cancelled,following,retry]]
 checks['pageErrors']=errors
 page.locator('nav button').filter(has_text='Results').click()
 page.screenshot(path=str(evidence/'workbench-batch.png'),animations='disabled')
 browser.close()
checks['allBooleanChecksPass']=all(v for v in checks.values() if isinstance(v,bool))
(evidence/'checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
(session/'report/latest-verification.txt').write_text(str(evidence),encoding='utf-8')
print(json.dumps(checks,indent=2))
assert checks['allBooleanChecksPass'] and not errors
assert checks.get('videoExitCode')==0 and checks['nativeScreenshots']>=1
