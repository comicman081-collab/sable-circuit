# 확장 항목 2 — 계약 선택과 REDLINE (2026-10-04)

범위: **2A–2F만**. 시작 HEAD `7b26a15201c76238e6b06518c9b496dccf1e393d`(항목 1과 N-1 검수 PASS). 선택 사항 9.9 N-4·N-5·N-6·N-7·N-9와 항목 3은 진행하지 않았다.

## 1. 커밋과 바뀐 파일

- `e091e25f380d8eb13d5ac1d74d418b5c2a898d27` — 계약 3택, REDLINE, 저장 5, 화면·시험·러너. 24개 경로만 지정한 로컬 커밋.
- 이 README와 증거는 다음의 별도 로컬 기록 커밋으로 반입한다. 기록 커밋 해시는 `git log -1 --format=%H -- qa/expansion_item2_20261004/README_KO.md`로 확인할 수 있다.

| 그룹 | 경로 / 역할 |
|---|---|
| 계약 | `scripts/core/run_contract.gd`: `offers`, REDLINE 제안, 표시 문구, 보스용 인자 |
| 흐름·저장 | `scripts/core/game_flow.gd`, `campaign_progression.gd`: 다음 run ID 읽기, 정식 출격에서 선택 재검증, 저장 5와 정제된 `redline_cleared` |
| 실제 전투·기록 | `scripts/missions/story_stage_01.gd`, `scripts/core/play_session_log.gd`: 보스 REDLINE 이동/간격 제외, 계약 id·REDLINE 기록 |
| UI | `scripts/ui/briefing_screen.gd`, `mission_results.gd`, `base_lobby.gd` |
| 시험 | `m11_run_contract_smoke` 신규 등록(내용 불변); `run_contract_offers_smoke`, `run_contract_ui_smoke`, `redline_smoke`, `run_contract_save_smoke`, `contract_fixture`와 UID; 기존 `play_session_log_smoke`, `site7_boss_duel_smoke` 확대 |
| 고정물 | `tests/fixtures/run_contract/head_7b26a152_golden.json`, `save_v3.json`, `save_v4.json` |
| 러너 | `tools/maintenance/run_regression_suite.py`: quick 5개 추가. 기존 등록·full_op_01–10 인자 불변 |

`RunContract.build` 함수 본문은 시작 HEAD와 바이트가 같다(LF 정규화 SHA `7e7b41b36c730cd666d9074f9622c906e415a61fd55071ec93afbe4096491b7e`). 골든 64개는 수정 전에 HEAD 실행으로 생성했다. 64개 × 작전 10개에서 키·카드·배율을 비교했다. JSON 정수/실수 저장형 차이와 1e-9 이하 왕복 오차만 허용하며 키 누락/추가는 실패다. 실제 기본값 출격은 타입을 포함한 Dictionary 전체 equality로 `build(run_id)`와 같다. 기존 GameFlow의 부가 `mission_id` 키는 계약에서 제외하고 미션 id는 원래 stage/summary/log 필드로 유지한다.

브리핑은 대화와 계약 화면이 같은 자리에서 **교대로** 보인다. 통신 패널이 보이면 계약 패널은 숨겨지고, 계약 화면이 보이면 통신 패널은 숨겨진다. 경로 패널·뒤로·출격 버튼은 기존 자리를 유지한다. 대화를 완료하면 계약 화면을 보여 주되 아무 선택 입력 없이도 첫 계약으로 출격한다. 실제 마우스·Enter 입력을 시험했고 열 작전에서 사각형·최소 글자 크기를 검사했다. 결과 보고문은 빈 줄을 없애고 손실 두 항목을 한 줄에 함께 보인다(정보 삭제 없음).

## 2. 시험과 대조

시작 전 직접 실행한 기존 `m11_run_contract_smoke.gd`: PASS. 작업 중 빠른 진단은 Godot 직접 실행으로 `.cache/diag/expansion_item2_20261004/`에 기록했다. `--only` 회귀 실행은 하지 않았다.

명령: `python tools/maintenance/run_regression_suite.py --suite quick` **1회**. stamp `20261004_164705_quick`.

결과 **52/52 PASS**, 567초, 소스 커밋 `e091e25f380d8eb13d5ac1d74d418b5c2a898d27`, 시작 dirty=0. 기존 QA 파일 **변경0/삭제0/추가0**. 원래 러너 요약: `qa/regression_runs/20261004_164705_quick/SUMMARY_KO.md`. 사본 `records/quick_SUMMARY_KO.md`, 전체 JSON `records/quick_summary.json`에 52개 결과를 보존했다.

| 러너 id | 결과 | 검사 수 | 시간 s |
|---|---|---:|---:|
| run_contract | PASS | 34 | 6.4 |
| contract_offers | PASS | 26950 | 2.2 |
| contract_ui | PASS | 484 | 9.3 |
| redline | PASS | 77 | 5.4 |
| contract_save | PASS | 69 | 0.6 |
| play_log | PASS | 25 | 6.8 |
| boss_registry | PASS | 163 | 17.4 |
| boss_pattern | PASS | 978 | 4.0 |
| boss_duel | PASS | 2184 | 57.1 |
| boss_room_fairness | PASS | 21 | 17.8 |
| robot_roster | PASS | 302 | 8.2 |
| upgrade_economy | PASS | 225 | 2.2 |
| campaign_data | PASS | 292 | 0.8 |
| combat_query_fastpath | PASS | 34 | 12.6 |
| firing_lane | PASS | 325 | 27.9 |
| hazard_expansion | PASS | 438 | 25.9 |
| world_layout | PASS | — | 16.9 |
| mood_light | PASS | — | 72.2 |

네이티브 UI 실행은 캡처 저장/크기 8검사를 더한 **492 PASS**이며 headless UI는 484 PASS다. 기존 play_log 23 →25(+계약 id/REDLINE 두 검사), boss_registry163/boss_pattern978/boss_room_fairness21/robot_roster302는 이전과 같은 수다.

실제 REDLINE 액터 시험은 작전 1의 첫 웨이브와 보스·지원 로봇의 HP(원래 encounter 행 순서에 맞춰 한 번만 ×1.5), 투사체 피해 ×1.35, 일반 로봇 이동 ×1.15/간격 ×0.8, 보스 이동·간격 ×1을 확인한다. cargo 140/10/10은 336/24/24가 된다. 과대 입력 99를 넣어 원래 HP·피해 ×3, 속도·간격 ×2, 보상 ×4 상한도 실제 경로로 확인했다.

**배율 두 번 대조**: 정상 Stage를 상속한 사본에서 `_spawn_wave`의 `apply_run_modifiers` 한 줄만 두 번 호출했다. 같은 77검사 중 7개의 실제 HP 검사가 실패하고 Godot 종료 코드는 1이었다. 파싱·SCRIPT ERROR 0. 원래 시험은 PASS 77. 원본 게임 파일을 변형했다 되돌리는 방법을 쓰지 않았으며 사본·출처·SHA·원출력은 `records/counter_double/`에 보존한다.

보스 시험은 표준의 모든 기존 1,124검사를 유지하고 REDLINE 10종/각 6공격을 더해 2,184검사가 됐다(+1,060). 원래 SIGNATURES·경고 개수·기하·시간·기본 경고 피해 상한은 그대로다. REDLINE에서 이미 존재하던 경고 피해 경로(`source.run_damage_multiplier`)를 반영해 실제 대상 피해를 검사한다. 보스 공격 패턴이나 경고 코드 수정 0. 표준 공정성 검사에서 경고 최대 20/투사체 최대 24 등의 한계는 그대로다. REDLINE은 기존 계약의 피해 곱셈 때문에 경고의 실제 피해가 20×1.35=27이 될 수 있다. 경고 시간과 모양은 표준과 같고 ANCHOR 0.95s/나머지 1.1s WINDUP을 유지한다.

전멸·조기 추출·미리보기·잠긴 결과·중복 거래·클리어 전 위조 REDLINE은 REDLINE 기록을 만들지 않는다. 이미 깬 작전에서 전체 EXTRACTED한 유효 결과만 기록된다. 일반 `cleared_missions`와 해금은 REDLINE으로 바뀌지 않는다. 저장 v3·v4의 모든 고정 필드/자원/분석/장비/거래 id/run serial을 보존하고 v5로 왕복했다. 미래 필드와 모르는/클리어하지 않은 REDLINE id는 버린다. 플레이어 저장은 사용하지 않고 시험 전용 프로젝트 경로만 쓴다.

플레이어 `campaign_progression_v1.json`과 `settings.cfg`의 존재 여부·SHA·크기·수정 시각을 quick 전후 비교해 **동일**함을 확인했다(`records/player_files_before_quick.json`, `player_files_after_quick.json`). 실제 저장 파일의 내용은 기록으로 복사하지 않았다.

full 스위트는 실행하지 않았다(사용자 지시대로 Claude 담당). `full_op_01–10`의 기본 계약/인자/시험 코드는 불변이다.

## 3. 상수와 한계

| 파일·이름 | 이전 → 이후 | 이유 |
|---|---|---|
| `campaign_progression.gd / SAVE_SCHEMA_VERSION` | 4 → 5 | REDLINE 클리어 목록 저장 |
| `run_contract.gd / REDLINE_HEALTH` | 없음 → 1.50 | 첫 제안, ≤1.50 |
| `REDLINE_DAMAGE` | 없음 → 1.35 | 첫 제안, ≤1.35 |
| `REDLINE_SPEED` | 없음 → 1.15 | 일반 로봇만; ≤1.15 |
| `REDLINE_INTERVAL` | 없음 → 0.80 | 일반 로봇만; ≥0.80 |
| `REDLINE_HAZARD_REWARD` | 없음 → 1.60 | 첫 제안, ≤1.60 |
| `REDLINE_OPPORTUNITY_REWARD` | 없음 → 1.50 | 기존 기회 클램프 [0.5,3.0] 안; 총 보상 2.40 |
| 위험 점수 | 표준 2–3(불변), REDLINE 없음 → 5 | 표준 제안보다 높음 |
| 브리핑 UI | 계약 없음 → 패널(476,196,758×400), 버튼(280,622,480×50), 선택(714×72/간격77) | 동시에 보이는 기존 사각형과 겹치지 않음 |
| 결과 UI | 보고문 높이220 →184, 계약 표시(34,326,540×40)/12pt 추가 | 기존 정보 유지, 별도 자리 확보 |
| 러너 | 78(quick47/full31) →83(quick52/full31) | 기존 M11 등록 + 새 시험 4개 |
| `boss_duel` 검사 | 1,124 →2,184 | 표준 유지, REDLINE 10종 추가 |

새 preload 상수는 자원 경로를 가리킨다: `RunContract.MissionCatalog` → `site7_campaign.gd`; 제안 시험의 `Fixture` → `tests/support/contract_fixture.gd`; 저장 시험의 `Output/Fixture`, 실제 액터 시험의 `Stage/Output`, UI 시험의 `Flow/Output` → 기존 Stage/GameFlow/test_output과 새 fixture 비교기. 기존 자원 경로 상수는 변경0.

구현 클램프(위험 보상1–2, 기회0.5–3, 적 HP·피해0.5–3, 속도·간격0.5–2, 스테이지 보상0.5–4), x2 캠페인/연산자 상한, 보스 공정성·고정 와인드업, 경제 대역·LEGACY·가격은 **변경 0**. 테스트 상수 TICK/SPEEDUP/BOSS_HEALTH/SIGNATURES와 기존 테스트 시간 상한도 변경 0.

세 제안은 같은 회수 우선순위에 서로 다른 위험 카드를 붙인다. 위험이 더 큰 제안이 특정 자원의 보상을 낮추는 경우를 방지하면서 첫 기본값을 완전히 보존한다. 선택은 run/mission에 결정적이며 다음 출격이나 저장에 남지 않는다.

## 4. 데이터·그림 불변

미션 JSON, `data/progression/`, `data/story/`, `data/visual/`, `assets/`, `art_src/`, `motion_lab_v1/` 변경 **0**. 데이터 변경은 런타임의 저장 schema5/`redline_cleared`뿐이며 플레이어 저장 파일은 변경하지 않았다. 작전 10 승인 파일 **17/17 SHA 일치**. 바닥·덮개·벽·보스 원화·코드·패턴 수정 0. `world_layout --check`와 `mood_light --check`는 quick에서 실행된다.

## 5. 네이티브 1080p 증거

명령: `Godot --path . --log-file .cache/diag/expansion_item2_20261004/native_release_engine.log -s res://tests/smoke/run_contract_ui_smoke.gd -- --out=res://.cache/diag/expansion_item2_20261004/native_release`.

실제 실행 창/viewport 1920×1080, 기존 UI 논리 공간1280×720(게임의 canvas stretch ×1.5). 생성 그림·업스케일한 캡처 없음. 원래 게임 UI와 입력/흐름을 실행한다. 결과와 로비 표시를 위한 cargo/클리어 기록은 시험 메모리의 고정물이다. **사람의 플레이 캡처나 작전 완주 증거가 아니다.**

| 경로(모두1920×1080) | 장면 | SHA-256 |
|---|---|---|
| `captures/briefing_default.png` | 기본값을 건드리지 않은 출격 전 3택 | `672c26e07f2d78e9b97f532d4948c6ad9927a75290c5837eec5736fa0760cb97` |
| `captures/briefing_redline.png` | 이미 깬 작전의 REDLINE 네 번째 선택 | `f0480557d9cb1bf0eb8df6e2d8132c09e35586386dae98747119ecaf37e2cd2c` |
| `captures/results_redline.png` | 적용 계약과 보상2.40 표시(시험 cargo) | `53d7a9be6f892c2c80da0e5eb6ff6bb195ceaad90de9f7e053982f6219fe35dc` |
| `captures/lobby_redline_cleared.png` | 클리어한 REDLINE의 로비/작전 선택 표시 | `419654314f1dfca66bc77a0e0e829ef95b17c63f0fa9b132666708bfa4c91e66` |

`tools/art_pipeline/validate_visual_evidence_1080p.py … --require-dynamic-capture --output qa/expansion_item2_20261004/records/visual_validation.json`: container **PASS**, dynamic_capture **PASS**, 이미지4/4 디코드/크기 PASS. 그 PASS는 **크기와 디코드뿐**이고 그림·취향·플레이·균형 승인이 아니다. 수동으로 네 화면을 보아 새 선택/계약/REDLINE 표시의 겹침·잘림을 확인했다. FPS 개선이나 후퇴가 없다는 주장은 하지 않는다.

## 6. REDLINE 제안 수치용 봇

full 스위트가 아닌 **진단 사본 2회**. 기존 `site7_full_operation_smoke.gd`를 `.cache/`로 복사해 중립 계약 인자 하나를 `RunContract.redline(run_id)`로 바꿨다. 원래 승리·순서·처치·입력·피해 검사는 모두 그대로다. 건강/탄약/피해 치트나 삭제/텔레포트 없음. 원래 데이터·게임 코드·기본 full_op 등록 변경 0. 시작에 이미 클리어한 재도전의 전투 제안을 재현하고 Campaign 저장 거래는 쓰지 않는다.

| 작전 | 계약 | 결과(승리 검사는 FAIL) | 마지막 클리어 깊이 | 경과 s | 받은 피해 HP |
|---|---|---|---|---|---|
| 1 | REDLINE | WIPED(보스방) | 4/6 | 138.870 | 441.900 |
| 10 | REDLINE | WIPED(보스방) | 4/6 | 155.670 | 625.300 |

공통 실패는 추출/6방 완주/총처치 조건이며 작전10은 두 선택방 회수 조건도 실패했다. 시간 초과·경로 정지·스크립트 오류 없음. 두 실행을 PASS로 계산하지 않는다. HEAD 계약의 새 봇 대조는 실행하지 않았으므로 HEAD 대비 피해·승률 변화는 주장하지 않는다. PC 부하와 봇 선택으로 결과가 흔들리며 표본은 각 1회뿐이다. 이 배율과 2.4배 보상은 **제안**이고 확정은 사용자와 사람 플레이의 몫이다. Claude는 full/독립 봇/골든/저장/화면을 재검수한다.

증거 폴더의 `.gitattributes`는 이 폴더에만 줄끝 변환을 끈다. Git 체크아웃에서도 원출력·캡처의 바이트와 `records/evidence_manifest.json`의 SHA-256을 보존한다.

## 7. 정리와 남은 검수

정리 대상인 옛 `native/`, `native_final/` 캡처·로그 등 **15개/23,725,855.0 bytes**의 파일 삭제가 자동 승인 검토에서 **`blocked by policy`**로 거절됐다. 명령이 실행되기 전에 거절되어 삭제 **0**이며 다른 삭제 경로로 우회하지 않았다. 파일은 모두 보존하고 정확한 경로·SHA·사유를 `records/cleanup_20261004.json`에 남겼다. 현재 `native_release` 작업 이미지와 QA, 기준선, 대조 사본, 봇 원출력은 검수용으로 보존한다.

Claude의 항목 2 검수는 아직 받지 않았다. 검증은 PC 네이티브와 headless이며 웹/내보내기 실행은 하지 않았다. 선택 사항 9.9의 시험 보강은 미착수 상태다. 항목 3은 시작하지 않았다. 코드·문구·캡처의 기술 검사가 인간의 난이도·취향 결정을 대신하지 않는다.

**이 기록은 그림·플레이·균형 승인이 아니다.**


## 8. B-1 수정 (2026-10-04)

범위: 제작 지시서 9.10의 **B-1만**. 시작 HEAD `f2cbe1d653cae292e54a5f34a2c0ad9c6442c22b`. 선택 사항 N-A/N-B1…B4는 미착수이며 항목 3은 시작하지 않았다.

### 바꾼 파일과 복원

- `scripts/core/game_flow.gd`: 계약 기본값/대안/REDLINE 선택을 마친 뒤, `view.configure_campaign` 바로 앞에 `7b26a152`와 같은 `last_run_contract["mission_id"] = id` 한 줄을 복원했다. 다른 게임 코드 변경 0.
- `tests/smoke/run_contract_ui_smoke.gd`: 아래 세 기대 사전에 알려진 작전 id `MIS_CH01_01` 키 하나를 추가했다. 실제 계약에서 키를 지우거나 부분 비교하지 않고 **Dictionary 전체 equality**를 유지했다. 기존 `RunContract.is_redline(chosen)`도 유지한다.
- 이 README 끝에만 정정·검증을 덧붙였고, 새 러너 요약 4개를 `records/b1_fix/`에 반입했다. 앞선 기록·캡처·매니페스트는 덮어쓰지 않았다.

게임 코드 diff가 그 한 줄만임을 시작 HEAD와 비교했다. UI의 check 호출 수는 전후 같으며 검사 삭제 0. 한계·상수·데이터·그림·러너 등록·다른 시험 변경 0.

### 세 검사의 이전 → 이후

| 기존 검사 | 이전 기대값 → 이후 기대값 |
|---|---|
| `untouched/default briefing deploy exactly equals HEAD contract (no added keys)` | `stage.debug_run_contract() == build(stage._run_id)` → `expected_default = build(stage._run_id)`에 `mission_id: MIS_CH01_01`을 추가한 사전과 전체 equality. 새 라벨은 `...plus mission_id (no other added keys)` |
| `alternative survives actual GameFlow deploy` | 선택 사전 `chosen` → `chosen`에 `mission_id: MIS_CH01_01` 하나를 더한 기대 사전과 전체 equality |
| `REDLINE flows to actual stage` | 선택 사전 `chosen` → `chosen`에 같은 mission_id 하나를 더한 기대 사전과 전체 equality, AND `is_redline(chosen)` 유지 |

이 절은 앞의 1절에서 계약의 `mission_id`를 제외했다고 설명한 결정을 정정한다. `build`/제안/골든은 불변이며, GameFlow가 Stage에 주는 사전은 이전 HEAD처럼 mission_id를 포함한다. 앞의 `records/evidence_manifest.json`은 `b4aa2ae0`의 원래 기록 스냅샷이며, 이번에 덧붙인 README 해시를 뜻하지 않는다.

### 실행한 시험

```
python tools/maintenance/run_regression_suite.py --only campaign,contract_ui,contract_offers,redline,contract_save,run_contract,play_log,m13_loadout,m10_intel,demo_integration
python tools/maintenance/run_regression_suite.py --suite quick
```

- `only`: **10/10 PASS**, 86초. 요약 `qa/regression_runs/20261004_215548_custom/SUMMARY_KO.md`; 바이트 동일 사본 `records/b1_fix/only_SUMMARY_KO.md`, `only_summary.json`. 기존 QA 변경/삭제/추가 **0/0/0**.

- `quick`: **52/52 PASS**, 563초. 요약 `qa/regression_runs/20261004_215901_quick/SUMMARY_KO.md`; 바이트 동일 사본 `records/b1_fix/quick_SUMMARY_KO.md`, `quick_summary.json`. 기존 QA 변경/삭제/추가 **0/0/0**.

두 실행은 위 시작 HEAD + 게임/UI 두 파일 수정(dirty=2)에서 끝났고, 그 동일 수정과 이 기록을 경로 지정한 로컬 커밋 하나에 담는다. 커밋 해시는 `git log -1 --format=%H -- scripts/core/game_flow.gd`로 확인할 수 있다.

#### 지정 묶음 (10개)

| 시험 id | 결과 | 검사 수 | 시간 s |
|---|---|---:|---:|
| run_contract | PASS | 34 | 6.4 |
| contract_offers | PASS | 26950 | 2.2 |
| contract_ui | PASS | 484 | 8.2 |
| redline | PASS | 77 | 5.4 |
| contract_save | PASS | 69 | 0.6 |
| play_log | PASS | 25 | 6.2 |
| demo_integration | PASS | 26 | 8.0 |
| m10_intel | PASS | 39 | 4.8 |
| m13_loadout | PASS | 46 | 5.2 |
| campaign | PASS | 235 | 23.3 |

#### quick 전체 (52개, 1회)

| 시험 id | 결과 | 검사 수 | 시간 s |
|---|---|---:|---:|
| combat_density | PASS | 67 | 18.8 |
| cover_navigation | PASS | 43 | 20.7 |
| floor_segment | PASS | 23 | 42.5 |
| combat_query_fastpath | PASS | 34 | 13.2 |
| player_cover | PASS | 5 | 7.6 |
| cover_alpha_clip | PASS | 5 | 2.0 |
| cover_texture | PASS | 17 | 2.6 |
| battle_flow | PASS | —(러너 계수 없음) | 9.0 |
| combat_entry | PASS | —(러너 계수 없음) | 7.4 |
| drone_app | PASS | 171 | 2.4 |
| anchor_app | PASS | 271 | 1.8 |
| campaign_data | PASS | 292 | 0.6 |
| upgrade_economy | PASS | 225 | 1.6 |
| boss_registry | PASS | 163 | 15.5 |
| boss_pattern | PASS | 978 | 3.2 |
| boss_duel | PASS | 2184 | 55.9 |
| boss_room_fairness | PASS | 21 | 18.0 |
| robot_roster | PASS | 302 | 8.8 |
| enemy_facing | PASS | 224 | 2.8 |
| machine_source | PASS | 436 | 2.6 |
| emission_owner | PASS | 1293 | 5.2 |
| m2_story | PASS | 27 | 5.6 |
| m9_skill | PASS | 44 | 4.8 |
| m10_base_ui | PASS | 10 | 1.0 |
| m10_persistence | PASS | 27 | 0.6 |
| run_contract | PASS | 34 | 5.8 |
| contract_offers | PASS | 26950 | 2.0 |
| contract_ui | PASS | 484 | 8.8 |
| redline | PASS | 77 | 5.2 |
| contract_save | PASS | 69 | 0.8 |
| m12_revive | PASS | 25 | 4.8 |
| play_log | PASS | 25 | 6.2 |
| hit_hurt_vfx | PASS | 47 | 2.8 |
| combat_vfx | PASS | 189 | 3.0 |
| elite_affix | PASS | 71 | 5.4 |
| elite_expansion | PASS | 438 | 7.4 |
| zone_hazard | PASS | 366 | 48.1 |
| hazard_expansion | PASS | 438 | 25.1 |
| firing_lane | PASS | 325 | 27.7 |
| platform_carry | PASS | 6 | 5.8 |
| contact_carry | PASS | 27 | 14.4 |
| world_layout | PASS | —(러너 계수 없음) | 17.2 |
| mood_light | PASS | —(러너 계수 없음) | 77.0 |
| walk_registration | PASS | —(러너 계수 없음) | 1.2 |
| plate_axis | PASS | 2 | 2.8 |
| variety_placement | PASS | 10 | 1.6 |
| seam_waiver | PASS | 10 | 2.2 |
| mood_contact | PASS | 13 | 3.0 |
| deploy_warmer | PASS | 83 | 7.2 |
| m13_migration | PASS | 9 | 0.8 |
| m13_campaign | PASS | 16 | 0.6 |
| m13_runtime | PASS | 18 | 5.0 |

러너 시작 전마다 Get-CimInstance로 기존 러너가 없는 것을 확인했고 순차 실행했다. 각 실행이 끝날 때까지 QA 기록을 바꾸지 않았다. full은 실행하지 않았다(Claude 담당). 게임 코드 복원과 실제 출격 흐름의 기술 검증이며 그림·플레이·균형 승인은 아니다. K-13 최종 확인과 항목 2 재검수는 Claude가 한다.
