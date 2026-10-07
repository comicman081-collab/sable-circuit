# 항목 3 검수 — 보스 정보의 장비화 (분석 5 · 모듈 5 · 무기 2 · 표본 키 8 · 저장 6)

검수일 2026-10-06 · 검수자 Claude · 대상 `453d20cb..98292b3d` (고정물 `4d0a63f2`, 구현 `fb8a5ca8` `4ab13d7a` `c83ddf6c` `d6094211`, 기록 `98292b3d`)
근거 지시서 `docs/production/SITE7_EXPANSION_1_3_CODEX_ORDER_KO.md` (기준 L-01…L-16, C-01…C-11. 보완은 그 9.13절, 이 검수의 요약은 9.14절)

## 판정: **PASS (기술)** — 1차(정적) 검수는 HOLD 사유 없음이었고, 내 Godot 재확인(8절)으로 확정한다. 풀 스위트 87/88(실패 1건은 작전 8 봇의 보스방 전멸, 두 번 돌려 두 번 짐)

1~7절은 **1차(정적) 검수의 기록 그대로**이고(그때는 Godot 신호가 없었다), Godot를 돌린 결과와 최종 판정은 **8절**에 있다. 검사한 코드는 Codex의 `98292b3d`가 아니라 그 위에 내가 사용자 지시로 손질한 `0a14d5b6`이다(8.1, 8.7).

지시서 7절은 "확인할 수 없으면 항목은 HOLD"라고 쓴다. 1차에서 나는 **Godot를 쓰지 않았다**(사용자 신호 없음). 그래서 1차는 두 층이었다.

- **내가 직접 읽고 계산한 것(Godot 없이)**: 범위, 코드 diff 전체, 표본 키 매핑 16개, 무기 DPS와 경제 계산, 모듈 상한, 저장 고정물의 출처, 러너 요약(`summary.json`)의 검사 수 비교, 캡처 7장의 검증기 재실행과 눈으로 보기, 플레이어 저장 파일. 결함은 없었다.
- **Codex가 돌린 것을 기록으로 확인한 것**: `qa/regression_runs/20261006_003832_quick` = **56/56 PASS**(494 s), `20261006_004731_custom` = `m10_intel` 39 · `m13_loadout` 53 · `campaign` 235 **3/3 PASS**(42 s). 둘 다 깨끗한 트리(`d6094211`)에서, `qa/` 가드 0·0·0. 규칙 깨기 9개(Codex)의 실행 기록도 읽었다.
- **아직 못 한 것(Godot 필요, 6절)**: 내가 직접 쓰는 규칙 깨기 표, quick 전체 재실행, 풀 스위트(88개), 선택으로 FPS A/B. 그 전에는 "PASS 확정"이라고 쓰지 않는다. (뒤의 셋은 8절에서 했고, 선택인 FPS A/B만 하지 않았다.)

이 기록은 그림·플레이·균형 승인이 아니다. 모듈 5개·무기 2개·연구비는 9.13.3의 **제안값**이고 사람이 쏴 본 적이 없다.

## 1. 한눈에

| 항목 | 결과 |
|---|---|
| 범위 (`453d20cb..98292b3d`) | 커밋 6개. 코드 5개: `4d0a63f2` 1파일 · `fb8a5ca8` 13파일 +223 −34 · `4ab13d7a` 4파일 +145 −9 · `c83ddf6c` 15파일 +195 −8 · `d6094211` 9파일 +289 −25 (모두 `qa/` 제외 33파일 +846 −69). 기록 `98292b3d` 91파일 +7,984, 전부 `qa/expansion_item3_20261006/` 안 |
| 보호 경로 | `assets` `art_src` `motion_lab_v1` `sound` `data/visual` `tests/smoke/site7_boss_*` 변경 **0**. `upgrade_economy_smoke.gd` · `upgrades.json` 변경 0. `AGENTS.md` · `docs` 변경 0 (Codex). 승인 그림 **17 of 17 unchanged** |
| 러너 | `--list`: **56 quick + 32 full = 88** (이전 52 + 31): 새 quick `intel_supply` `module_expansion` `weapon_expansion` `lab_geometry`, 새 full 전용 `lab_capture_geometry` |
| quick 전체 (Codex, `d6094211`) | **56/56 PASS**, 494 s, 가드 clean |
| 풀 전용 (Codex) | `m10_intel` 39 · `m13_loadout` 53 (46→53) · `campaign` 235 — **3/3 PASS**, 42 s, 가드 clean |
| 검사 수 (C-05) | 지운 `_check` 0. 줄이 바뀐 시험 4개는 모두 *넓히는* 교체(5줄)이고 보고서 3절 표에 있다. 어떤 시험도 이전 PASS 최대보다 줄지 않았다(`campaign_data` 292는 열 작전이 모두 열렸을 때의 정상값 — AGENTS.md "292 with ten open") |
| 보스 시험 (C-11) | `boss_registry` 163 · `boss_pattern` 978 · `boss_duel` 2,184 · `boss_room_fairness` 21 · `robot_roster` 302 — 항목 2 끝과 **같은 숫자** |
| 표본 키 매핑 (L-13) | 작전 1–10의 `enemy_id` 16개를 옛 규칙과 새 규칙에 각각 넣어 비교: 바뀐 것은 **새 보스 5개뿐**(AERATOR · CRYO · GANTRY · ARCHIVE · ORIGIN), 작전 1–5 보스는 ANCHOR 그대로, `BULWARK` `DRONE` `MORTAR` → SECURITY, `RAM` → ABERRANT, `PRISM` `NULL_PYLON` → 없음. 일반 `"BOSS"` 검사를 앞에 두면 새 보스 5개가 전부 ANCHOR가 된다(대조군) |
| 무기 DPS (L-11) | RAIL CARBINE 순간 **57.9** / 지속 **44.3** (호환 ASTER 67.8 · MICA 61.2 이하), NULL BREACHER **96.0** / **54.5** (ROOK 62.7 이하). 상한 100 / 78 이내. 기존 6종의 표는 그대로 |
| 경제 (L-07) | 새 분석 5개의 연구비 합 **900 ≤ 952**. 소비처 5,180 → **6,080**, 수입 4,088 대비 **1.4873배**(대역 0.9–1.5, 여유 0.0127). 분석은 연구만 쓰므로 부품·신호와 `LEGACY` 가격은 그대로. `upgrade_economy` 225검사 PASS, 수정 0 |
| 모듈 상한 (L-04·L-11) | 6개 효과: 지속 +1.0 / +1.0→**+2.0** / +1.5 s, 쿨다운 −20 % ×2, 거리 **+50 px**. 전부 상한(+2.0 s · −25 % · +50 px) 이내이고 **RAIL SPOOL의 거리와 ECHO RELAY의 지속은 상한에 정확히 닿는다**. 피해 보너스를 주는 모듈은 없다(피해 곱셈 줄과 ×2 클램프 줄은 한 줄도 바뀌지 않았다) |
| 저장 (L-08) | `SAVE_SCHEMA_VERSION` 5 → 6. `save_v5.json`: 번호 5, 3키, 분석 3, 무기 6. 쓴 코드의 git blob이 `381ef0fb` · 시작 HEAD · 고정물 직전 커밋에서 모두 `cbd6062f094b…`로 같고, 파일 SHA-256 `0531c6e4…8002`가 보고서와 같다. `contract_save` 175검사(69→175) PASS (v3·v4·v5, 8키·분석 8·무기 8, 새 내용은 잠김·0, 쓰고 읽어 같음) |
| 캡처 7장 (C-08) | 검증기 `--require-dynamic-capture` 직접 재실행 **exit 0**, 7/7 디코드, 1920×1080, SHA-256 7개가 보고서와 일치. 7장 모두 직접 봤다(4절). 이 PASS는 크기와 디코드뿐이다 |
| 플레이어 저장 (C-10) | `campaign_progression_v1.json` SHA-256 `5c600d90…2426ea` 그대로(2026-08-30), `settings.cfg` 없음, 2026-10-05 20:00 이후 바뀐 파일 0. `user://.cache/diag/expansion_item3_20261006`에 빈 폴더 1개(파일 0) |
| 규칙 깨기 (Codex) | 변형 9개 전부 실제 실패와 exit 1: 일반 BOSS 먼저 → `intel_supply` **21**검사 실패, ORIGIN 키 제거 → **8**, 모듈 갈고리 끄기 5개 → 1·1·2·1·1, 무기 실제 피해 0 두 개 → 각 **4**. 내 규칙 깨기는 6절(미실행) |

## 2. 기준 ID별 판정

`PASS`는 위 두 층 중 어느 쪽이 근거인지 괄호로 적는다. `OPEN`은 Godot가 필요해 아직 확인하지 못한 부분이 남았다는 뜻이고 HOLD가 아니다.

### 공통 (C-01 … C-11)

| ID | 판정 | 근거 |
|---|---|---|
| C-01 | PASS (git 읽기) | `git log 453d20cb..HEAD`: 커밋 6개, 모두 로컬, 경로 지정 커밋(`4d0a63f2`는 1파일, `98292b3d`는 `qa/expansion_item3_20261006/`만). push·PR·Pages·Actions 흔적 없음. 작업 트리 clean. Codex의 작업 파일은 git-ignored `.cache/diag/expansion_item3_20261006/`뿐이고 기록(`records/cleanup_manifest.json`)은 그 폴더의 105개 파일(18.9 MiB)을 지웠다고 쓴다 — 내 `.cache/claude_scratch/`는 그대로다. C: 드라이브 전체 검색은 하지 않았다 |
| C-02 | PASS (git + 해시) | `git diff --stat 453d20cb..HEAD -- assets art_src motion_lab_v1 data/visual` 비어 있음. `verify_hashes.py` → 17 of 17 approved files unchanged. `sound/` 변경도 0 |
| C-03 | PASS (Codex 러너) | quick의 `world_layout` `mood_light`가 Codex 실행에서 PASS. `data/visual` 변경 0 |
| C-04 | PASS (git) | `tests/smoke/site7_boss_*` 변경 0, `upgrade_economy_smoke.gd` · `upgrades.json` 변경 0, 보스 경고·와인드업 상수 변경 0. 스크립트 diff에서 클램프·피해 곱셈 줄은 한 줄도 바뀌지 않았다 |
| C-05 | PASS (diff 읽기) | 지운 `_check` 0. 줄이 바뀐 파일 4개를 읽었다: `m13_weapon_loadout_smoke`(무기 카탈로그 6→8, 새 봉투 검사 +4), `run_contract_save_smoke`(5→6, 고정물 `[3,4]`→`[3,4,5]`, 키별·행별 엄격 비교로 쪼갬 +10), `m13_weapon_base_migration_smoke`(6→8), `m10_persistence_smoke`(3키 → `IntelSamples.empty()` 8키). 표본 키·행 비교는 옛 행 **전체 사전 equality**를 id로 찾아 비교하므로 약해지지 않았다. 보고서 3절 표에 파일·이름·이전→이후·이유가 있다 |
| C-06 | PASS (`--list` + 가드) | 88개(56 + 32). 새 시험 5개가 모두 등록됐고 파일을 쓰는 시험은 `Output.path`(`test_output.gd`)를 쓴다(새 시험 4개 + 캡처 1개 모두 확인). 날짜 QA 폴더를 겨냥한 시험 없음. Codex 러너 두 번의 `qa/` 가드 0·0·0. 두 번째 러너 없음 |
| C-07 | PASS (코드 읽기) | 새 효과는 `vfx_painter`의 `streak` `glow` `oval_ring` `fading_beam`과 기존 도우미(`_core` `_sparks` `_shock` `_debris`)뿐. 스크립트 전체 diff에 새 `draw_circle` `draw_colored_polygon` `draw_line` 등 도형별 호출 0. 로봇·연산자 `modulate`/`material` 추가 0. FPS는 주장하지 않았다(보고서 6절) |
| C-08 | PASS | 위 1절 |
| C-09 | PASS (읽기) | 보고서가 6절 8항목을 모두 채운다: 커밋, 시험(`--only`·quick stamp·full 전용 stamp), 상수 표, 데이터 표(분석·무기), 캡처 SHA와 검증기, FPS **미실행**을 명시, 한계, "이 기록은 그림·플레이·균형 승인이 아니다" 문장. 풀 스위트와 봇 비교를 돌리지 않았다고 솔직히 썼다 |
| C-10 | PASS (파일 검사) | 위 1절. 새 시험의 저장은 `res://.cache/…` 프로젝트 안 경로(`--out`), UI 시험은 `persist_campaign=false`. 설정 저장 호출 0 |
| C-11 | PASS (러너 요약) | 1절의 보스 시험 숫자 5개가 항목 2 끝과 같다 |

### 항목 3 (L-01 … L-16)

| ID | 판정 | 근거 |
|---|---|---|
| L-01 | PASS (Codex 시험 + 내 매핑) | `intel_supply` 83검사: 새 보스 5개는 자기 키 1개(런당 한 번), 작전 1–5 보스는 ANCHOR, 보스 10개를 쓰러뜨리고 옛 로봇 갈래를 더하면 분석 8개의 표본 비용이 모두 채워진다(`SECURITY` 비용 2는 BULWARK · DRONE · MORTAR 세 종류로 채움). 중복 처치는 두 번 주지 않는다 |
| L-02 | PASS (내 계산) | 분석 행 8개 모두 10개 필드가 있다(없는 필드 0). 기존 세 행은 diff에서 **한 줄도 바뀌지 않았다**(`intel_discoveries.json` +60 −0). 모듈 id 8개 유일, 새 다섯의 `operator_id`는 ROOK(SPORE FILTER · NULL ANCHOR) · ASTER(FROST LENS · RAIL SPOOL) · MICA(ECHO RELAY) |
| L-03 | PASS (Codex 시험·기록) · OPEN (내 변형) | 모듈 5개 모두 실제 액터의 시전 전·후·해제 값을 잰다(`records/module_expansion.json`, 86검사): SPORE 5.0→6.0→5.0, FROST 4.0→3.2→4.0 (피해 26 불변), RAIL 150→200 · 5.0→4.0 → 원래, ECHO 4.0→6.0 (방어율 0.2 불변), NULL 5.0→6.5 (방어 5.0→6.5). 무기 2종은 실제 탄 소모·펠릿·충돌 피해·자기 피격 가문(`weapon_expansion` 122검사). 대조군은 Codex 변형 9개(위 1절) |
| L-04 | PASS (내 계산 + diff) | 피해 보너스 모듈 0. 쿨다운 −20 %, 지속 +1.0 … +2.0 s, 거리 +50 px: 전부 상한 이내(표 아래 숫자). 피해 곱셈 줄·클램프 줄 변경 0이라 ×2 클램프 안 |
| L-05 | PASS (코드 + 시험 숫자) | 무기 2종 `WPN_DMR_RAIL_01`(ASTER·MICA) · `WPN_SHOTGUN_NULL_01`(ROOK), `PRJ_WEAPON_RAIL_01`/`HIT_WEAPON_RAIL_01` · `PRJ_WEAPON_NULL_01`/`HIT_WEAPON_NULL_01`: 투사체 몸체 · 총구 · 피격이 가문 `WEAPON_RAIL` · `WEAPON_NULL`로 따로 있다(새 id는 `ASTER` 같은 기존 가문 토큰을 담지 않고, `family_for`에서 새 가문 검사가 맨 앞이다). `combat_vfx` 189 → 195검사(가문 표 · 피격 가문 확대). 연산자 손 그림과 두 소리 프로필은 그대로(`assets` 변경 0, `_weapon_art_profile`이 두 필드만 덮는다) |
| L-06 | PASS (시험 + 캡처) · OPEN | 분석이 3쪽으로 모두 닿고(1/3 · 3/3 캡처), 연산자별 모듈 순환(`ModuleCycle_<op>`: EQUIP → NEXT MOD → UNEQUIP), `m10_base_ui`가 처음 상태의 바인딩 `PRISM FOCUS`→ASTER · `BREACH LINER`→ROOK · `SENSOR ARRAY`→MICA를 그대로 확인(10검사, quick 전체 PASS) |
| L-07 | PASS (내 계산 + `upgrade_economy`) | 1절. 음수 대조군(옛 3레벨 상한)은 `upgrade_economy` 안에 그대로 있다. 한 번 클리어로 못 사는 분석은 없다(`intel_supply`의 "all analyses reachable") |
| L-08 | PASS (내 고정물 검사 + Codex 시험) · OPEN (내 왕복) | 1절. v3 · v4 · v5 고정물이 모두 있고 `contract_save`가 셋을 돈다. 내가 새 저장을 만들어 옛 코드로 읽는 왕복은 Godot가 필요해 아직 안 했다 |
| L-09 | PASS (diff) | C-05. 넓어지기만 했다: `m10_base_ui` 10 · `m10_persistence` 27 · `m10_intel` 39 · `m13_*` 9 / 16 / 18 / 53 · `upgrade_economy` 225 · `campaign` 235 — 전부 같거나 늘었다 |
| L-10 | PASS (코드 diff) | `_sync_weapon_unlocks`: 기존 세 줄은 한 줄도 바뀌지 않았고 두 줄만 추가(`ANL_GANTRY_RAIL_MODEL` → RAIL, `ANL_ORIGIN_NULL_MODEL` → NULL) |
| L-11 | PASS (내 계산) | 1절·위 표. 역할 문장이 행마다 있다(`role`). `m13_weapon_loadout`이 `weapons.json`에서 같은 수치를 계산해 확인한다(+4검사). 모듈 상한은 11 참조 |
| L-12 | PASS (grep + 시험) · OPEN (내 변형) | 키·순서의 권위는 `scripts/core/intel_samples.gd` 한 곳(8키, 약어). `campaign_progression`(`INTEL_KEYS` · 초기 사전 · `_sanitize_intel` · `debug_reset`) · `story_stage_01`(`INTEL_KEYS` · `_cargo_intel` · `secured_intel` · `lost_intel_samples` = `IntelSamples.total`) · `base_lobby` · `mission_results` · `story_stage_hud`가 모두 이 파일을 쓴다. 남은 글자 `"SECURITY"`/`"ABERRANT"`는 전리품 `LOT_INTEL_MECHANICAL`과 `debug_seed_intel`의 옛 서명뿐이고 의도다. 표준·REDLINE·선택 계약이 표본을 곱하지 않는다(`intel_supply`가 계약 4종으로 확인). 전멸은 8키 모두 잃고 합계에 센다 |
| L-13 | PASS (내 계산) | 1절. 대조군(`BOSS` 먼저)이 새 보스 5개를 전부 ANCHOR로 만든다는 것을 계산으로 보였고 Codex의 변형 실행이 `intel_supply` 21검사 실패로 증명한다 |
| L-14 | PASS (Codex 시험·기록) · OPEN (내 변형) | 해제하면 정확히 원래 값, 같은 효과를 두 번 적용해도 한 번(갈고리가 시전마다 `has_module`을 읽고 곱셈 캐시가 없다 — 코드 읽기 확인), A에서 B로 바꾸면 B만 남는다, `MODULE_LOCKED` · `MODULE_INCOMPATIBLE` 거절은 `campaign_progression`에 있고 시험이 확인한다. 이미 켜진 스킬은 자연 만료까지 가고 로드아웃은 기지에서만 바뀐다 |
| L-15 | PASS (시험 + 캡처) | `lab_geometry` 3,694검사: 1280×720에서 모든 쪽의 라벨·버튼이 패널 안이고 겹치지 않으며 글자가 상자를 넘지 않는다, 모든 분석이 쪽을 넘겨 닿고 모든 해금 모듈이 순환으로 닿는다. 캡처 1쪽 · 3쪽 · 모듈 순환 후 · 8키 HUD · 8키 결과 화면 모두 1080p. 눈으로 본 결과의 nit는 4절 |
| L-16 | OPEN | Codex의 quick 전체(56/56)와 `--only m10_intel,m13_loadout,campaign`(3/3)은 PASS이고 보스 시험은 같은 숫자다. **내가 돌리는 quick 전체와 풀 스위트는 Godot 신호를 기다린다.** 풀 스위트의 봇 `full_op_06` · `full_op_10`은 항목 2 때부터 알려진 WIPED 위험이 있어 숫자로 보고한다(판정이 아니다) |

모듈 상한의 숫자(L-04 · L-11): SPORE FILTER 지속 5.0 → 6.0 (+1.0 s) · FROST LENS 쿨다운 4.0 → 3.2 (−20 %) · RAIL SPOOL 쿨다운 5.0 → 4.0 (−20 %)와 거리 150 → 200 (+50 px) · ECHO RELAY 지속 4.0 → 6.0 (+2.0 s) · NULL ANCHOR 지속 5.0 → 6.5 (+1.5 s). 상한은 −25 % · +2.0 s · +50 px.

## 3. 내가 코드를 읽고 확인한 것 (Codex 시험이 닿지 않는 곳)

- `OperatorActor._weapon_art_profile()`은 `projectile_profile`과 `hit_vfx_profile` **두 필드만** 복사본에 덮어쓴다. 정체성 · 손 그림 · 두 소리 프로필은 연산자 원본이다.
- 모듈 갈고리는 `_q_cooldown` `_e_cooldown` `_dash_distance` `_bulwark_duration` `_relay_duration` `_scatter_duration`처럼 **시전마다** `actor.has_module(...)`를 읽는다. 누적 곱셈이나 상수 변경이 없어서 "한 번만, 걷으면 원래대로"가 구조적으로 맞다. `Q_COOLDOWNS` · `E_COOLDOWNS` 상수는 그대로이고(ASTER 4.0 / 5.0) 효과 문구의 숫자와 같다.
- `_dash_distance` `_bulwark_duration` `_relay_duration` `_scatter_duration`은 연산자 id를 따로 검사하지 않고 `has_module(...)`만 읽는다(`_q_cooldown` `_e_cooldown`만 `CHR_PROTO_01`을 한 번 더 본다). 모듈은 분석 행의 `operator_id`로 그 연산자에게만 장착되므로(`MODULE_INCOMPATIBLE`) 다른 연산자로 새지 않는다.
- 로비 순환의 선택지는 `discoveries` 행 순서이고 장착된 id가 선택지에 없으면 "NO MODULE" + `EQUIP`(첫 선택지)으로 떨어진다. 마지막 선택지 뒤는 `UNEQUIP`(빈 요청)이고 이 경로는 옛 UI에도 있었다.
- `lost_intel_samples`는 `IntelSamples.total(_cargo_intel)`이다(옛 세 키 합은 지워졌다). `debug_seed_intel`은 옛 서명을 유지하고 추가 키 사전을 받는다.
- `m10_base_ui_action_smoke`가 글자 `"EQUIP"` 버튼 3개를 찾는데 새 UI는 장착 안 된 처음 상태에서 `EQUIP`을 그대로 쓴다(그래서 통과). 이 글자를 바꾸면 그 시험이 깨진다. 풀 전용 시험 가운데 바뀐 UI 글자·노드를 읽는 것은 없다(grep: `demo_integration` `m7_visual` `traversal_audit` `full_op_*` 어디에도 `intel` 참조 0).
- 러너 밖의 `tools/validate_m10_intel_contract.py`는 HUD 글자 `"INTEL  SEC"`(공백 둘)를 찾는 옛 도구로 기준선부터 FAIL이다. 이번에도 FAIL이고 PASS로 세지 않는다(보고서 7절과 같다).

## 4. 화면 7장 (직접 봄)

`qa/expansion_item3_20261006/captures/`, 전부 1920×1080 RGBA. 취향·그림 승인은 사용자의 것이다.

| 장면 | 본 것 |
|---|---|
| `lab_page1.png` · `lab_page3.png` | 분석 목록 `1/3` · `3/3`과 `<` `>` 버튼, 분석 행 3 / 2개, 모듈 칸 `ASTER // LOCKED` 등. 겹침·잘림 없음. 효과 글자는 작지만(약 10 px) 읽힌다 |
| `lab_module_cycle.png` | ASTER `FROST LENS` · ROOK `SPORE FILTER` · MICA `ECHO RELAY`와 `NEXT MOD` `NEXT MOD` `UNEQUIP`, 우상단 `ARMORY MODULE // MOD_ECHO_RELAY EQUIPPED`, 연구 8660. 깨끗하다 |
| `field_intel8.png` | HUD `INTEL SEC 02 ABR 01 ANC 01 AER 01 CRY 01 GAN 01 ARC 01 ORG 01`이 `CARGO` 줄 아래 오른쪽에 들어간다. 힌트 배너와 겹치지 않는다 |
| `results_intel8.png` | `SECURED INTEL` 두 줄, `LOST … INTEL SAMPLES`, `BASE STOCK` 줄과 `INTEL SEC 03 …` 줄. **T-1:** 마지막 `INTEL` 줄이 바로 아래 COMMAND 상자의 왼쪽 막대 맨 위에 닿는다(첫 글자 `I`가 막대와 겹친다) |
| `vfx_wpn_dmr_rail_01.png` | 레일 탄(흰 심 + 시안 곁선 + 사라지는 꼬리)과 총구 포크. **T-2:** 탄이 적이 아니라 커서(왼쪽 위)로 나가서 맞는 장면이 없다 |
| `vfx_wpn_shotgun_null_01.png` | NULL 총구(세 갈래 + 타원 고리)와 오른쪽 아래 작은 충돌 불빛. 가문이 레일과 다르게 보인다 |

결과 화면 카드의 `+11`과 줄의 `SECURED RESEARCH 12`는 같은 값(`secured_research`)에서 나온다. 카드 숫자는 0.5 s 기다렸다가 0.9 s 동안 0에서 올라가는 애니메이션(`mission_results.gd`의 `_stat_tile`)이라 캡처가 12에 닿기 직전에 찍힌 것이다(T-8). 규칙의 문제가 아니다.

## 5. 다듬을 점 (막지 않음 — Codex에 한 줄씩, 사용자가 원하면)

| ID | 무엇 | 왜 |
|---|---|---|
| T-1 | 결과 화면의 둘째 `INTEL` 줄이 COMMAND 상자의 왼쪽 막대에 닿는다 | `mission_results.gd`의 `_campaign_line`이 두 줄이 되며 상자 위쪽 경계 위로 한 줄 밀려 닿았다. 줄 간격 한 칸이나 상자를 6–8 px 내리면 된다. 겹침 검사가 이 쌍을 안 본다 |
| T-2 | 두 VFX 캡처가 적을 향하지 않는다 | `expansion_item3_capture.gd`의 조준점이 월드 좌표 `Vector2.RIGHT`(원점 근처). 적 위치를 조준하면 피격 가문(`HIT_WEAPON_*`)도 화면에 담긴다. headless 가문 시험은 통과했다 |
| T-3 | 최소 글꼴 검사가 없다 | `_fit_lab_label`이 글자를 8 px까지 줄일 수 있고 `lab_geometry`는 "상자를 안 넘는다"만 본다. 실제 캡처에서는 10 px 안팎이라 읽힌다. 하한(예: 10 px)을 검사에 더하면 이후 문구가 길어져도 안 숨는다 |
| T-4 | 샷마다 프로필 깊은 복사 | `_weapon_art_profile()`이 한 발마다 `art_profile.duplicate(true)`. 연사(LMG 0.145 s)와 산탄에서 불필요한 할당이다. 무기를 바꿀 때 한 번 만들어 두면 된다. **측정하지 않았다**(FPS A/B 미실행) |
| T-5 | HUD `_intel_label` 상자가 힌트 배너 상자와 겹친다 | 글자가 오른쪽 정렬이라 화면에서는 안 겹친다(캡처 확인). 상자만 줄이면 겹침 검사가 잡을 수 있다 |
| T-6 | 로비의 모듈 이름 줄 | 해금했지만 장착 안 하면 `NO MODULE`(옛: 모듈 이름). 효과 설명과 툴팁에 이름이 있어 정보는 있으나 처음 보는 사람은 무엇이 해금됐는지 한 번 눌러야 안다. 로비 `SAMPLES` 줄도 전체 이름에서 약어(SEC ABR …)로 바뀌었다. 설계 선택이라 사용자의 눈으로 정할 일 |
| T-7 | 기존 음악 원본 `sound/music/originals/fps_bgm_06_sniper_ridge.wav` | 첫 두 바이트가 `FF FB`라 실제로는 **MP3 데이터에 `.wav` 이름**이다(`2026-09-24`의 `34344749`부터). Codex가 보고서 7절에서 처음 알린 항목 3과 무관한 기존 상태이고 둘 다 고치지 않았다. 항목 6(작전 6–10 음악)에서 다룰 일 |
| T-8 | 결과 화면 캡처가 숫자가 올라가는 중에 찍혔다 | 카드가 `+11`(최종 12). 1.5 s 이상 기다린 뒤 찍으면 최종 값이 담긴다 |

T-1 · T-2 · T-3 · T-4 · T-8은 8절에서, **T-5 · T-6 · T-7은 9절에서 고쳤다**(위 표는 1차 검수 때의 모습이다).

## 6. 아직 못 한 것 (Godot 신호를 기다린다) 

내가 직접 하는 것들이고 Codex는 이미 같은 방향의 기록이 있다. 신호를 받으면 이 순서로 한다.

1. **내 quick 전체**(약 10분, 깨끗한 스냅샷 또는 현재 트리). 요약의 검사 수가 위 1절과 같은지.
2. **규칙 깨기 표**(스냅샷 사본, 원본은 건드리지 않는다). Codex가 안 한 것을 중심으로:
   M1 일반 `BOSS`를 새 보스 앞에 · M2 옛 체인 인라인 복원 · **M3 `lost_intel_samples`를 옛 세 키 합으로** · **M4 `INTEL_KEYS`를 옛 세 키로** · M5 `_sanitize_intel` 되돌림 · M6 모듈 갈고리 6개를 하나씩 · **M7 `_weapon_art_profile`이 `hit_vfx_profile`을 안 덮음** · **M8 RAIL 피해 40으로(지속 80.5 > 78)** · **M9 무기 해금 규칙 한 줄 삭제** · M10 로비 라벨 겹침 · **M11 새 분석의 연구비 합을 +60 올려 6,140(1.502배 > 1.5)으로 — `upgrade_economy`가 빨개져야 한다(여유가 52뿐)** · M12 새 표본 키를 `secured_intel`에서 제외.
   변형마다 "실패한 검사 수 / 전체 검사 수"를 적는다(`negative-control` 교훈).
3. **저장 왕복**: v3 · v4 · v5 고정물을 새 코드로 읽고 쓰고 다시 읽어 같음, 새 v6을 옛 코드(`381ef0fb`)로 읽어도 공통 키가 같음.
4. **모듈 전·후 숫자를 내 손으로**(실제 액터): Codex 기록의 6개 값과 같은지.
5. **풀 스위트 88개**(약 100분, Codex가 쉬는 동안, 다른 세션이 Godot를 쓰지 않을 때). 봇 `full_op_06` · `full_op_10`은 숫자로 보고.
6. (선택) 작전별 FPS A/B: Codex는 재지 않았다. 새 가문은 기존 `vfx_painter` 도우미라 위험이 낮지만 측정한 것은 아니다.

사용자의 몫(판정이 아니다): 모듈 5개 · 무기 2개 · 연구비 900의 수치를 사람이 쏴 보고 정하는 것, T-1…T-8을 Codex에 보낼지, 그리고 항목 4 · 5 · 1D를 언제 시작할지.

## 7. 근거 파일

- Codex 기록: `qa/expansion_item3_20261006/README_KO.md`(+ `records/` 27 · `controls/` 50 · `captures/` 8 · `tools/` 5)
- 러너: `qa/regression_runs/20261006_003832_quick/summary.json`(56/56) · `20261006_004731_custom/summary.json`(3/3). 그 폴더는 git 무시라서 숫자를 `evidence/runner_compare_out.txt`에 옮겨 두었다(시험마다 이전 PASS 최대와 비교: 줄어든 것은 `campaign_data` 292 하나이고 열 작전이 모두 열렸을 때의 정상값, 늘어난 것은 `contract_save` +106 · `combat_vfx` +6 · `m13_loadout` +7, 새 시험 4개는 비교 대상 없음)
- 내 도구(모두 읽기 전용이고 `qa/`에 아무것도 쓰지 않는다) 와 출력:
  - `tools/static_audit.py` → `evidence/static_audit_out.txt`: 범위·보호 경로, 표본 키 매핑 16개와 대조군, 무기 DPS와 봉투, 분석 행 필드, 경제, 모듈 상한, 고정물 출처(blob · SHA-256)
  - `tools/runner_compare.py` → `evidence/runner_compare_out.txt`
  - `tools/cleanup_scope.py` → `evidence/cleanup_scope_out.txt`: Codex의 정리 기록이 지운 105개 파일(18.9 MiB)의 범위는 전부 `.cache/diag/expansion_item3_20261006/` 안이다
- 다시 만들려면 프로젝트 루트에서 `python qa/expansion_item3_review_20261006/tools/static_audit.py`(기준 커밋 `453d20cb`는 스크립트 안에 있다). 캡처 검증기 재실행: `python tools/art_pipeline/validate_visual_evidence_1080p.py --require-dynamic-capture <7개 png>`(`--output`을 주지 않아 파일을 쓰지 않는다)

## 8. 후속 — 내 손질과 Godot 재확인 (2026-10-06 저녁, Claude)

사용자가 Codex를 닫았고(“코덱스 종료다”) Godot 신호를 주었다(“godot 돌려”). 그 직후 “돌리기 전에 코드 수정할꺼 해라”라고 해서, Godot를 돌리기 전에 5절의 T-1·T-2·T-3·T-4·T-8을 **내가 직접** 고쳤다. 항목 1~3에서 Codex가 짠 게임 쪽 코드를 내가 고친 것은 항목 2의 REDLINE 수치(`4158aaaa`)에 이어 두 번째이고, 둘 다 사용자 지시가 있었다. 규칙·수치·그림·소리는 바꾸지 않았고 T-5·T-6·T-7은 그대로 둔다. 증거와 도구는 `followup/`에 있다(`followup/README_KO.md`가 목차). 검사한 코드는 깨끗한 `0a14d5b6`이고, 증거를 더한 커밋(`941a9c3c`, `ccfaa96e`)과 코드가 같다.

### 8.1 손질 — 커밋 2개, 코드는 5곳

| ID | 고친 것 | 파일 | 새 검사 |
|---|---|---|---|
| T-1 | COMMAND 왼쪽 막대를 y 404 / 높이 88 → **416 / 82**. 처음에 414로 옮겼다가 `lab_geometry`가 빨개졌다: 두 줄짜리 BASE STOCK·INTEL 라벨은 글 14에서 줄당 23.5 px라 상자가 45가 아니라 **47 px**이고 415에서 끝난다. 열 작전 × 두 결과(20장면)를 재서 디브리프 글이 3줄(78 px)까지이고 상자 82 px, 하단 498, 버튼 상단 516임을 확인했다 | `scripts/ui/mission_results.gd` | `lab_geometry`: 막대와 겹치는 Label·Button 0개, 재고 글 하단 ≤ 막대 상단(+17검사) |
| T-2 | VFX 캡처가 커서가 아니라 **적을 향해 실제 발사**(적을 발사점 오른쪽 230 px에 놓고 `debug_fire_once()`) | `tests/render/expansion_item3_capture.gd` | 적이 있다는 검사 |
| T-3 | 글꼴 하한 | `tests/smoke/lab_geometry_smoke.gd` | `MIN_FONT` 10 px: 글을 가진 모든 연구소 컨트롤(+294검사) |
| T-4 | `_weapon_art_profile()`의 한 발당 깊은 복사를 **무기·프로필이 바뀔 때만** 만들도록 캐시(`is_same`로 `weapon_spec`·`art_profile` 교체를 감지) | `scripts/actors/operator_actor.gd` | `weapon_expansion` +9검사(122 → 131): 같은 무기는 같은 객체, 무기 교체·프로필 교체는 새로 만들고 값이 같음 |
| T-8 | 결과 화면 캡처가 2.0 s 기다리고 최종 `+12`를 assert(숫자가 올라가는 중에 찍지 않음) | 같은 캡처 | 카드 글이 최종 값과 같다 |

- 게임에 영향이 있는 변경은 T-1(막대 위치)과 T-4(같은 값을 만드는 캐시)뿐이다. T-4는 값이 같다는 것을 시험이 직접 본다. 함수 하나의 비용만 쟀다(탐침 `profile_bench.gd`, 같은 프로세스에서 번갈아 5라운드 × 20,000회): RAIL CARBINE 5.01 → 0.27 µs, NULL BREACHER 5.82–5.91 → 0.33–0.34 µs(두 번 재서, 한 호출당, `same_value=true`). **FPS 주장은 하지 않는다**(`followup/probes/profile_bench_out.txt`).
- T-1은 1080p 네이티브 캡처로 직접 봤다: INTEL 줄과 COMMAND 막대가 더는 닿지 않는다(`followup/polish_native/results_intel8.png`, 검증기 PASS, SHA-256은 `validator_report.json`). T-2의 두 장(`vfx_wpn_*.png`)은 발사 불꽃·탄·적이 오른쪽으로 맞는다.

### 8.2 내 quick 전체와 보조 4개

| 실행 | 결과 |
|---|---|
| quick 전체(`20261006_182512_quick`, 깨끗한 `0a14d5b6`, 621 s) | **56/56 PASS**, `git_dirty` 0, `qa/` 보호 changed / removed / added = 0 / 0 / 0 |
| Codex의 quick(`d6094211`, 494 s)과 검사 수 | 56개 모두 같고 다른 것은 둘뿐: `weapon_expansion` 122 → 131, `lab_geometry` 3,694 → 4,005(둘 다 내 손질이 더한 검사). 내 쪽이 127 s 느렸다(이유는 재지 않았다: 이 PC의 다른 작업 부하일 수 있다. 시험 결과는 같다) |
| `--only m10_intel,m13_loadout,campaign,lab_capture_geometry` (`20261006_183634_custom`) | **4/4 PASS**: 39 / 53 / 235 / 5, 가드 0·0·0. 앞의 셋은 Codex의 기록과 검사 수가 같다. `lab_capture_geometry`의 러너판은 headless라 지형 검사 5개만 돈다 |

### 8.3 규칙 깨기 표 — 변형 27개

복사본(`proj_i3` = `0a14d5b6`)에 한 번에 하나씩 적용해 관련 시험을 돌렸다(`followup/matrix/i3_table.md`가 칸마다 “실패한 검사 / 전체 검사”를 적은 전체 표). 변형이 아닌 기준 실행 16개는 모두 PASS이고 `ERROR:` 줄이 0이다(종료 때 나오는 `resources still in use`는 검사 실패가 아니라서 셈에서 뺐다).

| 묶음 | 변형 | 잡은 시험(실패한 검사 / 전체) | 못 잡은 시험 |
|---|---|---|---|
| 표본 키·흐름 7 | 일반 `BOSS`를 새 보스 앞에(M1) · 옛 체인 복원(M2) · `lost_intel_samples`를 옛 세 키 합으로(M3) · `CampaignProgression.INTEL_KEYS`와 `StoryStage01.INTEL_KEYS`를 옛 세 키로(M4a/b) · `_sanitize_intel` 되돌림(M5) · `secured_intel`에서 ORIGIN 제외(M12) | `intel_supply` **21/83 · 21/83 · 5/83 · 6/83 · 5/83 · 7/83 · 5/83** | `m10_intel`, `campaign`, `contract_save`, `m10_persistence`, `m13_migration` — 전부 초록 |
| 무기 4 | `_weapon_art_profile`이 `hit_vfx_profile`을 안 덮음(M7) · RAIL 피해 40(M8) · RAIL 해금 규칙 삭제 · NULL 해금 규칙 삭제(M9) | `weapon_expansion` **3/131 · 3/131 · 3/131 · 2/131**, RAIL 피해 40은 `m13_loadout` **3/53**도 | `hit_hurt_vfx` · `m13_campaign` · `m13_runtime` · `upgrade_economy` · 해금 규칙 삭제에서 `m13_loadout`·`m13_migration` |
| 경제 3 | 새 분석 연구비 합 +52(경계) · +53 · +60(M11) | `upgrade_economy` **+53: 1/225, +60: 1/225**. +52(6,132 = 정확히 1.5배)는 **초록으로 남는다** — 경계가 맞다 | `m10_intel` |
| 모듈 갈고리 6 | FROST LENS · RAIL SPOOL(쿨다운) · RAIL SPOOL(거리) · SPORE FILTER · ECHO RELAY · NULL ANCHOR 각각 효과가 안 켜짐(M6) | `module_expansion` **각각 1/86**(“실제 효과와 debug 권위가 정확히 한 번 일치”) | `m10_intel` |
| 내 손질 7 | 막대를 옛 위치로(T-1) · 연구소 효과 글 9 px(T-3) · 연구소 상태 라벨을 제목 위로(M10) · 캐시가 무기 교체를 무시 · 캐시가 프로필 교체를 무시 · 샷마다 복사로 되돌림(T-4) · 캡처가 1.0 s만 기다림(T-8) | `lab_geometry` **2/4,005 · 32/4,005 · 15/4,005**, `weapon_expansion` **6/131 · 3/131 · 3/131**, T-8은 **네이티브 캡처만** 잡았다: 변형 `FAIL (19 checks)` “results count-up finished before the capture: +11”, 통제 실행 `PASS (19 checks)` | 상태 라벨 변형에서 `m10_base_ui` 초록. **T-8은 러너의 headless `lab_capture_geometry`로는 안 잡힌다**(카운트업 검사가 네이티브에만 있다) |

읽는 법: 변형 27개 가운데 진짜로 깬 것은 26개이고 하나는 경계(+52)다. 깬 26개 중 25개는 러너의 시험이 잡았고 하나(T-8의 1.0 s 대기)는 네이티브 캡처만 잡았다: **깬 26개 전부 잡혔다.** 경계는 안 잡히는 것이 맞고 실제로 초록으로 남았다. 눈여겨볼 약한 곳은 다음이다(어느 것도 고칠 결함은 아니다).
- **표본 키 규칙은 `intel_supply` 한 시험이 혼자 지킨다.** 다른 저장·흐름 시험(`contract_save`, `m10_persistence`, `m13_migration`)은 고정물이 옛 세 키뿐이라 새 키를 잃는 변형을 못 본다. `intel_supply`가 바뀌거나 빠지면 이 규칙은 아무도 안 본다.
- 모듈 갈고리는 각각 **검사 1개**가 지킨다(`module_expansion`의 “실제 효과와 debug 권위가 일치”). 그 검사 하나가 빠지면 같은 변형이 통과한다.
- `upgrade_economy`는 무기 피해를 지키지 않는다(`weapon_expansion`·`m13_loadout`이 지킨다).

### 8.4 저장 왕복 (옛 코드 `381ef0fb` ↔ 새 코드 `0a14d5b6`)

같은 저장 파일을 옛 코드(형식 5)와 새 코드(형식 6)의 `CampaignProgression`이 각각 읽는다. 읽고 → `snapshot()` → 저장 → 다시 읽기 → 두 번째 저장의 순서이고, 플레이어의 저장은 읽지도 않았다(복사본·고정물만). 도구: `followup/tools/probes/save_probe.gd`, `compare_saves.py`. 출력: `followup/probes/compare_saves_out.txt`.

| 저장 | 새 코드가 읽은 것 vs 옛 코드가 읽은 것 | 왕복 |
|---|---|---|
| v3 · v4 · v5 고정물 | 키 31개 모두 있고, **값이 다른 키는 넷뿐**: `schema_version` 5 → 6, `intel_samples`(옛 세 키는 같고 새 키 다섯이 0), `discoveries`(옛 3행은 변하지 않고 새 5행 추가), `weapon_catalog`(옛 6행은 변하지 않고 새 2행 추가). 옛 키 손실 0 | 옛·새 코드 모두 저장 → 다시 읽기 `snapshot()` 같음, 두 번째 저장의 파일이 첫 저장과 같음, 쓴 파일의 형식 번호는 5 / 6 |
| 새 코드로 만든 가득 찬 v6(표본 8키, 분석 8개, 모듈 3개·무기 2개 장착) | 새 코드는 같음. **옛 코드가 읽으면** 새 내용(새 표본·분석·모듈·무기 장착)은 걸러지고 옛 세 키와 기존 항목만 남는다 | 옛 코드가 그것을 다시 저장하면 새 내용이 사라진다 — 옛 빌드로 새 저장을 여는 일은 보장 대상이 아니고(정보로만 적는다) 새 코드 쪽 읽기·쓰기는 손실이 없다 |

### 8.5 모듈 전·후 숫자 (실제 시전, 내 quick의 `module_expansion.json`)

시험이 실제 액터로 시전해 잰 값이고, 피해 보너스는 0이며 기준으로 되돌리면 정확히 같다.

| 모듈 | 전 → 후 | 같이 재 본 것 |
|---|---|---|
| FROST LENS | Q 쿨다운 4.0 → **3.2 s**(−20 %) | 피해 26 그대로 |
| RAIL SPOOL | 대시 150 → **200 px**(+50, 상한), E 쿨다운 5.0 → **4.0 s** | |
| SPORE FILTER | ROOK 불워크 5.0 → **6.0 s** | 피해 감소 0.5 그대로 |
| ECHO RELAY | MICA 릴레이 4.0 → **6.0 s**(+2.0, 상한) | 피해 감소 0.2 그대로 |
| NULL ANCHOR | ROOK 산개 5.0 → **6.5 s** | 피해 감소 0.5 그대로 |

정적 검수 때 읽은 값과 같다. 모듈 갈고리를 하나씩 끈 변형 6개가 모두 이 시험에서 빨개졌으므로(8.3) 이 숫자는 갈고리가 실제로 만든 것이다.

### 8.6 풀 스위트 (88개)

실행 `20261006_185434_full`: 18:54 시작, **5,268 s(약 88분)**, 깨끗한 `ccfaa96e`(코드는 `0a14d5b6`과 같고 그 사이에 늘어난 것은 `qa/` 기록뿐), `git_dirty` 0, `qa/` 가드 changed / removed / added = **0 / 0 / 0**. 요약과 표는 `followup/runs/`에 있다(`full_ccfaa96e_summary.json`, `full_ccfaa96e_SUMMARY_KO.md`, 줄 맞춤 `full_vs_quick.txt`, 도구 `followup/tools/compare_full_vs_quick.py`).

**결과: 88개 가운데 87개 PASS, FAIL 1개(`full_op_08`).** 88/88이 아니다.

| 묶음 | 결과 |
|---|---|
| quick 56개 | 56/56 PASS. **검사 수가 내 quick 실행(`0a14d5b6`)과 56개 모두 같다**(다른 것 0, 빠진 것 0) |
| full 전용 32개 | 31 PASS + `full_op_08` FAIL. 항목 3의 넷 `m10_intel` 39 · `m13_loadout` 53 · `campaign` 235 · `lab_capture_geometry` 5는 따로 돌린 값과 같다. 그 밖: `rook_app` 1,895(98 s) · `hazard_expansion` 438 · `contract_ui` 484 · `variety_capture` 96 · `nav_pockets` 죽은 칸 0 · `traversal_audit` 2,394 · `connector_alignment` 1,060 · `battle_geometry` 5,039 · `motion_lab_python` 137 · `motion_lab_js` 30 |
| 봇 10개(러너 초) | 작전 1 136 · 2 125 · 3 142 · 4 166 · 5 158 · **6 182** · 7 226 · **8 FAIL 135** · 9 168 · **10 208**. 작전 6·10은 항목 2 최종 실행에서 두 번씩 졌는데 이번에는 첫 실행에서 이겼다(원인은 재지 않았다) |

**작전 8 봇 — 두 번 돌려 두 번 졌다.** ① 풀 실행: 135.4 s(게임 시간 129.9 s). ② `--only full_op_08` 재실행(`20261006_202305_custom`, 같은 `ccfaa96e`, 144.3 s·게임 시간 138.0 s, 가드 0·0·0). 보고서는 `followup/runs/full_op_08_wipe_run1_report.json`과 `…run2_report.json`. 두 번 모두 5번째 방(`R05_TERMINAL`, 보스방)에서 분대가 전멸했다(`outcome` WIPED, `extraction_depth` 4): 첫 번째는 로봇 19기를 잡고 GANTRY를 1,920 가운데 **1,448**(마지막 기록, 120 s)까지, 두 번째는 20기를 잡고 **632**(130 s)까지 깎았다. 실패한 검사는 두 번 모두 같은 넷이고(`Live combat and extraction succeed without cheats` 외 셋) 전멸의 결과이며 스크립트 오류는 0이다. 전멸 경로도 두 번 실제로 돌았다: `lost_intel_samples` 4, `lost_unsecured` 152, 8키 합에서 오류가 없었다.

**항목 3의 것이 아니라고 보는 이유(코드를 읽은 것이고 잰 것이 아니다).**
1. 봇은 `configure_campaign({}, "…-TECHNICAL-PLAYTHROUGH", {})`로 **빈 캠페인에서 시작**하고 스크립트에 모듈·장착·분석·해금·로드아웃 낱말이 **0개**다. 모듈이 없으니 `has_module`은 전부 거짓이고 쿨다운·지속·거리는 기준값이다. 새 무기 둘도 해금되지 않는다.
2. 항목 3이 이 길에 더한 코드는 처치 때 표본 키를 고르는 `IntelSamples.enemy_key`와, 같은 값을 만드는 VFX 프로필 캐시(T-4)뿐이다.
3. 이 봇의 이전 기록(AGENTS.md "Operation 8 enabled"·"Operation 9 enabled"): 러너에서 9번 가운데 2번 이겼고(2026-09-30 5번 중 2, 2026-10-01 4번 중 0, 같은 보스방 전멸, GANTRY 431–629 남음, 항목 1 이전). 항목 1 이후에도 `4e3ac9e6` 풀 스위트에서 한 번 졌다가 재실행에서 이겼고 `04eba6c3`(항목 2 최종)에서는 통과했다. 이번 0/2는 그 범위 안이다.

**재지 않은 것.** 원인(부하인지, 항목 1의 작전 8 배치인지, 길찾기 수정인지)은 재지 않았다. 옛 코드(`381ef0fb`)와 번갈아 돌리는 A/B도 하지 않았다: 이기는 비율이 낮은 봇은 몇 쌍으로는 두 코드를 구별하지 못한다(이길 확률 0.25인 봇을 양쪽 4번씩 돌리면 양쪽 모두 0승일 확률이 약 10 %). 봇이나 작전 8을 고치는 일, 러너가 전멸을 재시도하게 하는 일은 균형·도구 정책이라 사용자의 몫이고(2026-09-30 결정: 작전 8은 그대로 둔다) 이번에도 아무것도 바꾸지 않았다. 10쌍 A/B가 필요하면 약 1시간이다.

### 8.7 판정

**항목 3은 PASS (기술).** 1차(정적) 검수에서 OPEN이던 칸이 모두 닫혔고 막히는 기준이 없다.

| 1차 때 OPEN이던 것 | 닫은 근거 |
|---|---|
| L-03 · L-14 (내 변형: 모듈·무기) | 8.3: 모듈 갈고리 변형 6개가 각각 `module_expansion` 1/86으로 빨개짐, 무기 변형 4개가 `weapon_expansion` 2–3/131. 8.5: 실제 시전 값 |
| L-08 (내 저장 왕복) | 8.4: v3 · v4 · v5에서 옛 키 손실 0, 왕복과 두 번째 저장이 같다 |
| L-12 (내 변형: 표본 키) | 8.3: 표본 키·흐름 변형 7개가 `intel_supply` 5–21/83으로 빨개짐(그 시험이 혼자 지킨다) |
| L-06 · L-15 | 8.1·8.2: 1080p 네이티브 캡처(결과 화면의 INTEL 줄과 COMMAND 막대가 닿지 않는다)와 `lab_geometry` 4,005검사 |
| L-16 (내 quick 전체, 풀 스위트) | 8.2: quick 56/56, 보조 4개 4/4. 8.6: 풀 스위트 87/88 |

**조건과 한계(숨기지 않는 것).**
1. 풀 스위트는 **87/88**이다. 실패 하나는 작전 8 봇의 보스방 전멸이고 두 번 돌려 두 번 졌다. 항목 3과 무관하다고 보지만(빈 캠페인으로 도는 봇이라 모듈이 꺼져 있다) 원인은 재지 않았다. 88/88이라고 쓰지 않는다.
2. 내가 검사한 코드(`0a14d5b6`, 풀 스위트는 같은 코드의 `ccfaa96e`)는 Codex가 닫은 `98292b3d`와 다르다. 사용자가 허락한 내 손질 5건(T-1·T-2·T-3·T-4·T-8, 8.1) 때문이다: `98292b3d` 대비 `qa/` 밖 코드 변경은 5파일 +50 −9(`operator_actor.gd` 18줄, `mission_results.gd` 3줄, 캡처 23줄, `lab_geometry_smoke` +10줄, `weapon_expansion_smoke` +5줄)이고 게임에 닿는 것은 앞의 둘뿐이다. 규칙·수치·그림·소리 변경 0.
3. 열려 있는 것: T-5 · T-6 · T-7(이때는 손대지 않았다. 9절에서 고쳤다), 작전별 FPS A/B(하지 않았다. T-4는 함수 한 번의 비용만 쟀다), 항목 4 · 5 · 1D의 시작.
4. 이 판정은 기술적 확인이다. **그림·플레이·균형 승인이 아니다.** 모듈 5개 · 무기 2개 · 연구비 900은 사람이 쏴 본 적이 없는 제안값이다. 모듈은 시간형(쿨다운 −20 %, 지속 +1.0–2.0 s, 거리 +50 px)이라 피해를 올리지 않는다. 보상과 위험을 정하는 일은 사용자의 몫이다.

### 8.8 이번에 쓴 것

- 복사본 `proj_i3`(`0a14d5b6`)와 `proj_i3old`(`381ef0fb`)는 풀 스위트가 끝난 뒤 `drop_snapshot.sh`로 지웠다(연결 6개를 먼저 풀고 지운 다음 main 폴더의 항목 수가 그대로인 것을 확인: art_src 4 · assets 11 · motion_lab_v1 48 · sound 2 · third_party 4 · `.godot/imported` 2,941). 초안과 로그는 git에 안 들어가는 `.cache/claude_scratch/item3_review/`에 남아 있다.
- 이 PC의 부하는 시험 결과(특히 봇)를 흔든다(앞선 기록 참고). 이번 실행 동안의 부하는 재지 않았다.
- 그림·플레이·균형 승인이 아니다. 모듈 5개 · 무기 2개 · 연구비 900은 아직 사람이 쏴 본 적이 없는 제안값이다.

## 9. T-5 · T-6 · T-7을 고쳤다 (2026-10-06 밤, Claude)

**판정: 5절에 열려 있던 세 줄(T-5 · T-6 · T-7)을 닫았다. 항목 3의 판정(PASS (기술), 풀 스위트 87/88)은 그대로다.** 사용자가 5절을 읽고 "다듬을 점이 뭐야?" 다음에 "다 고쳐"라고 했고, 설계 선택인 T-6은 "T6도 네가 알아서"라고 맡겼다. Codex는 닫혀 있어 코드는 내가 직접 고쳤다(Codex가 만든 게임 쪽 코드를 내가 고친 세 번째: REDLINE 수치 `4158aaaa`, 손질 5건 `4fd9d502` `0a14d5b6`, 이번). 게임 규칙·수치·그림·소리는 바꾸지 않았다. 화면에 닿는 것은 스테이지 HUD의 INTEL 글 상자(T-5)와 연구소 화면의 글(T-6)뿐이고, T-7은 가져오기 설정 한 줄이다. 고친 코드는 커밋 `92cc7eb3`(T-5) · `4d0ae528`(T-6) · `cfcb065a`(T-7)이고 한 개씩 되돌릴 수 있다. 증거와 도구는 `followup_t567/`.

### 9.1 무엇을 어떻게 바꿨나

| ID | 바꾼 것 | 근거 숫자 |
|---|---|---|
| T-5 | `story_stage_hud.gd`: HUD `_intel_label` 상자를 (616, 82) 640×16에서 **(924, 82) 332×16**으로. 오른쪽 끝은 1256 그대로 | 옛 상자는 교신 상자(`_transmission_panel`, x 360–920, y 70–118)와 x 616–920 구간 304×16 px 겹쳤다. 글자는 오른쪽 정렬이라 화면에서는 닿지 않았다(8개 키가 다 있는 최악의 글 324 px, 시작 x 932). 새 상자는 교신 상자와 4 px 떨어지고 최악의 글 324 px를 8 px 여유로 담고 화면 안이다(Label이 높이를 17로 올려 실제 332×17, 탐침 `ui_probe_out.txt`) |
| T-6 | (a) `IntelSamples.named_counts()`를 더해 로비 `SAMPLES` 줄이 약어(SEC ABR …) 대신 **전체 이름 8개와 숫자**를 보인다. (b) 연구소의 작전자 줄: 해금한 모듈이 하나라도 있으면 둘째 줄 `ModuleChoices_<작전자>`가 **해금한 모듈 이름을 모두** ` / `로 나열하고 장착한 것을 `[ ]`로 묶는다(첫 줄 `ModuleLabel_*`는 그대로 장착한 이름 또는 `NO MODULE`) | (a) 전체 이름 줄은 12 px에서 543 px(11 px 498, 10 px 453), 상자 570×22라서 12 px 그대로 들어간다. (b) 둘째 줄은 10 px에서 169 / 187 / 120 px(세 작전자의 해금 전부, 3 · 3 · 2개), 상자 240 안이다. 잠긴 작전자 줄은 옛 모양 그대로이고 버튼 `ModuleCycle_*`의 자리·크기·동작도 그대로다 |
| T-7 | `sound/music/originals/fps_bgm_06_sniper_ridge.wav.import`를 `importer="keep"` 한 줄 설정으로 | 이 파일은 MP3 데이터에 `.wav` 이름이라 Godot가 가져올 때마다 "Not a WAV file…" 오류 3줄이 났다. `keep`은 Godot가 그 파일을 가져오지 않고 지나가게 한다. 파일의 이름·내용과 `qa/music_integration_20260920/source_retirement.json` 기록은 그대로이고 게임 코드와 `sound/music/catalog.json`은 이 파일을 쓰지 않는다. 이름을 `.mp3`로 바꾸지 않은 이유: 이름을 바꾸면 위 기록과 `34344749`의 설명이 어긋나고 그 파일을 어떻게 할지는 항목 6(음악)의 일이다 |

**T-6은 내가 정한 설계다(사용자 위임).** 5절에서 걸린 것은 "해금했지만 장착하지 않으면 `NO MODULE`이라 무엇이 해금됐는지 한 번 눌러야 안다"와 "`SAMPLES` 줄이 약어로 바뀌었다"였다. 버튼을 늘리거나 패널 크기(1224×202)를 바꾸지 않고 줄 하나를 더하는 쪽을 골랐다. 마음에 안 들면 `4d0ae528` 한 커밋을 되돌린다(시험도 같이 되돌아간다).

**손대지 않은 것.** 같은 HUD 윗줄의 `_cargo_label`(858, 66, 398×17)과 `_optional_label`(858, 98, 398×17) 상자는 교신 상자와 겹치고(x 858–920) 새 `_intel_label` 상자와도 각각 y로 1 px 닿는다(66–83과 82–99, 98–115와 82–99). 모두 항목 3 이전부터 있던 배치이고(5절의 T-5는 `_intel_label`만 가리킨다) 캡처에서 글자는 닿지 않아 건드리지 않았다. `lab_geometry`의 새 검사는 교신 상자와의 겹침과 화면 안만 본다.

### 9.2 확인

| 확인 | 결과 |
|---|---|
| `lab_geometry` | **PASS 5,089검사**(4,005 → +1,084): 새 검사(로비 전체 이름 8개·정확한 줄·12 px, 작전자별 둘째 줄의 존재·이름·`[ ]`, HUD 상자가 교신 상자와 안 겹침·화면 안)와, 새 라벨 3개가 기존 겹침·글꼴 검사에 들어간 것이다. ERROR 0줄 |
| 1080p 네이티브 캡처 | `EXPANSION_ITEM3_CAPTURE: PASS (19 checks)`, 7장 모두 1920×1080 RGBA, 검증기 PASS(`native/validator_report.json`, 화질 주장 아님). 직접 본 것: `lab_page1.png`(`SAMPLES` 줄 전체 이름) · `lab_module_cycle.png`(작전자별 둘째 줄과 `[ ]`) · `field_intel8.png`(HUD INTEL 줄)와 1:1 잘라내기 |
| 규칙 깨기 표 | 변형 9개를 실제 트리에 한 번에 하나씩: **8개 잡힘, 1개는 같은 효과의 변형**(9.3) |
| 가져오기 로그 | 러너의 가져오기 로그(`_import.log`)에서 `keep` 전 58개(2026-09-28–10-06)는 모두 ERROR 3줄 · `Not a WAV` 1줄, `keep` 뒤 2개(`20261006_205946_custom`, `20261006_210230_custom`)는 ERROR 0줄 · `Not a WAV` 0줄(`probes/import_logs_before_after.txt`). 이번 quick은 가져오기를 다시 하지 않았다 |
| T-6을 되돌려도 되는가 | T-5만 있는 트리(옛 로비와 `IntelSamples` + HUD 상자 + 그 검사)에서 `lab_geometry` **PASS 4,007검사**(4,005 + HUD 2): 커밋을 만들 때 이 트리로 먼저 돌렸다. 곧 `4d0ae528`을 되돌린 트리와 같다(`probes/state_a_lab_geometry.json`) |
| quick 전체 | **56/56 PASS**(`20261006_210605_quick`, 531 s, `qa/` 가드 0·0·0). 트리에 있던 것은 검사한 다섯 파일뿐이었고 커밋한 파일과 git blob이 모두 같다(`runs/tested_blobs.txt`). 이전 quick(`0a14d5b6`)과 검사 수가 다른 시험은 `lab_geometry`(4,005 → 5,089) 하나이고 나머지 55개는 상태와 검사 수가 같다(`runs/quick_vs_previous_quick.txt`) |
| 보조 4개 | `m10_intel` 39 · `m13_loadout` 53 · `campaign` 235 · `lab_capture_geometry` 5, **4/4 PASS**(`20261006_211542_custom`, 54 s, 가드 0·0·0). 항목 3의 앞선 값과 같다 |

### 9.3 규칙 깨기 표 (변형 9개, 실제 트리, `lab_geometry` 한 시험으로)

대조군(고친 그대로)은 PASS 5,089검사. 변형마다 `lab_geometry`를 다시 돌리고 "실패한 검사 수 / 전체 검사 수"를 적는다. 트리는 변형마다 백업에서 되돌렸고 끝에서 바이트까지 같음을 확인했다(`RESTORED_BYTES_EQUAL True`).

| 변형 | 결과 | 어떤 검사가 잡았나 |
|---|---|---|
| `hud_box_old_position` (옛 상자 616 / 640) | **잡힘 1/5,089** | HUD 상자가 교신 상자와 안 겹침 |
| `lobby_samples_abbreviations` (약어 줄로 되돌림) | **잡힘 9/5,089** | 로비 전체 이름 8개 + 정확한 줄 |
| `lobby_no_second_line` (둘째 줄 없음) | **잡힘 11/4,020** | 해금한 모듈을 누르지 않고 보인다 |
| `lobby_bracket_first_not_equipped` (첫 모듈에 항상 `[ ]`) | **잡힘 8/5,089** | 장착한 것만 `[ ]` |
| `lobby_never_brackets` (`[ ]` 없음) | **잡힘 16/5,089** | 장착한 것만 `[ ]` |
| `lobby_listing_font_9` (둘째 줄 9 px) | **잡힘 42/5,089** | 최소 글꼴 10 px |
| `lobby_listing_overlaps_first_line` (둘째 줄을 3 px 위로) | **잡힘 42/5,089** | 첫 줄과 안 겹침 |
| `lobby_listing_runs_into_button` (둘째 줄 상자 300 px) | **잡힘 42/5,089** | 버튼 `ModuleCycle_*`와 안 겹침 |
| `hud_box_too_narrow` (HUD 상자 250 px) | 안 잡힘 0/5,089 — **같은 효과의 변형** | Label은 글자 너비(324 px) 밑으로 줄지 않아서 상자는 그대로 324 px이고 교신 상자 오른쪽 · 화면 안이다. 어긋나는 것은 글 끝이 8 px(1256 → 1248) 왼쪽으로 가는 것뿐이라 지킬 규칙이 위반된 것이 아니다 |

### 9.4 아직 열려 있는 것과 사용자의 몫

- 항목 4 · 5 · 1D의 시작, 작전 8 봇의 보스방 전멸(원인 미측정, 2026-09-30 결정은 "그대로 둔다"), 작전별 FPS A/B(하지 않았다)는 그대로다.
- T-6의 새 연구소 줄은 사람이 연구소 화면에서 보고 정할 일이다(내 설계). HUD 상자 변경은 화면에서 달라 보이지 않는다(글자 위치 그대로).
- 이 절은 기술 확인이다. 그림·플레이·균형 승인이 아니다. 모듈 5개 · 무기 2개 · 연구비 900은 사람이 쏴 본 적이 없는 제안값이다.

### 9.5 근거 파일

`followup_t567/README_KO.md`가 목록이다: `runs/`(quick 전체와 보조 4개의 러너 요약, 이전 quick과의 줄 맞춤), `native/`(캡처 보고서와 1080p 검증기 보고, PNG는 git 무시라서 작업 사본에만 있고 SHA-256이 보고서에 있다), `break/`(변형 표와 원자료), `probes/`(연구소 줄의 실제 자리·너비 탐침), `tools/`(변형 적용기, 줄 맞추기, 탐침 스크립트).
