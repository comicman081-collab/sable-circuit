# SITE-7 작전 7 COLD STORAGE 켜기 (2026-09-30)

**판정: PASS_TECHNICAL_ONLY.** 코드와 자동 시험이 통과했다는 뜻이다. 그림, 균형, 플레이 승인이 아니다. 작전 7은 이제 **출격 가능**하다. 작전 8–10은 판이 없어 그대로 출격 불가다(`deployable: false`, `staging` 유지).

사용자 지시(2026-09-30): "코덱스 작업 끝났다. 확인하고 작전 7 켜라". 근거는 `docs/production/SITE7_OPERATIONS_6_10_DESIGN_KO.md` 6절 C이고, 작전 6을 켠 기록 `qa/site7_op6_enable_20260929/README_KO.md`의 교훈(갈래방 종류, 오래된 반복문 게이트, 방 바닥 공정성)을 따랐다.

## 1. 한눈에

| 항목 | 결과 |
|---|---|
| 작전 7 켜기(6절 C 1–3) | **됨.** `staging`, `deployable: false`, `pending`을 지웠고 작전 6의 COMMAND 디브리프가 Cold Storage를 알린다 |
| Codex 납품 확인 | 판 15장(방 8, 통로 7), 이음부 14개 0 px, 무드·심연·엄폐 행. 3절 |
| 데이터 게이트(`campaign_data`, `campaign`, `demo_integration`) | PASS (279 / 179 / 26 검사) |
| 켜며 찾은 것 | 보스방 바닥 공정성 시험이 CRYO의 3페이즈 축 레인(900 px)을 잡았다. **레인을 300 px로 줄여 맞췄다**(규칙은 그대로). 4절 |
| 작전 7 풀플레이(`full_op_07`) | PASS. 봇이 EXTRACTED까지 클리어했고 CRYO가 세 페이즈에서 공격했다(5절) |
| 실제 보스방 바닥에서의 공정성(`boss_room_fairness`) | PASS. R05_VAULT 격자 25 px에서 공격 4,680개 중 0개 실패(고치기 전 10곳), 가장 가까운 안전 바닥 120 px(한도 180), 가장 빠듯한 탈출 여유 0.43 s(한도 0.25 s) |
| CRYO 자기 방 캡처(1080p) | **됨.** 7장과 1:1 크롭 시트 2장(7절) |
| 게임 소리 영상 | **됨.** 10초 600프레임, 실제 게임 믹스(8절) |
| quick·full 스위트 | 최종 커밋 `a602501a` 위에서 quick 41/41, full 67/67 PASS, `qa/` 가드 변경 0(6절) |
| 같은 세션 회전 A/B FPS | **못 했다**(10절) |
| 사람 플레이, 균형, 그림 승인 | **못 했다.** 사용자 몫이다(10절) |

## 2. 커밋과 바뀐 것

| 커밋 | 내용 |
|---|---|
| `f167523a` | (Codex) 작전 7 판 통합: 판 15장, 바닥·문·월드 배치·전투 지형·엄폐·무드·램프·허공 마스크·심연 `cryo` 스타일, 판 목록을 넓힌 시험들. 작전 7은 여전히 출격 불가였다(`deployable: false`) |
| `5dedb07e` | 작전 7 켜기. 러너의 `full_op_07`, 라이브 진입 스모크의 반복 범위, 오래된 반복문 게이트 일반화, 보스 캡처가 CRYO를 자기 방에서 찍는 것, CRYO 축 레인 300 px와 그 고정 |
| `a602501a` | 문서: `AGENTS.md`("Operation 7 enabled"와 작전 6–10 절), 설계 문서(상태표, 6절 C), 보스 지시서(구현된 `frost_sweep` 값) |
| (이 폴더를 추가한 커밋) | 이 기록, `README.md`와 `sound/README.md`의 낡은 "작전 6–10은 출격 불가" 문장. 코드는 건드리지 않았다. 커밋은 `git log -- qa/site7_op7_enable_20260930`로 찾는다 |

**켜는 순서(설계 문서 6절 C).**

| 순서 | 한 일 |
|---|---|
| 1 | `data/missions/MIS_CH01_07.json`에서 `staging` 블록을 지웠다 |
| 2 | `data/story/site7_campaign.json`의 작전 7 행에서 `"deployable": false`와 `"pending"`을 지웠다 |
| 3 | 작전 6의 COMMAND 디브리프를 `Verdant Lock complete. Cold Storage is now available.`로 바꿨다(데이터 게이트가 강제한다). 작전 7 자신의 디브리프는 "Cold Storage complete. Refit at base."로 두었다(출격 불가인 작전 8을 이야기에 올리지 않는다) |
| 4 | 게이트 `campaign_data`, `campaign`, `demo_integration` |
| 5 | 6에서 멈춘 곳: `tests/smoke/site7_live_entry_autostart_smoke.gd`의 `range(1, 7)`을 `range(1, 8)`로, 러너의 `full_op_%02d`를 7까지. 나머지 작전 반복문은 Codex가 판을 통합하며 이미 7까지 넓혀 두었다(`f167523a`). `campaign_data`의 오래된 반복문 게이트가 남은 곳이 없음을 확인한다 |

**오래된 반복문 게이트를 일반화했다.** 작전 6을 켤 때 만든 게이트(`stale_loop_gaps`)는 "다섯에서 멈춘 반복문"만 알았다. 이제 출격 가능한 작전 수 N이 얼마든 5 ≤ 끝 < N인 `range(1, 끝 + 1)` 반복문, 튜플, 목록, 표가 남아 있으면 파일과 끝 번호를 말해 준다. 음성·양성 대조를 더했다: 여섯 작전에서 멈춘 반복문(일곱이 출격 가능할 때 거절), 붙여 쓴 `range(1,7)`, 튜플 `(1,2,3,4,5,6)`, `"MIS_CH01_06"]`으로 끝나는 목록, 06으로 끝나는 표, 일곱으로 넓힌 것(통과), 여덟이 출격 가능할 때 하나 모자란 것(거절). 작전 8을 켤 때 넓힐 곳은 이 게이트가 알려 준다.

## 3. Codex 납품 확인

`qa/site7_ops_6_10_plates_20260929/stage_b/README_KO.md`(Codex의 단계 B 기록)와 커밋 `f167523a`를 읽고, 아래를 직접 확인했다.

| 확인한 것 | 결과 |
|---|---|
| 판 15장 | 방 `S7_R01`–`R06`, 갈래 `S7_O01`, `S7_O02`, 통로 `S7_C01`–`C07`은 이렇게 있다: RAW_NATIVE와 MASTER는 `art_src/environments/site7_v2/stage07/`, 게임용 GAME은 `assets/environments/site7_v2/stage07/`. RAW와 MASTER는 바이트가 같다(Codex 기록). `S7_R01`의 첫 후보는 S3_R01의 원형 팬 벽 실루엣을 되풀이해 거절되어 `art_src/environments/site7_v2/_quarantine/S7_R01/attempt01`에 보존되어 있고, 나머지 14장은 첫 후보를 채택했다 |
| 판이 다른 작전과 겹치지 않는가 | 겹치지 않는다. `tests/smoke/site7_battle_geometry_smoke.gd`가 판마다 한 작전만 쓰는지 확인한다(`battle_geometry` 3,491검사 PASS) |
| 이음부 | 월드 레이아웃의 14개 연결 틈이 모두 0 px다(Codex의 strict audit). `world_layout --check`가 quick 스위트에서 PASS(7개 작전)한다 |
| 무드·램프·허공 마스크 | `mood_light --check`가 quick 스위트에서 PASS한다(판 105장, 램프 풀 530개, 허공 마스크 105장: 작전 1–7) |
| 작전 데이터 | 방 여덟 개(R01_INTAKE 이벤트, R02_FREEZE 전투, R03_LEDGER 연구, R04_COMPRESSORS 엘리트, R05_VAULT 보스, R06_LOCK 탈출, 갈래 O01_REAGENTS ← R02, O02_RECORDER ← R05), 보스 CRYO COMPRESSOR 체력 1,740, 패턴 `frost_sweep`. `campaign_data` 통과 |
| 엄폐 소품 | 9개(작전 6은 11개, 1–5는 12–15개). **R05_VAULT의 목록이 비어 있다**(Codex 기록: 방 중앙에 엄폐물을 두지 않음). 작전 1–7에서 엄폐물이 없는 방은 이 방 하나다. 게이트는 방마다 행이 있는지, 진행 스모크는 작전 전체에 방 수 이상의 소품이 붙는지를 보므로 통과한다. 방 설계의 선택으로 보고 고치지 않았다(10절) |
| 보스 | `BOSS_SITE7_CRYO_01`은 2026-09-29에 등록됐다(프로필, 패턴, 효과, 안내문). 이번에 처음 자기 방에서 잰다(4절) |

## 4. 실제 보스방 바닥에서의 공정성

`tests/smoke/site7_boss_room_fairness_smoke.gd`(quick `boss_room_fairness`)는 출격 가능한 각 작전의 새 보스를 자기 방에 세우고 여섯 공격(세 페이즈 × A/B)을 모두 깐다. 대원이 설 수 있는 모든 자리(칠해진 바닥 위, 엄폐 밖, 보스에서 150–800 px)에서 경고가 덮지 않는 1.5 대원 폭의 바닥이 180 px 안에 있고, 곧게 걸어 닿을 수 있고, 가장 느린 걸음(138 px/s)이 그 자리의 경고가 터지기 0.25 s 전에 닿아야 한다.

**작전 7에서 처음 실패했다.** 작전 7이 열리자 이 시험이 R05_VAULT에서 실패했다(`20260930_011528_custom`, `boss_room_fairness` FAIL 9검사). 원인은 CRYO의 3페이즈 **축 레인**이다. 압축기에서 대상 방향으로 900 px를 달리는 이 레인은 빈 바닥에서는 문제가 없었지만(`boss_pattern`이 800 × 800 px 바닥에서 통과) 실제 방의 좁은 곳, 서쪽 턱과 문 어귀에서는 레인이 대상 자리를 지나 계속 달려서 그 옆에 1.5 대원 폭의 안전 바닥을 남기지 않았다.

| 축 레인 길이 | 실패한 공격 (20 px 격자, 7,260개) | (25 px, 4,680개) | (30 px, 3,300개) | 가장 가까운 안전 바닥(최악) | 가장 빠듯한 탈출 여유 |
|---:|---:|---:|---:|---:|---:|
| 900 (고치기 전) | 20 | 10 | 12 | 210–240 px | −0.22 ~ −0.86 s |
| 400 | 14 | 8 | 8 | 210 px | −0.22 s |
| 340 | 0 | 0 | 0 | 120 px | 0.43 s |
| **300 (지금)** | **0** | **0** | **0** | **120 px** | **0.43 s** |
| 없음(비교용) | 0 | 0 | 0 | 90 px | 0.65–0.67 s |

- **고친 것은 보스다. 한도가 아니다.** 축 레인을 `FROST_AXIS_REACH` = 300 px로 줄였다(`scripts/combat/site7_enemy_tactics.gd`): 압축기에서 두 번째 막대까지 가서 멈춘다. 레인의 폭(반폭 22)과 준비 시간(1.4 s), 막대 네 개와 파도 순서, 시그니처(`S0C0L5 / S0C0L5`)는 그대로다. 안전 바닥 180 px와 탈출 여유 0.25 s는 낮추지 않았다.
- `boss_pattern`이 이제 축 레인 길이 300과 상한 340을 고정한다(400 px는 이 방에서 실패했으므로 더 긴 레인은 공정성 후퇴다). 나머지 946검사는 그대로 통과한다.
- 표는 레인 길이를 임시 환경 변수로 바꿔 가며 잰 것이고 그 코드는 커밋에 없다(`boss_room_fairness_axis_lane_sweep.json`). 300 px 근처는 격자 20–40 px 21가지 모두 실패 0이다(가장 가까운 안전 바닥 120 px, 탈출 여유 0.43 s 이상).
- 작전 6의 R05_ATRIUM은 그대로 통과한다(최악 90 px, 여유 1.05 s).

고친 뒤 세 격자에서(`boss_room_fairness_grid100.json`, `boss_room_fairness_grid50.json`, `boss_room_fairness_grid25.json`):

| 격자 | 서 볼 자리 | 시험한 공격 | 실패 | 가장 가까운 안전 바닥(최악) | 가장 빠듯한 탈출 여유 | 엄폐 |
|---|---:|---:|---:|---:|---:|---:|
| 100 px | 46 | 276 | 0 | 120 px | 0.65 s | 0 |
| 50 px(러너 기본) | 198 | 1,188 | 0 | 120 px | 0.45 s | 0 |
| 25 px | 780 | 4,680 | 0 | 120 px | 0.43 s | 0 |

최악은 페이즈 3 공격 A에서 보스에서 316 px 떨어진 자리다(안전 바닥이 120 px). 방에 엄폐가 0개라 엄폐가 경로를 막는 일은 없다.

## 5. 작전 7 풀플레이

`tests/smoke/site7_full_operation_smoke.gd --mission=MIS_CH01_07`(러너 `full_op_07`). 봇이 실제 액터 물리, 무기 쿨다운, 투사체 충돌, 임무 상호작용으로 진행한다(`debug_fire_once` 없음). 파일: `full_operation_op07.json`(최종 full 실행 `20260930_015157_full`의 `full_op_07`, 커밋 `a602501a` 위).

- 결과 `PASS_TECHNICAL_PLAYTHROUGH`: 결과 `EXTRACTED`, 전 경로 클리어, 적 23기 처치, 게임 시간 219.4 s(러너 시간 223.1 s), 보급 상자(`field_supplies`)와 증거(`THERMAL LEDGER`) 회수. 확보한 것은 연구 478, 부품 7, 신호 조각 3, 정보 표본 6(ABERRANT 2, ANCHOR 1, SECURITY 3)이다.
- CRYO가 페이즈 1에서 3번, 페이즈 2에서 1번, 페이즈 3에서 4번 공격했고(모두 8번), 대원에게 준 피해는 합해서 114.0이다. 스킬은 Q·E·X 실제 키 입력으로 썼다(Q 11, E 11, X 12).
- 축 레인을 줄인 뒤 처음 돌린 실행(`20260930_013244_custom`, 224.6초)도 PASS했다(CRYO 공격 2·3·6번, 피해 110.2). 통과는 두 번이다.
- 봇의 통과는 균형 승인이 아니다. `full_op_03`처럼 마지막 보스에서 봇이 가끔 지는지는 두 번으로는 알 수 없다. 같은 full 실행에서 `full_op_01`–`06`도 모두 PASS했다(126 / 126 / 147 / 154 / 160 / 188초).

## 6. 시험 결과

`regression_runs.json`이 아래 실행의 요약을 담고 있다(러너 폴더 `qa/regression_runs/`는 git이 무시한다). 시간 열은 한 시험만 돌린 실행이면 그 시험의 시간이고, 스위트면 실행 전체 시간이다.

| 실행 | 내용 | 결과 | 시간 |
|---|---|---|---:|
| `20260930_011528_custom` | `campaign_data`, `boss_registry`, `boss_room_fairness`, `demo_integration`, `campaign`. 작전 7을 켠 직후, 축 레인을 줄이기 전(커밋 `abed2972` 위, 커밋 전 경로 6개) | **FAIL** — `boss_room_fairness`(9검사)가 R05_VAULT에서 실패. 나머지는 PASS(279 / 160 / 26 / 179검사) | 43.0초 |
| `20260930_013004_custom` | `boss_registry`(160), `boss_pattern`(946), `boss_duel`(1,124), `boss_room_fairness`(9). 축 레인을 300 px로 줄인 뒤(커밋 전 경로 8개) | PASS 4개 중 4개 | 63.0초 |
| `20260930_013244_custom` | `full_op_07`, 같은 작업 폴더 | PASS | 224.6초 |
| `20260930_014627_quick` | quick 스위트, **커밋 `a602501a` 위**(`git_head` `a602501a`, 더러운 경로 없음) | PASS 41개 중 41개 PASS, `qa/` 가드 바뀜 0·사라짐 0·추가 0 | 294초 |
| `20260930_015157_full` | full 스위트, 같은 커밋 위(더러운 경로 없음) | PASS 67개 중 67개 PASS, `qa/` 가드 바뀜 0·사라짐 0·추가 0 | 3,252초 |

- 마지막 두 실행은 코드와 문서가 모두 커밋된 깨끗한 작업 폴더에서 돌았다(Codex의 커밋 전 파일도 없었다). 이 기록의 커밋은 기록과 두 `README.md`만 더하고 코드는 그대로이므로 두 실행은 그 커밋에도 그대로 해당한다.
- full 실행은 작전 7에 해당하는 시험을 모두 새로 돌렸다: `full_op_07`(223초), `connector_alignment`(742검사, 737초, `--mission=7` 문턱 양방향 왕복 포함), `traversal_audit`(1,687검사, 607초), `battle_geometry`(3,491검사), `world_route`(67검사), `boss_capture_geometry`, `boss_lineup`, `campaign`(179검사), `demo_integration`(26검사). 작전 6의 기록은 `connector_alignment`와 `traversal_audit`를 팁에서 다시 돌리지 못했다(그 full 실행은 Codex의 작전 7 판이 커밋되기 전에 시작됐다). 이번 full 실행은 판 15장, 작전 7 켜기, 축 레인 변경이 모두 커밋된 깨끗한 작업 폴더에서 작전 1–7 전체를 한 번에 확인했다.
- quick의 `world_layout`은 PASS(7개 작전)이고 `mood_light`는 PASS(판 105장, 램프 풀 530개, 허공 마스크 105장)다. Codex가 판을 넘길 때 만든 데이터가 오래되지 않았다는 뜻이다.
- 한 번 실패한 것은 `boss_room_fairness`뿐이고 4절의 진짜 발견이다. 시험을 낮추지 않고 보스를 고쳐 PASS했다.

## 7. 자기 방 캡처 (CRYO COMPRESSOR, R05_VAULT)

창을 띄운 실제 렌더, 네이티브 1920 × 1080. `tests/render/site7_boss_pattern_capture.gd`가 이제 CRYO를 미션 3의 시험대가 아니라 **작전 7의 자기 보스방**에 세운다(작전 8–10은 계속 시험대). 캡처는 통제된 페이즈 고정 장면(`controlled_phase_fixture`)이다: 페이즈와 공격 번호를 시험이 정해 넣었다.

| 파일 | 내용 |
|---|---|
| `captures/mission7_boss_room.png` | 보스방 전경: 압축기와 냉각 패널, 체력바, 기둥 네 개, 대원 패널과 HUD(목표 "Shut down the cryo compressor", 선택 목표 Reagent Stores와 Cold Recorder) |
| `captures/mission7_phase{1,2,3}{a,b}_warning.png` × 6 | 페이즈·공격별로 바닥에 깔린 경고. 경고 수: 1A 2, 1B 0(얼음 파편 2발), 2A 3, 2B 4, 3A 5, 3B 5 |
| `crop_sheets_1to1/mission7_cryo_1to1_sheet_{a,b}.png` | 보스와 경고 부분을 보간 없이 오려 붙인 1:1 시트(원본 해상도) |

- 모든 장면에서 경고가 덮지 않는 안전 바닥이 이 방의 실제 바닥에 있다(`safe_floor_gap` 6/6). 경고 수는 일곱 개 한도 안이다.
- 눈으로 본 것: 압축기가 방 가운데 서고 체력바가 위에 뜬다. 서리 막대가 압축기에서 대상 쪽으로 평행하게 놓이고 페이즈 3에는 짧아진 축 레인이 두 번째 막대까지 뻗는다. 1B에서는 얼음 파편 두 발이 나간다. 방은 차가운 회청색 강철 바닥에 분홍 비상등이 켜진 냉동고 무드라서 작전 6의 밝은 녹색 재배동과 뚜렷이 다르다. **이것은 그림 승인이 아니다.**
- **관찰(고치지 않음):** 보스 발밑 타원 그림자는 모든 보스가 같은 크기다(이전 기록 2절). 방 전체가 확 트여 엄폐가 없다(3절).
- `tools/art_pipeline/validate_visual_evidence_1080p.py --require-dynamic-capture`를 이 폴더의 이미지와 영상에 돌린 기록이 `visual_evidence_1080p.json`이다(PASS: 10개 파일). 이 검사는 컨테이너와 해상도만 확인하고 그림의 질을 판정하지 않는다. PNG와 영상은 git이 무시하고 작업 폴더에만 있다.

## 8. 게임 소리 영상

`tools/environment/record_stage_battle_with_audio.py`(`SABLE_CAPTURE_MISSIONS=7`, `SABLE_CAPTURE_BOSS=1`). 보스방에서 실제 입력 경로(WASD, 마우스 조준, 발사)로 10초를 진행한다.

- `video/stage7_combat_10s_sound_1080p.mp4`: 1920 × 1080, 60 fps, 600프레임, 10.0초. 소리는 Godot의 실제 믹스이고 스테레오 48 kHz 480,000 샘플이다(RMS 0.0667, 최대 0.500, 무음 아님). 본 적: CRYO, ENM_SITE7_BULWARK_01, ENM_SITE7_PRISM_01. 영상 sha256 `e6c840c6…ce33e`. 기록: `video/encode.json`, `video/capture.json`.
- 시계는 `--fixed-fps 60`이다. **성능 측정이 아니다.**
- 세 대원이 R05_VAULT에서 CRYO와 교전하고 서리 막대가 파도로 켜지고, 피격·총구 불꽃·스킬 효과가 나온다(중간 프레임을 눈으로 확인했다). 사람이 듣고 보고 판단할 몫이다.

## 9. 파일

| 파일 | 내용 |
|---|---|
| `README_KO.md` | 이 문서 |
| `regression_runs.json` | 인용한 실행의 요약(추적) |
| `boss_room_fairness_grid{100,50,25}.json` | R05_VAULT와 R05_ATRIUM 공정성 결과(추적) |
| `boss_room_fairness_axis_lane_sweep.json` | CRYO 축 레인 길이별 공정성(추적). 임시 환경 변수로 잰 것이라 그 코드는 커밋에 없다 |
| `full_operation_op07.json` | 작전 7 봇 풀플레이 보고서(추적) |
| `capture_report.json` | 캡처 보고서(추적). 작전 7 행만 남겼다(같은 실행이 찍은 작전 1–6 자기 방과 작전 8–10 시험대는 뺐다) |
| `visual_evidence_1080p.json` | 1080p 검증기 결과(추적) |
| `captures/`, `crop_sheets_1to1/`, `video/` | 이미지와 영상. `qa/**/*.png`와 영상은 git이 무시한다 |

## 10. 하지 못한 것, 사용자와 Codex 몫

1. **사람 플레이와 균형.** 봇 통과는 균형 승인이 아니다. CRYO의 체력 1,740, 공격 세기, 방의 난이도, 보상은 사람이 해 보고 정한다. 특히 3페이즈 축 레인을 줄였으므로(4절) 페이즈 3이 예전 설계보다 조금 너그럽다. 그 느낌이 맞는지는 사람이 판단한다.
2. **그림 승인.** 작전 7의 판 15장(Codex)과 CRYO의 겉모습은 이 기록이 승인하지 않는다.
3. **같은 세션 회전 A/B FPS.** `AGENTS.md`는 FPS를 같은 세션의 회전 A/B로만 비교하라고 한다. 작전을 골라 그렇게 재는 정식 도구가 없다. 그래서 작전 7은 재지 못했다(영상은 고정 시계라 성능 자료가 아니다). 사람이 F9(FPS 표시)로 작전 7을 플레이하며 보는 것이 가장 빠르다.
4. **엄폐 소품**(3절). 작전 7의 보스방 R05_VAULT에는 엄폐가 없다(작전 1–6의 방은 모두 하나 이상 있다). 더 원하면 Codex가 소품을 더한다. 더하면 `boss_room_fairness`를 다시 돌린다(방의 공정성 기하가 바뀐다).
5. **작전 8–10.** 판이 없어 그대로다. Codex가 작전 8의 판을 끝내면 같은 순서(6절 C)로 사용자의 지시에 따라 켠다. 그때 `tests/render/site7_boss_pattern_capture.gd`의 `TEST_BED`에서 GANTRY의 행을 빼고 `BOSS_IDS`에 넣으면(`FIRST_A_B_ROOM` 이상) 자기 방 캡처가 되고, `boss_room_fairness`가 자동으로 그 방을 잰다.
