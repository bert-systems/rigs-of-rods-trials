"""Real source-built barrier qualification. Retains every attempt, including failures."""
import argparse,json,time,urllib.request,hashlib,os,signal,ctypes
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--base',default='http://127.0.0.1:54324');p.add_argument('--phase',default='spike',choices=['spike','matrix','faults','controls','regression']);p.add_argument('--speed',type=float,default=5);p.add_argument('--release',type=float);p.add_argument('--distance',type=float);a=p.parse_args()
root=Path(a.session).resolve();out=root/'report'/('verification-04-'+a.phase+'-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
base=a.base
def get(path):return json.load(urllib.request.urlopen(base+path,timeout=30))
token=get('/api/session')['session']
def post(path,data):
 req=urllib.request.Request(base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Trials-Session':token},method='POST')
 return json.load(urllib.request.urlopen(req,timeout=30))
def current(id):return get('/api/attempts/'+id+'/status')
def wait(id,fn,seconds=900):
 end=time.time()+seconds
 while time.time()<end:
  v=current(id)
  if fn(v):return v
  time.sleep(.2)
 raise AssertionError((id,v['execution'],v['events'][-2:]))
runs=[];checks={}
def save():
 (out/'checks.json').write_text(json.dumps(dict(phase=a.phase,runs=runs,checks=checks,evidence=str(out)),indent=2),encoding='utf-8')
def enqueue(name,**extra):
 d=dict(name=name,scenario='barrier-v1',vehicle='b6b0UID-semi.truck',launchSpeedMps=a.release or a.speed,targetImpactSpeedMps=a.speed,
  barrierDistanceM=a.distance or a.speed*2.4,durationSeconds=9,settleSeconds=3,repeats=1,performanceProbe=True,accounting=True,observation='full',environment=dict(gravity=-9.81),detailFault='none')
 d.update(extra);return post('/api/experiments',d)['attemptIds']
def done(id):
 v=wait(id,lambda v:v['execution'] in ['Completed','Failed','Cancelled']);runs.append(v);save()
 prov=json.loads((Path(v['archivePath'])/'process-provenance.json').read_text(encoding='utf-8-sig'))
 assert prov['observedExe'].lower()==prov['expectedExe'].lower()
 assert v['executableSha256']==hashlib.sha256((root/'build/bin/RoR.exe').read_bytes()).hexdigest().upper()
 assert all(not m.lower().startswith('d:\\rigs of rods\\') or m.lower().startswith(str(Path(v['archivePath'])/'worker').lower()) for m in prov['modules'])
 print(json.dumps(dict(id=id,execution=v['execution'],capture=v['capture'],science=v['validation'],impact=v['metrics'].get('impactQualification'),detail=v['metrics'].get('impactDetail'))),flush=True)
 return v
if a.phase=='spike':
 done(enqueue('Barrier setup qualification spike')[0])
elif a.phase=='matrix':
 for id in enqueue(f'Barrier {a.speed:g} mps / repeat matrix',repeats=5):
  v=done(id);assert v['execution']=='Completed' and v['capture']=='Complete' and v['metrics']['impactQualification']['status']=='Passed',v['metrics']
 checks['fiveSeparateProcesses']=len(set(v['processId'] for v in runs))==5
elif a.phase=='faults':
 for fault in ['short-history','queue-overflow','storage-error']:
  ids=enqueue('Barrier injected '+fault,detailFault=fault)
  successor=enqueue('Barrier independent queue successor '+fault)[0]
  bad=done(ids[0]);assert bad['execution']=='Completed' and bad['capture']=='Incomplete' and bad['validation']=='NotReady'
  assert bad['metrics']['impactDetail']['lastTick']>bad['metrics']['impactDetail']['triggerTick']+1000
  good=done(successor);assert good['execution']=='Completed' and good['capture']=='Complete'
  checks[fault]=dict(continuedAfterLoss=True,independentSuccessor=successor)
elif a.phase=='regression':
 for scenario,duration in [('freefall-v1',.5),('spring-v1',1),('damper-v1',5)]:
  v=done(enqueue('Slice 04 regression '+scenario,scenario=scenario,vehicle='ror-'+scenario+'.truck',launchSpeedMps=0,settleSeconds=0,durationSeconds=duration,environment=dict(gravity=0 if scenario!='freefall-v1' else -9.81))[0]);assert v['capture']=='Complete' and v['validation']=='Passed'
elif a.phase=='controls':
 id=enqueue('Barrier tick-safe pause / resume')[0]
 wait(id,lambda v:v['execution']=='Running' and (v.get('workerStatus')or{}).get('timeSeconds',0)>4)
 post('/api/attempts/'+id+'/pause',{});paused=wait(id,lambda v:v['execution']=='Paused' and (v.get('workerStatus')or{}).get('paused',False))
 tick=paused['workerStatus']['tick'];time.sleep(.6);assert current(id)['workerStatus']['tick']==tick
 post('/api/attempts/'+id+'/resume',{});v=done(id)
 assert v['execution']=='Completed' and v['capture']=='Complete';checks['pauseResume']=dict(pausedTick=tick,nativeClockStopped=True)
 id=enqueue('Barrier cancellation retains required prefix')[0]
 wait(id,lambda v:(v.get('workerStatus')or{}).get('detailTriggerTick',0)>0 and v['workerStatus']['tick']>v['workerStatus']['detailTriggerTick']+1500)
 post('/api/attempts/'+id+'/cancel',{});v=done(id)
 assert v['execution']=='Cancelled' and v['capture']=='Incomplete' and v['metrics']['impactDetail']['records']>4000
 checks['cancelPrefix']=dict(attempt=id,retainedFrames=v['metrics']['impactDetail']['records'])
 id=enqueue('Barrier abrupt worker exit')[0];successor=enqueue('Barrier after independent crashed worker')[0]
 active=wait(id,lambda v:(v.get('workerStatus')or{}).get('detailTriggerTick',0)>0 and v['workerStatus']['tick']>v['workerStatus']['detailTriggerTick']+2000)
 # Verify the live OS image path immediately before terminating this owned qualification process.
 kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.restype=ctypes.c_void_p
 handle=kernel.OpenProcess(0x1000,False,active['processId']);assert handle
 size=ctypes.c_ulong(32768);image=ctypes.create_unicode_buffer(size.value)
 kernel.QueryFullProcessImageNameW.argtypes=[ctypes.c_void_p,ctypes.c_ulong,ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_ulong)]
 assert kernel.QueryFullProcessImageNameW(handle,0,image,ctypes.byref(size));kernel.CloseHandle.argtypes=[ctypes.c_void_p];kernel.CloseHandle(handle)
 assert Path(image.value).resolve()==Path(active['processPath']).resolve();os.kill(active['processId'],signal.SIGTERM)
 bad=done(id);good=done(successor)
 assert bad['execution']=='Failed' and bad['capture']=='Incomplete' and not bad['metrics']['impactDetail']['closed']
 assert good['execution']=='Completed' and good['capture']=='Complete'
 post('/api/attempts/'+id+'/retry',{})
 retry=next(v for v in get('/api/state')['attempts'] if v['retryOf']==id);new=done(retry['id'])
 assert new['id']!=id and new['execution']=='Completed' and new['capture']=='Complete'
 checks['crashAndFreshRetry']=dict(crashed=id,successor=successor,manualRetry=new['id'],retainedVerifiedFrames=bad['metrics']['impactDetail']['records'])
save();print(str(out),flush=True)
