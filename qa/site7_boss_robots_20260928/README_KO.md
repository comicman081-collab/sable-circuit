# SITE-7 신규 보스 원화 HOLD — 2026-09-28

`docs/production/SITE7_BOSS_ROBOTS_CODEX_PROMPT_KO.md` 7절의 첫 순서인 RELAY SENTINEL 원화 제작에서 중단했다. Codex 내장 ImageGen으로 최대 허용 횟수 3회를 생성했으며, 세 파일 모두 원본 RGBA PNG의 알파 최대값이 255였다. 일반 정책 `motion_lab_v1/source_alpha_policy.py`의 허용 범위는 0..254이고 스테이지 4/5의 사용자 예외는 이번 보스에 적용되지 않는다. 알파를 잘라내거나 키잉하거나 후보를 런타임에 연결하지 않았다.

| 시도 | 원본 크기 | 알파 범위 | 알파 255 픽셀 | 판정 |
|---|---:|---:|---:|---|
| 1 | 1254×1254 | 0..255 | 753 | FAIL_NOT_PROMOTABLE |
| 2 | 1254×1254 | 0..255 | 699 | FAIL_NOT_PROMOTABLE |
| 3 | 1254×1254 | 0..255 | 736 | FAIL_NOT_PROMOTABLE |

받은 원본 세 장은 `motion_lab_v1/art/site7_enemies_raw/quarantine/relay_sentinel/attempt01.png`–`attempt03.png`에 그대로 보존했다. `relay_imagegen_responses.json`과 `boss_asset_gate.json`에 관리형 응답 경로, 프로젝트 사본, SHA-256 및 검사값을 기록했다. 생성 프롬프트 전문은 `relay_prompts.md`에 있다. 관리형 생성 사본도 보존했다.

지시서의 HOLD 조건에 따라 RESONANCE REMNANT 생성과 패턴·레지스트리·게임 데이터 변경은 시작하지 않았다. ANCHOR는 변경하지 않았다. 따라서 quick/full 회귀, 게임 캡처, 영상 검증은 이 배치에서 실행하지 않았으며 완료 또는 PASS로 주장하지 않는다. Claude의 지시서와 커밋은 변경하지 않았다.
