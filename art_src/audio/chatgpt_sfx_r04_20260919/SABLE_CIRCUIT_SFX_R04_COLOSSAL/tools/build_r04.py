#!/usr/bin/env python3
"""R04: replace 12 blast/stomp/collapse WAVs; keep the other 108 intact.
The bundled licensed explosion is a lossy stock source, NOT a new field recording.
Deterministic sample layering, dynamic shaping, granular diffuse decay, no oscillator.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy import signal, ndimage
SR=48000
SPEC={
 'boss_cross_beam':dict(duration=6.4,rate=.57,decay=1.35,tail=1.65,peak=-3.5,label='보스 스킬 · 초대형 폭압 / 넓게 구르는 잔향'),
 'boss_stomp':dict(duration=4.0,rate=.72,decay=.66,tail=.90,peak=-5.5,label='보스 착지 · 거대한 지면 충격 / 구조물 진동'),
 'boss_destroy':dict(duration=7.0,rate=.49,decay=1.72,tail=1.95,peak=-3.5,label='보스 붕괴 · 대형 연쇄 붕괴 / 두꺼운 폭압'),
}

def band(x,lo=None,hi=None,order=3):
 if lo and hi:sos=signal.butter(order,[lo,hi],btype='bandpass',fs=SR,output='sos')
 elif lo:sos=signal.butter(order,lo,btype='highpass',fs=SR,output='sos')
 else:sos=signal.butter(order,hi,btype='lowpass',fs=SR,output='sos')
 return signal.sosfilt(sos,x,axis=0)

def fade(x,attack=.003,release=.12):
 x=x.copy();a=min(len(x),round(attack*SR));b=min(len(x),round(release*SR))
 if a:x[:a]*=np.sin(np.linspace(0,np.pi/2,a))**2
 if b:x[-b:]*=np.cos(np.linspace(0,np.pi/2,b))**2
 return x

def size(x,n):
 out=np.zeros(n);out[:min(n,len(x))]=x[:n];return out

def rms(x):return float(np.sqrt(np.mean(np.square(x))))

def unit(x,start=.025,end=.7):
 s=x[round(start*SR):min(len(x),round(end*SR))]
 return x/max(rms(s),1e-9)

def rate(x,r):
 return signal.resample_poly(x,1000,round(1000*r),axis=0)

def place(y,x,at,gain=1):
 k=round(at*SR);n=min(len(y)-k,len(x))
 if k>=0 and n>0:y[k:k+n]+=x[:n]*gain

def density(x,power=.5,maxgain=4):
 # Increase the sample's body relative to its isolated peaks with smooth gain.
 env=np.sqrt(np.maximum(ndimage.uniform_filter1d(x*x,round(.024*SR)),1e-12))
 ref=np.percentile(env[:min(len(x),SR)],72)
 g=np.minimum((max(ref,1e-8)/env)**power,maxgain)
 g=ndimage.gaussian_filter1d(g,round(.006*SR))
 return x*g

def texture(source,n,rg,lo,hi,grain_s=.26):
 """Crossfaded source-tail grains, no repeated explosive onset and no clicks."""
 grain=round(grain_s*SR);hop=round(grain*.29);out=np.zeros(n+grain);weight=np.zeros(n+grain)
 src=band(source,lo,hi);first=round(.22*SR);last=len(src)-grain-1
 win=np.sin(np.linspace(0,np.pi,grain))**2
 for k in range(-grain+hop,n,hop):
  start=int(rg.integers(first,max(first+1,last)))
  seg=src[start:start+grain].copy()
  if len(seg)<grain:seg=np.pad(seg,(0,grain-len(seg)))
  seg/=max(rms(seg),1e-7)
  seg*=win; a=max(0,k);b=min(len(out),k+grain);off=a-k
  out[a:b]+=seg[off:off+b-a];weight[a:b]+=win[off:off+b-a]
 out=out[:n]/np.maximum(weight[:n],.1)
 return unit(out,0,min(1,n/SR))

def reverberate(x,n,rg,decay):
 """Aperiodic, damped noise IR. This is designed ambience, not measured acoustics."""
 irn=round(min(n/SR,3.7)*SR);t=np.arange(irn)/SR
 ir=band(rg.normal(size=irn),110,1800)
 ir*=np.exp(-t/decay)*(1-np.exp(-t/.045))
 ir[:round(.032*SR)]=0
 ir/=max(np.sqrt(np.sum(ir*ir)),1e-12)
 out=signal.fftconvolve(band(x,105,2800),ir)[:n]
 return unit(out,.10,.95)

def tame(x):
 # Smooth peak gain rather than waveform clipping. Shared control for L/R.
 p=ndimage.maximum_filter1d(np.max(np.abs(x),axis=1),round(.006*SR)|1)
 g=np.minimum(1,3.6/np.maximum(p,1e-9))
 g=ndimage.minimum_filter1d(g,round(.004*SR)|1)
 g=ndimage.uniform_filter1d(g,round(.003*SR)|1)
 return x*g[:,None]

def tp(x):return float(np.max(np.abs(signal.resample_poly(x,4,1,axis=0))))

def metric(x):
 mono=x.mean(axis=1) if x.ndim==2 else x
 peak=float(np.max(abs(x)));energy=mono*mono;total=float(energy.sum());cum=np.cumsum(energy)/max(total,1e-15)
 return dict(duration_s=len(x)/SR,peak_dbfs=20*np.log10(max(peak,1e-12)),
  true_peak_dbfs_4x_est=20*np.log10(max(tp(x),1e-12)),rms_dbfs=20*np.log10(max(rms(x),1e-12)),
  first_800ms_rms_dbfs=20*np.log10(max(rms(x[:round(.8*SR)]),1e-12)),
  energy_95_s=float(np.searchsorted(cum,.95)/SR),energy_99_s=float(np.searchsorted(cum,.99)/SR),
  clipped_samples=int((abs(x)>=1).sum()),dc_offset=float(np.mean(x)),finite=bool(np.isfinite(x).all()))

def make(cue,variant,src):
 spec=SPEC[cue];n=round(spec['duration']*SR);t=np.arange(n)/SR
 seed=int.from_bytes(hashlib.sha256(f'SC_R04_{cue}_{variant}'.encode()).digest()[:8],'little')
 rg=np.random.default_rng(seed)
 sm=src.mean(axis=1)
 r=spec['rate']*rg.uniform(.972,1.028)
 slow=rate(sm,r)
 # Full-bodied blast from the licensed stock waveform, fixed-rate, never a pitch sweep.
 body=unit(density(band(slow,38,2450),.50,3.3),.025,.80)
 body=size(body,n)*(1-np.exp(-t/.004))*np.exp(-t/spec['decay'])
 # A distinct but restrained air crack; it must not dwarf the body.
 crack=rate(sm,.87+variant*.018)
 crack=unit(band(crack,550,6900),.002,.13)
 crack=size(crack,n)*np.exp(-t/.046)
 # Large, non-tonal pressure movement: source-derived, not a sine-wave kick.
 bass=rate(sm,.44+variant*.008)
 bass=unit(density(band(bass,28,150),.65,3.5),.03,.80)
 bass=size(bass,n)*(1-np.exp(-t/.016))*np.exp(-t/(spec['decay']*.90))
 lowmid=texture(sm,n,rg,115,640,.32)
 variation=np.interp(t,np.linspace(0,spec['duration'],21),rg.uniform(.75,1.16,21))
 lowmid*=(1-np.exp(-t/.020))*np.exp(-t/(spec['decay']*.80))*variation
 dry=body*.62+crack*.11+bass*.57+lowmid*.30
 # Avoid a single thin pop followed by near-silence: retain irregular material rumble.
 rumbles=[]
 for c in range(2):
  tex=texture(src[:,c],n,rg,65,1150,.38)
  env=(1-np.exp(-t/.09))*np.exp(-t/spec['tail'])
  undulation=np.interp(t,np.linspace(0,spec['duration'],29),rg.uniform(.68,1.2,29))
  rumbles.append(tex*env*undulation)
 if cue=='boss_destroy':
  for at,g in [(.31,.23),(.78,.15),(1.31,.085)]:
   sec=unit(band(rate(sm,r*rg.uniform(.91,1.10)),40,950),.035,.50)
   sec*=np.exp(-np.arange(len(sec))/SR/.56)
   place(dry,fade(sec,.035,.15),at,g)
 late=[reverberate(body,n,rg,.51 if cue=='boss_stomp' else .80) for _ in range(2)]
 wet=.13 if cue=='boss_stomp' else .21
 # Common dry bass stays central; only the spatial body/decay has side energy.
 stereo=np.column_stack([dry+rumbles[c]*.29+late[c]*wet for c in range(2)])
 mid=stereo.mean(axis=1);side=band((stereo[:,0]-stereo[:,1])*.5,125,None)*1.0
 stereo=np.column_stack([mid+side,mid-side])
 stereo=tame(stereo)
 for c in range(2):stereo[:,c]=fade(band(stereo[:,c],25,10500),.0018,.48)
 peak=tp(stereo);gain=10**(spec['peak']/20)/max(peak,1e-12);stereo*=gain
 stereo[0]=0;stereo[-1]=0
 mono=stereo.mean(axis=1)
 recipe=dict(revision='R04',seed=str(seed),source_ids=['explode_large'],
  method='fixed-rate source layers + body density shaping + source-tail granular rumble + nonperiodic stereo diffusion',
  source_rate=r,new_field_recording=False,new_external_audio_download_used=False,
  tonal_oscillators=False,pitch_sweeps=False,metal_click_layers=False,hard_clipping=False,
  stereo_bass_below_125_hz='centered',master_linear_gain=gain,target_stereo_true_peak_dbfs=spec['peak'],
  license='CC-BY-3.0; modified Michel Baradari explosion source; attribution required')
 return mono,stereo,recipe

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);r=ap.parse_args().root.resolve()
 p=r/'sources/explode_large.opus';raw=p.read_bytes()
 assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()=='151e5ef229830524ead6de285c753f5b59f2f99c'
 result=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','f64le','-ac','2','-ar',str(SR),'-'],capture_output=True,check=True)
 src=np.frombuffer(result.stdout,dtype='<f8').reshape(-1,2).copy()
 m=json.loads((r/'BANK_MANIFEST.json').read_text());changed=[];extra=[]
 baseline={a['file']:a['sha256'] for a in json.loads((r/'history/BANK_MANIFEST_R03.json').read_text())['assets']}
 for a in m['assets']:
  if a['cue'] not in SPEC:continue
  mono,stereo,recipe=make(a['cue'],a['variant'],src);dst=r/a['file'];old=baseline[a['file']]
  sf.write(dst,mono,SR,subtype='PCM_24');mono,_=sf.read(dst)
  st=r/'extras/stereo_boss'/dst.name;sf.write(st,stereo,SR,subtype='PCM_24');stereo,_=sf.read(st)
  a.update(label_ko=SPEC[a['cue']]['label'],sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),bytes=dst.stat().st_size,metrics=metric(mono),recipe=recipe)
  a['stereo_alternate']=str(st.relative_to(r))
  changed.append(dict(file=a['file'],cue=a['cue'],variant=a['variant'],previous_sha256=old,sha256=a['sha256']))
  extra.append(dict(file=str(st.relative_to(r)),cue=a['cue'],variant=a['variant'],sha256=hashlib.sha256(st.read_bytes()).hexdigest(),metrics=metric(stereo)))
  print(a['cue'],a['variant'],'first0.8',round(a['metrics']['first_800ms_rms_dbfs'],2),'99%',a['metrics']['energy_99_s'],flush=True)
 m.update(bank='SABLE CIRCUIT — R04 COLOSSAL',version='SC-R04-Colossal-1.0',revision='R04_COLOSSAL',
  perceptual_status='USER_AUDITION_PENDING',technical_status='SEE validation/R04_VALIDATION.json',
  changes='12 blast/stomp/collapse WAVs rebuilt; other 108 R03 WAVs byte-preserved; 12 optional stereo alternates',
  notes_ko=['폭발 본체 및 잔향 재설계. 기존 폭발 소스를 가공한 사운드 디자인이며 신규 실녹음이 아님.',
   '게임용 기본 120개는 모노. 보스 폭발 12개만 별도 스테레오 대안 제공.',
   '기술 검사와 별개로 사용자의 음색/적합도 승인이 필요함. 게임 엔진 통합은 실행하지 않음.'])
 (r/'BANK_MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
 (r/'extras/STEREO_MANIFEST.json').write_text(json.dumps(extra,ensure_ascii=False,indent=2))
 (r/'validation/CHANGED_ASSETS_R04.json').write_text(json.dumps(changed,ensure_ascii=False,indent=2))
 cm=json.loads((r/'CUE_MAP.json').read_text());cm['bank_revision']='R04_COLOSSAL'
 for c in cm['cues']:
  if c['id'] in SPEC:
   c.update(label_ko=SPEC[c['id']]['label'],runtime_pitch_range=[1.,1.],tail_policy='Let decay continue after attack animation. Do not stop/retrigger same voice on pose changes.',license='CC-BY-3.0 attribution required')
 (r/'CUE_MAP.json').write_text(json.dumps(cm,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
