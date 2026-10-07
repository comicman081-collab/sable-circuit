# Ponytail FULL — anatomical builder R3 제한 코드 재검수

검수자: `/root/ponytail_motion_audit` (Ponytail FULL 독립 검수)

검수일: 2026-09-07. 판정: **지정된 R2 P1의 코드 경로는 닫힘. 실제 제작·시각 승인은 HOLD**.

읽기 전용으로 실제 runner → 승인/1회 claim → builder → collector → 첫 포즈 감사 호출을 추적했습니다. Blender, 렌더, 테스트 프로세스는 실행하지 않았습니다. 이 보고서는 아직 제시되지 않은 정확한 build plan의 승인도 아닙니다.

## 검수 스냅샷

| 파일 | SHA-256 |
| --- | --- |
| `tools/character_pipeline/build_mica_anatomical_candidate.py` | `64ff5ad0a10ebe1af3339d2960a9e3350932736d99d882604c1c20adc1ad49aa` |
| `tools/character_pipeline/run_mica_anatomical_candidate.py` | `e2f0fb7da2f47b7b5f260e74b32373ae73c510ba9a38e23df0b2701e0e6cfd31` |
| `tools/character_pipeline/collect_generation_mesh_preflight.py` | `6d540f387cc3e93780ecfdd8795e7e127317f26985e486a40ca1fe10864b6805` |
| `tools/character_pipeline/generation_harness.py` | `4a10c7ca1464b21ee57fa0e55e74ffdf8ceaf89159c7b9ec72433bbfae60bc46` |
| `tools/character_pipeline/generation_contract.json` | `da9ce074cdc1abf34ae888b29b5a895a9e3fcf5b4767c40805fcc5ee8d517d81` |
| `.agents/skills/sable-motion-production/SKILL.md` | `ce6fd9ffa9eb44bde19a02dca08058b8ad99d7d2034064ad15e5da554dd91834` |

## 이전 P1 수정의 확인

1. **내피 SOLIDIFY와 바닥 강제 평탄화 제거: 코드상 닫힘.** `fitted_region()`(builder:62)는 실제 인체의 선택된 면·원래 정점 ID·스킨 가중치를 복사합니다. 닫기 분기(72–82)는 현재 외피 경계만 검사하고, 경계 정점에 z<0.35m가 있으면 `BOOT_OUTER_SURFACE_HAS_NON_CUFF_HOLE`로 중단합니다. `holes_fill`은 위쪽 cuff 구멍만 닫습니다. 발 안쪽에 추가 껍질을 만드는 SOLIDIFY도, 저점 정점을 동일 평면으로 덮어쓰는 코드도 없습니다. 정점 수가 달라지면 중단하며 정렬된 원본 정점 ID 목록을 `outer_surface_source_vertex_ids`에 남깁니다.
2. **실제 외피 발바닥 선택: 코드상 닫힘.** builder:230–241에서 좌우 발을 분리하고 각 발의 실제 최저 z를 구합니다. 아래 방향 면(`normal.z < -0.55`)에 속하면서 각 발 저점+0.006m 아래인 실제 외피 정점만 sole ID로 선택합니다. cuff cap은 높이 제한으로 이 저점 집합에 들어갈 수 없습니다. 한쪽이라도 3개 미만이면 중단합니다. 별도의 숨은 접지 helper나 의도된 IK 좌표를 측정값으로 쓰지 않습니다.
3. **측정 바닥 원점: 코드상 닫힘.** builder:240, 276–282의 `ground_z`는 만들어진 부츠 외피의 실제 최저점입니다. 이 값을 body frame과 계약의 바닥 원점에 같이 사용하고 원하는 지면 값으로 정점을 바꾸지 않습니다. 이는 중립 장면 구성 규칙이며, 애니메이션 중 실제 접지 품질을 보장하지는 않습니다.
4. **실제 collector 소비 경로 유지.** collector:210–219는 선택된 sole ID를 dependency graph에서 평가한 메시의 세계 좌표로 채집합니다. collector:267–301은 보이는 실제 스킨 메시, 서로 분리된 좌우 집합, 실제 면에 속한 가중 정점, 닫힌 해부학 토폴로지를 검사합니다. builder는 그 감사에 오류가 있으면 렌더 전에 중단합니다. 따라서 단순히 목록에 정점 번호가 있다는 것을 렌더·접지 PASS로 처리하는 경로로 바뀌지 않았습니다.

## 같이 요청된 작은 수정

- builder:140–149는 열린 코트 외피의 각 면을 몸통 바깥 방향으로 명시적으로 뒤집어, 폐쇄 체적의 법선 추론에만 의존하던 모호성을 제거했습니다. 실제 접힘·안감·허리 연결의 외형은 첫 포즈에서 확인해야 합니다.
- builder:290의 실제 Cycles thread 수는 `plan['limits']['threads']`를 사용합니다. runner가 승인된 thread 제한과 timeout을 전달하는 경로와 일치합니다.
- 갱신된 스킬은 `source receipt → exact build plan/review → build receipt → 1회 실행 예약/runner·builder claim`을 사용합니다. 이전 `check_build_handoff.py`를 필수 제작 입구로 요구하지 않습니다. 원래 원화 request/permit의 implementation binding을 새 builder로 소급 편집하는 지침도 없습니다.

## 남은 검증은 별도 HOLD

이번에 실제 `.blend`를 생성하거나 렌더하지 않았으므로 최종 부츠의 면 수·체적·정점 대응·법선·좌우 sole 개수·피부 및 복장 외형에 대한 실제 통과를 주장할 수 없습니다. 특히 source ID 목록의 보존은 추적성을 제공할 뿐, 아직 생성되지 않은 실제 평가 메시와 육안 관찰을 대신하지 않습니다.

다음 정확한 build plan은 현 builder/runner 및 의존 코드 해시, 라이선스가 확인된 읽기 전용 실제 인체 입력, source receipt, 소비 이미지, 제한된 새 출력 경로를 묶어 독립 검수해야 합니다. 그 뒤 허용된 한 장의 중립 포즈에서 실제 mesh preflight와 외형을 확인해야 합니다. 빈손 중립 포즈에는 보이는 총구가 없으므로 현재 `visible_muzzle` 항목을 PASS로 기입해서는 안 됩니다. 중립 구성 검사와 별도 무기/전투 포즈 검사의 경계는 그대로 유지해야 합니다.

결론: 요청된 SOLIDIFY/평탄화/숨은 sole 관련 기존 P1을 재현하던 **코드 메커니즘은 수정되었습니다**. 이 제한 검수 범위에서 새로운 동일 수준의 실행 전 결함은 발견하지 못했습니다. 실제 캐릭터 외형, 8방향 이동·사격, 런타임, HTML 또는 Luna 준비가 완료되었다는 판정은 아닙니다.

사용한 지침: `sable-motion-production` 및 Ponytail FULL. 변경은 이 독립 보고서뿐이며 소스 코드·원화·기존 보고서는 수정하지 않았습니다.
