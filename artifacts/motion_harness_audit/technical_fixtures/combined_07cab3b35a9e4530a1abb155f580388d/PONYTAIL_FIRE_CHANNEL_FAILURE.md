# Ponytail FULL — combined fire-channel 중단 원인 분석

- Reviewer: Codex Ponytail FULL `/root/ponytail_motion_audit`
- Reviewed UTC: `2026-09-07T10:35:49Z`
- Subject: `fbd6c57b97ae99091ebf6f14df93c57604adac6779f5fb6aaa36ffe5e64bca9f`
- Scope: 지정 synthetic marker fixture의 실제 원장과 현재 runtime/actor/검사/수집 코드를 읽기 전용으로 대조. 보고서 이외 파일은 변경하지 않았으며 Godot·Blender·Luna를 실행하지 않았습니다.
- Verdict: **FAIL/HOLD 유지. 이동 활성화와 방향 계산의 서로 다른 미세 이동 기준 때문에 발생한 실제 runtime 계약 불일치입니다. fire 상태 누락 또는 총구 세계좌표 불일치가 원인은 아닙니다.**

## 1. 실제 실행 범위와 최초 실패

이 폴더에는 `runtime_30hz.json`만 있습니다. 30Hz Godot는 240사례 전체 수집을 끝냈고 `stdout.log`에 `MOTION_HARNESS_CAPTURE_COMPLETE cases=240 hz=30`을 남겼습니다. 이후 Python `validate_runtime_subject`가 실패하여 score/summary 작성 및 60/120Hz 실행으로 진행하지 못했습니다. 따라서 이번 폴더를 30/60/120Hz 모두 수행한 결과로 보고하면 안 됩니다.

- 실제 30Hz: 240사례 × 63표본 = 15,120표본, 1,856발.
- 최초 검사 실패: **`collision_fire/NW`, sample index 30 (0-based)**.
- 전체 원장을 같은 독립 각도/상태 규칙으로 대조했을 때 해당 오류는 아래 6발입니다. 다른 사례에서 같은 shot-channel 오류는 찾지 못했습니다.
- 아래 모든 실제 shot state는 `move_fire`, frame은 17입니다. 표본과 shot의 채널도 동일합니다.

| Hz | Case | Sample | 실제 변위 (world px) | 거리 (px) | 검사에서 요구한 채널 | 실제 채널 |
| --- | --- | --- | --- | --- | --- | --- |
| 30 | collision_fire/NW | 30 | (+0.0009155273, -0.0009155273) | 0.0012947512 | walk/NE/NW/fire | walk/NW/NW/fire |
| 30 | collision_fire/NW | 36 | (+0.0009765625, -0.0009155273) | 0.0013386055 | walk/NE/NW/fire | walk/NW/NW/fire |
| 30 | collision_fire/NW | 42 | (-0.0009155273, +0.0009765625) | 0.0013386055 | walk/SW/NW/fire | walk/NW/NW/fire |
| 30 | collision_fire/NW | 48 | (-0.0009155273, +0.0009765625) | 0.0013386055 | walk/SW/NW/fire | walk/NW/NW/fire |
| 30 | collision_fire/NW | 54 | (-0.0009155273, +0.0009765625) | 0.0013386055 | walk/SW/NW/fire | walk/NW/NW/fire |
| 30 | collision_fire/NW | 60 | (-0.0009155273, +0.0009765625) | 0.0013386055 | walk/SW/NW/fire | walk/NW/NW/fire |

## 2. 실제 실행 경로와 원인

`scripts/actors/operator_actor.gd:233`부터 실제 `move_and_slide`/arena clamp 변위를 구하고, `:237`에서 `commit_actor_displacement`를 호출한 후 `:243`에서 사격합니다. `_try_fire`의 `:294`는 primary_fired 신호를 동기 전달한 뒤 projectile을 만듭니다. 이전에 고친 이동/표시/사격 순서 문제는 이번 실패 원인이 아닙니다.

불일치는 `scripts/animation/fast_character_runtime.gd` 내부에 있습니다.

1. `:390`: `displacement.length_squared() > 0.000001`이면 이동으로 처리합니다. 길이 기준으로 **0.001px 초과**입니다.
2. `:394`: 같은 displacement를 `_sector_from_vector`에 넘깁니다.
3. `:605–607`: 이 helper는 `length_squared() < 0.0001`이면 실제 변위 각도를 쓰지 않고 **actor.facing_sector**로 돌아갑니다. 길이 기준으로 **0.01px 미만**입니다.
4. 따라서 **0.001 < 이동거리 < 0.01px** 구간은 이동 상태/위상은 활성화되지만 이동 방향은 조준 방향으로 대체됩니다.
5. 새 `motion_harness.py:909–919`는 실제 위치 차분이 0.001px보다 크면 그 실제 각도와 입력 mode/aim으로 fire 채널을 계산합니다. NW 벽 접촉 중의 미세 NE/SW 보정 변위는 NW가 아니므로 검사가 올바르게 이 불일치를 잡았습니다.

첫 실패의 실제 속도는 약 **0.03884px/s**에 불과합니다. 해당 표본은 slide_collisions=2이고, 지면 이동이라기보다는 충돌 solver의 미세 보정이 locomotion으로 오인된 상황입니다. 근거 없이 wanted velocity나 NW 입력을 정답으로 대입하여 검사식을 통과시키면 안 됩니다.

## 3. normalize 한 줄만으로 끝내면 안 되는 이유

`_sector_from_vector(displacement.normalized())`는 임계값 불일치 자체는 없앨 수 있습니다. 그러나 이 fixture에는 더 큰 왕복 collision recovery도 있습니다.

- sample 25: 0.0006905px → stationary/base fire.
- sample 26: 0.0641482px, 약 1.92445px/s → `walk/SE/NW/fire`.
- sample 27–30: 약 0.0013px → 지금 코드는 fallback으로 `walk/NW/NW/fire`.
- sample 31: 0.0635291px → `walk/NW/NW/fire`.
- sample 32: 0.0634983px → `walk/SE/NW/fire`.
- NW collision/collision_fire 각각 sample 16 이후 최대 보정 거리 약 0.0641904px, 누적 이동 길이 약 0.4370483px입니다.

즉 normalize만 하면 거의 정지한 벽 앞에서 하체 채널이 SE/NW/NE/SW로 왕복하는 현상은 남거나 더 늘 수 있습니다. 이것은 다리 위상 숫자가 작더라도 전신 방향 그림이 갈아끼워지는 문제입니다. 현재 0.01px deadband로만 맞추는 것도 0.064px 보정에는 충분하지 않습니다.

## 4. 최소 수정 권고

새 추상화나 별도 runtime을 만들 필요가 없습니다. 기존 `MOVE_THRESHOLD := 12.0` (`fast_character_runtime.gd:10`, px/s) 같은 이미 정의된 정지 기준을 **실제 관측 속도** `displacement.length() / delta`에 적용하는 방법을 우선 권고합니다.

1. 실제 이동/정지 판정, gait 위상 증가, 보여 줄 channel, 실제 shot의 기대 state/channel에 **같은 단위의 정지 의미**를 사용합니다. 이 기준 이하의 충돌 보정은 stationary/base fire로 표시하고 gait 위상을 진행시키지 않습니다.
2. 그 이상으로 실제 이동한 경우에는 정규화한 관측 변위로 이동 방향을 구합니다. 조준/입력 방향 fallback이 이동 방향을 대체하지 않도록 합니다.
3. 독립 motion 계약에 presentation의 stationary deadband 의미를 명시하고, Python 검사도 raw world-position 차분과 dt에서 같은 물리 단위 판정을 계산해야 합니다. runtime이 보고한 moving/state를 정답으로 다시 받아서는 안 됩니다.
4. **실제 root 원장의 미세 변위를 지우거나 0으로 고치지 않습니다.** 실제 속도·경계·collision·지면 접지·누적 미끄럼 측정은 원래 변위를 그대로 사용합니다. 기술 수용 오차나 아트/보폭 기준을 완화해서 PASS시키는 수정이 아닙니다.
5. 오류 메시지에 hz/case/index/실제 변위/expected/actual channel을 포함하면 다음 실패에서 전체 렌더를 다시 돌리지 않고 바로 원인을 좁힐 수 있습니다.

12px/s는 기존 표현 코드의 기준을 재사용하는 제안이지 이번 synthetic 결과만으로 최종 게임 접지 기준을 승인한 값이 아닙니다. 정상적인 실제 느린 wall sliding을 어떻게 표시할지까지 명시적으로 검증해야 합니다. 이동/정지 경계를 아무 설명 없이 검사에만 추가하거나, 관측 각도 검사를 삭제하는 수정은 승인하지 않습니다.

## 5. 필요한 한정 회귀 검증

- 현재 6발을 기존 코드에서는 실패하는 부정 회귀로 보존합니다.
- 기존 임계값 충돌 구간(0.001px~0.01px)과 이 원장에 실제 나온 0.064px 왕복 보정을 입력한 경우, 새 관측 속도 기준에서 gait/표시/fire가 같은 stationary 상태를 갖는지 확인합니다.
- 정지 속도 경계 바로 아래/위, zero delta, 실제 tangent wall slide, 정상 walk/run, same-tick start/aim/fire를 각각 검증합니다.
- 정지로 분류한 동안 실제 원장과 root 측정은 남아 있고, 위상은 증가하지 않으며 발사 원점은 실제 sprite marker와 일치해야 합니다.
- 경계 위의 이동은 실제 변위 방향을 사용하고, 정상 이동 연사 중 travel atlas를 잘못 표시하는 이전 회귀는 계속 FAIL이어야 합니다.
- 이후 **동일 새 코드 snapshot**으로 30/60/120Hz를 새 fixture 경로에 다시 수행합니다. 과거 raw/score/subject를 수정하여 성공 결과로 바꾸지 않습니다.

## 6. 이번 증거로 확인 가능한 정상 부분과 한계

1,856발을 읽기 전용으로 대조했을 때 non-fire state shot은 0이었으며, 수집된 실제 빨간 texture marker의 세계좌표와 projectile 원점 간 최대 오차는 **0px**였습니다. fixture의 display_scale=1.7, display_offset=[13,-9]를 사용하므로 단위 배율/원점 0만 맞춘 결과도 아닙니다. 위 6발 역시 총구 오차는 0이고 state는 move_fire입니다.

이 사실은 marker fixture의 기술적 연결에 한정합니다. 전체 검사 함수는 위 오류에서 중단되어 뒤쪽 모든 검증이 완료된 것은 아니므로, 30Hz 전체 PASS나 60/120Hz PASS를 선언하지 않습니다. 실제 MICA 외형·3D 메시·UAL·보폭·발 높이·접지·무기 축·HTML 또는 Luna 준비 증거로 사용할 수 없습니다.

## 7. 정확한 증거/코드 바인딩

아래 네 소스 파일의 현재 SHA는 읽은 시점에 `engine/input_snapshot.json`과 모두 일치했습니다. 변경된 소스를 과거 fixture 결과에 섞어 해석한 원인은 아닙니다.

| 파일 | SHA-256 |
| --- | --- |
| engine/runtime_30hz.json | `fc7054235edfbf3db1a01f6085e1f55d444fabe03cf95dfa5aa1f775c7f64e15` |
| engine/input_snapshot.json | `518805a7bd7c8e9dbbef0805a4d43a2de9451596cbc1dc88d2e56ca0ada4deda` |
| engine/process_30hz/stdout.log | `a00c4c6542575de58455272b5c84b5dd3fd741f3e8510bd8e88e4b1245b9ae27` |
| input/runtime_descriptor.json | `b5bcba8743f7440e5cc7cae6ff1a602f479a26372633cb70df4a4ce363ca0e07` |
| scripts/actors/operator_actor.gd | `5808fef8229fdc11b63603b72e08073ef1222bb6da1f8378e049176d9cd9417d` |
| scripts/animation/fast_character_runtime.gd | `1c470ee710807f39bc22cc03006e6f9261437d6cab5b8abe7b4023129792d4f8` |
| tests/render/character_motion_harness.gd | `b784ee7154157f5a0c6bce1368fe8f3ffb03ddb008488dcd90e2f7b8376e6c62` |
| tools/character_pipeline/motion_harness.py | `32b1ba084c09a1f32aba4070027eb8f1c097309c94ff14d9eff8e4ee8d7b8505` |

서명: **Codex Ponytail FULL reviewer `/root/ponytail_motion_audit`**.
