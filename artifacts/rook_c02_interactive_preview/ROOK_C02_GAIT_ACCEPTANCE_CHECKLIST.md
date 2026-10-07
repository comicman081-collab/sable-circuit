# ROOK C02 8방향 보행·사격 수용 체크리스트

## 현재 판정 — V25는 불합격

이 문서는 ROOK C02의 다음 모션 후보에 적용하는 Ponytail Full 검증 계약이다. 모든 항목이 통과하기 전에는 `current` 승격, 런타임 배포, 또는 “보행 완료” 판정을 해서는 안 된다.

V25(`rook-c02-v25-true-side-stride`)는 아래 근거로 **FAIL**이다.

- 사용자 재현 영상: [user_report_20260902_060253](user_report_20260902_060253/), 특히 [HUD 접촉 시트](user_report_20260902_060253/hud_contact_2fps_8x8.png). 옆 이동에서 걷는 대신 같은 다리의 무릎을 든 자세가 오래 유지되고, 이동·사격 전환에서 전신 방향이 바뀐다.
- `render_walk_pose_sources_blender_ual.py`의 `phase_for_move()`는 24개 UAL 샘플을 A/B 두 소스로만 선택한다. 실제 디코드 RGBA 검사 결과도 E·SE·S·SW·W·NW·N·NE 모두 **2/24개** 고유 이동 셀뿐이다. A는 00–05, 18–23이고 B는 06–17이다.
- 동일 스크립트는 idle을 `A,A,B,B`, fire를 `A,A,B,B,A,A`로 작성한다. 따라서 정지·사격 중 하체가 보행 포즈 사이를 전환한다.
- 현재 HTML은 이동 중에는 `gaitDirection` 전신 아틀라스를, 사격 중에는 `player.direction` 전신 아틀라스를 선택한다. 그러나 총구·발사체는 항상 `player.direction`를 사용한다. 조준과 이동이 다를 때 발사 순간 전신이 튀며, 사용자에게 보이는 총구와 발사체의 연속성도 보장되지 않는다.

## 적용 범위와 증거 산출물

검증 대상 방향은 `E, SE, S, SW, W, NW, N, NE`이며, `W`는 검증된 E 원화의 Blender 수평 포즈 전이일 수 있다. 그 경우에도 좌향 보행의 발·무릎·골반 진행 방향은 왼쪽이어야 한다.

후보는 다음 증거를 프로젝트 내부에 남긴다.

| 증거 | 최소 내용 |
| --- | --- |
| `ROOK_C02_GAIT_8DIR_24F_CONTACT_1920X1080.png` | 방향별 24개 이동 셀, 1:1 원본 크기 하체 확대 패널, 프레임 번호·접지측·UAL 샘플 번호 |
| `ROOK_C02_GAIT_8DIR_5S_1920X1080.mp4` | 각 방향을 최소 한 번 이상 5초간 지속 이동한 네이티브 1920×1080 동영상 |
| `ROOK_C02_AIM_GAIT_8X8_1920X1080.png` 및 동영상 | 이동 8방향 × 조준 8방향의 조합에서 이동·사격 직전/직후를 보이는 매트릭스 |
| `ROOK_C02_IDLE_FIRE_LEG_LOCK_1920X1080.png` | 방향별 idle 4셀과 fire 6셀의 하체 원본 크기 비교 |
| `ROOK_C02_GAIT_ACCEPTANCE.json` | 아래 자동 검사 수치, 소스/아틀라스 SHA-256, 실행 명령, PASS/FAIL 사유 |

정적 HTML만으로는 동적 통과가 될 수 없다. 모든 영상과 정적 검토 이미지는 `tools/art_pipeline/validate_visual_evidence_1080p.py`의 네이티브 1080p 검증을 통과해야 한다.

## 필수 수용 기준

### 1. 실제 시간 보행 셀

- 각 방향의 `move`는 24개 384×384 RGBA 셀을 제공한다.
- 프레임을 파일 해시가 아닌 **디코드 RGBA 픽셀**로 비교했을 때, 하체 영역(골반 아래)의 고유 포즈가 최소 8개여야 한다. 같은 픽셀 셀의 연속 반복은 최대 2프레임(24fps에서 약 83ms)까지만 허용한다.
- 인코딩 차이, 전신 1–2px 평행 이동, 색상 잡음, 또는 상체 반동만으로 해시가 달라진 경우는 새 하체 포즈로 계산하지 않는다. 하체 마스크·발 위치·무릎 각도 중 하나가 실제로 달라져야 한다.
- 24프레임 순서는 UAL 샘플·접지 이벤트와 함께 후보 매니페스트에 기록한다. UAL JSON을 단지 메타데이터로 읽는 것만으로는 통과하지 않는다.

자동 검사 방법:

```powershell
@'
from hashlib import sha256
from pathlib import Path
from PIL import Image

candidate = Path(r'art_src/characters/rook/fast_pipeline/motion/<candidate>')
for direction in ('E','SE','S','SW','W','NW','N','NE'):
    frames = []
    for path in sorted((candidate/'blender_frames'/direction/'move').glob('*.png')):
        rgba = Image.open(path).convert('RGBA')
        # 골반 아래만 비교한다. 후보가 별도 lower mask를 제공하면 그 마스크를 우선 사용한다.
        lower = rgba.crop((0, int(rgba.height * .45), rgba.width, rgba.height))
        frames.append(sha256(lower.tobytes()).hexdigest())
    runs, start = [], 0
    for index in range(1, len(frames) + 1):
        if index == len(frames) or frames[index] != frames[start]:
            runs.append(index - start); start = index
    print(direction, {'unique_lower_rgba': len(set(frames)), 'max_identical_run': max(runs)})
'@ | python -
```

이 출력은 모든 방향에서 `unique_lower_rgba >= 8`, `max_identical_run <= 2`여야 한다. 이 수치는 필요조건일 뿐이며, 아래의 접지 시각 검토를 대체하지 않는다.

### 2. 좌·우 교대 접지와 8방향 진행

모든 방향의 루프에서 왼발과 오른발이 순서대로 다음 상태를 보여야 한다: 접지 → 체중 지지 → 뒤꿈치/발끝 이탈 → 반대발 전방 통과 → 반대발 접지. 한쪽 발만 계속 앞으로 들거나, 양발이 같은 방향으로 고정된 채 몸통만 미끄러지는 것은 FAIL이다.

| 입력 방향 | 시각 수용 기준 |
| --- | --- |
| E / W | 엄격한 측면 보행이다. 몸통·골반·양 부츠가 진행 방향을 향하고, 선행 발과 후행 발이 매 반주기 교대한다. 정면을 향한 한 발 또는 양 발, 높은 무릎 고정 자세, 90° 허리 꺾임은 FAIL이다. |
| N / S | 원근 때문에 겹치더라도 양 발의 좌우 지지 순서와 전·후 발 위치 교대가 읽혀야 한다. 한 발 실루엣만 흔들리거나 두 부츠가 계속 겹치면 FAIL이다. |
| NE / NW / SE / SW | 대각 진행 방향에 맞는 골반·양발 진행 벡터를 유지하면서 좌우 접지가 교대한다. 수평/수직 원화를 단순 섞어 허리만 90° 꺾이는 조합은 FAIL이다. |

UAL의 접지 표기는 실제 화면과 일치해야 한다. 각 후보의 24프레임 검토 시트에는 최소한 좌 접지 시작/지지/이탈과 우 접지 시작/지지/이탈이 각각 식별되어야 한다. 두 접지 구간의 발 지지측이 영상에서 반대로 보이면 FAIL이다.

정지 배경 격자 위에서 접지 발을 추적한다. 한 접지 구간에서 같은 부츠의 화면상 위치는 60fps 캡처 기준 3px 이내로 유지되고, 몸통과 반대발이 진행해야 한다. 이 기준을 넘는 연속 활주는 스케이팅으로 FAIL이다.

### 3. idle·fire 하체 잠금

- idle 4프레임은 보행 주기를 재생하지 않는다. 방향별 하체 마스크와 부츠·무릎 관절 배치는 동일해야 한다.
- fire 6프레임도 하체의 접지측, 무릎 각도, 발 위치를 바꾸지 않는다. 상체·무기 반동은 허용하지만 하체를 A/B 보행 포즈로 교체해서는 안 된다.
- 전신 반동을 사용하는 경우에도 하체는 등록 보정 후 동일해야 하며, 보정량은 2px 이하이다.

자동 검사 방법: 후보는 각 상태 셀의 하체 마스크 SHA-256과 하체 기준점 등록 오차를 `ROOK_C02_GAIT_ACCEPTANCE.json`에 기록한다. idle은 모든 셀이 동일 해시, fire는 2px 이내 등록 후 동일 해시여야 한다. 하체 해시가 이동 셀의 접지 포즈와 교차하면 FAIL이다.

### 4. 조준·이동·총구·발사체의 단일 계약

현재 조작 문구는 이동과 마우스 8방향 조준을 함께 약속한다. 그러므로 이동 중 조준이 이동 방향과 다른 64개 조합을 지원해야 한다.

- 이동 상태에서 사격 상태로 바뀌어도 전신 또는 골반이 `gaitDirection`에서 `player.direction`로 한 프레임에 교체되어서는 안 된다.
- 독립 조준을 구현한다면 하체는 이동 방향의 실제 보행, 상체·총은 조준 방향을 유지해야 하며, 골반 경계는 연속적이어야 한다. 조합을 이유로 허리가 90°로 꺾이거나 잘려 보이면 FAIL이다.
- 총구 표식, 펠릿 첫 위치, 펠릿 평균 진행 벡터는 플레이어가 실제로 보는 조준 총구와 일치해야 한다. 표식/첫 펠릿의 총구 중심 오차는 원본 셀 기준 4px 이하, 펠릿 방향과 총열 방향의 각도 오차는 5° 이하여야 한다.
- 동일 화면 프레임의 상태값(`aim`, `gait`, `state`, `atlas frame`)과 선택 아틀라스/레이어 정보를 디버그 API에서 읽을 수 있어야 한다. state 전환으로 방향 정책이 암묵적으로 달라져서는 안 된다.

각 이동 방향에 대해 8개 조준 방향을 최소 0.5초 이동 후 사격해 64개 조합을 캡처한다. 특히 `A/D × E/W`, `A/D × NE/NW/SE/SW`, 그리고 정반대 조준 조합을 별도 확대한다. Godot 런타임은 `rook_c02_fast_runtime_smoke.gd`의 기존 소켓 원점 일치 검사(`distance < 0.01`)도 계속 통과해야 한다.

### 5. 원화·파이프라인 경계

- 새 보행 원화는 Codex built-in ImageGen으로만 만들고, 선택 결과와 해시를 먼저 이 저장소에 복사한다. Blender+UAL은 원화를 대체하거나 국소 픽셀을 복원하는 용도가 아니라, 승인된 원화의 움직임·포즈 전이·패키징에만 사용한다.
- 각 ImageGen 원본은 균일한 chroma green 마스터를 보존하고, 런타임에는 별도 RGBA 파생본을 사용한다.
- 후보·현재·이전 후보의 출처와 SHA-256을 남긴다. 불합격 후보를 `current` 또는 런타임 경로에 복사해 통과처럼 보이게 해서는 안 된다.

### 6. 게이트 도달성·12포즈 출처 스키마

- `validation_required` 매니페스트 문자열만으로는 검증이 실행된 것이 아니다. 보행 계약 검사는 패키징 직후, `current` 승격 전에 실제 승격 대상 아틀라스를 입력으로 **반드시 실행**되고, 그 JSON 결과가 후보 안에 남아야 한다. 누락·실행 오류·FAIL은 승격을 차단한다.
- 12포즈 렌더러를 사용할 경우 패키저는 “정확히 두 포즈”라는 이전 V23–V25 출처 스키마를 사용해서는 안 된다. 방향마다 F00–F11의 12개 authority를 모두 읽어 각 원본·마스크·정규화 QA·SHA-256·수평 미러 여부를 검증해야 한다. 두 포즈만 검증하거나 나머지 10개를 출처 없이 패키징하면 FAIL이다.
- 보행 구조 검사 기준은 `move_lower_body_unique_frames >= 8`, `move_max_consecutive_identical_lower_frames <= 2`, `idle_lower_body_unique_frames == 1`, `fire_lower_body_unique_frames == 1`이다. 6개 고유 하체 포즈로 낮추면 불완전한 반주기 후보가 통과할 수 있으므로 허용하지 않는다.
- 검증기가 후보의 `*_green.png`을 검사하는지, 런타임 RGBA `*.png`을 검사하는지 입력 계약을 하나로 고정한다. 두 형식 중 하나가 빠져 검사 자체가 건너뛰거나, 승격 뒤에만 검사되어 실패한 후보가 이미 `current`가 되는 경로는 FAIL이다.
- F00–F11에는 `phase_name`, `support_foot`, `ual_sample_indices`가 명시되어야 한다. UAL 접지 이벤트와 그 표기를 대조하여 F11→F00 루프 경계까지 좌·우 접지 순서가 이어짐을 확인한다. 단순 `index // 2` 순번과 서로 다른 픽셀만으로는 반전된 발 순서·비연속 루프를 검출할 수 없다.
- fire 6셀은 하체를 잠그되, 상체/무기·총구에는 실제 반동 또는 발사 시각 변화가 있어야 한다. 전신 F00 정지 셀 여섯 장과 발사체만으로 fire 애니메이션을 주장할 수 없다.

## 실행 순서와 최종 판정

1. 후보의 원화·Blender 렌더·UAL 샘플 매핑을 완성하고, 위 1–3항의 하체 해시/접지 검사를 생성한다.
2. 다음 기본 구조 검사를 실행한다.

```powershell
python tools/character_pipeline/sable_character_pipeline.py validate --spec tools/character_pipeline/specs/rook_c02_fast_v1.json
python -m pytest -q tests/test_sable_character_pipeline.py
godot --headless --path . --script res://tests/smoke/rook_c02_fast_runtime_smoke.gd
```

3. 네이티브 캡처와 HTML을 함께 검증한다.

```powershell
python tools/art_pipeline/validate_visual_evidence_1080p.py `
  artifacts/rook_c02_interactive_preview/ROOK_C02_INTERACTIVE_STRIDE_FIRE.html `
  artifacts/rook_c02_interactive_preview/ROOK_C02_GAIT_8DIR_5S_1920X1080.mp4 `
  artifacts/rook_c02_interactive_preview/ROOK_C02_GAIT_8DIR_24F_CONTACT_1920X1080.png `
  --require-dynamic-capture `
  --output artifacts/rook_c02_interactive_preview/ROOK_C02_GAIT_1080P_VALIDATION.json
```

4. Ponytail Full 검토자는 8방향 24프레임 시트, 5초 동영상, 64개 aim/gait 사격 매트릭스, idle/fire 하체 잠금 시트를 모두 원본 크기로 확인한다. 자동 검사와 시각 검토가 모두 PASS이고, 사용자 보고 영상에서 보인 스케이팅·측면 보행·허리 꺾임·총구 불일치가 재현되지 않을 때만 최종 PASS이다.

`sable_character_pipeline.py validate`의 기존 PASS는 파일 형식·크기·알파를 확인하는 구조 검증일 뿐이다. 위 보행 시각 수용 기준의 PASS를 의미하지 않는다.
