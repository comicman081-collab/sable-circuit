# 작전 10 `null` 허공 밝히기 (2026-10-02)

기술 확인과 수치 기록이다. 균형과 사람 플레이는 하지 않았고 주장하지도 않는다. 모습의 승인은 사용자의 것이다: 밝힌 허공 모습은 사용자가
같은 날 "승인한다"고 답했다(7절).

## 1. 요청과 결과

- 사용자 지시(2026-10-02): "허공 모습: null 허공이 거의 검게 보입니다.. 검은 배경 없게 하고". 같은 요청이 2026-09-27에도
  있었다(`AGENTS.md`의 "Mood light"). 작전 10을 켠 날 기록(`qa/site7_op10_enable_20261002/README_KO.md` 3절·10절)에도 이 허공이
  검은 배경에 가깝게 보인다고 적고 사용자의 판단으로 남겨 두었던 바로 그 항목이다.
- 결과: 보이는 허공의 평균 밝기(Rec.601 luma, 0–1) **0.025 → 0.124**, 장면별 **0.017–0.031 → 0.094–0.158**.
  같은 방법으로 잰 작전 1–7·9는 0.062–0.107, 작전 8의 새벽 바다는 0.175다. 비교판은
  `before_after_sheet_1920x1684.png`(왼쪽 이전, 오른쪽 수정; 1080p 원본 프레임 6장씩을 줄여 붙인 것),
  원본 프레임은 `frames/before_head/`, `frames/after/`(git 무시, SHA-256은 `void_luma.json`).
- 작전 10의 판 이미지, 보스, 게임 로직, 다른 작전의 판·마스크·행은 바뀌지 않았다.

## 2. 바꾼 것

| 파일 | 변경 |
|---|---|
| `data/visual/site7_mood.json` | 작전 10 `abyss` 행: 바탕 [0.012,0.014,0.02] → [0.065,0.08,0.112], 안개 [0.022,0.028,0.038]×0.1 → [0.11,0.135,0.185]×0.85, 연무 0.045 → 0.1, `void_fill_px` 28 추가 |
| `scripts/missions/site7_abyss_backdrop.gd` | `null` 스타일(9번) 블록만: 격자선 `exp(-d²/1.5)`×0.085 → `exp(-d²/2.4)`×0.2, 격자 후광 `exp(-d²/18)`×0.012 → `exp(-d²/60)`×0.045, 붉은 점 `exp(-d²/8)+0.08·exp(-d²/100)`×0.55 → `exp(-d²/20)+0.18·exp(-d²/320)`×0.8. 다른 스타일, 유니폼, 셰이더 구조는 그대로 |
| `tools/environment/build_site7_mood_light.py` | 선택 기능 `outer_void()`: 행에 `void_fill_px`가 있으면 그 반지름의 두 배보다 좁은 통로로만 이미지 경계에 닿는 "허공"을 불투명으로 돌린다. 없는 작전은 종전 규칙 |
| `data/visual/site7_void_masks.json` | 작전 10의 15장만 다시 만들었다(나머지 135장은 바이트 동일, `void_mask_fill.json`) |
| `tests/test_site7_mood_contact_compare.py` | `VoidFill`, `NullAbyssLit` 추가(빠른 시험 `mood_contact`에 이미 등록돼 있다) |
| `AGENTS.md`, `docs/production/SITE7_OPERATIONS_6_10_DESIGN_KO.md` | "Operation 10 void lit" 절, 상태표·설계표·`null` 심연 항목 |

판 픽셀, 허공 임계값(`VOID_MAX` 12), 다른 심연 스타일, 접촉 그림자(`contact_shadow_px`, dawn 전용)는 손대지 않았다.

## 3. 측정

방법(`tools/capture_abyss_pairs.gd`, `tools/void_stats.py`):

- `tools/environment/capture_site7_plate_edges.gd`와 같은 여섯 카메라(`R01`, `R05`, `O02`, `C03`, `C05`, `C06`; 줌 1.22; 셰이더
  `TIME` 1.0 고정; 배우·HUD·엄폐물 숨김)로 한 장은 그대로, 한 장은 판을 모두 숨겨(허공만) 찍는다. 창 모드 Godot 4.7.1,
  1920×1080, `gl_compatibility`, RTX 4070 SUPER(헤드리스는 셰이더를 그리지 않는다).
- "보이는 허공" = 그대로 찍은 프레임이 허공만 찍은 프레임과 모든 채널에서 3/255 이내로 같은 픽셀(그 자리의 판이 투명하다).
  그 픽셀의 luma 평균을 장면마다 구하고, 여섯 장면의 평균을 낸다.
- 스테이지가 처리되지 않는 캡처에서는 허공 배경의 `camera_center`가 갱신되지 않아 실행마다 허공 픽셀의 30–40 %가 달랐다.
  캡처 스크립트가 이를 카메라 위치에 고정해 최종 상태를 두 번 찍은 12장이 바이트까지 같다. 이전(HEAD) 프레임은 한 번 찍었다.
- 이전 프레임: 세 파일(행·마스크·셰이더)을 `e97fb6ac`의 것으로 잠시 되돌려 찍고 작업본으로 복원했다(해시 확인).

| 장면 | 이전 | 이후 |
|---|---|---|
| R01 (첫 방) | 0.017 | 0.094 |
| R05 (보스방) | 0.026 | 0.120 |
| O02 | 0.031 | 0.158 |
| C03 | 0.027 | 0.135 |
| C05 | 0.024 | 0.115 |
| C06 | 0.026 | 0.124 |
| **평균** | **0.025** | **0.124** |

다른 작전(같은 방법, 현재 그대로의 모습): 작전 1 0.091, 2 0.073, 3 0.107, 4 0.076, 5 0.062, 6 0.083, 7 0.101, 8(새벽 바다)
0.175, 9 0.079. 그 프레임은 이 폴더에 두지 않았고 수치는 `void_luma.json`에 있다.

사실 하나: 작전 1–7·9의 **첫 방(R01) 장면**은 같은 방법으로 0.028–0.046이고(작전 10의 이전 값 0.017과 같은 자릿수), 이번에
손대지 않았다. 사용자가 이 작전들의 모습에 대해서는 문제를 제기하지 않았기 때문이다.

## 4. 벽 틈새 투명(마스크 누수)과 `void_fill_px`

허공이 밝아지자 판 쪽의 문제가 드러났다. 허공 판정(밝기 12 이하이고 4방향으로 이미지 경계에 이어진 픽셀)은 좁고 어두운
틈을 타고 거의 검은 벽 안쪽까지 들어가서, 파이프와 기둥 사이의 어두운 오목한 곳이 투명 처리됐다. 검은 허공 앞에서는 보이지
않았지만 밝은 허공 앞에서는 푸르스름한 회색 얼룩으로 "녹아" 보였다(작전 4·5·10의 허공 중 4–5 %).

`void_fill_px`(작전 10은 28)는 그 반지름의 두 배보다 좁은 통로로만 경계와 이어진 허공을 불투명으로 돌린다. 결과
(`void_mask_fill.json`, 도구 `tools/mask_fill_stats.py`):

- 작전 10 마스크의 허공 2,887,482픽셀(마스크 해상도) 중 118,031(4.09 %)이 불투명으로 돌아갔다. 판별 0.94 %(C06) ~ 9.77 %(C05).
- 새로 투명해진 픽셀 0. 다른 작전의 판 135장은 바이트 동일.
- 캡처에서 벽이 그린 그대로 나오는 것을 확인했다(C05, R05, R01 가장자리).

접촉 그림자 방식(`contact_shadow_px`)은 새벽 바다처럼 밝은 허공에 쓰는 기존 답이고 그대로 두었다. 허공을 나중에 밝히는 다른
작전은 판 벽을 같은 눈으로 봐야 한다.

## 5. FPS A/B (허공 배경 하나만)

같은 창, 같은 세션에서 이전(HEAD) 셰이더·행과 새 셰이더·행을 번갈아(변형 순서는 라운드·장면마다 돌려) 쟀다. 1080p, 수직동기
끔, RTX 4070 SUPER, `gl_compatibility`, 5라운드 × 장면 2(C05, R05) × 3초(변형당 10표본). 판·연무·카메라는 공유하고 허공 한 장만
다르다(`tools/null_ab.gd`, 결과 `fps_ab.json`).

| | FPS | 프레임 ms | GPU ms |
|---|---|---|---|
| 이전 | 213.1 | 4.764 | 2.153 |
| 이후 | 214.8 | 4.674 | 2.147 |

차이 없음(이 PC의 부하 변동 안쪽이다: 같은 변형의 표본 하나가 148–230 fps를 오갔다). 이것은 허공 배경만의 비교이고 작전
10 전체의 FPS가 아니다(작전별 도구는 없다).

## 6. 시험

러너(`python tools/maintenance/run_regression_suite.py`)를 커밋 `e97fb6ac` 위의 작업 트리(이 변경 포함)에서 돌렸다. 실행 폴더는
git 무시인 `qa/regression_runs/`이고, 러너의 `qa/` 보호 검사(기존 파일이 바뀌거나 사라지거나 늘면 실패)를 통과했다.

- 빠른 묶음 44개: **44/44 PASS**, 503초(`20261002_193208_quick`). 이 변경이 닿는 것: `mood_light`(`--check`, 150판·788풀·150
  허공 마스크·15 접촉 그림자가 최신), `mood_contact`(13개, `VoidFill`·`NullAbyssLit` 포함), `campaign_data`(292), `plate_axis`,
  `seam_waiver`, `boss_room_fairness`.
- `battle_geometry`(전체 묶음 전용; 판이 미션 행을 따르는지, 허공 마스크, 연결 축, 허공 배경): **PASS (5,039 checks)**
  (`20261002_194153_custom`).
- 변형 시험: 허공 행을 이전의 검정 행으로 되돌리면 `NullAbyssLit`이, `void_fill_px`를 빼면 `VoidFill`이 실패한다.
- 전체 묶음(73개, 약 90분)은 돌리지 않았다. 바뀐 것은 허공 셰이더(헤드리스는 그리지 않는다)·행·마스크 JSON·마스크 도구뿐이고 그것을
  읽는 시험은 위 묶음에 모두 들어 있다. 시험 기준은 낮추지 않았고 시험을 빼지도 않았다.
- 셰이더가 실제 렌더러에서 컴파일되고 그려지는 것은 시험이 아니라 창 모드 캡처(3절)와 A/B(5절)로 확인했다.

## 7. 주장하지 않는 것

- 그림 승인: 판·보스·허공의 모습이 마음에 드는지는 사용자의 눈이다. 시험은 크기·이음매·밝기 같은 기술 기준만 본다.
  **사용자 승인(2026-10-02)**: 보고와 전/후 비교판(`before_after_sheet_1920x1684.png`)을 본 사용자가 "승인한다"고 답했다. 이 승인은
  밝힌 작전 10 `null` 허공 모습만 뜻한다. 다른 작전의 첫 방 허공(0.028–0.046), 균형, 플레이는 이 승인에 들어 있지 않다. 작전 10의
  판 15장과 ORIGIN CORE의 그림은 같은 날 사용자가 "판·보스 그림까지 승인"으로 따로 승인했다(`qa/site7_op10_art_approval_20261002/`). 행 값이나 `null` 셰이더 상수를 나중에 바꾸면 사용자가 다시 봐야 한다.
- 균형, 사람 플레이, 작전 전체 FPS.
- 허공의 취향(색, 격자, 붉은 점의 세기): 행 값 몇 개와 셰이더 상수 몇 개로 바로 바뀐다.
- 1080p 증거 검증기(`visual_evidence_1080p.json`)의 PASS는 컨테이너 해상도와 디코딩만 뜻한다.

## 8. 다시 만드는 법

```
git show e97fb6ac:scripts/missions/site7_abyss_backdrop.gd > .cache/null_abyss/abyss_old.gd
godot --path . -s res://qa/site7_null_abyss_20261002/tools/capture_abyss_pairs.gd -- --out=res://.cache/null_abyss/after --mission=MIS_CH01_10
python qa/site7_null_abyss_20261002/tools/void_stats.py .cache/null_abyss/after
godot --path . -s res://qa/site7_null_abyss_20261002/tools/null_ab.gd -- --out=res://.cache/null_abyss/null_ab.json --old=res://.cache/null_abyss/abyss_old.gd
git show e97fb6ac:data/visual/site7_void_masks.json > .cache/null_abyss/void_masks_before.json
python qa/site7_null_abyss_20261002/tools/mask_fill_stats.py --before=.cache/null_abyss/void_masks_before.json --after=data/visual/site7_void_masks.json --out=.cache/null_abyss/void_mask_fill.json
```

Godot는 창 모드로 한 번에 하나만 돌린다. 출력은 프로젝트의 git 무시 폴더 `.cache/`에 둔다(C 드라이브에는 쓰지 않는다).
