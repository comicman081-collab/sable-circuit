// A fixed-step, renderer-independent controller shared by preview and combat.
export const DIRECTIONS=['E','SE','S','SW','W','NW','N','NE'];
export const TAU=Math.PI*2;
export const STEP=1/120;
export const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export const wrap=a=>Math.atan2(Math.sin(a),Math.cos(a));
export const direction=a=>(Math.round(a/(Math.PI/4))+8)%8;

export class Actor {
  constructor(profile){
    this.profile=profile;
    this.x=this.y=this.vx=this.vy=this.phase=this.time=this.distance=0;
    this.direction=0;this.aim=0;this.moveAngle=0;this.amount=0;
    this.run=false;this.firing=false;this.cooldown=0;this.reload=0;this.lastShot=-10;this.shotBuffer=0;
    this.ammo=profile.weapon.magazine;this.shots=0;this.kills=0;this.hp=100;
  }
  get recoil(){const t=(this.time-this.lastShot)*27;return t<0?0:(1+t)*Math.exp(-t);}
  requestReload(){if(this.reload===0&&this.ammo<this.profile.weapon.magazine)this.reload=this.profile.weapon.reloadSeconds;}
  queueShot(){this.shotBuffer=.18;}
  update(dt,input,blocks=[]){
    if(!(dt>0&&dt<=.05))throw new RangeError('Use bounded fixed simulation steps.');
    this.time+=dt;this.run=!!input.run;
    const firing=!!input.fire||this.shotBuffer>0;this.firing=firing;this.shotBuffer=Math.max(0,this.shotBuffer-dt);
    let x=input.x||0,y=input.y||0;const length=Math.hypot(x,y);
    if(length>1){x/=length;y/=length;}
    const speed=this.run?this.profile.locomotion.runSpeed:this.profile.locomotion.walkSpeed;
    const gain=1-Math.exp(-18*dt);
    this.vx+=(x*speed-this.vx)*gain;this.vy+=(y*speed-this.vy)*gain;
    let nx=this.x+this.vx*dt,ny=this.y+this.vy*dt;const radius=this.profile.radius||.19;
    for(const b of blocks){
      if(nx>b.x-radius&&nx<b.x+b.w+radius&&this.y>b.y-radius&&this.y<b.y+b.h+radius){nx=this.x;this.vx=0;}
      if(ny>b.y-radius&&ny<b.y+b.h+radius&&nx>b.x-radius&&nx<b.x+b.w+radius){ny=this.y;this.vy=0;}
    }
    nx=clamp(nx,-7.7,7.7);ny=clamp(ny,-5.7,5.7);
    const travel=Math.hypot(nx-this.x,ny-this.y);this.distance+=travel;
    this.x=nx;this.y=ny;
    if(travel>.000001){
      this.moveAngle=Math.atan2(this.vy,this.vx);
      const stride=this.run?this.profile.locomotion.runStride:this.profile.locomotion.walkStride;
      this.phase=(this.phase+travel/stride)%1;
    }
    this.amount+=(clamp(travel/(dt*speed),0,1)-this.amount)*(1-Math.exp(-16*dt));
    // Facing follows the requested direction immediately; velocity alone
    // still eases through the turn and controls the foot-cycle distance.
    if(input.aim!=null)this.aim=input.aim;else if(length>.02)this.aim=Math.atan2(y,x);
    if(Math.abs(wrap(this.aim-this.direction*Math.PI/4))>Math.PI/8+.035)this.direction=direction(this.aim);
    if(input.reload)this.requestReload();
    if(this.reload>0){this.reload=Math.max(0,this.reload-dt);if(this.reload===0)this.ammo=this.profile.weapon.magazine;}
    this.cooldown-=dt;
    let fired=false;
    if(firing&&this.reload===0&&this.cooldown<=0){
      if(this.ammo>0){
        this.ammo--;this.shots++;this.lastShot=this.time;fired=true;this.shotBuffer=0;
        this.cooldown+=this.profile.weapon.fireInterval;
      }else this.requestReload();
    }
    if(!firing||this.reload>0)this.cooldown=Math.max(0,this.cooldown);
    return fired;
  }
  renderPose(facingDirection=this.direction){
    const backwards=Math.cos(this.moveAngle-facingDirection*Math.PI/4)<-.35;
    return {phase:backwards?(1-this.phase)%1:this.phase,amount:this.amount,run:this.run,
      // Keep the weapon raised through the held-fire/recoil window so the
      // authored body and the muzzle/projectile line read as one action.
      firing:this.firing||this.recoil>.045,recoil:this.recoil,aim:this.aim,facing:facingDirection*Math.PI/4,time:this.time,
      reload:this.reload?Math.sin(Math.PI*this.reload/this.profile.weapon.reloadSeconds):0};
  }
}

export function segmentCircle(a,b,c,r){
  const dx=b[0]-a[0],dy=b[1]-a[1];
  const t=clamp(((c[0]-a[0])*dx+(c[1]-a[1])*dy)/(dx*dx+dy*dy||1),0,1);
  return Math.hypot(a[0]+t*dx-c[0],a[1]+t*dy-c[1])<=r;
}
export function segmentBox(a,b,box){
  let lo=0,hi=1;
  for(const [i,min,max] of [[0,box.x,box.x+box.w],[1,box.y,box.y+box.h]]){
    const d=b[i]-a[i];
    if(Math.abs(d)<1e-9){if(a[i]<min||a[i]>max)return false;continue;}
    let t0=(min-a[i])/d,t1=(max-a[i])/d;if(t0>t1)[t0,t1]=[t1,t0];
    lo=Math.max(lo,t0);hi=Math.min(hi,t1);if(lo>hi)return false;
  }
  return true;
}
