# 항목 2 검수 — 계약 3택 · 브리핑 화면 · REDLINE · 저장 5

검수일 2026-10-04 · 검수자 Claude · 대상 `7b26a152..b4aa2ae0` (구현 `e091e25f`, 기록 `b4aa2ae0`)
근거 지시서 `docs/production/SITE7_EXPANSION_1_3_CODEX_ORDER_KO.md` (기준 K-01…K-14, C-01…C-11. 이 검수의 보완 지시는 그 9.10절)

## 판정: **HOLD** (결함 하나, 고치는 데 한 줄) — 이후 해결되어 최종 **PASS**(기술), 9절과 10절

계약 3택, 브리핑 화면, REDLINE, 저장 5는 지시한 대로 움직인다. 막는 것은 **기존 시험 하나**다. 풀 전용 `campaign`이 첫 검사에서 스크립트 오류로 멈춘다.

- **B-1** 출격 때 스테이지가 받는 계약에서 작전 id 키(`mission_id`)가 사라졌다. `7b26a152`의 `GameFlow.deploy_mission`은 계약을 만든 직후 `last_run_contract["mission_id"] = id`로 그 키를 붙였는데, `e091e25f`가 그 줄을 지웠다("기본값이 `build(run_id)`와 똑같아야 한다"는 K-01을 글자 그대로 맞춘 결과, Codex README 1절). 그 키를 읽는 곳은 게임 코드에 없고 **풀 전용 시험 하나**(`site7_campaign_progression_smoke.gd:60`)뿐이다. 그 시험은 quick에 없어서 Codex의 quick 52/52에는 보이지 않았고 내가 돌려서 나왔다. 한 줄을 되돌린 사본에서 `campaign`은 235검사 통과로 돌아온다.

이 판정은 게임이 틀리게 도는 이야기가 아니라 **하나의 키와 그 키를 못 박은 시험** 이야기다. 나머지 기준은 2절의 숫자대로 충족이다. 확인할 수 없어 남긴 것은 풀 스위트 한 가지다(고친 뒤에 돌린다, 7절).

이 기록은 그림·플레이·균형 승인이 아니다.

## 1. 한눈에

| 항목 | 결과 |
|---|---|
| 범위 (`7b26a152..b4aa2ae0`) | 커밋 2개(`e091e25f` 24파일 +3,789 −12, `b4aa2ae0` QA 기록). `assets` `art_src` `motion_lab_v1` `data` 변경 0 (`dca7ef20..HEAD`의 `data/visual`도 0). 승인 그림 17 of 17 unchanged |
| quick 전체(`b4aa2ae0`) | **52/52 PASS**, 579 s, `qa/` 가드 clean (`qa/regression_runs/20261004_172313_quick/`). Codex의 실행도 52/52, 567 s |
| 풀 전용 `campaign` | **SCRIPT_ERROR** (9.6 s): `Invalid access to property or key 'mission_id' on a base object of type 'Dictionary'` (`20261004_173328_custom`) → B-1 |
| 한 줄 되돌린 사본 | `campaign` **235검사 PASS**. 같은 사본에서 `contract_ui`의 세 검사만 실패(모두 "키가 하나도 더해지지 않았다" 비교) |
| 표적 풀 전용 | 배포·브리핑·장비 흐름을 건드리는 나머지 풀 전용 셋: `demo_integration` 26 · `m10_intel` 39 · `m13_loadout` 46 **PASS** (`20261004_182829_custom`). 러너 밖의 `m8_extraction_progression_smoke`는 HEAD와 같은 결과(46줄 PASS, 둘이 이미 실패 — 항목 2와 무관) |
| `build()` 불변 (K-01) | run id 472개를 `7b26a152` 압축본과 `e091e25f`에서 각각 뽑아 비교: **같은 JSON 472 / 다른 것 0** (두 덤프 파일이 바이트까지 같다) |
| 제안 구조 (K-02·03) | run id 364개 × 작전 10개 = 3,640칸: 3개가 아닌 칸 0, 첫 제안이 `build`와 다른 칸 0, 쌍이 구별되지 않는 칸 0, 클램프 밖 0, 위험이 높은데 보상이 낮은 쌍 0. 두 프로세스 비교 완전 일치. 위험 카드 4종의 배율이 제안 전체(10,920개)에서 `build()`의 카드와 같다 |
| 실제 흐름 (K-04·05·08) | 진짜 `GameFlow`로 작전 10개 전부: **1,473검사 · 실패 0** (브리핑 지오메트리, 고른 계약 = 스테이지가 받은 계약, 로봇 HP/피해/속도/간격, 추출 보상, 잘못된 인덱스 5가지는 기본값) |
| 보스 시험 숫자 (C-11) | `boss_registry` 163 · `boss_pattern` 978 · `boss_duel` 2,184 (표준 1,124가 그대로 + REDLINE 1,060) · `boss_room_fairness` 21 · `robot_roster` 302 |
| 저장 (K-11) | 실제/손으로 만든 저장 5개: 새 코드와 옛 코드가 공통 키를 전부 같게 읽고, 쓴 뒤 다시 읽어도 같다. 새 저장을 옛 코드가 읽어도 문제 없음 |
| 캡처 4장 (C-08) | 검증기 재실행 PASS, 4/4 1920×1080. 4장 모두 직접 봤다(겹침·잘림 없음, 글 nit는 4절) |
| 플레이어 저장 (C-10) | `campaign_progression_v1.json` SHA-256 `5c600d90…2426ea` 그대로, `settings.cfg` 없음 그대로 |
| 규칙 깨기 | 변형 46개 중 **40개 잡힘**(실행 302번). 놓친 6개: 하나는 무해, 다섯은 시험 빈틈이고 코드는 맞다(4절 N-B, 6절) |
| 봇 세 갈래(작전 1) | 중립 계약 3판 중 **3** 추출 · 실제 run id의 기본 제안 3판 중 **3** 추출 · REDLINE 3판 중 **0** 추출 (5.3절) |

## 2. 기준 ID별 판정

`PASS`/`HOLD`와 측정값. "Codex 시험"은 Codex가 쓴 시험이 통과한다는 뜻이고, "내 측정"은 내가 따로 잰 것이다. 내 변형(규칙을 일부러 깬 사본) 전체 표는 6절과 `evidence/raw/mutations_ic.md`.

### 공통 (C-01 … C-11)

| ID | 판정 | 근거 |
|---|---|---|
| C-01 | PASS | `git log 7b26a152..HEAD`: Codex 커밋 둘. `e091e25f` 24파일(게임 코드 8 · 시험 12 · 고정물 3 · 러너 1), `b4aa2ae0`는 `qa/expansion_item2_20261004/` 안의 기록뿐. 모두 로컬, push·PR·Pages·Actions 없음. 작업 트리 clean. C: 드라이브 기록 없음(작업 파일은 git-ignored `.cache/`) |
| C-02 | PASS | `git diff --stat 7b26a152..b4aa2ae0 -- assets art_src motion_lab_v1 data` 비어 있음. `verify_hashes.py` → 17 of 17 approved files unchanged |
| C-03 | PASS | quick의 `world_layout`, `mood_light`가 내 실행에서도 PASS. `data/visual` 변경 0 |
| C-04 | PASS | 한계·상수 변경 0. `site7_boss_*_smoke.gd`의 유일한 변경은 `boss_duel`의 REDLINE 추가분(상수 변경 0, `SIGNATURES` 불변). `upgrade_economy_smoke.gd`, `upgrades.json`, `site7_enemy_tactics.gd`, `enemy_profiles.json` 변경 0. 클램프(1–2 / 0.5–3 / 0.5–3 / 0.5–2 / 0.5–4)와 ×2 상한 변경 0 |
| C-05 | PASS | 기존 시험 세 개의 diff를 읽었다. 지워진 `_check` 0. `play_session_log_smoke`는 중립 호출을 제안 2번 호출로 바꾸고 검사 2개를 더했고(23 → 25), `site7_boss_duel_smoke`는 REDLINE 판을 더했으며(1,124 → 2,184) 표준 검사는 그대로다. 러너는 5줄 추가뿐 |
| C-06 | PASS | `--list`: 52 quick + 31 full = 83 (78 + 새 시험 4 + 기존 `m11`). 새 시험이 모두 quick으로 등록됐고 파일을 쓰는 셋은 `--out`을 받는다(`contract_ui` dir, `redline` `redline.json`, `contract_save` `save.json`). 두 번째 러너 없음. 내 quick의 `qa/` 가드 clean |
| C-07 | PASS | 새 도형·입자·로봇 틴트 없음(화면 글자와 상자뿐). 계약 효과는 숫자뿐이라 FPS를 주장하지 않았고 나도 재지 않았다 |
| C-08 | PASS | `validate_visual_evidence_1080p.py --require-dynamic-capture` 직접 재실행: container PASS, dynamic PASS, 4/4 디코드, 1920×1080. 이 PASS는 크기와 디코드뿐이다 |
| C-09 | PASS | README가 6절 항목을 채운다: 커밋, 시험, 상수 표, 캡처 SHA, 한계, 사용자 결정 수치, "승인이 아니다" 문장. 봇은 표본 1회씩이라고 적었고 full은 돌리지 않았다고 솔직히 적었다 |
| C-10 | PASS | 새 시험이 쓰는 저장은 `res://.cache/…`의 프로젝트 안 경로뿐. 플레이어 저장·설정 SHA·시각 전후 같음(Codex 기록과 내 확인). 참고: 플레이어 `user://.cache/diag/expansion_item2_20261004/counter_double`에 **빈 폴더 3개**가 있다(파일 0, 4 KB, 16:13 — Codex의 진단 실행 흔적이고 저장·설정이 아니다). 지우지 않았다 |
| C-11 | PASS | 위 1절의 숫자. `boss_duel`의 증가분은 전부 REDLINE 판이고 표준 1,124검사는 그대로 있다 |

### 항목 2 (K-01 … K-14)

| ID | 판정 | 근거 |
|---|---|---|
| K-01 | PASS (`build`·골든) · **B-1** | `RunContract.build`의 본문은 `7b26a152`와 바이트가 같다. 내가 `7b26a152` 압축본과 `e091e25f`에서 run id 472개를 각각 뽑아 비교: 472 = 472. Codex의 골든 표(64개 × 작전 10개)는 수정 전 HEAD 실행으로 만들었다. 기본 출격이 받는 계약은 `build(run_id)`와 딕셔너리째 같다. **다만 HEAD가 스테이지에 주던 계약에는 `mission_id`가 하나 더 있었고 그 키를 읽는 시험이 있다 → B-1** |
| K-02 | PASS | 내 측정: 3,640칸에서 제안은 항상 3개, 서로 다른 (위험, 기회) 쌍 3개, 첫째 = `build(run id)`, 같은 id·작전이면 늘 같은 3개(두 프로세스 완전 일치), 클램프 안, 대안의 배율은 그 위험 카드의 배율. Codex 시험 26,950검사. 내 변형은 6절 |
| K-03 | PASS | 위험이 더 높은 제안의 자원 3종 보상이 낮은 쌍 0. **관찰:** 3,640칸 전부에서 세 제안의 기회 카드가 같다. 제안은 위험 카드만 바꾼다. 연구 보상 차이는 0.032–0.065(평균 0.049)로 작다 — 5.2절 |
| K-04 | PASS | 작전 10개 모두 브리핑에서 3택(클리어한 작전은 4택)이 보이고, 마우스와 Enter로 고르고, 사각형은 경로 패널·통신/계약 패널·세 버튼과 겹치지 않고 1280×720 안, 글자는 잘리지 않는다(내 흐름 감사 1,473검사 + Codex 484검사). 아무것도 안 고르면 기본값(index 0)으로 출격. 한계: 내 감사가 본 선택지 70개는 기회 카드가 늘 SALVAGE PRIORITY 하나였다(같은 run id 규칙). 나머지 기회 카드 셋은 계산으로만 확인했다: 가장 긴 제목줄은 50자(본 것 48자), 가장 넓은 줄이 362 px이고 선택지 안쪽은 686 px라 들어간다 |
| K-05 | PASS | 내 흐름 감사: 고른 계약 = 스테이지가 받은 계약(작전 10개 × 선택지 전부), 첫 전투 방과 보스방의 로봇 HP·피해·속도·간격이 계약대로, 추출 보상 배율이 계약대로. Codex `redline_smoke`: 실제 스테이지에서 HP 한 번만 곱함, 투사체 피해 한 번 |
| K-06 | PASS | `results_redline.png`: "CONTRACT REDLINE // MAXIMUM RECOVERY", "REWARDS RESEARCH ×2.40 / SALVAGE ×2.40 / SIGNAL ×2.40"이 보인다. `contract_ui`가 이 문구와 사각형을 검사한다(결과 화면 변형 `results_neutral` 잡힘) |
| K-07 | PASS | `CampaignProgression.snapshot()`에 `run_contract`, `active_run_boosts` 없음(`m11` 34검사 유지, 내 `save_probe`로 새 저장에도 없음, 변형 `contract_persisted` 잡힘). 새 배포는 중립에서 시작 |
| K-08 | PASS | REDLINE 선택지는 클리어한 작전에만 나타난다(내 흐름 감사: 클리어 전 3택, 클리어 후 4택, 클리어 전에 인덱스 3을 넘기면 기본값). 전멸·조기 탈출·미리보기·잠긴 결과·중복·클리어 전 위조는 `redline_cleared`를 바꾸지 않는다(Codex `redline_smoke`의 실패 6가지 + 유효 1가지, 변형 `redline_on_wipe`·`redline_on_early`·`commit_gate_off` 잡힘). 일반 해금·클리어 규칙은 불변 |
| K-09 | PASS (수치는 사용자 몫) | REDLINE 값: HP ×1.50, 피해 ×1.35, 속도 ×1.15, 간격 ×0.80, 위험 보상 ×1.60 × 기회 ×1.50 = ×2.40. **모두 제안 범위의 끝값**이고(5.1절) 모든 제안보다 높다. 보스는 HP·피해만 받고 이동·간격 ×1.0. `boss_duel`을 REDLINE으로 한 번 더 돌린 결과(내 quick에서 2,184검사 PASS): 경고 모양·와인드업이 표준과 같다(1.1 s, ANCHOR 0.95 s). 보스 면제 변형 4개가 모두 잡힌다. 보스 경고 피해만 20 → 27이 된다(5.1절) |
| K-10 | PASS | `redline_cleared` 저장(schema 5), 읽을 때 정제(모르는 id·클리어하지 않은 id·중복 버림 — `contract_save` 69검사, 내 저장 5개, 변형 `sanitize_off` 잡힘). `lobby_redline_cleared.png`: 작전 목록에 "01 BLACKOUT AT SITE-7 / REDLINE CLEARED"와 "REDLINE CLEARED // REPLAY AVAILABLE" |
| K-11 | PASS | 저장 5개(`evidence/raw/save_matrix.md`): v3(플레이어 저장 사본)·v4(옛 코드가 만듦)·Codex 고정물 v3·v4·새 v5. 새 코드가 읽은 공통 키 = 옛 코드가 읽은 값, `redline_cleared`는 옛 4개에서 `[]`, 새 저장에서 `["MIS_CH01_01"]`, 쓰고 다시 읽어도 같다. 새 저장을 옛 코드가 읽어도 문제 없다. 모르는 미래 필드는 버려진다 |
| K-12 | PASS | `play_log` 25검사(23 → 25): 고른 대안의 `contract_id`, 평시 `redline: false`, 중단된 REDLINE 기록도 `REDLINE/REDLINE_RECOVERY`와 `redline: true`. 변형 `playlog_no_id`·`playlog_no_redline` 잡힘 |
| K-13 | **HOLD (확인 대기)** | `--list`로 `run_contract`와 새 시험 4개가 quick임을 확인. `full_op_01`–`10`은 자기 호출에서 중립 계약(`configure_campaign({}, id, {})`)을 쓰므로 브리핑·`offers`와 무관해 보이나, **풀 스위트를 이 팁에서 돌리지 않았다**(B-1이 고쳐지면 팁이 바뀐다). 고친 뒤 돌린다 |
| K-14 | PASS | `redline` 77검사: 실제 스테이지 1·4단계에서 HP 한 번, 보스·지원 로봇 HP, 투사체 피해 한 번, 보상 336/24/24, 과대 입력 99가 400/40/40과 3/3/2/2로 잘림. 대조군: Codex의 `_spawn_wave` 한 줄을 두 번 호출한 사본이 77검사 중 7개에서 실패. 내 변형 `double_apply`도 같은 7개(`redline`)와 `m11` 1개가 실패 |

## 3. B-1 — 스테이지가 받는 계약에서 `mission_id`가 사라져 `campaign`이 멈춘다

**증상.** `python tools/maintenance/run_regression_suite.py --only campaign` → `SCRIPT_ERROR`, 9.6 s. `site7_campaign_progression_smoke.gd:60`의 `check(stage._run_contract.mission_id==id, "Run contract scoped %d")`가 키가 없는 딕셔너리를 읽는다. `4e3ac9e6`의 풀 실행(`20261003_170533_full`, 74/78)에서 `campaign`은 통과였다.

**원인.** `7b26a152`의 `GameFlow.deploy_mission`:

```
last_run_contract = RunContract.build(run_id)
last_run_contract["mission_id"] = id
```

`e091e25f`는 둘째 줄을 지우고, 계약 3택에서 고른 사전을 그대로 스테이지에 넘긴다. README 1절은 이를 "기존 GameFlow의 부가 mission_id 키는 계약에서 제외"라고 적었다. 게임 코드에서 이 키를 읽는 곳은 없다(`scripts/`와 `tests/`에서 계약 사전의 `mission_id`를 읽는 줄은 위 `campaign` 한 줄뿐). 그러므로 게임이 틀리게 도는 것이 아니라 **기존 시험이 못박은 동작이 조용히 바뀐 것**이다.

**왜 이제야 나왔나.** 9.9의 내 메시지는 quick 전체를 요구했고 Codex는 52/52를 만들었다. `campaign`은 풀 전용이다(공용 함수의 모양을 바꾸면 이름이 안 나온 시험이 깨진다 — N-1과 같은 종류). 풀은 내 몫이었고 내 실행에서 나왔다.

**고치는 법 (권장 A).** 선택을 마친 뒤 `last_run_contract["mission_id"] = id` 한 줄을 HEAD처럼 되돌린다. 그러면 기본 출격의 계약 = `build(run_id)` + `mission_id` 하나, 곧 HEAD가 스테이지에 주던 것과 같다. 골든 표와 `offers`는 `build`/제안 사전을 비교하므로 영향이 없다. 되돌린 사본에서 `contract_ui`의 세 검사만 실패한다(모두 "정확히 같다 / 키 추가 없음" 비교):

- `untouched/default briefing deploy exactly equals HEAD contract (no added keys)` (`run_contract_ui_smoke.gd:40`)
- `alternative survives actual GameFlow deploy`
- `REDLINE flows to actual stage`

세 검사는 `mission_id` 하나만 제외하고 비교하도록 고친다(첫째는 `build(run_id)` + `{"mission_id": id}`와 딕셔너리째 같다는 엄격함을 그대로 둔다). 대안 B는 `campaign`의 60행을 `stage.mission_id == id`로 바꾸는 것인데, 계약의 범위를 보던 검사를 다른 것으로 바꾸므로(C-05) 권하지 않는다.

**내가 확인한 것.** 한 줄을 되돌린 사본(`proj_ic`)에서 `campaign` 235검사 PASS(28 s), `offers` 26,950 · `redline` 77 · `save` 69 · `m11` · `play_log` 25 PASS, `contract_ui`만 위 3검사 실패.

## 4. 막지 않는 덧붙임

- **N-A (권장)** `tools/validate_m11_run_contract.py`가 `7b26a152`에서 PASS였고 이 팁에서 FAIL이다: `campaign_progression.gd`에 `run_contract`라는 글자가 있으면 "run-only M11 state leaked"로 본다. 새 코드의 72줄과 95줄이 추출 요약의 `"run_contract"`를 *읽을* 뿐 저장하지는 않는다(`snapshot()`에 없음, K-07). 러너에 없는 옛 검증기(`.github/workflows/validate.yml`이 부르고, 사용자 규칙으로 GitHub 작업은 안 한다)라 막지 않는다. 같은 폴더의 M12·M13 검증기는 `7b26a152`에서도 이미 실패다(별개). 검증기를 "저장되는 곳에 `run_contract`가 없다"로 좁히거나 요약 키를 읽는 줄을 허용하게 한다.
- **N-B 시험 빈틈 (권장, 같은 커밋에 한 줄씩)** 내 변형 46개 중 못 잡힌 6개. 모두 코드는 지금 맞고(내 측정) 시험이 못 본다:
  - **N-B1** 대안의 적 배율이 제 위험 카드의 배율이다 — `offers_no_hazard_stats`(대안이 기본값의 배율을 그대로 가져도 통과). 내 측정: 위험 카드 4종의 (체력, 피해, 속도, 간격)이 제안 10,920개 전부에서 `build()`의 카드와 같고, (위험, 기회) 쌍 16가지의 보상 3종도 `build()`와 같다. 한 줄: 제안 각각의 배율 네 개가 같은 `hazard_id`의 `build()` 카드(골든)와 같다.
  - **N-B2** `deploy_mission(클리어 전 작전, 3)`은 기본 계약이다 — `deploy_redline_unvalidated`(검증을 빼도 통과). 브리핑은 클리어 전에 인덱스 3을 내놓지 않고 `commit_mission`이 클리어 전 REDLINE 요약을 거부하므로(`redline_smoke`) 실제 길은 막혀 있다. 내 흐름 감사의 잘못된 인덱스 5가지(3, 4, 9, −1, 100)는 모두 기본값으로 갔다.
  - **N-B3** 브리핑 선택지 글이 효과 문구를 담는다, 기본 선택지가 눌린 상태다 — `ui_no_effect_text`, `ui_default_unpressed`. 캡처에서는 둘 다 보인다(효과 문구 줄, 하이라이트된 기본 선택지).
  - **N-B4** `debug_reset`이 `redline_cleared`도 비운다 — `debug_reset_keeps`(디버그 전용 함수). 그리고 `contract_save`는 스냅샷에 `redline_cleared` 키가 없으면 검사 하나를 실패시키는 대신 스크립트 오류로 멈춰 **끝나지 않는다**(변형 `snapshot_no_redline`: 러너의 120 s 제한까지 매달린다. 러너는 TIMEOUT으로 빨갛게 표시하므로 잡히긴 한다). `.get("redline_cleared", …)`로 읽으면 깨끗이 실패한다.
  - 못 잡힌 여섯째 `ui_choice_short`(선택지 상자 높이 72 → 40)는 **무해**하다: 상자가 최소 높이(65 px)로 늘어나 글이 그대로 들어간다(내 흐름 감사도 같은 결과, 상자 3개 모두 65 px).
- **N-C 글** 브리핑 아래쪽 안내문 "REDLINE keeps boss movement and warning timing."이 REDLINE을 고를 수 없는 작전(클리어 전)에서도 보인다. 처음 하는 사람에게 안 보이는 선택지를 설명하는 셈이다. "ATTACK GAP −10%"는 간격 배율 0.90의 표시라서 −가 맞지만 처음 보면 헷갈릴 수 있다. 결과 화면은 손실 두 항목을 한 줄에 모았다(정보 삭제는 없음).
- **N-D 입력** 브리핑 대화가 끝나면 계약 패널이 뜨고 포커스가 출격 버튼에 있어서 Enter를 계속 누르면 선택 없이 기본값으로 출격한다. 지시서 K-04가 요구한 동작이다(아무것도 안 고르면 기본값). 기록만 한다.
- **N-E 정리** Codex는 옛 작업 사본 15개(23.7 MB)의 삭제가 정책 검토에서 거절되어 그대로 두고 경로와 SHA를 `records/cleanup_20261004.json`에 남겼다. 정당한 처리이고 나도 지우지 않았다. 지울지는 사용자가 정한다(`.cache/diag/expansion_item2_20261004/` 아래).

## 5. 사용자에게 가는 숫자 (판정이 아니다)

기술 검수가 통과해도 사람 플레이가 없으면 난이도와 균형은 확정이 아니다. 이 PC에는 기록된 사람 플레이가 없다(`playtest_logs/` 비어 있음).

### 5.1 REDLINE은 얼마나 센가 (표준에서 가장 센 위험 카드와 비교)

| 값 | 표준에서 가장 센 것 | REDLINE | 지시서 제안 범위 |
|---|---|---|---|
| 적 체력 | +25 % | **+50 %** | ≤ +50 % (끝값) |
| 적 피해 | +20 % | **+35 %** | ≤ +35 % (끝값) |
| 적 속도 | +10 % | **+15 %** | ≤ +15 % (끝값) |
| 공격 간격 | −12 % | **−20 %** | ≥ 0.80 (끝값) |
| 연구 보상 | ×1.586 | **×2.40** | 위험 보상 ≤ 1.6, 기회 보상은 별도 |
| 분석(salvage)·신호 조각 보상 | ×1.83 | **×2.40** | 같음 |

- 모든 값이 제안 범위의 **끝**에 있다. 값을 한 칸씩 줄이는 것은 `REDLINE_*` 상수 여섯 개를 바꾸면 된다.
- 내 추정(봇 아님): 적을 쓰러뜨리는 데 걸리는 시간이 ×1.5, 한 방이 ×1.35, 공격 빈도는 최대 ×1.25(와인드업은 안 줄어듦) → 받는 피해가 표준의 대략 2배에서 2.5배. 이 계산은 가정이고 사람 플레이로 확인해야 한다.
- 보스는 HP ×1.5, 피해 ×1.35만 받는다. 그 결과 **보스 경고 한 방이 20 → 27**이다. 표준에서 가장 센 위험 카드는 24(20 × 1.20)다. 연산자 체력은 ASTER 96, MICA 112, ROOK 138이라 ASTER에게 27은 28 %다. 경고 모양·시간은 표준과 같다(공정성 시험은 표준 계약 기준으로 통과하고 한계는 낮추지 않았다).
- 보상: 연구소가 6단계(+72 %)일 때 연구 보상은 REDLINE ×4.13, 표준 최대 ×2.73이다(분석·신호 조각: 2.40 대 1.83). 업그레이드 소모처의 합(연구 5,180 · 분석 36 · 신호 18, `upgrade_economy`)이 REDLINE 반복으로 더 빨리 찬다. 값은 제안이고 사용자 결정이다.

### 5.2 3택은 얼마나 다른가

세 제안은 위험 카드만 다르고 기회 카드는 같다(3,640칸 전부). 한 칸에 들어가는 위험 카드 조합은 4가지 중 하나이고 고르게 나온다(869–955칸). 연구 보상 차이는 3–6.5 %뿐이다 — 보상은 거의 같고 적 구성만 다르다. 그대로 두는 것도, 기회 카드까지 바꿔 보상 차이를 키우는 것도 사용자 결정이다.

### 5.3 봇이 말하는 것

작전 1에서 같은 사본(`b4aa2ae0`)으로 세 갈래를 라운드마다 순서를 돌려 가며 한 번에 하나씩, 3라운드 9판 돌렸다. 갈래는 (1) 러너의 `full_op_01`과 같은 중립 계약, (2) 실제 run id로 만든 기본 제안(`build`), (3) REDLINE이다.

- **중립 계약**: 3판 중 3판 추출 (걸린 시간 136 / 123 / 122 s, 받은 피해 416 / 287 / 352 HP)
- **실제 run id의 기본 제안**: 3판 중 3판 추출 (걸린 시간 129 / 118 / 127 s, 받은 피해 403 / 390 / 360 HP)
- **REDLINE**: 3판 중 0판 추출; 라운드 0 전멸(118 s, 처치 16, 보스방, 보스 남은 체력 296 / 930); 라운드 1 전멸(112 s, 처치 14, 보스방, 보스 남은 체력 628 / 930); 라운드 2 전멸(108 s, 처치 14, 보스방, 보스 남은 체력 703 / 930)

읽는 법: 이것은 사람이 아니라 한 종류의 봇이고(저장된 업그레이드나 무기 선택을 쓰지 않는 기본 장비의 봇), 이 PC의 부하가 봇의 결과를 흔든다(작전 3·7·8·10의 기록이 그렇다). 갈래당 판 수가 적어 "얼마나 더 센가"를 숫자로 말하지 않는다. 이 봇이 추출한 판은 REDLINE에서 3판 중 0판, 중립·기본 제안에서 6판 중 6판이다. Codex의 REDLINE 봇도 작전 1·10에서 보스방 전멸(표본 각 1회)이었다. 클리어한 뒤에 다시 도는 플레이어는 업그레이드와 장비가 이 봇보다 강할 수 있으므로 이 숫자를 곧바로 사람의 난이도로 읽으면 안 된다. REDLINE 값을 내릴지는 사람 플레이를 본 뒤 사용자가 정한다.

판마다의 표는 `evidence/raw/bots_arms.md`, 판마다의 원자료(방별·원천별 피해, 틱별 체력 추적)는 `evidence/raw/bot_runs/`.

## 6. 규칙 깨기 — 규칙을 일부러 깬 사본에서 시험이 실패하는가

사본(`proj_ic` = `b4aa2ae0`)에서 코드 한 곳씩 깬 변형 46개를 시험 6–8개에 돌렸다(실행 302번, 1시간 남짓). 한 변형이 어느 시험에서든 빨갛게 되면 "잡힘"이다. `HANG`은 스크립트 오류 뒤 종료하지 못해 제한 시간에서 중단한 것(러너는 TIMEOUT으로 빨갛게 표시).

| 규칙 묶음 | 변형 | 잡힘 | 놓침 |
|---|---:|---:|---|
| 제안 3택 (결정성·순서·쌍·보상) | 5 | 4 | `offers_no_hazard_stats` |
| REDLINE 수치(제안 범위 안) | 6 | 6 | |
| REDLINE 해금 | 2 | 2 | |
| 보스 면제 | 4 | 4 | |
| 실제 적용(두 번 곱·ids·보상·클램프) | 4 | 4 | |
| 출격 흐름 | 4 | 3 | `deploy_redline_unvalidated` |
| 저장·정제·기록 | 8 | 7 | `debug_reset_keeps` |
| 플레이 기록·결과·로비 | 5 | 5 | |
| 브리핑 화면 | 8 | 5 | `ui_choice_short`(무해), `ui_default_unpressed`, `ui_no_effect_text` |
| **합계** | **46** | **40** | **6** |

수정 사본(`mission_id_restored`, 변형이 아님)은 B-1의 확인이다: `campaign` PASS, `contract_ui` 3개만 실패.

전체 표(변형 × 시험, 실패한 검사 수 / 전체 검사 수)는 `evidence/raw/mutations_ic.md`.

## 7. 내가 하지 않은 것

- 풀 스위트(약 90분)는 이 팁에서 돌리지 않았다. B-1의 수정이 팁을 바꾸므로 고친 뒤에 돌린다. `full_op_03/07/08/10`의 단독 WIPED는 알려진 소음이라 `--only`로 다시 돌린다.
- FPS는 재지 않았다. 계약 화면과 한 번의 곱셈뿐이다.
- 사람 플레이, 화면 취향, REDLINE 배율과 보상은 사용자 몫이다.
- Codex가 보존한 15개 파일은 지우지 않았다.
- 항목 3은 이 판정과 무관하게 시작하지 않았다.

## 8. 증거와 재현

`evidence/README_KO.md`와 `evidence/MANIFEST.json`(SHA-256). 도구는 `evidence/tools/`, 원출력은 `evidence/raw/`.

## 9. 후속 (2026-10-04, 이 판정 이후)

- **B-1은 Codex가 `125be138`로 고쳤다.** 그 트리에서 `campaign` 235검사와 `contract_ui` 484검사가 PASS이고 K-01은 PASS다. K-13(풀 스위트)은 Godot가 빌 때까지 열려 있다.
- **5절의 숫자는 사용자가 나에게 맡겼고("네가 알아서 해줘") 상수를 직접 고치라고 했다("수정부터 해").** 결정과 이유는 주문서 9.11절, 근거 파일은 `redline_numbers/`다: REDLINE 체력 1.50 → 1.35, 피해 1.35 → 1.25, 속도 1.15 → 1.12, 간격 0.80 → 0.85, 보상 ×2.40과 3택은 그대로(커밋 `4158aaaa`).
- **5.3절의 봇 "REDLINE 0/3"은 정정한다.** 같은 값을 이번 세션에서는 업그레이드 없는 봇이 2판 모두 추출했다(합쳐서 5판 중 2판). 그 0/3은 REDLINE이 너무 세다는 증거가 아니었고, 이 봇의 추출 개수는 설정의 세기를 가르는 눈금이 아니다(`redline_numbers/README_KO.md`). 5.1절의 REDLINE 숫자(+50 % 등)는 `e091e25f` 시점의 값이다.

## 10. K-13 풀 스위트와 최종 판정 (2026-10-05)

**항목 2는 PASS (기술).** `04eba6c3`에서 풀 스위트 83개 가운데 **81개가 PASS, 2개가 FAIL**이고, 실패 둘은 작전 6과 작전 10의 봇 플레이스루가 보스방에서 전멸한 것이다. 열 개 플레이스루는 모두 빈 계약으로 돌았고 항목 2는 이 봇의 전투 경로에 닿지 않는다. 그래서 K-13은 충족이다. 한 번에 끝까지 간 실행이 아니라 세 번을 합친 것이다(1차는 사용자가 다른 세션의 Godot를 위해 멈추라고 해서 53개에서 끊겼다). 밀려 있던 Godot 시험 7개와 `campaign`·`contract_ui`는 모두 PASS다.

세부: 주문서 9.12절. 증거와 재현: `full_suite_final/README_KO.md`, 83줄 표 `full_suite_final/results_83.md`, 전멸 네 판 `full_suite_final/wiped_runs.md`, 파일마다 SHA-256 `full_suite_final/MANIFEST.json`.

두 봇이 지는 원인(길찾기 수정, 항목 1의 배치, 부하)은 재지 않았다. 균형·도구 정책은 사용자의 몫이다. 사람 플레이와 그림 승인은 없다.
