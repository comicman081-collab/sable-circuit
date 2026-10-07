# 맵 판 경계 직선 제거 — 2026-09-26

VFX 개편(`5d3d6a850`) 화면에서 판 경계가 직선으로 잘려 보였다. 이 경계는 사용자가 앞서 지적한 맵 연결 문제의 남은 부분이다.

기준 커밋은 `5d3d6a850`이다. 그림 픽셀은 바꾸지 않았다. 판을 그릴 때의 투명도만 바꿨다.

## 원인
- 통로 판: 바닥 조명이 판의 위아래 끝까지 칠해져 있다. 그래서 그 아래 방 그림 위에서 밝은 바닥이 직선으로 끊겼다.
  - 전에는 통로의 좌우 끝(이음매)만 흐리게 했다.
- 방 판: 방 판은 흐림 처리가 없었다. 그래서 레벨 밖 검은 공간과 만나는 테두리가 사각형 직선으로 보였다.

## 바뀐 것
- `scripts/missions/site7_room_art_layer.gd`
  - 통로 판(`CAP_FADE` 0.1)
    - 위아래 끝 10 %를 흐리게 한다.
    - 자기 바닥(대원이 걷는 데크) 위는 흐리지 않는다. 데크 경계에서 20 px에 걸쳐 부드럽게 이어진다.
  - 방 판(`ROOM_EDGE_FADE` 0.05)
    - 네 변을 5 %씩 흐리게 한다.
    - 방의 걷는 바닥은 판 테두리에서 7.5 % 안쪽에서 멈춘다. 그래서 흐려지는 바닥은 없다.
  - 이제 모든 판이 셰이더 재질을 가진다. 전에는 앞 판의 바닥과 겹치지 않는 방 판에는 재질이 없었다.
- `tools/environment/build_site7_world_layout.py`
  - `--preview` 합성 이미지도 같은 두 가지 흐림을 똑같이 적용한다.
  - 저장된 배치(`site7_world_layout.json`)는 바뀌지 않았다. `--check` PASS.
- `tests/smoke/site7_battle_geometry_smoke.gd`: 검사 80개를 더했다(2019 → 2099).
  - 작전 5개 모두에서 통로 7개가 위아래 흐림을 가지는지 본다.
  - 방 판마다 네 변 흐림이 있는지 본다.
  - `ROOM_EDGE_FADE`가 바닥 안쪽 여백(`MASK_EDGE_FADE`의 절반)을 넘지 않는지 본다.
  - HEAD의 아트 레이어로 돌리면 통로와 방 검사가 FAIL한다. 이 FAIL을 직접 확인했다.

## 확인
- 지오메트리 테스트 4개 PASS: `qa/regression_runs/20260926_111646_custom/`
  - `floor_segment`
  - `world_layout`
  - `connector_alignment` (검사 320개)
  - `battle_geometry` (검사 2019개, 가드를 넣기 전)
- 가드를 넣은 뒤 `battle_geometry`(검사 2099개) PASS: `qa/regression_runs/20260926_112944_custom/`
- quick 스위트 33/33 PASS: `qa/regression_runs/20260926_112515_quick/`
- 걷는 바닥, 충돌, 경로는 바뀌지 않았다. 바뀐 것은 판을 그리는 투명도뿐이다.

## 화면 (창 모드 실제 렌더, 1920×1080, 무손실 WebP)
- `probe/plate_seam_capture.gd`로 찍었다. 작전 1이고, 배우, 엄폐물, HUD는 숨겼다.
  - 통로는 줌 0.84, 방은 줌 1.22다.
- `before`는 `5d3d6a850`의 아트 레이어로, `after`는 이 커밋으로 찍었다.
- 다시 찍으려면 스크립트를 `.cache/diag/`에 복사해서 `--out=res://.cache/...`로 돌린다.

| 파일 | 내용 | SHA-256 |
|---|---|---|
| `01_connector_C3_before.webp` | 통로 C3: 위아래 끝의 밝은 바닥이 직선으로 끊김 | `dc60be0a079d8f47274410a8f547d4167527bf3c6c7c947afc04d64fba02a721` |
| `01_connector_C3_after.webp` | 같은 곳: 끝이 흐려지고 데크는 그대로 | `e58403bb62b087f41e1ec1e2187343fd89b872785cc342debd648ba13540dfd7` |
| `02_room_R02_b_before.webp` | R02 오른쪽: 오른쪽 아래 검은 사각형, 오른쪽 위 통로 끝 직선 | `334bd700ca5bf595182fda734da0750e77c35df0391ed4fd88595bf37448ba7f` |
| `02_room_R02_b_after.webp` | 같은 곳: 두 경계가 흐려짐 | `b48aa8fca15a5e4e1f6d80a6988de9324af19ff0957b7e86374cd9f319b3e7b0` |
| `03_room_R01_a_before.webp` | R01 왼쪽: 방 판 왼쪽 변이 검은 공간과 직선으로 만남 | `4a1f969f54aae1d73e67f222aabc2b5687209e9325470097c9a42f561caf81a8` |
| `03_room_R01_a_after.webp` | 같은 곳: 왼쪽 변이 어둠으로 흐려짐 | `e94ec2356ef9a9a0c816ce98a7dd340124becb2d2c03d191d1b50f58df5ae628` |

- `visual_evidence_validation.json`: `validate_visual_evidence_1080p.py` PASS. 컨테이너와 디코딩만 확인한 것이다.

## 남은 것
- 판마다 그려진 조명이 달라서, 통로 데크와 방 바닥이 만나는 곳에 밝기 차이가 남는다. R02 왼쪽의 청록 바닥이 그 예다.
  - 이것은 그림 자체의 차이라 투명도로는 없앨 수 없다.
- 기술 검증이다. 아트 승인이나 사람의 플레이 승인이 아니다.
- 웹 빌드는 다시 재지 않았다. 판 셰이더의 비용은 판 15장에 대한 단순한 계산이다.
