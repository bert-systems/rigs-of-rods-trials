
"""Slice 02 real native fixtures, browser controls, capture, repeatability and relative observer cost."""
import argparse,json,time,subprocess,urllib.request,urllib.error,hashlib,shutil,struct,zlib,statistics
from pathlib import Path
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--session',required=True);ap.add_argument('--base',default='http://127.0.0.1:54322');args=ap.parse_args()
root=Path(args.session).resolve();out=root/'report'/('verification-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir(exist_ok=False)
base=args.base
def get(p):return json.load(urllib.request.urlopen(base+p,timeout=20))
token=get('/api/session')['session']
def post(p,d):
 req=urllib.request.Request(base+p,data=json.dumps(d).encode(),headers={'Content-Type':'application/json','X-Trials-Session':token},method='POST')
 with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
def current(id):return next(a for a in get('/api/state')['attempts'] if a['id']==id)
def wait(id,predicate,seconds=160):
 end=time.time()+seconds
 while time.time()<end:
  a=current(id)
  if predicate(a):return a
  time.sleep(.15)
 raise AssertionError((id,a['execution'],a.get('events',[])[-2:]))
def enqueue(name,sc='coast-v1',**kw):
 d={'name':name,'scenario':sc,'vehicle':'b6b0UID-semi.truck' if sc=='coast-v1' else 'ror-'+sc+'.truck',
    'settleSeconds':3 if sc=='coast-v1' else 0,'durationSeconds':12 if sc=='coast-v1' else .5 if sc=='freefall-v1' else 5,
    'launchSpeedMps':5 if sc=='coast-v1' else 0,'environment':{'gravity':0 if sc in ['spring-v1','damper-v1'] else -9.81}}
 d.update(kw);return post('/api/experiments',d)['attemptIds']
def done(id,validation='Passed'):
 a=wait(id,lambda a:a['execution'] in ['Completed','Failed','Cancelled'])
 assert a['execution']=='Completed' and a['capture']=='Complete',(a['execution'],a['metrics'])
 assert a['validation']==validation,(id,a['metrics'].get('qualification'))
 return a
def records(a):
 f=(Path(a['archivePath'])/'steps.rort').open('rb');assert f.read(8)==b'RORTRIAL';schema,size=struct.unpack('<II',f.read(8));assert (schema,size)==(2,2080)
 values=[]
 while f.read(4)==b'DATA':
  n,length,crc=struct.unpack('<III',f.read(12));data=f.read(length)
  assert len(data)==n*size and zlib.crc32(data)==crc and f.read(4)==b'DONE'
  for i in range(n):values.append(data[i*size:(i+1)*size])
 f.close();return values
checks={};runs=[];errors=[]
native_frames=get('/api/state')['configuration'].get('evidenceFrames',False)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=browser.new_page(viewport={'width':1600,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(base,wait_until='load');page.get_by_label('Study scenario').wait_for()
 page.get_by_label('Study scenario').select_option('spring-v1')
 checks['fixtureDefaults']=page.get_by_label('Settling · s').input_value()=='0' and page.get_by_label('Gravity Y · m/s²').input_value()=='0'
 page.get_by_label('Experiment name').fill('UI-qualified spring')
 before={a['id'] for a in get('/api/state')['attempts']}
 page.get_by_role('button',name='Queue experiment').click()
 end=time.time()+8
 while time.time()<end:
  fresh=[a for a in get('/api/state')['attempts'] if a['id'] not in before]
  if fresh:break
  time.sleep(.1)
 assert len(fresh)==1;spring_id=fresh[0]['id'];runs.append(done(spring_id))
 page.wait_for_timeout(300);page.screenshot(path=str(out/'spring-qualified-workbench.png'),full_page=True,animations='disabled')
 page.get_by_label('Study scenario').select_option('coast-v1');page.get_by_label('Experiment name').fill('Slice 02 coast / pause / force channels')
 before={a['id'] for a in get('/api/state')['attempts']};page.get_by_role('button',name='Queue experiment').click()
 end=time.time()+8
 while time.time()<end:
  fresh=[a for a in get('/api/state')['attempts'] if a['id'] not in before]
  if fresh:break
  time.sleep(.1)
 id=fresh[0]['id'];active=wait(id,lambda a:a['execution']=='Running' and (a.get('workerStatus') or {}).get('timeSeconds',0)>1)
 title=subprocess.check_output(['powershell.exe','-NoProfile','-Command','(Get-Process -Id '+str(active['processId'])+').MainWindowTitle'],text=True).strip();assert title
 recorder=None;log=None
 if not native_frames:
  log=(out/'native-video.log').open('wb')
  recorder=subprocess.Popen([r'C:\Users\berts\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe','-hide_banner','-y','-f','gdigrab','-framerate','30','-draw_mouse','0','-i','title='+title,
    '-vf','scale=1280:-2','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-t','25','-movflags','+faststart',str(out/'native-accounting-coast.mp4')],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log)
 active=wait(id,lambda a:a['execution']=='Running' and (a.get('latest') or {}).get('timeSeconds',0)>4)
 page.screenshot(path=str(out/'coast-running.png'),full_page=True,animations='disabled')
 post('/api/attempts/'+id+'/pause',{});paused=wait(id,lambda a:a['execution']=='Paused' and a['workerStatus'].get('paused'))
 time.sleep(.25);tick=current(id)['workerStatus']['tick'];time.sleep(.8);checks['pauseStopsClock']=current(id)['workerStatus']['tick']==tick
 page.screenshot(path=str(out/'coast-paused.png'),animations='disabled');post('/api/attempts/'+id+'/resume',{})
 coast=done(id,'NotReady');runs.append(coast)
 if recorder:
  if recorder.poll() is None:
   try:recorder.communicate(input=b'q\n',timeout=10)
   except subprocess.TimeoutExpired:recorder.kill();recorder.wait()
  log.close();checks['nativeVideoExit']=recorder.returncode
 else:
  subprocess.run([r'D:\Rigs of Rods\source-build-2026-10-08\tools\Scripts\python.exe',str(Path(__file__).with_name('native-frames-video.py')),
     '--attempt',coast['archivePath'],'--output',str(out/'native-accounting-coast.mp4')],check=True)
  checks['nativeVideoExit']=0
 checks['videoRequiresPixelValidation']=True
 page.screenshot(path=str(out/'coast-result.png'),full_page=True,animations='disabled')
 for sc in ['freefall-v1','spring-v1','damper-v1']:
  ids=enqueue('Repeated '+sc,sc,repeats=2)
  for id in ids:runs.append(done(id))
 for enabled in [False,True,False,True]:
  id=enqueue('Observer cost '+str(enabled),durationSeconds=5,accounting=enabled)[0]
  runs.append(done(id,'NotReady'))
 checks['noPageErrors']=not errors
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/'workbench-mobile.png'),full_page=True)
 # Tables are intentionally locally scrollable.
 checks['mobileNoPageOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 browser.close()
exe_hash=hashlib.sha256((root/'build/bin/RoR.exe').read_bytes()).hexdigest().upper()
checks['processProvenance']=True;checks['allNewExecutableHashes']=all(a['executableSha256']==exe_hash for a in runs)
for a in runs:
 archive=Path(a['archivePath'])
 provenance=json.loads((archive/'process-provenance.json').read_text(encoding='utf-8'))
 assert provenance['observedExe'].lower()==a['processPath'].lower()
 for module in provenance['modules']:
  if any(x in Path(module).name.lower() for x in ['ogre','rendersystem','freeimage','ois','mygui','caelum']):
   assert str(archive/'worker').lower() in module.lower(),module
 for i,shot in enumerate((archive/'worker/config/screenshots').glob('*.png')):
  shutil.copy2(shot,out/(a['definition']['scenario']+'-'+a['id'][:8]+'-'+str(i)+'.png'))
repeatability={}
for sc in ['freefall-v1','spring-v1','damper-v1']:
 pair=[a for a in runs if a['definition']['scenario']==sc and a['definition']['name'].startswith('Repeated ')]
 rr=[records(a) for a in pair];assert len(rr[0])==len(rr[1]);worst=0
 for a,b in zip(*rr):
  for offset in [40,48,56,64,72,80,144,1144,1160]:
   worst=max(worst,abs(struct.unpack_from('<d',a,offset)[0]-struct.unpack_from('<d',b,offset)[0]))
 repeatability[sc]={'records':len(rr[0]),'maxDifferenceAcrossPositionMomentumAndEnergySI':worst,'distinctPids':pair[0]['processId']!=pair[1]['processId']}
 assert worst<1e-7 and repeatability[sc]['distinctPids']
performance={}
for enabled in [False,True]:
 pair=[a for a in runs if a['definition']['name']=='Observer cost '+str(enabled)]
 cpu=[]
 for a in pair:cpu.extend(struct.unpack_from('<d',r,1256)[0] for r in records(a) if struct.unpack_from('<I',r,16)[0]==1)
 cpu.sort();performance[str(enabled)]={'steps':len(cpu),'medianStepElapsedUs':statistics.median(cpu),'p95StepElapsedUs':cpu[int(len(cpu)*.95)],'meanStepElapsedUs':statistics.mean(cpu)}
performance['medianRatio']=performance['True']['medianStepElapsedUs']/performance['False']['medianStepElapsedUs']
performance['nativeRendererScreenshotRequestsEnabled']=native_frames
performance['baselineScope']='Same accounting-v2 native build with channel attribution disabled; storage scans and aggregate recorder remain enabled. Not instrumentation-off or upstream baseline.'
summary={'checks':checks,'errors':errors,'runs':[{k:a[k] for k in ['id','definition','execution','capture','validation','archivePath','processId','executableSha256','metrics']} for a in runs],
         'repeatability':repeatability,'performance':performance,'evidence':str(out)}
(out/'checks.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
assert all(v for k,v in checks.items() if k!='nativeVideoExit') and checks['nativeVideoExit']==0,checks
print(json.dumps({'evidence':str(out),'checks':checks,'repeatability':repeatability,'performance':performance}))
