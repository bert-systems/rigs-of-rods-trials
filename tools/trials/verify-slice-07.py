"""Fresh native later-collision runs, original fixture regressions and exact repeats."""
import argparse,hashlib,json,struct,time,urllib.request,zlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--base',default='http://127.0.0.1:54328');p.add_argument('--phase',choices=['prototype','qualification'],required=True);a=p.parse_args()
root=Path(a.session).resolve();out=root/'report'/('verification-07-'+a.phase+'-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
def get(path):return json.load(urllib.request.urlopen(a.base+path,timeout=30))
token=get('/api/session')['session'];runs=[];live={};checks={};native=hashlib.sha256((root/'build/bin/RoR.exe').read_bytes()).hexdigest().upper()
def save():(out/'checks.json').write_text(json.dumps(dict(runs=runs,live=live,checks=checks,nativeSha256=native),indent=2),encoding='utf-8')
def post(path,d):return json.load(urllib.request.urlopen(urllib.request.Request(a.base+path,data=json.dumps(d).encode(),headers={'Content-Type':'application/json','X-Trials-Session':token},method='POST'),timeout=30))
def payloads(path,magic,record_bytes=None):
 with path.open('rb') as f:
  assert f.read(8)==magic
  f.read(24 if magic==b'RORDTAIL' else 8);result=[]
  while f.read(4)==b'DATA':
   n,size,crc=struct.unpack('<III',f.read(12));data=f.read(size);assert zlib.crc32(data)==crc and f.read(4)==b'DONE'
   result.extend([data[i*record_bytes:(i+1)*record_bytes] for i in range(n)] if record_bytes else [data])
  footer=f.read();assert len(footer)==(28 if magic==b'RORDTAIL' else 20)
  return result
def run(scenario,duration=7,fault='none'):
 impact=scenario.startswith('impact-');definition=dict(name=f'Slice 07 {a.phase} {scenario} {fault}',scenario=scenario,vehicle='ror-'+scenario+'.truck',launchSpeedMps=5 if impact else 0,settleSeconds=0,durationSeconds=duration,repeats=1,performanceProbe=True,barrierDistanceM=13 if impact else 12,detailFault=fault,environment=dict(gravity=-9.81 if scenario=='freefall-v1' else 0))
 id=post('/api/experiments',definition)['attemptIds'][0];live[id]=[];end=time.time()+180
 while time.time()<end:
  v=get('/api/attempts/'+id+'/status');live[id].append(dict(wall=time.time(),execution=v['execution'],capture=v['capture'],workerStatus=v.get('workerStatus'),recorderHealth=v.get('recorderHealth')))
  if v['execution'] in ['Completed','Failed','Cancelled']:break
  time.sleep(.25)
 else:raise AssertionError(('timeout or resource hold',v))
 runs.append(v);save();print(json.dumps(dict(id=id,scenario=scenario,fault=fault,execution=v['execution'],capture=v['capture'],science=v['validation'],qualification=v['metrics'].get('qualification'))),flush=True)
 archive=Path(v['archivePath']);prov=json.loads((archive/'process-provenance.json').read_text(encoding='utf-8-sig'))
 assert prov['observedExe'].lower()==prov['expectedExe'].lower()==str(archive/'worker/RoR.exe').lower() and v['executableSha256']==native
 assert all(not m.lower().startswith('d:\\rigs of rods\\') for m in prov['modules']),prov
 assert v['execution']=='Completed'
 if a.phase=='qualification':
  assert v['capture']==('Incomplete' if fault!='none' else 'Complete') and v['validation']==('NotReady' if fault!='none' else 'Passed'),v['metrics']
 if impact and fault=='none':
  d=v['metrics']['impactDetail'];assert d['complete'] and d['records']==12001 and d['triggerTick']>4000
 return v
if a.phase=='prototype':
 for s in ['impact-yield-v1','impact-fracture-v1']:run(s)
else:
 for s in ['impact-yield-v1','impact-fracture-v1']:
  pairs=[run(s) for _ in range(3)];dh=[];ah=[]
  for v in pairs:
   archive=Path(v['archivePath']);dense=payloads(archive/'detail.rort',b'RORDTAIL');aggregate=payloads(archive/'steps.rort',b'RORTRIAL',2080)
   dh.append(hashlib.sha256(b''.join(dense)).hexdigest())
   ah.append(hashlib.sha256(b''.join(r[:1256]+r[1264:] for r in aggregate)).hexdigest())
  assert len(set(dh))==len(set(ah))==1,'native repeats differ'
  checks[s]=dict(attempts=[v['id'] for v in pairs],detailPayloadSha256=dh[0],aggregateWithoutTimerSha256=ah[0],denseFrames=12001,aggregateTicks=14000)
 run('impact-yield-v1',fault='queue-overflow');run('impact-fracture-v1',fault='storage-error')
 for s,d in [('freefall-v1',.5),('spring-v1',1),('damper-v1',5),('yield-tension-v1',.2),('yield-compression-v1',.2),('fracture-v1',.2),('protected-beam-v1',.2)]:run(s,d)
 checks['fifteenFreshProcesses']=len(set((v['processId'],json.loads((Path(v['archivePath'])/'process-provenance.json').read_text(encoding='utf-8-sig'))['startTimeUtc']) for v in runs))==15
 checks['allDeclaredOutcomes']=True
save();print(str(out),flush=True)
