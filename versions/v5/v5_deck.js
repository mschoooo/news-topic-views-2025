const slides=[...document.querySelectorAll('.slide')];
const meta=JSON.parse(document.querySelector('#slide-meta').textContent);
const stage=document.querySelector('#stage');
const W=Number(stage.dataset.width)||1920,H=Number(stage.dataset.height)||1080;
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let current=0,notesOpen=false,revealTimer=null;
function resize(){
 const viewportWidth=document.documentElement.clientWidth;
 const viewportHeight=document.documentElement.clientHeight;
 const side=notesOpen&&viewportWidth>650?430:0;
 const below=notesOpen&&viewportWidth<=650?viewportHeight*.42:0;
 const w=viewportWidth-side,h=viewportHeight-below-52;
 const scale=Math.min(w/W,h/H);
 stage.style.transform=`translate(${(w-W*scale)/2}px,${(h-H*scale)/2}px) scale(${scale})`;
}
function go(n,update=true){
 if(revealTimer){clearTimeout(revealTimer);revealTimer=null}
 current=Math.max(0,Math.min(slides.length-1,n));
 slides.forEach((s,i)=>{s.classList.toggle('active',i===current);s.setAttribute('aria-hidden',i!==current)});
 document.querySelector('#position').textContent=`${current+1} / ${slides.length}`;
 document.querySelector('.progress').style.width=`${(current+1)/slides.length*100}%`;
 document.querySelector('.notes h2').textContent=`${current+1}. ${meta[current].title}`;
 document.querySelector('.note-text').textContent=meta[current].notes;
 document.querySelector('#announcer').textContent=meta[current].title;
 if(update)history.replaceState(null,'',`#${current+1}`);
 const targets=slides[current].querySelectorAll('.reveal');
 if(!reduced.matches&&window.anime&&targets.length){
  const finish=()=>{anime.remove(targets);targets.forEach(e=>{e.style.opacity=1;e.style.transform='none'})};
  anime.remove(targets);anime({targets,opacity:[1,1],translateY:[10,0],duration:350,delay:anime.stagger(75),easing:'easeOutCubic',complete:finish});
  revealTimer=setTimeout(finish,700);
 }
 else targets.forEach(e=>{e.style.opacity=1;e.style.transform='none'});
 resize();
}
function notes(){notesOpen=!notesOpen;document.querySelector('#notes-pane').classList.toggle('open',notesOpen);document.querySelector('#notes').setAttribute('aria-pressed',notesOpen);resize()}
function overview(){document.querySelector('#overview').classList.toggle('open')}
async function fullscreen(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen()}catch(e){console.info('Fullscreen unavailable')}}
document.querySelector('#prev').onclick=()=>go(current-1);
document.querySelector('#next').onclick=()=>go(current+1);
document.querySelector('#notes').onclick=notes;
document.querySelector('.notes .close').onclick=notes;
document.querySelector('#toc').onclick=overview;
document.querySelector('.overview>button').onclick=overview;
document.querySelector('#fullscreen').onclick=fullscreen;
meta.forEach((s,i)=>{const b=document.createElement('button');b.textContent=`${String(i+1).padStart(2,'0')}  ${s.title}`;b.onclick=()=>{overview();go(i)};document.querySelector('.toc').appendChild(b)});
window.addEventListener('keydown',e=>{
 if(e.ctrlKey||e.metaKey||e.altKey||/INPUT|TEXTAREA|SELECT/.test(e.target.tagName))return;
 if(e.key==='Escape'){document.querySelector('#overview').classList.remove('open');return}
 if(document.querySelector('#overview').classList.contains('open'))return;
 if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();go(current+1)}
 if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();go(current-1)}
 if(e.key==='Home'){e.preventDefault();go(0)}
 if(e.key==='End'){e.preventDefault();go(slides.length-1)}
 if(e.key.toLowerCase()==='n')notes();if(e.key.toLowerCase()==='o')overview();if(e.key.toLowerCase()==='f')fullscreen();
});
let sx=null;
stage.addEventListener('touchstart',e=>sx=e.changedTouches[0].clientX,{passive:true});
stage.addEventListener('touchend',e=>{if(e.target.closest('a'))return;const dx=e.changedTouches[0].clientX-sx;if(Math.abs(dx)>70)go(current+(dx<0?1:-1))},{passive:true});
window.addEventListener('resize',resize);
window.addEventListener('hashchange',()=>{const n=parseInt(location.hash.slice(1));if(n)go(n-1,false)});
go((parseInt(location.hash.slice(1))||1)-1,false);
