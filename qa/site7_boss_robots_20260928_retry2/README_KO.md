# SITE-7 RELAY SENTINEL 재생성 HOLD — 2026-09-28

사용자의 재생성 지시에 따라 Codex 내장 ImageGen으로 RELAY SENTINEL을 새 배치에서 3회 더 생성했다. 세 후보의 기계 형태는 보스 설정에 대체로 맞지만, 원본 RGBA에 모두 알파 255 픽셀이 있다. `motion_lab_v1/source_alpha_policy.py --source`가 세 장 모두 `ALPHA_RANGE_0_254_REQUIRED`로 거절했다. 5번 후보는 본체 밖에 떨어진 화소도 보여 시각 검수에서 거절했다.

| 재시도 | 원본 크기 | 알파 범위 | 알파 255 픽셀 | 판정 |
|---|---:|---:|---:|---|
| 1 (전체 4) | 1254×1254 | 0..255 | 496 | FAIL_NOT_PROMOTABLE |
| 2 (전체 5) | 1254×1254 | 0..255 | 343 | FAIL_NOT_PROMOTABLE |
| 3 (전체 6) | 1254×1254 | 0..255 | 264 | FAIL_NOT_PROMOTABLE |

새 원본은 `motion_lab_v1/art/site7_enemies_raw/quarantine/relay_sentinel/attempt04.png`–`attempt06.png`에 바이트 그대로 격리 보존했다. 앞선 `attempt01.png`–`attempt03.png`와 관리형 생성 사본도 보존했다. `boss_asset_gate.json`에 관리형 경로, 프로젝트 사본, SHA-256과 검사값을, `relay_prompts.md`에 프롬프트를 기록했다. 후보의 알파를 보정·키잉하거나 런타임에 연결하지 않았다.

지시서 7절의 이번 배치 3회 제한으로 RELAY SENTINEL은 다시 HOLD다. RESONANCE REMNANT 생성과 보스 패턴·레지스트리·게임 데이터 작업은 시작하지 않았다. 따라서 quick/full 회귀, 게임 캡처와 영상은 실행하지 않았으며 PASS로 주장하지 않는다. 스테이지 4/5 원화의 알파 255 예외는 이 신규 보스에 적용하지 않았다. Claude의 파일과 커밋은 변경하지 않았다.
