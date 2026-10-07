# N-1 길찾기 막다른 구역 — 2026-10-03

## 결과

길찾기 감사는 수정 전 **70칸 FAIL**에서 수정 후 **12 px / 8 px 모두 0칸 PASS**가 됐다. 두 길찾기 파일을 되돌린 사본은 다시 **70칸 FAIL(exit 1)**이며 최초 감사와 JSON 바이트도 같다. 작전 9 봇은 세 번 모두 추출했고 600초 길찾기 정지는 없었다.

**전체 N-01…N-07을 PASS로 판정하지 않는다. N-06의 작전 10 결과 종류 일치 조건은 미충족이다.** 작전 10은 수정 전 2/2 추출, 수정 후 1/2 추출·1/2 전멸이다. 전멸 실행의 러너 FAIL과 원본 JSON을 보존했다. WIPED는 아래 관찰 숫자로 보고하며 균형 판정을 대신하지 않는다.

## 1. 커밋과 변경 파일

- 수정: `48a0bd28123d130defb39dcd6e917a3404400a1f` — Fix navigation escape paths at floor-clipped cover corners.
- 수정 전 고정 사본: `753cf02957bb104ac30450918deca10139b427d9`. 작업 중 Claude가 `cce3e6244c07783ff555cf04761e955f6ba34f38`에 검수 문서·증거를 커밋했다. 그 커밋에는 게임 코드·데이터 변경이 없으며 그대로 보존했다.
- 기록은 수정 커밋 이후 이 폴더만 지정하는 별도 로컬 커밋에 넣는다. 기록 커밋은 `git log -1 --format=fuller -- qa/nav_pockets_20261003`으로 확인한다.

| 그룹 | 변경 |
|---|---|
| 길찾기 | `scripts/combat/cover_navigation.gd`: 바닥 밖 덮개 모서리를 `battlefield.constrain`으로 걷는 바닥에 투영하고, 목표 보정과 기존 바닥·충돌 검사에 통과한 노드만 남김 |
| 충돌 확인 | 같은 파일: 경계 상자는 넓은 범위의 1차 검사로 사용. 상자에 걸린 구간은 실제 캐릭터 충돌 모양과 지상 충돌체를 3 px 여유로 조회. 양 끝 겹침 검사와 연속 이동 검사를 모두 수행. 전투 바닥·실제 충돌체가 없는 호출은 기존의 보수적인 상자 검사 유지 |
| 사격 위치 경로 | `scripts/combat/site7_enemy_tactics.gd`의 `LaneRoutes`만 변경: 별도 모서리 생성 대신 `CoverNavigation._fixed_nodes`를 공유하여 `_plan`과 노드·경로 길이가 같도록 함 |
| 시험 | `tests/smoke/cover_navigation_smoke.gd`: 기존 검사 유지, 네 막다른 구역에서 실제 `CharacterBody2D` 이동 검사 28개 추가 |
| 러너 | `tools/maintenance/run_regression_suite.py`: `nav_pockets`, full 전용, solo, 400초, `--out` JSON |
| 기록 | 이 README와 `evidence/`, `evidence_manifest.json`, 바이트 보존용 `.gitattributes` |

수정 커밋은 코드·시험·러너 네 파일뿐이다. 바닥, 덮개, 판, 미션·전투 데이터, 감사 도구를 수정하지 않았다. 공격·보스 패턴·적 수·체력·경제 한도 변경도 없다.

## 2. 검증

### N-01…N-07

| 기준 | 관찰 결과 |
|---|---|
| N-01 | PASS: 30개 방, 12 px 105,535칸 / 8 px 237,208칸, 각각 막힌 칸 0, exit 0 |
| N-02 | PASS: 두 길찾기 파일을 되돌린 사본의 12 px 감사가 70칸·4개 방, exit 1. 최초 재현 JSON과 SHA-256도 같음 |
| N-03 | PASS: 관련 다섯 시험 모두 통과. 기존 검사 삭제·기준 완화 없음. 아래 검사 수 비교 |
| N-04 | PASS: 수정 커밋의 `assets`, `art_src`, `motion_lab_v1`, `data` 변경 0. 고정 사본의 데이터 37파일 바이트 비교도 변경 0. 승인 원화 17/17 해시 일치 |
| N-05 | PASS: `--list`에 `nav_pockets full 400s … (solo)`. 77.8초 실측으로 full 전용. quick 47개·full 전용 31개·합 78개 |
| N-06 | **미충족 항목 있음**: 작전 9 3/3 추출·정지 없음, 작전 1·5 결과 종류 일치. 작전 10은 기준선 추출 2회와 달리 수정 후 전멸 1회 관찰 |
| N-07 | PASS: 같은 12 px 감사 69.493초 → 77.8초, **1.1195배(+11.95%)**, 1.25배 이내. 되돌림 대조는 65.415초. 8 px는 109.464초이며 수정 전 8 px 시간은 측정하지 않음 |

최초 70칸: 작전 1 `R02_CORRIDOR` 23, 작전 5 `R05_CARRIER` 9, 작전 9 `R04_GALLERY` 23, 작전 10 `R04_GALLERY` 15. 수정 후에도 12 px 검사 대상 바닥 칸·방·덮개 상자 수는 최초 재현과 같다.

감사 도구 SHA-256(수정 전·후·되돌림 모두 동일): `622f3edcc7cd7c6616b8dea439c6debb69a58246a62b607095fb08ec68ebf243`.

감사 JSON SHA-256:

| 파일 | SHA-256 |
|---|---|
| `evidence/baseline12.json`, `evidence/reverted12.json` | `5350c371feab59e8de61053c7cdc8813f35fbdca2f6536887b45d938764b4edb` |
| `evidence/fixed12.json` | `6e443aa8967a7e9d6c6ad8905c14a52c9c4ca73cb44ac9494ba5452e1c26b1e3` |
| `evidence/fixed8.json` | `34b651c66448e272e5d8e8cf522ee4c348d322906a76935af80bf0df99226889` |

### 기존 시험 검사 수

| 러너 이름 | 수정 전 | 수정 후 | 결과 |
|---|---:|---:|---|
| `cover_navigation` | 15 | 43 | PASS |
| `firing_lane` (`firing_lane_search_smoke.gd`) | 325 | 325 | PASS. 실제 10작전에서 후보별 경로 길이와 선택 사격 위치 동치 |
| `enemy_cover_nav` | 29사례 | 29사례 | PASS. 기존 시험은 요약 줄에 검사 총수를 출력하지 않음. 양쪽 `check.json`의 사례 수 비교 |
| `cover_ai` | 46 | 46 | PASS |
| `world_route` | 94 | 94 | PASS |

최종 `--only enemy_cover_nav,cover_ai,cover_navigation,world_route,firing_lane,nav_pockets`: `20261003_152407_custom`, **6/6 PASS**, QA 보호 변경·추가·삭제 0. 수정 전 다섯 시험: 고정 사본 `20261003_145123_custom`, **5/5 PASS**.

### 실제 이동 추가 시험

모든 사례는 실제 방·덮개와 연산자 충돌체를 사용한다. 시험 중 적·장판·분대 자동 처리를 멈추고 실제 연산자의 물리 이동을 구동한다. 게임 코드나 데이터를 바꾼 상태가 아니다. 각 사례는 열린 바닥, 경로 존재, 모든 구간의 바닥·충돌 안전, 실제 30 px 이상 탈출, 20초 내 목표 12 px 이내 도달, 바닥 이탈 없음, 0.8초 초과 정지 없음의 일곱 검사를 한다.

| 방 | 시작점 | 물리 tick | 목표까지 남은 거리 | 최대 연속 정지 |
|---|---|---:|---:|---:|
| 작전 1 R02_CORRIDOR | (3766, −289) | 93 | 9.88 px | 0.000초 |
| 작전 5 R05_CARRIER | (12246, −3639) | 205 | 10.31 px | 0.000초 |
| 작전 9 R04_GALLERY | (−6013, 3856) | 119 | 10.64 px | 0.000초 |
| 작전 10 R04_GALLERY | (9472, −2149) | 91 | 8.08 px | 0.000초 |

원본 출력: `evidence/fixed_navigation/cover_navigation.log`. 길이 동치 출력: `evidence/fixed_navigation/firing_lane.log`.

### 러너와 봇 원본 결과

시험은 전부 공식 러너의 `--only`로 실행했다. 감사 8 px와 되돌림 대조는 같은 감사 도구를 직접 실행했다. 러너를 중복 실행하지 않았고 감사와 봇을 동시에 돌리지 않았다. 모든 완료 러너의 QA 보호 변경·추가·삭제는 0이다.

| 묶음 | stamp | `--only` | 결과 |
|---|---|---|---|
| 수정 전 길찾기 | `20261003_145123_custom` | `cover_navigation,firing_lane,enemy_cover_nav,cover_ai,world_route` | **PASS**, 5/5 PASS |
| 최종 길찾기 | `20261003_152407_custom` | `cover_navigation,firing_lane,enemy_cover_nav,cover_ai,world_route,nav_pockets` | **PASS**, 6/6 PASS |
| 수정 전 봇 | `20261003_153434_custom` | `full_op_01,full_op_05,full_op_10` | **PASS**, 3/3 PASS |
| 수정 후 봇 1차 | `20261003_154433_custom` | `full_op_01,full_op_05,full_op_09,full_op_10` | **FAIL**, 3/4 PASS |
| 작전 9·10 재주행 | `20261003_155720_custom` | `full_op_09,full_op_10` | **PASS**, 2/2 PASS |
| 작전 9 3차 | `20261003_160946_custom` | `full_op_09` | **PASS**, 1/1 PASS |
| 수정 전 작전 10 추가 대조 | `20261003_160508_custom` | `full_op_10` | **PASS**, 1/1 PASS |

표의 수정 전 실행 폴더는 `.cache/diag/nav_pockets_20261003/baseline_project/qa/regression_runs/` 아래이고 나머지는 루트 `qa/regression_runs/` 아래다. 원본 summary와 봇 JSON을 `evidence/<묶음>/`에 바이트 그대로 복사했다.

| 구분 | 작전 | stamp | 결과 / exit | 게임 시간(초) | 마지막 기록 tick | 총 받은 피해 |
|---|---:|---|---|---:|---:|---:|
| 수정 전 | 1 | `20261003_153434_custom` | EXTRACTED / 0 | 120.276 | 6600 | 245.00 |
| 수정 전 | 5 | `20261003_153434_custom` | EXTRACTED / 0 | 152.544 | 9000 | 515.25 |
| 수정 전 | 10 | `20261003_153434_custom` | EXTRACTED / 0 | 233.607 | 13800 | 732.05 |
| 수정 후 | 1 | `20261003_154433_custom` | EXTRACTED / 0 | 126.608 | 7200 | 310.10 |
| 수정 후 | 5 | `20261003_154433_custom` | EXTRACTED / 0 | 153.412 | 9000 | 497.20 |
| 수정 후 | 9 | `20261003_154433_custom` | EXTRACTED / 0 | 165.324 | 9600 | 412.60 |
| 수정 후 | 10 | `20261003_154433_custom` | WIPED / 1 | 133.236 | 7800 | 413.20 |
| 수정 후 | 9 | `20261003_155720_custom` | EXTRACTED / 0 | 163.067 | 9600 | 358.10 |
| 수정 후 | 10 | `20261003_155720_custom` | EXTRACTED / 0 | 204.677 | 12000 | 872.00 |
| 수정 후 | 9 | `20261003_160946_custom` | EXTRACTED / 0 | 180.529 | 10200 | 487.30 |
| 수정 전 | 10 | `20261003_160508_custom` | EXTRACTED / 0 | 227.045 | 13200 | 610.90 |

작전 9: **3/3 EXTRACTED, WIPED 0, 600초 정지 0**. 게임 시간 165.324 / 163.067 / 180.529초. 작전 1·5는 수정 전·후 각각 추출 1회로 결과 종류가 같다.

작전 10: **수정 전 추출 2회·전멸 0회, 수정 후 추출 1회·전멸 1회**. 전멸은 게임 시간 133.236초, 보스방 step 4에서 발생했다. 경로 정지나 600초 제한으로 끝난 것이 아니다. 추출, 여섯 방, 선택 방 수거, 전체 적 처치 검사 네 개가 실패했고 해당 러너는 **FAIL**이다. 이 실패를 PASS로 바꾸거나 집계에서 빼지 않았다. 기준선과 수정 후 각각 두 판으로 원인을 확정하지 못하며, 균형 판단은 Claude 검수와 사용자의 몫이다. 특히 전멸 판은 일찍 끝나므로 총 피해를 완주 판과 직접 같은 기준으로 비교할 수 없다.

최초 재현과 되돌림의 감사 명령은 아래와 같다. 실행 시 로그 파일도 프로젝트 `.cache/`로 지정했다. `Godot`은 `D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64_console.exe`다.

```text
Godot --headless --path . -s res://tools/environment/audit_nav_pockets.gd -- --cell=12 --out=res://.cache/diag/nav_pockets_20261003/baseline12.json
Godot --headless --path . -s res://tools/environment/audit_nav_pockets.gd -- --cell=8 --out=res://.cache/diag/nav_pockets_20261003/fixed8.json
Godot --headless --path .cache/diag/nav_pockets_20261003/reverted_project -s res://tools/environment/audit_nav_pockets.gd -- --cell=12 --out=res://.cache/reverted12.json
python tools/maintenance/run_regression_suite.py --list
python qa/site7_op10_art_approval_20261002/tools/verify_hashes.py
git diff --check
```

수정 후 12 px는 등록한 `nav_pockets`의 기본 격자로 공식 러너에서 실행했다. 수정 전 사본의 시험은 같은 공식 명령에 `--project .cache/diag/nav_pockets_20261003/baseline_project`를 붙였다. 전체 quick / 전체 full은 **실행하지 않았다**. 이번 지시대로 필요한 `--only`만 실행했다.

중간 조사 실패도 보존한다: `20261003_150107_custom`은 작전 1의 23칸이 남고 실제 이동 시험도 실패했다. `20261003_151913_custom`은 감사 0칸이지만 기존 합성 지형 검사 세 개가 실패했다. 실제 전투 바닥이 아닌 호출에서 원래 경계 상자 검사를 유지하도록 고친 뒤 최종 `20261003_152407_custom`에서 기존 15개와 새 28개가 모두 통과했다. 두 중간 요약은 `evidence/investigation_1/`, `evidence/investigation_2/`에 남겼다.

## 3. 상수와 검사 한도

| 파일 / 이름 | 이전 → 이후 | 이유 |
|---|---|---|
| `cover_navigation.gd` / `GROUND_MARGIN` | 기존 `Vector2(3,3)`의 3 px → 이름을 둔 3.0 px | 상자 확대와 실제 충돌 모양 조회에 같은 여유 사용. 수치는 그대로 |
| 같은 파일 / `CORNER_CLEARANCE`, `LOCAL_OBSTACLE_RADIUS`, `MAX_GRAPH_EDGE` | 12 / 1000 / 900 → 동일 | 기존 길찾기 한도 유지 |
| 같은 파일 / 새 지상 조회 `collision_mask` | 새 조회에 1 | 지상 충돌을 확인. 로봇·연산자의 충돌 레이어 설정은 변경 없음 |
| `cover_navigation_smoke.gd` / 네 시작점 | 새 사례, 위 실제 이동 표의 좌표 | 최초 네 클러스터를 실제 캐릭터로 검증 |
| 같은 시험 / 이동 한도 | 새 사례에 20초, 목표 12 px, 이동 30 px 초과, 정지 0.8초 이하 | 경로 존재뿐 아니라 실제 이동·도달·멈춤 검증. 원래 검사 삭제 없음 |
| 같은 시험 / tick·대기 | 새 사례에 1/60초, 장면 대기 8+4 프레임·정리 3 프레임 | 실제 물리 서버의 방·충돌체 준비 후 이동 |
| 러너 / `nav_pockets` | 새 항목 400초, solo, full 전용, `nav_pockets.json` | 감사 실측 77.8초로 1분 초과. 기존 시험 시간 한도 변경 없음 |

바닥 구간의 기존 검사, 900 px 간선 제한, Dijkstra 선택 순서와 기존 캐시는 유지한다. 실제 지상 조회는 고정 간선의 양방향 응답이 같도록 끝점 순서를 정규화한다. `LaneRoutes`는 추가된 모서리 노드까지 같은 생성 함수를 사용한다. 보스 공정성·경제의 상수는 변경하지 않았다.

## 4. 데이터와 승인 그림

데이터 변경 **0**. 수정 전 고정 사본의 `data/` 37파일과 현재 파일의 SHA-256을 비교해 변경 0을 확인했다. 비교 값은 `evidence/baseline_source.json`과 `evidence/audit_comparison.json`에 있다. 바닥 추적, 덮개 위치·크기, 판 이미지, 미션 JSON은 그대로다.

승인 그림 검사 출력: **`17 of 17 approved files unchanged`**, exit 0. 승인 SHA와 현재 SHA는 `evidence/approved_art.json`에 있다. `assets`, `art_src`, `motion_lab_v1`의 Git 변경도 0이다.

고정 사본은 수정 전 코드·데이터를 복사하고 리소스를 원본의 읽기 입력으로 연결했다. 두 사본에서는 가져오기를 실행하지 않았다. 그 폴더의 `git` 조회는 부모 저장소를 가리키므로 러너 메타에 작업 중 HEAD가 찍힐 수 있다. 실제 기준은 `evidence/baseline_source.json`의 고정 원본 커밋·파일 해시와 봇 JSON의 `tested_code_sha256`이다. 되돌림 사본에는 두 길찾기 파일만 그 원본 바이트로 덮었고 감사 JSON은 최초 재현과 바이트까지 같다.

## 5. 캡처와 증거

새 그림·게임 이미지·영상 캡처 **없음**. 따라서 이번에는 `validate_visual_evidence_1080p.py`를 실행하지 않았다. 물리 이동과 실제 작전 주행은 위 시험 출력·봇 원본 JSON으로 기록했다. 이 증거는 사람의 플레이나 그림 승인을 대신하지 않는다.

모든 복사 증거의 SHA-256은 `evidence_manifest.json`에 있다. 봇 원본에는 결과·경로 trace·피해·공격/발사 기록·시험 코드 해시·실패 목록이 포함돼 있다. 작업 파일과 원본 실행 폴더는 프로젝트 `.cache/` 및 git-ignored 회귀 실행 폴더에 보존했다. QA 반입은 모든 러너가 종료되고 `Get-CimInstance Win32_Process`로 새 러너가 없음을 확인한 뒤 수행했다.

증거의 CRLF 바이트를 보존한 상태에서는 최초 Git staged whitespace 검사가 줄끝 CR을 공백으로 보고 실패했다. 이 기록 폴더에만 `-text`와 기존 기본 공백 검사에 `cr-at-eol`을 더한 속성을 지정하여 원본 바이트를 유지했고, 최종 scoped 검사에서 통과했다. 게임 시험이나 감사 기준의 변경은 없다.

## 6. FPS

FPS 측정·개선 주장 **없음**. 위 12 px 감사 실행 시간 비교는 길찾기 감사의 비용이며 게임 FPS 측정이 아니다. 같은 세션 회전 A/B FPS 시험은 실행하지 않았다.

## 7. 남은 항목과 검수

- **N-06 작전 10 결과 종류 일치 미충족**: 0/2 → 1/2 WIPED. Claude가 변경 방향·경로와 봇 결과를 독립 검수할 때 확인할 숫자다. 전멸 원인을 추측으로 확정하지 않았다. 적 수·체력·보스 공격·시험 기준을 조절하지 않았다.
- 12 px / 8 px 격자는 각각 검사한 칸의 결과다. 모든 연속 좌표의 무결함이나 사람 플레이·균형 승인을 주장하지 않는다. 네 클러스터에는 실제 물리 탈출 검사를 추가했다.
- 전체 quick / 전체 full, 이미지 캡처·1080p 검증기, FPS A/B는 이번에 실행하지 않았다. 실행한 명령과 실제 결과는 위에 구분했다.
- 항목 2는 시작하지 않았다. 기록과 로컬 커밋 이후 멈춘다.

**이 기록은 그림·플레이·균형 승인이 아니다.**


## 8. 9.8 B-3 / B-4 보완 — 2026-10-03

Claude의 9.8 검수(`4f86d3af3749efc4518305c076568a863898005c`, `qa/nav_pockets_review_20261003/REVIEW_KO.md`)는 N-01…N-07을 충족한 것으로 정리했다. 앞선 보고의 N-06 미충족 표기는 초기 보고이며, 검수에서는 봇 결과를 합격/불합격 기준이 아닌 관찰 숫자로 판단했다. 원래 결과와 전멸 증거는 그대로 보존한다. 이번 변경은 검수가 지적한 quick 시험 B-3와 B-4만 보완한다.

### 변경 범위와 C-05

| 파일 | 변경 |
|---|---|
| `tests/smoke/combat_query_fastpath_smoke.gd` | 새 충돌·탈출 노드 규칙을 사용하는 독립 기준 계획기 추가. 생산 코드의 가시성·물리 조회·목표 보정·노드 생성 함수를 호출하지 않는 전체 Dijkstra 스캔으로 캐시 계획기의 결과를 정확히 비교. 옛 `ref_plan`·`ref_clear_ground`는 `ref_old_*`로 보존하고, 옛 계획기가 찾은 경로보다 길거나 그 경로를 잃는 경우를 거절하는 검사 추가 |
| `tests/smoke/hazard_expansion_smoke.gd` | 기존 가상 1000×1000 상자에 대응하는 실제 `StaticBody2D`를 장판 중심에 시험 중에만 설치. 지상 layer 1, mask 0, 같은 크기의 직사각형 충돌체. 물리 서버 등록 후 기존 막힌 탈출 거절 검사를 수행하고, 즉시 해제한 뒤 다음 장판을 검사 |
| `qa/nav_pockets_20261003/README_KO.md` | 이 변경 요약·정상 실행·대조 확인을 뒤에 추가 |

기존 검사 삭제·조건 완화 **0**. `combat_query_fastpath`는 **31 → 34개**, `hazard_expansion`는 **438 → 438개(15개 방)**다. 바닥 3,000점·구간 2,000개·소품당 60개 ray·actor당 36개 계획의 기존 표본 수를 유지했다. 옛 두 기준 함수의 본문은 이름과 내부 호출 이름을 되돌려 비교했을 때 이전 HEAD와 정확히 같다.

추가된 시험 상수 `REF_GROUND_MARGIN=3.0`은 기존 게임 규칙의 3 px를 기준 계획기에 고정한 값이다. B-4 fixture의 1000×1000은 이전 가상 상자 크기 그대로이며, 등록·해제 후 각각 물리/처리 프레임 두 번을 기다린다. 게임 상수, 적 수·체력, 경제·보스 한도, 장판 경고·피해·탈출 시간 한도는 변경하지 않았다.

### 공식 러너 결과

| 명령 | 실행 폴더 | 관찰 결과 |
|---|---|---|
| `python tools/maintenance/run_regression_suite.py --only combat_query_fastpath,hazard_expansion` | `qa/regression_runs/20261003_194543_custom/` | **2/2 PASS**, 52초. B-3 34개(11.6초), B-4 438개(26.9초) |
| `python tools/maintenance/run_regression_suite.py --suite quick` | `qa/regression_runs/20261003_195111_quick/` | **47/47 PASS**, 499초 |

각 실행의 `SUMMARY_KO.md`·`summary.json`·`logs/`가 원본이다. 두 실행 모두 QA 보호 변경·추가·삭제 **0**이다. 러너 시작 직전마다 `Get-CimInstance Win32_Process`로 기존 `run_regression_suite.py`가 없음을 확인했고, 두 공식 실행과 아래 대조 실행은 모두 순차 실행했다. quick 전체는 한 번 실행했다. full은 이번에 실행하지 않았다.

B-3의 **324개 계획 모두 새 기준과 정확히 일치**한다. 옛 계획기가 찾은 273개 중 더 길어진 계획은 0개, 짧아진 계획은 25개다. 옛 계획기가 찾지 못했던 51개 중 15개가 새로 연결되어 새 계획의 유효 경로는 288개다. 옛 기준이 길을 못 찾은 경우만 길이 부등식 검사에서 제외하며, 새 기준과의 정확한 비교는 324개 전부 수행한다.

### 대조 확인

작업 사본·원본/사본 SHA-256·변형 한 줄은 `.cache/diag/nav_quick_fixes_20261003/counterfactual_variants.json`, 대조 결과와 로그 해시는 `counterfactual_results.json`에 보존했다. 게임 코드와 데이터는 바꾸지 않은 채 시험 사본의 한 줄만 바꿨다.

| 대조 사본 | 한 줄 변형 | 실제 결과 |
|---|---|---|
| `combat_query_old_reference.gd` | 정확한 비교의 기준을 다시 `ref_old_plan`으로 변경 | **예상 FAIL, exit 1**. 34개 중 계획 비교 검사 3개 실패(예시 9줄을 포함한 출력은 `12 of 34`). 작전 1·3·5에서 108개씩 검사하여 각각 14·11·15개의 불일치 재현 |
| `hazard_without_blocker.gd` | `stage.add_child(blocker)`를 생략하여 물리 세계에 충돌체를 설치하지 않음 | **예상 FAIL, exit 1**. 기존 438개 중 작전 7 `R02_FREEZE`, `R04_COMPRESSORS`의 막힌 탈출 거절 두 검사만 실패. 정상판에서는 두 검사 모두 통과 |

두 대조 모두 `SCRIPT ERROR` 없이 끝났다. 정상판과 B-4 대조의 실제 탈출 격자에서 방별 서 있을 수 있는 칸 수는 같고, 실제 장판 탈출 실패 칸은 모두 0이다. 바뀐 결과는 막힌 탈출의 음성 대조 둘뿐이다. 대조의 FAIL은 검사 민감도 확인이며 공식 러너 PASS에 합산하지 않는다.

대조 명령(로그는 해당 `.cache/diag/nav_quick_fixes_20261003/`의 `.godot.log`·`.stdout.log`):

```text
Godot --headless --path . --log-file "D:/AI 종합 폴더/Games/Sable-circuit/.cache/diag/nav_quick_fixes_20261003/combat_query_old_reference.godot.log" -s res://.cache/diag/nav_quick_fixes_20261003/combat_query_old_reference.gd
Godot --headless --path . --log-file "D:/AI 종합 폴더/Games/Sable-circuit/.cache/diag/nav_quick_fixes_20261003/hazard_without_blocker.godot.log" -s res://.cache/diag/nav_quick_fixes_20261003/hazard_without_blocker.gd -- --out=res://.cache/diag/nav_quick_fixes_20261003/hazard_without_blocker.json
```

`Godot`은 앞선 기록과 같은 D: 드라이브의 4.7.1 콘솔 실행 파일이다. 공식 러너와 대조에서 TEMP/TMP는 프로젝트 `.cache/tmp/`, Python bytecode 캐시는 `.cache/python/`으로 지정했다. 검수용 대조 사본·실패 로그는 보존하며, 중복 기록 초안은 반입 후 정리한다.

### 범위와 남은 검수

시험 파일 두 개와 이 README만 로컬 커밋한다. 게임 코드·미션/전투 데이터·바닥·덮개·그림·감사 도구·러너·UID 변경은 0이다. 커밋은 `git log -1 --format=fuller -- tests/smoke/combat_query_fastpath_smoke.gd tests/smoke/hazard_expansion_smoke.gd qa/nav_pockets_20261003/README_KO.md`로 확인한다.

9.8의 권장 N-6(`LaneRoutes`의 막다른 구역 길이 동치 추가 검사), N-7(끝점 순서·1 px 틈 변형 추가 검사), N-8은 이번 B-3/B-4 범위에서 별도 보완하지 않았다. 새 그림·게임 이미지/영상 캡처·FPS 측정은 없다. 항목 2는 시작하지 않는다. **그림·플레이·균형 승인이 아니다.**
