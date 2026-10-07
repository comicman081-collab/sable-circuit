// Owned source-cycle review surface. Native unwarped atlas cells, 1x only.
// A playback trace documents presentation, never an anatomical approval.
const preview=await fetch('./cycle-preview.json',{cache:'no-store'}).then(r=>r.json());
const canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d',{alpha:false});
const label=document.querySelector('#status'),button=document.querySelector('button');
const image=new Image();image.src='./public/'+preview.clip.image;await image.decode();
const recipe=preview.cycleInputs.recipeValues,clip=preview.clip;
const speed=recipe.speed,stride=recipe.stride,height=recipe.heightMetres;
const direction=['E','SE','S','SW','W','NW','N','NE'].indexOf(preview.cycleInputs.direction)*Math.PI/4;
const frameAt=phase=>{for(let i=5;i>=0;i--)if(phase>=clip.phaseStarts[i])return i;return 0;};
function draw(t){
  const phase=(t*speed/stride)%1,index=frameAt(phase),[cw,ch]=clip.cell;
  ctx.fillStyle='#101e27';ctx.fillRect(0,0,1920,1080);
  ctx.fillStyle='#e4ece9';ctx.font='20px sans-serif';
  ctx.fillText(`${preview.cycleInputs.character} · ${preview.cycleInputs.direction} · 1x · ${t.toFixed(3)}s · frame ${index}`,28,34);
  ctx.fillText('SOURCE-CYCLE OBSERVATION — not game-runtime / art approval',28,68);
  ctx.drawImage(image,index%3*cw,Math.floor(index/3)*ch,cw,ch,30,170,cw,ch);
  ctx.strokeStyle='#72897e';ctx.beginPath();ctx.moveTo(30,170+clip.root[1]);ctx.lineTo(798,170+clip.root[1]);ctx.stroke();
  const ratio=270/clip.height,dx=t*speed*270/height*Math.cos(direction),dy=t*speed*270/height*.5*Math.sin(direction);
  ctx.strokeStyle='#2b4349';ctx.beginPath();
  for(let x=880;x<1920;x+=80){const xx=880+((x-880-dx)%1040+1040)%1040;ctx.moveTo(xx,190);ctx.lineTo(xx,1000);}
  for(let y=190;y<1000;y+=60){const yy=190+((y-190-dy)%810+810)%810;ctx.moveTo(880,yy);ctx.lineTo(1910,yy);}
  ctx.stroke();ctx.drawImage(image,index%3*cw,Math.floor(index/3)*ch,cw,ch,1240,550,cw*ratio,ch*ratio);
  return {phase,index};
}
draw(0);button.disabled=false;label.textContent='원화 준비됨 · 1배속 세 주기 관찰';
button.onclick=()=>{
  button.disabled=true;const start=performance.now(),rows=[],visibility=[];
  const onVisibility=()=>visibility.push({wallSeconds:(performance.now()-start)/1000,state:document.visibilityState});
  document.addEventListener('visibilitychange',onVisibility);onVisibility();
  function tick(now){
    const t=(now-start)/1000,shown=draw(t);
    rows.push({seconds:t,phase:shown.phase,frame:shown.index,rate:1,visibility:document.visibilityState});
    label.textContent=`1x 관찰 중 · ${t.toFixed(2)} / ${preview.durationSeconds.toFixed(2)}초`;
    if(t<preview.durationSeconds){requestAnimationFrame(tick);return;}
    document.removeEventListener('visibilitychange',onVisibility);
    const trace={kind:'sable-cycle-live-observation',recordedAt:new Date().toISOString(),
      cycleInputs:preview.cycleInputs,atlas:preview.atlas,video:preview.video,nativeCanvas:[canvas.width,canvas.height],
      viewport:[innerWidth,innerHeight],devicePixelRatio,
      durationSeconds:t,rate:1,seeking:false,rows,visibility,artApproval:false};
    window.cyclePlaybackTrace=trace;
    fetch('/__qa/rifle_e_live_'+Date.now()+'.json',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(trace)})
      .then(r=>{if(!r.ok)throw Error('trace save failed');label.textContent='1x 재생 기록 저장 — 원화·보행 승인 아님';})
      .catch(e=>{label.textContent=String(e);});
    button.disabled=false;
  }
  requestAnimationFrame(tick);
};
