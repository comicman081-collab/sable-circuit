# MICA C03 V5 R16 검수 결과와 다음 수정 기준

검수일: 2026-09-05  
대상: `candidate_r14_r8c_unique_move_qa`  
상태: **FAIL_NOT_PROMOTABLE / QUARANTINE_PRESERVE**

## 확인된 사실

- Ponytail FULL이 native 1920×1080, 24fps, 384프레임(8방향×48프레임)을 실제 디코드하여 판정했다.
- 각 방향의 24개 셀은 모두 고유하고 `F00..F23`가 두 사이클 재생된다. 포즈 래스터의 중복 바디, 종아리 팽창, 90도 발목, 초록 잔여, 알파/z-order 파손은 확인되지 않았다.
- 그러나 전 방향에서 지지발이 배경에 고정되는 구간이 0회다. 두 sole track의 전진량은 방향별로 약 1.83–11.59px/frame 범위이며, 실제 지지발도 계속 이동한다.
- root ledger는 모든 방향에서 `7.600px → 5.066px → 7.600px → 5.066px`를 반복한다. 프레임은 진행하지만 일정한 24fps 속도가 아니므로 strict cadence가 아니다.
- `F23→F00` 래스터 wrap은 약 5.066–5.067px로 연속적이지만, 이것만으로 지지발 고정이나 실제 전진을 증명할 수 없다.
- 캡처 경로는 `StoryStage01 → OperatorActor.debug_drive → FastCharacterRuntime → descriptor override → candidate move atlas`이며, 실제 production registry는 여전히 `current` atlas를 가리킨다. 캡처는 충돌 비활성화·고정 카메라·2.6배 검수 스케일인 capture-only 조건이다.

## 원인

현재 R16은 `24개 고유 셀`과 `root factor 1.0`을 맞췄지만, authored lower-body stride가 실제 이동 속도에 비해 너무 작다. 화면상 지지발 이동량은 sprite displacement와 world root displacement가 함께 더해져 누적된다. 따라서 단순히 셀을 고유하게 만들거나 root factor를 1.0으로 고정하는 것만으로는 보행이 되지 않는다. 또한 `samples_per_pose`/스케줄러 경계가 실제 24fps에서 두 단계 root step을 만들어 cadence가 교대한다.

## 다음 후보의 필수 계약

1. ImageGen 원화는 중립·양발 접지 상태를 authority로 유지하고, 걷기 stride를 원화에 선인쇄하지 않는다.
2. Blender+UAL에서 방향별 hip/knee/ankle/toe landmark를 사용해 좌우 지지발을 명시한다. 지지발은 stance 구간의 world sole residual이 0–1px(검수 스케일 기준)이어야 한다.
3. 한 사이클의 root advance와 authored foot travel을 먼저 계산하여 실제 ground speed를 충족시킨다. 불충분한 stride를 유지한 채 actor velocity만 높이지 않는다.
4. 24fps 각 프레임의 root step은 일정해야 하며, 7.600/5.066 같은 교대 스텝이나 zero-step을 허용하지 않는다.
5. 8방향 각각에 대해 native 1920×1080 동적 캡처와 원본 셀 대조를 다시 수행한다. 고정 카메라·충돌 비활성화 캡처는 기술 진단으로만 기록한다.
6. 새 후보는 별도 project-local 디렉터리에 만들고, R16과 모든 이전 FAIL/HOLD 자산은 quarantine에 유지한다. Ponytail FULL 및 기존 ChatGPT 웹 검수, runtime/pointer/technical 게이트가 모두 PASS하기 전에는 승격·삭제하지 않는다.

## 현재 처분

R16은 폐기하지 않는다. 후보 manifest, MP4, PNG 프레임, HTML fallback, 정적/동적 validator 결과, 본 분석 문서를 함께 보존한다. 완료 replacement와 retirement manifest가 생기기 전까지 삭제 금지다.
