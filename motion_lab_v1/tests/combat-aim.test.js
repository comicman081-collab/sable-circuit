import test from 'node:test';
import assert from 'node:assert/strict';
import {Actor,STEP,wrap} from '../public/simulation.js';
import {CombatKeyboard} from '../public/keyboard-input.js';
import {aimAtTarget,resolvePointerAim,applyPointerAim,createPlayerProjectile} from '../public/combat-aim.js';

const profile={radius:.19,locomotion:{walkSpeed:1.35,runSpeed:2.8,walkStride:1.6,runStride:1.95},weapon:{magazine:24,fireInterval:.11,reloadSeconds:1.25,damage:25}};

test('A cursor between the character and illustrated muzzle cannot make a bullet fly behind the facing',()=>{
  const actor=new Actor(profile),origin=[.8,-.4,1.23];
  const aim=aimAtTarget([0,0],[.2,0],actor.aim);
  actor.update(STEP,{x:0,y:-1,aim,fire:true});
  const bullet=createPlayerProjectile(actor,origin);
  assert.equal(actor.direction,0);
  assert.equal(bullet.vx,17);assert.equal(bullet.vy,0);
  assert.deepEqual([bullet.x,bullet.y,bullet.z],origin,'Emission still uses the actual transformed muzzle');
});

test('Turning throughout held moving fire keeps every projectile and rendered facing on one aim at 30/60/120 Hz',()=>{
  for(const hz of [30,60,120])for(const run of [false,true])for(let move=0;move<8;move++){
    const actor=new Actor(profile);let accumulator=0,shots=0;const faced=new Set();
    for(let frame=0;frame<hz*4;frame++){
      const facing=Math.floor(frame/hz*4)%8,angle=facing*Math.PI/4;
      const target=[actor.x+Math.cos(angle)*.25,actor.y+Math.sin(angle)*.25];
      accumulator+=1/hz;
      while(accumulator+1e-12>=STEP){
        const aim=aimAtTarget([actor.x,actor.y],target,actor.aim);
        if(actor.update(STEP,{x:Math.cos(move*Math.PI/4),y:Math.sin(move*Math.PI/4),run,aim,fire:true})){
          const bullet=createPlayerProjectile(actor,[actor.x+.8,actor.y-.4,1.23]);
          const shotAngle=Math.atan2(bullet.vy,bullet.vx);
          assert.ok(Math.abs(wrap(shotAngle-actor.aim))<1e-12);
          assert.ok(Math.abs(wrap(shotAngle-actor.renderPose().facing))<=Math.PI/8+.035+1e-9);
          shots++;faced.add(actor.direction);
        }
        accumulator-=STEP;
      }
    }
    assert.ok(shots>24);assert.equal(faced.size,8);assert.ok(actor.distance>1);
  }
});

test('A fresh movement chord can take aim during held mouse fire and the next mouse move can take it back',()=>{
  const actor=new Actor(profile),keyboard=new CombatKeyboard();let pointer=[2,0];
  const step=()=>actor.update(STEP,{...keyboard.read(),aim:pointer?aimAtTarget([actor.x,actor.y],pointer,actor.aim):null,fire:true});
  step();assert.equal(actor.direction,0);
  for(const code of ['KeyW','KeyA']){
    if(keyboard.keyDown({code},{followMovement:true,mouseAiming:true}).takeFacing)pointer=null;
    step();
  }
  assert.equal(actor.direction,5);
  pointer=[actor.x,actor.y+2];step();assert.equal(actor.direction,2);
  assert.equal(keyboard.keyDown({code:'KeyA',repeat:true}).takeFacing,false);
  step();assert.equal(actor.direction,2);
  const bullet=createPlayerProjectile(actor,[actor.x,actor.y,1.23]);assert.ok(bullet.vy>0);
});

test('An exactly centred cursor retains the previous aim instead of forcing east',()=>{
  assert.equal(aimAtTarget([1,2],[1,2],Math.PI),Math.PI);
});

test('One muzzle-aware solution preserves actual cursor hits and body/shot alignment throughout a turn',()=>{
  const actor=new Actor(profile);
  const muzzle=facing=>{const a=facing*Math.PI/4;return [actor.x+.8*Math.cos(a)+.2*Math.sin(a),actor.y+.8*Math.sin(a)-.2*Math.cos(a),1.23];};
  for(let degrees=0;degrees<720;degrees+=3){
    actor.update(STEP,{x:1,y:-1,fire:true});
    const angle=degrees*Math.PI/180,target=[actor.x+3*Math.cos(angle),actor.y+3*Math.sin(angle)];
    const solution=resolvePointerAim(actor,target,muzzle);actor.aim=solution.aim;actor.direction=solution.direction;
    const bullet=createPlayerProjectile(actor,muzzle(actor.direction));
    const dx=target[0]-bullet.x,dy=target[1]-bullet.y;
    assert.equal(solution.converges,true);
    assert.ok(Math.abs(dx*bullet.vy-dy*bullet.vx)<1e-10,'Shot ray must pass through the cursor');
    assert.ok(dx*bullet.vx+dy*bullet.vy>0,'Target must be ahead of the muzzle');
    assert.ok(Math.abs(wrap(Math.atan2(bullet.vy,bullet.vx)-actor.renderPose().facing))<=Math.PI/4+1e-9,'Use the nearest forward authored view at the discrete-muzzle boundary');
  }
});

test('A target inside weapon reach cannot turn only the bullet backwards',()=>{
  const actor=new Actor(profile),target=[.2,0];
  const solution=resolvePointerAim(actor,target,d=>[Math.cos(d*Math.PI/4),Math.sin(d*Math.PI/4),1.23]);
  assert.equal(solution.converges,false);assert.equal(solution.direction,0);assert.equal(solution.aim,0);
});

test('Rapid aim commits without advancing gait, recoil, ammo or cooldown; old projectiles do not home',()=>{
  const actor=new Actor({...profile,weapon:{...profile.weapon,fireInterval:.42}});
  actor.update(STEP,{x:1,y:0,fire:true});
  const muzzle=d=>[actor.x+Math.cos(d*Math.PI/4)*.8,actor.y+Math.sin(d*Math.PI/4)*.8,1.23];
  const old=createPlayerProjectile(actor,muzzle(0)),before=JSON.stringify(old);
  const invariant=()=>[actor.time,actor.phase,actor.distance,actor.x,actor.y,actor.ammo,actor.cooldown,actor.lastShot];
  const saved=invariant();
  for(const i of [4,0,2,6,1,5,3,7]){
    const angle=i*Math.PI/4,target=[actor.x+3*Math.cos(angle),actor.y+3*Math.sin(angle)];
    applyPointerAim(actor,target,muzzle);
    assert.equal(actor.direction,i);assert.ok(Math.abs(wrap(actor.aim-angle))<1e-12);
    assert.deepEqual(invariant(),saved);assert.equal(JSON.stringify(old),before);
  }
});

test('30/60/120 Hz rapid reversals use the latest sample at the first eligible shot without changing cadence',()=>{
  for(const hz of [30,60,120]){
    const actor=new Actor({...profile,weapon:{...profile.weapon,magazine:100,fireInterval:.42}});
    let accumulator=0,lastShot=null,count=0;
    const muzzle=d=>[actor.x+.8*Math.cos(d*Math.PI/4),actor.y+.8*Math.sin(d*Math.PI/4),1.23];
    for(let f=0;f<hz*3;f++){
      const aim=f%2?Math.PI:0,target=[actor.x+3*Math.cos(aim),actor.y];
      applyPointerAim(actor,target,muzzle);
      assert.ok(Math.abs(wrap(actor.aim-aim))<1e-12,'No fixed-step wait for latest input');
      accumulator+=1/hz;
      while(accumulator+1e-12>=STEP){
        const fired=actor.update(STEP,{x:0,y:1,fire:true,aim:actor.aim});
        applyPointerAim(actor,target,muzzle);
        if(fired){
          const b=createPlayerProjectile(actor,muzzle(actor.direction));
          assert.ok(Math.abs((target[0]-b.x)*b.vy-(target[1]-b.y)*b.vx)<1e-10);
          if(lastShot!==null)assert.ok(Math.abs(actor.time-lastShot-.42)<=STEP+1e-10);
          lastShot=actor.time;count++;
        }
        accumulator-=STEP;
      }
    }
    assert.equal(count,8);
  }
});
