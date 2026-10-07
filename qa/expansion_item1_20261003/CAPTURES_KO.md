## 캡처 — 최종 네이티브 1080p 14장

최종 증거는 `capture_native_v2/`의 14장이다. 이전 `capture_native/` 후보는 이력으로 남겼고 삭제하지 않았다. 실제 작전 6·7·8·9 방의 기존 판·소품·무드·심연을 렌더했다. 새 그림, 부분 합성, 이미지 확대는 없다. 네이티브 창과 PNG는 **1920×1080**, 논리 캔버스는 1280×720, 14장 모두 실제 게임의 정상 카메라 줌 **1.22×1.22**다. 원화·로봇·연산자의 축척은 바꾸지 않았다.

이 증거는 **controlled runtime fixture이며 사람 플레이 캡처가 아니다.** 화면에도 `CONTROLLED RUNTIME FIXTURE // NOT HUMAN PLAY`를 표시한다. 스테이지·분대·로봇의 이동과 공격을 정지하고 실제 장판 컨트롤러의 단계, 부화 타이머를 검토할 시점에 고정했다. BROODING·BEACON 부모를 죽일 때의 `99999` 피해는 캡처 준비용이다. 실제 전투 입력, 탈출 공정성, 난이도·균형의 증거로 세지 않는다.

- 캡처 로그: [capture_native_v2.log](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/logs/capture_native.log>) — `EXPANSION_ITEM1_CAPTURE: PASS (124 checks)`.
- 메타데이터: [capture_report.json](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/records/capture_report.json>) — `PASS_TECHNICAL_ONLY`, 124검사, 실패 0, 배치 없음에 의한 SKIP 0, 실제 캡처 14장. 파일 SHA-256: `9d4547258424fac22ee1c438a858c62da1305ffaccc119d697a9bb3f42e2eae6`.
- 현재 검증 결과의 원본 경로는 [visual_validation.json](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/records/visual_validation.json>)이다(`report/visual_validation.json`은 이 초안 작성 시 존재하지 않았다). SHA-256: `b9f8b9ca0c7f58d26e4256785482da8f85047b63aaa083c692c5a62cf23c519e`.
- `tools/art_pipeline/validate_visual_evidence_1080p.py` 결과는 `gate=PASS`, `container_gate=PASS`, `dynamic_capture_gate=PASS`, `dynamic_capture_required=true`. 14장 모두 디코드 가능, RGBA 1920×1080이다. **이 PASS는 컨테이너 크기와 디코드만 확인한다. 시각 품질·그림·플레이·균형을 승인하지 않는다.**

### 파일·장면·SHA-256

| 파일 | 실제 방·장면 | SHA-256 |
|---|---|---|
| [01_op6_brooding_parent.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/01_op6_brooding_parent.png>) | 작전 6 `R04_PUMPS`, BROODING 부모의 링·이름 표시 | `5934b3b524aa25290dd42fecac63897cef01db3811baea40356f7b308df58b90` |
| [02_op6_brooding_hatching.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/02_op6_brooding_hatching.png>) | 같은 방, 실제 파괴로 생성된 일반 드론 2기의 부화 링·타이머 고정 | `a91ff13d96accd5523cdd728ee48b123a1c5907294cbe2665cc6fa5335d9bec4` |
| [03_op6_brooding_hatched.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/03_op6_brooding_hatched.png>) | 같은 방, 부화 타이머 완료 후 드론 2기; 변종 없음 | `4af2aecf237b1466b6ca47b3ec75c3ffc87e576e0ffb5fa6adf88ac033bdd68a` |
| [04_op9_beacon_links.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/04_op9_beacon_links.png>) | 작전 9 `R04_GALLERY`, BEACON이 보호하는 다른 로봇 3기로 연결선 | `496f514a048f2f884fe130a087c0fe02f22b44b21fd4f215df372865194701ef` |
| [05_op9_beacon_released.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/05_op9_beacon_released.png>) | 같은 방, 비콘을 실제 피해로 파괴한 뒤 연결선·보호 해제 | `a5230b889c0e48c522bf31a481e783b12847d65ccce8285c5b37cfe0349ef50e` |
| [06_spore_cloud_idle.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/06_spore_cloud_idle.png>) | 작전 6 `R02_GALLERY`, SPORE_CLOUD 첫 대기; 대상들은 밖의 실제 바닥 | `570de37183b06e231a372af91fe70a65e3ed56258dcf9f3dab0739aa65ac3e91` |
| [06_spore_cloud_telegraph.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/06_spore_cloud_telegraph.png>) | 같은 방·동일 카메라, 경고 구름·링; 대상들은 밖, 경고 피해 0 | `6eaae217b0b2f11364bd905652f8a982961c8d989cba0e7ca44d4f3d64cee72c` |
| [06_spore_cloud_active.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/06_spore_cloud_active.png>) | 같은 방·동일 카메라, 대상들을 양끝 안쪽에 놓고 실제 지속 피해 갱신 | `01492d943896ed2fe68661e39a80d312970f57669bf8270d5724a7b8cabcf7b4` |
| [07_frost_plate_idle.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/07_frost_plate_idle.png>) | 작전 7 `R02_FREEZE`, FROST_PLATE 첫 대기, 속도 토큰 1.0 | `9bf17265eaaf41d784fcf4f08558cdf855dd5f66798b4632b29bd785427132c3` |
| [07_frost_plate_active.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/07_frost_plate_active.png>) | 같은 방·동일 카메라, 서리 위 연산자와 RAM의 실제 속도 토큰 0.7 | `e4c3a5f60b700c20f0be381609626d12ee50593bf00b5a8ef17c5a6b8f6f4833` |
| [07_frost_plate_cleared.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/07_frost_plate_cleared.png>) | 같은 방, 실제 장판 정리 뒤 두 대상 속도 토큰 정확히 1.0 복원 | `4e675d6ffa2310fc0866341c052765b82615ad9be240fecf9e0f36e5358cff57` |
| [08_rail_lane_idle.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/08_rail_lane_idle.png>) | 작전 8 `R02_MARSHALLING`, RAIL_LANE 띠의 첫 대기 | `4d8310175380502a730df1e7b54d3bed94d1968c9216ed71a2c53f67d6ea8013` |
| [08_rail_lane_telegraph.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/08_rail_lane_telegraph.png>) | 같은 방·동일 카메라, 띠 경고; 대상들은 밖, 경고 피해 0 | `14759d69c98b406c5a4d66c4e938fe8f0df44fcfb7b9d55622de3bdd036c9950` |
| [08_rail_lane_active.png](<D:/AI 종합 폴더/Games/Sable-circuit/qa/expansion_item1_20261003/captures/08_rail_lane_active.png>) | 같은 방·동일 카메라, 실제 방전 직전에 두 대상을 띠 안쪽 양끝에 배치 | `3e899f27f96a93f481b95591ae5a2713f85edc9655b4cf6b6fa29051a9eb32e6` |

### 준비 방법과 관측 수치

BROODING은 실제 `apply_damage` → `spawn_elite_brood` → 부모의 defeated 신호 순서로 생성했다. 부모 사망 전 방의 적은 4, 새끼 +2·부모 −1 뒤 5다. 부화 시간은 0.6초이고 공격하지 않는 부화 중 링을 고정했다. 실제 파괴 효과가 자연스럽게 끝나도록 1.5초 기다렸으므로 그 프레임의 경과 시간이 실제 부화 길이를 보여 주는 것은 아니다. 부화·방 개방·세대 제한 검증은 별도의 기능 시험이 담당한다.

BEACON 프레임에는 실제 연결선 3개와 감쇠율 0.25가 기록된다. 파괴 직후 각 보호 대상에 `beacon_for(...) == null`인 것을 검사했다.

장판은 실제 배치 위치를 움직이지 않았다. 첫 대기와 경고에서는 두 대상을 밖의 걷는 바닥으로 옮겼다. 활성 프레임에서만 양끝 안쪽으로 넣었고, 실제 방의 일반 로봇 중 `combat_hit_rect` 면적이 작은 하나를 골랐다. SPORE 대상은 PRISM, FROST 대상은 RAM이다. 같은 장판의 세 프레임은 카메라 위치·줌이 같다.

| 장판 | 이 fixture에서 관측한 연산자 피해 | 로봇 피해 | 속도 토큰 |
|---|---|---|---|
| SPORE_CLOUD | 0.204 HP | 0.408 HP | 1.0 유지 |
| FROST_PLATE | 0 | 0 | 두 대상 모두 1.0 → 0.7 → 정확히 1.0 |
| RAIL_LANE | 14 HP | 24 HP | 1.0 유지 |

SPORE 수치는 경고 종료 후 약 0.051초만 진행한 준비 장면의 값이다. 전체 지속 피해, AI 회피, 실제 방 탈출의 검증을 대신하지 않는다. 카메라에 보이는 위치·개체 ID·단계·실제 크기·SHA·속도 토큰은 `capture_report.json`에 남겼다.

사용자 결정에 따라 **변종 없는 같은 로봇의 공통 weathering material은 유지하고, 변종의 추가 착색만 금지했다.** 로봇 그림을 새로 만들거나 착색하지 않았다. 메타데이터의 `material_present=true`는 기존 공통 weathering을 뜻하며, 변종 전용 재질을 허용했다는 뜻이 아니다. sprite `modulate`·`self_modulate`와 material 존재·경로를 각 대상별로 기록했다.

### 시각 검토 한계

- BROODING의 일반 드론 2기는 기존 게임 이미지 폭 때문에 서로 일부 겹친다. 새끼 2기 존재는 메타데이터·개체 검사가 확인하지만, 그림 두 장이 완전히 분리되어 보이는 증거는 아니다.
- SPORE는 대상 몸이 링을 가리던 첫 후보를 개선했다. 최종 프레임에서도 실제 소품의 높이와 깊이 정렬 때문에 아래쪽 일부가 가려진다. 소품·바닥·장판 위치·축척은 그 때문에 바꾸지 않았다.
- 긴 fixture 설명문 일부는 화면 하단에서 줄임표로 끝난다. 전문, 단계와 준비용 피해값은 메타데이터 및 이 기록에 남겼다. 이 캡처로 HUD 문구 전체가 잘리지 않는다고 주장하지 않는다.
- 캡처 로그에는 기존 `M7_RASTER_QUARANTINED identity=aster status=partial ...` 진단이 반복되어 있다. 캡처 도구의 기술 PASS가 그 진단을 해결하거나 연산자 그림을 승인한 것은 아니다.

이 기록은 그림·플레이·균형 승인이 아니다.
