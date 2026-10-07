# SITE-7 작전 6 VERDANT LOCK — 단계 A 판 연결 기록

2026-09-29. 사용자 승인 A0 판 `S6_R02`, `S6_C01`, `S6_C06`을 다시 만들지 않고, 나머지 12장을 Codex ImageGen으로 제작했다. 작전 6 전용 방 8장과 통로 7장을 모두 반입해 바닥·문·월드 배치·전투 엄폐·무드·심연을 연결했다. `data/story/site7_campaign.json`의 작전 6 `deployable`은 `false` 그대로다. 단계 B–E와 작전 활성화는 진행하지 않았다.

## 반입과 원화

- RAW, MASTER, GAME 15장 모두 네이티브 불투명 RGB. RAW와 MASTER는 바이트가 같고, GAME에는 판 전체에 동일한 sRGB 노출 계수만 적용했다. GAME 배율은 1.0, Godot import는 `compress/mode=0`, `mipmaps/generate=false`다.
- A0 3장의 GAME SHA-256은 승인 당시 [A0 매니페스트](../../../art_src/environments/site7_v2/SITE7_OP6_A0_MANIFEST.md)와 동일함을 재확인했다. 새 12장의 정확한 최종 프롬프트, 참조, 원본·반입 해시, 시도 횟수와 노출 계수는 [단계 A 매니페스트](../../../art_src/environments/site7_v2/SITE7_OP6_STAGE_A_MANIFEST.md)에 있다.
- `S6_R04`, `S6_R05`의 첫 후보는 요구되지 않은 SE 출입구 때문에, `S6_R06`의 첫 후보는 S3 기준판과 지나치게 비슷한 벽 때문에 거절했다. 원본과 해시는 `_quarantine`에 보존했다. 선택된 판은 모두 ImageGen 3회 이내다.
- `S6_R05`는 직선형 재배 선반·환기 기둥 벽으로 구성했다. 현재 AERATOR TOWER 원화의 흰 버섯 갓과 라임 꽃잎 방출구는 [실루엣 검토 합성](S6_R05_aerator_silhouette_review_1920x1080.webp)에서 벽과 구분된다. 이 합성은 게임 플레이 캡처가 아니다.

## 연결과 화면 검토

- `site7_plate_floors.json`에 그려진 바닥과 8개 방의 실제 문턱을 추적했다. R01의 가짜 SW 바닥 혀를 제외하고, R02/R04/R05의 NE 문 중심을 실제 열린 문턱에 놓았다. 월드 생성기의 14개 연결 틈은 0 px이며 작전 6은 판을 공유하지 않는다.
- 전투방 R02·엘리트 R04·보스방 R05의 바닥, 출발점, 적 배치와 엄폐물을 연결했다. 엄폐 정착은 쓰기 실행 후 마른 실행 모두 `moved=0`이었다.
- 작전 6의 녹색 온실 무드 15장, 램프 및 허공 마스크를 생성하고 코드 기반 `spore` 심연 스타일을 연결했다. 판 원화의 중성 바닥은 유지하고 런타임 셰이더가 분위기를 입힌다.
- [전체 조감](S6_world_overview.webp)은 최종 문 중심으로 다시 생성한 1920×1080 화면이다. [15장 연락 시트](S6_all_15_contact_1920x1080.webp), [S3 기준판과 15장 비교](comparison/), [실제 게임 1080p 방·통로 23장](runtime_capture/)과 [실제 게임 1080p 바닥·경로 오버레이 15장](walk_graph/)을 확인했다. `runtime_capture`는 방마다 두 시점, 통로마다 한 시점이며 무손실 WebP다. 원래 PNG 23장은 프로젝트 `.cache/diag/site7_ops_a/runtime_capture/`에 남겼다.
- [1080p 증거 검증](visual_evidence_1080p.json)은 `--require-dynamic-capture` PASS다. 이 검증은 크기와 디코드만 증명하며 플레이 품질 승인은 아니다.

## 기술 검증

| 항목 | 결과 |
|---|---|
| [원화 조명 strict audit](strict_audit.json) | PASS, 판 15장·이음부 14개, 기준 밖 0건 |
| 월드 레이아웃 / 무드 `--check` | PASS, 6개 작전 / 90장·램프 풀 498개·허공 마스크 90장 |
| 엄폐 정착 마른 실행 | PASS, 이동 0건 |
| quick 회귀 | PASS 39/39, `qa/regression_runs/20260929_145013_quick/SUMMARY_KO.md` |
| full 회귀 | PASS 63/63, `qa/regression_runs/20260929_145928_full/SUMMARY_KO.md` |
| full 내 순회 / 연결 왕복 / 전투 지형 | 각각 1468 / 636 / 2994 검사, 실패 0건 |
| 작전 6 두 갈래 실제 이동 | PASS, `site7_branch_navigation_regression.gd --mission=6`의 O01/O02 목표 도달 |
| 15판 headless 로딩 검사 | PASS, `qa/regression_runs/20260929_145810_custom/SUMMARY_KO.md` 및 full 항목 |

전체 회귀는 기존 출격 가능 작전 1–5의 자동 플레이를 포함하며, 출격 불가 작전 6의 자동 플레이나 사람의 플레이 승인을 뜻하지 않는다. 중간 진단 실행 한 번은 테스트 2개가 모두 통과했으나, 같은 시간 이 폴더에 비교 시트를 추가해 회귀 러너의 QA 불변성 검사에서 실패했다. 증거 작성이 끝난 뒤 실행한 quick/full은 QA 변경 0건으로 통과했다.
