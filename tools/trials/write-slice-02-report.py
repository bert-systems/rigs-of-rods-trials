
from pathlib import Path
import json,html,shutil,hashlib,struct,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
root=Path(r'D:\Rigs of Rods\rigs-of-rods-trials');session=Path(r'D:\Rigs of Rods\trial-slice-02-2026-10-08-221217')
proof=session/'report/verification-20261008-230307'
results=json.loads((proof/'checks.json').read_text(encoding='utf-8'))
report=session/'report';pictures=report/'images';pictures.mkdir(exist_ok=True)
fixtures=[next(a for a in results['runs'] if a['definition']['scenario']==sc) for sc in ['freefall-v1','spring-v1','damper-v1']]
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f7faf7','axes.facecolor':'#ffffff'})
fig,axes=plt.subplots(1,3,figsize=(14,3.8),constrained_layout=True)
for a,ax in zip(fixtures,axes):
 sc=a['definition']['scenario'];data=[json.loads(line) for line in (Path(a['archivePath'])/'summaries.jsonl').read_text(encoding='utf-8').splitlines()]
 t=np.array([s['timeSeconds'] for s in data]);pos=np.array([s['centerM'][1 if sc=='freefall-v1' else 0] for s in data])
 pos=pos if sc=='freefall-v1' else pos-501
 ref=20-.5*9.81*t*t if sc=='freefall-v1' else .05*np.cos(10*t) if sc=='spring-v1' else .05*np.exp(-t)*(np.cos(math.sqrt(99)*t)+np.sin(math.sqrt(99)*t)/math.sqrt(99))
 ax.plot(t,pos,color='#077f79',linewidth=2,label='Native summary')
 ax.plot(t,ref,color='#ad653b',linewidth=1,linestyle='--',label='Continuous reference')
 ax.set(title=sc,xlabel='Simulated time / s',ylabel='Height / m' if sc=='freefall-v1' else 'Extension / m');ax.grid(alpha=.2)
axes[0].legend(fontsize=9);fig.savefig(pictures/'native-fixtures.svg');fig.savefig(pictures/'native-fixtures.png',dpi=150);plt.close(fig)
# Actual every-step mechanical balance and work, then reduce only for plotting.
fig,axes=plt.subplots(1,2,figsize=(12,3.8),constrained_layout=True)
for a,ax in zip(fixtures[1:],axes):
 file=(Path(a['archivePath'])/'steps.rort').open('rb');file.read(16);samples=[];work=0;initial=None
 while file.read(4)==b'DATA':
  n,size,crc=struct.unpack('<III',file.read(12));payload=file.read(size);assert file.read(4)==b'DONE'
  for i in range(n):
   r=payload[i*2080:(i+1)*2080];at=lambda off:struct.unpack_from('<d',r,off)[0]
   if initial is None:initial=at(136)+at(1136)+at(1152)
   work+=at(1176)+at(1232)+at(1240)
   tick=struct.unpack_from('<Q',r)[0]
   if tick%20==0:samples.append((tick*at(24),at(144)+at(1144)+at(1160)-work-initial))
 file.close()
 ax.plot([v[0] for v in samples],[v[1] for v in samples],color='#077f79',label='Δ mechanical storage − nonconservative work − ports')
 ax.axhline(0,color='#ad653b',linestyle='--');ax.set(title=a['definition']['scenario'],xlabel='Simulated time / s',ylabel='Cumulative discrepancy / J');ax.grid(alpha=.2)
fig.savefig(pictures/'native-energy.svg');fig.savefig(pictures/'native-energy.png',dpi=150);plt.close(fig)
for name in ['spring-qualified-workbench.png','coast-running.png','coast-result.png','workbench-mobile.png','fixture-acceptance-panel.png','wind-force-panel.png']:
 shutil.copy2(proof/name,pictures/name)
# Extract the scientific qualification panel into a readable standalone screenshot later; native renderer frame is already source-pinned.
shutil.copy2(proof/'native-renderer-frames/native-frame-0012.png',pictures/'native-source-scene.png')
def h(x):return html.escape(str(x))
def checks(a):
 return '<tr><td>'+h(a['definition']['scenario'])+'</td><td>'+str(a['metrics']['records'])+'</td><td>'+h(a['validation'])+'</td><td>'+str(a['metrics']['dropped'])+'</td></tr>'
tables=''.join(checks(a) for a in results['runs'])
perf=results['performance'];sha=results['runs'][0]['executableSha256']
def body(prefix):
 media_prefix=prefix.replace('/report/','/media/') if prefix else '../media/'
 # absolute file URL for repo HTML; relative files for portable session report
 video=(session/'media/slice-02-native/playback.html').as_uri() if prefix else '../media/slice-02-native/playback.html'
 recovery1=(session/'media/slice-01-recovered/playback.html').as_uri() if prefix else '../media/slice-01-recovered/playback.html'
 recovery0=(session/'media/baseline-recovered/playback.html').as_uri() if prefix else '../media/baseline-recovered/playback.html'
 def pic(name,alt):return '<figure><img src="'+prefix+'images/'+name+'" alt="'+h(alt)+'"><figcaption>'+h(alt)+'</figcaption></figure>'
 return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>RoR Trials · Slice 02 · Forces and core energy</title>
<style>body{margin:0;background:#f5f8f4;color:#173641;font:16px/1.6 system-ui}header{background:#13333d;color:#e6f3ef;padding:55px max(22px,calc((100vw - 1150px)/2))}main{max-width:1150px;margin:auto;padding:25px 22px 60px}h1{font-size:42px;line-height:1.15;margin:12px 0}h2{font-size:28px}h3{font-size:19px}p{max-width:1050px}section{padding:24px 0;border-bottom:1px solid #cbd9d3}a{color:#087d76}header a{color:#83e3d3}.eyebrow{font-size:12px;letter-spacing:2px;color:#9ddfd3}.badge{display:inline-block;padding:6px 13px;border-radius:20px;background:#28645f;margin-right:8px;font-size:13px}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.card{padding:20px;background:white;border:1px solid #d4dfd9;border-radius:9px}.card b{display:block;font-size:27px}.card small{color:#547078}.notice{background:#fff0d6;border-left:4px solid #bd862e;padding:18px 22px}.twocol{display:grid;grid-template-columns:1fr 1fr;gap:22px}table{border-collapse:collapse;width:100%;font-size:14px;background:white}th,td{padding:10px;text-align:left;border-bottom:1px solid #d4dfd9}th{background:#e3ece6}.scroll{overflow:auto}img{max-width:100%;border-radius:9px;border:1px solid #bacdc4}figure{margin:20px 0}figcaption,small{font-size:13px;color:#56727b}iframe{border:1px solid #36525f;width:100%;height:900px;border-radius:9px;background:#0b1620}code,pre{font:13px monospace;overflow-wrap:anywhere}pre{white-space:pre-wrap;background:#193640;color:#e0f2eb;padding:20px;border-radius:8px}svg{width:100%}.hash{overflow-wrap:anywhere;font:12px monospace}nav{display:flex;gap:20px;flex-wrap:wrap}footer{margin-top:30px;font-size:13px;color:#5f7c80}@media(max-width:760px){h1{font-size:32px}.cards{grid-template-columns:1fr 1fr}.twocol{grid-template-columns:1fr}iframe{height:650px}}</style></head><body>
<header><div class="eyebrow">RIGS-OF-RODS-TRIALS · IMPLEMENTATION EVIDENCE · 2026-10-08</div><h1>Forces, work and core energy.<br>Measured inside the native solver.</h1><p>Slice 02 connects force attribution, explicit storage and work terms, analytical fixture qualification and a live workbench to a newly source-built simulation.</p><span class="badge">7 scoped fixture passes</span><span class="badge">13 complete final attempts</span><span class="badge">0 required-record loss</span></header>
<main><nav><a href="#accounting">Accounting</a><a href="#fixtures">Fixtures</a><a href="#evidence">Visual proof</a><a href="#cost">Cost and limits</a><a href="#provenance">Reproduction</a></nav>
<section><div class="cards"><div class="card"><b>16</b><small>Force channels</small></div><div class="card"><b>~2 kHz</b><small>Every-step aggregate archive</small></div><div class="card"><b>2,080 B</b><small>Schema 2 record payload</small></div><div class="card"><b>41</b><small>Real native renderer frames</small></div></div>
<p>The delivered slice attributes consumed force and midpoint work to gravity, generic drag, ground/object contact, elastic beams, beam damping, native beam corrections, wheels, aero, buoyancy, commands, mouse, cab contact, slide nodes, inter-actor passes, free forces and an explicit unattributed channel. Per-node caches preserve force provenance across the native force reset. The archive stores aggregate vectors and work; it does not provide raw node trajectories or contact patches.</p>
<div class="notice"><b>Qualification has a narrow scope.</b> Passed applies to the pinned dry one-moving-node fixtures with precise beam lengths. The Daf vehicle study remains <b>NotReady</b>. This slice does not establish whole-vehicle energy closure, real-world material calibration, impact energy dispersal or coherent atmospherics.</div></section>
<section id="accounting"><h2>The accounting boundary</h2>
<svg viewBox="0 0 1040 215" role="img" aria-label="Generated forces persist in preallocated node caches and are consumed at the next integration with current contact; a bounded queue feeds archived records and qualification"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#078177"/></marker></defs>
<g fill="#e3eee7" stroke="#8fb6a9"><rect x="5" y="35" width="180" height="115" rx="8"/><rect x="225" y="35" width="180" height="115" rx="8"/><rect x="445" y="35" width="190" height="115" rx="8"/><rect x="675" y="35" width="165" height="115" rx="8"/><rect x="875" y="35" width="160" height="115" rx="8"/></g>
<g font-family="system-ui" font-size="15" text-anchor="middle" fill="#173c44"><text x="95" y="67">Actual phase writes</text><text x="95" y="94">Beam / wheel / drag</text><text x="95" y="124">tick n</text><text x="315" y="67">Preallocated caches</text><text x="315" y="94">Per-node, per-channel</text><text x="315" y="124">Carried across reset</text><text x="540" y="67">Native integration</text><text x="540" y="94">Contact + Δp + work</text><text x="540" y="124">tick n+1</text><text x="758" y="67">Bounded SPSC</text><text x="758" y="94">Writer thread</text><text x="758" y="124">CRC / durable close</text><text x="955" y="67">Archive analysis</text><text x="955" y="94">Scoped gates</text><text x="955" y="124">React projections</text></g>
<g stroke="#078177" stroke-width="2" marker-end="url(#arrow)"><path d="M185 90H220"/><path d="M405 90H440"/><path d="M635 90H670"/><path d="M840 90H870"/></g><text x="520" y="190" text-anchor="middle" fill="#547279" font-family="system-ui" font-size="14">Ground/object contact is generated and consumed in the current tick; stored epochs describe the carried base.</text></svg>
<pre>p = Σ mᵢ vᵢ                         K = ½ Σ mᵢ |vᵢ|²
W_channel = Σ F_channel,ᵢ · (v_before,ᵢ + v_after,ᵢ)/2 · dt
Ug = −Σ mᵢ g yᵢ                    Us = ½ Σ k (length − restLength)²
Core discrepancy = ΔK + ΔUg + ΔUs − W_nonconservative − storage-change ports</pre>
<p>Gravity and eligible elastic work are excluded from the nonconservative sum to avoid counting the same energy twice. Linear storage uses active normal, unbounded, local beams. Shock, hydro, rope, inter-actor and other unsupported storage paths stay visible as unclosed elements. Native constitutive corrections and finite-precision force accumulation are recorded separately. Unknown force coverage is the sum of per-node magnitudes, so opposing omissions cannot cancel in the resultant.</p>
<p>Initialization reports injected momentum and kinetic energy. Subsequent mass/velocity changes report mutation ports; mass/cohort exchange is unqualified. Fixed nodes are excluded from kinetic/work cohorts, with their applied-force sum retained separately. Beam rest/stiffness changes and removals carry bounded transition snapshots, before/after storage estimates and strength/stress fields. A removal port is bookkeeping for disappearing model storage, <b>not measured fracture energy</b>. Strength-only changes and complete plastic/fracture constitutive accounting need later adapters.</p>
<p>Wind decomposition records F_drag·v = F_drag·(v−wind) + F_drag·wind. A separate −8 m/s², density1 kg/m³, wind[3,0,−1] m/s vehicle run exercised a nonzero wind port. Across124,000 fully attributed records, maximum channel force reconstruction error was3.01×10⁻¹¹N, work error5.12×10⁻¹³J and wind/relative-work identity error6.44×10⁻¹⁵J; the wind port reached0.848J/tick. It explains the adopted generic drag path; airfoil models, thermal transfer, coherent pressure/water fields, gusts and particles remain unqualified.</p></section>
<section id="fixtures"><h2>Real native fixtures and acceptance gates</h2>
<p>Three versioned truck assets from this checkout run as fresh source-built actors on Simple2. One movable 100 kg node and three fixed anchors use contactless, drag-disabled initial states. Spring/damper geometry has a 1 m rest length and 0.05 m extension, with k = 10,000 N/m; the damper uses c = 200 Ns/m. Free fall uses gravity −9.81 m/s² and zero beam stiffness; the linear fixtures use zero gravity.</p>
<p>The first legacy-precision spring and damper attempts failed their declared trajectory/energy budgets. The solver's inverse-square-root approximation and fixture coordinate initialization were investigated. The analytical profile now explicitly selects precise beam normalization and initializes relative coordinates near the origin; vehicle studies preserve the existing approximate kernel. Manifests identify this distinction. Failed attempts were retained.</p>'''+pic('native-fixtures.png','Native summaries versus continuous analytical references. The actual acceptance calculation uses a separate double-precision kick-drift reference for every captured step.')+pic('native-energy.png','Cumulative mechanical storage minus nonconservative work and storage ports, computed from every-step native records; finite-step discrepancy is retained.')+'''
<div class="scroll"><table><thead><tr><th>Scenario</th><th>Records</th><th>Scientific result</th><th>Lost</th></tr></thead><tbody>'''+tables+'''</tbody></table></div>
<p>Acceptance requires complete execution/capture, the pinned initialization, one moving node, finite observations, supported storage, negligible unknown forces and no unexpected state mutation. Declared limits include 0.003 m position error, 0.04 m/s velocity error, 0.3 J core discrepancy (and undamped energy envelope), 10⁻⁵ N unknown/reconstruction bounds, 10⁻³ kg·m/s impulse discrepancy and 10⁻³ J midpoint-work discrepancy. Free-fall closure removes its known semi-implicit discretization trend, −½m g² dt² N. These are scenario-specific engineering budgets, not a general 1% physical-accuracy certificate.</p>
<p>Two separate-process repeats per fixture produced zero difference in the compared recorded positions, momentum and storage values on this workstation. This is not a cross-platform determinism claim. Exact per-check observations, limits and scope are retained in each result and in the machine-readable delivery record.</p></section>
<section id="evidence"><h2>Source-built visual proof and playback recovery</h2>'''+pic('native-source-scene.png','RoR native render-window screenshot from the final source-built coast worker. OpenGL provides the rendered scene; the observer records the physics independently.')+'''
<p><a href="'''+video+'''">Open the new recording and image-frame player</a>. The sequence contains 41 actual screenshots requested from RoR at nominal 0.5 render-second intervals, encoded at 2 fps. Capture requests can be delayed; video timing is not a physics measurement clock. The compatible image player presents 82 decoded samples at 4 Hz, including repeated source frames. No scene imagery was generated or reconstructed from telemetry.</p>
<iframe src="'''+video+'''" title="Native renderer recording with codec-independent image playback" loading="lazy"></iframe>
<p>GDI window capture of the OpenGL worker produced black frames and was rejected as proof. The failed MP4 remains in the earlier verification directory. Native renderer capture produced visible images; the packaged WebM was checked using screenshot pixel means/variances at 1, 3 and 5 seconds, and the image player was checked for progression. All 82 decoded native-video samples passed nonblank image checks.</p>
<p>The user-reported historical playback issue is handled with <a href="'''+recovery1+'''">Slice 01 recovered playback</a> and <a href="'''+recovery0+'''">original source-build recovered playback</a>. The older MP4 files contain visible frames; WebM and image-frame alternatives preserve their content. Chrome visible-pixel tests passed. Codex in-app GPU playback could not be directly checked because its browser automation helper failed to initialize; use Play frames if video is still blank. The protected baseline and original MP4s were not overwritten.</p>
<div class="twocol">'''+pic('fixture-acceptance-panel.png','Actual React acceptance checks for the native spring fixture, including observed values and declared limits.')+pic('wind-force-panel.png','Actual nonzero-wind force/work dashboard; the vehicle remains scientific NotReady.')+'''</div></section>
<section id="cost"><h2>Measured cost and remaining gates</h2>
<div class="scroll"><table><thead><tr><th>Same native build</th><th>Observed released steps</th><th>Median step elapsed</th><th>p95 step elapsed</th></tr></thead><tbody>
<tr><td>Channel attribution disabled</td><td>'''+str(perf['False']['steps'])+'''</td><td>'''+str(perf['False']['medianStepElapsedUs'])+''' µs</td><td>'''+str(perf['False']['p95StepElapsedUs'])+''' µs</td></tr>
<tr><td>Channel attribution enabled</td><td>'''+str(perf['True']['steps'])+'''</td><td>'''+str(perf['True']['medianStepElapsedUs'])+''' µs</td><td>'''+str(perf['True']['p95StepElapsedUs'])+''' µs</td></tr></tbody></table></div>
<p>Two 5 s coast runs per mode measured a median ratio of '''+f"{perf['medianRatio']:.3f}"+'''× (about 79.5% additional step duration). The baseline retains storage scans and the aggregate recorder. Both modes requested native evidence frames. These are steady-clock elapsed durations including native scheduling/barriers, <b>not process CPU time or an instrumentation-off comparison</b>. The proposed ≤10% overhead target is not achieved. Optimize phase/node passes and characterize a true instrumentation-off build before large asset or actor workloads.</p>
<p>Schema 2 is 2,080 payload bytes per step, about 4.16 MB/s at 2 kHz for one actor, excluding framing and summary/event projections. The 32,768-record ring holds about 65 MiB (16.4 simulated seconds). Events are limited to eight transitions per step; overflow marks required capture incomplete while simulation continues. No raw node/contact window recorder, impact trigger history or production multiactor pipeline is delivered here.</p>
<p>Next gates: profiling/optimization, controlled barrier and contact/impact windows, nonlinear/plastic/fracture closure, relative-air environmental qualification, broader asset catalog/configuration, then driven journeys and flight. Vehicle momentum/work arithmetic can be inspected now; reliable impact outcome acceptance needs these later gates.</p></section>
<section id="provenance"><h2>Build, run and reproduce</h2>
<p>Fork: <a href="https://github.com/bert-systems/rigs-of-rods-trials">bert-systems/rigs-of-rods-trials</a>, upstream <a href="https://github.com/RigsOfRods/rigs-of-rods">RigsOfRods/rigs-of-rods</a>. Content revision: <code>34fefdd126784bf87b068fc283f812525d159dd7</code>. New build outputs live outside the checkout. A fresh native build was followed by documented incremental repairs and rebuilds; Conan dependencies reuse the existing cache.</p>
<p>Final source-built executable: <code>'''+h(session/'build/bin/RoR.exe')+'''</code><br>SHA-256: <span class="hash">'''+sha+'''</span>. All final workers matched this hash and their observed private process paths. Engine/render DLL modules were verified within their private worker directories; the installed parent game was not used for proof.</p>
<pre>$trialSession='''+h("'"+str(session)+"'")+'''
.\u005ctools\u005ctrials\u005cbuild.ps1 -Session $trialSession
.\u005ctools\u005ctrials\u005cstart.ps1 -Session $trialSession -Port 54322 -Renderer OpenGL -EvidenceFrames
python tools/trials/verify-slice-02.py --session $trialSession
python tools/trials/media-evidence.py --input &lt;native-MP4&gt; --output &lt;media-directory&gt;
python tools/trials/verify-media.py --directory &lt;media-directory&gt;</pre>
<p>The source-built C++ ledger checks passed. .NET built with zero warnings/errors; contract checks cover bounds, pinned scenario/asset pairs, CRC, catalog restart, corrupted/truncated committed prefixes and nonpassing incomplete/legacy fixture capture. Locked npm install and production React build passed. Browser checks covered authoring defaults, native pause/resume, source/module provenance, scientific results, desktop/mobile layout and browser errors. Original failed precision, Direct3D9 device startup, black GDI video and mobile overflow probes remain in the session.</p>
<p>Publications include this lightweight report, contracts, tests and runbooks in Git. Large build trees, binary captures, logs and media remain in <code>'''+h(session)+'''</code>. The standalone report archive includes the report, media, figures and checks; it excludes the build, private workers and raw step archives.</p></section>
<footer>Slice 02 delivery · Exact run measurements and source identities in slice-02-results.json. Publication identity is recorded after commit/merge/push in the session publication record. Fixture scope and remaining performance/model gates remain explicit.</footer></main></body></html>'''
(report/'index.html').write_text(body(''),encoding='utf-8')
(root/'doc/project/reports/trial-slice-02-2026-10-08.html').write_text(body(report.as_uri()+'/'),encoding='utf-8')
light={k:results[k] for k in ['checks','runs','repeatability','performance','evidence']}
light['channelChecks']=results.get('channelChecks',{});light['nativeExecutableSha256']=sha;light['mediaChecks']={k:json.loads((session/'media'/k/'playback-check.json').read_text(encoding='utf-8')) for k in ['baseline-recovered','slice-01-recovered','slice-02-native']}
(root/'doc/project/slices/slice-02-results.json').write_text(json.dumps(light,indent=2),encoding='utf-8')
print(json.dumps({'report':str(report/'index.html'),'fixtures':len(fixtures),'sha256':sha}))
