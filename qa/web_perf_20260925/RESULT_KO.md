# 웹 전투 FPS 개선 — 2026-09-25

로컬에서만 확인했다. 배포하지 않았다(GitHub Pages 등 외부 게시 없음). 이전 기록은 `qa/web_fps_20260925/`.

## 1. 뜨거운 wasm 함수 이름 찾기 (`wasm_function_names.json`)
- 이름 정보가 있는 wasm을 먼저 찾았지만 이 컴퓨터에는 없다.
  - 4.7.1 웹 템플릿 두 개(`web_nothreads_debug.zip`, `web_nothreads_release.zip`) 모두 name 섹션이 없다.
  - 4.7.2 `web_dlink_*` 템플릿의 side 모듈에는 내보내기 이름이 있지만, 엔진 버전이 다르고 배포 wasm과 다른 바이너리다.
  - 이름을 남긴 템플릿을 만들려면 Emscripten SDK를 내려받아 엔진을 빌드해야 한다. 외부 바이너리를 내려받지 않는다는 조건 때문에 하지 않았다.
- 대신 배포한 wasm 자체를 정적으로 분석했다. 로컬 release 템플릿의 `godot.wasm`은 배포한 `index.wasm`과 바이트까지 같다(SHA-256 `35116f68…`).
  - 함수 본문을 디코딩해 `i32.const` 주소를 데이터 세그먼트의 C 문자열로 바꿨다. 오류 매크로가 남기는 파일·함수 이름, 시그널 이름, 설정 이름이 나온다.
  - import 호출은 JS 글루의 `wasmImports` 표로 이름을 붙였다. 직접 호출 관계를 따라갔다.

| wasm 함수 | 정체 | 근거 |
|---|---|---|
| 2238 (자기 시간 38.8%) | `GDScriptFunction::call` — GDScript 인터프리터 루프 | gdscript_vm 오류 문자열, 154칸 opcode 분기표, 본문 56.6 KB |
| 43559 | `GDScript::callp` (정적 함수 호출) | "Can't call non-static function", 2238 호출 |
| 18792 / 21616 | `Main::iteration` / 웹 메인 루프 콜백 | "Project FPS: %d", 캔버스 크기 갱신 |
| 65213 / 65205 | `SceneTree::physics_process` / `process` | "physics_frame", "process_frame" |
| 67307 / 67306 | `RasterizerCanvasGLES3::request_polygon` / `free_polygon` | 함수 이름 문자열, glGenVertexArrays·glDeleteVertexArrays |
| 19098 ← 3148 | `canvas_item_add_polygon` ← `CanvasItem::draw_polygon` | 함수 이름 문자열 |
| 19109 ← 24112 | `canvas_item_add_polyline` ← `draw_polyline` (`draw_arc` 포함) | 함수 이름 문자열 |
| 9311 ← 24122 | `canvas_item_add_ellipse` ← `draw_ellipse` (`draw_circle`) | 함수 이름 문자열 |
| 65926 | `CanvasItem::_redraw_callback` | "_draw", MessageQueue flush에서 호출 |
| 67327 | `RasterizerGLES3` 초기화 | glGetIntegerv/glGetFloatv/glGetInteger64v를 부르는 유일한 함수 |

- 결론: 웹 메인 스레드의 가장 큰 몫은 GDScript 실행이다. 다각형 VAO·버퍼는 `_draw`가 다시 불릴 때마다 모두 새로 만들어진다.

## 2. 매 프레임 `getParameter`의 호출처
- 엔진(`glGetIntegerv`)은 시작할 때 한 번만 부른다(함수 67327).
- 매 프레임 부르는 곳은 Emscripten의 `GL.blitOffscreenFramebuffer`다. 화면 밖 프레임버퍼를 캔버스로 복사하는 함수로, 프레임마다 한 번 돈다.
  - `gl.getParameter(3089)`(SCISSOR_TEST)와 `gl.getParameter(36006)`(FRAMEBUFFER_BINDING)을 읽는다.
  - Chromium에서 SCISSOR_TEST를 `getParameter`로 읽으면 GPU 프로세스와 동기식으로 한 번 왕복한다. `isEnabled`는 클라이언트 쪽 상태로 같은 값을 돌려준다.
  - FRAMEBUFFER_BINDING은 WebGL이 가진 바인딩 객체를 그대로 돌려준다.
- 고침: `tools/environment/build_sites_demo.py`의 `patch_frame_blit()`가 내보낸 `index.js`에서 `var prevScissorTest=gl.getParameter(3089)`을 `gl.isEnabled(3089)`로 바꾼다.
  - 정확히 한 번 나오지 않으면 빌드를 멈춘다. 엔진이나 Emscripten 버전이 바뀌면 다시 확인해야 한다.

## 3. 바꾼 것
모든 변경은 같은 입력에 같은 결과를 내도록 했다. 계산을 건너뛰는 조건은 결과가 바뀔 수 없는 경우로만 잡았다.

### 3-1. 물리 틱마다 도는 GDScript (웹 VM 시간의 대부분)
- `CombatHitGeometry.hit_point`: 선분의 경계 상자가 사각형에서 1 px 넘게 떨어져 있으면 바로 "안 맞음"을 돌려준다.
  - 교차 판정의 허용 오차보다 넓은 여유다. 네 변 검사는 배열을 만들지 않고 풀어서 같은 순서로 한다.
- `Site7EnvironmentProp`: 이미지와 바닥 발자국의 월드 경계 상자를 global_transform이 바뀔 때만 다시 계산한다.
  - `projectile_hit`는 탄도가 이미지 상자(2 px 여유)에 닿지 않으면 알파 샘플링 전에 끝낸다.
  - `ground_world_rect()`는 CoverNavigation이 매번 만들던 발자국 사각형을 캐시에서 준다.
- `Site7Battlefield.is_walkable / segment_walkable`: 바닥 다각형과 경로 캡슐마다 경계 상자(2 px 여유)를 한 번 만들어 둔다. 상자 밖이면 정밀 검사를 건너뛴다.
- `CoverNavigation._plan`: 전투 바닥 위에서는 고정 노드(웨이포인트, 엄폐물 모서리)와 그 이웃 목록, 쌍별 가시성을 캐시한다. 캐시 키와 비우는 시점은 기존 간선 캐시와 같다.
  - 다익스트라는 기존과 같은 순서로 노드를 고른다(거리가 같으면 낮은 번호). 간선도 같은 순서로 검사하고 캐시한다.
  - 전투 바닥 밖에서는 기존 전체 탐색을 그대로 쓴다.

### 3-2. 매 프레임 다시 그리던 노드 (다시 그릴 때마다 다각형마다 VAO와 버퍼를 새로 만든다)
- `EnemyGroundShadow`: 적 종류가 바뀔 때만 다시 그린다.
- `OperatorGroundShadow`: 조종 중이거나 쓰러진 대원의 링은 애니메이션이라 매 프레임 그린다. 나머지 대원은 속도 비율, 색, 상태가 바뀔 때만 그린다.
- `TacticalMinimap`: 두 층으로 나눴다.
  - 격자와 바닥 판은 투영(확대, 초점, 밝힌 방, 크기)이 바뀔 때만 그린다.
  - 맥동하는 목표, 적, 대원 표시는 자식 `Markers` 층이 매 프레임 그린다. 그리는 순서는 전과 같다.
- `CinematicFieldOverlay`(비네트): 크기에만 의존하는데 매 프레임 테두리 10개와 원 14개를 다시 만들고 있었다. 이제 크기가 바뀔 때만 그린다.
- `StoryStageHUD`:
  - 스킬 칸 테두리색을 매 프레임 같은 값으로 다시 넣고 있었다. 그러면 StyleBox가 `changed`를 보내 패널 세 개가 매 프레임 다시 그려졌다. 이제 값이 다를 때만 넣는다.
  - 탄약 숫자와 X 스킬 글자색도 같은 방식으로 매 프레임 다시 넣어 글자를 다시 조판하고 있었다. 이제 다를 때만 넣는다.
  - 재장전 아이콘은 진행률이 바뀔 때만 그린다.
- `OperatorVisual`: 링은 선택 상태와 색에만 의존한다. 이제 총구 섬광이 보이는 동안과 그 섬광이 사라지는 프레임에만 다시 그린다.
  - 지금 세 대원은 모두 Motion Lab 런타임을 쓴다. 이 런타임이 이 노드의 modulate 알파를 0으로 둔다(`motion_lab_character_runtime.gd:133`). 그래서 이 링과 섬광은 원래 화면에 보이지 않고, 보이지 않는 그리기 비용만 줄였다.
- `PrototypeProjectile`: ASTER 탄의 광원 그라디언트 텍스처를 탄마다 새로 만들고 있었다.
  - 새 텍스처가 생길 때마다 렌더러의 2D 광원 아틀라스를 다시 만들었다(`checkFramebufferStatus`).
  - 이제 같은 설정의 텍스처 하나를 모든 탄이 함께 쓴다. 텍스처 픽셀은 같다.

### 3-3. 웹 전용
- 2절의 `getParameter(3089)` → `isEnabled(3089)` 패치.

## 4. 웹 측정 (같은 세션, 순서를 돌린 A/B)
- 환경: Edge(ANGLE D3D11), RTX 4070 SUPER, 1920x1080, 전용 DevTools 포트(9333이 아닌 임의 포트, 각 JSON의 `devtools_port`). 디스플레이가 100 Hz라 rAF는 100 fps에서 멈춘다.
- 흐름은 `qa/web_fps_20260925`와 같다(`tools/web_fps_ab.py`).
  - 타이틀에서 4초를 잰다. 작전 1에 배치하고 8초 기다린다.
  - 전투 10초: 조종 대원(ASTER)을 WASD로 움직이며 클릭으로 연사하는 약 11초 가운데 마지막 10초.
  - 뒤 6초: 그다음 입력 없이 선 채로 AI 대원들이 싸우는 6초.
- 빌드는 모두 로컬 `http.server`(127.0.0.1)로 제공했다. 최종 URL: `http://127.0.0.1:8801/index.html`(기존 배포본), `…:8805/index.html`(new2), `…:8806/index.html`(최종).

| 빌드 | 내용 |
|---|---|
| base | 기존 배포 빌드(`web_demo/dist`, e76cfea00의 기록) |
| blitfix | base + 2절 패치만 |
| scripts | 3-1 + 그림자·미니맵 변경, 패치 없음 |
| new | scripts + 패치 |
| new2 | new + 비네트·HUD·OperatorVisual |
| 최종 | new2 + ASTER 광원 텍스처 공유 (커밋하는 코드) |

### 유효한 측정의 조건을 바꿨다
- 이전 규칙은 "전투 FPS < 90"이었다. 메뉴에 머문 측정이 제한 없는 FPS를 보이기 때문이었다.
- 새 빌드는 전투에서도 100 Hz 한도 근처까지 올라가서, 이 규칙이 전투 중이던 측정(91.5, 94.9 fps)을 무효로 버렸다. 캡처에는 전투 HUD와 F9 FPS가 보였다.
- 새 규칙: 전투 1920x1080 캡처의 대원 카드 영역(36,816)-(520,1056)이 기준 전투 캡처와 평균 절대 차 12 이하여야 한다. 전투 캡처는 0.0–1.9, 메뉴·인트로 캡처는 약 40이었다. 준비 완료와 URL 유지 조건은 그대로다.
- 앞의 두 A/B도 이 규칙으로 다시 요약했다(`*_revalidated` 내용을 담은 파일, 행마다 `fps_rule_valid`와 `field_region_mad`).

### A/B 3 — 최종 (`web_fps_ab_3_base_new2_final.json`, 4라운드, 12회 모두 유효)
| 빌드 | 전투 10초 FPS 중앙값 (각 회) | 뒤 6초 중앙값 | 전투 10초 p95 프레임 시간 |
|---|---|---|---|
| base | **14.1** (14.0, 13.0, 21.8, 14.2) | 17.2 | 80–180 ms |
| new2 | 71.4 (65.2, 65.8, 77.0, 81.9) | 96.5 | 20–30 ms |
| 최종 | **78.2** (80.8, 75.5, 69.2, 85.4) | 93.9 | 20 ms |

- 같은 세션에서 최종 빌드의 전투 FPS는 base의 약 5.5배다. 뒤 6초는 100 Hz 한도에 거의 닿아서 빌드 차이를 가리지 못한다. 이동 중인 전투 10초가 차이를 보여 준다.
- new2와 최종의 차이(71.4 대 78.2)는 회차 사이 편차(65–86) 안에 있다. ASTER 텍스처 변경의 효과는 5절의 프로파일로 확인했다.

### A/B 1·2 (같은 날 앞선 세션)
| A/B | 빌드 | 유효 | 전투 10초 중앙값 | 뒤 6초 중앙값 |
|---|---|---|---|---|
| 1 | base | 3/4 | 12.8 | 16.0 |
| 1 | blitfix | 3/4 | 36.7 | 43.0 |
| 1 | scripts | 4/4 | 46.9 | 66.8 |
| 1 | new | 4/4 | 73.8 | 95.4 |
| 2 | base | 4/4 | 24.4 | 23.4 |
| 2 | new | 4/4 | 77.5 | 97.3 |
| 2 | new2 | 4/4 | 89.3 | 98.5 |

- A/B 1의 1라운드 base·blitfix는 컴퓨터가 바빠 메뉴 클릭이 빗나가 전투에 들어가지 못했다(캡처 차 39–43). 규칙대로 뺐다.
- 패치만 넣은 blitfix는 base의 약 2.9배, 스크립트 변경만 넣은 scripts는 약 3.7배다. 둘을 합친 new는 약 5.8배다.
- base의 절대값은 세션마다 12.8–24.4로 흔들렸다. 같은 세션 안의 비교만 의미가 있다.

### 매 프레임 WebGL 호출 수 (`web_gl_counts_*.json`, 전투 뒤 6초 평균)
| 빌드 | createVertexArray | createBuffer | bufferData | getParameter | isEnabled |
|---|---|---|---|---|---|
| base (네 번 측정) | 270.7–276.7 | 389.7–398.1 | 404.5–414.8 | 2 | 0 |
| new (두 번) | 106.8–108.4 | 154.0–157.4 | 168.7–171.8 | 1 | 1 |
| new2 | 73.6 | 103.8 | 118.7 | 1 | 1 |
| 최종 (두 번) | 72.9–115.7 | 102.8–164.7 | 117.5–178.3 | 1 | 1 |

- 지우는 수(deleteVertexArray, deleteBuffer)는 만드는 수와 같다.
- 최종 빌드의 첫 측정(base 272.6 / 최종 72.9)은 실행 출력에만 남았다. 그 JSON은 호출 종류를 늘린 두 번째 측정(base/new2/최종)으로 덮어썼다.
- 남은 VAO는 매 프레임 움직이는 것들(적중 효과, 표적 표시, 조준선, 바닥 안내, 적 머리 위 표시)이다. 화면에 떠 있는 적중 효과 수에 따라 달라지므로 최종 빌드의 두 측정이 72.9와 115.7로 갈렸다.
- 남은 `getParameter` 한 번은 blit의 `getParameter(36006)`(FRAMEBUFFER_BINDING)다. WebGL이 가진 객체를 돌려주므로 GPU 왕복이 없다.
- 마지막 측정(base/new2/최종)에서는 `checkFramebufferStatus`, `framebufferTexture2D`, `texImage2D`도 셌다. 이 6초에는 세 빌드 모두 `checkFramebufferStatus`가 0이었다. 이 구간에는 ASTER가 쏘지 않는다. `texImage2D`는 세 빌드 모두 프레임당 6–8회로 같다. 이번 변경과 무관하며 출처는 조사하지 않았다.

## 5. 웹 프로파일 (`web_profile_compare.json`, `web_profile_*_summary.json`)
- `web_profile.py`: 전투 진입 뒤 이동하며 연사하는 약 16초를 0.5 ms 간격으로 샘플링했다. 빌드마다 한 번씩 측정했다.
- 비율은 측정 시간 대비다. 프레임당 시간은 비율 × (1000 / 그 측정의 FPS)로 어림했다.

| 함수 | base (19.7 fps) | new (81.8 fps) | 최종 (71.5 fps) |
|---|---|---|---|
| GDScript VM (2238) 자기 / 포함 | 39.0% / 70.6% | 18.4% / 51.5% | 22.5% / 59.4% |
| SceneTree::physics_process 포함 | 62.2% (≈31.6 ms/프레임) | 23.7% (≈2.9 ms) | 30.0% (≈4.2 ms) |
| CanvasItem::_redraw_callback 포함 | 8.2% (≈4.2 ms) | 21.4% (≈2.6 ms) | 20.6% (≈2.9 ms) |
| getParameter | 18.4% (≈9.3 ms) | 0.0% | 0.0% |
| checkFramebufferStatus | 0.4% | 2.6% | **0.0%** |
| 유휴 | 0.1% | 17.3% | 9.6% |

- base는 메인 스레드가 쉬는 시간이 없었다. 새 빌드는 유휴 시간이 생겼다.
- `checkFramebufferStatus` 2.6% → 0.0%: new에서는 ASTER 탄마다 새 광원 텍스처가 2D 광원 아틀라스를 다시 만들고 있었다. 최종 빌드에서는 사라졌다.
- 프로파일은 한 번씩이라 그때의 부하와 전투 상황에 따라 흔들린다. new와 최종의 차이가 그렇다. FPS 비교의 근거는 4절의 A/B다.

## 6. 네이티브 측정 (`native_ab.json`)
- 도구: `tools/native_ab.py`, `tools/perf_op1.gd`. 같은 세션에서 4라운드, 라운드마다 순서를 바꿨다.
  - old: 바꾼 스크립트 11개의 HEAD(e76cfea00) 판. new: 작업본.
  - 끝난 뒤 작업본을 바이트 그대로 되돌렸고, 스크립트가 확인했다.
- `perf_op1.gd`: 작전 1 R02 전투 미리보기. 대원은 AI로 싸운다. 30초, 1920x1080 창, vsync 끔, FPS 제한 없음. 첫 5초를 빼고 5초 단위 FPS 4개씩 모았다.

| 판 | 표본 | FPS 중앙값 | 범위 | 물리 모니터 중앙값 | 스크립트 오류 |
|---|---|---|---|---|---|
| old | 16 | 72.8 | 43.1–94.7 | 23.7 ms | 0 |
| new | 16 | **137.1** | 106.0–184.5 | 7.9 ms | 0 |

- 네이티브에서도 약 1.9배다. 모든 new 표본이 모든 old 표본보다 빠르다.
- 물리 모니터는 Godot `TIME_PHYSICS_PROCESS`의 5초 평균이다. 상대 비교로만 본다.

### 다시 그리기 횟수 (`redraw_census.json`, `tools/census_ab.py`, `tools/redraw_census.gd`)
- 같은 전투에서 `draw` 신호를 스크립트별로 셌다. old와 new를 차례로 실행했다.
- 프레임당 다시 그리기: **42.2 → 26.0**.

| 스크립트·클래스 | old | new |
|---|---|---|
| Panel (스킬 칸 세 개) | 3.00 | 0 |
| operator_visual.gd | 3.00 | 0.69 |
| operator_ground_shadow.gd | 3.00 | 1.07 |
| enemy_ground_shadow.gd | 2.94 | 0.00 |
| Label | 1.04 | 0.02 |
| tactical_minimap.gd (바닥 층) | 1.00 | 0 |
| cinematic_field_overlay.gd | 1.00 | 0 |
| combat_hit_vfx.gd | 6.11 | 6.87 |
| site7_machine_sprite.gd / premium_enemy_presentation.gd / enemy_overhead_ui.gd | 약 2.8–3.0 | 약 2.8–3.0 |
| battle_reticle.gd / site7_floor_guide.gd / boss_arena_presentation.gd | 1.00 | 1.00 |

- 아래 네 줄은 매 프레임 움직이는 그림이라 그대로 두었다.
- 바꾸지 않은 스크립트의 수치(enemy_actor.gd 2.02 → 1.13 등)는 게임 시간에 따라 다시 그리는 노드들이다. FPS가 오르면 프레임당 비율이 떨어진다.

## 7. 화면이 같은지 확인
### 7-1. 캐시한 그림 = 새로 그린 그림 (`redraw_equivalence.txt`, `tools/redraw_equiv.gd`)
- 방법:
  - 작전 1 R02 실전투(대원 AI) 중 40프레임마다 물리 단계가 시작될 때 트리를 멈춘다. 모두 40회.
  - 직전 프레임에 다시 그리지 않은 CanvasItem, 곧 캐시한 그림을 보여 주는 노드를 모은다.
  - 스크립트(없으면 클래스)별로 묶어, 한 묶음씩 현재 상태에서 다시 그리게 한다.
  - 묶음마다 1920x1080 프레임을 받아 직전 프레임과 바이트 단위로 비교한다.
  - 같다는 것은 그 노드들의 캐시한 그림이 "매 프레임 다시 그리기"(이번에 없앤 동작)가 보여 줄 그림과 같다는 뜻이다.
- 결과: **40/40 표본에서 차이 0**. 43개 묶음에서 17,872회 다시 그렸다. 멈춘 동안 두 프레임은 40/40 같았다.
- 바꾼 노드가 모두 캐시 상태로 검사됐다(표본 40회 동안의 합):

  | 노드 | 검사 횟수 |
  |---|---|
  | cinematic_field_overlay.gd | 40 |
  | tactical_minimap.gd(바닥 층) | 40 |
  | enemy_ground_shadow.gd | 135 |
  | operator_ground_shadow.gd | 78 |
  | operator_visual.gd | 89 |
  | prototype_projectile.gd | 117 |
  | site7_environment_prop.gd | 600 |
  | HUD Panel(스킬 칸 포함) | 400 |
  | Label | 1130 |
  | 재장전 아이콘 등 내부 클래스(스크립트 경로 없음) | 719 |

- 음성 대조(`redraw_equivalence_negative_control.txt`): 표본마다 AI 대원의 속도를 그림자 모르게 바꿨다. 캐시 키가 빠졌을 때와 같은 상황이다. 40/40 표본에서 `operator_ground_shadow.gd`만 차이로 잡혔다. 속도는 표본을 마친 뒤 되돌렸다.
- 첫 설계는 모든 CanvasItem을 다시 그리게 했고, 28/40 표본에서 달랐다.
  - 원인은 이번에 건드리지 않고 매 프레임 그리는 노드였다. 적중 효과는 불꽃 위치가 무작위고, 조준선은 그릴 때 실시간 마우스 위치를 읽는다.
  - 이 노드들은 전에도 지금도 매 프레임 그려서 캐시 대상이 아니다. 그래서 직전 프레임에 그리지 않은 노드만 검사하도록 바꿨다.

### 7-2. 미니맵 (`minimap_equivalence.txt`, `tools/minimap_equiv.gd`)
- HEAD의 한 층 미니맵(class_name만 지운 사본)과 새 두 층 미니맵을 같은 실전투에 붙였다. 각각 190x106 SubViewport에서 2000프레임 동안 그렸다.
  - 확대·축소와 그 보간, 확대 상태에서 이동, 전체 보기에서 이동을 포함한다.
- 4프레임마다 비교해 **495/495 같음, 최대 채널 차 0**. 비교 가운데 315회는 새 바닥 층이 캐시 상태였다(이동 중 25회).

### 7-3. ASTER 광원 텍스처 (`aster_light_texture_check.txt`)
- 두 탄의 광원이 같은 텍스처를 쓰고(shared=true), 그 픽셀이 커밋된 코드가 탄마다 만들던 텍스처와 같다(same_pixels=true).

### 7-4. 물리 빠른 경로 (`tests/smoke/combat_query_fastpath_smoke.gd`, 회귀 러너 quick에 등록)
- 작전 1·3·5의 실제 바닥, 엄폐물, 배우에서 빠른 경로와 교체 전 코드의 원문 사본을 비트 단위로 비교한다. 31개 검사가 통과했다.
- 대상:

  | 함수 | 호출 수 |
  |---|---|
  | `hit_point` | 15,600 |
  | `is_walkable` | 12,924 |
  | `segment_walkable` | 6,000 |
  | `projectile_hit` | 2,460 |
  | `_plan` | 324 (경로가 있는 것 251) |

### 7-5. 1080p 캡처 (`web_op1_field_base_1080p.png`, `web_op1_field_final_1080p.png`, `visual_evidence_1080p.json` PASS)
- A/B 3의 4라운드 전투 캡처다. 두 장 모두 전투 HUD가 보이고, F9 표시는 base FPS 9, 최종 FPS 89다.
- 같은 순간이 아니므로 같은 그림인지 비교하는 근거는 아니다. 그 근거는 7-1과 7-2다.
- 검증기 PASS는 1920x1080 원본 컨테이너라는 뜻일 뿐, 화질 판정이 아니다.

## 8. 빌드 기록 (`web_build/`)
- `python tools/environment/build_sites_demo.py --scripts-only --qa=qa/web_perf_20260925/web_build`. 출력은 git이 무시하는 `web_demo/dist`에 있다.
- `index.pck` 210,531,420 B, SHA-256 `d4ef04b298e6a4dd16749b465771fa17f5c1e45e2d2b995d810bac9508937b3d` (`web_build/chunks.json`).
- `index.wasm` 39,513,091 B, SHA-256 `35116f68…`. 엔진 템플릿 그대로라 기존 배포본과 같다.
- `index.js`만 `patch_frame_blit()`로 한 줄 바뀐다.
- `DEMO_PACKED_ASSETS` pass(`web_build/packed_assets.log`).
- 배포하지 않았다. 배포는 사용자 승인 뒤에 한다.

## 9. 남은 기회 (이번에 하지 않은 것)
- 미니맵 바닥 층은 확대 상태에서 부대가 움직이면 초점이 따라가서 매 프레임 다시 그린다.
  - 바닥을 옮겨 다니는 자식 노드로 두면 다시 그리지 않아도 된다.
  - 하지만 좌표의 부동소수 반올림 순서가 달라져 픽셀이 비트 단위로 같지 않다. 그래서 하지 않았다.
- 매 프레임 움직이는 그림(적중 효과, 표적 표시, 조준선, 바닥 안내, 적 머리 위 표시, 적 기계 스프라이트)은 여전히 그릴 때마다 VAO와 버퍼를 만든다.
  - MultiMesh나 텍스처로 바꾸면 줄일 수 있다. 모양이 바뀔 위험이 있어 이번 범위에서 뺐다.
- `texImage2D` 프레임당 6–8회의 출처는 조사하지 않았다.
- GDScript VM은 여전히 가장 큰 몫이다(자기 시간 18–23%).
- 이름 있는 wasm은 Emscripten으로 엔진을 직접 빌드해야 얻는다(1절).

## 10. 측정 조건과 한계
- 측정하는 동안 이 PC는 다른 앱(Edge, ChatGPT, Codex, Claude 등)으로 CPU를 약 61% 쓰고 있었다.
- 18:01 무렵에는 다른 세션이 본 체크아웃에서 회귀 검사를 돌렸다.
- 그래서 절대 FPS는 부하에 따라 흔들린다(base 전투 10초 중앙값이 세션마다 12.8–24.4). 근거로 삼은 것은 같은 세션 안에서 순서를 돌린 비교뿐이다.
- 디스플레이가 100 Hz라 웹 FPS는 100에서 멈춘다.
- 스크립트로 조작한 측정이다. 사람의 플레이 테스트나 밸런스 승인이 아니다.

## 11. 회귀 검사
`python tools/maintenance/run_regression_suite.py`로 돌렸다. 결과 폴더는 git이 무시하는 `qa/regression_runs/`에 있다.

| 실행 | 결과 | 폴더 |
|---|---|---|
| quick (1차) | PASS 26/26 | `20260925_184210_quick` |
| full (1차) | **FAIL 44/45**: `cover_ai` 60 Hz 추종 검사 | `20260925_184616_full` |
| quick (최종) | PASS 26/26 | `20260925_194445_quick` |
| full (최종) | PASS 45/45 (1790초, 플레이스루 5개와 Motion Studio Python/JS 포함) | `20260925_194854_full` |

- 새 스모크 `combat_query_fastpath`(31 체크)를 러너의 quick 묶음에 넣었다(`tests/smoke/combat_query_fastpath_smoke.gd`).
  - 실제 작전 바닥, 엄폐물, 대원에서 빠른 경로가 바꾸기 전 코드(e76cfea00 사본)와 비트 단위로 같은 답을 내는지 확인한다. 대상은 적중 판정, 알파 투사체 차단, 바닥 걷기 판정, 엄폐물 발자국, 엄폐 경로 계획이다.
- 1차 full의 `cover_ai` 실패("Follower bypasses cover and stops at hostile body at 60Hz (gap=212.49)"). 자세한 기록은 `cover_ai_teleport_ride.txt`.
  - 보통 타이밍에서는 새 스크립트가 3/3 실패하고 HEAD 스크립트는 3/3 통과했다(`tools/coverai_bisect.py`).
  - `--fixed-fps 60`으로 프레임 타이밍을 고정했다. 이때 엄폐 경로 계획 기록이 새 스크립트와 HEAD에서 2664줄 모두 같고, 둘 다 똑같이 실패했다(gap 201.18, `tools/coverai_trace.py`). 성능 변경이 결과를 바꾼 것이 아니다. 테스트 결과가 프레임 타이밍에 달려 있었다.
  - 원인(`tools/cover_ai_probe.gd`):
    - 대원과 로봇은 기본값인 GROUNDED 모드의 `CharacterBody2D`다.
    - 앞 단계 끝에서 대원이 드론에 닿으면, 그 드론이 대원의 "바닥"(움직이는 발판)으로 기록된다.
    - 테스트의 `reset_positions()`가 드론을 순간이동시킨다. 물리 서버는 다음 한 스텝 동안 그 이동을 드론의 속도로 알린다(약 (8991, 9279) px/s).
    - 대원이 바로 그 스텝에 움직이면 드론의 순간이동을 발판처럼 타고 약 200 px 튄다.
    - HEAD는 느린 프레임에서 물리 스텝이 두 번 돌아 드론 속도가 0으로 돌아간 뒤에 움직일 때만 통과했다. 스크립트가 빨라져 프레임마다 물리 스텝이 한 번이 되자 매번 이 경로로 갔다.
  - 고침(테스트만, 게임 스크립트는 바꾸지 않음): `tests/render/site7_cover_ai_check.gd`의 `reset_positions()`가 순간이동 뒤 물리 프레임을 세 번 기다린다(이동 스텝 한 번, 정지 스텝 한 번). 호출하는 곳은 모두 `await`한다.
  - 고친 뒤 결과. 추종 결과 `[hz, 끝 거리, 옆 이동]`은 모두 `[30,34.9,59.0] [60,34.9,59.2] [120,34.9,59.2]`로 같다.
    - `--fixed-fps 60`: 새 스크립트와 HEAD 스크립트 모두 46/46 PASS.
    - 보통 타이밍 3회씩: 새 스크립트 3/3, HEAD 스크립트 3/3 PASS.
  - 남긴 것: 실제 플레이에서도 움직이는 로봇에 북쪽에서 닿은 대원이 같은 방식으로 끌려갈 수 있다. 고치려면 이동 방식(motion_mode 또는 platform 설정)을 바꿔야 해서 게임 동작이 달라진다. 그래서 이번 범위에서 빼고 따로 결정하도록 남겼다.

## 12. 파일
| 파일 | 내용 |
|---|---|
| `wasm_function_names.json` | 1절 정적 이름 찾기 결과 |
| `web_fps_ab_1_base_blitfix_scripts_new.json`, `web_fps_ab_2_base_new_new2.json`, `web_fps_ab_3_base_new2_final.json` | 4절 A/B. 1·2는 새 유효 규칙으로 다시 요약한 것 |
| `web_gl_counts_base_new.json`, `web_gl_counts_base_new2_final.json` | 4절 WebGL 호출 수 |
| `web_profile_compare.json`, `web_profile_{base,new,final}_summary.json` | 5절 프로파일 |
| `native_ab.json`, `redraw_census.json` | 6절 |
| `redraw_equivalence.txt`, `redraw_equivalence_negative_control.txt`, `minimap_equivalence.txt`, `aster_light_texture_check.txt` | 7절 |
| `web_op1_field_base_1080p.png`, `web_op1_field_final_1080p.png`, `visual_evidence_1080p.json` | 7-5절 |
| `web_build/` | 8절 빌드 기록 |
| `cover_ai_teleport_ride.txt` | 11절 `cover_ai` 실패 진단과 테스트 수정 |
| `tools/` | 이 기록을 만든 측정 스크립트 사본. 원본은 git이 무시하는 `.cache/`에 있다. `.gd`는 `.cache/diag/`에 두고 `-s res://.cache/diag/<이름>.gd`로 실행한다. `field_reference_1080p.png`는 유효 규칙의 기준 캡처다. |
