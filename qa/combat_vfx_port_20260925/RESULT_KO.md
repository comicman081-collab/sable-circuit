# 전투 피격 이펙트 이식 — 2026-09-25 (WP-4)

`feat/combat-hit-hurt-vfx-v1` 브랜치의 볼류메트릭 피격 이펙트(V2)를 현재 런타임에 옮겼다.
그 브랜치의 CombatAuthority, RuntimePools, RuntimeSettings는 현재 코드에 없으므로 이펙트와 셰이더만 가져왔고,
반응 판정은 `CombatFeedback.hurt_reaction`으로 대신했다.

## 바뀐 점
- 명중 이펙트: 셰이더 기반 볼륨 광원 + 스파크/파편/증기. 탄의 진행 방향을 받아 맞은 면에서 반대쪽으로 튄다
  (엄폐물 명중 포함). 크기와 깊이(z 3100, 배율 0.42/앵커 0.75)는 기존 값을 유지했다.
- 피격 반응: 대원과 로봇이 맞으면 몸 중앙에서 반응 이펙트가 나온다. 체력 대비 피해 4% 미만 FLINCH,
  4% 이상 LIGHT, 14% 이상 HEAVY, 0이 되면 DOWNED. 로봇은 연사로 작은 피해가 이어지면 90ms에 한 번만 보이고,
  처치 순간은 기존 파괴 연출(EnemyDeathSequence)에 맡긴다. 보스는 더 크고 오래 보인다.
- 순간 조명(PointLight2D)은 데스크톱에서만 켠다. 웹 렌더러는 광원마다 캔버스 패스가 늘어 끈다.
- 브랜치의 인간형(RIFLE/SHIELD/ABERRANT) 프로필 그리기는 코드에 남아 있지만 현재 적 데이터가 쓰지 않는다.
- 화면 흔들림: 큰 타격과 폭발에만 약하게(최대 7px, 초당 2.4 감쇠). 대원 HEAVY 0.4(비조종 0.2)·DOWNED 0.55,
  박격포 착탄 0.3, 보스 범위 공격 0.35, 로봇 파괴 0.15, 보스 파괴 0.75. 작은 명중은 흔들지 않는다.
  일시정지 메뉴(FIELD MANUAL)의 `SCREEN SHAKE: ON/OFF`로 끄며 `user://settings.cfg`에 저장된다.

## 확인
- `tests/smoke/combat_hit_hurt_vfx_smoke.gd` 47개 검사 PASS(흔들림 포함) (러너 quick 스위트 `hit_hurt_vfx`).
- `tests/render/combat_hit_hurt_vfx_capture.gd` 창 모드 실제 렌더 1920×1080 두 장:
  - `01_room_hits_and_hurt.png` 작전 1 방 2에서 로봇 3기 명중+HEAVY 반응, ROOK 피격 반응.
    SHA-256 9dd27845e4f364165e78d3a464584b430984e34bc7ace94b1069b1eb46ee8dc7
  - `02_profile_and_reaction_matrix.png` 윗줄 ASTER/ROOK/MICA/드론/앵커/일반 명중, 아랫줄 FLINCH/LIGHT/HEAVY/DOWNED, 대원 HEAVY, 보스 HEAVY.
    SHA-256 a04468cb5c54c7f91d627683b21ec0dffd97d81d79003b7a921323d19e46500e
- `validate_visual_evidence_1080p.py` → `visual_evidence_1080p.json` (컨테이너·디코딩 확인일 뿐 화질 판정 아님).
- 사람 플레이 감각, 웹 성능, 아트 승인은 이 기록으로 판정하지 않는다.
