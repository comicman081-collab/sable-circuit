# 엘리트 변종 — 2026-09-25 (WP-6, D7)

D7은 권장안대로 결정했다: 엘리트 변종을 먼저 만들고, 구역 위험 요소는 그다음에 한다.
이번 작업은 새 적을 만들지 않는다. 기존 로봇에 속성만 붙인다.
로봇 아트 픽셀은 색을 입히거나 바꾸지 않는다. 변종 표시는 코드로 그린 바닥 링과 머리 위 이름표뿐이다.

## 속성 (`data/progression/elite_affixes.json`)
- SHIELDED(청록): 체력의 30%만큼 방벽이 피해를 먼저 흡수한다. 4.5초 동안 피해를 받지 않으면 초당 20%씩 다시 찬다. 체력바 위에 방벽 바가 따로 보인다.
- OVERCHARGED(주황): 피해 ×1.2, 공격 간격 ×0.9, 이동 ×1.05. 작전 난이도 배율 위에 곱해진다.
- VOLATILE(노랑): 파괴되면 반경 140 경고 원이 1.0초 표시된 뒤 폭발해 원 안의 대원에게 18 피해를 준다(작전 피해 배율 적용).
  - 보스 범위 공격처럼 엄폐를 무시한다.
  - 플레이 기록에는 그 로봇의 피해로 남는다.
- 전투 안내 문구에 그 방에 있는 변종의 설명이 붙는다.

## 배치 (임무 JSON 행의 `"affix"`)
| 작전 | 방 | 변종 |
|---|---|---|
| 1 | R04 봉쇄 교차로 | 첫 BULWARK SHIELDED |
| 2 | R04 | 첫 드론 OVERCHARGED |
| 3 | R04 | BULWARK SHIELDED, 드론 VOLATILE |
| 4 | R02 전투 | BULWARK SHIELDED |
| 4 | R04 | PRISM OVERCHARGED, 증원 드론 VOLATILE |
| 5 | R04 | NULL PYLON SHIELDED, CINDER OVERCHARGED, 증원 드론 VOLATILE |

보스에는 붙이지 않았다. 사용자가 30분 플레이한 기록(`playtest_logs/`)을 보고 조정한다.

첫 제안값에서 한 차례 낮췄다:
- 첫 제안값은 방벽 35%, OVERCHARGED 피해 ×1.25, VOLATILE 22 피해였고, 작전 2의 변종은 CINDER에 있었다.
- 그 값으로 전체 스위트를 돌렸더니 작전 2와 작전 4의 자동 플레이 봇이 보스 방에서 전멸했다.
- 봇은 변종을 넣기 전에도 보스전을 HP [6, 1, 55] 정도로 겨우 넘겼다. 엘리트 방이 보스 방 바로 앞이라, 들어가는 체력이 줄자 넘어가지 못했다.
- 그래서 수치를 위와 같이 낮추고, 작전 2의 OVERCHARGED를 돌진형 CINDER에서 첫 드론으로 옮겼다.
- 조정 후 작전 2와 작전 4 봇이 PASS했다. 끝날 때 HP는 [9.6, 19.6, 39.2]와 [15.6, 11.3, 4.2]로, 변종을 넣기 전과 비슷하게 여전히 얇다.

## 확인
- `tests/smoke/elite_affix_smoke.gd` 43개 검사 PASS (러너 quick 스위트 `elite_affix`).
  - 데이터: 속성 정의, 작전별 행 수, 보스 제외.
  - 작전 3 엘리트 방의 실제 스폰 결과.
  - 방벽: 흡수, 넘친 피해, 재충전 지연과 상한. 수치는 표에서 읽어 검사한다.
  - OVERCHARGED 배율 중첩, 중복 적용 방지.
  - VOLATILE: 경고 중 무피해, 경고가 끝나면 원 안 1명만 피해, 피해 출처 기록, 자체 정리.
- `tests/render/elite_affix_capture.gd` 창 모드 실제 렌더 1920×1080:
  - `01_op3_shielded_and_volatile.png` 방벽을 절반 쓴 SHIELDED BULWARK와 VOLATILE 드론.
    SHA-256 f487ba415ed535708e82ac4d3b2b15acd26dcb1380f10fce1bf19813083e2720
  - `02_op3_volatile_warning.png` VOLATILE 드론 파괴 0.5초 뒤 경고 원.
    SHA-256 ba075f522bf206a4dd8d9dc82e42a2fb37bfd1442867951b274ea5462fce13d6
  - `03_op5_shielded_and_overcharged.png` SHIELDED NULL PYLON과 OVERCHARGED CINDER.
    SHA-256 334d84770b26f653dc143302c96bac77b871ddcfd54cd76b8db5a7e1d39b7462
  - 캡처 연출: 동료 사격에 대상이 먼저 사라지지 않도록, 대기 중에는 변종 로봇의 체력을 채워 두었다. 02의 드론과 03의 CINDER는 HUD에 가리지 않도록 분대 옆으로 옮겨서 찍었다.
  - 위치는 `elite_affix_layout.json`에 있다.
  - 세 장은 수치를 낮추기 전에 찍었다. 표시 방식은 같고, 방벽 바 길이만 그때 비율(35%) 기준이다.
- `validate_visual_evidence_1080p.py` → `visual_evidence_1080p.json` gate PASS. 이는 컨테이너와 디코딩만 확인한 것이고 화질이나 아트 승인이 아니다.
- 전체 스위트(작전 1~5 자동 플레이 추출 포함) 결과는 커밋 메시지에 적는다.
- 사람 플레이 난이도 판정은 이 기록으로 하지 않는다.
