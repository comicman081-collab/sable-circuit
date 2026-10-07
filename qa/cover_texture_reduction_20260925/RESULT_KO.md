# 엄폐물 텍스처 GPU 사본 축소 — 2026-09-25 (WP-5, D6)

D6는 권장안대로 결정했다. 엄폐물(kArchive 소품) 4종의 GPU 사본만 줄이고, 캐릭터·로봇 아트는 원본 그대로 둔다.
원본 파일과 소품 스펙은 바꾸지 않았다. 게임이 불러올 때 메모리 안에서만 줄인다.

## 바뀐 점
- `site7_environment_props.gd` `reduced_prop_texture()`:
  - 1920×1080 원본에서 알파가 있는 영역에 여백 2px을 더해 잘라낸다.
  - GPU 텍스처는 그 영역을 0.5배(Lanczos)로 줄이고 밉맵을 붙인다.
  - 탄 판정용 알파는 잘라낸 영역을 원본 해상도 LA8로 보관한다.
- `site7_environment_prop.gd`:
  - 스프라이트는 영역 위치와 크기에 맞게 배치해 화면에서 예전과 같은 사각형을 덮는다.
  - 탄 판정은 예전 전체 스프라이트와 같은 변환을 가진 `SourcePixelSpace` 노드로 원본 픽셀 좌표를 계산한다.
  - 샘플 수, 경계, 알파 임계값 0.5는 그대로다.

## 확인
- `tests/smoke/cover_texture_reduction_smoke.gd` 17개 검사 PASS (러너 quick 스위트 `cover_texture`).
  - 소품마다 무작위 탄 1,500발을 예전 방식(전체 알파, 전체 스프라이트 변환)과 비교했다. 명중 위치와 샘플 수가 1,500/1,500 모두 같다.
  - 화면 사각형이 같다(0.01px 이내).
  - 메모리: 엄폐물 텍스처와 알파를 합쳐 63.3 MB에서 10.2 MB로 줄었다(밉맵 포함 추정치).
- 엄폐 관련 기존 검사(cover_navigation, player_cover, cover_alpha_clip)도 PASS.
- `tests/render/cover_texture_ab_capture.gd` 창 모드 실제 렌더 1920×1080:
  - `cover_full_vs_reduced_1080p.png`: 윗줄은 원본 전체 텍스처, 아랫줄은 축소 사본이다. 줌 1.22는 일반 전투 카메라 값이고, 표시 폭은 게임과 같다.
    SHA-256 cadc8b21ec7f83574476c6d0141c853be9f382bdd6f78b8c8d3caed3b9f473d9
  - 위아래 494px 차이로 겹쳐 비교한 소품별 PSNR:

    | 소품 | PSNR | 최대 차 | 8 초과 화소 |
    |---|---|---|---|
    | barrier | 46.74 dB | 27 | 0.52% |
    | cabinet | 44.73 dB | 18 | 0.34% |
    | crate | 39.27 dB | 29 | 2.66% |
    | generator | 48.55 dB | 12 | 0.02% |

    차이는 가장자리 밉맵 필터링에서 나온다. 일반 줌에서 축소 사본은 텍셀당 화면 0.4~0.5px 이하로 계속 축소 표시되므로 확대 표시로 뭉개지지 않는다.
  - `cover_ab_layout.json`: 배치, 영역, 텍스처 크기.
- `01_room_hits_and_hurt.png`, `02_profile_and_reaction_matrix.png`: 축소 적용 후 VFX 캡처 스크립트로 다시 찍은 실제 방 화면이다. 작전 1 방 2에 방벽, 상자, 캐비닛이 보인다.
  - 01: SHA-256 1b29f20faef1bc41a657c37c194474da57afbebc79cad5b167528ecb70241d13
  - 02: SHA-256 e25fd0ba083dd94cbe4761e7648be6e34e56d5f99599150ceed16971f1f94726
- `validate_visual_evidence_1080p.py` → `visual_evidence_1080p.json` gate PASS. 이는 컨테이너와 디코딩만 확인한 것이고 화질 판정이 아니다.
- 웹 빌드의 실제 메모리·FPS 측정은 WP-2에서 따로 한다. 이 기록은 아트 승인이 아니다.
