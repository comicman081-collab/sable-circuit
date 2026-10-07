# SITE-7 작전 6–10 보스 5기와 공격 패턴 — Codex 작업 지시서

작성: 2026-09-29. 대상: 이 저장소에서 작업하는 Codex. 사용자 지시(2026-09-29): "작전 즉, 스테이지를 10까지 확장해봐라."

작전마다 보스가 따로 있다(`AGENTS.md` "Boss robots and per-boss patterns"). 이 문서는 작전 6–10 보스 5기의 원화, 등록, 공격 패턴을 다룬다. 설계와 통합 절차는 `docs/production/SITE7_OPERATIONS_6_10_DESIGN_KO.md`가, 맵 판 75장은 `docs/production/SITE7_OPERATIONS_6_10_PLATES_CODEX_PROMPT_KO.md`가 다룬다. 형식은 작전 2·3 보스 지시서(`docs/production/SITE7_BOSS_ROBOTS_CODEX_PROMPT_KO.md`)를 따른다. 그 문서의 알파 규칙은 낡았다. 이 문서 1절이 지금 규칙이다.

**진행 상태 (2026-10-02).** 7절 순서 1(원화)은 Codex가 끝냈고, 순서 2–4(패턴 구조, 등록과 패턴, 검증)는 Claude가 끝냈다. 보스 5기는 프로필, 패턴, 효과 계열, 안내문까지 등록되어 있고 작전 파일의 보스 행이 자기 보스를 가리킨다. 작전 6은 2026-09-29 사용자 지시("작전 6 켜라")로, 작전 7과 8은 2026-09-30 사용자 지시("작전 7 켜라", "8 켜라")로, 작전 9는 2026-10-01 사용자 지시("작전 9 켜고")로, 작전 10은 2026-10-02 사용자 지시("작전 10 켜라")로 **켰다**(`staging`과 `deployable: false`를 지웠고 앞 작전의 디브리프가 알린다). AERATOR는 자기 방(R05_ATRIUM)에서, CRYO는 자기 방(R05_VAULT)에서, GANTRY는 자기 방(R05_TERMINAL)에서, INDEX SPIRE는 자기 방(R05_STACKS)에서, ORIGIN CORE는 자기 방(R05_CORE)에서 찍고 방 바닥 공정성 시험 `boss_room_fairness`를 통과했으며, 봇 풀플레이는 `full_op_06`, `full_op_09`, `full_op_10`이 통과했고 `full_op_07`은 지기도 하고 재실행에서 이기기도 한다(작전 9·10 기록의 6절). `full_op_08`은 봇이 이길 때도 지고(2026-10-01에는 4번 모두 보스방에서 졌다) 그 원인은 보스가 아니라 작전 구성이다(작전 8 기록의 "봇 풀플레이"). CRYO는 그 시험에서 3페이즈 축 레인을 900에서 300 px로 줄였고(아래 4.2절), GANTRY는 열기 전에 뒤 페이즈 준비 시간을 1.4·1.5초에서 1.6초로 늘렸고(같은 절), INDEX SPIRE는 열기 전에 메아리 준비 시간을 1.0초에서 1.3초로 늘렸고(4.3절), ORIGIN CORE는 열기 전에 마지막 단계의 예고를 1.2·1.3·1.55초에서 1.6초로 늘렸다(`ORIGIN_LATE_WINDUP`, 4.2절). 열 보스 모두 자기 방에서 찍혔고(보스 캡처의 시험대는 비었다) 열 작전이 모두 출격 가능하다. 실제 FPS(같은 세션 회전 A/B)는 작전별 도구가 없어 아직 못 쟀다. 켠 작전의 기록: `qa/site7_op6_enable_20260929/README_KO.md`, `qa/site7_op7_enable_20260930/README_KO.md`, `qa/site7_op8_enable_20260930/README_KO.md`, `qa/site7_op9_enable_20261001/README_KO.md`, `qa/site7_op10_enable_20261002/README_KO.md`. 기록: `qa/site7_ops_6_10_boss_integration_20260929/README_KO.md`. 아래 4절의 수치는 시작값이었고, 실제로 들어간 값과 바꾼 곳은 그 기록의 "지시서와 다른 점"에 있다.

Codex에 처음 보낼 메시지(순서 1, 끝남):

> `AGENTS.md`를 먼저 읽고, `docs/production/SITE7_OPERATIONS_6_10_BOSSES_CODEX_PROMPT_KO.md`를 끝까지 읽어라. **7절의 순서 1(원화)** 만 진행해라. 보스 5기의 원화를 만들어 알파 검사를 통과시키고, 새 5기와 기존 5기를 같은 크기로 나란히 놓은 1080p 검토 시트로 보고한 뒤 멈춰라.

---

## 0. 범위와 판정

- 작전 6–10의 보스 행은 이 지시서를 시작할 때 자리표시 `BOSS_SITE7_CARRIER_01`이었고, 계획한 보스는 각 작전 파일의 `staging.boss`에 있다. 등록을 끝내며 보스 행의 `enemy_id`를 새 id로 바꿨다(설계 문서 6절 B, 2026-09-29).
- 기존 보스 5종(ANCHOR, RELAY, REMNANT, FORGE, CARRIER)과 새 5종, 합쳐 10종이 실루엣, 공격 모양, 강조색, 안내문이 모두 달라야 한다.
- 보스 체력은 게이트가 순증을 요구한다: 620 → 710 → 820 → 1120 → 1380 → **1560 → 1740 → 1920 → 2100 → 2460**.
- 보스는 한 기씩 끝낼 수 있다. 작전 N의 판 15장과 보스가 모두 끝나야 그 작전을 켠다. 그래서 작전 6의 보스를 먼저 하는 순서가 맞다.

## 1. 반드시 지킬 규칙

- `AGENTS.md`의 적 규칙을 따른다.
  - 사람형 적은 0이다. 다리, 발, 무릎, 손 달린 팔, 머리·얼굴, 궤도·바퀴가 없다.
  - 보스는 고정 기계(`anchored_machine`)다. 그림 한 장, 고정된 뿌리, 보이는 방출구 하나다.
  - 방출구는 어느 방향에서 봐도 같은 것이어야 한다(꼭대기의 노드나 렌즈). 한쪽을 향한 포신은 안 된다. 그림 한 장을 전방향으로 쓰기 때문이다(`.agents/skills/sable-character-studio/references/enemy-facing.md`, ANCHOR 선례).
  - 로봇 그림에 색을 입히지 않는다. 엘리트 표식, 경고, 피격 효과는 그림 위에 코드로 그린다.
- 원화는 Codex 내장 ImageGen만 쓴다. 로컬 이미지 모델, 부분 칠, 합성은 쓰지 않는다.
- **알파 규칙**(`motion_lab_v1/source_alpha_policy.py`, 정책 `native_rgba_alpha_0_255_v2`, 사용자 2026-09-28):
  - 진짜 RGBA PNG(RGB는 거절). 배경 알파 0, 캔버스 네 모서리 알파 0, 알파 0인 픽셀이 화면의 10% 이상.
  - 보이는 픽셀의 80% 이상이 알파 250 이상이고 최대 알파도 250 이상이다. 내부는 254 또는 **255**다. 255는 이제 기본으로 허용된다. 254로 깎지 않는다.
  - 네이티브 최대 변 1024 이상(이전 보스 지시서 기준. 기존 보스 원본은 1254와 1334).
  - 녹색 배경으로 생성하거나, 받은 그림의 알파를 자르거나 키잉하지 않는다. 통과하지 못하면 HOLD다.
- 생성 참조 이미지는 저장소 안 파일만 쓴다.
- ImageGen 응답은 저장소로 옮기고 해시를 남긴다. 응답 JSON에 `projectCopy`와 SHA-256을 둔다(선례: `motion_lab_v1/qa/stage1_enemies_20260913/anchor_master_tool_response.json`).
- 생성한 작업 이미지는 작업이 끝날 때까지 지우지 않는다. 거절 후보는 격리 폴더에 해시와 사유를 적어 보존한다.
- 전투 효과는 코드로만 그린다. `scripts/vfx/vfx_painter.gd`를 통하고, 효과 층마다 프레임당 삼각형 배열 2개 이하다. 새 효과를 넣기 전에 같은 세션 A/B로 FPS를 잰다(`AGENTS.md`).
- 테스트는 `--out=res://.cache/...`로 쓴다. 플레이어의 저장과 설정은 건드리지 않는다.
- 검토 이미지와 영상은 네이티브 1920×1080이다. 전투 영상은 게임 소리를 포함한다(`tools/environment/record_stage_battle_with_audio.py`).
- 로컬 커밋만 한다. GitHub 작업과 웹 배포는 하지 않는다.
- Claude의 파일과 커밋은 건드리지 않는다. 작업 트리를 함께 쓰므로 자기 파일만 골라서 커밋한다.

---

## 2. 보스 5기

| 항목 | 작전 6 | 작전 7 | 작전 8 | 작전 9 | 작전 10 |
|---|---|---|---|---|---|
| id | `BOSS_SITE7_AERATOR_01` | `BOSS_SITE7_CRYO_01` | `BOSS_SITE7_GANTRY_01` | `BOSS_SITE7_ARCHIVE_01` | `BOSS_SITE7_ORIGIN_01` |
| 이름(`name`) | `AERATOR TOWER` | `CRYO COMPRESSOR` | `SIGNAL GANTRY` | `INDEX SPIRE` | `ORIGIN CORE` |
| 방 | R05_ATRIUM (`S6_R05`) | R05_VAULT (`S7_R05`) | R05_TERMINAL (`S8_R05`, 긴 접근 복도, 보스는 출구 끝) | R05_STACKS (`S9_R05`) | R05_CORE (`S10_R05`) |
| 체력 | 1560 | 1740 | 1920 | 2100 | 2460 |
| 패턴(`boss_pattern`) | `bloom_field` | `frost_sweep` | `rail_charge` | `echo_copy` | `null_convergence` |
| 강조색(`arena_accent`) | 라임 `#8fdc4a` | 분홍 `#ff7fc8` | 신호 노랑 `#ffd84a` | 청록 `#2fe0b4` | 따뜻한 흰색 `#f4efe8` |
| 실루엣 | 버섯: 넓은 갓과 가는 기둥 | 낮은 압축기 블록과 한쪽의 높은 라디에이터 벽(깃발) | T자: 기둥과 가로보 | 계단식 지구라트와 가는 바늘 | 뾰족한 결정 다발 |
| 이야기 | 수경재배동의 공조 탑. 응답 신호를 온실 안테나로 중계한다 | 저온 보관고의 압축기. 응답이 식지 않게 유지한다 | 자기부상 야적장의 신호 가트리. 발송 명령을 내보낸다 | 봉인된 저장고의 색인 첨탑. 서 있던 자리를 기억한다 | 근원 갱도의 핵심. 응답의 출처다 |

- id는 반드시 `BOSS_`로 시작하고 `BOSS`가 들어가야 한다. 보스 판정(고정, 페이즈 보호막, 체력바, 정보 보상)이 이 문자열로 걸린다. 위 id는 이미 게이트 형식(`BOSS_SITE7_<NAME>_01`)을 만족한다.
- id와 프로필 이름에 다음 문자열을 넣지 않는다. 다른 효과 계열로 잘못 들어간다: `ASTER`(예: MASTER), `ROOK`, `MICA`, `DRONE`, `SHIELD`, `PRISM`, `_RAM_`, `GUARD`, `PYLON`, `MORTAR`, `RIFLE`, `ANCHOR`, `FORGE`, `CARRIER`. 프로필 문자열(`motion_profile`, `projectile_profile`, `hit_vfx_profile`)에도 같은 규칙이다.
- 강조색은 10종이 서로 달라야 한다. 기존: ANCHOR 보라, RELAY 진홍, REMNANT 얼음 청백, FORGE 호박, CARRIER 청록(`#62c9eb`). CARRIER의 보라가 ANCHOR와 겹쳐 청록으로 바꾼 선례가 있다.

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

**`{DESIGN}` — AERATOR TOWER**

```
A bulbous hydroponic air-handler: a fat armoured pressure-vessel cap sits on a short, thick pedestal on a wide octagonal floor mount, like a mushroom cap on a stem. Bundled irrigation hoses and root-like cable runs hang from the cap's underside into the mount; two side-mounted planter-tank pods of unequal size cling to the pedestal. Lime-green status slits run along the armour. The emitter is a lime-green spore-bloom node crowning the cap, wrapped by five armoured petal-shaped louvres that stand open like a flower bud (petals, not rings). Overall shape: a wide cap over a narrow stem, with asymmetric side pods.
```

**`{DESIGN}` — CRYO COMPRESSOR**

```
A refrigeration compressor stack bolted to a heavy skid: a low, wide compressor block with coolant manifolds and vacuum-jacketed pipes wrapped around it, and on one side a tall, flat radiator wall of frost-rimed heat-rejection fins that rises above the block like a sail. Hot-pink status lamps sit in the frost-white armour. The emitter is a hot-pink beacon node on a short open lattice mast rising from the middle of the compressor block, just clear of the fin wall. Overall shape: a low block with one tall flat wall on one side, asymmetric, all faces flat-sided; no round faces and no visible circular ends.
```

**`{DESIGN}` — SIGNAL GANTRY**

```
A signal gantry machine: one heavy central mast rises from a rectangular buffer-stop base and carries a wide horizontal cross-beam, so the machine makes a T shape. The beam is hung with banks of signal lamps, cable drapes and two counterweight blocks of unequal size. Yellow-and-black hazard striping on the base only. The emitter is a single signal-yellow lens cluster at the centre top of the cross-beam that reads the same from every direction. Overall shape: wide at the top, narrow at the bottom, a clear T.
```

**`{DESIGN}` — INDEX SPIRE**

```
A stepped memory-stack ziggurat: four tiers of slotted memory-blade shelving narrow upward from a wide base, with fibre-optic trunk cables running down the tiers into the floor mount and indigo status slits along the armour. A slender needle-shaped read-head rises from the top tier. The emitter is a turquoise node at the needle's tip. Overall shape: a wide stepped pyramid with one thin needle on top.
```

**`{DESIGN}` — ORIGIN CORE**

```
A jagged crystalline core machine: three interlocking black-alloy prisms of different heights are clamped by heavy structural ribs to a vast floor mount; hairline seams glowing white run along their faces and cable trunks feed the mount. The emitter is a single white node at the tip of the tallest prism. Overall shape: an irregular faceted cluster with one clear peak; no round parts, no ring, no iris.
```

**참조 이미지** (모두 저장소 안)
1. `assets/enemies/stage4_forge_warden/authored_core_v1/FORGE_WARDEN.png`: 카메라, 렌더 품질, 틀 안의 크기에만 쓴다. 모양을 옮기지 않는다.
2. 그 보스의 방 판(`assets/environments/site7_v2/stage06/S6_R05/S6_R05_GAME.png` 등, 판이 반입된 뒤): 재질과 색 맥락에만 쓴다. 판이 아직 없으면 생략한다.
3. `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png`: 재질 품질.

**구분 기준**
- 열 보스(ANCHOR, RELAY, REMNANT, FORGE, CARRIER + 새 5기)를 같은 크기로 나란히 놓았을 때 실루엣이 모두 달라야 한다. 특히 RELAY(낮고 넓은 코일 탑)와 CRYO(낮은 블록과 한쪽 벽), REMNANT(가늘고 높은 기둥)와 ARCHIVE(넓은 계단식)를 나란히 놓고 확인한다.
- 새 다섯 보스에는 둥근 홍채, 동심원, 원형 포털이 없어야 한다.
- 보스가 자기 방 뒷벽의 구조물과 똑같아 보이면 안 된다. 방은 배경, 보스는 그 앞의 기계다.

### 2.2 파일

| 종류 | 위치 |
|---|---|
| 원본(ImageGen 그대로) | `motion_lab_v1/art/site7_enemies_raw/<이름>_master.png` (`aerator_tower`, `cryo_compressor`, `signal_gantry`, `index_spire`, `origin_core`) |
| 런타임 | `assets/enemies/stage6_aerator_tower/authored_core_v1/AERATOR_TOWER.png`, `stage7_cryo_compressor/…/CRYO_COMPRESSOR.png`, `stage8_signal_gantry/…/SIGNAL_GANTRY.png`, `stage9_index_spire/…/INDEX_SPIRE.png`, `stage10_origin_core/…/ORIGIN_CORE.png` |
| 명세 | 같은 폴더 `spec.json` |
| 격리 | `motion_lab_v1/qa/site7_enemies_raw/quarantine/<이름>/attemptNN.png` (선례: `resonance_remnant/attempt01.png`) |

- 런타임 PNG는 원본 그대로(크롭·축소 없이)를 기본으로 한다. `.import`는 `compress/mode=0`, `mipmaps/generate=false`.
- `spec.json`은 FORGE/RELAY 형식이다: `schema_version: 1`, `enemy_id`, `kind: "anchored_machine"`, `texture`(`res://` 경로), `texture_sha256`, `display_height`(RELAY 230), `root_px`(바닥 고정점, 원본 픽셀), `emitter_px`(방출구 중심, 원본 픽셀), `emitter_visible: true`, `emission_contract`(한 줄: 방출구가 하나이고 어느 방향에서도 같다는 것). 본보기: `assets/enemies/stage2_relay_sentinel/authored_core_v1/spec.json`.
- 기록: `qa/site7_ops_6_10_bosses_<날짜>/`
  - `boss_asset_gate.json`: 형식은 `qa/site7_boss_robots_20260928_final/boss_asset_gate.json`과 같다. `source_alpha_policy`는 위 `native_rgba_alpha_0_255_v2`다.
  - ImageGen 응답 JSON(`projectCopy`, SHA-256), 최종 프롬프트 전문, 시도 횟수, 거절 사유

### 2.3 등록

작전 2의 RELAY 등록이 본보기다(커밋 `dc6cd290`). `grep -rn "RELAY" scripts tests data tools`로 나오는 자리를 새 보스마다 모두 채운다. 현재 자리(줄 번호는 2026-09-29 기준이라 밀릴 수 있다):

**데이터**
- `data/art_profiles/enemy_profiles.json`: RELAY 행을 본보기로 다섯 행을 넣는다.
  - `tier: "BOSS"`, `body_plan: "robot"`, `runtime_enabled: true`
  - `motion_profile`: `MOT_BOSS_AERATOR_01` 형식
  - `projectile_profile`: `PRJ_BOSS_<이름>_<탄>_01` (예: `PRJ_BOSS_AERATOR_SPORE_01`)
  - `hit_vfx_profile`: `HIT_BOSS_<이름>_<효과>_01` (예: `HIT_BOSS_AERATOR_BLOOM_01`)
  - `fire_sfx_profile`은 `SFX_FIRE_BOSS_ANCHOR_01`, `impact_sfx_profile`은 `SFX_HIT_BOSS_ANCHOR_01`을 그대로 쓴다(RELAY와 같다). `rig_sheet`는 `""`.
  - `palette`(어두운 기본, 강조, 발광), `silhouette`, `master_asset`, `machine_asset`(spec 경로와 **spec.json 파일**의 SHA-256), `introduced_in`
  - `boss_pattern`(4절), `boss_brief`(4.4), `arena_accent`(2절 표)
- `data/art_profiles/site7_enemy_body_plan.json`: `active_enemy_ids`와 `roles`에 추가한다. `locomotion: "anchored"`. (`motion_lab_v1/tests/test_enemy_body_plan.py`가 미션 파일의 모든 `enemy_id`가 여기 있는지 검사한다.)
- `data/missions/MIS_CH01_0N.json`: 보스 행의 `enemy_id`를 새 id로 바꾸고 `new_enemy_ids`에 넣는다. 체력, 위치, 지원 행, 증원은 그대로다. `staging` 블록은 작전을 켤 때 지운다.
- `data/visual/site7_battle_layouts.json`의 `boss_anchor`는 새 그림의 발판이 방 바닥과 엄폐에 겹치지 않는지 확인하고 필요하면 옮긴다.

**id로 묶인 코드** (새 id를 넣지 않으면 공격을 안 하거나 등록에 실패한다)
- `scripts/combat/site7_enemy_tactics.gd`: `ROLES`(11줄 근처) → `"boss"`, `_boss_attack`의 `match`(306줄)에 다섯 패턴
- `scripts/animation/site7_machine_sprite.gd`: `expected_kind`(169줄 근처) → `"anchored_machine"`, 방출구 빛과 테두리 색(370줄 근처)
- `scripts/actors/enemy_actor.gd`: `_projectile_color`(472줄 근처), 레거시 뼈대를 만들지 않는 목록(511줄 근처)
- `scripts/animation/enemy_detail_overlay_presentation.gd`: 건너뛰기 목록(20줄 근처)
- 보스방 연출과 안내문은 프로필의 `arena_accent`, `boss_brief`를 읽으므로 id를 넣을 필요가 없다(`boss_arena_presentation.gd`, `enemy_overhead_ui.gd`, `story_stage_01.gd`).

**효과 계열** (프로필 문자열로 찾는다. `AERATOR`, `CRYO`, `GANTRY`, `ARCHIVE`, `ORIGIN`을 `ANCHOR` 검사보다 앞에 넣는다)
- `scripts/vfx/combat_hit_vfx.gd`: `FAMILIES`(29줄 근처), `family_for`(95줄 근처), 보스 충격 크기 목록(126줄), 그리기 분기(403줄 근처). 다섯 계열의 피격 효과를 새로 그린다: AERATOR 포자 구름이 피어나는 파열, CRYO 서리 파편, GANTRY 노란 아크 스파크, ARCHIVE 청록 글리프 흩어짐, ORIGIN 흰 균열.
- `scripts/vfx/combat_muzzle_vfx.gd`: 지속 시간 표(12줄), `family_for`(45줄), 그리기 분기(196줄 근처), 보스 목록(256줄)
- `scripts/combat/prototype_projectile.gd`: 크기 표(19줄), `ANIMATED`(22줄), 속도·피해·수명 조정(165줄 근처), 그리기 분기(265줄 근처). 피해는 ANCHOR(24) 이하로 한다.
- `tests/smoke/combat_vfx_overhaul_smoke.gd`의 삼각형 예산과 자기 해제 검사를 통과해야 한다.

**도구와 테스트의 보스 표**
- `tools/environment/record_stage_battle_with_audio.py`(131줄 근처 `expected`: 작전 번호 → 보스 id. 작전 번호 허용 목록과 `MIS_CH01_0{number}` 형식은 설계 문서 6절 A 8단계), `tests/render/site7_boss_pattern_capture.gd`(`BOSS_IDS`)
- 5절 목록

---

## 3. 구조

- `enemy_profiles.json`의 `boss_pattern` 값으로 `_boss_attack`이 패턴을 고른다. 새 값: `bloom_field`, `frost_sweep`, `rail_charge`, `echo_copy`, `null_convergence`. 기존 값(`anchor_iris`, `relay_chain`, `resonance_lanes`, `forge_press`, `carrier_null`)과 그 동작은 바꾸지 않는다.
- 부품은 지금 있는 세 가지만 쓴다.
  - 투사체: `_fire(direction)`
  - 원형 경고: `_warning("circle", 위치, 방향, 반지름, 길이, 반폭, 준비 시간)`
  - 직선 레인 경고: `_warning("lane", 시작점, 방향, 58.0, 길이, 반폭, 준비 시간)`. 레인은 시작점에서 방향으로 `길이`만큼 뻗는다.
- `_warning`은 이미 반지름, 길이, 반폭, 준비 시간을 받는다. 시그니처를 바꾸지 않는다.
- 공격 A는 홀수 `attack_serial`, 공격 B는 짝수 `attack_serial`이다. 페이즈 `phase`는 1–3이다.
- 페이즈 경계(체력 66 %, 33 %), 3페이즈 보호막(`boss_phase_transition_guard.gd`, 8초 CORE SHIELDED), 회복 시간 공식은 그대로다.

### 3.1 공정성 규칙 (모든 패턴, `tests/smoke/site7_boss_pattern_smoke.gd`가 검사)

- 모든 피해는 먼저 경고된다. 경고 준비 시간은 1.0초 이상이다.
- 한 번의 공격이 만드는 경고는 7개 이하다.
- 경고 하나의 피해는 20 이하, 투사체 피해는 24 이하다.
- 대상 주변 300 px 안(반경 120, 180, 240, 300)에 대원 폭의 1.5배 이상 되는 폭으로 경고가 덮지 않는 바닥이 늘 있어야 한다.
- 다섯이 아니라 **열 보스가 같은 페이즈에서 같은 모양**(투사체·원·레인 개수의 조합, 공격 A/B 쌍)이 되면 안 된다.

## 4. 보스별 공격 패턴

`대상`은 보스가 고른 조작 대원 `T`, `B`는 보스 위치, `g`는 `locked_ground`(보스→대상 방향), `s`는 `g.orthogonal()`이다. 수치는 **시작값**이다. 풀플레이와 공정성 규칙에 맞게 조정해도 되지만 경고를 없애거나 규칙을 넘기지는 않는다. 시그니처 `S<투사체>C<원>L<레인>`은 공격 A/공격 B 순서로 적었다(`site7_boss_pattern_smoke.gd`의 표기).

### 4.1 요약

| 패턴 | 1페이즈 A / B | 2페이즈 A / B | 3페이즈 A / B | 피하는 법 |
|---|---|---|---|---|
| `bloom_field` (AERATOR, 작전 6) | 고리 원 4개 / 고리를 45° 돌린 4개 — `S0C4L0 / S0C4L0` | 고리 5개 + 중심 원 1개 / 포자 볼트 3발 — `S0C6L0 / S3C0L0` | 고리 6개 + 중심 원 / 30° 돌린 고리 6개 + 중심 원 — `S0C7L0 / S0C7L0` | 중심이 피기 전에 벗어나 고리의 틈으로 나간다 |
| `frost_sweep` (CRYO, 작전 7) | 서리 막대 2개(바깥으로 번짐) / 얼음 파편 2발 — `S0C0L2 / S2C0L0` | 막대 3개 / 막대 4개 — `S0C0L3 / S0C0L4` | 막대 4개 + 축 레인 / 같은 것을 안쪽으로 번지게 — `S0C0L5 / S0C0L5` | 방금 지나간 막대의 틈으로 들어가고 압축기에 붙지 않는다 |
| `rail_charge` (GANTRY, 작전 8) | 대상 위 십자 레인 / 충돌 원 — `S0C0L2 / S0C1L0` | 십자 + 대각 레인 / 양쪽 끝 원 2개 — `S0C0L3 / S0C2L0` | 별 모양 레인 4개 / 별 + 대상 원 — `S0C0L4 / S0C1L4` | 교차점을 떠나 레인 사이 쐐기 안으로 들어간다 |
| `echo_copy` (ARCHIVE, 작전 9) | 지금 자리 원(+기억한 자리) — `S0C1L0 / S0C2L0` | 지금 자리 + 기억한 자리 2개 — `S0C3L0 / S0C3L0` | 지금 + 기억 3개 / 같음 + 보스→대상 레인 — `S0C4L0 / S0C4L1` | 멈추지 않고, 같은 길을 되밟지 않는다 |
| `null_convergence` (ORIGIN, 작전 10) | 수렴 레인 3개 / 대상 원 + 볼트 2발 — `S0C0L3 / S2C1L0` | 수렴 레인 4개 / 보스 원 + 대상 원 + 볼트 2발 — `S0C0L4 / S2C2L0` | 수렴 레인 5개 + 대상 원 / 수렴 3개 + 보스 원 + 대상 원 — `S0C1L5 / S0C2L3` | 레인 사이 틈에 서고 코어에 붙지 않는다 |

기존 시그니처(같은 페이즈에서 겹치면 안 되는 목록):

| 페이즈 | ANCHOR | RELAY | REMNANT | FORGE | CARRIER |
|---|---|---|---|---|---|
| 1 | `S3C0L0 / S3C0L0` | `S0C3L0 / S0C3L0` | `S0C0L3 / S0C0L3` | `S0C1L0 / S2C0L0` | `S2C0L1 / S2C0L1` |
| 2 | `S5C0L0 / S0C1L0` | `S0C5L0 / S2C0L0` | `S0C0L3 / S0C1L2` | `S0C2L0 / S2C0L0` | `S0C0L3 / S0C0L3` |
| 3 | `S5C0L0 / S0C1L4` | `S0C7L0 / S2C0L0` | `S0C0L5 / S0C1L2` | `S0C2L2 / S2C0L2` | `S0C1L3 / S0C1L3` |

RELAY의 값은 스모크의 대원 3명(조작 1 + 동료 2) 기준이다. 새 패턴이 위 표와 같아지지 않는지 스모크가 검사한다.

### 4.2 패턴 상세

**`bloom_field` — 포자 고리 (AERATOR TOWER)**
- 고리 원: `T` 주위 반지름 190 px(2·3페이즈 200·210 px)의 고리에 원(반지름 64)을 `n`개 놓는다. 각도는 `g`의 각도 + `TAU * i / n` + 회전(공격 B는 45°(1페이즈), 30°(3페이즈)). 준비 시간은 `1.2 + 0.1 * i`초로 하나씩 순서대로 열린다.
- 중심 원(2·3페이즈): `T` 위치에 원(반지름 70), 준비 시간 1.7초. 가만히 서 있으면 맞는다.
- 2페이즈 공격 B: 포자 볼트 3발(`locked_aim` ± 0.3 rad).
- 브리핑 문장과 맞춘다: "Spore rings close in around you."

**`frost_sweep` — 서리 훑기 (CRYO COMPRESSOR)**
- 서리 막대는 보스→대상 축에 **수직**인 레인이다: 시작점 `B + g * d - s * 350`, 방향 `s`, 길이 700, 반폭 30. 막대 간격은 150 px. 구현은 `d = 130 + 150·i`(130, 280, 430, 580)이다: 가장 가까운 막대를 압축기에서 130 px 밖에 두어 발치에 서는 것도 공짜가 아니다.
- 준비 시간은 바깥으로 번진다: 가까운 막대부터 `1.1, 1.3, 1.5, 1.7`초. 3페이즈 공격 B는 먼 막대부터 시작해(`1.7 … 1.1`) 안쪽으로 번진다.
- 1페이즈 공격 A: 막대 2개(`d = 130, 280`). 공격 B: 얼음 파편 2발(`locked_aim` ± 0.2 rad).
- 2페이즈 A: 막대 3개, B: 막대 4개.
- 3페이즈: 막대 4개 + 축 레인 1개(`B`에서 `g`로 길이 **300**, 반폭 22, 준비 1.4초). A는 바깥으로, B는 안쪽으로 번진다. 축 레인은 두 번째 막대까지 가서 멈춘다(`FROST_AXIS_REACH`). 처음 값 900은 작전 7의 R05_VAULT 좁은 바닥(서쪽 턱, 문 어귀)에서 대상 옆에 1.5명 폭의 빈 바닥을 남기지 않았다(`boss_room_fairness`, 25 px 격자에서 10곳). 340 px 이하는 그 시험을 통과하고 400 px는 실패하므로 `boss_pattern`이 300을 고정하고 340 이하만 허용한다.

**`rail_charge` — 레일 교차 (SIGNAL GANTRY)**
- 십자: `T`를 지나는 레인 2개. 방향 `g`와 `s`, 각각 시작점 `T - dir * 550`, 길이 1100, 반폭 26, 준비 1.4초. `T`의 자리는 덮인다. 1.4초 안에 벗어나야 한다.
- 1페이즈 공격 B: 충돌 원(`T`, 반지름 100, 준비 1.2초).
- 2페이즈 공격 A: 십자에 +45° 대각 레인 1개(반폭 22)를 더한다. 셋 모두 준비 **1.6초**(`GANTRY_LATE_WINDUP`). 공격 B: `T ± s * 160`에 원 2개(반지름 90, 준비 1.2초).
- 3페이즈 공격 A: 별 모양 레인 4개(`g`, +45°, +90°, +135°, 반폭 20, 준비 **1.6초**). 공격 B: 별을 22.5° 돌리고 `T` 원(반지름 90, 준비 1.6초)을 더한다.
- 뒤 페이즈의 1.6초: 처음 값(대각 십자 1.4초, 별과 그 원 1.5초)은 작전 8의 R05_TERMINAL 바닥에서 벽 옆의 가장 가까운 빈 쐐기가 180 px 밖이 되는 자리가 있어, 가장 느린 걸음(138 px/s)이 1.30초 걸리는 그곳에 0.10–0.20초밖에 남기지 않았다(`boss_room_fairness` 50 px 격자, 1,410번 중 101번 실패. 한계는 0.25초). `boss_pattern`이 1.56초를 하한으로 고정한다.
- 브리핑 문장과 맞춘다: "Rail lines cross where you stand."

**`echo_copy` — 메아리 (INDEX SPIRE)**
- 전술 객체에 `_echo_points: Array[Vector2]`(최대 3개, 먼저 들어온 것부터 버린다)를 둔다. 페이즈가 바뀌어도 지우지 않는다. 보스가 새로 만들어질 때만 비어 있다.
- 공격마다: (1) `T` 위치에 원(반지름 70, 준비 **1.6초**)을 놓고, (2) 기억한 자리 중 최근 것부터 `min(저장 수, phase)`개에 원(반지름 70, 준비 `1.3 + 0.1 * i`초, `ECHO_WINDUP`)을 놓고, (3) `T`를 저장한다. 첫 공격에는 기억이 없으므로 원이 1개다. 메아리가 먼저 터지고 대상의 지금 자리가 맨 나중이다.
- 3페이즈 공격 B는 보스→대상 레인 1개(길이 900, 반폭 22, 준비 **1.7초**)를 더한다.
- 준비 시간이 1.3초부터인 까닭: 처음 값(지금 자리 1.3초, 메아리 `1.0 + 0.1 * i`초, 레인 1.4초)은 작전 9의 R05_STACKS에서 실패했다. 가만히 선 대상에게는 메아리가 모두 한 자리에 쌓여서 가장 새 메아리가 떠날 시간의 전부인데, 벽 옆의 가장 가까운 빈 바닥이 120 px(가장 느린 걸음 138 px/s로 0.87초)이라 1.0초에서는 0.13초가 남았다(한계 0.25초. `boss_room_fairness` 25 px 격자에서 4,524번 중 2번, 모두 3페이즈 공격 B). 1.3초에서는 0.43초가 남고 20–100 px 격자 여덟 가지가 모두 통과한다. `boss_pattern`이 1.12초(그 걸음 + 한계)를 바닥으로 박았다.
- 브리핑 문장과 맞춘다: "The spire echoes where you stood a moment ago."

**`null_convergence` — 수렴 (ORIGIN CORE)**
- 수렴 레인: `T` 주위 각도 `g의 각도 + TAU * i / n`(n = 3, 4, 5), 시작점 `T + dir * 420`, 방향 `-dir`, 길이 460(`T`를 40 px 지난다), 반폭 20(3페이즈 22), 준비 1.3초(3페이즈는 `ORIGIN_LATE_WINDUP` 1.6초). `T`의 자리는 모든 레인이 덮는다.
- 보스 원: `B`에 원(반지름 150, 준비 1.2초, 3페이즈는 `ORIGIN_LATE_WINDUP` 1.6초). 코어에 붙지 않게 한다.
- 대상 원: `T`에 원(반지름 90, 준비 1.2초, 3페이즈는 `ORIGIN_LATE_WINDUP` 1.6초). 3페이즈의 1.2·1.3·1.55초는 작전 10의 실제 R05_CORE에서 `boss_room_fairness`를 재 보고 열기 전에 1.6초로 늘렸다(커밋 `749ff72b`).
- 1페이즈 공격 B: 대상 원 + 볼트 2발(±0.25 rad). 2페이즈 공격 B: 보스 원 + 대상 원 + 볼트 2발. 3페이즈 공격 B: 수렴 3개 + 보스 원 + 대상 원.
- 브리핑 문장과 맞춘다: "Warning lanes converge on you from every side."

### 4.3 공정성 사전 점검 (계산으로 확인한 값)

- 수렴/별 레인 사이 쐐기: 5개 레인(72°), 반폭 20이면 `T`에서 180 px 떨어진 곳의 빈 폭이 186 px이다. 4개(45°)의 별은 240 px에서 148 px이다. 대상 폭의 1.5배(약 60 px)를 넘는다.
- 고리 원 6개(반지름 64, 고리 반지름 210): 인접한 원 사이 빈 폭 82 px. 구멍으로 빠질 수 있다.
- 서리 막대 간격 150 px, 반폭 30: 막대 사이 빈 폭 90 px.
- 스모크의 안전 틈 검사는 반경 120–300 px 원 위에서 폭 1.5배의 빈 자리를 찾는다. 위 값은 모두 통과하는 계산이지만 실제 실행이 기준이다.

### 4.4 보스방 연출과 안내문

- 단상과 기둥 색은 프로필 `arena_accent`에서 온다(2절 표). 체력바 강조색도 같다.
- `boss_brief`(브리핑 화면과 보스방 안내문):

| 보스 | `boss_brief` |
|---|---|
| AERATOR | `Spore rings close in around you. Leave the middle before it blooms and slip out through a gap; shots are blocked while CORE SHIELDED.` |
| CRYO | `The compressor sends frost bars outward in waves. Step into the gap a bar has just cleared and do not hug the stack; shots are blocked while CORE SHIELDED.` |
| GANTRY | `Rail lines cross where you stand. Leave the crossing and keep off the rails; shots are blocked while CORE SHIELDED.` |
| ARCHIVE | `The spire echoes where you stood a moment ago. Never stop and never walk the same line twice; shots are blocked while CORE SHIELDED.` |
| ORIGIN | `Warning lanes converge on you from every side. Stay in the gaps between them and keep away from the core; shots are blocked while CORE SHIELDED.` |

## 5. 테스트

**고칠 테스트** (보스 목록을 가지고 있다)
- `tests/smoke/site7_boss_pattern_smoke.gd`: `OTHER_BOSSES`에 새 보스를 넣고 `signatures`에 그 시그니처를 채운다. 새 5기의 공격 A/B 시그니처가 4.1 표와 같은지, 기존 5기와 같은 페이즈에서 겹치지 않는지 확인한다. 음성 확인(두 보스의 `boss_pattern`을 메모리에서 같게 만들면 FAIL)은 유지한다.
- `tests/smoke/site7_robot_roster_smoke.gd`: `ALLOWED`, `NEW_IDS`(작전 6–10이 새 보스만 `new_enemy_ids`에 넣는지)
- `tests/smoke/site7_boss_registry_smoke.gd`: `BOSSES`(작전 → 보스 id)
- `tests/smoke/site7_emission_owner_smoke.gd`: `ROLE_BY_ID`와 보스별 기대 투사체 수
- `tests/smoke/combat_vfx_overhaul_smoke.gd`: `ENEMY_FAMILIES`, `PROJECTILE_FAMILIES`
- `tests/smoke/site7_full_operation_smoke.gd`(87줄 근처): 보스별 투사체 개수 기대값. 경고 없는 투사체를 막는 검사는 유지한다.
- `tests/smoke/deploy_warmer_smoke.gd`: 작전 6–10이 새 보스 그림을 미리 읽는지
- `tests/smoke/site7_campaign_data_smoke.gd`: 보스 등록 검사가 이제 그 작전을 "출격 가능"으로 볼 때 통과해야 한다(설계 문서 7절).

**새 패턴이 지키는 것** (스모크가 기계적으로 검사)
- 공격당 경고 7개 이하, 준비 시간 1.0초 이상, 경고 피해 20 이하, 투사체 피해 24 이하
- 대상 주변 300 px 안에 폭 1.5배의 빈 바닥
- 모든 투사체는 그 공격에서 나온 것이다(경고 없는 발사 없음)

## 6. 검증과 기록

1. 새 보스 원본이 `source_alpha_policy.py` 알파 검사를 통과한다. 원본 크기로 밝은 배경과 어두운 배경 위에서 가장자리와 내부를 확인한다.
2. `python tools/maintenance/run_regression_suite.py`(quick)와 `--suite full`이 PASS한다. 켠 작전의 풀플레이(`full_op_0N`)를 본다. `full_op_03`은 봇이 약 3번에 1번 전멸한다. FAIL이 한 번 나오면 다시 돌린다. 같은 보스에서 계속 전멸하면 그 패턴의 수치를 공정성 규칙 안에서 조정한다.
3. 1080p 게임 캡처
   - 새 보스를 자기 방에서 게임 크기로 찍는다. 원본 크기 크롭도 함께 둔다.
   - 열 보스를 같은 크기로 나란히 놓은 한 장
   - 보스별 경고 모양: 페이즈마다 한 장씩, 새 보스 5기(`tests/render/site7_boss_pattern_capture.gd`)
4. 전투 영상: 새 보스 각각 10초, 게임 소리 포함(`record_stage_battle_with_audio.py`). 600프레임, 10초, 소리가 들어 있는지 확인한다.
5. `tools/art_pipeline/validate_visual_evidence_1080p.py --require-dynamic-capture`를 모든 검토 이미지와 영상에 돌린다.
6. 기록: `qa/site7_ops_6_10_bosses_<날짜>/README_KO.md`와 위 증거
7. 로컬에 커밋한다.

## 7. 순서와 멈출 지점

1. **원화**: 보스 5기를 만들고 알파 검사와 원본 크기 검수, 열 보스 나란히 비교를 한다. **멈추고 보고한다.** (Codex, 끝남)
2. **패턴 구조**: 새 `boss_pattern` 값을 `_boss_attack`에 넣는다. 기존 다섯 패턴이 그대로인지 `site7_boss_pattern_smoke.gd`의 기준값(anchor 고정 포함)으로 먼저 확인한다. (Claude, 끝남 2026-09-29)
3. **등록과 패턴**: 보스를 하나씩 등록하고 패턴, 효과 계열, 투사체 조정, 연출, 안내문을 넣는다. 작전 6 → 10 순서다. (Claude, 끝남 2026-09-29)
4. **검증**: 6절을 한 보스가 끝날 때마다 한다. 작전의 판 15장이 이미 연결되어 있으면 그 작전을 설계 문서 6절 C로 켠다. 판이 아직 없으면 켜지 않고 보스까지만 끝낸다. (Claude, 보스까지만 끝냄: 작전 7–10은 판이 없고, 작전 6은 판이 들어왔지만 켜지 않음. 자기 방 캡처, 소리 영상, FPS는 작전이 열린 뒤)

- 예상 생성량: 5장 × 평균 2회 ≈ ImageGen 10회. 형태 규칙(사람형 금지, 전방향 방출구, 홍채 금지)과 알파를 함께 맞춰야 해서 늘 수 있다. 선례: 작전 2 RELAY는 6회를 시도해 4번째를 채택했고(알파 0..254 규칙 아래에서), 작전 3 REMNANT는 첫 시도를 채택했다. 지금은 알파 255가 허용되므로 알파 때문의 재시도는 줄어야 한다.

**중단(HOLD) 조건**
- 한 보스가 ImageGen 3회 안에 알파 규칙이나 1절의 형태 규칙을 맞추지 못하면 멈춘다. 그 보스를 HOLD로 기록하고 받은 후보를 보존한 채 보고한다.
- 풀플레이가 새 패턴 때문에 계속 실패하면 공정성 규칙 안에서 수치를 조정한다. 규칙이나 테스트 기준을 낮추지 않는다.
- 이 작업은 보스와 패턴의 연결과 검증까지다. 사람의 플레이 승인이나 배포 승인을 대신하지 않는다.
