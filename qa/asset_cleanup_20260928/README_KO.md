# 2026-09-28 폐기 자산 정리

사용자 지시: "qa 때 만들었던 비디오 파일들도 전부 포함해서 필요없는 자산들과 테스트본 들 전부 삭제해라",
"테스트에서 사용하는 Motion Studio 픽스처도 지워라 그냥".

`tools/maintenance/retire_20260928.py --apply`로 1,237건(21.4 GB)을 git 무시 폴더 `_retired_20260928/`로
옮겼다. 영구 삭제는 사용자가 이 폴더를 지워서 한다. 행 목록은 `retirement_manifest.jsonl`에 있다.
파일은 SHA-256과 크기를, 스크래치 폴더는 파일 수와 바이트를 기록했다. git 추적에서 뺀 파일
1,105개는 `tracked_removed.txt`에 있다.

| 분류 | 크기 | 항목 |
|---|---:|---|
| `.cache/` 스크래치 (Godot, tmp, sites_tmp, Codex 작업 중인 diag 제외) | 11,287 MB | 폴더 25 + 파일 |
| 끝난 Claude worktree 3개 (브랜치는 유지, `git worktree prune`) | 8,119 MB | 3 |
| QA 캡처·리뷰 이미지 (JSON·MD 기록과 오디오, 문서가 인용한 1장은 유지) | 813 MB | 626 |
| v1 맵 판 원본 (IMAGE_A 참고 이미지와 로비 판 원본은 유지) | 505 MB | 132 |
| v1 맵 판 런타임 이미지와 .import (로비 배경 1장, 소품, 방 윤곽 유지) | 266 MB | 178 |
| v2 판 생성 시도본 (선택된 것은 RAW_NATIVE와 같은 바이트) | 150 MB | 76 |
| 회귀 실행 출력 `qa/regression_runs/` | 85 MB | 5,588 파일 |
| v2 격리·대체된 판 이미지 (prompt·rejection 기록은 유지) | 62 MB | 33 |
| Motion Studio 후보 이미지와 픽스처 스펙 | 51 MB | 59 |
| QA 영상 | 23 MB | 1 |
| 픽스처 전용 렌더 테스트 2개 | 0 MB | 2 |

테스트 변경:
- `site7_enemy_facing_smoke.gd`와 `site7_machine_source_smoke.gd`(퀵 스위트)는 이제 2026-09-13 후보
  대신 레지스트리의 검토된 스펙(`EnemyActor.reviewed_machine_spec`)을 붙인다. 이식 후 각각
  224 / 436 checks로 PASS했다.
- `site7_enemy_facing_capture.gd`, `site7_new_robots_check.gd`, `site7_anchor_candidate_capture.gd`는
  앱 레지스트리 경로만 남기거나 기본 입력을 런타임 스펙으로 바꿨다.
- `site7_machine_candidate_capture.gd`와 `site7_machine_edge_case_smoke.gd`는 퇴역했다. 이 테스트의
  근접 목표, 숨은 RGB 중복, 중단된 경고 케이스는 더 이상 검사하지 않는다.

## git 저장소 정리 (같은 날, 사용자 지시 "오래된 것들은 다 지워")

- 정리 전 `.git` 전체(팩 6.55 GiB, ref 71개)를 `_retired_20260928/git_before_prune/`에 하드링크로 보존했다.
  `git --git-dir=_retired_20260928/git_before_prune ...`로 옛 기록을 그대로 읽을 수 있고, 이 폴더를 지우면 사라진다.
- 옛 ref 68개 삭제(`git_refs_plan.txt`의 DEL 행): 8월 기능 브랜치 18개, `main`, `claude/*` 3개, `codex/m27–m29`,
  `chore/ual-free-standard-assets`, GitHub 원격 추적 ref 22개(`origin/HEAD` 포함), 보관 태그 18개, 9/25·9/27 Codex 체크포인트 2개.
  남은 ref: `integrate/site7-demo-20260924`와 오늘의 Codex 체크포인트(작업 트리 스냅샷).
- 기록 경계: `.git/shallow` = `9bf6487f7`(9/24 "retire unused assets"). 그 이후 커밋의 해시는 바뀌지 않았다.
  브랜치 기록은 66개 커밋이다. 이전 커밋 해시를 인용한 기록은 위 백업에서 읽는다.
- reflog를 모두 비우고 `git -c pack.threads=2 gc --prune=1.hour.ago`로 닿지 않는 객체를 지웠다.
  Codex가 동시에 쓴 1시간 이내 객체는 남겼다. 이미 없는 그래프를 가리키던 `commit-graph-chain`은
  `.cache/tmp/`로 옮기고 `git commit-graph write --reachable`로 다시 만들었다.
- 결과: `.git` 6.8 GB → 2.7 GB(팩 1개, 2.68 GiB, 쓰레기 0). `git fsck --connectivity-only` 통과.
  남은 2.7 GB는 9/24 이후 기록이며, 오늘 퇴역한 QA 캡처와 v1 판(약 1 GB)도 여기에 들어 있다.
