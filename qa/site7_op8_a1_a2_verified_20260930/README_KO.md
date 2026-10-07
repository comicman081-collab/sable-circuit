# 작전 8 Stage C A1/A2 검증 (Claude, 2026-09-30)

작전 8은 **아직 켜지 않았다.** `deployable: false`와 `staging` 블록, 작전 7의 COMMAND 디브리프, `full_op_08` 등록은 그대로다. 사용자의 "작전 8 켜라"가 없었다.
이 문서는 Codex의 마무리 작업([`qa/site7_ops_6_10_plates_20260929/stage_c/finish_20260930/`](../site7_ops_6_10_plates_20260929/stage_c/finish_20260930/README_KO.md))인 A1(`S8_O02` GAME 노출)과 A2(새벽 배경 접촉 그림자)를 Claude가 독립으로 다시 잰 결과와, Claude가 더한 시험·러너 변경의 기록이다. 사람의 그림·플레이·균형·FPS 승인이 아니다.

## 1. A1 — `S8_O02` GAME 노출 재현

`o02_lut_check.txt` (원화 RAW를 직접 읽어 LUT `min(255, round(v × 계수))`를 다시 적용).

| 항목 | 결과 |
|---|---|
| RAW = MASTER | 둘 다 `95999fdb…7116aa`, 1672×941 RGB (바이트 불변) |
| 이전 GAME (`0d5f1e24…`, 격리 보관본) | RAW × LUT(0.5396)과 **바이트 일치** |
| 현재 GAME (`d5cda085…`) | RAW × LUT(0.5831)과 **바이트 일치** |
| 같은 바이트를 만드는 계수 | 0.5831, 0.5832, 0.5833 (반올림 구간이라 하나로 정해지지 않는다) |
| 바닥 밝기(감사 자체 값) | 0.1798 (이전 0.1664), 한도 0.17–0.24 |

색조·채도·부분 보정은 없다. 이전 GAME은 `art_src/environments/site7_v2/_quarantine/S8_O02/game_exposure_20260930_before/`에 그대로 있다.

## 2. 8개 작전 전체 strict 감사

`strict_audit_all_missions.log/.json` (`audit_site7_plate_lighting.py --strict`, 작전 1–8).

- 판 **120/120 PASS**. 이음매 112곳 = 109 PASS + 승인 예외 3곳(`S8_C01`/R01_GATE, `S8_C03`/R04_JUNCTION, `S8_C05`/R05_TERMINAL) + FAIL 0.
- 예외 세 곳은 게임이 싣는 이음매 보정을 적용한 뒤 채도비 1.41 / 1.28 / 1.27배, 밝기 차 +0.04 / −0.00 / −0.01스톱으로 원래 목표(1.5배, 0.35스톱) 안이다. 마지막 줄: `SITE7_PLATE_LIGHTING PASS (0 plates/seams off target, 3 seams waived)`.

## 3. HEAD 대비 데이터 변경 (`data_diff_vs_head.txt`)

- `site7_void_masks.json`, `site7_mood_lamps.json`: 바뀐 판 행은 `S8_O02` 하나뿐. 판 수 120 = 120.
- `site7_seam_light.json`: `MIS_CH01_08`의 통로 행 `C6`(= `S8_C07`) 하나뿐. 작전 1–7 행은 그대로.
- Codex의 `preservation.json`도 작전 1–7의 허공 마스크 105행과 램프 105행이 원래 행 그대로임을 적었다.

## 4. Claude가 더한 시험

### 4.1 접촉장 배선 가드 (`tests/smoke/site7_battle_geometry_smoke.gd`, +50 검사)

A2는 배경 쉐이더에 들어가는 데이터라서 헤드리스 Godot는 그림을 그리지 않는다. 그림의 모양을 보는 것은 Codex의 실제 GPU 캡처 6장이 맡고, 스모크는 **연결이 끊기지 않았는지**를 지킨다.

- 새벽 배경(강도 > 0)이면 접촉장이 판 15장 모두에 있고(`MAX_CONTACTS` 15 이하), 다른 스타일에는 없어야 한다. 아틀라스가 있고 크기가 메타와 같다. 거울 뒤집은 새벽 판은 거부한다(장이 뒤집히지 않는다).
- 판마다 불투명 픽셀 중 5 마스크 픽셀 옆에 투명(허공) 픽셀이 있는 가장자리 점을 골라(4점 이상), 쉐이더 자신의 사각형·UV 값으로 아틀라스를 읽는다. 모두 0.95 이상이어야 하고(`missed == 0`), 같은 읽기를 12 px 밀면 실패해야 한다(시험 안의 부정 대조).
- 시험 자체를 검증: 파일 변형 두 가지를 넣고 각각 시험이 실패함을 확인했다(`geometry_guard_mutations.txt`).
  - M1 접촉 사각형의 패딩 오프셋 제거 → `Contact field misses its plate's wall S8 (59 of 120 edge points)`, FAIL.
  - M2 접촉장이 배경에 전달되지 않음 → `Abyss contact atlas is missing S8` 등, FAIL.
  - 되돌린 뒤 파일 SHA-256이 백업과 같고(`0a71bd64…`) 기준선은 다시 **PASS (4038 검사)**. 가드 전은 3,988 검사였다.

### 4.2 접촉장 `--check` 비교기 (`same_contacts`)와 `mood_contact` 시험

`build_site7_mood_light.py --check`가 접촉장 PNG 문자열을 그대로 비교했다. 다른 zlib·numpy 빌드에서 같은 픽셀도 다른 바이트로 인코딩되면 이유 없이 실패한다(허공 마스크는 이미 `same_masks`로 디코드 비교한다). 이제 디코드한 픽셀을 픽셀당 1단계까지 허용해 비교한다.
- `tests/test_site7_mood_contact_compare.py`(quick `mood_contact`, 5시험, 파일을 쓰지 않는다): 같은 데이터 통과, 다른 PNG 인코딩 통과, 1단계 통과·2단계 실패, 판 누락·추가 실패, 패딩·스케일·크기·schema 변경 실패.
- 변형 3가지(정확 비교, 항상 참, 3단계 허용)는 모두 이 시험에서 잡힌다(`mood_contact_compare.txt`, 대조 10개 PASS).

### 4.3 러너 시간 예산

`connector_alignment`(작전 1–8 × 통로 7개 × 양방향의 실시간 물리)는 러너 한도 900초에서 작전 7을 돌던 중 TIMEOUT이 났다. 시험이 틀린 것이 아니라 한도가 모자랐다.

| 실행 | 결과 |
|---|---|
| Codex 16:17 러너 (`regression_initial_summary.json`) | TIMEOUT 900.3초, 작전 1–6 완료 (실패 0). PASS로 세지 않았다. |
| 18:28 Claude 직접 실행과 Codex 재시도 | 두 실행이 겹쳤고 18:43 재부팅으로 둘 다 요약 없이 끝났다. 어느 쪽도 PASS로 세지 않았다(Codex의 `incomplete_retry.json`). |
| Codex 최종 러너 `20260930_191825_custom` | **5/5 PASS**, 1,237초. `connector_alignment` **1,138.1초, 848 검사 PASS** |

한도를 1,800초로 올리고 `mood_contact`를 quick에 등록했다(`tools/maintenance/run_regression_suite.py`). 시험 스크립트·assertion·물리·작전 선택은 바꾸지 않았다.

## 5. 이번 수정 뒤의 실행

- Codex 최종 러너(작업 트리, 커밋 `2d7a51a9` + 변경 15개): `world_layout`, `mood_light`, `mood_contact`(5), `connector_alignment`(848), `battle_geometry`(4,038) **5/5 PASS**, QA 보호 변경·삭제·추가 0건 (`../site7_ops_6_10_plates_20260929/stage_c/finish_20260930/regression_summary.json`).
- Claude quick 스위트(44개, `python tools/maintenance/run_regression_suite.py`): **44/44 PASS**, 424초, 작업 트리(커밋 `2d7a51a9` + 변경 21개), QA 보호 변경·삭제·추가 0건(`quick_summary.json`, `quick_SUMMARY_KO.md`). 새 `mood_contact`(5), `mood_light`(120판·620풀·120허공 마스크·15접촉 거리장), `plate_axis`(2), `seam_waiver`(10), `boss_room_fairness`(9), `campaign_data`(279), `boss_duel`(1,124)을 포함한다. `connector_alignment`와 `battle_geometry`는 full 묶음이라 quick에 없고, 위 Codex 최종 러너와 4.1의 직접 실행이 재었다.

## 6. 하지 않은 것과 남은 일

- 작전 8 켜기와 그 목록(`staging`/`deployable`/`pending`, 작전 7 디브리프, 캠페인 반복문, `full_op_08`, GANTRY 캡처를 자기 방으로, 자기 방 캡처와 소리 클립, full 스위트)은 사용자의 명령 뒤에 한다.
- 사람이 봐야 할 것: 새벽 배경 테두리와 판의 그림(접촉 그림자가 실제 화면에서 자연스러운지), 작전 8 플레이·균형·FPS.
- 보스방 `R05_TERMINAL`에는 엄폐물이 없다. 더하려면 Codex의 그림 일이고 `boss_room_fairness`를 다시 돌려야 한다.
- 작전 6의 `S6_C07` 데크 띠가 등록된 걸을 수 있는 다각형 밖에 있어 보이는 곳(오버레이 증거만 있음)은 손대지 않았다. 사용자가 원하면 확인한다.

## 파일

| 파일 | 내용 |
|---|---|
| `strict_audit_all_missions.json/.log` | 작전 1–8 strict 감사 전체 |
| `o02_lut_check.txt` | `S8_O02` LUT 재현 |
| `data_diff_vs_head.txt` | HEAD 대비 데이터 행 변경 |
| `geometry_guard_mutations.txt` | 접촉장 가드의 변형 시험 |
| `mood_contact_compare.txt` | `same_contacts` 대조 10개, 단위시험, 변형 3개 |
| `quick_summary.json`, `quick_SUMMARY_KO.md` | Claude quick 스위트 요약 |
