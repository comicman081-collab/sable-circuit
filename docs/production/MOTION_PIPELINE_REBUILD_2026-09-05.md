# SABLE CIRCUIT 이동 생성 과정 감사와 새 검증 경로

2026-09-07 사용자 정정: 아래의 실제 리그/스킨/접지 요건은 Blender에서
캐릭터 외형을 재제작하라는 허가가 아닙니다. ImageGen 원화를 보존한 움직임만
구현합니다. 새 얼굴·헤어·복장·부츠 모델링 경로는 폐쇄됐으며
`GENERATION_GATES_2026-09-07.md`의 최신 art-authority 경계가 우선합니다.

최종 프레임의 캐릭터 픽셀은 (1) 승인된 ImageGen 원화 픽셀/레이어를 그대로
변형한 결과이거나, (2) Blender/UAL 포즈 가이드를 참고해 built-in ImageGen이
새로 저작하고 동일성·복장 검수를 통과한 포즈여야 합니다. Blender/UAL에서 만든
일반 3D/VRoid 외형 렌더는 포즈 가이드일 뿐이며 atlas나 런타임 자산이 아닙니다.

상태: **검증 하네스 구축 / 기존 MICA 후보는 미완성·승격 금지**.
하네스 회귀 테스트 PASS와 캐릭터의 시각적 PASS는 서로 다른 판정입니다.
이 문서는 기존 실패 자산을 완성본으로 인정하지 않습니다.

## 1. 반복 실패의 원인

| 확인된 원인 | 실제 영향 | 새 차단 지점 |
| --- | --- | --- |
| R21은 `requested_velocity.normalized()`만 사용하고 고정 FPS로 root track을 재생 | MICA 설정은 걷기 152 / 달리기 224px/s인데 실제 E 이동은 약 14px/s, 걷기와 달리기가 동일 | 실제 월드 위치 차분과 독립 속도 계약 비교, 30/60/120Hz |
| actor가 실제 이동 후 `velocity=requested_velocity`로 덮어씀 | 로그의 152를 실제 속도로 오인 | `world_position[n]-world_position[n-1]` 재계산; 보고 velocity를 정답으로 사용하지 않음 |
| fire 전신 atlas가 정지 다리이며 root track을 초기화 | 사격 순간 약 14→152px/s로 바뀌고 다리는 미끄러짐 | 8×8 이동/조준 연사, 이동 프레임 유지와 속도 구간 검사 |
| HTML은 250px/s 및 별도 move-fire 로직 | HTML에서 확인한 동작과 Godot가 다름 | 레거시 HTML 기본 생산 차단; 같은 엔진 웹 내보내기 + 브라우저 입력 행렬 |
| R4 프레임을 R22로 그대로 재포장 | 사용자가 거절한 사각 코트 패널·분리 다리 재등장 | R4/R22 거절 경로 및 내용 SHA 색인, R22 builder 실행 차단 |
| R22 디스크 출력에 월드→픽셀 변환이 빠져 있음 | 약 0.19~0.21px/cycle, 현재 수정된 builder와 산출물도 불일치 | 빌드 입력·도구·출력 해시, 단위/속도 게이트 |
| ROOK용 화면 좌/우 분할과 직사각형 coat guard를 MICA에 적용 | 코트가 다리 레이어에 중복되고 종아리 부풀음·사각 절단 발생 | MICA 기존 cutout/warp 생산 경로 차단; 해부학적 좌우와 실제 스킨 메쉬 필수 |
| calf plane 전체가 회전하는데 manifest는 발목 고정을 주장 | 발목 90도 회전과 구현/문서 불일치 | 평가된 정점·부츠/발목·발끝 방향 관측과 원본 프레임 검수 |
| UAL Jog 이름만 남기고 stance=0.62 수제 보행곡선을 사용 | 비행 구간이 없는 걷기를 달리기로 보고 | walk/run 별 보폭·높이·접지·비행 구간 계약 |
| 같은 descriptor 총구 좌표를 정답으로 다시 비교 | 실제 총열과 떨어진 좌표도 기술 PASS | 빈 공간 socket 자동 거절 + 모든 프레임 실제 총열 끝/축 독립 관측 |
| build가 동적 검수 전에 current/descriptor를 바꿈 | HOLD 결과가 이미 사용자 런타임으로 배포됨 | immutable 후보 생성 → 별도 검수 → receipt → 마지막 원자적 pointer 교체 |

근거 코드: `scripts/animation/fast_character_runtime.gd`,
`scripts/actors/operator_actor.gd`, `tools/character_pipeline/render_fast_motion_blender_ual.py`,
`tools/character_pipeline/build_mica_r22_r4_wide_stride_candidate.py`.
구형 검사의 “root target과 일치”, “프레임 SHA가 다름”, “1080p 컨테이너”는 각각
한정된 기술 사실이며 보행 품질의 정답이 아닙니다.

## 2. 구현한 보호 장치

- `motion_contract.json`: 독립 이동 속도, 8방향, 30/60/120Hz, 보폭/키·발 높이/키,
  누적 접지 미끄럼, 종아리 폭, 발목·발끝, 몸 흔들림, 루프 연결 기준.
  수치는 초기 휴머노이드 전술 보행/달리기 기준입니다. 예술적 최종 품질을
  수치만으로 보장하지 않으며 변경 시 계약 해시와 모든 검수를 갱신합니다.
- `motion_harness.py audit`: RGBA/프레임/socket/root 단위·속도·입력 해시 검사.
  자동 검사에서 큰 오류가 없더라도 **HOLD**이며, 시각 PASS를 발행하지 않습니다.
- `character_motion_harness.gd`: 실제 OperatorActor + FastCharacterRuntime을
  공개 키/마우스 입력으로 구동합니다. `debug_drive`나 private cursor 수정은 쓰지
  않습니다. 헤드리스 마우스는 SubViewport 공개 입력으로 전달하고 실제 조준
  벡터까지 대조합니다. 루트 창에서 마우스 입력이 전달되지 않았던 초기 r2/r3
  진단의 사격 방향 수치는 무효이며 최종 행렬로 대체합니다.
- 한 주파수당 **240개**, 3개 주파수 합계 **720개** 입력 사례. 8방향 walk/run,
  각각 8×8 이동/조준 사격, 정지 사격, 시작/정지, 인접/반대 전환, 속도 변경,
  재장전, 경계와 실제 충돌을 포함합니다.
- `export_evaluated_motion_geometry.py`: 같은 Blender 실행에서 native master와
  runtime cell을 렌더하고 depsgraph의 실제 스킨 메쉬 발바닥 정점을 채집합니다.
  장면/action/frame/이미지/정점 해시를 render receipt로 결합합니다.
  IK 목표점/코드의 의도 좌표는 측정으로 받지 않습니다.
  기존 2D plane 조각은 실제 스킨 메쉬 증거를 제공할 수 없으므로 중단됩니다.
- `review-pack`은 기술/관측/HTML 증거 전체 SHA 묶음을 고정합니다. visual,
  Ponytail FULL, 기존 ChatGPT web 리뷰가 같은 후보와 같은 증거 묶음을 승인해야
  `seal`을 만들 수 있습니다. 검수 파일 교체, 다른 영상 PASS 재사용은 불가합니다.
- `build`와 `all`은 고유 후보 경로만 만듭니다. `promote-runtime`/`register`/
  레거시 `promote-motion`은 receipt 없이는 쓰기 전에 거절합니다. pointer 교체는
  검증한 원본 bytes를 임시 파일에 복사한 후 마지막에 원자적으로 수행합니다.
- `rotate_verified`, `retain_current_and_previous`는 이전 자산을 삭제하지 않고
  해시 목록을 남겨 격리합니다. 사용자의 기존 FAIL 보존 정책을 유지합니다.

## 3. 앞으로의 생성 순서

```text
ImageGen 원화/복장 승인
  → 해부학적 좌우·가려진 면·코트/다리 분리 자료 확정
  → Blender 실제 스킨 메쉬 + UAL action 리타깃
  → 월드 속도/단위/카메라/접지 계산 및 평가 정점 측정
  → E/W + N/S 최소 파일럿 검수
  → 대각선 포함 8방향 / 이동·사격 결합
  → 720사례 실제 엔진 + 같은 런타임 웹 검증
  → 실제 크기 1080p 동영상 + 원본 픽셀 + 독립 검수
  → review-pack / seal / 단일 pointer 승격
```

1. 원화와 가려진 면의 보충은 Codex built-in ImageGen만 사용합니다. 모든 채택
   파일은 프로젝트 안으로 가져와 해시 검증합니다. 로컬 diffusion/ComfyUI
   복원으로 대체하지 않습니다. 기존 원화의 어깨·복장 제한도 유지합니다.
2. 한 장의 정면 원화에 스킨 메쉬·가려진 다리 면이 이미 존재한다고 가정하지
   않습니다. 발·정강이·허벅지·코트의 소유 영역을 명시하고 중복 픽셀/잘린 면을
   숨기기 위해 crop guard를 계속 추가하지 않습니다. 이 자료가 없으면 제작 HOLD.
3. Blender+UAL은 실제 평가된 뼈/스킨 변형을 사용합니다. 코트는 별도 스킨/
   관절로 다리와 겹침 순서를 해결하고, 발목과 발은 분리해 회전 한계를 둡니다.
   UAL의 이름이나 실행 로그만으로 “UAL 모션 구현”을 승인하지 않습니다.
   기술 위상 탐색의 18 mm 접촉 대역만으로 생성 요청을 승인하지 않습니다.
   `pose_guide_visual_promotion_contract.json`에 따라 실제 지지 밑창은 고정 지면
   4 mm 이내, 같은 쪽 contact→down 평가 골반 하강은 15 mm 이상이어야 합니다.
   현재 게이트·두 계약·보정기·보정/캡처 행·실제 밑창 배열·고정 지면을 정확한
   해시로 결합하고, 수치 통과 뒤에도 visual + Ponytail FULL 검수가 필요합니다.
4. 게임 속도는 이미지 보폭에 맞추어 몰래 낮추지 않습니다. 계약을 먼저 고정하고
   `speed = cycle_distance / cycle_duration`을 만족시킵니다. 걷기/달리기는 별도
   접지·비행·관절 곡선이며, 재생 FPS만 높여 탭댄스로 만들지 않습니다.
5. root/골반 기준점과 투영 카메라를 잠급니다. 뷰를 바꿀 때 다리만 화면 축에
   맞춰 회전시키지 않습니다. 화면 y 변화를 발의 3D 높이로 오인하지 않습니다.
6. 8방향 하체 + 독립 조준 상체 또는 실제 8×8 결합 자료가 필요합니다. 하나의
   전신 8방향 atlas로 64개 움직임/조준 조합을 표현할 수 있다고 선언하지 않습니다.
   ASTER의 기존 상하체 분리 및 이동 사격 중 위상 유지 구조는 재사용 검토 대상이며,
   그 코드 자체의 시각 PASS가 MICA에 자동 상속되지는 않습니다.
7. 이동 사격 중 하체 위상·실제 속도를 유지하고, 반동은 필요한 상체 채널에만
   적용합니다. 총구 위치뿐 아니라 보이는 총열 축과 발사 방향도 검수합니다.
8. E/W 및 N/S 파일럿이 실패하면 8방향 전체를 다시 만들지 않습니다. 원인을
   한 범주로 분리해 수정한 뒤 파일럿을 재검사합니다. source/topology 오류에는
   숫자/속도/root-track 패치로 대응하지 않습니다. 실패 2회가 같은 범주라면
   동일 생성 방식을 중지하고 설계/입력자료부터 Ponytail FULL 재검토합니다.
9. 검수 대기 중에는 회귀 테스트, 원인분석, 미사용 입력 정리(삭제 아님)를
   진행할 수 있습니다. 승인 대기를 완료 선언으로 바꾸지 않습니다.

## 4. 실행 명령

PowerShell, 프로젝트 루트에서 실행합니다. `$out`은 매번 새 경로로 지정합니다.
도구가 상태를 `FAIL` 또는 `HOLD`로 판단하면 0이 아닌 종료 코드가 정상입니다.

```powershell
python tests/test_motion_harness.py
python tests/test_sable_character_pipeline.py

python tools/character_pipeline/sable_character_pipeline.py build --spec tools/character_pipeline/specs/mica_c03_fast_v1.json --candidate <새_Blender_UAL_녹색_atlas_폴더>

python tools/character_pipeline/motion_harness.py audit --descriptor <후보/runtime_descriptor.json> --out <새_진단/report.json>
python tools/character_pipeline/motion_harness.py run --descriptor <후보/runtime_descriptor.json> --godot "D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64_console.exe" --out <새_진단/engine>

python tools/character_pipeline/motion_harness.py review-pack --bundle <검수묶음.json> --out <검수요청_고정목록.json>
python tools/character_pipeline/motion_harness.py seal --bundle <독립검수까지_추가한_묶음.json> --out <receipt.json>
python tools/character_pipeline/motion_harness.py verify --receipt <receipt.json>
python tools/character_pipeline/sable_character_pipeline.py promote-runtime --spec <spec.json> --receipt <receipt.json>
```

`--hz 60`은 좁힌 디버그 실행 옵션이며 세 주파수 승격 증거를 대체하지 못합니다.
Godot는 한 번에 하나의 자식 프로세스만 사용하고 프로세스별 최대 180초입니다.
TEMP/TMP/cache/log/output을 프로젝트 안으로 지정하며, timeout/취소 시 자신이
시작한 PID만 종료합니다. 백그라운드 반복 렌더/웹 export는 시작하지 않습니다.
원본 모델/설치 도구 경로를 수정하거나 정리하지 않습니다.

## 5. 증거 데이터 계약

- 후보 폴더의 `MOTION_BUILD_INPUTS.json`: `files`는 경로→SHA, `roles`는
  `source_art`, `blender_scene`, `ual`, `generator`, `license` 각각의 정확한
  프로젝트 파일 목록. 빈 manifest, role 누락, 변경된 입력은 승격 불가.
  spec의 `motion_build_roles`로 기록합니다. 테스트용 `qa_fixture_only`는 승격 불가.
- Blender exporter config: `skinned_mesh`, `body_coordinate_frame`,
  `sole_vertex_ids: {left:[...],right:[...]}`, `subject_sha256`, `output`,
  `render_receipt`, `native_size`(기본 1920 정사각), `runtime_cell`(기본 384),
  `frames: [{frame,time_s,master_image,image},...]`. 출력은 모두 새 파일이어야 하며
  1회 최대 49프레임, CPU 렌더 스레드는 2개로 제한합니다.
  body frame은 ground root를 따라가는
  단위 스케일 직교 좌표계(x 전방/y 해부학적 왼쪽/z 위)여야 합니다.
  원본 blend는 저장/수정하지 않습니다. 출력·작업·임시 경로는 프로젝트 내부.
- `observations`: 두 완전 주기 + wrap sample, 방향/모드별 geometry ref, 실제
  atlas 프레임과 동일한 이미지, 실제 정점 기반 좌우 sole 좌표, 독립 접지,
  종아리 폭/발목/발끝/골반 관측. 모든 숫자는 코드의 IK target에서 복사하지 않습니다.
  정점 원장의 source blend도 후보 snapshot에 포함되어야 합니다.
- `visible_muzzles`: direction/state/frame마다 atlas RGBA 픽셀 SHA,
  사람이 해당 decoded frame에서 본 `visible_tip_xy`, 총열-발사 축 오차,
  원본 검수 증거 ref. descriptor socket은 이 관측치와 2 source pixels 이내여야 합니다.
- bundle: `descriptor`, `subject_sha256`, `runtime_reports`(30/60/120),
  `observations`, `visible_muzzles`, `html_parity`, `reviews`.
  파일 ref는 항상 `{path, sha256}`입니다. 각 review는 role, reviewer,
  reviewed_utc, verdict, directions, checks, subject_sha256,
  reviewed_evidence_sha256, reply_evidence를 기록합니다.
- HTML parity는 실제 브라우저 입력으로 같은 240사례를 실행한 원장과 네이티브
  1920×1080 이상 영상, 정확한 영상의 `--require-dynamic-capture` 검증 결과를
  요구합니다. 레거시 템플릿의 파일 복사/설정 PASS는 이 요건을 만족하지 않습니다.
- 추가 상태는 `idle/move/fire/run/move_fire/run_fire`만 지원하며 선언된 상태
  모두의 atlas/socket을 검사합니다. 새 표현은 어댑터·테스트 없이 추가할 수 없습니다.
  `representation: {schema:1,kind,assets:[...]}`는 실제 파일 ref와
  cell_size/frames/fps를 포함합니다. 현재 실제 소비자가 구현된 경로는
  authored_8x8입니다. independent_upper_lower는 아직 생산 어댑터가 없어
  선언만으로 사용할 수 없습니다. authored_8x8은 walk/run ×
  이동 8 × 조준 8 × firing false/true(256개)를 모두 요구합니다. 문자열만으로
  “독립 조준 지원”을 선언하는 것은 통과하지 못합니다.

### 2026-09-07 실행·접지 결합 보강

- 네이티브 행렬은 Hz당 240개, 총 720개입니다. 기존 행렬에 경계 사격,
  충돌 사격, 정지→이동/반대 조준 첫 사격, 조준 전환 사격 각 8방향을 추가했습니다.
- gait/geometry/config/paired-render는 정확한 mode/move/aim/firing 채널을
  결합합니다. 16개 기본 이동 클립으로 256개 조준·이동 조합을 승인할 수 없습니다.
- 물리 이동을 적용한 뒤 실제 변위로 위상/표시 프레임을 확정하고, 그 프레임의
  총구에서 발사합니다. 경계 충돌 직전 프레임 총구를 재사용하지 않습니다.
- 벽의 미세 recovery 변위를 실제 이동으로 오인하지 않도록 표시용 정지 기준은
  기존 12px/s입니다. 위치 원장은 수정하지 않습니다. 속도/접지 검사는 별개로
  계속 실제 변위를 사용하며, 판정자는 표시 위상·채널도 독립 계약으로 재계산합니다.
- root_translation_locked 캡처는 승인 카메라의 지면 XY 이동만 허용합니다.
  몸의 들썩임·yaw·배율·원근은 따라갈 수 없고, 실제 바닥 행렬과 카메라를 매
  프레임 결합합니다. 이미지 잘라 붙이기나 발 타깃으로 접지를 꾸미지 않습니다.
- 합성 색/총구 marker 스프라이트는 소비자 기술 회귀용입니다. 실제 보이는
  픽셀과 world transform을 검사해도 MICA 외형/걸음/실제 총열 승인은 아닙니다.

## 6. 현재 범위와 남은 제작

하네스와 차단 경로는 구현했지만 **MICA 자체의 보행/사격 수리는 완료되지 않았습니다**.
R4/R21/R22는 통과 후보가 아닙니다. source-plane 변형을 계속 재포장하지 않도록
막았으며, 다음 제작은 승인된 실제 스킨/해부학 자료를 확정하는 파일럿 단계부터입니다.
기존 실패물·검수 기록은 삭제하지 않았고 현재 플레이 가능한 descriptor도 임의 교체하지
않았습니다. 숫자 자동 검증은 원화 형태·복장·움직임 자연스러움에 대한 사람/독립 시각
판단을 대체하지 않으며, 그것을 생략한 “무오류 완성” 보고는 금지합니다.

## 7. 이번 실행 결과

- 회귀 테스트 **26개 PASS**. 후보-only build/승격 차단 연동 smoke도 PASS.
- Blender 5.2.1에서 테스트 전용 skinned sole 형상 2프레임을 실제 렌더했습니다.
  native 1920×1920 → runtime 384×384, 평가 정점 변화 및 렌더 이미지 변화,
  장면/프레임/출력 해시 결합 확인 PASS. **테스트 형상이지 MICA 완성본이 아닙니다.**
- R21 최종 엔진 테스트는 각 Hz 208사례 중 184사례에서 계약 위반을 검출했습니다.
  총 624사례이며, 같은 원인의 반복 검출을 서로 다른 버그 수로 세지 않습니다.

| 실제 E 이동 | 30Hz | 60Hz | 120Hz | 요구 |
| --- | ---: | ---: | ---: | ---: |
| 걷기 | 13.809px/s | 13.809px/s | 13.809px/s | 152px/s |
| 달리기 | 13.809px/s | 13.809px/s | 13.809px/s | 224px/s |
| 이동 사격 | 약 152px/s | 약 152px/s | 약 152px/s | 속도 유지 + 다리 계속 이동 |

이동 사격의 속도만 맞는다고 PASS가 아닙니다. 다리가 fire 정지 프레임이어서
`STATIC_LEGS_WHILE_MOVING`/`NO_TEMPORAL_LEG_FRAME_COVERAGE`로 거절됩니다.
최종 행렬에는 입력 미전달/다른 descriptor/충돌 설정 누락에 의한 하네스 오류가
남아 있지 않습니다. 이전 r1~r4/행렬 v1 진단은 디버깅 이력으로 보존합니다.

- 최종 코드/계약/자산 묶음 SHA:
  `ca6dbab898034bc8a33053505b706725cdee15bd9846ffc31ca1f54107ebe71c`
- 증거: `artifacts/motion_harness_audit/r21_engine_matrix_final/`,
  `r21_static_final.json`, `r22_static_final.json`,
  `technical_fixtures/blender_pair_v1/test_result.json`.
- Ponytail FULL: 3차 독립 코드 검토에서 핵심 회귀 차단과 최종 승인 결합 PASS.
  실제 MICA 정상 후보 전체의 종단/시각 검수는 아직 없으므로 후보 판정은 FAIL 유지.
