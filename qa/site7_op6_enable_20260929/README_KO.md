# SITE-7 작전 6 VERDANT LOCK 켜기 (2026-09-29)

**판정: PASS_TECHNICAL_ONLY.** 코드와 자동 시험이 통과했다는 뜻이다. 그림, 균형, 플레이 승인이 아니다. 작전 6은 이제 **출격 가능**하다. 작전 7–10은 판이 없어 그대로 출격 불가다(`deployable: false`, `staging` 유지).

사용자 지시(2026-09-29): "작전 6 켜라". 근거는 `docs/production/SITE7_OPERATIONS_6_10_DESIGN_KO.md` 6절 C다. 앞선 기록 `qa/site7_ops_6_10_boss_integration_20260929/README_KO.md`의 11–12절이 "켜기만 남았다"고 적어 둔 일을 이 기록이 끝낸다.

## 1. 한눈에

| 항목 | 결과 |
|---|---|
| 작전 6 켜기(6절 C 1–3) | **됨.** `staging`, `deployable: false`, `pending`을 지웠고 작전 5의 COMMAND 디브리프가 Verdant Lock을 알린다 |
| 데이터 게이트(`campaign_data`, `campaign`, `demo_integration`) | PASS (272 / 158 / 26 검사) |
| 켜며 찾은 버그 | 갈래방을 id로만 읽어서 작전 6–10의 보급·신호 회수가 지급되지 않았다. **고침**(3절) |
| 작전 6 풀플레이(`full_op_06`) | PASS. 봇이 EXTRACTED까지 클리어했고 AERATOR가 세 페이즈에서 공격했다(5절) |
| 실제 보스방 바닥에서의 공정성(`boss_room_fairness`) | PASS. R05_ATRIUM 격자 25 px에서 공격 3,720개 중 0개 실패, 가장 가까운 안전 바닥 90 px(한도 180), 가장 빠듯한 탈출 여유 1.05 s(한도 0.25 s)(4절) |
| AERATOR 자기 방 캡처(1080p) | **됨.** 7장과 1:1 크롭 시트 2장(7절) |
| 게임 소리 영상 | **됨.** 10초 600프레임, 실제 게임 믹스(8절) |
| 같은 세션 회전 A/B FPS | **못 했다**(10절) |
| 사람 플레이, 균형, 그림 승인 | **못 했다.** 사용자 몫이다(10절) |

## 2. 커밋과 바뀐 것

| 커밋 | 내용 |
|---|---|
| `a6792b95` | 갈래방의 종류를 id가 아니라 `type`으로 읽는다(`StoryStage01.optional_kind_of`). 진행 스모크가 두 갈래방을 실제 상호작용으로 회수해 본다 |
| `90b5572b` | 작전 6 켜기. 5에 묶여 있던 시험(전투 캡처, 라이브 진입 스모크, 러너의 `full_op` 등록)을 6까지 넓혔고, 보스 패턴 캡처가 AERATOR를 자기 방에서 찍는다 |
| `6693f13c` | 방 바닥 공정성 시험 `boss_room_fairness`(quick 스위트) |
| `f167523a` | (Codex) 작전 7 판 통합. 코드 커밋과 문서 커밋 사이에 들어왔다. 작전 7은 여전히 출격 불가다(`deployable: false`) |
| `49d0f640` | 이 기록의 커밋: `AGENTS.md`(작전 6–10 절, 보스 절, "Operation 6 enabled"), 설계 문서, 보스 지시서, 이전 기록 머리말, 이 폴더 |

**켜는 순서(설계 문서 6절 C).**

| 순서 | 한 일 |
|---|---|
| 1 | `data/missions/MIS_CH01_06.json`에서 `staging` 블록을 지웠다 |
| 2 | `data/story/site7_campaign.json`의 작전 6 행에서 `"deployable": false`와 `"pending"`을 지웠다 |
| 3 | 작전 5의 COMMAND 디브리프를 `Offshore Null complete. The answer signal is tracing back into Site-7's sealed lower wings. Verdant Lock is now available.`로 바꿨다(데이터 게이트가 강제한다) |
| 4 | 게이트 `campaign_data`, `campaign`, `demo_integration` |
| 5 | 5에서 멈춘 곳: `tests/render/site7_battle_capture.gd`와 `tests/smoke/site7_live_entry_autostart_smoke.gd`의 `range(1, 6)`을 `range(1, 7)`로, 러너의 `full_op_%02d`를 6까지. `campaign_data`의 5개 한계 게이트(`stale_loop_gaps`)가 남은 표시를 찾아 준다 |

## 3. 켜며 나온 것

**3.1 갈래방 종류(버그, 고침).** 작전 1–5는 갈래방을 `O01_SUPPLY`, `O02_RESEARCH`로 부르지만 작전 6–10은 자리 이름(작전 6은 `O01_STORES`, `O02_NURSERY`)으로 부른다. `story_stage_01.gd`는 앞의 두 id만 알아봤다. 그래서 작전 6–10에서는 보급 상자와 신호 조각이 지급되지 않았고, 런 부스트(`data/progression/run_modifiers.json`이 `source_room`을 옛 id로 부른다)도 켜지지 않았고, 풀플레이 봇이 첫 갈래방으로 영영 걸어갔다. 작전 6이 열리기 전에는 아무도 이 길을 밟지 않아 드러나지 않았다.

- 첫 `full_op_06`은 608초를 쓰고 FAIL했다(`20260929_230910_custom`, 봇이 첫 갈래방으로 걸어가기만 했다). 원인을 찾아 갈래방의 `type`(`SUPPLY`, `RESEARCH`), 없으면 옛 id, 없으면 순서로 종류를 정한다(`optional_kind_of`). 진행 그림의 갈래 선도 실제 부모 방에서 그린다(`branch_parent`).
- 진행 스모크(`site7_campaign_progression_smoke.gd`)가 이제 출격 가능한 모든 작전에서 두 갈래방을 실제 상호작용(`_handle_interaction`)으로 회수해 본다. **음성 대조:** 옛 id 판독으로 되돌리면 작전 6에서 정확히 세 검사가 실패한다("Optional room O01_STORES recovers…", "O02_NURSERY…", "Supply cache and signal fragment both recovered…", `20260929_232751_custom`).
- 고친 뒤 `full_op_06`은 PASS했다(`20260929_232900_custom`, 187초).
- 다른 곳은 영향이 없다: 작전 2–10의 갈래방은 모두 `loot`를 직접 적었고(작전 1만 없다), 경제 스모크와 모의(`upgrade_economy_smoke.gd`, `upgrade_economy_sim.py`)는 `loot`를 먼저 읽으므로 옛 id 분기를 타지 않는다.

**3.2 엄폐 소품 하한.** 작전 6은 소품이 11개다(작전 1–5는 12–15개). 진행 스모크는 "12개 이상"을 요구해 처음에 FAIL했다(`20260929_225735_custom`, 128 검사). 하한을 **방마다 하나**로 바꿨다(`campaign_data`가 이미 요구하는 값). 그려 둔 소품이 모두 붙어야 한다는 검사는 그대로다. 작전 6에 엄폐를 더 두는 일은 Codex의 그림 작업이고 사용자가 원할 때만 한다.

## 4. 실제 보스방 바닥에서의 공정성

`tests/smoke/site7_boss_pattern_smoke.gd`는 새 보스의 공격을 800 × 800 px 열린 바닥에서 재고, `boss_duel`은 세 대원을 세워 두고 재지만 실제 방은 아니다. 새 시험 `tests/smoke/site7_boss_room_fairness_smoke.gd`(quick `boss_room_fairness`)가 출격 가능한 각 작전의 새 보스를 자기 방(`R05_ATRIUM`)에 세우고 여섯 공격을 모두 깐다.

- 대원이 설 수 있는 모든 자리(칠해진 바닥 위, 엄폐 밖, 보스에서 150–800 px)에서: 경고가 덮지 않는 1.5 대원 폭의 바닥이 180 px 안에 있고, 바닥 위를 엄폐를 피해 곧게 걸어 닿을 수 있고, 가장 느린 걸음(138 px/s)이 그 자리의 경고가 터지기 0.25 s 전에 닿는다. 방 전체를 덮는 경고는 안전 바닥이 없다고 나와야 한다(음성 대조).
- 한도는 낮추지 않았다.

| 격자 | 서 볼 자리 | 시험한 공격 | 실패 | 가장 가까운 안전 바닥(최악) | 가장 빠듯한 탈출 여유 | 엄폐 |
|---|---:|---:|---:|---:|---:|---:|
| 100 px | 38 | 228 | 0 | 90 px | 1.05 s | 2 |
| 50 px(러너 기본) | 154 | 924 | 0 | 90 px | 1.05 s | 2 |
| 25 px | 620 | 3,720 | 0 | 90 px | 1.05 s | 2 |

최악은 페이즈 2 공격 A에서 보스에서 700–775 px 떨어진 자리다(90 px를 0.65 s에 걸어 1.70 s 안에 나온다). 격자를 4배 촘촘하게(100 → 25 px) 해도 최악이 같으므로 표본 간격 탓이 아니다. 파일: `boss_room_fairness_grid100.json`, `..._grid50.json`, `..._grid25.json`. 작전 7–10이 열리면 이 시험이 그 보스도 자기 방에서 잰다.

## 5. 작전 6 풀플레이

`tests/smoke/site7_full_operation_smoke.gd --mission=MIS_CH01_06`(러너 `full_op_06`). 봇이 실제 액터 물리, 무기 쿨다운, 투사체 충돌, 임무 상호작용으로 진행한다(`debug_fire_once` 없음). 파일: `full_operation_op06.json`.

- 결과 `PASS_TECHNICAL_PLAYTHROUGH`: 결과 `EXTRACTED`, 전 경로 클리어, 적 23기 처치, 게임 시간 183.3 s(러너 시간 187.3 s), 보급 상자(`field_supplies`)와 증거(`GERMINATION LOG`) 회수.
- AERATOR가 페이즈 1에서 3번, 페이즈 2에서 2번, 페이즈 3에서 5번 공격했고(모두 10번), 대원에게 준 피해는 합해서 105.7이다. 스킬은 Q·E·X 실제 키 입력으로 썼다(Q 16, X 7, E 2).
- 봇의 통과는 균형 승인이 아니다. 통과는 두 번이다(`20260929_232900_custom`, Codex의 full 실행). 앞서 한 번 실패한 것은 3.1의 갈래방 버그 때문이고 봇이 보스에게 진 것이 아니다. `full_op_03`처럼 마지막 보스에서 봇이 가끔 지는지는 두 번으로는 알 수 없다.

## 6. 시험 결과

`regression_runs.json`이 아래 실행의 요약을 담고 있다(러너 폴더 `qa/regression_runs/`는 git이 무시한다). 시간 열은 한 시험만 돌린 실행이면 그 시험의 시간이고, 스위트면 실행 전체 시간이다.

| 실행 | 내용 | 결과 | 시간 |
|---|---|---|---:|
| `20260929_225735_custom` | `campaign_data`, `demo_integration`, `campaign`, 소품 하한 수정 전 | **FAIL** 128검사 | 14.4초 |
| `20260929_230910_custom` | `full_op_06`, 갈래방 수정 전 | **FAIL** | 608.4초 |
| `20260929_232615_custom` | `campaign`, 수정 후 | PASS 158검사 | 12.0초 |
| `20260929_232751_custom` | `campaign`, 옛 id 판독으로 일부러 되돌린 음성 대조 | **FAIL** 158검사 | 11.8초 |
| `20260929_232900_custom` | `full_op_06`, 수정 후 | PASS | 187.3초 |
| `20260929_233428_custom` | `boss_room_fairness` | PASS 5검사 | 5.6초 |
| `20260929_233400_full` | full 스위트(Codex가 시작), `full_op_01–06`, `boss_capture_geometry`, `traversal_audit` 포함 | PASS 65개 중 65개 PASS, `qa/` 가드 바뀜 0·사라짐 0·추가 0 | 2998초 |
| `20260930_002743_quick` | quick 스위트, `boss_room_fairness`, `boss_duel`, `boss_pattern` 포함. 커밋 전 작업 폴더(Codex의 작전 7 파일이 커밋 전인 채로 들어 있었다) | PASS 41개 중 41개 PASS, `qa/` 가드 바뀜 0·사라짐 0·추가 0 | 301초 |
| `20260930_003905_quick` | quick 스위트, **커밋 `49d0f640` 위**(`git_head` `49d0f640`, 더러운 경로 없음) | PASS 41개 중 41개 PASS, `qa/` 가드 바뀜 0·사라짐 0·추가 0 | 291초 |
| `20260930_004448_custom` | 같은 커밋 위에서 작전 6에 해당하는 시험 6개: `campaign`(158검사), `demo_integration`(26), `battle_geometry`(3,491), `world_route`(67), `boss_capture_geometry`, `full_op_06` | PASS 6개 중 6개 PASS, `qa/` 가드 바뀜 0·사라짐 0·추가 0 | 271초(실행 전체) |

- Codex가 시작한 full 실행(`20260929_233400_full`)은 시작 시점의 작업 폴더에 이 기록의 코드 변경이 커밋 전 상태로 이미 들어 있었다. 시작 뒤 내가 고친 것은 보스 패턴 캡처 스크립트의 변수 타입 지정 한 줄(파싱 오류)뿐이고, 그 시험(`boss_capture_geometry`)은 실행 끝에 돌아 수정 뒤의 파일을 읽었다. 러너는 시작할 때 시험 목록을 읽으므로 그 뒤에 등록한 `boss_room_fairness`는 이 full 실행에 없다. 그 시험은 아래 최종 quick 실행과 위 격자 실행(`20260929_233428_custom`)에서 돈다.
- Codex의 작업 폴더에는 작전 7 작업 중인 커밋 전 파일(`data/visual/*`, 작전 7로 넓힌 시험들, `stage07` 그림 등)이 있었고 이 기록의 어떤 커밋에도 들어 있지 않다. 그 변경이 위 앞쪽 실행 결과에 영향을 주었을 수 있다. 결과는 PASS다. 그 파일들은 뒤에 Codex가 `f167523a`로 커밋했고, 마지막 두 실행(`20260930_003905_quick`, `20260930_004448_custom`)은 그 커밋과 이 기록의 커밋(`49d0f640`)이 모두 들어 있는 깨끗한 작업 폴더에서 돌았다.
- tip에서 다시 돌리지 않은 것: `connector_alignment`(full 실행에서 737초)와 `traversal_audit`(607초). `f167523a`가 두 시험의 반복 범위를 넓혔고 마지막 full 실행(`20260929_233400_full`)은 그 커밋 전의 작업 폴더에서 돌았다. 마지막 두 실행은 작전 6에 해당하는 시험만 다시 돌린다.

## 7. 자기 방 캡처 (AERATOR, R05_ATRIUM)

창을 띄운 실제 렌더, 네이티브 1920 × 1080. `tests/render/site7_boss_pattern_capture.gd`가 이제 AERATOR를 미션 3의 시험대가 아니라 **작전 6의 자기 보스방**에 세운다(작전 7–10은 계속 시험대). 캡처는 통제된 페이즈 고정 장면(`controlled_phase_fixture`)이다: 페이즈와 공격 번호를 시험이 정해 넣었다.

| 파일 | 내용 |
|---|---|
| `captures/mission6_boss_room.png` | 보스방 전경: 보스, 체력바, 기둥 네 개, 대원 패널과 HUD(목표 "Silence the aerator tower", 선택 목표 Seed Stores와 Antenna Nursery) |
| `captures/mission6_phase{1,2,3}{a,b}_warning.png` × 6 | 페이즈·공격별로 바닥에 깔린 경고. 경고 수: 1A 4, 1B 4, 2A 6, 2B 0(포자 볼트 3발), 3A 7, 3B 7 |
| `crop_sheets_1to1/mission6_aerator_1to1_sheet_{a,b}.png` | 보스와 경고 부분을 보간 없이 오려 붙인 1:1 시트(원본 해상도) |

- 모든 장면에서 경고가 덮지 않는 안전 바닥이 이 방의 실제 바닥에 있다(`safe_floor_gap` 6/6). 경고 수는 일곱 개 한도 안이다.
- 눈으로 본 것: 보스가 방 가운데 서고 체력바가 위에 뜬다. 경고 원이 대상 둘레의 바닥에 깔리고 페이즈 3에는 "CORE SHIELDED" 막대가 뜬다. 방은 밝은 녹색 재배동 무드라서 작전 5의 보스방(어두운 회청색, 비)과 뚜렷이 다르다. **이것은 그림 승인이 아니다.**
- **관찰(고치지 않음):** 보스 발밑 타원 그림자는 모든 보스가 같은 크기다(이전 기록 2절). 방 전체가 확 트여 엄폐가 둘(발전기, 상자)뿐이다(3.2의 소품 수와 같은 이야기다).
- `tools/art_pipeline/validate_visual_evidence_1080p.py --require-dynamic-capture`를 이 폴더의 이미지와 영상에 돌린 기록이 `visual_evidence_1080p.json`이다(PASS: 10개 파일). 이 검사는 컨테이너와 해상도만 확인하고 그림의 질을 판정하지 않는다. PNG와 영상은 git이 무시하고 작업 폴더에만 있다.

## 8. 게임 소리 영상

`tools/environment/record_stage_battle_with_audio.py`(`SABLE_CAPTURE_MISSIONS=6`, `SABLE_CAPTURE_BOSS=1`). 보스방에서 실제 입력 경로(WASD, 마우스 조준, 발사)로 10초를 진행한다.

- `video/stage6_combat_10s_sound_1080p.mp4`: 1920 × 1080, 60 fps, 600프레임, 10.0초. 소리는 Godot의 실제 믹스이고 스테레오 48 kHz 480,000 샘플이다(RMS 0.0678, 최대 0.422, 무음 아님). 본 적: AERATOR, ENM_SITE7_DRONE_01, ENM_SITE7_PRISM_01. 영상 sha256 `630a24e3…2269`. 기록: `video/encode.json`, `video/capture.json`.
- 시계는 `--fixed-fps 60`이다. **성능 측정이 아니다.**
- 세 대원이 R05_ATRIUM에서 AERATOR와 교전하고 피격, 총구 불꽃, 스킬 효과가 나온다(중간 프레임을 눈으로 확인했다). 사람이 듣고 보고 판단할 몫이다.

## 9. 파일

| 파일 | 내용 |
|---|---|
| `README_KO.md` | 이 문서 |
| `regression_runs.json` | 인용한 실행의 요약(추적) |
| `boss_room_fairness_grid{100,50,25}.json` | R05_ATRIUM 공정성 결과(추적) |
| `full_operation_op06.json` | 작전 6 봇 풀플레이 보고서(추적) |
| `capture_report.json` | 캡처 보고서(추적). 작전 6 행만 남겼다(같은 실행이 찍은 작전 1–5 자기 방과 작전 7–10 시험대는 뺐다) |
| `visual_evidence_1080p.json` | 1080p 검증기 결과(추적) |
| `captures/`, `crop_sheets_1to1/`, `video/` | 이미지와 영상. `qa/**/*.png`와 영상은 git이 무시한다 |

## 10. 하지 못한 것, 사용자와 Codex 몫

1. **사람 플레이와 균형.** 봇 통과는 균형 승인이 아니다. AERATOR의 체력 1,560, 공격 세기, 방의 난이도, 보상은 사람이 해 보고 정한다.
2. **그림 승인.** 작전 6의 판 15장(Codex)과 AERATOR의 겉모습은 이 기록이 승인하지 않는다.
3. **같은 세션 회전 A/B FPS.** `AGENTS.md`는 FPS를 같은 세션의 회전 A/B로만 비교하라고 한다. 작전을 골라 그렇게 재는 정식 도구가 없다(이전 측정 `qa/vfx_perf_20260925/`은 작전 1 전투 미리보기를 임시 스크립트로 쟀다). 그래서 작전 6은 재지 못했다(영상은 고정 시계라 성능 자료가 아니다). 사람이 F9(FPS 표시)로 작전 6을 플레이하며 보는 것이 가장 빠르다.
4. **엄폐 소품**(3.2). 작전 6의 보스방은 엄폐가 둘이다. 더 원하면 Codex가 소품을 더한다.
5. **작전 7–10.** 판이 없어 그대로다. 작전 7은 Codex가 판을 하고 있다. 끝나면 같은 순서(6절 C)로 사용자의 지시에 따라 켠다. 그때 `site7_boss_pattern_capture.gd`의 `TEST_BED`에서 그 보스의 행을 빼고 `BOSS_IDS`에 넣으면(`FIRST_A_B_ROOM` 이상) 자기 방 캡처가 되고, `boss_room_fairness`가 자동으로 그 방을 잰다.
6. **Codex의 작업 폴더 변경**(작전 7 작업 중인 파일)은 손대지 않았고 커밋하지 않았다.
