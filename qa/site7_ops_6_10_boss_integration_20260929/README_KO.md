# SITE-7 작전 6–10 보스 5기: 등록, 패턴, 시험 (2026-09-29)

**판정: PASS_TECHNICAL_ONLY.** 코드와 자동 시험이 통과했다는 뜻이다. 그림, 균형, 플레이 승인이 아니다. 작전 6–10은 **켜지 않았다**(`deployable: false`와 `staging` 그대로). 작전 7–10은 판이 없다. 작전 6은 Codex가 판 15장을 이 작업 도중 커밋했지만(`d6e05d44`) 켜는 결정이 사용자에게 남았다(11절).

> **갱신 (2026-09-30).** 이 기록을 쓴 뒤 사용자가 "작전 6 켜라"고 지시해 작전 6을 켰다(`90b5572b`). 아래 11절의 1·2·4·5번과 12절의 작전 6 항목은 `qa/site7_op6_enable_20260929/README_KO.md`에서 끝났다: 작전 6 켜기, AERATOR 자기 방 캡처와 실제 바닥 공정성(`boss_room_fairness`), 작전 6 풀플레이(`full_op_06`), 작전 6의 게임 소리 영상. 그대로 남은 것: 작전 7–10은 켜지 않았다(이 문서의 "켜지 않았다"는 그 넷에 해당한다), 같은 세션 회전 A/B FPS, 사람의 그림·균형 확인. 이 문서의 8절 캡처는 그때의 시험대 기록이다.

사용자 지시(2026-09-29): "보스 등록·패턴(7절 순서 2–4)은 코드와 시험은 네가 해라." 근거 문서는 `docs/production/SITE7_OPERATIONS_6_10_BOSSES_CODEX_PROMPT_KO.md` 7절이다. 순서 1(원화)은 Codex가 끝냈고, 이 기록은 순서 2–4를 다룬다.

## 1. 한눈에

| 작전 | 보스 | id | 체력 | 패턴 | 강조색 |
|---|---|---|---:|---|---|
| 6 | AERATOR TOWER | `BOSS_SITE7_AERATOR_01` | 1560 | `bloom_field` | `#8fdc4a` |
| 7 | CRYO COMPRESSOR | `BOSS_SITE7_CRYO_01` | 1740 | `frost_sweep` | `#ff7fc8` |
| 8 | SIGNAL GANTRY | `BOSS_SITE7_GANTRY_01` | 1920 | `rail_charge` | `#ffd84a` |
| 9 | INDEX SPIRE | `BOSS_SITE7_ARCHIVE_01` | 2100 | `echo_copy` | `#2fe0b4` |
| 10 | ORIGIN CORE | `BOSS_SITE7_ORIGIN_01` | 2460 | `null_convergence` | `#f4efe8` |

- 각 보스는 프로필, 기계 명세, 패턴, 총구·피격·투사체 효과, 안내문, 보스방 강조색까지 등록되어 있고, 작전 파일의 보스 행이 자기 보스를 가리킨다(자리표시 `BOSS_SITE7_CARRIER_01`은 없어졌다).
- 원화는 Codex가 ImageGen으로 만든 마스터를 **한 바이트도 바꾸지 않고** 런타임에 넣었다(`tools/environment/build_site7_boss_runtime.py`, `--check`). 자르기, 키잉, 크기 변경, 재인코딩이 없다. 바인딩 기록은 `runtime_binding.json`이다.
- 기존 다섯 패턴(`anchor_iris`, `relay_chain`, `resonance_lanes`, `forge_press`, `carrier_null`)의 동작은 그대로다. 시험이 ANCHOR의 출하값을 고정해 놓고 비교한다.
- 작전 6–10은 계속 출격 불가다. 다른 작전의 판이나 보스 그림을 빌리거나 대용품을 그리지 않았다. 작전 6의 판은 Codex가 만든 그 작전 전용 15장이다.

## 2. 기계 명세와 표시

| 보스 | 원본 크기(px) | 기계 본체 `visible_rect_px` | 방출구 `emitter_px` | 바닥점 `root_px` | 게임 안 높이(월드 px) |
|---|---|---|---|---|---:|
| AERATOR | 1254×1254 | [379, 240, 888, 994] | (632, 324) | (632, 990) | 226 |
| CRYO | 1243×1265 | [34, 46, 1209, 1221] | (575, 246) | (412, 1216) | 236 |
| GANTRY | 1361×1156 | [24, 38, 1341, 1107] | (695, 123) | (697, 1103) | 236 |
| ARCHIVE | 1402×1122 | [200, 64, 1203, 1063] | (701, 86) | (701, 1060) | 246 |
| ORIGIN | 1190×1322 | [151, 22, 1047, 1285] | (614, 100) | (616, 1281) | 262 |

기존 보스는 RELAY 217, REMNANT 219, CARRIER 195, ANCHOR 266이다. 시험이 열 보스의 화면 높이가 중앙값의 0.8–1.25배 안인지 본다.

- `spec.json`의 새 선택 항목 `visible_rect_px`는 그림 안에서 기계 본체가 차지하는 사각형이다(없으면 그림 전체). `Site7MachineSprite.visible_rect`가 이것을 읽고 피격 상자(본체의 76×70 % 안쪽), 체력바 위치(본체 꼭대기 12 px 위, `EnemyOverheadUI.bar_y_local`), 총구 검사가 따른다. 새 마스터는 투명한 여백이 크다(AERATOR는 캔버스 376 px에 본체 226 px). 이것 없이 캔버스를 기준으로 삼으면 체력바가 허공에 뜨고 피격 상자가 실제 그림과 어긋난다.
- 보스는 생성 위치에 고정된다(`BossAnchorLockPresentation`). 그림 크기는 명세의 `display_height`다.
- **관찰(고치지 않음):** 보스 발밑의 타원 그림자(`EnemyGroundShadow`)는 모든 보스가 같은 크기(rx 74, ry 18)다. 새 기계의 바닥 모양(CRYO의 옆으로 긴 블록, GANTRY의 좁은 발판)과 꼭 맞지는 않는다. 눈으로 보고 정할 일이라 그대로 두었다.

## 3. 패턴

공격 A는 홀수 `attack_serial`, B는 짝수이고, 페이즈는 체력 66 %와 33 %에서 바뀐다. 시그니처 `S<투사체>C<원>L<레인>`은 시험의 대원 3명 기준이다.

| 패턴 | 1페이즈 A / B | 2페이즈 A / B | 3페이즈 A / B | 요점 |
|---|---|---|---|---|
| `bloom_field` (AERATOR) | `S0C4L0 / S0C4L0` | `S0C6L0 / S3C0L0` | `S0C7L0 / S0C7L0` | 대상 둘레 고리에 포자 원이 하나씩 열린다. 2페이즈부터 대상 자리도 핀다. B는 고리를 돌린다(1페이즈 45°, 3페이즈 30°). 2페이즈 B는 포자 볼트 3발 |
| `frost_sweep` (CRYO) | `S0C0L2 / S2C0L0` | `S0C0L3 / S0C0L4` | `S0C0L5 / S0C0L5` | 보스→대상 축에 수직인 서리 막대가 150 px 간격으로 바깥으로 번진다(3페이즈 B는 안쪽으로). 3페이즈는 축 레인이 더해진다 |
| `rail_charge` (GANTRY) | `S0C0L2 / S0C1L0` | `S0C0L3 / S0C2L0` | `S0C0L4 / S0C1L4` | 대상이 선 자리에서 레일이 교차한다. 다음은 양쪽 끝 원, 마지막은 별 모양 레일 |
| `echo_copy` (ARCHIVE) | `S0C1L0 / S0C2L0` | `S0C3L0 / S0C3L0` | `S0C4L0 / S0C4L1` | 대상 자리와, 대상이 지난 공격에서 서 있던 자리(`ECHO_MEMORY` 3, 페이즈가 바뀌어도 유지)가 핀다. 멈추거나 같은 길을 되밟으면 맞는다 |
| `null_convergence` (ORIGIN) | `S0C0L3 / S2C1L0` | `S0C0L4 / S2C2L0` | `S0C1L5 / S0C2L3` | 레인이 사방에서 대상 자리로 모이고, 코어 발밑도 닫힌다 |

열 보스 모두 같은 페이즈에서 시그니처가 서로 다르다(시험이 확인하고, 두 보스의 패턴을 메모리에서 같게 만들면 FAIL하는 음성 대조가 있다).

## 4. 공정성

**공통 규칙(전 보스, 낮추지 않았다):** 공격당 경고 7개 이하, 준비 시간 1.0초 이상, 경고 피해 20 이하, 투사체 피해 24 이하, 대상 주변 300 px 안에 대원 폭 1.5배의 경고 없는 실제 바닥. 열 보스 모두 통과한다.

**새 5기에 더한 가드(`site7_boss_pattern_smoke.gd`):**

1. 대상이 어디에 서 있든 경고 없는 바닥이 **180 px 안에** 있다.
2. 그 바닥까지 가장 느린 대원(ROOK, 138 px/s)의 걸음으로 갈 수 있고, 대상 자리를 덮는 가장 이른 경고가 터지기 **0.25초 전**에 도착한다.
3. 시험 범위는 페이즈 3 × 공격 2 = 6공격, 보스로부터 150–550 px 5단계 × 방향 6개다.

| 보스 | 가장 먼 안전 바닥 | 가장 빠듯한 탈출 여유 |
|---|---:|---:|
| AERATOR | 90 px | 1.05초 |
| CRYO | 60 px | 0.67초 |
| GANTRY | 150 px | 0.33초 |
| ARCHIVE | 90 px | 0.65초 |
| ORIGIN | 120 px | 0.43초 |

GANTRY가 가장 빠듯하다(1페이즈 B의 충돌 원: 120 px을 걸어 나가는 데 0.87초, 원은 1.2초에 터진다). 3페이즈 B는 레일 별에 대상 원이 겹쳐 안전 바닥이 150 px 밖이라(걸어 나가는 데 1.09초) 대상 원의 준비 시간을 레일과 같은 1.5초로 했다. 지시서는 그 원의 준비 시간을 적지 않았고, 다른 원처럼 1.2초로 두면 여유가 0.25초 가드에 못 미친다.

## 5. 효과 계열 (모두 코드로 그린다, `vfx_painter.gd`)

| 보스 | 총구 | 피격 | 투사체 | 색 |
|---|---|---|---|---|
| AERATOR | 라임 연기 원뿔, 벌어지는 꽃잎 다섯, 흩날리는 포자 | 포자 파열: 꽃잎 모양 개화, 떠다니는 포자, 빛나는 증기 | `PRJ_BOSS_AERATOR_SPORE_01` 꽃잎 셋이 도는 라임 싹과 떠도는 알갱이 | `#8fdc4a` |
| CRYO | 연분홍 원뿔, 긴 얼음 조각 둘, 서리 고리 | 서리 파열: 여섯 갈래 결정과 유리 조각 | `PRJ_BOSS_CRYO_SHARD_01` 반짝이는 꼬리를 단 뾰족한 얼음 조각 | `#ff7fc8` |
| GANTRY | 두 레일 사이로 뻗는 납작한 섬광 | 레일 아크: 맞은 자리를 지나는 밝은 선, 노란 아크, 긴 불꽃 | `PRJ_BOSS_GANTRY_RAIL_01` 얇은 레일 둘 사이의 긴 노란 막대, 끝은 흰색 | `#ffd84a` |
| ARCHIVE | 청록 섬광과 방출구에서 떠나는 사각 괄호 | 글리프 흩어짐: 청록 괄호와 데이터 조각 | `PRJ_BOSS_ARCHIVE_ECHO_01` 잔상 복사본을 남기는 청록 데이터 사각 | `#2fe0b4` |
| ORIGIN | 옆으로 갈라지는 실금이 있는 흰 심장 | 균열: 맞은 자리에서 흰 금이 뻗고 어두운 합금 조각이 날린다 | `PRJ_BOSS_ORIGIN_NULL_01` 꼬리에 실금이 깜박이는 흰 점 | `#f4efe8` |

로봇 그림은 색을 입히지 않았고 빛은 더하기 합성이다. 삼각형 예산과 자기 해제는 `combat_vfx_overhaul_smoke.gd`가 본다.

## 6. 바꾼 파일

등록은 커밋 `0eda283c`(45개 파일)에 들어 있다. 이번 후속 커밋은 시험 하나, 러너 한 줄, 문서, 이 기록이다.

**원화 연결 (커밋 `0eda283c`)**

- `assets/enemies/stage6_aerator_tower`, `stage7_cryo_compressor`, `stage8_signal_gantry`, `stage9_index_spire`, `stage10_origin_core` 아래 `authored_core_v1/`: PNG(Codex 마스터와 같은 바이트), `.png.import`, `spec.json` 각 5벌.
- `tools/environment/build_site7_boss_runtime.py`(스펙 생성과 `--check`), `qa/site7_ops_6_10_boss_integration_20260929/runtime_binding.json`.
- 마스터 자체(`motion_lab_v1/art/site7_enemies_raw/*_master.png` 5장)는 Codex의 파일이라 이 커밋에 없었다. 나중에 커밋 `ce479b55`(마스터, 격리한 시도 이미지, `qa/site7_ops_6_10_bosses_20260929/`)로 추적되게 됐다. `--check`는 그 파일이 작업 폴더에 있어야 통과한다.

**데이터**

- `data/art_profiles/enemy_profiles.json`(보스 프로필 5행), `site7_enemy_body_plan.json`(활성 로봇 목록).
- `data/missions/MIS_CH01_06.json`–`10.json`: 보스 행이 자리표시 `BOSS_SITE7_CARRIER_01`에서 자기 보스로 바뀜. `staging`, `deployable: false`는 그대로.

**코드**

- `scripts/combat/site7_enemy_tactics.gd`: 새 패턴 5개(`bloom_field`, `frost_sweep`, `rail_charge`, `echo_copy`, `null_convergence`)와 역할표. 기존 다섯은 손대지 않았다.
- `scripts/actors/enemy_actor.gd`, `scripts/animation/site7_machine_sprite.gd`(`visible_rect`), `scripts/ui/enemy_overhead_ui.gd`, `scripts/animation/enemy_detail_overlay_presentation.gd`: `visible_rect_px`를 따르는 피격 상자, 체력바, 총구.
- `scripts/combat/prototype_projectile.gd`(투사체 5종), `scripts/vfx/combat_hit_vfx.gd`, `scripts/vfx/combat_muzzle_vfx.gd`: 효과 계열. 모두 `vfx_painter.gd`로 그린다.

**시험과 도구**

- 갱신: `site7_boss_registry_smoke.gd`(열 보스, 작전의 `deployable`을 따름), `site7_boss_pattern_smoke.gd`(시그니처 표와 새 5기의 기하·탈출 검사), `site7_emission_owner_smoke.gd`, `site7_full_operation_smoke.gd`, `deploy_warmer_smoke.gd`, `site7_campaign_data_smoke.gd`, `site7_robot_roster_smoke.gd`, `combat_vfx_overhaul_smoke.gd`.
- 캡처: `tests/render/site7_boss_pattern_capture.gd`(시험대 캡처), `combat_vfx_showcase_capture.gd`, 새 `site7_boss_lineup_capture.gd`(열 보스 한 장).
- 러너: `boss_lineup` 등록. `tools/environment/record_stage_battle_with_audio.py`는 **파일 전체가 커밋되면서 Codex의 두 줄 변경**(허용 작전 번호를 6까지, `{number:02d}`)**이 함께 들어갔다.** 내 변경이 아니고 되돌리지 않았다.

**후속 커밋** (`a0ecfe9f`, `ae6d5028`, `9e129c07`, 그리고 이 기록을 마지막으로 갱신한 커밋)

- `a0ecfe9f`: `tests/smoke/site7_boss_duel_smoke.gd`(새 시험)와 러너의 `boss_duel` 한 줄(러너의 다른 변경인 `walk_graph_capture`는 Codex의 것이라 스테이징하지 않았다), `AGENTS.md`(작전 6–10 보스 절), `docs/production/SITE7_OPERATIONS_6_10_DESIGN_KO.md`, `..._BOSSES_CODEX_PROMPT_KO.md`(진행 상태), 앞 커밋에 빠졌던 `tests/render/site7_boss_lineup_capture.gd.uid`.
- `ae6d5028`: 이 README와 이 폴더의 JSON들(`boss_duel.json`, `capture_report.json`, `lineup_report.json`, 실행 요약 2개, `visual_evidence_1080p.json`), `tests/smoke/site7_boss_duel_smoke.gd.uid`. 이미지는 git이 무시한다.
- `9e129c07`: `AGENTS.md`, 설계 문서, 보스 지시서의 진행 상태 문구를 "작전 7–10은 판이 없고 작전 6은 판이 있지만 켜지 않았다"로 바로잡았다(문서만, 코드와 데이터는 그대로).
- 마지막 갱신 커밋: HEAD에서 다시 돌린 full의 요약 `regression_full_head_summary.json`과 이 README(7절, 10절).

## 7. 시험과 결과

| 실행 폴더 | 범위 | 시험 수 | 결과 | 시간 | 기준 커밋 |
|---|---|---:|---|---:|---|
| `20260929_183105_quick` | quick | 40개 | PASS 40/40 | 274초 | `d6e05d44` |
| `20260929_145928_full` | full | 63개 | PASS 63/63 | 2514초 | `0eda283c` |
| `20260929_220441_full` | full | 64개 | PASS 64/64 | 2625초 | `ae6d5028` |

실행 기록은 러너의 git 무시 폴더에 있고, 요약 JSON만 이 폴더에 둔다(`regression_quick_summary.json`, `regression_full_summary.json`, `regression_full_head_summary.json`). 세 실행 모두 `qa/`와 `motion_lab_v1/qa/`의 기존 파일이 바뀌지 않았는지 검사하는 가드를 통과했다(`guard`의 세 목록이 비어 있다).

- quick `20260929_183105_quick`은 내가 돌린 마지막 실행이다(HEAD `d6e05d44`, 작업 폴더에는 추적되지 않은 파일만 있었다). 같은 날 15:42에 돌린 quick(`20260929_154207_quick`)은 시험 40/40이 PASS였지만, 그 사이 Codex가 작전 6 기록(`qa/site7_ops_6_10_plates_20260929/stage_a/README_KO.md`)을 쓰고 있어서 `qa/` 불변 검사가 전체를 FAIL로 판정했다. 조용한 작업 폴더에서 다시 돌려 PASS했다.
- full `20260929_145928_full`은 Codex가 돌린 실행이다(기준 커밋 `0eda283c`와 그 시점의 작업 폴더). 작전 1–5 풀플레이 5개와 `boss_capture_geometry`를 포함한 63개가 PASS했다. 이 실행에는 나중에 더한 `boss_duel`이 없다. 그 실행 뒤에 추가된 코드는 `boss_duel`과 러너의 그 한 줄이고, Codex의 작전 6 연결은 그 실행이 시작될 때 이미 작업 폴더에 있었다. 아래 HEAD 실행이 이 차이를 메운다.
- full `20260929_220441_full`은 내가 마지막에 돌린 실행이다(기준 커밋 `ae6d5028`, 22:04–22:48, 2625초). 64개가 모두 PASS했다: 작전 1–5 풀플레이 5개(124–158초), `boss_duel`(1124 검사), `boss_capture_geometry` 포함. 이 실행 뒤에 들어간 커밋은 보스 마스터와 검토 기록(`ce479b55`)과 문서 수정(`9e129c07`)뿐이라 코드는 같다. **주의:** 실행 도중(22:30) Codex가 작업 폴더의 `scripts/missions/site7_abyss_backdrop.gd`에 작전 7용 `cryo` 심연 스타일을 커밋하지 않은 채 덧붙였다(STYLES 끝에 하나, 셰이더 분기 하나). 그 뒤에 시작한 시험은 수정본을 읽었을 수 있고 결과는 PASS다. 그 파일은 이 기록의 어떤 커밋에도 들어 있지 않다.

**보스와 관련된 시험**(quick 실행 기준 검사 수)

| 시험 | 검사 수 | 지키는 것 |
|---|---:|---|
| `boss_registry` | 158 | 열 보스가 등록되어 있고 작전 파일이 자기 보스를 가리킨다(`deployable`을 따른다). 열린 작전이면 라이브 스테이지에서 세운다 |
| `boss_pattern` | 944 | 열 보스의 공격 모양(시그니처)을 고정하고 공정성 한계와 새 5기의 기하·탈출 여유를 검사한다. 음성 대조 포함 |
| `boss_duel` | 1124 | **새 시험.** 열 보스를 실제 컨트롤러와 경고 루프로 6공격씩 돌려 모양, 준비 시간, 주기, 피해 시각을 잰다. 페이즈, 8초 코어 보호막, 격파까지 확인한다. 음성 대조 3개 |
| `emission_owner` | 1293 | 보스 공격당 실제로 나온 투사체 수와 주인(30/60/120 Hz) |
| `robot_roster` | 302 | 로봇 명단, 보스 크기 띠(220–270 px), 열 보스 화면 높이 |
| `combat_vfx` | 189 | 새 효과 계열의 삼각형 예산, 중복 제거, 자기 해제 |
| `campaign_data` | 272 | 열 작전 자료(보스 행이 자리표시로 돌아가지 않았는지 포함) |
| `deploy_warmer` | 83 | 보스 그림 예열 목록 |
| `boss_lineup` | — | 열 보스를 한 게임 배율로 나란히(헤드리스 기하) |
| `boss_capture_geometry` | — | 시험대 캡처의 기하와 안전 바닥 여유(헤드리스) |

열 보스를 각각 6공격(페이즈마다 2공격)까지 실제 컨트롤러와 경고 노드로 돌린 결과다(`boss_duel.json`, 1124 검사). 대원 3명은 서 있고 쓰러지지 않는다.

- 준비 시간(WINDUP)은 1.10초(ANCHOR 0.95초), 공격 간격은 회복(1.6/1.4/1.2초) + 재배치 0.45초 + 준비 1.1초 = **3.15 / 2.95 / 2.75초**(1/60초 단위 오차 안, ANCHOR는 준비가 0.15초 짧아 그만큼 짧다). 첫 공격은 시작 1.8초 뒤(ANCHOR 1.65초).
- 피해는 경고가 터지는 순간에만, 경고가 뜬 지 0.95초 이상 지나서, 그 안에 선 대원에게만 들어간다(기하는 시험 안에서 따로 계산한 값과 비교). 첫 피해가 들어온 시각은 그 경고의 준비 시간과 ±0.06초 안에서 맞는다.
- 코어 보호막(체력 33 % 이하 8초)은 8초 동안 피해를 막고, 그동안에도 공격은 계속되며(모든 보스에서 3번), 8초 뒤 다시 맞는다. 격파는 정확히 한 번 알려지고 경고와 투사체가 남지 않는다.
- 음성 대조 3개(GANTRY에 다른 패턴 끼우기, 경고가 0.5초 일찍 터지게 하기, 피해를 35로 키우기)는 각각 `damage` 13, `early` 53, `shape` 6개의 실패를 냈다. 시험이 이 결함을 잡는다.

**서 있는 대상(ASTER, 보스에서 200 px)이 6공격 동안 받는 피해**(관찰: 균형 판단이 아니다. 조작 체력은 96–138)

| 보스 | 경고 피해 합 | 총알 피해 합 | 첫 공격(초) | 공격 사이(초) 1/2/3페이즈 |
|---|---:|---:|---:|---|
| ANCHOR | 60 | 288 | 1.65 | 3.03 / 2.82 / 2.62 |
| RELAY | 80 | 64 | 1.78 | 3.18 / 2.97 / 2.77 |
| REMNANT | 80 | 0 | 1.78 | 3.18 / 2.97 / 2.77 |
| FORGE | 100 | 108 | 1.78 | 3.18 / 2.97 / 2.77 |
| CARRIER | 160 | 64 | 1.78 | 3.18 / 2.97 / 2.77 |
| AERATOR | 60 | 16 | 1.78 | 3.18 / 2.97 / 2.77 |
| CRYO | 40 | 36 | 1.78 | 3.18 / 2.97 / 2.77 |
| GANTRY | 300 | 0 | 1.78 | 3.18 / 2.97 / 2.77 |
| ARCHIVE | 360 | 0 | 1.78 | 3.18 / 2.97 / 2.77 |
| ORIGIN | 380 | 0 | 1.78 | 3.18 / 2.97 / 2.77 |

GANTRY, ARCHIVE, ORIGIN이 서 있는 대상을 가장 세게 벌한다(300–380). 의도한 방향이다: GANTRY는 서 있는 자리에서 레일이 교차하고, ARCHIVE는 멈추면 맞고, ORIGIN은 레인이 대상에게 모인다. AERATOR와 CRYO는 1페이즈에서 서 있는 대상을 건드리지 않는다(고리와 막대가 옆을 지난다). 수치가 맞는지는 사람이 플레이해서 정한다.

## 8. 캡처 (1080p)

모두 네이티브 1920 × 1080, 창을 띄운 실제 렌더다. **작전 6–10은 켜지 않았고(작전 7–10은 판도 없다) 자기 방을 찍을 수 없어 시험대**다: 새 보스 5기를 미션 3의 보스 홀에 세웠고(GANTRY는 복도형 방이라 미션 3의 두 번째 방), 각 파일에 `testbed_`가 붙어 있고 기록에 `test_bed: true`, `visual_approval: false`가 있다. 그 작전의 방이 아니므로 방 모양, 바닥, 엄폐물, 조명은 판단 자료가 아니다.

| 묶음 | 파일 | 내용 |
|---|---|---|
| 시험대 전경 | `captures/testbed_<boss>_room.png` × 5 | 보스와 대원, 방출구 표시 |
| 시험대 경고 | `captures/testbed_<boss>_p{1,2,3}{a,b}_warning.png` × 30 | 페이즈·공격별로 바닥에 깔린 경고(페이즈와 공격 번호는 시험이 정해 넣었다: `controlled_phase_fixture`) |
| 기존 보스 비교 | `captures/mission{1..5}_boss_room.png`, `mission{1..5}_phase{1,2,3}_warning.png` × 20 | 기존 5기를 자기 방에서 같은 카메라로(비교용) |
| 열 보스 한 장 | `captures/bosses_01_10_game_scale.png`, `lineup_report.json` | 같은 게임 배율. 화면 높이 중앙값 314 px 대비 0.93–1.15배 |
| 1:1 크롭 | `crop_sheets_1to1/*.png` × 5 | 새 보스별 시험대 프레임에서 보스와 경고 부분을 보간 없이 오려 붙임(원본 해상도, `crop_sheets_manifest.json`) |
| 효과 계열 | `vfx/*.png` × 11 | 총구, 투사체, 피격, 폭발, 피격 반응 쇼케이스(`combat_vfx_showcase_capture.gd`) |
| 몽타주 | `captures/_montage_rooms.png` | 시험대 전경 5장을 한 장으로(훑어보기용) |

`tools/art_pipeline/validate_visual_evidence_1080p.py --require-dynamic-capture`를 이 폴더의 이미지 79장에 돌린 기록이 `visual_evidence_1080p.json`이다(PASS). 이 검사는 컨테이너와 해상도만 확인하고 그림의 질을 판정하지 않는다. PNG는 git이 무시하고(`.gitignore`의 `qa/**/*.png`) 작업 폴더에만 있다.

## 9. 지시서와 다른 점

지시서(`SITE7_OPERATIONS_6_10_BOSSES_CODEX_PROMPT_KO.md`) 4절의 값이 시작값이었고, 아래는 실제로 들어간 값과 다른 곳이다. 나머지 서리·레일 수치는 지시서대로다.

1. **CRYO 서리 막대는 200 px가 아니라 130 px에서 시작한다**(130, 280, 430, 580 px). 보스 안내문이 "압축기에 붙지 말라"고 하는데, 200 px에서 시작하면 압축기 바로 앞이 가장 안전한 자리가 된다. 시작을 당겨 그 자리(100–160 px)를 첫 막대가 덮게 했다. 간격 150 px와 반폭 30 px(틈 90 px)는 지시서대로이고, 4절의 안전 바닥 가드는 이 값에서 통과한다.
2. **GANTRY 3페이즈 B의 대상 원은 준비 1.5초**다. 지시서는 그 원의 준비 시간을 정하지 않았다. 다른 원처럼 1.2초로 두면 레일 별 안쪽에서 걸어 나오는 시간(1.09초)에 0.25초 여유가 못 미친다(4절).
3. **`spec.json`에 선택 항목 `visible_rect_px`를 새로 넣었다.** 새 마스터는 투명 여백이 커서(AERATOR는 캔버스 376 px 안의 본체 226 px), 캔버스를 기준으로 삼으면 체력바가 허공에 뜨고 피격 상자가 그림과 어긋난다. 없으면 그림 전체를 쓰므로 기존 보스는 바뀌지 않았다.
4. **공정성 가드를 지시서보다 더했다.** 공통 한계는 그대로(낮추지 않음). 새 5기에는 안전 바닥 180 px 이내와 0.25초 탈출 여유(가장 느린 대원 걸음)를 5거리 × 6방향 × 6공격으로 검사한다(4절).
5. **등록 시험이 `deployable`을 따른다.** 지시서는 보스 표에 새 보스를 넣으라고만 했다. 작전이 열리는 날 시험이 조용히 낡지 않도록, 열린 작전은 보스를 라이브 스테이지에 세우고 `staging`이 없어야 하며 닫힌 작전은 `staging`이 `ART_PENDING`이고 보스 id가 `staging.boss.id`와 같아야 한다.
6. **실시간 교전 시험(`boss_duel`)을 더했다.** 지시서에 없는 시험이다. 판이 없어 `full_op_06–10` 풀플레이를 못 하므로, 실제 컨트롤러와 경고 루프를 열 보스 모두에 돌린다(3절 끝, 7절).

## 10. 지시서 6절(검증과 기록) 대조

지시서 6절의 항목을 하나씩 대조한 표다. "하지 않음"과 "시험대로 대신"은 작전 6을 켜야 하거나 작전 7–10의 판이 들어와야 할 수 있는 일이다(11절).

| 6절 | 지시서가 요구한 것 | 상태 | 근거 |
|---|---|---|---|
| 1 | 새 원본의 알파 검사, 원본 크기로 밝은/어두운 배경 위 검수 | **됨**(순서 1, Codex) | `qa/site7_ops_6_10_bosses_20260929/`(`boss_asset_gate.json`, `art_review/`). 이 기록은 그 마스터가 런타임 PNG까지 같은 바이트인지 `build_site7_boss_runtime.py --check`로 확인했다 |
| 2 | quick과 full PASS, 켠 작전의 풀플레이 | **됨**: quick PASS 40/40, full PASS 64/64(HEAD `ae6d5028`). 켠 작전이 없어 `full_op_06–10`은 없다 | 7절. 그 자리를 `boss_duel`이 메운다 |
| 3 | 1080p 게임 캡처: 새 보스 자기 방 + 원본 크기 크롭 | **시험대로 대신**(작전 6은 켜지 않아, 7–10은 판이 없어 자기 방을 못 찍었다) | 8절. 크롭은 `crop_sheets_1to1/` |
| 3 | 열 보스를 같은 크기로 나란히 한 장 | **됨** | `captures/bosses_01_10_game_scale.png`, `lineup_report.json` |
| 3 | 보스별 경고 모양, 페이즈마다 한 장, 새 5기 | **됨**(페이즈 3 × 공격 A/B = 6장 × 5기) | `captures/testbed_<boss>_p<N><a,b>_warning.png` |
| 4 | 새 보스 각각 10초 전투 영상, 게임 소리 포함 | **하지 않음**(작전을 켠 뒤, 작전 7–10은 판 이후) | 11절 |
| 5 | `validate_visual_evidence_1080p.py --require-dynamic-capture`를 모든 검토 이미지·영상에 | **됨**: 이미지 79장 PASS. 영상은 없다 | `visual_evidence_1080p.json` |
| 6 | `README_KO.md`와 증거를 남긴다 | **됨**: 이 폴더. 지시서가 적은 폴더 이름 `qa/site7_ops_6_10_bosses_<날짜>`는 Codex의 원화 기록이 이미 쓰고 있어 `site7_ops_6_10_boss_integration_20260929`로 했다 | 이 폴더 |
| 7 | 로컬 커밋 | **됨**(푸시 없음) | 6절에 적은 커밋 |

HOLD 조건(지시서 7절 끝) 확인: 풀플레이(작전 1–5)가 새 코드 때문에 실패한 일은 없다(HEAD의 full 실행에서 `full_op_01–05` PASS). 공정성 한계와 시험 기준은 낮추지 않았다(4절).

## 11. 하지 못한 것

아래는 하지 않았거나 할 수 없었던 일이다. 작전 7–10은 판이 없어서(대용품을 그리거나 다른 작전의 판을 빌리지 않는다는 지시), 작전 6은 켜는 결정이 사용자에게 남아서다.

1. **작전 6 켜기.** Codex가 작전 6의 판 15장을 이 작업 도중 커밋했다(`d6e05d44`, 15:44, `deployable`은 `false` 그대로). 지시서 7절 순서 4는 판이 연결되어 있으면 그 작전을 켜라고 하지만, 켜는 편집(`data/story/site7_campaign.json`의 작전 6 행과 작전 5의 COMMAND 디브리프, `data/missions/MIS_CH01_06.json`의 `staging`)이 이 세션의 자동 권한 판정에서 공유 자원 수정으로 두 번 거절되어 하지 않았다. 다른 방법으로 우회하지 않았고, 켤지는 사용자가 정한다. 판(A)과 보스(B)는 둘 다 끝났으므로 남은 것은 12절의 목록이다.
2. **작전 6 방에서의 AERATOR 확인.** 켜지 않은 채로 `R05_ATRIUM`에 AERATOR를 세워 찍고 실제 바닥에서 공정성을 재는 임시 스크립트(`.cache/`)도 같은 판정에 막혀 만들지 못했다. 그래서 8절 캡처는 AERATOR도 미션 3의 보스 홀에 세운 시험대다. 각 보스의 방 크기, 바닥, 엄폐물, 문, 조명, 심연은 보이지 않는다.
3. **게임 소리가 든 전투 영상**(`record_stage_battle_with_audio.py`)과 **같은 세션 회전 A/B FPS**(`AGENTS.md`의 규칙). 새 보스 효과는 삼각형 예산과 자기 해제만 시험(`combat_vfx_overhaul_smoke.gd`)했고 실제 프레임 비용은 재지 못했다.
4. **작전 6–10 풀플레이**(`full_op_06–10`). 작전 6은 켜지 않아 러너에 자리가 없고, 작전 7–10은 판이 없다. 대신 `boss_duel`이 보스 쪽 실시간 검사를 한다. 전투방, 증원, 탈출, 보상 흐름은 작전이 열려야 시험된다.
5. **실제 방 바닥에서의 공정성.** 4절의 탈출 검사는 800 × 800 px 열린 바닥에서 한다. 좁은 방(GANTRY의 복도형)에서는 미션 3의 보스 홀 시험대가 안전 바닥 여유(`safe_floor_gap`)를 재지만 자기 방은 아니다. 방마다 `boss_anchor`와 `enemy_spawns` 배치 뒤에 다시 잰다.
6. **그림, 균형, 플레이 승인.** 코드와 자동 시험이 통과했다는 뜻뿐이다. 보스의 겉모습, 체력, 공격 강도, 위 표의 수치는 사람이 보고 정한다.
7. **관찰(고치지 않음).** 보스 발밑의 타원 그림자는 모든 보스가 같은 크기다(2절). 서 있는 대상이 6공격 동안 받는 경고 피해는 ORIGIN 380, ARCHIVE 360, GANTRY 300으로 가장 크고 AERATOR 60, CRYO 40으로 가장 작다(7절 표, 조작 체력은 96–138). 의도한 방향이지만 수치를 정하는 것은 사람의 일이다.

## 12. 다음에 할 일

작전 6은 판 15장(Codex, `d6e05d44`)과 보스가 모두 끝나서 켜기만 남았다. 작전 7–10은 판 15장이 들어올 때마다, 한 번에 하나씩 같은 순서를 따른다.

**작전 6 켜기** (설계 문서 6절 C에 아래 잔여 항목을 더한 것)

1. `data/missions/MIS_CH01_06.json`의 `staging` 블록을 지운다.
2. `data/story/site7_campaign.json`: 작전 6 행에서 `"deployable": false`와 `"pending"`을 지우고, 작전 5의 COMMAND 디브리프를 `Offshore Null complete. The answer signal is tracing back into Site-7's sealed lower wings. Verdant Lock is now available.`로 바꾼다.
3. 5에서 멈춘 곳: `tools/maintenance/run_regression_suite.py`의 `full_op` 등록(`range(1, 6)`을 6까지, 이름과 `--mission` 형식은 `%02d`). `campaign_data` 게이트가 목록의 파일에서 `range(1, 6)` 같은 표시를 찾아 알려 준다. 러너에 등록되지 않은 `tests/smoke/site7_live_entry_autostart_smoke.gd`(`range(1, 6)`)는 그 목록에도 없으니 따로 넓힌다.
4. `tests/render/site7_boss_pattern_capture.gd`: AERATOR를 `TEST_BED`에서 빼고 `BOSS_IDS`(자기 방)에 넣는다.
5. 게이트: `python tools/maintenance/run_regression_suite.py --only campaign_data,campaign,demo_integration`. 이어서 quick과 full(`full_op_06` 포함). `full_op_03`처럼 봇이 마지막 보스에서 자주 지면 다시 돌려 보고, 계속 지면 공정성 규칙 안에서 수치를 조정한다.
6. 자기 방 캡처(방 + 페이즈별 경고), 게임 소리 영상(`record_stage_battle_with_audio.py`, 10초 600프레임), 같은 세션 회전 A/B FPS, 실제 바닥에서의 공정성(`boss_capture_geometry`가 작전 6 방을 재도록). 그 뒤에 사람이 그림과 균형을 본다.
7. `AGENTS.md`(작전 6–10 절과 보스 절)와 설계 문서 0절의 상태를 고친다.
