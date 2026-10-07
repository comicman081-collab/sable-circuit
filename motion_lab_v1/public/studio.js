import {Actor,DIRECTIONS,STEP,TAU,clamp,direction,segmentCircle,segmentBox} from './simulation.js';
import {AtlasRenderer,phaseForFrame,phaseIndex} from './atlas-renderer.js';
import {CombatKeyboard} from './keyboard-input.js';
import {applyPointerAim,createPlayerProjectile} from './combat-aim.js';

const $=s=>document.querySelector(s);
const floor=$('#floor'),canvas=$('#character'),effects=$('#effects');
const ground=floor.getContext('2d'),fx=effects.getContext('2d');
const characterId=new URLSearchParams(location.search).get('character')||'mica';
if(!/^[a-z0-9_-]+$/.test(characterId))throw Error('Invalid character id');
const profile=window.__MOTION_PROFILE__||await(await fetch('assets/atlas/'+characterId+'/profile.json')).json();
let fireBundle=window.__MOTION_FIRE_BUNDLE__||null;
if(!fireBundle&&profile.id==='aster'&&profile.animation?.presentation!=='authored_frames'){
  // The coherent family is the only live ASTER route.  The former split
  // upper/lower bundle remains quarantined and is never used as a fallback.
  let response=await fetch('assets/atlas/'+profile.id+'/coherent/manifest.json');
  if(!response.ok)response=await fetch('assets/atlas/'+profile.id+'/fire/manifest.json');
  if(response.ok)fireBundle=await response.json();
}
$('#operator-name').textContent=profile.name;$('#hero-name').textContent=profile.name;
effects.setAttribute('aria-label',profile.name+' 이동 및 사격 전투 화면');
$('.portrait').style.backgroundImage=`url("${window.__MOTION_PORTRAIT__||'assets/atlas/'+profile.id+'/portrait.png'}")`;
const renderer=new AtlasRenderer(canvas);
try{await renderer.load(profile,fireBundle);$('#loading').remove();}catch(error){$('#loading').textContent='이미지 로딩 실패: '+error.message;throw error;}
let actor=new Actor(profile),mode='combat',action='walk',held=null,fireHeld=false,mouseDown=false;
let width=0,height=0,size=270,scaleTime=1,pointer=null,last=0,accumulator=0,elapsed=0;
let galleryPhase=0,selected='E',paused=false,frameOverride=null,combat=false;
let camera={x:0,y:0},fps=60,frameCounter=0,frameTime=0;
const keyboard=new CombatKeyboard(),keys=keyboard.codes,bullets=[],particles=[],targets=[],events=[];
const blocks=[{x:-1.9,y:-1.0,w:1.2,h:.5,z:.88},{x:1.6,y:1.6,w:1.1,h:.5,z:.88}];
const ppm=()=>size/profile.heightMetres;
const project=(x,y,z=0)=>[width*.5+(x-camera.x)*ppm(),height*.66+(y-camera.y)*ppm()*.5-z*ppm()];
const unproject=(x,y,z=0)=>[(x-width*.5)/ppm()+camera.x,((y-height*.66)/ppm()+z)/.5+camera.y];
function reviewClip(name=selected){
  const view=profile.views[name]||{};
  return view[action==='run'&&view.run?'run':action==='idle'?'idle':'walk']||view.walk;
}
function reviewPhase(name=selected,frame=frameOverride){
  if(frame===null)return galleryPhase;
  const clip=reviewClip(name);
  return phaseForFrame(frame,clip?.frames||1,clip?.phaseStarts);
}
function reviewFrame(name=selected,phase=galleryPhase){
  const clip=reviewClip(name);
  return phaseIndex(phase,clip?.frames||1,clip?.phaseStarts);
}

function resetTargets(){
  targets.length=0;
  for(const [i,[x,y]]of [[-2.8,-2.4],[0,-3.3],[2.9,-2.3],[-3,2.5],[2.8,2.6]].entries())
    targets.push({x,y,hp:100,hit:0,dead:0,cooldown:1.5+i*.43});
}
resetTargets();
function reset(){actor=new Actor(profile);camera={x:0,y:0};held=null;pointer=null;fireHeld=mouseDown=false;combat=false;paused=false;frameOverride=null;keys.clear();events.length=bullets.length=particles.length=0;resetTargets();$('#combat-toggle').textContent='교전 시작';$('#pause').textContent='일시정지';}
function resize(){
  const r=$('#surface').getBoundingClientRect();width=r.width;height=r.height;
  const dpr=Math.min(devicePixelRatio||1,2);
  for(const c of [floor,canvas,effects]){c.width=Math.round(width*dpr);c.height=Math.round(height*dpr);}
  ground.setTransform(dpr,0,0,dpr,0,0);fx.setTransform(dpr,0,0,dpr,0,0);
}
new ResizeObserver(resize).observe($('#surface'));
function line(ctx,a,b,color,lineWidth=1){ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.strokeStyle=color;ctx.lineWidth=lineWidth;ctx.stroke();}
function label(ctx,value,x,y,fontSize=11,color='#8ab0ae',align='left'){
  ctx.font=fontSize+'px Raj, sans-serif';ctx.fillStyle=color;ctx.textAlign=align;ctx.fillText(value,x,y);
}
function rect(ctx,x,y,w,h,fill,stroke=null,r=3){ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fillStyle=fill;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.stroke();}}
function ellipse(ctx,x,y,rx,ry,fill,stroke=null){ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,TAU);if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.stroke();}}
function shadow(x,y,r=30){
  ground.save();ground.translate(x,y);ground.scale(1,.38);const g=ground.createRadialGradient(0,0,0,0,0,r);g.addColorStop(0,'#0000006b');g.addColorStop(1,'#00000000');ground.fillStyle=g;ground.beginPath();ground.arc(0,0,r,0,TAU);ground.fill();ground.restore();
}

function drawFloor(){
  const f=ground;f.clearRect(0,0,width,height);
  const gradient=f.createRadialGradient(width*.5,height*.5,30,width*.5,height*.5,width*.75);
  gradient.addColorStop(0,'#26393e');gradient.addColorStop(1,'#09171e');f.fillStyle=gradient;f.fillRect(0,0,width,height);
  const [left,top]=unproject(0,0),[right,bottom]=unproject(width,height);
  for(let y=Math.floor(top)-1;y<=Math.ceil(bottom)+1;y++)for(let x=Math.floor(left)-1;x<=Math.ceil(right)+1;x++){
    const a=project(x,y),b=project(x+1,y+1);
    rect(f,a[0]+2,a[1]+2,b[0]-a[0]-4,b[1]-a[1]-4,(x+y)%2?'#1e3036':'#1a2b32','#7690910c',2);
    line(f,[a[0]+6,b[1]-6],[b[0]-6,b[1]-6],'#040d1270',1);
  }
  const centre=project(0,0);for(let i=0;i<3;i++)ellipse(f,...centre,(1.2+i*.9)*ppm(),(.6+i*.45)*ppm(),null,'#6ac9b910');
  const a=project(-8,-6),b=project(8,6);f.strokeStyle='#6da79f55';f.strokeRect(a[0],a[1],b[0]-a[0],b[1]-a[1]);
  for(const y of [-5.7,5.7]){const a=project(-7.7,y),b=project(7.7,y);line(f,a,b,'#5ab1a744',2);for(let x=-7.6;x<8;x+=1.7){const p=project(x,y);f.shadowBlur=10;f.shadowColor='#6fffd850';f.fillStyle='#86e3cd';f.fillRect(p[0],p[1],ppm()*.32,2);f.shadowBlur=0;}}
  for(const b of blocks){const p=project(b.x+b.w*.5,b.y+b.h);shadow(...p,ppm()*.7);}
  for(const t of targets){const p=project(t.x,t.y);shadow(...p,ppm()*.25);}
  const p=project(actor.x,actor.y);shadow(...p,ppm()*.31);
  label(f,'S A B L E  /  FIELD 07',centre[0],centre[1]+ppm()*2.25,15,'#91b8ab22','center');
}
function drawBlock(ctx,b){
  const p=project(b.x,b.y),q=project(b.x+b.w,b.y+b.h),lift=b.z*ppm();
  rect(ctx,p[0],p[1]-lift,q[0]-p[0],q[1]-p[1],'#304a52','#5b787c',2);
  rect(ctx,p[0],q[1]-lift,q[0]-p[0],lift,'#213740','#3a5960',1);
  line(ctx,[p[0]+7,p[1]-lift],[q[0]-7,p[1]-lift],'#99d9cc',2);
  line(ctx,[p[0]+7,q[1]-lift+7],[q[0]-7,q[1]-lift+7],'#486b70',1);
  for(let x=p[0]+8;x<q[0]-9;x+=11)line(ctx,[x,q[1]-16],[x+5,q[1]-22],'#b2a87855',2);
}
function drawTarget(ctx,t){
  const p=project(t.x,t.y),head=project(t.x,t.y,profile.weapon.height),r=ppm()*.14;
  ellipse(ctx,...p,r*1.8,r*.75,'#0d1d26','#557d80');
  if(t.dead>0){label(ctx,t.dead.toFixed(1),p[0],p[1]-10,11,'#577a78','center');return;}
  rect(ctx,p[0]-r*.33,head[1],r*.66,p[1]-head[1]-4,'#294b56');
  const warm=t.hit>0?'#fff0b5':combat?'#e0a277':'#9db29b';
  rect(ctx,head[0]-r,head[1]-r,r*2,r*2,warm,null,4);
  rect(ctx,head[0]-r+3,head[1]-r+3,r*2-6,r*2-6,'#152831',null,2);
  ellipse(ctx,...head,r*.58,r*.58,null,warm);ellipse(ctx,...head,r*.15,r*.15,warm);
  rect(ctx,p[0]-r,head[1]-r-12,r*2,3,'#11252b');rect(ctx,p[0]-r,head[1]-r-12,r*2*Math.max(0,t.hp/100),3,'#8bceb6');
}
function worldObjects(front){
  const objects=[...blocks.map(b=>({y:b.y+b.h,draw:c=>drawBlock(c,b)})),...targets.map(t=>({y:t.y,draw:c=>drawTarget(c,t)}))];
  objects.sort((a,b)=>a.y-b.y);
  for(const o of objects)if((o.y>actor.y+.05)===front)o.draw(front?fx:ground);
}
function addParticles(x,y,z,color,count=12){
  for(let i=0;i<count;i++){const a=Math.random()*TAU,s=.25+Math.random()*1.3;particles.push({x,y,z,vx:Math.cos(a)*s,vy:Math.sin(a)*s,vz:Math.random()*1.5,life:.22+Math.random()*.23,color});}
}
function muzzleWorld(facingDirection=actor.direction){
  const name=DIRECTIONS[facingDirection],p=actor.renderPose(facingDirection),root=project(actor.x,actor.y);
  if(renderer.hasFullBody(name)){
    const full=renderer.fullBodyFrame(name,p),m=renderer.projectFullBodyPoint(name,p,full.muzzle,...root,size);
    if(m)return [...unproject(...m,profile.weapon.height),profile.weapon.height];
  }
  const record=renderer.frame(name,p);
  if(p.firing&&renderer.hasFire(name)){
    const fire=renderer.fireFrame(name,p),root=project(actor.x,actor.y),m=renderer.projectFirePoint(name,p,fire.muzzle,...root,size);
    if(m)return [...unproject(...m,profile.weapon.height),profile.weapon.height];
  }
  if(!record)return [actor.x,actor.y,profile.weapon.height];
  const local=record.model.view.muzzle||record.clip.muzzles[record.index];
  const m=renderer.projectPoint(record.clip,p,local,...root,size);
  return [...unproject(...m,profile.weapon.height),profile.weapon.height];
}
function fire(target=null,converges=false){
  const [x,y,z]=muzzleWorld(),aim=actor.aim;
  bullets.push(createPlayerProjectile(actor,[x,y,z]));
  addParticles(x,y,z,'#c8ffdf',4);events.push({time:actor.time,direction:DIRECTIONS[actor.direction],origin:[x,y,z],aim,target,converges});
  if(events.length>512)events.shift();
}
function syncPointerAim(){
  if(!pointer)return null;
  const target=unproject(...pointer,profile.weapon.height);
  return {...applyPointerAim(actor,target,muzzleWorld),target};
}
function stepWorld(dt){
  const input=keyboard.read();let {x,y}=input;
  if(held!==null){x=Math.cos(held*Math.PI/4);y=Math.sin(held*Math.PI/4);}
  if(action==='idle'&&!keys.size){x=0;y=0;}
  let aim=null;
  if(pointer)aim=actor.aim;
  else if(!$('#autoaim').checked)aim=actor.aim;
  const fired=actor.update(dt,{x,y,run:input.run||action==='run',aim,fire:input.fire||mouseDown||fireHeld||$('#autofire').checked,reload:input.reload},blocks);
  camera.x+=(actor.x-camera.x)*(1-Math.exp(-dt*7));camera.y+=(actor.y-camera.y)*(1-Math.exp(-dt*7));
  // Aim in the camera/frame that will actually be presented, before emission.
  const solution=syncPointerAim();
  if(fired)fire(solution?.target||null,!!solution?.converges);
  for(const t of targets){
    t.hit=Math.max(0,t.hit-dt);
    if(t.dead>0){t.dead=Math.max(0,t.dead-dt);if(!t.dead)t.hp=100;continue;}
    t.cooldown-=dt;
    if(combat&&t.cooldown<=0&&Math.hypot(t.x-actor.x,t.y-actor.y)<6){
      t.cooldown=1.8;const angle=Math.atan2(actor.y-t.y,actor.x-t.x);
      bullets.push({x:t.x,y:t.y,z:profile.weapon.height,vx:Math.cos(angle)*3.3,vy:Math.sin(angle)*3.3,life:3,enemy:true});
    }
  }
  for(const b of bullets){
    const old=[b.x,b.y];b.x+=b.vx*dt;b.y+=b.vy*dt;b.life-=dt;
    if(blocks.some(o=>b.z<=o.z&&segmentBox(old,[b.x,b.y],o))){b.life=-1;addParticles(b.x,b.y,b.z,'#81cdd4',3);continue;}
    if(b.enemy){
      if(segmentCircle(old,[b.x,b.y],[actor.x,actor.y],.19)){actor.hp=Math.max(0,actor.hp-5);b.life=-1;addParticles(b.x,b.y,b.z,'#ffbc96',5);if(actor.hp===0){combat=false;$('#combat-toggle').textContent='다시 교전';}}
    }else{
      for(const t of targets)if(t.dead===0&&segmentCircle(old,[b.x,b.y],[t.x,t.y],.19)){
        t.hp-=profile.weapon.damage;t.hit=.14;b.life=-1;addParticles(t.x,t.y,b.z,'#ffe0a1',12);
        if(t.hp<=0){t.dead=4;actor.kills++;addParticles(t.x,t.y,b.z,'#f2c995',22);}break;
      }
    }
  }
  for(let i=bullets.length-1;i>=0;i--)if(bullets[i].life<=0)bullets.splice(i,1);
  for(const p of particles){p.x+=p.vx*dt;p.y+=p.vy*dt;p.z+=p.vz*dt;p.vz-=3.2*dt;p.life-=dt;}
  for(let i=particles.length-1;i>=0;i--)if(particles[i].life<=0||particles[i].z<0)particles.splice(i,1);
}
function drawEffects(){
  for(const b of bullets){const p=project(b.x,b.y,b.z),tail=project(b.x-b.vx*.02,b.y-b.vy*.02,b.z);line(fx,tail,p,b.enemy?'#ee876355':'#90ffe64d',5);line(fx,tail,p,b.enemy?'#ffc8a2':'#d9fff4',1.8);}
  for(const p of particles){fx.globalAlpha=clamp(p.life/.25,0,1);const a=project(p.x,p.y,p.z),b=project(p.x-p.vx*.035,p.y-p.vy*.035,p.z-p.vz*.035);line(fx,a,b,p.color,1.4);}fx.globalAlpha=1;
}
function hud(q){
  const p=project(actor.x,actor.y);ellipse(fx,p[0],p[1]+3,ppm()*.2,ppm()*.09,null,'#80d7bc66');
  if(q&&actor.recoil>.4){fx.shadowColor='#9affcd';fx.shadowBlur=25;ellipse(fx,...q.muzzle,actor.recoil*6,actor.recoil*4,'#f5ffe8');fx.shadowBlur=0;}
  if(pointer){for(const s of [-1,1]){line(fx,[pointer[0]+s*5,pointer[1]],[pointer[0]+s*10,pointer[1]],'#c3f8da');line(fx,[pointer[0],pointer[1]+s*5],[pointer[0],pointer[1]+s*10],'#c3f8da');}ellipse(fx,...pointer,2,2,'#c3f8da');}
  if(actor.reload){fx.strokeStyle='#b0ecce';fx.lineWidth=2;fx.beginPath();fx.arc(p[0],p[1]-size-19,9,-Math.PI/2,-Math.PI/2+TAU*(1-actor.reload/profile.weapon.reloadSeconds));fx.stroke();}
  label(fx,'MOVE / AIM',width-145,35,10,'#6f9797');label(fx,(actor.amount<.05?'—':DIRECTIONS[direction(actor.moveAngle)])+' / '+DIRECTIONS[actor.direction],width-145,62,23,'#bcead8');
  label(fx,Math.hypot(actor.vx,actor.vy).toFixed(2)+' M/S · '+actor.shots+' SHOTS',width-145,80,10,'#7da7a1');
}

function gallery(){
  ground.fillStyle='#0e1b23';ground.fillRect(0,0,width,height);
  const fireActive=$('#autofire').checked||fireHeld||keyboard.read().fire;
  const top=138,cw=(width-56)/4,ch=(height-top-26)/2;
  for(let i=0;i<8;i++){
    const x=28+(i%4)*cw,y=top+Math.floor(i/4)*ch,name=DIRECTIONS[i];
    rect(ground,x+4,y,cw-8,ch-10,name===selected?'#1c343a':'#152730',name===selected?'#52766c':'#2a4148',4);
    label(ground,name,x+18,y+25,18,'#a5e2cd');label(ground,'0'+(i+1),x+cw-22,y+25,10,'#647e85','right');
    const rootY=y+ch-28;line(ground,[x+18,rootY],[x+cw-18,rootY],'#456861');shadow(x+cw*.5,rootY,cw*.23);
    if(!renderer.models[name]){label(fx,'원화 제작 중',x+cw*.5,y+ch*.5,14,'#788f94','center');continue;}
    const p={phase:reviewPhase(name),amount:action==='idle'?0:1,run:action==='run',firing:fireActive,recoil:fireActive?(1+(elapsed%.11)*27)*Math.exp(-(elapsed%.11)*27):0,reload:0,time:elapsed,facing:i*Math.PI/4};
    const q=renderer.draw(name,p,x+cw*.47,rootY,Math.min(size*1.12,ch-62,cw*1.13));
    if(q&&p.recoil>.55&&fireActive)ellipse(fx,...q.muzzle,3.5,2.5,'#eeffe6');
    label(fx,'FRAME '+String(q.frame+1).padStart(2,'0')+' / '+String(q.frameCount).padStart(2,'0'),x+18,rootY+17,10,'#729f96');
  }
}
function inspectFrame(){
  ground.fillStyle='#11202a';ground.fillRect(0,0,width,height);
  const model=renderer.models[selected];if(!model)return;
  const sz=Math.min(height-200,680),p={phase:reviewPhase(selected),amount:action==='idle'?0:1,run:action==='run',recoil:0,reload:0,time:0,facing:DIRECTIONS.indexOf(selected)*Math.PI/4};
  const origin=[width*.46,height-46];const q=renderer.draw(selected,p,...origin,sz);
  if(!q)return;
  const clip=q.clip;
  ellipse(fx,...q.muzzle,6,6,null,'#ffce86');line(fx,[q.muzzle[0]+8,q.muzzle[1]],[q.muzzle[0]+65,q.muzzle[1]],'#ffce86');label(fx,'MUZZLE',q.muzzle[0]+70,q.muzzle[1]+4,12,'#ffce86');
  const i=q.frame,source=clip.sources?.[i];
  label(fx,selected+' / FRAME '+(i+1)+' / '+(source?.native?('AUTHORED '+source.native.join(' × ')+' PX'):'FULL-BODY RUNTIME '+clip.cell.join(' × ')+' PX'),32,height-21,12,'#92c7b8');
  window.motionDebug.inspector={origin,scale:sz/clip.height,clip,index:i};
}
function updateHud(){
  $('#ammo').innerHTML=String(actor.ammo).padStart(2,'0')+' <small>/ '+profile.weapon.magazine+'</small>';
  $('#kills').textContent=String(actor.kills).padStart(2,'0');$('#health').textContent=actor.hp+'%';
  $('#direction-label').textContent=(actor.amount>.05?DIRECTIONS[direction(actor.moveAngle)]:'—')+' → '+DIRECTIONS[actor.direction];
  $('#state-label').textContent=actor.reload?'RELOADING':actor.amount<.05?'READY':actor.run?'RUNNING':'MOVING';
  $('#perf').textContent=fps.toFixed(0)+' FPS / '+canvas.width+' × '+canvas.height;
}
function tick(now){
  const raw=last?Math.min((now-last)/1000,.12):1/60;last=now;frameCounter++;frameTime+=raw;
  if(frameTime>.5){fps=frameCounter/frameTime;frameCounter=0;frameTime=0;}
  const dt=paused?0:raw*scaleTime;elapsed+=dt;
  if(mode==='combat'){
    accumulator=Math.min(accumulator+dt,.25);while(accumulator+1e-12>=STEP){stepWorld(STEP);accumulator-=STEP;}
  }else if(action!=='idle')galleryPhase=(galleryPhase+dt*(action==='run'?1.55:.84))%1;
  fx.clearRect(0,0,width,height);renderer.begin(width,height);
  if(mode==='combat'){
    // A high-refresh render may have no fixed step. Never display stale aim.
    syncPointerAim();
    drawFloor();worldObjects(false);const p=actor.renderPose(),position=project(actor.x,actor.y);
    const q=renderer.draw(DIRECTIONS[actor.direction],p,...position,size);worldObjects(true);drawEffects();hud(q);
    if($('#skeleton').checked){line(fx,[position[0]-45,position[1]],[position[0]+45,position[1]],'#e8bf81');label(fx,'ROOT',position[0]+49,position[1]+4,10,'#e8bf81');}
    window.motionDebug.current={direction:DIRECTIONS[actor.direction],spriteDirection:q?.direction,aim:actor.aim,frame:q?.frame,frameCount:q?.frameCount,action:q?.action||(actor.amount<.06?'idle':actor.run?'run':'walk'),run:actor.run,amount:actor.amount,lowerFrame:q?.lowerFrame,firePose:q?.fire===true,phase:actor.phase,position:[actor.x,actor.y],shots:actor.shots,ammo:actor.ammo,muzzle:q?.muzzle,health:actor.hp};
  }else if(mode==='directions')gallery();else inspectFrame();
  updateHud();requestAnimationFrame(tick);
}

function setMode(next){
  mode=next;pointer=null;held=null;mouseDown=fireHeld=false;accumulator=0;keys.clear();frameOverride=null;paused=false;$('#pause').textContent='일시정지';
  document.querySelectorAll('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===mode));
  $('#rig-help').hidden=mode!=='rig';
  $('#scene-caption').textContent={combat:'이동 · 독립 조준 · 실시간 사격',directions:'8개의 시점에서 같은 보행 위상 비교',rig:'원본 해상도와 프레임 · 총구 위치 확인'}[mode];
}
function setAction(next){action=next;frameOverride=null;if(next==='idle')held=null;document.querySelectorAll('[data-action]').forEach(b=>b.classList.toggle('active',b.dataset.action===next));}
function setDirection(name){selected=name;const i=DIRECTIONS.indexOf(name);actor.direction=i;actor.aim=i*Math.PI/4;pointer=null;if(mode==='combat'){held=i;if(action==='idle')setAction('walk');}document.querySelectorAll('[data-dir]').forEach(b=>b.classList.toggle('active',b.dataset.dir===name));}
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>setMode(b.dataset.mode));
document.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>setAction(b.dataset.action));
document.querySelectorAll('[data-dir]').forEach(b=>b.onclick=()=>setDirection(b.dataset.dir));
$('#stop-move').onclick=()=>{held=null;keys.clear();};$('#reset').onclick=reset;
$('#scale').oninput=e=>{size=+e.target.value;$('#scale-value').textContent=size+' px';};
$('#time-scale').oninput=e=>{scaleTime=+e.target.value/100;$('#time-value').textContent=scaleTime.toFixed(2)+'×';};
$('#fire').onpointerdown=e=>{fireHeld=true;actor.queueShot();e.currentTarget.setPointerCapture(e.pointerId);};
$('#fire').onpointerup=()=>fireHeld=false;$('#fire').onpointercancel=()=>fireHeld=false;
$('#reload').onclick=()=>actor.requestReload();
$('#combat-toggle').onclick=()=>{if(actor.hp===0)reset();combat=!combat;$('#combat-toggle').textContent=combat?'교전 중지':'교전 시작';};
$('#pause').onclick=()=>{paused=!paused;if(!paused&&frameOverride!==null){galleryPhase=reviewPhase(selected,frameOverride);frameOverride=null;}$('#pause').textContent=paused?'재생':'일시정지';};
$('#frame-step').onclick=()=>{if(mode==='combat')setMode('directions');paused=true;const count=reviewClip(selected)?.frames||1;frameOverride=((frameOverride??reviewFrame(selected))+1)%count;$('#pause').textContent='재생';};
$('#edit-muzzle').onchange=e=>{if(e.target.checked){paused=true;frameOverride=reviewFrame(selected);$('#pause').textContent='재생';}};
addEventListener('keydown',e=>{
  const result=keyboard.keyDown(e,{followMovement:$('#autoaim').checked});
  if(!result.handled)return;
  e.preventDefault();
  if(result.movement){held=null;effects.focus({preventScroll:true});}
  // The latest directional input wins, including while mouse fire is held.
  // Repeated keys do not steal aim; an actual pointer move takes it back.
  if(result.takeFacing)pointer=null;
  if(result.reloadPressed)actor.requestReload();
  if(result.firePressed)actor.queueShot();
},{capture:true});
addEventListener('keyup',e=>keyboard.keyUp(e),{capture:true});
addEventListener('blur',()=>{keys.clear();held=null;fireHeld=mouseDown=false;pointer=null;});
const localPoint=e=>{const r=effects.getBoundingClientRect();return[e.clientX-r.left,e.clientY-r.top];};
effects.onpointermove=e=>{if(mode==='combat'){pointer=localPoint(e);syncPointerAim();}};
effects.onpointerdown=e=>{
  if(e.button!==0)return;effects.focus();effects.setPointerCapture(e.pointerId);
  if(mode==='combat'){pointer=localPoint(e);syncPointerAim();mouseDown=true;actor.queueShot();}
  if(mode==='rig'&&$('#edit-muzzle').checked){const info=window.motionDebug.inspector,p=localPoint(e);info.clip.muzzles[info.index]=[(p[0]-info.origin[0])/info.scale+info.clip.root[0],(p[1]-info.origin[1])/info.scale+info.clip.root[1]];}
};
effects.onpointerup=()=>mouseDown=false;effects.onpointercancel=()=>mouseDown=false;
effects.onpointerleave=()=>{if(!mouseDown)pointer=null;};
$('#export').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(profile,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=profile.id+'.motion-profile.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
window.motionDebug={profile,renderer,events,keys,keyboard,get actor(){return actor},get mode(){return mode},get controls(){return {mouseDown,fireHeld,aimSource:pointer?'pointer':$('#autoaim').checked?'movement':'locked'}},get aimSnapshot(){return {aim:actor.aim,muzzle:muzzleWorld(),target:pointer?unproject(...pointer,profile.weapon.height):null}},get world(){return{targets,blocks,bullets,camera}},setMode,setAction,setDirection,
  pause:value=>{paused=value;},setFrame:value=>{frameOverride=value;paused=true;},project,unproject};
requestAnimationFrame(tick);
