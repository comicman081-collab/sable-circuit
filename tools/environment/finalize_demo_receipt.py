"""Record exact local demo implementation and existing intro-transcode provenance."""
from pathlib import Path
import hashlib, json, subprocess, sys
import av

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'qa/demo_20260920'
def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
paths=['project.godot','scripts/core/game_flow.gd','scripts/ui/title_screen.gd',
       'scripts/ui/demo_theme.gd','scripts/ui/demo_input.gd','scripts/ui/demo_controls.gd',
       'scripts/ui/demo_intro.gd','scripts/ui/base_lobby.gd','scripts/ui/story_stage_hud.gd',
       'scripts/ui/battle_reticle.gd','scripts/ui/briefing_screen.gd','scripts/ui/mission_results.gd',
       'scripts/actors/operator_actor.gd','scripts/actors/squad_controller.gd',
       'scripts/combat/operator_skill_controller.gd','scripts/missions/story_stage_01.gd',
       'tests/render/demo_integration_check.gd']
source=ROOT/'motion_lab_v1/cinematics/flow_intro_20260915/delivery_1080p/SABLE_CIRCUIT_INTRO_60s_1080p_SILENT.mp4'
movie=ROOT/'assets/cinematics/sable_intro.ogv'
with av.open(str(movie)) as media:
    stream=media.streams.video[0]
    movie_info={'codec':stream.codec_context.name,'resolution':[stream.width,stream.height],
                'duration_seconds':media.duration/av.time_base,'audio_streams':len(media.streams.audio),
                'frames_decoded':sum(1 for _ in media.decode(video=0))}
assert movie_info['frames_decoded']==1440 and movie_info['audio_streams']==0
captures=[OUT/(name+'.png') for name in ['title','intro','operations','touch_combat','manual']]
subprocess.run([sys.executable,str(ROOT/'tools/art_pipeline/validate_visual_evidence_1080p.py'),
                *map(str,captures),'--output',str(OUT/'visual_evidence.json')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
logs=['demo_flow','demo_progression','demo_sfx','demo_stage45','demo_persistence','demo_loadout','demo_intel','demo_input_matrix','demo_intro_complete']
log_results={}
for name in logs:
    path=ROOT/f'qa/karchive_props_20260919/{name}.stdout.log'
    text=path.read_text(encoding='utf-8')
    assert 'PASS' in text and not any(term in text for term in ['SCRIPT ERROR','Parse Error','ERROR:','FAIL']),name
    log_results[name]={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),
                       'summary':[line for line in text.splitlines() if 'PASS' in line][-1]}
receipt={'status':'LOCAL_NATIVE_DEMO_VERIFIED_NOT_DEPLOYED','source_hashes':{p:sha(ROOT/p) for p in paths},
         'intro':{**movie_info,'path':movie.relative_to(ROOT).as_posix(),'sha256':sha(movie),
                  'source':source.relative_to(ROOT).as_posix(),'source_sha256':sha(source),
                  'original_source_resolution':[1280,720],'watermark':'retained','new_generation':False},
         'captures':{p.name:sha(p) for p in captures},'checks':log_results,
         'browser_qa':'NOT_RUN','physical_touch_device':'NOT_RUN','deployment':'NOT_PERFORMED',
         'web_design_engineer':'SOFT_OFF_ROUTING_ONLY_NO_GLOBAL_CHANGE'}
(OUT/'completion.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print('LOCAL_DEMO_RECEIPT_PASS',movie_info)
