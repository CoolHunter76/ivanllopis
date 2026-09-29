(() => {
  const room = document.querySelector("[data-arcade-room]");
  if (!room) return;

  const modal = document.querySelector("[data-arcade-modal]");
  const canvas = modal.querySelector("[data-game-canvas]");
  const ctx = canvas.getContext("2d");
  const boot = modal.querySelector("[data-boot-screen]");
  const coin = modal.querySelector("[data-insert-coin]");
  const initials = modal.querySelector("[data-initials]");
  const titleScreen = modal.querySelector("[data-title-screen]");
  const creditNode = modal.querySelector("[data-credit]");
  const recordNode = modal.querySelector("[data-modal-record]");
  const pedrisControls = modal.querySelector("[data-pedris-controls]");
  const names = {
    "gamer-universe-76": "GAMER UNIVERSE 76",
    "sky-patrol-76": "SKY PATROL 76",
    "block-breaker-76": "IVANOID",
    "platform-quest-76": "PLATFORM QUEST 76",
    "metal-command-76": "METAL COMMAND 76",
    "island-hero-76": "ISLAND HERO 76",
    "neon-blocks-76": "PEDRIS",
  };
  const subtitles = {
    "gamer-universe-76": "GAMER PINBALL SYSTEM",
    "sky-patrol-76": "OPERATION NEON STORM",
    "block-breaker-76": "IVANOID // THE NEON WALL",
    "platform-quest-76": "LOST PORTALS",
    "metal-command-76": "IRON FRONT",
    "island-hero-76": "TROPICAL RUN",
    "neon-blocks-76": "BLAUGRANA BLOCKS",
  };


  window.arcade76Assets = window.arcade76Assets || {};
  const loadAsset = (key, url) => {
    const image = new Image();
    image.src = url;
    window.arcade76Assets[key] = image;
  };
  loadAsset("ivanoidPaddle", "/static/images/arcade76/ivanoid-paddle.png");
  loadAsset("skyPlane", "/static/images/arcade76/sky-patrol-plane.png");
  loadAsset("skyEnemyPlane", "/static/images/arcade76/sky-patrol-enemy-plane.png");
  loadAsset("pedrisBackground", "/static/images/arcade76/pedris-background.png");

  const runtime = {
    slug: "", session: "", claim: "", score: 0, credit: 0,
    running: false, paused: false, sound: false, frame: 0,
    game: null, last: 0, cleanups: [],
  };
  let audio;

  const fetchJson = async (url, options) => {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  };
  const tone = (frequency, duration = 0.05) => {
    if (!runtime.sound) return;
    audio ||= new AudioContext();
    const oscillator = audio.createOscillator();
    const gain = audio.createGain();
    oscillator.type = "square";
    oscillator.frequency.value = frequency;
    gain.gain.setValueAtTime(0.025, audio.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audio.currentTime + duration);
    oscillator.connect(gain).connect(audio.destination);
    oscillator.start(); oscillator.stop(audio.currentTime + duration);
  };
  const addCleanup = (cleanup) => runtime.cleanups.push(cleanup);
  const listen = (target, type, handler, options) => {
    target.addEventListener(type, handler, options);
    addCleanup(() => target.removeEventListener(type, handler, options));
  };
  const clearGame = () => {
    runtime.running = false;
    runtime.game?.destroy?.();
    runtime.game = null;
    runtime.cleanups.splice(0).forEach((cleanup) => cleanup());
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };
  const pointer = (event) => {
    const rect = canvas.getBoundingClientRect();
    return {
      x: (event.clientX - rect.left) * canvas.width / rect.width,
      y: (event.clientY - rect.top) * canvas.height / rect.height,
    };
  };
  const drawText = (text, x, y, size = 24, color = "#fff", align = "center") => {
    ctx.fillStyle = color; ctx.font = `800 ${size}px ui-monospace, monospace`;
    ctx.textAlign = align; ctx.fillText(text, x, y);
  };
  const rectHit = (one, two) => one.x < two.x + two.w && one.x + one.w > two.x && one.y < two.y + two.h && one.y + one.h > two.y;

  const hallOfFame = async () => {
    try {
      const data = await fetchJson("/api/arcade/hall-of-fame");
      const list = room.querySelector("[data-arcade-hof]"); list.innerHTML = "";
      Object.entries(data.games).forEach(([key, value]) => {
        const item = document.createElement("li");
        item.innerHTML = `<span>${names[key]}</span><b>${value.initials}</b><u>${String(value.score).padStart(6, "0")}</u>`;
        list.append(item);
      });
    } catch { room.querySelector("[data-arcade-hof]").innerHTML = "<li>ARCADE NETWORK OFFLINE</li>"; }
  };

  const finish = async (score) => {
    if (!runtime.running) return;
    runtime.running = false; runtime.score = Math.max(0, Math.round(score));
    try {
      const data = await fetchJson(`/api/arcade/games/${runtime.slug}/score`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ score: runtime.score, session_token: runtime.session }),
      });
      if (data.is_high_score) {
        runtime.claim = data.claim_token; initials.hidden = false;
        initials.querySelector("[data-new-score]").textContent = String(runtime.score).padStart(6, "0");
      } else { coin.hidden = false; coin.querySelector("button").textContent = "INSERT COIN"; }
    } catch { coin.hidden = false; }
  };

  const baseBackground = (top = "#17245c", bottom = "#040713") => {
    const gradient = ctx.createLinearGradient(0, 0, 0, 960);
    gradient.addColorStop(0, top); gradient.addColorStop(1, bottom);
    ctx.fillStyle = gradient; ctx.fillRect(0, 0, 720, 960);
  };

  function blockBreaker() {
    const paddle = { x: 270, y: 890, w: 180, h: 22 };
    const ball = { x: 360, y: 815, vx: 330, vy: -430, r: 10 };
    let bricks = [];
    for (let row = 0; row < 8; row += 1) for (let col = 0; col < 9; col += 1)
      bricks.push({ x: 28 + col * 75, y: 115 + row * 38, w: 66, h: 27, hp: row < 2 ? 2 : 1, color: `hsl(${185 + row * 23} 90% 62%)` });
    runtime.score = 0;
    const move = (event) => { paddle.x = Math.max(0, Math.min(720 - paddle.w, pointer(event).x - paddle.w / 2)); };
    listen(canvas, "pointermove", move); listen(canvas, "pointerdown", move);
    return {
      update(dt) {
        ball.x += ball.vx * dt; ball.y += ball.vy * dt;
        if (ball.x < ball.r) { ball.x = ball.r; ball.vx = Math.abs(ball.vx); }
        if (ball.x > 720 - ball.r) { ball.x = 720 - ball.r; ball.vx = -Math.abs(ball.vx); }
        if (ball.y < 70) { ball.y = 70; ball.vy = Math.abs(ball.vy); }
        if (ball.y + ball.r >= paddle.y && ball.y < paddle.y + paddle.h && ball.x >= paddle.x && ball.x <= paddle.x + paddle.w) {
          ball.y = paddle.y - ball.r; ball.vy = -Math.abs(ball.vy);
          ball.vx = Math.max(-520, Math.min(520, ball.vx + (ball.x - (paddle.x + paddle.w / 2)) * 3)); tone(420);
        }
        for (const brick of bricks) if (brick.hp > 0 && ball.x > brick.x && ball.x < brick.x + brick.w && ball.y - ball.r < brick.y + brick.h && ball.y + ball.r > brick.y) {
          brick.hp -= 1; ball.vy *= -1; runtime.score += brick.hp ? 50 : 150; tone(250 + runtime.score % 300); break;
        }
        bricks = bricks.filter((brick) => brick.hp > 0);
        if (!bricks.length) finish(runtime.score + 5000);
        else if (ball.y > 990) finish(runtime.score);
      },
      draw() {
        baseBackground(); bricks.forEach((brick) => { ctx.fillStyle = brick.color; ctx.fillRect(brick.x, brick.y, brick.w, brick.h); ctx.strokeStyle = "#fff7"; ctx.strokeRect(brick.x, brick.y, brick.w, brick.h); });
        const paddleImage = window.arcade76Assets?.ivanoidPaddle;
        if (paddleImage?.complete && paddleImage.naturalWidth) {
          ctx.drawImage(paddleImage, paddle.x, paddle.y - 12, paddle.w, 46);
        } else {
          const paddleGradient = ctx.createLinearGradient(paddle.x, 0, paddle.x + paddle.w, 0);
          paddleGradient.addColorStop(0, "#ff4b18");
          paddleGradient.addColorStop(.18, "#fff");
          paddleGradient.addColorStop(.5, "#60656c");
          paddleGradient.addColorStop(.82, "#fff");
          paddleGradient.addColorStop(1, "#ff4b18");
          ctx.fillStyle = paddleGradient;
          ctx.fillRect(paddle.x, paddle.y, paddle.w, paddle.h);
        }
        ctx.fillStyle = "#ffe85c"; ctx.beginPath(); ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2); ctx.fill();
        drawText(`SCORE ${String(runtime.score).padStart(6, "0")}`, 20, 45, 24, "#fff", "left");
      }, destroy() {},
    };
  }

  function skyPatrol() {
    const ship = { x: 330, y: 800, w: 55, h: 60 }; const shots = []; const foes = []; const keys = new Set(); let cooldown = 0, lives = 3, elapsed = 0;
    const down = (event) => keys.add(event.code); const up = (event) => keys.delete(event.code);
    listen(document, "keydown", down); listen(document, "keyup", up);
    const move = (event) => { const point = pointer(event); ship.x = point.x - ship.w / 2; ship.y = point.y - 90; };
    listen(canvas, "pointermove", move); listen(canvas, "pointerdown", move);
    runtime.score = 0;
    return { update(dt) { elapsed += dt; cooldown -= dt; if (keys.has("ArrowLeft") || keys.has("KeyA")) ship.x -= 350 * dt; if (keys.has("ArrowRight") || keys.has("KeyD")) ship.x += 350 * dt; if (keys.has("ArrowUp") || keys.has("KeyW")) ship.y -= 350 * dt; if (keys.has("ArrowDown") || keys.has("KeyS")) ship.y += 350 * dt; ship.x = Math.max(0, Math.min(665, ship.x)); ship.y = Math.max(80, Math.min(880, ship.y)); if (cooldown <= 0) { shots.push({ x: ship.x + 25, y: ship.y, w: 6, h: 20 }); cooldown = .13; } if (Math.floor(elapsed * 10) % 7 === 0 && foes.length < 12) foes.push({ x: Math.random() * 665, y: -50, w: 48, h: 42, vy: 130 + elapsed * 1.5 }); shots.forEach((shot) => shot.y -= 560 * dt); foes.forEach((foe) => foe.y += foe.vy * dt); for (const foe of foes) { for (const shot of shots) if (!foe.dead && !shot.dead && rectHit(foe, shot)) { foe.dead = true; shot.dead = true; runtime.score += 200; tone(280); } if (!foe.dead && rectHit(foe, ship)) { foe.dead = true; lives -= 1; if (lives <= 0) finish(runtime.score); } } for (let i = shots.length - 1; i >= 0; i -= 1) if (shots[i].dead || shots[i].y < -30) shots.splice(i, 1); for (let i = foes.length - 1; i >= 0; i -= 1) if (foes[i].dead || foes[i].y > 1000) foes.splice(i, 1); }, draw() { baseBackground("#0a3150", "#061018"); for (let y = 0; y < 960; y += 70) { ctx.strokeStyle = "#55ddff22"; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(720, y); ctx.stroke(); } const planeImage = window.arcade76Assets?.skyPlane;
        if (planeImage?.complete && planeImage.naturalWidth) {
          ctx.drawImage(planeImage, ship.x, ship.y, ship.w, ship.h);
        } else {
          ctx.fillStyle = "#d8d09a";
          ctx.beginPath();
          ctx.moveTo(ship.x + 27, ship.y);
          ctx.lineTo(ship.x + 55, ship.y + 58);
          ctx.lineTo(ship.x + 27, ship.y + 48);
          ctx.lineTo(ship.x, ship.y + 58);
          ctx.closePath();
          ctx.fill();
        } ctx.fillStyle = "#ffe85c"; shots.forEach((shot) => ctx.fillRect(shot.x, shot.y, shot.w, shot.h)); const enemyPlaneImage = window.arcade76Assets?.skyEnemyPlane;
        foes.forEach((foe) => {
          if (enemyPlaneImage?.complete && enemyPlaneImage.naturalWidth) {
            ctx.drawImage(enemyPlaneImage, foe.x, foe.y, foe.w, foe.h);
          } else {
            ctx.fillStyle = "#ff526b";
            ctx.beginPath();
            ctx.moveTo(foe.x + 24, foe.y + 42);
            ctx.lineTo(foe.x, foe.y);
            ctx.lineTo(foe.x + 24, foe.y + 12);
            ctx.lineTo(foe.x + 48, foe.y);
            ctx.closePath();
            ctx.fill();
          }
        }); drawText(`SCORE ${String(runtime.score).padStart(6, "0")}  SHIPS ${lives}`, 20, 43, 22, "#fff", "left"); }, destroy() {} };
  }

  function neonBlocks() {
    const cols = 10, rows = 20, cell = 34, ox = 190, oy = 130; const board = Array.from({ length: rows }, () => Array(cols).fill(0));
    const shapes = [[[1,1,1,1]],[[1,1],[1,1]],[[0,1,0],[1,1,1]],[[1,0],[1,0],[1,1]],[[0,1],[0,1],[1,1]],[[1,1,0],[0,1,1]],[[0,1,1],[1,1,0]]];
    let piece;
    let timer = 0;
    let elapsed = 0;
    let clearedLines = 0;
    let dropInterval = 0.65;
    runtime.score = 0;
    const spawn = () => { piece = { shape: shapes[Math.floor(Math.random()*shapes.length)].map(r=>[...r]), x: 3, y: 0, color: 1 + Math.floor(Math.random()*6) }; if (collides(0,0,piece.shape)) finish(runtime.score); };
    const collides = (dx,dy,shape=piece.shape) => shape.some((row,y)=>row.some((v,x)=>v && (piece.x+x+dx<0 || piece.x+x+dx>=cols || piece.y+y+dy>=rows || (piece.y+y+dy>=0 && board[piece.y+y+dy][piece.x+x+dx]))));
    const lock = () => { piece.shape.forEach((row,y)=>row.forEach((v,x)=>{if(v&&piece.y+y>=0) board[piece.y+y][piece.x+x]=piece.color})); let lines=0; for(let y=rows-1;y>=0;y--) if(board[y].every(Boolean)){board.splice(y,1);board.unshift(Array(cols).fill(0));lines++;y++;} runtime.score += [0,100,300,700,1500][lines];
    clearedLines += lines;
    spawn(); };
    const rotate = () => { const rotated = piece.shape[0].map((_,i)=>piece.shape.map(row=>row[i]).reverse()); if(!collides(0,0,rotated)) piece.shape=rotated; };
    const key = e => { if(e.code==='ArrowLeft'&&!collides(-1,0))piece.x--; if(e.code==='ArrowRight'&&!collides(1,0))piece.x++; if(e.code==='ArrowDown'){if(!collides(0,1))piece.y++;else lock();} if(e.code==='ArrowUp'||e.code==='Space')rotate(); };
    listen(document,'keydown',key); listen(canvas,'pointerdown',rotate); let startX=0; listen(canvas,'pointerdown',e=>startX=e.clientX); listen(canvas,'pointerup',e=>{const d=e.clientX-startX;if(Math.abs(d)>30){const dx=d>0?1:-1;if(!collides(dx,0))piece.x+=dx;}}); spawn();
    return {
    update(dt) {
      elapsed += dt;
      timer += dt;

      const timeProgress = Math.min(elapsed / 420, 1);
      const lineProgress = Math.min(clearedLines / 60, 1);
      const difficultyProgress = Math.min(
        timeProgress * 0.78 + lineProgress * 0.22,
        1,
      );

      dropInterval = 0.65 - difficultyProgress * 0.46;

      if (timer >= dropInterval) {
        timer = 0;

        if (!collides(0, 1)) {
          piece.y += 1;
        } else {
          lock();
        }
      }
    }, draw(){
      const pedrisGradient = ctx.createLinearGradient(0, 0, 720, 960);
      pedrisGradient.addColorStop(0, "#004d98");
      pedrisGradient.addColorStop(.48, "#0a2f75");
      pedrisGradient.addColorStop(.52, "#7f0035");
      pedrisGradient.addColorStop(1, "#a50044");
      ctx.fillStyle = pedrisGradient;
      ctx.fillRect(0, 0, 720, 960);
      const pedrisBackground = window.arcade76Assets?.pedrisBackground;
      if (pedrisBackground?.complete && pedrisBackground.naturalWidth) {
        ctx.save();
        ctx.globalAlpha = .47;
        ctx.drawImage(pedrisBackground, 0, 0, 720, 960);
        ctx.restore();
      }
      const pedrisShade = ctx.createLinearGradient(0, 0, 0, 960);
      pedrisShade.addColorStop(0, "rgba(0,0,0,.13)");
      pedrisShade.addColorStop(1, "rgba(3,5,18,.62)");
      ctx.fillStyle = pedrisShade;
      ctx.fillRect(0, 0, 720, 960);
      ctx.strokeStyle="#d7bcff42";for(let x=0;x<=cols;x++){ctx.beginPath();ctx.moveTo(ox+x*cell,oy);ctx.lineTo(ox+x*cell,oy+rows*cell);ctx.stroke()}for(let y=0;y<=rows;y++){ctx.beginPath();ctx.moveTo(ox,oy+y*cell);ctx.lineTo(ox+cols*cell,oy+y*cell);ctx.stroke()} const colors=['','#004d98','#005bb5','#1672c4','#a50044','#c51155','#7f0035'];board.forEach((row,y)=>row.forEach((v,x)=>{if(v){ctx.fillStyle=colors[v];ctx.fillRect(ox+x*cell+2,oy+y*cell+2,cell-4,cell-4)}}));piece.shape.forEach((row,y)=>row.forEach((v,x)=>{if(v){ctx.fillStyle=colors[piece.color];ctx.fillRect(ox+(piece.x+x)*cell+2,oy+(piece.y+y)*cell+2,cell-4,cell-4)}}));drawText(`PEDRIS  ${String(runtime.score).padStart(6,'0')}`,360,75,24,"#fff");},destroy(){}};
  }

  function runner(kind) {
    const hero={x:120,y:745,w:55,h:70,vy:0};const obstacles=[];let elapsed=0,ground=815;runtime.score=0;
    const jump=()=>{if(hero.y>=ground-hero.h-2)hero.vy=-650};listen(canvas,'pointerdown',jump);listen(document,'keydown',e=>{if(e.code==='Space'||e.code==='ArrowUp')jump()});
    return {update(dt){elapsed+=dt;hero.vy+=1500*dt;hero.y+=hero.vy*dt;if(hero.y>ground-hero.h){hero.y=ground-hero.h;hero.vy=0}if(Math.floor(elapsed*10)%17===0&&obstacles.length<5)obstacles.push({x:760,y:kind==='island'?755:765,w:45,h:60});obstacles.forEach(o=>o.x-=(260+elapsed*2)*dt);for(const o of obstacles)if(!o.hit&&rectHit(hero,o)){o.hit=true;finish(runtime.score)}for(let i=obstacles.length-1;i>=0;i--)if(obstacles[i].x<-60){obstacles.splice(i,1);runtime.score+=100}runtime.score+=dt*12},draw(){baseBackground(kind==='island'?"#56c9ef":"#2a1950",kind==='island'?"#1e7c5a":"#07050e");ctx.fillStyle=kind==='island'?"#e8cf75":"#2e3958";ctx.fillRect(0,ground,720,145);ctx.fillStyle=kind==='island'?"#ffb64e":"#6cf0ff";ctx.fillRect(hero.x,hero.y,hero.w,hero.h);ctx.fillStyle=kind==='island'?"#70492d":"#ff5664";obstacles.forEach(o=>ctx.fillRect(o.x,o.y,o.w,o.h));drawText(`${kind==='island'?'ISLAND HERO':'PLATFORM QUEST'}  ${String(Math.floor(runtime.score)).padStart(6,'0')}`,20,45,22,"#fff","left")},destroy(){}};
  }

  function metalCommand(){const player={x:80,y:750,w:55,h:75},bullets=[],enemies=[];let cooldown=0,elapsed=0;runtime.score=0;const aim=e=>{const p=pointer(e);player.y=Math.max(100,Math.min(820,p.y-player.h/2))};listen(canvas,'pointermove',aim);listen(canvas,'pointerdown',aim);return{update(dt){elapsed+=dt;cooldown-=dt;if(cooldown<=0){bullets.push({x:player.x+55,y:player.y+30,w:20,h:6});cooldown=.16}if(Math.floor(elapsed*10)%11===0&&enemies.length<8)enemies.push({x:760,y:120+Math.random()*700,w:60,h:65});bullets.forEach(b=>b.x+=650*dt);enemies.forEach(e=>e.x-=180*dt);for(const e of enemies){for(const b of bullets)if(!e.dead&&!b.dead&&rectHit(e,b)){e.dead=true;b.dead=true;runtime.score+=250;tone(180)}if(!e.dead&&rectHit(e,player))finish(runtime.score)}for(let i=bullets.length-1;i>=0;i--)if(bullets[i].dead||bullets[i].x>760)bullets.splice(i,1);for(let i=enemies.length-1;i>=0;i--)if(enemies[i].dead||enemies[i].x<-80)enemies.splice(i,1)},draw(){baseBackground("#4c3f32","#11120f");ctx.fillStyle="#59614f";ctx.fillRect(0,840,720,120);ctx.fillStyle="#72e5a8";ctx.fillRect(player.x,player.y,player.w,player.h);ctx.fillStyle="#ffe25c";bullets.forEach(b=>ctx.fillRect(b.x,b.y,b.w,b.h));ctx.fillStyle="#ff5c54";enemies.forEach(e=>ctx.fillRect(e.x,e.y,e.w,e.h));drawText(`METAL COMMAND  ${String(runtime.score).padStart(6,'0')}`,20,45,22,"#fff","left")},destroy(){}}}

  function pinball(){const ball={x:360,y:180,vx:145,vy:0,r:12};const bumpers=[{x:230,y:350,r:45},{x:490,y:350,r:45},{x:360,y:510,r:50}];let left=false,right=false,balls=3;runtime.score=0;const press=e=>{const p=pointer(e);if(p.x<360)left=true;else right=true};const release=()=>{left=false;right=false};listen(canvas,'pointerdown',press);listen(canvas,'pointerup',release);listen(document,'keydown',e=>{if(e.code==='ArrowLeft')left=true;if(e.code==='ArrowRight')right=true});listen(document,'keyup',e=>{if(e.code==='ArrowLeft')left=false;if(e.code==='ArrowRight')right=false});return{update(dt){ball.vy+=400*dt;ball.x+=ball.vx*dt;ball.y+=ball.vy*dt;if(ball.x<ball.r||ball.x>720-ball.r)ball.vx*=-1;if(ball.y<80){ball.y=80;ball.vy=Math.abs(ball.vy)}for(const b of bumpers){const dx=ball.x-b.x,dy=ball.y-b.y,d=Math.hypot(dx,dy);if(d<b.r+ball.r){const nx=dx/d||1,ny=dy/d||0;ball.x=b.x+nx*(b.r+ball.r);ball.y=b.y+ny*(b.r+ball.r);const speed=470;ball.vx=nx*speed;ball.vy=ny*speed;runtime.score+=500;tone(500)}}const hitFlipper=(active,x1,x2)=>{if(active&&ball.y>800&&ball.y<875&&ball.x>x1&&ball.x<x2){ball.vy=-560;ball.vx+=(ball.x-(x1+x2)/2)*4;runtime.score+=50}};hitFlipper(left,90,355);hitFlipper(right,365,630);if(ball.y>990){balls--;if(balls<1)finish(runtime.score);else Object.assign(ball,{x:360,y:180,vx:145,vy:0})}},draw(){baseBackground("#4a1c68","#080513");ctx.strokeStyle="#69efff";ctx.lineWidth=8;ctx.strokeRect(50,75,620,820);bumpers.forEach((b,i)=>{ctx.fillStyle=['#ff50ce','#65efff','#ffe45a'][i];ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,Math.PI*2);ctx.fill()});ctx.strokeStyle="#fff";ctx.lineWidth=18;ctx.beginPath();ctx.moveTo(100,840);ctx.lineTo(left?340:300, left?790:850);ctx.moveTo(620,840);ctx.lineTo(right?380:420,right?790:850);ctx.stroke();ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(ball.x,ball.y,ball.r,0,Math.PI*2);ctx.fill();drawText(`JACKPOT ${String(runtime.score).padStart(6,'0')}  BALL ${balls}`,360,48,22,"#fff")},destroy(){}}}

  const factories={"gamer-universe-76":pinball,"sky-patrol-76":skyPatrol,"block-breaker-76":blockBreaker,"platform-quest-76":()=>runner('platform'),"metal-command-76":metalCommand,"island-hero-76":()=>runner('island'),"neon-blocks-76":neonBlocks};

  const close=()=>{clearGame();pedrisControls.hidden=true;modal.hidden=true;document.body.style.overflow="";};
  const bootGame=async(button)=>{clearGame();runtime.slug=button.dataset.game;pedrisControls.hidden=runtime.slug!=="neon-blocks-76";runtime.credit=0;creditNode.textContent="0";modal.hidden=false;document.body.style.overflow="hidden";modal.querySelector("[data-modal-title]").textContent=names[runtime.slug];boot.hidden=false;coin.hidden=true;initials.hidden=true;boot.querySelector("[data-boot-message]").textContent="PRESENTS";ctx.clearRect(0,0,720,960);const data=await fetchJson(`/api/arcade/games/${runtime.slug}/session`,{method:"POST"});runtime.session=data.session_token;recordNode.textContent=`HI ${data.high_score.initials} ${String(data.high_score.score).padStart(6,"0")}`;setTimeout(()=>{if(modal.hidden)return;boot.hidden=true;coin.hidden=false;titleScreen.textContent=names[runtime.slug];titleScreen.nextElementSibling.textContent=subtitles[runtime.slug];},1800)};
  const start=()=>{runtime.credit=1;creditNode.textContent="1";coin.hidden=true;clearGame();runtime.running=true;runtime.paused=false;runtime.last=performance.now();runtime.game=factories[runtime.slug]();};
  const loop=now=>{const dt=Math.min(.033,(now-(runtime.last||now))/1000);runtime.last=now;if(runtime.running&&!runtime.paused)runtime.game?.update(dt);runtime.game?.draw();runtime.frame=requestAnimationFrame(loop)};runtime.frame=requestAnimationFrame(loop);
  room.querySelectorAll("[data-game]").forEach(button=>button.addEventListener("click",()=>bootGame(button)));
  modal.querySelector("[data-coin]").addEventListener("click",start);
  modal.querySelectorAll("[data-modal-close],[data-game-exit]").forEach(button=>button.addEventListener("click",close));
  modal.querySelector("[data-game-pause]").addEventListener("click",()=>runtime.paused=!runtime.paused);
  modal.querySelector("[data-game-sound]").addEventListener("click",event=>{runtime.sound=!runtime.sound;event.currentTarget.textContent=runtime.sound?"SOUND ON":"SOUND OFF"});
  modal.querySelector("[data-game-full]").addEventListener("click",()=>modal.querySelector(".arcade-modal-machine").requestFullscreen?.());

  const pedrisKeyByAction = {left: "ArrowLeft", right: "ArrowRight", rotate: "ArrowUp"};
  let pedrisHoldTimer = 0;
  let pedrisRepeatTimer = 0;
  const dispatchPedrisAction = (action) => {
    if (runtime.slug !== "neon-blocks-76" || !runtime.running || runtime.paused) return;
    const code = pedrisKeyByAction[action];
    if (code) document.dispatchEvent(new KeyboardEvent("keydown", {code, bubbles: true}));
  };
  const stopPedrisHold = () => {
    window.clearTimeout(pedrisHoldTimer);
    window.clearInterval(pedrisRepeatTimer);
    pedrisHoldTimer = 0;
    pedrisRepeatTimer = 0;
  };
  pedrisControls.querySelectorAll("[data-pedris-action]").forEach((button) => {
    button.addEventListener("pointerdown", (event) => {
      event.preventDefault();
      stopPedrisHold();
      const action = button.dataset.pedrisAction;
      dispatchPedrisAction(action);
      if (action === "rotate") return;
      pedrisHoldTimer = window.setTimeout(() => {
        pedrisRepeatTimer = window.setInterval(() => dispatchPedrisAction(action), 95);
      }, 260);
    });
    button.addEventListener("pointerup", stopPedrisHold);
    button.addEventListener("pointercancel", stopPedrisHold);
    button.addEventListener("pointerleave", stopPedrisHold);
  });

  const chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",letters=["A","A","A"];
  modal.querySelectorAll("[data-letter-up]").forEach(button=>button.addEventListener("click",()=>{const i=+button.dataset.letterUp;letters[i]=chars[(chars.indexOf(letters[i])+1)%chars.length];modal.querySelector(`[data-letter="${i}"]`).textContent=letters[i]}));
  modal.querySelectorAll("[data-letter-down]").forEach(button=>button.addEventListener("click",()=>{const i=+button.dataset.letterDown;letters[i]=chars[(chars.indexOf(letters[i])-1+chars.length)%chars.length];modal.querySelector(`[data-letter="${i}"]`).textContent=letters[i]}));
  modal.querySelector("[data-initials-confirm]").addEventListener("click",async()=>{await fetchJson(`/api/arcade/games/${runtime.slug}/high-score`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({initials:letters.join(""),claim_token:runtime.claim})});initials.hidden=true;coin.hidden=false;hallOfFame()});
  document.addEventListener("keydown",event=>{if(event.key==="Escape"&&!modal.hidden)close()});
  document.addEventListener("visibilitychange",()=>{if(document.hidden){stopPedrisHold();if(runtime.running)runtime.paused=true}});
  hallOfFame();
})();
