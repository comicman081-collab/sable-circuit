import {bindVertex,deformPoint,DIRECTIONS} from './motion.js';
export class CharacterRenderer{
 constructor(canvas){
  this.canvas=canvas;const gl=this.gl=canvas.getContext('webgl',{alpha:true,antialias:true,premultipliedAlpha:false,preserveDrawingBuffer:true});if(!gl)throw Error('WebGL을 사용할 수 없습니다.');
  const shader=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s};
  const p=this.program=gl.createProgram();gl.attachShader(p,shader(gl.VERTEX_SHADER,'attribute vec2 a_position;attribute vec2 a_uv;uniform vec2 u_resolution;varying vec2 v_uv;void main(){gl_Position=vec4(a_position/u_resolution*vec2(2.,-2.)+vec2(-1.,1.),0.,1.);v_uv=a_uv;}'));gl.attachShader(p,shader(gl.FRAGMENT_SHADER,'precision mediump float;uniform sampler2D u_image;uniform float u_opacity;uniform vec3 u_tint;varying vec2 v_uv;void main(){vec4 c=texture2D(u_image,v_uv);gl_FragColor=vec4(c.rgb*u_tint,c.a*u_opacity);}'));gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));
  this.pos=gl.getAttribLocation(p,'a_position');this.uv=gl.getAttribLocation(p,'a_uv');this.res=gl.getUniformLocation(p,'u_resolution');this.opacity=gl.getUniformLocation(p,'u_opacity');this.tint=gl.getUniformLocation(p,'u_tint');this.models={};
 }
 async load(profile){
  for(const dir of DIRECTIONS){const v=profile.views[dir];this.models[dir]=[];for(const layer of [1,2,3,0]){const im=new Image();im.src=v.layers?.[layer]||v.image;await im.decode();const gl=this.gl,texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,im);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
   const step=12,cols=Math.ceil(im.width/step),rows=Math.ceil(im.height/step),points=[],bindings=[],uvs=[],idx=[];
   for(let y=0;y<=rows;y++)for(let x=0;x<=cols;x++){const p=[x/cols*im.width,y/rows*im.height];points.push(p);bindings.push(bindVertex(v,p,layer));uvs.push(x/cols,y/rows);}
   for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){let i=y*(cols+1)+x;idx.push(i,i+1,i+cols+1,i+1,i+cols+2,i+cols+1);}
   const uvbuf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,uvbuf);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(uvs),gl.STATIC_DRAW);
   const ibuf=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ibuf);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(idx),gl.STATIC_DRAW);
   this.models[dir].push({v,texture,points,bindings,uvbuf,ibuf,posbuf:gl.createBuffer(),positions:new Float32Array(points.length*2),count:idx.length});
  }
  }
 }
 begin(width,height){const gl=this.gl;gl.viewport(0,0,this.canvas.width,this.canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.useProgram(this.program);gl.uniform2f(this.res,width,height);gl.enable(gl.BLEND);gl.blendFuncSeparate(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA,gl.ONE,gl.ONE_MINUS_SRC_ALPHA);}
 draw(direction,pose,x,y,height=230,{opacity=1,tint=[1,1,1]}={}){
  const gl=this.gl,scale=height/this.models[direction][0].v.height;for(const m of this.models[direction]){
  for(let i=0;i<m.points.length;i++){const p=deformPoint(m.points[i],m.bindings[i],pose);m.positions[i*2]=x+(p[0]-pose.root[0])*scale;m.positions[i*2+1]=y+(p[1]-pose.root[1])*scale;}
  gl.bindBuffer(gl.ARRAY_BUFFER,m.posbuf);gl.bufferData(gl.ARRAY_BUFFER,m.positions,gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(this.pos);gl.vertexAttribPointer(this.pos,2,gl.FLOAT,false,0,0);
  gl.bindBuffer(gl.ARRAY_BUFFER,m.uvbuf);gl.enableVertexAttribArray(this.uv);gl.vertexAttribPointer(this.uv,2,gl.FLOAT,false,0,0);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,m.ibuf);gl.bindTexture(gl.TEXTURE_2D,m.texture);gl.uniform1f(this.opacity,opacity);gl.uniform3fv(this.tint,tint);gl.drawElements(gl.TRIANGLES,m.count,gl.UNSIGNED_SHORT,0);
  }const project=p=>[x+(p[0]-pose.root[0])*scale,y+(p[1]-pose.root[1])*scale];return{muzzle:project(pose.muzzle),joints:pose.joints.map(chain=>chain.map(project)),feet:pose.feet.map(f=>({...f,ground:project(f.ground)}))};
 }
}
