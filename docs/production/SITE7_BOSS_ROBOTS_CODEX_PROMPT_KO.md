# SITE-7 새 보스 로봇 2종과 보스별 공격 패턴 — Codex 작업 지시서

사용자 지시(2026-09-28): 새 보스 로봇을 만든다. 작전이 반복되는 느낌을 없애는 작업의 일부다(`AGENTS.md` "Mission styles and route structure").

## 0. 판정: 보스는 그림도 싸움도 반복된다

- 작전 1·2·3이 같은 보스 `BOSS_SITE7_ANCHOR_01`을 쓴다. 체력만 620 → 710 → 820으로 오른다.
- 보스 5종 모두 공격 코드가 하나다. `scripts/combat/site7_enemy_tactics.gd` `_boss_attack`:
  - 1페이즈: 3발 부채꼴
  - 2페이즈: 짝수 공격마다 원형 경고, 아니면 5발 부채꼴
  - 3페이즈: 십자 레인 4개 추가
  - FORGE와 CARRIER도 그림, 체력, 투사체 색만 다르다.
- 보스방 연출도 같다.
  - `scripts/missions/boss_arena_presentation.gd:47`: 모든 보스에 같은 보라 단상과 기둥을 둔다.
  - `scripts/missions/story_stage_01.gd:488`: 모든 보스에 같은 안내문("Central iris active…")을 띄운다.
- 보스 그림 셋 중 둘이 둥근 홍채 계열이다(ANCHOR 중앙 아이리스, FORGE 청록 용광로 아이리스).
- 그래서 이번 작업은 두 가지다.
  1. 작전 2·3에 새 보스 2종을 만든다. 작전 1은 ANCHOR를 그대로 쓴다.
  2. 보스 5종이 각자 다른 공격 패턴, 보스방 강조색, 안내문을 갖게 한다. ANCHOR의 공격은 지금 그대로 둔다.

---

## 1. 반드시 지킬 규칙

- `AGENTS.md`의 적 규칙을 따른다.
  - 사람형 적은 0이다. 다리, 발, 무릎, 손 달린 팔, 머리·얼굴, 궤도·바퀴가 없다.
  - 보스는 고정 기계(`anchored_machine`)다. 그림 한 장, 고정된 뿌리, 보이는 방출구 하나다.
  - 방출구는 어느 방향에서 봐도 같은 것이어야 한다(꼭대기의 노드나 갈퀴). 한쪽을 향한 포신은 안 된다. 그림 한 장을 전방향으로 쓰기 때문이다(`references/enemy-facing.md`, ANCHOR 선례).
  - 로봇 그림에 색을 입히지 않는다. 엘리트 표식, 경고, 피격 효과는 그림 위에 코드로 그린다.
- 원화는 Codex 내장 ImageGen만 쓴다. 로컬 이미지 모델, 부분 칠, 합성은 쓰지 않는다.
- 알파 규칙(`motion_lab_v1/source_alpha_policy.py` `inspect_master`):
  - 진짜 RGBA PNG, 배경 알파 0, 보이는 부분 1..254, 내부 254.
  - 네이티브 최대 변 1024 이상.
  - 스테이지 4/5 보스의 알파 255 예외는 그 배치에만 해당한다. 이번 보스에는 적용하지 않는다.
  - 녹색 배경으로 생성하거나, 받은 그림의 알파를 자르거나 키잉하지 않는다. 통과하지 못하면 HOLD다.
- 생성 참조 이미지는 저장소 안 파일만 쓴다.
- ImageGen 응답은 저장소로 옮기고 해시를 남긴다. 응답 JSON에 `projectCopy`와 SHA-256을 둔다(ANCHOR 선례: `motion_lab_v1/qa/stage1_enemies_20260913/anchor_master_tool_response.json`).
- 생성한 작업 이미지는 작업이 끝날 때까지 지우지 않는다. 거절 후보는 격리 폴더에 해시와 사유를 적어 보존한다.
- 전투 효과는 코드로만 그린다. `scripts/vfx/vfx_painter.gd`를 통하고, 효과 층마다 프레임당 삼각형 배열 2개 이하다.
- 테스트는 `--out=res://.cache/...`로 쓰고, 플레이어의 저장과 설정은 건드리지 않는다.
- 검토 이미지와 영상은 네이티브 1920×1080이다. 전투 영상은 게임 소리를 포함한다(`tools/environment/record_stage_battle_with_audio.py`).
- 로컬 커밋만 한다. GitHub 작업과 웹 배포는 하지 않는다.
- Claude의 파일과 커밋은 건드리지 않는다.

---

## 2. 새 보스 2종

| 항목 | 작전 2 | 작전 3 |
|---|---|---|
| id | `BOSS_SITE7_RELAY_01` | `BOSS_SITE7_REMNANT_01` |
| 이름(`name`) | `RELAY SENTINEL` | `RESONANCE REMNANT` |
| 방 | R05_RELAY (`S2_R05` 가라앉은 중계 구덩이) | R05_ANCHOR (`S3_R05` 부서진 앵커 기둥) |
| 체력 | 710 (그대로) | 820 (그대로) |
| 강조색 | 진홍 (`#d8283c` 계열) | 얼음빛 흰 아크 (`#bfe8ff` 계열) |
| 이야기 | "Disable the relay sentinel": 하층 중계망의 보호막 주기를 돌리는 기계 | "Destroy the anchor remnant": 기둥이 부서진 뒤에도 살아남은 마지막 앵커의 공명 코어 |

- id에는 반드시 `BOSS_`로 시작하고 `BOSS`가 들어가야 한다. 보스 판정(고정, 페이즈 보호막, 체력바, 정보 보상 `ANCHOR`)이 이 문자열로 걸린다.
- id와 프로필 이름에 다음 문자열을 넣지 않는다. 다른 효과 계열로 잘못 들어간다: `ASTER`(예: MASTER), `ROOK`, `MICA`, `DRONE`, `SHIELD`, `PRISM`, `_RAM_`, `GUARD`, `PYLON`, `MORTAR`, `RIFLE`, `ANCHOR`, `FORGE`, `CARRIER`.

### 2.1 ImageGen 프롬프트

영어로 쓴다. 요청에 `background: transparent_alpha`를 넣는다. 한 번에 한 장씩 만들고 받자마자 알파 검사를 한다.

**공통 코어**

```
Premium 2.5D tactical sci-fi BOSS MACHINE for SABLE CIRCUIT, underground research facility SITE-7, drawn for a fixed near-orthographic three-quarter top-down dimetric game camera (the same camera as the reference environment plate).
SUBJECT: one stationary, non-humanoid boss machine bolted to a heavy floor mount. It is anchored in place and never walks: no legs, no feet, no knees, no arms with hands, no head or face, no tracks, no wheels.
EMITTER: exactly one clearly visible glowing emitter at the top of the machine that reads the same from every direction. It is not a gun barrel and does not point one way.
FRAMING: the whole machine fits inside the image with clear margin on every side. The floor mount's ground contact is at the bottom centre. The silhouette must stay readable when the machine is about 230 pixels tall on screen.
BACKGROUND: genuinely transparent RGBA alpha. No floor, no ground shadow plate, no backdrop, no green or chroma colour, no checkerboard.
LIGHT: neutral-white key light from the upper left, as on the SITE-7 plates. Coloured light comes only from the machine's own lamps and emitter.
EXCLUDE: text, numbers, logos, UI, characters, creatures, projectiles, explosions, smoke, floor decals, any round iris, concentric rings or circular portal.
STYLE: premium stylized realism with hard-surface armour thickness, recessed panels, bolts, cables and cast self-shadow. Not low-poly, not flat vector, not generic neon cyberpunk, not blurry concept art.
DESIGN: {DESIGN}
```

**`{DESIGN}` — RELAY SENTINEL**

```
A squat, heavily armoured relay-transformer sentinel on a wide square floor mount. Four stacked transformer coil towers of different heights ring a central vertical relay mast; thick insulated cable bundles run down into the mount. Crimson status slits along the armour. The emitter is a crimson relay node crowning the central mast, with a small caged spark gap around it. Overall shape: wide and low at the base, stepped up toward the mast, asymmetric coil heights.
```

**`{DESIGN}` — RESONANCE REMNANT**

```
The surviving resonance core of a shattered signal-anchor mast, held upright in a heavy clamp cradle on a floor mount. Split armoured housings hang open around a cylindrical core; severed conduit bundles and snapped structural ribs stick out from the broken top. Emergency clamp frames and bracing struts hold it together. The emitter is an exposed forked arc coil at the broken top, leaking ice-white arcs between its two prongs. Overall shape: tall, narrow, broken and leaning slightly, clearly damaged but still powered.
```

**참조 이미지** (모두 저장소 안)
1. `assets/enemies/stage4_forge_warden/authored_core_v1/FORGE_WARDEN.png`: 카메라, 렌더 품질, 틀 안의 크기에만 쓴다. 모양을 옮기지 않는다.
2. 그 보스의 방 판(`assets/environments/site7_v2/stage02/S2_R05/S2_R05_GAME.png`, `.../stage03/S3_R05/S3_R05_GAME.png`): 재질과 색 맥락에만 쓴다.
3. `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png`: 재질 품질.

**구분 기준**
- 다섯 보스(ANCHOR, RELAY, REMNANT, FORGE, CARRIER)를 같은 크기로 나란히 놓았을 때 실루엣이 서로 달라야 한다.
- 새 두 보스에는 둥근 홍채, 동심원, 원형 포털이 없어야 한다.
- 보스가 자기 방 뒷벽의 구조물과 똑같아 보이면 안 된다. 방은 배경, 보스는 그 앞의 기계다.

### 2.2 파일

| 종류 | RELAY SENTINEL | RESONANCE REMNANT |
|---|---|---|
| 원본(ImageGen 그대로) | `motion_lab_v1/art/site7_enemies_raw/relay_sentinel_master.png` | `motion_lab_v1/art/site7_enemies_raw/resonance_remnant_master.png` |
| 런타임 | `assets/enemies/stage2_relay_sentinel/authored_core_v1/RELAY_SENTINEL.png` | `assets/enemies/stage3_resonance_remnant/authored_core_v1/RESONANCE_REMNANT.png` |
| 명세 | 같은 폴더 `spec.json` | 같은 폴더 `spec.json` |

- 런타임 PNG는 원본 그대로(크롭·축소 없이)를 기본으로 한다. FORGE/CARRIER 선례와 같다.
- `.import`: `compress/mode=0`(무손실), `mipmaps/generate=false`.
- `spec.json`은 FORGE 형식을 따른다: `kind: "anchored_machine"`, `display_height`(220–250), `root_px`(바닥 고정점), `emitter_px`(방출구 중심), `emitter_visible: true`, `emission_contract`, 이미지 SHA-256.
- 기록: `qa/site7_boss_robots_<날짜>/`
  - `boss_asset_gate.json`: 형식은 `qa/stage45_implementation_20260919/stage45_asset_gate.json`과 같다. `source_alpha_policy`는 일반 정책(0..254)이다.
  - ImageGen 응답 JSON(`projectCopy`, SHA-256), 최종 프롬프트 전문, 시도 횟수, 거절 사유

### 2.3 등록

**데이터**
- `data/art_profiles/enemy_profiles.json`: FORGE 행(183–203줄)을 본보기로 두 행을 넣는다.
  - `tier: "BOSS"`, `body_plan: "robot"`, `runtime_enabled: true`, `biped_asset` 없음
  - `motion_profile`: `MOT_BOSS_RELAY_01`, `MOT_BOSS_REMNANT_01`
  - `projectile_profile`: `PRJ_BOSS_RELAY_BOLT_01`, `PRJ_BOSS_REMNANT_ARC_01`
  - `hit_vfx_profile`: `HIT_BOSS_RELAY_SURGE_01`, `HIT_BOSS_REMNANT_ARC_01`
  - 소리: `SFX_FIRE_BOSS_ANCHOR_01`, `SFX_HIT_BOSS_ANCHOR_01`을 그대로 쓴다(FORGE/CARRIER 선례).
  - `palette`, `silhouette`, `master_asset`, `machine_asset`(spec 경로와 **spec.json 파일**의 SHA-256), `introduced_in`
  - 새 필드 `boss_pattern`(3절)과 `boss_brief`(3.4)
- `data/art_profiles/site7_enemy_body_plan.json`: `active_enemy_ids`와 `roles`에 추가한다. `locomotion: "anchored"`.
- `data/missions/MIS_CH01_02.json`, `MIS_CH01_03.json`:
  - 보스 행의 `enemy_id`를 새 id로 바꾼다. 체력, 위치, 지원 행, 증원은 그대로다.
  - `new_enemy_ids`에 새 보스를 넣는다(작전 4·5 선례).
- `data/visual/site7_battle_layouts.json`의 R05_RELAY, R05_ANCHOR `boss_anchor`는 새 그림의 발판이 방 바닥과 엄폐에 겹치지 않는지 확인하고, 필요하면 옮긴다.

**id로 묶인 코드** (새 id를 넣지 않으면 공격을 안 하거나 등록에 실패한다)
- `scripts/combat/site7_enemy_tactics.gd` `ROLES` → `"boss"`
- `scripts/animation/site7_machine_sprite.gd` 165–169줄 `expected_kind` → `"anchored_machine"`
- `scripts/animation/site7_machine_sprite.gd` 359–372줄: 방출구 빛과 테두리 색
- `scripts/actors/enemy_actor.gd`
  - 507–508줄: 레거시 뼈대를 만들지 않는 목록
  - 464–477줄 `_projectile_color`: RELAY 진홍, REMNANT 얼음빛 흰색
- `scripts/animation/enemy_detail_overlay_presentation.gd` 18–19줄: 건너뛰기 목록

**효과 계열** (프로필 문자열로 찾는다)
- `scripts/vfx/combat_hit_vfx.gd` `family_for`에 `RELAY`, `REMNANT`를 `ANCHOR` 검사보다 앞에 넣는다.
  - 두 계열의 피격 효과를 새로 그린다: RELAY는 진홍 전류가 튀는 서지, REMNANT는 흰 아크가 갈라지는 방전.
  - `FAMILIES`, `LIFE`, `TRAIL_LENGTH`, `ANIMATED`, 그리기 분기를 추가한다.
- `scripts/vfx/combat_muzzle_vfx.gd`, `scripts/combat/prototype_projectile.gd`: 두 계열의 방출과 투사체 그리기를 넣는다.
- `prototype_projectile.gd` 162줄: 지금은 `ANCHOR` 프로필만 속도·피해·수명을 조정하고(560 / 24 / 1.6), FORGE와 CARRIER는 기본값(720 / 10 / 1.1)으로 떨어진다. 보스 투사체 다섯 종 모두 명시적으로 조정한다. 피해는 ANCHOR(24) 이하로 한다.
- `tests/smoke/combat_vfx_overhaul_smoke.gd`의 삼각형 예산과 자기 해제 검사를 통과해야 한다.

---

## 3. 보스별 공격 패턴

### 3.1 구조

- `enemy_profiles.json`의 `boss_pattern` 값으로 `_boss_attack`이 패턴을 고른다. 값: `anchor_iris`, `relay_chain`, `resonance_lanes`, `forge_press`, `carrier_null`.
- `anchor_iris`는 지금 `_boss_attack`과 **완전히 같다.** 값이 없는 보스도 이것을 쓴다.
- 부품은 지금 있는 세 가지만 쓴다.
  - 투사체: `_fire(direction)`
  - 원형 경고: `_warning("circle", ...)`, 기본 반지름 58
  - 직선 레인 경고: `_warning("lane", ...)`, 기본 길이 430, 반폭 16
- `_warning`이 반지름, 길이, 반폭, 준비 시간을 인자로 받게 넓힌다. 기본값은 지금과 같다.

### 3.2 공정성 규칙 (모든 패턴)

- 모든 피해는 먼저 경고된다. 경고 준비 시간은 1.0초 이상이다.
- 한 번의 공격이 만드는 경고는 7개 이하다.
- 경고 하나의 피해는 20(ANCHOR와 같음) 이하, 투사체 피해는 24 이하다.
- 대상 주변 300 px 안에 경고가 덮지 않는 바닥이 늘 있어야 한다. 경고 사이의 안전한 틈은 대원 폭의 1.5배 이상이다.
- 페이즈 경계(체력 66 %, 33 %), 3페이즈 보호막(`boss_phase_transition_guard.gd`, 8초 CORE SHIELDED), 회복 시간 공식은 그대로다.

### 3.3 패턴

`대상`은 보스가 고른 조작 대원이다. `보스→대상`은 보스에서 대상으로 가는 방향이다.

| 패턴 | 1페이즈 | 2페이즈 | 3페이즈 | 피하는 법 |
|---|---|---|---|---|
| `anchor_iris` (ANCHOR, 작전 1) | 지금 그대로 | 지금 그대로 | 지금 그대로 | 부채꼴 사이, 원 밖 |
| `relay_chain` (RELAY, 작전 2) | **중계 사슬**: 보스→대상 선 위에 원 3개(대상 중심, 간격 110 px). 준비 시간은 보스 쪽부터 1.1 / 1.3 / 1.5초로 바깥으로 번진다 | 사슬, 그리고 다른 대원마다 원 1개(1.3초). 다음 공격은 쌍 볼트 2발(±0.15 rad) | 사슬 원 5개(간격 110 px)와 다른 대원 원. 다음 공격은 쌍 볼트 | 사슬을 옆으로 가로질러 벗어난다 |
| `resonance_lanes` (REMNANT, 작전 3) | **공명 레인**: 보스에서 뻗는 레인 3개(0, ±0.45 rad, 길이 700) | 공명 레인과 **공명 폭발**을 번갈아 쓴다. 폭발은 보스 중심 원(반지름 160, 1.2초)과 대각 레인 2개(±0.8 rad) | 레인 5개(0, ±0.35, ±0.7 rad)와 공명 폭발을 번갈아 쓴다 | 레인 사이로 들어가고, 보스에 붙지 않는다 |
| `forge_press` (FORGE, 작전 4) | **프레스**: 대상에 원(반지름 90, 1.2초). 다음 공격은 녹은 볼트 2발(±0.2 rad) | 프레스, 그리고 보스 앞 가까운 원(반지름 160, 보스→대상 방향 140 px). 근접을 막는다 | 2페이즈 공격에 방의 대각 축을 따라 보스에서 뻗는 고정 레인 2개(길이 900)를 더한다 | 거리를 두고, 원 밖으로 빠진다 |
| `carrier_null` (CARRIER, 작전 5 긴 복도) | **널 레인**: 대상을 향한 긴 레인 1개(길이 1000, 반폭 22)와 볼트 2발(±0.3 rad) | 긴 레인 3개. 대상 레인과 좌우 ±150 px 평행 레인 | 2페이즈 레인에 대상 원(반지름 120, 레인보다 0.3초 늦게)을 더한다 | 레인 사이 틈으로 들어가 틈을 따라 움직인다 |

- 수치는 시작값이다. 풀플레이와 공정성 규칙에 맞게 조정해도 된다. 경고를 없애거나 규칙을 넘기지는 않는다.
- 두 보스가 같은 페이즈에서 같은 모양(경고 종류와 개수의 조합)이 되면 안 된다(5절 테스트).

### 3.4 보스방 연출과 안내문

- `boss_arena_presentation.gd:47`: 단상과 기둥 색을 보스 프로필의 `palette` 강조색에서 가져온다. 지금은 모든 보스가 보라다. ANCHOR는 보라 그대로다.
- `scripts/ui/enemy_overhead_ui.gd`: 보스 체력바 강조색(지금 `9179ff`/`f0529d` 고정)을 같은 방식으로 보스별로 바꾼다.
- `story_stage_01.gd:488` 안내문을 프로필 `boss_brief`에서 읽는다. 없으면 지금 문장을 쓴다.

| 보스 | `boss_brief` |
|---|---|
| ANCHOR | `Central iris active. Evade the announced fan and floor blast; reposition while CORE SHIELDED is active.` (지금 그대로) |
| RELAY | `Relay chain ripples outward from the sentinel. Cross the chain sideways; shots are blocked while CORE SHIELDED.` |
| REMNANT | `Resonance lanes fan from the broken mast. Step between the lanes and do not hug the core; it bursts at close range.` |
| FORGE | `The press slams where you stand. Keep moving and keep your distance from the furnace front.` |
| CARRIER | `Null lanes run the length of the corridor. Slip into the gap between lanes and move along it.` |

---

## 4. 이야기 문장

`data/story/site7_campaign.json`에서 ANCHOR를 전제로 한 문장을 새 보스에 맞게 고친다. 나머지 문장은 그대로 둔다.

| 작전 | 지금 | 새 문장 |
|---|---|---|
| 2 브리핑 ROOK | `Recover the reserve cache before the quarantine crossing. A second anchor means another shield cycle. Keep an escape lane open.` | `Recover the reserve cache before the quarantine crossing. The relay sentinel runs the sublevel shield cycle. Keep an escape lane open.` |
| 3 브리핑 MICA | `The final anchor has a stronger core. Its central iris is the emitter; the shield phase still blocks our shots.` | `The final anchor's resonance core survived its broken mast. The arc fork on top is the emitter; the shield phase still blocks our shots.` |

작전 2 요약("disable the sublevel sentinel"), 작전 3 요약("shut down the resonance anchor")과 목표 문장은 이미 새 보스와 맞는다.

---

## 5. 테스트

**고칠 테스트** (보스 목록을 가지고 있다)
- `tests/smoke/site7_robot_roster_smoke.gd`
  - 5줄: 작전 1–3에 나올 수 있는 적 목록 `ALLOWED`에 새 두 보스를 넣는다.
  - 40줄: 지금은 작전마다 `new_enemy_ids == [INTRODUCED[n-1]]`이다. 작전 2는 `[RAM, RELAY]`, 작전 3은 `[MORTAR, REMNANT]`을 기대하게 바꾼다.
- `tests/smoke/site7_stage45_registry_smoke.gd`를 본보기로 `tests/smoke/site7_boss_registry_smoke.gd`를 만든다. 새 두 보스의 등록과 런타임을 검사하고 러너에 등록한다.
- `tests/smoke/site7_emission_owner_smoke.gd` 8–11줄 `ROLE_BY_ID`
- `tests/smoke/combat_vfx_overhaul_smoke.gd` 13–21줄 `ENEMY_FAMILIES`, `PROJECTILE_FAMILIES`
- `tests/smoke/site7_full_operation_smoke.gd` 85줄: 보스의 투사체 개수 기대값을 보스별 패턴에 맞게 바꾼다. 경고 없는 투사체를 막는 검사는 유지한다.
- `tests/smoke/deploy_warmer_smoke.gd`: 작전 2·3이 새 보스 그림을 미리 읽는지
- `tests/smoke/site7_anchor_app_smoke.gd`, `tests/render/site7_anchor_capture_smoke.gd`: 새 보스용으로 복사해 쓸 수 있다.

**새 테스트** `tests/smoke/site7_boss_pattern_smoke.gd` (quick 묶음에 등록)
- 보스 5종을 각 페이즈에서 연속 공격 2번씩 실제 `Site7EnemyTactics`로 돌린다.
- 확인한다:
  - `anchor_iris`의 경고와 투사체가 지금 코드와 같다(기준값 고정).
  - 모든 경고의 준비 시간 1.0초 이상, 공격당 경고 7개 이하, 경고 피해 20 이하
  - 대상 주변 300 px 안에 경고가 덮지 않는 바닥 점이 있다.
  - 두 보스가 같은 페이즈에서 같은 모양이 아니다.
  - 투사체는 모두 그 공격에서 나온 것이다(경고 없는 발사 없음).
- 음성 확인: 두 보스의 `boss_pattern`을 메모리에서 같게 만들면 FAIL하는지 확인하고 결과를 기록한다.

---

## 6. 검증과 기록

1. 새 두 보스 원본이 `source_alpha_policy.py` 알파 검사를 통과한다. 원본 크기로 밝은 배경과 어두운 배경 위에서 가장자리와 내부를 확인한다.
2. `python tools/maintenance/run_regression_suite.py`(quick)와 `--suite full`이 PASS한다.
   - 작전 1–5 풀플레이를 모두 본다. 작전 4·5도 패턴이 바뀌었다.
   - `full_op_03`은 봇이 약 3번에 1번 전멸한다. FAIL이 한 번 나오면 다시 돌린다. 같은 보스에서 계속 전멸하면 그 패턴의 수치를 조정한다.
3. 1080p 게임 캡처
   - 새 두 보스를 자기 방에서 게임 크기로 찍는다. 원본 크기 크롭도 함께 둔다.
   - 보스 5종을 같은 크기로 나란히 놓은 한 장
   - 보스별 경고 모양: 페이즈마다 한 장씩, 보스 5종
4. 전투 영상: 보스 5종 각각 10초, 게임 소리 포함(`record_stage_battle_with_audio.py`). 600프레임, 10초, 소리가 들어 있는지 확인한다.
5. `tools/art_pipeline/validate_visual_evidence_1080p.py --require-dynamic-capture`를 모든 검토 이미지와 영상에 돌린다.
6. 기록: `qa/site7_boss_robots_<날짜>/README_KO.md`와 위 증거
7. 로컬에 커밋한다.

---

## 7. 순서와 멈출 지점

1. **원화**: RELAY SENTINEL, RESONANCE REMNANT를 만들고 알파 검사와 원본 크기 검수를 한다.
2. **패턴 구조**: `boss_pattern` 선택을 넣는다. `anchor_iris`가 지금과 같은지 새 테스트로 먼저 고정한다.
3. **등록과 패턴**: 새 보스를 등록하고 작전 2·3에 넣는다. 다섯 패턴, 효과 계열, 투사체 조정, 연출, 안내문, 이야기 문장을 넣는다.
4. **검증**: 6절 전체를 한 뒤 **멈추고 사용자에게 보고한다.**

- 예상 생성량: 2장 × 평균 2회 ≈ ImageGen 4–6회.

**중단(HOLD) 조건**
- 한 보스가 ImageGen 3회 안에 알파 규칙(0..254)이나 1절의 형태 규칙(사람형 금지, 전방향 방출구, 홍채 금지)을 맞추지 못하면 멈춘다.
  - 그 보스를 HOLD로 기록하고 받은 후보를 보존한 채 보고한다.
  - 알파 255 예외는 사용자만 줄 수 있다.
- 풀플레이가 새 패턴 때문에 계속 실패하면, 공정성 규칙 안에서 수치를 조정한다. 규칙이나 테스트 기준을 낮추지 않는다.
- 이 작업은 새 보스와 패턴의 연결과 검증까지다. 사람의 플레이 승인이나 배포 승인을 대신하지 않는다.
