# SITE-7 배경 원화 전면 재제작 (맵 키트 v2) — Codex 작업 지시서

작성: 2026-09-27. 대상: 이 저장소에서 작업하는 Codex. 이 문서가 작업 지시의 본문이다.

Codex에 처음 보낼 메시지:

> `docs/production/SITE7_MAP_KIT_V2_CODEX_PROMPT_KO.md`를 끝까지 읽고 **단계 0(파일럿)** 만 진행해라. `AGENTS.md`를 먼저 읽고 그 규칙이 이 문서보다 우선한다. 단계 0이 끝나면 멈추고, 게임 안 1080p 캡처와 `audit_site7_plate_lighting.py` 결과를 보고해라.

---

## 0. 판정: 맵 배경 45장을 한 규격으로 전부 다시 만든다

부분 수정으로는 해결되지 않는다. 판 하나하나가 각자의 카메라, 축척, 조명으로 따로 그려졌다. 그래서 이어 붙이는 곳마다 어긋난다.

런타임 보정은 이미 한계까지 했다.
- 배치 풀이: `build_site7_world_layout.py`
- 바닥 마스크와 경계 흐림: `site7_room_art_layer.gd`
- 이음매 조명: `site7_seam_light.json`

그래도 원화 자체의 차이는 남는다.

측정 도구: `python tools/environment/audit_site7_plate_lighting.py`. 이 도구는 조명 보정 전의 원화 픽셀을 잰다.

| 문제 | 측정값 |
|---|---|
| 이음매(통로 끝이 방 바닥과 만나는 곳) | 42곳 중 39곳이 기준 밖이다. 밝기 차가 최대 1.6스톱(3배)이다. |
| 색조 충돌 | 통로 7장의 8곳에서 색조가 41–174° 어긋난다. 그중 7곳은 주황 데크와 청록 방처럼 120° 이상 반대색이다. 런타임 보정은 색조를 바꾸지 않으므로 고칠 수 없다. |
| 판 바닥 조명 | 45장 중 36장이 기준 밖이다. 원인은 방 색으로 물든 바닥(채도 최대 0.70), 바닥 위 검은 구멍, 과노출 조명 웅덩이다. |
| 카메라 | 바닥 축 기울기가 판마다 15°–32°로 제각각이다. 판별 런타임 배율(0.82 / 0.84 / 0.88 / 1.0)로 크기만 억지로 맞췄다. |
| 갈래 통로 | C06과 C07(갈래)은 좌우를 뒤집어 쓴다. 그래서 그려진 색 전환이 거꾸로 붙는다. 주황 끝이 청록 방에 닿는다. 원래 오르막으로 그렸기 때문이다. |
| 문 | 방에 문이 그려져 있지 않다. 통로 데크가 방의 벽 그림 위를 덮고 들어간다. 판 가장자리에는 비네트(어두워짐)와 검은 공간이 있다. |
| 크기 | 스테이지 2·3 통로 데크 폭은 110–175 px다. 대원 키가 129.6 px이니 한 사람 폭이다. 방 다수도 폭 160–240 px의 긴 복도 띠다. |

**유지하는 것**
- 작전 5개와 방 ID, 방 순서. 주 경로 방 6개, 갈래 방 2개, 통로 7개.
- 방마다의 이름과 테마. 적, 대원, 엄폐물(kArchive 소품) 아트.
- 런타임 판 시스템: 방 판과 통로 판, 바닥 마스크, 경계 흐림, 이음매 조명. 이음매 조명은 새 판에서도 남은 작은 차이를 보정한다.

**새로 만드는 것**
- 원화 45장: 스테이지 1은 작전 1용 15장, 스테이지 2는 작전 2용 15장, 스테이지 3은 작전 3·4·5가 함께 쓰는 15장이다.
- 새 원화에 맞춰 바닥 윤곽, 문 위치, 전투방 레이아웃, 엄폐물 위치, 배치 풀이를 다시 만든다.

**예상 생성량**: 판 45장 × 평균 2회 ≈ ImageGen 90회. 파일럿 3장은 따로 센다.

---

## 1. 반드시 지킬 규칙

원문은 `AGENTS.md`이고, 원문이 이 요약보다 우선한다.

**생성 도구**
- 원화는 Codex 내장 ImageGen으로만 만든다.
- 로컬 확산 모델, ComfyUI, 로컬 인페인팅, LoRA, ControlNet은 금지다.
- 참조 이미지는 이 저장소 안의 파일만 쓴다. 다른 프로젝트 파일, 클립보드, 관리 스테이징 경로는 쓸 수 없다. 단, 방금 받은 결과물은 예외다.

**결과물 반입**
- 결과물은 저장소로 옮긴다.
- SHA-256을 확인한 뒤 관리 스테이징 사본을 지운다.
- 로컬 디스크 규칙: C 드라이브에 백업, 캐시, 임시 파일을 만들지 않는다. 작업 파일은 git-ignore된 `.cache/`에 둔다.

**Git**
- GitHub push, PR, Pages, Actions 작업은 금지다. 커밋은 로컬에서만 한다.

**보존**
- 현재 후보와 바로 앞 후보 1개를 남긴다.
- 실패하거나 거절된 후보는 격리 폴더에 해시와 함께 보존한다. 지우지 않는다.
- v1 판은 v2가 모든 검증을 통과하고 사용자가 승인할 때까지 그대로 둔다. 코드와 메뉴가 참조하는 파일은 지우지 않는다.

**환경 판의 형식**
- 불투명 RGB로 만든다. 알파, 크로마 키, 초록 배경을 쓰지 않는다.
- 캐릭터용 네이티브 알파 규칙은 배경 판에 해당하지 않는다.

**원화 픽셀**
- 파생본(GAME)은 균등 크롭과 균등 축소로만 만든다. 늘이기, 부분 칠, 부분 보정은 금지다.
- 밝기나 색이 조금 모자라면 먼저 ImageGen 편집으로 다시 뽑는다.
- 예외로, 판 전체에 똑같이 적용되는 노출·화이트밸런스 한 번은 GAME 파생본에만 허용한다. 이때 매니페스트에 수치와 적용 전후 해시를 남긴다. MASTER는 그대로 둔다.

**증거 자료**
- 검토 이미지는 네이티브 1920×1080 이상이어야 한다.
- 모두 `tools/art_pipeline/validate_visual_evidence_1080p.py`로 검사한다.
- 이 검사의 PASS는 해상도와 디코딩만 보증한다. 화질 승인이 아니다.

**테스트와 기록**
- 테스트가 파일을 쓰면 `--out=res://.cache/...`를 준다. 날짜가 붙은 QA 폴더를 대상으로 테스트를 돌리지 않는다.
- 회귀 스위트가 도는 동안에는 `qa/` 아래에 쓰지 않는다.
- 플레이어의 세이브와 설정을 건드리지 않는다.

**기존 연결 규칙**
- `AGENTS.md`의 "Map connections, wall collision and ASTER gait" 절은 계속 지킨다. 이 절이 다루는 것:
  - 바닥 안쪽 여백
  - 문 앞 110 px 엄폐물 금지
  - 스폰 경로 20 px 여유
  - `settle_cover_on_floor.gd` 재정착
- 규칙이 바뀌는 부분(갈래 통로 반전, 문 앵커)은 이 문서 5절대로 코드와 `AGENTS.md`를 함께 고친다.

---

## 2. 맵 키트 v2 규격

모든 판은 이 규격을 따른다. 파일럿(단계 0)이 승인되면 그 결과가 이후 모든 생성의 화풍·조명 기준 이미지가 된다.

### 2.1 카메라와 투영

- 모든 판이 하나의 고정 카메라를 쓴다. 위에서 비스듬히 내려다보는 3/4 탑다운이고, 원근이 거의 없는 dimetric 투영이다.
- 바닥 판넬 이음새와 벽 밑선은 두 방향 모두 **2:1 기울기(수평에서 26.6°)** 로 달린다.
- 소실점 수렴, 어안, 기울어진 수평선은 금지다.
- 검사 기준: 실제로 추적한 바닥 윤곽의 길이 가중 평균 변 기울기가 22.5°–30.5° 안에 있어야 한다. `audit_site7_plate_lighting.py`의 `axis` 항목이다. **2026-09-30 사용자 승인: 판 ID가 C06·C07로 끝나는 ↘ 분기 통로만 22.5°–31.5°**를 적용한다(2:1 등각 26.6° ± 5°). 2026-10-01에 사용자가 이 상한을 **32.5°**로 올렸다(작전 9 S9_C06 3차 32.26°, 이미지 생성은 이 통로를 30.7–33.5°로 그린다). 그 밖의 판은 기존 상한 30.5°를 유지한다. 표준 윤곽으로 실제 윤곽을 대체하지 않으며, 양 끝 폭은 표준 왼쪽 332 px / 오른쪽 326 px의 ±15%, 색·구조·문 조건은 그대로 검사한다.

방향 이름(화면 기준):

| 이름 | 위치 | 쓰임 |
|---|---|---|
| NE | 오른쪽 위 | 주 경로가 나가는 쪽 |
| SW | 왼쪽 아래 | 주 경로가 들어오는 쪽 |
| SE | 오른쪽 아래 | 갈래가 나가는 쪽 |
| NW | 왼쪽 위 | 갈래 방으로 들어오는 쪽 |

- 벽: NW 변과 NE 변에만 뒷벽이 선다. SW 변과 SE 변은 낮은 턱이나 난간으로 끝나고 벽을 세우지 않는다. 바닥을 가리지 않게 하기 위해서다.

### 2.2 축척

- 런타임 배율은 모든 판이 **1.0**이다. 판별 배율로 크기를 맞추지 않는다.
- 기준은 대원이다. 서 있는 대원의 키는 게임에서 129.6 px다. 1536 px 너비 판에서는 **너비의 약 1/12**이다.
- 부위별 크기:
  - 바닥 판넬 한 칸: 대원 키 정도의 정사각형
  - 난간: 허리 높이(대원 키의 약 0.55배)
  - 문틀: 대원 키의 약 1.6배 높이
  - 문 너비: 대원 키의 약 2.3배(≈300 px)
- 축척 참조 이미지(축척 전용): `qa/map_gait_20260925/MIS_CH01_01_start.png`. 대원 3명, 드론, 바리케이드, 상자의 크기 관계가 목표다. 이 그림의 바닥 화풍과 글자는 따르지 않는다.
- 바닥 크기 최소치(런타임 px, 주축 × 부축):

| 종류 | 최소 크기 | 비고 |
|---|---|---|
| 전투방 | 1000 × 560 | |
| 전투 복도 | 1300 × 380 | 지금 290–350 폭보다 넓힌다. |
| 보스 | 1100 × 520 | |
| 비전투 방 | 850 × 450 | |
| 통로 데크 | 폭 260 이상, 보이는 길이 1200–1500 | 폭은 대원 두 명 이상 |

- 바닥은 그림 면적의 25% 이상이어야 하고, 판 테두리에서 8% 이상 안쪽에 있어야 한다. 런타임 바닥 안쪽 여백 7.5% 규칙 때문이다.

### 2.3 바닥과 조명 (수치 목표)

**바닥**
- 모든 판의 걷는 바닥은 같은 **SITE-7 표준 데크**다. 짙은 건메탈 강철 판에 가는 이음새와 약한 마모가 있다.
- 글자, 숫자, 로고, 잡동사니를 두지 않는다.
- 배수 격자와 글자 없는 안전선은 허용한다.

**바닥 조명**
- 바닥 위 조명은 **중성 백색(5500–6500K) 천장 조명 하나로 고르게** 한다.
- 조명 웅덩이, 검은 구멍, 비네트, 모서리 어두워짐, 바닥 위 안개는 금지다.
- 바닥 색은 회색 강철이다. 방 색으로 물들지 않는다.

**방의 색 정체성**
- 방의 색은 **벽, 설비, 소품, 벽의 작은 조명에만** 쓴다.
- 그 빛이 바닥에 번지는 것은 약하게 한다.
- 문에서 대원 키 1배 이내에는 색 번짐이 없어야 한다.

**건축 밖**
- 건축물 바깥은 **평평한 거의 검정(#07090D)** 이다. 그라데이션을 넣지 않는다.

**런타임 무드 조명 (2026-09-27 추가)**
- 방마다 다른 분위기(밝기, 색, 채도, 조명 웅덩이)는 런타임이 입힌다. `data/visual/site7_mood.json`, `site7_room_art_layer.gd` 판 셰이더.
- 그래서 원화 바닥은 위 규격대로 중성으로 그린다. 분위기를 원화 바닥에 그려 넣으면 이음매가 다시 어긋난다.
- 벽의 작은 조명은 방 색으로 또렷하게 그린다. 도구가 이 조명을 찾아 바닥 웅덩이의 위치와 색으로 쓴다.
- 건축 밖의 평평한 검정은 도구가 투명 마스크로 바꾼다. 그 자리에 코드로 그린 심연 배경(`site7_abyss_backdrop.gd`)이 보인다. 그라데이션이나 그림을 넣으면 마스크가 끊긴다.
- 새 스테이지 판을 연결하면 다음을 한다.
  1. `site7_mood.json`에 작전 행과 판마다 한 행을 넣는다.
  2. `python tools/environment/build_site7_mood_light.py`를 실행한다.
  3. quick 스위트의 `mood_light`가 `--check`로 판과 데이터가 맞는지 검사한다.

**수치 목표**(`audit_site7_plate_lighting.py --strict`가 검사)

| 대상 | 항목 | 목표 |
|---|---|---|
| 바닥 | 평균 휘도(sRGB 0–1) | 0.17–0.24 |
| 바닥 | 하위 10% 휘도 | 0.07 이상 |
| 바닥 | 상위 10% 휘도 | 0.38 이하 |
| 바닥 | 평균색 채도 | 0.15 이하 |
| 이음매 | 밝기 차 | 0.35스톱 이하 |
| 이음매 | 채도 비 | 1.5배 이하 |
| 이음매 | 색조 차 | 30° 이하. 한쪽이 회색(채도 < 0.15)이면 색조는 보지 않는다. |

**이음매 예외 (2026-09-30 사용자 승인).** 작전 8의 세 이음매만 원화 기준을 넘는 것을 받아들인다(판을 다시 만드는 대신 사용자가 고른 방법이다): `S8_C01`↔`R01_GATE`(채도비 1.95배까지), `S8_C03`↔`R04_JUNCTION`(2.1배까지), `S8_C05`↔`R05_TERMINAL`(채도비 1.9배까지, 밝기 차 0.40스톱까지). 목록은 `audit_site7_plate_lighting.py`의 `SEAM_WAIVERS`다. 이 이음매도 실행 시점 이음매 보정(`site7_seam_light.json`)을 적용한 값이 위 표의 목표(1.5배, 0.35스톱)를 넘으면 예외가 무효이고, 색조 차에는 예외가 없다. 다른 판, 다른 작전에는 적용되지 않으며 `seam_waiver` 시험이 이를 지킨다. 새 판을 만들 때 이 예외를 기대하지 말고 표를 지켜라.

### 2.4 문과 연결 규격

**방의 문**
- 표의 "문" 열에 적힌 변에만 문을 그린다.
- NW·NE 뒷벽의 문은 무거운 문틀이 있는 열린 문이다. 문짝과 셔터는 그리지 않는다.
- SW·SE 턱의 문은 난간이 끊긴 틈이다.

**문 앞 바닥(도어웨이 에이프런)**
- 문 안팎으로 대원 키 1.5배 거리까지는 같은 표준 데크를 깐다.
- 조명은 같은 중성 백색이고, 휘도는 약 0.20, 채도는 0.10 이하다.
- 모든 판의 문 앞 바닥이 같은 모습이어야 이음매가 사라진다. 이 규격의 핵심이다.

**통로**
- 한 장에 곧은 데크 하나가 그림 전체를 가로지른다.
  - 주 경로(C01–C05): 왼쪽 아래 → 오른쪽 위(↗)
  - 갈래(C06–C07): 왼쪽 위 → 오른쪽 아래(↘)
- **갈래 통로는 처음부터 ↘ 방향으로 그린다. 좌우 반전으로 만들지 않는다.**
- 데크의 두 끝은 그림 가장자리에서 밝기 그대로 잘린다. 끝을 흐리게 하거나 어둡게 하거나 벽·문을 두지 않는다. 끝부분 흐림은 런타임 셰이더가 한다.
- 데크 폭은 대원 키의 약 2.2배로, 전 길이에서 일정하다.
- 벽과 난간 위치:
  - ↗ 통로: 데크 위쪽(NW 쪽)에 뒷벽, 아래쪽(SE 쪽)에 난간이 있고 그 너머는 빈 공간이다.
  - ↘ 통로: 데크 위쪽(NE 쪽)에 뒷벽, 아래쪽(SW 쪽)에 난간이 있다.
- 통로 단면(데크 폭, 벽 높이, 난간 높이)은 방 문의 크기와 같다. 그래서 벽이 문틀로 그대로 이어진다.
- 양 끝의 데크와 조명은 도어웨이 에이프런과 같다.
- 방 색은 벽에만 쓴다. 들어가는 방 쪽 끝의 벽은 그 방의 색이고, 나가는 방 쪽 끝의 벽은 그 방의 색이다. 가운데에서 바뀐다.

### 2.5 금지

- 캐릭터, 적, 로봇, 무기, UI, HUD
- 글자, 표지판, 숫자, 로고
- 투사체, 폭발, 바닥 위 연기
- 반투명하거나 겹쳐 보이는 구조물, 떠 있는 구조물
- 바닥 가운데의 장애물. 엄폐물은 런타임 소품이 따로 놓는다.
- 로우폴리, 플랫 벡터, 흔한 네온 사이버펑크, 흐릿한 컨셉아트
- 판 가장자리의 검은 테두리나 액자

---

## 3. ImageGen 프롬프트

프롬프트는 영어로 쓴다. 한 번에 한 장씩 만든다. 한 장을 받으면 바로 검사하고 다음 장으로 넘어간다.

### 3.1 공통 코어 (모든 판)

```
Premium 2.5D tactical sci-fi game environment plate for SABLE CIRCUIT, underground research facility SITE-7.
CAMERA: fixed near-orthographic three-quarter top-down dimetric view. Floor panel seams and wall bases run at exactly a 2:1 slope (26.6 degrees from horizontal) in both diagonal directions. No perspective convergence, no fisheye, no tilted horizon.
SCALE: a standing adult would be about 1/12 of the image width tall. Square floor panels about one adult-height wide; waist-high railings; door frames about 1.6 adult-heights tall.
FLOOR: one clean, open, flat SITE-7 standard deck of dark gunmetal steel plates with fine seams and light wear, bounded by a wall base or a low raised lip. The floor is uncluttered: no text, no markings with letters or numbers, no objects in the open floor.
LIGHT: even neutral-white overhead industrial light (about 6000K) across the entire walkable floor. No hot spots, no pitch-black patches, no vignette, no darkened corners, no fog or haze over the floor. The floor stays neutral grey steel and is never tinted by room colour.
COLOUR IDENTITY: only on walls, machinery, fixtures and small practical lamps along the perimeter; their light spill on the floor is subtle and never reaches within one adult-height of a doorway.
OUTSIDE: everything beyond the architecture is flat near-black void (#07090D) with no gradient.
EXCLUDE: characters, creatures, robots, weapons, UI, HUD, text, signage, numbers, logos, projectiles, explosions, smoke over the floor, translucent or doubled geometry, black borders or frames.
STYLE: premium stylized realism with hard-surface wall thickness, recessed panels, structural supports and cast contact shadows. Not low-poly, not flat vector, not generic neon cyberpunk, not blurry concept art.
```

### 3.2 방 추가 블록

```
ROOM PLATE. The walkable floor is a dimetric diamond or elongated hexagon whose sides face NW (upper-left), NE (upper-right), SE (lower-right) and SW (lower-left). Back walls rise only along the NW and NE sides; the SW and SE sides end in a low lip or railing with no wall so nothing hides the floor. Keep the floor at least 8% away from every image border.
DOORS: open doorways exactly on these sides: {DOORS}. Each doorway is an unobstructed opening about 2.3 adult-heights wide with a heavy steel frame (a framed opening in a back wall, or a gap in the lip railing on the SW/SE side); no door leaf, no shutter. The same standard deck and the same neutral-white overhead light continue through every doorway for about 1.5 adult-heights on both sides of the threshold.
ROOM TYPE: {TYPE} — walkable floor at least {SIZE} (long x short, in the scale above).
IDENTITY: {IDENTITY}. Accent colour {ACCENT}, on walls and fixtures only.
```

### 3.3 통로 추가 블록

```
CONNECTOR CORRIDOR PLATE. One straight deck crosses the whole image along the {DIRECTION} 2:1 diagonal. Both ends of the deck are cut cleanly by the image edges at full brightness: no fade, no darkening, no end wall, no door at either end. The deck is about 2.2 adult-heights wide, constant along its whole length, and completely empty.
A back wall runs along the {WALL_SIDE} side of the deck; the other side ends in a waist-high railing over the void. The corridor cross-section (deck width, wall height, railing height) matches a standard doorway, so these walls continue straight into the door frames of the rooms at each end.
At both ends the deck and light are identical to a doorway apron: standard deck, even neutral-white overhead light. Wall accents are {ACCENT_A} near the {END_A} end, changing to {ACCENT_B} near the {END_B} end, on walls only.
IDENTITY: {IDENTITY}.
```

`{DIRECTION}`, `{WALL_SIDE}`, `{END_A}`, `{END_B}` 값:
- ↗ 주 경로 통로: `lower-left to upper-right (ascending)`, `upper-left`, `lower-left`, `upper-right`
- ↘ 갈래 통로: `upper-left to lower-right (descending)`, `upper-right`, `upper-left`, `lower-right`

### 3.4 참조 이미지

모두 저장소 안의 파일이다.

1. `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png`: 화질·재질 기준. 사용자가 제공한 참조 이미지이며 런타임 자산이 아니다.
2. 파일럿 승인 뒤: 승인된 v2 방 판 1장과 통로 판 1장. 카메라·조명·데크 기준이다.
3. `qa/map_gait_20260925/MIS_CH01_01_start.png`: 축척 기준만 본다.
4. 그 판의 v1 원화: 방 정체성(구조물 종류)만 참고한다. 카메라, 조명, 바닥은 따르지 않는다.

### 3.5 판별 정체성 (`{IDENTITY}` / `{ACCENT}`)

| 판 | IDENTITY | ACCENT |
|---|---|---|
| S1_R01 Outer Gate | massive reinforced security gateway, blast-door ribs, access-terminal structures, hazard-stripe language on walls | amber |
| S1_R02 Decon Corridor | decontamination hall, cold decon arches and spray manifolds on the walls, wet-steel wall panels | cold cyan |
| S1_R03 Archive Annex | physical archive chamber, data shelving and secure storage along the back walls, scanner fixtures | teal |
| S1_R04 Containment Junction | reinforced emergency bulkheads, breach barriers against the walls, controlled damage, alarm beacons | orange-red |
| S1_R05 Core C | monumental upper-wall iris reactor, energy housings along the back walls, concentric outer rim; central floor is an open boss arena | violet |
| S1_R06 Emergency Lift | industrial lift terminal, vertical guide rails and shaft machinery on the back wall | green |
| S1_O01 Emergency Stores | secure logistics room, armored supply cases and racks along the walls | amber |
| S1_O02 Signal Lab | signal-analysis lab, sensor arrays and scanner hardware along the walls | teal-cyan |
| S2_R01 Service Reentry | armoured service re-entry, airlock ribs, access hardware | amber |
| S2_R02 Flooded Maintenance | maintenance hall with pipe systems on the walls; water only in covered perimeter channels, never on the walkable floor | cyan |
| S2_R03 Relay Archive | relay archive cabinets and scanning rig along the back walls | teal |
| S2_R04 Quarantine Crossing | isolation gates and hazard partitions at the perimeter | hazard yellow |
| S2_R05 Sublevel Relay (단계 5 교체) | sunken relay pit: tall relay-transformer stacks, cable risers and drained sump grilles set into the back walls around an open, dry arena floor. No round iris, no concentric rings, no circular portal | crimson |
| S2_R06 Service Lift | vertical lift terminal, guide rails | green |
| S2_O01 Reserve Field Cache | protected field-cache racks and logistics equipment | amber |
| S2_O02 Echo Recorder | acoustic signal recorder, sensor housings | cyan-teal |
| S3_R01 Pressure Breach | ruptured pressure deck walls, sealed-door mechanisms; damage stays on walls | red |
| S3_R02 Inner Defense Line | reinforced defense line, emergency barriers built into the walls | red |
| S3_R03 Carrier Trace | carrier-tracing laboratory, diagnostic machines along the walls (the floor stays neutral steel; today it is saturated cyan) | teal |
| S3_R04 Collapsed Bulkhead | damaged bulkhead route, controlled debris strictly at the perimeter | amber |
| S3_R05 Anchor Remnant (단계 5 교체) | the shattered stump of a giant signal-anchor mast: split armoured housings, severed conduit bundles and emergency clamp frames braced against the back walls, pressure-relief vents; open central arena floor. No round iris, no concentric rings, no circular portal | ice-white arc light |
| S3_R06 Emergency Shaft | escape-shaft terminal, vertical mechanisms | green |
| S3_O01 Breached Armory | breached armory racks | amber |
| S3_O02 Resonance Chamber | resonance instrument chamber, waveform hardware at the perimeter | teal |
| S4_R01 Thermal Spine | vertical thermal spine: a massive insulated heat-exchange column and pressure manifolds on the back wall, heat-shield cladding | amber |
| S4_R02 Forge Gate | heavy forge blast-gate frames built into the walls, riveted heat shields, ingot-transfer rails along the wall base | orange |
| S4_R03 Heat-map Trace | thermal-survey consoles and heat-map scanner banks along the walls | red-orange |
| S4_R04 Cooling Line | coolant pipe galleries, condensation tanks and heat-exchanger fins along the walls | pale coolant blue |
| S4_R05 Forge Warden | monumental forge press and crucible machinery along the back walls, glowing ingot slots set into the walls only; open central arena floor | molten orange-white |
| S4_R06 Service Lock | service airlock: heavy pressure-lock wheel frames and lock-cycle machinery on the back wall | green |
| S4_O01 Coolant Cache | sealed coolant canister racks and cryo cabinets along the walls | coolant cyan |
| S4_O02 Thermal Observatory | thermal-observation instruments, pyrometer arrays and recording drums along the walls | amber-white |
| S5_R01 Offshore Relay | weathered offshore-rig relay deck: salt-streaked bulkheads, cable drums and relay masts against the walls; no water on the floor | cold white |
| S5_R02 Relay Defense | armoured relay pylons and signal cabinets set into the walls around an open arena | cyan |
| S5_R03 Null Carrier Trace | carrier-trace consoles, oscilloscope banks and antenna feeds along the walls | pale violet |
| S5_R04 Jammer Array | rows of jammer emitter dishes and antenna racks along the back walls | blue-white |
| S5_R05 Carrier Null | monumental carrier-aperture machine: a rectangular framed aperture of stacked emitter rings on the back wall (not a round iris) at the far end of a long defense corridor | warning red |
| S5_R06 Transit Escape | transit relay dock: a sealed transit-capsule berth and guide rails on the back wall | green |
| S5_O01 Transit Stores | offshore crew emergency lockers and survival-gear racks | safety orange |
| S5_O02 Signal Observatory | radar and sensor-array consoles, dish housings at the perimeter | teal |

통로의 IDENTITY는 "A 방의 구조물이 B 방의 구조물로 바뀌는 연결 복도"로 쓴다. 예: `security gateway structures becoming decontamination arches`. ACCENT_A와 ACCENT_B는 양 끝 방의 ACCENT다.

단계 5의 작전 4·5 전용 통로(`S4_C*`, `S5_C*`)는 IDENTITY 앞에 작전 공통 벽 구조를 붙인다. 데크와 조명은 표준 그대로다.
- `S4_C*` FORGE DESCENT: `forge descent catwalk: riveted heat-shield wall cladding, glowing slag channels behind heavy grilles set into the back wall only, heat-exchanger ribs; `
- `S5_C*` OFFSHORE NULL: `offshore rig gangway: salt-streaked bulkhead wall, cable trays, storm louvres and caged rig lamps; the railing is an open-grate gangway rail over the void; `
- 이 공통 구조 뒤에 "A 방 구조물 → B 방 구조물"을 이어 쓴다. 예: `thermal-spine heat-exchange column becoming forge blast-gate frames`.

---

## 4. 판별 작업 목록 (45장 전부)

"현재 측정 문제"는 v1 원화를 `audit_site7_plate_lighting.py`로 잰 값이다. 문제가 "없음"인 판도 다시 만든다. 카메라, 문, 에이프런 규격이 달라지기 때문이다.

새 통로 ID `Sx_C0n`은 현재 매니페스트의 n번째 통로다. 월드 배치 기준으로는 `C(n-1)`이다.

표 읽는 법:
- "밝기 차"는 log2(방 바닥 ÷ 통로 데크)다. 음수면 통로 데크가 방보다 밝다.
- "색조" 숫자의 대략적인 뜻: 약 140은 주황·호박색, 약 -45는 청록, 0 부근은 보라·자홍.

#### 스테이지 1 방 (작전 1)

| 새 ID | 현재 원화 | 방 · 종류 | 문 | 현재 측정 문제 |
|---|---|---|---|---|
| `S1_R01` | `01_OUTER_GATE_CONTINUITY.png` | R01_ENTRY · 비전투 | NE | 검은 구멍 p10 0.058; 색 캐스트 채도 0.26 |
| `S1_R02` | `02_DECON_CORRIDOR_CONTINUITY.png` | R02_CORRIDOR · 전투방 | SW, NE | 바닥 밝기 0.156; 색 캐스트 채도 0.30; 바닥 축 30.9° |
| `S1_R03` | `03_ARCHIVE_ANNEX_CONTINUITY.png` | R03_ARCHIVE · 비전투 | SW, NE, SE | 없음 |
| `S1_R04` | `04_CONTAINMENT_JUNCTION_CONTINUITY.png` | R04_CONTAINMENT · 전투 복도 | SW, NE, SE | 바닥 밝기 0.147; 검은 구멍 p10 0.062 |
| `S1_R05` | `05_CORE_C_CONTINUITY.png` | R05_CORE · 보스 | SW, NE | 바닥 밝기 0.161 |
| `S1_R06` | `06_EMERGENCY_LIFT_CONTINUITY.png` | R06_EXTRACTION · 비전투 | SW | 없음 |
| `S1_O01` | `07_EMERGENCY_STORES_CONTINUITY.png` | O01_SUPPLY · 비전투 | NW | 색 캐스트 채도 0.23; 바닥 축 31.3° |
| `S1_O02` | `08_SIGNAL_LAB_CONTINUITY.png` | O02_RESEARCH · 비전투 | NW | 바닥 축 32.1° |

#### 스테이지 1 통로

| 새 ID | 현재 원화 | 연결 | 방향 | 현재 측정 문제 |
|---|---|---|---|---|
| `S1_C01` | `09_GATE_DECON_CONNECTOR_GAME.png` | R01_ENTRY → R02_CORRIDOR | ↗ R01 NE 문 → R02 SW 문 | R01 쪽: 밝기 차 -0.43 스톱, 채도 0.42 vs 0.21 / R02 쪽: 밝기 차 -1.62 스톱 |
| `S1_C02` | `10_DECON_ARCHIVE_CONNECTOR_GAME.png` | R02_CORRIDOR → R03_ARCHIVE | ↗ R02 NE 문 → R03 SW 문 | R02 쪽: 밝기 차 -1.62 스톱 / R03 쪽: 채도 0.09 vs 0.17 / 바닥: 검은 구멍 p10 0.059; 바닥 축 18.9° |
| `S1_C03` | `11_ARCHIVE_CONTAINMENT_CONNECTOR_GAME.png` | R03_ARCHIVE → R04_CONTAINMENT | ↗ R03 NE 문 → R04 SW 문 | R03 쪽: 밝기 차 +0.50 스톱, 채도 0.57 vs 0.21 / R04 쪽: 밝기 차 +0.43 스톱, 채도 0.18 vs 0.08 / 바닥: 바닥 밝기 0.159; 검은 구멍 p10 0.037 |
| `S1_C04` | `12_CONTAINMENT_CORE_CONNECTOR_GAME.png` | R04_CONTAINMENT → R05_CORE | ↗ R04 NE 문 → R05 SW 문 | R04 쪽: 밝기 차 -1.33 스톱, 채도 0.62 vs 0.17, 색조 121 vs -7 (128°) / R05 쪽: 밝기 차 +0.90 스톱, 채도 0.77 vs 0.11 / 바닥: 바닥 밝기 0.166; 검은 구멍 p10 0.058; 색 캐스트 채도 0.18 |
| `S1_C05` | `13_CORE_LIFT_CONNECTOR_GAME.png` | R05_CORE → R06_EXTRACTION | ↗ R05 NE 문 → R06 SW 문 | R05 쪽: 채도 0.58 vs 0.10 / R06 쪽: 밝기 차 -0.48 스톱, 채도 0.17 vs 0.07 |
| `S1_C06` | `14_ARCHIVE_STORES_CONNECTOR_GAME.png` | R03_ARCHIVE → O01_SUPPLY | ↘ R03 SE 문 → O01 NW 문. 이 방향으로 새로 그림(반전 금지) | R03 쪽: 채도 0.46 vs 0.18, 색조 139 vs -57 (165°) / O01 쪽: 색조 -62 vs 143 (156°) / 바닥: 색 캐스트 채도 0.16 |
| `S1_C07` | `15_CONTAINMENT_SIGNAL_CONNECTOR_GAME.png` | R04_CONTAINMENT → O02_RESEARCH | ↘ R04 SE 문 → O02 NW 문. 이 방향으로 새로 그림(반전 금지) | R04 쪽: 밝기 차 -0.48 스톱, 채도 0.20 vs 0.09 / O02 쪽: 채도 0.62 vs 0.15, 색조 125 vs -47 (172°) / 바닥: 색 캐스트 채도 0.20 |

#### 스테이지 2 방 (작전 2)

| 새 ID | 현재 원화 | 방 · 종류 | 문 | 현재 측정 문제 |
|---|---|---|---|---|
| `S2_R01` | `S02_01_SERVICE_REENTRY_CONTINUITY.png` | R01_REENTRY · 비전투 | NE | 바닥 밝기 0.155; 검은 구멍 p10 0.049; 색 캐스트 채도 0.16; 바닥 축 15.1° |
| `S2_R02` | `S02_02_FLOODED_MAINTENANCE_CONTINUITY.png` | R02_MAINTENANCE · 전투 복도 | SW, NE | 바닥 밝기 0.241; 검은 구멍 p10 0.063; 과노출 p90 0.407 |
| `S2_R03` | `S02_03_RELAY_ARCHIVE_CONTINUITY.png` | R03_RELAY_ARCHIVE · 비전투 | SW, NE, SE | 색 캐스트 채도 0.28 |
| `S2_R04` | `S02_04_QUARANTINE_CROSSING_CONTINUITY.png` | R04_QUARANTINE · 전투 복도 | SW, NE, SE | 색 캐스트 채도 0.26 |
| `S2_R05` | `S02_05_SUBLEVEL_RELAY_CONTINUITY.png` | R05_RELAY · 보스 | SW, NE | 색 캐스트 채도 0.38 |
| `S2_R06` | `S02_06_SERVICE_LIFT_CONTINUITY.png` | R06_EVAC · 비전투 | SW | 과노출 p90 0.408; 바닥 축 21.7° |
| `S2_O01` | `S02_07_RESERVE_FIELD_CACHE_CONTINUITY.png` | O01_SUPPLY · 비전투 | NW | 검은 구멍 p10 0.065; 바닥 축 19.4° |
| `S2_O02` | `S02_08_ECHO_RECORDER_CONTINUITY.png` | O02_RESEARCH · 비전투 | NW | 바닥 밝기 0.157 |

#### 스테이지 2 통로

| 새 ID | 현재 원화 | 연결 | 방향 | 현재 측정 문제 |
|---|---|---|---|---|
| `S2_C01` | `S02_09_REENTRY_MAINTENANCE_GAME.png` | R01_REENTRY → R02_MAINTENANCE | ↗ R01 NE 문 → R02 SW 문 | R01 쪽: 채도 0.35 vs 0.05 / R02 쪽: 채도 0.27 vs 0.17 / 바닥: 바닥 밝기 0.160; 검은 구멍 p10 0.057; 색 캐스트 채도 0.17; 바닥 축 17.9° |
| `S2_C02` | `S02_10_MAINTENANCE_RELAY_ARCHIVE_GAME.png` | R02_MAINTENANCE → R03_RELAY_ARCHIVE | ↗ R02 NE 문 → R03 SW 문 | R02 쪽: 밝기 차 +0.80 스톱, 채도 0.22 vs 0.03 / R03 쪽: 밝기 차 -1.08 스톱 / 바닥: 검은 구멍 p10 0.028; 과노출 p90 0.408; 색 캐스트 채도 0.19; 바닥 축 19.4° |
| `S2_C03` | `S02_11_RELAY_ARCHIVE_QUARANTINE_GAME.png` | R03_RELAY_ARCHIVE → R04_QUARANTINE | ↗ R03 NE 문 → R04 SW 문 | R03 쪽: 밝기 차 +0.37 스톱 / R04 쪽: 밝기 차 -0.72 스톱, 채도 0.13 vs 0.43 / 바닥: 바닥 축 20.4° |
| `S2_C04` | `S02_12_QUARANTINE_SUBLEVEL_RELAY_GAME.png` | R04_QUARANTINE → R05_RELAY | ↗ R04 NE 문 → R05 SW 문 | R04 쪽: 색조 78 vs 120 (41°) / R05 쪽: 밝기 차 -0.83 스톱 / 바닥: 바닥 밝기 0.275; 과노출 p90 0.426; 색 캐스트 채도 0.23; 바닥 축 20.2° |
| `S2_C05` | `S02_13_SUBLEVEL_RELAY_SERVICE_LIFT_GAME.png` | R05_RELAY → R06_EVAC | ↗ R05 NE 문 → R06 SW 문 | R05 쪽: 밝기 차 +0.78 스톱 / R06 쪽: 밝기 차 -1.38 스톱, 채도 0.09 vs 0.49 / 바닥: 바닥 밝기 0.134; 검은 구멍 p10 0.046; 바닥 축 20.0° |
| `S2_C06` | `S02_14_RELAY_ARCHIVE_FIELD_CACHE_GAME.png` | R03_RELAY_ARCHIVE → O01_SUPPLY | ↘ R03 SE 문 → O01 NW 문. 이 방향으로 새로 그림(반전 금지) | R03 쪽: 밝기 차 -0.40 스톱, 채도 0.58 vs 0.25, 색조 141 vs -49 (171°) / O01 쪽: 밝기 차 -0.81 스톱 / 바닥: 바닥 밝기 0.273; 과노출 p90 0.445; 색 캐스트 채도 0.17 |
| `S2_C07` | `S02_15_QUARANTINE_ECHO_RECORDER_GAME.png` | R04_QUARANTINE → O02_RESEARCH | ↘ R04 SE 문 → O02 NW 문. 이 방향으로 새로 그림(반전 금지) | 없음 |

#### 스테이지 3 방 (작전 3. 단계 4 전에는 작전 3·4·5 공유)

| 새 ID | 현재 원화 | 방 · 종류 | 문 | 현재 측정 문제 |
|---|---|---|---|---|
| `S3_R01` | `S03_01_PRESSURE_BREACH_CONTINUITY.png` | R01_BREACH · 비전투 | NE | 바닥 밝기 0.147; 검은 구멍 p10 0.070; 바닥 축 16.7° |
| `S3_R02` | `S03_02_INNER_DEFENSE_LINE_CONTINUITY.png` | R02_DEFENSE · 전투 복도 | SW, NE | 검은 구멍 p10 0.066; 색 캐스트 채도 0.18 |
| `S3_R03` | `S03_03_CARRIER_TRACE_CONTINUITY.png` | R03_TRACE · 비전투 | SW, NE, SE | 바닥 밝기 0.273; 과노출 p90 0.438; 색 캐스트 채도 0.70; 바닥 축 20.0° |
| `S3_R04` | `S03_04_COLLAPSED_BULKHEAD_CONTINUITY.png` | R04_BULKHEAD · 전투 복도 | SW, NE, SE | 바닥 밝기 0.145; 검은 구멍 p10 0.037 |
| `S3_R05` | `S03_05_ANCHOR_REMNANT_CONTINUITY.png` | R05_ANCHOR · 보스 | SW, NE | 과노출 p90 0.389; 색 캐스트 채도 0.20 |
| `S3_R06` | `S03_06_EMERGENCY_SHAFT_CONTINUITY.png` | R06_ESCAPE · 비전투 | SW | 바닥 밝기 0.160; 바닥 축 19.7° |
| `S3_O01` | `S03_07_BREACHED_ARMORY_CONTINUITY.png` | O01_SUPPLY · 비전투 | NW | 색 캐스트 채도 0.28; 바닥 축 21.3° |
| `S3_O02` | `S03_08_RESONANCE_CHAMBER_CONTINUITY.png` | O02_RESEARCH · 비전투 | NW | 색 캐스트 채도 0.20 |

#### 스테이지 3 통로 (작전 3. 단계 5 전에는 작전 3·4·5 공유)

| 새 ID | 현재 원화 | 연결 | 방향 | 현재 측정 문제 |
|---|---|---|---|---|
| `S3_C01` | `S03_09_PRESSURE_DEFENSE_GAME.png` | R01_BREACH → R02_DEFENSE | ↗ R01 NE 문 → R02 SW 문 | R02 쪽: 밝기 차 -1.13 스톱, 채도 0.22 vs 0.04 / 바닥: 검은 구멍 p10 0.056; 색 캐스트 채도 0.21; 바닥 축 18.3° |
| `S3_C02` | `S03_10_DEFENSE_CARRIER_TRACE_GAME.png` | R02_DEFENSE → R03_TRACE | ↗ R02 NE 문 → R03 SW 문 | R02 쪽: 채도 0.07 vs 0.16 / R03 쪽: 채도 0.05 vs 0.71 / 바닥: 바닥 축 19.4° |
| `S3_C03` | `S03_11_CARRIER_TRACE_BULKHEAD_GAME.png` | R03_TRACE → R04_BULKHEAD | ↗ R03 NE 문 → R04 SW 문 | R03 쪽: 밝기 차 +0.62 스톱, 채도 0.14 vs 0.72 / R04 쪽: 밝기 차 -0.99 스톱, 채도 0.37 vs 0.12 / 바닥: 바닥 밝기 0.168; 검은 구멍 p10 0.064; 색 캐스트 채도 0.18; 바닥 축 18.2° |
| `S3_C04` | `S03_12_BULKHEAD_ANCHOR_REMNANT_GAME.png` | R04_BULKHEAD → R05_ANCHOR | ↗ R04 NE 문 → R05 SW 문 | R04 쪽: 밝기 차 -0.75 스톱 / R05 쪽: 채도 0.14 vs 0.37 / 바닥: 바닥 밝기 0.264; 과노출 p90 0.491; 색 캐스트 채도 0.20; 바닥 축 20.2° |
| `S3_C05` | `S03_13_ANCHOR_EMERGENCY_SHAFT_GAME.png` | R05_ANCHOR → R06_ESCAPE | ↗ R05 NE 문 → R06 SW 문 | R05 쪽: 밝기 차 -0.76 스톱 / R06 쪽: 채도 0.16 vs 0.01 / 바닥: 바닥 축 21.2° |
| `S3_C06` | `S03_14_CARRIER_TRACE_ARMORY_GAME.png` | R03_TRACE → O01_SUPPLY | ↘ R03 SE 문 → O01 NW 문. 이 방향으로 새로 그림(반전 금지) | R03 쪽: 색조 144 vs -42 (174°) / O01 쪽: 채도 0.32 vs 0.12 / 바닥: 검은 구멍 p10 0.052; 바닥 축 18.7° |
| `S3_C07` | `S03_15_BULKHEAD_RESONANCE_GAME.png` | R04_BULKHEAD → O02_RESEARCH | ↘ R04 SE 문 → O02 NW 문. 이 방향으로 새로 그림(반전 금지) | R04 쪽: 밝기 차 -0.75 스톱, 채도 0.34 vs 0.02 / O02 쪽: 밝기 차 +0.57 스톱, 색조 140 vs -47 (174°) / 바닥: 색 캐스트 채도 0.22 |


#### 스테이지 4 방 (작전 4 전용, 단계 4)

작전 4는 방마다 자기 판을 쓴다. 통로는 `S3_C01`–`S3_C07`을 그대로 쓴다(주 경로 5장은 `reverse`). 문은 작전 4가 실제로 쓰는 쪽에만 낸다. "바닥 기준"은 그 방이 지금 쓰는 S3 판이다. 바닥 넓이는 그 판 이상으로 한다.

| 새 ID | 방 · 종류 | 문 | 바닥 기준 |
|---|---|---|---|
| `S4_R01` | R01_ENTRY · 비전투 | SW | S3_R06 |
| `S4_R02` | R02_GATE · 전투 | NE, SW | S3_R04 |
| `S4_R03` | R03_TRACE · 비전투(연구) | NE, SW, SE | S3_R01 |
| `S4_R04` | R04_LINE · 엘리트 | NE, SW, SE | S3_R02 |
| `S4_R05` | R05_WARDEN · 보스 | NE, SW | S3_R05 |
| `S4_R06` | R06_ESCAPE · 비전투(탈출) | NE | S3_R03 |
| `S4_O01` | O01_SUPPLY · 비전투 | NW | S3_O01 |
| `S4_O02` | O02_RESEARCH · 비전투 | NW | S3_O02 |

#### 스테이지 5 방 (작전 5 전용, 단계 4)

| 새 ID | 방 · 종류 | 문 | 바닥 기준 |
|---|---|---|---|
| `S5_R01` | R01_ENTRY · 비전투 | NE | S3_R01 |
| `S5_R02` | R02_DEFENSE · 전투 | SW, NE, SE | S3_R05 |
| `S5_R03` | R03_TRACE · 비전투(연구) | SW, NE | S3_R03 |
| `S5_R04` | R04_ARRAY · 엘리트 | SW, NE, SE | S3_R04 |
| `S5_R05` | R05_CARRIER · 보스(긴 방어선 복도, 보스는 출구 끝) | SW, NE | S3_R02 |
| `S5_R06` | R06_ESCAPE · 비전투(탈출) | SW | S3_R06 |
| `S5_O01` | O01_SUPPLY · 비전투 | NW | S3_O01 |
| `S5_O02` | O02_RESEARCH · 비전투 | NW | S3_O02 |

#### 스테이지 4 통로 (작전 4 전용, 단계 5)

- 작전 4의 주 경로 통로(C01–C05)는 `reverse`다. 판은 ↗로 그리지만 길은 위 오른쪽 끝(앞 방)에서 아래 왼쪽 끝(다음 방)으로 내려간다.
- 그래서 `{ACCENT_A}`(아래 왼쪽 끝)는 다음 방, `{ACCENT_B}`(위 오른쪽 끝)는 앞 방의 색이다.
- "크기 기준"은 그 자리에서 지금 쓰는 S3 통로다. 판 크기와 데크 길이·폭을 그 판과 같게 한다(↗ 1774×887, ↘ 1254×1254).

| 새 ID | 연결(길 순서) | 문 | 아래 왼쪽 / 위 왼쪽 끝 | 위 오른쪽 / 아래 오른쪽 끝 | 크기 기준 |
|---|---|---|---|---|---|
| `S4_C01` | R01_ENTRY → R02_GATE | ↗ 판, R01 SW 문 → R02 NE 문 | R02 Forge Gate · orange | R01 Thermal Spine · amber | S3_C01 |
| `S4_C02` | R02_GATE → R03_TRACE | ↗ 판, R02 SW → R03 NE | R03 Heat-map Trace · red-orange | R02 Forge Gate · orange | S3_C02 |
| `S4_C03` | R03_TRACE → R04_LINE | ↗ 판, R03 SW → R04 NE | R04 Cooling Line · pale coolant blue | R03 Heat-map Trace · red-orange | S3_C03 |
| `S4_C04` | R04_LINE → R05_WARDEN | ↗ 판, R04 SW → R05 NE | R05 Forge Warden · molten orange-white | R04 Cooling Line · pale coolant blue | S3_C04 |
| `S4_C05` | R05_WARDEN → R06_ESCAPE | ↗ 판, R05 SW → R06 NE | R06 Service Lock · green | R05 Forge Warden · molten orange-white | S3_C05 |
| `S4_C06` | R03_TRACE → O01_SUPPLY | ↘ R03 SE → O01 NW (반전 금지) | R03 Heat-map Trace · red-orange | O01 Coolant Cache · coolant cyan | S3_C06 |
| `S4_C07` | R04_LINE → O02_RESEARCH | ↘ R04 SE → O02 NW (반전 금지) | R04 Cooling Line · pale coolant blue | O02 Thermal Observatory · amber-white | S3_C07 |

#### 스테이지 5 통로 (작전 5 전용, 단계 5)

작전 5는 `reverse`가 없다. `{ACCENT_A}`는 앞 방, `{ACCENT_B}`는 다음 방이다. 갈래 O01은 R02_DEFENSE에서 갈라진다(R03 아님).

| 새 ID | 연결(길 순서) | 문 | 아래 왼쪽 / 위 왼쪽 끝 | 위 오른쪽 / 아래 오른쪽 끝 | 크기 기준 |
|---|---|---|---|---|---|
| `S5_C01` | R01_ENTRY → R02_DEFENSE | ↗ R01 NE → R02 SW | R01 Offshore Relay · cold white | R02 Relay Defense · cyan | S3_C01 |
| `S5_C02` | R02_DEFENSE → R03_TRACE | ↗ R02 NE → R03 SW | R02 Relay Defense · cyan | R03 Null Carrier Trace · pale violet | S3_C02 |
| `S5_C03` | R03_TRACE → R04_ARRAY | ↗ R03 NE → R04 SW | R03 Null Carrier Trace · pale violet | R04 Jammer Array · blue-white | S3_C03 |
| `S5_C04` | R04_ARRAY → R05_CARRIER | ↗ R04 NE → R05 SW | R04 Jammer Array · blue-white | R05 Carrier Null · warning red | S3_C04 |
| `S5_C05` | R05_CARRIER → R06_ESCAPE | ↗ R05 NE → R06 SW | R05 Carrier Null · warning red | R06 Transit Escape · green | S3_C05 |
| `S5_C06` | R02_DEFENSE → O01_SUPPLY | ↘ R02 SE → O01 NW (반전 금지) | R02 Relay Defense · cyan | O01 Transit Stores · safety orange | S3_C06 |
| `S5_C07` | R04_ARRAY → O02_RESEARCH | ↘ R04 SE → O02 NW (반전 금지) | R04 Jammer Array · blue-white | O02 Signal Observatory · teal | S3_C07 |

#### 보스방 교체 (단계 5)

작전 1·2·3이 모두 같은 앵커 보스를 쓰고, 보스방 세 곳의 뒷벽이 모두 둥근 보라 아이리스다. 앵커의 본거지인 `S1_R05`만 아이리스로 두고 나머지 두 장을 새로 그린다. 새 정체성은 3.5 표에 있다.

| ID | 작전 · 방 | 문 | 바닥 기준 | 새 정체성 |
|---|---|---|---|---|
| `S2_R05` | 작전 2 R05_RELAY · 보스 | SW, NE | 지금 `S2_R05` | 가라앉은 중계 구덩이, 진홍 |
| `S3_R05` | 작전 3 R05_ANCHOR · 보스 | SW, NE, SE | 지금 `S3_R05` | 부서진 앵커 기둥 잔해, 얼음빛 흰 아크 |

---

## 5. 생성 뒤 연결 작업

### 5.1 파일

| 종류 | 위치와 이름 |
|---|---|
| 원본 | `art_src/environments/site7_v2/stage0N/<ID>/<ID>_RAW_NATIVE.png` (받은 그대로) |
| 마스터 | `<ID>_MASTER.png` (= RAW, 또는 균등 크롭) |
| 런타임 | `assets/environments/site7_v2/stage0N/<ID>/<ID>_GAME.png` |

- GAME 크기는 네이티브 그대로가 기본이다. 줄일 때는 균등 축소만 한다. 확대는 금지다.
- `.import` 설정은 v1과 같게 한다: `compress/mode=0`(무손실), `mipmaps/generate=false`.
- 매니페스트: `art_src/environments/site7_v2/SITE7_MAP_KIT_V2_MANIFEST.md`. 판마다 다음을 적는다.
  - 최종 프롬프트 전문과 참조 이미지 목록
  - 네이티브 크기
  - RAW / MASTER / GAME SHA-256
  - 시도 횟수와 거절 사유
  - 적용한 전역 보정(있다면 수치)
- 거절 후보는 `art_src/environments/site7_v2/_quarantine/<ID>/`에 해시와 사유를 적어 보존한다.

### 5.2 데이터와 코드

1. `data/visual/site7_plate_floors.json`에 v2 판을 추가한다.
   - `floor`: 실제로 칠해진 걷는 바닥의 윤곽. 정규화 좌표다.
   - `doors`: 변별 문 중심과 너비. 예: `{"NE": [x, y, width], ...}`
   - 추적 결과는 `tests/render/site7_walk_graph_capture.gd`의 1080p 오버레이로 확인한다.
2. `data/visual/site7_battle_art.json`을 고친다.
   - 경로를 v2로 바꾸고 `scale: 1.0`으로 한다.
   - 통로마다 `deck: "ascending" | "descending"`을 추가한다.
3. `tools/environment/build_site7_world_layout.py`를 고친다.
   - `mirror=i >= 5` 하드코딩을 없앤다. `deck` 값을 읽어 ↘ 판을 반전 없이 쓴다.
   - `deck_ends`, `link`, `visible_along_deck`, 미리보기, 이음매 조명이 반전 없는 ↘ 데크를 처리하게 한다.
   - 통로 데크 끝의 중심을 방 `doors`의 문 중심에 맞추는 배치를 넣는다. 지금의 "바닥 안쪽 15%까지 밀어 넣기"를 대신한다.
   - `--check`와 `world_layout` 테스트를 유지한다.
4. `tests/smoke/site7_connector_alignment_smoke.gd`를 고친다.
   - 지금은 "갈래는 반전된 통로"를 검사한다. 이것을 "↘ 판은 반전 없음"으로 바꾼다.
   - 문 정렬 검사를 추가한다. 데크 끝 중심과 문 중심의 오차 기준을 정한다.
5. `data/visual/site7_battle_layouts.json`의 전투방 15개(작전 5개 × 3개)를 다시 작성한다.
   - 대상: 바닥, 엄폐물, 스폰.
   - 그다음 `godot ... -s tools/environment/settle_cover_on_floor.gd -- --write`를 돌린다.
   - 위험지대 배치(`hazard_points`)가 새 바닥에서도 성립하는지 확인한다.
6. `scripts/missions/site7_room_art_layer.gd`의 흐림 상수를 확인한다.
   - 대상: 이음매 12%, `CAP_FADE`, `ROOM_EDGE_FADE`, `MASK_EDGE_FADE`.
   - 문 규격에 맞게 필요하면 조정하고, `site7_battle_geometry_smoke.gd`의 관련 검사를 함께 고친다.
7. `python tools/environment/build_site7_world_layout.py`로 배치와 이음매 조명을 다시 만든다.
8. 메뉴 배경이 쓰는 판을 v2의 같은 방으로 바꾼다.
   - `scripts/ui/title_screen.gd` `TITLE_PLATE` → S3_R05
   - `scripts/ui/base_lobby.gd` `BASE_PLATE` → S2_O01
9. `AGENTS.md`의 맵 절을 v2 규칙으로 고친다: 문 앵커, 반전 없는 갈래, 키트 규격 문서 위치.
10. 무드 조명을 연결한다(2.3의 런타임 무드 조명).
    - `data/visual/site7_mood.json`에 그 작전의 행과 v2 판 15장의 행을 넣는다. 작전 1 행이 본보기다.
    - `python tools/environment/build_site7_mood_light.py`로 조명 웅덩이와 투명 마스크를 만든다. `--preview .cache/...`로 찾은 조명을 확인한다.
    - 방끼리, 그리고 앞뒤 작전과 분위기가 겹치지 않게 한다. 계획은 아래 표와 같다.

    | 작전 | 전체 | 방 |
    |---|---|---|
    | 1 BLACKOUT | 중성, 방마다 뚜렷함 | 적용됨: 입구 호박, 제독 밝은 청백, 기록실 어두운 청록, 격리 적색 경보(맥동), 코어 보라, 리프트 녹색, 보급 따뜻함, 신호 청색 |
    | 2 RECOVERY SWEEP | 1보다 어둡고 차가움, 심연은 탁한 청록 | 재진입 비상 호박, 침수 정비 차가운 청록(젖은 반사), 중계 기록 청록 데이터, 검역 병든 황록 경고, 하층 중계(보스) 진홍 맥동, 리프트 따뜻한 백색, 보급 주황, 반향 기록 청보라 |
    | 3 CORE PRESSURE | 가장 어두운 진홍, 대비 높음 | 작전 행 `plates`: 방마다 붉은 비상 채움과 맥동 경보, S3_R01·R02는 붉은 등 자체가 점멸, 차가운 등은 약하게 |
    | 4 FORGE DESCENT | 호박·주황, 밝고 채도 높음, 불티 | 방 앞쪽 모서리에서 올라오는 열기(깊이 내려갈수록 강함), 따뜻한 채움, 점멸 없음 |
    | 5 OFFSHORE NULL | 차가운 회청, 채도 낮음, 비 | 차가운 채움, 방을 느리게 지나는 신호등, 따뜻한 등은 약하게, 보스방 붉은 등만 맥동 |

    - 작전 3·4·5 행은 이미 있다. v1 원화에는 투명 마스크가 없어서 심연을 원화 가장자리만큼 어둡게 두었다. 스테이지 3 v2 판을 연결하면 심연 안개와 연무를 작전 1 수준으로 올린다.

### 5.3 검증 (단계마다)

1. `python tools/environment/audit_site7_plate_lighting.py --mission <해당 작전> --strict`가 PASS해야 한다. 이음매 수치는 조명 보정 전 원화 기준이다.
2. `python tools/maintenance/run_regression_suite.py`(quick)와 `--suite full`이 PASS해야 한다.
   - 특히 `connector_alignment`, `battle_geometry`, `floor_segment`, `world_layout`, 적 엄폐 경로 회귀, 작전 풀플레이를 본다.
   - `full_op_03`은 봇이 약 3번에 1번 전멸한다. FAIL이 한 번 나오면 다시 돌려 본다.
3. 게임 안 1080p 캡처를 찍는다.
   - `qa/plate_lighting_20260927/probe/plate_seam_capture.gd`를 `.cache/diag/`로 복사한다.
   - `--resolution 1920x1080 -s res://.cache/diag/plate_seam_capture.gd -- --mission=<ID> --out=res://.cache/...`로 돌린다.
   - 결과는 통로 7장과 방 16장이다.
4. 전체 조감을 만든다: `build_site7_world_layout.py --preview .cache/...`
5. v1과 v2 비교 캡처를 만든다. 같은 방, 같은 카메라로 찍는다.
6. 기록: `qa/site7_map_kit_v2_<날짜>/`
   - `README_KO.md`
   - 1080p 무손실 WebP
   - `audit` JSON
   - `validate_visual_evidence_1080p.py --require-dynamic-capture` 결과
7. 로컬에 커밋한다.

---

## 6. 단계와 멈출 지점

**단계 0 — 파일럿 3장**
- 대상:
  - `S1_R02`: 전투방, 문 SW·NE, 청록 정체성. 방 색을 벽에만 가두는지 시험한다.
  - `S1_C01`: ↗ 통로.
  - `S1_C06`: ↘ 갈래 통로.
- 5.1–5.3을 이 3장에 대해서만 한다. 코드 변경 가운데 ↘ 비반전 지원과 문 앵커는 여기서 만든다. 나머지 판은 v1으로 둔다.
- audit에서는 v2 판 3장과 그 판이 닿는 이음매만 판정한다. v1 판은 원래 FAIL로 나오므로 이 단계에서는 `--strict`를 쓰지 않는다.
  - v1 방과 v2 통로가 만나는 이음매는 참고용이다. v2 방끼리 만나는 곳이 아직 없기 때문이다.
- **멈추고 사용자에게 보고한다.**
  - 게임 안 캡처
  - audit 수치
  - v1/v2 비교
- 사용자 승인이 나면 이 3장이 이후 모든 생성의 기준 이미지가 된다.

**단계 1 — 스테이지 1 나머지 12장**
- 작전 1을 v2로 전환한다. 검증한 뒤 **멈추고 보고한다.**

**단계 2 — 스테이지 2 15장**
- 작전 2를 전환한다. 검증한 뒤 멈추고 보고한다.

**단계 3 — 스테이지 3 15장**
- 작전 3·4·5를 전환한다. 전투방 레이아웃 9개를 다시 쓴다. 검증한 뒤 멈추고 보고한다.
- 2026-09-27부터 작전 3·4·5는 같은 판을 서로 다른 순서와 방향으로 쓴다(`AGENTS.md` "Mission styles and route structure").
  - 작전 3: 판 순서 그대로 오르막. O01은 S3_R03, O02는 보스홀 S3_R05에서 갈라진다.
  - 작전 4: 역방향 내리막. S3_R06 → S3_R04 → S3_R01 → S3_R02 → S3_R05 → S3_R03. O01은 S3_R01, O02는 S3_R02에서 갈라진다.
  - 작전 5: S3_R01 → S3_R05 → S3_R03 → S3_R04 → S3_R02 → S3_R06. O01은 S3_R05, O02는 S3_R04에서 갈라진다.
- 그래서 스테이지 3 판의 문은 세 작전의 합집합이다.

  | 판 | 문 |
  |---|---|
  | S3_R01 | NE, SW, SE |
  | S3_R02 | SW, NE, SE |
  | S3_R03 | SW, NE, SE |
  | S3_R04 | SW, NE, SE |
  | S3_R05 | SW, NE, SE |
  | S3_R06 | SW |
  | S3_O01, S3_O02 | NW |

  - 한 작전에서 쓰지 않는 문은 봉인된 격벽이나 난간으로 읽혀야 한다. 심연으로 뚫린 빈 틈으로 두지 않는다.
  - 판마다 전투 바닥은 하나다. 방이 어느 판에 있든 그 판의 바닥과 엄폐를 쓴다.
- 작전 행의 무드와 심연 스타일(`pressure`, `forge`, `offshore`)은 이미 있다. v2 판을 연결하면 심연 안개와 연무를 작전 1 수준으로 올린다.

**단계 4 — 작전 4·5 전용 방 16장** (사용자 지시 2026-09-27)
- 목적: 작전 3·4·5가 같은 방 원화 8장을 쓰는 반복을 없앤다.
  - 작전 3은 S3 판을 그대로 쓴다. 작전 4는 `S4_*`, 작전 5는 `S5_*` 방 판을 쓴다(4절 표).
  - 통로 7장은 세 작전이 계속 공유한다. 단계 5에서 작전 4·5 전용 통로로 바꾼다.
- 규격: 2.1–2.5, 3.1, 3.2를 그대로 따른다. 판 크기, 문 너비(약 300 px), 에이프런(약 195 px)은 스테이지 3 방과 같다.
- 참조 이미지:
  - Image 1: 그 방의 "바닥 기준" S3 판. 카메라, 축척, 바닥 재질, 문 규격에만 쓴다.
  - 품질 참조(`IMAGE_A`)는 그대로 쓴다.
  - 벽 구조물은 새로 그린다. S3 판의 벽 모양, 기계 배치, 실루엣을 옮기지 않는다.
- 구분 기준: 새 16장은 S3 8장과도, 서로와도 벽 실루엣이 달라야 한다.
  - 검수할 때 같은 방 순서로 S3 판과 나란히 놓고 확인한다.
  - 바닥 모양은 달라도 된다(긴 육각형, 비대칭 다이아몬드). 같은 다이아몬드를 반복하지 않는다.
  - 표준 데크와 중성 조명은 그대로다.
- 문: 표의 쪽에만 낸다. 쓰지 않는 문을 그리지 않는다. 작전 4·5 방에는 봉인 격벽이 필요 없다.
- 연결:
  - `site7_battle_art.json`의 작전 4·5 방 경로를 새 판으로 바꾼다. 통로 행(작전 4 `reverse`)은 그대로 둔다.
  - 다음을 다시 만든다:
    - 바닥과 문(`site7_plate_floors.json`)
    - 배치 풀이와 이음매 조명
    - 전투방 6개의 레이아웃: 작전 4의 R02·R04·R05, 작전 5의 R02·R04·R05
    - 엄폐 정착
    - 스폰 씨앗(`spawn`, `enemy_spawns`, `boss_anchor`). 작전 4의 방은 오른쪽 위에서 들어온다.
  - 무드:
    - 새 판 16장의 행을 `site7_mood.json`의 공유 `plates`에 넣는다.
    - 시작점은 그 방이 지금 쓰는 S3 판의 작전 행(`missions.MIS_CH01_04.plates`, `missions.MIS_CH01_05.plates`)이다. 경로만 바꿔 옮긴다.
    - `lights`의 `at`을 새 바닥에 맞춘다. 작전 4의 열기는 바닥 앞쪽 모서리에, 작전 5의 신호등은 뒤쪽에 둔다.
    - 옮긴 뒤 작전 4·5의 `plates` 블록을 지운다.
    - 작전 3 블록과 작전 행 값은 건드리지 않는다.
    - 그다음 `build_site7_mood_light.py`를 돌린다.
  - `AGENTS.md`의 맵 절과 무드 절에서 "작전 3–5가 판을 공유한다"는 문장을 고친다.
- 검증: 5.3을 그대로 따른다.
  - 작전 4·5의 strict audit
  - quick과 full 회귀
  - 1080p 캡처
  - S3 판과 새 판의 같은 카메라 비교
- 게임 캡처 바닥에 보이는 방 이름, 화살표, 쉐브론은 `scripts/missions/site7_floor_guide.gd`가 그리는 길 안내다. 원화의 글자가 아니다.
- 예상 생성량: 16장 × 평균 1.2회 ≈ ImageGen 20회.
- 순서:
  - 원화 생성과 검수는 바로 시작한다.
  - 게임 데이터 연결은 git log에 Claude의 "Light SITE-7 missions 3-5 rooms per mission" 커밋이 보인 뒤에 한다.
- 검증 뒤 **멈추고 보고한다.**

**단계 5 — 작전 4·5 전용 통로 14장과 보스방 2장** (사용자 지시 2026-09-28)
- 목적: 단계 4 뒤에 남은 반복 두 가지를 없앤다.
  - 작전 3·4·5가 통로 `S3_C01`–`S3_C07`을 함께 쓴다. 조명만 다르고 벽 구조가 같다.
  - 작전 1·2·3의 보스방 뒷벽이 모두 둥근 보라 아이리스다.
- 끝나면 75장(작전 5개 × 15장) 모두 한 작전만 쓴다. 공유하는 판이 없어진다.
- 대상(4절 표):
  - 통로 14장: `S4_C01`–`S4_C07`, `S5_C01`–`S5_C07`
  - 보스방 2장: `S2_R05`, `S3_R05`. `S1_R05`는 그대로 둔다.
- 시작: 단계 4를 커밋하고 보고한 뒤에 시작한다.
- 규격: 2.1–2.5, 3.1을 그대로 따른다. 통로는 3.3, 보스방은 3.2를 쓴다.
  - 통로 판 크기, 데크 길이·폭, 양 끝 에이프런은 "크기 기준" S3 통로와 같다.
  - 보스방의 판 크기(1672×941), 문 너비(약 300 px), 에이프런(약 195 px)은 지금 판과 같다.
- 참조 이미지:
  - Image 1: 통로는 "크기 기준" S3 통로, 보스방은 지금 그 판. 카메라, 축척, 데크, 문 규격에만 쓴다.
  - 품질 참조(`IMAGE_A`)는 그대로 쓴다.
  - 통로에는 양 끝 방의 새 판(`S4_*`, `S5_*`)을 참조로 더해도 된다. 문틀과 벽이 이어지는지 맞출 때만 쓴다.
  - 벽 구조물은 새로 그린다. S3 통로와 지금 보스방의 벽 모양, 기계 배치, 실루엣을 옮기지 않는다.
- 구분 기준:
  - 새 통로 14장은 S3 통로 7장과도, 서로와도 벽 실루엣이 달라야 한다. 같은 자리의 S3 통로와 나란히 놓고 검수한다.
  - 보스방 다섯 곳(`S1_R05`–`S5_R05`)은 뒷벽 실루엣이 서로 달라야 한다. 둥근 아이리스와 동심원 고리는 `S1_R05`에만 있다.
- 보스방 교체 파일:
  - 같은 ID와 같은 경로를 쓴다. 게임 데이터의 경로는 바뀌지 않는다.
  - 교체 전 RAW, MASTER, GAME은 `art_src/environments/site7_v2/_superseded/<ID>/`로 옮긴다. 매니페스트에 이전 해시와 교체 이유를 적는다. 지우지 않는다.
- 연결:
  - `site7_battle_art.json`: 작전 4·5 통로 행의 `asset`을 새 판으로 바꾼다.
    - `reverse`와 `deck`, `position`은 그대로 둔다.
    - 작전 5 C06의 `asset_id`는 `ENV_S05_DEFENSE_SUPPLY`로 고친다. 지금 `ENV_S05_TRACE_SUPPLY`지만 갈래는 R02_DEFENSE에서 나간다.
  - `site7_plate_floors.json`: 새 통로 14장의 데크, 두 보스방의 바닥과 문을 다시 추적한다.
  - 다시 만든다:
    - 배치 풀이와 이음매 조명(`build_site7_world_layout.py`)
    - 전투방 2개 레이아웃: 작전 2 R05_RELAY, 작전 3 R05_ANCHOR. 바닥, 엄폐, `spawn`, `enemy_spawns`, `boss_anchor`
    - 엄폐 정착. dry run에서 움직이는 것이 없을 때까지 돌린다.
  - 무드(`site7_mood.json`):
    - 새 통로 14장의 행을 공유 `plates`에 넣는다. 시작점은 같은 자리 S3 통로의 행이다. 등(`lamps`)은 새 원화에 맞춘다.
    - `S2_R05` 행은 작전 2의 진홍 맥동을 유지한다. `lights`의 `at`만 새 바닥에 맞춘다.
    - `S3_R05` 공유 행의 보라 조명은 새 정체성(얼음빛 흰 아크)에 맞게 색과 위치를 바꾼다. 작전 3 행의 `S3_R05`(붉은 경보)는 유지하고 `at`만 맞춘다.
    - 작전 행 값(노출, 색조, 채도, 대비, 그림자, 심연)은 건드리지 않는다.
    - 그다음 `build_site7_mood_light.py`를 돌린다.
  - `tests/smoke/site7_battle_geometry_smoke.gd`:
    - 공유 통로가 없어지면 `connector_pairs > 0` 검사("No connector shared between missions was compared")가 FAIL한다.
    - 이 검사를 "모든 판(방과 통로)은 한 작전에서만 쓴다" 검사로 바꾼다. 판 경로별로 쓰는 작전을 모으고, 두 작전 이상이면 `"Plate %s used by %s and %s"`로 FAIL한다.
    - 방·통로 조명 비교 코드는 그대로 둔다.
  - `AGENTS.md`: 맵 절과 무드 절의 "missions 4 and 5 ... share the 7 stage-3 connectors", "The stage-3 connectors remain shared" 문장을 고친다. 판을 공유하지 않는다는 것과 위 검사를 적는다.
- 검증: 5.3을 그대로 따른다.
  - 작전 2·3·4·5의 strict audit
  - quick과 full 회귀. `connector_alignment`, `traversal_audit`, 작전 2–5 풀플레이를 본다.
  - 1080p 캡처: 새 통로 14장, 보스방 2장
  - 같은 카메라 비교: S3 통로와 새 통로, 교체 전후 보스방, 보스방 다섯 곳 한 장
  - 타이틀 화면: `scripts/ui/title_screen.gd`의 `TITLE_PLATE`가 `S3_R05`다. 교체 뒤 타이틀을 1080p로 찍어 확인한다.
- 예상 생성량: 16장 × 평균 1.2회 ≈ ImageGen 20회.
- 검증 뒤 **멈추고 보고한다.**

**중단(HOLD) 조건**
- 한 판이 ImageGen 3회 안에 2.1–2.4 규격(카메라 축, 문, 에이프런, 바닥 조명)을 못 맞추면 멈춘다. 그 판을 HOLD로 기록하고 보고한다.
  - 손으로 칠하기, 부분 합성, 로컬 모델로 넘어가지 않는다.
- 회귀 테스트가 실패했는데 원인이 원화 문제면 HOLD로 둔다.
  - 테스트 기준을 낮추지 않는다. 사용자 결정 없이 규칙 문장을 바꾸지 않는다.
- 이 작업은 원화 교체와 연결까지다. 사람의 플레이 승인이나 배포 승인을 대신하지 않는다. 웹 배포는 사용자가 따로 허락해야 한다.

---

## 7. 최소안 (전면 재제작을 미룰 때만)

방 24장은 두고 통로 21장만 다시 만드는 안이다. 규격은 2.1–2.5의 통로 부분을 따른다. 양 끝은 이웃 방의 문 앞 바닥 색과 밝기를 참조 이미지로 맞춘다.

우선순위:
1. 색조 충돌 7장: `S1_C04`, `S1_C06`, `S1_C07`, `S2_C04`, `S2_C06`, `S3_C06`, `S3_C07`
   - 갈래 통로(C06·C07)는 ↘로 새로 그린다. 5.2의 3·4번(↘ 비반전 지원)이 필요하다.
2. 밝기 차가 1스톱을 넘는 5장: `S1_C01`, `S1_C02`, `S2_C02`, `S2_C05`, `S3_C01`

이 안으로 해결되지 않는 것:
- 방마다 다른 카메라 각도
- 방 바닥의 색 캐스트(S3_R03 채도 0.70 등)
- 벽을 덮고 들어가는 데크(문 없음)
- 좁은 스테이지 2·3 방

이 문제들은 남는다. 그래서 기본 판정은 전면 재제작이다.
