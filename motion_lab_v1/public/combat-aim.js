import {direction,wrap} from './simulation.js';

// Resolve cursor, authored facing and muzzle together before emitting a shot.
// The firing path must never compute a different angle behind the renderer.
export function aimAtTarget(position,target,fallback=0){
  const dx=target[0]-position[0],dy=target[1]-position[1];
  return Math.hypot(dx,dy)<1e-6?fallback:Math.atan2(dy,dx);
}

export function resolvePointerAim(actor,target,muzzleForDirection){
  const root=[actor.x,actor.y],fallback=aimAtTarget(root,target,actor.aim);
  const records=Array.from({length:8},(_,facing)=>{
    const muzzle=muzzleForDirection(facing),aim=aimAtTarget(muzzle,target,fallback);
    return {direction:facing,muzzle,aim,error:Math.abs(wrap(aim-facing*Math.PI/4))};
  });
  // Inside the illustrated weapon reach there may be no forward ray toward
  // the cursor. Keep a forward body/shot cone instead of shooting backwards.
  const reach=Math.max(...records.map(r=>Math.hypot(r.muzzle[0]-actor.x,r.muzzle[1]-actor.y)));
  if(Math.hypot(target[0]-actor.x,target[1]-actor.y)>reach+.05){
    const current=records[actor.direction];
    if(current.error<=Math.PI/8+.035)return {...current,converges:true};
    // Discrete authored muzzles can leave a gap between adjacent half-octant
    // cones. Pick the closest forward-facing view, at most one octant away,
    // rather than missing a reachable cursor or iterating between two views.
    const candidates=records.filter(r=>r.error<=Math.PI/4).sort((a,b)=>a.error-b.error);
    if(candidates.length)return {...candidates[0],converges:true};
  }
  return {aim:fallback,direction:direction(fallback),converges:false};
}

// Commit the latest sample synchronously, not through the locomotion clock or
// weapon cooldown. Reuse this before emission and presentation as the camera,
// authored frame and recoil can move the illustrated muzzle in between inputs.
export function applyPointerAim(actor,target,muzzleForDirection){
  const solution=resolvePointerAim(actor,target,muzzleForDirection);
  actor.aim=solution.aim;actor.direction=solution.direction;
  return solution;
}

export function createPlayerProjectile(actor,origin){
  const [x,y,z]=origin,aim=actor.aim;
  return {x,y,z,vx:Math.cos(aim)*17,vy:Math.sin(aim)*17,life:1.15,enemy:false};
}
