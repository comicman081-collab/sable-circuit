# SITE-7 작전 7 COLD STORAGE — 단계 B 판 연결 기록

2026-09-29. 파일럿 없이 작전 7 전용 방 8장과 통로 7장을 Codex ImageGen으로 한 장씩 제작·검사했다. RAW/MASTER/GAME을 반입하고 바닥, 문, 월드 배치, 전투 지형, 엄폐, 무드, 심연을 연결했다. `data/story/site7_campaign.json`의 작전 7 `deployable: false`와 `data/missions/MIS_CH01_07.json`의 `staging`은 건드리지 않았다. 작전 활성화는 Claude가 담당한다.

## 원화와 반입

- 원화 15장은 네이티브 불투명 RGB다. RAW와 MASTER는 바이트가 같고, GAME에는 판 전체의 같은 sRGB 노출 계수만 적용했다. GAME 배율은 1.0, Godot import는 `compress/mode=0`, `mipmaps/generate=false`다. 정확한 최종 ImageGen 프롬프트, 참조, 해시, 시도 횟수와 노출 계수는 [단계 B 매니페스트](../../../art_src/environments/site7_v2/SITE7_OP7_STAGE_B_MANIFEST.md)에 있다.
- `S7_R01` 첫 후보는 S3_R01의 원형 팬 벽 실루엣을 반복해 거절했다. RAW/MASTER/GAME과 거절 사유는 `_quarantine/S7_R01/attempt01`에 보존했다. 나머지 14장은 첫 후보를 채택했다. 관리형 ImageGen 원본도 남겨 두었다.
- `S7_R05_VAULT`의 벽은 직선형 냉동 설비 패널로 그렸다. [CRYO COMPRESSOR 실루엣 합성](S7_R05_cryo_silhouette_review_1920x1080.webp)에서 보스의 밝은 설비 실루엣은 벽과 분리된다. 합성은 게임 플레이 캡처가 아니다. 방 중앙에 엄폐물을 두지 않았고 `boss_anchor`는 북동쪽 입구 반대편 `[0.37, 0.62]`다.

## 연결과 화면 검토

- `site7_plate_floors.json`에 그려진 바닥과 방 8개의 실제 문턱을 추적했다. C01–C05는 `reverse: true`로 주 경로가 내려가며, 두 선택 갈래는 C06–C07로 연결한다. 월드 레이아웃의 14개 연결 틈은 모두 0 px이고 작전 사이에 판을 공유하지 않는다.
- 전투방 R02, 엘리트 통로 R04, 보스방 R05의 바닥·출발점·적 배치와 엄폐를 연결했다. 엄폐 정착 마른 실행은 `moved=0`이다.
- 15장 고유 냉동 무드, 램프 및 허공 마스크를 생성하고 코드 기반 `cryo` 심연 스타일을 연결했다. 원화의 중성 바닥은 유지하며 분위기는 런타임 셰이더가 입힌다.
- [전체 조감](S7_world_overview.webp), [15장 연락 시트](S7_all_15_contact_1920x1080.webp), [S3 기준판 비교 15장](comparison/), [실제 게임 1080p 방·통로 23장](runtime_capture/)과 [실제 게임 1080p 바닥·경로 오버레이 15장과 조감](walk_graph/)을 확인했다. 원래 PNG는 `.cache/diag/site7_ops_b/`에 남겼다.
- [1080p 증거 검증](visual_evidence_1080p.json)은 `--require-dynamic-capture` PASS, 총 57장이다. 크기와 디코드 검증이며 플레이 품질 승인은 아니다.

## 기술 검증

| 항목 | 결과 |
|---|---|
| [원화 조명 strict audit](strict_audit.json) | PASS, 판 15장·이음부 14개, 기준 밖 0건 |
| 월드 레이아웃 / 무드 `--check` | PASS, 7개 작전 / 105장·램프 풀 530개·허공 마스크 105장 |
| 엄폐 정착 마른 실행 | PASS, 이동 0건 |
| quick 회귀 | PASS 41/41, `qa/regression_runs/20260930_002743_quick/SUMMARY_KO.md` |
| 전투 지형 전용 회귀 | PASS 3491 검사, `qa/regression_runs/20260929_225927_custom/SUMMARY_KO.md` |
| full 회귀 | PASS 65/65, `qa/regression_runs/20260929_233400_full/SUMMARY_KO.md`; 기존 QA 기록 변경·삭제·추가 0건 |
| 전체 순회 감사 | PASS 1687 검사, `site7_traversal_audit_smoke.gd`의 작전 1–7, 작전 7 연결 틈 0 px |
| 작전 7 문턱 양방향 왕복 | PASS 106 검사, `site7_connector_alignment_smoke.gd --mission=7` |
| 전체 월드 경로 탐색 | PASS 67 검사, `site7_world_route_navigation_smoke.gd` |
| 작전 7 두 갈래 실제 이동 | PASS, O01/O02 목표 도달 |
| 15판 로딩 검사 | PASS, 실제 게임 캡처 15판 및 오버레이 15판 |

작전 7은 출격 불가 상태이므로 자동 플레이 또는 사람의 플레이 승인을 뜻하지 않는다. 검토 시트와 기록은 다른 회귀 러너가 실행되는 동안 `.cache/diag`에만 보관했고, 러너가 없는 것을 확인한 뒤 QA 폴더에 옮겼다.
