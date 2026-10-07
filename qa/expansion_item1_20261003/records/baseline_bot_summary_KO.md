# baseline — 작전 6–10 실제 봇 기록

Selected 3 stamp(s); expected 3. Missing records stay unknown.

피해는 실제 `damage_by_source` 합계다. 부활·보급 이전 피해도 포함하며 최종 체력으로 추정하지 않는다.
기록이 없거나 러너가 진행 중이면 미확인으로 남긴다. 이 표는 사람 플레이·균형 승인이 아니다.

| 회차 | 작전 | 러너 상태 | 기술 기록 | 결과 | WIPED | 받은 피해 HP | 러너 stamp |
|---|---|---|---|---|---|---|---|
| 1 | MIS_CH01_06 | PASS | PASS_TECHNICAL_PLAYTHROUGH | EXTRACTED | False | 544.6 | 20261003_100926_custom |
| 1 | MIS_CH01_07 | PASS | PASS_TECHNICAL_PLAYTHROUGH | EXTRACTED | False | 911.2 | 20261003_100926_custom |
| 1 | MIS_CH01_08 | FAIL | FAIL | WIPED | True | 346.0 | 20261003_100926_custom |
| 1 | MIS_CH01_09 | PASS | PASS_TECHNICAL_PLAYTHROUGH | EXTRACTED | False | 396.0 | 20261003_100926_custom |
| 1 | MIS_CH01_10 | PASS | PASS_TECHNICAL_PLAYTHROUGH | EXTRACTED | False | 745.9 | 20261003_100926_custom |
| 2 | MIS_CH01_06 | PASS | PASS_TECHNICAL_PLAYTHROUGH | EXTRACTED | False | 514.1 | 20261003_102455_custom |
| 2 | MIS_CH01_07 | FAIL | FAIL | WIPED | True | 591.7 | 20261003_102455_custom |
| 2 | MIS_CH01_08 | FAIL | FAIL | WIPED | True | 346.0 | 20261003_102455_custom |
| 2 | MIS_CH01_09 | PASS | PASS_TECHNICAL_PLAYTHROUGH | EXTRACTED | False | 316.6 | 20261003_102455_custom |
| 2 | MIS_CH01_10 | PASS | PASS_TECHNICAL_PLAYTHROUGH | EXTRACTED | False | 971.06 | 20261003_102455_custom |
| 3 | MIS_CH01_06 | PASS | PASS_TECHNICAL_PLAYTHROUGH | EXTRACTED | False | 487.5 | 20261003_103852_custom |
| 3 | MIS_CH01_07 | PASS | PASS_TECHNICAL_PLAYTHROUGH | EXTRACTED | False | 860.25 | 20261003_103852_custom |
| 3 | MIS_CH01_08 | FAIL | FAIL | WIPED | True | 394.3 | 20261003_103852_custom |
| 3 | MIS_CH01_09 | FAIL | FAIL | 미확인 | 미확인 | 109.0 | 20261003_103852_custom |
| 3 | MIS_CH01_10 | PASS | PASS_TECHNICAL_PLAYTHROUGH | EXTRACTED | False | 761.65 | 20261003_103852_custom |

## 작전별 요약

| 작전 | 관측 보고서 | 기대 회차 | WIPED | WIPED 미확인 회차 | 피해 평균 | 피해 최소–최대 |
|---|---|---|---|---|---|---|
| MIS_CH01_06 | 3 | 3 | 0 | 0 | 515.4 | 487.500–544.600 |
| MIS_CH01_07 | 3 | 3 | 1 | 0 | 787.717 | 591.700–911.200 |
| MIS_CH01_08 | 3 | 3 | 3 | 0 | 362.1 | 346.000–394.300 |
| MIS_CH01_09 | 3 | 3 | 0 | 1 | 273.867 | 109.000–396.000 |
| MIS_CH01_10 | 3 | 3 | 0 | 0 | 826.203 | 745.900–971.060 |

## 미확인·실패 및 출처

- 20261003_100926_custom / full_op_06 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_100926_custom\out\full_op_06\full_operation.json` / SHA-256 `77e147ea2e6f74c419716a56dfae4ab80e80ba55c4338036ef26fb9c7face6ff`
- 20261003_100926_custom / full_op_07 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_100926_custom\out\full_op_07\full_operation.json` / SHA-256 `58410a1f5a4d5649823d78bdfe7ef89e7c416bdb9d707ffdada6804274d3297f`
- 20261003_100926_custom / full_op_08: Live combat and extraction succeed without cheats; All six rooms reached; not early extraction; Both optional rooms recovered; All authored waves and boss defeated through real damage
- 20261003_100926_custom / full_op_08 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_100926_custom\out\full_op_08\full_operation.json` / SHA-256 `cd5a0070f7a99a6425acdf77cba3450eff153c13d4efcd91413d279c510ac03a`
- 20261003_100926_custom / full_op_09 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_100926_custom\out\full_op_09\full_operation.json` / SHA-256 `c44398ce4a96941e162e681d65df294b9e54003ce7de1d7a1d494f0700237350`
- 20261003_100926_custom / full_op_10 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_100926_custom\out\full_op_10\full_operation.json` / SHA-256 `4d24d4e064f496ee9b0a5890226a80c837ad0b3411435344de89a36ae848e312`
- 20261003_102455_custom / full_op_06 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_102455_custom\out\full_op_06\full_operation.json` / SHA-256 `5c6a7829324bbeef6bef711ba57519e268bfddba87f62bdc7cd12490cc80b09a`
- 20261003_102455_custom / full_op_07: Live combat and extraction succeed without cheats; All six rooms reached; not early extraction; Both optional rooms recovered; All authored waves and boss defeated through real damage
- 20261003_102455_custom / full_op_07 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_102455_custom\out\full_op_07\full_operation.json` / SHA-256 `3d771cc85bff7240f861e3938fe6fe215cf078b0e905f31cdc368a4fb8391cec`
- 20261003_102455_custom / full_op_08: Live combat and extraction succeed without cheats; All six rooms reached; not early extraction; Both optional rooms recovered; All authored waves and boss defeated through real damage
- 20261003_102455_custom / full_op_08 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_102455_custom\out\full_op_08\full_operation.json` / SHA-256 `aa7c8c310d41556c89caec9b8db116d11cfc0868eff883e0093aafc50191b179`
- 20261003_102455_custom / full_op_09 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_102455_custom\out\full_op_09\full_operation.json` / SHA-256 `89bd472647615249daf536fcb932c2178e188a155899520465d6c6d22ecc7de3`
- 20261003_102455_custom / full_op_10 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_102455_custom\out\full_op_10\full_operation.json` / SHA-256 `ea170314e3688eb3fc096fdbc632142153b546b9e9162239ec0eb144e53b95a2`
- 20261003_103852_custom / full_op_06 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_103852_custom\out\full_op_06\full_operation.json` / SHA-256 `d0a97d19fcdba064aa9b430999171b62bc7ef932ea804022cb55a4ef399de733`
- 20261003_103852_custom / full_op_07 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_103852_custom\out\full_op_07\full_operation.json` / SHA-256 `63b584003b0c1ea92610f672523dff97034a88a943a17613469933f715543f4f`
- 20261003_103852_custom / full_op_08: Live combat and extraction succeed without cheats; All six rooms reached; not early extraction; Both optional rooms recovered; All authored waves and boss defeated through real damage
- 20261003_103852_custom / full_op_08 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_103852_custom\out\full_op_08\full_operation.json` / SHA-256 `1b92392d506644e65e6f29adc1505aa6b89e3fa78541d7669d7b1606bf1648b7`
- 20261003_103852_custom / full_op_09: reported mission None differs from expected MIS_CH01_09; Route finishes within technical playthrough bound; Live combat and extraction succeed without cheats; All six rooms reached; not early extraction; Ledger acquired through interaction; Both optional rooms recovered; All authored waves and boss defeated through real damage
- 20261003_103852_custom / full_op_09 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_103852_custom\out\full_op_09\full_operation.json` / SHA-256 `a7c7a2237f53b341e2b39e9f0043bf915f145ca26cc6af354a4a258a3238cb75`
- 20261003_103852_custom / full_op_10 보고서: `D:\AI 종합 폴더\Games\Sable-circuit\.cache\diag\expansion_item1_20261003\baseline_project\qa\regression_runs\20261003_103852_custom\out\full_op_10\full_operation.json` / SHA-256 `f35e7da41535ae484b6dbc96c2842261518023cafbc9be1ef7bb2bd460e86fb0`
