# SITE-7 v2 단계 5 검증 기록

단계 4 로컬 커밋 `2d659c8d4`를 보고한 뒤 작업했다. 이 단계에서 작전 4·5 전용 통로 `S4_C01`–`S4_C07`, `S5_C01`–`S5_C07` 14장과 작전 2·3 보스방 `S2_R05`, `S3_R05` 2장을 새로 제작하고 게임에 연결했다. 작전 1 `S1_R05`는 교체하지 않았다. 각 작전이 방 8장과 통로 7장, 총 15장의 전용 판을 사용한다.

원화와 파생본은 `art_src/environments/site7_v2/SITE7_MAP_KIT_V2_MANIFEST.md`와 `stage5_derivatives.json`에 기록했다. 선택한 16장 모두 RAW와 MASTER가 바이트 단위로 같고, GAME은 원본과 같은 크기에서 전체 픽셀에 단일 sRGB 노출 계수만 적용했다. `derivative_validation.json`이 이 관계와 SHA-256을 16/16 검증한다. 잘라내기, 리사이즈, 반전, 부분 칠은 하지 않았다. 거절한 `S4_C01` 두 번째 후보는 `_quarantine/S4_C01/`에 보존했다. 교체 전 두 보스방의 RAW·MASTER·GAME·원래 후보는 `_superseded/`에 보존하고 이전 경로, 새 보존 경로, 해시, 교체 이유를 `stage5_replaced_boss_manifest.json`에 남겼다.

전체 검증 뒤 이번 배치의 관리형 ImageGen 임시 사본 17개만 해시로 확인하고 정리했다(`staging_cleanup.json`). 프로젝트 안의 선택 원본, 거절 후보, 교체 전 원화는 보존했다.

작전 4 주 경로 통로는 기존 `reverse` 배치를 그대로 사용한다. 판의 아래 왼쪽 끝은 다음 방, 위 오른쪽 끝은 앞 방의 벽 강조색이다. 작전 5의 `C06` ID는 `ENV_S05_DEFENSE_SUPPLY`로 정정했다. 새 바닥 윤곽과 두 보스방의 문 앵커, 보스 전투 바닥·스폰·엄폐, 무드 조명과 공허 마스크, 월드 배치 및 이음매 조명을 연결했다. 엄폐 재정착 후 dry run은 `moved=0`이었다. `site7_battle_geometry_smoke.gd`는 모든 판 경로가 한 작전에서만 쓰이는지 검사한다.

검증 결과:

- `audit_site7_plate_lighting.py --strict`: 작전 1–5 각각 15/15 판, 14/14 이음매 PASS. 결과: `plate_lighting_all_missions.json`.
- `build_site7_world_layout.py --check`: 5개 작전 PASS. `build_site7_mood_light.py --check`: 75장, 램프 풀 427개, 공허 마스크 75개 PASS.
- 회귀 quick: 34/34 PASS. 회귀 full: 55/55 PASS. full에서 작전 1–5 전체 진행, 보행 감사 1235건, 통로 정렬 530건, 전투 기하 2497건 모두 PASS. 영수증과 작전 2–5 결과는 `regression/`에 보존했다.
- 실제 Godot 1920×1080 캡처는 `game/`에 새 통로 14장과 교체 보스방 2장, `compare/`에 같은 카메라의 이전 판 16장과 나란히 놓은 비교 16장, `boss_five/`에 보스방 5장과 한 장 비교, `title/`에 교체된 `S3_R05`를 사용하는 타이틀을 보존한다. `walk_graph/`는 새 통로와 교체 보스방을 포함한 보행 바닥 윤곽 검토용이다. `evidence_manifest.json`은 네이티브 캡처 73장과 무손실 WebP의 픽셀 일치 및 해시를 기록한다. `resolution_validation.json`은 90개 검토 이미지의 1080p 검사기 PASS 결과다.

캡처의 방 이름과 화살표는 게임의 길 안내 오버레이이며 원화에 포함되지 않는다. 이 기록은 원화 교체와 게임 연결 검증이다. 사람 플레이 승인이나 배포 승인은 별개다.
