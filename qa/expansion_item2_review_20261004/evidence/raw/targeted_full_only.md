# 풀 전용 시험 표적 실행 (b4aa2ae0 팁)

Codex의 quick 52/52는 풀 전용 시험을 볼 수 없다. 이 커밋이 건드린 흐름(`GameFlow.deploy_mission`, 브리핑, 저장 스키마, 계약 사전)을
읽는 풀 전용 시험을 `deploy_mission(` `open_mission_briefing` `SAVE_SCHEMA_VERSION` `_run_contract` `configure_campaign(` `briefing_screen`으로 찾아 따로 돌렸다.

| 시험(러너 id) | 결과 | 검사 | 기록 |
|---|---|---:|---|
| `campaign` | **SCRIPT_ERROR** (9.6 s) `Invalid access to property or key 'mission_id' on a base object of type 'Dictionary'` | - | `qa/regression_runs/20261004_173328_custom` (git-ignored), `raw/only_campaign.log` |
| `campaign` (한 줄 되돌린 사본 `proj_ic`) | PASS (28 s) | 235 | `raw/cases/mission_id_restored__c.log`, `raw/ic_matrix.jsonl` |
| `demo_integration` | PASS | 26 | `raw/runs/20261004_182829_custom_*` |
| `m10_intel` | PASS | 39 | 같음 |
| `m13_loadout` | PASS | 46 | 같음 |
| `m8_extraction_progression_smoke` (러너에 없음, `-s`로 직접) | `b4aa2ae0`와 `7b26a152`에서 **바이트까지 같은 로그**: 46줄 PASS, 둘 실패("Core C actual node opens extraction decision gate", "M8 extraction IDs match authored mission data") | 48 | `raw/m8_proj_head.log` · `raw/m8_proj_ic.log` (`cmp` 일치). 항목 2와 무관한 이전부터의 실패 |

판단: B-1 말고는 이 표적 묶음에서 새로 깨진 풀 전용 시험이 없다. 풀 스위트 전체(`--suite full`, 약 90분)는 B-1이 고쳐진 팁에서 돌린다.
