import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const root=process.argv[2],modulePath=process.argv[3];
if(!root||!modulePath)throw Error('Usage: node render-implementation.mjs <repo> <marked.esm.js>');
const {marked}=await import(pathToFileURL(modulePath).href);
const here=path.dirname(fileURLToPath(import.meta.url));
const source=path.join(root,'doc/project/design/trial-platform-implementation-spec.md');
const output=path.join(root,'doc/project/reports/trial-implementation-spec-2026-10-08.html');
const md=fs.readFileSync(source,'utf8');
const style=fs.readFileSync(path.join(root,'doc/project/research/2026-10-08/report-style.css'),'utf8');
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function tile(x,y,w,h,title,lines,tone='light'){
 const colors=tone==='dark'?['#183b4c','#ffffff','#dbecee']:tone==='amber'?['#fff1df','#713e12','#795731']:['#e9f5f3','#125b59','#42636a'];
 return '<g><rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="10" fill="'+colors[0]+'" stroke="#b4c6cb"/><text x="'+(x+16)+'" y="'+(y+29)+'" font-size="16" font-weight="700" fill="'+colors[1]+'">'+esc(title)+'</text>'+lines.map((s,i)=>'<text x="'+(x+16)+'" y="'+(y+57+i*23)+'" font-size="13" fill="'+colors[2]+'">'+esc(s)+'</text>').join('')+'</g>';
}
const arrow=(x1,y1,x2,y2)=>'<path d="M'+x1+','+y1+' L'+x2+','+y2+'" fill="none" stroke="#64818c" stroke-width="2" marker-end="url(#arrow)"/>';
function figure(id,title,desc,w,h,body,caption){
 return '<figure class="figure" id="'+id+'"><div class="figure-head">'+esc(title)+'</div><div class="svg-scroll" tabindex="0" aria-label="Scrollable architecture diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+w+' '+h+'" role="img" aria-labelledby="'+id+'-title '+id+'-desc"><title id="'+id+'-title">'+esc(title)+'</title><desc id="'+id+'-desc">'+esc(desc)+'</desc><defs><marker id="'+id+'-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#64818c"/></marker></defs>'+body.replaceAll('url(#arrow)','url(#'+id+'-arrow)')+'</svg></div><figcaption>'+esc(caption)+'</figcaption></figure>';
}
const architecture=figure('implementation-boundaries','Selected architecture · local React, .NET and native RoR','A React workbench sends commands to a .NET coordinator, which launches an isolated instrumented RoR worker. Native physics feeds retained chunks, then analysis. Reduced snapshots travel to the coordinator and workbench; the native scene remains a separate window.',960,493,
 tile(12,16,264,139,'React workbench',['Authoring · queue · live charts','Archived results · manual actions','Local browser, initially'])+
 tile(348,16,264,139,'.NET coordinator',['Revisions · sequential attempts','Process / command ownership','HTTP / SignalR · SQLite'],'dark')+
 tile(684,16,264,139,'C++ RoR trial worker',['Setup · environment · physics','Force / energy epochs · capture','Private profile per attempt'])+
 arrow(276,61,342,61)+arrow(348,116,282,116)+arrow(612,61,678,61)+arrow(684,116,618,116)+
 '<text x="311" y="48" font-size="11" fill="#526675" text-anchor="middle">intent</text><text x="311" y="137" font-size="11" fill="#526675" text-anchor="middle">live / results</text><text x="648" y="48" font-size="11" fill="#526675" text-anchor="middle">command</text><text x="648" y="137" font-size="11" fill="#526675" text-anchor="middle">ACK / status</text>'+
 tile(12,225,264,139,'Analysis / validation',['Balances · coverage · fixtures','Repeat comparisons · reports','Scoped outcomes'],'amber')+
 tile(348,225,264,139,'Retained archive',['Binary chunks · manifests','Events · gaps · health counters','Explicit manual retention'],'amber')+
 tile(684,225,264,139,'Separate RoR window',['Source-built scene evidence','Images / native-window video','3D scientific inspector later'])+
 arrow(480,161,480,219)+arrow(348,294,282,294)+arrow(816,161,816,219)+
 '<path d="M735,161 L735,192 L548,192 L548,219" fill="none" stroke="#64818c" stroke-width="2" marker-end="url(#arrow)"/><text x="588" y="184" font-size="12" fill="#526675">raw capture</text>'+
 '<path d="M144,219 L144,193 L414,193 L414,161" fill="none" stroke="#64818c" stroke-width="2" marker-end="url(#arrow)"/>'+
 '<text x="16" y="411" font-size="15" font-weight="700" fill="#125b59">Native timing owns the measurements. The archive owns the evidence.</text><text x="16" y="441" font-size="13" fill="#526675">Every-step accounting / event detail is independent of the 10–20 Hz dashboard.</text><text x="16" y="467" font-size="13" fill="#526675">Named pipes, SQLite and binary chunk layouts are proposed engineering choices.</text>',
 'Confirmed module direction; subsystem contracts remain to be implemented and qualified. The diagrams show planned data flow, not a running system.');
const quality=figure('quality-policy','Execution, capture and validation · independent outcomes','Required measurement loss continues the active trial, marks capture incomplete, and prevents a passing scientific validation result. An individual completed or failed attempt may allow the next independent trial; a shared blocker holds new launches. A crash can be retried manually as a new attempt.',960,421,
 tile(12,16,276,112,'Required measurement gap',['Continue active observation','Preserve later records / gaps'],'amber')+
 tile(342,16,276,112,'Capture: Incomplete',['Sticky quality state','Normal finish remains possible'],'amber')+
 tile(672,16,276,112,'Validation: cannot pass',['Explicit unavailable / failed checks','No silent reconstruction'],'amber')+
 arrow(288,72,336,72)+arrow(618,72,666,72)+
 tile(12,168,276,112,'Attempt completes / fails',['Retain its outcome and evidence','No automatic retries'])+
 tile(342,168,276,112,'Next independent trial',['Continue eligible serial queue','New process / private results'])+
 tile(672,168,276,112,'Shared blocking problem',['Hold new launches','Display reason / resolve blocker'],'dark')+
 arrow(288,224,336,224)+
 '<text x="638" y="229" font-size="19" font-weight="700" fill="#526675">≠</text>'+
 '<rect x="12" y="325" width="936" height="76" rx="10" fill="#f8fafb" stroke="#b4c6cb"/><text x="29" y="353" font-size="15" font-weight="700" fill="#183b4c">Crash / cancellation preserve partial evidence. Manual retry creates a fresh attempt.</text><text x="29" y="379" font-size="13" fill="#526675">UI coalescing is distinct from a missing required measurement record.</text>',
 'D008.2–D008.4 govern required capture loss, queue progression and retry behavior. Storage preflight protects new launches; D012 retains data until explicit manual archive/cleanup.');
let body=marked.parse(md,{gfm:true}).replace(/<h1>.*?<\/h1>\n?/,'');
let diagrams=0;
body=body.replace(/<pre><code class="language-mermaid">[\s\S]*?<\/code><\/pre>/g,()=>[architecture,quality][diagrams++]);
if(diagrams!==2)throw Error('Expected two Mermaid diagrams');
const nav=[];
body=body.replace(/<h2>(.*?)<\/h2>/g,(all,title)=>{const id='section-'+String(nav.length+1).padStart(2,'0');nav.push({id,title});return '<h2 id="'+id+'">'+title+'</h2>';});
let tables=0;
body=body.replace(/<table>[\s\S]*?<\/table>/g,t=>'<div class="table-scroll" tabindex="0" aria-label="Scrollable data table '+(++tables)+'">'+t+'</div>');
body=body.replace(/href="([^"]+)"/g,(all,href)=>{
 if(/^(?:[a-z][a-z\d+.-]*:|#|\/)/i.test(href))return all;
 const [file,fragment]=href.split('#');
 const target=path.resolve(path.dirname(source),decodeURIComponent(file));
 const relative=path.relative(path.dirname(output),target).split(path.sep).map(encodeURIComponent).join('/');
 return 'href="'+relative+(fragment?'#'+fragment:'')+'"';
});

const explorer='<aside class="policy-explorer" id="policy-explorer" aria-label="Illustrative confirmed policy explorer"><div class="eyebrow">Confirmed policies · illustrative outcomes</div><h3>Follow an attempt through a condition</h3><p>This is a documentation aid, not live telemetry or a simulated result.</p><label for="policy-case">Condition<select id="policy-case"><option value="complete">Normal execution with complete capture</option><option value="gap">Required measurement gap</option><option value="crash">Native worker crashes</option><option value="pause">Acknowledged pause</option><option value="storage">Insufficient storage before launch</option><option value="failedcheck">Scoped validation check fails</option><option value="disconnect">Browser dashboard disconnects</option></select></label><div class="policy-results" aria-live="polite">'+['execution','capture','validation','queue'].map(key=>'<div><span>'+key.charAt(0).toUpperCase()+key.slice(1)+'</span><output id="policy-'+key+'"></output></div>').join('')+'</div><p id="policy-note"></p></aside>';
body=body.replace(/(<h2 id="section-05">)/,explorer+'$1');
const extraCSS=String.raw`
.summary-card h2{border:0;padding:0}
.policy-explorer{background:#e8f3f2;border:1px solid #add2ce;border-radius:12px;margin:30px 0;padding:26px}
.policy-explorer h3{margin:7px 0 10px}.policy-explorer .eyebrow{color:#087c79}
.policy-explorer>p{font-size:14px}.policy-explorer label{display:block;font-size:14px;font-weight:600;max-width:560px}
.policy-explorer select{display:block;width:100%;margin-top:8px;border:1px solid #9ebdbe;border-radius:5px;padding:10px;background:white;color:#172e3d;font:14px "Segoe UI",sans-serif}
.policy-results{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:22px 0}
.policy-results>div{background:white;padding:15px 18px;border-radius:7px}.policy-results span{display:block;text-transform:uppercase;letter-spacing:.07em;font-size:11px;color:#526675}
.policy-results output{display:block;font-size:17px;font-weight:650;color:#005b5b;line-height:1.5;margin-top:5px}
@media(max-width:780px){.policy-explorer{padding:20px}.policy-results{grid-template-columns:1fr}}
@media print{.policy-explorer{break-inside:avoid}.policy-explorer select{border:0}}
`;
const hero='<header class="hero"><div class="eyebrow">Implementation specification / Review baseline 0.1 / 08 October 2026</div><h1>A measured trial.<br>A traceable result.</h1><p>The completed Q&A, consolidated into a native force-and-energy pipeline, environmental foundation and React/.NET trial workbench.</p><div class="meta">Fork: bert-systems/rigs-of-rods-trials · source e85535569102 · 15 confirmed selections<br>Documentation baseline. New engine instrumentation and trial software remain unimplemented.</div><div class="actions"><a href="../design/trial-platform-implementation-spec.md">Canonical specification</a><a href="../design/implementation-decisions.md">Confirmed decision log</a><a href="trial-architecture-options-2026-10-08.html">Architecture evaluation</a><a href="../../../PROJECT.md">Project introduction</a></div></header>';
const summary='<div class="summary-grid"><div class="summary-card"><div class="eyebrow">Confirmed delivery</div><h2>Ground impacts first</h2><p>Pinned Daf / Simple2, controlled coast and analytical fixtures. React with a .NET coordinator.</p></div><div class="summary-card"><div class="eyebrow">Honest outcomes</div><h2>Keep observing after loss</h2><p>Required gaps stay incomplete and cannot pass validation. Independent queued trials can continue.</p></div><div class="summary-card"><div class="eyebrow">Engineering proposals</div><h2>Measure before accepting</h2><p>Fixture numbers, tolerances, transports and resource budgets require versioned contracts and evidence.</p></div></div>';
const sidebar='<aside class="sidebar"><div class="brand">rigs-of-rods-trials</div><div class="eyebrow">Implementation baseline</div><nav aria-label="Report sections">'+nav.map(x=>'<a href="#'+x.id+'">'+x.title+'</a>').join('')+'</nav><small>Q&A complete.<br>14 epics · five delivery gates.<br>Preserve recorded data until manual archive/cleanup.</small></aside>';
const script=fs.readFileSync(path.join(here,'implementation-client.js'),'utf8');
const html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RoR Trials — Implementation Specification</title><style>'+style+extraCSS+'</style></head><body>'+sidebar+'<main class="page">'+hero+summary+'<article>'+body+'</article><footer class="footnote">Generated from the canonical implementation specification. Diagrams and policy explorer are explanatory. Numeric budgets are proposals/calculated examples, not benchmarks or new physics-validation results. No engine or launcher implementation was performed for this review.</footer></main><script>'+script+'</script></body></html>';
fs.writeFileSync(output,html,'utf8');
console.log(JSON.stringify({report:output,bytes:Buffer.byteLength(html),sections:nav.length,tables,diagrams}));
