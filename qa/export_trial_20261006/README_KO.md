# Windows 시험 빌드 — 만들었고, 켜 봤고, 담긴 파일을 전부 읽어 봤다

작성 2026-10-06 밤 · 작성자 Claude · 대상 커밋 `25fc3c31` (런타임 폴더는 커밋과 같다: `git status`에서 `scripts` `scenes` `data` `assets` `sound` `motion_lab_v1/public/assets/atlas` `project.godot` 변경 0)

## 판정: 닫힌 시험용(아는 사람 몇 명에게 나눠 주는 것)으로는 만들어진다. 공개 배포 수준은 아니다

사용자가 "이거 배포해도 될 수준이냐?"고 물었을 때 나는 "닫힌 시험은 되고 공개는 아직"이라고 답하고, 아직 어떤 내보내기 빌드도 시도해 본 적이 없다는 것을 이유 하나로 들었다. 그 이유를 지우려고 실제로 내보냈다. **결과: 내보내기는 된다.** 나머지 이유(사람이 쏴 본 기록이 없다, 승인한 그림은 작전 10뿐이다, 서명·설치기가 없다)는 그대로다. 이 기록은 그림·플레이·균형·배포 승인이 아니고, 아무것도 올리거나 서명하거나 공개하지 않았다(`AGENTS.md` 첫 절이 업로드를 막는다).

## 1. 한눈에

| 항목 | 결과 |
|---|---|
| 빌드 | Godot 4.7.1 공식 Windows **release** 템플릿(읽기 전용으로 복사, SHA-256 대조), 실행 파일 `SableCircuit.exe` 109,212,160 B + 팩 `SableCircuit.pck` 462,961,740 B = **572,173,900 B (545.6 MiB)**. 둘이 같은 폴더에 있어야 한다. 두 파일을 deflate로 묶으면 494,255,524 B(0.864배, 471 MiB) |
| 만든 시간 | 가져오기 77 s + 내보내기 14 s = 95 s(처음 만들 때는 가져오기가 34 s였다. 늘어난 이유는 재지 않았다) |
| 팩 | 726개 파일. `assets` 381 · `motion_lab_v1` 102 · `sound` 10 · `.godot/imported` 57 · `data` 38 · `scripts` 108 · `scenes` 13 |
| 켜 보기 | 제목 화면 · 작전 1–10 전투 미리보기(게임 자신의 `--battle-stage=N` 경로) · 출격 경로(`--stage1`): **26회 실행, 종료 코드 전부 0, 스크립트 오류 0** |
| 프레임 | 수직동기를 켠 모든 실행이 **60 FPS**(최저 60). 수직동기를 끈 실제 전투: 중앙값 **152–221 fps**, 최저 114–144(아래 3절) |
| 팩 감사 | 날 바이트 파일 374개 중 없는 것 **0** · 리소스 278개 중 없는 것 0 · 이미지 해독 84/84 · 로드 152/152 · 음악 9/9 |
| 엔진 메시지 | 종료 때 나는 "ObjectDB instances were leaked" 경고와 "resources still in use" 오류뿐. 프로젝트 폴더에서 돌릴 때도 똑같이 나고, 게임 기능과 무관하다 |
| 1080p 프레임 | 세 장, **정확히 1920×1080**, `validate_visual_evidence_1080p.py` PASS(동적 캡처 필수 조건 포함). 직접 봤다 |
| 진짜 저장 폴더 | 이 빌드의 모든 실행은 `APPDATA`와 `TEMP`를 `.cache/export_trial/env/`로 돌려서 돌렸다. `%APPDATA%\Godot\app_userdata\SABLE CIRCUIT`의 저장 파일 세 개(`campaign_progression_v1.json` · `active_run_checkpoint_v1.json` · `sable_profile_index.cfg`)의 수정 시각은 2026-08-29/30 그대로다 |
| 승인한 그림 | `verify_hashes.py`: **17 of 17 approved files unchanged** |

## 2. 만들고 확인한 방법

```
python tools/environment/build_windows_test_build.py build
python tools/environment/build_windows_test_build.py check --only boot,flow,perf,audit,native
```

`build`는 런타임 폴더만 `.cache/export_trial/stage/`에 복사해(프로젝트 폴더와 그 가져오기 캐시는 건드리지 않는다) 에디터로 가져오고, release로 내보내고, 팩 안의 파일 수를 센다. `check`는 내보낸 실행 파일을 직접 돌린다. 둘 다 다른 Godot나 회귀 러너가 살아 있으면 시작하지 않는다. 결과 JSON은 `records/`에 있다(`build_record.json` · `check_report.json` · `check_report_native.json` · `audit_result.json`).

## 3. 실행 결과

**수직동기를 끈 실제 전투(작전 첫 방, 2,400프레임).** 같은 세션이 아니면 서로 비교하지 않는다(프로젝트 규칙: 이 PC는 부하에 따라 ±20 % 흔들린다). 두 번 만든 빌드의 숫자를 나란히 적어 둔다.

| 작전 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 첫 빌드(`c4417936`, 22:45) 중앙값 | 292 | 273 | 245 | 223 | 221 | 244 | 237 | 234 | 218 | 213 |
| 이 빌드(`25fc3c31`, 23:08) 중앙값 | 221 | 200 | 169 | 152 | 165 | 176 | 172 | 164 | 160 | 163 |
| 이 빌드 최저 | 122 | 132 | 120 | 118 | 126 | 114 | 120 | 144 | 116 | 119 |

이 빌드가 25–35 % 낮다. **코드 때문이라고 볼 근거는 없다.** 두 빌드 사이에 게임 코드가 바뀐 곳은 방 규칙 줄(`_tick_room_rule`은 규칙이 없으면 빈 사전 검사 한 번이고, 훈련 시뮬레이터에서는 시작조차 하지 않는다)뿐이고, 이 PC에는 사용자의 다른 프로그램이 도는 시간이 있다. 같은 세션의 번갈아 돌린 A/B가 아니므로 "느려졌다"도 "같다"도 주장하지 않는다. 확실한 것은 두 번 다 60 FPS 상한의 두 배를 훨씬 넘는다는 것뿐이다.

**1080p 프레임.** `shots/native_title.png`(제목 화면: 캠페인 막대의 10칸이 모두 막대 안에 있고 `0 / 10`) · `shots/native_battle_op10.png`(작전 10 전투: RAM · MORTAR · 방패 로봇, 총구 불꽃과 폭발, 바닥의 위험 구역 고리, HUD가 모두 그려졌다) · `shots/native_deploy_op01.png`(출격 경로: 증원 2파 문구 `REINFORCEMENTS / WAVE 2-2`와 `HOSTILE SIGNALS INBOUND`, 증원 진입 표시). 해시는 `records/validate_1080p.json`.

첫 전체 실행의 네이티브 세 장은 1920×1082로 나왔다. 전체 화면 Godot 창이 모니터보다 2 px 크기 때문이다(창 사각형 `[2560, 0, 4480, 1082]`). `check_report.json`에 그대로 두었고, 도구가 이제 모니터 사각형으로 잘라서(`capture_window(..., clip_monitor=True)`) 다시 돌린 세 장이 `check_report_native.json`과 `shots/`의 것이다. 창 모드(1280×720 요청) 스모크 캡처는 1038×614로 나오므로 증거로 쓰지 않았고 커밋하지 않았다(`.cache/export_trial/record/shots/`에 있다).

## 4. 만들면서 맞닥뜨린 함정(도구가 모두 처리한다)

1. **Godot는 가져온 파일의 가져온 사본만 팩에 넣고 원본은 넣지 않는다.** 이 게임은 PNG · WEBP · JPG · MP3를 날 바이트로 읽는다(`Image.load_from_file`, 로봇 그림 등). `export_presets.cfg`의 `include_filter`만으로는 원본이 들어가지 않는다. 그래서 그 확장자를 스테이지에서 `importer="keep"`으로 둔다(웹 시연 빌더 `build_sites_demo.py`와 같은 방법, 260개 파일). 팩 감사가 날 바이트 374개를 모두 열어 본다.
2. **release 템플릿은 `-s`(스크립트 실행)를 무시한다.** 첫 시도는 스크립트를 돌리는 대신 게임을 그냥 켰다. 팩 감사는 에디터 바이너리에 `--main-pack`을 주어 돌리고, 프레임 수는 `--print-fps`로 읽는다.
3. 프로젝트 폴더에서 돌리면 나는 "Loaded resource as image file, this will not work on export" 경고가 내보낸 빌드에서는 날 파일이 팩에 있어 문제가 되지 않는다는 것을 위 감사와 로봇이 그려진 프레임으로 확인했다.
4. 내보낸 게임도 `playtest_logs/*.json`을 쓴다(`PlaySessionLog`, 작전 하나에 파일 하나). 위치는 `%APPDATA%\Godot\app_userdata\SABLE CIRCUIT\playtest_logs\`다. 전투에 들어간 실행 23회가 파일 23개를 `env/` 아래에 남겼다(전체 실행 26회 가운데 제목 화면 · 네이티브 제목 · 팩 감사는 전투에 들어가지 않는다).
5. 종료 때 ObjectDB 경고와 리소스 오류는 프로젝트에서도, 내보낸 빌드에서도 같다.

## 5. 나눠 줄 때 알아 둘 것(다른 PC에서는 시험하지 않았다)

- `SableCircuit.exe`와 `SableCircuit.pck`를 **같은 폴더에** 두어야 한다. 하나로 합치는 옵션(`embed_pck`)은 시도하지 않았다.
- 서명이 없어서 Windows가 "PC를 보호했습니다"(SmartScreen) 창을 띄울 수 있다. 추가 정보 → 실행. 설치기 · 아이콘 · 업데이트 경로는 없다.
- 시험하는 사람의 `%APPDATA%\Godot\app_userdata\SABLE CIRCUIT\playtest_logs\`를 돌려받아야 한다. 사람이 쏜 균형 기록이 지금 이것뿐이다(이 PC의 `playtest_logs/`는 비어 있다).
- 약 0.5 GB다. 메신저·메일로는 크고 클라우드 폴더나 USB가 맞다. 어디에 올릴지는 사용자의 결정이고 이 프로젝트의 규칙이 막고 있다.

## 6. 하지 않은 것

- 사람이 직접 한 플레이, 다른 PC(느린 GPU, 다른 Windows 버전)에서의 실행, 서명, 설치기, 웹·모바일 빌드.
- 이 PC의 작전별 FPS A/B(같은 세션에서 번갈아 돌리는 것)는 이 기록이 아니라 `qa/per_operation_fps_20261006/`의 프로젝트 실행 조사에 있다.
- 그림 · 소리 · 균형 승인. 기록된 그림 승인은 작전 10의 판 15장과 ORIGIN CORE뿐이다(`qa/site7_op10_art_approval_20261002/`).

## 7. 파일

- `records/build_record.json` — 템플릿 해시 · 스테이지 · 가져오기와 내보내기 시간 · 팩 구성
- `records/check_report.json` — 전체 실행(26회). 네이티브 세 장은 1920×1082로 기록돼 있다
- `records/check_report_native.json` — 모니터 사각형으로 자른 네이티브 세 장(1920×1080)
- `records/check_report_first_build.json` — 첫 빌드(`c4417936`)의 전체 실행(3절 표의 윗줄)
- `records/audit_result.json` — 팩 감사
- `records/validate_1080p.json` — 네이티브 프레임 검증기 결과(컨테이너와 해독만 본다. 화질 주장이 아니다)
- `shots/native_*.png` — 1920×1080 프레임 세 장
