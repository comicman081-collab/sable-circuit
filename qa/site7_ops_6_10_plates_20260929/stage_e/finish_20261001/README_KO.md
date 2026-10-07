# SITE-7 작전 10 ZERO POINT — 단계 E 완료 기록

2026-10-01. 판 **15/15장** 반입과 작전 10의 연결·무드·`null` 심연을 작성했다. ImageGen **23회**, 최종 채택 15장, 현재 거절 후보 8장이다. 각 판은 3회 이내다. **작전 10은 켜지 않았다. 그림·플레이·균형 승인이 아니다.**

## 사용자 결정과 보존 이력

- S10_R01 3차는 사용자 결정으로 채택했다. 공통 코너/끝 기둥·벽 베이·문틀 공유는 허용하고 같은 슬롯의 베이 장비·패널 내용 반복만 거절한다. 첫 HOLD와 당시 판정은 보존했다.
- S10_R05 3차도 사용자 결정으로 채택했다. 남은 방의 좌우 여백은 주 바닥 ≥4.5%, 전체 바닥 ≥3.5%; 상하 기준은 주 5%, 전체 4%다. 프롬프트 목표와 실제 측정을 구분한다.
- **이름 지정 면제: S10_R05 attempt03 전체 바닥 짧은 변 547 px**(정상 612–733 px). 면적 563,547 px², 전체 크기 1,547×547 px. 다른 판·감사 기준에는 적용하지 않았다.
- S10_R05 1·2차의 기존 여백 거절에 사용자 판단인 S3_R05 좌우 베이 내용 반복을 추가했다. 과거 측정·REJECTION 원문과 격리 사본을 유지한다.
- 채택 후보 RAW와 MASTER는 같은 PNG 바이트다. GAME은 전체 이미지에 노출 계수 하나를 적용한 sRGB LUT뿐이다. 색상별 처리·손칠·부분 합성·회전·전단·비균등 리사이즈·로컬 모델은 없다.
- 완료 직전 C05 2차 정식 RAW의 1바이트가 초기 검증 이후 달라져 SHA가 불일치했다. 변경 사본을 `.cache/diag/site7_ops_e/integrity_incident_c05/`에 보존하고, 해시가 일치하는 정식 MASTER와 작업 RAW를 대조해 원래 바이트로 복원했다. [사건 기록](source_integrity_incident_c05.json), 복원 뒤 23회 해시·LUT 재검사 PASS. 원인과 작성 프로세스는 확인하지 못했다.

## 15장 시도와 채택

| 판 | 호출 수 | 채택 차수 | 노출 계수 | 거절·채택 사유 |
|---|---:|---:|---:|---|
| S10_R01 | 3 | 3 | 0.7388 | 1차: S3_R01의 중앙 코너 기둥과 반복 리브 간격·동일 벽 베이 배치가 남았다. 원형 팬 제거와 색 변경만으로 새 벽 구조가 되지 않아 거절. 축 23.820°, 휘도 0.199857, 채도 0.052738, 문 NE 하나·여백·크기는 통과.; 2차: 네이티브 크기 1603×981로 목표 1672×941 대비 -69/+40 px, ±2 px 범위 밖. 크롭/리사이즈 없이 거절. NE 벽 베이·중앙 코너 기둥 구조 반복도 남음.; 공통 골조를 이유로 했던 과거 판정 보존, 3차 사용자 채택 |
| S10_R02 | 2 | 2 | 0.8279 | 1차: 전체 바닥(에이프런 포함) 여백 왼쪽 3.409%, 오른쪽 3.469%로 4% 하한 미달. 실제 좌우 끝 x=57/1614. 크기·축 25.564°·휘도·채도·문은 통과, 새 오벨리스크 베이 내용도 사용자 기준으로 통과. 여백만으로 거절. |
| S10_R03 | 1 | 1 | 0.7712 | 첫 후보 채택: 새 베이 내용·수치 검사 통과 |
| S10_R04 | 1 | 1 | 0.6446 | 첫 후보 채택: 새 베이 내용·수치 검사 통과 |
| S10_R05 | 3 | 3 | 0.8125 | 1차: Main-floor right border margin 4.784689% (80 px) is below 5%; actual whole-floor width1498 height675 area576423.5, axis24.663517,luma0.200238,apron saturation0.0775-0.0788 otherwise pass. Bay content distinct; no boss crystal silhouette in wall. Actual painted-floor trace retained; no polygon shrink to hide failure.; 2차: Actual main-floor right border margin 4.724880% (79 px) below5%; whole-floor area576403.5 width1499 height676, axis24.748862,luma0.200173,apr on saturations0.07869-0.08056 otherwise pass. The generated boundary remained almost unchanged despite inset request. Keep actual trace, no shrinking registration.; 1·2차는 사용자 재검토에서 벽 베이 반복도 거절, 3차는 짧은 변 면제 포함 사용자 채택 |
| S10_R06 | 1 | 1 | 0.7687 | 첫 후보 채택: 새 베이 내용·수치 검사 통과 |
| S10_O01 | 1 | 1 | 0.6912 | 첫 후보 채택: 새 베이 내용·수치 검사 통과 |
| S10_O02 | 1 | 1 | 0.7422 | 첫 후보 채택: 새 베이 내용·수치 검사 통과 |
| S10_C01 | 1 | 1 | 0.7891 | 첫 후보 채택: 새 베이 내용·수치 검사 통과 |
| S10_C02 | 2 | 2 | 0.8506 | 1차: 벽 내용 반복: 중앙 x650–790 베이의 대형 루버·벤트 패널 구성이 S3_C02와 같고 색·조명만 바뀜. 공통 골조 공유와 별개의 같은 베이 내용. |
| S10_C03 | 1 | 1 | 0.8263 | 첫 후보 채택: 새 베이 내용·수치 검사 통과 |
| S10_C04 | 2 | 2 | 0.7614 | 1차: 벽 내용 반복: 좌측 x350–440과 x535–630 루버 패널 베이 구성이 S3_C04와 같다. 색·조명만 바뀐 해당 베이는 거절. |
| S10_C05 | 2 | 2 | 0.7537 | 1차: Wall bay-content repetition: lower-left wide square closed panel with attached narrow control box and lower vent retains S3_C05 equipment arrangement; upper-right large closed-panel bay also remains substantially the reference configuration. Numeric inspection passes; changed accents and middle grille alone do not clear all repeated bays. |
| S10_C06 | 1 | 1 | 0.7239 | 첫 후보 채택: 새 베이 내용·수치 검사 통과 |
| S10_C07 | 1 | 1 | 0.7214 | 첫 후보 채택: 새 베이 내용·수치 검사 통과 |

## RAW/MASTER/GAME 해시

[source_integrity.json](source_integrity.json)의 23회 모든 원화·MASTER 바이트 일치 및 GAME LUT 전 픽셀 검사는 PASS다. [generation.json](generation.json)은 전체 프롬프트·참조와 참조 SHA·과거 판정·채택 이력을 담는다. [floor_traces.json](floor_traces.json)은 채택 15장의 실제 추적 윤곽이다.

| 판 | RAW SHA-256 = MASTER SHA-256 | GAME SHA-256 |
|---|---|---|
| S10_R01 | `b71b0135f06423c7da3202108e1ba442c6ce68c2526ee9ceb20277dda11f082d` | `e567a57d15a61df6f042a51c79ee4222f8bd807945bb2599e428b01e3d2569eb` |
| S10_R02 | `787f34dbbd408c6bb232f7241d89eded7f71028ef3b242fce6e222e9bc18c2da` | `ac97f989f9516bfea70b114f1c5e55980d106150f4d036b3ea0e49fa9ab1c00a` |
| S10_R03 | `a3cf48345e106f571bf3f71fb77ef4ef742a7731603ca80e880930bf7d7722bf` | `49f00392c28aeaac3bd3f060f4725c2078025bd3fd6e32832632d32af0bec2a4` |
| S10_R04 | `10dae607a9624cf28555af3e67e4be3b301d92d1a479d2aeafa23beeb67e31f7` | `7277efe6504c0392d7283cf665369c71280219cd96e3a686d0cf6994b96aade9` |
| S10_R05 | `6fd9b23af85998c3f083fdfeff1793d852359e9e11e2bed6c2bd5c40bfbf8c0a` | `49cd7a027eda96db253555775111379d11214e7b4f26444610f77c9ac4050b57` |
| S10_R06 | `5bf2630a51c772319fe9adf71570c2cecf77a35d3df716314b4126bef9390d5a` | `6a165077bb11d98e8e0d367dd65a1ed3e382d9c509a2943551230a5c98bd4ab0` |
| S10_O01 | `25f2c44eae0cd6012fb48b12f5398728b0c2ff4df3dcc2f95f7f74e27915848c` | `5184151da84bc3a51775cec8d605f3e63c6a267ba7c25203dbb392c4e014c5df` |
| S10_O02 | `33f3bd42a8746115d5b4eb59cd5b1e32935fcef79cf67a9c915f19e59399d243` | `afcbafa192ef8651004cf1df46f9e10f858d2863b907812d9d7113f5aa023d3e` |
| S10_C01 | `14c4b7d84e8e6243c61c6246822684fc97cb4a8fc11647981d2d27fdc285d7f5` | `b9743811e38ba02620a7cfb24e401661e2296908ec36e6d8a45c00dc485c9aaf` |
| S10_C02 | `903568f8a74feaa5e489e293e0e944766a92e5f14571368d5cf83d9ae402c97e` | `f2001c3177fb892af5704ab62ace2759ebf219fbff2c8f33fe92522f567fa347` |
| S10_C03 | `03847d21cf798108455c2edf8ada2fe04038f21416fc68d8431e651df5075a16` | `054ce7ed67d07666045b0128c64c1e1626446c81d8baa0ecfb2a9ac0532b8d4a` |
| S10_C04 | `020ca12a56ec37438d74808e81902e033f159bfb7166d7acd5ecf6252d39e0ac` | `bab4bbfc2b26392535f27aefa51387159a83273f58a8d5dc40c9077c16be0515` |
| S10_C05 | `253f75a8244b3267dbe081a789193b23d2ce19820276edb20a6c9ab599b0cfa1` | `3bd354aa975e1b105cfc9b4b990f35435b9633dd9e26cac6ba5b40351880849f` |
| S10_C06 | `04c40388c151e32906d98eca846c9676e102991bb87ed2b023bec067a3707cfb` | `72dc5e6af1107c0e49b994aa2eddefdaa7de17755ad2f22d752a693d0d92fc57` |
| S10_C07 | `af893fd791bbeae5fc51584c99533a274a2632f0f372a6f0b88839e5650af84f` | `ab56d63b7b388855bf6bbbae4fafdfef34ee70f6455df1b268429c2a47ecbbf6` |

## 실제 바닥 검사

실제 그려진 바닥과 문 에이프런을 추적해 등록했다. 표준 윤곽으로 대체하지 않았다. 축·휘도·채도는 strict 감사의 등록 윤곽 샘플 값이다. 이 샘플은 intake 당시 캔버스 좌표의 반올림 측정과 작은 차이가 날 수 있다. 네이티브 크기는 그대로이며 가로·세로 ±2 px 허용 안이다.

| 판 | 네이티브 px | 축 ° | 휘도 | p10 / p90 | 채도 | 문 | 전체 바닥 면적 % |
|---|---|---:|---:|---|---:|---|---:|
| S10_R01 | 1672×941 | 24.024 | 0.199535 | 0.167776 / 0.232098 | 0.047585 | NE | 27.21 |
| S10_R02 | 1672×941 | 26.673 | 0.200320 | 0.153667 / 0.250408 | 0.034415 | SW, NE, SE | 30.25 |
| S10_R03 | 1672×941 | 25.152 | 0.199753 | 0.155565 / 0.235169 | 0.056433 | SW, NE | 32.27 |
| S10_R04 | 1774×887 | 22.832 | 0.199880 | 0.168906 / 0.235126 | 0.056571 | SW, NE | 33.83 |
| S10_R05 | 1672×941 | 24.896 | 0.200024 | 0.165306 / 0.237471 | 0.078414 | SW, NE, SE | 35.82 |
| S10_R06 | 1672×941 | 27.260 | 0.200132 | 0.160616 / 0.246078 | 0.050016 | SW | 32.62 |
| S10_O01 | 1672×941 | 25.897 | 0.199761 | 0.163686 / 0.225427 | 0.069369 | NW | 27.61 |
| S10_O02 | 1672×941 | 25.920 | 0.199754 | 0.155565 / 0.227325 | 0.064452 | NW | 27.49 |
| S10_C01 | 1774×887 | 26.150 | 0.199961 | 0.143243 / 0.242690 | 0.007997 | 양 끝 절단 | 31.54 |
| S10_C02 | 1774×887 | 23.929 | 0.199955 | 0.134227 / 0.250298 | 0.022233 | 양 끝 절단 | 33.81 |
| S10_C03 | 1774×887 | 25.288 | 0.200078 | 0.150192 / 0.238322 | 0.023344 | 양 끝 절단 | 31.01 |
| S10_C04 | 1774×887 | 23.358 | 0.200189 | 0.132161 / 0.246612 | 0.017328 | 양 끝 절단 | 27.96 |
| S10_C05 | 1774×887 | 25.861 | 0.199537 | 0.141176 / 0.242243 | 0.010559 | 양 끝 절단 | 30.91 |
| S10_C06 | 1254×1254 | 31.618 | 0.210088 | 0.118373 / 0.261851 | 0.031147 | 양 끝 절단 | 28.15 |
| S10_C07 | 1254×1254 | 29.846 | 0.199774 | 0.107055 / 0.246165 | 0.018858 | 양 끝 절단 | 26.67 |

| 방 | 주 바닥 좌/상/우/하 여백 % | 전체 바닥 좌/상/우/하 여백 % |
|---|---|---|
| S10_R01 | 9.390 / 23.911 / 8.493 / 13.071 | 9.390 / 23.911 / 8.493 / 13.071 |
| S10_R02 | 14.115 / 24.230 / 13.278 / 13.390 | 8.134 / 24.230 / 8.971 / 13.390 |
| S10_R03 | 9.031 / 22.423 / 7.536 / 10.840 | 8.134 / 22.423 / 7.536 / 10.840 |
| S10_R04 | 7.554 / 22.661 / 6.313 / 8.117 | 6.313 / 22.661 / 6.313 / 8.117 |
| S10_R05 | 6.758 / 24.867 / 7.476 / 20.723 | 3.529 / 22.848 / 3.947 / 19.022 |
| S10_R06 | 10.885 / 20.510 / 8.014 / 8.608 | 7.057 / 20.510 / 8.014 / 8.608 |
| S10_O01 | 11.244 / 19.554 / 10.467 / 12.540 | 11.244 / 19.554 / 10.467 / 12.540 |
| S10_O02 | 10.885 / 19.554 / 10.526 / 13.177 | 10.885 / 19.554 / 10.526 / 13.177 |

| 방 | 에이프런 | 평균 휘도 | 평균 채도 ≤0.10 |
|---|---|---:|---:|
| S10_R01 | NE | 0.227357 | 0.038085 |
| S10_R02 | SW | 0.232781 | 0.035726 |
| S10_R02 | NE | 0.219700 | 0.021854 |
| S10_R02 | SE | 0.217659 | 0.034925 |
| S10_R03 | SW | 0.233067 | 0.056464 |
| S10_R03 | NE | 0.221150 | 0.065166 |
| S10_R04 | SW | 0.210650 | 0.053319 |
| S10_R04 | NE | 0.228831 | 0.043804 |
| S10_R05 | SW | 0.230504 | 0.075956 |
| S10_R05 | NE | 0.193653 | 0.093426 |
| S10_R05 | SE | 0.229304 | 0.075084 |
| S10_R06 | SW | 0.249472 | 0.072009 |
| S10_O01 | NW | 0.239501 | 0.035607 |
| S10_O02 | NW | 0.227011 | 0.066790 |

| 통로 | 실제 양 끝 세로 폭 px | 내부 단면 폭 px | 끝 채도 |
|---|---|---|---|
| S10_C01 | ↗ 양 모서리 절단 | 313 / 309 / 302 | 0.024196 / 0.011857 |
| S10_C02 | ↗ 양 모서리 절단 | 323 / 320 / 318 | 0.077189 / 0.013869 |
| S10_C03 | ↗ 양 모서리 절단 | 311 / 302 / 298 | 0.013406 / 0.041721 |
| S10_C04 | ↗ 양 모서리 절단 | 265 / 255 / 247 | 0.052743 / 0.007475 |
| S10_C05 | ↗ 양 모서리 절단 | 305 / 300 / 296 | 0.048289 / 0.004483 |
| S10_C06 | [340, 366] | 344 / 352 / 361 | 0.024051 / 0.036222 |
| S10_C07 | [339, 330] | 338 / 335 / 332 | 0.033702 / 0.013942 |

- ↘ C06 끝 폭 340/366 px, 축 31.618°; C07 339/330 px, 축 29.846°. 양 끝은 표준 332/326 px의 ±15% 안이며 이 두 판만 축 상한 32.5°를 쓴다. 다른 판은 22.5–30.5°다.
- C06의 실제 오른쪽 아래 y=1190, C07 y=1120이다. 요청 y=1081과 다르므로 실제 윤곽을 등록했다. C06 GAME 계수는 최종 0.7239(목표 휘도 약 0.21)다. 이전 측정 계수 0.6894와 그 GAME/측정 사본은 `.cache/diag/site7_ops_e/candidates/S10_C06/attempt01/`에 보존했다.
- 방 문 점은 그려진 문턱 중심이다. 긴 에이프런 경계는 데크 방향을 따르고, NE 문기둥이 가린 일부 짧은 경계도 실제 그림대로 추적했다. 미화를 위한 이상적인 다각형으로 대체하지 않았다. 직접 작전 10 왕복 정렬 시험 106 체크는 PASS다.

## Strict 감사 — 15판·14이음매

[strict_audit.json](strict_audit.json): **15 plates / 14 seams PASS**, 모든 `problems=[]`, 작전 10의 `waived=[]`. 새 이음매 예외와 기준 변경은 없다. 채도비와 색상차는 감사 도구의 기존 저채도/회색 판정과 함께 읽는다. 아래 수치가 모두 채도비 1.5 또는 색상차 30° 이하라는 뜻은 아니다.

| 통로 | 방 | raw 밝기 차 stops | 데크/방 채도 | 채도비 | 색상차 ° | 판정 |
|---|---|---:|---|---:|---:|---|
| S10_C01 | R01_DESCENT | +0.100074 | 0.006156 / 0.034830 | 2.0963 | 152.942 | PASS |
| S10_C01 | R02_RELAY | +0.106492 | 0.007950 / 0.033483 | 1.9135 | 133.930 | PASS |
| S10_C02 | R02_RELAY | -0.059585 | 0.064083 / 0.027578 | 1.7673 | 22.389 | PASS |
| S10_C02 | R03_LOG | -0.025945 | 0.013698 / 0.050133 | 2.0812 | 53.258 | PASS |
| S10_C03 | R03_LOG | -0.109194 | 0.023303 / 0.054179 | 1.7130 | 111.489 | PASS |
| S10_C03 | R04_GALLERY | -0.207754 | 0.091381 / 0.050601 | 1.5776 | 2.079 | PASS |
| S10_C04 | R04_GALLERY | -0.073403 | 0.038966 / 0.060632 | 1.3674 | 0.295 | PASS |
| S10_C04 | R05_CORE | +0.069306 | 0.007089 / 0.070990 | 3.3590 | 111.625 | PASS |
| S10_C05 | R05_CORE | -0.276045 | 0.037343 / 0.096806 | 2.0370 | 1.020 | PASS |
| S10_C05 | R06_EXIT | +0.051509 | 0.012024 / 0.066767 | 2.7094 | 57.222 | PASS |
| S10_C06 | R05_CORE | -0.223159 | 0.024957 / 0.070801 | 2.0197 | 3.436 | PASS |
| S10_C06 | O01_VAULT | +0.147610 | 0.032725 / 0.064877 | 1.6098 | 1.397 | PASS |
| S10_C07 | R02_RELAY | -0.223713 | 0.031488 / 0.036325 | 1.0939 | 14.054 | PASS |
| S10_C07 | O02_RECORDER | +0.017998 | 0.013805 / 0.064280 | 2.4932 | 22.892 | PASS |

## 연결과 검증

- `site7_plate_floors`, `site7_battle_art`: 실제 바닥·문, 전용 15판, `ENV_S10_*`/`S10_C01`–`C07`, scale 1.0. C01–C05 `ascending`/seam fade 0.10, C06·C07 `descending`/0.075, **reverse 없음**.
- `site7_battle_layouts`: R02 COMBAT, R04 ELITE 통로, R05 BOSS. R05 적 슬롯과 boss_anchor는 NE/SE 에이프런 밖이다. 적 수·체력·보스 패턴은 Codex가 바꾸지 않았다.
- `site7_environment_props`: 9개 엄폐, 보스방 0개. 작전10만 정착하는 `--mission` 옵션을 도구에 추가했다. 초기 마른 실행 4개 이동 필요 → write 4개 → 최종 **moved=0**. [최종 로그](settle_final_dry.log).
- `site7_mood`: 작전 행과 15판 행, 램프·void 마스크. `null`은 별도 그림 없는 코드 쿼드 한 장이다. 흰 등각 격자와 붉은 점, 매우 약한 안개; 웹의 안개 옥타브 절반 유지. 로봇·작전자·엘리트·소품은 착색하지 않는다.
- 레이아웃 생성/`--check` PASS: 10 missions. 무드 생성/`--check` PASS: 150 plates, 788 pools, 150 void masks, 기존 dawn contact 15. [기존 행 바이트 보호](existing_row_bytes.json): 작전1–9의 기존 값 바이트 동일, contact 파일 전체 동일.
- [직접 작전10 정렬 로그](connector_initial_mission10.log): 7통로, **106 checks PASS**, 실제 WASD 양방향 왕복. 방 추적이 순차 연결 전에는 정렬 시험을 방마다 수행하지 못했고, 15판 연결 후에 이 직접 검사와 전체 러너 검사를 수행했다.
- GAME 15장 Godot 텍스처 import: 실제 네이티브 크기와 디코딩된 GAME 픽셀 일치 PASS(해당 JSON·로그 포함). 전체 editor import 종료 0이지만 기존 `fps_bgm_06_sniper_ridge.wav` MP3 헤더 오류가 있어 전체 프로젝트 import 무오류라고 주장하지 않는다. [import 로그](godot_import.log).
- 실제 캡처 로그에는 기존 ASTER 보조 raster의 `M7_RASTER_QUARANTINED` 경고와 viewport export 경고도 남아 있다. 현재 MotionLab runtime은 active이고 실제 입력·공격 검사는 PASS였다. 캐릭터/오디오를 고치지 않았다.

## 회귀 러너

실행 명령(도구 출력과 아래 러너 요약을 기준으로 결과를 기록한다):

```text
python tools/environment/build_site7_world_layout.py
python tools/environment/build_site7_world_layout.py --check
python tools/environment/build_site7_mood_light.py
python tools/environment/build_site7_mood_light.py --check
python tools/environment/audit_site7_plate_lighting.py --mission MIS_CH01_10 --strict --out .cache/diag/site7_ops_e/integration/strict_audit.json
godot --headless -s res://tools/environment/settle_cover_on_floor.gd -- --mission=MIS_CH01_10 --write
godot --headless -s res://tools/environment/settle_cover_on_floor.gd -- --mission=MIS_CH01_10
godot --headless -s res://tests/smoke/site7_connector_alignment_smoke.gd -- --mission=10
python tools/maintenance/run_regression_suite.py --only world_layout,mood_light,mood_contact,plate_axis,seam_waiver,battle_geometry,connector_alignment,traversal_audit,world_route,floor_segment,zone_hazard,firing_lane,elite_affix,combat_density,campaign_data
python tools/maintenance/run_regression_suite.py
```

- custom: **PASS**, 15/15. [요약](custom_summary.json), 원본 실행 폴더 `qa/regression_runs/20261001_202459_custom`.

| 시험 | 결과 | 초 |
|---|---|---:|
| combat_density | PASS | 22.3 |
| floor_segment | PASS | 50.6 |
| campaign_data | PASS | 1.6 |
| elite_affix | PASS | 9.5 |
| zone_hazard | PASS | 58.4 |
| firing_lane | PASS | 37.5 |
| world_layout | PASS | 26.1 |
| mood_light | PASS | 107.8 |
| plate_axis | PASS | 5.4 |
| seam_waiver | PASS | 4.1 |
| mood_contact | PASS | 1.8 |
| traversal_audit | PASS | 899.1 |
| world_route | PASS | 28.0 |
| connector_alignment | PASS | 1438.0 |
| battle_geometry | PASS | 31.4 |
- quick: **PASS**, 44/44. [요약](quick_summary.json), 원본 실행 폴더 `qa/regression_runs/20261001_211310_quick`.

| 시험 | 결과 | 초 |
|---|---|---:|
| combat_density | PASS | 19.0 |
| cover_navigation | PASS | 1.6 |
| floor_segment | PASS | 38.5 |
| combat_query_fastpath | PASS | 10.8 |
| player_cover | PASS | 7.2 |
| cover_alpha_clip | PASS | 1.6 |
| cover_texture | PASS | 2.4 |
| battle_flow | PASS | 9.2 |
| combat_entry | PASS | 7.0 |
| drone_app | PASS | 2.0 |
| anchor_app | PASS | 1.8 |
| campaign_data | PASS | 0.6 |
| upgrade_economy | PASS | 1.6 |
| boss_registry | PASS | 13.6 |
| boss_pattern | PASS | 3.0 |
| boss_duel | PASS | 36.9 |
| boss_room_fairness | PASS | 14.2 |
| robot_roster | PASS | 7.8 |
| enemy_facing | PASS | 2.8 |
| machine_source | PASS | 2.0 |
| emission_owner | PASS | 4.2 |
| m2_story | PASS | 5.0 |
| m9_skill | PASS | 4.4 |
| m10_base_ui | PASS | 0.8 |
| m10_persistence | PASS | 0.6 |
| m12_revive | PASS | 4.4 |
| play_log | PASS | 5.8 |
| hit_hurt_vfx | PASS | 2.4 |
| combat_vfx | PASS | 2.6 |
| elite_affix | PASS | 4.6 |
| zone_hazard | PASS | 48.9 |
| firing_lane | PASS | 30.7 |
| platform_carry | PASS | 6.4 |
| contact_carry | PASS | 15.8 |
| world_layout | PASS | 13.8 |
| mood_light | PASS | 72.4 |
| walk_registration | PASS | 2.4 |
| plate_axis | PASS | 3.2 |
| seam_waiver | PASS | 2.0 |
| mood_contact | PASS | 1.0 |
| deploy_warmer | PASS | 7.4 |
| m13_migration | PASS | 0.8 |
| m13_campaign | PASS | 0.6 |
| m13_runtime | PASS | 4.6 |

## 1080p 검토 증거

[전체 15장 연락 시트](S10_all_15_contact_1920x1080.webp)는 네이티브 1920×1080 컨테이너의 축소 개요다. 상세 판정에는 `comparison/`의 **15장 원래 픽셀 1:1 비교**, `floor_trace/`의 실제 등록 바닥 추적 15장을 함께 쓴다. ↘ 판은 1920×1440에 원래 1254×1254 픽셀을 담았다.

- `runtime_capture/`: 실제 Godot 화면 23장(방8×2 시점 + 통로7, 이음매 포함).
- `walk_graph/`: 판별 바닥·경로 오버레이15 + 전체조감1, JOIN_GAPS 0. `world_preview/`: 조감1 + 이음매7.
- `plate_edges/`: R01/R05/O02/C03/C05/C06 여섯 실제 1920×1080 카메라. 흰 격자와 붉은 점을 확인했다.
- `gameplay/`: R02/R04/R05의 실제 게임 화면 3장과 scripted WASD/공격 보고. 방2곳 이상에서 null 가독성 확인. 자율 사람 플레이나 풀플레이 기록은 아니다.
- `null_gameplay/`: 같은 실제 게임 축척에서 카메라만 180 px 낮춘 R02/R04 화면 2장. HUD·작전자·적과 허공의 흰 격자/붉은 점을 함께 보여 준다. 런타임 설정이나 원화를 바꾸지 않은 캡처 전용 카메라다.
- `S10_R05_origin_silhouette_COMPOSITE_native_1920x1080.webp`: 등록된 ORIGIN CORE를 게임 축척으로 방 위에 얹은 **실루엣 검토 합성, 플레이 캡처 아님**. 등록 원화는 검정/금빛 본체에 밝은 끝을 갖고 있으며 벽의 평평한 합금 상자와 다른 뾰족한 다발 실루엣이다. 원화를 바꾸지 않았다.
- [visual_evidence_1080p.json](visual_evidence_1080p.json): 90장의 컨테이너 크기·디코딩 PASS. 픽셀 확대나 그림/플레이/균형 승인을 보증하지 않는다. 첫 실행은 파일 대신 디렉터리를 인자로 넣어 FAIL했고, `visual_evidence_initial_input_error.json`에 남긴 뒤 실제 파일들로 재실행했다.

## 보스방과 Claude가 켜기 전에 확인할 것

R05_CORE의 그려진 전체 바닥은 **563,547 px², 1,547×547 px**, 주 바닥 면적 468,463 px²다. 주 바닥 면적·높이에는 별도 하한이 없고 전체 짧은 변 547 px만 사용자 면제다. 가운데 엄폐물 0, boss_anchor `[0.69,0.52]`, SW 입구의 먼 쪽 내부다. NE 출구와 SE 보급 갈래 문어귀에 보스나 지원 적을 두지 않았다.

**보스방 공정성은 Claude 담당의 별도 측정이다.** 제작 지시서의 초기 후보/등록 후 측정은 일부 공격 실패를 보고했다. 작업 중 Claude가 커밋 `749ff72b`에서 마지막 단계 wind-up을 1.6초로 맞췄고, 문서 커밋 `f0edcfbf`에는 100/75/60/50/40/30/25/20/15/10 px 격자 통과(10 px: 34,458 공격, 실패0, 최악 안전 바닥150 px, 여유0.33초)라고 기록했다. 이는 Claude의 보고이며 Codex가 독립 실행한 작전10 공정성 결과가 아니다. 보스에서150–800 px의 모든 서는 자리에서 180 px 안에 1.5명 폭의 경고 없는 바닥, 곧게 닿는 길, 138 px/s 기준 0.25초 여유라는 한도는 유지한다. Quick의 boss_room_fairness는 출격 가능한1–9만 검사하므로 작전10 공정성 PASS를 대신하지 않는다. Claude가 켜기 전에 최종 납품 바닥·anchor·현재 패턴과 측정 증거가 맞는지 확인한다. Codex는 보스 코드/시험을 수정하거나 커밋에 넣지 않았다.

보급 갈래가 보스방에서 열리고 PRISM7기·총27기·엘리트5기로 가장 무거운 작전이다. Claude가 사용자의 켜기 지시 뒤 실제 방 공정성·봇 풀플레이·자기 방 보스 캡처·소리 영상·full 스위트를 확인한다. Codex는 full 스위트/full_op_10을 실행·등록하지 않았다. 같은 세션 FPS A/B와 사람 플레이, 그림·균형 승인은 미실행이다.

## 변경 범위와 공유 작업 트리

RAW/MASTER/GAME와 `.import`, 격리 이력, 매니페스트, 바닥/문/배치/엄폐/무드/램프/void/이음매 데이터, null 심연, 허용된 시험 목록과 캡처/정착 도구, 이 QA 기록을 변경했다. `changed_paths.txt`와 커밋 범위 JSON이 실제 경로 목록이다.

작전9 판/연결 값과 작전1–9 기존 데이터 값은 그대로다. 캠페인의 deployable/pending, 작전10 staging, 작전9 COMMAND, full_op_10, 보스 코드·시험·원화는 Codex가 고치거나 스테이지하지 않았다. 동시에 Claude가 보스 코드/시험 등을 수정한 경우 그 경로는 이 커밋에서 제외하고 검증 시점에 읽은 공유 작업 트리 상태를 기록한다. 원화·작업 이미지·관리형 스테이징·격리 사본을 삭제하지 않았다.

QA 반입 전마다 러너 프로세스를 확인한다. 러너 실행 중에는 `.cache/`에만 증거를 썼다. custom: QA 변경 0 / 삭제 0 / 추가 0; quick: QA 변경 0 / 삭제 0 / 추가 0

로컬 커밋은 자기 경로만 지정한다. 커밋 해시는 최종 보고에서 확인한다. 원격 push/PR/Pages/Actions는 없다. **단계 E에서 멈춘다. 작전10을 켜거나 그림·플레이·균형 승인을 하지 않는다.**

## 검토 이미지의 로컬 커밋

저장소 `.gitignore`는 QA 사진을 기본 제외하며 문서가 인용한 사진은 `add -f`로 넣도록 적혀 있다. 이번 보고가 인용한 현재90장과 보존된 HOLD28장만 경로를 지정해 추가 커밋했다. [이미지 SHA-256](review_image_integrity.json), [역사 포함118장 컨테이너/디코딩 검사](visual_evidence_with_history_1080p.json) PASS. 첫 아트/데이터/코드 커밋은 `f2462d2e`이며 추가 이미지 커밋 해시는 최종 보고에서 확인한다. ignored 작업/cache/회귀 출력은 스테이지하지 않았다. 기존 사진을 다시 그리거나 리사이즈하지 않았다.
