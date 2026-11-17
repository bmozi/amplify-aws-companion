
const key='amplify-advanced-reading-v1';
let saved={};try{saved=JSON.parse(localStorage.getItem(key)||'{}');if(!saved||typeof saved!=='object'||Array.isArray(saved))saved={};}catch{}
const boxes=[...document.querySelectorAll('[data-lesson]')];
function render(){let n=0;for(const box of boxes){box.checked=saved[box.dataset.lesson]===true;if(box.checked)n++;}const p=document.querySelector('progress');if(p)p.value=n;const s=document.querySelector('#progress-status');if(s)s.textContent=`${n} of ${boxes.length} lessons marked read. This is not a cloud verification record.`;}
for(const box of boxes)box.addEventListener('change',()=>{saved[box.dataset.lesson]=box.checked;try{localStorage.setItem(key,JSON.stringify(saved));}catch{}render();});render();
document.querySelector('#export-progress')?.addEventListener('click',()=>{const blob=new Blob([JSON.stringify({kind:'reading-progress-only',exportedAt:new Date().toISOString(),lessons:saved},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='amplify-reading-progress.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
