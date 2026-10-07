# 고정 코어 보스 — 앱 연결 후 확인

2026-09-13, 현재 주 작업 에이전트의 실제 관찰. 사용자/GPT/Luna 승인 아님.

- 기본 레지스트리의 `authored_core_v1/spec.json` SHA256:
  `c3f98d11fc537fd5e7d542e7114296cdc0c12b7f2f4877e71c1bd6fed194b763`.
  원화 SHA256 `c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4`.
- 앱 로딩·고정 몸체·실제 예고 후 발사: 271개 검사 통과.
  `anchor_app_1789289257_709.json`, SHA256
  `7f7ed4122dce4049bd79e2bdea856862cb2d39767d6c4e762fbc5ed09fe10845`.
- 앱 기본 경로의 네이티브 1920×1080 캡처:
  `anchor_native_1789289325_473/capture_report.json`, SHA256
  `010862d5a58bc71aed6b52619aa0f60c136620a83e4bdc248b0aa221759116fd`.
  실제 관찰한 장면은 phase1_attack1_attack, phase2_attack2_ground_impact,
  phase3_attack2_ground_warning이다. 중앙 홍채에서 분대를 향한 부채꼴 탄환,
  지면 공격 후 ASTER 체력 76/96, 원형/교차선 예고와 기둥 위 체력바를 확인했다.
  22장 전체의 해상도/디코딩은 `anchor_app_1080p.json`으로 검사했다.
- 이 캡처는 단계별 HP와 공격 순번을 지정한 촬영용 사례다. 적·분대를 모두
  자유롭게 둔 무수정 플레이 영상이라고 주장하지 않는다.
- 별도로 실제 전투/이동/상호작용을 구동한 `full_operation.json`이 다시 통과했다.
  현재 SHA256 `6eeb71e78af59e4887252f311c8ac853cbef92dad581402f0df49171a51e0f40`.
  HP/탄약 무한화나 살아 있는 적 삭제 없이 탈출했으며 인간 난이도 검증은 아니다.
- 보스 연결 후 드론 앱 회귀도 170개 통과했다:
  `drone_app_1789289734_917.json` SHA256
  `20b4fb501a528ba765e8d35527e204aca50b1cd09d458e0f4be6b8366467ad83`.

이 보스의 범위는 고정 중앙 코어 발사와 기존 3단계 공격이다. 네 팔 개별
회전/발사나 링 뒤집기 동작은 제작하지 않았다. 짧은 headless 시험 종료의
ObjectDB 경고는 미해결로 남긴다. 네이티브 캡처와 전체 경로 시험의 stderr에는
오류가 없었다. 소총병·방패병·변이체 제작 및 전체 MVP 완료와는 구분한다.
