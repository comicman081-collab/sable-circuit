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
  return {schema:1,kind:'motion-studio-combat-browser',recordedAt:new Date().toISOString(),character:debug.profile.id,build:window.__MOTION_BUILD__,testScriptSHA256,externalResources,viewport:[innerWidth,innerHeight],input:'Real held mouse button; synthetic DOM movement/pointer events; actual fixed-step and WebGL renderer',results,pass:results.length===17&&results.every(r=>r.pass)};
}
