
'use strict';
const fields=['nodes','hz','channels','minutes','buffer'].map(x=>document.getElementById('budget-'+x));
const format=new Intl.NumberFormat('en-US',{maximumFractionDigits:2});
function calculate(){
 const [n,h,c,m,b]=fields.map(el=>Number(el.value));
 const valid=fields.every(el=>el.value.trim()!==''&&el.checkValidity())&&[n,h,c,m,b].every(Number.isFinite)&&[n,h,c].every(Number.isInteger)&&n>0&&h>0&&h<=2000&&c>=0&&m>0&&b>0;
 const rate=n*h*(9+3*c)*4;
 const values=valid?[rate/1e6,rate*m*60/1e9,b*1048576/rate]:null;
 ['rate','total','lag'].forEach((key,i)=>document.getElementById('budget-'+key).textContent=values?format.format(values[i]):'\u2014');
 document.getElementById('budget-warning').hidden=valid;
}
fields.forEach(el=>el.addEventListener('input',calculate));calculate();
