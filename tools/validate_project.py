#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
required_files = [
    'project.godot','README.md','.gitignore','.gitattributes',
    '.github/workflows/validate.yml',
    'assets/external/manifest.json','schemas/repository_layout.json',
    'scenes/bootstrap/Bootstrap.tscn','scripts/core/bootstrap.gd',
    'docs/GDD_v0.1.md','docs/TECH_ARCHITECTURE_v0.1.md','docs/ANIMATION_SPEC_v0.1.md',
    'docs/FOLDER_STRUCTURE.md','docs/GITHUB_ACTIONS_POLICY.md','docs/VALIDATION_REPORT.md','docs/TITLE_AND_REPO.md',
    'scenes/mission/PrototypeArena.tscn','scenes/actors/player/OperatorActor.tscn',
    'scenes/actors/enemy/TargetDummy.tscn','scripts/actors/operator_actor.gd',
    'scripts/actors/squad_controller.gd','scripts/actors/target_dummy.gd',
    'scripts/animation/operator_visual.gd','scripts/combat/prototype_projectile.gd',
    'scripts/missions/prototype_arena.gd','scripts/ui/prototype_hud.gd',
    'tests/smoke/prototype_smoke.gd','docs/M1_PLAYABLE_SQUAD_PROTOTYPE.md',
    'scenes/bootstrap/GameFlow.tscn','scripts/core/game_flow.gd',
    'scenes/ui/TitleScreen.tscn','scripts/ui/title_screen.gd',
    'scenes/base/BaseLobby.tscn','scripts/ui/base_lobby.gd',
    'scenes/story/BriefingScreen.tscn','scripts/ui/briefing_screen.gd',
    'scenes/mission/StoryStage01.tscn','scripts/missions/story_stage_01.gd',
    'scripts/ui/story_stage_hud.gd','scenes/ui/MissionResults.tscn','scripts/ui/mission_results.gd',
    'data/story/chapter_01.json','data/missions/MIS_CH01_01.json',
    'tests/smoke/m2_story_flow_smoke.gd','docs/M2_STORY_VERTICAL_SLICE.md'
]
errors=[]
for f in required_files:
    if not (ROOT/f).is_file():
        errors.append(f'missing required file: {f}')

layout_path=ROOT/'schemas/repository_layout.json'
if layout_path.exists():
    try:
        layout=json.loads(layout_path.read_text(encoding='utf-8'))
        dirs=layout.get('directories')
        if layout.get('schema_version') != 1: errors.append('repository layout schema_version must be 1')
        if layout.get('project_root') != 'repository-root': errors.append('project_root must be repository-root')
        if not isinstance(dirs, list) or not dirs: errors.append('repository layout directories must be a non-empty list')
        else:
            if len(dirs) != len(set(dirs)): errors.append('repository layout contains duplicate directory entries')
            for d in dirs:
                if not isinstance(d, str) or d.startswith('/') or '..' in Path(d).parts:
                    errors.append(f'invalid repository layout directory: {d!r}')
            for required_dir in ('data/story','data/missions','scenes/base','scenes/story','scenes/mission','scenes/ui'):
                if required_dir not in dirs:
                    errors.append(f'repository layout missing M2 directory: {required_dir}')
        if 'game' not in layout.get('forbidden_roots', []): errors.append('repository layout must forbid game/ root wrapper')
    except Exception as e:
        errors.append(f'repository layout parse error: {e}')

project_text=(ROOT/'project.godot').read_text(encoding='utf-8') if (ROOT/'project.godot').exists() else ''
if 'run/main_scene="res://scenes/bootstrap/Bootstrap.tscn"' not in project_text:
    errors.append('project.godot must point to Bootstrap.tscn')
if (ROOT/'game').exists():
    errors.append('forbidden root wrapper: game/')

mp=ROOT/'assets/external/manifest.json'
if mp.exists():
    try:
        data=json.loads(mp.read_text(encoding='utf-8'))
        if data.get('schema_version') != 1: errors.append('external manifest schema_version must be 1')
        if not isinstance(data.get('assets'), list): errors.append('external manifest assets must be a list')
        else:
            ids=set()
            for i,a in enumerate(data['assets']):
                for k in ('id','name','origin','version','license','destination','sha256'):
                    if k not in a: errors.append(f'external asset[{i}] missing {k}')
                if 'id' in a:
                    if a['id'] in ids: errors.append(f'duplicate external asset id: {a["id"]}')
                    ids.add(a['id'])
                sha=a.get('sha256','')
                if sha and not re.fullmatch(r'[0-9a-fA-F]{64}', sha): errors.append(f'invalid sha256 for external asset[{i}]')
    except Exception as e:
        errors.append(f'external manifest parse error: {e}')

wfdir=ROOT/'.github/workflows'
if wfdir.exists():
    for p in wfdir.glob('*.y*ml'):
        text=p.read_text(encoding='utf-8', errors='replace').lower()
        if 'actions/deploy-pages' in text or 'pages: write' in text or 'github-pages' in text:
            errors.append(f'pages deployment is forbidden in pre-production: {p.relative_to(ROOT)}')

prototype_contracts = {
    'scripts/animation/operator_visual.gd': ['Skeleton2D.new()', 'Bone2D.new()', 'AnimationPlayer.new()', 'AnimationTree.new()', 'muzzle_socket'],
    'scripts/actors/operator_actor.gd': ['CharacterBody2D', 'move_and_slide()', 'debug_fire_once', '_sector_from_vector', 'set_movement_bounds'],
    'scripts/actors/squad_controller.gd': ['request_control', '_update_formation', 'operators'],
    'tests/smoke/prototype_smoke.gd': ['PROTOTYPE_SMOKE: PASS', 'get_bone_count()', 'debug_fire_once'],
    'scripts/core/game_flow.gd': ['show_title', 'enter_base', 'open_briefing', 'deploy_stage_01', 'show_results'],
    'scripts/missions/story_stage_01.gd': ['_spawn_combat', '_apply_progress_bounds', '_finish_mission', 'stage_completed'],
    'tests/smoke/m2_story_flow_smoke.gd': ['M2_STORY_FLOW_SMOKE: PASS', 'game boots to title', 'result debrief returns to operations base'],
}
for rel, needles in prototype_contracts.items():
    path=ROOT/rel
    if not path.exists():
        continue
    text=path.read_text(encoding='utf-8')
    for needle in needles:
        if needle not in text:
            errors.append(f'{rel} missing milestone contract token: {needle}')

story_path=ROOT/'data/story/chapter_01.json'
if story_path.exists():
    try:
        story=json.loads(story_path.read_text(encoding='utf-8'))
        if story.get('chapter_id') != 'CH01': errors.append('chapter_01 chapter_id must be CH01')
        if story.get('title') != 'BLACKOUT AT SITE-7': errors.append('chapter_01 title contract changed')
        if not isinstance(story.get('briefing'), list) or len(story.get('briefing', [])) < 4:
            errors.append('chapter_01 briefing must contain at least 4 authored lines')
    except Exception as e:
        errors.append(f'chapter_01 parse error: {e}')

mission_path=ROOT/'data/missions/MIS_CH01_01.json'
if mission_path.exists():
    try:
        mission=json.loads(mission_path.read_text(encoding='utf-8'))
        route=mission.get('main_route', [])
        optional=mission.get('optional_rooms', [])
        expected_types=['EVENT','COMBAT','RESEARCH','ELITE','BOSS','EXTRACTION']
        if mission.get('mission_id') != 'MIS_CH01_01': errors.append('M2 mission_id must be MIS_CH01_01')
        if [room.get('type') for room in route] != expected_types:
            errors.append('M2 main route must preserve authored EVENT→COMBAT→RESEARCH→ELITE→BOSS→EXTRACTION order')
        ids=[room.get('id') for room in route] + [room.get('id') for room in optional]
        if len(ids) != len(set(ids)): errors.append('M2 mission room IDs must be unique')
        if len(optional) != 2: errors.append('M2 mission must have exactly 2 optional rooms')
    except Exception as e:
        errors.append(f'MIS_CH01_01 parse error: {e}')

if errors:
    print('VALIDATION: FAIL')
    for e in errors: print(' -', e)
    sys.exit(1)
print('VALIDATION: PASS')
print(f'checked {len(required_files)} required files, repository policy, M1 combat contracts, and M2 story-flow contracts')
