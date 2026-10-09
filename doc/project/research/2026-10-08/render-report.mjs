
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const root=process.argv[2];
if(!root||!process.argv[3])throw new Error('Usage: node render-report.mjs <repository> <marked.esm.js>');
const {marked}=await import(pathToFileURL(process.argv[3]).href);
const here=path.dirname(fileURLToPath(import.meta.url));
const style=fs.readFileSync(path.join(here,'report-style.css'),'utf8');
const client=fs.readFileSync(path.join(here,'report-client.js'),'utf8');
const md=fs.readFileSync(path.join(root,'platform.md'),'utf8');
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function tile(x,y,w,h,title,lines,kind='native'){
 const colors=kind==='proposed'?['#fff4e4','#c6873c','#824b13']:kind==='dark'?['#173d4e','#173d4e','#fff']:['#e6f3f1','#61aaa1','#125b59'];
 return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="10" fill="'+colors[0]+'" stroke="'+colors[1]+'"/><text x="'+(x+16)+'" y="'+(y+27)+'" fill="'+colors[2]+'" font-size="16" font-weight="700">'+esc(title)+'</text>'+lines.map((s,i)=>'<text x="'+(x+16)+'" y="'+(y+53+i*21)+'" fill="'+colors[2]+'" font-size="13">'+esc(s)+'</text>').join('');
}
function arrow(x1,y1,x2,y2){return '<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="#64818c" stroke-width="2" marker-end="url(#arrowhead)"/>';}
function diagram(id,title,desc,w,h,body,caption){
 return '<figure class="figure"><div class="figure-head">'+esc(title)+'</div><div class="svg-scroll" tabindex="0" aria-label="Scrollable diagram"><svg viewBox="0 0 '+w+' '+h+'" role="img" aria-labelledby="'+id+'-title '+id+'-desc" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial,sans-serif"><title id="'+id+'-title">'+esc(title)+'</title><desc id="'+id+'-desc">'+esc(desc)+'</desc><defs><marker id="'+id+'-arrowhead" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#64818c"/></marker></defs>'+body.replaceAll('url(#arrowhead)','url(#'+id+'-arrowhead)')+'</svg></div><figcaption>'+caption+'</figcaption></figure>';
}
const platform=diagram('platform','Platform map · existing surfaces and proposed additions','Versioned content and controls feed the existing RoR engine. The engine exposes frame state and events. A proposed native observer adds tick-level force and energy data. A proposed experiment layer coordinates setup, execution, acceptance and archiving.',960,430,
 tile(12,12,240,122,'Versioned content',['Vehicles · configurations','Terrains · surfaces · fixtures','Assets and physical parameters'])+
 tile(12,160,240,122,'Existing controls',['AngelScript · commands','Waypoint AI · autopilot','Gravity · persistent forces'])+
 tile(316,69,276,180,'RoR simulation core',['Mass-bearing nodes','Axial spring/damper beams','Contact · drivetrain · aero','Fixed 0.5 ms physics step'],'dark')+
 tile(654,12,294,122,'Exposed observations',['Frame-level node state','Script events · logs · OutGauge','Screenshots · native video'])+
 tile(654,160,294,122,'Native observer · proposed',['Tick and solver-phase identity','Contact impulse · force channels','Work and energy ledger'],'proposed')+
 arrow(252,73,310,127)+arrow(252,220,310,183)+arrow(592,127,648,73)+arrow(592,183,648,220)+
 '<rect x="12" y="328" width="936" height="88" rx="10" fill="#f8fafb" stroke="#899da6" stroke-dasharray="6 4"/><text x="30" y="356" font-size="16" font-weight="700" fill="#25485a">Experiment coordination · proposed evaluation direction</text><text x="30" y="384" font-size="14" fill="#526675">Resolve → verify setup → execute → accept/reject → reduce outcomes → archive evidence</text>'+
 arrow(454,255,454,322),
 'Teal shows source-supported surfaces; amber identifies missing measurement work. The dashed layer is a concept to evaluate in the next design session, not an implemented architecture.');
let ticks='';for(let i=0;i<=66;i++)ticks+='<line x1="'+(120+i*11.6)+'" y1="57" x2="'+(120+i*11.6)+'" y2="77" stroke="#338b86" stroke-width="'+(i%2?1:2)+'"/>';
const timing=diagram('timing','Sampling diagram · a frame can miss an impact peak','Illustrative physics ticks occur every half millisecond. Render or script frames are about 16.7 milliseconds apart at 60 hertz. A five millisecond pulse falls between adjacent frame samples, illustrating why frame samples cannot establish peak contact forces.',960,266,
 '<text x="12" y="72" font-size="13" fill="#526675">Physics ticks</text>'+ticks+
 '<text x="120" y="43" font-size="13" fill="#125b59">0.5 ms per tick (2,000 ticks per simulated second)</text>'+
 '<line x1="120" y1="122" x2="894" y2="122" stroke="#b2c3cc"/><text x="12" y="127" font-size="13" fill="#526675">Script frames</text>'+
 [120,507,894].map((x,i)=>'<circle cx="'+x+'" cy="122" r="7" fill="#173d4e"/><text x="'+x+'" y="150" font-size="12" fill="#526675" text-anchor="middle">'+['0','16.7','33.3'][i]+' ms</text>').join('')+
 '<line x1="120" y1="233" x2="894" y2="233" stroke="#b2c3cc"/><text x="12" y="213" font-size="13" fill="#526675">Force example</text><path d="M120,233 L252,233 C267,233 280,172 310,172 C340,172 354,233 368,233 L894,233" fill="#ffe8c8" stroke="#c6873c" stroke-width="3"/><text x="465" y="201" font-size="14" fill="#824b13">Illustrative 5 ms force pulse</text><text x="465" y="223" font-size="13" fill="#526675">No frame sample observes its peak.</text>',
 'The pulse and 60 Hz frame rate are illustrative, not measured data. Scripts run once per frame; physics advances in tick batches. Solver-phase placement matters even when a node force getter is available.');
const energy=diagram('energy','Energy ledger · measured channels before interpretation','Initial mechanical energy and actuator work feed retained kinetic, gravitational and elastic energy, plus model-dependent damping, plasticity, contact, fracture and fluid transfers. Any unclosed residual remains explicit instead of being called absorbed energy.',960,374,
 tile(12,98,252,135,'Energy entering the window',['Initial kinetic + potential','Initial stored elastic energy','Integrated actuator work'])+
 tile(326,12,332,138,'State retained / transferred',['Node kinetic energy','Gravitational potential','Model-consistent elastic storage','Coupled actors and boundaries'])+
 tile(326,176,332,156,'Model-dependent channels',['Beam damping and plastic work','Contact friction / dissipation','Breakage and constraint changes','Fluid / aerodynamic transfer'],'proposed')+
 tile(722,100,226,134,'Unclosed residual',['Numerics · unobserved terms','Timing / model mismatch','Report and bound explicitly'],'proposed')+
 arrow(264,146,320,87)+arrow(264,188,320,249)+arrow(658,87,716,143)+arrow(658,249,716,195)+
 '<text x="18" y="362" font-size="13" fill="#526675">Kinetic-energy decrease alone is not a measurement of impact absorption.</text>',
 'This diagram lists analytical channels without assigning invented percentages. A defensible ledger needs work integrals, declared boundaries, consistent state times and calibration.');
const lifecycleNames=[
 ['Define',['Question · parameters','Metrics and limits']],
 ['Resolve',['Pin content and build','Validate effective setup']],
 ['Settle / verify',['Fresh state and transient','Pose · mass · health']],
 ['Arm',['Observer and controller','Window · clock alignment']],
 ['Execute',['Drive / fly / impact','Observe actual conditions']],
 ['Gate',['Preconditions and outcome','Reject invalid trials']],
 ['Finalize',['Export data and errors','Compute declared metrics']],
 ['Archive',['Manifest · hashes · media','Compare repetitions']]
];
const positions=[[12,12],[252,12],[492,12],[732,12],[732,151],[492,151],[252,151],[12,151]];
let lifeBody='';
lifecycleNames.forEach((entry,i)=>{const [x,y]=positions[i];lifeBody+=tile(x,y,216,112,(i+1)+'. '+entry[0],entry[1],i===5?'proposed':'native');});
lifeBody+=arrow(228,68,246,68)+arrow(468,68,486,68)+arrow(708,68,726,68)+arrow(840,130,840,145)+arrow(732,207,714,207)+arrow(492,207,474,207)+arrow(252,207,234,207);
const lifecycle=diagram('lifecycle','Trial lifecycle · a conceptual acceptance process','A proposed sequence defines the question, resolves exact content, settles and verifies initial conditions, arms observation, executes, gates outcome validity, finalizes data and archives evidence. Invalid trials are retained with reasons.',960,280,lifeBody,
 'A failed precondition or incomplete capture should produce a rejected trial with a reason. This lifecycle is a research concept; implementation choices await the architecture/design specification.');
const calc='<aside class="calculator" aria-label="Illustrative impact calculation"><div class="eyebrow">Calculated example · not simulation data</div><h4>Momentum, kinetic energy, and mean net force</h4><p>Ideal one-dimensional stop of a fixed mass. Change the speed to see why energy grows faster than momentum.</p><div class="calc-inputs"><label>Mass (kg)<input id="calc-mass" type="number" min="0.000001" step="any" value="1000"></label><label>Approach speed (m/s)<input id="calc-speed" type="number" min="0" step="any" value="10"></label><label>Stopping interval (ms)<input id="calc-stop" type="number" min="0.000001" step="any" value="100"></label></div><div class="calc-results" aria-live="polite"><div><span>Momentum magnitude · kg·m/s</span><output id="calc-momentum"></output></div><div><span>Initial kinetic energy · J</span><output id="calc-energy"></output></div><div><span>Mean net force magnitude · N</span><output id="calc-force"></output></div></div><p id="calc-warning" hidden>Enter finite values: positive mass and stopping interval; nonnegative speed.</p><p>p = mv; K = ½mv²; |F̄<sub>net</sub>| = mv/Δt for a complete stop. Mean net force is not peak contact force. Initial kinetic energy is not measured absorbed energy. Real trials require vector state, a defined body, and other forces.</p></aside>';
const filters='<div class="filters" role="search" aria-label="Filter use-case coverage"><label>Search dimensions<input id="coverage-search" type="search" placeholder="e.g. wind, momentum, flight"></label><label>Capability status<select id="coverage-status"><option value="all">All statuses</option><option>Native</option><option>Compose</option><option>Derive</option><option>Extend</option><option>Unverified</option></select></label><output id="coverage-count" aria-live="polite"></output></div>';
let body=marked.parse(md,{gfm:true,breaks:false});
body=body.replace(/<h1>.*?<\/h1>\n?/,'');
const nav=[];
body=body.replace(/<h2>(.*?)<\/h2>/g,(all,title)=>{
 const id='section-'+String(nav.length+1).padStart(2,'0');nav.push({id,title});
 return '<h2 id="'+id+'">'+title+'</h2>';
});
function afterH2(id,addition){body=body.replace(new RegExp('(<h2 id="'+id+'">.*?<\\/h2>)'),'$1'+addition);}
function afterH3(prefix,addition){body=body.replace(new RegExp('(<h3>'+prefix.replace('.','\\.')+'[^<]*<\\/h3>)'),'$1'+addition);}
afterH2('section-03',platform);afterH3('6.2',timing);afterH2('section-07',energy);afterH3('7.3',calc);afterH3('8.3',lifecycle);
let tables=0;body=body.replace(/<table>[\s\S]*?<\/table>/g,table=>{
 tables++;const coverage=table.includes('<th>Requested dimension</th>');
 if(coverage)table=table.replace('<table>','<table id="coverage-table">');
 return (coverage?filters:'')+'<div class="table-scroll" tabindex="0" aria-label="Scrollable data table '+tables+'">'+table+'</div>'+(coverage?'<p id="coverage-empty" class="empty" hidden>No dimensions match these filters.</p>':'');
});
body=body.replace(/href="([^"]+)"/g,(all,href)=>{
 if(/^(?:[a-z][a-z\d+.-]*:|#|\/)/i.test(href))return all;
 return 'href="../../../'+href+'"';
});
const hero='<header class="hero"><div class="eyebrow">Platform research / 08 October 2026</div><h1>From vehicle sandbox<br>to measurable trials</h1><p>Rigs of Rods capabilities, physics, content and observability — evaluated against repeatable vehicle, impact and flight experiments.</p><div class="meta">Personal fork: bert-systems/rigs-of-rods-trials · source e85535569102 · content 34fefdd12678<br>Evidence boundary: source inspection + official documentation + the preserved driving baseline. No new physics experiments.</div><div class="actions"><a href="../../../platform.md">Canonical platform.md</a><a href="../../../PROJECT.md">Project introduction</a><a href="../research/2026-10-08/references.json">Reference catalog</a></div></header>';
const summary='<div class="summary-grid"><div class="summary-card"><div class="eyebrow">Reuse</div><h2>Simulation and control</h2><p>Deformable vehicles, terrain, AI, scripts and node state provide a practical starting point.</p></div><div class="summary-card"><div class="eyebrow">Instrument</div><h2>The measurement gap</h2><p>Contact-force peaks, work and energy channels need observation at the physics step.</p></div><div class="summary-card"><div class="eyebrow">Validate</div><h2>The physical interpretation</h2><p>Repeatability, asset calibration, gravity behavior and wind need explicit validation.</p></div></div>';
const navigation='<aside class="sidebar"><div class="brand">rigs-of-rods-trials</div><div class="eyebrow">Platform evaluation</div><nav aria-label="Report sections">'+nav.map(n=>'<a href="#'+n.id+'">'+n.title+'</a>').join('')+'</nav><small>54 primary-source / documentation references.<br>Source-supported does not mean every feature was runtime-tested.<br>Design specification follows this research.</small></aside>';
const html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>Rigs of Rods — Platform &amp; Trial Evaluation</title><style>'+style+'</style></head><body>'+navigation+'<main class="page">'+hero+summary+'<article>'+body+'</article><footer class="footnote">Generated from platform.md using the preserved local renderer. Diagrams and calculator are explanatory artifacts, not recorded simulation evidence. Source and citations are pinned where possible; future sessions must recheck the current tree.</footer></main><script>'+client+'</script></body></html>';
const out=path.join(root,'doc/project/reports/platform-evaluation-2026-10-08.html');
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,html,'utf8');
console.log(JSON.stringify({output:out,bytes:Buffer.byteLength(html),sections:nav.length,tables,diagrams:4,references:54}));
