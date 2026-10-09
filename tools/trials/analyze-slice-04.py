"""Streaming independent analysis of real committed native detail frames."""
import argparse,json,struct,zlib,math,hashlib,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--session',required=True);a=p.parse_args();root=Path(a.session);out=root/'report'/'analysis-04';out.mkdir(exist_ok=True)
def frames(path):
 with path.open('rb') as f:
  assert f.read(8)==b'RORDTAIL';schema,n,b,cap,pre,post=struct.unpack('<6I',f.read(24));assert schema==1 and pre==4000 and post==8000
  while True:
   marker=f.read(4)
   if marker!=b'DATA':break
   count,size,crc=struct.unpack('<3I',f.read(12));raw=f.read(size)
   if count!=1 or len(raw)!=size or zlib.crc32(raw)!=crc or f.read(4)!=b'DONE':break
   yield raw,n,b
result=[]
for path in sorted((root/'archive').glob('*/result.json')):
 v=json.loads(path.read_text(encoding='utf-8-sig'))
 if v['definition']['scenario']!='barrier-v1' or v['capture']!='Complete' or 'repeat matrix' not in v['definition']['name']:continue
 detail=path.parent/'detail.rort';data=[];max_channel_error=0;max_impulse_error=0;count=0;impulse=[0,0,0];peak=0;peak_net=0
 for raw,n,b in frames(detail):
  tick,dt=struct.unpack_from('<Qd',raw);cc=struct.unpack_from('<I',raw,28)[0];net=[0.,0.,0.]
  for i in range(n):
   at=128+i*256;mass=struct.unpack_from('<f',raw,at+8)[0]
   before=struct.unpack_from('<3f',raw,at+28);after=struct.unpack_from('<3f',raw,at+40);force=struct.unpack_from('<3f',raw,at+52)
   channels=struct.unpack_from('<48f',raw,at+64)
   max_channel_error=max(max_channel_error,math.dist(force,[sum(channels[j::3]) for j in range(3)]))
   if not struct.unpack_from('<I',raw,at+4)[0]:max_impulse_error=max(max_impulse_error,math.sqrt(sum((mass*(after[j]-before[j])-force[j]*dt)**2 for j in range(3))))
  for i in range(cc):
   at=128+n*256+b*112+i*104
   if not struct.unpack_from('<I',raw,at+12)[0]:continue
   f=struct.unpack_from('<3f',raw,at+64);peak=max(peak,math.sqrt(sum(x*x for x in f)))
   for j in range(3):net[j]+=f[j];impulse[j]+=f[j]*dt
  peak_net=max(peak_net,math.sqrt(sum(x*x for x in net)));count+=1
  data.append(dict(tick=tick,timeSeconds=tick*dt,netBarrierForceN=net,kineticJ=struct.unpack_from('<d',raw,96)[0],frontDistanceM=struct.unpack_from('<d',raw,112)[0]))
 expected=v['metrics']['impactDetail'];assert count==expected['records']==12001
 assert math.isclose(peak,expected['peakApplicationForceN'],rel_tol=1e-12) and math.isclose(peak_net,expected['peakNetBarrierForceN'],rel_tol=1e-12)
 assert math.dist(impulse,expected['barrierImpulseNs'])<1e-8
 record=dict(id=v['id'],target=v['definition']['targetImpactSpeedMps'],records=count,bytes=detail.stat().st_size,maxFloat32ChannelReconstructionErrorN=max_channel_error,maxNodeMomentumKickResidualKgMps=max_impulse_error,peakApplicationForceN=peak,peakNetBarrierForceN=peak_net,barrierImpulseNs=impulse)
 result.append(record)
 # Compact actual per-tick series for plotting; every frame is retained, no force peak decimation.
 (out/(v['id']+'-series.json')).write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
 (out/'checks.json').write_text(json.dumps(dict(runs=result,scope='Independent raw magic/schema/CRC/DONE, force/impulse reduction and disclosed float32 reconstruction error; cohort/finite/window/footer validation is performed by DetailReader; not vehicle scientific qualification'),indent=2),encoding='utf-8')
 print(json.dumps(record),flush=True)
print(str(out),flush=True)
