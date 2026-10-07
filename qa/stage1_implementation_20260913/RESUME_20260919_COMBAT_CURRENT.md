# 현재 재개 지점 — 2026-09-19 캠페인 / 신규 로봇 이후

이전 엄폐 AI 배치 이후 3개 작전의 정상 출격·완료·다음 임무 흐름과 신규 로봇
3종이 연결됐다. 최신 적 작업은 `qa/stage_enemies_20260919/RESULT_KO.md` 및
그 디렉터리의 exact-content manifest를 먼저 읽는다. BULWARK는 1, CINDER는
2, VESPER는 3스테이지에 도입된다. 드론으로 전부 되돌리지 않는다.

아래는 이전 배치 기록이다. `source_design_pending`은 후속 신규 로봇에 의해
대체됐으며, 인간형 적 취소와 플레이어 모션 보존 조건은 그대로 유효하다.

현재 근거는 `qa/cover_ai_20260919/RESULT_KO.md`, `full_operation_final.json` 및
`battle_194039/encode_manifest.json`이다. 인간형 총병과 Kimodo 총병 파일럿 재개
문서는 취소된 역사다. 인간형 적을 생성하거나 예전 목업으로 복구하지 않는다.

현재 앱은 플레이어 ASTER/ROOK/MICA, 검토된 드론 재사용, 고정 보스,
kArchive 엄폐물 15개, 실제 SFX, 엄폐 우회 AI, 탄환 차단 및 보호막을 사용한다.
스테이지 1 전체 전투/선택 구역/탈출과 화면 전환 검사가 통과했다.
영상은 실제 입력을 사용하는 네이티브 10초 연습전이며 전체 임무 완주 영상은 아니다.

차후 신규 방패/돌진 로봇 작업은 아직 `source_design_pending`이다. 현재 플레이어
외형·보행·1.8배 배율은 재제작 대상이 아니다. 조준·탄환·엄폐 공유 코드를 바꿀 때는
현재 Studio 적 지침의 cover_navigation/cover_ai/보스 보호막 및 앱 회귀 검사를
함께 사용한다. 완주 PASS를 새 원화나 Luna 재현 승인으로 확대하지 않는다.
