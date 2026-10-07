# 작전 10 ZERO POINT — 단계 E S10_R05 HOLD

2026-10-01. **채택 4/15장, 누적 ImageGen 10회(이번 재개 7회)**. 사용자 결정으로 S10_R01 3차를 바이트 그대로 반입하고 R02·R03·R04를 제작·반입했다. S10_R05는 3회 모두 수치 규격을 못 맞춰 HOLD다. **R06부터는 미시작**이며 추가 호출 없이 멈춘다. 작전 10은 켜지 않았다.

## 판 상태와 호출 수

| 판 | 호출 / 상한 | 채택 차수 | 상태 · 거절 사유 |
|---|---:|---:|---|
| S10_R01 | 3 / 3 | 3 | 3차 사용자 채택. 1차는 과거 벽 판정, 2차는 크기 ±2px 밖. 기존 HOLD/거절 기록 유지. |
| S10_R02 | 2 / 3 | 2 | 2차 채택. 1차 에이프런 끝 여백 좌3.409% / 우3.469% (<4%). |
| S10_R03 | 1 / 3 | 1 | 1차 채택. |
| S10_R04 | 1 / 3 | 1 | 1차 채택. |
| S10_R05 | 3 / 3 | — | HOLD: 1·2차 주 바닥 오른쪽 <5%; 3차 전체 좌·우 <4% 및 보스 전체 높이 <612px. |
| S10_R06 | 0 / 3 | — | 미시작 |
| S10_O01 | 0 / 3 | — | 미시작 |
| S10_O02 | 0 / 3 | — | 미시작 |
| S10_C01 | 0 / 3 | — | 미시작 |
| S10_C02 | 0 / 3 | — | 미시작 |
| S10_C03 | 0 / 3 | — | 미시작 |
| S10_C04 | 0 / 3 | — | 미시작 |
| S10_C05 | 0 / 3 | — | 미시작 |
| S10_C06 | 0 / 3 | — | 미시작 |
| S10_C07 | 0 / 3 | — | 미시작 |

## 사용자 결정과 벽 내용 검사

S10_R01 3차 RAW/MASTER `b71b0135…`와 GAME `e567a57d…`, 계수0.7388을 그대로 반입했다. 추가 ImageGen 0회, 전체 3회로 마감했다. 격리 원본·REJECTION·측정·기존 HOLD를 덮어쓰지 않고 채택 사유를 뒤에 이어 적었다. [정식 반입 기록](../../stage10/S10_R01/adoption.json).

이번 사용자 기준: 중앙 코너·끝 기둥, 벽 베이, 문 틈·문 주변 기둥 등 지도 키트 공통 골조의 공유는 거절 사유가 아니다. **같은 자리 베이의 장비·패널 구성이 S3 또는 같은 작전 판과 같을 때만 거절**한다. 이후 프롬프트에 이 기준을 명시했다. S3 같은 슬롯과 1:1로 나란히 확인했다. R01은 긴 밀폐 해치, R02는 흰 커넥터면을 가진 릴레이 오벨리스크, R03은 기록 카트리지와 작은 읽기 콘솔, R04는 두 줄의 쌍갈래 널 방출기다. R05 후보는 뭉툭한 직사각 모놀리스와 붉은 이음선이며, 깨진 S3 앵커 설비나 보스의 뾰족한 결정 다발을 벽에 되풀이하지 않는다.

## 채택 판 수령 검사

실제 보이는 바닥과 문 에이프런을 수동 추적했다. 표준 다각형으로 바꾸거나 기울기를 고치려고 회전·전단·리사이즈하지 않았다. 주 바닥≥5%, 에이프런 끝 포함 전체≥4%, 크기 각 축±2px, 나머지 수치 기준을 유지했다.

| 판 | 네이티브 | 실제 축 | 휘도 | p10 / p90 | 채도 | 주 바닥 / 전체 여백 최소 | 문 | GAME 계수 |
|---|---|---:|---:|---|---:|---|---|---:|
| S10_R01 | 1672×941 | 24.024209° | 0.199663 | 0.167776 / 0.232098 | 0.047610 | 8.493% / 8.493% | NE | 0.7388 |
| S10_R02 | 1672×941 | 26.672901° | 0.200287 | 0.153667 / 0.250408 | 0.034372 | 13.278% / 8.134% | SW, NE, SE | 0.8279 |
| S10_R03 | 1672×941 | 25.152090° | 0.200067 | 0.156012 / 0.235337 | 0.056402 | 7.536% / 7.536% | SW, NE | 0.7712 |
| S10_R04 | 1774×887 | 22.831851° | 0.199978 | 0.169184 / 0.235126 | 0.056565 | 6.313% / 6.313% | SW, NE | 0.6446 |

모든 채택 방은 요청한 문만 열리고, 나머지 변은 닫혀 있다. 채택 에이프런 채도는 모두0.10 이하이고 중앙 바닥은 비었다. 문 폭과 문턱 좌표·각 에이프런 채도/휘도·실제 윤곽은 [selected.json](selected.json), 누적 후보의 측정은 [measurements.json](measurements.json)에 있다. 방 판이므로 통로 폭은 해당하지 않는다. C01–C07은 미시도다. 문 정렬/WASD와 이음매는 실제 통로가 없어서 미검증이며 수령 검사 통과가 연결 승인인 것은 아니다.

## S10_R05 HOLD 측정

| 차수 | 실제 축 | 휘도 / 채도 | 주 바닥 여백 최소 | 전체 좌 / 우 여백 | 전체 바닥 면적 | 에이프런 포함 전체 폭×높이 | 거절 사유 |
|---:|---:|---|---:|---|---:|---|---|
| 1 | 24.663517° | 0.200238 / 0.080627 | 4.784689% | 5.622010% / 4.784689% | 576,423.5px² | 1498×675px | 주 바닥 오른쪽 여백 <5% |
| 2 | 24.748862° | 0.200173 / 0.079197 | 4.724880% | 5.622010% / 4.724880% | 576,403.5px² | 1499×676px | 주 바닥 오른쪽 여백 <5% |
| 3 | 24.895838° | 0.200099 / 0.078365 | 6.758373% | 3.528708% / 3.947368% | 563,547.0px² | 1547×547px | 전체 좌·우 <4%, 높이547 <612px |

세 후보 모두 RGB1672×941, 축22.5–30.5°, 휘도0.17–0.24, 채도≤0.15와 에이프런 채도≤0.10을 통과했다. 1·2차는 오른쪽 주 바닥이 각각80px/79px밖에 떨어지지 않아5% 미만이다. 3차는 주 바닥 여백은6.758%로 통과하지만 전체 좌59px/우66px이고 높이547px로 규격을 못 맞췄다. 등록 윤곽을 줄여 숨기지 않았고 **세 후보 모두 런타임 바닥·판에 등록하지 않았다**.

보스방 면적과 크기는 **문 에이프런 포함 실제 그려진 바닥 전체** 기준이다. 주 바닥만의 면적·높이에는 별도 하한을 걸지 않았다. 세 후보 바닥 중앙은 열려 있고 엄폐물은0개다. 보스 원화 바이트를 바꾸지 않고 게임 축척으로 얹은 합성3장도 증거에 포함했다(texture display_height274px, visible mass261.8px, 예정 anchor[.69,.52]). 흰빛 결정 다발은 벽의 넓은 직사각 모놀리스와 분리되어 읽힌다. 이 합성은 **거절 후보의 실루엣 검토용이며 플레이 캡처가 아니다**. 실제 보스방·공정성·적 슬롯·boss_anchor 검증은 하지 않았다.

## 해시·노출·출처

RAW와 MASTER는 ImageGen 반환 바이트가 동일하다. GAME은 계수 하나를 전체 이미지의 모든 sRGB 채널에 같은 LUT로 적용했다. 다른 색 처리, 손칠, 부분 합성, 크롭·회전·전단·비균등 리사이즈는 없다. [source_integrity.json](source_integrity.json): 누적10회 RAW=MASTER SHA, GAME SHA, 단일 LUT 픽셀 재현, 참조 SHA와 관리형 스테이징 보존 **PASS**.

| 판 / 차수 | 상태 | RAW = MASTER SHA-256 | GAME SHA-256 | 전역 LUT |
|---|---|---|---|---:|
| S10_R01 / 1 | REJECTED | `ef3c182c060bf975fb5392a39415e6ee96919c46d0e95e179aaf6d6b9ed7bda0` | `396f012fc967dc02c0b92aafa48e8c46a2694a1657ad8a67d4ec99be3bb61ac5` | 0.8521 |
| S10_R01 / 2 | REJECTED | `23467911c66c9a486e000261d6ec1f72d599129c5d2493b0f6177d4828829df2` | `65aeb5b5065198a4d81d2fbe3e87c944fd01628cbe1f5e240139fd547472b8e7` | 0.7471 |
| S10_R01 / 3 | SELECTED_BY_USER | `b71b0135f06423c7da3202108e1ba442c6ce68c2526ee9ceb20277dda11f082d` | `e567a57d15a61df6f042a51c79ee4222f8bd807945bb2599e428b01e3d2569eb` | 0.7388 |
| S10_R02 / 1 | REJECTED | `1c52fdd2828df56ccadfa9cc33b04a818fbd40a79e884268a93ef47616623f72` | `d611c0c54439f08c28f60572d218476a4f0da58e4dc3028c7b6ff31ea81ccf6d` | 0.7329 |
| S10_R02 / 2 | SELECTED | `787f34dbbd408c6bb232f7241d89eded7f71028ef3b242fce6e222e9bc18c2da` | `ac97f989f9516bfea70b114f1c5e55980d106150f4d036b3ea0e49fa9ab1c00a` | 0.8279 |
| S10_R03 / 1 | SELECTED | `a3cf48345e106f571bf3f71fb77ef4ef742a7731603ca80e880930bf7d7722bf` | `49f00392c28aeaac3bd3f060f4725c2078025bd3fd6e32832632d32af0bec2a4` | 0.7712 |
| S10_R04 / 1 | SELECTED | `10dae607a9624cf28555af3e67e4be3b301d92d1a479d2aeafa23beeb67e31f7` | `7277efe6504c0392d7283cf665369c71280219cd96e3a686d0cf6994b96aade9` | 0.6446 |
| S10_R05 / 1 | REJECTED | `e234a466b69e0d852ff4d0fbb3fd84781ebdb10048f115dd283d51be650b8c0a` | `bde37b723cf57c6694b8baa715eb0f80e804ee8a84e4b1f79c0cb96e8015d74e` | 0.7095 |
| S10_R05 / 2 | REJECTED | `1001a4748d0cdcda126436e7561915e5fd7afbd445e1af4c4023507e127bc367` | `c597b6e4fb608d2ffd08d22b639f3edff4db76e30a00a6b4c77f94b69e37680a` | 0.7153 |
| S10_R05 / 3 | REJECTED | `6fd9b23af85998c3f083fdfeff1793d852359e9e11e2bed6c2bd5c40bfbf8c0a` | `49cd7a027eda96db253555775111379d11214e7b4f26444610f77c9ac4050b57` | 0.8125 |

[generation.json](generation.json)에 호출별 전체 프롬프트, 참조·참조 해시, 경로, 시도와 사유를 보존했다. R01 3차는 이전 거절→사용자 채택 이력까지 포함한다. [단계 E 매니페스트](../../SITE7_OP10_STAGE_E_MANIFEST.md)에 기록을 이어 적었다. 모든 작업 이미지와 관리형 스테이징, 실패 후보를 유지했다.

## 검토 증거와 검증

`validate_visual_evidence_1080p.py` **21/21 PASS**, [visual_evidence_1080p.json](visual_evidence_1080p.json). 네이티브1920×1080 이상 컨테이너와 디코딩을 확인한 결과이며 화질·그림·플레이·균형 승인이 아니다. S3 비교, 바닥 추적, 채택4장 시트는 원화1:1로 배치했고, HOLD 연락 시트의 썸네일은 목록용이다. 보스만 등록된 게임 축척으로 표시했다.

- [S10_R01_attempt03_floor_native_1920x1080.webp](evidence/S10_R01_attempt03_floor_native_1920x1080.webp)
- [S10_R01_attempt03_vs_S3_native_3840x1080.webp](evidence/S10_R01_attempt03_vs_S3_native_3840x1080.webp)
- [S10_R02_attempt01_floor_native_1920x1080.webp](evidence/S10_R02_attempt01_floor_native_1920x1080.webp)
- [S10_R02_attempt01_vs_S3_native_3840x1080.webp](evidence/S10_R02_attempt01_vs_S3_native_3840x1080.webp)
- [S10_R02_attempt02_floor_native_1920x1080.webp](evidence/S10_R02_attempt02_floor_native_1920x1080.webp)
- [S10_R02_attempt02_vs_S3_native_3840x1080.webp](evidence/S10_R02_attempt02_vs_S3_native_3840x1080.webp)
- [S10_R03_attempt01_floor_native_1920x1080.webp](evidence/S10_R03_attempt01_floor_native_1920x1080.webp)
- [S10_R03_attempt01_vs_S3_native_3840x1080.webp](evidence/S10_R03_attempt01_vs_S3_native_3840x1080.webp)
- [S10_R04_attempt01_floor_native_1920x1080.webp](evidence/S10_R04_attempt01_floor_native_1920x1080.webp)
- [S10_R04_attempt01_vs_S3_native_3840x1080.webp](evidence/S10_R04_attempt01_vs_S3_native_3840x1080.webp)
- [S10_R05_attempt01_floor_native_1920x1080.webp](evidence/S10_R05_attempt01_floor_native_1920x1080.webp)
- [S10_R05_attempt01_origin_silhouette_COMPOSITE_native_1920x1080.webp](evidence/S10_R05_attempt01_origin_silhouette_COMPOSITE_native_1920x1080.webp)
- [S10_R05_attempt01_vs_S3_native_3840x1080.webp](evidence/S10_R05_attempt01_vs_S3_native_3840x1080.webp)
- [S10_R05_attempt02_floor_native_1920x1080.webp](evidence/S10_R05_attempt02_floor_native_1920x1080.webp)
- [S10_R05_attempt02_origin_silhouette_COMPOSITE_native_1920x1080.webp](evidence/S10_R05_attempt02_origin_silhouette_COMPOSITE_native_1920x1080.webp)
- [S10_R05_attempt02_vs_S3_native_3840x1080.webp](evidence/S10_R05_attempt02_vs_S3_native_3840x1080.webp)
- [S10_R05_attempt03_floor_native_1920x1080.webp](evidence/S10_R05_attempt03_floor_native_1920x1080.webp)
- [S10_R05_attempt03_origin_silhouette_COMPOSITE_native_1920x1080.webp](evidence/S10_R05_attempt03_origin_silhouette_COMPOSITE_native_1920x1080.webp)
- [S10_R05_attempt03_vs_S3_native_3840x1080.webp](evidence/S10_R05_attempt03_vs_S3_native_3840x1080.webp)
- [S10_R05_HOLD_review_native_1920x1080.webp](evidence/S10_R05_HOLD_review_native_1920x1080.webp)
- [S10_selected_4_native_3840x2160.webp](evidence/S10_selected_4_native_3840x2160.webp)

## 미실행 항목과 QA 보호

| 검증 / 작업 | 결과 |
|---|---|
| 원화 바이트·실제 윤곽/휘도·채도·문·여백 수령 검사 | 채택4장, R05 HOLD / 상세 JSON |
| Godot GAME 4장 import/로드 | 4/4 PASS: 크기와 import 픽셀 동일. 전체 import에는 기존 WAV 오류가 있음 |
| 바닥·문 등록, 오르막 deck, 월드/전투/엄폐 moved=0 | 미실행: 15판 전 HOLD |
| layout/mood --check, null 심연·램프·허공 마스크 | 미실행 |
| strict15plates/14seams 및 이음매별 수치 | 미실행: 통로 없음 |
| 방별 connector_alignment --mission=10 | 미실행: 방·통로 쌍 및 작전10 연결 데이터 없음 |
| 시험 확장과 전용/quick/full 회귀 | 미실행; Codex 러너 실행 번호 없음 |
| 실제 게임1080p, 바닥·경로15장, 조감, 판 테두리6곳 | 미실행 |
| ORIGIN 실루엣 합성3장 | 완료, 거절 후보 위 검토 합성 / 실제 fairness 미검증 |

Claude의 full 러너 PID34104/34420이 보고 준비 때도 실행 중이었다([프로세스 확인](runner_processes_before_report.json)). Codex는 새 회귀 러너를 시작하지 않았고 `qa/`와 `motion_lab_v1/qa/`에 파일을 만들거나 고치지 않았다. 러너의 전체 QA 보호 결과는 이 작업에서 확정하지 않았다. 검토·기록은 `.cache/diag/site7_ops_e/hold_r05_20261001/`와 이 격리 폴더에 보존했다. 예정 `qa/site7_ops_6_10_plates_20260929/stage_e/` 반입은 **러너 종료 후로 보류**다.

## 변경 범위와 다음 조건

변경은 단계E 매니페스트, R01 채택 이력, 정식stage10 source/runtime4장, R02 1차 및 R05 세 후보 격리·측정·증거뿐이다. 작전9 판·연결 데이터, campaign deployable/pending와 미션staging, COMMAND 디브리프, full_op_10, 보스 코드·패턴·원화, 적 수·체력, 시험·감사 기준은 건드리지 않았다. 로컬 경로 지정 커밋만 했고 GitHub 작업은 없다.

**S10_R05는 3/3 상한으로 HOLD**다. 추가 ImageGen은 사용자 명시적 허용이 필요하다. 이후 R06→O01→O02→C01…C07과 제작 지시서7절1–12를 완료해야 한다. Claude는 켜기 전에 실제 R05_CORE의 boss_room_fairness, NE·SE 에이프런을 피한 보스/적 슬롯, 출구 접근성·WASD 양방향 교차, null의 게임1080p 가시성을 확인해야 한다. 이 보고는 그림·사람의 플레이·균형 승인이 아니다.


## 실행 명령과 관찰 결과

- `python .cache/diag/site7_ops_e/adopt_r01_and_prepare_r02.py`: R01 3차 RAW/MASTER/GAME 해시 일치 확인 후 정식 반입, 사용자 채택 이력 추가. 기존 격리 사본 유지.
- `python .cache/diag/site7_ops_e/inspect_candidate.py <ID> <관리형 반환 경로> --attempt N --floor <실제 윤곽> --doors <문 좌표> --aprons <실제 에이프런>`: R02 두 후보·R03·R04·R05 세 후보 즉시 검사. 각 입력과 결과는 후보별 `measurements.json`, `request.json`, 누적 `generation.json`에 있다.
- `python .cache/diag/site7_ops_e/report_r05_hold.py`: 누적 10회 바이트와 LUT, 참조 해시 재현 PASS; 원본 픽셀로 검토 증거 생성.
- `python tools/art_pipeline/validate_visual_evidence_1080p.py <현재 증거 21개> --output .cache/diag/site7_ops_e/hold_r05_20261001/visual_evidence_1080p.json`: 종료 0, 21/21 PASS(컨테이너·디코딩만).
- `Godot_v4.7.1-stable_win64_console.exe --headless --editor --path . --import --log-file .cache/diag/site7_ops_e/hold_r05_20261001/godot_import.log`: 종료 0. 새 GAME 4장 texture import 완료. 프로젝트의 기존 `fps_bgm_06_sniper_ridge.wav`가 WAV 대신 MP3 헤더라는 오류도 나왔으므로 **전체 프로젝트 import를 오류 없는 PASS로 세지 않는다**. 그 파일과 소리는 변경하지 않았다. [원문 로그](godot_import.log).
- `Godot_v4.7.1-stable_win64_console.exe --headless --path . -s res://.cache/diag/site7_ops_e/hold_r05_20261001/texture_intake_check.gd --log-file .cache/diag/site7_ops_e/hold_r05_20261001/texture_intake_check.log`: 종료 0, `S10_GAME_INTAKE_CHECK PASS 4 textures`. 각 `load()` 결과의 실제 크기와 import 픽셀이 GAME과 동일. [4장 결과](texture_intake_check.json), [로그](texture_intake_check.log), [검사 스크립트](texture_intake_check.gd). 원본 Image를 비교 목적으로 읽어서 생기는 export 경고 4개가 있으며 이 검사 자체는 프로젝트 로컬 intake 확인용이다. 실제 게임·export·연결 승인으로 세지 않는다.

일반 작업의 TEMP/TMP/Python/Godot 사용자 캐시는 저장소 `.cache/`로 지정했다. ImageGen의 관리형 반환 사본은 사용자 보존 지시대로 유지했다. QA, 플레이어 세이브·설정, 다른 작전 판은 쓰지 않았다.

## 커밋 직전 QA 보호 재확인

Claude의 앞 full 러너 대신 전용 러너 PID **21612/34604**, `--only traversal_audit,full_op_07,full_op_08`이 실행 중이었다([최종 프로세스 원문](runner_processes_before_commit.json)). QA 반입을 계속 보류했고 Codex 러너는 시작하지 않았다. 위34104/34420은 보고 준비 시의 과거 관찰이다.

`git diff --cached --check`는 Godot 원문 로그의 마지막 빈 줄 한 곳만 보고했다(`godot_import.log:53: new blank line at EOF`). 로그 원문을 보존해 그 결과를 PASS로 세지 않고 기록한다. 다른 소스·데이터의 공백 오류는 보고되지 않았다.
