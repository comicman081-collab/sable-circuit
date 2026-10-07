# SITE-7 작전 6–10 맵 판 75장 — Codex 작업 지시서

작성: 2026-09-29. 대상: 이 저장소에서 작업하는 Codex. 사용자 지시(2026-09-29): "작전 즉, 스테이지를 10까지 확장해봐라."

**진행 상태 (2026-10-02).** 작전 6–10의 판 75장이 모두 들어왔고 작전 6–10 모두 출격 가능하다(작전 10은 2026-10-02 사용자 지시 "작전 10 켜라"로 켰다). 이 문서는 판을 만들던 때의 지시서이므로 아래 0절의 "출격할 수 없다"와 `deployable`에 관한 문장은 그때의 상태다.

이 문서는 작전 6–10의 **맵 판 75장**만 다룬다. 설계, 적, 무드, 통합 절차는 `docs/production/SITE7_OPERATIONS_6_10_DESIGN_KO.md`가 본문이고, 보스 5기는 `docs/production/SITE7_OPERATIONS_6_10_BOSSES_CODEX_PROMPT_KO.md`가 다룬다.

작전 9–10(판 30장)의 작업 순서, 작전 6–8을 만들며 굳은 규칙, 켜기까지는 `docs/production/SITE7_OPERATIONS_9_10_PRODUCTION_ORDER_KO.md`(2026-09-30)가 본문이다. 아래 4절의 작전 9·10 표는 그 문서 6절에 그대로 옮겨져 있다.

Codex에 처음 보낼 메시지:

> `AGENTS.md`를 먼저 읽고, `docs/production/SITE7_OPERATIONS_6_10_PLATES_CODEX_PROMPT_KO.md`와 `docs/production/SITE7_MAP_KIT_V2_CODEX_PROMPT_KO.md`의 1–3절을 끝까지 읽어라. **단계 A0(작전 6 파일럿 3장)** 만 진행해라. 3장을 만들어 1080p 검토 시트로 보고하고 멈춰라. 규칙 순위는 `AGENTS.md` > 이 문서 > 맵 키트 문서다.

---

## 0. 범위

- 작전 6–10은 판을 15장씩(방 8 + 통로 7) 쓴다. 합계 75장이다. 작전 1–5의 75장과 합쳐 150장이 되고, **어떤 판도 두 작전이 함께 쓰지 않는다.** `AGENTS.md`의 규칙이고 `tests/smoke/site7_battle_geometry_smoke.gd`가 검사한다.
- 지금 작전 6–10은 캠페인 데이터에 올라 있지만 판이 없어서 출격할 수 없다(`data/story/site7_campaign.json`의 `"deployable": false`). 한 작전의 판 15장과 보스가 모두 끝나면 **그 작전만** 켠다. 그래서 작전 하나씩, 순서대로 끝낸다. 작전 6이 끝나기 전에는 7을 시작하지 않는다.
- 예상 생성량: 판 75장 × 평균 1.5–2회 ≈ ImageGen 110–150회.
  - 맵 키트 v2 실적(`art_src/environments/site7_v2/SITE7_MAP_KIT_V2_MANIFEST.md`): 파일럿 3장에 20회(`S1_R02` 9, `S1_C01` 4, `S1_C06` 7), 규격이 잡힌 뒤 작전 1의 12장에 14회.
  - 그래서 작전 6에 파일럿(단계 A0)을 두고, 규격이 잡히면 나머지를 이어 간다. 작전 7–10은 파일럿 없이 시작한다.

## 1. 규칙

원문 순위는 `AGENTS.md` > 이 문서 > `docs/production/SITE7_MAP_KIT_V2_CODEX_PROMPT_KO.md`다. 맵 키트 문서의 **1절(규칙), 2절(규격), 3.1–3.3절(프롬프트 코어, 방 블록, 통로 블록)을 그대로** 따른다. 이 문서는 그 위에 작전 6–10의 판별 표를 얹고, 다음 네 가지만 다르다.

1. **참조 이미지**: 이미 승인된 v2 판이 기준이다.
   - Image 1: 그 판의 "바닥 기준" 스테이지 3 판(`assets/environments/site7_v2/stage03/<기준 ID>/<기준 ID>_GAME.png`). 카메라, 축척, 바닥 재질, 문 규격에만 쓴다. 통로는 "크기 기준" 통로 판을 쓴다.
   - Image 2: `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png`(화질과 재질).
   - 통로에는 양 끝 방의 새 판을 참조로 더해도 된다. 문틀과 벽이 이어지는지 맞출 때만 쓴다.
   - **벽 구조는 새로 그린다.** 기준 판의 벽 모양, 기계 배치, 실루엣을 옮기지 않는다.
2. **통로 벽 구조**: 작전마다 공통 벽 문법이 있다(4절 각 작전 머리). 통로의 `{IDENTITY}` 앞에 붙인다.
3. **문 조합**: 작전의 구조(오르막/내리막, 갈래 부모)가 정한다. 4절 표를 그대로 쓴다. 표에 없는 쪽에는 문을 그리지 않는다. 작전 6–10에는 봉인 격벽이 필요 없다.
4. **구분 기준**: 새 75장은 S1–S5의 75장과도, 서로와도 벽 실루엣이 달라야 한다.
   - 검수 때 같은 자리(방 순서, 통로 번호)의 S3 판과 나란히 놓고 확인한다.
   - 한 작전의 방 8장도 서로 달라야 한다.
   - 바닥 모양(긴 육각형, 비대칭 다이아몬드)은 달라도 된다. 표준 데크와 중성 조명은 그대로다.

추가로 지킨다.
- 판은 불투명 RGB다. 알파, 크로마 키, 초록 배경을 쓰지 않는다(캐릭터용 알파 규칙은 배경 판에 해당하지 않는다).
- 건축 밖은 평평한 거의 검정(`#07090D`)이다. 그라데이션, 하늘, 구름, 안개를 넣지 않는다. 런타임이 이 검정을 투명 마스크로 바꾸고 코드로 그린 심연 배경을 그 자리에 보여 준다. 작전 8의 새벽 하늘도 마찬가지다.
- 방마다 다른 분위기(밝기, 채도, 조명 웅덩이)는 런타임 무드가 입힌다. 원화 바닥에 분위기를 그려 넣지 않는다(맵 키트 2.3).
- Codex의 생성물은 저장소로 옮기고 SHA-256을 남긴다. 작업 이미지는 작전 하나가 끝날 때까지 지우지 않는다.

## 2. 판 분류와 프롬프트 채우기

방 분류(`{TYPE}`, `{SIZE}`는 맵 키트 3.2의 자리표시다). 바닥은 늘 "바닥 기준" 판 이상으로 만든다.

| 분류 | 뜻 | `{TYPE}` | `{SIZE}` 최소 | 종횡비 |
|---|---|---|---|---|
| NC | 비전투 방 | `non-combat room` | 850 × 450 | 16:9 (1672×941) |
| CR | 전투방 | `combat room` | 1000 × 560 | 16:9 |
| CC | 전투 복도 | `combat corridor` | 1300 × 380 | 2:1 (1774×887)도 가능(`S3_R04` 선례) |
| BA | 보스 아레나 | `boss arena` | 1100 × 520 | 16:9 |
| BC | 보스 복도 | `boss approach corridor, the boss stands at the exit end` | 1300 × 380 | 2:1 |

통로 판: ↗ 주 경로 통로는 2:1(1774×887), ↘ 갈래 통로는 1:1(1254×1254). 크기와 데크 길이·폭은 "크기 기준" S3 통로와 같다.

통로 프롬프트(맵 키트 3.3)의 값:

| 종류 | `{DIRECTION}` | `{WALL_SIDE}` | `{END_A}` | `{END_B}` |
|---|---|---|---|---|
| ↗ 주 경로 통로 | `lower-left to upper-right (ascending)` | `upper-left` | `lower-left` | `upper-right` |
| ↘ 갈래 통로 | `upper-left to lower-right (descending)` | `upper-right` | `upper-left` | `lower-right` |

- `{ACCENT_A}`는 `{END_A}` 쪽 방의 ACCENT, `{ACCENT_B}`는 `{END_B}` 쪽 방의 ACCENT다. 4절 통로 표의 두 열이 이미 그 순서다.
- **내리막 작전(7, 9)의 주 경로 통로**는 판을 ↗로 그리지만 길은 위 오른쪽 끝(앞 방)에서 아래 왼쪽 끝(다음 방)으로 내려간다. 그래서 아래 왼쪽 끝은 **다음 방**의 색이다. 표가 이미 그렇게 적혀 있다(맵 키트 4절 "스테이지 4 통로"와 같은 규칙).
- 통로 `{IDENTITY}`는 4절의 문장을 그대로 쓴다. 문장은 `{END_A}` 쪽 구조가 `{END_B}` 쪽 구조로 바뀌는 순서다.
- 생성 순서: 그 작전의 방 8장(R01 → R06, O01, O02) → 통로 7장(C01 → C07). 한 장을 받으면 바로 검사한다(카메라 축 22.5°–30.5°, 문 위치, 문 앞 에이프런, 바닥 조명, 바닥에 금지 사항 없음).

## 3. 작전 구조 한눈에

| 작전 | 주 경로 | 갈래 | 방 문 조합 |
|---|---|---|---|
| 6 VERDANT LOCK | 오르막 | O01←R01, O02←R03 | R01 NE/SE; R02 SW/NE; R03 SW/NE/SE; R04 SW/NE; R05 SW/NE; R06 SW; O01 NW; O02 NW |
| 7 COLD STORAGE | 내리막(`reverse`) | O01←R02, O02←R05 | R01 SW; R02 NE/SW/SE; R03 NE/SW; R04 NE/SW; R05 NE/SW/SE; R06 NE; O01 NW; O02 NW |
| 8 SWITCHYARD | 오르막 | O01←R04, O02←R05 | R01 NE; R02 SW/NE; R03 SW/NE; R04 SW/NE/SE; R05 SW/NE/SE; R06 SW; O01 NW; O02 NW |
| 9 MEMORY VAULT | 내리막(`reverse`) | O01←R04, O02←R03 | R01 SW; R02 NE/SW; R03 NE/SW/SE; R04 NE/SW/SE; R05 NE/SW; R06 NE; O01 NW; O02 NW |
| 10 ZERO POINT | 오르막 | O01←R05, O02←R02 | R01 NE; R02 SW/NE/SE; R03 SW/NE; R04 SW/NE; R05 SW/NE/SE; R06 SW; O01 NW; O02 NW |


## 4. 작전별 판 목록 (75장)

표 읽는 법: `분류`는 2절, `문`은 그 방에서 실제로 쓰는 변, `바닥 기준`은 참조 이미지(Image 1)로 쓰는 스테이지 3 판이다.

### 작전 6 VERDANT LOCK — `S6_*`, `assets/environments/site7_v2/stage06/`

- 지역: Site-7 Hydroponic Wing (`MIS_CH01_06`)
- 주제: 온실 · 수경재배동. 밝은 에메랄드와 흰 재배등, 습한 안개, 포화도 높음
- 구조: 오르막: 길은 아래 왼쪽에서 위 오른쪽으로 올라간다. 갈래: `O01_STORES`는 `R01_AIRLOCK`에서, `O02_NURSERY`는 `R03_LAB`에서 나간다.
- 통로 공통 벽 문법(`S6_C*`의 `{IDENTITY}` 앞에 붙인다): `hydroponic gantry: frosted-glass wall panels with grow-lamp rails and condensation runs, irrigation pipes along the back wall only; the railing is a lattice rail over the void;`
- 바닥에 그리지 않는 것: 물, 흙, 식물, 이끼, 젖은 얼룩을 바닥에 그리지 않는다. 초록은 벽과 설비의 색이다.

**방**

| 새 ID | 방 · 종류 | 분류 | 문 | 바닥 기준 |
|---|---|---|---|---|
| `S6_R01` | R01_AIRLOCK · 비전투 | NC | NE, SE | S3_R01 |
| `S6_R02` | R02_GALLERY · 전투 복도 | CC | SW, NE | S3_R04 |
| `S6_R03` | R03_LAB · 비전투(연구) | NC | SW, NE, SE | S3_R03 |
| `S6_R04` | R04_PUMPS · 엘리트 | CR | SW, NE | S3_R02 |
| `S6_R05` | R05_ATRIUM · 보스 | BA | SW, NE | S3_R05 |
| `S6_R06` | R06_LIFT · 비전투(탈출) | NC | SW | S3_R06 |
| `S6_O01` | O01_STORES · 비전투 | NC | NW | S3_O01 |
| `S6_O02` | O02_NURSERY · 비전투(연구) | NC | NW | S3_O02 |

**IDENTITY / ACCENT** (`{IDENTITY}`, `{ACCENT}`)

| 판 | IDENTITY | ACCENT |
|---|---|---|
| `S6_R01` Hydro Airlock | sealed hydroponic airlock: heavy glass-and-steel lock ribs, condensation streaks on the wall panels and misting manifolds along the back walls; no water or plants on the walkable floor | pale green |
| `S6_R02` Planter Gallery | long grow gallery: stacked hydroponic planter troughs and grow-lamp racks set behind low glass barriers along both back walls; the walkable floor stays bare steel | emerald green |
| `S6_R03` Germination Lab | germination laboratory: seed-sorting benches, sample refrigerators and scanner arms against the back walls | teal-white |
| `S6_R04` Irrigation Pumps | irrigation pump hall: vertical pump housings, valve manifolds and sluice gates built into the walls, sealed sump grilles at the wall base | aqua green |
| `S6_R05` Grow Atrium | tiered grow atrium: stepped terrace walls with sealed planter beds, an armoured air-handling tower housing and vent stacks along the back walls; open central arena floor. No round iris, no concentric rings, no circular portal | lime yellow-green |
| `S6_R06` Seed Lift | seed-pallet freight lift: vertical guide rails and lift-cage machinery on the back wall | green |
| `S6_O01` Seed Stores | cold-chain seed lockers and pallet racks along the walls | amber |
| `S6_O02` Antenna Nursery | antenna nursery: rows of sensor masts in raised beds behind glass barriers, signal-analysis cabinets along the walls | soft cyan |

**통로**

`{ACCENT_A}`는 앞 방(아래 왼쪽 끝), `{ACCENT_B}`는 다음 방(위 오른쪽 끝)이다. 갈래는 `{ACCENT_A}` = 갈라지는 방(위 왼쪽 끝), `{ACCENT_B}` = 갈래 방(아래 오른쪽 끝)이다.

| 새 ID | 연결(길 순서) | 문 · 방향 | `{ACCENT_A}` | `{ACCENT_B}` | 크기 기준 |
|---|---|---|---|---|---|
| `S6_C01` | R01_AIRLOCK → R02_GALLERY | ↗ 판, R01 NE 문 → R02 SW 문 | R01 Hydro Airlock · pale green | R02 Planter Gallery · emerald green | S3_C01 |
| `S6_C02` | R02_GALLERY → R03_LAB | ↗ 판, R02 NE 문 → R03 SW 문 | R02 Planter Gallery · emerald green | R03 Germination Lab · teal-white | S3_C02 |
| `S6_C03` | R03_LAB → R04_PUMPS | ↗ 판, R03 NE 문 → R04 SW 문 | R03 Germination Lab · teal-white | R04 Irrigation Pumps · aqua green | S3_C03 |
| `S6_C04` | R04_PUMPS → R05_ATRIUM | ↗ 판, R04 NE 문 → R05 SW 문 | R04 Irrigation Pumps · aqua green | R05 Grow Atrium · lime yellow-green | S3_C04 |
| `S6_C05` | R05_ATRIUM → R06_LIFT | ↗ 판, R05 NE 문 → R06 SW 문 | R05 Grow Atrium · lime yellow-green | R06 Seed Lift · green | S3_C05 |
| `S6_C06` | R01_AIRLOCK → O01_STORES | ↘ R01 SE → O01 NW (반전 금지) | R01 Hydro Airlock · pale green | O01 Seed Stores · amber | S3_C06 |
| `S6_C07` | R03_LAB → O02_NURSERY | ↘ R03 SE → O02 NW (반전 금지) | R03 Germination Lab · teal-white | O02 Antenna Nursery · soft cyan | S3_C07 |

**통로 IDENTITY** (`{IDENTITY}` = 위 공통 벽 문법 + 아래 문장)

- `S6_C01`: `hydro-airlock lock ribs and misting manifolds becoming planter troughs and grow-lamp racks`
- `S6_C02`: `planter troughs and grow-lamp racks becoming germination benches and sample refrigerators`
- `S6_C03`: `germination benches and sample refrigerators becoming pump housings and valve manifolds`
- `S6_C04`: `pump housings and valve manifolds becoming terraced planter beds and air-handling housings`
- `S6_C05`: `terraced planter beds and air-handling housings becoming seed-pallet lift guide rails`
- `S6_C06`: `hydro-airlock lock ribs and misting manifolds becoming cold-chain seed lockers`
- `S6_C07`: `germination benches and sample refrigerators becoming antenna-mast planting beds`

### 작전 7 COLD STORAGE — `S7_*`, `assets/environments/site7_v2/stage07/`

- 지역: Site-7 Cryo Archive (`MIS_CH01_07`)
- 주제: 냉동 보관고. 밝은 서리 흰색과 분홍 비상등, 낮은 채도의 차가운 강철
- 구조: 내리막(`reverse`): 길은 위 오른쪽에서 아래 왼쪽으로 내려간다. 판은 ↗로 그린다. 갈래: `O01_REAGENTS`는 `R02_FREEZE`에서, `O02_RECORDER`는 `R05_VAULT`에서 나간다.
- 통로 공통 벽 문법(`S7_C*`의 `{IDENTITY}` 앞에 붙인다): `cryo transfer bridge: thick insulated cladding, frost-rimed coolant conduits and vacuum-jacketed pipes on the back wall only; the railing is a rimed steel rail over the void;`
- 바닥에 그리지 않는 것: 서리, 얼음, 눈, 물을 바닥에 그리지 않는다. 서리는 벽, 배관, 설비에만 낀다. 바닥은 마른 건메탈 강철이다.

**방**

| 새 ID | 방 · 종류 | 분류 | 문 | 바닥 기준 |
|---|---|---|---|---|
| `S7_R01` | R01_INTAKE · 비전투 | NC | SW | S3_R01 |
| `S7_R02` | R02_FREEZE · 전투방 | CR | NE, SW, SE | S3_R02 |
| `S7_R03` | R03_LEDGER · 비전투(연구) | NC | NE, SW | S3_R03 |
| `S7_R04` | R04_COMPRESSORS · 엘리트(전투 복도) | CC | NE, SW | S3_R04 |
| `S7_R05` | R05_VAULT · 보스 | BA | NE, SW, SE | S3_R05 |
| `S7_R06` | R06_LOCK · 비전투(탈출) | NC | NE | S3_R06 |
| `S7_O01` | O01_REAGENTS · 비전투 | NC | NW | S3_O01 |
| `S7_O02` | O02_RECORDER · 비전투(연구) | NC | NW | S3_O02 |

**IDENTITY / ACCENT** (`{IDENTITY}`, `{ACCENT}`)

| 판 | IDENTITY | ACCENT |
|---|---|---|
| `S7_R01` Cryo Intake | cryo-archive intake dock: frost-rimed transfer rails, heavy vacuum doors set into the walls and insulated cladding | ice white |
| `S7_R02` Deep Freeze Hall | deep-freeze storage hall: rows of vacuum-jacketed storage vaults built into the back walls, coolant trunk lines along the wall base | magenta |
| `S7_R03` Thermal Ledger | thermal-ledger control room: temperature-log consoles and cryo telemetry boards along the walls | pale silver-blue |
| `S7_R04` Compressor Deck | compressor deck: massive refrigeration compressors and heat-rejection fins built into the back walls, pressure relief stacks | cold teal |
| `S7_R05` Cryo Vault | cryogenic vault: a stepped wall of armoured coolant tanks and a central cooling column housing along the back walls; open central arena floor. No round iris, no concentric rings, no circular portal | hot pink-white |
| `S7_R06` Cargo Lock | cargo airlock: heavy pressure-lock frames and transfer rails on the back wall | green |
| `S7_O01` Reagent Stores | reagent and coolant canister racks along the walls | amber |
| `S7_O02` Cold Recorder | cold-signal recorder: frost-rimed sensor drums and analysis racks | lavender |

**통로**

주 경로 통로 5장(C01–C05)은 `reverse`다. `{ACCENT_A}`(아래 왼쪽 끝)는 다음 방, `{ACCENT_B}`(위 오른쪽 끝)는 앞 방이다.

| 새 ID | 연결(길 순서) | 문 · 방향 | `{ACCENT_A}` | `{ACCENT_B}` | 크기 기준 |
|---|---|---|---|---|---|
| `S7_C01` | R01_INTAKE → R02_FREEZE | ↗ 판, R01 SW 문 → R02 NE 문 | R02 Deep Freeze Hall · magenta | R01 Cryo Intake · ice white | S3_C01 |
| `S7_C02` | R02_FREEZE → R03_LEDGER | ↗ 판, R02 SW 문 → R03 NE 문 | R03 Thermal Ledger · pale silver-blue | R02 Deep Freeze Hall · magenta | S3_C02 |
| `S7_C03` | R03_LEDGER → R04_COMPRESSORS | ↗ 판, R03 SW 문 → R04 NE 문 | R04 Compressor Deck · cold teal | R03 Thermal Ledger · pale silver-blue | S3_C03 |
| `S7_C04` | R04_COMPRESSORS → R05_VAULT | ↗ 판, R04 SW 문 → R05 NE 문 | R05 Cryo Vault · hot pink-white | R04 Compressor Deck · cold teal | S3_C04 |
| `S7_C05` | R05_VAULT → R06_LOCK | ↗ 판, R05 SW 문 → R06 NE 문 | R06 Cargo Lock · green | R05 Cryo Vault · hot pink-white | S3_C05 |
| `S7_C06` | R02_FREEZE → O01_REAGENTS | ↘ R02 SE → O01 NW (반전 금지) | R02 Deep Freeze Hall · magenta | O01 Reagent Stores · amber | S3_C06 |
| `S7_C07` | R05_VAULT → O02_RECORDER | ↘ R05 SE → O02 NW (반전 금지) | R05 Cryo Vault · hot pink-white | O02 Cold Recorder · lavender | S3_C07 |

**통로 IDENTITY** (`{IDENTITY}` = 위 공통 벽 문법 + 아래 문장)

- `S7_C01`: `vacuum-jacketed storage vaults becoming frost-rimed intake rails and vacuum doors`
- `S7_C02`: `temperature-log consoles becoming vacuum-jacketed storage vaults`
- `S7_C03`: `refrigeration compressors and heat-rejection fins becoming temperature-log consoles`
- `S7_C04`: `armoured coolant tanks and cooling-column housing becoming refrigeration compressors and heat-rejection fins`
- `S7_C05`: `cargo pressure-lock frames becoming armoured coolant tanks and cooling-column housing`
- `S7_C06`: `vacuum-jacketed storage vaults becoming reagent and coolant canister racks`
- `S7_C07`: `armoured coolant tanks and cooling-column housing becoming cold-signal recorder drums`

### 작전 8 SWITCHYARD — `S8_*`, `assets/environments/site7_v2/stage08/`

- 지역: Site-7 Surface Maglev Yard (`MIS_CH01_08`)
- 주제: 지상 자기부상 선로 야적장, 새벽. 유일한 밝은 지상 작전: 옅은 금색 빛, 낮은 채도, 긴 그림자, 신호등
- 구조: 오르막: 길은 아래 왼쪽에서 위 오른쪽으로 올라간다. 갈래: `O01_DEPOT`는 `R04_JUNCTION`에서, `O02_DISPATCH`는 `R05_TERMINAL`에서 나간다.
- 통로 공통 벽 문법(`S8_C*`의 `{IDENTITY}` 앞에 붙인다): `maglev service walkway: catenary mast brackets, cable trays and signal lamps along the back wall only; the railing is a yellow-and-black safety rail over the void;`
- 바닥에 그리지 않는 것: 선로, 침목, 자갈, 풀을 바닥에 그리지 않는다. 하늘, 구름, 지평선도 그리지 않는다(건축 밖은 평평한 거의 검정이고, 새벽 하늘은 런타임이 그린다).

**방**

| 새 ID | 방 · 종류 | 분류 | 문 | 바닥 기준 |
|---|---|---|---|---|
| `S8_R01` | R01_GATE · 비전투 | NC | NE | S3_R01 |
| `S8_R02` | R02_MARSHALLING · 전투 복도 | CC | SW, NE | S3_R04 |
| `S8_R03` | R03_TOWER · 비전투(연구) | NC | SW, NE | S3_R03 |
| `S8_R04` | R04_JUNCTION · 엘리트(전투 복도) | CC | SW, NE, SE | S3_R04 |
| `S8_R05` | R05_TERMINAL · 보스(긴 접근 복도, 보스는 출구 끝) | BC | SW, NE, SE | S3_R02 |
| `S8_R06` | R06_PLATFORM · 비전투(탈출) | NC | SW | S3_R06 |
| `S8_O01` | O01_DEPOT · 비전투 | NC | NW | S3_O01 |
| `S8_O02` | O02_DISPATCH · 비전투(연구) | NC | NW | S3_O02 |

**IDENTITY / ACCENT** (`{IDENTITY}`, `{ACCENT}`)

| 판 | IDENTITY | ACCENT |
|---|---|---|
| `S8_R01` Yard Gate | maglev yard gatehouse: heavy gate frames, catenary mast brackets and signal gantries against the walls | safety yellow |
| `S8_R02` Marshalling Track | marshalling corridor: parallel guideway girders behind low barriers, switch machines and signal boxes built into the back walls; the walkable floor is a bare steel platform with no rails or ties on it | signal blue |
| `S8_R03` Signal Tower | signal-control tower interior: interlocking consoles and relay racks along the walls | pale gold |
| `S8_R04` Switch Junction | switch junction: heavy points machinery and cross-over girders framing the back walls, warning lamps | signal red |
| `S8_R05` Depot Terminal | maglev terminal hall: a tall gantry-crane frame and buffer-stop machinery along the back walls at the far end of a long approach hall; open floor. No round iris, no concentric rings, no circular portal | white-gold |
| `S8_R06` Departure Platform | departure platform: a sealed maglev capsule berth and guide rails on the back wall | green |
| `S8_O01` Parts Depot | spare-parts racks and pallet lifts along the walls | orange |
| `S8_O02` Dispatch Office | dispatch office: blank status panels, radio racks and a large route-board frame with no lettering along the walls | steel blue |

**통로**

`{ACCENT_A}`는 앞 방(아래 왼쪽 끝), `{ACCENT_B}`는 다음 방(위 오른쪽 끝)이다. 갈래는 `{ACCENT_A}` = 갈라지는 방(위 왼쪽 끝), `{ACCENT_B}` = 갈래 방(아래 오른쪽 끝)이다.

| 새 ID | 연결(길 순서) | 문 · 방향 | `{ACCENT_A}` | `{ACCENT_B}` | 크기 기준 |
|---|---|---|---|---|---|
| `S8_C01` | R01_GATE → R02_MARSHALLING | ↗ 판, R01 NE 문 → R02 SW 문 | R01 Yard Gate · safety yellow | R02 Marshalling Track · signal blue | S3_C01 |
| `S8_C02` | R02_MARSHALLING → R03_TOWER | ↗ 판, R02 NE 문 → R03 SW 문 | R02 Marshalling Track · signal blue | R03 Signal Tower · pale gold | S3_C02 |
| `S8_C03` | R03_TOWER → R04_JUNCTION | ↗ 판, R03 NE 문 → R04 SW 문 | R03 Signal Tower · pale gold | R04 Switch Junction · signal red | S3_C03 |
| `S8_C04` | R04_JUNCTION → R05_TERMINAL | ↗ 판, R04 NE 문 → R05 SW 문 | R04 Switch Junction · signal red | R05 Depot Terminal · white-gold | S3_C04 |
| `S8_C05` | R05_TERMINAL → R06_PLATFORM | ↗ 판, R05 NE 문 → R06 SW 문 | R05 Depot Terminal · white-gold | R06 Departure Platform · green | S3_C05 |
| `S8_C06` | R04_JUNCTION → O01_DEPOT | ↘ R04 SE → O01 NW (반전 금지) | R04 Switch Junction · signal red | O01 Parts Depot · orange | S3_C06 |
| `S8_C07` | R05_TERMINAL → O02_DISPATCH | ↘ R05 SE → O02 NW (반전 금지) | R05 Depot Terminal · white-gold | O02 Dispatch Office · steel blue | S3_C07 |

**통로 IDENTITY** (`{IDENTITY}` = 위 공통 벽 문법 + 아래 문장)

- `S8_C01`: `yard gate frames and catenary masts becoming guideway girders and switch machines`
- `S8_C02`: `guideway girders and switch machines becoming interlocking consoles and relay racks`
- `S8_C03`: `interlocking consoles and relay racks becoming points machinery and cross-over girders`
- `S8_C04`: `points machinery and cross-over girders becoming gantry-crane frame and buffer-stop machinery`
- `S8_C05`: `gantry-crane frame and buffer-stop machinery becoming capsule berth and guide rails`
- `S8_C06`: `points machinery and cross-over girders becoming spare-parts racks and pallet lifts`
- `S8_C07`: `gantry-crane frame and buffer-stop machinery becoming route-board frame and radio racks`

### 작전 9 MEMORY VAULT — `S9_*`, `assets/environments/site7_v2/stage09/`

- 지역: Sealed Memory Vault (`MIS_CH01_09`)
- 주제: 봉인된 기억 저장고, 성당 같은 서가. 짙은 남보라와 금빛 필라멘트, 대비 높음
- 구조: 내리막(`reverse`): 길은 위 오른쪽에서 아래 왼쪽으로 내려간다. 판은 ↗로 그린다. 갈래: `O01_BLADES`는 `R04_GALLERY`에서, `O02_RESTORE`는 `R03_CHAPEL`에서 나간다.
- 통로 공통 벽 문법(`S9_C*`의 `{IDENTITY}` 앞에 붙인다): `archive causeway: vertical memory-blade racks and fibre trunks along the back wall only, indigo light strips at the wall base; the railing is a slim brass-trimmed rail over the void;`
- 바닥에 그리지 않는 것: 바닥에 글자 같은 문양, 금빛 웅덩이, 빛 번짐을 그리지 않는다. 금빛과 남보라는 벽과 서가에만 쓴다.

**방**

| 새 ID | 방 · 종류 | 분류 | 문 | 바닥 기준 |
|---|---|---|---|---|
| `S9_R01` | R01_ANTECHAMBER · 비전투 | NC | SW | S3_R01 |
| `S9_R02` | R02_NAVE · 전투방 | CR | NE, SW | S3_R02 |
| `S9_R03` | R03_CHAPEL · 비전투(연구) | NC | NE, SW, SE | S3_R03 |
| `S9_R04` | R04_GALLERY · 엘리트 | CR | NE, SW, SE | S3_R02 |
| `S9_R05` | R05_STACKS · 보스 | BA | NE, SW | S3_R05 |
| `S9_R06` | R06_LIFT · 비전투(탈출) | NC | NE | S3_R06 |
| `S9_O01` | O01_BLADES · 비전투 | NC | NW | S3_O01 |
| `S9_O02` | O02_RESTORE · 비전투(연구) | NC | NW | S3_O02 |

**IDENTITY / ACCENT** (`{IDENTITY}`, `{ACCENT}`)

| 판 | IDENTITY | ACCENT |
|---|---|---|
| `S9_R01` Vault Antechamber | vault antechamber: a monumental blast-door frame with brass-trimmed ribs and plain panel walls | indigo |
| `S9_R02` Index Nave | index nave: towering memory-blade racks in slotted arches along both back walls | gold |
| `S9_R03` Read-Out Chapel | read-out chapel: reader consoles and fibre-bundle risers against the walls | violet |
| `S9_R04` Echo Gallery | echo gallery: rows of resonant relay columns set into the walls behind low barriers | electric blue |
| `S9_R05` Core Stacks | monumental memory-spire housing: slotted memory blades stacked in tall shafts along the back walls and a central read-head column; open central arena floor. No round iris, no concentric rings, no circular portal | white-gold |
| `S9_R06` Archive Lift | archive freight lift: vertical guide rails and lift-cage machinery on the back wall | green |
| `S9_O01` Spare Blades | spare memory-blade racks and maintenance carts along the walls | bronze |
| `S9_O02` Restore Lab | restore laboratory: blade-repair rigs and diagnostic racks along the walls | magenta-violet |

**통로**

주 경로 통로 5장(C01–C05)은 `reverse`다. `{ACCENT_A}`(아래 왼쪽 끝)는 다음 방, `{ACCENT_B}`(위 오른쪽 끝)는 앞 방이다.

| 새 ID | 연결(길 순서) | 문 · 방향 | `{ACCENT_A}` | `{ACCENT_B}` | 크기 기준 |
|---|---|---|---|---|---|
| `S9_C01` | R01_ANTECHAMBER → R02_NAVE | ↗ 판, R01 SW 문 → R02 NE 문 | R02 Index Nave · gold | R01 Vault Antechamber · indigo | S3_C01 |
| `S9_C02` | R02_NAVE → R03_CHAPEL | ↗ 판, R02 SW 문 → R03 NE 문 | R03 Read-Out Chapel · violet | R02 Index Nave · gold | S3_C02 |
| `S9_C03` | R03_CHAPEL → R04_GALLERY | ↗ 판, R03 SW 문 → R04 NE 문 | R04 Echo Gallery · electric blue | R03 Read-Out Chapel · violet | S3_C03 |
| `S9_C04` | R04_GALLERY → R05_STACKS | ↗ 판, R04 SW 문 → R05 NE 문 | R05 Core Stacks · white-gold | R04 Echo Gallery · electric blue | S3_C04 |
| `S9_C05` | R05_STACKS → R06_LIFT | ↗ 판, R05 SW 문 → R06 NE 문 | R06 Archive Lift · green | R05 Core Stacks · white-gold | S3_C05 |
| `S9_C06` | R04_GALLERY → O01_BLADES | ↘ R04 SE → O01 NW (반전 금지) | R04 Echo Gallery · electric blue | O01 Spare Blades · bronze | S3_C06 |
| `S9_C07` | R03_CHAPEL → O02_RESTORE | ↘ R03 SE → O02 NW (반전 금지) | R03 Read-Out Chapel · violet | O02 Restore Lab · magenta-violet | S3_C07 |

**통로 IDENTITY** (`{IDENTITY}` = 위 공통 벽 문법 + 아래 문장)

- `S9_C01`: `memory-blade racks in slotted arches becoming monumental blast-door ribs`
- `S9_C02`: `reader consoles and fibre risers becoming memory-blade racks in slotted arches`
- `S9_C03`: `resonant relay columns becoming reader consoles and fibre risers`
- `S9_C04`: `memory-spire shafts and read-head column becoming resonant relay columns`
- `S9_C05`: `archive lift guide rails becoming memory-spire shafts and read-head column`
- `S9_C06`: `resonant relay columns becoming spare blade racks and maintenance carts`
- `S9_C07`: `reader consoles and fibre risers becoming blade-repair rigs`

### 작전 10 ZERO POINT — `S10_*`, `assets/environments/site7_v2/stage10/`

- 지역: Site-7 Origin Shaft (`MIS_CH01_10`)
- 주제: 근원 갱도. 검은 합금과 흰 빛, 붉은 이음선. 흑백에 가까운 최소 채도와 강한 대비
- 구조: 오르막: 길은 아래 왼쪽에서 위 오른쪽으로 올라간다. 갈래: `O01_VAULT`는 `R05_CORE`에서, `O02_RECORDER`는 `R02_RELAY`에서 나간다.
- 통로 공통 벽 문법(`S10_C*`의 `{IDENTITY}` 앞에 붙인다): `origin approach: monolithic dark-alloy wall plating, exposed structural ribs and a single glowing seam low on the back wall only; the railing is a plain black rail over the void;`
- 바닥에 그리지 않는 것: 바닥을 검게 칠하지 않는다. 바닥은 표준 건메탈 회색 데크다(휘도 0.17–0.24). 검은 합금과 붉은 이음선은 벽에만 둔다.

**방**

| 새 ID | 방 · 종류 | 분류 | 문 | 바닥 기준 |
|---|---|---|---|---|
| `S10_R01` | R01_DESCENT · 비전투 | NC | NE | S3_R01 |
| `S10_R02` | R02_RELAY · 전투방 | CR | SW, NE, SE | S3_R02 |
| `S10_R03` | R03_LOG · 비전투(연구) | NC | SW, NE | S3_R03 |
| `S10_R04` | R04_GALLERY · 엘리트(전투 복도) | CC | SW, NE | S3_R04 |
| `S10_R05` | R05_CORE · 보스 | BA | SW, NE, SE | S3_R05 |
| `S10_R06` | R06_EXIT · 비전투(탈출) | NC | SW | S3_R06 |
| `S10_O01` | O01_VAULT · 비전투 | NC | NW | S3_O01 |
| `S10_O02` | O02_RECORDER · 비전투(연구) | NC | NW | S3_O02 |

**IDENTITY / ACCENT** (`{IDENTITY}`, `{ACCENT}`)

| 판 | IDENTITY | ACCENT |
|---|---|---|
| `S10_R01` Sealed Descent | sealed descent shaft terminus: monolithic dark-alloy wall plating with a single glowing seam low on the wall and a heavy sealed hatch frame | cold white |
| `S10_R02` First Relay | origin relay chamber: black-alloy relay obelisks standing in wall alcoves, thin red conduit lines along the wall base | warning red |
| `S10_R03` Answer Log | answer-log reading room: dark-alloy record columns and slim reader consoles along the walls | pale violet |
| `S10_R04` Null Gallery | null gallery: two rows of tall black-alloy null emitters set into the back walls, hairline red seams between the panels | bone white |
| `S10_R05` Origin Core | monolithic origin-core housing: a vast black-alloy monolith bracketed into the back walls with hairline red seams and heavy structural ribs; open central arena floor. No round iris, no concentric rings, no circular portal | white-red |
| `S10_R06` Way Out | origin-shaft service lift: vertical guide rails and lift-cage machinery on the back wall | green |
| `S10_O01` Reserve Vault | sealed reserve vault: armoured storage lockers and heavy supply cases along the walls | amber |
| `S10_O02` First Recorder | first-signal recorder: dark-alloy recording drums and a single lit console on the back wall | teal |

**통로**

`{ACCENT_A}`는 앞 방(아래 왼쪽 끝), `{ACCENT_B}`는 다음 방(위 오른쪽 끝)이다. 갈래는 `{ACCENT_A}` = 갈라지는 방(위 왼쪽 끝), `{ACCENT_B}` = 갈래 방(아래 오른쪽 끝)이다.

| 새 ID | 연결(길 순서) | 문 · 방향 | `{ACCENT_A}` | `{ACCENT_B}` | 크기 기준 |
|---|---|---|---|---|---|
| `S10_C01` | R01_DESCENT → R02_RELAY | ↗ 판, R01 NE 문 → R02 SW 문 | R01 Sealed Descent · cold white | R02 First Relay · warning red | S3_C01 |
| `S10_C02` | R02_RELAY → R03_LOG | ↗ 판, R02 NE 문 → R03 SW 문 | R02 First Relay · warning red | R03 Answer Log · pale violet | S3_C02 |
| `S10_C03` | R03_LOG → R04_GALLERY | ↗ 판, R03 NE 문 → R04 SW 문 | R03 Answer Log · pale violet | R04 Null Gallery · bone white | S3_C03 |
| `S10_C04` | R04_GALLERY → R05_CORE | ↗ 판, R04 NE 문 → R05 SW 문 | R04 Null Gallery · bone white | R05 Origin Core · white-red | S3_C04 |
| `S10_C05` | R05_CORE → R06_EXIT | ↗ 판, R05 NE 문 → R06 SW 문 | R05 Origin Core · white-red | R06 Way Out · green | S3_C05 |
| `S10_C06` | R05_CORE → O01_VAULT | ↘ R05 SE → O01 NW (반전 금지) | R05 Origin Core · white-red | O01 Reserve Vault · amber | S3_C06 |
| `S10_C07` | R02_RELAY → O02_RECORDER | ↘ R02 SE → O02 NW (반전 금지) | R02 First Relay · warning red | O02 First Recorder · teal | S3_C07 |

**통로 IDENTITY** (`{IDENTITY}` = 위 공통 벽 문법 + 아래 문장)

- `S10_C01`: `sealed hatch frame and dark-alloy plating becoming relay obelisks in wall alcoves`
- `S10_C02`: `relay obelisks in wall alcoves becoming record columns and reader consoles`
- `S10_C03`: `record columns and reader consoles becoming null emitter rows`
- `S10_C04`: `null emitter rows becoming origin-core monolith housing`
- `S10_C05`: `origin-core monolith housing becoming service lift guide rails`
- `S10_C06`: `origin-core monolith housing becoming armoured reserve lockers`
- `S10_C07`: `relay obelisks in wall alcoves becoming recording drums and a single lit console`

## 5. 파일, 반입, 연결

- 파일 위치와 매니페스트는 맵 키트 5.1과 같다. 스테이지 번호만 `stage06`–`stage10`이다.

  | 종류 | 위치와 이름 |
  |---|---|
  | 원본 | `art_src/environments/site7_v2/stage06/<ID>/<ID>_RAW_NATIVE.png`(받은 그대로) |
  | 마스터 | `<ID>_MASTER.png`(= RAW, 또는 균등 크롭) |
  | 런타임 | `assets/environments/site7_v2/stage06/<ID>/<ID>_GAME.png` + `.import`(`compress/mode=0`, `mipmaps/generate=false`) |
  | 거절 후보 | `art_src/environments/site7_v2/_quarantine/<ID>/attemptNN/`에 해시와 사유. 지우지 않는다. |
  | 매니페스트 | `art_src/environments/site7_v2/SITE7_MAP_KIT_V2_MANIFEST.md`에 작전 절을 덧붙인다: 최종 프롬프트 전문, 참조 목록, 네이티브 크기, RAW/MASTER/GAME SHA-256, 시도 횟수, 거절 사유, 전역 보정 수치 |

- GAME은 네이티브 크기가 기본이다. 줄일 때는 균등 축소만, 확대는 금지다. 판 전체에 똑같이 적용하는 노출 보정 한 번만 GAME에 허용한다(맵 키트 1절).
- 작전 10은 두 자리 번호다. 폴더 `stage10`, 판 ID `S10_R01`, `S10_C01`이다. `site7_battle_art.json`의 통로 ID는 작전 5의 `S05_C01` 선례대로 `S06_C01` … `S10_C01`이고, 방의 `asset_id`는 `ENV_S06_<이름>` 형식이다.
- 판 15장이 반입되면 데이터 연결을 한다. 절차는 설계 문서 6절 A(1–9)이고 이 문서 담당이다. 요약:
  1. `site7_plate_floors.json`에 바닥과 문을 추적한다(`tests/render/site7_walk_graph_capture.gd` 1080p 오버레이로 확인).
  2. `site7_battle_art.json`에 작전 행을 만든다(내리막 작전 7, 9는 주 경로 통로에 `"reverse": true`, 통로마다 `deck`과 `seam_fade`).
  3. `python tools/environment/build_site7_world_layout.py`(`--check`가 PASS해야 한다).
  4. `site7_battle_layouts.json`의 전투방 3개(COMBAT, ELITE, BOSS)와 `site7_environment_props.json`의 소품, `settle_cover_on_floor.gd -- --write`.
  5. `site7_mood.json`의 작전 행과 판 15장 행, `python tools/environment/build_site7_mood_light.py`.
  6. `python tools/environment/audit_site7_plate_lighting.py --mission MIS_CH01_0N --strict`.
- **`deployable`은 지우지 않는다.** 그 작전의 보스까지 끝난 뒤에 설계 문서 6절 C에서 켠다.

## 6. 단계와 멈출 지점

**단계 A0 — 작전 6 파일럿 3장**
- 대상: `S6_R02`(전투 복도, 문 SW·NE), `S6_C01`(↗ 통로), `S6_C06`(↘ 갈래 통로).
- 목적: 새 주제(수경재배)의 벽 문법과 정체성이 표준 데크·중성 조명 규격과 함께 성립하는지 본다. 게임에 연결하지 않는다.
- 3장을 기준 S3 판(`S3_R04`, `S3_C01`, `S3_C06`)과 나란히 놓은 1080p 검토 시트와 원본 크기 크롭을 만든다. `tools/art_pipeline/validate_visual_evidence_1080p.py`를 통과시킨다.
- **멈추고 사용자에게 보고한다.** 승인되면 이 3장이 작전 6–10의 새 주제 기준이다.

**단계 A — 작전 6 (`S6_*`) 나머지 12장 + 연결 + 검증**
- 판 15장을 완성하고 반입한 뒤 6절 A 연결 1–6을 한다.
- 검증(맵 키트 5.3): strict audit, quick 스위트, 1080p 게임 캡처(방 8 + 통로 7), 전체 조감(`build_site7_world_layout.py --preview .cache/...`), S3 판과 나란히 놓은 비교.
- 기록: `qa/site7_ops_6_10_plates_<날짜>/README_KO.md`와 증거. 로컬로 커밋한다.
- **멈추고 보고한다.**

**단계 B — 작전 7 (`S7_*`), 단계 C — 작전 8 (`S8_*`), 단계 D — 작전 9 (`S9_*`), 단계 E — 작전 10 (`S10_*`)**
- 각 단계는 단계 A와 같다. 파일럿은 없다. 앞 단계를 보고하고 사용자가 승인한 뒤에 다음 단계를 시작한다.

**중단(HOLD) 조건** (맵 키트 6절과 같다)
- 한 판이 ImageGen 3회 안에 규격(카메라 축, 문, 에이프런, 바닥 조명)을 못 맞추면 멈추고 그 판을 HOLD로 기록해 보고한다. 손으로 칠하기, 부분 합성, 로컬 모델로 넘어가지 않는다.
- 회귀 테스트가 실패했는데 원인이 원화 문제면 HOLD로 둔다. 테스트 기준을 낮추지 않는다.
- 이 작업은 원화 반입과 연결까지다. 사람의 플레이 승인이나 배포 승인을 대신하지 않는다. GitHub 작업과 웹 배포는 하지 않는다.
