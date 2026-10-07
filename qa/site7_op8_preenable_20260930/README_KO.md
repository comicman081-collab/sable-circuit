# 작전 8 SWITCHYARD 켜기 전 검증 (Claude, 2026-09-30)

작전 8은 **아직 켜지 않았다.** `deployable: false`와 `staging` 블록이 그대로다. 사용자의 켜라는 명령이 없었고, 설계 문서 6절 A-6의 조건(`audit_site7_plate_lighting.py --strict`가 15 plates, 14 seams 통과)이 채워지지 않았다.
**후속(같은 날):** 사용자가 이음매 세 곳을 예외로 받아들였고(7절 3번) 감사에 반영했다. 8개 작전 전체 감사(120개 판)의 남은 실패는 `S8_O02` 바닥 밝기 1건이고(`strict_audit_with_waivers.json`), 그 밖에 새벽 배경 테두리 결함이 있다. 둘 다 Codex 몫이다(8절).
이 문서는 Codex의 Stage C 기록(`qa/site7_ops_6_10_plates_20260929/stage_c/`)을 Claude가 독립으로 다시 잰 결과와, Claude 몫(보스 공정성, 완주 시험, 검증)의 결과다. 사람 플레이, 균형, 그림 승인은 아니다.

## 1. Codex 기록의 재현

기준 커밋 `a186e53d`(작업 트리 깨끗). `python tools/environment/audit_site7_plate_lighting.py --mission MIS_CH01_08 --strict`를 다시 돌렸고 Codex의 기록과 같은 4건이 실패한다(`strict_audit_reproduced.json`). 판 14/15, 이음매 11/14 통과.

| 대상 | 잰 값 | 한도 |
|---|---|---|
| 판 `S8_O02` 바닥 밝기 | 0.166 | 0.17–0.24 |
| 이음매 `S8_C01` ↔ R01_GATE 채도 | 0.07 대 0.15, 감사의 비 1.87배 | 1.5배 |
| 이음매 `S8_C03` ↔ R04_JUNCTION 채도 | 0.17 대 0.07, 감사의 비 2.03배 | 1.5배 |
| 이음매 `S8_C05` ↔ R05_TERMINAL 밝기 | −0.363 스톱 | 0.35 |
| 같은 이음매 채도 | 0.21 대 0.10, 감사의 비 1.81배 | 1.5배 |

정정: 처음 채팅 보고에 적은 2.11/2.32/1.97배는 두 채도를 그냥 나눈 값이다. 감사가 실제로 비교하는 비는 분자와 분모에 0.02를 더해 계산하므로 위의 1.87/2.03/1.81배다(`saturation_ratio`).

- 가지 통로 C06/C07의 바닥 축(30.9°, 31.4°)은 승인된 31.5° 규칙 안이다. 다른 판은 30.5°를 지킨다. 이 규칙을 지키는 `tests/test_site7_plate_lighting_axis.py`는 러너에 등록되어 있지 않아 `plate_axis`로 등록했다(quick, 2 체크, 1초).
- 정적 감사는 보정 전의 판을 잰다. 게임이 실제로 싣는 실행 시점 이음매 보정(`site7_seam_light.json`)을 셰이더와 같은 계산(`apply_light`)으로 적용한 뒤 다시 재면 세 이음매는 채도비 1.41배 / 1.28배 / 1.27배, 밝기 차 +0.04 / −0.00 / −0.01스톱이다. 표의 목표(1.5배, 0.35스톱) 안이다(`seam_residual_op8.json`은 작전 8의 모든 이음매를 `seam_residual.py`로 잰 값이고, 세 이음매는 `strict_audit_with_waivers.json`의 `with_seam_light`에도 있다). 채팅 보고의 "추정 1.06–1.21배"는 최댓값/최솟값으로 어림한 틀린 추정이었고, 이 값이 실측이다.
- O02는 판을 다시 그릴 필요가 없다. `GAME` 판은 `RAW`에 노출 계수 하나(`game_exposure_factor_srgb`, 지금 0.5396)를 곱한 것이다. 계수를 약 0.585로 다시 구하면 바닥 밝기가 약 0.18이 되어 한도 안이다(RAW 바이트 불변).

## 2. 보스 GANTRY를 R05_TERMINAL에 맞춤

`boss_room_fairness`는 출격 가능한 작전만 돈다. 작전 8용 사본으로 R05_TERMINAL 바닥에서 쟀다.

- 맞추기 전(50 px 격자): 1,410 공격 중 101개 실패. 별 모양(3페이즈)과 2페이즈 대각 레일에서 가장 가까운 빈 바닥이 180 px이고, 가장 느린 걸음(138 px/s)으로 1.30초가 걸리는데 예고가 1.4–1.5초여서 여유가 0.10–0.20초였다(한도 0.25초). `boss_room_fairness_op8_before_fit_grid50.json`.
- 맞춘 뒤: 2페이즈 대각 레일, 3페이즈 별, 별의 B 원이 `GANTRY_LATE_WINDUP`(1.6초)로 예고한다. 격자 100/50/25/20 px에서 실패 0(공격 348/1,410/5,652/8,784개), 가장 빠듯한 여유 0.30초. `boss_room_fairness_op8_after_fit_grid*.json`. 한도(180 px, 0.25초, 138 px/s)는 낮추지 않았다.
- `site7_boss_pattern_smoke.gd`가 1.6초와 바닥 1.56초를 고정한다(도보 180 px + 여유 0.25초 = 1.554초; 처음 잡은 1.55초는 이 계산에 걸려 1.56초로 올렸다). 부정 대조: 상수를 1.4초로 되돌리고 `boss_pattern`을 돌리면 `lane winds up 1.6 s, never under 1.56 s in GANTRY phase=2 serial=1` 등으로 실패한다(`boss_pattern_negative_control_1.4s.txt`). 되돌린 뒤 작업 트리는 깨끗하다.
- R05_TERMINAL에는 엄폐물이 없다(`cover_obstacles` 0). 작전 7 R05_VAULT와 같다. 더할지는 Codex의 그림 일이며 사용자가 원할 때만 한다.
- 커밋 `628aeae8`(내용은 커밋 전에 quick으로 잰 작업 트리와 같다). quick 41/41 PASS(`qa/regression_runs/20260930_151005_quick`, 356초). 커밋 뒤 `--only boss_capture_geometry,boss_lineup` PASS(`20260930_152338_custom`). 러너 실행 폴더는 git 밖이다.

## 3. 작전 8 봇 완주 (기술 시험)

`site7_full_operation_smoke.gd -- --mission=MIS_CH01_08`을 직접 돌렸다(`full_op_08_summary.json`). 작전 8은 아직 러너에 등록되지 않았다.

- `PASS_TECHNICAL_PLAYTHROUGH`, 실패 0. 결과 EXTRACTED, 193.5초, 적 24 격파(GANTRY 포함), 두 갈래방 회수(`field_supplies`), 연구 512, 부품 7, 조각 4, 정보 샘플 확보.
- 이 봇은 진짜 물리, 무기 쿨다운, 투사체, 상호작용으로 움직인다. 균형이나 사람 플레이 승인이 아니다.

## 4. 정렬 시험의 조향 변경 검토

Codex는 `site7_connector_alignment_smoke.gd`의 `_follow`에 "옆으로 벗어나면 통로 중심선으로 돌아온 뒤 140 px 앞을 본다"는 조향을 더해 통과시켰다. 이것이 시험을 느슨하게 만들었는지 확인했다.

- 문 너비는 그대로다. 문 오차 한도 0.5 px와 WASD 왕복 교차 검사는 바뀌지 않았다.
- 작전 8의 통로가 유난히 좁아서 봐준 것이 아니다. 8개 작전의 통로를 20 px 간격으로 잰 가장 좁은 걸을 수 있는 너비(세로 방향 폭)는 작전 1·2가 약 192–196 px, 작전 3·4·6·7과 작전 8의 데크가 88 px, 작전 5가 52 px이고, 작전 8의 문 어귀는 108 px로 작전 3–7의 어귀(52–88 px)보다 좁지 않다. 조향 변경은 시험 운전자를 고친 것이다.

## 5. 새벽(dawn) 배경의 회색 테두리 (결함)

`halo_S8_C05_native_1080p.png`(1920×1080 게임 캡처)와 `halo_compare_op7_op8.png`(위: 작전 7 방, 작전 8 방 / 아래: 같은 통로 C4의 작전 7, 작전 8).

- 작전 8의 밝은 구름 배경 위에서 벽 윗변 바깥에 거칠고 흐린 회색 테두리가 보인다. 통로 `S8_C05`가 가장 심하다. 어두운 배경의 작전 1–7에는 없다.
- 원인: 판의 바깥 허공은 "가장 큰 채널이 12 이하이고 가장자리에서 이어진 평평한 검정"만 투명 처리한다. 그 바로 안쪽의 어두운 경계 픽셀(13 이상)은 남고, 작전 8의 그림자 들어올리기(`shadows` 강도 0.65)와 대비가 이를 회색으로 끌어올린다. 배경이 어두우면 보이지 않고 밝으면 테두리로 읽힌다. 마스크 문턱만 키우면 벽 테두리까지 먹는다(테두리와 벽 가장자리의 밝기 분포가 겹친다).
- 고치는 방법은 그림 결정이 들어간다(7절).

## 6. 이 세션에서 하지 않은 것

- 작전 8 켜기, `staging`/`deployable` 변경, 앞 작전 디브리프 변경.
- 전체(full) 스위트: 이 변경은 보스 예고 시간뿐이라 quick과 보스 캡처 두 개(`boss_capture_geometry`, `boss_lineup`)만 돌렸다. 작전 8을 켤 때 full을 돈다.
- Codex의 판, 무드, 마스크, 감사 도구 수정.
- 작전 6의 `S6_C07` 데크 띠가 등록된 걸을 수 있는 다각형 밖에 있어 보이는 곳(오버레이 증거만 있음)은 손대지 않았다. 사용자가 원하면 확인한다.

## 7. 남은 일과 결정

1. `S8_O02`: 노출 계수 다시 구하기(기계적, 그림 생성 없음). 사용자 결정 불필요. **Codex 몫.**
2. 새벽 배경 테두리: 무드/마스크/배경 도구 수정. 그림 생성 없음. 방법 선택은 Codex가 하고 전후 캡처로 보인다. **Codex 몫.**
3. `S8_C01`/`S8_C03`/`S8_C05` 이음매: **사용자가 (나)를 골랐다**(2026-09-30, "나로 하자"; 그림을 다시 생성하지 않는다). Claude가 구현했다.
   - `audit_site7_plate_lighting.py`의 `SEAM_WAIVERS`: (작전, 판, 방)으로 이름 붙인 세 이음매만, 각자 측정값보다 조금 넓은 한도(채도비 `S8_C01` 1.95배, `S8_C03` 2.1배, `S8_C05` 1.9배와 밝기 0.40스톱). 색조는 예외가 없다.
   - 예외는 게임이 싣는 이음매 보정을 적용한 값이 표의 목표 안일 때만 유효하다(1절의 1.41/1.28/1.27배). 아니면 다시 실패한다.
   - `seam_waiver` 시험(quick, 10 체크): 예외 없이는 정확히 이 세 곳만 실패, 예외가 (작전, 판, 방) 열쇠와 자기 한도를 지킴, 보정이 없거나 아무것도 안 하면 실패, 색조는 예외 없음, 오래된 예외 검출. 변형 4가지(한도를 측정값 아래로 낮춤, 보정 뒤 검사 끔, 작전 열쇠 무시, 색조 검사 끔)를 넣어 각각 시험이 실패함을 확인했다.
   - `strict_audit_with_waivers.json`: 판 14/15, 이음매 14/14 통과(3개 예외 적용). 남은 실패는 `S8_O02` 바닥 밝기 1건(위 1번)이다.
4. 위가 끝나면 사용자가 "작전 8 켜라"고 해야 켠다(6절 C 순서). 켤 때 Claude가 할 일: `staging`/`deployable`/`pending` 삭제, 작전 7 COMMAND 디브리프를 `Cold Storage complete. Switchyard is now available.`로 교체, `campaign_data` 작전 반복문과 `full_op_08` 등록(`range(1, 9)`), 보스 캡처 GANTRY를 `R05_TERMINAL` 자기 방으로 옮기기, 라이브 진입 스모크 확대, `boss_room_fairness`가 출격 가능 목록으로 돌게 된 뒤 재실행, quick과 full 실행, AGENTS.md의 "Operation 8 enabled" 절과 `qa/site7_op8_enable_<날짜>/` 기록.

## 8. Codex 지시문 (지금 해도 된다. 이음매 예외는 Claude가 처리했으므로 A만 남았다)

```
[작전 8 Stage C 마무리 — Claude 검증 반영]
읽을 것: qa/site7_op8_preenable_20260930/README_KO.md (Claude가 a186e53d를 독립으로 재현한 결과).
하지 말 것: 작전 8 켜기. staging / "deployable": false / pending, 작전 7의 COMMAND 디브리프, 러너의 full_op_08 등록은 사용자가 "작전 8 켜라"고 한 뒤 Claude가 한다.
작업 트리는 나와 공유한다. 내 변경은 모두 커밋되어 있다(git log). 러너는 내가 돌리고 있지 않은지 확인하고 돌려라.
이음매 세 곳(S8_C01/C03/C05)의 채도와 밝기는 사용자가 예외로 받아들였고 내가 audit_site7_plate_lighting.py의 SEAM_WAIVERS로 넣었다. 그 판들을 다시 그리거나 감사 기준을 만지지 마라.

A. 그림 생성 없이 하는 일
A1. S8_O02 밝기. strict 감사에서 바닥 밝기 0.166(한도 0.17–0.24). intake_one.py의 노출 계수 0.5396이 원인이다. RAW/MASTER 바이트는 그대로 두고 같은 방식(전체 이미지에 노출 계수 하나, sRGB LUT)으로 계수만 다시 구해 GAME 판을 다시 쓴다. 바닥 밝기 약 0.18이 목표(계수 약 0.585). 다른 색 처리는 하지 않는다. 그 뒤 build_site7_mood_light.py와 build_site7_world_layout.py를 다시 돌리고, 두 --check, strict 감사, site7_battle_geometry_smoke.gd, site7_connector_alignment_smoke.gd가 PASS하는지 확인한다. 이전/새 GAME 해시와 계수를 기록에 남긴다.
A2. 새벽(dawn) 배경 테두리. 작전 8의 밝은 구름 배경 위에서 벽 윗변 바깥에 거친 회색 테두리가 보인다(qa/site7_op8_preenable_20260930/halo_S8_C05_native_1080p.png, halo_compare_op7_op8.png). 원인은 허공 마스크 문턱(최대 채널 12) 바로 위의 어두운 경계 픽셀이 작전 8의 shadows/contrast로 회색으로 올라가는 것이다. 고치고 같은 1080p 캡처(S8_C05를 포함한 6곳)로 전후를 보여라.
  조건: 작전 1–7의 site7_void_masks.json / site7_mood_lamps.json 행이 바이트 그대로일 것(작전 8 전용 설정으로만). mood_light --check PASS. 로봇, 작전자, 엘리트, 소품은 착색하지 않는다. 문턱만 키우면 벽 가장자리까지 먹으니 쓰지 않는다.
  후보: (1) 작전 8 abyss 행에 페더 폭을 두고 허공 가장자리 알파를 단계로 낮춘다. (2) 판 둘레의 구름을 어둡게 하는 접촉 그림자를 abyss 코드에 더한다. (3) 작전 8의 shadows/contrast를 조정한다. 하나를 골라 이유를 적어라.
```
