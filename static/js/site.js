// Sprint 10 - Landing V2 (LF)
const menuButton=document.getElementById('menu-button');
const mobileMenu=document.getElementById('mobile-menu');
if(menuButton&&mobileMenu){menuButton.onclick=()=>mobileMenu.classList.toggle('hidden');}

function switchLanguage(v){
  const p=location.pathname.split('/').filter(Boolean);
  location.href=v+(p[1]==='hobbies'?'/hobbies':'')+location.hash;
}

const revealObserver=new IntersectionObserver(entries=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){entry.target.classList.add('visible');}
  });
},{threshold:.08});

document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

// Animated counters
const counterObserver=new IntersectionObserver(entries=>{
  entries.forEach(entry=>{
    if(!entry.isIntersecting)return;
    const target=entry.target;
    const end=parseInt(target.dataset.count||'0',10);
    let current=0;
    const step=Math.max(1,Math.ceil(end/40));
    const timer=setInterval(()=>{
      current+=step;
      if(current>=end){
        current=end;
        clearInterval(timer);
      }
      target.textContent=current;
    },30);
    counterObserver.unobserve(target);
  });
});

document.querySelectorAll('[data-count]').forEach(el=>counterObserver.observe(el));

// Typewriter effect
const typewriter=document.querySelector('[data-typewriter]');
if(typewriter){
  const text=typewriter.textContent;
  typewriter.textContent='';
  let i=0;
  const timer=setInterval(()=>{
    typewriter.textContent+=text.charAt(i);
    i++;
    if(i>=text.length) clearInterval(timer);
  },35);
}

// Matrix background preserved
(()=>{
 const c=document.getElementById('matrix-background');
 if(!c||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 const x=c.getContext('2d');
 let w,h,s,n,d;
 function r(){const q=Math.min(devicePixelRatio||1,2);w=innerWidth;h=innerHeight;c.width=w*q;c.height=h*q;x.setTransform(q,0,0,q,0,0);s=w<600?14:16;n=Math.ceil(w/s);d=Array.from({length:n},()=>-Math.random()*50)}
 function draw(){x.fillStyle='rgba(1,7,3,.09)';x.fillRect(0,0,w,h);x.font=s+'px monospace';for(let i=0;i<n;i++){x.fillStyle=Math.random()>.92?'#86efacaa':'#22c55e66';x.fillText(Math.random()>.5?'1':'0',i*s,d[i]*s);d[i]=d[i]*s>h&&Math.random()>.985?-15:d[i]+.65}}
 r();setInterval(draw,58);addEventListener('resize',r);
})();
