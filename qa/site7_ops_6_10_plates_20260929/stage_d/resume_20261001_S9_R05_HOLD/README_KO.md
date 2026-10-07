# 작전 9 MEMORY VAULT — 단계 D 재개 / S9_R05 HOLD

2026-10-01. **S9_R02 3차는 사용자 승인 기준으로 채택했고, S9_R03·R04는 각각 3차를 채택했다. S9_R05가 3회 안에 규격을 충족하지 못해 HOLD로 중단했다.** 누적 ImageGen 13회, 채택 반입 4/15장, 현재 거절 후보 9장, 미시도 10장이다. 이 재개에서 새로 호출한 것은 R03/R04/R05 각각 3회, 총 9회다. R02 추가 호출은 없다.

이 기록과 새 evidence는 별도 하위 폴더에 보존한다. 상위 README의 이전 S9_R02 HOLD 본문, 이전 generation/measurements 및 격리 REJECTION은 그대로 두고 채택 결정과 현재 HOLD를 뒤에 덧붙인다.

## 판별 시도·채택·거절

| 판 | 누적 시도 | 채택 차수 | 결과와 거절 사유 |
|---|---:|---:|---|
| S9_R01 | 1 | 1 | 채택 반입, 이전 커밋 유지 |
| S9_R02 | 3 | 3 | 3차 사용자 채택(주 바닥 7.42%, 전체 4.67%); 1차 여분 SE 문·전체 3.89%, 2차 전체 3.23% 거절 |
| S9_R03 | 3 | 3 | 3차 채택; 1차 S3 모니터 벽 배치 반복, 2차 네이티브 1602×982 규격 불일치 |
| S9_R04 | 3 | 3 | 3차 채택; 1차 주/전체 여백 4.90/3.23%, 2차 4.96/3.47% 거절 |
| S9_R05 | 3 | — | HOLD: 1차 주 여백·SW 에이프런 채도; 2차 주 여백·높이·NE/SW 에이프런 채도; 3차 주 여백·면적 실패 |
| S9_R06 | 0 | — | 미시도: S9_R05 HOLD에서 중단 |
| S9_O01 | 0 | — | 미시도: S9_R05 HOLD에서 중단 |
| S9_O02 | 0 | — | 미시도: S9_R05 HOLD에서 중단 |
| S9_C01 | 0 | — | 미시도: S9_R05 HOLD에서 중단 |
| S9_C02 | 0 | — | 미시도: S9_R05 HOLD에서 중단 |
| S9_C03 | 0 | — | 미시도: S9_R05 HOLD에서 중단 |
| S9_C04 | 0 | — | 미시도: S9_R05 HOLD에서 중단 |
| S9_C05 | 0 | — | 미시도: S9_R05 HOLD에서 중단 |
| S9_C06 | 0 | — | 미시도: S9_R05 HOLD에서 중단 |
| S9_C07 | 0 | — | 미시도: S9_R05 HOLD에서 중단 |

## 새 후보 실제 추적 측정

주 바닥은 실제 그려진 바닥에서 실제 문 에이프런 폴리곤을 뺀 영역이다. 채택 기준은 주 바닥 여백 ≥7%, 전체 ≥4%이고 프롬프트 목표는 8% 이상을 유지했다. 실제 윤곽에서 기존 `floor_axis()`·`plate_floor()`를 사용했으며 이상적인 좌표로 대체하지 않았다. 에이프런 색은 실제 폴리곤을 10% 안쪽으로 줄인 샘플이다. [measurements.json](measurements.json)에 좌표·에이프런·좌상우하 여백·폭·색·실패가 있다.

| 판/차수 | 축 ° | 휘도 | 채도 | 주/전체 최소 여백 % | 주 면적 px² | 노출 계수 | 결과 |
|---|---:|---:|---:|---|---:|---:|---|
| S9_R03/1 | 25.151518 | 0.200194 | 0.065283 | 7.895 / 7.895 | 449150 | 0.6406 | 새 벽 실루엣 실패 |
| S9_R03/2 | 24.651471 | 0.199978 | 0.065455 | 7.615 / 5.243 | 434739 | 0.6890 | native size (1602, 982) != (1672, 941) |
| S9_R03/3 | 25.110692 | 0.200130 | 0.084738 | 7.835 / 7.835 | 448714 | 0.6910 | PASS / 채택 |
| S9_R04/1 | 25.500531 | 0.200448 | 0.025577 | 4.904 / 3.230 | 529688 | 0.7652 | main floor border margin 4.904% below 7%; whole floor border margin 3.230% below 4% |
| S9_R04/2 | 25.422867 | 0.200198 | 0.017520 | 4.964 / 3.469 | 539544 | 0.7308 | main floor border margin 4.964% below 7%; whole floor border margin 3.469% below 4% |
| S9_R04/3 | 25.050312 | 0.200169 | 0.000820 | 8.194 / 5.981 | 484149 | 0.8146 | PASS / 채택 |
| S9_R05/1 | 24.121365 | 0.200114 | 0.108977 | 4.665 / 4.665 | 503029 | 0.8357 | main floor border margin 4.665% below 7%; SW apron saturation 0.110023 exceeds .10 |
| S9_R05/2 | 26.387151 | 0.200138 | 0.104160 | 4.725 / 4.007 | 539640 | 0.8558 | main floor border margin 4.725% below 7%; main floor bounds below (1100, 612); NE apron saturation 0.114004 exceeds .10; SW apron saturation 0.103072 exceeds .10 |
| S9_R05/3 | 25.751452 | 0.200030 | 0.074953 | 6.280 / 5.144 | 466650 | 0.7750 | main floor border margin 6.280% below 7%; boss open main arena below 490000 px2 |

### S9_R05 마지막 3차

- 실제 주 바닥 bounds `[108,237,1567,852]`: 폭 **1459 px**, 높이 **615 px**, 면적 **466,650 px²**. 크기/면적 기준(4.3절 최소 약 490,000 px²)보다 면적이 작다. 주 여백 좌/상/우/하 **6.459/25.186/6.280/9.458%**, 전체 최소 **5.144%**다.
- 축 **25.751452°**, 휘도 **0.200030**, 채도 **0.074953**은 통과다. 최종 에이프런 색과 전체 여백도 통과하지만 주 여백과 면적을 숨기거나 완화하지 않았다.
- NE/SW 문만 있으며 NW/SE는 닫혔다. 벽 부착 읽기 헤드와 직사각 블레이드 랙이고 중앙 바닥 장애물은 없다. 채택 보스방이 없으므로 런타임 엄폐·spawn·boss_anchor 및 INDEX SPIRE 합성은 아직 만들지 않았다.
- 3회 상한에 도달했다. 다음 판 R06/O01/O02 및 통로는 시작하지 않았다. 추가 호출은 사용자 허가 전에는 없다.

## 원화·반입·해시

RAW와 MASTER는 바이트 동일. GAME은 전체 이미지 단일 sRGB LUT 노출 계수만 적용했다. R02 3차 채택 복사는 RAW/MASTER/GAME 모두 격리 사본과 바이트·SHA 동일, 계수 0.7500 그대로다. 회전·전단·비균등 리사이즈·손칠·부분 자산 합성·로컬 모델은 없다. [hash_integrity.json](hash_integrity.json) 누적 13회 SHA/LUT 검사 PASS.

채택 위치: `art_src/environments/site7_v2/stage09/S9_R01`…`S9_R04` 및 `assets/environments/site7_v2/stage09/S9_R01`…`S9_R04`. 새 격리는 `_quarantine/S9_R03`, `S9_R04`, `S9_R05`이고 각 차수의 RAW/MASTER/GAME/request/measurement/REJECTION을 보존했다. 모든 작업 이미지·관리형 스테이징 원본도 보존한다. [generation.json](generation.json)은 호출 당시 이력이며 R02의 현재 채택은 [S9_R02_adoption.json](S9_R02_adoption.json)과 [selected.json](selected.json)이 기록한다.

| 채택 판 | RAW/MASTER SHA-256 | GAME SHA-256 | 계수 |
|---|---|---|---:|
| S9_R01 | `730a850b2b5eeab8394a7974383ecede5ba4e0fd74419b38f73384a59928c71c` | `1320d7a71a6ab9e35e413ab642cb90bf159db80c4401e401e77f61798f6b3d59` | 0.7329 |
| S9_R02 | `43aab4e4ab15e9b716ce65240ddcdc58d9ef21cf1c18b69b19fcb31a57015c89` | `92eb87d83a7cda89813393a91736d934afd2595f6078c8e8b27a4fae40cb5876` | 0.7500 |
| S9_R03 | `dde725716f925c7170b81a0be5dd2f83d8991972189612b43f7f586ac31ea7d6` | `6d68fd48db6222690848170a4534a8d8ae42f539f83f7b058538096d7f3c89ce` | 0.6910 |
| S9_R04 | `0c34ec924baae774a145d62166e2f3f410ed2cc5832f47442d004136c80f5ed1` | `c0c1d9039b332e25791c65846bd998fd22f6fa10488807b964c2363d95ca39f7` | 0.8146 |

## 검증과 실행하지 않은 항목

| 항목 | 결과 |
|---|---|
| 원화 실제 바닥·문·여백·색 | 새 후보 모두 측정; R03/R04 3차 통과, R05 HOLD |
| SHA / 원화-MASTER 바이트 / 전역 LUT | 누적 13회 PASS |
| 네이티브 1080p 검토 컨테이너 | `visual_evidence_1080p.json` 확인: 크기·디코딩만 검증 |
| 바닥·문 데이터 / reverse / 월드·전투 지형 / 엄폐 moved=0 | 미실행: 15판 전 HOLD |
| mood / vault / lamp / void / 반복문 확장 | 미실행 |
| strict 15 plates / 14 seams, layout·mood --check | 미실행 |
| 전용 회귀 / quick / full | 미실행; 러너 요약 없음. 러너를 시작하지 않았다 |
| 실제 게임 1080p 15판·경로 오버레이·조감·테두리 6곳 | 미실행 |
| 채택 보스방 실루엣 / fairness | 미실행: 보스방 HOLD |

## 검토 시트

- [채택 4장, 네이티브 3840×2160](evidence/S9_selected_4_native_3840x2160.png)
- [S9_R05 3회 HOLD 검토, 네이티브 3840×2160](evidence/S9_R05_HOLD_native_3840x2160.png)
- 새 후보 실제 바닥/에이프런 오버레이 9장, 채택 R02/R03/R04와 S3 비교 3장, 새 거절 후보와 S3 비교 7장. 각 원화는 **1:1** 그대로 컨테이너에 배치했다. R03 2차 1602×982도 확대하지 않았다.
- **그림/윤곽 검토 합성이며 플레이 캡처가 아니다.** 1080p PASS는 화질·그림·플레이·균형 승인을 대신하지 않는다.

## Claude가 켜기 전에 확인할 것

현재 켤 수 있는 단계가 아니다. S9_R05 HOLD를 해결하고 나머지 10판을 제작한 뒤 지시서 7절 1–12의 연결·strict·회귀·게임 캡처를 완료해야 한다. 이후 Claude가 실제 바닥에서 boss_room_fairness, 보스 배치와 출구 슬롯, 물리 경로를 확인한다. 사람의 그림·플레이·균형 승인은 별도로 필요하다.

deployable/pending/staging, 작전 8 COMMAND, full_op_09, 보스 코드·패턴·원화, 적 수·HP, 작전 10은 변경하지 않았다. 데이터 연결과 시험 기준도 변경하지 않았다. 커밋은 지정한 자기 아트·격리·QA 경로만 대상으로 로컬에서 한다.

## 반입 import와 QA 보호 확인

새 검토 이미지 21장의 `validate_visual_evidence_1080p.py` 결과는 **PASS**다(크기·디코딩만). R02/R03/R04 texture import는 lossless이며 UID/ctex를 생성했고 파일 존재를 확인했다([import_checks.json](import_checks.json)). Godot editor import 종료 코드 0이나 전체 스캔 중 기존 `sound/music/originals/fps_bgm_06_sniper_ridge.wav`의 MP3 헤더 때문에 오디오 오류가 났다. [godot_import.log](godot_import.log)에 기록했고 해당 파일은 바꾸지 않았다. 전체 프로젝트 import가 무오류였다는 주장은 하지 않는다.

QA 반입 직전 PowerShell 프로세스 목록에서 회귀 러너가 없음을 확인했다. 상위 README 뒤에만 승인·현재 HOLD를 덧붙이고 기존 stage_d 파일은 그대로 보존했다([qa_protection.json](qa_protection.json)). 기록·증거는 먼저 `.cache/diag/site7_ops_d/`에서 작성한 뒤 복사했다.
