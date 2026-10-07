# 2026-09-12 — 개선 사항의 하네스·스킬 반영

요청 범위인 재사용 시스템 업데이트를 완료했다. 새 캐릭터 생성, Luna 모델 실행, 운영 캐릭터 교체, 배포, 원본 삭제는 하지 않았다. `sable-character-studio`로 기존 작업 경로를 유지하고 `skill-creator` 기준으로 실행 가능한 보조 도구·검사와 필요한 인계 설명을 추가했다.

## 바뀐 동작

- `character_workflow.py handoff --character ID`: 실제 참조·레시피·현재 거절/누락 슬롯·다음 명령과 의존 파일 해시를 저장한다. `verify-handoff --packet PATH`는 내용과 현재 상태를 재계산한다. 코드, 텍스처, 원화, 검토 증거, 누락 파일의 신규 추가, 승인/실행 주장 변조를 거부한다.
- `status`와 인계는 실제 `repair` 슬롯을 미생성 슬롯보다 먼저 처리한다. ROOK는 `E/walk/0`을 우선하며, MICA는 기존 런타임 검증으로 안내한다. 다른 캐릭터의 거절 방향도 해당 방향의 preview 명령으로 전달한다.
- `compact_atlas.py pack/verify`: R3의 중복 제거를 캐릭터명·384px 상수에 묶이지 않는 공용 로컬 도구로 추출했다. 지원 범위는 명시적 FastRuntime 수직 RGBA 아틀라스다. 새 원화용 Motion Studio 컴파일러를 이것으로 교체하지 않는다. 출력은 새 `qa/` 후보 폴더로 제한하고 원본과 이전 결과를 덮어쓰지 않는다.
- `verify-improvements`: 고정된 R3 실제 근거, 입력 해시, 원본 픽셀/타이밍, 선언된 3회 성능 데이터를 다시 검사한다. 이동 사격 셀 동기화·정지 반동 보존·첫 로드 전 후보 선택·독점 실행기의 재사용 위치를 안내하지만 R3의 성능 FAIL/원화 HOLD는 유지한다. 새로운 게임 실행을 했다고 기록하지 않는다.
- 프로젝트 내 스킬, authoring 절차, Motion Studio AGENTS 및 README를 같은 명령으로 연결했다. 외형 변형, 무기 규칙의 무단 상속, 가짜 alpha, 안내용 가이드 색 복사, 보행/사격 위상 혼동에 대한 실제 실패 교훈을 포함한다.

## 실제 검증

| 항목 | 결과 | 범위 |
|---|---|---|
| Python 전체 회귀 검사 | 39/39 통과 | 신규 16개 포함, 기술 fixture |
| 기존 JS 전체 회귀 검사 | 28/28 통과 | 입력·조준·선택 프레임·거리 위상·충돌 등의 코드 검사 |
| 공용 도구로 실제 ROOK 재패킹 | 272/272 셀 RGBA·순서·시간 일치 | 새 원화 생성 아님 |
| 생성 PNG와 이전 R3 PNG 비교 | 8/8 SHA-256 일치 | 경로가 다른 새 명시적 manifest 사용 |
| R3 성능 판정 재계산 | FAIL 유지, p95 비율 1.1061643835616437 | 더 좋은 반복으로 바꾸지 않음 |
| 실제 ROOK·MICA 인계 패킷 생성/확인 | CURRENT_HANDOFF | 캐릭터 완성/모델 실행 주장이 아님 |
| 이전 패킷으로 코드 변경 후 검증 | NEEDS_FIX, 종료 코드 1 | stale `character_handoff.py` 실제 감지 |
| 스킬 검증기 | `Skill is valid!` | 구문/구조, 모델 제작 성능 검증 아님 |
| 기존 보호 원본 | 56/56 해시 동일 | 운영 포인터/원화 교체 없음 |

실행한 명령은 `python -B -m unittest discover -s tests -p 'test_*.py'`, `node --test tests/*.test.js`, 공용 `compact_atlas.py pack/verify`, `character_workflow.py verify-improvements`, `handoff`, `verify-handoff` 및 skill-creator의 `quick_validate.py`다. 설치된 Python/Node 환경은 변경하지 않았다. TEMP/TMP와 fixture/출력은 프로젝트 아래다. Git diff whitespace 검사도 종료 코드 0이었다.

## 현재 인계

- [Luna가 따라갈 공통 절차](<D:/AI 종합 폴더/Games/Sable-circuit/.agents/skills/sable-character-studio/references/reuse-improvements.md>)
- [ROOK 현재 패킷](<D:/AI 종합 폴더/Games/Sable-circuit/motion_lab_v1/qa/harness_upgrade_20260912/rook_handoff_current.json>)
- [MICA 기존 런타임 패킷](<D:/AI 종합 폴더/Games/Sable-circuit/motion_lab_v1/qa/harness_upgrade_20260912/mica_handoff_current.json>)
- [실제 R3 재사용 검증 결과](<D:/AI 종합 폴더/Games/Sable-circuit/motion_lab_v1/qa/harness_upgrade_20260912/r3_verified_reuse_current.json>)
- [공용 도구의 실제 재패킹 결과](<D:/AI 종합 폴더/Games/Sable-circuit/motion_lab_v1/qa/harness_upgrade_20260912/atlas_repack/manifest.json>)

`rook_handoff.json`과 `mica_handoff.json`은 이번 개발 중 이전 코드의 패킷이며 남겨둔 stale 증거다. 위 `_current` 파일을 먼저 검증하고 사용한다. 이후 어떤 관련 입력이 바뀌면 이 파일들도 재생성해야 한다. 한 번 검증한 패킷을 영구 승인으로 사용하지 않는다.

현재 ROOK 패킷은 레시피의 24발/.11초/1.25초 값이 실제 게임의 10발/.42초/1.38초와 다르다는 점을 읽어 경고한다. 제작 scaffold와 실제 산탄총 규칙을 구분하며 값을 운영에 자동 덮어쓰지 않는다.

남은 제한: 신규 ROOK 7/56 원화의 시각 HOLD와 기존 R3 성능 FAIL은 해결된 것이 아니다. Luna의 실제 캐릭터 생성/시각 완성/게임 전달 시험은 미실행이다. 이번 결과는 **Luna가 동일 도구와 검사를 따라 재개할 수 있는 실행 체계가 준비되었다는 것**이지, 예술 품질이나 무실패 생성을 보장한다는 뜻이 아니다.
