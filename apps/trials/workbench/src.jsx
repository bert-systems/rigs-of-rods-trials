import React, {useEffect,useState,useRef} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';

const initial={name:'Daf controlled barrier impact',launchSpeedMps:6.2,durationSeconds:9,settleSeconds:3,repeats:1,
 scenario:'barrier-v1',barrierDistanceM:12,targetImpactSpeedMps:5,detailFault:'none',vehicle:'b6b0UID-semi.truck',terrain:'simple2.terrn2',accounting:true,observation:'full',performanceProbe:false,observerProfiling:false,
 environment:{gravity:-9.81,temperatureK:288.15,density:1.225,windX:0,windY:0,windZ:0}};
const norm=v=>v?Math.hypot(...v):0;
const fmt=(n,d=2)=>Number.isFinite(n)?n.toLocaleString(undefined,{maximumFractionDigits:d}):'—';
const scienceFmt=n=>Number.isFinite(n)&&n!==0&&Math.abs(n)<.001?n.toExponential(3):fmt(n,7);
const axisFmt=n=>Math.abs(n)>0&&Math.abs(n)<.01?n.toExponential(2):fmt(n);
const terminal=['Completed','Failed','Cancelled','Interrupted'];
function Spark({points,field,vector=false,title,unit}){
 const width=660,height=154,pad=25;
 const values=points.map(p=>vector?p[field]??[0,0,0]:[p[field]??0]);
 const flat=values.flat(),lo=Math.min(0,...flat),rawHi=Math.max(0,...flat),hi=rawHi===lo?lo+1:rawHi,range=hi-lo;
 const minT=points[0]?.timeSeconds??0,maxT=points.at(-1)?.timeSeconds??1;
 const x=i=>pad+(points[i].timeSeconds-minT)/Math.max(.05,maxT-minT)*(width-pad*2);
 const y=v=>height-pad-(v-lo)/range*(height-pad*2);
 const colors=['#38c7bb','#69a5ff','#f5b863'];
 const paths=Array.from({length:vector?3:1},(_,axis)=>{
  let path='';
  points.forEach((p,i)=>{const gap=p.gap||i>0&&p.tick-points[i-1].tick>100;path+=(i===0||gap?'M':'L')+x(i).toFixed(2)+','+y(values[i][axis]).toFixed(2)+' ';});
  return <path key={axis} d={path} fill="none" stroke={colors[axis]} strokeWidth="2"/>;
 });
 return <section className="chart"><div className="section-title"><h3>{title}</h3><span>{unit}</span></div>
 <svg viewBox={'0 0 '+width+' '+height} role="img" aria-label={title+' versus recorded simulation time'}>
 {[.25,.5,.75].map(t=><line key={t} x1={pad} x2={width-pad} y1={pad+t*(height-pad*2)} y2={pad+t*(height-pad*2)} stroke="#263a48"/>)}
 <text x={pad} y="14" fill="#95aaba" fontSize="11">{axisFmt(lo)} … {axisFmt(hi)} {unit.split(" ")[0]}</text>
 {paths}<text x={pad} y={height-5} fill="#95aaba" fontSize="11">{fmt(minT)} s</text><text x={width-pad-35} y={height-5} fill="#95aaba" fontSize="11">{fmt(maxT)} s</text>
 {points.length===0&&<text x={width/2} y={height/2} textAnchor="middle" fill="#94a9bb" fontSize="14">Waiting for native observations</text>}
 </svg>{vector&&<div className="legend">{['X','Y','Z'].map((v,i)=><span key={v}><i style={{background:colors[i]}}/>{v}</span>)}</div>}</section>;
}
const FormContext=React.createContext(null);
function Field({label,k,env=false,min,max,step='any',disabled=false}){
 const {form,num}=React.useContext(FormContext);
 return <label>{label}<input type="number" step={step} min={min} max={max} disabled={disabled} value={env?form.environment[k]:form[k]} onChange={e=>num(k,e.target.value,env)} required/></label>;
}
function DetailInspector({attempt}){
 const d=attempt.metrics.impactDetail;
 const [tick,setTick]=useState(d.triggerTick),[node,setNode]=useState(0),[beam,setBeam]=useState(0);
 const [frame,setFrame]=useState(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 const load=async e=>{e.preventDefault();setBusy(true);setFrame(null);setError('');
  try{const response=await fetch(`/api/attempts/${attempt.id}/detail?tick=${tick}&node=${node}&beam=${beam}`);
   if(!response.ok)throw new Error(response.status===404?'This tick is not in the verified archive. A gap is not interpolated.':'The recorded frame could not be verified.');
   setFrame(await response.json());}catch(e){setError(e.message);}finally{setBusy(false);}};
 const vector=v=>v.map(x=>fmt(x,4)).join(' / ');
 return <section className="accounting"><div className="section-title"><h3>Archived tick inspector</h3><span>CRC VERIFIED · EXACT NATIVE TICK</span></div>
 <p>Select a retained tick, node and beam. Float32 solver state; generated beam forces belong to this tick, while carried node channels are consumed at integration.</p>
 <form onSubmit={load} className="detail-query"><label>Tick<input type="number" step="1" required min={d.firstTick} max={d.lastTick} value={tick} onChange={e=>setTick(+e.target.value)}/></label>
 <label>Node ID<input type="number" step="1" required min="0" max={d.nodes-1} value={node} onChange={e=>setNode(+e.target.value)}/></label>
 <label>Beam ID<input type="number" step="1" required min="0" max={d.beams-1} value={beam} onChange={e=>setBeam(+e.target.value)}/></label>
 <button disabled={busy}>{busy?'Verifying…':'Inspect tick'}</button></form>
 {error&&<div className="warning">{error}</div>}
 {frame&&<><p>Tick {frame.tick} · node {frame.node.id}: position {vector(frame.node.positionM)} m · velocity {vector(frame.node.velocityMps)} m/s · consumed force {vector(frame.node.consumedForceN)} N.</p>
 <p>Beam {frame.beam.id}: nodes {frame.beam.node1}/{frame.beam.node2}, length {fmt(frame.beam.lengthM,6)} m, rest {fmt(frame.beam.restM,6)} m, stress {fmt(frame.beam.stressN)} N, strength {fmt(frame.beam.strengthN)} N. Applied endpoint forces: {vector(frame.beam.generatedNode1ForceN)} / {vector(frame.beam.generatedNode2ForceN)} N.</p>
 <table><thead><tr><th>Node channel</th><th>Consumed force X / Y / Z · N</th></tr></thead><tbody>{Object.entries(frame.node.channels).map(([name,f])=><tr key={name}><td>{name}</td><td>{vector(f)}</td></tr>)}</tbody></table>
 <h4>Actual terrain/object applications ({frame.contacts.length})</h4><table><thead><tr><th>Node / feature</th><th>Applied vector · N</th><th>Normal vector · N</th><th>Tangential vector · N</th></tr></thead><tbody>{frame.contacts.map((c,i)=><tr key={i}><td>{c.node} / {c.barrier?'barrier':'surface'} {c.feature}</td><td>{vector(c.appliedForceN)}</td><td>{vector(c.normalForceN)}</td><td>{vector(c.tangentialForceN)}</td></tr>)}</tbody></table></>}
 </section>;
}
function TransitionView({attempt}){
 const summary=attempt.metrics.beamTransitions;
 const [page,setPage]=useState(summary),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 const load=async offset=>{setBusy(true);setError('');try{
  const r=await fetch(`/api/attempts/${attempt.id}/transitions?offset=${offset}&limit=20`);
  if(!r.ok)throw Error('The transition archive could not be verified.');setPage(await r.json());
 }catch(e){setError(e.message);}finally{setBusy(false);}};
 const kinds=k=>[k&1?'Parameters':null,k&2?'Removed':null,k&4?'Strength':null,k&8?'Unsupported parameters':null].filter(Boolean).join(' + ');
 return <section className="accounting transition-panel"><div className="section-title"><h3>Beam transition ledger</h3><span>{summary.projectionComplete?'COMPLETE PROJECTION':'DENSE DETAIL REQUIRED'}</span></div>
 <p>{summary.parameterChanges} parameter changes · {summary.strengthChanges} strength changes · {summary.removed} removed · {summary.omitted} omitted from aggregate projection.</p>
 <p>Rest/stiffness storage port: {scienceFmt(summary.restStoragePortJ)} J · removal storage port: {scienceFmt(summary.removedStoragePortJ)} J. These are signed model storage changes. Strength-only changes carry no spring-energy port. Material fracture dissipation remains unqualified.</p>
 {error&&<div className="warning">{error}</div>}
 <table><thead><tr><th>Tick / beam</th><th>Change</th><th>Rest · old → new m</th><th>Strength · old → new N</th><th>Rest / removal port · J</th></tr></thead><tbody>{page.events.map((e,i)=><tr key={i}><td>{e.tick} / {e.beam}</td><td>{kinds(e.kind)}</td><td>{fmt(e.oldRestM,6)} → {fmt(e.newRestM,6)}</td><td>{fmt(e.oldStrengthN,5)} → {fmt(e.newStrengthN,5)}</td><td>{scienceFmt(e.restStoragePortJ)} / {scienceFmt(e.removedStoragePortJ)}</td></tr>)}</tbody></table>
 {summary.total===0&&<p>No aggregate transitions recorded.</p>}
 <div className="controls"><button disabled={busy||page.offset===0} onClick={()=>load(Math.max(0,page.offset-20))}>Previous transitions</button><span>{page.offset+page.events.length} of {page.total}</span><button disabled={busy||page.offset+page.events.length>=page.total} onClick={()=>load(page.offset+20)}>Next transitions</button></div>
 </section>;
}
function RecorderView({attempt}){
 const health=attempt.recorderHealth;
 const streams=health?['aggregate','probe','detail'].filter(k=>health[k]).map(k=>[k,health[k]]):[];
 const busy=attempt.execution==='Finalizing',lost=attempt.capture==='Incomplete'||streams.some(([,s])=>s.dropped>0||s.ioError);
 return <section className="accounting recorder-panel"><div className="section-title"><h3>Recorder health</h3><span>{lost?'REQUIRED LOSS':busy?'DRAINING':streams.length&&streams.every(([,s])=>s.closed)?'WRITERS CLOSED':'LIVE COUNTERS'}</span></div>
 {busy&&<p className="drain-note">Physics finished. Waiting for archive writers and verification. {lost?'Required loss remains incomplete.':'Capture is still being finalized.'}</p>}
 {streams.length===0?<p>Recorder diagnostics are unavailable for this attempt.</p>:<>
 <p>Queue pressure shows admitted frames waiting for the recorder. Detail includes prehistory and frames outside the selected impact window. Written frames await sync; durable frames have completed file synchronization. Final CRC and coverage checks determine capture quality.</p>
 {lost&&<div className="warning">Required loss is sticky. Later frames continue recording; scientific acceptance cannot pass.</div>}
 <div className="recorder-streams">{streams.map(([name,s])=>{
  const pressure=s.capacity?s.queued/s.capacity:0;
  return <div className="recorder-stream" key={name} data-stream={name}><div className="section-title"><h4>{name==='aggregate'?'Aggregate ledger':name==='probe'?'Control probe':'Detailed impact'}</h4><span>{s.closed?'CLOSED':s.ioError?'I/O ERROR':'RECORDING'}</span></div>
   <label>Queue {fmt(s.queued,0)} / {fmt(s.capacity,0)} frames · {fmt(pressure*100,1)}%<progress max="1" value={Math.min(1,pressure)} aria-label={name+' queue pressure'}/></label>
   {pressure>=.8&&<p className="pressure-note">Queue exceeds 80% capacity. Recording continues at the configured rate.</p>}
   <div className="recorder-values"><div>Queue high-water<strong>{fmt(s.highWater,0)} frames</strong></div><div>Reserved queue<strong>{fmt(s.reservedQueueBytes/2**20,1)} MiB</strong></div>
   <div>Written / durable<strong>{fmt(s.written,0)} / {fmt(s.durable,0)}</strong></div><div>Pending sync<strong>{fmt(s.pendingSync,0)} frames</strong></div>
   <div>Committed frame bytes<strong>{fmt(s.archiveBytes/2**20,1)} MiB</strong></div><div>Required loss / I/O<strong className={s.dropped||s.ioError?'bad':''}>{fmt(s.dropped,0)} / {s.ioError?'Error':'Healthy'}</strong></div></div>
  </div>;
 })}</div></>}
 {attempt.metrics?.observerProfile&&<><h4>Diagnostic observer phases</h4><p>Opt-in clock overhead is included. These diagnostic timings are excluded from the performance budget comparisons.</p><div className="recorder-values">{attempt.metrics.observerProfile.phases.map(p=><div key={p.name}>{p.name}<strong>{fmt(p.sumWallUs/attempt.metrics.observerProfile.steps,2)} µs / step</strong></div>)}</div></>}
 </section>;
}
function App(){
 const [data,setData]=useState(null),[form,setForm]=useState(initial),[selected,setSelected]=useState(null);
 const [error,setError]=useState(''),[live,setLive]=useState(false),[sending,setSending]=useState(false),[tab,setTab]=useState('Trials');
 const token=useRef(null);
 const selectedRef=useRef(selected);selectedRef.current=selected;
 useEffect(()=>{
  let cancelled=false,timer;
  async function poll(){
   try{
    if(!token.current)token.current=(await (await fetch('/api/session')).json()).session;
    const response=await fetch('/api/state?compact=true&selected='+encodeURIComponent(selectedRef.current??''));
    if(!response.ok)throw Error('Live state unavailable');
    const next=await response.json();if(!cancelled){setData(next);setLive(true);}
   }catch(e){if(!cancelled)setLive(false);}
   if(!cancelled)timer=setTimeout(poll,100);
  }poll();
  return()=>{cancelled=true;clearTimeout(timer);};
 },[]);
 const attempts=data?.attempts??[];
 const current=attempts.find(a=>a.id===selected)??attempts.find(a=>['Running','Finalizing','Starting','Paused','Pausing','Resuming'].includes(a.execution))??attempts.at(-1);
 const sample=current?.latest,history=current?.history??[];
 const off=current?.definition.observation==='off';
 const impactFixture=['impact-yield-v1','impact-fracture-v1'].includes(form.scenario);
 const fixture=!['coast-v1','barrier-v1'].includes(form.scenario);const barrier=form.scenario==='barrier-v1';
 const transitionFixture=fixture&&!['freefall-v1','spring-v1','damper-v1'].includes(form.scenario);
 const scenario=value=>setForm(f=>({...f,scenario:value,vehicle:['coast-v1','barrier-v1'].includes(value)?'b6b0UID-semi.truck':'ror-'+value+'.truck',
   launchSpeedMps:value.startsWith('impact-')?5:value==='barrier-v1'?6.2:value==='coast-v1'?5:0,detailFault:'none',accounting:true,observation:'full',targetImpactSpeedMps:5,barrierDistanceM:value.startsWith('impact-')?13:12,durationSeconds:value.startsWith('impact-')?7:value==='barrier-v1'?9:value==='coast-v1'?12:value==='freefall-v1'?.5:['spring-v1','damper-v1'].includes(value)?5:.2,
   settleSeconds:['coast-v1','barrier-v1'].includes(value)?3:0,environment:{...f.environment,gravity:['coast-v1','barrier-v1','freefall-v1'].includes(value)?-9.81:0,windX:0,windY:0,windZ:0}}));
 const num=(key,value,env=false)=>setForm(f=>env?{...f,environment:{...f.environment,[key]:value}}:{...f,[key]:value});
 async function post(url,body){
  const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json','X-Trials-Session':token.current??''},body:JSON.stringify(body??{})});
  const value=await response.json();if(!response.ok)throw Error(value.error??'Request rejected');return value;
 }
 async function enqueue(event){
  event.preventDefault();setSending(true);setError('');
  try{const payload={...form,environment:Object.fromEntries(Object.entries(form.environment).map(([k,v])=>[k,Number(v)]))};
  for(const k of ['launchSpeedMps','durationSeconds','settleSeconds','repeats','barrierDistanceM','targetImpactSpeedMps'])payload[k]=Number(payload[k]);
  const result=await post('/api/experiments',payload);setSelected(result.attemptIds[0]);}catch(e){setError(e.message);}finally{setSending(false);}
 }
 async function command(op){setError('');try{await post('/api/attempts/'+current.id+'/'+op);}catch(e){setError(e.message);}}
 const env=current?.definition.environment??form.environment;
 return <div className="shell">
 <aside className="sidebar"><div className="brand"><span className="mark">R</span><div>RoR Trials<small>PHYSICAL STUDIES</small></div></div>
 <nav>{['Trials','Results','Environment'].map(name=><button key={name} className={tab===name?'active':''} onClick={()=>setTab(name)}>{name}<span>↗</span></button>)}</nav>
 <div className="sidebar-note"><span className={'dot '+(live?'ok':'')}/>{live?'Workbench connected':'Connecting / stale view'}<p>Native recording continues independently of this view.</p></div>
 <div className="sidebar-footer">Source-built simulation<br/>Local trial archive<br/>Manual data retention</div></aside>
 <main><header className="topbar"><span>WORKBENCH / {tab.toUpperCase()}</span><div><span className={'dot '+(live?'ok':'')}/>{live?'Live connection':'Last-known state'}</div></header>
 <div className="heading"><div className="eyebrow">DEFINE · OBSERVE · COMPARE</div><h1>{tab==='Environment'?'Physical environment':tab==='Results'?'Retained trial results':'Experiment workbench'}</h1><p>Controlled vehicle studies with native observations and a traceable result for every attempt.</p></div>
 {error&&<div className="error" role="alert">{error}</div>}
 {!live&&data&&<div className="warning">Live view disconnected. Showing last-known observations; refresh does not repeat trial commands.</div>}
 <div className="workspace"><aside className="author"><div className="section-title"><h2>New experiment</h2><span>PINNED PILOT</span></div>
 <FormContext.Provider value={{form,num}}><form onSubmit={enqueue}><label>Experiment name<input value={form.name} maxLength={120} onChange={e=>setForm({...form,name:e.target.value})} required/></label>
 <label>Study scenario<select value={form.scenario} onChange={e=>scenario(e.target.value)}>
 <option value="barrier-v1">Daf controlled barrier · 2 kHz detail</option><option value="coast-v1">Daf rolling coast · study</option><option value="freefall-v1">Free fall · dry fixture</option>
 <option value="spring-v1">Linear spring · dry fixture</option><option value="damper-v1">Spring + damper · dry fixture</option>
 <option value="impact-yield-v1">Later collision yield + strength / two-mass fixture</option><option value="impact-fracture-v1">Later collision removal / two-mass fixture</option><option value="yield-tension-v1">Tensile yield + strength · fixture</option><option value="yield-compression-v1">Compressive yield · fixture</option><option value="fracture-v1">Beam removal · fixture</option><option value="protected-beam-v1">Protected beam strength · fixture</option></select></label>
 <label>Observation profile<select disabled={impactFixture} value={form.observation==='off'?'off':form.accounting?'full':'basic'} onChange={e=>setForm(f=>({...f,observation:e.target.value==='off'?'off':'full',accounting:e.target.value==='full',observerProfiling:e.target.value==='off'?false:f.observerProfiling,performanceProbe:e.target.value==='off'?true:f.performanceProbe}))}>
 <option value="full">Full force / core energy ledger</option><option value="basic">Channels disabled · base ledger</option><option value="off">Ledger off · control probe only</option></select></label>
 <label className="probe-option"><input type="checkbox" checked={form.performanceProbe} disabled={form.observation==='off'} onChange={e=>setForm({...form,performanceProbe:e.target.checked,observerProfiling:e.target.checked?form.observerProfiling:false})}/> Timing / equivalence probe</label>
 <label className="probe-option"><input type="checkbox" checked={form.observerProfiling} disabled={form.observation==='off'} onChange={e=>setForm({...form,observerProfiling:e.target.checked,performanceProbe:e.target.checked?true:form.performanceProbe})}/> Diagnostic observer phase profiling</label>
 <div className="asset"><span>Vehicle / fixture</span><strong>{impactFixture?'Two 100 kg moving nodes + one beam':fixture?'100 kg movable node + fixed anchors':'Daf Semi'}</strong><small>{form.vehicle}</small></div>
 <div className="asset"><span>Terrain</span><strong>Simple Test Terrain</strong><small>simple2.terrn2</small></div>
 <div className="form-pair"><Field label="Release speed · m/s" k="launchSpeedMps" disabled={impactFixture} min="0" max="20"/><Field label="Observe · s" k="durationSeconds" disabled={impactFixture} min={fixture?".1":"1"} max={impactFixture?"7":transitionFixture?"1":fixture?"5":"120"}/></div>
 <div className="form-pair"><Field label="Settling · s" k="settleSeconds" disabled={impactFixture} min={fixture?"0":"2"} max={fixture?"0":"30"}/><Field label="Repeats" k="repeats" min="1" max="20" step="1"/></div>
 {barrier&&<><div className="form-pair"><Field label="Barrier distance from front · m" k="barrierDistanceM" min="1" max="100"/><Field label="Target approach speed · m/s" k="targetImpactSpeedMps" min=".1" max="20"/></div>
 <div className="setup-note">Fixed concrete box: 16 m wide, 6 m high, 1 m deep. All nodes, force channels, beams and terrain/object contacts: every 0.5 ms, 2 s before / 4 s after consumed impact. Release and target speeds are separate; no continuous speed correction.</div></>}
 <details open={tab==='Environment'}><summary>Gravity, air and steady wind</summary>
 <Field label="Gravity Y · m/s²" k="gravity" env disabled={impactFixture} min="-30" max="0"/>
 <div className="form-pair"><Field label="Temperature · K" k="temperatureK" env min="180" max="350"/><Field label="Density · kg/m³" k="density" env min=".001" max="3"/></div>
 <div className="wind-fields">{['X','Y','Z'].map(axis=><Field key={axis} label={'Wind '+axis+' · m/s'} k={'wind'+axis} env disabled={impactFixture} min="-30" max="30"/>)}</div></details>
 <div className="setup-note">{impactFixture?"Pinned later collision: two 100 kg moving nodes, 1 m initially unstressed beam, k=10,000 N/m, 2,000 N strength, 5 m/s, barrier face x=514 m after 13 m flight, zero gravity/drag, 7 s. All-node/contact/beam detail: 2 s pre / 4 s post, 64 MiB queue. Yield uses 200 N bounds; removal uses high yield bounds. These are native model checks, not material calibration.":fixture?"Pinned dry/contactless state: 100 kg, 1 m rest length, ±0.05 m extension, k=10,000 N/m. Transition fixtures: 200 N yield / 2,000 N strength or 200 N removal threshold; compression uses negative extension. Free fall disables stiffness; damper c=200 Ns/m.":"Settle, initialize rolling motion, then coast with propulsion off."} Each attempt gets a fresh process and private profile.</div>
 <button className="primary" disabled={sending||!live}>{sending?'Saving revision…':'Queue experiment'} <span>→</span></button></form></FormContext.Provider>
 <div className="scope-note"><strong>Current study scope</strong><p>16 force channels, linear beam storage, state/work ports and required transition capture. Analytical dry fixtures have scoped qualification. Controlled approach/capture checks are separate from vehicle constitutive and nonlinear energy qualification.</p></div></aside>
 <section className="monitor"><div className="attempts"><div className="section-title"><h2>Trial queue</h2><span>{attempts.length} ATTEMPTS · SERIAL</span></div>
 {attempts.length===0?<div className="empty">Define an experiment to launch the source-built worker.</div>:<div className="queue-list">{attempts.slice().reverse().map(a=><button key={a.id} className={'queue-item '+(a.id===current?.id?'selected':'')} onClick={()=>setSelected(a.id)}><div><strong>{a.definition.name}</strong><small>{a.id.slice(0,8)} · {a.definition.launchSpeedMps} m/s · {a.retryOf?'retry':'new attempt'}</small></div><span className={'pill '+a.execution.toLowerCase()}>{a.execution}</span></button>)}</div>}</div>
 <div className="run-header"><div><div className="eyebrow">SELECTED ATTEMPT</div><h2>{current?.definition.name??'No active attempt'}</h2><p>{current?current.id:'Ready for a controlled study'}</p></div><div className="controls">
 {current&&<><button disabled={current.execution!=='Running'} onClick={()=>command('pause')}>Pause</button><button disabled={current.execution!=='Paused'} onClick={()=>command('resume')}>Resume</button><button disabled={!['Running','Paused','Queued'].includes(current.execution)} onClick={()=>command('cancel')}>Cancel</button></>}
 </div></div>
 {current?.blockedReason&&<div className="warning">{current.blockedReason}</div>}
 <div className="quality"><div><span>Execution</span><strong>{current?.execution??'—'}</strong></div><div><span>Capture</span><strong className={current?.capture==='Incomplete'?'bad':''}>{current?.capture??'—'}</strong></div><div><span>Scientific validation</span><strong className="amber">{current?.validation??'Not evaluated'}</strong></div><div><span>Simulation clock</span><strong>{fmt(current?.workerStatus?.timeSeconds??sample?.timeSeconds,3)} <small>s</small></strong></div></div>
 {current&&<RecorderView attempt={current}/>}
 {off?<><div className="warning">Force/energy ledger disabled. Complete capture refers only to the declared control probe; scientific qualification is NotReady.</div>
 <div className="chart-pair"><Spark points={history} field="sentinelSpeedMps" title="Node 0 speed · control probe" unit="m/s"/><Spark points={history} field="physicsStepElapsedUs" title="Native step elapsed · control probe" unit="µs"/></div></>:<>
 <div className="metrics">{[
 ['COM speed',sample?norm(sample.momentumKgMps)/sample.massKg:null,'m/s'],
 ['Momentum',sample?norm(sample.momentumKgMps):null,'kg·m/s'],
 ['Node kinetic energy',sample?.kineticJ,'J'],
 ['Peak node force',sample?.peakNodeForceN,'N'],
 ['Observed mass',sample?.massKg,'kg'],
 ['Required records lost',current?.workerStatus?.dropped??sample?.dropped??current?.metrics?.dropped,'records']
 ].map(([title,value,unit])=><div className="metric" key={title}><span>{title}</span><strong>{fmt(value)}<small>{unit}</small></strong></div>)}</div>
 <Spark points={history} field="forceN" vector title="Consumed force components" unit="N · WORLD AXES"/>
 <div className="chart-pair"><Spark points={history} field="kineticJ" title="Node kinetic energy" unit="J"/><Spark points={history} field="workResidualJ" title="Kinetic / work residual" unit="J / TICK"/></div>
 <div className="chart-pair"><Spark points={history.map(p=>({...p,mechanicalJ:p.kineticJ+(p.gravityPotentialJ??0)+(p.linearElasticJ??0)}))} field="mechanicalJ" title="K + gravity + linear beam storage" unit="J"/>
 <Spark points={history} field="mechanicalResidualJ" title="Core energy closure discrepancy" unit="J / TICK"/></div>
 <section className="accounting"><div className="section-title"><h3>Force and work attribution</h3><span>CONSUMED / GENERATED EPOCHS</span></div>
 <p>Carried base from tick {sample?.consumedFromTick??'—'}; ground/object contact is added at consumption; force increments generated in tick {sample?.generatedTick??'—'}. Internal forces can cancel in the vector sum; node-level unaccounted force remains visible.</p>
 <table><thead><tr><th>Channel</th><th>Consumed F · X / Y / Z N</th><th>Work · J / tick</th><th>Generated |F| · N</th></tr></thead>
 <tbody>{Object.entries(sample?.channels??{}).map(([name,c])=><tr key={name}><td>{name}</td><td>{c.forceN.map(v=>fmt(v,4)).join(' / ')}</td><td>{fmt(c.workJ,6)}</td><td>{fmt(norm(c.generatedN),4)}</td></tr>)}</tbody></table>
 <div className="env-grid"><div>Unattributed node force L1<strong>{fmt(sample?.unattributedNodeForceL1N,8)} N</strong></div>
 <div>Unsupported active storage<strong>{sample?.unclosedBeams??'—'} beams</strong></div><div>Linear elastic storage<strong>{fmt(sample?.linearElasticJ,5)} J</strong></div>
 <div>Gravity storage<strong>{fmt(sample?.gravityPotentialJ,5)} J</strong></div></div>
 <p>Wind port: {fmt(sample?.windWorkJ,7)} J/tick · relative-flow drag work: {fmt(sample?.relativeDragWorkJ,7)} J/tick. Beam removal storage is a model bookkeeping port; fracture dissipation is not inferred.</p></section>
 {current?.metrics?.qualification&&<section className="accounting"><div className="section-title"><h3>Scientific qualification</h3><span>{current.metrics.qualification.status}</span></div>
 <p>{current.metrics.qualification.scope}</p><table><thead><tr><th>Check</th><th>Observed</th><th>Maximum</th><th>Result</th></tr></thead><tbody>
 {current.metrics.qualification.checks.map(c=><tr key={c.name}><td>{c.name}</td><td>{scienceFmt(c.observed)}</td><td>{scienceFmt(c.limit)}</td><td>{c.passed?'Passed':'Failed'}</td></tr>)}</tbody></table></section>}
 </>}
 {['barrier-v1','impact-yield-v1','impact-fracture-v1'].includes(current?.definition?.scenario)&&<section className="accounting impact-panel"><div className="section-title"><h3>Controlled barrier / detailed impact</h3><span>{current.metrics?.impactQualification?.status??'CAPTURING'}</span></div>
 <p>{current.execution==='Finalizing'&&<strong>Physics finished; native archive is draining. </strong>}{current.definition.scenario==='barrier-v1'?`Approach/capture profile: barrier-approach-capture-v1. Scientific vehicle qualification: ${current.validation}.`:`Two-mass impact profile: local native-law checks and dense/aggregate parity. Scoped qualification: ${current.validation}. Vehicle and material calibration remain unqualified.`} {current.definition.detailFault!=='none'&&<strong className="bad">Injected qualification fault: {current.definition.detailFault}</strong>}</p>
 {current.metrics?.impactTimeline&&<div className="collision-sequence"><h4>Observed collision sequence</h4><p>Contact tick {current.metrics.impactTimeline.firstContactTick} → first parameter change {current.metrics.impactTimeline.firstParameterTick??'none'} → first strength change {current.metrics.impactTimeline.firstStrengthTick??'none'} → first removal {current.metrics.impactTimeline.firstRemovalTick??'none'}.</p><p>These transitions occur during motion after contact. Signed storage removal is not calibrated fracture dissipation.</p></div>}
 <div className="env-grid"><div>First consumed contact<strong>Tick {current.impact?.triggerTick??current.metrics?.impactDetail?.triggerTick??'—'}</strong></div>
 <div>Peak individual contact<strong>{fmt(current.metrics?.impactDetail?.peakApplicationForceN??current.impact?.peakApplicationForceN)} N</strong></div>
 <div>Peak net barrier force<strong>{fmt(current.metrics?.impactDetail?.peakNetBarrierForceN??current.impact?.peakNetBarrierForceN)} N</strong></div>
 <div>Barrier impulse X / Y / Z<strong>{(current.metrics?.impactDetail?.barrierImpulseNs??current.impact?.barrierImpulseNs??[]).map(v=>fmt(v)).join(' / ')} N·s</strong></div>
 <div>Required detail frames<strong>{current.metrics?.impactDetail?.records??current.detailProgress?.durable??current.impact?.detailDurable??'—'}</strong></div>
 <div>Detail loss<strong>{current.metrics?.impactDetail?.dropped??current.workerStatus?.detailDropped??'—'}</strong></div></div>
 <Spark points={current.impactHistory??[]} field="peakNetBarrierForceN" title="Barrier contact force · peak preserved per summary" unit="N"/>
 <p>Archive window: {current.metrics?.impactDetail?.firstTick??'—'} to {current.metrics?.impactDetail?.lastTick??'—'} · parameter transitions {current.metrics?.impactDetail?.parameterTransitions??'—'} · strength transitions {current.metrics?.impactDetail?.strengthTransitions??'—'} · removed beams {current.metrics?.impactDetail?.removedBeams??'—'}. Dense beam capture preserves transitions omitted from the aggregate projection. Removed storage is not measured fracture dissipation.</p>
 {current.metrics?.impactDetail?.problem&&<div className="warning">{current.metrics.impactDetail.problem}</div>}
 {current.metrics?.impactQualification?.checks?.length>0&&<table><thead><tr><th>Approach / capture check</th><th>Observed</th><th>Limit</th><th>Result</th></tr></thead><tbody>{current.metrics.impactQualification.checks.map(c=><tr key={c.name}><td>{c.name}</td><td>{scienceFmt(c.observed)}</td><td>{scienceFmt(c.limit)}</td><td>{c.passed?'Passed':'Failed'}</td></tr>)}</tbody></table>}
 </section>}
 {current?.metrics?.impactDetail?.records>0&&<DetailInspector key={'detail-'+current.id} attempt={current}/>}
 {current?.metrics?.beamTransitions&&<TransitionView key={'transition-'+current.id} attempt={current}/>}
 {current?.metrics?.performanceProbe&&<section className="accounting"><div className="section-title"><h3>Performance probe</h3><span>RELEASED STEPS · WALL ELAPSED</span></div><p>Median {fmt(current.metrics.performanceProbe.medianUs,3)} µs · p95 {fmt(current.metrics.performanceProbe.p95Us,3)} µs · {current.metrics.performanceProbe.releasedRecords} released records · {current.metrics.performanceProbe.fingerprints} state fingerprints. Timing includes native work, job barriers and enabled ledger reduction; probe sampling/queueing is excluded. Fingerprints are diagnostic samples, not a checkpoint.</p></section>}
 <div className="bottom-pair"><section className="environment"><div className="section-title"><h3>Effective dry environment</h3><span>{sample&&!off?'NATIVE SAMPLE':'REQUESTED'}</span></div>
 <div className="env-grid"><div>Gravity<strong>{fmt(sample?.gravityMps2??env.gravity)} m/s²</strong></div><div>Air density<strong>{fmt(sample?.densityKgM3??env.density,3)} kg/m³</strong></div><div>Temperature<strong>{fmt(env.temperatureK)} K</strong></div><div>Steady wind<strong>{(sample?.windMps??[env.windX,env.windY,env.windZ]).map(v=>fmt(v)).join(' / ')} m/s</strong></div></div><p>{['coast-v1','barrier-v1'].includes(current?.definition?.scenario)?'Density and relative wind feed generic dry drag. Temperature is recorded; thermal exchange is outside this model.':'Pinned fixtures disable drag. Density and temperature are metadata; gravity is applied only in the free-fall fixture.'}</p></section>
 <section className="events"><div className="section-title"><h3>Attempt timeline</h3><span>DURABLE EVENTS</span></div>{current?.events?.slice(-5).reverse().map(e=><div className="event" key={e.sequence}><i/><div><strong>{e.kind}</strong><p>{e.message}</p></div></div>)??<p>No attempt events yet.</p>}</section></div>
 {current&&<section className="archive"><div><h3>Retained evidence</h3><p>Every-step binary records and checksums, manifests, requested inputs and scoped outcomes.</p><div className="links">{['manifest.json','result.json','process-provenance.json',...(off?['probe.rort']:['steps.rort','beam-transitions.jsonl']),...(['barrier-v1','impact-yield-v1','impact-fracture-v1'].includes(current.definition.scenario)?['detail.rort','detail-health.json','detail-profile.json','barrier.json',...(current.definition.scenario==='barrier-v1'?['approach.json']:[]),'impact-events.jsonl','impact-beam-transitions.jsonl','contact-materials.json']:[]),...(!off&&current.definition.performanceProbe?['probe.rort']:[])].map(name=><a key={name} href={'/api/attempts/'+current.id+'/artifacts/'+name}>{name}</a>)}</div></div><div className="controls"><button disabled={!terminal.includes(current.execution)} onClick={()=>command('retry')}>New retry</button><button disabled={!terminal.includes(current.execution)||current.archived} onClick={()=>command('archive')}>{current.archived?'Archived · retained':'Mark archived'}</button></div></section>}
 <footer>Captured sample: {fmt(sample?.timeSeconds,3)} s; native clock and recorder publication are independent. Coverage: {current?.coverage??'Awaiting native worker'}. Complete capture alone does not establish physical validation.</footer>
 </section></div></main></div>;
}
createRoot(document.getElementById('root')).render(<App/>);
