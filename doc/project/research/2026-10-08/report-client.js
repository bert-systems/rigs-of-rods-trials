
'use strict';
const formatter=new Intl.NumberFormat('en-US',{maximumFractionDigits:2});
const fields=['mass','speed','stop'].map(id=>document.getElementById('calc-'+id));
function calculate(){
 const values=fields.map(el=>Number(el.value));
 const [m,v,t]=values;
 const valid=fields.every(el=>el.value.trim()!==''&&el.checkValidity())&&values.every(Number.isFinite)&&m>0&&v>=0&&t>0;
 const result=valid?[m*v,.5*m*v*v,m*v/(t/1000)]:null;
 ['momentum','energy','force'].forEach((id,i)=>document.getElementById('calc-'+id).textContent=result?formatter.format(result[i]):'\u2014');
 document.getElementById('calc-warning').hidden=valid;
}
fields.forEach(el=>el.addEventListener('input',calculate));calculate();
const filter=document.getElementById('coverage-search');
const status=document.getElementById('coverage-status');
const rows=Array.from(document.querySelectorAll('#coverage-table tbody tr'));
function updateCoverage(){
 let n=0;const q=filter.value.trim().toLowerCase(),kind=status.value.toLowerCase();
 for(const row of rows){const label=row.cells[1]?.textContent.toLowerCase()||'';const show=row.cells[0].textContent.toLowerCase().includes(q)&&(kind==='all'||label.includes(kind));row.hidden=!show;if(show)n++;}
 document.getElementById('coverage-count').textContent=n+' of '+rows.length+' dimensions';
 document.getElementById('coverage-empty').hidden=n!==0;
}
filter.addEventListener('input',updateCoverage);status.addEventListener('change',updateCoverage);updateCoverage();
