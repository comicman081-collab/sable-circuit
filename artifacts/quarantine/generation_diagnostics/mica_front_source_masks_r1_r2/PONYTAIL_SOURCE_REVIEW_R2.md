# MICA S 중립 원화 R2 — Ponytail FULL 독립 시각 검수

- Reviewer: Codex Ponytail FULL reviewer `/root/ponytail_motion_audit`
- Role: `Ponytail FULL`
- Reviewed UTC: `2026-09-07T10:21:04Z`
- Actor / costume: `CHR_PROTO_03` / `MICA_RECON_C03`
- Source subject SHA-256: `499f0e877df1e4ce788be893b80e3d1d8059991bfe75d4a6d15914ca2e80be08`
- Scope: 신규 ImageGen S 정면 중립 A포즈 원화와 R2 주석·visible material swatch 마스크만.
- Overall verdict: **FAIL — R2 trousers 마스크를 그대로 승인할 수 없습니다. 원화 전체를 다시 생성하라는 판정은 아닙니다.**

## 실제 확인한 증거

원본 `MICA_C03_S_NEUTRAL_RIG_GREEN_R1.png`, `SOURCE_REVIEW_R2_NATIVE_2304x1920.png`, request의 기존 정면 identity authority와 E profile costume reference를 각각 직접 열어 비교했습니다. 허벅지 원본/오버레이는 동일 좌표의 원본 배율 crop으로 추가 확인했으며, 확대·재도색하거나 검사 이미지 파일을 새로 저장하지 않았습니다. R2 마스크의 해당 원본 좌표 포함 여부도 읽기 전용으로 확인했습니다.

`generation_harness.py next --input art_src/characters/mica/rigged_v2/job_r03.json`은 `REQUEST_INDEPENDENT_SOURCE_REVIEWS`, errors 0, production_ready false, allow_batch_generation false였습니다. SOURCE_AUDIT_R2의 16개 binding은 현재 파일 SHA와 모두 일치했습니다. 기술 감사의 errors 0을 시각 PASS로 대신하지 않았습니다.

| source_review_checks | 판정 | 직접 본 근거와 한정 |
| --- | --- | --- |
| `identity_and_costume` | PASS | 기존 정면·측면 참조와 비교하여 성인 얼굴의 눈·눈썹·코·턱 인상, 갈색의 해부학적 오른쪽 브레이드, 청록 눈, 짙은 기술직물, 좁은 베이지 코트 테두리, 청록 안감, 허리·허벅지 장비, 무릎 보호구, 스트랩 부츠, 등 뒤 두 센서 장비의 연속성이 유지됩니다. 손을 비우고 A포즈로 바꾼 것은 request에 명시되어 있으므로 무기 삭제·재설계로 판정하지 않습니다. 이번 원화는 carbine의 새 권위 자료가 아닙니다. |
| `true_body_facing` | PASS | 얼굴만 정면이 아니라 어깨·흉곽·골반·무릎 보호구와 양쪽 부츠 앞면이 함께 정면입니다. 체중이 한쪽으로 치우친 전투 포즈, 다리 교차, 발목 90도 회전은 보이지 않습니다. 양팔이 몸에서 떨어져 있고 손이 코트/몸통을 가리지 않습니다. 정적 S뷰의 시각적 정면 판정이며 실제 3D orthographic camera를 측정한 결과는 아닙니다. |
| `shared_scale_and_ground` | PASS | 이 한 S뷰 내부에서 양쪽 다리 길이와 부츠 바닥 높이는 일관됩니다. head_top y=42, ground y=1424, 양 toe y=1422는 원본에서 보이는 머리/부츠 바닥과 대체로 맞고, 해부학적 left/right는 화면 좌우와 올바르게 반대입니다. 1.72m는 제작용 기준 높이이지 원화에서 실측한 물리 치수가 아닙니다. 다른 방향의 배율·지면까지 승인하지 않습니다. |
| `unoccluded_texture_regions` | HOLD | 얼굴과 중앙 몸통, 코트 일부, 부츠 전면 및 바지 천에는 재사용할 수 있는 노출 영역이 있습니다. 그러나 현재 trousers의 길쭉한 두 swatch가 허벅지 장비 가로 스트랩을 가로지르므로 현재 선택 전체를 '가리지 않은 바지 천'으로 승인할 수 없습니다. 천 영역만 남기는 R3 분할/제외 마스크가 필요합니다. 이 원화에서 가려진 뒤·옆면은 승인 범위가 아닙니다. |
| `no_foreign_parts_in_uv_masks` | FAIL | `trousers_MASK_R2.png`의 두 폴리곤이 외부 허벅지 장비의 가로 웨빙/스트랩을 포함합니다. 원본/오버레이 ROI에서 띠가 마스크를 횡단하는 것이 보이며, 예를 들어 원본 좌표 (469,748), (465,810), (549,776)가 포함 픽셀입니다. 현재 의미는 `volumetric_texture` / `MICA_Trousers`용 보수적 material swatch이므로 별도 장비 띠를 바지 천과 섞어 재사용하면 반복 띠·끊긴 장비 텍스처를 다시 만들 수 있습니다. 초록 제외만으로는 이 의미적 혼입이 제거되지 않습니다. 얼굴/코트/부츠의 현재 좁은 선택에서 명백한 손 복사나 다른 신체 부위 혼입은 발견하지 못했습니다. |
| `native_source_resolution` | PASS | 원본은 실제 1024×1536이고, 주석상 머리~지면은 1382 source pixels로 1024픽셀 피사체 높이 하한을 충족합니다. 검수판 2304×1920에는 1024×1536 원본 두 패널이 원본 배율로 배치되어 있습니다. 원본을 2048×3072로 생성했다거나 검수판 크기를 원화 해상도로 주장하지 않습니다. `REVIEW_1080P_R2.json`의 PASS는 컨테이너/디코딩에 한정합니다. |

## 최소 수정과 승인 경계

1. 원본 ImageGen 파일은 변경하지 않습니다. R2 trousers swatch에서 실제 가로 스트랩·버클·장비 픽셀을 제외하고, 노출된 바지 천 구간만 각각 선택한 새 R3 마스크를 만듭니다. 장비를 사용하려면 그 부위를 별도 semantic region/허용 mesh part로 정의해야 하며, 바지 천에 섞어 반복 투영하면 안 됩니다.
2. 새 manifest/audit/동일 배율 검수판을 만들고 변경된 정확한 subject로 재검수합니다. 이 R2 판정의 해시나 verdict만 바꿔 재사용할 수 없습니다.
3. 모든 마스크는 visible material swatch일 뿐 전체 UV unwrap이 아닙니다. 코트 안감/뒷면, 얼굴 옆/뒤, 종아리 뒤, 부츠 뒤꿈치 등 보이지 않는 표면에 이 승인만으로 원화 의미를 확장하지 않습니다.
4. 정면에서 뒤꿈치는 가려져 있습니다. `heel_left/right`는 불투명 부츠를 통과해 추정한 construction landmark이며 실제 뒤꿈치 위치·발바닥 정점·접지·미끄럼의 관측 증거가 아닙니다. 해당 제한을 R2 주석이 명시한 점은 확인했습니다.
5. 배경은 시각적으로 녹색 크로마 계열이지만 요청한 `#00FF00`이 모든 배경 픽셀에 정확히 동일하게 반환된 것은 아닙니다. 외곽 표본도 RGB (8,240,5)~(26,228,14) 등으로 달랐습니다. '완벽한 단일 RGB 배경'으로 보고하지 말고, 이후 RGBA 파생물의 경계·초록 번짐은 별도 실제 검사를 거쳐야 합니다. 원본 pixels를 이번 검수에서 수정하지 않았습니다.
6. R1 초록 혼입 마스크와 R2 실패 마스크/원화/증거는 보존합니다. 이 판정은 3D 스킨 메시, 실제 UAL, 관절·코트 변형, 8방향 보행/달리기, 사격·접지, Godot/HTML, 최종 MICA 또는 Luna 준비 승인과 무관합니다.

## 정확한 검수 파일 해시

| 파일 | SHA-256 |
| --- | --- |
| `SOURCE_MANIFEST_R2.json` | `bf3e9628f5e89e9e9f72328f7d647c46fc9cd75f5f179da1afaacdf386bb8733` |
| `SOURCE_AUDIT_R2.json` | `ab924415d58a94db6806e19368828f7fb107de5a409e38e8cff408743faec7d7` |
| `MICA_C03_S_NEUTRAL_RIG_GREEN_R1.png` | `6224f3efd1f72e97fcb95f04bd13479bbaf7c740049435705f567cd6692e8895` |
| `SOURCE_REVIEW_R2_NATIVE_2304x1920.png` | `c6e9915e7b228d33d8e83329195d097c2407013e47492e5395583043b54aef4e` |
| `trousers_MASK_R2.png` | `0d34b55942bd49fda5b3da81ad0a8a6957fe729895c07da4e6e00fb94381f2c6` |
| `S_LANDMARKS_R2.json` | `0cede9deaf7ee1b926283578f3dcb309610bcb8857e524aeac4228e574716c5a` |
| 기존 S identity authority | `e007bd5ca9d9da6cb309c0b059489dc84f60eb50ff891c382b83cab24aef839b` |
| 기존 E profile costume reference | `7ece6e83561bf3c9ee720b4c5a1f75820f73ae4afce95b895fe9b38d3299f4a1` |

서명: **Codex Ponytail FULL reviewer `/root/ponytail_motion_audit`**. 이 파일만 작성했으며 다른 작성자의 파일·판정·원화는 변경하지 않았습니다.
