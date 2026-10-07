# SITE-7 작전 11과 챕터 2의 시작 — UPLINK ARRAY (확장 항목 5 작업 지시서)

작성: 2026-10-06, Claude. 사용자 지시 "남은것들 해"에 따른 지시서다. **이 문서를 쓴 시점에는 아무 것도 시작하지 않았다.** 작전 6–10과 같은 분담이다: 그림(판 15장과 보스 한 기)은 Codex의 내장 ImageGen만 만들고, 데이터·코드·시험·기록은 Claude가 한다(`AGENTS.md`의 "Bosses of operations 6-10" 선례). 사용자가 분담을 따로 정하면 그것이 이긴다. 규칙 순위: `AGENTS.md` > 이 문서.

이 문서는 작전 6–10의 문서를 복사하지 않는다. **그대로 따르는 것**과 **작전 11에서 달라지는 것**만 적는다. 이야기, 이름, 색, 수치는 모두 **제안**이고 사용자의 결정이다(11절). 아래 파일 줄 번호와 개수는 2026-10-06 `39176d13`에서 읽고 센 값이다.

따르는 문서:
- 판 규칙과 규격: `docs/production/SITE7_MAP_KIT_V2_CODEX_PROMPT_KO.md`(1–3절)와 `docs/production/SITE7_OPERATIONS_6_10_PLATES_CODEX_PROMPT_KO.md`(1–3절, 5–6절). 이 문서의 4절 표는 그 문서 4절의 작전별 표와 같은 모양이다.
- 작전 6–8에서 굳은 거절 원인, 문 모양, 보스 아레나 크기, 램프와 심연 규칙, 켜기 전 점검: `docs/production/SITE7_OPERATIONS_9_10_PRODUCTION_ORDER_KO.md`
- 설계와 켜는 절차(6절 C): `docs/production/SITE7_OPERATIONS_6_10_DESIGN_KO.md`
- 보스: `docs/production/SITE7_OPERATIONS_6_10_BOSSES_CODEX_PROMPT_KO.md`

## 0. 왜 작전 11인가, 그리고 어디가 큰 일인가

작전 1–10은 모두 열려 있다. 사람이 열 작전을 한 번 하고 나면 할 일은 반복(REDLINE, 장비 모으기)뿐이다. 작전 11은 그 뒤의 첫 걸음이다. 한 작전이 아니라 **세 가지**가 같이 온다.

1. **챕터라는 개념**: 코드는 챕터를 모른다. 캠페인 행은 평평한 목록이고(`site7_campaign.gd`), "CHAPTER 01"은 화면 문구 여덟 곳(2.2)에 박혀 있고, `chapter_complete`는 "행이 모두 클리어"다(`campaign_progression.gd:193`). 실제로 챕터 필드가 있는 곳은 미션 파일의 `chapter_id`(`story_stage_01.gd:801`이 읽고 결과 요약에 싣는다)와 실행 번호 접두사(`campaign_progression.gd:58`, 기본 `CH01`)뿐이다.
2. **열 개를 가정한 곳**: id 숫자를 `right(2)`로 읽는 곳 8군데(6개 파일), id를 `"MIS_CH01_%02d" % n`으로 만들거나(32개) `range(1, 11)`로 도는(33개) 시험·도구 파일 49개(작전 id를 한 번이라도 이름 붙이는 파일까지 치면 95개), 미션 id가 키인 데이터 파일 열 개(`site7_battle_layouts`, `site7_mood`, `site7_battle_art`, `site7_seam_light`, `site7_world_layout`, `site7_environment_props`, `site7_campaign`, `enemy_profiles`, `site7_enemy_body_plan`, 미션 JSON).
3. **새 그림 16점**: 판 15장과 보스 한 기. 작전 6–10에서 판 한 작전이 끝나기까지 20–34번의 생성이 걸렸다.

## 1. 설정 제안 (사용자의 결정)

- **이야기 고리**: 작전 10의 답 기록(`ANSWER LOG`)은 "the message the carrier was built to receive, and the reply it has sent every hour since the blackout"(`MIS_CH01_10.json:169`)라고 적혀 있다. **매 시간 보낸 답에는 받는 쪽이 있다**는 것이 열린 고리다. 제안: 그 받는 쪽은 지상의 **UPLINK ARRAY**이고, 코어가 멈춘 뒤에도 마지막 송신이 한 번 더 나갔다.
- **작전 11 이름**: `UPLINK ARRAY`. 지역: 소금 평원 위의 야간 안테나 어레이와 그 밑의 케이블 갱도(지금까지의 열 작전은 수경 구역, 침수, 냉동, 용광로, 해상, 선로, 서고, 수직 갱도라서 겹치지 않는 지상의 밤이다).
- **보스**: `ZENITH ARRAY`. 키가 크고 면이 평평한 위상배열 탑. 기존 보스 열 기와 실루엣이 겹치지 않아야 한다(`boss_lineup` 캡처로 확인).
- 이야기 문장은 자리표시다. 사용자가 정하기 전에는 `data/story/site7_campaign.json`에 넣지 않는다. **작전 10의 마지막 대사**("Chapter 01 complete. All ten operations are available for recovery runs and upgrades.", `site7_campaign.json:142`)는 작전 11이 켜지는 날에 고친다. 그 전에는 후속 작전을 이름 붙이거나 약속하지 않는다(`AGENTS.md`).

## 2. 챕터와 열 작전 가정 (Claude)

### 2.1 id: `MIS_CH01_11`을 권한다

`MIS_CH02_01`처럼 챕터를 id에 넣으면 아래가 모두 깨진다: 화면의 작전 번호(8군데가 id 끝 두 자리를 읽는다: `demo_music.gd:56`, `game_flow.gd:114`, `briefing_screen.gd:111`, `base_lobby.gd:255`, `mission_results.gd:109`·`:110`, `title_screen.gd:137`·`:180`), 음악 선택(`stage_key`), 장면 상태 이름(`"STAGE_" + id.right(2)`가 `STAGE_01`과 겹친다), 그리고 시험·도구 32개의 id 조립과 `site7_campaign_data_smoke.gd:350`의 "행 N의 id는 `MIS_CH01_N`" 규칙. 얻는 것은 id의 겉모양뿐이다. 챕터는 데이터 필드(`chapter_id`)가 맡는다. id를 `MIS_CH02_11`로 하면 숫자 읽기는 살지만 시험 조립과 행 규칙은 여전히 고쳐야 한다. 사용자가 id에 챕터를 원하면 그때 비용을 다시 잰다.

### 2.2 화면의 챕터 문구 (작전 11을 켜는 날 함께 고친다)

| 곳 | 지금 | 켜는 날 |
|---|---|---|
| `briefing_screen.gd:111` | `CHAPTER 01  //  OPERATION %s  //  MISSION BRIEFING` | 행의 `chapter` |
| `mission_results.gd:110` | `CHAPTER 01  //  OPERATION %s  //  DEBRIEF` | 행의 `chapter` |
| `base_lobby.gd:255` | `OPERATION %s  //  CHAPTER 01` | 행의 `chapter` |
| `base_lobby.gd:265` | `CH01 COMPLETE // REPLAY AVAILABLE` | 챕터별 완료 |
| `title_screen.gd:161` | `CAMPAIGN  //  CHAPTER 01`(진행 막대의 머리말) | 마지막으로 열린 챕터 |
| `title_screen.gd:180` | `CHAPTER COMPLETE  ▸  REPLAY ANY OPERATION` | 챕터별 완료 |
| `title_screen.gd:96` | `SITE-7 CONTAINMENT  //  CHAPTER 01  //  BLACKOUT PROTOCOL`(게임 부제) | 사용자 결정 |
| `demo_intro.gd:21` | 인트로 자막 `CHAPTER 01` | 그대로(인트로는 챕터 1의 것) |

캠페인 행에 `chapter`(없으면 1)를 두고 `MissionCatalog.chapter_of(id)`가 읽는다. 미션 파일의 `chapter_id`는 `"CH02"`로 쓴다(이미 `story_stage_01.gd:801`이 읽는다). 실행 번호 접두사(`issue_run_id`)는 `CH01` 그대로 둔다: 저장에 `run_serial` 하나뿐이고, 접두사를 바꾸면 계약 뽑기(`RunContract.build(run_id)`)의 입력이 달라진다. `chapter_complete`의 뜻("모든 행이 클리어")은 행 열한 개가 되면 챕터 1의 끝이 아니라 전체의 끝이 되므로, 챕터별 함수와 `all_chapters_complete`로 나눈다. 저장 형식은 클리어 목록(id 문자열)이라 바뀌지 않는다. 바뀌면 저장 버전을 올리고 v3–v6 고정물이 모두 열려야 한다.

### 2.3 행은 그림과 함께 넣는다 (권고)

held-back 행(`"deployable": false`)은 작전 6–10의 선례처럼 목록에 "IN PREPARATION"으로 뜬다. 그런데 지금 열 작전을 모두 마친 플레이어의 화면은 "CH01 COMPLETE // REPLAY AVAILABLE"이고, 행이 하나 생기면 `chapter_complete`가 거짓이 되어 그 문구가 사라진다(`site7_campaign_progression_smoke.gd:108`이 그 뜻을 못 박는다). 지인에게 건네는 닫힌 시험 빌드를 생각하면 **판과 보스가 들어오기 전에는 행을 넣지 않는다**. 설계는 이 문서가 기록한다(`staging` 블록 없이). 사용자가 "작전 11 준비 중" 예고를 원하면 그때 held-back 행(작전 6–10의 `staging` 블록, 상태 `ART_PENDING`)으로 넣는다. 어느 쪽이든 판 15장과 보스가 오기 전에 `deployable`을 켜지 않고, 다른 작전의 판이나 보스 그림을 빌리거나 대체 그림을 그리지 않는다.

### 2.4 제목 화면의 진행 막대 (고쳤다: `b4050519`)

옛 `title_screen.gd`는 작전마다 막대 조각을 60 px 간격으로 놓았다. 상자는 x=916에서 시작하고 화면 폭은 1,280이라 조각 일곱 번째부터(작전 7–10) 화면 밖이었다. `TitleScreen.campaign_segments`가 이제 조각 수를 상자 폭(300 px) 안에 넣고, 다섯 개까지는 옛 60 px 간격을 그대로 쓴다. `title_geometry`(quick)가 길이 1–20과 실제 제목 화면(전부 깬 것과 아무것도 안 깬 것)을 본다. 열한 번째 작전은 이 계산에 그대로 들어가므로 따로 고칠 것이 없다.

### 2.5 시험과 도구

- `site7_campaign_data_smoke.gd`의 열 작전 밀도 규칙, 행 id 규칙(`:350`), 낡은 반복문 검사(`stale_loop_gaps`, 이미 N작전 일반형)와 그 `PER_OPERATION_FILES` 목록이 열한 작전을 보게 넓힌다. 줄이지 않는다.
- 러너: `run_regression_suite.py:149`의 `range(1, 11)`을 11로 넓혀 `full_op_11`을 넣는다(전체 90 → 91, 빠른 58은 그대로: 2026-10-06 `title_geometry`와 `room_rule`이 빠른 시험에 들어와 56 → 58). `tools/environment/audit_nav_pockets.gd:44`도 같다. `upgrade_economy_smoke.gd:225`의 수입 합도 같이 넓힌다.
- `tools/maintenance/per_operation_fps.py`(기본 `--ops 1-10`)와 `per_operation_fps_probe.gd`(`:18`, `:41`, `:54`의 1–10)를 11까지 허용한다.
- 같은 작업 묶음에 든 시험 중 id를 직접 이름 붙인 것(`deploy_warmer_smoke`, `elite_affix_smoke`, `firing_lane_search_smoke`, `floor_segment_smoke`, `site7_boss_registry_smoke`, `zone_hazard_smoke`, `test_site7_mood_contact_compare.py`, 저장 고정물)은 대부분 "작전 10까지"라서 줄이지 않고 11을 더한다.

## 3. 작전 구조 제안 (사용자의 결정)

| 항목 | 값 | 이유 |
|---|---|---|
| 경로 | 오르막(↗, `reverse` 없음) | 오르막 일곱(1·2·3·5·6·8·10), 내리막 셋(4·7·9). 새 통로 해법이 필요 없다. |
| 갈래 | `O01_DEPOT`는 `R02_FEED`에서, `O02_LOGGER`는 `R03_CONTROL`에서 | 지금까지 쓴 갈래 부모의 쌍은 {3,4}(작전 1·2·4·9), {3,5}(3), {2,4}(5), {1,3}(6), {2,5}(7·10), {4,5}(8)다. {2,3}은 아직 없다. 보급이 첫 전투방 바로 뒤라서 정예 방 앞에서 치료할 수 있다(작전 8·10은 보급이 정예 방이나 보스 방 뒤라서 봇이 가장 힘들었다). |
| 방 종류 | R01 비전투(진입), R02 전투방, R03 비전투(연구), R04 정예(전투 복도), R05 보스 아레나, R06 비전투(탈출), O01 보급, O02 연구 | 6–10과 같다. 방 뼈대가 같아서 시험 규칙도 그대로다. |
| 심연 `style` | `dust`(새 스타일): 별빛 아래 먼지바람과 멀리서 치는 번개 | 코드로 그린 한 장의 사각형(그림 없음). `site7_abyss_backdrop.gd:16`의 `STYLES`(지금 열 개) 끝에 더하고 셰이더에 열한 번째 블록을 만든다. 웹은 안개 옥타브 절반. |
| 심연 밝기 | 판을 가린 패스로 잰 투명 구멍의 평균 휘도 0.06 이상 | "검은 배경 금지"(`AGENTS.md`의 "Operation 10 void lit"). 작전 1–7·9가 잰 0.062–0.107의 아래쪽 끝이다. 가까운 검정으로 돌아가지 않는다. |
| 음악 | 새 곡 없음 | `sound/music/catalog.json`의 자기 곡은 다섯이라 작전 11은 `stage_key`가 `stage1`을 고른다. 새 곡은 소리 일이라 별도 결정이다. |

## 4. 판 15장 (Codex)

규칙, 규격, 프롬프트 틀, 참조 이미지, 거절 원인은 위의 두 문서를 그대로 따른다. 스테이지 폴더는 `assets/environments/site7_v2/stage11/`, 판 id는 `S11_R01`, `S11_C01` … 이다. 한 판은 한 작전에만 속한다(`site7_battle_geometry_smoke.gd`가 검사).

- 지역: Surface Uplink Array (`MIS_CH01_11`)
- 주제: 소금 평원 위의 야간 안테나 어레이와 케이블 갱도. 어두운 건메탈 강철, 나트륨 주황 작업등, 차가운 백색 보조등, 낮은 채도
- 구조: 오르막(길은 아래 왼쪽에서 위 오른쪽으로 올라간다). 갈래: `O01_DEPOT`는 `R02_FEED`에서, `O02_LOGGER`는 `R03_CONTROL`에서 나간다.
- 통로 공통 벽 문법(`S11_C*`의 `{IDENTITY}` 앞에 붙인다): `array service gantry: insulated cable looms and conduit racks on the back wall only, low sodium work lamps on the rail posts; the railing is a steel lattice rail over the void;`
- 바닥에 그리지 않는 것: 소금, 모래, 먼지 더미, 물웅덩이, 바닥을 가로지르는 케이블을 바닥에 그리지 않는다. 소금과 먼지는 벽과 설비의 얼룩으로만 나온다. 바닥은 마른 어두운 건메탈 강철이다.

**방**

| 새 ID | 방 · 종류 | 분류 | 문 | 바닥 기준 |
|---|---|---|---|---|
| `S11_R01` | R01_HATCH · 비전투 | NC | NE | S3_R01 |
| `S11_R02` | R02_FEED · 전투방 | CR | SW, NE, SE | S3_R02 |
| `S11_R03` | R03_CONTROL · 비전투(연구) | NC | SW, NE, SE | S3_R03 |
| `S11_R04` | R04_TRENCH · 엘리트(전투 복도) | CC | SW, NE | S3_R04 |
| `S11_R05` | R05_FOCUS · 보스 | BA | SW, NE | S3_R05 |
| `S11_R06` | R06_LIFT · 비전투(탈출) | NC | SW | S3_R06 |
| `S11_O01` | O01_DEPOT · 비전투 | NC | NW | S3_O01 |
| `S11_O02` | O02_LOGGER · 비전투(연구) | NC | NW | S3_O02 |

문 조합은 모두 작전 6–8에 같은 모양이 이미 있다(R01 NE: 작전 8, R02 SW·NE·SE: 작전 7, R03 SW·NE·SE: 작전 6, R04 SW·NE: 작전 6·7, R05 SW·NE: 작전 6).

**IDENTITY / ACCENT** (`{IDENTITY}`, `{ACCENT}`)

| 판 | IDENTITY | ACCENT |
|---|---|---|
| `S11_R01` Surface Hatch | surface hatch vestibule: a heavy pressure door frame in a bare steel stairwell, cable-trench stairs and work lamps on the walls, hazard stripes on the wall panels only | cold white |
| `S11_R02` Feed Hall | cable feed hall: rows of thick insulated feeder conduits and breaker cabinets along both back walls, a low junction block in each back corner | amber |
| `S11_R03` Control Room | array control room: operator desks with dark spectrum displays and a wall of patch panels against the back walls | teal |
| `S11_R04` Cable Trench | cable trench corridor: long open cable trays on both walls and low transformer blocks set into the wall base, a narrow steel walkway | sodium orange |
| `S11_R05` Focus Bay | focus bay under the array: heavy bearing housings and bracketed antenna mount columns along the back walls, an open central arena floor. No round iris, no concentric rings, no circular portal | cobalt blue |
| `S11_R06` Surface Lift | maintenance lift to the surface: vertical guide rails, a cage frame and signal flags on the back wall | green |
| `S11_O01` Field Depot | field depot: stacked supply cases, spare feed reels on racks and a charging rack along the walls | warm yellow |
| `S11_O02` Sky Logger | sky logger room: tape drums and racked recorders along the walls, one lit console under a ceiling skylight grid | pale blue-white |

**통로**

`{ACCENT_A}`는 앞 방(아래 왼쪽 끝), `{ACCENT_B}`는 다음 방(위 오른쪽 끝)이다. 갈래는 `{ACCENT_A}` = 갈라지는 방(위 왼쪽 끝), `{ACCENT_B}` = 갈래 방(아래 오른쪽 끝)이다.

| 새 ID | 연결(길 순서) | 문 · 방향 | `{ACCENT_A}` | `{ACCENT_B}` | 크기 기준 |
|---|---|---|---|---|---|
| `S11_C01` | R01_HATCH → R02_FEED | ↗ 판, R01 NE 문 → R02 SW 문 | R01 Surface Hatch · cold white | R02 Feed Hall · amber | S3_C01 |
| `S11_C02` | R02_FEED → R03_CONTROL | ↗ 판, R02 NE 문 → R03 SW 문 | R02 Feed Hall · amber | R03 Control Room · teal | S3_C02 |
| `S11_C03` | R03_CONTROL → R04_TRENCH | ↗ 판, R03 NE 문 → R04 SW 문 | R03 Control Room · teal | R04 Cable Trench · sodium orange | S3_C03 |
| `S11_C04` | R04_TRENCH → R05_FOCUS | ↗ 판, R04 NE 문 → R05 SW 문 | R04 Cable Trench · sodium orange | R05 Focus Bay · cobalt blue | S3_C04 |
| `S11_C05` | R05_FOCUS → R06_LIFT | ↗ 판, R05 NE 문 → R06 SW 문 | R05 Focus Bay · cobalt blue | R06 Surface Lift · green | S3_C05 |
| `S11_C06` | R02_FEED → O01_DEPOT | ↘ R02 SE → O01 NW (반전 금지) | R02 Feed Hall · amber | O01 Field Depot · warm yellow | S3_C06 |
| `S11_C07` | R03_CONTROL → O02_LOGGER | ↘ R03 SE → O02 NW (반전 금지) | R03 Control Room · teal | O02 Sky Logger · pale blue-white | S3_C07 |

**통로 IDENTITY** (`{IDENTITY}` = 위 공통 벽 문법 + 아래 문장)

- `S11_C01`: `surface hatch stair frames and hazard-striped wall panels becoming feeder conduit racks and breaker cabinets`
- `S11_C02`: `feeder conduit racks and breaker cabinets becoming operator desks and patch panels`
- `S11_C03`: `operator desks and patch panels becoming open cable trays and transformer blocks`
- `S11_C04`: `open cable trays and transformer blocks becoming bearing housings and bracketed antenna mount columns`
- `S11_C05`: `bearing housings and bracketed antenna mount columns becoming lift guide rails and signal flags`
- `S11_C06`: `feeder conduit racks and breaker cabinets becoming stacked supply cases and feed-reel racks`
- `S11_C07`: `operator desks and patch panels becoming tape drums and a skylight console`

갈래 통로(C06, C07)의 바닥 윤곽 한계는 `AGENTS.md`의 그대로다(축 22.5–30.5°, `plate_axis`가 지키고 C06·C07만 32.5°까지). 생성은 방 8장(R01 → R06, O01, O02) 다음 통로 7장, 한 번에 한 장이다. 한 장을 받으면 바로 검사한다(카메라 축, 문 위치, 문 앞 에이프런, 바닥 조명, 바닥에 금지 사항 없음). 작전 9–10의 교훈: 새 판은 같은 자리의 S3 판과 나란히 놓아 벽 실루엣이 달라야 한다. 예상 생성량은 판 15장 × 1.5–2회 = 25–30회다(작전 9는 34회, 작전 10의 마지막 단계는 12장에 19회였다).

## 5. 보스 `ZENITH ARRAY` (Codex가 그림, Claude가 등록과 패턴)

- id `BOSS_SITE7_ZENITH_01`, 종류 `anchored_machine`(기존 보스 열 기와 같다). 체력은 작전 10(2,460)보다 높게: 제안 2,700(`campaign_data`가 체력의 증가를 지킨다).
- 그림 규칙은 작전 6–10 보스 문서와 같다: 사람형 없음, 방출구는 눈에 보이는 하나(어느 방향에서 봐도 같은 것: 맨 위 붐 끝의 혼 급전부), 둥근 홍채·동심원·원형 포털 없음, 알파 규칙, 원본이 런타임까지 그대로. 눈에 보이는 기계의 키는 220–270 px(`site7_boss_registry_smoke.gd`).
- 프롬프트 `{DESIGN}`: `A tall, flat-faced phased-array tower on a squat rectangular pedestal: four rectangular antenna panels of different widths stacked on one central spindle and angled at different yaws, thick cable looms down the spindle into the pedestal, and a slim boom at the very top carrying one glowing horn feed that reads the same from every direction. Overall shape: tall and narrow with flat panel faces, clearly different from a round dish. Cobalt blue status lamps along the panel edges.`
- **아레나 색**: 열 보스의 아레나 색은 ANCHOR 보라 `#8572FF`, RELAY 붉은색 `#d8283c`, REMNANT 연한 얼음 파랑 `#bfe8ff`, FORGE 구리 `#b97b4b`, CARRIER 하늘 `#62c9eb`, AERATOR 라임 `#8fdc4a`, CRYO 분홍 `#ff7fc8`, GANTRY 노랑 `#ffd84a`, ARCHIVE 청록 `#2fe0b4`, ORIGIN 흰색 `#f4efe8`이다. 아직 쓰지 않은 색조는 선명한 코발트 파랑이라 제안 `#3d7bff`이고, 확정은 마스터의 램프 색을 보고 한다. 시험은 문자열 일치만 거르니(`site7_boss_pattern_smoke.gd:172`) 눈으로 열 색과 구분되는지 `boss_lineup` 캡처에서 본다.
- 패턴(Claude가 그림이 온 뒤 정한다): `zenith_sweep`. 방향이 단계적으로 도는 선이 먼저 모든 칸을 미리 보여 주고 한 칸씩 켜진다. 보스 공정성의 한계는 그대로다: 경고 ≥ 1.0 s, 공격당 경고 ≤ 7, 경고 피해 ≤ 20, 투사체 피해 ≤ 24, 300 px 안에 대원 폭 1.5배의 빈 바닥, 가장 느린 걸음(138 px/s)이 경고 0.25 s 전에 닿는다. 실제 R05 방에 격자(100·75·50·40·25·20 px)로 놓고 보스를 방에 맞춘다. 한계는 낮추지 않는다(선례: INDEX SPIRE, ORIGIN CORE).
- **등록할 때 같이 건드리는 곳**: `enemy_profiles.json`, `build_site7_boss_runtime.py`(바이트 그대로 복사와 `--check`), `site7_enemy_tactics.gd`, `combat_hit_vfx.gd` `family_for`, `combat_muzzle_vfx.gd`, `prototype_projectile.gd`(`PRJ_BOSS_ZENITH_*`), `deploy_warmer`, 등록·패턴·결투·방 공정성 시험. 그리고 항목 3이 남긴 함정: 보스가 쓰러질 때 나오는 정찰 표본의 키(`IntelSamples.enemy_key`)는 id의 부분 문자열로 고르므로 새 보스의 키를 일반 `"BOSS"` 검사보다 **먼저** 둔다(안 그러면 표본이 ANCHOR의 것이 된다). 새 표본 키와 분석 행을 둘지는 사용자의 결정이다(둔다면 `upgrade_economy`의 대역 0.9–1.5배는 작전 11의 수입이 늘어서 여유가 생긴다).

## 6. 연결 (Claude, 판이 온 뒤)

작전 6–10과 같은 순서다(`SITE7_OPERATIONS_6_10_DESIGN_KO.md` 6절).

1. `data/visual/site7_battle_art.json`(방 `asset_id`와 통로 id), `site7_plate_floors.json`, `site7_room_art.json`에 행을 넣고 `tools/environment/build_site7_world_layout.py`로 세계 배치를 푼다. 통로의 `reverse`는 쓰지 않는다. 갈래는 미션 JSON의 `"from"`(`O01_DEPOT` ← `R02_FEED`, `O02_LOGGER` ← `R03_CONTROL`)로 정하고 `StoryStage01.branch_parent`로 읽는다.
2. `data/visual/site7_mood.json`: 미션 행(노출, 색조, 채도, 대비, 그림자, `abyss`의 `dust` 스타일)과 판 행(방 등급, 램프, 추가 빛). `tools/environment/build_site7_mood_light.py`로 램프와 투명 구멍 마스크를 만든다. 심연이 밝으면 어두운 벽 틈이 새는지(`void_fill_px`) 판을 가린 패스로 확인한다.
3. `data/visual/site7_battle_layouts.json`: 방의 전투 바닥, 엄폐, 스폰 슬롯, 보스 `boss_anchor`. 오르막 방이므로 먼 쪽이 위 오른쪽이다. `tools/environment/settle_cover_on_floor.gd -- --write`를 변화가 없을 때까지 반복한다.
4. `data/visual/site7_environment_props.json`: 엄폐 소품(kArchive 모델, `AGENTS.md`의 규칙). 방마다 하나 이상.
5. 미션 JSON(`data/missions/MIS_CH01_11.json`)과 캠페인 행(`chapter`: 2, `requires`: `MIS_CH01_10`)에 브리핑·디브리핑·적 구성·보상. 새 일반 로봇(항목 4)이 있으면 그것을, 없으면 기존 여섯 로봇을 쓴다.
6. 화면 문구(2.2), 열한 작전으로 넓힌 시험(2.5), 작전 10의 마지막 대사(1절).

## 7. 시험과 켜기 전 점검

- `site7_battle_geometry_smoke.gd`(판이 미션 행을 따름, 빛 24개 상한, 투명 구멍, 통로 축, 배경), `site7_connector_alignment_smoke.gd`, 엄격 감사(판 15장과 이음 14곳), `plate_axis`, `world_layout --check`, `mood_light --check`가 모두 통과한다.
- `boss_room_fairness`, `boss_pattern`, `boss_duel`, `boss_registry`: 새 보스 포함. 50 px 기본 격자가 ORIGIN의 실패를 놓친 적이 있어 보스 방은 100에서 20 px까지 돌린다.
- `full_op_11` 봇: 켜는 날 러너의 단독 플레이스루에 들어간다. 봇이 잡음이 있는 작전(3·6·7·8·10)의 선례처럼 한 번의 WIPED는 회귀가 아니고 `--only`로 다시 돌린다. 새 종류의 이유(경로, 보상, 탈출, 시간 초과)로 서면 결함이다.
- 같은 세션 회전 FPS 비교: `python tools/maintenance/per_operation_fps.py --ops 1-11`(2.5에서 11까지 허용한 뒤). 작전 1–10의 2026-10-06 기준값은 `qa/per_operation_fps_20261006/`에 있다(195–251 fps, 한 작전도 가볍거나 무겁다고 표시되지 않았다).
- 기록: `qa/site7_op11_preenable_<날짜>/`(판 재측정, 엄격 감사, 빠른 시험 전체, 보스 격자, 봇 다섯 번)와 `qa/site7_op11_enable_<날짜>/`. 마지막 줄에 "이 기록은 그림·플레이·균형 승인이 아니다."

## 8. 순서와 멈출 지점

1. **A0 (Claude, 그림 없이, 지금 해도 된다)**: 2.4의 진행 막대 결함 수정과 시험. 행은 넣지 않는다(2.3).
2. **A1 (Codex)**: 보스 마스터. Claude가 등록, 패턴, 시험, `boss_lineup` 포함. 이 단계에서 멈추고 보고한다.
3. **A2 (Codex)**: 판 방 8장 → 통로 7장. 한 장씩, 받자마자 검사. 거절은 사유와 수치를 적어 돌려보낸다.
4. **A3 (Claude)**: 6절의 연결과 7절의 점검, 2.2·2.5의 코드·시험 수정.
5. **A4**: 사용자의 "작전 11 켜라" 뒤에 `deployable`·`staging`이 없는 행으로 켜고 작전 10의 디브리핑을 고친다.

**중단(HOLD) 조건**
- 판이 3번 안에 규격을 못 맞추면 그 판을 HOLD로 기록하고 후보를 보존한 채 보고한다(작전 9–10의 규칙). 규격이나 시험 기준을 낮춰서 통과시키지 않는다.
- 새 `dust` 심연이 가까운 검정으로 읽히거나(휘도 0.06 미만) 판의 어두운 벽 틈이 새면 켜지 않는다.
- 사용자의 승인 없이 행을 `deployable`로 켜지 않는다.

## 9. 이 작업이 건드리지 않는 것

- 승인된 작전 10 그림 17개(`python qa/site7_op10_art_approval_20261002/tools/verify_hashes.py`).
- 작전 1–10의 판, 보스, 무드 행, 심연 행. 바이트 단위로 같아야 한다.
- 보스 공정성, 경제(`upgrade_economy`)의 대역, 2배 클램프, REDLINE 수치, 저장된 플레이어 데이터.
- 작전 11의 보상이 `upgrade_economy`의 대역(연구 0.9–1.5배, 부품·신호 0.5–1.5배)을 넘기면 시험이 먼저 빨개진다. 수입이 늘면 그것은 균형이고 사용자의 결정이다.

## 10. 위험

- 작전 11은 챕터 구조, 새 심연 스타일, 새 보스 패턴, 새 판 15장이 한꺼번에 오는 가장 큰 작업이다. 그림이 오기 전(A0)과 후(A3)를 나눈 이유다.
- 사람이 작전 1–10을 한 번도 플레이하지 않은 상태다(`playtest_logs/`가 비어 있다). 챕터 2의 난이도는 지금 정할 수 없고, 켜는 날의 수치는 모두 시작값이다.
- 판 15장은 작전 6–10의 거절 기록처럼 예상보다 많이 걸릴 수 있다(작전 10의 R05는 사용자가 이름 있는 예외로 받았다).

## 11. 사용자의 몫

- 이야기와 이름(챕터 2의 고리, 작전 이름, 보스 이름, 브리핑 대사), `dust` 분위기, 갈래 구조의 승인.
- 작전 11을 지금 시작할지, 사람이 열 작전을 한 번 플레이한 뒤에 시작할지. **권고는 후자다**: 열 작전이 한 번도 플레이되지 않은 채 열한 번째를 얹으면 확인되지 않은 면적만 늘어난다.
- 행을 그림과 함께 넣을지, 미리 "준비 중"으로 보일지(2.3).
- 판 15장과 보스 그림의 승인(승인 전에는 승인된 그림으로 쓰지 않는다).
- "작전 11 켜라".
