"""Dated Slice 03 native evidence report; charts use measured raw records."""
import argparse,json,struct,zlib,statistics,html,shutil
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--repo',required=True);a=p.parse_args()
root=Path(a.session).resolve();repo=Path(a.repo).resolve();report=root/'report';plots=report/'plots';plots.mkdir(exist_ok=True)
bench=json.loads(sorted(report.glob('verification-03-benchmark-*/checks.json'))[-1].read_text(encoding='utf-8'))
visual=json.loads(sorted(report.glob('verification-03-visual-*/checks.json'))[-1].read_text(encoding='utf-8'))
assert all(bench['checks'].values()) and all(visual['checks'].values())
runs=bench['runs']+visual['runs']
def records(v,name):
 with (Path(v['archivePath'])/name).open('rb') as f:
  f.read(8);schema,size=struct.unpack('<II',f.read(8));rows=[]
  while True:
   tag=f.read(4)
   if tag==b'END!':break
   assert tag==b'DATA';n,length,crc=struct.unpack('<III',f.read(12));raw=f.read(length)
   assert len(raw)==n*size and zlib.crc32(raw)==crc and f.read(4)==b'DONE'
   rows.extend(raw[i*size:(i+1)*size] for i in range(n))
 return rows
# Independently verify complete sentinel bytes, including signed-zero encodings.
for comparison in bench['comparisons'].values():
 left,right=[next(v for v in bench['runs'] if v['id']==id) for id in comparison['attemptIds']]
 xx,yy=records(left,'probe.rort'),records(right,'probe.rort')
 mismatches=sum(x[40:88]!=y[40:88] for x,y in zip(xx,yy))
 assert len(xx)==len(yy) and mismatches==0
 comparison['sentinelByteMismatches']=mismatches
performance={}
plt.rcParams.update({'figure.facecolor':'#f5f8fa','axes.facecolor':'white','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(10,4.5))
for i,speed in enumerate([5,15]):
 perf={}
 for j,mode in enumerate(['off','full']):
  subset=[v for v in bench['runs'] if v['definition']['name']==f'Performance {speed} mps {mode}']
  times=[struct.unpack_from('<d',r,32)[0] for v in subset for r in records(v,'probe.rort') if struct.unpack_from('<I',r,8)[0]==1]
  medians=[v['metrics']['performanceProbe']['medianUs'] for v in subset];times.sort()
  perf[mode]=dict(steps=len(times),repeats=len(subset),medianUs=statistics.median(times),p95Us=times[int((len(times)-1)*.95)],meanUs=statistics.mean(times),repeatMedianUs=medians)
  ax.bar(i*3+j,perf[mode]['medianUs'],width=.75,color='#167f8b' if mode=='off' else '#b76a27',label=mode if i==0 else None)
  ax.vlines(i*3+j,min(medians),max(medians),color='#182f48',lw=3)
  ax.text(i*3+j,perf[mode]['medianUs']+2,f"{perf[mode]['medianUs']:.1f}",ha='center')
 perf['medianRatio']=perf['full']['medianUs']/perf['off']['medianUs'];perf['additionalPercent']=(perf['medianRatio']-1)*100
 performance[str(speed)]=perf
 ax.hlines(perf['off']['medianUs']*1.1,i*3-.5,i*3+1.5,color='#922f32',ls='--',label='Proposed 10% ceiling' if i==0 else None)
ax.set_xticks([.5,3.5],['5 m/s release','15 m/s release']);ax.set_ylabel('Steady-clock step elapsed / microseconds')
ax.set_title('Native Daf coast: same executable, interleaved profiles, 3 repeats each');ax.set_ylim(0,100)
ax.legend(loc='upper left',ncol=3,fontsize=9);fig.tight_layout();fig.savefig(plots/'observer-cost.png',dpi=180);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(12,4))
for mode,color in [('off','#167f8b'),('full','#b76a27')]:
 v=next(x for x in bench['runs'] if x['definition']['name']==f'Performance 15 mps {mode}')
 rr=records(v,'probe.rort')[::20];tt=[struct.unpack_from('<Q',r)[0]*struct.unpack_from('<d',r,24)[0] for r in rr]
 for ax,vals in [(axs[0],[struct.unpack_from('<d',r,56)[0] for r in rr]),(axs[1],[(sum(struct.unpack_from('<d',r,o)[0]**2 for o in [64,72,80]))**.5 for r in rr])]:
  ax.plot(tt,vals,color=color,label=mode,lw=3 if mode=='off' else 1.2,ls='-' if mode=='off' else '--')
for ax in axs:ax.set_xlabel('Native time / seconds');ax.legend();ax.grid(alpha=.2)
axs[0].set_ylabel('Node 0 world Z / m');axs[1].set_ylabel('Node 0 speed / m/s')
fig.suptitle('Ledger on/off state traces coincide; Y-up world axes');fig.tight_layout();fig.savefig(plots/'native-equivalence.png',dpi=180);plt.close(fig)
old=json.loads((repo/'doc/project/slices/slice-02-results.json').read_text(encoding='utf-8'))
regressions={}
for sc in ['freefall-v1','spring-v1','damper-v1']:
 v=next(x for x in bench['runs'] if x['definition']['scenario']==sc and x['definition']['observation']=='full')
 prev=next(x for x in old['runs'] if x['definition']['scenario']==sc and x['validation']=='Passed')
 xx=records(v,'steps.rort');yy=records(prev,'steps.rort');diff=0;assert len(xx)==len(yy),(sc,len(xx),len(yy))
 for x,y in zip(xx,yy):
  for offset in list(range(24,1256,8))+list(range(1264,1336,8)):
   diff=max(diff,abs(struct.unpack_from('<d',x,offset)[0]-struct.unpack_from('<d',y,offset)[0]))
 regressions[sc]=dict(records=len(xx),maxDifferenceSI=diff,oldAttempt=prev['id'],newAttempt=v['id'])
 assert diff<1e-7,(sc,diff)
summary=dict(date='2026-10-09',session=str(root),nativeSha256=runs[0]['executableSha256'],performance=performance,comparisons=bench['comparisons'],fixtureAccountingRegression=regressions,
 checks=dict(benchmark=bench['checks'],visual=visual['checks']),runs=[{k:v[k] for k in ['id','definition','execution','capture','validation','processId','archivePath','executableSha256','metrics']} for v in runs],
 limitations=['Proposed <=10% overhead target not met','Ledger-off retains the common control probe; not unmodified upstream','10 Hz diagnostic fingerprints are not every-tick full-state equality','Vehicle/impact/environment closure NotReady','Two scheduled screenshots in benchmark profiles; continuous frames only visual phase','Codex in-app GPU video playback unverified; image fallback is primary'])
(report/'results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
(repo/'doc/project/slices/slice-03-results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
h=lambda v:html.escape(str(v))
costRows=''.join(f"<tr><td>{s} m/s</td><td>{p['off']['medianUs']:.1f} / {p['off']['p95Us']:.1f}</td><td>{p['full']['medianUs']:.1f} / {p['full']['p95Us']:.1f}</td><td>{p['medianRatio']:.3f}x (+{p['additionalPercent']:.1f}%)</td><td>{p['full']['steps']:,} / mode</td></tr>" for s,p in performance.items())
comparisonRows=''.join(f"<tr><td>{h(label)}</td><td>{c['records']:,}</td><td>{c['sentinelMaxPositionDifferenceM']:g} / {c['sentinelMaxVelocityDifferenceMps']:g}</td><td>{c['fullNodeBeamFingerprints']}</td><td>{c['fingerprintMismatches']}</td></tr>" for label,c in bench['comparisons'].items())
runRows=''.join(f"<tr><td><code>{v['id'][:8]}</code><br>{h(v['definition']['name'])}</td><td>{h(v['definition']['observation'])}{' / base' if not v['definition']['accounting'] else ''}</td><td>{v['execution']}</td><td>{v['capture']}</td><td>{v['validation']}</td><td>{v['processId']}</td></tr>" for v in runs)
native=sorted((root/'media/final/native-renderer-frames').glob('*.png'));assert len(native)>=8
shots=report/'images';shots.mkdir(exist_ok=True)
for tag,src in [('native-start',native[min(15,len(native)-1)]),('native-middle',native[len(native)//2]),('native-end',native[-1])]:shutil.copy2(src,shots/(tag+'.png'))
for name in ['full-ledger-live.png','ledger-off-paused.png','ledger-off-complete.png','mobile-workbench.png']:shutil.copy2(Path(visual['evidence'])/name,shots/name)
for name in ['spring-v1-qualified.png','damper-v1-qualified.png']:shutil.copy2(Path(bench['evidence'])/name,shots/name)
page=(repo/'tools/trials/slice-03-report.html').read_text(encoding='utf-8')
for key,value in {'COUNT_COMPLETE':sum(v['execution']=='Completed' for v in runs),'COUNT_PASSED':sum(v['validation']=='Passed' for v in runs),'COST_ROWS':costRows,'COMPARISON_ROWS':comparisonRows,'RUN_ROWS':runRows,'REGRESSION_MAX':max(v['maxDifferenceSI'] for v in regressions.values()),'REGRESSION_RECORDS':sum(v['records'] for v in regressions.values()),'NATIVE_SHA':summary['nativeSha256'],'SESSION_PATH':h(root)}.items():page=page.replace(key,str(value))
(report/'index.html').write_text(page,encoding='utf-8')
repoPage=page
for name in ['slice-03-evidence.zip','results.json','publication.json','sha256-manifest.json']:repoPage=repoPage.replace(f'href="{name}"',f'href="{(report/name).as_uri()}"')
for folder in ['plots','images']:
 for attr in ['src','href']:repoPage=repoPage.replace(f'{attr}="{folder}/',f'{attr}="{(report/folder).as_uri()}/')
repoPage=repoPage.replace('../media/slice-03-final-native/',(root/'media/slice-03-final-native').as_uri()+'/')
(repo/'doc/project/reports/trial-slice-03-2026-10-09.html').write_text(repoPage,encoding='utf-8')
print(json.dumps(dict(performance=performance,accountingRegression=regressions,runs=len(runs))))
