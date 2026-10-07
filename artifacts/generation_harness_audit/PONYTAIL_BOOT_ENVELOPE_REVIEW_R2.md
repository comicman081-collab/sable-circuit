# Ponytail FULL — actual boot envelope mechanism R2

검수자: `/root/ponytail_motion_audit` (독립 Ponytail FULL)

실제 검수 시각: **2026-09-07 12:39:25 UTC / 21:39:25 KST** (시계 도구 확인).
판정: **PASS_LIMITED_GEOMETRY_MECHANISM_ONLY**. 이는 정확한 다음 제작 계획을 검토할 근거이며, 제작 실행 예약·첫 포즈·외형·보행 승인이 아닙니다.

## 실제로 읽고 대조한 증거

- `anatomical_boot_envelope.py`: `df0c658ebba7a743f610faf2d7a7bf4f1933140e2d8d3e37a09b724d19db8789`
- `mesh_surface_orientation.py`: `730cf302bfd53c651a7e905bac9ad3c23dca0a6a843379c69a3e66e1bf97a362`
- `triangle_surface_checks.py`: `2361d5d3839832a92a18409e7bd02b78f0f304357dba60a8a0a7cf38c483e62a`
- `mica_boot_envelope_adapter_r6/VOLUME_DIAGNOSTIC.json`: `c80eece8fe32cfad788199be1e73d522d0856097e3d03c334f8297a152833d82` 및 같은 폴더의 완료 영수증.
- `boot_enclosure_unit_r4/results.json`: `d9c3b77877db13dd25020e1ad12ff389b2679f33ee85991d29318287d2ad9220`.

두 증거 폴더는 `artifacts/quarantine/generation_diagnostics/` 아래입니다. R6 원장에 기록된 원본 rig, builder, diagnostic 및 세 helper의 해시와 현재 파일을 대조했습니다. `production_ready:false`, `rendered:false`를 유지하고 있습니다. 실제 caller인 `build_mica_anatomical_candidate.py:253–268`과 `diagnose_boot_volume_envelope.py:54–70`, 9개 Python 단위 테스트의 코드 및 실제 Blender BVH 6사례 테스트 코드도 읽었습니다. 이번 검수자가 Blender·렌더·테스트를 다시 실행하지는 않았습니다.

## 원인과 수정 판정

기존 R2의 cuff 후 오른쪽 외피 뒤집힘은 전역 winding 문제였고, 원래 발가락의 국소 접힘은 9mm 법선 offset으로 악화되었습니다. 전체 component 방향만 뒤집는 것으로 국소 자기 교차가 해결되지는 않습니다. 새 helper는 원본 인체를 수정하지 않고, 별도 부츠에만 3mm voxel remesh를 적용하며 `preserve_volume=False`로 접힌 원래 표면에 재투영하지 않습니다.

R5의 실제 로그는 `AMBIGUOUS_CLOSED_SHELL_RAY_PARITY`로 중단됐으며 완료 원장이 없습니다. 이를 PASS로 재해석하지 않았습니다. 현재 helper는 ray 출발점 전진을 명시된 1e-5m 수치 공차로 하고, 1e-6m 미만 재충돌·edge hit를 여전히 모호한 ray로 처리합니다. 2개 이상의 비모호한 결과가 모두 일치해야 하며 불일치는 예외입니다. 현재 해시로 수행된 실제 cube 검사는 내부, 외부 모서리, 표면 양쪽 및 boundary 6사례가 각각 예상 분류와 일치합니다. 이 테스트는 임의 복잡도/임의 스케일 메시 전체에 대한 수학적 보증이 아닙니다.

## R6 원장에서 독립 확인한 값

| 검사 | 실제 확인 | 판정 범위 |
| --- | --- | --- |
| 외피 | 60,842 정점, 60,838 면, 닫힌 두 component, 양의 체적 0.00436770336 / 0.00433330920m³ | 정지 제작 외피 기하 PASS |
| 교차/퇴화/접힘 | vertex incidence를 별도 열거한 shared-boundary 후보 761,555쌍 검사, 교차 0, folded triangle 0. 별도 BVH 비인접 후보는 0 | 단순히 adjacency를 제외한 검사가 아님. 모든 삼각형 퇴화 검사도 별도 실행 |
| 실제 원본 내부 포함 | source vertex 2,860개, 좌우 각 1,430개, 모두 세 ray `(1,1,1)`, outside 0, boundary 0 | z<0.40m의 실제 source **정점** 범위; cuff·전체 triangle 내부·동작 전 주기를 승인하지 않음 |
| 표면 간 거리 | 내부 source 정점의 최근접 거리 6.856–15.205mm, 새 외피의 body 최근접 최대 10.106mm | 1e-5m boundary 예외로 실제 발을 통과시키지 않음 |
| 분리 microcell 제거 | 정확히 7개, 각 8정점/6면. 최대 축 0.994414mm, 최대 절대 체적 1.95931e-10m³. 56정점/42면만 제거하고 각 좌표·면·ID·체적 보존 | 두 주 외피/원본 자산 삭제 아님 |
| 새 정점 provenance | 60,842개 transfer가 ID 0..60841 전체를 중복 없이 포함. 실제 source triangle 및 3개 source ID·barycentric 기록 | 이전 offset sole/source ID를 새 topology에 재사용하지 않음 |
| weight 전달 | barycentric 0..1, 최대 합 오차 1.37836e-7. 정규화 skin row 합 오차 2.22045e-16, 빈 row 0, 미존재 bone 0 | 두 오차는 서로 다른 값. skin row 수치이지 최종 evaluated 동작 검증이 아님 |

현재 코드의 실제 부츠 path는 **최종 외피 생성 → 실제 body triangle에서 weights 전달 → Armature skin 적용 → 새 외피의 아래 방향 면/최저점으로 sole 재선정**입니다. 원래 바닥 정점을 평탄화하거나 숨겨진 내부 면을 접지 정점으로 대체하지 않습니다. `closed_component_orientation`의 폐쇄·일관된 winding·체적 검사, 모든 triangle의 퇴화/접힘 검사, shared point를 넘어가는 교차 검사에서 이번 범위의 추가 실행 전 P1은 발견하지 못했습니다.

## 남은 범위와 금지되는 확대 해석

- R6의 `skin` 통계는 전달 row를 측정합니다. 저장 후 재로드된 최종 Blender vertex group·evaluated sole·실제 영상 전 주기 검사를 대신하지 않습니다.
- 0.40m 이상 cuff cap의 최대 최근접 거리는 47.942mm이며 명시된 별도 cap 범위입니다. 이를 전체 부츠 외피 오차 10.106mm와 혼동하지 않습니다.
- 내부 검사는 실제 source 정점 검사입니다. 모든 source 삼각형 내부 및 움직이는 신체/의복의 충돌 없음까지 증명했다고 말할 수 없습니다.
- 다음은 현재 코드·source·범위를 묶은 새 build plan 승인과 새 1회 예약을 거친 S 중립 한 장의 실제 construction입니다. 이번 보고서만으로 직접 실행하거나 과거 실패 예약을 재사용할 수 없습니다.
- 최종 collector, 신규 sole의 실제 변형, native 첫 포즈의 부츠 모양/발목/복장/얼굴, 보행·달리기·8방향·8×8 사격·HTML·Luna는 **HOLD/미검수**입니다. 원본/실패 자산은 보존합니다.

적용 지침: `sable-motion-production` 및 Ponytail FULL. 이번 기하 감사의 수정 범위는 이 보고서 하나이며 소스 코드·자산은 수정하지 않았습니다.
