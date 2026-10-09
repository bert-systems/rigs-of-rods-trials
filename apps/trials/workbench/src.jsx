import React, {useEffect,useState,useRef} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';

const initial={name:'Daf steady-wind coast',launchSpeedMps:5,durationSeconds:12,settleSeconds:3,repeats:1,
 environment:{gravity:-9.81,temperatureK:288.15,density:1.225,windX:0,windY:0,windZ:0}};
const norm=v=>v?Math.hypot(...v):0;
const fmt=(n,d=2)=>Number.isFinite(n)?n.toLocaleString(undefined,{maximumFractionDigits:d}):'—';
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
  points.forEach((p,i)=>{const gap=i>0&&p.tick-points[i-1].tick>100;path+=(i===0||gap?'M':'L')+x(i).toFixed(2)+','+y(values[i][axis]).toFixed(2)+' ';});
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
function Field({label,k,env=false,min,max,step='any'}){
 const {form,num}=React.useContext(FormContext);
 return <label>{label}<input type="number" step={step} min={min} max={max} value={env?form.environment[k]:form[k]} onChange={e=>num(k,e.target.value,env)} required/></label>;
}
function App(){
 const [data,setData]=useState(null),[form,setForm]=useState(initial),[selected,setSelected]=useState(null);
 const [error,setError]=useState(''),[live,setLive]=useState(false),[sending,setSending]=useState(false),[tab,setTab]=useState('Trials');
 const token=useRef(null);
 useEffect(()=>{
  let cancelled=false,timer;
  async function poll(){
   try{
    if(!token.current)token.current=(await (await fetch('/api/session')).json()).session;
    const response=await fetch('/api/state');
    if(!response.ok)throw Error('Live state unavailable');
    const next=await response.json();if(!cancelled){setData(next);setLive(true);}
   }catch(e){if(!cancelled)setLive(false);}
   if(!cancelled)timer=setTimeout(poll,100);
  }poll();
  return()=>{cancelled=true;clearTimeout(timer);};
 },[]);
 const attempts=data?.attempts??[];
 const current=attempts.find(a=>a.id===selected)??attempts.at(-1);
 const sample=current?.latest,history=current?.history??[];
 const num=(key,value,env=false)=>setForm(f=>env?{...f,environment:{...f.environment,[key]:value}}:{...f,[key]:value});
 async function post(url,body){
  const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json','X-Trials-Session':token.current??''},body:JSON.stringify(body??{})});
  const value=await response.json();if(!response.ok)throw Error(value.error??'Request rejected');return value;
 }
 async function enqueue(event){
  event.preventDefault();setSending(true);setError('');
  try{const payload={...form,environment:Object.fromEntries(Object.entries(form.environment).map(([k,v])=>[k,Number(v)]))};
  for(const k of ['launchSpeedMps','durationSeconds','settleSeconds','repeats'])payload[k]=Number(payload[k]);
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
 <div className="asset"><span>Vehicle</span><strong>Daf Semi</strong><small>b6b0UID-semi.truck</small></div>
 <div className="asset"><span>Terrain</span><strong>Simple Test Terrain</strong><small>simple2.terrn2</small></div>
 <div className="form-pair"><Field label="Release speed · m/s" k="launchSpeedMps" min="0" max="20"/><Field label="Observe · s" k="durationSeconds" min="1" max="120"/></div>
 <div className="form-pair"><Field label="Settling · s" k="settleSeconds" min="2" max="30"/><Field label="Repeats" k="repeats" min="1" max="20" step="1"/></div>
 <details open={tab==='Environment'}><summary>Gravity, air and steady wind</summary>
 <Field label="Gravity Y · m/s²" k="gravity" env min="-30" max="-.001"/>
 <div className="form-pair"><Field label="Temperature · K" k="temperatureK" env min="180" max="350"/><Field label="Density · kg/m³" k="density" env min=".001" max="3"/></div>
 <div className="wind-fields">{['X','Y','Z'].map(axis=><Field key={axis} label={'Wind '+axis+' · m/s'} k={'wind'+axis} env min="-30" max="30"/>)}</div></details>
 <div className="setup-note">Settle, initialize rolling motion, then coast with propulsion off. Each attempt gets a fresh process and private profile.</div>
 <button className="primary" disabled={sending||!live}>{sending?'Saving revision…':'Queue experiment'} <span>→</span></button></form></FormContext.Provider>
 <div className="scope-note"><strong>Current study scope</strong><p>Consumed force, contact response, momentum and kinetic-work updates. Barrier fixtures and complete force/model energy attribution are pending qualification.</p></div></aside>
 <section className="monitor"><div className="attempts"><div className="section-title"><h2>Trial queue</h2><span>{attempts.length} ATTEMPTS · SERIAL</span></div>
 {attempts.length===0?<div className="empty">Define an experiment to launch the source-built worker.</div>:<div className="queue-list">{attempts.slice().reverse().map(a=><button key={a.id} className={'queue-item '+(a.id===current?.id?'selected':'')} onClick={()=>setSelected(a.id)}><div><strong>{a.definition.name}</strong><small>{a.id.slice(0,8)} · {a.definition.launchSpeedMps} m/s · {a.retryOf?'retry':'new attempt'}</small></div><span className={'pill '+a.execution.toLowerCase()}>{a.execution}</span></button>)}</div>}</div>
 <div className="run-header"><div><div className="eyebrow">SELECTED ATTEMPT</div><h2>{current?.definition.name??'No active attempt'}</h2><p>{current?current.id:'Ready for a controlled study'}</p></div><div className="controls">
 {current&&<><button disabled={current.execution!=='Running'} onClick={()=>command('pause')}>Pause</button><button disabled={current.execution!=='Paused'} onClick={()=>command('resume')}>Resume</button><button disabled={!['Running','Paused','Queued'].includes(current.execution)} onClick={()=>command('cancel')}>Cancel</button></>}
 </div></div>
 {current?.blockedReason&&<div className="warning">{current.blockedReason}</div>}
 <div className="quality"><div><span>Execution</span><strong>{current?.execution??'—'}</strong></div><div><span>Capture</span><strong className={current?.capture==='Incomplete'?'bad':''}>{current?.capture??'—'}</strong></div><div><span>Scientific validation</span><strong className="amber">{current?.validation??'Not evaluated'}</strong></div><div><span>Simulation clock</span><strong>{fmt(current?.workerStatus?.timeSeconds??sample?.timeSeconds,3)} <small>s</small></strong></div></div>
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
 <div className="bottom-pair"><section className="environment"><div className="section-title"><h3>Effective dry environment</h3><span>{sample?'NATIVE SAMPLE':'REQUESTED'}</span></div>
 <div className="env-grid"><div>Gravity<strong>{fmt(sample?.gravityMps2??env.gravity)} m/s²</strong></div><div>Air density<strong>{fmt(sample?.densityKgM3??env.density,3)} kg/m³</strong></div><div>Temperature<strong>{fmt(env.temperatureK)} K</strong></div><div>Steady wind<strong>{(sample?.windMps??[env.windX,env.windY,env.windZ]).map(v=>fmt(v)).join(' / ')} m/s</strong></div></div><p>Density and relative wind feed generic dry drag. Temperature is recorded; thermal exchange is outside this model.</p></section>
 <section className="events"><div className="section-title"><h3>Attempt timeline</h3><span>DURABLE EVENTS</span></div>{current?.events?.slice(-5).reverse().map(e=><div className="event" key={e.sequence}><i/><div><strong>{e.kind}</strong><p>{e.message}</p></div></div>)??<p>No attempt events yet.</p>}</section></div>
 {current&&<section className="archive"><div><h3>Retained evidence</h3><p>Every-step binary records and checksums, manifests, requested inputs and scoped outcomes.</p><div className="links">{['manifest.json','result.json','steps.rort','process-provenance.json'].map(name=><a key={name} href={'/api/attempts/'+current.id+'/artifacts/'+name}>{name}</a>)}</div></div><div className="controls"><button disabled={!terminal.includes(current.execution)} onClick={()=>command('retry')}>New retry</button><button disabled={!terminal.includes(current.execution)||current.archived} onClick={()=>command('archive')}>{current.archived?'Archived · retained':'Mark archived'}</button></div></section>}
 <footer>Captured sample: {fmt(sample?.timeSeconds,3)} s; native clock and recorder publication are independent. Coverage: {current?.coverage??'Awaiting native worker'}. Complete capture alone does not establish physical validation.</footer>
 </section></div></main></div>;
}
createRoot(document.getElementById('root')).render(<App/>);
