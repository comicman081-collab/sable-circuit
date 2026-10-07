# Ponytail FULL — 실제 부츠 sole 선택 실패 원인

검수자: `/root/ponytail_motion_audit` (독립 Ponytail FULL)

날짜: 2026-09-07. 판정: **직접 실패 원인 확인. 수정 구현·잔여 토폴로지 검수 HOLD**.

코드와 실제 무렌더 진단 JSON을 읽고 수치를 독립 계산했습니다. 이 검수에서는 Blender·렌더·테스트를 실행하지 않았고 builder를 수정하지 않았습니다.

## 직접 본 증거

- R2 실제 `model_r02/blender.log`: builder의 `ACTUAL_BOOT_BOTTOM_VERTEX_SELECTION_FAILED`에서 자식 exit 2. 렌더/완료 전에 중단되었습니다.
- 검수한 builder: `tools/character_pipeline/build_mica_anatomical_candidate.py`, SHA `e91cfdbf3e5a8dcf337d3d097d0bc9f0325b7e992ecb9694813bf6e7f650987f`.
- 실제 rig 입력: `Realistic_Anatomical_Base_UAL_Walk_DIAGNOSTIC.blend`, SHA `6aae643c4c750ce896b5232a3df1f77e4577e408383381d22d704065472cc467`.
- `mica_boot_surface_r1/BOOT_SURFACE_DIAGNOSTIC.json`, SHA `9606afd40773702bd3a5a0ee56064d322e54b897fc527df24bea786b6a06be7b`.
- `mica_boot_surface_r2/BOOT_SURFACE_DIAGNOSTIC.json`, SHA `0eddc904c51a23e6d6cbff79cd288547c93fe8b7c3d9b13e3741342418613773`. 이 진단의 producer 코드 해시는 `83ea7868c18e5f599c2a58202280daa26105fd463faef55c7ca976b7271a807b`입니다. `completion.json`은 실제 자식 종료·원본 불변·위 보고서 해시를 기록하며 `production_ready: false`입니다.

위 진단 폴더는 모두 `artifacts/quarantine/generation_diagnostics/` 아래입니다. 진단 결과를 생산 또는 외형 승인으로 읽지 않았습니다.

## 확인된 직접 원인

실제 `fitted_region()`의 cuff 폐쇄 후 면 방향 재계산(builder:79–80)에서 **오른쪽 닫힌 부츠의 방향이 안쪽으로 뒤집힙니다**. 그 뒤 builder:243–250은 실제 저점과 아래 방향 면 정점의 교집합을 찾으므로 오른쪽 후보가 1개만 남아 정상적으로 차단됩니다.

| 실제 단계 | 오른발 저점/교집합 | 왼발 저점/교집합 | 오른발 signed volume |
| --- | --- | --- | --- |
| `mesh_object` recalc 후, cuff 이전 | 91 / 91 | 91 / 91 | 열린 표면이므로 부호를 체적 승인에 사용하지 않음 |
| cuff 닫힘 + recalc 이후 | 91 / 1 | 91 / 91 | `-0.00438905736227826 m³` |
| 진단용 폐쇄 component 방향 반전 이후 | 91 / 91 | 91 / 91 | `+0.004363019465509196 m³` |

닫힌 단계의 양쪽 경계 edge와 nonmanifold edge 수는 각각 0입니다. 저점 정점이 부족한 것이 아니며 좌우 분류도 정상입니다. 오른발 sample 252의 원본 법선은 `(0.165955, 0.182178, -0.969159)`인데 새 부츠에서는 `(-0.165924, -0.181709, +0.969253)`입니다. low vertex 전체의 원본→새 법선 내적은 왼쪽 `0.9928…1.0`, 오른쪽 `-1.0…-0.9899`입니다.

독립 계산한 `new_position - (source_position + 0.009 * source_normal)`의 최대 절대 오차는 왼쪽 약 `7.50e-9m`, 오른쪽 약 `7.40e-9m`입니다. 따라서 해당 low vertex의 offset 계산이나 원본 normal 캐시가 잘못되어 위치가 엉뚱해졌다는 가설은 이 증거로 지지되지 않습니다. 좌표에서 계산한 폐쇄 component의 음수 체적 역시 단순한 법선 표시 캐시 문제만으로 설명되지 않습니다.

## 최소 수정 방향

실제 cuff를 닫은 뒤, **각각의 연결된 폐쇄 component**에 대해 경계/nonmanifold가 없고 체적이 유한·비영인지 확인한 후 음수 방향만 뒤집는 것은 타당한 수정입니다. 전체 양발 합계 체적만 검사하면 오른발 음수를 왼발 양수가 가릴 수 있습니다. 수정은 정점 좌표·source ID·weights를 보존해야 합니다.

수정 후 같은 실제 인체 입력에서 별도의 새 진단으로 양쪽 양수 체적과 각 91개 교집합을 재확인해야 합니다. 6mm 범위 확대, `normal.z < -0.55` 제거, 임의 sole ID 추가, 평탄화 또는 숨은 helper 추가는 원인 수리가 아닙니다. 합성 회귀에서는 한 component만 뒤집힌 폐쇄 메시가 실제로 탐지·교정되는지 검사하되, 그 결과를 실제 캐릭터 검증으로 확대하지 않습니다.

## 추가 발견: 방향 수리만으로 토폴로지 PASS를 줄 수 없음

진단의 `direct_vs_rna_normal_max`는 cuff 이전부터 우 `1.999812`, 좌 `1.988684`이며 반전 뒤에도 남습니다. 비평면 quad의 triangle normal과 polygon normal은 다를 수 있지만, 거의 반대 방향까지 차이 나는 값을 정상 오차라고 단정할 수 없습니다. 원본과 9mm offset의 해당 최악 면/triangle을 비교하여 접힌 면·뒤집힌 삼각형·자기교차인지 확인해야 합니다.

또한 오른발 방향을 뒤집은 뒤 체적의 절대값이 약 **0.59%** 달라집니다. 정점 좌표를 움직이지 않았더라도 비평면 polygon의 재삼각분할이 바뀌면 실제 삼각형 표면은 달라질 수 있습니다. 따라서 “정점 불변이니 모든 표면 기하도 완전히 동일하다”는 주장 역시 아직 성립하지 않습니다.

다음 제작-plan 승인 전에는 최악 면의 위치·면적·원본/offset normal 방향과 실제 triangulation을 확인해야 합니다. 이는 source ImageGen 재생성 사유가 아니라 부츠 표면 구성의 한정 진단 사유입니다. signed volume 양수와 닫힌 edge만으로 자기교차 없는 해부학 표면을 증명할 수 없습니다.

결론: **cuff 폐쇄 이후 오른발 방향 반전은 확인된 직접 실패 원인**이며 component 단위 바깥 방향 정규화는 올바른 수정 방향입니다. 남은 국소 표면 접힘 가능성은 별도 HOLD입니다. 현재 메시·외형·8방향 이동·총구·HTML 또는 최종 완성은 승인하지 않습니다.

적용 지침: `sable-motion-production` 및 Ponytail FULL. 변경한 파일은 이 보고서 하나뿐입니다.
