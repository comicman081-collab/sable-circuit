// Portable character motion: artwork, pose, and gameplay share this module.
export const DIRECTIONS=['E','SE','S','SW','W','NW','N','NE'];
export const TAU=Math.PI*2;
export const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
export const mix=(a,b,t)=>a+(b-a)*t;
const smooth=x=>{x=clamp(x,0,1);return x*x*(3-2*x)};
export function sector(x,y){return ((Math.round(Math.atan2(y,x)/(Math.PI/4))%8)+8)%8}
export function wrap(a){return Math.atan2(Math.sin(a),Math.cos(a))}
const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const add=(a,b)=>a.map((x,i)=>x+b[i]);
const sub=(a,b)=>a.map((x,i)=>x-b[i]);
const mul=(a,s)=>a.map(x=>x*s);
const norm=a=>mul(a,1/(Math.hypot(...a)||1));
function knee3(hip,ankle,forward,a=.435,b=.43){
  const d=sub(ankle,hip),len=clamp(Math.hypot(...d),.05,a+b-.003),axis=norm(d);
  const reach=(a*a-b*b+len*len)/(2*len),height=Math.sqrt(Math.max(0,a*a-reach*reach));
  const bend=norm(sub(forward,mul(axis,dot(forward,axis))));
  return add(add(hip,mul(axis,reach)),mul(bend,height));
}
function segmentTransform(a,b,c,d){
  const u=sub(b,a),v=sub(d,c),ll=Math.hypot(...u)||1,tl=Math.hypot(...v)||1;
  const ux=u[0]/ll,uy=u[1]/ll,vx=v[0]/tl,vy=v[1]/tl,s=tl/ll;
  const m=[s*vx*ux+vy*uy,s*vy*ux-vx*uy,s*vx*uy-vy*ux,s*vy*uy+vx*ux,0,0];
  m[4]=c[0]-m[0]*a[0]-m[2]*a[1];m[5]=c[1]-m[1]*a[0]-m[3]*a[1];return m;
}
function rigid(anchor,target,angle=0){const c=Math.cos(angle),s=Math.sin(angle);return[c,s,-s,c,target[0]-c*anchor[0]+s*anchor[1],target[1]-s*anchor[0]-c*anchor[1]]}
export const transform=(m,p)=>[m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]];

export function pose(view,{phase=0,amount=1,run=false,moveAngle=0,facing=0,time=0,recoil=0,reload=0}={}){
  const ppm=view.height/1.72,forward=[Math.cos(facing),Math.sin(facing),0],move=[Math.cos(moveAngle),Math.sin(moveAngle),0];
  const stance=run?.43:.64,stride=run?1.85:1.7;
  const pulse=Math.sin(TAU*phase*2),bob=amount*(run?.035:.014)*(-Math.cos(TAU*phase*2));
  const breath=(1-amount)*Math.sin(time*2)*.0025;
  const upperAngle=amount*.007*Math.sin(TAU*phase)+Math.cos(facing)*recoil*.045+Math.cos(facing)*reload*.055;
  const hipTarget=[view.hip[0]-recoil*ppm*.018*Math.cos(facing),view.hip[1]-(bob+breath)*ppm+reload*ppm*.016];
  const upper=rigid(view.hip,hipTarget,upperAngle), matrices=[upper],joints=[],feet=[];
  for(let side=0;side<2;side++){
    const p=(phase+side*.5)%1; let advance,lift,roll;
    if(p<stance){advance=stride*(stance*.5-p);lift=0;roll=smooth((p/stance-.78)/.22)*(run?.24:.15);}
    else{const s=(p-stance)/(1-stance);advance=mix(-stride*stance*.5,stride*stance*.5,smooth(s));lift=Math.sin(Math.PI*s)*(run?.29:.13);roll=-Math.sin(Math.PI*s)*.16;}
    advance*=amount;lift*=amount;roll*=amount;
    const h=view.hips[side],a=view.ankles[side],sole=view.soles[side];
    const half=(side===0?-1:1)*.085;
    const lateral=[-Math.sin(facing)*half,Math.cos(facing)*half,0];
    const foot=[lateral[0]+move[0]*advance,lateral[1]+move[1]*advance,lift];
    const hip=[lateral[0],lateral[1],.91+bob];
    const screen=(v)=>[view.hip[0]+(h[0]-view.hip[0])+ (v[0]-lateral[0])*ppm,view.hip[1]+(h[1]-view.hip[1]) +(.91-v[2]+v[1]*.58)*ppm];
    const targetGround=screen(foot),ground=targetGround.map((n,j)=>mix(sole[j]-(j===1?bob*ppm:0),n,amount));const bootAngle=-Math.cos(facing)*roll;
    const boot=rigid(sole,ground,bootAngle),ankle=transform(boot,a);
    const ankle3=[(ankle[0]-h[0])/ppm+lateral[0],foot[1],.91+foot[1]*.58-(ankle[1]-h[1])/ppm];
    const k=knee3(hip,ankle3,forward),targetKnee=screen(k),knee=targetKnee.map((n,j)=>mix(view.knees[side][j]-(j===1?bob*ppm:0),n,amount)),hip2=screen(hip).map((n,j)=>mix(h[j]-(j===1?bob*ppm:0),n,amount));
    const thigh=segmentTransform(h,view.knees[side],hip2,knee),calf=segmentTransform(view.knees[side],a,knee,ankle);
    matrices.push(thigh,calf,boot);joints.push([hip2,knee,ankle,ground]);
    feet.push({phase:p,contact:p<stance||amount<.02,ground,lift,advance});
  }
  const root=[view.hip[0],view.hip[1]+.91*ppm];
  return{matrices,joints,feet,root,muzzle:transform(upper,view.muzzle),upper,coatSway:amount*(run?.024:.012)*ppm*Math.sin(TAU*phase-.7),ppm,phase,amount};
}
function inPolygon(p,poly){let c=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])c=!c;}return c}
function distanceSegment(p,a,b){const d=sub(b,a),t=clamp(dot(sub(p,a),d)/(dot(d,d)||1),0,1);return Math.hypot(p[0]-a[0]-t*d[0],p[1]-a[1]-t*d[1])}
export function bindVertex(v,p,layer=null){
  if(layer===0)return{ids:[0],weights:[1],coat:0};
  if(layer===1)return{ids:[0],weights:[1],coat:smooth((p[1]-v.waistY)/(v.height*.5))};
  if(p[1]<v.waistY)return{ids:[0],weights:[1],coat:0};
  const coat=layer===null&&v.coatPolygons.some(poly=>inPolygon(p,poly));
  if(coat)return{ids:[0],weights:[1],coat:smooth((p[1]-v.waistY)/(v.height*.5))};
  const distance=[0,1].map(i=>Math.min(distanceSegment(p,v.hips[i],v.knees[i]),distanceSegment(p,v.knees[i],v.ankles[i]),distanceSegment(p,v.ankles[i],v.soles[i])));
  const side=layer===2?0:layer===3?1:distance[0]<distance[1]?0:1;
  const h=v.hips[side],k=v.knees[side],a=v.ankles[side];
  // Soft skinning only around actual joints. The boot and illustrated torso stay rigid.
  const upper=smooth((p[1]-(h[1]-v.height*.055))/(v.height*.075));
  const calf=smooth((p[1]-(k[1]-v.height*.045))/(v.height*.09));
  const boot=smooth((p[1]-(a[1]-v.height*.035))/(v.height*.07));
  return{ids:[0,1+side*3,2+side*3,3+side*3],weights:[1-upper,upper*(1-calf),upper*calf*(1-boot),upper*calf*boot],coat:0};
}
export function deformPoint(p,b,pose){let x=0,y=0;for(let i=0;i<b.ids.length;i++){const q=transform(pose.matrices[b.ids[i]],p);x+=q[0]*b.weights[i];y+=q[1]*b.weights[i];}return[x+pose.coatSway*b.coat,y+Math.abs(pose.coatSway)*b.coat*.16]}

export class Controller{
  constructor(profile){this.profile=profile;this.x=0;this.y=0;this.vx=0;this.vy=0;this.phase=0;this.amount=0;this.run=false;this.moveAngle=0;this.aim=0;this.direction=0;this.recoil=0;this.recoilVelocity=0;this.cooldown=0;this.reload=0;this.ammo=profile.weapon.magazine;this.shots=0;this.health=100;this.kills=0;this.time=0;this.distance=0;}
  update(dt,input,blocks=[]){
    dt=clamp(dt,0,.1);this.time+=dt;this.run=!!input.run;let x=input.x||0,y=input.y||0,l=Math.hypot(x,y);if(l>1){x/=l;y/=l;l=1;}
    const speed=this.run?this.profile.locomotion.runSpeed:this.profile.locomotion.walkSpeed;
    const k=1-Math.exp(-dt*18);this.vx=mix(this.vx,x*speed,k);this.vy=mix(this.vy,y*speed,k);
    let nx=this.x+this.vx*dt,ny=this.y+this.vy*dt;
    const radius=.2;for(const b of blocks){if(nx>b.x-radius&&nx<b.x+b.w+radius&&this.y>b.y-radius&&this.y<b.y+b.h+radius)nx=this.x;if(ny>b.y-radius&&ny<b.y+b.h+radius&&nx>b.x-radius&&nx<b.x+b.w+radius)ny=this.y;}
    nx=clamp(nx,-8,8);ny=clamp(ny,-5.7,5.7);
    const distance=Math.hypot(nx-this.x,ny-this.y);this.distance+=distance;this.x=nx;this.y=ny;
    if(distance>1e-6){this.moveAngle=Math.atan2(this.vy,this.vx);this.phase=(this.phase+distance/(this.run?this.profile.locomotion.runStride:this.profile.locomotion.walkStride))%1;}
    this.amount=mix(this.amount,clamp(distance/(dt*speed||1),0,1),1-Math.exp(-dt*16));
    if(input.aim!=null)this.aim=input.aim;else if(l>.01)this.aim=this.moveAngle;
    const desired=sector(Math.cos(this.aim),Math.sin(this.aim));
    if(Math.abs(wrap(this.aim-this.direction*Math.PI/4))>Math.PI/8+.04)this.direction=desired;
    this.cooldown=Math.max(0,this.cooldown-dt);const wasReloading=this.reload>0;this.reload=Math.max(0,this.reload-dt);
    if(wasReloading&&this.reload===0)this.ammo=this.profile.weapon.magazine;
    if(input.reload&&this.reload===0&&this.ammo<this.profile.weapon.magazine)this.reload=this.profile.weapon.reloadSeconds;
    this.recoilVelocity+=(-this.recoil*240-this.recoilVelocity*24)*dt;this.recoil+=this.recoilVelocity*dt;
    let fired=false;if(input.fire&&!this.reload&&this.cooldown===0){if(this.ammo>0){this.ammo--;this.shots++;this.cooldown=this.profile.weapon.fireInterval;this.recoil=1;this.recoilVelocity=0;fired=true;}else this.reload=this.profile.weapon.reloadSeconds;}
    return fired;
  }
  pose(view){return pose(view,{phase:this.phase,amount:this.amount,run:this.run,moveAngle:this.moveAngle,facing:this.direction*Math.PI/4,time:this.time,recoil:Math.max(0,this.recoil),reload:this.reload?Math.sin(Math.PI*this.reload/this.profile.weapon.reloadSeconds):0});}
}
