"""Run retained, source-built transition fixtures and unchanged analytical regressions."""
import argparse, hashlib, json, struct, time, urllib.request, urllib.error, zlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--base',default='http://127.0.0.1:54325');a=p.parse_args()
root=Path(a.session).resolve();out=root/'report'/('verification-05-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
def get(path):return json.load(urllib.request.urlopen(a.base+path,timeout=30))
token=get('/api/session')['session'];runs=[];checks={}
def save():
 (out/'checks.json').write_text(json.dumps(dict(runs=runs,checks=checks),indent=2),encoding='utf-8')
def post(path,data):
 return json.load(urllib.request.urlopen(urllib.request.Request(a.base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Trials-Session':token},method='POST'),timeout=30))
def records(path):
 data=path.read_bytes();assert data[:8]==b'RORTRIAL' and struct.unpack_from('<II',data,8)==(2,2080)
 at=16;result=[]
 while data[at:at+4]==b'DATA':
  n,size,crc=struct.unpack_from('<III',data,at+4);assert size==n*2080 and 0<n<=128
  block=data[at+16:at+16+size];assert zlib.crc32(block)==crc and data[at+16+size:at+20+size]==b'DONE'
  result.extend(block[i*2080:(i+1)*2080] for i in range(n));at+=20+size
 assert data[at:at+4]==b'END!' and len(data)==at+24
 assert struct.unpack_from('<QQI',data,at+4)==(len(result),0,0)
 assert [struct.unpack_from('<Q',r)[0] for r in result]==list(range(1,len(result)+1))
 return result
def run(scenario,duration):
 definition=dict(name=f'Slice 05 {scenario} / {duration:g}s',scenario=scenario,vehicle='ror-'+scenario+'.truck',launchSpeedMps=0,settleSeconds=0,
  durationSeconds=duration,repeats=1,performanceProbe=True,environment=dict(gravity=-9.81 if scenario=='freefall-v1' else 0))
 id=post('/api/experiments',definition)['attemptIds'][0];end=time.time()+120
 while time.time()<end:
  v=get('/api/attempts/'+id+'/status')
  if v['execution'] in ['Completed','Failed','Cancelled']:break
  time.sleep(.2)
 else:raise AssertionError(('worker timeout or resource hold',v))
 runs.append(v);save();print(json.dumps(dict(id=id,scenario=scenario,duration=duration,execution=v['execution'],capture=v['capture'],science=v['validation'],checks=v['metrics'].get('qualification'))),flush=True)
 archive=Path(v['archivePath']);prov=json.loads((archive/'process-provenance.json').read_text(encoding='utf-8-sig'))
 assert prov['observedExe'].lower()==prov['expectedExe'].lower()==str(archive/'worker/RoR.exe').lower()
 assert v['executableSha256']==hashlib.sha256((root/'build/bin/RoR.exe').read_bytes()).hexdigest().upper()
 assert all(not m.lower().startswith('d:\\rigs of rods\\') or m.lower().startswith(str(archive/'worker').lower()) for m in prov['modules'])
 assert v['execution']=='Completed' and v['capture']=='Complete' and v['validation']=='Passed',v['metrics']
 raw=records(archive/'steps.rort');assert len(raw)==round(duration/.0005)
 page=get('/api/attempts/'+id+'/transitions?offset=0&limit=1');assert len(page['events'])<=1 and page['projectionComplete']
 if scenario in ['yield-tension-v1','yield-compression-v1','fracture-v1','protected-beam-v1']:
  assert page['total']==1 and page['events'][0]['tick']==1 and page['events'][0]['beam']==0
  assert get('/api/attempts/'+id+'/transitions?offset=1&limit=1')['events']==[]
 for query in ['offset=-1&limit=20','offset=0&limit=101']:
  try:get('/api/attempts/'+id+'/transitions?'+query);raise AssertionError('invalid page accepted')
  except urllib.error.HTTPError as e:assert e.code==400
 (out/(id+'-transitions.json')).write_text(json.dumps(page,indent=2),encoding='utf-8')
 return v,raw
for scenario in ['yield-tension-v1','yield-compression-v1','fracture-v1','protected-beam-v1']:
 short,rs=run(scenario,.2);long,rl=run(scenario,1)
 # Independent exact-state prefix repeatability; observer timing and initialization ports are excluded.
 def state_digest(values):
  h=hashlib.sha256()
  for r in values:
   h.update(r[24:1184]);h.update(r[1216:1256]);h.update(r[1336:])
  return h.hexdigest()
 assert state_digest(rs)==state_digest(rl[:len(rs)]),'state prefix changed across fresh native workers'
 checks[scenario]=dict(short=short['id'],long=long['id'],exactStatePrefixSha256=state_digest(rs),prefixTicks=len(rs))
 save()
for scenario,duration in [('freefall-v1',.5),('spring-v1',1),('damper-v1',5)]:run(scenario,duration)
checks['elevenFreshNativeProcesses']=len(set(v['processId'] for v in runs))==11
checks['allCompleteScopedPassed']=all(v['capture']=='Complete' and v['validation']=='Passed' for v in runs)
checks['boundedPagesAndInvalidInputs']=True;save();print(str(out),flush=True)
