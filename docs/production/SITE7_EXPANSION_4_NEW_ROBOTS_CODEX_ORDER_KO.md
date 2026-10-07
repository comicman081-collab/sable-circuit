# SITE-7 새 일반 로봇 2종 — LANCER와 TENDER (확장 항목 4 작업 지시서)

작성: 2026-10-06, Claude. 사용자 지시 "남은것들 해"에 따른 지시서다. **이 문서를 쓴 시점에는 아무 것도 시작하지 않았다.** 그림은 Codex의 내장 ImageGen만 만든다(`AGENTS.md`). 코드·데이터·시험·기록은 보스 2종(2026-09-28)과 보스 5종(2026-09-29)의 선례대로 Claude가 한다. 사용자가 분담을 따로 정하면 그것이 이긴다. 규칙 순위: `AGENTS.md` > 이 문서. 숫자 중 "(시작값)"은 제안이고, 공정성 한계(6절)를 넘지 않는 범위에서 시험이 정한다.

## 0. 왜 새 일반 로봇인가

작전 3–10의 방은 같은 여섯 로봇을 섞어 쓴다. 보스는 열 종이 서로 다른데, 일반 로봇은 작전 5 이후 하나도 늘지 않았다.

| 로봇 | 이동 | `ROLES` | 하는 일 | 화면 높이(px) | 첫 등장 |
|---|---|---|---|---|---|
| `ENM_SITE7_DRONE_01` 정찰 드론 | hover | drone | 궤도를 돌며 예고 후 사격 | 110 | 작전 1 |
| `ENM_SITE7_BULWARK_01` | tracked | shield | 전면 장갑, 느리게 접근해 단발 사격 | 91.8 | 작전 1 |
| `ENM_SITE7_RAM_01` CINDER | hover | melee | 예고 레인을 따라 돌진 | 86.6 | 작전 2 |
| `ENM_SITE7_MORTAR_01` VESPER | anchored | mortar | 고정 낙하점 원 | 108.6 | 작전 3 |
| `ENM_SITE7_PRISM_01` | hover | skimmer | 중거리 펄스 | 110 | 작전 4 |
| `ENM_SITE7_NULL_PYLON_01` | anchored | mortar | 렌즈 원 | 132 | 작전 5 |

빈 역할은 둘이다.

1. **지원**: 다른 로봇을 돕는 로봇이 없다. 그래서 어느 방이든 "가까운 것부터 쏜다"가 정답이다.
2. **먼 거리의 한 줄**: CINDER의 레인은 근접, PRISM은 중거리, VESPER는 원이다. 멀리서 직선 한 줄로 길을 막는 로봇이 없다.

이번 작업은 이 둘을 메운다. **LANCER**(먼 거리의 한 줄)와 **TENDER**(지원). 일반 로봇은 한 방에 여러 마리가 나오므로 보스보다 읽기 쉬움과 공정성이 더 중요하다.

## 1. 반드시 지킬 규칙

- 사람형 적은 0이다(`data/art_profiles/site7_enemy_body_plan.json`). 다리, 발, 무릎, 손 달린 팔, 머리·얼굴이 없다. 허용되는 이동은 `tracked`와 `hover`뿐이다. 금지 목록 `forbidden_new_enemy_locomotion`을 따른다.
- 원화는 Codex 내장 ImageGen만 쓴다. 로컬 이미지 모델, 부분 칠, 합성, **좌우 반전과 평면 회전으로 방향 만들기**는 쓰지 않는다. 이동형은 8방향(`authored_yaw8`)을 방향마다 따로 그린다. 한 장을 전방향으로 쓰지 않는다(`references/enemy-facing.md`).
- 알파: 진짜 RGBA PNG, 배경 알파 0, 보이는 부분 1..255(2026-09-28부터 255 허용, 254로 깎지 않는다), 네이티브 최대 변 1024 이상. 녹색 배경으로 만들거나 받은 그림을 자르고 키잉하지 않는다. 통과하지 못하면 HOLD다(`motion_lab_v1/source_alpha_policy.py` `inspect_master`).
- 생성 참조 이미지는 저장소 안 파일만 쓴다. ImageGen 응답은 저장소로 옮기고 응답 JSON에 `projectCopy`와 SHA-256을 둔다(선례: `motion_lab_v1/art/site7_enemies_raw/drone_E_v1_tool_response.json`). 생성한 작업 이미지는 작업이 끝날 때까지 지우지 않는다(2026-09-27). 거절 후보는 격리 폴더에 해시와 사유를 적어 둔다.
- 로봇 그림에는 색을 입히지 않는다. 엘리트 표식, 경고, 피격, 연결선은 그림 위에 코드로 그린다. 전투 효과는 `scripts/vfx/vfx_painter.gd`만 쓰고 효과 층마다 프레임당 삼각형 배열 2개 이하다.
- id와 프로필에 다음 문자열을 넣지 않는다(다른 효과·표본 계열로 잘못 들어간다): `ASTER`, `ROOK`, `MICA`, `DRONE`, `SHIELD`, `PRISM`, `_RAM_`, `GUARD`, `PYLON`, `MORTAR`, `RIFLE`, `ANCHOR`, `FORGE`, `CARRIER`, `BOSS`, `ABERRANT`, `BULWARK`. 소리 프로필 필드는 기존 것을 재사용해도 된다(PRISM이 `SFX_FIRE_ENM_DRONE_01`을 쓴다).
- 승인된 작전 10 그림 17개는 그대로여야 한다: `python qa/site7_op10_art_approval_20261002/tools/verify_hashes.py`.
- 검토 이미지와 영상은 네이티브 1920×1080이다(`tools/art_pipeline/validate_visual_evidence_1080p.py`). 테스트는 `--out=res://.cache/...`로 쓰고 플레이어의 저장과 설정을 건드리지 않는다. 로컬 커밋만 하고 GitHub 작업과 웹 배포는 하지 않는다.
- 이 작업은 그림·플레이·균형 승인이 아니다. 새 로봇의 수치와 배치는 사람이 한 번도 플레이하지 않은 제안이다.

## 2. 새 로봇 2종

| 항목 | LANCER | TENDER |
|---|---|---|
| id | `ENM_SITE7_LANCER_01` | `ENM_SITE7_TENDER_01` |
| 프로필 이름(`name`) | `LANCER / RAIL` | `TENDER / MEND` |
| 이동, `kind` | tracked, `tracked_machine` | hover, `hover_machine` |
| 새 `ROLES` 값 | `lancer` | `tender` |
| 화면 높이(`display_height`) | 96 (90–105) | 78 (72–90) |
| 역할 | 먼 거리에서 한 줄을 예고하고 한 발 쏜다 | 가장 다친 아군 로봇을 잠깐 고친다. 직접 공격은 없다 |
| 폴더 | `assets/enemies/lancer_rail/authored_yaw8_v1` | `assets/enemies/tender_mend/authored_yaw8_v1` |

### 2.1 LANCER — 레일 포 차량

- **실루엣**: 길고 낮고 납작한 궤도 선체. 선체 위에 길이가 선체 길이의 55 % 이상인 레일 포신 하나가 실루엣을 지배하고, 포신에는 코일 고리 셋이 있다. 포탑 고리는 없다. 선체 전체가 돌아서 포신이 앞을 향한다(BULWARK와 같은 방식). 뒤에 방열판. 방출구는 포신 끝에 눈에 보이는 하나다.
- **BULWARK와 달라야 하는 점**: BULWARK는 두껍고 넓은 방패가 앞을 가린다. LANCER는 앞이 열려 있고 얇다. 둘을 같은 크기로 나란히 놓고 실루엣만 봐도 구분돼야 한다.
- **색**: 대표 강조색이 기존 여섯과 달라야 한다(황토색 BULWARK, 구리색 CINDER, 보라 VESPER, 청록·보라 PRISM, 청록 PYLON 렌즈). 제안: 건메탈 선체, 백열 흰 레일, 자홍색 충전 빛.
- **싸움**(시작값; 공정성 한계는 6절):
  - 거리 380–520 px를 유지한다. 사격 위치는 드론과 같은 사선 탐색(`Site7EnemyTactics.LaneRoutes`)으로 고르고, 사선이 막히면 다시 자리를 잡는다. 엄폐를 뚫는 사격은 없다.
  - **WINDUP 1.4 s**: 멈추고, 선체 방향과 조준을 잠근다. 잠긴 사선을 따라 가는 흰 선(길이 900, 반폭 12)이 점점 밝아진다. 이 동안 피해는 0이다.
  - 발사: 한 발. 속도 900, 피해 18, 수명 1.2 s. 엄폐물의 알파 윤곽에 막힌다(양쪽 모두의 규칙). 경고 뒤에 엄폐가 생기면 실제로 흡수된다.
  - 다음 예고까지 3.2 s 이상. 동시에 공격하는 로봇 수(`MAX_CONCURRENT_ATTACKERS` 3)는 그대로다.
  - 경직(stagger)이나 `interrupt()`는 예고를 취소한다(기존 규칙).
- **안내문**(`StoryStage01._combat_story`): `LANCER: leave the thin white lane before it fires; cover stops the bolt.`

### 2.2 TENDER — 수리 스키프

- **실루엣**: 낮고 넓은 직사각 뗏목 모양 선체. 가운데에 가는 돛대, 그 위에 관절 크레인 붐 하나가 있고 붐 끝에 노즐이 있다(손이 아니다). 양옆에 수리액 탱크 두 개와 작은 안정 제트 한 줄. 방출구는 노즐 하나다. DRONE(둥근 센서 몸통)과 PRISM(삼각 프리즘)과 확실히 달라야 한다.
- **색**: 밝은 회백색 선체와 안전 청록 강조. 주황 경고 줄무늬는 CINDER의 구리색과 겹치지 않는 선에서만.
- **싸움**(시작값):
  - **고르기**: 420 px 안에서 체력 비율이 가장 낮은(동률이면 가까운) 보스 아닌 로봇. TENDER는 대상이 아니다. 없으면 분대 쪽으로 260 px까지 다가가서 총에 맞을 수 있게 한다.
  - **자리**: 대상에서 110–170 px, 분대와 반대쪽. 도망다니며 시간을 끌지 않는다.
  - **MEND**: 240 px 안이고 대상 체력이 90 % 미만이면 연결한다. 대상 최대 체력의 초당 6 %(초당 12 HP 이하)를 최대 3.5 s 동안 고치고, 4 s 쉰다. 한 TENDER는 한 번에 연결 하나. 한 대상은 8 s에 한 번만 연결된다. 체력은 최대치를 넘지 않고, 쓰러진 로봇은 살리지 않는다. TENDER가 경직되거나 최대 체력의 25 % 이상을 한 번에 잃으면 연결이 끊긴다.
  - **연결선**: 코드로 그린 선(맥박치는 알파, 끝에 작은 불꽃). 로봇 그림은 칠하지 않는다.
  - **OVERLOAD**: 고칠 대상이 남지 않으면(다른 로봇이 없거나 TENDER뿐) 속도 70으로 가장 가까운 대원에게 다가가 90 px 안에서 1.2 s 예고 원(반지름 70, 자기 자리)을 그리고 터져 자신을 없앤다. 피해 12 이하, 원 안의 모든 것이 맞는다. 방이 TENDER 하나 때문에 영영 안 끝나는 일을 막는 규칙이다. 터지는 것도 처치로 센다(`defeated`가 정확히 한 번).
  - **체력**: 방 행에서 정한다. 시작값은 DRONE 행의 0.6배.
- **안내문**: `TENDER: its mend line heals the weakest robot; cut the line by staggering it or destroy it first.`

### 2.3 검토한 다른 후보와 버린 이유

- 지뢰 투하기: 새 개체(지뢰)와 따르는 연산자·봇의 회피 규칙이 한꺼번에 필요하다. 장판(`ZoneHazard`)이 이미 같은 일을 한다.
- 방벽 투사기(아군에게 돔 방어막): 정예 변종 BEACON과 효과가 겹친다.
- 빠른 측면 돌격기: CINDER와 역할이 겹친다.

## 3. ImageGen 프롬프트

영어로 쓴다. 요청마다 `background: transparent_alpha`를 넣는다. **한 번에 한 장**씩 만들고 받자마자 알파 검사를 한다.

**공통 코어**

```
Premium 2.5D tactical sci-fi ROBOT for SABLE CIRCUIT, underground research facility SITE-7, drawn for a fixed near-orthographic three-quarter top-down dimetric game camera (the same camera as the reference environment plate).
SUBJECT: one non-humanoid machine. No legs, no feet, no knees, no arms with hands, no head or face.
FRAMING: the whole machine fits inside the image with clear margin on every side. The ground contact (tracks or hover underside) is at the bottom centre. The silhouette must stay readable when the machine is about 90 pixels tall on screen.
BACKGROUND: genuinely transparent RGBA alpha. No floor, no ground shadow plate, no backdrop, no green or chroma colour, no checkerboard.
LIGHT: neutral-white key light from the upper left, as on the SITE-7 plates. Coloured light comes only from the machine's own lamps and emitter.
EXCLUDE: text, numbers, logos, UI, characters, creatures, projectiles, explosions, smoke, floor decals.
STYLE: premium stylized realism with hard-surface armour thickness, recessed panels, bolts, cables and cast self-shadow. Not low-poly, not flat vector, not generic neon cyberpunk, not blurry concept art.
DESIGN: {DESIGN}
```

**`{DESIGN}` — LANCER**

```
A long, low, flat tracked rail-gun carriage. Two continuous tracks under a thin armoured hull; radiator fins at the rear. One long fixed rail barrel runs along the top of the hull and dominates the silhouette, its length more than half the hull length, with three coil rings along it. The whole hull points the barrel; there is no turret ring. The emitter is the visible muzzle at the barrel tip. The front is open and slim, never a shield. Gunmetal hull, white-hot rail, magenta charge glow.
```

**`{DESIGN}` — TENDER**

```
A low, wide, rectangular hovering repair skiff. A thin mast rises from the middle of the flat hull and carries one articulated crane boom that ends in a small glowing nozzle (a tool, not a hand). Two cylindrical repair-fluid tanks sit on the flanks and a row of small stabiliser jets runs along the underside. The emitter is the boom nozzle. Light grey-white hull with safety-teal accents.
```

**8방향.** 먼저 마스터 한 장(3/4 시점)을 만든다. 그다음 방향마다 한 장씩 만들고, 마스터를 참조 이미지로 넣고 이렇게 덧붙인다.

```
YAW VIEW {DIR}: the same machine as the reference, turned so its front (the barrel tip / the boom nozzle) faces screen-{DIR}. E = screen right, S = toward the camera, N = away from the camera, and the diagonals between. Keep proportions, colours, panel layout and emitter position identical to the reference. Do not mirror the reference; redraw the machine from the new yaw.
```

방향 이름은 `scripts/animation/site7_machine_sprite.gd`의 방향 선택과 BULWARK/PRISM 묶음(`assets/enemies/bulwark/authored_yaw8_v1/`)과 같은 규약을 쓴다. 쓰기 전에 그 코드를 읽어 `E`가 어느 쪽인지 확인한다.

**참조 이미지**(모두 저장소 안): 카메라, 렌더 품질, 틀 안의 크기에만 쓴다. 모양을 옮기지 않는다.
1. `assets/enemies/bulwark/authored_yaw8_v1/E.png`와 `assets/enemies/prism_skimmer/authored_yaw8_v1/E.png`
2. `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png`

**구분 기준**
- 여덟 일반 로봇(기존 여섯과 새 둘)을 같은 눈높이로 나란히 놓았을 때 실루엣이 모두 달라야 한다.
- 8방향의 각 장은 서로 다른 그림이어야 한다(런타임이 같은 파일과 같은 보이는 RGBA를 거부한다). 앞과 뒤의 면, 부속품 수, 방출구 위치가 방향에 맞아야 한다.

## 4. 파일, 명세, 기록

| 종류 | LANCER | TENDER |
|---|---|---|
| 원본(ImageGen 그대로) | `motion_lab_v1/art/site7_enemies_raw/lancer_master.png`, `lancer_{E,NE,N,NW,W,SW,S,SE}_v1.png` + `_tool_response.json` | `.../tender_master.png`, `tender_{…}_v1.png` + `_tool_response.json` |
| 런타임 | `assets/enemies/lancer_rail/authored_yaw8_v1/{E,NE,N,NW,W,SW,S,SE}.png` | `assets/enemies/tender_mend/authored_yaw8_v1/{…}.png` |
| 명세 | 같은 폴더 `spec.json` | 같은 폴더 `spec.json` |

- 런타임 PNG는 원본 그대로(크롭·축소 없이)가 기본이다. 크롭이 필요하면 무손실 크롭만 쓰고 기록한다(2026-09-19 선례).
- `.import`: `compress/mode=0`, `mipmaps/generate=false`.
- `spec.json`은 BULWARK 형식이다: `kind`, `facing_mode: "authored_yaw8"`, 방향마다 `texture`, `texture_sha256`, `display_height`, `root_px`(바닥 접점), `emitter_px`(LANCER는 포신 끝, TENDER는 노즐), `emitter_visible: true`.
- 기록: `qa/site7_new_regulars_<날짜>/`. 최종 프롬프트 전문, 시도 횟수, 거절 사유, 알파 검사 결과, 방향별 SHA-256, `regular_asset_gate.json`(형식은 `qa/site7_boss_robots_20260928_final/boss_asset_gate.json`을 따른다).

## 5. 등록 (Claude)

**데이터**
- `data/art_profiles/enemy_profiles.json`: PRISM 행을 본보기로 두 행. `tier: "NORMAL"`, `body_plan: "robot"`, `runtime_enabled: true`, `motion_profile`(`MOT_LANCER_RAIL`, `MOT_TENDER_MEND`), LANCER만 `projectile_profile: PRJ_ENM_LANCER_RAIL_01`, `hit_vfx_profile`(`HIT_ENM_LANCER_RAIL_01`, `HIT_ENM_TENDER_MEND_01`), `machine_asset`(spec 경로와 spec.json의 SHA-256), `palette`, `silhouette`, `introduced_in`.
- `data/art_profiles/site7_enemy_body_plan.json`: `active_enemy_ids`와 `roles`에 추가한다.
- `data/progression/intel_discoveries.json`: PRISM이 있는 곳을 읽고 같은 방식으로 필요한 만큼 넣는다.

**id로 묶인 코드**(새 id를 넣지 않으면 공격을 안 하거나 등록에 실패한다)
- `scripts/combat/site7_enemy_tactics.gd` `ROLES`와 `step`의 역할 분기, 새 공격 함수 `_lancer_attack`, `_tender_*`
- `scripts/animation/site7_machine_sprite.gd`: `expected_kind`와 방출구 빛 색
- `scripts/actors/enemy_actor.gd`: `_projectile_color`와 레거시 뼈대 제외 목록
- `scripts/animation/enemy_detail_overlay_presentation.gd`: 건너뛰기 목록
- `scripts/combat/prototype_projectile.gd`: LANCER 투사체의 속도·피해·수명·몸통 그리기
- `scripts/vfx/combat_hit_vfx.gd` `family_for`, `scripts/vfx/combat_muzzle_vfx.gd`, `scripts/combat/combat_feedback.gd`: LANCER와 TENDER 계열을 DRONE 검사보다 **앞에** 넣는다(보스 선례).
- `scripts/audio/combat_sfx_bank.gd`: PRISM이 나오는 곳을 읽고 같은 방식으로(소리는 기존 것을 재사용한다)
- `scripts/missions/story_stage_01.gd` `_combat_story`: 두 안내문
- `scripts/core/intel_samples.gd` `enemy_key`: 두 로봇을 `SECURITY`로 묶는다(저장 형식은 그대로).
- `scripts/core/deploy_warmer.gd`: 새 로봇 그림을 그 로봇이 나오는 작전의 로드 때 미리 읽는다.

**고칠 시험**(`grep -n "PRISM" tests/`로 하나씩 확인한다): `site7_robot_roster_smoke`(`ALLOWED`, `new_enemy_ids`), `site7_emission_owner_smoke`(`ROLE_BY_ID`), `combat_vfx_overhaul_smoke`(`ENEMY_FAMILIES`, `PROJECTILE_FAMILIES`), `site7_campaign_data_smoke`, `intel_supply_smoke`, `deploy_warmer_smoke`, `m10_intel_loadout_smoke`. 기대 개수는 넓히기만 하고 줄이지 않는다.

## 6. 공정성 한계 (시험이 지킨다. 낮추지 않는다)

- 모든 피해는 먼저 경고된다. 경고 준비 시간 ≥ 1.0 s(LANCER 1.4 s, OVERLOAD 1.2 s).
- 투사체 피해 ≤ 24(LANCER 18). 경고 원의 피해 ≤ 20(OVERLOAD 12). 이것은 보스의 한계와 같은 숫자다.
- 가장 느린 연산자 걸음(138 px/s)으로 LANCER의 선 반폭 12 px + 연산자 반경을 0.25 s 안에 벗어난다. OVERLOAD 원(반지름 70)은 경고 1.2 s 안에 벗어난다: (1.2 − 0.25) × 138 = 131 px ≥ 70 px.
- TENDER가 한 대상에게 주는 치료는 8 s에 최대 체력의 25 % 이하다. 보스와 TENDER에게는 연결하지 않는다. 쓰러진 로봇을 살리지 않는다.
- 로봇 그림은 칠하지 않는다. 연결선과 경고는 코드로 그린다.
- 새 로봇이 나온 방의 `boss_room_fairness`, `traversal_audit`, `combat_density`, `battle_geometry`와 `full_op_NN` 봇이 통과해야 한다. 봇이 새 종류의 이유(경로, 보상, 탈출, 시간 초과)로 실패하면 결함이다. WIPED 횟수는 판정이 아니라 사용자에게 가는 수치다.
- TENDER가 있는 방의 정리 시간이 없는 방의 1.3배를 넘지 않는다(봇의 시뮬레이션 시간으로 잰다).

## 7. 시험

**새 시험**(러너에 등록, quick)
- `tests/smoke/site7_regulars_registry_smoke.gd`: `site7_stage45_registry_smoke.gd`를 본보기로. 두 로봇의 등록, 런타임 그림 바인딩, 8방향이 서로 다른 그림인지, 방향마다 방출구 좌표, 소리·효과 프로필, 금지 문자열이 id에 없는지, 보스가 아닌 일반 로봇으로 처리되는지.
- `tests/smoke/site7_regulars_tactics_smoke.gd`: 실제 `Site7EnemyTactics`로 30/60/120 Hz.
  - LANCER: 경고 ≥ 1.4 s, 경고 중 피해 0, 잠긴 선과 투사체 방향이 같다, 엄폐 뒤 사격은 막힌다, 경직이면 취소된다, 쿨다운 ≥ 3.2 s.
  - TENDER: 고르기(가장 다친 로봇), 8 s 치료 상한, 보스 제외, 연결 끊김 조건, 최대 체력 초과 없음, 쓰러진 로봇 불가, 마지막 로봇일 때 OVERLOAD 경고와 한 번의 처치, 방이 닫힌다.
- 음성 대조: 규칙마다 일부러 깬 사본(치료 상한 제거, 경고 제거, 보스에 연결, OVERLOAD 제거)이 시험에서 실패해야 하고, 실패한 검사 수를 기록한다.
- `site7_enemy_facing_smoke.gd`가 새 두 로봇의 8방향 조준, 첫 프레임, 예고 잠금, 반대 방향 회복을 같은 방식으로 돈다.

**고치는 시험**은 5절 목록. 기존 시험의 검사 수는 줄지 않는다.

## 8. 배치 (사용자의 난이도 결정)

그림과 등록과 시험이 끝나도 **어느 작전에도 넣지 않는다.** 배치는 항목 1C처럼 미션 JSON만 바꾸는 **단독 커밋 하나**여서 `git revert` 한 번이 이전 난이도로 되돌린다.

- 권장 첫 배치: 작전 9의 R02에 LANCER 하나(DRONE 한 마리를 바꿔 넣음), R04에 TENDER 하나(PRISM 한 마리를 바꿔 넣음). 이유: 그 작전의 봇이 6번 중 6번 탈출해서 변화가 읽힌다. 로봇 수, 체력 합, 보상은 그대로 두고 `new_enemy_ids`에 새 id를 넣는다.
- 주제 배치(LANCER는 작전 8의 선로, TENDER는 작전 6의 수경 구역)는 사람이 한 번 플레이한 뒤에 정한다. 봇이 아슬아슬한 작전 3·6·7·8·10에는 처음에 넣지 않는다.
- 새 로봇이 나오는 방마다 `deploy_warmer`, `site7_robot_roster_smoke`의 "새 종류가 실제로 나온다" 검사, 같은 세션 회전 FPS 비교(`tools/maintenance/per_operation_fps.py`)를 돌린다.

## 9. 검증과 기록

1. 두 로봇 원본이 알파 검사를 통과한다. 원본 크기로 밝은 배경과 어두운 배경 위에서 가장자리와 내부를 본다.
2. `python tools/maintenance/run_regression_suite.py`(quick)와 `--suite full`. 새 시험과 고친 시험은 `--only`로 먼저, 끝에 quick 전체 한 번. 지워진 키는 `grep`으로 tests와 tools 전체에서 찾는다(앞 작업에서 풀 전용 시험이 놓친 적이 있다).
3. 1080p 캡처: 두 로봇의 8방향 한 장씩(게임 크기와 원본 크기 크롭), 일반 로봇 여덟을 같은 크기로 나란히 놓은 한 장, 방 안의 실제 장면(LANCER의 예고 선과 발사, TENDER의 연결선과 OVERLOAD).
4. 전투 영상 각 10초, 게임 소리 포함(`tools/environment/record_stage_battle_with_audio.py`, 600프레임·10초·소리 확인). `SABLE_CAPTURE_ROOT`는 임시 폴더로 돌린다.
5. `validate_visual_evidence_1080p.py --require-dynamic-capture`를 모든 검토 이미지와 영상에 돌린다.
6. 기록: `qa/site7_new_regulars_<날짜>/README_KO.md`와 위 증거. 마지막 줄에 "이 기록은 그림·플레이·균형 승인이 아니다."

## 10. 순서와 멈출 지점

1. **원화**: 마스터 → 8방향. 로봇당 약 9장, 실패를 감안해 로봇당 12–14번 정도의 ImageGen 호출. 각 장마다 알파 검사.
2. **등록과 전술**: 5·6절(Claude).
3. **시험과 대조**: 7절.
4. **검증**: 9절을 한 뒤 **멈추고 사용자에게 보고한다.** 배치는 8절대로 사용자 결정 뒤에.

**중단(HOLD) 조건**
- 한 장이 ImageGen 3번 안에 알파 규칙이나 1절의 형태 규칙(사람형 금지, 방향이 맞는 면, 반전 금지)을 맞추지 못하면 그 방향을 HOLD로 기록하고 후보를 보존한 채 보고한다.
- 8방향 중 앞과 뒤가 같은 그림이거나, 마스터와 방향 그림의 부속품 수가 다르면 그 장은 거절이다.
- 풀플레이가 새 로봇 때문에 새로운 종류로 실패하면 공정성 한계 안에서 수치를 조정한다. 한계나 시험 기준은 낮추지 않는다.

## 11. 사용자의 몫

- 두 로봇의 그림 승인(승인 전에는 이 그림을 승인된 것으로 쓰지 않는다. `verify_hashes.py` 방식의 해시 기록을 승인 때 만든다).
- 8절의 배치와 난이도, 이름, 두 로봇을 다 만들지 하나만 만들지(TENDER가 더 크다).
- 사람 플레이(`playtest_logs/`에 기록된다).
