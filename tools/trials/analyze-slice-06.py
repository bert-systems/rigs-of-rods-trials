"""Independent CRC/layout, exact-state/accounting equivalence and resource analysis."""
import argparse,json,struct,zlib,hashlib,statistics,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--session',required=True);a=p.parse_args();root=Path(a.session).resolve()
out=root/'report'/('analysis-06-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
base=read(sorted((root/'report').glob('verification-06-baseline-*/checks.json'))[-1]);opt=read(sorted((root/'report').glob('verification-06-optimized-*/checks.json'))[-1])
prototype=read(sorted((root/'report').glob('verification-06-prototype-*/checks.json'))[-1])
cadence=read(sorted((root/'report').glob('verification-06-cadence-d-*/checks.json'))[-1])
def records(v,name):
 with (Path(v['archivePath'])/name).open('rb') as f:
  magic=f.read(8);schema,size=struct.unpack('<II',f.read(8));count=0
  assert (magic,schema,size) in [(b'RORPROBE',1,128),(b'RORTRIAL',2,2080)]
  while True:
   tag=f.read(4)
   if tag==b'END!':
    n,lost,io=struct.unpack('<QQI',f.read(20));assert n==count and not lost and not io and not f.read();return
   assert tag==b'DATA';n,length,crc=struct.unpack('<III',f.read(12));data=f.read(length)
   assert n<=128 and length==n*size and zlib.crc32(data)==crc and f.read(4)==b'DONE'
   for i in range(n):count+=1;yield data[i*size:(i+1)*size]
comparisons=[]
def compare(x,y,aggregate=False):
 name='steps.rort' if aggregate else 'probe.rort';xx=list(records(x,name));yy=list(records(y,name));assert len(xx)==len(yy)
 offsets=(1256,1264) if aggregate else (32,40);diff=0;hashes=0;sha=hashlib.sha256()
 for r,s in zip(xx,yy):
  rr=r[:offsets[0]]+r[offsets[1]:];ss=s[:offsets[0]]+s[offsets[1]:]
  diff+=rr!=ss;sha.update(rr)
  if not aggregate and struct.unpack_from('<I',r,96)[0]:hashes+=1
 result=dict(kind='all accounting bytes except declared timer' if aggregate else 'every-tick sentinel/metadata plus sampled diagnostic fingerprint',attempts=[x['id'],y['id']],records=len(xx),mismatches=diff,fingerprints=hashes,normalizedSha256=sha.hexdigest())
 comparisons.append(result);assert diff==0,result
def coasts(d,mode):return [v for v in d['runs'] if v['definition']['name'].endswith('coast '+mode)]
for d in [base,prototype,opt]:
 for x,y in zip(coasts(d,'off'),coasts(d,'full')):compare(x,y)
for mode in ['full','off']:
 for x,y in zip(coasts(base,mode),coasts(opt,mode)):
  compare(x,y)
  if mode=='full':compare(x,y,True)
def barrier(d):return next(v for v in d['runs'] if v['definition']['name'].endswith('whole-pilot barrier'))
x,y=barrier(base),barrier(opt);compare(x,y);compare(x,y,True)
compare(barrier(base),barrier(cadence));compare(barrier(base),barrier(cadence),True)
detail=[]
for v in [x,barrier(prototype),barrier(cadence),y,next(v for v in opt['runs'] if v['definition']['detailFault']=='storage-error')]:
 sha=hashlib.sha256();count=0;payload=0;first=last=0;gaps=[];contacts=0
 with (Path(v['archivePath'])/'detail.rort').open('rb') as f:
  assert f.read(8)==b'RORDTAIL';schema,nodes,beams,cap,pre,post=struct.unpack('<IIIIII',f.read(24));assert (schema,nodes,beams,cap,pre,post)==(1,176,744,736,4000,8000)
  while True:
   tag=f.read(4)
   if tag==b'END!':
    n,lost,missing,io=struct.unpack('<QQQI',f.read(28));assert n==count and not f.read();break
   assert tag==b'DATA';n,length,crc=struct.unpack('<III',f.read(12));data=f.read(length)
   assert n==1 and zlib.crc32(data)==crc and f.read(4)==b'DONE'
   tick,dt=struct.unpack_from('<Qd',data);nn,bb,cc=struct.unpack_from('<III',data,20)
   assert nn==nodes and bb==beams and cc<=cap and length==128+nn*256+bb*112+cc*104
   if last and tick!=last+1:gaps.append([last,tick])
   first=first or tick;last=tick;contacts+=cc;count+=1;payload+=length;sha.update(data)
 d=dict(attempt=v['id'],records=count,first=first,last=last,dropped=lost,missing=missing,ioError=io,gaps=gaps,contacts=contacts,payloadBytes=payload,payloadSha256=sha.hexdigest());detail.append(d)
 print(json.dumps(d),flush=True)
 if v['definition']['detailFault']=='none':assert count==12001 and not lost and not missing and not io and not gaps
 else:assert count==12000 and missing==1 and io==1 and len(gaps)==1
assert len({d['payloadSha256'] for d in detail[:4]})==1,'Dense data changed across optimization'
health=[]
for v in opt['runs']:
 h=read(Path(v['archivePath'])/'recorder-health.json');assert h==v['recorderHealth']
 for name,s in h.items():
  if name=='schema' or s is None:continue
  assert s['closed'] and s['queued']==0 and s['highWater']<=s['capacity'] and s['pendingSync']==0 and s['written']==s['durable']
  assert s['enqueued']==s['processed'] and s['archiveBytes']>0 and s['syncCalls']>=3
  fileName={'aggregate':'steps.rort','probe':'probe.rort','detail':'detail.rort'}[name]
  assert (Path(v['archivePath'])/fileName).stat().st_size==s['archiveBytes']+(64 if name=='detail' else 40)
 health.append(dict(attempt=v['id'],recorders=h))
timings={}
for name,d in [('baseline',base),('prototypeSameDrive',prototype),('optimized',opt)]:
 timings[name]={}
 for mode in ['off','full']:
  runs=coasts(d,mode);timings[name][mode]=dict(mediansUs=[v['metrics']['performanceProbe']['medianUs'] for v in runs],p95Us=[v['metrics']['performanceProbe']['p95Us'] for v in runs])
  timings[name][mode]['medianOfMediansUs']=statistics.median(timings[name][mode]['mediansUs'])
 timings[name]['overheadRatio']=timings[name]['full']['medianOfMediansUs']/timings[name]['off']['medianOfMediansUs']
 b=barrier(d);timings[name]['barrier']=dict(stepMedianUs=b['metrics']['performanceProbe']['medianUs'],p95Us=b['metrics']['performanceProbe']['p95Us'],workerWallSeconds=b['metrics']['workerWallSeconds'],physicsFinishedWallSeconds=b['metrics'].get('observedPhysicsFinishedWallSeconds'))
h=read(Path(y['archivePath'])/'recorder-health.json')['detail'];produced=y['workerStatus']['produced'];stride=read(Path(y['archivePath'])/'detail-profile.json')['strideBytes']
copy=dict(fullStrideBytes=stride*produced,populatedBytes=h['copiedBytes'],reductionFraction=1-h['copiedBytes']/(stride*produced),reservedQueueBytes=h['reservedQueueBytes'],historyBytes=read(Path(y['archivePath'])/'detail-profile.json')['historyBytes'])
crc=json.loads((root/'report'/'crc-benchmark.txt').read_text(encoding='utf-8-sig').splitlines()[-1]);crc['speedup']=statistics.median(crc['byteTableMs'])/statistics.median(crc['slicing8Ms'])
db=barrier(cadence);timings['finalSameDriveBarrier']=dict(stepMedianUs=db['metrics']['performanceProbe']['medianUs'],p95Us=db['metrics']['performanceProbe']['p95Us'],workerWallSeconds=db['metrics']['workerWallSeconds'],physicsFinishedWallSeconds=db['metrics'].get('observedPhysicsFinishedWallSeconds'),recorder=db['recorderHealth']['detail'])
result=dict(baselineEvidence=base['evidence'],optimizedEvidence=opt['evidence'],baselineSha256=base['executableSha256'],optimizedSha256=opt['executableSha256'],prototypeSha256=prototype['executableSha256'],timings=timings,comparisons=comparisons,detail=detail,health=health,copy=copy,crc=crc,phaseProfile=next(v['metrics']['observerProfile'] for v in opt['runs'] if v['definition']['observerProfiling']),proposedAggregateBudgetPassed=timings['optimized']['overheadRatio']<=1.1,detailBudget='Unqualified: no barrier off profile; one before/after detail run each',scope='5 m/s single-pilot coast; fixed 5 m/s barrier; diagnostic fingerprints are not full engine checkpoints. Baseline and prototype coast, plus final cadence barrier, use D. Final repeated coast qualification uses C; cross-volume wall changes are confounded.')
(out/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(str(out),flush=True)
