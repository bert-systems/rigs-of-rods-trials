"""Slice 03 source-native observer equivalence/performance and UI proof.
No telemetry-only animation is used as native visual evidence. Each invocation
retains a distinct verification directory and writes results after every run."""
import argparse,json,time,urllib.request,struct,zlib,statistics,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--base',default='http://127.0.0.1:54323');p.add_argument('--phase',choices=['benchmark','visual'],default='benchmark');a=p.parse_args()
root=Path(a.session).resolve();out=root/'report'/('verification-03-'+a.phase+'-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
base=a.base
def get(path):return json.load(urllib.request.urlopen(base+path,timeout=20))
token=get('/api/session')['session']
def post(path,data):
 req=urllib.request.Request(base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Trials-Session':token},method='POST')
 return json.load(urllib.request.urlopen(req,timeout=20))
def current(id):return get('/api/attempts/'+id+'/status')
def wait(id,condition,seconds=180):
 end=time.time()+seconds
 while time.time()<end:
  v=current(id)
  if condition(v):return v
  time.sleep(.15)
 raise AssertionError((id,v['execution'],v['events'][-2:]))
runs=[];checks={};comparisons={};errors=[]
def save():
 (out/'checks.json').write_text(json.dumps(dict(phase=a.phase,runs=runs,checks=checks,comparisons=comparisons,browserErrors=errors,evidence=str(out)),indent=2),encoding='utf-8')
def enqueue(name,scenario='coast-v1',**extra):
 d=dict(name=name,scenario=scenario,vehicle='b6b0UID-semi.truck' if scenario=='coast-v1' else 'ror-'+scenario+'.truck',
        launchSpeedMps=5 if scenario=='coast-v1' else 0,settleSeconds=2 if scenario=='coast-v1' else 0,
        durationSeconds=5 if scenario!='freefall-v1' else .5,environment=dict(gravity=0 if scenario in ['spring-v1','damper-v1'] else -9.81),
        performanceProbe=True,observation='full',accounting=True)
 d.update(extra);return post('/api/experiments',d)['attemptIds'][0]
def done(id):
 v=wait(id,lambda v:v['execution'] in ['Completed','Failed','Cancelled'])
 runs.append(v);save()
 assert v['execution']=='Completed' and v['capture']=='Complete',(id,v['events'][-2:],v['metrics'])
 assert v['validation']==('Passed' if v['definition']['scenario']!='coast-v1' and v['definition']['observation']=='full' and v['definition']['accounting'] else 'NotReady'),v['metrics']
 manifest=json.loads((Path(v['archivePath'])/'manifest.json').read_text(encoding='utf-8-sig'))
 provenance=json.loads((Path(v['archivePath'])/'process-provenance.json').read_text(encoding='utf-8-sig'))
 assert provenance['observedExe'].lower()==provenance['expectedExe'].lower()
 assert v['executableSha256']==hashlib.sha256((root/'build/bin/RoR.exe').read_bytes()).hexdigest().upper()
 forbidden=[m for m in provenance['modules'] if m.lower().startswith('d:\\rigs of rods\\') and not m.lower().startswith(str(Path(v['archivePath'])/'worker').lower())]
 assert not forbidden,forbidden
 if v['definition']['observation']=='off':
  assert not (Path(v['archivePath'])/'steps.rort').exists()
  assert not (Path(v['archivePath'])/'summaries.jsonl').exists()
 return v
def records(v,name):
 f=(Path(v['archivePath'])/name).open('rb')
 magic=f.read(8);schema,size=struct.unpack('<II',f.read(8));values=[]
 assert (magic,schema,size) in [(b'RORPROBE',1,128),(b'RORTRIAL',2,2080)]
 while True:
  tag=f.read(4)
  if tag==b'END!':
   count,lost,io=struct.unpack('<QQI',f.read(20));assert count==len(values) and not lost and not io and not f.read();break
  assert tag==b'DATA'
  n,length,crc=struct.unpack('<III',f.read(12));data=f.read(length);assert n<=128 and length==n*size and zlib.crc32(data)==crc and f.read(4)==b'DONE'
  values.extend(data[i*size:(i+1)*size] for i in range(n))
 return values
def compare(label,x,y):
 xx=records(x,'probe.rort');yy=records(y,'probe.rort')
 assert len(xx)==len(yy)
 maxp=maxv=0;hashes=mismatches=state_mismatches=0
 for r,s in zip(xx,yy):
  assert r[:32]==s[:32] # tick, phase, cohort, flags, dt
  state_mismatches+=r[40:88]!=s[40:88]
  for at in [40,48,56]:maxp=max(maxp,abs(struct.unpack_from('<d',r,at)[0]-struct.unpack_from('<d',s,at)[0]))
  for at in [64,72,80]:maxv=max(maxv,abs(struct.unpack_from('<d',r,at)[0]-struct.unpack_from('<d',s,at)[0]))
  if struct.unpack_from('<I',r,96)[0]:
   hashes+=1;mismatches+=r[88:96]!=s[88:96]
 comparisons[label]=dict(records=len(xx),sentinelMaxPositionDifferenceM=maxp,sentinelMaxVelocityDifferenceMps=maxv,fullNodeBeamFingerprints=hashes,fingerprintMismatches=mismatches,sentinelByteMismatches=state_mismatches,bitwiseStateEquivalent=maxp==0 and maxv==0 and mismatches==0 and state_mismatches==0,attemptIds=[x['id'],y['id']])
 save()
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 page=browser.new_page(viewport=dict(width=1600,height=1100));page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(base,wait_until='load');page.get_by_label('Observation profile').wait_for()
 if a.phase=='benchmark':
  assert not get('/api/state')['configuration']['evidenceFrames']
  page.goto('about:blank')
  for speed in [5,15]:
   grouped={}
   # Interleaved full/off order limits sustained workload/order bias; 3 repeats each.
   for mode in ['off','full','full','off','off','full']:
    v=done(enqueue(f'Performance {speed} mps {mode}',launchSpeedMps=speed,observation=mode))
    grouped.setdefault(mode,[]).append(v)
    print(json.dumps(dict(id=v['id'],speed=speed,mode=mode,timing=v['metrics']['performanceProbe'])),flush=True)
   for i in range(3):compare(f'coast-{speed}-pair-{i+1}',grouped['off'][i],grouped['full'][i])
   compare(f'coast-{speed}-repeat-off',*grouped['off'][:2]);compare(f'coast-{speed}-repeat-full',*grouped['full'][:2])
  basic=done(enqueue('Basic ledger reference',accounting=False))
  full=next(v for v in runs if v['definition']['name']=='Performance 5 mps full')
  compare('basic-vs-full',basic,full)
  for scenario in ['freefall-v1','spring-v1','damper-v1']:
   full=done(enqueue('Qualified '+scenario,scenario));off=done(enqueue('Ledger off '+scenario,scenario,observation='off'))
   compare(scenario,full,off)
   page.goto(base,wait_until='load');page.locator('.queue-item').filter(has_text=full['id'][:8]).click();page.wait_for_timeout(250)
   page.screenshot(path=str(out/(scenario+'-qualified.png')),full_page=True,animations='disabled');page.goto('about:blank')
  wind=dict(gravity=-8,density=1,temperatureK=290,windX=3,windY=0,windZ=-1)
  woff=done(enqueue('Relative-wind ledger off',observation='off',environment=wind))
  wfull=done(enqueue('Relative-wind ledger full',environment=wind));compare('steady-wind',woff,wfull)
  checks['allProfilesCompletedNoLoss']=True
 else:
  assert get('/api/state')['configuration']['evidenceFrames']
  page.get_by_label('Study scenario').select_option('coast-v1');page.get_by_label('Observation profile').select_option('off')
  page.get_by_label('Experiment name').fill('UI ledger-off controls');page.get_by_label('Observe · s').fill('12')
  before={v['id'] for v in get('/api/state')['attempts']};page.get_by_role('button',name='Queue experiment').click()
  end=time.time()+15
  while time.time()<end:
   fresh=[v for v in get('/api/state')['attempts'] if v['id'] not in before]
   if fresh:break
   time.sleep(.1)
  assert len(fresh)==1;id=fresh[0]['id']
  wait(id,lambda v:v['execution']=='Running' and (v.get('latest') or {}).get('timeSeconds',0)>4)
  page.locator('.queue-item').filter(has_text=id[:8]).click();page.wait_for_timeout(300)
  checks['offHasNoAccountingTable']=page.get_by_role('heading',name='Force and work attribution').count()==0
  checks['offNoticeVisible']=page.get_by_text('Force/energy ledger disabled.',exact=False).is_visible()
  page.get_by_role('button',name='Pause',exact=True).click()
  wait(id,lambda v:v['execution']=='Paused' and (v.get('workerStatus') or {}).get('paused'))
  time.sleep(.3);tick=current(id)['workerStatus']['tick'];time.sleep(.8)
  checks['pauseStopsProbeClock']=current(id)['workerStatus']['tick']==tick
  page.screenshot(path=str(out/'ledger-off-paused.png'),full_page=True,animations='disabled')
  page.get_by_role('button',name='Resume',exact=True).click();done(id)
  page.screenshot(path=str(out/'ledger-off-complete.png'),full_page=True,animations='disabled')
  cancel=enqueue('Probe-only cancellation',observation='off',durationSeconds=12)
  wait(cancel,lambda v:v['execution']=='Running' and (v.get('workerStatus') or {}).get('timeSeconds',0)>3)
  post('/api/attempts/'+cancel+'/cancel',{})
  v=wait(cancel,lambda v:v['execution'] in ['Cancelled','Failed']);runs.append(v)
  checks['cancellationPreservesProbe']=v['execution']=='Cancelled' and v['validation']=='NotReady' and (Path(v['archivePath'])/'probe.rort').exists();save()
  full=enqueue('Slice 03 native full-ledger evidence',durationSeconds=12)
  wait(full,lambda v:v['execution']=='Running' and (v.get('latest') or {}).get('timeSeconds',0)>6)
  page.locator('.queue-item').filter(has_text=full[:8]).click();page.wait_for_timeout(300)
  page.screenshot(path=str(out/'full-ledger-live.png'),full_page=True,animations='disabled')
  v=done(full)
  checks['nativeEvidenceAttempt']=v['id']
  page.wait_for_timeout(250);page.screenshot(path=str(out/'full-ledger-complete.png'),full_page=True,animations='disabled')
 page.goto(base,wait_until='load');page.get_by_label('Observation profile').wait_for()
 page.set_viewport_size(dict(width=390,height=844));page.wait_for_timeout(300)
 checks['mobileNoPageOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 page.screenshot(path=str(out/'mobile-workbench.png'),full_page=True)
 checks['browserNoErrors']=not errors;browser.close()
save()
assert all(checks.values()),checks
if a.phase=='benchmark':
 assert all(v['bitwiseStateEquivalent'] for v in comparisons.values()),comparisons
print(json.dumps(dict(evidence=str(out),checks=checks,comparisons=comparisons)),flush=True)
