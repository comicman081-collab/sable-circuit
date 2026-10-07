# 확장 항목 1 — 구현 기록 / 기준선 경로 실패로 HOLD

작성: 2026-10-03. 범위: 1A BROODING·BEACON → 1B SPORE_CLOUD·FROST_PLATE·RAIL_LANE → 1C 권장 배치. 1D와 항목 2·3은 시작하지 않았다.

**상태: HOLD.** 기능·배치·시험 등록과 네이티브 캡처를 만들었으나, 변경 전 기준선의 3회차 `full_op_09`가 R04 전투 정리 후 이동하지 못하고 기술 상한에서 실패했다. 지시서 2절의 “변경 전에도 기존 시험이 실패한다” 중단 조건에 따라 후속 러너와 성능 측정을 시작하지 않았다. 기존 실패를 PASS로 바꾸거나 시험 상한을 늘리지 않았다. Claude의 검수는 아직 받지 않았다.

## 1. 로컬 커밋과 변경 파일

| 커밋 | 내용 |
|---|---|
| `602162a0` | 1A 두 정예 변종, 실제 액터 계약 시험, 처치 수 확장, 러너 등록 |
| `50a9dc9b` | 1B 장판 세 종류, 혼합 배치·속도 토큰·지속 피해, 시험·캡처·러너 등록 |
| `5cb3e012` | **1C 단독 커밋: 미션 JSON 06·07·08·09 네 파일만** |
| `36ccff9a` | 서리 실제 방 탈출 격자 추가, 네이티브 캡처의 대상 가림 개선 |

이 README·증거를 포함하는 마지막 로컬 커밋은 `git log --oneline -- qa/expansion_item1_20261003`으로 찾을 수 있다. GitHub push·PR·Pages·Actions는 하지 않았다.

변경 파일 그룹:

- 데이터: `data/progression/elite_affixes.json`, `zone_hazards.json`, 미션 06–09 JSON.
- 런타임: `scripts/combat/elite_affix.gd`, `zone_hazard.gd`, `scripts/actors/enemy_actor.gd`, `operator_actor.gd`, `scripts/missions/story_stage_01.gd`, `site7_battlefield.gd`.
- 시험: 기존 `elite_affix_smoke.gd`, `zone_hazard_smoke.gd`, `site7_full_operation_smoke.gd` 확대. 신규 `elite_expansion_smoke.gd`, `hazard_expansion_smoke.gd`, `test_expansion_item1_placement.py`, `tests/render/expansion_item1_capture.gd`.
- 러너: `tools/maintenance/run_regression_suite.py`에 새 시험 4개 등록.
- 기록: 이 QA 폴더. 작업·거절·최초 실패·변형 대조 사본은 `.cache/diag/expansion_item1_20261003/`에 보존했다.

`assets/`, `art_src/`, `motion_lab_v1/`, `data/visual/`, 작전 1–5·10 미션 변경 **0**. 승인 원화 도구: `python qa/site7_op10_art_approval_20261002/tools/verify_hashes.py` → **17/17 불변, exit 0**. 보스 코드·패턴·시험 한계, 경제 대역·LEGACY, 곱셈 클램프 변경 **0**. `records/scope_verification.json`의 정적 Git·해시 확인을 게임 실행 PASS로 대신하지 않는다.

## 2. 실행 명령과 관측 결과

새 시험의 권장 `--only` 목록은 `elite_expansion,variety_placement,hazard_expansion,variety_capture`다. 등록 77개: quick 46 / full 전용 31. 기존 73개 등록·상한은 그대로다. 쓰는 시험은 `--out`을 받고, 날짜 QA 폴더를 직접 겨냥하지 않는다.

| 실제 실행 | 결과 | 증거 |
|---|---|---|
| 변경 전 `python tools/maintenance/run_regression_suite.py` | **quick 44/44 PASS**, guard 변경·추가·삭제 0 | `qa/regression_runs/20261003_095928_quick`, `records/baseline_quick_summary.json` |
| 신규 elite 실제 액터 직접 진단 | **248 PASS** | `logs/elite_expansion.log` |
| 기존 elite 확대 직접 진단 | **71 PASS** | `logs/elite_affix.log` |
| `python -m unittest discover -s tests -p test_expansion_item1_placement.py -v` | **5 PASS** | 배치 전·후 stdout에서 5개 PASS 관측; 전용 unittest 로그는 별도 보관하지 않음 |
| 신규 hazard `godot --headless ... -s res://tests/smoke/hazard_expansion_smoke.gd -- --out=res://.cache/.../hazard_all_shapes_report.json` | **438 PASS / 15방** | `logs/hazard_expansion.log`, `records/hazard_expansion.json` |
| 기존 zone hazard 확대 직접 진단 | **366 PASS / 15방** | `logs/zone_hazard.log` |
| 신규 capture 직접 headless 진단 | **96 PASS** (이미지 증거 아님) | 캐시 `capture_headless.log` |
| 신규 capture 직접 native 실행 | **124 PASS / 14장 / 1920×1080** | `logs/capture_native.log`, `records/capture_report.json` |
| 네이티브 이미지 검증기 `--require-dynamic-capture` | **14장 PASS** (크기·디코드만) | `records/visual_validation.json` |
| 변경 후 등록된 `--only`, quick 46 전체 | **미실행: 기준선 경로 실패로 중단** | PASS로 세지 않음 |
| 변경 후 작전 6–10 각 3회 / 전체 full 77 | **미실행: 기준선 경로 실패로 중단** | Claude 독립 검수도 대기 |
| 같은 세션 회전 FPS A/B | **미실행: 기준선 경로 실패로 중단** | 캐시 프로브·래퍼 준비만 함; V-20 미확인 |

직접 Godot 진단도 기존 러너의 bounded `run_process`를 통해 실행해 exit·로그를 남겼다. 러너 안에서 돌아간 결과로 표시하지 않는다. 기준선 quick의 `world_layout --check`는 10작전, `mood_light --check`는 150판 PASS다. 파생 데이터 변경은 없지만 변경 후 두 `--check` 재실행은 **미실행**이다.

보스 기준선 검사 수: registry **163**, pattern **978**, duel **1124**, room fairness **21**, robot roster **302**; 모두 변경 전 quick PASS. 경제 **225 PASS**, machine_source **436 PASS**. 변경 후 전체 quick를 실행하지 못했으므로 C-11의 전후 동일 검사 수 PASS는 아직 확정하지 않았다.

### 실제 방 탈출 검사와 변형 대조

신규 시험은 기존 ARC도 포함해 실제 15방을 검사했다. 25px 격자의 피해 장판 **365** 지점은 138px/s + 0.25초 경고 여유를 통과했고, 무피해 서리 **24** 지점은 벽·엄폐를 피하는 경로가 존재했다. 서리에는 새 시간 상한을 만들지 않았다. 보고서의 timed/untimed 표와 blocked-negative를 분리했다. Claude의 별도 50·25px 독립 격자 검수는 아직 받지 않았다.

| 실제로 실행한 사본 변형 | 결과 |
|---|---|
| BEACON 감쇠 제거 | **FAIL exit 1**, 관련 검사 6개 실패 |
| BROODING `enemies_alive += 2` 누락 | **FAIL exit 1**, 관련 검사 7개 실패 |
| SPORE 지속 피해 함수 비활성 | **FAIL exit 1**, 정확한 DPS·출처 검사 5개 실패 |
| FROST 토큰 해제 함수 비활성 | **FAIL exit 1**, 독립 배율·실제 이동·방 정리 검사 6개 실패 |

`controls/`에 변형 설명·소스 SHA·실제 로그를 보존했다. 장판 대조는 380검사 단계에서 실행했고 그 뒤 실제 방 서리 격자를 438검사로 확대했다. 대조의 당시 소스와 최종 시험을 같은 바이트라고 주장하지 않는다. 최초 elite 246검사/1실패는 새끼 정리 확인 타이밍을 고친 뒤 248 PASS가 됐으며 최초 로그도 캐시에 보존했다.

## 3. 상수와 기존 검사 확대

상세 파일·이름·이전→이후·이유는 [CONSTANTS_KO.md](CONSTANTS_KO.md)에 전부 적었다. 주요 값:

| 대상 | 이전 → 이후 | 이유 |
|---|---|---|
| 변종 표 | 3 → 5 | BROODING·BEACON 추가; 기존 3종 보존 |
| BROODING | 없음 → 새끼2, authored HP 비율0.25, 부화0.6s, 세대1 | 계약 체력 배율1회, 부모 −1보다 새끼 +2 먼저 |
| BEACON | 없음 → 반경360px, 감쇠0.25(상한0.35), 표시선6 | 실제 보호는 7번째 이상도 적용; 최강 하나→장벽 |
| SPORE | 없음 → 반경70, 경고1.2s, 지속3s, DPS4/8 | 연산자/로봇 모두 실제 피해, 경고 중0 |
| FROST | 없음 → 반경70, 속도0.7, 피해0 | 독립 토큰·기존 이동/skill/dash 배율 보존·즉시 복원 |
| RAIL | 없음 → 반길이90, 반폭24, −26.565°, 경고1.4s, 피해14/24 | 실제 띠 모양; 배치 바운딩 반경93.145 |
| 새 장판 초기 대기 | 없음 → 2.4s | ≥2s 유지 |
| 포자 FLINCH 표시 | 없음 → 최소90ms | 지속 피해 매 tick의 중복 VFX만 제한; HP·출처·health_changed 유지 |
| 혼합 이격 | radius×2.6 → max(radiusA,radiusB)×2.6 | 큰 장판 기준을 적용; 기존 한계 유지 |
| 봇 기대 처치 | authored encounter+증원 → 그 합+BROOD 부모당2 | 새끼를 실제 처치하기 전에 성공하지 못하게 확대 |
| 시험 등록 | 73/44quick → 77/46quick | 새4개; 기존 등록 삭제0 |

공통 weathering·hit flash는 유지하고 **변종의 추가 착색만 금지**한다는 사용자 결정을 적용했다. 같은 로봇의 변종 전후 Sprite2D modulate·self_modulate·shader 경로·모든 파라미터를 비교한다. 원래 `machine_source`의 공통 material 검사는 그대로다.

## 4. 1C 데이터 변경

| 작전·방 | 이전 → 이후 |
|---|---|
| 6 R02_GALLERY | ARC2 → ARC1+SPORE1 |
| 6 R04_PUMPS | ARC2 → ARC1+SPORE1; initial MORTAR VOLATILE → BROODING |
| 7 R02_FREEZE / R04_COMPRESSORS | 각각 ARC2 → ARC1+FROST1; 변종 불변 |
| 8 R02_MARSHALLING / R04_JUNCTION | 각각 ARC2 → ARC1+RAIL1; 변종 불변 |
| 9 R04_GALLERY | initial NULL_PYLON SHIELDED → BEACON; 장판 불변 |
| 1–5 / 10 | 전체 미션 JSON 바이트 불변 |

hazards·affix 밖의 로봇 수·HP·오프셋·증원·보상·intel 변경0. 방별 장판 총수와 정예 행 수(1/1/2/3/3/4/4/4/4/5)는 동일하다. BROODING은 런타임 새끼 두 기의 정상 처치·intel 경로를 추가하므로 authored JSON 행 불변이 실제 처치 수 불변을 뜻하지는 않는다. 배치만 거절하면 `5cb3e012` 한 커밋을 revert하여 원래 배치를 복원할 수 있다. 되돌리기를 실행하지는 않았다.

## 5. 변경 전 봇 3회와 중단 증거

기준선은 시작 HEAD `7dfe367e`의 scripts/scenes/data/tests/project.godot를 변경 전에 복사한 `baseline_project`다. 런타임은 비교 기준 `dca7ef20`과 같고 이후 차이는 지시 문서다. `records/baseline_sources.json`의 **565개 SHA 모두 일치**. 러너가 부모 저장소 HEAD를 읽어 적은 메타데이터보다 이 스냅샷의 바이트가 기준선 실행 근거다. 공유 assets 등은 읽기 입력으로 사용했고 변경하지 않았다.

명령: `python tools/maintenance/run_regression_suite.py --project .cache/diag/expansion_item1_20261003/baseline_project --only full_op_06,full_op_07,full_op_08,full_op_09,full_op_10`을 3회 순차 실행했다. stamp: `20261003_100926_custom, 20261003_102455_custom, 20261003_103852_custom`. 중복 러너는 시작하지 않았고 QA guard 결과를 그대로 보존했다.

| 회차 | 작전 | 러너 결과 | 작전 결과 | 받은 피해 HP |
|---|---|---|---|---|
| 1 | MIS_CH01_06 | PASS | EXTRACTED | 544.600 |
| 1 | MIS_CH01_07 | PASS | EXTRACTED | 911.200 |
| 1 | MIS_CH01_08 | FAIL | WIPED | 346.000 |
| 1 | MIS_CH01_09 | PASS | EXTRACTED | 396.000 |
| 1 | MIS_CH01_10 | PASS | EXTRACTED | 745.900 |
| 2 | MIS_CH01_06 | PASS | EXTRACTED | 514.100 |
| 2 | MIS_CH01_07 | FAIL | WIPED | 591.700 |
| 2 | MIS_CH01_08 | FAIL | WIPED | 346.000 |
| 2 | MIS_CH01_09 | PASS | EXTRACTED | 316.600 |
| 2 | MIS_CH01_10 | PASS | EXTRACTED | 971.060 |
| 3 | MIS_CH01_06 | PASS | EXTRACTED | 487.500 |
| 3 | MIS_CH01_07 | PASS | EXTRACTED | 860.250 |
| 3 | MIS_CH01_08 | FAIL | WIPED | 394.300 |
| 3 | MIS_CH01_09 | FAIL | 결과 없음 | 109.000 |
| 3 | MIS_CH01_10 | PASS | EXTRACTED | 761.650 |

| 작전 | WIPED / 결과가 있는 회차 | 결과 없는 회차 | 피해 평균 | 최소–최대 |
|---|---|---|---|---|
| MIS_CH01_06 | 0/3 | 0 | 515.400 | 487.500–544.600 |
| MIS_CH01_07 | 1/3 | 0 | 787.717 | 591.700–911.200 |
| MIS_CH01_08 | 3/3 | 0 | 362.100 | 346.000–394.300 |
| MIS_CH01_09 | 0/2 | 1 (경로 실패) | 273.867 | 109.000–396.000 |
| MIS_CH01_10 | 0/3 | 0 | 826.203 | 745.900–971.060 |

피해는 `damage_by_source` 합이며 부활·보급 전 피해도 포함한다. 결과 없음인 회차는 WIPED로 추정하지 않는다. 기존 작전7·8·10의 전멸 변동은 수치로 보존했고, 이번 작전9의 **경로 미완료**는 별도로 중단 사유로 남겼다. 변경 후 15회가 없으므로 전후 WIPED·피해 차이는 **미확인**이다.

3회차 작전9: 정리된 R04의 위치 약 `(-6100.857,3838.127)`에서 이동하지 못했다. 코드는 아직 회수하지 않은 O01 `(-3964.3,4646.3)`을 먼저 목표로 삼지만 런타임 goal은 기존 trace에 없으므로 실제 목표는 추정이다. 적0, 체력44/120/73; 최종 실패는 `Route finishes within technical playthrough bound; Live combat and extraction succeed without cheats; All six rooms reached; not early extraction; Ledger acquired through interaction; Both optional rooms recovered; All authored waves and boss defeated through real damage`. 실제 상한36,000프레임을 변경하지 않았다. [BASELINE_STALL_KO.md](BASELINE_STALL_KO.md)에 최소 재현·바닥/엄폐 경계 수치·확정하지 못한 원인을 적었다. nav 또는 물리 접촉 원인을 확정하려면 이동벡터·경로·동료 좌표를 추가 관측해야 한다. 이 작업에서는 기존 경로 코드·판·바닥을 수정하지 않았다.

## 6. 캡처와 남은 검수

14장 파일·SHA·장면·준비 방법은 [CAPTURES_KO.md](CAPTURES_KO.md), 원본은 `captures/`, 측정값은 `records/capture_report.json`이다. 복사는 원본과 SHA가 같다. 검증기 PASS는 **컨테이너 크기·디코드만** 확인하며 시각 품질·플레이·균형을 승인하지 않는다.

알려진 시각 한계: BROOD 일반 드론 두 이미지 일부 겹침, SPORE 아래쪽 일부의 실제 소품 가림, 긴 fixture 하단 설명의 줄임표. 캡처는 NORMAL_ZOOM1.22의 제어된 런타임이며 사람 플레이가 아니다. 기존 M7_RASTER_QUARANTINED 진단도 해결했다고 주장하지 않는다.

남은 것: 기준선 작전9 경로 실패 처리, 변경 후 등록 시험·quick46·봇15회, 보스 전후 검사 수 비교, V-20의 같은 세션 FPS A/B, Claude의 독립 대조·탈출 격자·전체 full·화면 검수. FPS 준비 도구는 실행하지 않아 후퇴 없음이라고 주장하지 않는다. 사람 플레이 로그는 만들지 않았다. 다음 항목은 시작하지 않는다.

**이 기록은 그림·플레이·균형 승인이 아니다.**


## 7. 항목 1 검수 보완 — B-1 / B-2 / N-2 / N-3 (2026-10-03)

사용자 지시 범위인 제작 지시서 9.1·9.2·9.3·9.3b만 반영했다. 위의 최초 HOLD 기록은 그대로 보존한다. 이 보완의 기술 검증은 통과했고 **항목 1 최종 판정은 Claude의 재검수 대기**다.

### 7.1 변경 경로와 검사

| 기준 | 변경 | 확인 |
|---|---|---|
| B-1 | `tests/smoke/elite_expansion_smoke.gd`: 기존 Sprite2D 비교를 유지하고 각 스프라이트부터 EnemyActor 루트까지 모든 CanvasItem의 modulate·self_modulate·재질 클래스·셰이더 코드/파라미터 비교를 추가 | 기존 248 → 438검사; 공통 weathering·hit flash 유지; 조상 틴트 복원 대조 포함 |
| B-2 | `tests/test_expansion_item1_placement.py`: 배치·보호 경로 검사를 고정 쌍 `5cb3e012^ → 5cb3e012`로 옮김 | 변경 경로는 미션 06–09 JSON 넷뿐; 1–5·10 바이트, hazards/affix 외 값, 정예 수, 장판 수·새 종류 위치/개수 검사; 현재 트리는 보스 금지·표의 ID·count≥1만 검사 |
| N-2 | `tests/render/expansion_item1_capture.gd.uid`, `tests/smoke/elite_expansion_smoke.gd.uid`, `tests/smoke/hazard_expansion_smoke.gd.uid`를 원래 바이트로 추적 | UID `c42tjpi23lhym`, `dsrw4hu3bjjge`, `fw2548aprpqb`; 변경 전후 SHA 동일 |
| N-3 | 러너의 `hazard_expansion` 등록 한 줄에 `quick=True` 추가 | solo·600초·출력 경로 유지; quick 46 → 47, full 전용 31 → 30, 전체 77 유지 |

게임 코드·데이터·assets·art_src·motion_lab_v1 변경은 0이다. 보스 공정성·경제·게임 상수는 바꾸지 않았다. 시험 기준과 기존 대조군을 줄이지 않았다.

### 7.2 실행한 러너

각 실행 직전에 `Get-CimInstance Win32_Process`로 Python `run_regression_suite.py` 프로세스가 없음을 확인했다. 실행은 순차로 끝냈고, QA 갱신은 두 러너가 종료한 뒤에 했다.

| 명령 | 결과 | 검사·시간 | 요약 |
|---|---|---|---|
| `python tools/maintenance/run_regression_suite.py --only elite_expansion,variety_placement` | **2/2 PASS**, exit 0 | elite 438검사 / 9.5초; placement 10시험 / 3.2초 | `qa/regression_runs/20261003_142934_custom/SUMMARY_KO.md` |
| `python tools/maintenance/run_regression_suite.py --only hazard_expansion` | **1/1 PASS**, exit 0 | 438검사·15방 / **27.8초** (1분 미만) | `qa/regression_runs/20261003_143221_custom/SUMMARY_KO.md` |

두 실행 모두 기존 `qa/`·`motion_lab_v1/qa/` 보호 결과 **변경·삭제·추가 0건**이다. 전체 quick·full·봇·새 캡처는 이번 좁은 보완 범위에서 다시 실행하지 않았다. 등록 한 줄 변경은 전체 실행을 통과했다는 뜻이 아니다.

### 7.3 실제 사본 변형과 합성 대조군

작업·변형 사본은 `.cache/diag/expansion_item1_review_fixes_20261003/controls/<이름>/`에 보존했다. 각 `control.json`에 명령·변형·SHA·시간·종료값, `stdout.log`에 실제 출력이 있다. 원본 게임 코드와 미션 JSON은 수정하지 않았다. Godot 사본은 리소스를 읽기 입력으로 공유하며 import/editor를 실행하지 않았다.

BEACON 사본은 `scripts/combat/elite_affix.gd`의 `_ready()`에서 `elite_beacons` 그룹 등록 직후, BEACON에만 다음 문장을 추가했다. 색은 모두 `Color(0.7, 1.0, 0.7)`이다. 각 사본에서 `Godot --headless --path <사본> --log-file <사본>/godot.log -s res://tests/smoke/elite_expansion_smoke.gd`를 실행했다.

| 사본 | 실제 변형 | 실제 결과 |
|---|---|---|
| `root_modulate` | `(get_parent() as CanvasItem).modulate = Color(0.7, 1.0, 0.7)` | **의도한 FAIL**, 438검사·36실패, exit 1; 조상 비교 36개가 거절 |
| `root_self_modulate` | `(get_parent() as CanvasItem).self_modulate = Color(0.7, 1.0, 0.7)` | **의도한 FAIL**, 438검사·36실패, exit 1; 조상 비교 36개가 거절 |
| `visual_root_modulate` | `(get_parent().get_node("HighResVisualRoot") as CanvasItem).modulate = Color(0.7, 1.0, 0.7)` | **의도한 FAIL**, 438검사·34실패, exit 1; 조상 비교 34개가 거절 |
| `legitimate_future_edits` | 사본의 작전 3 `ENM_SITE7_BULWARK_01` 정예 HP 272 → 273와 `assets/future_edit_control.txt` 추가 | **10시험 PASS**, exit 0; 정당한 후속 변경을 고정 배치 검사와 혼동하지 않음 |
| `missing_history` | 사본 시험의 고정 커밋 ID만 존재하지 않는 `0000000000000000000000000000000000000000`으로 교체 | 현재 **4시험 PASS**, 역사 비교 클래스만 **SKIP 1**; unavailable 이유 출력, exit 0 |

세 착색 사본 모두 `SCRIPT ERROR` 없이 의미 검사에서 실패했다. 정상 트리의 438검사는 스프라이트 로컬 검사를 유지하고, 루트·중간 노드 변형은 로컬 값이 그대로여도 조상 비교가 거절하며 복원 후 같아지는 것까지 확인한다.

B-2의 기존 합성 대조군은 모두 유지했다: 체력·offset_x·offset_y·로봇 수·보상 변경, 장판 수 증가, 다른 작전의 장판, 보스 affix. 새 합성 대조군은 고정 쌍의 변경 파일 목록에 `assets/`, `art_src/`, `motion_lab_v1/`, `data/visual/` 경로를 각각 추가하거나 미션 03을 추가하거나 필수 미션 하나를 빼면 거절하는지 검사한다. 현재 트리 대조군은 보스 장판·보스 affix·미등록 장판/affix ID·count=0을 각각 거절한다. 이들은 합성 입력의 오류 반환을 assert하는 검사이며 실제 저장소 데이터를 변조하지 않았다.

### 7.4 남은 검수와 범위

Claude가 이 보완 커밋을 다시 깨 보는 검수를 마쳐야 B-1·B-2 및 항목 1의 최종 PASS가 된다. 9.5 N-1의 기존 길찾기 막다른 구역은 이번에 수정하거나 다시 측정하지 않았다. 항목 1D·2·3은 시작하지 않았다. 이 기록은 그림·플레이·균형 승인이 아니다.
