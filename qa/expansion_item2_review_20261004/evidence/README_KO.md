# 증거 목록 (항목 2 검수, 2026-10-04)

`../REVIEW_KO.md`의 숫자가 나온 파일이다. 검수 대상은 `7b26a152..b4aa2ae0`(구현 `e091e25f`, 기록 `b4aa2ae0`)이고 비교 기준선은 `7b26a152`(항목 2 이전 코드, 압축본)다.
사본은 `git archive`로 만든 `.cache/claude_scratch/proj_head`(= `7b26a152`)와 `proj_ic`(= `b4aa2ae0`)이고, 만들 때 `tools/make_snapshot.sh`, 지울 때 `tools/drop_snapshot.sh`를 썼다.
저장소 작업 트리는 이 검수에서 바뀌지 않았다. 도구의 원본은 `.cache/claude_scratch/item2_review/`와 `item1_review/`(git 제외)에 있고, 경로는 거기에 맞춰져 있으므로 이 폴더의 `tools/`는 기록용 사본이다.

## 어느 측정이 어느 파일에서 나왔나

| 측정 (REVIEW 절) | 도구(`tools/`) | 결과(`raw/`) |
|---|---|---|
| quick 전체 52/52 (1절) | 저장소의 `tools/maintenance/run_regression_suite.py` (`b4aa2ae0` 작업 트리) | `quick_mine.log`, `runs/quick_b4aa2ae0_*` |
| B-1: `campaign`이 스크립트 오류 (3절) | 같은 러너 `--only campaign` | `only_campaign.log`, `runs/campaign_b4aa2ae0_*` |
| B-1: 한 줄 되돌린 사본에서 `campaign` PASS, `contract_ui` 3개만 실패 (3절) | `mutate_ic.py`(수정 사본 `mission_id_restored`), `ic_matrix.sh` | `ic_base_fix.log`, `cases/mission_id_restored__*.log`, `ic_matrix.jsonl` |
| 표적 풀 전용 시험 (1절) | 러너 `--only demo_integration,m10_intel,m13_loadout` + `-s` 직접 | `targeted_full_only.md`, `targeted_full_only.log`, `m8_proj_head.log`, `m8_proj_ic.log`, `runs/20261004_182829_custom_*` |
| K-01: `build()` 472개 불변 | `golden_dump.gd`(두 사본에서 각각), `analyze_offers.py` | `build_472_ids_7b26a152.json`(SHA-256 `1e74955a3d9aae76621c065b54a6aca1138f745d89a661787322f76e923bfa98`; `b4aa2ae0`에서 뽑은 덤프는 바이트까지 같아 해시만 MANIFEST에), `offers_analysis.md` |
| K-02·03: 제안 구조, 3,640칸, 두 프로세스 결정성, 보상 쌍 | `offers_dump.gd`(두 번), `analyze_offers.py` | `offers_analysis.md` (10 MB 덤프 둘은 해시만 MANIFEST에) |
| K-04·05·08: 실제 `GameFlow`로 작전 10개, 1,473검사 | `flow_audit.gd` | `flow_audit_headless.json`, `flow_audit_headless.log`, `flow_audit_choice_short.{json,log}`(상자 높이 변형) |
| K-10·11: 저장 5개(옛/새 코드 양쪽) | `make_old_save.gd`, `make_new_save.gd`, `save_probe.gd`, `compare_saves.py`, `save_matrix.sh` | `save_matrix.md`, `save_probes/probe_{old,new}__*.json` |
| C-08: 캡처 4장 검증기 | 저장소의 `tools/art_pipeline/validate_visual_evidence_1080p.py` | `visual_validation_mine.json` |
| 6절 규칙 깨기: 변형 46개 + 수정 사본 | `mutate_ic.py`, `ic_matrix.sh`, `make_ic_tables.py` | `mutations_ic.md`(표), `ic_matrix.jsonl`(302행 원자료), `ic_all.log`, `cases/<변형>__<시험>.log`(실패·스크립트 오류·기준·수정 사본의 기록만) |
| 5.3절 봇 세 갈래(작전 1) | `bot_arms.gd`, `bot_arms.sh`, `bots_arms_report.py` | `bots_arms.md`, `bots_arms.jsonl`, `bot_runs/bot_1_<갈래>_<라운드>.json`(판마다 `full_operation.json`), `bot_arms.log` |
| 증거 묶음 | `stage_item2_evidence.py` | `MANIFEST.json`(파일마다 SHA-256) |

`cases/` 로그 이름은 `<변형>__<시험 글자>.log`이고 글자는 `o` offers · `u` contract_ui · `r` redline · `s` contract_save · `m` run_contract(m11) · `p` play_log · `b` boss_duel · `c` campaign이다.

## 도구 메모

- `tools/lowrun.py`(`run_godot_low.sh`가 부른다)는 Godot을 낮은 우선순위로 돌리고 `LOWRUN_TIMEOUT`초(기본 200, 0 = 제한 없음, 봇은 900) 뒤에 **자기가 띄운 자식 하나만** 멈춘다. `-s` 시험이 스크립트 오류를 내면 `quit()`에 닿지 못해 Godot이 매달리기 때문이다(`snapshot_no_redline` 변형의 `contract_save`). 표에서 `HANG`이다.
- `mutate_ic.py`의 변형은 사본의 코드를 문자열 치환으로 한 곳씩 깬다. 저장소 작업 트리는 건드리지 않는다.
- 봇은 사람이 아니다. 갈래는 (1) 러너의 `full_op_01`과 같은 중립 호출, (2) 실제 run id의 기본 제안, (3) REDLINE이고, 라운드마다 순서를 돌려 가며 한 번에 하나씩 돌렸다. 결과는 개수로만 적었고 균형 판단이 아니다.

이 기록은 그림·플레이·균형 승인이 아니다.
