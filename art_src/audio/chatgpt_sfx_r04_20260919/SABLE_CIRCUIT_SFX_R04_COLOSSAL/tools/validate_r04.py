#!/usr/bin/env python3
"""File-level R04 validation. Does NOT certify artistic quality or engine integration."""
from __future__ import annotations
import argparse,hashlib,io,json,platform,subprocess,sys
from pathlib import Path
import numpy as np
import scipy
import soundfile as sf
from build_r04 import SR,SPEC,make,metric,tp

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(path):
 p=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','2','-ar',str(SR),'-f','f64le','-'],capture_output=True,check=True)
 return np.frombuffer(p.stdout,dtype='<f8').reshape(-1,2)
def video_hash(p):
 return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-']).decode().strip()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--video-dir',type=Path);ap.add_argument('--original-video',type=Path);a=ap.parse_args();r=a.root
 m=json.loads((r/'BANK_MANIFEST.json').read_text());prior=json.loads((r/'history/BANK_MANIFEST_R03.json').read_text());pmap={z['file']:z for z in prior['assets']}
 assets=m['assets'];assert len(assets)==120;assert len(list((r/'audio/wav').rglob('*.wav')))==120
 checked=[];changed=[];unchanged=[];hashes=[]
 for z in assets:
  p=r/z['file'];info=sf.info(p);x,sr=sf.read(p)
  assert sr==SR and info.channels==1 and info.subtype=='PCM_24',str(p)
  assert sha(p)==z['sha256'],str(p)
  st=metric(x);assert st['finite'] and st['clipped_samples']==0 and st['true_peak_dbfs_4x_est']<0
  same=sha(p)==pmap[z['file']]['sha256']
  (unchanged if same else changed).append(z['file']);hashes.append(sha(p))
  checked.append(dict(file=z['file'],sha256=sha(p),metrics=st))
 assert len(unchanged)==108 and len(changed)==12
 assert all(next(z['cue'] for z in assets if z['file']==f) in SPEC for f in changed)
 assert len(set(hashes))==120
 extra=json.loads((r/'extras/STEREO_MANIFEST.json').read_text());assert len(extra)==12
 folds=[]
 for z in extra:
  p=r/z['file'];x,sr=sf.read(p);i=sf.info(p);assert sr==SR and i.channels==2 and i.subtype=='PCM_24' and sha(p)==z['sha256']
  st=metric(x);assert st['finite'] and st['clipped_samples']==0 and st['true_peak_dbfs_4x_est']<0
  az=next(q for q in assets if q['cue']==z['cue'] and q['variant']==z['variant']);mono,_=sf.read(r/az['file'])
  err=float(np.max(abs(x.mean(axis=1)-mono)));assert err<=2**-23
  folds.append(dict(file=z['file'],mono_fold_max_abs_error=err,metrics=st))
 source=decode(r/'sources/explode_large.opus')
 repro=[]
 for z in assets:
  if z['cue'] not in SPEC:continue
  mono,stereo,recipe=make(z['cue'],z['variant'],source)
  for x,rel in [(mono,z['file']),(stereo,z['stereo_alternate'])]:
   b=io.BytesIO();sf.write(b,x,SR,format='WAV',subtype='PCM_24');h=hashlib.sha256(b.getvalue()).hexdigest();assert h==sha(r/rel),rel
   repro.append(dict(file=rel,byte_identical=True))
 lossy=[]
 for p in sorted((r/'previews').glob('*.mp3')):
  x=decode(p);st=metric(x);assert st['finite'] and st['clipped_samples']==0 and st['true_peak_dbfs_4x_est']<0
  lossy.append(dict(file=str(p.relative_to(r)),metrics=st))
 vid=[]
 if a.video_dir:
  for duration in [10,17]:
   p=a.video_dir/f'SABLE_CIRCUIT_COMBAT_SFX_R04_COLOSSAL_{duration}s.mp4'
   data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
   v=next(s for s in data['streams'] if s['codec_type']=='video');au=next(s for s in data['streams'] if s['codec_type']=='audio')
   assert v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='60/1' and int(v['nb_frames'])==duration*60
   assert int(au['sample_rate'])==SR and int(au['channels'])==2
   subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],capture_output=True,check=True)
   x=decode(p);st=metric(x);assert st['finite'] and st['clipped_samples']==0 and st['true_peak_dbfs_4x_est']<0
   item=dict(file=p.name,duration_s=float(data['format']['duration']),frames=int(v['nb_frames']),full_decode_ok=True,audio=st,sha256=sha(p))
   if duration==10 and a.original_video:
    h=video_hash(a.original_video);actual=video_hash(p);assert actual==h;item.update(video_stream_identical=True,original_video_stream_hash=h,new_video_stream_hash=actual)
   vid.append(item)
 t=json.loads((r/'previews/COMBAT_TIMELINE_R04.json').read_text());old=json.loads((r/'tools/COMBAT_EVENTS_PREVIOUS.json').read_text());assert t['master_linear_gain']==old['master_linear_gain']
 event_differences=[]
 for x,y in zip(old['events'],t['events']):
  if x['at_s']!=y['at_s']:event_differences.append(dict(cue=y['cue'],from_s=x['at_s'],to_s=y['at_s']))
 assert len(event_differences)==1 and event_differences[0]==dict(cue='boss_cross_beam',from_s=9.56,to_s=9.7)
 sm=json.loads((r/'sources/SOURCE_MANIFEST.json').read_text());source_checks=[]
 for x in sm['used']:
  p=r/x['file'];raw=p.read_bytes();assert sha(p)==x['sha256'];assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==x['git_blob_sha1']
  source_checks.append(dict(file=x['file'],sha256=sha(p),git_blob_matches=True))
 report=dict(revision='R04_COLOSSAL',technical_status='PASS',scope='File integrity, decode, waveform headroom, exact preservation and same-runtime deterministic rebuild ONLY',
  artistic_status='USER_AUDITION_PENDING',game_engine_integration='NOT_RUN',headphone_or_phone_listening_test='NOT_PERFORMED',
  bank_wav_count=120,changed_count=12,unchanged_count=108,stereo_alternates=12,unique_bank_hashes=120,
  previous_revision='R03_HEAVY_BLAST',unchanged_files=unchanged,changed_files=changed,game_assets=checked,
  stereo_checks=folds,same_runtime_rebuild=repro,source_integrity=source_checks,lossy_previews=lossy,videos=vid,
  event_timing_changes=event_differences,master_linear_gain=t['master_linear_gain'],other_sfx_duck=t['other_sfx_duck'],
  environment=dict(python=sys.version,platform=platform.platform(),numpy=np.__version__,scipy=scipy.__version__,soundfile=sf.__version__,ffmpeg=subprocess.check_output(['ffmpeg','-version']).decode().splitlines()[0]))
 (r/'validation/R04_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({k:report[k] for k in ['technical_status','artistic_status','game_engine_integration','bank_wav_count','changed_count','unchanged_count','stereo_alternates','unique_bank_hashes']},ensure_ascii=False,indent=2));print('Video audio peaks:',[(x['file'],x['audio']['true_peak_dbfs_4x_est']) for x in vid])
if __name__=='__main__':main()
