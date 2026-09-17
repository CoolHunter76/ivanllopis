(()=>{const q=s=>document.querySelector(s),toggle=q('#ai-toggle'),panel=q('#ai-panel'),close=q('#ai-close'),form=q('#ai-form'),input=q('#ai-input'),messages=q('#ai-messages'),history=[];if(!toggle)return;const add=(text,klass='')=>{const p=document.createElement('p');p.textContent=text;p.className=klass;messages.appendChild(p);messages.scrollTop=messages.scrollHeight;return p};toggle.onclick=()=>{panel.hidden=false;input.focus()};close.onclick=()=>panel.hidden=true;form.onsubmit=async event=>{event.preventDefault();const message=input.value.trim();if(!message)return;add(message,'ai-user');input.value='';input.disabled=true;const loading=add('Pensando...');try{const response=await fetch('/api/assistant/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,history:history.slice(-6),language:document.documentElement.lang||'es'})});const data=await response.json();if(!response.ok)throw new Error(data.detail||'Error');loading.textContent=data.answer;history.push({role:'user',content:message},{role:'assistant',content:data.answer})}catch(error){loading.textContent=error.message;loading.className='ai-error'}finally{input.disabled=false;input.focus()}}})();

(() => {
  const shell = document.getElementById("ai-chat-shell");
  const panel = document.getElementById("ai-panel");
  const toggle = document.getElementById("ai-toggle");
  const close = document.getElementById("ai-close");
  if (!shell || !panel || !toggle || !close || shell.dataset.sidecarReady === "true") return;
  shell.dataset.sidecarReady = "true";
  const openAssistant = () => { shell.hidden = false; panel.hidden = false; };
  const closeAssistant = () => { panel.hidden = true; shell.hidden = true; };
  toggle.addEventListener("click", openAssistant);
  close.addEventListener("click", closeAssistant);
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && !shell.hidden) closeAssistant(); });
})();
