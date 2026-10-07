// Development-only browser regression. Never bundled into a delivered HTML.
// Start a real held left mouse button on the canvas through the browser tool
// first; the test refuses to claim held-mouse coverage without it.
export async function runCombatChecks(){
  const debug=window.motionDebug,effects=document.getElementById('effects');
  if(!debug||debug.mode!=='combat'||!debug.controls.mouseDown)throw Error('Start held mouse fire on the combat canvas first');
  if(!window.__MOTION_BUILD__)throw Error('Open the current packaged HTML, not an unbound development page');
  if(!document.getElementById('autoaim').checked)throw Error('Enable movement facing before testing');
  const dirs=['E','SE','S','SW','W','NW','N','NE'];
  const chords=[['KeyD'],['KeyS','KeyD'],['KeyS'],['KeyS','KeyA'],['KeyA'],['KeyW','KeyA'],['KeyW'],['KeyW','KeyD']];
  const results=[],held=new Set();
  const key=(code,down,repeat=false)=>{
    effects.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,key:code,bubbles:true,cancelable:true,repeat}));
    if(down)held.add(code);else held.delete(code);
  };
  const release=()=>{for(const code of [...held])key(code,false);};
  const pointer=(angle,distance=.4)=>{
    const a=debug.actor,p=debug.project(a.x+Math.cos(angle)*distance,a.y+Math.sin(angle)*distance,debug.profile.weapon.height),r=effects.getBoundingClientRect();
    effects.dispatchEvent(new PointerEvent('pointermove',{pointerId:1,pointerType:'mouse',clientX:p[0]+r.left,clientY:p[1]+r.top,buttons:1,bubbles:true}));
  };
  const observe=(name,expected,updatePointer=null)=>new Promise((resolve,reject)=>{
    const started=performance.now(),shotStart=debug.actor.shots,eventStart=debug.actor.time,position=[debug.actor.x,debug.actor.y];
    const frames=new Set(),seenShots=new Set();let maxError=0,renderMatches=true,maxCursorError=0,convergedShots=0;
    function sample(now){
      if(!debug.controls.mouseDown){reject(Error('Held mouse fire was interrupted'));return;}
      const c=debug.current;frames.add(c.frame);renderMatches&&=c.spriteDirection===c.direction;
      for(const e of debug.events){
        if(e.time<=eventStart||seenShots.has(e.time))continue;
        seenShots.add(e.time);
        const angle=e.aim-dirs.indexOf(e.direction)*Math.PI/4;
        maxError=Math.max(maxError,Math.abs(Math.atan2(Math.sin(angle),Math.cos(angle)))*180/Math.PI);
        if(e.target&&e.converges){convergedShots++;maxCursorError=Math.max(maxCursorError,Math.abs((e.target[0]-e.origin[0])*Math.sin(e.aim)-(e.target[1]-e.origin[1])*Math.cos(e.aim)));}
      }
      if(now-started>=180&&debug.actor.shots>shotStart){
        const row={name,expected,direction:c.direction,spriteDirection:c.spriteDirection,shotCount:debug.actor.shots-shotStart,observedShots:seenShots.size,travel:Math.hypot(debug.actor.x-position[0],debug.actor.y-position[1]),frames:[...frames],maxFacingErrorDegrees:maxError,maxCursorError,convergedShots,heldMouse:debug.controls.mouseDown};
        const farAim=['mouse_E','mouse_S','mouse_W','mouse_N','repeat_preserves_mouse'].includes(name);
        row.pass=c.direction===expected&&c.spriteDirection===expected&&renderMatches&&maxError<=24.51&&row.travel>.01&&row.observedShots===row.shotCount&&(!farAim||(convergedShots>0&&maxCursorError<1e-5));
        resolve(row);return;
      }
      if(now-started>2400){reject(Error(name+': no shot within reload budget'));return;}
      if(updatePointer)updatePointer();
      requestAnimationFrame(sample);
    }
    if(updatePointer)updatePointer();requestAnimationFrame(sample);
  });
  try{
    key('KeyD',true);
    for(let i=0;i<8;i++)results.push(await observe('mouse_'+dirs[i],dirs[i],()=>pointer(i*Math.PI/4,i%2?.4:3)));
    release();
    for(let i=0;i<8;i++){
      pointer((i+4)%8*Math.PI/4,3);
      for(const code of chords[i])key(code,true);
      results.push(await observe('keyboard_'+dirs[i],dirs[i]));
      release();
    }
    key('KeyW',true);pointer(0,3);key('KeyW',true,true);
    results.push(await observe('repeat_preserves_mouse','E',()=>pointer(0,3)));
  }finally{release();}
  const rapidAim=await checkRapidAim(debug,effects);
  const scriptBytes=await fetch('/qa/combat-checks.js',{cache:'no-store'}).then(response=>{
    if(!response.ok)throw Error('Cannot fetch the browser test script');
    return response.arrayBuffer();
  });
  const digest=await crypto.subtle.digest('SHA-256',scriptBytes);
  const testScriptSHA256=[...new Uint8Array(digest)].map(value=>value.toString(16).padStart(2,'0')).join('');
  const externalResources=[...performance.getEntriesByType('resource')]
    .map(entry=>entry.name)
    .filter(name=>/^https?:/i.test(name)&&new URL(name,location.href).origin!==location.origin)
    .filter((name,index,all)=>all.indexOf(name)===index)
    .sort();
  return {schema:2,kind:'motion-studio-combat-browser',recordedAt:new Date().toISOString(),character:debug.profile.id,build:window.__MOTION_BUILD__,testScriptSHA256,externalResources,viewport:[innerWidth,innerHeight],input:'Real held mouse button; synthetic DOM movement/pointer events; actual fixed-step and WebGL renderer',results,rapidAim,pass:results.length===17&&results.every(r=>r.pass)&&rapidAim.every(r=>r.pass)};
}

// Eventual convergence is insufficient: probe in the input event's own turn,
// the first displayed frame, then the FIRST eligible projectile. Do not speed
// up the gun, refill ammo or retarget bullets to manufacture responsiveness.
async function checkRapidAim(d,effects){
  if(!d.aimSnapshot)throw Error('Runtime lacks immediate aim path');
  const frame=()=>new Promise(requestAnimationFrame),rows=[];
  const order=[0,4,2,6,1,5,3,7],dirs=['E','SE','S','SW','W','NW','N','NE'];
  const error=(m,t,a)=>Math.abs(Math.atan2(Math.sin(Math.atan2(t[1]-m[1],t[0]-m[0])-a),Math.cos(Math.atan2(t[1]-m[1],t[0]-m[0])-a)))*180/Math.PI;
  const move=down=>effects.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code:'KeyD',key:'d',bubbles:true,cancelable:true}));
  const locomotion=()=>JSON.stringify([d.actor.time,d.actor.phase,d.actor.distance,d.actor.x,d.actor.y,d.actor.ammo,d.actor.cooldown,d.actor.lastShot,d.actor.reload]);
  try{
    // Same bounded, obstacle-free lane as locomotion QA, while retaining the
    // real held trigger, cooldown, ammo, physics and renderer.
    d.actor.x=-4;d.actor.y=2.5;d.world.camera.x=-4;d.world.camera.y=2.5;
    const settle=performance.now();while(performance.now()-settle<400)await frame();
    for(const moving of [false,true]){
      if(moving)move(true);
      for(const dir of order){
        const initial=locomotion(),old=d.world.bullets.map(b=>[b,b.vx,b.vy]);
        const start=performance.now(),time=d.actor.time,shots=d.actor.shots,position=[d.actor.x,d.actor.y];
        const cooldown=Math.max(0,d.actor.cooldown),reload=d.actor.reload;
        const budget=(reload>0?Math.max(reload,cooldown):d.actor.ammo<=0?cooldown+d.profile.weapon.reloadSeconds:cooldown)+1/120;
        const r=effects.getBoundingClientRect();let screen;const inputSamples=[];
        // Several coalesced-style samples in one event-loop turn: last wins.
        for(const sample of [(dir+4)%8,(dir+2)%8,dir]){
          const a=sample*Math.PI/4;
          const actorPosition=[d.actor.x,d.actor.y],requestedTarget=[d.actor.x+4*Math.cos(a),d.actor.y+4*Math.sin(a)];
          screen=d.project(...requestedTarget,d.profile.weapon.height);
          effects.dispatchEvent(new PointerEvent('pointermove',{pointerId:1,pointerType:'mouse',clientX:r.left+screen[0],clientY:r.top+screen[1],buttons:1,bubbles:true}));
          inputSamples.push({sector:sample,actorPosition,requestedTarget,offsetMs:performance.now()-start,actorTime:d.actor.time,
            muzzle:[...d.aimSnapshot.muzzle],target:[...d.aimSnapshot.target],aim:d.aimSnapshot.aim});
        }
        const immediate=d.aimSnapshot;
        const inputError=error(immediate.muzzle,immediate.target,immediate.aim),immediateMs=performance.now()-start;
        const unchanged=locomotion()===initial;
        const afterInput=JSON.parse(locomotion());
        await frame();
        const c=d.current,visibleMuzzle=d.unproject(...c.muzzle,d.profile.weapon.height),visibleTarget=d.unproject(...screen,d.profile.weapon.height);
        const renderError=error(visibleMuzzle,visibleTarget,c.aim),firstFrameMs=performance.now()-start;
        let shot=d.events.find(e=>e.time>time);
        while(!shot&&performance.now()-start<2600){await frame();shot=d.events.find(e=>e.time>time);}
        const shotError=shot?.target?error(shot.origin,shot.target,shot.aim):999;
        const row={name:(moving?'moving':'stationary')+'_'+dirs[dir],heldMouse:d.controls.mouseDown,
          immediateErrorDegrees:inputError,immediateMs,firstFrameErrorDegrees:renderError,firstFrameMs,
          shotErrorDegrees:shotError,shotWaitSeconds:shot?shot.time-time:999,eligibleBudgetSeconds:budget,
          initialCooldownSeconds:cooldown,initialReloadSeconds:reload,initialAmmo:JSON.parse(initial)[5],
          inputSamples,locomotionBefore:JSON.parse(initial),locomotionAfterInput:afterInput,
          oldProjectileSamples:old.map(([b,x,y],index)=>({index,before:[x,y],after:[b.vx,b.vy]})),
          shotCount:d.actor.shots-shots,locomotionUnchanged:unchanged,
          travel:Math.hypot(d.actor.x-position[0],d.actor.y-position[1]),
          oldProjectileVelocityUnchanged:old.every(([b,x,y])=>b.vx===x&&b.vy===y)};
        row.pass=inputSamples.every(s=>Math.hypot(s.target[0]-s.requestedTarget[0],s.target[1]-s.requestedTarget[1])<1e-6)&&row.heldMouse&&inputError<1e-5&&renderError<1e-5&&shotError<1e-5&&immediateMs<=1000/120&&firstFrameMs<=50&&
          row.shotWaitSeconds<=budget+1/120+1e-8&&row.shotCount>=1&&unchanged&&row.oldProjectileVelocityUnchanged&&
          (moving?row.travel>.01:row.travel<.01);
        rows.push(row);
      }
      if(moving)move(false);
    }
  }finally{move(false);}
  return rows;
}
