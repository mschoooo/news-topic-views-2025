const slides=[...document.querySelectorAll('.slide')];
const meta=JSON.parse(document.querySelector('#slide-meta').textContent);
const stage=document.querySelector('#stage');
const W=Number(stage.dataset.width)||1920,H=Number(stage.dataset.height)||1080;
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let current=0,notesOpen=false,motionTimer=null,motionClock=null,printing=false;
let motionTargets=[],motionInstances=[];
const formatCount=(value,decimals=0)=>Number(value).toLocaleString('en-US',{minimumFractionDigits:decimals,maximumFractionDigits:decimals});

// The source DOM always contains final values. Only the current slide animates.
// A wall-clock fallback also finalizes if animation frames stall during loading.
function finishAllMotion(){
 if(motionTimer!==null){clearTimeout(motionTimer);motionTimer=null}
 if(motionClock!==null){clearInterval(motionClock);motionClock=null}
 motionInstances.forEach(a=>a.pause());motionInstances=[];
 if(window.anime&&motionTargets.length)anime.remove(motionTargets);
 motionTargets=[];
 document.querySelectorAll('[data-count-to]').forEach(e=>{
  e.querySelector('.count-display').textContent=formatCount(e.dataset.countTo,Number(e.dataset.decimals)||0);
 });
 document.querySelectorAll('[data-bar]').forEach(e=>e.setAttribute('width',e.dataset.finalWidth));
 document.querySelectorAll('[data-seq],.reveal').forEach(e=>{e.style.opacity='1';e.style.transform='none'});
 document.querySelectorAll('[data-emphasis]').forEach(e=>e.style.removeProperty('--emphasis-opacity'));
}

function playMotion(slide){
 if(reduced.matches||printing||!window.anime)return;
 // One elapsed-time clock drives Anime's easing. It also works when a browser
 // delays animation frames while decoding slide images. No repeated effects.
 const animate=options=>motionInstances.push(anime({...options,autoplay:false}));
 slide.querySelectorAll('[data-count-to]').forEach((el,i)=>{
  const display=el.querySelector('.count-display'),to=Number(el.dataset.countTo),decimals=Number(el.dataset.decimals)||0;
  // Reserve the final width before changing digits so text does not move.
  display.style.minWidth='';display.style.minWidth=display.getBoundingClientRect().width/(stage.getBoundingClientRect().width/W)+'px';
  const state={value:0};motionTargets.push(state);display.textContent=formatCount(0,decimals);
  animate({targets:state,value:to,duration:760,delay:100+i*65,easing:'easeOutCubic',update:()=>{
   const n=decimals?state.value:Math.round(state.value);display.textContent=formatCount(n,decimals);
  },complete:()=>display.textContent=formatCount(to,decimals)});
 });
 slide.querySelectorAll('[data-bar]').forEach(el=>{
  const state={value:0},to=Number(el.dataset.finalWidth);motionTargets.push(state);el.setAttribute('width','0');
  animate({targets:state,value:to,duration:550,delay:Number(el.dataset.bar)*50,easing:'easeOutCubic',update:()=>el.setAttribute('width',state.value),complete:()=>el.setAttribute('width',to)});
 });
 slide.querySelectorAll('[data-seq]').forEach(el=>{
  motionTargets.push(el);el.style.opacity='.12';
  animate({targets:el,opacity:[.12,1],translateY:el.dataset.motion==='fade'?[0,0]:[8,0],duration:330,delay:Number(el.dataset.seq)*50,easing:'easeOutCubic'});
 });
 const reveals=[...slide.querySelectorAll('.reveal')];
 if(reveals.length){motionTargets.push(...reveals);animate({targets:reveals,opacity:[1,1],translateY:[8,0],duration:380,delay:anime.stagger(110),easing:'easeOutCubic'})}
 slide.querySelectorAll('[data-emphasis="1"]').forEach(el=>{
  const state={opacity:0};motionTargets.push(state);
  animate({targets:state,opacity:[{value:.55,duration:180},{value:0,duration:260}],delay:880,easing:'easeInOutSine',update:()=>el.style.setProperty('--emphasis-opacity',state.opacity)});
 });
 if(motionTargets.length){
  const start=performance.now();
  motionClock=setInterval(()=>{
   if(reduced.matches||printing||document.hidden){finishAllMotion();return}
   const elapsed=performance.now()-start;motionInstances.forEach(a=>a.seek(elapsed));
  },16);
  motionTimer=setTimeout(finishAllMotion,1450);
 }
}
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
 finishAllMotion();
 current=Math.max(0,Math.min(slides.length-1,n));
 slides.forEach((s,i)=>{s.classList.toggle('active',i===current);s.setAttribute('aria-hidden',i!==current)});
 document.querySelector('#position').textContent=`${current+1} / ${slides.length}`;
 document.querySelector('.progress').style.width=`${(current+1)/slides.length*100}%`;
 document.querySelector('.notes h2').textContent=`${current+1}. ${meta[current].title}`;
 document.querySelector('.note-text').textContent=meta[current].notes;
 document.querySelector('#announcer').textContent=meta[current].title;
 if(update)history.replaceState(null,'',`#${current+1}`);
 resize();
 playMotion(slides[current]);
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
window.addEventListener('beforeprint',()=>{printing=true;finishAllMotion()});
window.addEventListener('afterprint',()=>{printing=false});
document.addEventListener('visibilitychange',()=>{if(document.hidden)finishAllMotion()});
reduced.addEventListener('change',()=>{if(reduced.matches)finishAllMotion()});
go((parseInt(location.hash.slice(1))||1)-1,false);
