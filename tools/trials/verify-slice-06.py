"""Fresh-process performance, required-capture and recorder-health qualification.
Every invocation retains a unique result directory. Baseline must run before rebuilding.
"""
import argparse, json, time, urllib.request, hashlib, struct, zlib, statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--base',default='http://127.0.0.1:54326');p.add_argument('--phase',choices=['baseline','optimized','cadence-d','visual'],required=True);a=p.parse_args()
root=Path(a.session).resolve();out=root/'report'/('verification-06-'+a.phase+'-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
def get(path):return json.load(urllib.request.urlopen(a.base+path,timeout=30))
token=get('/api/session')['session']
def post(path,data):
 r=urllib.request.Request(a.base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Trials-Session':token},method='POST')
 return json.load(urllib.request.urlopen(r,timeout=30))
runs=[];live={};checks={};exe=hashlib.sha256((root/'build/bin/RoR.exe').read_bytes()).hexdigest().upper()
def save():
 (out/'checks.json').write_text(json.dumps(dict(phase=a.phase,executableSha256=exe,runs=runs,live=live,checks=checks,evidence=str(out)),indent=2),encoding='utf-8')
def run(name,**extra):
 d=dict(name='Slice06 '+a.phase+' '+name,scenario='coast-v1',vehicle='b6b0UID-semi.truck',launchSpeedMps=5,settleSeconds=2,durationSeconds=3,performanceProbe=True,observation='full',accounting=True,environment=dict(gravity=-9.81));d.update(extra)
 id=post('/api/experiments',d)['attemptIds'][0];live[id]=[];save();end=time.time()+700
 while time.time()<end:
  v=get('/api/attempts/'+id+'/status')
  s=v.get('workerStatus') or {};q=v.get('detailProgress') or {}
  if s or q:live[id].append(dict(wall=time.time(),execution=v['execution'],workerStatus=s,detailProgress=q,recorderHealth=v.get('recorderHealth')))
  if v['execution'] in ['Completed','Failed','Cancelled']:break
  time.sleep(.3)
 else:raise AssertionError(('timeout',id,v['execution']))
 runs.append(v);save();print(json.dumps(dict(id=id,name=name,execution=v['execution'],capture=v['capture'],timing=v.get('metrics',{}).get('performanceProbe'))),flush=True)
 assert v['executableSha256']==exe
 prov=json.loads((Path(v['archivePath'])/'process-provenance.json').read_text(encoding='utf-8-sig'))
 assert prov['observedExe'].lower()==prov['expectedExe'].lower()
 assert all(not m.lower().startswith('d:\\rigs of rods\\') or m.lower().startswith(str(Path(v['archivePath'])/'worker').lower()) for m in prov['modules'])
 assert v['execution']=='Completed',v['events'][-2:]
 return v
if a.phase=='optimized':
 v=run('phase profile',observerProfiling=True);assert v['capture']=='Complete' and v['metrics']['observerProfile']['steps']==10000;checks['phaseProfile']=v['id']
for mode in ([] if a.phase in ['cadence-d','visual'] else ['off','full','full','off','off','full']):
 v=run('coast '+mode,observation=mode);assert v['capture']=='Complete' and v['validation']=='NotReady'
barrier=dict(scenario='barrier-v1',launchSpeedMps=6.2,targetImpactSpeedMps=5,barrierDistanceM=12,settleSeconds=3,durationSeconds=9)
v=run('whole-pilot barrier',**barrier)
assert v['capture']=='Complete' and v['metrics']['impactQualification']['status']=='Passed' and v['metrics']['impactDetail']['records']==12001
checks['healthyBarrierRequiredFrames']=12001
if a.phase=='optimized':
 v=run('partial-write fault',**barrier,detailFault='storage-error');detail=v['metrics']['impactDetail']
 assert v['capture']=='Incomplete' and v['validation']=='NotReady' and detail['lastTick']>=detail['triggerTick']+8000 and detail['records']==12000
 checks['partialWriteStickyLossAndLaterFrames']=True
 # Small independent successor, also qualifies phase profiling without affecting timing budget runs.
 checks['independentSuccessor']='The following freefall fixture must complete after the failed required capture.'
 for scenario,duration in [('freefall-v1',.5),('spring-v1',1),('damper-v1',5),('yield-tension-v1',.2)]:
  v=run('unchanged reference '+scenario,scenario=scenario,vehicle='ror-'+scenario+'.truck',launchSpeedMps=0,settleSeconds=0,durationSeconds=duration,environment=dict(gravity=-9.81 if scenario=='freefall-v1' else 0))
  assert v['capture']=='Complete' and v['validation']=='Passed'
 checks['referenceRegression']=True
identities=[(v['processId'],json.loads((Path(v['archivePath'])/'process-provenance.json').read_text(encoding='utf-8-sig'))['startTimeUtc']) for v in runs]
checks['allSeparateProcesses']=len(set(identities))==len(runs)
save();print(str(out),flush=True)
