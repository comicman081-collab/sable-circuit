import {DIRECTIONS,clamp} from './simulation.js';

// A source cycle may use a non-uniform amount of travelled distance per
// keyframe.  In particular, a natural walk lingers on each planted contact
// and crosses the two unweighted transition frames more quickly.  This stays
// distance-driven: frame timing never depends on wall-clock time or firing.
export function phaseIndex(phase,frames,phaseStarts=null){
  const count=Math.max(1,Math.trunc(Number(frames)||1));
  // Avoid adding 1 before a positive boundary: 0.2 + 1 can round below the
  // authored 0.20 transition on a binary float, holding the prior keyframe.
  const raw=Number(phase)||0;
  const p=raw-Math.floor(raw);
  const valid=Array.isArray(phaseStarts)&&phaseStarts.length===count&&phaseStarts[0]===0&&
    phaseStarts.every((value,index)=>Number.isFinite(value)&&value>=0&&value<1&&(index===0||value>phaseStarts[index-1]));
  if(valid){
    for(let index=count-1;index>=0;index--)if(p>=phaseStarts[index])return index;
  }
  return Math.floor(p*count)%count;
}

// Review tools address a keyframe by its ordinal. Pick the middle of its
// authored interval so a non-uniform contact dwell cannot make “frame 2”
// preview frame 1.
export function phaseForFrame(frame,frames,phaseStarts=null){
  const count=Math.max(1,Math.trunc(Number(frames)||1));
  const index=((Math.trunc(Number(frame)||0)%count)+count)%count;
  const valid=Array.isArray(phaseStarts)&&phaseStarts.length===count&&phaseStarts[0]===0&&
    phaseStarts.every((value,position)=>Number.isFinite(value)&&value>=0&&value<1&&(position===0||value>phaseStarts[position-1]));
  const start=valid?phaseStarts[index]:index/count;
  const end=valid?(phaseStarts[index+1]??1):(index+1)/count;
  return start+(end-start)*.5;
}

// Only authored RGBA frames enter the live texture. Recoil is a continuous
// upper-body transform, applied to a dense quad without detaching any limb.
export class AtlasRenderer {
  constructor(canvas){
    this.canvas=canvas;this.models={};
    const options={alpha:true,antialias:true,premultipliedAlpha:false,preserveDrawingBuffer:true};
    const gl=this.gl=canvas.getContext('webgl2',options)||canvas.getContext('webgl',options);
    if(!gl)throw new Error('WebGL을 사용할 수 없습니다.');
    this.webgl2=typeof WebGL2RenderingContext!=='undefined'&&gl instanceof WebGL2RenderingContext;
    const shader=(kind,source)=>{const s=gl.createShader(kind);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
    const p=this.program=gl.createProgram();
    let vs='attribute vec2 a_position;attribute vec2 a_uv;uniform vec2 u_resolution;varying vec2 v_uv;void main(){gl_Position=vec4(a_position/u_resolution*vec2(2.,-2.)+vec2(-1.,1.),0.,1.);v_uv=a_uv;}';
    let fs='precision highp float;uniform sampler2D u_image;uniform float u_alpha;varying vec2 v_uv;void main(){vec4 c=texture2D(u_image,v_uv);gl_FragColor=vec4(c.rgb,c.a*u_alpha);}';
    if(this.webgl2){vs='#version 300 es\n'+vs.replaceAll('attribute ','in ').replace('varying ','out ');fs='#version 300 es\n'+fs.replace('varying ','in ').replace('void main()','out vec4 fragColor;void main()').replace('texture2D(','texture(').replace('gl_FragColor','fragColor');}
    gl.attachShader(p,shader(gl.VERTEX_SHADER,vs));gl.attachShader(p,shader(gl.FRAGMENT_SHADER,fs));
    gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));
    this.aPosition=gl.getAttribLocation(p,'a_position');this.aUv=gl.getAttribLocation(p,'a_uv');
    this.uResolution=gl.getUniformLocation(p,'u_resolution');this.uAlpha=gl.getUniformLocation(p,'u_alpha');
    this.positionBuffer=gl.createBuffer();this.uvBuffer=gl.createBuffer();
  }
  async load(profile,fireBundle=null){
    this.profile=profile;this.fireModels={};this.fullBodyModels={};
    // A modern recipe owns ALL states. A leftover character-specific bundle
    // must not silently replace its approved full-body walk/idle artwork.
    if(profile.animation?.presentation==='authored_frames')fireBundle=null;
    const loadTexture=async(src)=>{
      const im=new Image();im.decoding='async';im.src=src;await im.decode();
      const gl=this.gl,texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);
      gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,im);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
      if(this.webgl2){gl.generateMipmap(gl.TEXTURE_2D);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);}
      return {texture,im};
    };
    await Promise.all(Object.entries(profile.views).map(async([name,view])=>{
      const clips={};
      for(const action of ['walk','run','idle']){if(!view[action])continue;
        const {texture,im}=await loadTexture(view[action].image);
        clips[action]={texture,im,clip:view[action]};
      }
      this.models[name]={...clips.walk,clips,view};
    }));
    // Current ASTER production uses one authored full-body raster for every
    // state.  This prevents the old upper/lower seam and keeps idle, walking,
    // and firing on the same identity/weapon silhouette.
    if(fireBundle?.runtime_eligible===true&&fireBundle.contracts?.single_full_body_texture_per_frame&&fireBundle.directions){
      const cell=Array.isArray(fireBundle.cell)?fireBundle.cell:[384,384];
      const artHeight=Number.isFinite(fireBundle.art_height)?fireBundle.art_height:340;
      const frameCounts=fireBundle.frames||{idle:4,move:24,fire:6};
      const frameRates=fireBundle.fps||{idle:4,move:24,fire:12};
      await Promise.all(Object.entries(fireBundle.directions).map(async([name,entry])=>{
        if(!entry?.idle||!entry.move||!entry.fire)return;
        const walkSource=entry.walk||entry.move,runSource=entry.run||walkSource;
        const [idle,move,fire,walk,run]=await Promise.all([
          loadTexture(entry.idle),loadTexture(entry.move),loadTexture(entry.fire),
          loadTexture(walkSource),loadTexture(runSource)
        ]);
        this.fullBodyModels[name]={idle,move,fire,walk,run,muzzle:entry.muzzle,root:entry.root||[192,350],cell,artHeight,
          frameCounts:{idle:frameCounts.idle||4,walk:frameCounts.walk||6,run:frameCounts.run||6,move:frameCounts.move||24,fire:frameCounts.fire||6},
          frameRates:{idle:frameRates.idle||4,walk:frameRates.walk||8,run:frameRates.run||12,move:frameRates.move||24,fire:frameRates.fire||12},muzzleFrame:fireBundle.muzzle_frame??2};
      }));
    }
    if(fireBundle?.candidate_status==='PASS'&&fireBundle.runtime_eligible===true&&fireBundle.directions){
      const cell=Array.isArray(fireBundle.cell)?fireBundle.cell:[384,384];
      const root=Array.isArray(fireBundle.root)?fireBundle.root:[192,350];
      const height=Number.isFinite(fireBundle.height)?fireBundle.height:340;
      await Promise.all(Object.entries(fireBundle.directions).map(async([name,entry])=>{
        if(!entry?.upper||!entry.idleLower||!entry.moveLower)return;
        const [upper,idleLower,moveLower]=await Promise.all([loadTexture(entry.upper),loadTexture(entry.idleLower),loadTexture(entry.moveLower)]);
        this.fireModels[name]={upper,idleLower,moveLower,muzzle:entry.muzzle,cell,root,height,frames:fireBundle.frames||6,frameRate:fireBundle.frameRate||12};
      }));
    }
  }
  hasFullBody(direction){return !!this.fullBodyModels?.[direction];}
  fullBodyFrame(direction,pose){
    const model=this.fullBodyModels?.[direction];if(!model)return null;
    const moving=(Number(pose.amount)||0)>.055;
    // Pure locomotion uses the authored six-frame walk cycle.  Held-fire
    // keeps the already-reviewed full-body moving-fire family, while run
    // uses the same coherent walk source at a distinct higher cadence and
    // the simulation's independently measured run speed/stride.
    let action=moving?(pose.firing?'move':(pose.run?'run':'walk')):(pose.firing?'fire':'idle');
    if(!model[action])action=moving?'move':(pose.firing?'fire':'idle');
    const frames=model.frameCounts[action]||1,rate=model.frameRates[action]||12;
    let index=0;
    if(['walk','run','move'].includes(action))index=Math.floor((((Number(pose.phase)||0)%1+1)%1)*frames)%frames;
    else if(action==='idle')index=Math.floor(Math.max(0,Number(pose.time)||0)*rate)%frames;
    else {
      const recoil=Number(pose.recoil)||0;
      if(recoil>.72)index=2;
      else if(recoil>.32)index=3;
      else if(recoil>.10)index=4;
      else if(pose.firing)index=Math.floor(Math.max(0,Number(pose.time)||0)*rate)%2;
      else index=5;
      index=Math.min(index,frames-1);
    }
    return {model,action,index,frameCount:frames,texture:model[action].texture,im:model[action].im,muzzle:model.muzzle,root:model.root,cell:model.cell,artHeight:model.artHeight};
  }
  projectFullBodyPoint(direction,pose,point,x,y,height=230){
    const record=this.fullBodyFrame(direction,pose);if(!record||!Array.isArray(point))return null;
    const scale=height/record.artHeight;
    return [x+(point[0]-record.root[0])*scale,y+(point[1]-record.root[1])*scale];
  }
  begin(width,height){
    this.width=width;this.height=height;const gl=this.gl;
    gl.viewport(0,0,this.canvas.width,this.canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);
    gl.useProgram(this.program);gl.uniform2f(this.uResolution,width,height);
    gl.enable(gl.BLEND);gl.blendFuncSeparate(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA,gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
  }
  frame(direction,pose){
    const model=this.models[direction];if(!model)return null;
    const action=pose.amount<.06&&model.clips.idle?'idle':pose.run&&model.clips.run?'run':'walk';
    const {clip,texture,im}=model.clips[action];
    const phase=pose.amount<.06?0:pose.phase;
    return {model,clip,texture,im,index:phaseIndex(phase,clip.frames,clip.phaseStarts)};
  }
  hasFire(direction){return !!this.fireModels?.[direction];}
  fireFrame(direction,pose){
    const model=this.fireModels?.[direction];if(!model)return null;
    const fireRecoil=Number(pose.recoil)||0;
    let upperIndex=0;
    if(fireRecoil>.72)upperIndex=2;
    else if(fireRecoil>.32)upperIndex=3;
    else if(fireRecoil>.10)upperIndex=4;
    else if(pose.firing)upperIndex=Math.floor(Math.max(0,pose.time||0)*model.frameRate)%2;
    else upperIndex=5;
    const moving=(Number(pose.amount)||0)>.055;
    const lower=model[moving?'moveLower':'idleLower'];
    const lowerFrames=moving?24:4;
    const lowerPhase=moving?pose.phase:(Math.max(0,pose.time||0)*.25);
    const lowerIndex=Math.floor(((lowerPhase%1+1)%1)*lowerFrames)%lowerFrames;
    return {model,upper:model.upper,lower,upperIndex,lowerIndex,muzzle:model.muzzle,root:model.root,height:model.height,cell:model.cell,frames:model.frames};
  }
  projectFirePoint(direction,pose,point,x,y,height=230){
    const model=this.fireModels?.[direction];if(!model||!Array.isArray(point))return null;
    const scale=height/model.height;
    return [x+(point[0]-model.root[0])*scale,y+(point[1]-model.root[1])*scale];
  }
  drawFireLayer(layer,frame,x,y,height,root,cell){
    const {texture,im}=layer,gl=this.gl,scale=height/340,[cw,ch]=cell;
    const x0=x-root[0]*scale,y0=y-root[1]*scale,x1=x+(cw-root[0])*scale,y1=y+(ch-root[1])*scale;
    const row=Math.max(0,Math.min(Math.floor(im.height/ch)-1,frame));
    const positions=[x0,y0,x1,y0,x0,y1,x0,y1,x1,y0,x1,y1];
    const v0=(row*ch)/im.height,v1=((row+1)*ch)/im.height;
    const uv=[0,v0,1,v0,0,v1,0,v1,1,v0,1,v1];
    gl.bindBuffer(gl.ARRAY_BUFFER,this.positionBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(positions),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aPosition);gl.vertexAttribPointer(this.aPosition,2,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ARRAY_BUFFER,this.uvBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(uv),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aUv);gl.vertexAttribPointer(this.aUv,2,gl.FLOAT,false,0,0);
    gl.bindTexture(gl.TEXTURE_2D,texture);gl.uniform1f(this.uAlpha,1);gl.drawArrays(gl.TRIANGLES,0,6);
  }
  drawFire(direction,pose,x,y,height=230){
    const record=this.fireFrame(direction,pose);if(!record)return null;
    // The V2 ImageGen upper is composited over the existing V6 lower in one
    // 384px source coordinate system. It keeps the authored shoulder, hand,
    // rifle and muzzle together; no raster rotation or procedural body bend.
    this.drawFireLayer(record.lower,record.lowerIndex,x,y,height,record.root,record.cell);
    this.drawFireLayer(record.upper,record.upperIndex,x,y,height,record.root,record.cell);
    const muzzle=this.projectFirePoint(direction,pose,record.muzzle,x,y,height);
    return {muzzle,frame:record.upperIndex,frameCount:record.frames,lowerFrame:record.lowerIndex,fire:true,root:[x,y],direction,record};
  }
  drawFullBodyLayer(record,x,y,height){
    const {texture,im}=record,gl=this.gl,scale=height/record.artHeight,[cw,ch]=record.cell;
    const x0=x-record.root[0]*scale,y0=y-record.root[1]*scale,x1=x+(cw-record.root[0])*scale,y1=y+(ch-record.root[1])*scale;
    const row=Math.max(0,Math.min(Math.floor(im.height/ch)-1,record.index));
    const positions=[x0,y0,x1,y0,x0,y1,x0,y1,x1,y0,x1,y1];
    const v0=(row*ch)/im.height,v1=((row+1)*ch)/im.height;
    const uv=[0,v0,1,v0,0,v1,0,v1,1,v0,1,v1];
    gl.bindBuffer(gl.ARRAY_BUFFER,this.positionBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(positions),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aPosition);gl.vertexAttribPointer(this.aPosition,2,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ARRAY_BUFFER,this.uvBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(uv),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aUv);gl.vertexAttribPointer(this.aUv,2,gl.FLOAT,false,0,0);
    gl.bindTexture(gl.TEXTURE_2D,texture);gl.uniform1f(this.uAlpha,1);gl.drawArrays(gl.TRIANGLES,0,6);
  }
  drawFullBody(direction,pose,x,y,height=230){
    const record=this.fullBodyFrame(direction,pose);if(!record)return null;
    this.drawFullBodyLayer(record,x,y,height);
    const muzzle=this.projectFullBodyPoint(direction,pose,record.muzzle,x,y,height);
    return {muzzle,frame:record.index,frameCount:record.frameCount,clip:{frames:record.frameCount,height:record.artHeight,root:record.root,cell:record.cell,sources:[]},root:[x,y],direction,fullBody:true,action:record.action,fire:!!pose.firing,record};
  }
  projectPoint(clip,pose,point,x,y,height){
    const scale=height/clip.height;
    const waist=clip.waistY||clip.root[1]-clip.height*.5;
    const w=clamp((waist+35-point[1])/65,0,1);
    const q=w*w*(3-2*w);
    const angle=(pose.recoil*.04+pose.reload*.05)*Math.cos(pose.facing);
    const px=point[0]-clip.root[0],py=point[1]-waist;
    const rx=Math.cos(angle)*px-Math.sin(angle)*py,ry=Math.sin(angle)*px+Math.cos(angle)*py;
    const breath=Math.sin(pose.time*2.5)*1.1*(1-pose.amount);
    return [x+(point[0]-clip.root[0]+(rx-px-pose.recoil*6*Math.cos(pose.facing))*q)*scale,
      y+(point[1]-clip.root[1]+(ry-py+pose.reload*6-breath)*q)*scale];
  }
  draw(direction,pose,x,y,height=230){
    if(this.hasFullBody(direction))return this.drawFullBody(direction,pose,x,y,height);
    if(pose.firing&&this.hasFire(direction))return this.drawFire(direction,pose,x,y,height);
    const record=this.frame(direction,pose);if(!record)return null;
    const {model,clip,index,texture,im}=record,gl=this.gl,[cw,ch]=clip.cell;
    const col=index%clip.columns,row=Math.floor(index/clip.columns),positions=[],uv=[];
    const cols=8,rows=40;
    const vertex=(i,j)=>{
      const point=[i/cols*cw,j/rows*ch];positions.push(...this.projectPoint(clip,pose,point,x,y,height));
      uv.push((col*cw+point[0])/im.width,(row*ch+point[1])/im.height);
    };
    for(let j=0;j<rows;j++)for(let i=0;i<cols;i++){vertex(i,j);vertex(i+1,j);vertex(i,j+1);vertex(i+1,j);vertex(i+1,j+1);vertex(i,j+1);}
    gl.bindBuffer(gl.ARRAY_BUFFER,this.positionBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(positions),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aPosition);gl.vertexAttribPointer(this.aPosition,2,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ARRAY_BUFFER,this.uvBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(uv),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aUv);gl.vertexAttribPointer(this.aUv,2,gl.FLOAT,false,0,0);
    gl.bindTexture(gl.TEXTURE_2D,texture);gl.uniform1f(this.uAlpha,1);gl.drawArrays(gl.TRIANGLES,0,positions.length/2);
    const muzzle=model.view.muzzle||clip.muzzles[Math.floor(index/(clip.steps||1))];
    return {muzzle:this.projectPoint(clip,pose,muzzle,x,y,height),frame:index,frameCount:clip.frames,clip,root:[x,y],direction};
  }
}
