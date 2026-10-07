# 작전 9 MEMORY VAULT — 단계 D 재개 / S9_C06 HOLD

2026-10-01. **사용자 결정대로 S9_C04 1차를 바이트 그대로 채택하고 C05를 2차에 반입했다. S9_C06은 3차까지 실제 축 상한31.5°를 충족하지 못해 HOLD로 멈췄다.** 채택 **13/15장**, 누적 ImageGen **30회**, 현재 거절 후보 **17장**, C07 **미시도**. 이번 재개 호출 **5회(C05 2회+C06 3회)**, C04 추가 호출 **0회**.

이전 R02/R05/C04 HOLD 본문·격리 원본·REJECTION·측정은 그대로 보존한다. 이번 채택/측정은 새 하위 폴더에 쓰고 상위 README와 매니페스트 뒤에 이어서 기록한다.

## 판 15장별 시도·결정

| 판 | 누적 시도 | 채택 차수 | 결과와 거절 사유 |
|---|---:|---:|---|
| S9_R01 | 1 | 1 | 1차 채택(이전 기록 유지) |
| S9_R02 | 3 | 3 | 3차 사용자 채택. 1차 여분 SE 문·전체 여백3.89%, 2차 전체3.23% 거절 |
| S9_R03 | 3 | 3 | 3차 채택. 1차 S3 모니터 배치 반복, 2차1602×982 거절 |
| S9_R04 | 3 | 3 | 3차 채택. 1·2차 전체 여백3.23/3.47% 거절 |
| S9_R05 | 3 | 3 | 3차 사용자 채택; 1·2차 계속 거절(기존 기록 유지) |
| S9_R06 | 1 | 1 | 1차 채택 |
| S9_O01 | 2 | 2 | 2차 채택. 1차 S3 벽 베이·기둥 간격·기계 배치 반복 |
| S9_O02 | 2 | 2 | 2차 채택. 1차1671×941 거절; 크기 보정 없음 |
| S9_C01 | 1 | 1 | 1차 채택 |
| S9_C02 | 1 | 1 | 1차 채택 |
| S9_C03 | 2 | 2 | 2차 채택. 1차 S3 경사 지지대·원통·벤트 베이 반복 |
| S9_C04 | 3 | 1 | 1차 사용자 채택(폭220px 기준). 2차 왼쪽 채도0.120, 3차0.158/금빛 번짐 계속 거절; 총3회 마감 |
| S9_C05 | 2 | 2 | 2차 채택. 1차1773×887 규격 불일치; 리사이즈 없음 |
| S9_C06 | 3 | — | HOLD: 1차 축32.079°/오른쪽폭380; 2차33.389°/385 및 S3 그릴·원통 베이 반복; 3차32.259°(폭323/370 통과) |
| S9_C07 | 0 | — | 미시도: C06 HOLD에서 중단 |

## C04 사용자 채택 결정

통로 세로 단면 수령 기준은 **≥220px**(벽 밑변→바깥 턱), 프롬프트는 **≥260px**로 유지한다. C06/C07의 끝 폭 표준±15%, 축≤31.5°, 에이프런 채도≤0.10, 금빛 바닥 웅덩이 금지 등은 그대로다. 문서 문구는 Claude가 수정하므로 제작 지시서 자체는 편집하지 않았다.

C04 1차: 실제 다각형 `[[0,754],[1774,8],[1774,252],[335,887],[0,887]]`, 축 **23.258826°**, 휘도 **0.199966**, 폭 **258/251/244px**, 바닥 비율 **28.0109%**, 끝10% 채도 **0.091095/0.012868**(왼쪽/오른쪽). 기존 GAME 노출 계수 **0.7208** 그대로이며 RAW/MASTER/GAME은 격리 사본과 바이트·SHA 동일하다. [S9_C04_adoption.json](S9_C04_adoption.json)에 격리 파일의 변하지 않은 해시와 채택 사유를 기록했다. 2·3차 거절은 유지하고 총3회로 마감했다.

## 이번 후보 실제 바닥 검사

원본 축척에서 실제 벽 밑변과 그려진 바깥 턱을 추적하고 기존 `floor_axis()`/`plate_floor()`로 측정했다. 표준 윤곽으로 실제 윤곽을 대체하지 않았다. 끝 채도는 실제 바닥의 이미지 끝10% 밴드에서 잰다. 방과의20% 밴드 밝기 비교는 **사전 비교이며 solved-world strict seam PASS를 대신하지 않는다**.

| 판/차수 | 축 ° | 휘도 | 채도 | 바닥 비율 % | 실제 세로 폭 px | 계수 | 결과 |
|---|---:|---:|---:|---:|---|---:|---|
| S9_C05/1 | 25.680097 | 0.224919 | 0.041844 | 30.400 | [296, 289, 236] | 0.8934 | REJECTED: Native 1773x887 instead of required 1774x887 (1px short); no resize/crop. Axis, >=220px widths, actual-end saturation and preliminary R06/R05 apron comparisons passed. |
| S9_C05/2 | 25.531088 | 0.225009 | 0.053268 | 29.813 | [290, 273, 242] | 0.9274 | SELECTED: 검사 통과 |
| S9_C06/1 | 32.079250 | 0.199875 | 0.049960 | 29.027 | [348, 380] | 0.6987 | REJECTED: Actual floor_axis 32.079250 deg exceeds31.5; right width380 exceeds374.9 (+/-15% standard). Real traced outline [[0,65],[1254,835],[1254,1215],[0,413]] retained. Colour, native size, no end doors and preliminary apron tests pass. |
| S9_C06/2 | 33.388512 | 0.199994 | 0.056590 | 28.030 | [318, 385] | 0.7917 | REJECTED: Actual axis exceeds31.5deg and right width385 exceeds374.9px. Central grille/cylinder bay masses repeat S3 reference; not acceptable wall novelty. Actual trace retained; no transform. |
| S9_C06/3 | 32.259310 | 0.200059 | 0.060056 | 27.632 | [323, 370] | 0.7574 | REJECTED: Actual floor_axis exceeds31.5deg; right lip1202 instead of standard1081. Width323/370px is inside standard +/-15%, but passing width does not waive actual axis. HOLD after3 ImageGen calls; no extra call or transform. |

### C05와 R06 NE 에이프런 밝기

채택 C05 2차는 바닥 휘도 **0.225009**를 목표로 RAW에서 전역 단일 sRGB LUT **0.9274**를 적용했다. 국소 보정·채도·색조 처리는 없다. 왼쪽(R06 쪽) 실제 끝20% 바닥 휘도 **0.244249**와 R06 NE 에이프런 **0.268305**의 차이는 **+0.024056**, **+0.125697stops**다. 오른쪽(R05 쪽) 휘도0.230098과 R05 SW0.222512의 차이는 **−0.044435stops**. 두 사전 비교는 PASS다. [accepted_connector_end_check.json](accepted_connector_end_check.json)에 끝10% 채도와 세부 수치를 남겼다. 최종14이음부 감사는 아직 하지 않았다.

### 현재 HOLD — S9_C06

| 차수 | 실제 윤곽 px | 축 ° | 왼쪽/오른쪽 폭 px | 실패 |
|---|---|---:|---|---|
| 1 | `[[0, 65], [1254, 835], [1254, 1215], [0, 413]]` | 32.079250 | [348, 380] | Actual floor_axis 32.079250 deg exceeds31.5; right width380 exceeds374.9 (+/-15% standard). Real traced outline [[0,65],[1254,835],[1254,1215],[0,413]] retained. Colour, native size, no end doors and preliminary apron tests pass. |
| 2 | `[[0, 64], [1254, 857], [1254, 1242], [0, 382]]` | 33.388512 | [318, 385] | Actual axis exceeds31.5deg and right width385 exceeds374.9px. Central grille/cylinder bay masses repeat S3 reference; not acceptable wall novelty. Actual trace retained; no transform. |
| 3 | `[[0, 64], [1254, 832], [1254, 1202], [0, 387]]` | 32.259310 | [323, 370] | Actual floor_axis exceeds31.5deg; right lip1202 instead of standard1081. Width323/370px is inside standard +/-15%, but passing width does not waive actual axis. HOLD after3 ImageGen calls; no extra call or transform. |

3차는 폭 **323/370px**가 표준±15% 안이지만 축 **32.259310° >31.5°**다. 평균 바닥 색/분위수와 접속 끝 채도, 양쪽 필수 강조색, 열린 끝은 통과했다. 오른쪽 아래 실제 턱은y=1202로 표준y=1081보다121px 낮다. 폭 통과가 축 실패를 면제하지 않는다. 모든 호출에 표준 네 좌표를 프롬프트 맨 앞에 쓰고 표준(노랑)·실제(초록) 비교를 남겼다. 3회 상한으로 추가 생성·C07·연결을 중단했다. 기울기 변형, 손칠, 부분 합성, 로컬 모델, 바닥 윤곽 대체나 이음매 예외를 사용하지 않았다.

## 채택13장 검사와 해시

| 판 | 실제 축 ° | 휘도 | 채도 | 문 | RAW/MASTER SHA-256 | GAME SHA-256 | 계수 |
|---|---:|---:|---:|---|---|---|---:|
| S9_R01 | 25.085754 | 0.199996 | 0.042666 | SW | `730a850b2b5eeab8394a7974383ecede5ba4e0fd74419b38f73384a59928c71c` | `1320d7a71a6ab9e35e413ab642cb90bf159db80c4401e401e77f61798f6b3d59` | 0.7329 |
| S9_R02 | 23.898372 | 0.200089 | 0.042802 | NE, SW | `43aab4e4ab15e9b716ce65240ddcdc58d9ef21cf1c18b69b19fcb31a57015c89` | `92eb87d83a7cda89813393a91736d934afd2595f6078c8e8b27a4fae40cb5876` | 0.7500 |
| S9_R03 | 25.110692 | 0.200130 | 0.084738 | NE, SW, SE | `dde725716f925c7170b81a0be5dd2f83d8991972189612b43f7f586ac31ea7d6` | `6d68fd48db6222690848170a4534a8d8ae42f539f83f7b058538096d7f3c89ce` | 0.6910 |
| S9_R04 | 25.050312 | 0.200169 | 0.000820 | NE, SW, SE | `0c34ec924baae774a145d62166e2f3f410ed2cc5832f47442d004136c80f5ed1` | `c0c1d9039b332e25791c65846bd998fd22f6fa10488807b964c2363d95ca39f7` | 0.8146 |
| S9_R05 | 25.751452 | 0.200030 | 0.074953 | NE, SW | `2c3d33e0be172d4d66af425fd70972c347f99901f3a4bff12e635975b774260a` | `293e3b51ba0eff3e4f05f59c577cdd547522a8fe1cf526bf6e2845bb1a250e68` | 0.7750 |
| S9_R06 | 24.691252 | 0.200071 | 0.058634 | NE | `a8ec9f6afc4fc89d705b129ee26470c89bfef0fcb5c40f2daee67552373a07a7` | `a933ef9a8cfcc6dfc68fc12cd90c60f10285b9bcee0b583bec0defd176b4d42d` | 0.8433 |
| S9_O01 | 26.856216 | 0.199859 | 0.058542 | NW | `22c1b1d6a693ac9176bbed5ea9ff2a44c29e4e5d39d7fa48f5d1a4591e48d074` | `9cd1fdf51ef7a86896c3b3a1b9b4d51ecc36542aa039ccddca0ec71df40f9a82` | 0.7917 |
| S9_O02 | 25.275095 | 0.199839 | 0.064109 | NW | `6eabc53ec7a0da7af755809c5f073adff227148541e1384243b95edf51d2c7c6` | `bf9a3a0e54701b5de09bcccbe0d8156b1e489dddebb429f91ff013c2635d1a97` | 0.7230 |
| S9_C01 | 25.882717 | 0.199963 | 0.025010 | 양끝 개방 | `31cc4fc6d0615e3eb0b3e2d974bc8097a4eb0b0d29e37d71a6d11da1b9450ac1` | `c6d3f9c5cf61a560055adca15a4948322f6c778a85e8e5c7a27c988c5b156298` | 0.7817 |
| S9_C02 | 23.792622 | 0.200123 | 0.043565 | 양끝 개방 | `4e3a3e68c2fa3efd2a623d8f328500eda377be229ff22f09abeb0d3353c49314` | `d0bbdaf0e09a59e16bb2ea4e3602f09ec9c45c8030f10d0e0b32ba91c3082d6a` | 0.7361 |
| S9_C03 | 25.354483 | 0.200057 | 0.018967 | 양끝 개방 | `f34bad79bee735fa86d12ee34fbca3eb2b9dc4c5c500589790d860db1289695d` | `e1b47dc2e3af04594797987e37bb6ba0803b47f098cf6e052ea07fab721acbed` | 0.7115 |
| S9_C04 | 23.258826 | 0.199966 | 0.040361 | 양끝 개방 | `405bb0e58398260d56b643c51eeeb47afa8b5c582408dbdc312742e6bf0555e5` | `c5316df1c370deb924ed30b9ead1e9a7166d58d960b3b82150a957642103de64` | 0.7208 |
| S9_C05 | 25.531088 | 0.225009 | 0.053268 | 양끝 개방 | `85254160a13337f715f882bd90f7f117b1afcf2fa6f2a7d46308a21bdc5e8745` | `8a3c1ce51aff7130eb9b1f9e607f854c398aa808b85a0616afc570c1d2503679` | 0.9274 |

방 문 좌표·실제 에이프런·여백과 통로 끝 채도·실제 폭은 [selected.json](selected.json)에 있다. 주 바닥≥5%, 전체≥4%, 프롬프트≥8%와 보스 전체 면적 기준은 이전 사용자 결정을 유지했다. [generation.json](generation.json)은 호출 당시 이력을 보존하며 현재 채택은 selected/adoption이 정한다. [hash_integrity.json](hash_integrity.json): 누적30회 원본 해시, RAW=MASTER 바이트, GAME의 정확한 단일 전역 LUT와 사용자 채택 사본 일치 **PASS**. 모든 작업 이미지와 관리형 스테이징·거절 후보를 보존한다.

## 보스방 크기와 실루엣

S9_R05의 실제 전체 바닥(에이프런 포함)은 **510,410.5px², 1,481×660px**다. 주 바닥 여백6.280%, 전체5.144%; NE/SW 에이프런 채도0.068071/0.074089. 중앙은 열려 있고 **엄폐 없는 배치를 예정**했다. INDEX SPIRE의 계단식 지구라트와 바늘을 벽에 반복하지 않는다. [등록 보스 게임 축척 검토 합성](evidence/S9_R05_index_spire_silhouette_review_1920x1080.png)은 texture display_height276px, visible mass245.74px, 예정anchor `[0.37,0.62]`(NE 입구 반대 SW 쪽)이며 **플레이 캡처가 아니다**. 원화를 바꾸지 않은 이전 합성을 그대로 포함했다. 실제 바닥 fairness·전투/엄폐 정착은 연결 전 HOLD로 미실행이다.

## 검증 결과와 미실행 항목

| 항목 | 결과 |
|---|---|
| 판 실제 윤곽/색/문/폭/구조 수령 검사 | 채택13장; C06 HOLD; C07 미시도 |
| 원본/MASTER/GAME 해시·전역 LUT·채택 동일 바이트 | 누적30회 PASS |
| Godot C04/C05 texture import | 아래 import_checks와 로그 참조 |
| 1080p 검토 증거 | 아래 visual_evidence PASS: 크기·디코딩만 |
| 바닥/문 등록·reverse·월드·전투·엄폐 moved=0 | 미실행: 15판 전 HOLD |
| layout/mood --check, vault, 램프/허공, 시험 반복문 확장 | 미실행 |
| strict15plates/14seams, 이음매별 최종 수치 | 미실행 |
| 전용 회귀·quick·full / 러너 실행번호·요약경로 | 미실행 / 없음. 새 러너 시작 없음 |
| 실제 게임1080p15판·경로15·전체조감·테두리6곳 | 미실행 |
| INDEX SPIRE 게임 축척 합성 | 완료, 비플레이 증거; 실제fairness는 미검증 |

## 검토 증거 위치

- [C06 세 후보 표준/실제 윤곽 HOLD 시트](evidence/S9_C06_HOLD_native_3840x2880.png)
- [현재 채택13장 시트1](evidence/S9_selected_13_sheet_1_native_3840x2160.png), [시트2](evidence/S9_selected_13_sheet_2_native_3840x2160.png), [시트3](evidence/S9_selected_13_sheet_3_native_3840x2160.png), [시트4](evidence/S9_selected_13_sheet_4_native_3840x2160.png)
- C04 채택 윤곽과S3 비교, C05 두 후보와S3 비교/실제 바닥, C06 세 후보와S3 비교/표준·실제 바닥. 원화1:1, 검토 캔버스1920×1080 이상. **플레이 캡처·사람의 그림/플레이/균형 승인이 아니다.**

## 변경 범위와 Claude가 켜기 전에 확인할 것

이번 범위: C04/C05 채택 source/runtime/import, C05 1차와C06 3후보 격리, Stage D 매니페스트 및 새 QA 기록/상위README 뒤 추가. 제작 지시서는 Claude 소유라 편집하지 않았다. deployable/pending/staging, Op8 COMMAND, full_op_09, 보스 코드/원화/패턴, 적 수/HP, Op10, 감사 기준은 변경하지 않았다.

**C06 3회 상한 해소에는 사용자 지시가 필요하다.** 이후 C07 및 제작 지시서7절1–12를 끝내고 strict·회귀·실제 게임 증거가 갖춰져야 한다. Claude는 진짜 보스방의 boss_room_fairness, NE 입구와 SW 보스 배치, 출구 에이프런 슬롯 금지, 모든 문 폭·WASD 교차·엄폐 접근성 및 C05↔R06 밝기 이음부를 확인해야 한다. 현재 작전9를 켤 수 있다는 보고가 아니다. 자기 경로로 로컬 커밋하고 HOLD에서 멈춘다.

## 이번 거절 후보 SHA-256

| 판/차수 | RAW/MASTER SHA-256 | GAME SHA-256 | 노출 계수 |
|---|---|---|---:|
| S9_C05/1 | `deaa9b9c95f263f5c739b052769f2c1aa192013f9738e44dee87407a58dad602` | `da0e6d6c7efa4dde4ea15f82bbe186028037e9e6fc6063f8b02dd0d33e6bc16c` | 0.8934 |
| S9_C06/1 | `cd421b856cbcd52f3ef3991b86eb492dd04fe599ff91e8f7ec6c7ae0811d6a27` | `04fa6e2921275eaffc7442f12a5c6c1f305497b1209cb322ef14b3c7912f8293` | 0.6987 |
| S9_C06/2 | `d190f8f8aaa41dedf5987724a7a8540d41edb815986fd8581061c63da171dbcf` | `a5128959337cadcba51c1de6f958dd5c0950600b7c3ff2c5dd55a91cafbb1c8f` | 0.7917 |
| S9_C06/3 | `6ec901123478b69217010297367e7bc136193ce3db09d497d102053568e64269` | `a23350dc5c3276888f0a45b665ec59530b11316e9585a2ecd0e6cdbe5b13cfac` | 0.7574 |

## 반입 import와 최종 증거 검사

C04/C05 texture2개는 lossless·mipmaps 없음, UID/ctex 생성·존재를 확인했다([import_checks.json](import_checks.json)). Godot 종료0이지만 기존 `sound/music/originals/fps_bgm_06_sniper_ridge.wav`의 MP3 헤더 때문에 WAV import 오류가 있었다. [godot_import.log](godot_import.log)에 남겼고 해당 오디오는 바꾸지 않았다. 전체 import 무오류라고 보고하지 않는다.

검토 이미지 **21장**, `validate_visual_evidence_1080p.py` **PASS**([visual_evidence_1080p.json](visual_evidence_1080p.json)); 네이티브 캔버스 크기·디코딩 검사이며 그림·플레이 승인이 아니다.

## QA 보호와 로컬 커밋

모든 기록·시트는 D: 저장소 `.cache/diag/site7_ops_d/`에서 만들었다. QA 반입 직전 프로세스 목록으로 회귀 러너 부재를 확인하고 복사했다. 기존 stage_d 파일을 바이트 그대로 보존하며 상위 README 뒤에만 최신 사용자 결정·HOLD를 추가했다([qa_protection.json](qa_protection.json)). 삭제0, 기존 기록 변경0(상위README 뒤 추가 제외), 새 하위 폴더만 추가. 러너를 시작하지 않았다. 아트·격리·QA 자기 경로만 지정해 로컬 커밋하며 커밋 해시는 최종 보고에서 제공한다.
