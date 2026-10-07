#!/usr/bin/env python3
"""Render the supplied 10 s combat timeline with the new blast at frame 582.
No game engine is run. Only the final blast event moves (9.56 -> 9.70 s).
"""
from __future__ import annotations
import argparse,json,subprocess,hashlib
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy import signal
from build_r04 import SR,metric,tp
CREDIT='Explosion source: 2 High Quality Explosions (explode), Michel Baradari, CC BY 3.0; modified. https://opengameart.org/content/2-high-quality-explosions ; https://creativecommons.org/licenses/by/3.0/'
def run(*args):subprocess.run(list(args),check=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=ap.parse_args();r=a.root
 out=r/'previews';out.mkdir(exist_ok=True)
 m=json.loads((r/'BANK_MANIFEST.json').read_text());bank={(z['cue'],z['variant']):sf.read(r/z['file'])[0] for z in m['assets']}
 stereo={(z['cue'],z['variant']):sf.read(r/z['stereo_alternate'])[0] for z in m['assets'] if 'stereo_alternate' in z}
 timeline=json.loads((r/'tools/COMBAT_EVENTS_PREVIOUS.json').read_text());master=timeline['master_linear_gain'];events=timeline['events']
 for e in events:
  if e['cue']=='boss_cross_beam':
   e.update(at_s=9.70,previous_at_s=9.56,reason='Frame inspection: white cross attack starts at frame 582/60 = 9.70 seconds',use_stereo_alternate=True)
 n=17*SR;regular=np.zeros((n,2));boss=np.zeros_like(regular)
 def add(dst,x,at):
  k=round(at*SR);ln=min(len(x),len(dst)-k)
  if k>=0 and ln>0:dst[k:k+ln]+=x[:ln]
 for e in events:
  key=e['cue'],e['variant'];pan=np.clip(e.get('pan',0),-1,1);ang=(pan+1)*np.pi/4
  if e.get('use_stereo_alternate'):
   x=stereo[key]*np.array([np.cos(ang),np.sin(ang)])*np.sqrt(2)*e['gain_linear'];add(boss,x,e['at_s'])
  else:
   mono=bank[key];x=np.column_stack([mono*np.cos(ang),mono*np.sin(ang)])*e['gain_linear'];add(regular,x,e['at_s'])
   room=e.get('room',0)
   if room:
    soft=signal.sosfilt(signal.butter(2,4300,fs=SR,output='sos'),x,axis=0)
    for delay,gain in [(.026,.14),(.057,.09),(.103,.045)]:add(regular,soft[:,::-1]*gain*room,e['at_s']+delay)
 t=np.arange(n)/SR
 # Only the final impact window is ducked; the rest of the mix retains its old gain.
 shape=np.interp(t,[0,9.66,9.70,10.12,11.0,17],[0,0,1,1,0,0]);duck=10**(-8*shape/20)
 mixed=(regular*duck[:,None]+boss)*master
 mixed[:960]*=np.linspace(0,1,960)[:,None];mixed[-960:]*=np.linspace(1,0,960)[:,None]
 assert tp(mixed)<.94,('Mix exceeds headroom',tp(mixed))
 reports=[]
 def write(stem,x):
  p=out/(stem+'.wav');sf.write(p,x,SR,subtype='PCM_24');y,_=sf.read(p)
  run('ffmpeg','-y','-v','error','-i',str(p),'-c:a','libmp3lame','-b:a','256k','-metadata','comment='+CREDIT,str(out/(stem+'.mp3')))
  reports.append(dict(file=str(p.relative_to(r)),metrics=metric(y)))
  return p
 write('COMBAT_R04_COLOSSAL_17s',mixed)
 x10=mixed[:10*SR].copy();x10[-480:]*=np.linspace(1,0,480)[:,None]
 write('COMBAT_R04_COLOSSAL_10s',x10)
 solo=stereo['boss_cross_beam',2];s=np.zeros((7*SR,2));s[12000:12000+len(solo)]=solo
 write('BOSS_BLAST_R04_7s',s)
 montage=np.zeros((20*SR,2))
 for cue,at in [('boss_cross_beam',.25),('boss_stomp',7.35),('boss_destroy',12.1)]:
  x=stereo[cue,2];k=round(at*SR);montage[k:k+len(x)]+=x
 write('BOSS_SCALE_REEL_R04_20s',montage)
 # A/B has equal true peak, not equal integrated loudness; decay is part of the change.
 prior=r/'history/BANK_MANIFEST_R03.json';old=json.loads(prior.read_text())
 baseline=r/'history'
 olda=next(z for z in old['assets'] if z['cue']=='boss_cross_beam' and z['variant']==2)
 if (baseline/'R03_boss_cross_beam_v02.wav').exists():
  x,_=sf.read(baseline/'R03_boss_cross_beam_v02.wav');x=np.column_stack([x,x]);x*=tp(solo)/tp(x)
  ab=np.zeros((12*SR,2));ab[12000:12000+len(x)]=x;ab[round(4.5*SR):round(4.5*SR)+len(solo)]=solo
  write('R03_THEN_R04_EQUAL_PEAK_AB_12s',ab)
 sf.write(out/'NON_BOSS_STEM_R04.wav',regular*duck[:,None]*master,SR,subtype='PCM_24')
 sf.write(out/'BOSS_ONLY_STEM_R04.wav',boss*master,SR,subtype='PCM_24')
 timeline.update(revision='R04_COLOSSAL',duration_s=17,master_gain_unchanged=True,
  boss_stereo_used=True,other_sfx_duck=dict(start_s=9.66,full_s=9.70,hold_until_s=10.12,end_s=11.,max_reduction_db=8),
  type='POSTPRODUCTION_DEMO_NOT_ENGINE_CAPTURE',freeze_frame_extension_s=7)
 (out/'COMBAT_TIMELINE_R04.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2))
 (r/'validation/R04_PREVIEW_AUDIO.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
 print(json.dumps(reports,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
