import test from 'node:test';
import assert from 'node:assert/strict';
import {Actor,STEP,DIRECTIONS,segmentCircle,segmentBox} from '../public/simulation.js';
const profile={radius:.19,locomotion:{walkSpeed:1.35,runSpeed:2.8,walkStride:1.6,runStride:1.95},weapon:{magazine:24,fireInterval:.11,reloadSeconds:1.25,damage:25}};
test('A click shorter than one render frame fires once without a held button',()=>{
  const actor=new Actor(profile);actor.queueShot();
  assert.equal(actor.update(STEP,{x:0,y:0,fire:false}),true);
  for(let i=0;i<120;i++)actor.update(STEP,{x:0,y:0,fire:false});
  assert.equal(actor.shots,1);assert.equal(actor.ammo,23);
  actor.requestReload();actor.queueShot();
  for(let i=0;i<180;i++)actor.update(STEP,{x:0,y:0,fire:false});
  assert.equal(actor.shots,1,'An expired click during reload must not fire later');
});
function simulate(hz,seconds,input,blocks=[]){
  const a=new Actor(profile);let accumulator=0;
  for(let frame=0;frame<hz*seconds;frame++){
    accumulator+=1/hz;
    while(accumulator+1e-12>=STEP){a.update(STEP,typeof input==='function'?input(a.time):input,blocks);accumulator-=STEP;}
  }
  return a;
}
test('All eight movement directions and all eight independent firing facings, at three display rates',()=>{
  for(const run of [false,true])for(let move=0;move<8;move++)for(let aim=0;aim<8;aim++){
    const angle=move*Math.PI/4,input={x:Math.cos(angle),y:Math.sin(angle),aim:aim*Math.PI/4,fire:true,run};
    const results=[30,60,120].map(hz=>simulate(hz,1,input));
    for(const a of results){
      assert.equal(a.direction,aim,DIRECTIONS[move]+' → '+DIRECTIONS[aim]);
      assert.ok(a.shots>=9&&a.shots<=10);assert.ok(a.distance>.9);
      assert.ok(Math.abs(Math.atan2(a.y,a.x)-angle)<1e-6||Math.abs(Math.abs(Math.atan2(a.y,a.x)-angle)-Math.PI*2)<1e-6);
      assert.ok(a.phase>=0&&a.phase<1);assert.ok(Number.isFinite(a.recoil));
    }
    for(const a of results.slice(1)){assert.equal(a.x,results[0].x);assert.equal(a.y,results[0].y);assert.equal(a.shots,results[0].shots);}
  }
});
test('Diagonal keys do not create a speed advantage',()=>{
  const horizontal=simulate(60,1,{x:1,y:0}),diagonal=simulate(60,1,{x:1,y:1});
  assert.ok(Math.abs(horizontal.distance-diagonal.distance)<1e-9);
});
test('Stop, resume and speed switch retain a valid continuous locomotion phase',()=>{
  const a=simulate(60,3,t=>t<.8?{x:1,y:0}:t<1.7?{x:0,y:0}:{x:0,y:1,run:true});
  assert.ok(a.x>0&&a.y>0);assert.equal(a.run,true);assert.ok(a.amount>.99);
  const stopped=simulate(60,2,t=>({x:t<.5?1:0,y:0}));
  assert.ok(stopped.amount<.001);assert.ok(Math.abs(stopped.vx)<1e-9);assert.ok(stopped.phase>0);
});
test('Held fire consumes ammunition, automatically reloads, and remains rate independent',()=>{
  const results=[30,60,120].map(hz=>simulate(hz,7,{x:0,y:0,aim:0,fire:true}));
  for(const a of results){assert.equal(a.shots,results[0].shots);assert.equal(a.ammo,results[0].ammo);assert.ok(a.shots>40&&a.shots<60);assert.ok(a.ammo>=0&&a.ammo<=24);}
});
test('Reload prevents shots and restores the magazine only when complete',()=>{
  const a=new Actor(profile);a.update(STEP,{fire:true});a.requestReload();const before=a.shots;
  for(let i=0;i<100;i++)a.update(STEP,{fire:true});assert.equal(a.shots,before);assert.equal(a.ammo,23);
  for(let i=0;i<100;i++)a.update(STEP,{fire:false});assert.equal(a.ammo,24);assert.equal(a.reload,0);
});
test('Obstacles and world bounds constrain actual position',()=>{
  const block={x:.7,y:-.5,w:.4,h:1};const a=simulate(120,3,{x:1,y:0,run:true},[block]);
  assert.ok(a.x<=block.x-.19+.00001);assert.ok(a.x>.45);
  const bounded=simulate(60,12,{x:1,y:1,run:true});assert.ok(bounded.x<=7.7&&bounded.y<=5.7);
});
test('Swept projectile collision catches thin targets between ticks',()=>{
  assert.equal(segmentCircle([-1,0],[1,0],[0,0],.1),true);
  assert.equal(segmentCircle([-1,.2],[1,.2],[0,0],.1),false);
  assert.equal(segmentBox([-2,0],[2,0],{x:-.1,y:-.2,w:.2,h:.4}),true);
  assert.equal(segmentBox([-2,1],[2,1],{x:-.1,y:-.2,w:.2,h:.4}),false);
});
