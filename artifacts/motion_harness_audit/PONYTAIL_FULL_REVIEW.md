# Ponytail FULL 독립 검토 기록

검토자: 현재 작업의 `/root/ponytail_motion_audit` (`ponytail_full` 전용 에이전트).
방식: 읽기 전용 독립 코드/자산 감사. 이 기록은 에이전트 응답의 요약이며,
외부 ChatGPT web 검수나 캐릭터의 시각 PASS를 대신하지 않습니다.

1차 원인 감사: 고정 FPS/속도 크기 누락, velocity 자기신고, fire 하체 정지,
HTML/Godot 비동일성, R4→R22 거절 프레임 재포장, 단위/산출물 불일치,
2D crop/warp의 코트·종아리/발목 결함, 자기참조 QA 및 검수 전 승격을 확인.

1차 하네스 검토: HOLD. frame_positions 키, 독립 속도 정답, 세부 입력 행렬,
브라우저 증거 해시, 빈 build provenance, 누적 미끄럼, 실제 정점 연결,
승격 전 bytes 검증 등 수정 요구. 모두 반영 및 부정 테스트 추가.

2차 검토: 핵심 회귀 차단 검토 통과, 최종 승인 결합 보완 필요.
실행 보고서의 actor/path/subject 직접 연결, 같은 렌더/mesh 생성 관계,
추가 state 및 upper/lower/8×8 실제 자산 목록 결합을 요구.

3차 최종 응답 요지:

> 요청하신 마지막 3항목 수정은 코드 검토 PASS입니다.

subject·actor·descriptor 직접 결합, 같은 Blender 실행의 렌더/평가 정점과
장면·프레임·이미지·geometry 해시 대조, 실제 추가 상태/표현의 전 자산 검사,
미지원 상태 차단을 확인했습니다. 홀수 ticks 전환 시점과 충돌벽 SubViewport
수정도 확인했으며 검토 범위의 중요한 승인 우회를 추가 발견하지 않았습니다.

판정: **하네스 정적 독립 리뷰 PASS**. 기존 R4/R22와 R21 후보는
**FAIL·승격 불가**. 정상 MICA 후보 전체의 실제 종단/시각 검증은 별도 필요.

검토 후 실제 실행은 주 에이전트가 수행했습니다: 회귀 26개,
Blender paired-render/evaluated-vertex 합성 fixture, 624개 Godot 입력 사례.
실행 증거는 같은 디렉터리의 최종 report 및 engine matrix에 보존했습니다.
