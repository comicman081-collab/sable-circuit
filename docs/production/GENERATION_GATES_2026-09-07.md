# 생성 전 단계부터 적용하는 SABLE 하네스

## 2026-09-07 사용자 경계 정정 — 이전 재구성 경로 폐쇄

원화 해시·라이선스·닫힌 메시 검사만으로 Blender의 외형 재제작을 허용한 것은
잘못입니다. ImageGen이 얼굴·머리·복장·부츠·무기 등 모든 원화/외형을 담당하고,
Blender·UAL은 승인 외형을 보존한 리깅·가중치·포즈·움직임 구현만 담당합니다.
원화의 작은 천/얼굴 조각을 붙인 신규 3D 캐릭터는 이 경계를 통과하지 못합니다.
최종 캐릭터 픽셀은 승인된 ImageGen 픽셀의 변형 또는 별도 승인된 ImageGen
포즈에서만 나와야 합니다. 로컬 3D/VRoid 렌더는 포즈 가이드로만 허용되며,
그 렌더 자체를 캐릭터 atlas나 런타임 자산으로 승격할 수 없습니다.

`build_mica_anatomical_candidate.py`, `run_mica_anatomical_candidate.py`와
구형 skinned pilot 두 진입점은 보존 사본을 격리한 뒤 실행 불가 상태로 바꿉니다.
`art_authority.py`는 경로/내용 은퇴 검사와 검수된 source-preserving adapter
등록 검사를 실행합니다. 같은 코드의 복사·이름 변경·diagnostic 플래그는 허가가
아닙니다. 미구현 adapter를 PASS 문자열로 등록하지 않습니다. 현재 등록 목록은
비어 있으며, 이는 아직 정상 캐릭터 생성 파이프라인이 완성되지 않았다는 뜻입니다.

구현/포니테일 검수의 `imagegen_art_preservation`은 별도 필수 항목입니다.
기존 원화는 손상되지 않았고 재생성 대상이 아닙니다. 코드 변경으로 영향받은
영수증은 새 검수로 갱신하되 과거 PASS를 고쳐 쓰지 않습니다. 이전 문서의
‘실제 스킨 메시’ 요구가 임의 얼굴/복장/부츠 제작 권한을 뜻하지 않습니다.
VRoid/CC0 몸도 동작 기준체로만 사용하며 그 외형을 MICA로 대체하지 않습니다.

현재 범위: **생성·승인·검증 경로 보강**. MICA 캐릭터 완성/시각 PASS를 뜻하지 않습니다.
ImageGen의 첫 출력이 항상 정확할 수는 없습니다. 이 하네스는 불량·미검수 출력이
메시, 여러 방향, 애니메이션, 사용자 런타임으로 증식하지 못하게 하는 장치입니다.

## 고정 실행 경로

```text
요청/원화 규격 → 1회 생성 예약 → 원화 1장
  → 실제 크기/방향/부위 마스크 검사 → 시각 + Ponytail FULL 승인
  → 정확한 제작 코드·라이선스·입출력 계획 검수 → 1회 실행 예약/소비
  → 실제 스킨 메시 검사 → 해당 방향 첫 포즈 1회
  → 원본 1080p 이상 시각 + Ponytail FULL 승인
  → 해당 방향의 한정 동작 클립 → 기존 보행/런타임 하네스
  → 8방향/8×8 조준·이동/30·60·120Hz/HTML/총구 검증
  → 전체 시각·Ponytail·기존 ChatGPT web 검수 → 정확한 후보만 승격
```

모델이 다음 단계를 추측하지 않도록 job JSON과 `next` 명령을 사용합니다.

```powershell
python tools/character_pipeline/generation_harness.py next --input JOB_JSON
```

`allowed_next_action`만 수행합니다. 각 산출물은 새 경로에 저장하고 실제 해시를
새 job revision에 기록합니다. 해시만 새 값으로 고쳐 과거 PASS를 재사용하면 안 됩니다.
스키마·실행 예시는 프로젝트 스킬의 `references/job-format.md`를 따릅니다.

## 새로 막는 오류

| 문제 | 실제 검사/차단 위치 |
| --- | --- |
| 새 builder를 예전 원화 승인에 몰래 추가 | 별도 build-plan subject/구현·Ponytail 검수, 원래 permit 보존 |
| 기존 mesh 파일이 있다고 제작 계획을 생략 | next 및 실제 pose construction에서 plan/receipt/claim 필수 |
| 승인하지 않은 폴더·텍스처로 첫 모델을 생성 | 실제 blend/collector/image/기록 출력 경계 및 소비 이미지 해시 검사 |
| 실패한 동일 제작 예약으로 계속 재실행 | runner·Blender child 각각 원자적 1회 claim; 실패한 예약은 사용 완료 |
| 요청한 해상도만 믿고 941px 원화를 확대 | 반환 파일 디코딩, 실제 캔버스와 피사체 높이 |
| 체크무늬 RGB를 투명 PNG라고 보고 | 실제 alpha 0/255, 테두리, 불투명 재질 마스크 검사 + 원본 크기 명암 배경 검수 |
| 총만 옆이고 골반/발은 정면 | 전체 방향, 골반·어깨·양쪽 발 방향의 source contract + 독립 시각 검수 |
| 코트에 손 복사, 종아리 팽창, 초록 띠 | 승인된 부위별 마스크, 제외 부위, 실제 per-face/per-loop UV 내부 및 필터 범위 |
| 숨겨진 가짜 발로 측정 | 실제 render-enabled Armature, 가중치, 얼굴/정점 연결, 발바닥 정점 |
| 파이프형 몸, 열린 허리, 뒤집힌 코트 | 해부학 메시의 체적·폐쇄성·가중치·경계 연결, 코트 면 방향 |
| 승인 이미지를 미끼 노드로 넣고 다른 재질 출력 | active Material Output의 실제 연결 경로, 미지원 node group/변환 거절 |
| 첫 포즈 승인 후 메모리에서 메시/재질 교체 | 정확한 승인 `.blend` 재로드 + 실제 메시 재검사 |
| 테스트 플래그 문자열로 검사 회피 | 실제 bool만 허용, 모든 fixture 출력 경로를 테스트 전용 영역으로 제한 |
| 다른 좌표계를 써 보폭/높이 수치 왜곡 | 해부학 좌표축·바닥 원점·좌표계 이름과 실제 행렬 고정 |
| 애니메이션 도중 카메라 방향/배율 변경 | 프레임마다 렌더 전 camera transform/projection 검사 |
| 일부 출력만 생긴 타임아웃을 완료 처리 | 소유 프로세스 종료 + 필요한 파일 디코딩/해시/영수증 검증 후 원자적 완료 기록 |
| source/pose PASS만으로 런타임 덮어쓰기 | 8개 방향 승인 해시 체인을 motion build/promotion에 필수 연결 |

사람 같은 외형, 실제 손 중복, 복장 동일성은 숫자로 완전히 판별할 수 없습니다.
기술 검사만 깨끗하면 HOLD이며 독립 검수 전에는 source/pose 승인서를 만들지 않습니다.
수치 임계값을 낮추거나 프로덕션을 synthetic fixture로 표시하는 것은 수정이 아닙니다.

## 국소 ImageGen 수리 실행 경계 (2026-09-08)

R3 실측에서 프롬프트의 `immutable`/절대 좌표 문구는 실제 공간 제약이 아니었고,
허용 영역 밖 공통 피사체 픽셀의 50% 이상이 다시 합성되었습니다. 따라서 참조
마스크를 한 장 더 보여주는 것만으로 국소 편집을 증명하지 않습니다.

`finalize_reviewed_visible_frame_repair_request.py`는 이제 정확한
`imagegen_repair_execution_contract.json`, 대상과 같은 해상도의 비어 있지 않은
이진 마스크, 선택한 생성기의 실제 hard-mask 소비, 마스크 밖 byte 불변성 및
독립 구현/Ponytail FULL 검수를 요구합니다. 현재 내장 ImageGen 편집 호출은 이
hard-mask 인터페이스가 입증되지 않았으므로 같은 prompt-only 수리를 예약할 수
없습니다. 이는 ImageGen 원화 권한을 Blender로 넘기는 예외가 아닙니다.

Blender+UAL 진단 파일에서는 `extract_vrm_ual_projected_joints.py`로 관절/접지
좌표만 추출할 수 있습니다. 출력 JSON에는 캐릭터 픽셀이 없으며, 승인된
ImageGen 픽셀을 보존하는 motion adapter의 입력일 뿐입니다. 좌표 추출 성공은
그 adapter나 보행/런타임/외형의 PASS가 아닙니다.

## 투명 원본 허용 — 실제 결과가 조건을 통과해야 함 (2026-09-07)

사용자는 깨끗하게 분리된다면 초록 배경 없이 ImageGen 투명 원본만 사용하는
것을 허용했습니다. 요청의 `background: transparent_alpha`를 지원하며 원본
알파를 그대로 보존합니다. 진짜 투명 픽셀, 불투명 피사체, 빈 테두리와 부위별
마스크를 검사한 뒤 `clean_subject_separation`을 독립 검수합니다. 밝고 어두운
배경에서 머리카락·손끝·옷·부츠 윤곽, 색 테두리와 내부 구멍을 실제로 봅니다.

현재 built-in 도구의 1회 실측은 **FAIL**입니다. 투명을 명시했지만 실제 반환은
1024×1536 RGB, 투명 픽셀 0개인 체크무늬 그림이었습니다. 공식 API의 투명
지원과 현재 내장 도구의 실제 반환을 혼동하지 않습니다. 다른 API로 바꾸거나
동일 실패를 반복 생성하지 않고 현재 좋은 초록 원본으로 제작을 계속합니다.
증거는 `artifacts/quarantine/generation_diagnostics/mica_native_alpha_probe_r1/`에
보존했습니다. 추후 실제 RGBA와 윤곽 검수가 통과하면 초록 중간본은 불필요합니다.

## 5.6 Luna용 재사용 스킬

사용자 지정 순서: **Astra에서 실제 생성·구현·필수 검수를 먼저 성공 → 성공한
절차를 하네스/스킬에 고정 → Luna로 재현 테스트**. 이 선행 조건이 충족되기
전에는 Luna 생성 및 추가 forward test를 진행하지 않습니다. 이미 수행한
읽기 전용 3사례 단계 판단 검사는 생성 성공이나 제작 능력 검증이 아닙니다.

프로젝트 `.agents/skills/sable-motion-production/SKILL.md`에 자동 발견 가능한
스킬을 작성했습니다. 핵심 동작은 장황한 자유 프롬프트 대신 job/계약/CLI로 고정합니다.

- 어디서 재개하는지: job + `next`.
- 어떤 입력을 쓰는지: 실제 파일 SHA, source/geometry authority.
- 무엇을 수정하는지: 실패 범주별 원화/UV/메시/동작/런타임 소유 구분.
- 언제 멈추는지: HOLD/FAIL, 미확인 라이선스, 동일 실패 2회.
- 무엇으로 완료를 증명하는지: 서로 독립적인 generation, motion, 시각, runtime 증거.

스킬 형식 검사와 제한된 forward test는 전체 캐릭터 제작 성공의 증거가 아닙니다.
Luna로 실제 원화→VRM/메시→UAL→8방향 런타임 배치를 완성하기 전에는 그 성공을
보고하지 않습니다. 품질 기준은 모델에 따라 낮아지지 않습니다.

## VRoid 선택 경로

VRoid Studio 2.14.0과 Blender 5.2용 VRM add-on 4.6.0 설치를 읽기 전용으로
확인했습니다. 기존 인체를 수제 실린더/다리 이미지 조각으로 만드는 대신,
라이선스가 확인된 실제 humanoid mesh/skin을 받는 **선택 경로**로 사용합니다.
설치 확인만으로 MICA의 비율/복장/UAL 리타깃이 통과했다고 보지 않습니다.

```powershell
python tools/character_pipeline/inspect_vrm_source.py --input PROJECT_MODEL_VRM --license EXACT_MODEL_LICENSE_JSON --out FRESH_INTAKE_REPORT
```

GLB의 실제 positions/joints/weights, humanoid bone 역할, 외부 파일 참조 및
상업/수정/게임 렌더 배포 근거를 먼저 검사합니다. 깨끗해도
`HOLD_BLENDER_RETARGET_AND_VISUAL_REVIEW`입니다. 기본 VRoid 재질을 ImageGen
원화로 가장하지 않습니다. MToon 변환은 별도 검증된 adapter가 필요합니다.

일반 상업 이용 안내와 개별 모델 허가는 다릅니다. 공식 근거와 설치 정보는
`tools/licenses/vroid_studio/INSTALLED_TOOL_REVIEW.json`에 기록합니다.
사용자가 허용한 외부 모델 다운로드는 프로젝트 안에 저장하고, 사용할 정확한
모델/모든 포함 아이템의 허가를 먼저 확인합니다. 모델 생성 서비스 자체를 외부에
배포하는 권한은 이 내부 제작 파이프라인 허가에서 추정하지 않습니다.

실제 Astra 시험에서 공식 `Seed-san.vrm`을 가져왔습니다. 상업/수정 허가는
`third_party/vrm/seed_san/MODEL_LICENSE.json`에 기록했고 출처 표기가 필요합니다.
리그 입력 시험은 `seed_san_import_astra_r2`에서 완료했으며, 51개 휴머노이드
역할과 5개 스킨 메시를 확인했습니다. 장식/로봇 팔이 포함된 모델이므로 MICA의
외형이나 복장을 그대로 대체하지 않습니다. 원본 모델·설치 애드온은 변경하지 않았습니다.

`seed_san_ual_astra_r3`는 UAL 걷기를 실제 메시로 리타깃한 **진단 파일럿**입니다.
좌우 각 54개 발 정점의 베이크 재생을 채집했고, r2의 1.333→1초 시간 압축을
r3에서 1.333→1.333초로 수정했습니다. 모델의 실제 발 변형 확인과 MICA의
지면 접지·속도·8방향·사격 승인 사이에는 아직 제작/검수 단계가 남아 있습니다.
진단 한 주기를 반복 재생한 영상은 두 독립 주기/런타임 검증을 대신하지 않습니다.

재현 명령과 결과는
`artifacts/generation_harness_audit/ASTRA_FIRST_PRODUCTION_STATUS.md`에 기록합니다.
**Luna 재현 시험은 아직 허용되지 않습니다.**

## 검증 명령

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONPYCACHEPREFIX=(Join-Path (Get-Location) 'artifacts/generation_harness_audit/cache')
python tests/test_generation_harness.py
python tests/test_motion_harness.py
python tests/test_sable_character_pipeline.py
python tests/run_generation_blender_smoke.py
```

마지막 명령은 최대 120초의 소유 Blender 프로세스 하나만 실행합니다. 합성 도형
회귀 시험이며 캐릭터 렌더/완성 증거가 아닙니다. installed original tool/model 파일은
바꾸지 않고 출력·TEMP·캐시·로그를 프로젝트로 제한합니다.

## 현재 생산 상태

기존 `pilot_01/02/03`의 초록색 재질, 가짜 손, 열린 연결 등은 실패 사례입니다.
생산 원화/메시 검사를 갖추지 않은 실험 builder는 새 하네스에서 막힙니다.
현재 runtime pointer와 프로필은 이번 보강 때문에 바뀌지 않습니다.
검수 실패 자산은 삭제하지 않고 격리 및 경로/해시 이력을 보존합니다.
