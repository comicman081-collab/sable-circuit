# 항목 1 상수·검증 표 초안

작성: 2026-10-03. 비교 기준 `dca7ef20`, 읽은 HEAD `36ccff9a`.
`AGENTS.md`의 Expansion / Upgrade economy 절과 확장 지시서 전체를 다시 읽고, `git diff dca7ef20..HEAD` 및 시험 파일의 현재 작업 트리 diff를 읽었다. 읽은 시점에 작업 트리 diff는 비어 있었다. 이 파일은 최종 QA 보고서에 옮길 캐시 초안이며, 이 하위 작업에서는 게임·시험·러너를 실행하지 않았다.

## 적용한 사용자 결정

공통 기계 weathering 셰이더와 공통 hit flash는 유지한다. 금지는 **변종이 추가하는 착색·재질 변경**이다. `elite_expansion_smoke.gd`는 변종 없는 같은 로봇과 변종 로봇의 모든 Sprite2D `modulate`, `self_modulate`, 재질 종류, 셰이더 경로와 모든 셰이더 파라미터를 비교한다. 공통 hit flash를 양쪽 모두 0.7로 둔 상태도 비교한다. 원래 공통 셰이더가 있는 스프라이트에 문자 그대로 `material == null`을 요구하지 않는다. `site7_machine_sprite.gd`와 기존 `site7_machine_source_smoke.gd`는 바꾸지 않았다.

## 1. 기존 기댓값·검사에서 달라진 것

| 파일 | 이름/대상 | 이전 → 이후 | 이유 |
|---|---|---|---|
| `tests/smoke/elite_affix_smoke.gd` | 변종 표 크기·필수 id | 3, 기존 3 id → 5, 기존 3 + BROODING + BEACON | V-01. 기존 행을 보존하며 2종 추가 |
| `tests/smoke/elite_affix_smoke.gd` | `EXPECTED_ROWS` | 작전 1–10: 1/1/2/3/3/4/4/4/4/5 → 동일 | 새 변종은 기존 정예 한 행을 교체 |
| `tests/smoke/zone_hazard_smoke.gd` | 사이클·추종자 검사 대상 | `vents[0]` → 그 방의 첫 `ARC_VENT` | 혼합 배치에서도 기존 ARC 검사 대상을 유지. 새 종류는 별도 확대 시험으로 검사 |
| `tests/smoke/zone_hazard_smoke.gd` | 바닥·엄폐 경계 표본 | 타원 16점 → `boundary_points()`(타원 16점, 띠 실제 4꼭짓점) | 실제 피해 모양 검사. 타원 표본 수는 동일 |
| `tests/smoke/zone_hazard_smoke.gd` | 장판 간 최소 간격 | `vent.radius × 2.6` → `max(vent.radius, other.radius) × 2.6` | 서로 다른 반경에서도 큰 장판 기준을 적용. 2.6은 유지 |
| `tests/smoke/zone_hazard_smoke.gd` | 방 안내 검사 | 기존 ARC VENT 안내 검사 → 기존 검사 + 각 선언 종류의 `tip` 검사 | 기존 검사 삭제 없이 종류별 안내를 추가 |
| `tests/smoke/site7_full_operation_smoke.gd` | `expected_hostiles` | 원래 encounter+증원 합 → 그 합 + BROODING 부모당 2 | 동적 새끼도 실제로 처치해야 route 완료 검사가 통과. 기존 처치 검사는 유지 |
| `tools/maintenance/run_regression_suite.py` | 등록 수 | 전체 73 / quick 44 / full 전용 29 → 77 / 46 / 31 | 새 시험 4개 등록; 기존 등록·상한은 유지 |
| 같은 파일 | `elite_expansion` / `variety_placement` | 없음 → quick, timeout 300 / 120 s | 빠른 실제 액터 계약 / 배치 비교 검사 |
| 같은 파일 | `hazard_expansion` | 없음 → full 전용, timeout 600 s, solo, `--out=hazard_expansion.json` | 방별 경로·격자 검사와 JSON 기록 |
| 같은 파일 | `variety_capture` | 없음 → full 전용, timeout 300 s, solo, `--out=dir` | 실제 방의 제어된 런타임 증거. headless에서는 그림 증거를 주장하지 않음 |

기존 검사에서 숫자 한계를 줄이거나 `_check`를 삭제한 변경은 발견하지 않았다. ARC 타이밍·추종자 검사를 혼합 장판 배열의 첫 항목에 잘못 적용하지 않도록 대상만 ARC로 명시했다. 시험 결과 수는 데이터 행과 표본 수의 증가에 따라 늘 수 있으며, 최종 러너의 실제 요약 수를 별도 표에 기록해야 한다.

## 2. 새 런타임·데이터 상수

새 기능의 값은 모두 `없음 → 값`이다. 기존 SHIELDED / OVERCHARGED / VOLATILE 및 ARC_VENT 데이터 값은 그대로다.

| 파일 | 이름/대상 | 이전 → 이후 | 이유 |
|---|---|---|---|
| `data/progression/elite_affixes.json` | BROODING `brood_count`, `brood_health_ratio`, `brood_hatch_windup` | 없음 → 2 / 0.25 / 0.6 s | 정확히 두 새끼, 작은 체력, 공격 전 부화 경고 |
| 같은 파일 | BROODING / BEACON `color` | 없음 → `9bda67` / `c0a4ff` | 코드로 그리는 링·라벨·연결선 구분; 로봇 그림에는 적용하지 않음 |
| 같은 파일 | BEACON `beacon_radius`, `beacon_reduction`, `beacon_max_links` | 없음 → 360 px / 0.25 / 6 | 반경의 다른 로봇 피해 감쇠·표시 예산 |
| `scripts/combat/elite_affix.gd` | BEACON 감쇠 하드 상한 / 연결선 하드 상한 | 없음 → 0.35 / 6 | V-06. 중첩은 가장 강한 하나만; 선 예산은 실제 보호 로봇 수를 제한하지 않음 |
| 같은 파일 | 비콘 연결선 굵기·알파 | 없음 → 2 px / 0.48 | Painter 배치 선. 보호 로봇당 가장 강한 비콘 하나에만 선을 연결 |
| `scripts/missions/story_stage_01.gd` | 부화 수 / 세대 / 최저 부화 시간 | 없음 → 2 / 1 / 0.6 s | 부모 −1 앞에 새끼 +2; 새끼는 재부화·affix를 거부 |
| 같은 파일 | 새끼 위치 검색 반경 / 방향 표본 | 없음 → 32,48,72,104,144,192,256,320 px / 각 24방향 | 부모 근처의 실제 걷는 바닥과 엄폐를 피하는 결정적 검색 |
| 같은 파일 | 새끼 최소 간격 / collider 기본 반폭 / 여유 / 경계 표본 | 없음 → 44 px / (21,21) px / +3 px / 16점 | 중심점만 바닥에 놓는 오류를 방지 |
| `scripts/actors/enemy_actor.gd` | 부화 링 반경·굵기·분할·바닥 비율 | 없음 → 34 px / 2·3 px / 32 / 0.55 | 공격 금지 시간을 코드 링으로 표시; Painter 한 배치 |
| `data/progression/zone_hazards.json` | SPORE_CLOUD 반경·초기 지연·idle·경고·지속·phase_step | 없음 → 70 px / 2.4 / 3.0 / 1.2 / 3.0 / 1.35 s | 경고 중 피해 0, 방전 부분의 시간만 적분 |
| 같은 파일 | SPORE_CLOUD 순간 피해 / DPS / 색 | 없음 → 연산자·로봇 순간 0·0, DPS 4·8 / `b1e86d` | V-12 지속 피해 상한 안 |
| 같은 파일 | FROST_PLATE 반경·초기 지연·phase_step·느려짐·피해·색 | 없음 → 70 px / 2.4 / 1.35 s / 0.7 / 0·0 / `b4d9ff` | 피해 없는 이동 제약; 기존 이동 배율과 별도 토큰 |
| 같은 파일 | RAIL_LANE 반길이·반폭·각도·바운딩 반경 | 없음 → 90 / 24 px / −26.565051177° / 93.145048178 px | 실제 180×48 띠 판정, 배치는 바운딩 원 기준 |
| 같은 파일 | RAIL_LANE 초기 지연·idle·경고·방전·phase_step | 없음 → 2.4 / 3.0 / 1.4 / 0.3 / 1.35 s | ARC급 방전이며 충분한 옆 탈출 경고 |
| 같은 파일 | RAIL_LANE 순간 피해·색 | 없음 → 연산자 14 / 로봇 24 / `ffd84a` | V-12 상한 그대로 |
| `scripts/actors/operator_actor.gd`, `enemy_actor.gd` | `set_hazard_speed_factor` clamp | 없음 → [0.5,1.0] | 서로 겹치는 frost는 가장 강한 감속 하나; 기존 run/FIELD STIM 곱을 보존 |
| `scripts/actors/operator_actor.gd` | SPORE FLINCH 최소 표시 간격 / 초기값 | 없음 → 90 ms / −1000 ms | 새 지속 피해가 매 tick 만드는 중복 시각 반응만 제한. HP·출처·health_changed는 모든 tick에 남고 일반 피격·HEAVY·DOWNED는 그대로 |
| `scripts/combat/zone_hazard.gd` | 새 띠 `_band_exit` 추가 여유 | 없음 → 기존 `SAFE_MARGIN 24` + 12 px | 기존 타원 exit와 같은 안전 여유 적용 |
| 같은 파일 | `boundary_points` 기본 표본 | 없음 → 16 | 기존 타원 검사 표본과 동일; band는 4 실제 꼭짓점 |
| 같은 파일 | 새 그림 반복 도형 예산 | 없음 → rail 가로침목 9 / frost 6결정×3팔 / spore 12알갱이 / 링 20분할 | 매 도형 캔버스 호출 대신 Painter 배치 |
| 같은 파일 | `debug_contract.draw_commands_max` | 없음 → ARC 23 / 새 장판 2 | 기존 ARC 고정 모양을 보존, 새 반복 도형은 Painter 삼각형 배열 2개 이하 |
| `scripts/missions/site7_battlefield.gd` | 혼합 장판 예약 간격 | 같은 종류 `radius × 2.6` → 같은 종류 그대로 + 혼합 `max(radiusA,radiusB) × 2.6` | 같은 위치 중복 방지. 큰 바운딩 반경 장판 먼저 배치 |

위에 새로 생긴 시간·거리·피해·반복 도형 수를 묶어 적었다. 기존 이동 기본값, actor 축척, 대시 520 px/s·0.14 s·0.65 s, 기존 ARC 그림과 phase carry, `SAFE_MARGIN=24`, `REACT_LEAD=0.6`, `FLOOR_RATIO=0.55`, 분대 이격 90 px, 첫 스폰 이격 30 px, 보호 스폰 4개는 바꾸지 않았다.

## 3. 새 시험·캡처 수치

| 파일 | 이름/대상 | 이전 → 이후 | 이유 |
|---|---|---|---|
| `tests/smoke/elite_expansion_smoke.gd` | 표 크기 / 새끼 수 / 부화 하한 / 감쇠 상한 / 선 상한 | 없음 → 5 / 2 / ≥0.6 s / ≤0.35 / ≤6 | V-01,04,06의 독립 계약 검사 |
| 같은 파일 | 계약 체력 고정물 | 없음 → 부모 authored 400 HP, 새끼 비율 0.25, 계약 1.3 → 새끼 130 HP | 배율이 정확히 한 번 적용되는 실제 액터 검사 |
| 같은 파일 | 부화 경계 tick | 없음 → 0.59 s + 0.011 s | 0.6 s 이전 attack·projectile 금지와 이후 해제를 직접 검사 |
| 같은 파일 | 비콘 중첩·7번째 peer·SHIELDED 고정물 | 없음 → 0.25/0.35/0.20 감쇠, 7peer/6선, 피해40→30→장벽30 | 가장 강한 하나, 보호·선 예산 분리, 감쇠 후 장벽 순서 |
| 같은 파일 | 공통 sprite hit flash 고정물 | 없음 → plain/affix 모두 0.7 | 사용자 결정대로 공통 hit flash 차이까지 비교 |
| `tests/smoke/hazard_expansion_smoke.gd` | `IDS`, 표 크기 | 없음 → ARC/SPORE/FROST/RAIL 4종 | 기존 ARC 데이터 골든 전체 필드를 고정·비교 |
| 같은 파일 | `GRID`, `SLOWEST_WALK`, `ESCAPE_MARGIN` | 없음 → 25 px / 138 px/s / 0.25 s | 피해 장판의 실제 걷는 바닥 경로. 보스 한계를 그대로 사용 |
| 같은 파일 | 피해·경고·초기 지연·감속 상한 | 없음 → 순간14/24, DPS4/8, 경고≥1.0 s, 초기≥2.0 s, 감속[0.5,0.8] | 지시서 V-11…13과 동일 |
| 같은 파일 | escape 후보 간격·방향·바깥 여유 | 없음 → 5 px / 48방향 / 1 px | 가려진 경로와 실제 장판 내부를 제외해 탐색 |
| 같은 파일 | 실제 바닥 경계·배치 검사 | 없음 → 경계32점, 시작 radius+90, 첫4슬롯 radius+30, 간격 max(radius)×2.6 | 기존 이격 한계 유지하며 모든 선언 방·종류 검사 |
| 같은 파일 | frost 탈출 검사 | 새 시험 첫 구현에서는 건너뜀 → 25 px 격자로 전부 검사, 탐색 거리=방 바닥 bbox 대각선 | 무피해 slow에는 경고 시한을 새로 만들지 않고 실제 경로 존재를 추가 검사. 피해 장판의 138+0.25 시간 조건은 그대로 |
| 같은 파일 | SPORE visual throttle 고정물 | 없음 → 120회 ×4/60 HP, 정확히 8 HP, 표시 간격90 ms | 모든 피해·출처 tick 보존과 시각 효과 수 제한 동시 검사 |
| `tests/test_expansion_item1_placement.py` | `BASELINE`, 허용 새 id 맵 | 없음 → `dca7ef20`, hazard {6:SPORE,7:FROST,8:RAIL}, affix {6:BROODING,9:BEACON} | ops1–5·10 전체 불변, hazards/affix 밖 필드 불변, 원래 배치도 단독 revert 가능 |
| `tests/render/expansion_item1_capture.gd` | 네이티브/콘텐츠 크기 | 없음 → 1920×1080 / 1280×720 | 런타임 카메라·그림 축척 유지한 네이티브 증거 |
| 같은 파일 | 카메라 zoom | 없음 → 기존 `NORMAL_ZOOM`(1.22) | 임의 sprite 확대 없이 동일 게임 시야 |
| 같은 파일 | 부화 제어 고정물 | 없음 → 실제 부모 피해99999, 부화 timer 절반(0.3 s), 파괴효과 자연 종료1.5 s | 실제 damage·spawn 경로 후 timer만 잡아 링을 확인. 플레이·회피 검사가 아님 |
| 같은 파일 | 장판 제어 고정물 | 없음 → 활성 controller tick0.05 s, 타원(±0.9r,−0.35×0.55r), rail(±0.85L,−0.65W) | idle/경고 때 실바닥 밖에 두고 활성 프레임에서만 실제 내부로 이동. 효과 중심 가림을 줄임 |
| 같은 파일 | 장판 밖 대상 검색 | 없음 → 추가 거리110/140/180/220 px, 10방향, contains 여유64 px | 실제 floor·cover 판정으로 경고 장면에서 효과 가림 방지 |

캡처 timer·배치·큰 처치 피해는 시험 고정물 값이다. 런타임 난이도 상한으로 옮기지 않는다. 제어된 런타임 캡처는 사람 플레이가 아니다. 네이티브 시각 검증기의 PASS는 크기와 디코드 검사만 뜻한다.

## 4. 보호 한계·경로의 정적 확인

| 확인 범위 | 읽은 diff 결과 | 실행 상태 |
|---|---|---|
| `assets/`, `art_src/`, `motion_lab_v1/`, `data/visual/` | `dca7ef20..36ccff9a` 변경 0 | 정적 확인. 승인17개 해시 도구와 layout/mood `--check`의 실행 결과는 최종 러너 표 필요 |
| ops1–5·10 미션 JSON | 변경 0 | 정적 확인 |
| 보스 `site7_enemy_tactics.gd`, profile 원화 등록, `site7_boss_*` 시험, phase guard | 변경 0 | 정적 확인. 보스5종 시험의 검사 수·PASS는 최종 실행 로그로 따로 확정 |
| 보스 fairness | 180 px / 0.25 s / 138 px/s, 경고≥1.0, 경고7·피해20·투사체24, GANTRY/ORIGIN1.56·ECHO1.12, `SIGNATURES` 변경 0 | 테스트 한계 감소 없음 |
| `upgrades.json`, `intel_discoveries.json`, `campaign_progression.gd`, `upgrade_economy_smoke.gd`, `run_contract.gd`, `game_flow.gd` | 변경 0 | 연구 [0.9,1.5], 부품·신호 [0.5,1.5], `LEGACY` 가격과 ×2 클램프 변경 없음 |
| `operator_actor.gd`, `enemy_actor.gd`, `story_stage_01.gd` 기존 run 배율 | 관련 diff의 기존 clamp 숫자 변경 0 | 새 frost 토큰을 곱하고 새끼 HP의 계약 적용 경로를 한 번만 호출 |
| 1C 커밋 `5cb3e012` | op6·7·8·9 미션 JSON 네 파일만 | hazards/affix 키만 교체, 총 장판 수·정예 행 수 동일. 원래 로봇 수·HP·offset·증원·보상 변경 없음 |
| 공통 machine weathering | `site7_machine_sprite.gd` 변경 0 | plain/affix 실제 스프라이트 비교가 추가됨 |

정적 확인 명령: `git diff --name-only dca7ef20..HEAD -- <위 보호 경로들>`, `git show --stat 5cb3e012`, 기존 시험·런타임 diff 읽기. 보호 경로 명령의 출력은 비어 있었다. 그 사실을 실행하지 않은 게임 검사 PASS로 대신 쓰지 않는다.

## 5. 실행 증거 표에 넣을 수 있는 관찰값

아래는 root가 실행하여 남긴 기존 로그를 **읽어서 확인한 값**이다. 이 하위 작업에서 재실행한 결과가 아니다. 최종 HEAD의 전체 quick·보스 요약·15회 봇·승인 그림17개·시각 validator 결과는 root가 마지막 실행 기록으로 덧붙인다.

| 로그/파일 (`.cache/diag/expansion_item1_20261003/` 아래) | 관찰된 요약 | 사용 주의 |
|---|---|---|
| `elite_legacy.log` | `ELITE_AFFIX_SMOKE: PASS (71 checks)` | 기존 정예 시험 확대 |
| `elite_v2.log`, `elite_after_hazards.log` | `ELITE_EXPANSION_SMOKE: PASS (248 checks)` | 두 파일의 요약 동일 |
| `hazard_placed.log` | `HAZARD_EXPANSION_SMOKE: PASS (378 checks, 15 rooms)` | frost 추가 격자 전 기록. 최종 기록으로 대체하지 않음 |
| `hazard_v2.log` | `HAZARD_EXPANSION_SMOKE: PASS (380 checks, 15 rooms)` | 실제 방 FROST 격자를 추가하기 전 단계 기록. 최종 기록으로 대체하지 않음 |
| `hazard_all_shapes_results.json` | exit0, `PASS (438 checks, 15 rooms)`, 23.45 s | 최종 혼합 실제 배치 15방 검사; FROST 실제 방 전체 격자까지 포함 |
| `zone_placed.log` | `ZONE_HAZARD_SMOKE: PASS (366 checks, 15 rooms)` | 기존 ARC 검사 포함 |
| `capture_native_v2.log` | `EXPANSION_ITEM1_CAPTURE: PASS (124 checks)` | 제어된 런타임 네이티브 캡처 검사; 인간 플레이 아님 |

최초 `elite.log`의 246검사/1실패는 새끼 사후 정리 확인 타이밍을 수정하기 전 기록으로 남아 있다. 수정 후 로그는 위 248검사 PASS이며, 최초 FAIL을 성공 기록으로 바꾸거나 지우지 않았다.

## 6. 캐시 FPS 진단의 상수·제약

소스/영구 시험에는 포함하지 않는 `.cache/diag/expansion_item1_20261003/perf/`의 준비값: 3회, AB/BA/AB, 표본7 s, warmup2 s, op6–10 R02/R04 분리, 네이티브1920×1080, vsync off, 기존 zoom1.22, 래퍼 process timeout170 s(프로브160 s). 동일 probe만 각 프로젝트의 `.cache/`에 복사하고 baseline 코드·데이터는 바꾸지 않는다.

기준선·현재의 실제 방에서 배우 위치와 적 AI를 고정하고 같은 실제 autofire를 실행한다. op6 R04는 양쪽 모두 MORTAR를 실제로 파괴하고 현재 버전의 새끼 부화 표시는 잡아 둔다. 증원 파동과 전체 작전 FPS·균형을 재는 검사가 아니다. 별도 프로젝트의 Godot는 중지하지 않으며, 각 arm 시작의 외부 PID·명령줄과 CPU LoadPercentage를 JSON에 남긴다. 모든 회귀 러너와 이 저장소 경로 Godot가 실행 중이면 새 측정을 시작하지 않는다. 이 하위 작업에서는 프로브·래퍼를 실행하지 않았으므로 FPS 결과·승인 주장은 없다.

이 기록은 그림·플레이·균형 승인이 아니다.
