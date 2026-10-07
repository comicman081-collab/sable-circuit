// Dev-only. Tests the actual selected WebGL source and live fixed-step actor.
// Pixel diversity is NOT an anatomical/visual approval.
export async function runLocomotionChecks(){
  const d=window.motionDebug,el=document.getElementById('effects');
  if(!d||!window.__MOTION_BUILD__)throw Error('Use the current packaged Motion Studio');
  if(d.controls.mouseDown)throw Error('Release the physical mouse button before locomotion QA');
  const dirs=['E','SE','S','SW','W','NW','N','NE'];
  const chords=[['KeyD'],['KeyD','KeyS'],['KeyS'],['KeyA','KeyS'],['KeyA'],['KeyA','KeyW'],['KeyW'],['KeyD','KeyW']];
  const results=[],held=new Set(),cache=new Map();
  const key=(code,down)=>{el.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,key:code,bubbles:true,cancelable:true}));if(down)held.add(code);else held.delete(code);};
  const release=()=>{for(const code of [...held])key(code,false);};
  const hash=bytes=>crypto.subtle.digest('SHA-256',bytes).then(b=>[...new Uint8Array(b)].map(v=>v.toString(16).padStart(2,'0')).join(''));
  const framePixels=(dir,pose)=>{
    const r=d.renderer.hasFullBody(dir)?d.renderer.fullBodyFrame(dir,pose):d.renderer.frame(dir,pose);
    const clip=r.clip||{cell:r.cell,columns:1};
    const [cw,ch]=clip.cell,col=r.index%clip.columns,row=Math.floor(r.index/clip.columns);
    const id=dir+'/'+(r.action||(pose.amount<.06?'idle':pose.run?'run':'walk'))+'/'+r.index;
    if(!cache.has(id)){
      const c=document.createElement('canvas');c.width=cw;c.height=ch;
      const ctx=c.getContext('2d',{willReadFrequently:true});ctx.drawImage(r.im,col*cw,row*ch,cw,ch,0,0,cw,ch);
      const pixels=ctx.getImageData(0,Math.floor(ch*.55),cw,ch-Math.floor(ch*.55)).data;
      // Ignore irrelevant RGB beneath alpha zero; hashing encoded files is not motion evidence.
      for(let i=0;i<pixels.length;i+=4)if(pixels[i+3]===0)pixels[i]=pixels[i+1]=pixels[i+2]=0;
      cache.set(id,hash(pixels));
    }
    return {index:r.index,frameCount:r.frameCount||clip.frames,hash:cache.get(id)};
  };
  const reset=()=>{
    release();document.getElementById('reset').click();d.pause(false);d.setMode('combat');d.setAction('walk');
    document.getElementById('autoaim').checked=true;document.getElementById('autofire').checked=false;
    const time=document.getElementById('time-scale');time.value=100;time.dispatchEvent(new Event('input'));
    // Bounded, obstacle-free test lane. We do not replace update(), rendering or phase.
    d.actor.x=-4;d.actor.y=2.5;d.world.camera.x=-4;d.world.camera.y=2.5;
  };
  const observe=(dir,run,firing,stationary=false)=>new Promise((resolve,reject)=>{
    const start=performance.now(),samples=[],startDistance=d.actor.distance;
    let ready=false,baseDistance=0,baseShots=0;
    const sample=now=>{
      if(now-start>5000){reject(Error('Locomotion timeout: '+dir));return;}
      if(!ready&&now-start>250){ready=true;baseDistance=d.actor.distance;baseShots=d.actor.shots;}
      if(ready){
        const actor=d.actor,c=d.current,frame=framePixels(dir,actor.renderPose());
        samples.push({time:actor.time,phase:actor.phase,frame:frame.index,frameCount:frame.frameCount,hash:frame.hash,position:[actor.x,actor.y],amount:actor.amount,direction:c.spriteDirection,shots:actor.shots});
        const stride=run?d.profile.locomotion.runStride:d.profile.locomotion.walkStride;
        if(stationary?now-start>1050:actor.distance-baseDistance>stride*1.08){
          Promise.all(samples.map(async s=>({...s,hash:await s.hash}))).then(rows=>{
            const frames=[...new Set(rows.map(s=>s.frame))],hashes=[...new Set(rows.map(s=>s.hash))];
            const count=rows[0].frameCount,travel=actor.distance-baseDistance,shots=actor.shots-baseShots;
            const row={name:(stationary?'stationary_fire':(run?'run':'walk')+(firing?'_fire':''))+'_'+dir,direction:dir,run,firing,stationary,frameCount:count,frames,lowerPixelHashes:hashes,travel,shots,samples:rows};
            row.pass=rows.every(s=>s.direction===dir)&&Number.isFinite(count)&&
              (stationary?travel<.001&&hashes.length===1:frames.length===count&&count>=6&&hashes.length>=6&&travel>stride)&&
              (firing?shots>0:shots===0);
            resolve(row);
          },reject);return;
        }
      }
      requestAnimationFrame(sample);
    };
    requestAnimationFrame(sample);
  });
  try{
    for(const run of [false,true])for(const firing of [false,true])for(let i=0;i<8;i++){
      reset();if(run)key('ShiftLeft',true);if(firing)key('Space',true);
      for(const code of chords[i])key(code,true);
      results.push(await observe(dirs[i],run,firing));
    }
    for(let i=0;i<8;i++){
      reset();d.actor.direction=i;d.actor.aim=i*Math.PI/4;key('Space',true);
      results.push(await observe(dirs[i],false,true,true));
    }
  }finally{reset();}
  return {schema:1,kind:'motion-studio-locomotion-browser',character:d.profile.id,build:window.__MOTION_BUILD__,
    testScriptSHA256:await hash(await(await fetch('/qa/locomotion-checks.js',{cache:'no-store'})).arrayBuffer()),
    viewport:[innerWidth,innerHeight],input:'Synthetic DOM physical-code chords, real fixed-step actor and selected renderer textures; not physical keyboard/IME coverage',
    visualApproval:false,results,pass:results.length===40&&results.every(r=>r.pass)};
}
