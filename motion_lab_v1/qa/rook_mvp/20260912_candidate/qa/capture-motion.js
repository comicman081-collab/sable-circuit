// Development evidence only. Capture live canvases at native pixels, never
// enlarge them. The recording is evidence for a human review, not an approval.
export async function captureMotion(name='aster_motion_native'){
  if(!/^[a-z0-9_-]+$/.test(name))throw Error('Invalid QA filename');
  const d=window.motionDebug,layers=['floor','character','effects'].map(id=>document.getElementById(id));
  if(!d||!window.__MOTION_BUILD__||d.controls.mouseDown)throw Error('Use packaged HTML with the physical mouse released');
  if(innerWidth<1920||innerHeight<1080)throw Error('Use a native 1080p viewport');
  const c=document.createElement('canvas');c.width=1920;c.height=1080;
  const ctx=c.getContext('2d'),held=new Set(),observations=[];
  const key=(code,down)=>{layers[2].dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,key:code,bubbles:true,cancelable:true}));down?held.add(code):held.delete(code);};
  const release=()=>{for(const code of [...held])key(code,false);};
  const reset=()=>{release();document.getElementById('reset').click();d.pause(false);d.setMode('combat');d.setAction('walk');document.getElementById('autoaim').checked=true;document.getElementById('autofire').checked=false;d.actor.x=-4;d.actor.y=2.5;d.world.camera.x=-4;d.world.camera.y=2.5;};
  const dirs=['E','SE','S','SW','W','NW','N','NE'],chords=[['KeyD'],['KeyD','KeyS'],['KeyS'],['KeyA','KeyS'],['KeyA'],['KeyA','KeyW'],['KeyW'],['KeyD','KeyW']];
  const segments=[];
  for(const run of [false,true])for(let i=0;i<8;i++)segments.push({direction:i,run,fire:i%2===1,ms:run?1400:1900});
  segments.push({direction:0,run:false,fire:true,stationary:true,ms:1700});
  // One uninterrupted lane sequence: preserve actor, phase and velocity across
  // adjacent/opposite turns, speed changes, release and fire transitions.
  segments.push(
    {direction:0,run:false,fire:false,ms:900,transition:'start'},
    {direction:7,run:false,fire:true,ms:650,transition:'adjacent turn + fire'},
    {direction:3,run:false,fire:true,ms:650,transition:'opposite turn'},
    {direction:0,run:true,fire:true,ms:650,transition:'speed up'},
    {direction:4,run:false,fire:false,ms:650,transition:'speed down + stop fire'},
    {direction:4,run:false,fire:true,stationary:true,ms:1300,transition:'stop + planted fire'},
    {direction:0,run:false,fire:false,ms:650,transition:'resume'}
  );
  const chunks=[],stream=c.captureStream(30),mime='video/webm;codecs=vp9';
  if(!MediaRecorder.isTypeSupported(mime))throw Error('Native VP9 MediaRecorder unavailable');
  const recorder=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:2300000});
  recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
  const stopped=new Promise((resolve,reject)=>{recorder.onstop=resolve;recorder.onerror=reject;});
  let active=true,label='',raf=0,captureStart=performance.now();
  const draw=()=>{
    if(!active)return;
    ctx.fillStyle='#0c171e';ctx.fillRect(0,0,c.width,c.height);
    const x=Math.round((c.width-layers[0].width)/2),y=Math.round((c.height-layers[0].height)/2);
    for(const layer of layers)ctx.drawImage(layer,x,y); // 1:1 source pixels, no resampling.
    ctx.fillStyle='#091117';ctx.fillRect(0,0,1920,65);ctx.fillStyle='#b7e0db';ctx.font='22px monospace';
    ctx.fillText(label+' | frame '+d.current?.frame+' | '+d.current?.action,24,30);
    ctx.font='14px monospace';ctx.fillText('Native live canvases / 1:1 pixels / build '+window.__MOTION_BUILD__.inputSHA256.slice(0,16),24,53);
    observations.push({elapsedMs:performance.now()-captureStart,time:d.actor.time,segment:label,...d.current});raf=requestAnimationFrame(draw);
  };
  try{
    reset();captureStart=performance.now();draw();recorder.start();
    for(const s of segments){
      release();
      if(!s.transition||s.transition==='start'){
        reset();d.actor.direction=s.direction;d.actor.aim=s.direction*Math.PI/4;
      }
      label=dirs[s.direction]+' '+(s.stationary?'stationary':s.run?'run':'walk')+(s.fire?' + fire':'')+(s.transition?' / '+s.transition:'');
      if(s.run)key('ShiftLeft',true);if(s.fire)key('Space',true);if(!s.stationary)for(const code of chords[s.direction])key(code,true);
      await new Promise(resolve=>setTimeout(resolve,s.ms));
      if(!s.transition){release();await new Promise(resolve=>setTimeout(resolve,260));}
    }
  }finally{active=false;cancelAnimationFrame(raf);recorder.stop();reset();}
  await stopped;for(const track of stream.getTracks())track.stop();
  const blob=new Blob(chunks,{type:mime});
  if(blob.size>=16000000)throw Error('Recording exceeds the bounded QA upload size');
  let response=await fetch('/__qa/'+name+'.webm',{method:'POST',body:blob});if(!response.ok)throw Error('Recording upload failed');
  const digest=async bytes=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');
  const report={kind:'motion-studio-native-capture',build:window.__MOTION_BUILD__,native:[1920,1080],canvasNative:layers.map(l=>[l.width,l.height]),pixelUpscaling:false,video:name+'.webm',videoSHA256:await digest(await blob.arrayBuffer()),captureScriptSHA256:await digest(await(await fetch('/qa/capture-motion.js',{cache:'no-store'})).arrayBuffer()),bytes:blob.size,segments,observations,visualApproval:false};
  response=await fetch('/__qa/'+name+'.json',{method:'POST',body:JSON.stringify(report)});if(!response.ok)throw Error('Recording metadata upload failed');
  return {video:report.video,bytes:blob.size,frames:observations.length,visualApproval:false};
}
