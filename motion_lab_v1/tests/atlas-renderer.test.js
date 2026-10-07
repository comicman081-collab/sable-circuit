import test from 'node:test';
import assert from 'node:assert/strict';
import {AtlasRenderer,phaseForFrame,phaseIndex} from '../public/atlas-renderer.js';
import {Actor,STEP,DIRECTIONS} from '../public/simulation.js';

test('An authored profile ignores leftover character-specific fire and leg-warp bundles',async()=>{
  const r=Object.create(AtlasRenderer.prototype);r.models={};
  const stale=new Proxy({},{get(){throw Error('Legacy bundle was accessed');}});
  await r.load({animation:{presentation:'authored_frames'},views:{}},stale);
  assert.deepEqual(r.fullBodyModels,{});assert.deepEqual(r.fireModels,{});
});

// Exercise the real renderer's selection logic; no DOM/WebGL is needed.
const renderer=Object.create(AtlasRenderer.prototype);
renderer.models=Object.fromEntries(DIRECTIONS.map(d=>[d,{view:{},clips:{walk:{texture:'authored-walk',im:{},clip:{frames:6}},idle:{texture:'authored-idle',im:{},clip:{frames:1}}}}]));
test('Shared authored route keeps identical leg phases with and without fire',()=>{
  for(const d of DIRECTIONS)for(const run of [false,true])for(let i=0;i<6;i++){
    const pose={amount:1,phase:(i+.1)/6,run,time:0,recoil:0};
    const before=renderer.frame(d,pose),shot=renderer.frame(d,{...pose,firing:true,recoil:1});
    assert.equal(before.index,i);assert.equal(shot.index,i);assert.equal(before.texture,shot.texture);
  }
});
test('Authored contact timing holds planted steps while preserving phase order',()=>{
  const starts=[0,.20,.33,.50,.70,.83];
  const expected=[
    [0,0],[.1999,0],[.20,1],[.3299,1],[.33,2],
    [.4999,2],[.50,3],[.6999,3],[.70,4],[.8299,4],[.83,5],[.9999,5]
  ];
  for(const [phase,index] of expected)assert.equal(phaseIndex(phase,6,starts),index,`phase ${phase}`);
  for(let index=0;index<6;index++)assert.equal(phaseIndex(phaseForFrame(index,6,starts),6,starts),index,`review frame ${index}`);
  // An ASTER-style profile has no separate run art, so sprint reuses the same
  // authored step ordering rather than reverting to equal wall-clock frames.
  renderer.models.E.clips.walk.clip.phaseStarts=starts;
  assert.equal(renderer.frame('E',{amount:1,run:true,phase:.205}).index,1);
  assert.equal(renderer.frame('E',{amount:1,run:true,phase:.505}).index,3);
  delete renderer.models.E.clips.walk.clip.phaseStarts;
});
test('Shared recoil transform cannot move support feet',()=>{
  const clip={root:[384,716],height:656};
  for(const facing of [0,Math.PI/2,Math.PI,3*Math.PI/2])for(const recoil of [0,.2,1]){
    const pose={facing,recoil,reload:0,time:1,amount:0};
    for(const foot of [[220,710],[540,709]])assert.deepEqual(renderer.projectPoint(clip,pose,foot,300,500,270),renderer.projectPoint(clip,{...pose,recoil:0},foot,300,500,270));
  }
});
renderer.fullBodyModels=Object.fromEntries(DIRECTIONS.map(d=>[d,{
  ...Object.fromEntries(['walk','run','move','idle','fire'].map(a=>[a,{texture:a,im:{height:384*(a==='move'?24:6)}}])),
  frameCounts:{walk:6,run:6,move:24,idle:4,fire:6},frameRates:{idle:4,fire:12},root:[192,350],cell:[384,384],artHeight:340,
}]));
test('Full-body walk AND run select all six phases, never recoil recovery frame 5',()=>{
  for(const d of DIRECTIONS)for(const run of [false,true])for(const recoil of [0,.2,.5,1]){
    const rows=Array.from({length:6},(_,i)=>renderer.fullBodyFrame(d,{amount:1,run,recoil,phase:(i+.1)/6}));
    assert.deepEqual(rows.map(r=>r.index),[0,1,2,3,4,5],`${d} run=${run} recoil=${recoil}`);
    assert.ok(rows.every(r=>r.action===(run?'run':'walk')));
  }
});
test('Locomotion is distance phase driven, not wall-clock or firing cadence',()=>{
  for(const firing of [false,true])for(const run of [false,true]){
    const a=renderer.fullBodyFrame('E',{amount:1,run,firing,phase:.35,time:0,recoil:0});
    const b=renderer.fullBodyFrame('E',{amount:1,run,firing,phase:.35,time:50,recoil:1});
    assert.equal(a.index,b.index);
  }
});
test('Live Actor → full-body renderer traverses walk/run cycles at 30/60/120 Hz',()=>{
  const profile={radius:.19,locomotion:{walkSpeed:1.35,runSpeed:2.8,walkStride:1.6,runStride:1.95},weapon:{magazine:24,fireInterval:.11,reloadSeconds:1.25}};
  for(const hz of [30,60,120])for(const run of [false,true])for(const d of DIRECTIONS){
    const actor=new Actor(profile),frames=new Set(),angle=DIRECTIONS.indexOf(d)*Math.PI/4;
    for(let t=0;t<hz*1.5;t++){
      for(let n=0;n<120/hz;n++)actor.update(STEP,{x:Math.cos(angle),y:Math.sin(angle),run});
      const r=renderer.fullBodyFrame(d,actor.renderPose());
      if(actor.amount>.1)frames.add(r.index);
    }
    assert.equal(frames.size,6,`${d} run=${run} hz=${hz}: frozen or skipped cycle`);
  }
});
