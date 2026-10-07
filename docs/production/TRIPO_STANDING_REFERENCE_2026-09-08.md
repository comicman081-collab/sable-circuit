# Tripo 스탠딩 리그·달리기 입력팩

사용자가 `세이블 서킷 코덱스 전달` 대화에 첨부한
`fantasy+spear+warrior+3d+model_Run.glb`를 원본 바이트 그대로 보존했다.
SHA-256: `253912742fa69261bd34ac44cf18cdde38a6a4dcc4ce17ccd0560942509c352b`.
유료 플랜 생성물이라는 사용자 설명과 공식 이용 조건을 해당 원본의 라이선스
manifest에 결합했다. 새로운 Tripo 생성/API나 외부 추론 모델은 사용하지 않았다.

현재 기준팩: `art_src/motion_reference/tripo_run_20260908/pack_r03/`.

- `STANDING_BODY_PACK.blend`: 스탠딩 기준 액션이 활성화된 재사용 팩.
  Action Editor/Asset Browser에서 원본 `preset:biped:run.001`로 전환 가능.
- `RUN_REFERENCE.blend`: 원본 달리기가 활성화된 장면, 24fps, 프레임 1~31.
- `SOURCE_RUN.blend`: 단위 변환 전의 원본 가져오기 장면.
- `HUMANOID_MAP.json`: 휴머노이드 역할, 부모·REST 행렬·좌표.
- `RUN_GEOMETRY.json`: 실제 메시의 좌우 밑창 정점 10/14개와 49개 시간 샘플.
- `CALIBRATOR_INPUT.json`: 기존 접지 진단기로 전달하는 장면·매핑 입력.

GLB 자체에 스탠딩 기본 포즈가 있어 새 인체 표면을 만들지 않았다. 새 액션은
기존 bind 상태를 재현한다. 스켈레톤 rebind나 얼굴·복장·신발·무기·UV·
가중치·텍스처 재제작은 없다. 비교용 1.70m는 한 번 적용한 단위 규약이며
실제 신장을 확인했다는 뜻이 아니다. 팩은 원본 복장과 무기를 포함한다.

`SABLE_MOTION_INPUT_R2.json`은 관절 샘플을 8방향 기하 좌표로 연결하고
기존 모션 계약의 ASTER 250, ROOK 205, MICA 224px/s를 결합한다. 소스 1.25초
구간에 요구되는 게임 이동량은 각각 312.5, 256.25, 280px다. 이것은 요구사항이며
SABLE 캐릭터가 실제로 그 속도·보폭을 만족했다는 검증 결과가 아니다.

검증된 기술 범위:

- 스킨 메시 26,588정점, 41개 본, 123개 애니메이션 채널.
- 원본 키 타이밍 1~31프레임/24Hz, 1.25초 보존.
- 저장된 3개 Blender 파일을 다시 열어 Run 키, 메시·UV·가중치와 packed texture
  바이트가 동일함을 검사했다. 저장된 Run 장면의 49개 밑창 샘플이 재현된다.
- 소비된 Blender child 예약 재사용은 가져오기 전에 거절된다.
- 라이선스·스킨·시간·외부 팩 참조·child claim 관련 회귀 11개 통과.
- 독립 Ponytail FULL 검수는 기준팩 구현 범위만 승인했다.

접지와 세이블 캐릭터 적용은 아직 HOLD다. 기본 REST 밑창 높이가 약 32.39mm
다르며 Run 최저 밑창도 고정 바닥 위 약 9.97mm/40.32mm다. Root는 정지하고
Hip이 약 4.92m 이동한다. 이 구간을 제자리 한 주기로 취급한 wrap/위상 검사는
적용 범위가 맞지 않는다. 그 결과를 모델 자체의 무효 판정으로 과장하지 않는다.
골반 이동·주기 분할·발축·고정 접지를 구분해 보정/검수해야 한다.

후속 작업은 이 리그/원본 동작으로 source-preserving 모션 어댑터의 기하 입력을
구현하는 것이다. ImageGen 외형 권한, 4mm 지지 밑창/15mm down 기준, 1080p
검수, 8×8 사격 및 30/60/120Hz 런타임 검증을 유지한다. Blender 렌더를 SABLE
visible atlas로 사용하거나 retired MICA builder를 복구하지 않는다.
현재 실행 경로와 다음 단계는 `motion_reference_job_r01.json`으로 재개한다.
